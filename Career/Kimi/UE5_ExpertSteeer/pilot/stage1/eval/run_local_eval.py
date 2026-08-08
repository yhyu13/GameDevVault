"""run_local_eval —— Qwen 小模型 × 9 任务本地推理基线评估（纯 stdlib，跨机器可跑）。

支持任何 OpenAI 兼容本地端点：ollama（默认 http://localhost:11434/v1）、
llama.cpp server（http://localhost:8080/v1）、vLLM（http://localhost:8000/v1）。

用法:
  python eval/run_local_eval.py --selftest                       # 环境自检（不需要模型）
  python eval/run_local_eval.py --list-models                    # 列出本地可用模型
  python eval/run_local_eval.py --samples 1                      # dry-run sanity（1 样本/对）
  python eval/run_local_eval.py --samples 10                     # 全量
  python eval/run_local_eval.py --models qwen3:1.7b --samples 5  # 指定模型

--base-url 可指向任意 OpenAI 兼容端点（本地或云）；--api-key 可选（本地通常不需要）。
输出: eval/results/results_<ts>.json（逐样本）+ summary_<ts>.md（pass@1 矩阵）
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

STAGE1 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STAGE1))

from teacher_pool import POOL, PROMPTS  # noqa: E402
import run_stage1 as rs  # noqa: E402  （复用 run_verifier）

SYSTEM = "你是 UE5 工程师。按任务要求输出完整、可直接运行的 Python 代码。只输出代码，不要任何解释、注释说明或多余文字。"
EXTRACT_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.S)

DEFAULT_BASE = "http://localhost:11434/v1"  # ollama


def _request(base, api_key, path, body=None, timeout=300):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    req = urllib.request.Request(base + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_models(base, api_key):
    """OpenAI 兼容 GET /models；失败时返回 []。"""
    try:
        data = _request(base, api_key, "/models")
        return [m.get("id", "") for m in data.get("data", [])]
    except Exception:
        return []


def chat(base, api_key, model, prompt, temperature, max_tokens, retries=4):
    body = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
        "temperature": temperature, "top_p": 0.9, "max_tokens": max_tokens,
    }
    for attempt in range(retries):
        try:
            data = _request(base, api_key, "/chat/completions", body)
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            return None
    return None


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.environ.get("EVAL_BASE_URL", DEFAULT_BASE),
                    help="OpenAI 兼容端点，默认 ollama http://localhost:11434/v1")
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--models", nargs="*", default=None, help="本地模型名；缺省自动选名称含 qwen 的模型")
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--samples", type=int, default=10)
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--list-models", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(0 if selftest() else 1)

    available = list_models(args.base_url, args.api_key)
    if args.list_models:
        print(f"base={args.base_url}")
        for m in available:
            print(" ", m)
        return

    if args.models:
        models = args.models
    else:
        models = [m for m in available if "qwen" in m.lower()]
        if not models:
            sys.exit(f"未在 {args.base_url} 发现 qwen 模型。用 --list-models 查看，或 --models 指定。")
    tasks = args.tasks or list(POOL.keys())

    results = []
    tmp = STAGE1 / "eval" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    print(f"base={args.base_url} models={models} tasks={len(tasks)} samples={args.samples} temp={args.temperature}")
    t0 = time.time()
    for model in models:
        for task_id in tasks:
            for i in range(args.samples):
                text = chat(args.base_url, args.api_key, model, PROMPTS[task_id], args.temperature, args.max_tokens)
                code = extract_code(text)
                rec = {"model": model, "task": task_id, "sample": i,
                       "parse_ok": code is not None, "l1_ok": None, "l3_ok": None, "l3_failed": None, "error": None}
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
                print(f"[{model}] {task_id} #{i}: {rec['verdict']}")
                time.sleep(0.1)

    out_dir = STAGE1 / "eval" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    (out_dir / f"results_{ts}.json").write_text(
        json.dumps({"base": args.base_url, "models": models, "tasks": tasks,
                    "samples": args.samples, "temperature": args.temperature,
                    "results": results}, ensure_ascii=False, indent=1), encoding="utf-8")

    lines = [f"# 本地基线摘要（base={args.base_url}，temp={args.temperature}，n={args.samples}/对）", ""]
    lines.append("| 模型 | 任务 | pass@1 | parse_fail | L1_pass_L3_fail |")
    lines.append("|---|---|---|---|---|")
    per_model = {m: {"pass": 0, "total": 0, "tasks": {}} for m in models}
    for r in results:
        m = per_model[r["model"]]
        m["total"] += 1
        m["pass"] += 1 if r["verdict"] == "PASS" else 0
        t = m["tasks"].setdefault(r["task"], {"n": 0, "pass": 0, "no_code": 0, "l1_only": 0})
        t["n"] += 1
        t["pass"] += 1 if r["verdict"] == "PASS" else 0
        t["no_code"] += 1 if r["verdict"] == "NO_CODE" else 0
        t["l1_only"] += 1 if r["verdict"] == "L3_FAIL" else 0
    for model in models:
        tm = per_model[model]
        lines.append(f"| **{model}** | 全部 | **{tm['pass']/tm['total']:.0%}** | — | — |")
        for task_id in tasks:
            t = tm["tasks"][task_id]
            lines.append(f"| | {task_id} | {t['pass']/t['n']:.0%} | {t['no_code']/t['n']:.0%} | {t['l1_only']/t['n']:.0%} |")
    lines.append("")
    lines.append(f"耗时 {time.time()-t0:.0f}s。对照 eval/success_criteria.md 判定。")
    (out_dir / f"summary_{ts}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nresults -> {out_dir / f'results_{ts}.json'}\nsummary -> {out_dir / f'summary_{ts}.md'}")


if __name__ == "__main__":
    main()
