"""fx 域验证总驱动器：3 任务 × 4 解 × REPEATS 次（flakiness 测量）。

用法: python run_all.py [REPEATS]   （默认 3）
输出:
  1. reports/verification_results.json —— 全量实测数据（供报告引用）
  2. 控制台摘要表：每解 verdict、首次拦截层、墙钟时间 min/median/max、判定稳定性
"""

import glob
import json
import os
import statistics
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SOLS = os.path.join(ROOT, "solutions")
REPORTS = os.path.join(ROOT, "reports")
REPEATS = int(sys.argv[1]) if len(sys.argv) > 1 else 3

TASKS = [
    ("fx_01_niagara_config", "verify_fx_01_niagara_config.py"),
    ("fx_02_curl_noise3d", "verify_fx_02_curl_noise3d.py"),
    ("fx_03_flipbook_uv", "verify_fx_03_flipbook_uv.py"),
]


def run_verifier(verifier_path, solution_path):
    proc = subprocess.run(
        [sys.executable, verifier_path, "--solution", solution_path],
        capture_output=True, text=True, cwd=BASE, timeout=60)
    for line in proc.stdout.splitlines():
        if line.startswith("RESULT "):
            return json.loads(line[len("RESULT "):])
    return {"verdict": "ERROR", "first_fail_layer": None,
            "error": "verifier 无 RESULT 输出 rc=%d stderr=%s" % (proc.returncode, proc.stderr[-300:])}


def main():
    results = {}
    print("=== fx 域分层验证实测（REPEATS=%d）===" % REPEATS)
    for task, verifier_name in TASKS:
        verifier_path = os.path.join(BASE, verifier_name)
        sol_dir = os.path.join(SOLS, task)
        sols = sorted(glob.glob(os.path.join(sol_dir, "*.py")),
                      key=lambda p: os.path.basename(p) != "golden")  # golden 排最前
        task_results = []
        print("\n[%s]" % task)
        print("%-28s %-8s %-6s %-16s %s" % ("solution", "verdict", "layer", "time (min/med/max s)", "stable"))
        for sol in sols:
            name = os.path.splitext(os.path.basename(sol))[0]
            runs = [run_verifier(verifier_path, sol) for _ in range(REPEATS)]
            verdicts = [r.get("verdict") for r in runs]
            layers = [r.get("first_fail_layer") for r in runs]
            times = [r.get("time_s", 0.0) for r in runs]
            stable = len(set(verdicts)) == 1
            verdict = verdicts[0] if stable else "|".join(sorted(set(verdicts)))
            layer = layers[0] if len(set(layers)) == 1 else "|".join(sorted({str(x) for x in set(layers)}))
            entry = {
                "solution": name,
                "runs": runs,
                "verdict": verdict,
                "verdict_stable": stable,
                "first_fail_layer": layer,
                "time_min_s": min(times),
                "time_median_s": statistics.median(times),
                "time_max_s": max(times),
            }
            task_results.append(entry)
            print("%-28s %-8s %-6s %-16s %s" % (
                name, verdict, layer,
                "%.4f/%.4f/%.4f" % (min(times), statistics.median(times), max(times)),
                "yes" if stable else "NO"))
        results[task] = task_results

    with open(os.path.join(REPORTS, "verification_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n结果已写入 reports/verification_results.json")


if __name__ == "__main__":
    main()
