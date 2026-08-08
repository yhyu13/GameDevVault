def validate_niagara_config(cfg):
    errors = []
    for name, typ in (("emitter_name", str), ("spawn_rate", float), ("particle_lifetime", float),
                      ("max_particles", int), ("bytes_per_particle", int)):
        if name not in cfg:
            errors.append(f"缺少字段 {name}")
        elif not isinstance(cfg[name], typ):
            errors.append(f"字段 {name} 类型应为 {typ.__name__}")
    if errors:
        return {"valid": False, "errors": errors, "peak_particles": 0.0, "memory_bytes": 0.0}
    peak, memory = compute_niagara_budget(cfg["spawn_rate"], cfg["particle_lifetime"], cfg["bytes_per_particle"])
    return {"valid": True, "errors": [], "peak_particles": peak, "memory_bytes": memory}


def compute_niagara_budget(spawn_rate, particle_lifetime, bytes_per_particle):
    peak = spawn_rate * particle_lifetime
    return peak, peak * bytes_per_particle
