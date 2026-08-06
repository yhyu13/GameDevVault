"""fx_01_niagara_config 验证器：L1 门禁 → L2 Schema 行为校验 → L3 hidden tests（容差 1e-4）。

用法: python verify_fx_01_niagara_config.py --solution <path.py>
输出: 末行 RESULT <json>，供 run_all.py 聚合。
L2 说明: 本任务是配置类任务。L2 即"Schema 校验层"——校验器对缺字段/越界/预算超限
输入的标记行为（外部 Schema 校验器在真实管线中的等价物）。
"""

import argparse
import importlib.util
import json
import os
import time

TOL = 1e-4


def load_solution(path):
    spec = importlib.util.spec_from_file_location("fx01_solution", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def l1_gate(mod):
    """L1：导入/语法门禁 + API 表面检查（函数存在、返回结构符合契约）。"""
    problems = []
    for fn in ("validate_niagara_config", "compute_niagara_budget"):
        if not callable(getattr(mod, fn, None)):
            problems.append("缺少函数 %s" % fn)
    if not problems:
        try:
            r = mod.validate_niagara_config(
                {"emitter_name": "e", "spawn_rate": 10.0, "particle_lifetime": 1.0,
                 "max_particles": 100, "bytes_per_particle": 64})
            if not isinstance(r, dict) or not all(k in r for k in ("valid", "errors", "peak_particles", "memory_bytes")):
                problems.append("validate_niagara_config 返回结构不符合契约")
        except Exception as e:
            problems.append("validate_niagara_config 调用异常: %s" % e)
    return problems


L2_CASES = [
    ("missing_lifetime", {"emitter_name": "e", "spawn_rate": 10.0, "max_particles": 100, "bytes_per_particle": 64}),
    ("negative_rate", {"emitter_name": "e", "spawn_rate": -5.0, "particle_lifetime": 2.0, "max_particles": 100, "bytes_per_particle": 64}),
    ("budget_overflow", {"emitter_name": "e", "spawn_rate": 1000.0, "particle_lifetime": 50.0, "max_particles": 10000, "bytes_per_particle": 64}),
    ("valid", {"emitter_name": "e", "spawn_rate": 10.0, "particle_lifetime": 2.0, "max_particles": 100, "bytes_per_particle": 64}),
]
L2_EXPECT_VALID = {3}  # 仅第 4 例应 valid=True


def l2_schema(mod):
    """L2：Schema 行为——缺字段/越界值/预算超限必须被标记，合法配置必须放行。"""
    fails = []
    for i, (name, cfg) in enumerate(L2_CASES):
        r = mod.validate_niagara_config(cfg)
        if r["valid"] == (i in L2_EXPECT_VALID):
            continue
        fails.append("%s: 期望 valid=%s 实际 %s (errors=%s)" % (
            name, i in L2_EXPECT_VALID, r["valid"], r["errors"][:2]))
    return fails


def _near(a, b):
    return abs(a - b) <= TOL


def l3_execute(mod):
    """L3：hidden tests——数值容差 1e-4（预算数学 + 有效配置集成值 + 结构性标志）。"""
    fails = []

    cases = [
        ("compute(100,3,64)", lambda s: s.compute_niagara_budget(100.0, 3.0, 64),
         (300.0, 19200.0), "tuple"),
        ("compute(150.5,2.3,128)", lambda s: s.compute_niagara_budget(150.5, 2.3, 128),
         (150.5 * 2.3, (150.5 * 2.3) * 128), "tuple"),
        ("compute(10000,10,4096)", lambda s: s.compute_niagara_budget(10000.0, 10.0, 4096),
         (100000.0, 409600000.0), "tuple"),
        ("validate(rate=150.5,lifetime=2.3) 峰值", lambda s: s.validate_niagara_config(
            {"emitter_name": "e", "spawn_rate": 150.5, "particle_lifetime": 2.3,
             "max_particles": 10000, "bytes_per_particle": 128})["peak_particles"],
         150.5 * 2.3, "float"),
        ("validate(rate=150.5,lifetime=2.3) 内存", lambda s: s.validate_niagara_config(
            {"emitter_name": "e", "spawn_rate": 150.5, "particle_lifetime": 2.3,
             "max_particles": 10000, "bytes_per_particle": 128})["memory_bytes"],
         (150.5 * 2.3) * 128, "float"),
        ("validate 缺字段必须报错", lambda s: s.validate_niagara_config(
            {"emitter_name": "e", "spawn_rate": 10.0, "max_particles": 100,
             "bytes_per_particle": 64})["valid"], False, "bool"),
        ("validate 内存超限必须报错", lambda s: s.validate_niagara_config(
            {"emitter_name": "e", "spawn_rate": 1000.0, "particle_lifetime": 100.0,
             "max_particles": 200000, "bytes_per_particle": 4096})["valid"], False, "bool"),
    ]
    for name, fn, expected, kind in cases:
        try:
            got = fn(mod)
        except Exception as e:
            fails.append("%s: 异常 %s" % (name, e))
            continue
        if kind == "tuple":
            ok = isinstance(got, (tuple, list)) and len(got) == 2 and _near(got[0], expected[0]) and _near(got[1], expected[1])
        elif kind == "float":
            ok = _near(got, expected)
        else:
            ok = bool(got) == expected
        if not ok:
            fails.append("%s: 期望 %s 实际 %s" % (name, expected, got))
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solution", required=True)
    args = ap.parse_args()

    t0 = time.perf_counter()
    result = {"task": "fx_01_niagara_config", "solution": os.path.basename(args.solution),
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

    l2_fails = l2_schema(mod)
    result["l2"] = len(l2_fails) == 0
    if l2_fails:
        result["l2_error"] = l2_fails
        result["first_fail_layer"] = "L2"
        print("RESULT " + json.dumps(result, ensure_ascii=False))
        return

    l3_fails = l3_execute(mod)
    result["l3_total"] = 7
    result["l3_passed"] = 7 - len(l3_fails)
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
