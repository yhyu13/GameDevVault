from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vn = (v_a - v_b).Dot(normal)
    if vn > 0.0:
        return v_a + FVector(0,0,0), v_b + FVector(0,0,0)
    j = -(1.0 + restitution) * vn / (1.0 / m_a + 1.0 / m_b)
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
