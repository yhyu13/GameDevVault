"""run_api_baseline —— Qwen 小模型 × 9 任务 API 基线评估（纯 stdlib，跨机器可跑）。

用法:
  python eval/run_api_baseline.py --selftest
  python eval/run_api_baseline.py --provider siliconflow --samples 10
  python eval/run_api_baseline.py --provider dashscope --models qwen3-0.6b --samples 5

环境变量: SILICONFLOW_API_KEY / DASHSCOPE_API_KEY（或 --api-key）
输出: eval/results/results_<ts>.json + summary_<ts>.md
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

from teacher_pool import POOL, TIER, PROMPTS, MODEL_SIZE, DOMAIN  # noqa: E402
import run_stage1 as rs  # noqa: E402  （复用 run_verifier）

SYSTEM = "你是 UE5 工程师。按任务要求输出完整、可直接运行的 Python 代码。只输出代码，不要任何解释、注释说明或多余文字。"
EXTRACT_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.S)

PROVIDERS = {
    "siliconflow": {
        "base": "https://api.siliconflow.cn/v1",
        "key_env": "SILICONFLOW_API_KEY",
        "models": ["Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B"],
    },
    "dashscope": {
        "base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "key_env": "DASHSCOPE_API_KEY",
        "models": ["qwen3-0.6b", "qwen3-1.7b", "qwen3-4b"],
    },
}


def chat(base, api_key, model, prompt, temperature, max_tokens, retries=4):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
        "temperature": temperature, "top_p": 0.9, "max_tokens": max_tokens,
    }).encode("utf-8")
    req = urllib.request.Request(
        base + "/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode("utf-8"))
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
    """写候选文件并跑分层验证器，返回逐层结果 dict。"""
    path = tmp_dir / f"{task_id.replace('/', '_')}_cand.py"
    path.write_text(code + "\n", encoding="utf-8")
    return rs.run_verifier(task_id, path)


def selftest():
    """环境自检：每任务取池内第一个 correct_high 候选，应 L1+L3 全过。"""
    ok = 0
    tmp = STAGE1 / "eval" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    for task_id, cands in POOL.items():
        name = sorted(cands.keys())[0]
        code = cands[name]
        r = run_sample(task_id, code, tmp)
        passed = r.get("l3_ok") is True
        ok += 1 if passed else 0
        print(f"[selftest] {task_id}/{name}: {'PASS' if passed else 'FAIL ' + str(r.get('error', r.get('l3_failures')))[:120]}")
    print(f"selftest {ok}/{len(POOL)} tasks passed")
    return ok == len(POOL)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=list(PROVIDERS), default="siliconflow")
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--samples", type=int, default=10)
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(0 if selftest() else 1)

    prov = PROVIDERS[args.provider]
    api_key = args.api_key or os.environ.get(prov["key_env"])
    if not api_key:
        sys.exit(f"缺少 API key：设置环境变量 {prov['key_env']} 或用 --api-key")
    models = args.models or prov["models"]
    tasks = args.tasks or list(POOL.keys())

    results = []
    tmp = STAGE1 / "eval" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    print(f"provider={args.provider} models={models} tasks={len(tasks)} samples={args.samples} temp={args.temperature}")
    t0 = time.time()
    for model in models:
        for task_id in tasks:
            for i in range(args.samples):
                text = chat(prov["base"], api_key, model, PROMPTS[task_id], args.temperature, args.max_tokens)
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
                print(f"[{model}] {task_id} #{i}: {rec['verdict']}"
                      + ("" if rec["verdict"] != "PASS" else "  (l3 all pass)"))
                time.sleep(0.3)

    out_dir = STAGE1 / "eval" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    (out_dir / f"results_{ts}.json").write_text(
        json.dumps({"provider": args.provider, "models": models, "tasks": tasks,
                    "samples": args.samples, "temperature": args.temperature,
                    "results": results}, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---- summary ----
    lines = [f"# API 基线摘要（{args.provider}，temp={args.temperature}，n={args.samples}/对）", ""]
    lines.append("| 模型 | 任务 | pass@1 | parse_fail | L1_pass_L3_fail |")
    lines.append("|---|---|---|---|---|")
    per_model = {}
    for model in models:
        per_model[model] = {"pass": 0, "total": 0, "tasks": {}}
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
    lines.append(f"耗时 {time.time()-t0:.0f}s。区分度判定见 eval_plan.md 成功标准表。")
    (out_dir / f"summary_{ts}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nresults -> {out_dir / f'results_{ts}.json'}\nsummary -> {out_dir / f'summary_{ts}.md'}")


if __name__ == "__main__":
    main()
