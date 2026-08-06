"""rendering_03_linear_srgb 播种失败解 1 —— 双伽马（失败簇：sRGB vs linear 双伽马）。

与 golden 的差异：对输入先做一次 sRGB 编码，再对结果做第二次 sRGB 编码
（即把已经编码的值当作 linear 再转一次）。
后果：输出整体过亮（0.5 -> 0.735 被二次映射到 ~0.879），色调严重错误——
对应 UE 里"linear 空间材质把输出当 sRGB 又转一遍"或"RT 标了 sRGB 又在 shader 手动转"。
代码可运行、签名正确，L1 拦不住。
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
    out = []
    for v in c:
        v = float(v)
        if v < 0.0:
            v = 0.0
        elif v > 1.0:
            v = 1.0
        # 失败点：二次编码（双伽马）
        out.append(_encode_single(_encode_single(v)))
    return tuple(out)
