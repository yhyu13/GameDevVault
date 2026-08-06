from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel = (v_a - v_b).Size()
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel / inv_mass
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
