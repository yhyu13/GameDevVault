def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)
