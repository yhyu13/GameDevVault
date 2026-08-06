"""rendering_03_linear_srgb 播种失败解 2 —— 伽马指数错（失败簇：指数 2.2/2.4 颠倒）。

与 golden 的差异：gamma 分支用 1/2.2（或 2.2 近似）代替标准 1/2.4。
后果：中高亮度系统性偏差（0.5 -> 0.7149 vs 标准 0.7355），
仅在 0/1 端点恰好一致，中间全错——正是"看着对、细看色偏"的典型形态。
代码可运行、签名正确，L1 拦不住。
"""

SRGB_THRESHOLD = 0.0031308
SRGB_ALPHA = 0.055
SRGB_1_055 = 1.055
SRGB_12_92 = 12.92
SRGB_GAMMA = 2.2  # 失败点：用 2.2 近似代替标准 2.4


def _encode_single(v):
    if v <= SRGB_THRESHOLD:
        return SRGB_12_92 * v
    return SRGB_1_055 * v ** (1.0 / SRGB_GAMMA) - SRGB_ALPHA


def linear_to_srgb(c):
    out = []
    for v in c:
        v = float(v)
        if v < 0.0:
            v = 0.0
        elif v > 1.0:
            v = 1.0
        out.append(_encode_single(v))
    return tuple(out)
