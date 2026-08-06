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
