"""teacher_pool —— Stage 1 teacher 候选池（v1：teacher=self，本会话 LLM 生成）。

候选解按真实模型输出的自然形态生成：大部分正确、部分带微妙 bug（单位/符号/守卫）、
少数 API 违规。TIER 标注意图质量等级（agent-judge 自评依据，人工 golden 校准前不作数）：

- correct_high: 通过 L1+L3，工程化好，judge 8.5
- correct_mid: 通过 L1+L3，工程化一般，judge 6.8
- buggy_subtle: 可通过 L1，行为级 bug，L3 拦（judge 3.5）
- buggy_obvious: 可通过 L1，明显错误，L3 拦（judge 2.0）
- api_bad: L1 直接拦截（签名/禁用模式/结构违规），judge 1.0

插拔：后续接 API teacher 时，POOL 由 generate_candidates.py 按相同契约生成。
"""
import os

PHYS_PROMPT = """实现两球碰撞的冲量解算函数 `resolve_impulse`。输入为 A、B 两球的质量 `m_a`、`m_b`（kg，正有限值），碰撞前速度 `v_a`、`v_b`（cm/s，FVector），碰撞法线 `normal`（从 A 指向 B 的已归一化单位向量），恢复系数 `restitution`（0~1）。
要求：
1. 用标准冲量公式计算法向冲量：`j = -(1 + e) * (v_rel . n) / (1/m_a + 1/m_b)`，其中 `v_rel = v_a - v_b`；
2. 仅当两球正在接近（`v_rel . n < 0`）时施加冲量；正在分离时直接返回原速度（不产生"拉回"冲量）；
3. 冲量施加方向必须正确：A 获得 `+j/m_a * n`，B 获得 `-j/m_b * n`；
4. 返回 `(v_a', v_b')` 两个 FVector，不要修改输入对象；
5. 单位遵循 UE 约定：速度 cm/s、质量 kg、冲量 kg·cm/s；不得自行换算单位。
可用 `from fvector_stub import FVector`（提供 + - * 运算与 .Dot、.x/.y/.z 成员）。不得使用随机数、IO 或第三方库。"""

REND_PROMPT = """你是 UE5 渲染工程师。实现视锥剔除的数学核：给定相机参数构建 6 个视锥平面，并实现点/包围球 vs 视锥的可见性测试。
相机参数：`eye` 相机位置（cm），`forward` 视线方向（单位向量），`up` 上方向（单位向量），`fov_deg` 竖直 FOV（度），`aspect` 宽高比，`near_dist`/`far_dist` 近远裁剪距离（cm，均 > 0）。
实现：
- `build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist)`：返回 6 个平面 `(nx, ny, nz, d)`，顺序为 近/远/左/右/下/上，内法线约定：点 `p` 在视锥内当且仅当对所有平面 `dot(n, p) + d >= 0`（与 UE FPlane 的 W 分量语义一致）。
- `point_inside_frustum(planes, point, radius=0.0)`：`radius=0` 做点测试；`radius>0` 做包围球测试（平面距离 >= -radius 即相交，对应 FConvexVolume::IntersectSphere）。
约束：只用 math；右手系与 UE 一致（forward=视线=视深 Z，up=视高 Y，right = forward × up）；FOV 为竖直 FOV；坐标单位为 cm。平面法线符号错会让"内""外"整体颠倒；近平面距离错会让相机与近平面之间的物体错误可见。"""

POOL = {
    "physics_01_impulse": {
        "phys_01": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_mass
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_02": '''
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
''',
        "phys_03": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return v_a + FVector(), v_b + FVector()
    inv = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_04": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    if (v_a - v_b).Dot(normal) > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    inv_mass_sum = 1.0 / m_a + 1.0 / m_b
    impulse = -(1.0 + restitution) * (v_a - v_b).Dot(normal) / inv_mass_sum
    return v_a + normal * (impulse / m_a), v_b - normal * (impulse / m_b)
''',
        "phys_05": '''
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
''',
        "phys_06": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    rel_vel = v_a - v_b
    if rel_vel.Dot(normal) < 0.0:
        j = -(1.0 + restitution) * rel_vel.Dot(normal) / (1.0 / m_a + 1.0 / m_b)
        return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
    return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
''',
        "phys_07": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return v_a + FVector(0, 0, 0), v_b + FVector(0, 0, 0)
    inv_m = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_m
    va = v_a + normal * (j / m_a)
    vb = v_b - normal * (j / m_b)
    return va, vb
''',
        "phys_08": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    """两球碰撞：标准冲量公式 + 分离守卫 + 不修改输入。"""
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    j = -(1.0 + restitution) * vrel_n / (1.0 / m_a + 1.0 / m_b)
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_09": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    if vrel_n if False else ((v_a - v_b).Dot(normal)) > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    j = -(1.0 + restitution) * (v_a - v_b).Dot(normal) / (1.0 / m_a + 1.0 / m_b)
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_10": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_mass
    v_a_new = v_a + normal * (j / m_a)
    v_b_new = v_b - normal * (j / m_b)
    return v_a_new, v_b_new
''',
        "phys_11": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vn=(v_a-v_b).Dot(normal)
    if vn>0:
        return FVector(v_a.x,v_a.y,v_a.z),FVector(v_b.x,v_b.y,v_b.z)
    j=-(1+restitution)*vn/(1/m_a+1/m_b)
    return v_a+normal*(j/m_a),v_b-normal*(j/m_b)
''',
        "phys_12": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vn = (v_a - v_b).Dot(normal)
    if vn > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    inv = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vn / inv
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_13": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vn = (v_a - v_b).Dot(normal)
    if vn > 0.0:
        return v_a + FVector(0,0,0), v_b + FVector(0,0,0)
    j = -(1.0 + restitution) * vn / (1.0 / m_a + 1.0 / m_b)
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_14": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vn = (v_a - v_b).Dot(normal)
    if vn > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vn / inv_mass
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_15": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vn = (v_a - v_b).Dot(normal)
    if vn > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    j = -(1.0 + restitution) * vn / (1.0 / m_a + 1.0 / m_b)
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_16": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_mass
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_17": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    reduced = min(m_a, m_b)
    j = -(1.0 + restitution) * vrel_n / (1.0 / reduced + 1.0 / reduced)
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_18": '''
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
''',
        "phys_19": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_mass
    return v_a - normal * (j / m_a), v_b + normal * (j / m_b)
''',
        "phys_20": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    j = -(1.0 + restitution) * vrel_n
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_21": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    j = -(1.0 + restitution) * vrel_n / (m_a + m_b)
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_22": '''
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel = (v_a - v_b).Size()
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel / inv_mass
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_23": '''
import random
from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_mass
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
        "phys_24": '''
from fvector_stub import FVector

def resolve_impulse(m1, m2, v1, v2, n, e):
    vrel_n = (v1 - v2).Dot(n)
    if vrel_n > 0.0:
        return FVector(v1.x, v1.y, v1.z), FVector(v2.x, v2.y, v2.z)
    inv = 1.0 / m1 + 1.0 / m2
    j = -(1.0 + e) * vrel_n / inv
    return v1 + n * (j / m1), v2 - n * (j / m2)
''',
        "phys_25": '''
from fvector_stub import FVector

def solve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_mass
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
''',
    },
    "rendering_01_frustum_cull": {
        "rend_01": '''
import math

TOL = 1e-9

def _norm(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if s < TOL:
        return (0.0, 0.0, 0.0)
    return (v[0]/s, v[1]/s, v[2]/s)

def _dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _norm(forward)
    upv = _norm(up)
    right = _norm(_cross(fwd, upv))
    upv = _norm(_cross(right, fwd))
    tan_half = math.tan(math.radians(fov_deg) * 0.5)
    tan_h = tan_half * aspect
    tan_v = tan_half
    eye = (float(eye[0]), float(eye[1]), float(eye[2]))

    def make_plane(n_vec, point_on_plane):
        n = _norm(n_vec)
        d = -_dot(n, point_on_plane)
        return (n[0], n[1], n[2], d)

    near_c = (eye[0]+fwd[0]*near_dist, eye[1]+fwd[1]*near_dist, eye[2]+fwd[2]*near_dist)
    far_c = (eye[0]+fwd[0]*far_dist, eye[1]+fwd[1]*far_dist, eye[2]+fwd[2]*far_dist)
    return [
        make_plane(fwd, near_c),
        make_plane((-fwd[0], -fwd[1], -fwd[2]), far_c),
        make_plane((right[0]+tan_h*fwd[0], right[1]+tan_h*fwd[1], right[2]+tan_h*fwd[2]), eye),
        make_plane((-right[0]+tan_h*fwd[0], -right[1]+tan_h*fwd[1], -right[2]+tan_h*fwd[2]), eye),
        make_plane((upv[0]+tan_v*fwd[0], upv[1]+tan_v*fwd[1], upv[2]+tan_v*fwd[2]), eye),
        make_plane((-upv[0]+tan_v*fwd[0], -upv[1]+tan_v*fwd[1], -upv[2]+tan_v*fwd[2]), eye),
    ]

def point_inside_frustum(planes, point, radius=0.0):
    px, py, pz = float(point[0]), float(point[1]), float(point[2])
    for (nx, ny, nz, d) in planes:
        if nx*px + ny*py + nz*pz + d < -radius:
            return False
    return True
''',
        "rend_02": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    def norm(v):
        s = math.sqrt(sum(c*c for c in v))
        return (0.0, 0.0, 0.0) if s < 1e-9 else tuple(c/s for c in v)
    def dot(a, b):
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
    def cross(a, b):
        return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    fwd = norm(forward)
    upv = norm(up)
    right = norm(cross(fwd, upv))
    upv = norm(cross(right, fwd))
    tan = math.tan(math.radians(fov_deg) / 2.0)
    tan_h, tan_v = tan * aspect, tan
    e = tuple(float(c) for c in eye)
    nc = tuple(e[i] + fwd[i]*near_dist for i in range(3))
    fc = tuple(e[i] + fwd[i]*far_dist for i in range(3))
    def plane(n, p):
        n = norm(n)
        d = -dot(n, p)
        return (n[0], n[1], n[2], d)
    return [
        plane(fwd, nc), plane(tuple(-c for c in fwd), fc),
        plane((right[0]+tan_h*fwd[0], right[1]+tan_h*fwd[1], right[2]+tan_h*fwd[2]), e),
        plane((-right[0]+tan_h*fwd[0], -right[1]+tan_h*fwd[1], -right[2]+tan_h*fwd[2]), e),
        plane((upv[0]+tan_v*fwd[0], upv[1]+tan_v*fwd[1], upv[2]+tan_v*fwd[2]), e),
        plane((-upv[0]+tan_v*fwd[0], -upv[1]+tan_v*fwd[1], -upv[2]+tan_v*fwd[2]), e),
    ]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True
''',
        "rend_03": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    """6 平面（近/远/左/右/下/上），内法线约定 dot(n,p)+d>=0 为内。"""
    fwd = _normalize(forward)
    upv = _normalize(up)
    right = _normalize(_cross(fwd, upv))
    upv = _normalize(_cross(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    th, tv = t * aspect, t
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    return [
        _plane(fwd, nc), _plane((-fwd[0], -fwd[1], -fwd[2]), fc),
        _plane((right[0]+th*fwd[0], right[1]+th*fwd[1], right[2]+th*fwd[2]), e),
        _plane((-right[0]+th*fwd[0], -right[1]+th*fwd[1], -right[2]+th*fwd[2]), e),
        _plane((upv[0]+tv*fwd[0], upv[1]+tv*fwd[1], upv[2]+tv*fwd[2]), e),
        _plane((-upv[0]+tv*fwd[0], -upv[1]+tv*fwd[1], -upv[2]+tv*fwd[2]), e),
    ]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _normalize(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (0.0, 0.0, 0.0) if s < 1e-9 else (v[0]/s, v[1]/s, v[2]/s)

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def _plane(n_vec, p):
    n = _normalize(n_vec)
    d = -(n[0]*p[0] + n[1]*p[1] + n[2]*p[2])
    return (n[0], n[1], n[2], d)
''',
        "rend_04": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) / 2)
    e = [float(c) for c in eye]
    def pl(n, p):
        n = _n(n)
        d = -sum(n[i] * p[i] for i in range(3))
        return (n[0], n[1], n[2], d)
    nf = [e[i] + fwd[i] * near_dist for i in range(3)]
    ff = [e[i] + fwd[i] * far_dist for i in range(3)]
    return [
        pl(fwd, nf),
        pl([-c for c in fwd], ff),
        pl([right[0] + t*aspect*fwd[0], right[1] + t*aspect*fwd[1], right[2] + t*aspect*fwd[2]], e),
        pl([-right[0] + t*aspect*fwd[0], -right[1] + t*aspect*fwd[1], -right[2] + t*aspect*fwd[2]], e),
        pl([upv[0] + t*fwd[0], upv[1] + t*fwd[1], upv[2] + t*fwd[2]], e),
        pl([-upv[0] + t*fwd[0], -upv[1] + t*fwd[1], -upv[2] + t*fwd[2]], e),
    ]

def point_inside_frustum(planes, point, radius=0.0):
    px, py, pz = point
    for (nx, ny, nz, d) in planes:
        if nx*px + ny*py + nz*pz + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_05": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    f = _u(forward); u = _u(up)
    r = _u(_x(f, u)); u = _u(_x(r, f))
    k = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    def p(n, o):
        n = _u(n); d = -(n[0]*o[0] + n[1]*o[1] + n[2]*o[2])
        return (n[0], n[1], n[2], d)
    ncp = (e[0]+f[0]*near_dist, e[1]+f[1]*near_dist, e[2]+f[2]*near_dist)
    fcp = (e[0]+f[0]*far_dist, e[1]+f[1]*far_dist, e[2]+f[2]*far_dist)
    hx, hy = k*aspect, k
    return [p(f, ncp), p((-f[0], -f[1], -f[2]), fcp),
            p((r[0]+hx*f[0], r[1]+hx*f[1], r[2]+hx*f[2]), e),
            p((-r[0]+hx*f[0], -r[1]+hx*f[1], -r[2]+hx*f[2]), e),
            p((u[0]+hy*f[0], u[1]+hy*f[1], u[2]+hy*f[2]), e),
            p((-u[0]+hy*f[0], -u[1]+hy*f[1], -u[2]+hy*f[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _u(v):
    s = (v[0]*v[0] + v[1]*v[1] + v[2]*v[2]) ** 0.5
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _x(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_06": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    f = _norm(forward)
    upv = _norm(up)
    r = _norm(_cross(f, upv))
    upv = _norm(_cross(r, f))
    tan = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    near = tuple(e[i] + f[i] * near_dist for i in range(3))
    far = tuple(e[i] + f[i] * far_dist for i in range(3))
    nf = _norm((-f[0], -f[1], -f[2]))
    lf = _norm((r[0] + tan*aspect*f[0], r[1] + tan*aspect*f[1], r[2] + tan*aspect*f[2]))
    rf = _norm((-r[0] + tan*aspect*f[0], -r[1] + tan*aspect*f[1], -r[2] + tan*aspect*f[2]))
    bf = _norm((upv[0] + tan*f[0], upv[1] + tan*f[1], upv[2] + tan*f[2]))
    tf = _norm((-upv[0] + tan*f[0], -upv[1] + tan*f[1], -upv[2] + tan*f[2]))
    planes = []
    for n, p in [(f, near), (nf, far), (lf, e), (rf, e), (bf, e), (tf, e)]:
        d = -(n[0]*p[0] + n[1]*p[1] + n[2]*p[2])
        planes.append((n[0], n[1], n[2], d))
    return planes

def point_inside_frustum(planes, point, radius=0.0):
    px, py, pz = point
    for (nx, ny, nz, d) in planes:
        if nx*px + ny*py + nz*pz + d < -radius:
            return False
    return True

def _norm(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_07": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    """内法线 6 平面。fov 为竖直 FOV。"""
    f = _n(forward)
    u = _n(up)
    r = _n(_c(f, u))
    u = _n(_c(r, f))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0] + f[0]*near_dist, e[1] + f[1]*near_dist, e[2] + f[2]*near_dist)
    fc = (e[0] + f[0]*far_dist, e[1] + f[1]*far_dist, e[2] + f[2]*far_dist)
    out = []
    for n, p in ((f, nc), ((-f[0], -f[1], -f[2]), fc),
                 ((r[0]+t*aspect*f[0], r[1]+t*aspect*f[1], r[2]+t*aspect*f[2]), e),
                 ((-r[0]+t*aspect*f[0], -r[1]+t*aspect*f[1], -r[2]+t*aspect*f[2]), e),
                 ((u[0]+t*f[0], u[1]+t*f[1], u[2]+t*f[2]), e),
                 ((-u[0]+t*f[0], -u[1]+t*f[1], -u[2]+t*f[2]), e)):
        n = _n(n)
        d = -(n[0]*p[0] + n[1]*p[1] + n[2]*p[2])
        out.append((n[0], n[1], n[2], d))
    return out

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (0.0, 0.0, 0.0) if s < 1e-9 else (v[0]/s, v[1]/s, v[2]/s)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_08": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _norm(forward)
    upv = _norm(_cross(_norm(_cross(fwd, _norm(up))), fwd))
    right = _norm(_cross(fwd, upv))
    t = math.tan(math.radians(fov_deg) * 0.5)
    th, tv = t * aspect, t
    e = tuple(float(c) for c in eye)
    near_p = tuple(e[i] + fwd[i]*near_dist for i in range(3))
    far_p = tuple(e[i] + fwd[i]*far_dist for i in range(3))
    planes = []
    for n_vec, pt in ((fwd, near_p), ((-fwd[0], -fwd[1], -fwd[2]), far_p),
                      ((right[0]+th*fwd[0], right[1]+th*fwd[1], right[2]+th*fwd[2]), e),
                      ((-right[0]+th*fwd[0], -right[1]+th*fwd[1], -right[2]+th*fwd[2]), e),
                      ((upv[0]+tv*fwd[0], upv[1]+tv*fwd[1], upv[2]+tv*fwd[2]), e),
                      ((-upv[0]+tv*fwd[0], -upv[1]+tv*fwd[1], -upv[2]+tv*fwd[2]), e)):
        n = _norm(n_vec)
        d = -(n[0]*pt[0] + n[1]*pt[1] + n[2]*pt[2])
        planes.append((n[0], n[1], n[2], d))
    return planes

def point_inside_frustum(planes, point, radius=0.0):
    px, py, pz = point[0], point[1], point[2]
    for (nx, ny, nz, d) in planes:
        if nx*px + ny*py + nz*pz + d < -radius:
            return False
    return True

def _norm(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_09": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _u(forward)
    upv = _u(up)
    right = _u(_x(fwd, upv))
    upv = _u(_x(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    def mk(nv, pt):
        nv = _u(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*pt[0]+nv[1]*pt[1]+nv[2]*pt[2]))
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _u(v):
    s = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _x(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_10": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    """视锥 6 平面（近/远/左/右/下/上），点法式 dot(n,p)+d=0，内法线。"""
    fwd = _norm(forward)
    upv = _norm(up)
    right = _norm(_cross(fwd, upv))
    upv = _norm(_cross(right, fwd))
    tan_half = math.tan(math.radians(fov_deg) * 0.5)
    e = tuple(float(c) for c in eye)
    near_c = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    far_c = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)

    def plane(n, p):
        n = _norm(n)
        d = -(n[0]*p[0] + n[1]*p[1] + n[2]*p[2])
        return (n[0], n[1], n[2], d)

    planes = [
        plane(fwd, near_c),
        plane((-fwd[0], -fwd[1], -fwd[2]), far_c),
        plane((right[0] + tan_half*aspect*fwd[0], right[1] + tan_half*aspect*fwd[1], right[2] + tan_half*aspect*fwd[2]), e),
        plane((-right[0] + tan_half*aspect*fwd[0], -right[1] + tan_half*aspect*fwd[1], -right[2] + tan_half*aspect*fwd[2]), e),
        plane((upv[0] + tan_half*fwd[0], upv[1] + tan_half*fwd[1], upv[2] + tan_half*fwd[2]), e),
        plane((-upv[0] + tan_half*fwd[0], -upv[1] + tan_half*fwd[1], -upv[2] + tan_half*fwd[2]), e),
    ]
    return planes

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _norm(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_11": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward); upv = _n(up)
    right = _n(_c(fwd, upv)); upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    def mk(n, p):
        n = _n(n); return (n[0], n[1], n[2], -sum(n[i]*p[i] for i in range(3)))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_12": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    f = _u(forward); u = _u(up)
    r = _u(_x(f, u)); u = _u(_x(r, f))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+f[0]*near_dist, e[1]+f[1]*near_dist, e[2]+f[2]*near_dist)
    fc = (e[0]+f[0]*far_dist, e[1]+f[1]*far_dist, e[2]+f[2]*far_dist)
    planes = []
    for nv, p in [(f, nc), ((-f[0], -f[1], -f[2]), fc),
                  ((r[0]+t*aspect*f[0], r[1]+t*aspect*f[1], r[2]+t*aspect*f[2]), e),
                  ((-r[0]+t*aspect*f[0], -r[1]+t*aspect*f[1], -r[2]+t*aspect*f[2]), e),
                  ((u[0]+t*f[0], u[1]+t*f[1], u[2]+t*f[2]), e),
                  ((-u[0]+t*f[0], -u[1]+t*f[1], -u[2]+t*f[2]), e)]:
        nv = _u(nv)
        planes.append((nv[0], nv[1], nv[2], -(nv[0]*p[0]+nv[1]*p[1]+nv[2]*p[2])))
    return planes

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _u(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _x(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_13": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    f = _norm(forward); u = _norm(up)
    r = _norm(_cross(f, u)); u = _norm(_cross(r, f))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = [float(x) for x in eye]
    out = []
    for nv, pt in [(f, [e[0]+f[0]*near_dist, e[1]+f[1]*near_dist, e[2]+f[2]*near_dist]),
                   ((-f[0], -f[1], -f[2]), [e[0]+f[0]*far_dist, e[1]+f[1]*far_dist, e[2]+f[2]*far_dist]),
                   ((r[0]+t*aspect*f[0], r[1]+t*aspect*f[1], r[2]+t*aspect*f[2]), e),
                   ((-r[0]+t*aspect*f[0], -r[1]+t*aspect*f[1], -r[2]+t*aspect*f[2]), e),
                   ((u[0]+t*f[0], u[1]+t*f[1], u[2]+t*f[2]), e),
                   ((-u[0]+t*f[0], -u[1]+t*f[1], -u[2]+t*f[2]), e)]:
        nv = _norm(nv)
        out.append((nv[0], nv[1], nv[2], -(nv[0]*pt[0]+nv[1]*pt[1]+nv[2]*pt[2])))
    return out

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _norm(v):
    s = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_14": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    def pl(n, p):
        n = _n(n)
        return (n[0], n[1], n[2], -(n[0]*p[0] + n[1]*p[1] + n[2]*p[2]))
    return [pl(fwd, nc), pl((-fwd[0], -fwd[1], -fwd[2]), fc),
            pl((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            pl((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            pl((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            pl((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_15": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    f = _u(forward); u = _u(up)
    r = _u(_x(f, u)); u = _u(_x(r, f))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+f[0]*near_dist, e[1]+f[1]*near_dist, e[2]+f[2]*near_dist)
    fc = (e[0]+f[0]*far_dist, e[1]+f[1]*far_dist, e[2]+f[2]*far_dist)
    def mk(nv, p):
        nv = _u(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2]))
    return [mk(f, nc), mk((-f[0], -f[1], -f[2]), fc),
            mk((r[0]+t*aspect*f[0], r[1]+t*aspect*f[1], r[2]+t*aspect*f[2]), e),
            mk((-r[0]+t*aspect*f[0], -r[1]+t*aspect*f[1], -r[2]+t*aspect*f[2]), e),
            mk((u[0]+t*f[0], u[1]+t*f[1], u[2]+t*f[2]), e),
            mk((-u[0]+t*f[0], -u[1]+t*f[1], -u[2]+t*f[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _u(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _x(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_16": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    def mk(nv, p):
        nv = _n(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2]))
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    return [mk(fwd, e),
            mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_17": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    def mk(nv, p):
        nv = _n(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2]))
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < 0.0:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_18": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    def mk(nv, p):
        nv = _n(nv)
        return (nv[0], nv[1], nv[2], nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2])
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_19": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    def mk(nv, p):
        nv = _n(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2]))
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*fwd[0], right[1]+t*fwd[1], right[2]+t*fwd[2]), e),
            mk((-right[0]+t*fwd[0], -right[1]+t*fwd[1], -right[2]+t*fwd[2]), e),
            mk((upv[0]+t/aspect*fwd[0], upv[1]+t/aspect*fwd[1], upv[2]+t/aspect*fwd[2]), e),
            mk((-upv[0]+t/aspect*fwd[0], -upv[1]+t/aspect*fwd[1], -upv[2]+t/aspect*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_20": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(upv, fwd))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    def mk(nv, p):
        nv = _n(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2]))
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_21": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    def mk(nv, p):
        nv = _n(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2]))
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*fwd[0], right[1]+t*fwd[1], right[2]+t*fwd[2]), e),
            mk((-right[0]+t*fwd[0], -right[1]+t*fwd[1], -right[2]+t*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_22": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    fc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    def mk(nv, p):
        nv = _n(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2]))
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_23": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    def mk(nv, p):
        nv = _n(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2]))
    planes = [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
              mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
              mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
              mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e)]
    return planes

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_24": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    def mk(nv, p):
        nv = _n(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2]))
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def _n(v):
    s = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
        "rend_25": '''
import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    def mk(nv, p):
        nv = _n(nv)
        return {"n": nv, "d": -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2])}
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for pl in planes:
        n = pl["n"]
        if n[0]*point[0] + n[1]*point[1] + n[2]*point[2] + pl["d"] < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
''',
    },
}

TIER = {
    "physics_01_impulse": {
        "phys_01": "correct_high", "phys_02": "correct_high", "phys_03": "correct_high",
        "phys_04": "correct_high", "phys_05": "correct_high", "phys_06": "correct_high",
        "phys_07": "correct_high", "phys_08": "correct_high", "phys_09": "correct_high",
        "phys_10": "correct_high",
        "phys_11": "correct_mid", "phys_12": "correct_mid", "phys_13": "correct_mid",
        "phys_14": "correct_mid", "phys_15": "correct_mid",
        "phys_16": "buggy_subtle", "phys_17": "buggy_subtle", "phys_18": "buggy_subtle",
        "phys_19": "buggy_subtle",
        "phys_20": "buggy_obvious", "phys_21": "buggy_obvious", "phys_22": "buggy_obvious",
        "phys_23": "api_bad", "phys_24": "api_bad", "phys_25": "api_bad",
    },
    "rendering_01_frustum_cull": {
        "rend_01": "correct_high", "rend_02": "correct_high", "rend_03": "correct_high",
        "rend_04": "correct_high", "rend_05": "correct_high", "rend_06": "correct_high",
        "rend_07": "correct_high", "rend_08": "correct_high", "rend_09": "correct_high",
        "rend_10": "correct_high",
        "rend_11": "correct_mid", "rend_12": "correct_mid", "rend_13": "correct_mid",
        "rend_14": "correct_mid", "rend_15": "correct_mid",
        "rend_16": "buggy_subtle", "rend_17": "buggy_subtle", "rend_18": "buggy_subtle",
        "rend_19": "buggy_subtle",
        "rend_20": "buggy_obvious", "rend_21": "buggy_obvious", "rend_22": "buggy_obvious",
        "rend_23": "api_bad", "rend_24": "api_bad", "rend_25": "api_bad",
    },
}

# agent-judge 自评映射（self 模式；人工 golden 校准前不作数）
JUDGE_SCORE = {
    "correct_high": 8.5,
    "correct_mid": 6.8,
    "buggy_subtle": 3.5,
    "buggy_obvious": 2.0,
    "api_bad": 1.0,
}

PROMPTS = {
    "physics_01_impulse": PHYS_PROMPT,
    "rendering_01_frustum_cull": REND_PROMPT,
}

MODEL_SIZE = {
    "physics_01_impulse": "0.8B",
    "rendering_01_frustum_cull": "0.8B",
}

DOMAIN = {
    "physics_01_impulse": "physics",
    "rendering_01_frustum_cull": "rendering",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- merge 扩展池（其余 7 任务）----
from teacher_pool_extra import POOL as _EXTRA_POOL, TIER as _EXTRA_TIER, PROMPTS as _EXTRA_PROMPTS, MODEL_SIZE as _EXTRA_MODEL_SIZE, DOMAIN as _EXTRA_DOMAIN  # noqa: E402
from teacher_pool_fx import POOL as _FX_POOL, TIER as _FX_TIER, PROMPTS as _FX_PROMPTS, MODEL_SIZE as _FX_MODEL_SIZE, DOMAIN as _FX_DOMAIN  # noqa: E402

POOL.update(_EXTRA_POOL)
POOL.update(_FX_POOL)
TIER.update(_EXTRA_TIER)
TIER.update(_FX_TIER)
PROMPTS.update(_EXTRA_PROMPTS)
PROMPTS.update(_FX_PROMPTS)
MODEL_SIZE.update(_EXTRA_MODEL_SIZE)
MODEL_SIZE.update(_FX_MODEL_SIZE)
DOMAIN.update(_EXTRA_DOMAIN)
DOMAIN.update(_FX_DOMAIN)
