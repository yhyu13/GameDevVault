def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % rows if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
