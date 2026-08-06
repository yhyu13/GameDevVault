from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    j = -(1.0 + restitution) * vrel_n
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
