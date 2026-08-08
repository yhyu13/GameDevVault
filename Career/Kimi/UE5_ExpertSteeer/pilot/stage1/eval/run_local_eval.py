"""run_local_eval.py — Qwen3.5 小模型 × 9 任务本地推理基线评估（直接加载，无 HTTP/server）。

从本地路径加载 Qwen3.5 safetensors，纯 transformers+torch，零外部服务。
支持任意本地 checkpoint（含 SFT/DPO 训练后的），所以既跑基线也跑训练后评估。

依赖（项目本地 venv，已装在 stage1/.venv）：
  pip install "transformers>=5" "accelerate>=1" "huggingface_hub>=1" "tokenizers>=0.21" torch==2.5.1+cu121

用法:
  .venv/bin/python eval/run_local_eval.py --selftest                  # 环境自检（不需要模型）
  .venv/bin/python eval/run_local_eval.py --samples 1                 # dry-run sanity
  .venv/bin/python eval/run_local_eval.py --samples 10                # 全量三档
  .venv/bin/python eval/run_local_eval.py --sizes 0.8B 2B 4B --samples 10
  .venv/bin/python eval/run_local_eval.py --model-path /path/to/sft-v1 --label sft-v1

输出: eval/results/results_<ts>.json（逐样本）+ summary_<ts>.md（pass@1 矩阵）
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

STAGE1 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STAGE1))

import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

from teacher_pool import POOL, PROMPTS  # noqa: E402
import run_stage1 as rs  # noqa: E402  （复用 run_verifier）

SYSTEM = "你是 UE5 工程师。按任务要求输出完整、可直接运行的 Python 代码。只输出代码，不要任何解释、注释说明或多余文字。"
EXTRACT_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.S)

DEFAULT_QWEN_DIR = Path(os.environ.get(
    "QWEN_HF_DIR", "/media/home/hangyu5/Documents/Hugging-Face/Qwen"))
DEFAULT_SIZES = ["0.8B", "2B", "4B"]
SIZE_DIR_FMT = "Qwen3.5-{size}"  # Qwen3.5-0.8B / Qwen3.5-2B / Qwen3.5-4B
SIZE_LABEL_FMT = "qwen3.5:{size}"  # 用于结果记录的短标签


def extract_code(text):
    if not text:
        return None
    m = EXTRACT_RE.search(text)
    if m and "def " in m.group(1):
        return m.group(1).strip()
    idx = text.find("def ")
    if idx == -1:
        return None
    return text[idx:].strip()


def run_sample(task_id, code, tmp_dir):
    path = tmp_dir / f"{task_id.replace('/', '_')}_cand.py"
    path.write_text(code + "\n", encoding="utf-8")
    return rs.run_verifier(task_id, path)


def selftest():
    """不加载模型，只跑 verifier 在 POOL 候选代码上的 sanity check。"""
    ok = 0
    tmp = STAGE1 / "eval" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    for task_id, cands in POOL.items():
        name = sorted(cands.keys())[0]
        r = run_sample(task_id, cands[name], tmp)
        passed = r.get("l3_ok") is True
        ok += 1 if passed else 0
        print(f"[selftest] {task_id}/{name}: {'PASS' if passed else 'FAIL ' + str(r.get('error', r.get('l3_failures')))[:120]}")
    print(f"selftest {ok}/{len(POOL)} tasks passed")
    return ok == len(POOL)


def load_model(path, dtype):
    tok = AutoTokenizer.from_pretrained(str(path))
    dtype_map = {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}
    model = AutoModelForCausalLM.from_pretrained(
        str(path),
        dtype=dtype_map[dtype],
        device_map="cuda:0",
        attn_implementation="sdpa",
    )
    model.eval()
    if tok.pad_token_id is None:
        tok.pad_token_id = tok.eos_token_id
    return model, tok


def generate_text(model, tok, system, user, temperature, max_new_tokens):
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    inputs = tok(text, return_tensors="pt").to(next(model.parameters()).device)
    with torch.inference_mode():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=0.9,
            pad_token_id=tok.pad_token_id,
            eos_token_id=tok.eos_token_id,
        )
    return tok.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)


def resolve_targets(args):
    """把 CLI 参数归一为 [(model_path, label), ...] 列表。"""
    if args.model_path:
        return [(Path(args.model_path), args.label or Path(args.model_path).name)]
    out = []
    for size in args.sizes:
        p = DEFAULT_QWEN_DIR / SIZE_DIR_FMT.format(size=size)
        if not p.is_dir():
            sys.exit(f"本地模型路径不存在：{p}。用 --model-path 显式指定，或设 QWEN_HF_DIR。")
        out.append((p, SIZE_LABEL_FMT.format(size=size)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", default=None,
                    help="任意本地 checkpoint 路径（SFT/DPO 后模型也可）。指定时忽略 --sizes。")
    ap.add_argument("--label", default=None,
                    help="结果记录里使用的模型标签（默认取路径最后一段）。")
    ap.add_argument("--sizes", nargs="*", default=DEFAULT_SIZES,
                    help="本地 Qwen3.5 尺寸档（默认 0.8B 2B 4B），路径 = $QWEN_HF_DIR/Qwen3.5-<size>")
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--samples", type=int, default=10)
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--dtype", default="bf16", choices=["bf16", "fp16", "fp32"],
                    help="模型 dtype（默认 bf16；4B bf16 ≈ 8GB 显存，RTX 3090 24GB 够用）")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(0 if selftest() else 1)

    targets = resolve_targets(args)
    tasks = args.tasks or list(POOL.keys())
    tmp = STAGE1 / "eval" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    print(f"targets={[(str(p), lbl) for p, lbl in targets]} tasks={len(tasks)} samples={args.samples} temp={args.temperature} dtype={args.dtype}")
    results = []
    t0 = time.time()
    for path, label in targets:
        print(f"\n[load] {label} <- {path}")
        model, tok = load_model(path, args.dtype)
        for task_id in tasks:
            for i in range(args.samples):
                text = generate_text(model, tok, SYSTEM, PROMPTS[task_id],
                                     args.temperature, args.max_tokens)
                code = extract_code(text)
                rec = {"model": label, "task": task_id, "sample": i,
                       "parse_ok": code is not None, "l1_ok": None, "l3_ok": None,
                       "l3_failed": None, "error": None}
                if code is None:
                    rec["verdict"] = "NO_CODE"
                else:
                    r = run_sample(task_id, code, tmp)
                    if "error" in r:
                        rec["error"] = r["error"]
                        rec["verdict"] = "VERIFIER_ERROR"
                    else:
                        rec["l1_ok"] = r["l1_ok"]
                        rec["l3_ok"] = r["l3_ok"]
                        rec["l3_failed"] = r.get("l3_failed")
                        rec["verdict"] = "PASS" if r["l3_ok"] else ("L1_FAIL" if not r["l1_ok"] else "L3_FAIL")
                results.append(rec)
                print(f"[{label}] {task_id} #{i}: {rec['verdict']}")
        del model, tok
        torch.cuda.empty_cache()

    out_dir = STAGE1 / "eval" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    (out_dir / f"results_{ts}.json").write_text(
        json.dumps({"base": "local", "models": [lbl for _, lbl in targets], "tasks": tasks,
                    "samples": args.samples, "temperature": args.temperature,
                    "dtype": args.dtype, "results": results}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    lines = [f"# 本地基线摘要（base=local，dtype={args.dtype}，temp={args.temperature}，n={args.samples}/对）", ""]
    lines.append("| 模型 | 任务 | pass@1 | parse_fail | L1_pass_L3_fail |")
    lines.append("|---|---|---|---|---|")
    per_model = {lbl: {"pass": 0, "total": 0, "tasks": {}} for _, lbl in targets}
    for r in results:
        m = per_model[r["model"]]
        m["total"] += 1
        m["pass"] += 1 if r["verdict"] == "PASS" else 0
        t = m["tasks"].setdefault(r["task"], {"n": 0, "pass": 0, "no_code": 0, "l1_only": 0})
        t["n"] += 1
        t["pass"] += 1 if r["verdict"] == "PASS" else 0
        t["no_code"] += 1 if r["verdict"] == "NO_CODE" else 0
        t["l1_only"] += 1 if r["verdict"] == "L3_FAIL" else 0
    for _, label in targets:
        tm = per_model[label]
        lines.append(f"| **{label}** | 全部 | **{tm['pass']/tm['total']:.0%}** | — | — |")
        for task_id in tasks:
            t = tm["tasks"][task_id]
            lines.append(f"| | {task_id} | {t['pass']/t['n']:.0%} | {t['no_code']/t['n']:.0%} | {t['l1_only']/t['n']:.0%} |")
    lines.append("")
    lines.append(f"耗时 {time.time()-t0:.0f}s（不含模型加载）。对照 eval/success_criteria.md 判定。")
    (out_dir / f"summary_{ts}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nresults -> {out_dir / f'results_{ts}.json'}\nsummary -> {out_dir / f'summary_{ts}.md'}")


if __name__ == "__main__":
    main()
