BUDGET = 67108864


def validate_niagara_config(cfg):
    errors = []
    for name, typ in (("emitter_name", str), ("spawn_rate", float), ("particle_lifetime", float),
                      ("max_particles", int), ("bytes_per_particle", int)):
        if name not in cfg:
            errors.append(f"缺少字段 {name}")
        elif not isinstance(cfg[name], typ):
            errors.append(f"字段 {name} 类型应为 {typ.__name__}")
    for name, lo, hi in (("spawn_rate", 0, 1e6), ("particle_lifetime", 0, 60),
                         ("max_particles", 1, 1e7), ("bytes_per_particle", 16, 4096)):
        if name in cfg and isinstance(cfg[name], (int, float)):
            if not (lo < cfg[name] <= hi):
                errors.append(f"字段 {name} 超出范围")
    if errors:
        return {"valid": False, "errors": errors, "peak_particles": 0.0, "memory_bytes": 0.0}
    peak, memory = compute_niagara_budget(cfg["spawn_rate"], cfg["particle_lifetime"], cfg["bytes_per_particle"])
    if peak > cfg["max_particles"]:
        errors.append("峰值粒子数超出 max_particles")
    if memory > BUDGET:
        errors.append("内存超过默认预算 64 MiB")
    return {"valid": not errors, "errors": errors, "peak_particles": peak, "memory_bytes": memory}


def compute_niagara_budget(spawn_rate, particle_lifetime, bytes_per_particle):
    peak = spawn_rate * particle_lifetime
    return peak, peak * bytes_per_particle
