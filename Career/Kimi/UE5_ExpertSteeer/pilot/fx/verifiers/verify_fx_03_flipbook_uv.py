"""fx_03_flipbook_uv 验证器：L1 门禁 → L3 hidden tests（行列整数值 + UV 矩形 1e-4）。

用法: python verify_fx_03_flipbook_uv.py --solution <path.py>
输出: 末行 RESULT <json>。
L2: 非配置类任务，无 L2 层（结果中 l2=None）。
"""

import argparse
import importlib.util
import json
import os
import time

TOL = 1e-4


def load_solution(path):
    spec = importlib.util.spec_from_file_location("fx03_solution", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def l1_gate(mod):
    problems = []
    for fn in ("flipbook_uv", "flipbook_uv_rect"):
        if not callable(getattr(mod, fn, None)):
            problems.append("缺少函数 %s" % fn)
    if not problems:
        try:
            r = mod.flipbook_uv(5, 4, 2, True)
            if not (isinstance(r, (tuple, list)) and len(r) == 2):
                problems.append("flipbook_uv 必须返回 (col, row)")
            r = mod.flipbook_uv_rect(5, 4, 2, True)
            if not (isinstance(r, (tuple, list)) and len(r) == 4):
                problems.append("flipbook_uv_rect 必须返回 (u0, v0, u1, v1)")
        except Exception as e:
            problems.append("API 调用异常: %s" % e)
    return problems


# (名称, 参数, 期望 (col,row)) —— 覆盖 0 帧、行/列边界、wrap 回卷、定格钳位、非方形网格
UV_CASES = [
    ("frame0 wrap", (0, 4, 2, True), (0, 0)),
    ("row0末列 wrap", (3, 4, 2, True), (3, 0)),
    ("row1首列 wrap", (4, 4, 2, True), (0, 1)),
    ("末帧 wrap", (7, 4, 2, True), (3, 1)),
    ("回卷首帧 wrap", (8, 4, 2, True), (0, 0)),
    ("回卷+1 wrap", (9, 4, 2, True), (1, 0)),
    ("越界1帧 clamp", (8, 4, 2, False), (3, 1)),
    ("大幅越界 clamp", (100, 4, 2, False), (3, 1)),
    ("非方形网格", (5, 3, 4, False), (2, 1)),
]

# (名称, 参数, 期望 (u0, v0, u1, v1))
RECT_CASES = [
    ("非方形网格 rect", (5, 3, 4, False), (2.0 / 3.0, 0.5, 1.0, 0.75)),
    ("wrap 末帧 rect", (11, 3, 4, True), (2.0 / 3.0, 0.0, 1.0, 0.25)),
    ("首帧 rect", (0, 3, 4, False), (0.0, 0.75, 1.0 / 3.0, 1.0)),
]


def l3_execute(mod):
    fails = []

    for name, args, expected in UV_CASES:
        try:
            got = mod.flipbook_uv(*args)
        except Exception as e:
            fails.append("%s: 异常 %s" % (name, e))
            continue
        if tuple(got) != expected:
            fails.append("%s: args=%s 期望 %s 实际 %s" % (name, args, expected, got))

    for name, args, expected in RECT_CASES:
        try:
            got = mod.flipbook_uv_rect(*args)
        except Exception as e:
            fails.append("%s: 异常 %s" % (name, e))
            continue
        for i in range(4):
            if abs(got[i] - expected[i]) > TOL:
                fails.append("%s: 分量[%d] 期望 %.6f 实际 %.6f" % (name, i, expected[i], got[i]))
                break
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solution", required=True)
    args = ap.parse_args()

    t0 = time.perf_counter()
    result = {"task": "fx_03_flipbook_uv", "solution": os.path.basename(args.solution),
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

    l3_fails = l3_execute(mod)
    result["l3_total"] = len(UV_CASES) + len(RECT_CASES)
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
