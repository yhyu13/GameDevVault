"""rendering_02_lod_distance 播种失败解 2 —— 降级阈值索引错（off-by-one，失败簇：阈值表索引错）。

与 golden 的差异：降级时迟滞带边界错误地取 目标(base) 的阈值 t[base]*(1-hyst)，
而不是 当前 LOD 的阈值 t[current_lod]*(1-hyst)。
后果：降级迟滞带过宽——0.40 应已降级到 LOD1（t[0]*0.9=0.45），
本解仍停留在 LOD0；0.17 应降到 LOD2（t[1]*0.9=0.18），本解仍停留在 LOD1。
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
        boundary = thresholds[base] * (1.0 + hysteresis)
        return base if screen_size >= boundary else current_lod

    # 失败点：降级边界用 t[base] 而非 t[current_lod]
    boundary = thresholds[base] * (1.0 - hysteresis)
    return base if screen_size < boundary else current_lod
