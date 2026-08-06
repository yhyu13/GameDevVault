"""rendering_03_linear_srgb 播种失败解 3 —— 无线性段/阈值错（失败簇：sRGB 常数或分段错）。

与 golden 的差异：去掉 c <= 0.0031308 的 12.92 线性段，全区间走 gamma 曲线。
后果：暗部严重错（0.001 -> 0.00434 vs 标准 0.01292，约 3 倍偏差），
低亮度区域失去线性段对比度——暗部细节被压坏。
代码可运行、签名正确，L1 拦不住。
"""

SRGB_THRESHOLD = 0.0031308
SRGB_ALPHA = 0.055
SRGB_1_055 = 1.055
SRGB_12_92 = 12.92
SRGB_GAMMA = 2.4


def _encode_single(v):
    # 失败点：无条件走 gamma 分支，线性段 12.92*c 丢失
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
