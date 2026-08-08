"""teacher_pool_fx —— fx 三任务候选池（v1：teacher=self）。由 teacher_pool.py 底部 merge。"""

FX1_PROMPT = """你是 UE5 特效工程师。Niagara 发射器配置以 JSON 对象给出，你需要实现配置校验器 + 预算计算器两个函数：
1. `validate_niagara_config(cfg)`：校验必填字段与类型（emitter_name: str 非空；spawn_rate: float；particle_lifetime: float；max_particles: int；bytes_per_particle: int），再做范围校验（spawn_rate ∈ (0, 1e6]、particle_lifetime ∈ (0, 60]、max_particles ∈ [1, 1e7]、bytes_per_particle ∈ [16, 4096]），最后做预算规则检查：
   - 峰值粒子数 peak = spawn_rate × particle_lifetime（GPU 发射器按连续速率分配）；若 peak > max_particles 报错（发射器会丢粒子）。
   - 内存 memory = peak × bytes_per_particle；若超过默认预算 64 MiB（67108864 字节）报错。
   返回 dict：{"valid": bool, "errors": [str], "peak_particles": float, "memory_bytes": float}。
2. `compute_niagara_budget(spawn_rate, particle_lifetime, bytes_per_particle)`：返回 (peak, memory)。必须保留浮点精度，禁止取整（截断会让预算失真）。
约束：不用第三方库；错误消息用中文并指明字段；结构性错误（缺字段/类型/范围）时 peak_particles/memory_bytes 返回 0.0，预算错误时返回计算值（便于调参）。"""

FX2_PROMPT = """你是 UE5 特效工程师。实现 3D curl noise：速度场 v = curl(Psi)，其中 Psi = (psi_x, psi_y, psi_z) 是三个标量势场（正弦叠加近似），p = (x, y, z) 为世界坐标（cm），t 为时间（秒）。
势场定义（必须与此规格一致）：
psi_i(p, t) = sum_{k=0}^{2} amp_k * sin(2*pi*f_k*(w_k . p) + t*s_k + phase[i][k])
amp_k = 1/(k+1)   f_k = 2^k   s_k = (0.5, 1.0, 1.5)
w_0=(0.6,0.8,0.0)  w_1=(0.0,0.6,0.8)  w_2=(0.8,0.0,0.6)
phase = ((0.1,0.7,1.3), (2.1,0.3,1.7), (1.1,2.3,0.9))
速度场（curl 标准符号约定，符号错会破坏 divergence-free）：
vx = ∂psi_z/∂y − ∂psi_y/∂z
vy = ∂psi_x/∂z − ∂psi_z/∂x
vz = ∂psi_y/∂x − ∂psi_x/∂y
实现 `curl_noise3d(p, t)` 返回 (vx, vy, vz)。约束：只用 math；幅度衰减 1/(k+1) 必须保留（高频项压不掉会撕裂画面）；时间项 t*s_k 必须参与（静止场不是 curl noise）。"""

FX3_PROMPT = """你是 UE5 特效工程师。实现 flipbook（序列帧）的帧号 → 行列与 UV 矩形换算，供粒子按帧动画采样：
1. `flipbook_uv(frame, cols, rows, wrap)` → (col, row)（均 0 起始）
   - wrap=True：帧索引对总帧数 cols*rows 取模（循环播放）。
   - wrap=False：钳到最后一帧 cols*rows-1（播放到头定格）。
   - 行列规则：col = f % cols，row = f // cols（行优先，row 0 是第一行）。
2. `flipbook_uv_rect(frame, cols, rows, wrap)` → (u0, v0, u1, v1)（UV 矩形）
   - u0 = col/cols，u1 = (col+1)/cols
   - v 向下约定：v1 = 1.0 - row/rows（行顶），v0 = 1.0 - (row+1)/rows（行底）；row 0 的 v 更大。
约束：不用第三方库；帧号非负；cols、rows 为正整数；结果必须始终落在 [0, cols-1] × [0, rows-1] 内（越界帧 = UV 越界 = 采样错误）。"""

_BUDGET = 67108864


def _mk_niagara_high(cand_id, tail):
    return (f"fx1_{cand_id:02d}", tail)


POOL = {
    "fx_01_niagara_config": {
        "fx1_01": '''
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
''',
        "fx1_02": '''
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
''',
        "fx1_03": '''
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
''',
        "fx1_04": '''
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
''',
        "fx1_05": '''
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
''',
        "fx1_06": '''
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
''',
        "fx1_07": '''
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
''',
        "fx1_08": '''
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
''',
        "fx1_09": '''
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
''',
        "fx1_10": '''
BUDGET=67108864

def validate_niagara_config(cfg):
    errors=[]
    for name,typ in (("emitter_name",str),("spawn_rate",float),("particle_lifetime",float),("max_particles",int),("bytes_per_particle",int)):
        if name not in cfg:
            errors.append(f"缺少字段 {name}")
        elif not isinstance(cfg[name],typ):
            errors.append(f"字段 {name} 类型应为 {typ.__name__}")
    if "spawn_rate" in cfg and isinstance(cfg["spawn_rate"],(int,float)) and not (0<cfg["spawn_rate"]<=1e6):
        errors.append("字段 spawn_rate 范围应为 (0, 1e6]")
    if "particle_lifetime" in cfg and isinstance(cfg["particle_lifetime"],(int,float)) and not (0<cfg["particle_lifetime"]<=60):
        errors.append("字段 particle_lifetime 范围应为 (0, 60]")
    if "max_particles" in cfg and isinstance(cfg["max_particles"],int) and not (1<=cfg["max_particles"]<=1e7):
        errors.append("字段 max_particles 范围应为 [1, 1e7]")
    if "bytes_per_particle" in cfg and isinstance(cfg["bytes_per_particle"],int) and not (16<=cfg["bytes_per_particle"]<=4096):
        errors.append("字段 bytes_per_particle 范围应为 [16, 4096]")
    if errors:
        return {"valid":False,"errors":errors,"peak_particles":0.0,"memory_bytes":0.0}
    peak,memory=compute_niagara_budget(cfg["spawn_rate"],cfg["particle_lifetime"],cfg["bytes_per_particle"])
    if peak>cfg["max_particles"]:
        errors.append(f"峰值粒子数 {peak} 超过 max_particles {cfg['max_particles']}")
    if memory>BUDGET:
        errors.append(f"内存 {memory} 字节超过默认预算 64 MiB")
    return {"valid":not errors,"errors":errors,"peak_particles":peak,"memory_bytes":memory}

def compute_niagara_budget(spawn_rate,particle_lifetime,bytes_per_particle):
    peak=spawn_rate*particle_lifetime
    return peak,peak*bytes_per_particle
''',
        "fx1_11": '''
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
''',
        "fx1_12": '''
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
''',
        "fx1_13": '''
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
''',
        "fx1_14": '''
BUDGET = 67108864


def validate_niagara_config(cfg):
    errors = []
    for name, typ in (("emitter_name", str), ("spawn_rate", float),
                      ("max_particles", int), ("bytes_per_particle", int)):
        if name not in cfg:
            errors.append(f"缺少字段 {name}")
        elif not isinstance(cfg[name], typ):
            errors.append(f"字段 {name} 类型应为 {typ.__name__}")
    if "spawn_rate" in cfg and isinstance(cfg["spawn_rate"], (int, float)) and not (0 < cfg["spawn_rate"] <= 1e6):
        errors.append("字段 spawn_rate 范围应为 (0, 1e6]")
    if "max_particles" in cfg and isinstance(cfg["max_particles"], int) and not (1 <= cfg["max_particles"] <= 1e7):
        errors.append("字段 max_particles 范围应为 [1, 1e7]")
    if "bytes_per_particle" in cfg and isinstance(cfg["bytes_per_particle"], int) and not (16 <= cfg["bytes_per_particle"] <= 4096):
        errors.append("字段 bytes_per_particle 范围应为 [16, 4096]")
    if errors:
        return {"valid": False, "errors": errors, "peak_particles": 0.0, "memory_bytes": 0.0}
    peak, memory = compute_niagara_budget(cfg["spawn_rate"], cfg.get("particle_lifetime", 0.0), cfg["bytes_per_particle"])
    if peak > cfg["max_particles"]:
        errors.append(f"峰值粒子数 {peak} 超过 max_particles {cfg['max_particles']}")
    if memory > BUDGET:
        errors.append(f"内存 {memory} 字节超过默认预算 64 MiB")
    return {"valid": not errors, "errors": errors, "peak_particles": peak, "memory_bytes": memory}


def compute_niagara_budget(spawn_rate, particle_lifetime, bytes_per_particle):
    peak = spawn_rate * particle_lifetime
    return peak, peak * bytes_per_particle
''',
        "fx1_15": '''
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
    peak = int(spawn_rate * particle_lifetime)
    return peak, peak * bytes_per_particle
''',
        "fx1_16": '''
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
''',
        "fx1_17": '''
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
    peak, memory = cfg["spawn_rate"] * cfg["particle_lifetime"], cfg["spawn_rate"] * cfg["particle_lifetime"] * cfg["bytes_per_particle"]
    if peak > cfg["max_particles"]:
        errors.append(f"峰值粒子数 {peak} 超过 max_particles {cfg['max_particles']}")
    if memory > BUDGET:
        errors.append(f"内存 {memory} 字节超过默认预算 64 MiB")
    return {"valid": not errors, "errors": errors, "peak_particles": peak, "memory_bytes": memory}
''',
        "fx1_18": '''
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
''',
    },

    "fx_02_curl_noise3d": {
        "fx2_01": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    """v = curl(Psi)：vx = dpsi_z/dy - dpsi_y/dz 等，divergence-free。"""
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_02": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_03": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def curl_noise3d(p, t):
    vx = 0.0
    vy = 0.0
    vz = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        c = 2.0 * math.pi * FREQS[k]
        vx += amp * c * DIRS[k][1] * math.cos(c * dot + t * SPEEDS[k] + PHASES[2][k])
        vx -= amp * c * DIRS[k][2] * math.cos(c * dot + t * SPEEDS[k] + PHASES[1][k])
        vy += amp * c * DIRS[k][2] * math.cos(c * dot + t * SPEEDS[k] + PHASES[0][k])
        vy -= amp * c * DIRS[k][0] * math.cos(c * dot + t * SPEEDS[k] + PHASES[2][k])
        vz += amp * c * DIRS[k][0] * math.cos(c * dot + t * SPEEDS[k] + PHASES[1][k])
        vz -= amp * c * DIRS[k][1] * math.cos(c * dot + t * SPEEDS[k] + PHASES[0][k])
    return (vx, vy, vz)
''',
        "fx2_04": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    return (_dpsi(2, 1, p, t) - _dpsi(1, 2, p, t),
            _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t),
            _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t))
''',
        "fx2_05": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def curl_noise3d(p, t):
    """v = curl(Psi)。每分量 = 两次偏导之差，divergence-free。"""
    vx = 0.0
    vy = 0.0
    vz = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        w = DIRS[k]
        dot = w[0] * p[0] + w[1] * p[1] + w[2] * p[2]
        c = 2.0 * math.pi * FREQS[k]
        base = c * dot + t * SPEEDS[k]
        vx += amp * c * w[1] * math.cos(base + PHASES[2][k])
        vx -= amp * c * w[2] * math.cos(base + PHASES[1][k])
        vy += amp * c * w[2] * math.cos(base + PHASES[0][k])
        vy -= amp * c * w[0] * math.cos(base + PHASES[2][k])
        vz += amp * c * w[0] * math.cos(base + PHASES[1][k])
        vz -= amp * c * w[1] * math.cos(base + PHASES[0][k])
    return (vx, vy, vz)
''',
        "fx2_06": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_07": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_08": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_09": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_10": '''
import math

DIRS=((0.6,0.8,0.0),(0.0,0.6,0.8),(0.8,0.0,0.6))
FREQS=(1.0,2.0,4.0)
SPEEDS=(0.5,1.0,1.5)
PHASES=((0.1,0.7,1.3),(2.1,0.3,1.7),(1.1,2.3,0.9))

def _dpsi(axis,j,p,t):
    acc=0.0
    for k in range(3):
        amp=1.0/(k+1.0)
        dot=DIRS[k][0]*p[0]+DIRS[k][1]*p[1]+DIRS[k][2]*p[2]
        arg=2.0*math.pi*FREQS[k]*dot+t*SPEEDS[k]+PHASES[axis][k]
        acc+=amp*2.0*math.pi*FREQS[k]*DIRS[k][j]*math.cos(arg)
    return acc

def curl_noise3d(p,t):
    return (_dpsi(2,1,p,t)-_dpsi(1,2,p,t),_dpsi(0,2,p,t)-_dpsi(2,0,p,t),_dpsi(1,0,p,t)-_dpsi(0,1,p,t))
''',
        "fx2_11": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_12": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_13": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_14": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) + _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_15": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_16": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_17": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
''',
        "fx2_18": '''
import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    return (vx, vy)
''',
    },

    "fx_03_flipbook_uv": {
        "fx3_01": '''def flipbook_uv(frame, cols, rows, wrap):
    """帧号 -> (col, row)。wrap 取模总帧数，否则钳到末帧。"""
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    """UV 矩形 (u0, v0, u1, v1)，v 向下约定。"""
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
''',
        "fx3_02": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return f % cols, f // cols


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
''',
        "fx3_03": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    col = f % cols
    row = f // cols
    return (col, row)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
''',
        "fx3_04": '''def flipbook_uv(frame, cols, rows, wrap):
    """wrap=True 循环，False 定格；行优先，0 起始。"""
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
''',
        "fx3_05": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    if wrap:
        f = frame % total
    else:
        f = frame if frame < total else total - 1
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
''',
        "fx3_06": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
''',
        "fx3_07": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
''',
        "fx3_08": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
''',
        "fx3_09": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
''',
        "fx3_10": '''def flipbook_uv(frame,cols,rows,wrap):
    total=cols*rows
    f=frame%total if wrap else min(frame,total-1)
    return (f%cols,f//cols)

def flipbook_uv_rect(frame,cols,rows,wrap):
    col,row=flipbook_uv(frame,cols,rows,wrap)
    return (col/cols,1.0-(row+1)/rows,(col+1)/cols,1.0-row/rows)
''',
        "fx3_11": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
''',
        "fx3_12": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
''',
        "fx3_13": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
''',
        "fx3_14": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f // rows, f % rows)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
''',
        "fx3_15": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % rows if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
''',
        "fx3_16": '''import math


def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    if wrap:
        f = frame % total
    else:
        f = min(frame, total)
    col = math.ceil(f / cols) - 1
    row = f // cols
    return (col, row)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
''',
        "fx3_17": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)
''',
        "fx3_18": '''def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
''',
    },
}

TIER = {
    "fx_01_niagara_config": {f"fx1_{i:02d}": "correct_high" for i in range(1, 10)}
    | {f"fx1_{i:02d}": "correct_mid" for i in range(10, 14)}
    | {"fx1_14": "buggy_subtle", "fx1_15": "buggy_subtle", "fx1_16": "buggy_obvious",
       "fx1_17": "api_bad", "fx1_18": "correct_mid"},
    "fx_02_curl_noise3d": {f"fx2_{i:02d}": "correct_high" for i in range(1, 10)}
    | {f"fx2_{i:02d}": "correct_mid" for i in range(10, 14)}
    | {"fx2_14": "buggy_subtle", "fx2_15": "buggy_subtle", "fx2_16": "buggy_obvious",
       "fx2_17": "buggy_obvious", "fx2_18": "api_bad"},
    "fx_03_flipbook_uv": {f"fx3_{i:02d}": "correct_high" for i in range(1, 10)}
    | {f"fx3_{i:02d}": "correct_mid" for i in range(10, 14)}
    | {"fx3_14": "buggy_subtle", "fx3_15": "buggy_subtle", "fx3_16": "buggy_obvious",
       "fx3_17": "api_bad", "fx3_18": "correct_mid"},
}

PROMPTS = {
    "fx_01_niagara_config": FX1_PROMPT,
    "fx_02_curl_noise3d": FX2_PROMPT,
    "fx_03_flipbook_uv": FX3_PROMPT,
}

MODEL_SIZE = {
    "fx_01_niagara_config": "2B",
    "fx_02_curl_noise3d": "0.8B",
    "fx_03_flipbook_uv": "0.8B",
}

DOMAIN = {
    "fx_01_niagara_config": "fx",
    "fx_02_curl_noise3d": "fx",
    "fx_03_flipbook_uv": "fx",
}
