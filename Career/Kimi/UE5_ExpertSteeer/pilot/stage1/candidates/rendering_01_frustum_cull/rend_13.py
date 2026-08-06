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
