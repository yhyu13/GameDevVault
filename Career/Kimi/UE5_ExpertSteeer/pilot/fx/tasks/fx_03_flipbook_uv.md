# 任务 fx_03_flipbook_uv：flipbook 帧号 → 行列 + UV 矩形

## 元信息

- **id**: `fx_03_flipbook_uv`
- **域**: fx
- **目标模型尺寸**: 0.8B（单函数级数学/边界逻辑）
- **UE C++ 形态**（Stage 1 迁移目标）: Niagara 粒子 flipbook 模块——按粒子帧索引算 `(col, row)` 并输出 UV 矩形（Niagara 的 `Flipbook` 采样模块 / 材质函数 `FlipbookUV`，v 向下约定：纹理顶部 v=1，row 0 为第一行）。

## 任务描述（prompt，中文）

> 你是 UE5 特效工程师。实现 flipbook（序列帧）的帧号 → 行列与 UV 矩形换算，供粒子按帧动画采样：
>
> 1. `flipbook_uv(frame, cols, rows, wrap)` → `(col, row)`（均 0 起始）
>    - `wrap=True`：帧索引对总帧数 `cols*rows` 取模（循环播放）。
>    - `wrap=False`：钳到最后一帧 `cols*rows-1`（播放到头定格）。
>    - 行列规则：`col = f % cols`，`row = f // cols`（行优先，row 0 是第一行）。
> 2. `flipbook_uv_rect(frame, cols, rows, wrap)` → `(u0, v0, u1, v1)`（UV 矩形）
>    - `u0 = col/cols`，`u1 = (col+1)/cols`
>    - **v 向下约定**：`v1 = 1.0 - row/rows`（行顶），`v0 = 1.0 - (row+1)/rows`（行底）；row 0 的 v 更大。
>
> 约束：不用第三方库；帧号非负；`cols`、`rows` 为正整数；结果必须始终落在 `[0, cols-1] × [0, rows-1]` 内（越界帧 = UV 越界 = 采样错误）。

## 输入规格

- Python 签名（UE C++ 对应：`FIntPoint FlipbookIndex(int32 Frame, int32 Cols, int32 Rows, bool bWrap)` + `FVector2D(4) FlipbookUV(...)`）

```python
def flipbook_uv(frame: int, cols: int, rows: int, wrap: bool) -> tuple[int, int]: ...
def flipbook_uv_rect(frame: int, cols: int, rows: int, wrap: bool) -> tuple[float, float, float, float]: ...
```

## Golden 解

见 `solutions/fx_03_flipbook_uv/golden.py`。要点：wrap/clamp 先归一化帧索引 `f`，再统一 `col = f % cols; row = f // cols`；UV 矩形复用行列结果，避免两处逻辑漂移。

## Hidden tests

- 容差：整数精确比对；UV 浮点用 **1e-4**
- 行列（含 wrap 回卷、定格钳位、非方形网格）：
  - `(0,4,2,True)=(0,0)`、`(3,4,2,True)=(3,0)`、`(4,4,2,True)=(0,1)`、`(7,4,2,True)=(3,1)`
  - `(8,4,2,True)=(0,0)`（回卷首帧）、`(9,4,2,True)=(1,0)`
  - `(8,4,2,False)=(3,1)`（定格末帧）、`(100,4,2,False)=(3,1)`
  - `(5,3,4,False)=(2,1)`（非方形，抓行列互换）
- UV 矩形：
  - `(5,3,4,False)=(2/3, 0.5, 1.0, 0.75)`
  - `(11,3,4,True)=(2/3, 0.0, 1.0, 0.25)`（末行 v 下界到 0）
  - `(0,3,4,False)=(0.0, 0.75, 1/3, 1.0)`（首帧顶行）

## Judge rubric（L4 维度，每维 0-10）

| 维度 | 说明 | 权重 |
|---|---|---|
| 正确性 | 行列换算、wrap/clamp 边界、UV v 向下约定 | 高 |
| API 正确性 | UE 语义（行优先、v 向下、0 起始帧号） | 高 |
| 工程化 | 边界逻辑集中、rect 复用 uv 逻辑 | 中 |
| 性能意识 | 无循环/无分配（O(1)） | 中 |

加权分 = 0.35×正确性 + 0.35×API + 0.15×工程化 + 0.15×性能；PASS 门槛：加权 ≥ 7 且 正确性 ≥ 6。

## 播种失败解（3 个）

| # | 类型（取自失败簇预测表） | 描述 | 文件 |
|---|---|---|---|
| 1 | 轴约定错（行列互换） | `col = f // rows, row = f % rows`；方形网格下侥幸正确，非方形全错 | `fail1_row_col_swapped.py` |
| 2 | wrap 边界错 | 循环时对行数取模 `frame % rows`（应为总帧数），超一行即错误回卷 | `fail2_wrap_modulo_rows.py` |
| 3 | 取整方向错 + 定格越界 | col 用 ceil 语义（余数非零即进 1）；非 wrap 钳到 `total` 而非 `total-1`，帧号=total 时 row 越界、UV 出 v<0 | `fail3_ceil_and_clamp_bug.py` |
