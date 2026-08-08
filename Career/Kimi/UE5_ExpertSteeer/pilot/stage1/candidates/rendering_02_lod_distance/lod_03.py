def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    """首帧无迟滞；有状态时升级/降级各设迟滞带，防阈值附近抖动。"""
    n = len(thresholds)
    if n == 0:
        return 0
    base = n - 1
    for i in range(n):
        if screen_size >= thresholds[i]:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < n - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
