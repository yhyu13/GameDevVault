"""rendering_02_lod_distance golden —— LOD 距离选择（带 hysteresis）。

UE C++ 形态（Stage 1 迁移目标）:
- UStaticMeshComponent::ComputeDesiredLODLevel / GetLODForScreenSize（ScreenSize 数组 + hysteresis）
- FLODSettings / UStaticMeshComponent LODData 的 ScreenSize（降序：LOD0 最大）
- 约定：screen_size >= thresholds[i] 选 LOD i；thresholds 严格降序；末级覆盖 [t[n-1], 0)。

hysteresis 语义（经典双向迟滞）:
- 升级（变精细，i -> i-1）：必须 screen_size >= t[i-1] * (1 + hyst)
- 降级（变粗糙，i -> i+1）：必须 screen_size <  t[i]   * (1 - hyst)
- current_lod=None（首次/状态丢失）时不施加 hysteresis，直接取基础选择。
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

    if base < current_lod:  # 升级：越过目标 LOD 上界的迟滞带
        boundary = thresholds[base] * (1.0 + hysteresis)
        return base if screen_size >= boundary else current_lod

    # 降级：跌破当前 LOD 下界的迟滞带
    boundary = thresholds[current_lod] * (1.0 - hysteresis)
    return base if screen_size < boundary else current_lod
