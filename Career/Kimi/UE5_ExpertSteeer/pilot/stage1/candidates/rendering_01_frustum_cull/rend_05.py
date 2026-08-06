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
