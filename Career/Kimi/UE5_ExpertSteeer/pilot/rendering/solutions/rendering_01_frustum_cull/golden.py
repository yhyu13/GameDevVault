"""rendering_01_frustum_cull golden —— 视锥剔除点/包围球测试（6 平面，内法线约定）。

UE C++ 形态（Stage 1 迁移目标）:
- FConvexVolume::Intersect( FBoxSphereBounds ) / UWorld::IsPointInFrustum
- 视锥平面由 UGameViewportClient / ViewFrustum（FrustumPlanes[6]）构建；
  shader 侧对应 Common.ush 的 View.SFrustumLeftPlane / RightPlane / TopPlane / BottomPlane / NearPlane / FarPlane。
- 约定：dot(n, p) + d >= 0 为视锥内（内法线），与 UE FPlane 的 W 分量等价。

本 pilot 用纯 Python + tuple 表示平面 (nx, ny, nz, d)，Stage 1 迁移为 FPlane/FConvexVolume。
"""

import math

TOL = 1e-9


def _norm(v):
    s = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if s < TOL:
        return (0.0, 0.0, 0.0)
    return (v[0] / s, v[1] / s, v[2] / s)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    """按相机参数构建 6 个平面，返回 [(nx,ny,nz,d), ...]，顺序：近/远/左/右/下/上。

    坐标系与 UE 一致：forward=视线方向(+Z 视深)、up=上(+Y 视高)、right=forward x up。
    fov_deg 为竖直 FOV；aspect = 宽/高。约束：fov_deg in (0,180)，near/far > 0。
    """
    fwd = _norm(forward)
    upv = _norm(up)
    right = _norm(_cross(fwd, upv))
    upv = _norm(_cross(right, fwd))  # 正交化修正

    tan_half = math.tan(math.radians(fov_deg) * 0.5)
    tan_h = tan_half * aspect
    tan_v = tan_half

    eye = (float(eye[0]), float(eye[1]), float(eye[2]))

    # 视空间不等式：near <= dot(fwd, p-eye) <= far，
    #              |dot(right, p-eye)| <= dot(fwd,p-eye)*tanH,
    #              |dot(up, p-eye)|   <= dot(fwd,p-eye)*tanV
    # 内法线平面：n = (0,0,-1) 方向法线组合，d = -dot(n, eye)（点法式）。
    near_center = (eye[0] + fwd[0] * near_dist,
                   eye[1] + fwd[1] * near_dist,
                   eye[2] + fwd[2] * near_dist)
    far_center = (eye[0] + fwd[0] * far_dist,
                  eye[1] + fwd[1] * far_dist,
                  eye[2] + fwd[2] * far_dist)

    def make_plane(n_vec, point_on_plane):
        n = _norm(n_vec)
        d = -_dot(n, point_on_plane)
        return (n[0], n[1], n[2], d)

    planes = [
        make_plane(fwd, near_center),            # 近
        make_plane((-fwd[0], -fwd[1], -fwd[2]), far_center),  # 远
        make_plane((right[0] + tan_h * fwd[0],   # 左
                    right[1] + tan_h * fwd[1],
                    right[2] + tan_h * fwd[2]), eye),
        make_plane((-right[0] + tan_h * fwd[0],  # 右
                    -right[1] + tan_h * fwd[1],
                    -right[2] + tan_h * fwd[2]), eye),
        make_plane((upv[0] + tan_v * fwd[0],     # 下
                    upv[1] + tan_v * fwd[1],
                    upv[2] + tan_v * fwd[2]), eye),
        make_plane((-upv[0] + tan_v * fwd[0],    # 上
                    -upv[1] + tan_v * fwd[1],
                    -upv[2] + tan_v * fwd[2]), eye),
    ]
    return planes


def point_inside_frustum(planes, point, radius=0.0):
    """点/包围球 vs 6 平面。radius>0 时做球测试（距离 >= -radius 视为相交）。
    语义对应 UE FConvexVolume::IntersectSphere。
    """
    px, py, pz = float(point[0]), float(point[1]), float(point[2])
    for (nx, ny, nz, d) in planes:
        if nx * px + ny * py + nz * pz + d < -radius:
            return False
    return True
