"""播种失败解 3：取整方向错（col 用 ceil）+ 定格钳位越界一帧。

失败簇类型：取整/边界错。col 对 (f % cols)/cols 向上取整（任何非整除余数都进 1，
且除以 cols 而非按 cols 分段），非 wrap 时钳到 total 而不是 total-1，
帧号 == total 时 row 越界（row == rows），UV 矩形出现 v < 0。
"""

import math


def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    if wrap:
        f = frame % total
    else:
        f = min(frame, total)  # 错误：应钳到 total-1
    r = f % cols
    col = math.ceil(r / cols) if r != 0 else 0  # 错误：ceil 语义
    row = f // cols
    return (col, row)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
