def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    n = len(thresholds)
    base = n
    for i, t in enumerate(thresholds):
        if screen_size >= t:
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
