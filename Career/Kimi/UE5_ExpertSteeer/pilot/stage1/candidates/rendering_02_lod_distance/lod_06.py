def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    """迟滞：升级带在上界 (1+hyst)，降级带在下界 (1-hyst)。"""
    if not thresholds:
        return 0
    n = len(thresholds)
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
