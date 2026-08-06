"""fx_03_flipbook_uv golden —— flipbook 帧号 → 行列 + UV 矩形。

UE C++ 形态（Stage 1 迁移目标）: Niagara 粒子 flipbook 模块（FNiagaraModule 按
ParticleID/帧索引算 UV，写 CustomHDRUV / 材质函数 FlipbookUV）。
UE 约定：v 坐标向下（纹理顶部 v=1），row 0 为第一行。

API:
    flipbook_uv(frame, cols, rows, wrap) -> (col, row)      # 0 起始
    flipbook_uv_rect(frame, cols, rows, wrap) -> (u0, v0, u1, v1)
wrap=True  帧索引对总帧数取模（循环播放）
wrap=False 钳到最后一帧（播放到头后定格）
"""


def flipbook_uv(frame, cols, rows, wrap):
    """帧号 → (col, row)。wrap 控制循环（取模）或定格（钳位）。"""
    total = cols * rows
    if wrap:
        f = frame % total
    else:
        f = min(frame, total - 1)
    col = f % cols
    row = f // cols
    return (col, row)


def flipbook_uv_rect(frame, cols, rows, wrap):
    """帧号 → UV 矩形 (u0, v0, u1, v1)。v 向下约定：行 0 的 v 更大。"""
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
