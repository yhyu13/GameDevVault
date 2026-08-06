"""两球碰撞冲量解算 —— 播种失败解 #3：float32 精度截断（失败簇：质量与速度尺度/数值精度）。

把关键中间量全部 cast 到 float32（模仿"为性能优化把物理降精度"的常见做法）。
公式与结构完全正确；低速度下误差 < 1e-5 肉眼不可见，但高速（1e5 cm/s，
UE 中子弹/高速抛射物常见量级）或非整数法线分量时误差达 1e-2 cm/s，
超过 KINDA_SMALL_NUMBER=1e-4 容差。静态读码几乎无法判定其错误。
"""
import struct

from fvector_stub import FVector


def _f32(v):
    """把 float 截断到 float32（struct 打包，无第三方依赖）。"""
    return struct.unpack('f', struct.pack('f', v))[0]


def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = _f32((v_a - v_b).Dot(normal))

    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)

    inv_mass = _f32(_f32(1.0 / m_a) + _f32(1.0 / m_b))
    j = _f32(-_f32(_f32(1.0 + restitution) * vrel_n) / inv_mass)

    v_a_new = v_a + normal * _f32(j / m_a)
    v_b_new = v_b - normal * _f32(j / m_b)
    return v_a_new, v_b_new
