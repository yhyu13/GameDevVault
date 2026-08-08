import math

def linear_to_srgb(c):
    """linear -> sRGB（每通道分段，IEC 61966-2-1）。"""
    return tuple(
        12.92 * max(0.0, min(1.0, v)) if max(0.0, min(1.0, v)) <= 0.0031308
        else 1.055 * max(0.0, min(1.0, v)) ** (1.0 / 2.4) - 0.055
        for v in c
    )
