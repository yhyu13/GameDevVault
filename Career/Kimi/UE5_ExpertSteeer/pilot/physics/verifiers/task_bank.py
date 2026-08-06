"""L3 hidden tests 注册表（pilot/physics）。

每个任务一组测试，全部为确定性输入/输出对（容差 1e-4 = FMath::IsNearlyEqual 的
KINDA_SMALL_NUMBER 级别）或不变量运行器。期望值由 golden 公式闭式独立计算，
验证器不与解共享实现，避免同义反复。

不变量测试（spring_run）驱动解函数逐帧跑 N 步，断言：
  1) 每步能量 E = 0.5*m*v^2 + 0.5*k*(x-rest)^2 不超过 E0 * 1.5（能量有界）
  2) 末态收敛到 rest 附近（不漂移、不发散）
用 `not (e <= bound)` 判断以同时捕获 NaN（NaN 比较为 False 会漏判）。
"""
from fvector_stub import FVector

TOL = 1e-4


def _vec_close(a, b, tol=TOL):
    return (abs(a.x - b.x) <= tol and abs(a.y - b.y) <= tol and abs(a.z - b.z) <= tol)


def run_spring_invariant(fn, p):
    k, c, rest, m, dt = p["k"], p["c"], p["rest"], p["m"], p["dt"]
    x, v = p["x0"], p["v0"]
    e0 = 0.5 * m * v * v + 0.5 * k * (x - rest) ** 2
    if e0 == 0.0:
        e0 = 1.0  # 静止在平衡点：能量恒为 0，用归一化基准
    for _ in range(p["steps"]):
        x, v = fn(x, v, k, c, rest, m, dt)
        e = 0.5 * m * v * v + 0.5 * k * (x - rest) ** 2
        if not (e <= e0 * 1.5):
            return False, f"第 {_ + 1} 步能量越界 E/E0={e / e0:.3g}"
    if not (abs(x - rest) <= p["x_tol"] and abs(v) <= p["v_tol"]):
        return False, f"未收敛 x={x:.6g} v={v:.6g}"
    return True, ""


TASKS = {
    "physics_01_impulse": {
        "fn": "resolve_impulse",
        "params": ["m_a", "m_b", "v_a", "v_b", "normal", "restitution"],
        "smoke": {"args": (1, 1, FVector(0, 0, 0), FVector(0, 0, 0), FVector(1, 0, 0), 0.5),
                  "returns": "vector_pair"},
        "tests": [
            {"type": "literal", "kind": "vector_pair", "tol": TOL, "note": "e=1 弹性对撞：速度完全交换",
             "args": (1, 1, FVector(-100, 0, 0), FVector(100, 0, 0), FVector(1, 0, 0), 1.0),
             "expected": (FVector(100, 0, 0), FVector(-100, 0, 0))},
            {"type": "literal", "kind": "vector_pair", "tol": TOL, "note": "e=0 完全非弹性：黏在一起",
             "args": (1, 1, FVector(-100, 0, 0), FVector(100, 0, 0), FVector(1, 0, 0), 0.0),
             "expected": (FVector(0, 0, 0), FVector(0, 0, 0))},
            {"type": "literal", "kind": "vector_pair", "tol": TOL, "note": "质量悬殊：约化质量主导",
             "args": (1, 1000, FVector(-100, 0, 0), FVector(0, 0, 0), FVector(1, 0, 0), 0.5),
             "expected": (FVector(49.85014985014985, 0, 0), FVector(-0.14985014985014986, 0, 0))},
            {"type": "literal", "kind": "vector_pair", "tol": TOL, "note": "斜碰：切向速度保持",
             "args": (2, 3, FVector(-50, 50, 0), FVector(10, 20, 0),
                      FVector(0.7071067811865475, 0.7071067811865475, 0), 0.7),
             "expected": (FVector(-34.7, 65.3, 0), FVector(-0.2, 9.8, 0))},
            {"type": "literal", "kind": "vector_pair", "tol": TOL, "note": "分离情形：不施加冲量",
             "args": (1, 1, FVector(100, 0, 0), FVector(-100, 0, 0), FVector(1, 0, 0), 0.9),
             "expected": (FVector(100, 0, 0), FVector(-100, 0, 0))},
            {"type": "literal", "kind": "vector_pair", "tol": TOL, "note": "纯切向：法向分量为 0",
             "args": (1, 1, FVector(0, 50, 0), FVector(0, 0, 0), FVector(1, 0, 0), 0.5),
             "expected": (FVector(0, 50, 0), FVector(0, 0, 0))},
            {"type": "literal", "kind": "vector_pair", "tol": TOL,
             "note": "高速斜碰 1e5 cm/s（非整数法线分量）：float32 截断在此量级产生 >1e-4 误差",
             "args": (1, 1, FVector(-100000, -100000, 0), FVector(100000, 100000, 0),
                      FVector(0.7071067811865475, 0.7071067811865475, 0), 0.5),
             "expected": (FVector(50000, 50000, 0), FVector(-50000, -50000, 0))},
        ],
    },

    "physics_02_spring_euler": {
        "fn": "spring_step",
        "params": ["x", "v", "k", "c", "rest", "m", "dt"],
        "smoke": {"args": (1.0, 0.0, 10.0, 0.5, 1.0, 1.0, 0.01), "returns": "float_pair"},
        "tests": [
            {"type": "literal", "kind": "float_pair", "tol": TOL, "note": "平衡点静止：不动",
             "args": (1.0, 0.0, 10.0, 0.5, 1.0, 1.0, 0.02),
             "expected": (1.0, 0.0)},
            {"type": "literal", "kind": "float_pair", "tol": TOL, "note": "单步：v'=a*dt, x'=x+v'*dt（半隐式关键）",
             "args": (0.0, 0.0, 10.0, 0.5, 1.0, 1.0, 0.02),
             "expected": (0.004, 0.2)},
            {"type": "literal", "kind": "float_pair", "tol": TOL, "note": "m=2：a=F/m 不可漏除",
             "args": (2.0, 1.0, 10.0, 0.5, 1.0, 2.0, 0.02),
             "expected": (2.0179, 0.895)},
            {"type": "invariant", "kind": "spring_run", "note": "200 步能量有界 + 收敛（k=100 欠阻尼）",
             "params": {"k": 100.0, "c": 2.0, "rest": 1.0, "m": 1.0, "dt": 0.05,
                        "x0": 0.0, "v0": 0.0, "steps": 200, "x_tol": 0.05, "v_tol": 0.5}},
            {"type": "invariant", "kind": "spring_run", "note": "大 dt=0.1 仍收敛（dt 尺度鲁棒性）",
             "params": {"k": 10.0, "c": 1.0, "rest": 1.0, "m": 1.0, "dt": 0.1,
                        "x0": 0.0, "v0": 0.0, "steps": 100, "x_tol": 0.15, "v_tol": 0.5}},
        ],
    },

    "physics_03_wheel_friction": {
        "fn": "wheel_longitudinal_force",
        "params": ["slip", "fz", "fy", "mu", "ks"],
        "smoke": {"args": (0.1, 500.0, 0.0, 1.0, 1000.0), "returns": "float"},
        "tests": [
            {"type": "literal", "kind": "float", "tol": TOL, "note": "纯纵向：ks*slip 未超预算",
             "args": (0.3, 1000.0, 0.0, 1.0, 2000.0), "expected": 600.0},
            {"type": "literal", "kind": "float", "tol": TOL, "note": "纵向 clamp 上限",
             "args": (0.9, 1000.0, 0.0, 1.0, 2000.0), "expected": 1000.0},
            {"type": "literal", "kind": "float", "tol": TOL, "note": "纵向 clamp 下限（制动符号）",
             "args": (-0.9, 1000.0, 0.0, 1.0, 2000.0), "expected": -1000.0},
            {"type": "literal", "kind": "float", "tol": TOL, "note": "摩擦圆耦合：Fy 占用后预算=600",
             "args": (0.9, 1000.0, 800.0, 1.0, 2000.0), "expected": 600.0},
            {"type": "literal", "kind": "float", "tol": TOL, "note": "抓地耗尽：Fy==mu*Fz",
             "args": (0.9, 1000.0, 1000.0, 1.0, 2000.0), "expected": 0.0},
            {"type": "literal", "kind": "float", "tol": TOL, "note": "Fy>mu*Fz：sqrt 负值必须安全为 0",
             "args": (0.9, 1000.0, 1200.0, 1.0, 2000.0), "expected": 0.0},
            {"type": "literal", "kind": "float", "tol": TOL, "note": "零载荷：无接触返回 0",
             "args": (0.5, 0.0, 0.0, 1.0, 2000.0), "expected": 0.0},
            {"type": "literal", "kind": "float", "tol": TOL, "note": "负载荷守卫",
             "args": (0.5, -100.0, 0.0, 1.0, 2000.0), "expected": 0.0},
            {"type": "literal", "kind": "float", "tol": TOL, "note": "制动符号保持",
             "args": (-0.3, 1000.0, 0.0, 1.0, 2000.0), "expected": -600.0},
            {"type": "literal", "kind": "float", "tol": TOL, "note": "mu 缩放：预算=mu*Fz=1000",
             "args": (0.5, 2000.0, 0.0, 0.5, 3000.0), "expected": 1000.0},
            {"type": "literal", "kind": "float", "tol": TOL, "note": "混合参数：小 slip 不触预算",
             "args": (0.15, 800.0, 100.0, 1.2, 2500.0), "expected": 375.0},
        ],
    },
}


def check_test(fn, test):
    """执行单个 hidden test，返回 (ok, 失败说明)。"""
    if test["type"] == "literal":
        out = fn(*test["args"])
        tol = test.get("tol", TOL)
        kind = test["kind"]
        if kind == "vector_pair":
            ok = (isinstance(out, tuple) and len(out) == 2
                  and _vec_close(out[0], test["expected"][0], tol)
                  and _vec_close(out[1], test["expected"][1], tol))
        elif kind == "float_pair":
            ok = (isinstance(out, tuple) and len(out) == 2
                  and abs(out[0] - test["expected"][0]) <= tol
                  and abs(out[1] - test["expected"][1]) <= tol)
        else:
            ok = isinstance(out, (int, float)) and abs(out - test["expected"]) <= tol
        return ok, "" if ok else f"期望 {test['expected']} 实际 {out}"
    if test["type"] == "invariant":
        return run_spring_invariant(fn, test["params"])
    return False, f"未知测试类型 {test['type']}"
