"""rendering_02_lod_distance 播种失败解 3 —— hysteresis 方向反（失败簇：迟滞带方向/数学错）。

与 golden 的差异：迟滞带方向颠倒——升级用 (1-hyst)、降级用 (1+hyst)。
后果：迟滞带缩成"加快切换"的反向带：0.52 本应停留在 LOD1（升级带 [0.5,0.55)），
本解在 0.52 就升级到 LOD0；0.19 本应停留在 LOD1（降级带 [0.18,0.2)），
本解在 0.19 就降到 LOD2。迟滞不仅没抑制抖动，反而放大抖动。
代码可运行、签名正确，L1 拦不住。
"""


def _base_lod(screen_size, thresholds):
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            return i
    return len(thresholds) - 1


def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    thresholds = list(thresholds)
    if not thresholds:
        return 0

    base = _base_lod(screen_size, thresholds)

    if current_lod is None or not (0 <= current_lod < len(thresholds)):
        return base

    if base == current_lod:
        return current_lod

    if base < current_lod:
        # 失败点：升级带方向反（应 (1+hyst)）
        boundary = thresholds[base] * (1.0 - hysteresis)
        return base if screen_size >= boundary else current_lod

    # 失败点：降级带方向反（应 (1-hyst)）
    boundary = thresholds[current_lod] * (1.0 + hysteresis)
    return base if screen_size < boundary else current_lod
