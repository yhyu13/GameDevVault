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
