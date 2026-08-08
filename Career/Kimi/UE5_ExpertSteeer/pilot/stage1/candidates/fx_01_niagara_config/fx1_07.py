BUDGET = 67108864


def validate_niagara_config(cfg):
    errors = []
    for name, typ in (("emitter_name", str), ("spawn_rate", float), ("particle_lifetime", float),
                      ("max_particles", int), ("bytes_per_particle", int)):
        if name not in cfg:
            errors.append(f"缺少字段 {name}")
        elif not isinstance(cfg[name], typ):
            errors.append(f"字段 {name} 类型应为 {typ.__name__}")
    if "spawn_rate" in cfg and isinstance(cfg["spawn_rate"], (int, float)) and not (0 < cfg["spawn_rate"] <= 1e6):
        errors.append("字段 spawn_rate 范围应为 (0, 1e6]")
    if "particle_lifetime" in cfg and isinstance(cfg["particle_lifetime"], (int, float)) and not (0 < cfg["particle_lifetime"] <= 60):
        errors.append("字段 particle_lifetime 范围应为 (0, 60]")
    if "max_particles" in cfg and isinstance(cfg["max_particles"], int) and not (1 <= cfg["max_particles"] <= 1e7):
        errors.append("字段 max_particles 范围应为 [1, 1e7]")
    if "bytes_per_particle" in cfg and isinstance(cfg["bytes_per_particle"], int) and not (16 <= cfg["bytes_per_particle"] <= 4096):
        errors.append("字段 bytes_per_particle 范围应为 [16, 4096]")
    if errors:
        return {"valid": False, "errors": errors, "peak_particles": 0.0, "memory_bytes": 0.0}
    peak, memory = compute_niagara_budget(cfg["spawn_rate"], cfg["particle_lifetime"], cfg["bytes_per_particle"])
    if peak > cfg["max_particles"]:
        errors.append(f"峰值粒子数 {peak} 超过 max_particles {cfg['max_particles']}")
    if memory > BUDGET:
        errors.append(f"内存 {memory} 字节超过默认预算 64 MiB")
    return {"valid": not errors, "errors": errors, "peak_particles": peak, "memory_bytes": memory}


def compute_niagara_budget(spawn_rate, particle_lifetime, bytes_per_particle):
    peak = spawn_rate * particle_lifetime
    return peak, peak * bytes_per_particle
