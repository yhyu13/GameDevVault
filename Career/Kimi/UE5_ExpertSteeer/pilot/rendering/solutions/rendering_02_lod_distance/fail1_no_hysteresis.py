"""rendering_02_lod_distance 播种失败解 1 —— 无 hysteresis（失败簇：LOD 切换抖动/来回跳）。

与 golden 的差异：完全忽略 current_lod 与 hysteresis，永远返回基础选择。
后果：screen_size 在阈值附近抖动时 LOD 每帧来回切换（pop/抖动），
迟滞带内（0.46 在 [0.45,0.5) 内、0.52 在 [0.5,0.55) 内）应保持原 LOD 的用例全部判错。
代码可运行、签名正确，L1 拦不住。
"""


def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    thresholds = list(thresholds)
    if not thresholds:
        return 0
    # 失败点：无 hysteresis，无状态
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            return i
    return len(thresholds) - 1
