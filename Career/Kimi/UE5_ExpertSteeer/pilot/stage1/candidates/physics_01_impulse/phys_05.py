from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    """冲量解算：仅在接近时施加。返回新速度，输入只读。"""
    vrel = v_a - v_b
    vn = vrel.Dot(normal)
    if vn > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    mass_term = (1.0 / m_a) + (1.0 / m_b)
    j = -(1.0 + restitution) * vn / mass_term
    new_a = v_a + normal * (j / m_a)
    new_b = v_b - normal * (j / m_b)
    return new_a, new_b
