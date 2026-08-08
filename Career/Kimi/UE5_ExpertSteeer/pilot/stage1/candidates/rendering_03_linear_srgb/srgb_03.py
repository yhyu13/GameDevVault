import math

TH = 0.0031308
K = 12.92


def _enc(x):
    x = max(0.0, min(1.0, x))
    if x <= TH:
        return K * x
    return 1.055 * x ** (1.0 / 2.4) - 0.055


def linear_to_srgb(c):
    """逐通道独立编码：c<=0.0031308 线性段，否则幂段。"""
    return tuple(_enc(v) for v in c)
