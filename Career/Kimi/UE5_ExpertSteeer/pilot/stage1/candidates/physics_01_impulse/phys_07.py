from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return v_a + FVector(0, 0, 0), v_b + FVector(0, 0, 0)
    inv_m = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_m
    va = v_a + normal * (j / m_a)
    vb = v_b - normal * (j / m_b)
    return va, vb
