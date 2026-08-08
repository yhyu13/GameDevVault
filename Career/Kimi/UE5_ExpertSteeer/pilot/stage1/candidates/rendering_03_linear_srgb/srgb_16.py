import math

def _enc(v):
    v = max(0.0, min(1.0, v))
    return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055


def linear_to_srgb(c):
    return tuple(_enc(_enc(v)) for v in c)
