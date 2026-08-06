"""播种失败解 2：不做范围/预算校验（负生成率、峰值超限、内存超限全部放行）。

失败簇类型：配置越界值/预算检查遗漏。只查必填字段与类型，
不查范围（spawn_rate <= 0 放行）、不查预算规则（rate×lifetime > max_particles 放行）。
"""

DEFAULT_MEMORY_BUDGET_BYTES = 64 * 1024 * 1024

REQUIRED_FIELDS = {
    "emitter_name": "str",
    "spawn_rate": "float",
    "particle_lifetime": "float",
    "max_particles": "int",
    "bytes_per_particle": "int",
}


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

    return {"valid": len(errors) == 0, "errors": errors, "peak_particles": 0.0, "memory_bytes": 0.0}
