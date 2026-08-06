"""单解执行器：L1 门禁 -> L3 执行，输出 JSON 结果。

用法：python run_one.py <task_id> <solution_path>
输出（stdout 最后一行）：{"task", "solution", "l1": {ok, reasons}, "l3": {ok, passed, failed, failures, exec_ms}}

进程隔离设计：每个解在独立子进程运行——某个解崩溃/死循环不影响其余解，
与 CI 中"一作业一沙箱"的形态一致；墙钟成本在 verify_physics.py 侧测量。
"""
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # pilot/
sys.path.insert(0, str(ROOT / "base"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness import load_module_from_path, l1_gate, smoke_call  # noqa: E402
import task_bank  # noqa: E402


def main():
    task_id, sol_path = sys.argv[1], sys.argv[2]
    spec = task_bank.TASKS[task_id]
    source = Path(sol_path).read_text(encoding="utf-8")
    result = {
        "task": task_id,
        "solution": Path(sol_path).name,
        "l1": {"ok": None, "reasons": []},
        "l3": {"ok": None, "passed": 0, "failed": 0, "failures": [], "exec_ms": None},
    }

    # ---- L1：导入 + 语法 + API 表面检查 ----
    try:
        module = load_module_from_path("sol_" + task_id, sol_path)
    except Exception as exc:
        result["l1"] = {"ok": False, "reasons": [f"导入/语法失败：{type(exc).__name__}: {exc}"]}
        print(json.dumps(result))
        return

    ok, reasons = l1_gate(source, module, spec)
    if ok:
        try:
            ok, why = smoke_call(getattr(module, spec["fn"]), spec)
        except Exception as exc:
            ok, why = False, f"冒烟调用异常：{type(exc).__name__}: {exc}"
        if not ok:
            reasons.append(why)
    result["l1"] = {"ok": ok, "reasons": reasons}
    if not ok:
        print(json.dumps(result))
        return

    # ---- L3：hidden tests 全跑 ----
    fn = getattr(module, spec["fn"])
    passed = failed = 0
    failures = []
    t0 = time.perf_counter()
    for i, test in enumerate(spec["tests"], 1):
        try:
            ok, why = task_bank.check_test(fn, test)
        except Exception as exc:
            ok, why = False, f"执行异常：{type(exc).__name__}: {exc}"
        if ok:
            passed += 1
        else:
            failed += 1
            failures.append({"test": i, "note": test.get("note", ""), "why": why})
    exec_ms = (time.perf_counter() - t0) * 1000.0

    result["l3"] = {
        "ok": failed == 0,
        "passed": passed,
        "failed": failed,
        "failures": failures,
        "exec_ms": exec_ms,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        main()
    except Exception as exc:
        print(json.dumps({"crash": f"{type(exc).__name__}: {exc}", "trace": traceback.format_exc()[-2000:]}))
