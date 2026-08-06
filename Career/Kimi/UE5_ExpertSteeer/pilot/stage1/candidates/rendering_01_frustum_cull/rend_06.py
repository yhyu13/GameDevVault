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
