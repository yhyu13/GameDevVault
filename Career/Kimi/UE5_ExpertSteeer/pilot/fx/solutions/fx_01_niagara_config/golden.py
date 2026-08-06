"""fx_01_niagara_config golden —— Niagara 发射器配置校验 + 预算计算。

UE C++ 形态（Stage 1 迁移目标）: UEditorValidator 读取 UNiagaraSystem 发射器参数
（SpawnRate / ParticleLifetime / MaxParticles）做配置审查；pilot 中配置以 JSON(dict) 表示。
"""

DEFAULT_MEMORY_BUDGET_BYTES = 64 * 1024 * 1024  # 64 MiB

REQUIRED_FIELDS = {
    "emitter_name": "str",
    "spawn_rate": "float",
    "particle_lifetime": "float",
    "max_particles": "int",
    "bytes_per_particle": "int",
}

# (字段, 下限, 上限, 是否闭区间)；spawn_rate/lifetime 下界开（必须 > 0）
RANGE_CHECKS = [
    ("spawn_rate", 0.0, 1_000_000.0, False),
    ("particle_lifetime", 0.0, 60.0, False),
    ("max_particles", 1, 10_000_000, True),
    ("bytes_per_particle", 16, 4096, True),
]


def compute_niagara_budget(spawn_rate, particle_lifetime, bytes_per_particle):
    """返回 (peak_particles, memory_bytes)。

    GPU 发射器按连续速率分配粒子，峰值 = 生成率 × 粒子寿命，内存 = 峰值 × 单粒子字节数。
    必须保留浮点精度，不可取整。
    """
    peak = float(spawn_rate) * float(particle_lifetime)
    memory = peak * float(bytes_per_particle)
    return peak, memory


def validate_niagara_config(cfg):
    """校验 Niagara 发射器配置 JSON。

    返回 {"valid": bool, "errors": [str], "peak_particles": float, "memory_bytes": float}。
    结构性错误（缺字段/类型/范围）返回 0.0；预算错误返回计算值便于调参。
    """
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
