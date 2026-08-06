import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _norm(forward)
    upv = _norm(_cross(_norm(_cross(fwd, _norm(up))), fwd))
    right = _norm(_cross(fwd, upv))
    t = math.tan(math.radians(fov_deg) * 0.5)
    th, tv = t * aspect, t
    e = tuple(float(c) for c in eye)
    near_p = tuple(e[i] + fwd[i]*near_dist for i in range(3))
    far_p = tuple(e[i] + fwd[i]*far_dist for i in range(3))
    planes = []
    for n_vec, pt in ((fwd, near_p), ((-fwd[0], -fwd[1], -fwd[2]), far_p),
                      ((right[0]+th*fwd[0], right[1]+th*fwd[1], right[2]+th*fwd[2]), e),
                      ((-right[0]+th*fwd[0], -right[1]+th*fwd[1], -right[2]+th*fwd[2]), e),
                      ((upv[0]+tv*fwd[0], upv[1]+tv*fwd[1], upv[2]+tv*fwd[2]), e),
                      ((-upv[0]+tv*fwd[0], -upv[1]+tv*fwd[1], -upv[2]+tv*fwd[2]), e)):
        n = _norm(n_vec)
        d = -(n[0]*pt[0] + n[1]*pt[1] + n[2]*pt[2])
        planes.append((n[0], n[1], n[2], d))
    return planes

def point_inside_frustum(planes, point, radius=0.0):
    px, py, pz = point[0], point[1], point[2]
    for (nx, ny, nz, d) in planes:
        if nx*px + ny*py + nz*pz + d < -radius:
            return False
    return True

def _norm(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
