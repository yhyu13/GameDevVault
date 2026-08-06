"""rendering_03_linear_srgb golden —— linear -> sRGB 转换（IEC 61966-2-1 标准 EOTF）。

UE C++/shader 形态（Stage 1 迁移目标）:
- shader: Common.ush 的 LinearToSrgb / LinearToSrgbLUT（色调映射后写回 sRGB RT 前）
- C++: 手动逐像素转换（FLinearColor -> FColor 的量化路径），或 SRGB 标志被误设时的双伽马
- 约定: 输入为 [0,1] linear 值；输出 [0,1] sRGB 编码值；越界输入先 Clamp。
- 失败簇映射: 双伽马（材质/后处理在 linear 空间再转一次 sRGB）、指数用 2.2/2.4 颠倒。

标准常数（IEC 61966-2-1）:
    c <= 0.0031308 : 12.92 * c
    c >  0.0031308 : 1.055 * c^(1/2.4) - 0.055
"""

SRGB_THRESHOLD = 0.0031308
SRGB_ALPHA = 0.055
SRGB_1_055 = 1.055
SRGB_12_92 = 12.92
SRGB_GAMMA = 2.4


def _encode_single(v):
    if v <= SRGB_THRESHOLD:
        return SRGB_12_92 * v
    return SRGB_1_055 * v ** (1.0 / SRGB_GAMMA) - SRGB_ALPHA


def linear_to_srgb(c):
    """输入 (r, g, b) linear 值，逐通道转 sRGB。越界输入 Clamp 到 [0,1]。"""
    out = []
    for v in c:
        v = float(v)
        if v < 0.0:
            v = 0.0
        elif v > 1.0:
            v = 1.0
        out.append(_encode_single(v))
    return tuple(out)
