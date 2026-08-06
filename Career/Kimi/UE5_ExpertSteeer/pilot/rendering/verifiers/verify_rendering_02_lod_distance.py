"""rendering_02_lod_distance 验证器：L1 门禁（导入/语法/签名）→ L3 hidden tests。

用法: python verify_rendering_02_lod_distance.py --solution <path.py>
输出: 末行 RESULT <json>。
L2: 非配置类任务，无 L2 层（结果中 l2=None）。
期望 LOD 由 golden 预计算并硬编码（不与解共享代码）。
"""

import argparse
import importlib.util
import json
import os
import time

THRESHOLDS = [0.5, 0.2, 0.05]  # 3 级 LOD，降序

# (current_lod, screen_size, hysteresis, expected_lod) —— golden 预计算
CASES = [
    ("首帧 None 0.4", None, 0.4, 0.1, 1),
    ("首帧 None 0.8", None, 0.8, 0.1, 0),
    ("首帧 None 0.01", None, 0.01, 0.1, 2),
    ("L0 0.4 降级", 0, 0.4, 0.1, 1),
    ("L0 0.46 迟滞带内停留", 0, 0.46, 0.1, 0),
    ("L1 0.55 升级", 1, 0.55, 0.1, 0),
    ("L1 0.52 升级迟滞带内停留", 1, 0.52, 0.1, 1),
    ("L1 0.19 降级迟滞带内停留", 1, 0.19, 0.1, 1),
    ("L1 0.17 降级", 1, 0.17, 0.1, 2),
    ("L2 0.8 跨级升级", 2, 0.8, 0.1, 0),
    ("L2 0.06 保持", 2, 0.06, 0.1, 2),
    ("hyst=0 纯阈值 0.49", 0, 0.49, 0.0, 1),
    ("L2 0.04 末级", 2, 0.04, 0.1, 2),
]


def load_solution(path):
    spec = importlib.util.spec_from_file_location("r02_solution", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def l1_gate(mod):
    problems = []
    if not callable(getattr(mod, "select_lod", None)):
        problems.append("缺少函数 select_lod")
        return problems
    try:
        got = mod.select_lod(0, 0.4, THRESHOLDS, 0.1)
        if not isinstance(got, int):
            problems.append("select_lod 必须返回 int，实际 %r" % type(got))
    except Exception as e:
        problems.append("select_lod 调用异常: %s" % e)
    return problems


def l3_execute(mod):
    fails = []
    for name, cur, size, hyst, expected in CASES:
        try:
            got = mod.select_lod(cur, size, THRESHOLDS, hyst)
        except Exception as e:
            fails.append("%s: 异常 %s" % (name, e))
            continue
        if got != expected:
            fails.append("%s: 期望 LOD%d 实际 LOD%d" % (name, expected, got))
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solution", required=True)
    args = ap.parse_args()

    t0 = time.perf_counter()
    result = {"task": "rendering_02_lod_distance", "solution": os.path.basename(args.solution),
              "l1": False, "l2": None, "l3_passed": 0, "l3_total": 0,
              "verdict": "FAIL", "first_fail_layer": "L1", "time_s": 0.0}

    try:
        mod = load_solution(args.solution)
    except Exception as e:
        result["l1_error"] = str(e)[:200]
        print("RESULT " + json.dumps(result, ensure_ascii=False))
        return

    l1_problems = l1_gate(mod)
    if l1_problems:
        result["l1_error"] = "; ".join(l1_problems)
        print("RESULT " + json.dumps(result, ensure_ascii=False))
        return
    result["l1"] = True

    try:
        l3_fails = l3_execute(mod)
    except Exception as e:
        result["l3_error"] = ["执行异常: %s" % e]
        l3_fails = ["__exception__"]

    result["l3_total"] = len(CASES)
    result["l3_passed"] = result["l3_total"] - len(l3_fails)
    if l3_fails:
        result["l3_error"] = l3_fails
        result["first_fail_layer"] = "L3"
    else:
        result["verdict"] = "PASS"
        result["first_fail_layer"] = None
    result["time_s"] = time.perf_counter() - t0
    print("RESULT " + json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
