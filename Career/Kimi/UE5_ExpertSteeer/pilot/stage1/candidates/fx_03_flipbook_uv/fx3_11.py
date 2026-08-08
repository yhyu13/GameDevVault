def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
