from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    fmax = FMath.SqrtSafe((mu * fz) ** 2 - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
