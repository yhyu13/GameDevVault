"""两球碰撞冲量解算 —— 播种失败解 #2：质量尺度错（失败簇：质量与速度尺度）。

用较小质量 min(m_a, m_b) 代替约化质量：当质量悬殊时冲量被严重低估。
只对小质量球"看起来合理"，m_a=m_b=1 时恰好正确（min=1=调和平均），
容易骗过直觉与测试抽样。
"""
from fvector_stub import FVector


def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)

    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)

    # BUG: 约化质量 = 1/(1/m_a+1/m_b)，这里错用 min(m_a, m_b)
    j = -(1.0 + restitution) * vrel_n * min(m_a, m_b)

    v_a_new = v_a + normal * (j / m_a)
    v_b_new = v_b - normal * (j / m_b)
    return v_a_new, v_b_new
