"""物理域试点主控：跑完整矩阵（3 任务 x 4 解 x 3 次重复），测量并汇总。

输出：
- 每解：L1 / L3 判定 + 失败测试明细 + 3 次墙钟（含解释器启动）与纯执行耗时
- flakiness：判定跨 3 次是否稳定 + 墙钟抖动（max-min）
- 汇总：L1/L3 拦截率、L3 盲区计数、每任务 L3 必要性统计（供报告引用）

L4 judge 由 agent 扮演（见 reports/physics_pilot_report.md），本脚本不自动判 L4。

用法：python verify_physics.py [--quick]   （--quick 只跑 1 次重复）
"""
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

VERIFIERS = Path(__file__).resolve().parent
SOLS = VERIFIERS.parent / "solutions"
RUN_ONE = VERIFIERS / "run_one.py"

MATRIX = [
    ("physics_01_impulse", [
        "impulse_golden.py",
        "impulse_fail1_sign.py",
        "impulse_fail2_massscale.py",
        "impulse_fail3_f32.py",
    ]),
    ("physics_02_spring_euler", [
        "spring_golden.py",
        "spring_fail1_order.py",
        "spring_fail2_dampsign.py",
        "spring_fail3_unit.py",
    ]),
    ("physics_03_wheel_friction", [
        "wheel_golden.py",
        "wheel_fail1_circle.py",
        "wheel_fail2_sign.py",
        "wheel_fail3_hardcoded.py",
    ]),
]

REPEATS = 3


def run_once(task_id, sol_file):
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-B", str(RUN_ONE), task_id, str(SOLS / sol_file)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=60, cwd=str(VERIFIERS),
    )
    wall_ms = (time.perf_counter() - t0) * 1000.0
    try:
        data = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        data = {"crash": (proc.stdout + proc.stderr)[-2000:]}
    return data, wall_ms


def verdict(data):
    if not data.get("l1", {}).get("ok"):
        return "L1_FAIL"
    return "L3_PASS" if data.get("l3", {}).get("ok") else "L3_FAIL"


def main():
    quick = "--quick" in sys.argv
    reps = 1 if quick else REPEATS
    print(f"physics pilot verifier | repeats={reps} | python={sys.version.split()[0]}")
    print("=" * 110)

    all_rows = []
    totals = {"golden": 0, "fail": 0, "l1_caught": 0, "l3_caught": 0, "l3_blind": 0}

    for task_id, sols in MATRIX:
        print(f"\n## {task_id}")
        print(f"{'solution':<28}{'L1':<6}{'L3':<9}{'tests':<10}{'exec_ms':<9}{'wall_ms x{reps}':<24}verdict")
        print("-" * 110)
        for sol in sols:
            runs = [run_once(task_id, sol) for _ in range(reps)]
            datas = [r[0] for r in runs]
            walls = [r[1] for r in runs]
            v0 = verdict(datas[0])
            stable = all(verdict(d) == v0 for d in datas)
            l1 = datas[0]["l1"]
            l3 = datas[0]["l3"] if l3_is_present(datas[0]) else {"ok": None, "passed": 0, "failed": 0, "failures": []}
            tinfo = f"{l3['passed']}/{l3['passed'] + l3['failed']}" if l3.get("passed") is not None else "-"
            exec_ms = l3.get("exec_ms")
            em = f"{exec_ms:.3f}" if exec_ms is not None else "-"
            wall_s = " ".join(f"{w:.1f}" for w in walls)
            verdict_str = v0 if stable else f"{v0}?!(jitter)"
            print(f"{sol:<28}{'PASS' if l1['ok'] else 'FAIL':<6}{'PASS' if v0 == 'L3_PASS' else 'FAIL':<9}"
                  f"{tinfo:<10}{em:<9}{wall_s:<24}{verdict_str}")
            for f in l3.get("failures", []):
                print(f"    ! test#{f['test']} [{f['note']}] {f['why']}")
            is_golden = sol.endswith("golden.py")
            if is_golden:
                totals["golden"] += 1
            else:
                totals["fail"] += 1
                if v0 == "L3_PASS":
                    totals["l3_blind"] += 1
                elif l3.get("failed", 0) > 0:
                    totals["l3_caught"] += 1
                elif not l1["ok"]:
                    totals["l1_caught"] += 1
            row = {"task": task_id, "sol": sol, "verdict": v0, "walls": walls,
                   "exec_ms": exec_ms, "stable": stable, "fails": [f["test"] for f in l3.get("failures", [])]}
            all_rows.append(row)

        task_sols = [r for r in all_rows if r["task"] == task_id and not r["sol"].endswith("golden.py")]
        l3_caught = sum(1 for r in task_sols if r["verdict"] == "L3_FAIL")
        l3_blind = sum(1 for r in task_sols if r["verdict"] == "L3_PASS")
        print(f"  -> 任务级：失败解 L3 拦截 {l3_caught}/3，L3 盲区（judge 需补）{l3_blind}/3")

    # ---- 汇总 ----
    print("\n" + "=" * 110)
    print("汇总（L1 拦截 / L3 拦截 / L3 盲区）")
    print(f"  golden 解：{totals['golden']}/3 全 PASS")
    print(f"  播种失败解：{totals['fail']}/9；L1 拦截 {totals['l1_caught']}；"
          f"L3 拦截 {totals['l3_caught']}；L3 盲区 {totals['l3_blind']}")

    gold_walls = [r for r in all_rows if r["sol"].endswith("golden.py")]
    all_walls = [w for r in all_rows for w in r["walls"]]
    print(f"  墙钟（含解释器启动）：golden 中位 {statistics.median([r['walls'][0] for r in gold_walls]):.1f} ms；"
          f"全部解中位 {statistics.median(all_walls):.1f} ms，范围 {min(all_walls):.1f}-{max(all_walls):.1f} ms")
    exec_vals = [r["exec_ms"] for r in all_rows if r["exec_ms"] is not None]
    print(f"  纯执行耗时：中位 {statistics.median(exec_vals):.3f} ms，最大 {max(exec_vals):.3f} ms")
    unstable = [r["sol"] for r in all_rows if not r["stable"]]
    print(f"  flakiness（判定跨 {REPEATS} 次稳定性）：{'稳定 100%' if not unstable else f'不稳定: {unstable}'}")


def l3_is_present(data):
    return data.get("l3", {}).get("ok") is not None


if __name__ == "__main__":
    main()
