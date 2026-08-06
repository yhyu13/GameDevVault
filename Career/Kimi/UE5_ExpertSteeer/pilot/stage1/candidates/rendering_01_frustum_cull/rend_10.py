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
