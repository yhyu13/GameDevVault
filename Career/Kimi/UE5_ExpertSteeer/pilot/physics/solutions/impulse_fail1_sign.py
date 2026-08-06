"""两球碰撞冲量解算 —— 播种失败解 #1：冲量符号反（失败簇：冲量符号）。

A 球速度方向加反了：v_a' = v_a - j/m_a * n，v_b' = v_b + j/m_b * n，
导致碰撞后两球互相"穿过"而非反弹。
"""
from fvector_stub import FVector


def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)

    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)

    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_mass

    # BUG: 符号反了，本应 +j/m_a、-j/m_b
    v_a_new = v_a - normal * (j / m_a)
    v_b_new = v_b + normal * (j / m_b)
    return v_a_new, v_b_new
