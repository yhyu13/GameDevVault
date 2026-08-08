def select_lod(current_lod, screen_size, thresholds):
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
    while lod > 0 and screen_size >= thresholds[lod - 1]:
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod]:
        lod += 1
    return lod
