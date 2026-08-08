from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    """Fx 受摩擦圆约束；无接触返回 0；slip 符号决定驱动/制动。"""
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
