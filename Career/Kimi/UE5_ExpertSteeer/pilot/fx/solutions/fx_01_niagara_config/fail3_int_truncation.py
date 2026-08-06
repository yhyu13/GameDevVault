"""播种失败解 3：compute_niagara_budget 用 int() 截断，丢失浮点精度。

失败簇类型：粒子寿命数学错（精度/取整）。校验逻辑（缺字段/范围/预算规则）完全正确，
但预算计算对非整数乘积截断，如 150.5×2.3=346.15 被算成 346，单粒子内存随之偏差。
"""

DEFAULT_MEMORY_BUDGET_BYTES = 64 * 1024 * 1024

REQUIRED_FIELDS = {
    "emitter_name": "str",
    "spawn_rate": "float",
    "particle_lifetime": "float",
    "max_particles": "int",
    "bytes_per_particle": "int",
}

RANGE_CHECKS = [
    ("spawn_rate", 0.0, 1_000_000.0, False),
    ("particle_lifetime", 0.0, 60.0, False),
    ("max_particles", 1, 10_000_000, True),
    ("bytes_per_particle", 16, 4096, True),
]


def compute_niagara_budget(spawn_rate, particle_lifetime, bytes_per_particle):
    peak = int(float(spawn_rate) * float(particle_lifetime))
    memory = int(peak * float(bytes_per_particle))
    return float(peak), float(memory)


def validate_niagara_config(cfg):
    if not isinstance(cfg, dict):
        return {"valid": False, "errors": ["cfg 必须是 JSON 对象"], "peak_particles": 0.0, "memory_bytes": 0.0}

    errors = []

    for field, ftype in REQUIRED_FIELDS.items():
        if field not in cfg:
            errors.append("缺少必填字段: %s" % field)
            continue
        v = cfg[field]
        if ftype == "str":
            if not isinstance(v, str) or not v.strip():
                errors.append("%s 必须是非空字符串" % field)
        elif ftype == "int":
            if isinstance(v, bool) or not isinstance(v, int):
                errors.append("%s 必须是 int" % field)
        else:
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                errors.append("%s 必须是 float" % field)

    if errors:
        return {"valid": False, "errors": errors, "peak_particles": 0.0, "memory_bytes": 0.0}

    for field, lo, hi, inclusive in RANGE_CHECKS:
        v = cfg[field]
        ok = lo <= v <= hi if inclusive else lo < v < hi
        if not ok:
            errors.append("%s=%s 超出范围 (%s, %s]" % (field, v, lo, hi))

    peak = memory = 0.0
    if not errors:
        peak, memory = compute_niagara_budget(
            cfg["spawn_rate"], cfg["particle_lifetime"], cfg["bytes_per_particle"]
        )
        if peak > cfg["max_particles"]:
            errors.append("峰值粒子数 %.1f 超过 max_particles=%d，发射器会丢粒子" % (peak, cfg["max_particles"]))
        if memory > DEFAULT_MEMORY_BUDGET_BYTES:
            errors.append("内存预算 %.0f 字节超过默认上限 %d (64 MiB)" % (memory, DEFAULT_MEMORY_BUDGET_BYTES))

    return {"valid": len(errors) == 0, "errors": errors, "peak_particles": peak, "memory_bytes": memory}
