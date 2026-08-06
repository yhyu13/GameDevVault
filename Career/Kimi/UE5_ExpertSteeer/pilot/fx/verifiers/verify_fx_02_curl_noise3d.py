"""fx_02_curl_noise3d 验证器：L1 门禁 → L3 hidden tests（数值容差 1e-4 + divergence 性质）。

用法: python verify_fx_02_curl_noise3d.py --solution <path.py>
输出: 末行 RESULT <json>。
L2: 非配置类任务，无 L2 层（结果中 l2=None）。
期望值由 golden 预计算并硬编码（不与解共享代码）。
"""

import argparse
import importlib.util
import json
import os
import time

TOL = 1e-4
DIV_TOL = 1e-2  # 有限差分步长 1e-4 下的 divergence 数值噪声 ~1e-5，容差取 1e-2


def load_solution(path):
    spec = importlib.util.spec_from_file_location("fx02_solution", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def l1_gate(mod):
    problems = []
    if not callable(getattr(mod, "curl_noise3d", None)):
        problems.append("缺少函数 curl_noise3d")
    else:
        try:
            v = mod.curl_noise3d((0.1, 0.2, 0.3), 0.0)
            if not isinstance(v, (tuple, list)) or len(v) != 3 or not all(isinstance(x, (int, float)) for x in v):
                problems.append("curl_noise3d 必须返回 3 元组数值")
        except Exception as e:
            problems.append("curl_noise3d 调用异常: %s" % e)
    return problems


# 硬编码 golden 期望值（由 golden 预计算）
VALUE_CASES = [
    ("p=(0.3,0.7,0.2) t=0.0", (0.3, 0.7, 0.2), 0.0, (0.5221411308, -1.1468744115, 2.0423511095)),
    ("p=(1.1,-0.4,0.9) t=2.0", (1.1, -0.4, 0.9), 2.0, (2.2067505074, -3.3493523517, 3.7620677580)),
    ("p=(0,0,0) t=0.5", (0.0, 0.0, 0.0), 0.5, (-2.0816721902, -0.7915578656, -13.8991641125)),
    ("p=(3.7,2.9,-1.8) t=-1.25", (3.7, 2.9, -1.8), -1.25, (6.4357722364, -2.2936853908, 2.4879074241)),
]

DIV_POINTS = [((0.5, 0.5, 0.5), 1.0), ((1.7, -0.9, 0.3), 0.3)]


def _finite_diff_divergence(sol, p, t, h=1e-4):
    x, y, z = p
    vxp = sol((x + h, y, z), t)
    vxm = sol((x - h, y, z), t)
    vyp = sol((x, y + h, z), t)
    vym = sol((x, y - h, z), t)
    vzp = sol((x, y, z + h), t)
    vzm = sol((x, y, z - h), t)
    return (vxp[0] - vxm[0] + vyp[1] - vym[1] + vzp[2] - vzm[2]) / (2 * h)


def l3_execute(mod):
    """L3：数值比对（1e-4）+ divergence-free 性质（|div| <= 1e-2）。"""
    fails = []

    for name, p, t, expected in VALUE_CASES:
        try:
            got = mod.curl_noise3d(p, t)
        except Exception as e:
            fails.append("%s: 异常 %s" % (name, e))
            continue
        if not isinstance(got, (tuple, list)) or len(got) != 3:
            fails.append("%s: 返回类型错误 %r" % (name, got))
            continue
        for i in range(3):
            if abs(got[i] - expected[i]) > TOL:
                fails.append("%s: 分量[%d] 期望 %.8f 实际 %.8f" % (name, i, expected[i], got[i]))
                break

    for p, t in DIV_POINTS:
        try:
            d = _finite_diff_divergence(mod.curl_noise3d, p, t)
        except Exception as e:
            fails.append("divergence p=%s t=%s: 异常 %s" % (p, t, e))
            continue
        if abs(d) > DIV_TOL:
            fails.append("divergence 非零: p=%s t=%s div=%.4f (|div|<=%.0e)" % (p, t, d, DIV_TOL))
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solution", required=True)
    args = ap.parse_args()

    t0 = time.perf_counter()
    result = {"task": "fx_02_curl_noise3d", "solution": os.path.basename(args.solution),
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
    result["l3_total"] = len(VALUE_CASES) + len(DIV_POINTS)
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
