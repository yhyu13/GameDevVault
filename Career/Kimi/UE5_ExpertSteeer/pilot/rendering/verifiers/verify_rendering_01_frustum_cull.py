"""rendering_01_frustum_cull 验证器：L1 门禁（导入/语法/签名+API 表面）→ L3 hidden tests。

用法: python verify_rendering_01_frustum_cull.py --solution <path.py>
输出: 末行 RESULT <json>。
L2: 非配置类任务，无 L2 层（结果中 l2=None）。
期望平面值/判定由 golden 预计算并硬编码（不与解共享代码）。
"""

import argparse
import importlib.util
import json
import os
import time

PLANE_TOL = 1e-4

# 由 golden 预计算并硬编码（不与解共享代码）
CANONICAL_PLANES = [
    (0.0000000000, 1.0000000000, 0.0000000000, -1.0000000000),
    (-0.0000000000, -1.0000000000, -0.0000000000, 100.0000000000),
    (0.6000000000, 0.8000000000, 0.0000000000, -0.0000000000),
    (-0.6000000000, 0.8000000000, 0.0000000000, -0.0000000000),
    (0.0000000000, 0.7071067812, 0.7071067812, -0.0000000000),
    (0.0000000000, 0.7071067812, -0.7071067812, -0.0000000000),
]
ROTATED_PLANES = [
    (0.0000000000, 0.0000000000, -1.0000000000, -0.0000000000),
    (-0.0000000000, -0.0000000000, 1.0000000000, 39.5000000000),
    (0.6546536707, 0.0000000000, -0.7559289460, -0.9313428684),
    (-0.6546536707, 0.0000000000, -0.7559289460, 1.6872718144),
    (0.0000000000, 0.8660254038, -0.5000000000, 1.1160254038),
    (0.0000000000, -0.8660254038, -0.5000000000, -0.6160254038),
]

CANONICAL_ARGS = ((0, 0, 0), (0, 1, 0), (0, 0, 1), 90.0, 4.0 / 3.0, 1.0, 100.0)
ROTATED_ARGS = ((2.0, -1.0, 0.5), (0, 0, -1), (0, 1, 0), 60.0, 2.0, 0.5, 40.0)

# (point, radius, expected) —— 判定由 golden 预计算
POINT_CASES = [
    ("canonical (0,2,0)", (0, 2, 0), 0.0, True),
    ("canonical (0,50,0)", (0, 50, 0), 0.0, True),
    ("canonical (0,150,0) far 外", (0, 150, 0), 0.0, False),
    ("canonical (0,-5,0) near 后", (0, -5, 0), 0.0, False),
    ("canonical (10,2,0) 右外", (10, 2, 0), 0.0, False),
    ("canonical (2.6,2,0) 右内", (2.6, 2, 0), 0.0, True),
    ("canonical (2.8,2,0) 右外", (2.8, 2, 0), 0.0, False),
    ("canonical (0,2,1.5) 上内", (0, 2, 1.5), 0.0, True),
    ("canonical (0,2,2.5) 上外", (0, 2, 2.5), 0.0, False),
    ("canonical (0,5,4.5) 上内", (0, 5, 4.5), 0.0, True),
    ("rotated (2,-1,0.4) near 前", (2, -1, 0.4), 0.0, False),
    ("rotated (2,-1,-5) 内", (2, -1, -5), 0.0, True),
    ("rotated (10,-1,-5) 右外", (10, -1, -5), 0.0, False),
    ("rotated (2,3,-5) 上外", (2, 3, -5), 0.0, False),
    ("rotated (2,-1,-39.4) far 内", (2, -1, -39.4), 0.0, True),
    ("rotated (2,-1,-39.6) far 外", (2, -1, -39.6), 0.0, False),
    ("rotated (2,-4,-5) 内", (2, -4, -5), 0.0, True),
]
SPHERE_CASES = [
    ("球心右外 r=0.5 相交", (3.0, 2, 0), 0.5, True),
    ("球心 near 前 r=0.6 相交", (0, 0.5, 0), 0.6, True),
    ("球 far 外 r=5 剔除", (0, 150, 0), 5.0, False),
    ("大球 r=20 全相交", (10, 2, 0), 20.0, True),
]


def load_solution(path):
    spec = importlib.util.spec_from_file_location("r01_solution", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def l1_gate(mod):
    problems = []
    for fn in ("build_frustum_planes", "point_inside_frustum"):
        if not callable(getattr(mod, fn, None)):
            problems.append("缺少函数 %s" % fn)
    if problems:
        return problems
    try:
        planes = mod.build_frustum_planes(*CANONICAL_ARGS)
        if not isinstance(planes, (list, tuple)) or len(planes) != 6:
            problems.append("build_frustum_planes 必须返回 6 个平面")
        else:
            for i, p in enumerate(planes):
                if not isinstance(p, (list, tuple)) or len(p) != 4 or \
                        not all(isinstance(v, (int, float)) for v in p):
                    problems.append("平面[%d] 必须是 (nx,ny,nz,d) 四元组" % i)
        ok = mod.point_inside_frustum(planes, (0.0, 2.0, 0.0), 0.0)
        if not isinstance(ok, bool):
            problems.append("point_inside_frustum 必须返回 bool")
    except Exception as e:
        problems.append("API 表面调用异常: %s" % e)
    return problems


def _planes_close(a, b, tol):
    return all(abs(a[i][j] - b[i][j]) <= tol for i in range(6) for j in range(4))


def l3_execute(mod):
    """L3：平面系数比对（1e-4）+ 点/球判定比对。"""
    fails = []

    planes_c = mod.build_frustum_planes(*CANONICAL_ARGS)
    planes_r = mod.build_frustum_planes(*ROTATED_ARGS)
    if not _planes_close(planes_c, CANONICAL_PLANES, PLANE_TOL):
        fails.append("canonical 平面系数偏差 > 1e-4")
    if not _planes_close(planes_r, ROTATED_PLANES, PLANE_TOL):
        fails.append("rotated 平面系数偏差 > 1e-4")

    for name, p, r, expected in POINT_CASES:
        got = mod.point_inside_frustum(planes_c if name.startswith("canonical") else planes_r, p, r)
        if got != expected:
            fails.append("%s: 期望 %s 实际 %s" % (name, expected, got))
    for name, p, r, expected in SPHERE_CASES:
        got = mod.point_inside_frustum(planes_c, p, r)
        if got != expected:
            fails.append("%s: 期望 %s 实际 %s" % (name, expected, got))
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solution", required=True)
    args = ap.parse_args()

    t0 = time.perf_counter()
    result = {"task": "rendering_01_frustum_cull", "solution": os.path.basename(args.solution),
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

    result["l3_total"] = 2 + len(POINT_CASES) + len(SPHERE_CASES)
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
