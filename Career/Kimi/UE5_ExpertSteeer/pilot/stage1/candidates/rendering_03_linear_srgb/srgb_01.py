import math

THRESHOLD = 0.0031308
LINEAR_COEF = 12.92
A = 1.055
B = 0.055
GAMMA = 2.4


def linear_to_srgb(c):
    """IEC 61966-2-1：线性段 + 幂段，越界先 clamp。"""
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        if v <= THRESHOLD:
            out.append(LINEAR_COEF * v)
        else:
            out.append(A * v ** (1.0 / GAMMA) - B)
    return tuple(out)
