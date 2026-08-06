"""rendering_03_linear_srgb 验证器：L1 门禁（导入/语法/签名）→ L3 hidden tests。

用法: python verify_rendering_03_linear_srgb.py --solution <path.py>
输出: 末行 RESULT <json>。
L2: 非配置类任务，无 L2 层（结果中 l2=None）。
期望值由 golden 预计算并硬编码（IEC 61966-2-1 标准，不与解共享代码）。
"""

import argparse
import importlib.util
import json
import os
import time

TOL = 1e-4

# (输入 linear 三元组, 期望 sRGB 三元组) —— golden 预计算硬编码
VALUE_CASES = [
    ("0.5/0.1/0.25", (0.5, 0.1, 0.25), (0.7353569831, 0.3491902126, 0.5370987305)),
    ("暗部 0.001/0.0/阈值 0.0031308", (0.001, 0.0, 0.0031308), (0.0129200000, 0.0, 0.0404499360)),
    ("越界 Clamp 1.7/-0.3/0.0", (1.7, -0.3, 0.0), (1.0, 0.0, 0.0)),
    ("端点 1.0", (1.0, 1.0, 1.0), (1.0, 1.0, 1.0)),
]


def load_solution(path):
    spec = importlib.util.spec_from_file_location("r03_solution", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def l1_gate(mod):
    problems = []
    if not callable(getattr(mod, "linear_to_srgb", None)):
        problems.append("缺少函数 linear_to_srgb")
        return problems
    try:
        got = mod.linear_to_srgb((0.5, 0.1, 0.25))
        if not isinstance(got, (tuple, list)) or len(got) != 3 or \
                not all(isinstance(v, (int, float)) for v in got):
            problems.append("linear_to_srgb 必须返回 3 元组数值")
    except Exception as e:
        problems.append("linear_to_srgb 调用异常: %s" % e)
    return problems


def l3_execute(mod):
    fails = []
    for name, inp, expected in VALUE_CASES:
        try:
            got = mod.linear_to_srgb(inp)
        except Exception as e:
            fails.append("%s: 异常 %s" % (name, e))
            continue
        if not isinstance(got, (tuple, list)) or len(got) != 3:
            fails.append("%s: 返回类型错误 %r" % (name, got))
            continue
        for i in range(3):
            if abs(got[i] - expected[i]) > TOL:
                fails.append("%s: 通道[%d] 期望 %.8f 实际 %.8f (|diff|<=%.0e)"
                             % (name, i, expected[i], got[i], TOL))
                break
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solution", required=True)
    args = ap.parse_args()

    t0 = time.perf_counter()
    result = {"task": "rendering_03_linear_srgb", "solution": os.path.basename(args.solution),
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

    result["l3_total"] = len(VALUE_CASES)
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
