"""fx_02_curl_noise3d golden —— 3 维 curl noise 的数值实现（正弦叠加势场 → curl 取速度）。

UE C++ 形态（Stage 1 迁移目标）: Niagara 模块 HLSL 中的 curl noise 函数；pilot 用
软件求值（数值比对）代替 GPU 运行。数学约定：速度场 v = curl(Psi)，div(v) = 0 恒成立，
是各向同性湍流状流动的标准构造（例：Perlin/正弦势场的 curl 近似）。

势场定义（任务规格，实现必须与此一致）:
    psi_i(p, t) = sum_k amp_k * sin(2*pi*f_k*(w_k . p) + t*s_k + phase[i][k])
    amp_k = 1/(k+1), f_k = 2^k, 方向 w_k 为单位向量, s_k 为时间速度
速度场（curl 分量，符号约定 ∂psi_z/∂y - ∂psi_y/∂z 等）:
    vx = ∂psi_z/∂y - ∂psi_y/∂z
    vy = ∂psi_x/∂z - ∂psi_z/∂x
    vz = ∂psi_y/∂x - ∂psi_x/∂y
"""

import math

# 方向 w_k（单位向量，非轴对齐——保证 curl 各分量混合坐标，divergence 测试能抓到符号错误）
DIRS = (
    (0.6, 0.8, 0.0),
    (0.0, 0.6, 0.8),
    (0.8, 0.0, 0.6),
)
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
# phase[axis][k]
PHASES = (
    (0.1, 0.7, 1.3),
    (2.1, 0.3, 1.7),
    (1.1, 2.3, 0.9),
)


def _dpsi(axis, j, p, t):
    """∂psi_axis/∂p_j = sum_k amp_k * 2*pi*f_k * (w_k)_j * cos(arg_k)。"""
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    """p: (x, y, z)，t: 时间（秒）。返回 (vx, vy, vz)，divergence-free。"""
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
