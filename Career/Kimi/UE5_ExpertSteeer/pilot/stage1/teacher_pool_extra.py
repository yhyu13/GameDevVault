"""teacher_pool_extra —— 剩余 7 任务候选池（v1：teacher=self）。由 teacher_pool.py 底部 merge。

本文件：physics_02_spring_euler / physics_03_wheel_friction / rendering_02_lod_distance / rendering_03_linear_srgb
teacher_pool_fx.py：fx_01 / fx_02 / fx_03
"""

SPRING_PROMPT = """实现阻尼弹簧的一步积分函数 `spring_step`，使用半隐式欧拉（symplectic Euler）：
1. 加速度：`a = (-k*(x - rest) - c*v) / m`（弹簧力 + 阻尼力，两项都必须带正确符号）；
2. 先更新速度：`v' = v + a*dt`；
3. 再用新速度更新位置：`x' = x + v'*dt`（这是半隐式与显式欧拉的关键区别，顺序不可颠倒）；
4. 返回 `(x', v')` 两个 float。
单位遵循 UE 约定：x 为 cm，刚度 k 为 N/cm，阻尼 c 为 N·s/cm，质量 m 为 kg，dt 为 s。不得对 k、c、m、dt 做任何单位换算。不使用任何库（纯 Python 浮点）。"""

WHEEL_PROMPT = """实现载具轮胎纵向力计算函数 `wheel_longitudinal_force`，遵守摩擦圆（friction circle）约束：
1. 总抓地预算 `grip = mu * fz`（mu 为摩擦系数，fz 为法向载荷 N）；
2. 横向力 `fy` 会占用部分抓地：纵向剩余预算 `fmax = sqrt(grip² - fy²)`；当 `fy >= grip` 时抓地耗尽，`fmax` 必须为 0——不得对负数开方（返回 NaN 即失败），可用 FMath.SqrtSafe；
3. 纵向力 `Fx = clamp(ks * slip, -fmax, fmax)`（ks 为纵向滑移刚度 N）；
4. 无接触（fz <= 0）时返回 0；
5. 符号约定：slip > 0 输出正力（驱动），slip < 0 输出负力（制动），符号不可反转。
单位：力 N、载荷 N、slip 无量纲、mu 无量纲。可用 `from fvector_stub import FMath`（提供 Clamp / SqrtSafe）。不得使用随机数、IO 或第三方库。"""

LOD_PROMPT = """你是 UE5 渲染工程师。实现 LOD 距离选择：给定当前 LOD、屏幕占比 `screen_size`（0~1，越大越近越精细）、降序阈值数组 `thresholds`（t[0] > t[1] > ...，screen_size >= t[i] 选 LOD i，低于末级阈值选最后一级），返回应显示的 LOD 索引。
必须实现 hysteresis（迟滞）以抑制阈值附近来回切换（pop/抖动）：
- 升级（变精细，i → i-1）：仅当 screen_size >= t[i-1] * (1 + hysteresis)
- 降级（变粗糙，i → i+1）：仅当 screen_size < t[i] * (1 - hysteresis)
- current_lod=None（首次调用/状态丢失）时不施加迟滞，直接返回基础选择。
实现 `select_lod(current_lod, screen_size, thresholds, hysteresis=0.1)`，返回 int。
约束：thresholds 可为空（返回 0）；hysteresis ∈ [0, 1)。无迟滞的解会在阈值附近每帧来回跳（画面抖动）；迟滞带方向做反会放大抖动而不是抑制它。"""

SRGB_PROMPT = """你是 UE5 渲染工程师。实现 linear → sRGB 编码（IEC 61966-2-1 标准），用于后处理/色调映射后写回 sRGB render target 前的逐像素转换。
标准分段（每通道独立）：
c <= 0.0031308 :  12.92 * c
c >  0.0031308 :  1.055 * c^(1/2.4) - 0.055
实现 `linear_to_srgb(c)`，输入 (r, g, b) 为 [0,1] 的 linear 值，返回编码后的 (r, g, b) 元组。输入越界先 Clamp 到 [0,1]（防御性，UE 语义：负值/超亮值不得产生 NaN/越界输出）。
约束：只用 math；常数必须是标准值（阈值 0.0031308、线性段 12.92、1.055、0.055、指数 2.4）。对已编码值再编码一次（双伽马）会让画面整体过亮；指数用 2.2 替代 1/2.4 会系统性色偏；丢掉线性段会压坏暗部对比度。"""

POOL = {
    "physics_02_spring_euler": {
        "spr_01": '''def spring_step(x, v, k, c, rest, m, dt):
    """阻尼弹簧半隐式欧拉单步：a -> v' -> x'（用新速度更新位置）。"""
    a = (-k * (x - rest) - c * v) / m
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new
''',
        "spr_02": '''def spring_step(x, v, k, c, rest, m, dt):
    """半隐式欧拉。单位：x cm、k N/cm、c N*s/cm、m kg、dt s。"""
    accel = (-k * (x - rest) - c * v) / m
    v1 = v + accel * dt
    x1 = x + v1 * dt
    return x1, v1
''',
        "spr_03": '''def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    v_new = v + a * dt
    return x + v_new * dt, v_new
''',
        "spr_04": '''def spring_step(x, v, k, c, rest, m, dt):
    """弹簧+阻尼合力产生加速度，半隐式更新次序（速度先行）。"""
    force = -k * (x - rest) - c * v
    a = force / m
    vp = v + a * dt
    xp = x + vp * dt
    return xp, vp
''',
        "spr_05": '''def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    v_next = v + a * dt
    x_next = x + v_next * dt
    return (x_next, v_next)
''',
        "spr_06": '''def spring_step(x, v, k, c, rest, m, dt):
    """symplectic Euler：先速度后位置，能量有界。"""
    acc = (-k * (x - rest) - c * v) / m
    v2 = v + acc * dt
    x2 = x + v2 * dt
    return x2, v2
''',
        "spr_07": '''def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    v_ = v + a * dt
    x_ = x + v_ * dt
    return x_, v_
''',
        "spr_08": '''def spring_step(x, v, k, c, rest, m, dt):
    """单步积分。弹簧力 Fs=-k(x-rest)，阻尼力 Fd=-c*v，a=(Fs+Fd)/m。"""
    a = (-k * (x - rest) - c * v) / m
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new
''',
        "spr_09": '''def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    v = v + a * dt
    x = x + v * dt
    return x, v
''',
        "spr_10": '''def spring_step(x,v,k,c,rest,m,dt):
    a=(-k*(x-rest)-c*v)/m
    v=v+a*dt
    x=x+v*dt
    return x,v
''',
        "spr_11": '''def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    return x + (v + a * dt) * dt, v + a * dt
''',
        "spr_12": '''def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    v_new = v + a * dt
    return x + v_new * dt, v_new
''',
        "spr_13": '''def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    vp = v + a * dt
    xp = x + vp * dt
    return xp, vp
''',
        "spr_14": '''def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    x_new = x + v * dt
    v_new = v + a * dt
    return x_new, v_new
''',
        "spr_15": '''def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / (m * 100.0)
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new
''',
        "spr_16": '''def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) + c * v) / m
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new
''',
        "spr_17": '''def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest)) / m
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new
''',
        "spr_18": '''def spring_step(x0, v0, kk, cc, rest, m, dt):
    a = (-kk * (x0 - rest) - cc * v0) / m
    v_new = v0 + a * dt
    x_new = x0 + v_new * dt
    return x_new, v_new
''',
    },

    "physics_03_wheel_friction": {
        "whl_01": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    """摩擦圆纵向力：剩余预算 sqrt((mu*fz)^2 - fy^2)，抓地耗尽归零。"""
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
''',
        "whl_02": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    remaining = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -remaining, remaining)
''',
        "whl_03": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    fmax = FMath.SqrtSafe((mu * fz) ** 2 - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
''',
        "whl_04": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    """Fx 受摩擦圆约束；无接触返回 0；slip 符号决定驱动/制动。"""
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
''',
        "whl_05": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    rem = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -rem, rem)
''',
        "whl_06": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
''',
        "whl_07": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    budget = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -budget, budget)
''',
        "whl_08": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
''',
        "whl_09": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
''',
        "whl_10": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip,fz,fy,mu,ks):
    if fz<=0.0:
        return 0.0
    fmax=FMath.SqrtSafe((mu*fz)**2-fy*fy)
    return FMath.Clamp(ks*slip,-fmax,fmax)
''',
        "whl_11": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    rem = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -rem, rem)
''',
        "whl_12": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
''',
        "whl_13": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
''',
        "whl_14": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    return FMath.Clamp(ks * slip, -grip, grip)
''',
        "whl_15": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return -FMath.Clamp(ks * slip, -fmax, fmax)
''',
        "whl_16": '''
import math
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = math.sqrt(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
''',
        "whl_17": '''
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
''',
        "whl_18": '''
import random
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
''',
    },

    "rendering_02_lod_distance": {
        "lod_01": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    """LOD 选择（带迟滞）。升级需越过 t[i-1]*(1+hyst)，降级需跌破 t[i]*(1-hyst)。"""
    if not thresholds:
        return 0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_02": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    n = len(thresholds)
    base = n - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < n - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_03": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    """首帧无迟滞；有状态时升级/降级各设迟滞带，防阈值附近抖动。"""
    n = len(thresholds)
    if n == 0:
        return 0
    base = n - 1
    for i in range(n):
        if screen_size >= thresholds[i]:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < n - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_04": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    base = sum(1 for t in thresholds if screen_size >= t)
    base = min(base, len(thresholds) - 1)
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_05": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    n = len(thresholds)
    if n == 0:
        return 0
    base = n - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < n - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_06": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    """迟滞：升级带在上界 (1+hyst)，降级带在下界 (1-hyst)。"""
    if not thresholds:
        return 0
    n = len(thresholds)
    base = n - 1
    for i in range(n):
        if screen_size >= thresholds[i]:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < n - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_07": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_08": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    n = len(thresholds)
    if n == 0:
        return 0
    base = n - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < n - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_09": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_10": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    base=len(thresholds)-1
    for i,t in enumerate(thresholds):
        if screen_size>=t:
            base=i; break
    if current_lod is None:
        return base
    lod=current_lod
    while lod>0 and screen_size>=thresholds[lod-1]*(1.0+hysteresis):
        lod-=1
    if lod<len(thresholds)-1 and screen_size<thresholds[lod]*(1.0-hysteresis):
        lod+=1
    return lod
''',
        "lod_11": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_12": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    n = len(thresholds)
    if n == 0:
        return 0
    base = n - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < n - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_13": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_14": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    return base
''',
        "lod_15": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 - hysteresis):
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod] * (1.0 + hysteresis):
        lod += 1
    return lod
''',
        "lod_16": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    n = len(thresholds)
    base = n
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < n - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
''',
        "lod_17": '''def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0.0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    return float(base)
''',
        "lod_18": '''def select_lod(current_lod, screen_size, thresholds):
    if not thresholds:
        return 0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1]:
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod]:
        lod += 1
    return lod
''',
    },

    "rendering_03_linear_srgb": {
        "srgb_01": '''import math

THRESHOLD = 0.0031308
LINEAR_COEF = 12.92
A = 1.055
B = 0.055
GAMMA = 2.4


def linear_to_srgb(c):
    """IEC 61966-2-1：线性段 + 幂段，越界先 clamp。"""
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        if v <= THRESHOLD:
            out.append(LINEAR_COEF * v)
        else:
            out.append(A * v ** (1.0 / GAMMA) - B)
    return tuple(out)
''',
        "srgb_02": '''import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = min(max(v, 0.0), 1.0)
        out.append(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
''',
        "srgb_03": '''import math

TH = 0.0031308
K = 12.92


def _enc(x):
    x = max(0.0, min(1.0, x))
    if x <= TH:
        return K * x
    return 1.055 * x ** (1.0 / 2.4) - 0.055


def linear_to_srgb(c):
    """逐通道独立编码：c<=0.0031308 线性段，否则幂段。"""
    return tuple(_enc(v) for v in c)
''',
        "srgb_04": '''import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        if v <= 0.0031308:
            out.append(12.92 * v)
        else:
            out.append(1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
''',
        "srgb_05": '''import math

def linear_to_srgb(c):
    r, g, b = c
    def enc(v):
        v = max(0.0, min(1.0, v))
        return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055
    return (enc(r), enc(g), enc(b))
''',
        "srgb_06": '''import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = min(1.0, max(0.0, v))
        out.append(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
''',
        "srgb_07": '''import math

def linear_to_srgb(c):
    res = []
    for v in c:
        v = max(0.0, min(1.0, v))
        if v <= 0.0031308:
            res.append(12.92 * v)
        else:
            res.append(1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(res)
''',
        "srgb_08": '''import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        out.append(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
''',
        "srgb_09": '''import math

def linear_to_srgb(c):
    """linear -> sRGB（每通道分段，IEC 61966-2-1）。"""
    return tuple(
        12.92 * max(0.0, min(1.0, v)) if max(0.0, min(1.0, v)) <= 0.0031308
        else 1.055 * max(0.0, min(1.0, v)) ** (1.0 / 2.4) - 0.055
        for v in c
    )
''',
        "srgb_10": '''import math

def linear_to_srgb(c):
    out=[]
    for v in c:
        v=max(0.0,min(1.0,v))
        out.append(12.92*v if v<=0.0031308 else 1.055*v**(1.0/2.4)-0.055)
    return tuple(out)
''',
        "srgb_11": '''import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        out.append(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
''',
        "srgb_12": '''import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        out.append(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
''',
        "srgb_13": '''import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        out.append(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
''',
        "srgb_14": '''import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        out.append(1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
''',
        "srgb_15": '''import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        out.append(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.2) - 0.055)
    return tuple(out)
''',
        "srgb_16": '''import math

def _enc(v):
    v = max(0.0, min(1.0, v))
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055


def linear_to_srgb(c):
    return tuple(_enc(_enc(v)) for v in c)
''',
        "srgb_17": '''import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        out.append(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055)
    return out[:2]
''',
        "srgb_18": '''import math

def srgb_encode(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        out.append(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
''',
    },
}

TIER = {
    "physics_02_spring_euler": {f"spr_{i:02d}": "correct_high" for i in range(1, 10)}
    | {f"spr_{i:02d}": "correct_mid" for i in range(10, 14)}
    | {"spr_14": "buggy_subtle", "spr_15": "buggy_subtle", "spr_16": "buggy_obvious",
       "spr_17": "buggy_obvious", "spr_18": "api_bad"},
    "physics_03_wheel_friction": {f"whl_{i:02d}": "correct_high" for i in range(1, 10)}
    | {f"whl_{i:02d}": "correct_mid" for i in range(10, 14)}
    | {"whl_14": "buggy_subtle", "whl_15": "buggy_subtle", "whl_16": "buggy_obvious",
       "whl_17": "buggy_obvious", "whl_18": "api_bad"},
    "rendering_02_lod_distance": {f"lod_{i:02d}": "correct_high" for i in range(1, 10)}
    | {f"lod_{i:02d}": "correct_mid" for i in range(10, 14)}
    | {"lod_14": "buggy_subtle", "lod_15": "buggy_subtle", "lod_16": "buggy_obvious",
       "lod_17": "api_bad", "lod_18": "api_bad"},
    "rendering_03_linear_srgb": {f"srgb_{i:02d}": "correct_high" for i in range(1, 10)}
    | {f"srgb_{i:02d}": "correct_mid" for i in range(10, 14)}
    | {"srgb_14": "buggy_subtle", "srgb_15": "buggy_obvious", "srgb_16": "buggy_obvious",
       "srgb_17": "api_bad", "srgb_18": "api_bad"},
}

PROMPTS = {
    "physics_02_spring_euler": SPRING_PROMPT,
    "physics_03_wheel_friction": WHEEL_PROMPT,
    "rendering_02_lod_distance": LOD_PROMPT,
    "rendering_03_linear_srgb": SRGB_PROMPT,
}

MODEL_SIZE = {
    "physics_02_spring_euler": "0.8B",
    "physics_03_wheel_friction": "0.8B-2B",
    "rendering_02_lod_distance": "0.8B",
    "rendering_03_linear_srgb": "0.8B",
}

DOMAIN = {
    "physics_02_spring_euler": "physics",
    "physics_03_wheel_friction": "physics",
    "rendering_02_lod_distance": "rendering",
    "rendering_03_linear_srgb": "rendering",
}
