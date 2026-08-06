"""rendering 域验证总驱动器：3 任务 × 4 解 × REPEATS 次（flakiness 测量）+ L1 门禁自检。

用法: python run_all.py [REPEATS]   （默认 3）
输出:
  1. reports/verification_results.json —— 全量实测数据（供报告引用）
  2. 控制台摘要表：每解 verdict、首次拦截层、墙钟时间 min/median/max、判定稳定性
  3. L1 自检：临时注入语法错误文件/缺函数文件，确认 L1 门禁本身有效
"""

import glob
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SOLS = os.path.join(ROOT, "solutions")
REPORTS = os.path.join(ROOT, "reports")
REPEATS = int(sys.argv[1]) if len(sys.argv) > 1 else 3

TASKS = [
    ("rendering_01_frustum_cull", "verify_rendering_01_frustum_cull.py"),
    ("rendering_02_lod_distance", "verify_rendering_02_lod_distance.py"),
    ("rendering_03_linear_srgb", "verify_rendering_03_linear_srgb.py"),
]

SYNTAX_ERROR_BODY = "def broken(:\n    return 1\n"
MISSING_FUNC_BODY = "VALUE = 42\n"


def run_verifier(verifier_path, solution_path):
    proc = subprocess.run(
        [sys.executable, verifier_path, "--solution", solution_path],
        capture_output=True, text=True, cwd=BASE, timeout=60)
    for line in proc.stdout.splitlines():
        if line.startswith("RESULT "):
            return json.loads(line[len("RESULT "):])
    return {"verdict": "ERROR", "first_fail_layer": None,
            "error": "verifier 无 RESULT 输出 rc=%d stderr=%s" % (proc.returncode, proc.stderr[-300:])}


def l1_self_check():
    """门禁有效性自检：语法错误 / 缺函数 必须被 L1 拦截。"""
    checks = {}
    with tempfile.TemporaryDirectory() as td:
        bad_syntax = os.path.join(td, "bad_syntax.py")
        with open(bad_syntax, "w", encoding="utf-8") as f:
            f.write(SYNTAX_ERROR_BODY)
        missing_fn = os.path.join(td, "missing_fn.py")
        with open(missing_fn, "w", encoding="utf-8") as f:
            f.write(MISSING_FUNC_BODY)

        for task, verifier_name in TASKS:
            v = os.path.join(BASE, verifier_name)
            r_syntax = run_verifier(v, bad_syntax)
            ok_syntax = (r_syntax["verdict"] == "FAIL" and r_syntax["first_fail_layer"] == "L1")
            r_missing = run_verifier(v, missing_fn)
            ok_missing = (r_missing["verdict"] == "FAIL" and r_missing["first_fail_layer"] == "L1")
            checks[task] = {"syntax_error_blocked": ok_syntax, "missing_fn_blocked": ok_missing}
            print("L1 自检 [%s] 语法错误拦截=%s 缺函数拦截=%s" % (
                task, ok_syntax, ok_missing))
    return checks


def main():
    results = {}
    t_wall = time.perf_counter()
    print("=== rendering 域分层验证实测（REPEATS=%d）===" % REPEATS)
    l1_self_check()

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

    results["_meta"] = {"repeats": REPEATS, "wall_clock_s": time.perf_counter() - t_wall,
                        "python": sys.version.split()[0]}
    with open(os.path.join(REPORTS, "verification_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n总墙钟 %.2fs，结果已写入 reports/verification_results.json"
          % results["_meta"]["wall_clock_s"])


if __name__ == "__main__":
    main()
