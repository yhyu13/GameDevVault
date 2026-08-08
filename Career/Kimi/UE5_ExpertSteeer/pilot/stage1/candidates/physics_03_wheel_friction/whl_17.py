from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
