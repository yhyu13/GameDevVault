def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    """LOD 选择（带迟滞）。升级需越过 t[i-1]*(1+hyst)，降级需跌破 t[i]*(1-hyst)。"""
    if not thresholds:
        return 0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod

