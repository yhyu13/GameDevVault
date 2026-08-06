"""播种失败解 1：漏检必填字段 particle_lifetime（缺字段直接放行）。

失败簇类型：配置缺字段检查遗漏。REQUIRED_FIELDS 中漏掉 particle_lifetime，
后续用 cfg.get 兜底成 0，导致缺失该字段的配置被错误判定为合法。
"""

DEFAULT_MEMORY_BUDGET_BYTES = 64 * 1024 * 1024

REQUIRED_FIELDS = {
    "emitter_name": "str",
    "spawn_rate": "float",
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
    peak = float(spawn_rate) * float(particle_lifetime)
    memory = peak * float(bytes_per_particle)
    return peak, memory


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

    for field, lo, hi, inclusive in RANGE_CHECKS:
        v = cfg.get(field)
        if v is None:
            continue
        ok = lo <= v <= hi if inclusive else lo < v < hi
        if not ok:
            errors.append("%s=%s 超出范围 (%s, %s]" % (field, v, lo, hi))

    peak = memory = 0.0
    if not errors:
        peak, memory = compute_niagara_budget(
            cfg.get("spawn_rate", 0.0), cfg.get("particle_lifetime", 0.0), cfg.get("bytes_per_particle", 0)
        )
        if peak > cfg.get("max_particles", 0):
            errors.append("峰值粒子数 %.1f 超过 max_particles" % peak)
        if memory > DEFAULT_MEMORY_BUDGET_BYTES:
            errors.append("内存预算超出默认上限")

    return {"valid": len(errors) == 0, "errors": errors, "peak_particles": peak, "memory_bytes": memory}
