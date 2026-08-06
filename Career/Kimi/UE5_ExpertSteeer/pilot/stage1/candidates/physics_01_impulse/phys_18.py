import struct
from fvector_stub import FVector

def _f32(x):
    return struct.unpack('f', struct.pack('f', x))[0]

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = _f32((v_a - v_b).Dot(normal))
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    inv_mass = _f32(1.0 / m_a + 1.0 / m_b)
    j = _f32(-(1.0 + restitution) * vrel_n / inv_mass)
    va = FVector(_f32(v_a.x + normal.x * (j / m_a)),
                 _f32(v_a.y + normal.y * (j / m_a)),
                 _f32(v_a.z + normal.z * (j / m_a)))
    vb = FVector(_f32(v_b.x - normal.x * (j / m_b)),
                 _f32(v_b.y - normal.y * (j / m_b)),
                 _f32(v_b.z - normal.z * (j / m_b)))
    return va, vb
