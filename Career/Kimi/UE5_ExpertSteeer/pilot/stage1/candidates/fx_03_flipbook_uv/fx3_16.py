import math


def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    if wrap:
        f = frame % total
    else:
        f = min(frame, total)
    col = math.ceil(f / cols) - 1
    row = f // cols
    return (col, row)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
