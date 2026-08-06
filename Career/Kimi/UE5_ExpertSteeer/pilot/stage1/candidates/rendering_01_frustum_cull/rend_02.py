import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    def norm(v):
        s = math.sqrt(sum(c*c for c in v))
        return (0.0, 0.0, 0.0) if s < 1e-9 else tuple(c/s for c in v)
    def dot(a, b):
        return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
    def cross(a, b):
        return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    fwd = norm(forward)
    upv = norm(up)
    right = norm(cross(fwd, upv))
    upv = norm(cross(right, fwd))
    tan = math.tan(math.radians(fov_deg) / 2.0)
    tan_h, tan_v = tan * aspect, tan
    e = tuple(float(c) for c in eye)
    nc = tuple(e[i] + fwd[i]*near_dist for i in range(3))
    fc = tuple(e[i] + fwd[i]*far_dist for i in range(3))
    def plane(n, p):
        n = norm(n)
        d = -dot(n, p)
        return (n[0], n[1], n[2], d)
    return [
        plane(fwd, nc), plane(tuple(-c for c in fwd), fc),
        plane((right[0]+tan_h*fwd[0], right[1]+tan_h*fwd[1], right[2]+tan_h*fwd[2]), e),
        plane((-right[0]+tan_h*fwd[0], -right[1]+tan_h*fwd[1], -right[2]+tan_h*fwd[2]), e),
        plane((upv[0]+tan_v*fwd[0], upv[1]+tan_v*fwd[1], upv[2]+tan_v*fwd[2]), e),
        plane((-upv[0]+tan_v*fwd[0], -upv[1]+tan_v*fwd[1], -upv[2]+tan_v*fwd[2]), e),
    ]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True
