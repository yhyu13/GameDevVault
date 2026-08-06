"""播种失败解 1：curl 分量符号错误（vx 用了 + 而不是 -）。

失败簇类型：符号错误。vy/vz 正确，仅 vx = ∂psi_z/∂y + ∂psi_y/∂z。
数值与 golden 不同，且破坏 divergence-free（div = 2·∂²psi_y/∂z∂x ≠ 0，因 w_k 非轴对齐）。
"""

import math

DIRS = (
    (0.6, 0.8, 0.0),
    (0.0, 0.6, 0.8),
    (0.8, 0.0, 0.6),
)
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = (
    (0.1, 0.7, 1.3),
    (2.1, 0.3, 1.7),
    (1.1, 2.3, 0.9),
)


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
