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
