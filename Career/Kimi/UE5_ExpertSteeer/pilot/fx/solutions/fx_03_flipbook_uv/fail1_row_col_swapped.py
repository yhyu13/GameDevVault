"""播种失败解 1：行列互换（col 用了行数、row 用了列数）。

失败簇类型：轴约定/取整错。非方形网格（cols != rows）下全部错误：
col = f // rows, row = f % rows。方形网格下侥幸正确，掩盖性极强。
"""


def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    if wrap:
        f = frame % total
    else:
        f = min(frame, total - 1)
    col = f // rows
    row = f % rows
    return (col, row)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
