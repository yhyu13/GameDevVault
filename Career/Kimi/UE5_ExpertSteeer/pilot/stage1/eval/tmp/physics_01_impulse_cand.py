from fvector_stub import FVector
from fvector_stub import FVector

def resolve_impulse(v_a, v_b, normal, m_a, m_b, restitution):
    """
    计算两球碰撞的冲量解算函数。
    
    参数:
    v_a, v_b: FVector - 碰撞前速度
    normal: FVector - 法线向量 (从 A 指向 B)
    m_a, m_b: float - 两球质量 (kg)
    restitution: float - 恢复系数 (0~1)
    
    返回:
    FVector - 碰撞后速度
    """
    # 计算相对速度
    v_rel = v_a - v_b
    
    # 计算法向分量
    v_rel_dot_n = v_rel.dot(normal)
    
    # 检查是否正在接近
    if v_rel_dot_n >= 0:
        return v_a, v_b
    
    # 计算法向冲量
    impulse = -(1 + restitution) * v_rel_dot_n / (1 / m_a + 1 / m_b)
    
    # 施加冲量
    v_a = v_a + impulse / m_a * normal
    v_b = v_b - impulse / m_b * normal
    
    return v_a, v_b
