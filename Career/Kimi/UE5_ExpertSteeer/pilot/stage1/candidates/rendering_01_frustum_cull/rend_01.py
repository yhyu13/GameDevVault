import math

TOL = 1e-9

def _norm(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if s < TOL:
        return (0.0, 0.0, 0.0)
    return (v[0]/s, v[1]/s, v[2]/s)

def _dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _norm(forward)
    upv = _norm(up)
    right = _norm(_cross(fwd, upv))
    upv = _norm(_cross(right, fwd))
    tan_half = math.tan(math.radians(fov_deg) * 0.5)
    tan_h = tan_half * aspect
    tan_v = tan_half
    eye = (float(eye[0]), float(eye[1]), float(eye[2]))

    def make_plane(n_vec, point_on_plane):
        n = _norm(n_vec)
        d = -_dot(n, point_on_plane)
        return (n[0], n[1], n[2], d)

    near_c = (eye[0]+fwd[0]*near_dist, eye[1]+fwd[1]*near_dist, eye[2]+fwd[2]*near_dist)
    far_c = (eye[0]+fwd[0]*far_dist, eye[1]+fwd[1]*far_dist, eye[2]+fwd[2]*far_dist)
    return [
        make_plane(fwd, near_c),
        make_plane((-fwd[0], -fwd[1], -fwd[2]), far_c),
        make_plane((right[0]+tan_h*fwd[0], right[1]+tan_h*fwd[1], right[2]+tan_h*fwd[2]), eye),
        make_plane((-right[0]+tan_h*fwd[0], -right[1]+tan_h*fwd[1], -right[2]+tan_h*fwd[2]), eye),
        make_plane((upv[0]+tan_v*fwd[0], upv[1]+tan_v*fwd[1], upv[2]+tan_v*fwd[2]), eye),
        make_plane((-upv[0]+tan_v*fwd[0], -upv[1]+tan_v*fwd[1], -upv[2]+tan_v*fwd[2]), eye),
    ]

def point_inside_frustum(planes, point, radius=0.0):
    px, py, pz = float(point[0]), float(point[1]), float(point[2])
    for (nx, ny, nz, d) in planes:
        if nx*px + ny*py + nz*pz + d < -radius:
            return False
    return True
