import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        out.append(1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
