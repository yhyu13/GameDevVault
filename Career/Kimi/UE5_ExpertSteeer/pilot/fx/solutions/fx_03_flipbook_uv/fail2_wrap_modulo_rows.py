"""播种失败解 2：wrap 边界错误（对行数取模而非总帧数）。

失败簇类型：wrap 边界错。循环播放时用 frame % rows（行数）而不是 frame % (cols*rows)，
超过一行就错误回卷；非 wrap 分支正确。cols=4, rows=2 时 frame=7 应到 (3,1)，
实际回卷到 (1,0)。
"""


def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    if wrap:
        f = frame % rows  # 错误：对行数取模
    else:
        f = min(frame, total - 1)
    col = f % cols
    row = f // cols
    return (col, row)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
