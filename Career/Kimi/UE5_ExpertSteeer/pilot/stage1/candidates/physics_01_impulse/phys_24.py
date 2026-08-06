from fvector_stub import FVector

def resolve_impulse(m1, m2, v1, v2, n, e):
    vrel_n = (v1 - v2).Dot(n)
    if vrel_n > 0.0:
        return FVector(v1.x, v1.y, v1.z), FVector(v2.x, v2.y, v2.z)
    inv = 1.0 / m1 + 1.0 / m2
    j = -(1.0 + e) * vrel_n / inv
    return v1 + n * (j / m1), v2 - n * (j / m2)
