from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    budget = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -budget, budget)
