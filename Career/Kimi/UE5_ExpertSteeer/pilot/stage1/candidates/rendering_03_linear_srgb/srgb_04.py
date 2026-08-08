import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        if v <= 0.0031308:
            out.append(12.92 * v)
        else:
            out.append(1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
