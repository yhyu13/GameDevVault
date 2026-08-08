import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = min(max(v, 0.0), 1.0)
        out.append(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
