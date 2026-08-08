def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    base = sum(1 for t in thresholds if screen_size >= t)
    base = min(base, len(thresholds) - 1)
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
