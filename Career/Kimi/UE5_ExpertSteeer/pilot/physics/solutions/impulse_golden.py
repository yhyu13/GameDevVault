"""两球碰撞冲量解算（restitution）—— 黄金解。

UE C++ 形态（Stage 1 迁移目标）：
- FVector 对应 UE::Math::TVector<float>（UE5 中 FVector）
- 对应 Chaos 刚体求解器中 ApplyImpulse 前的相对速度投影与冲量计算
  （类似 FChaosSolver 约束求解的 impulse 核）

单位约定（UE 世界单位）：速度 cm/s，质量 kg，冲量 kg*cm/s，法线为归一化单位向量。
"""
from fvector_stub import FVector


def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    """两球碰撞后速度 (v_a', v_b')。

    冲量公式：j = -(1 + e) * (v_rel . n) / (1/m_a + 1/m_b)
    仅当两球相向运动（v_rel . n < 0，即法线方向正在接近）时施加冲量；
    分离情形（v_rel . n > 0）直接返回原速度，不产生冲量。
    normal 为从 A 指向 B 的归一化法线。
    """
    vrel_n = (v_a - v_b).Dot(normal)

    # 正在分离：不施加冲量（物理上已离开碰撞阶段）
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)

    # 约化质量的倒数 = 1/m_a + 1/m_b（调和平均）
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_mass

    v_a_new = v_a + normal * (j / m_a)
    v_b_new = v_b - normal * (j / m_b)
    return v_a_new, v_b_new
