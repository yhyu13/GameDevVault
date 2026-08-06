from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    """两球碰撞冲量解算。单位：cm/s、kg；分离不施加冲量；不修改输入。"""
    v_rel = v_a - v_b
    vrel_n = v_rel.Dot(normal)
    if vrel_n >= 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    j = -(1.0 + restitution) * vrel_n / (1.0 / m_a + 1.0 / m_b)
    va2 = v_a + normal * (j / m_a)
    vb2 = v_b - normal * (j / m_b)
    return va2, vb2
