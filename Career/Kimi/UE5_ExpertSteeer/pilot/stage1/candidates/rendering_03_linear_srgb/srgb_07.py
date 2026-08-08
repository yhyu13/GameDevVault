import math

def linear_to_srgb(c):
    res = []
    for v in c:
        v = max(0.0, min(1.0, v))
        if v <= 0.0031308:
            res.append(12.92 * v)
        else:
            res.append(1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(res)
