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
