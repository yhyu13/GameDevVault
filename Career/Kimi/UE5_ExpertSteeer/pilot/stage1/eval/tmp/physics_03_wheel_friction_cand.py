
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    """摩擦圆纵向力：剩余预算 sqrt((mu*fz)^2 - fy^2)，抓地耗尽归零。"""
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)

