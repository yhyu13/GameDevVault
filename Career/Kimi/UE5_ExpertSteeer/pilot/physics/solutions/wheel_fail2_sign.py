"""载具轮纵向力 / 摩擦圆 —— 播种失败解 #2：符号反（失败簇：轴约定/符号）。

返回值整体取负：驱动力变成制动力。slip>0 时输出负力。
输入是 -0.0 或 0 的测试不受影响，其余全部反号。
"""
from fvector_stub import FMath


def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    # BUG: 符号反了，不应取负
    return -FMath.Clamp(ks * slip, -fmax, fmax)
