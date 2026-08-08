def flipbook_uv(frame, cols, rows, wrap):
    """wrap=True 循环，False 定格；行优先，0 起始。"""
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
