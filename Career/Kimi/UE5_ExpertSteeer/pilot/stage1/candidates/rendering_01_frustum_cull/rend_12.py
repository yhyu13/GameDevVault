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
