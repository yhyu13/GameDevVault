from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vn=(v_a-v_b).Dot(normal)
    if vn>0:
        return FVector(v_a.x,v_a.y,v_a.z),FVector(v_b.x,v_b.y,v_b.z)
    j=-(1+restitution)*vn/(1/m_a+1/m_b)
    return v_a+normal*(j/m_a),v_b-normal*(j/m_b)
