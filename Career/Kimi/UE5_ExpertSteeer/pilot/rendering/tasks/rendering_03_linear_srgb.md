# 任务 rendering_03_linear_srgb：linear → sRGB 转换（IEC 61966-2-1）

## 元信息

- **id**: `rendering_03_linear_srgb`
- **域**: rendering
- **目标模型尺寸**: 0.8B（单表达式/单函数数值核）
- **UE C++/shader 形态**（Stage 1 迁移目标）: shader 侧 `Common.ush` 的 `LinearToSrgb`/`LinearToSrgbLUT`（色调映射后写回 sRGB RT 前调用）；C++ 侧 `FLinearColor → FColor` 量化路径中的手动逐像素转换（`FColor` 的 sRGB 标志语义）。pilot 用 Python 软件求值（HLSL `pow` 分支逐一对应），Stage 1 换 DXC 编译 + 同一数值比对。

## 任务描述（prompt，中文）

> 你是 UE5 渲染工程师。实现 linear → sRGB 编码（IEC 61966-2-1 标准），用于后处理/色调映射后写回 sRGB render target 前的逐像素转换。
>
> 标准分段（每通道独立）：
> ```
> c <= 0.0031308 :  12.92 * c
> c >  0.0031308 :  1.055 * c^(1/2.4) - 0.055
> ```
>
> 实现 `linear_to_srgb(c)`，输入 `(r, g, b)` 为 [0,1] 的 linear 值，返回编码后的 `(r, g, b)` 元组。**输入越界先 Clamp 到 [0,1]（防御性，UE 语义：负值/超亮值不得产生 NaN/越界输出）。**
>
> 约束：只用 `math`；常数必须是标准值（阈值 0.0031308、线性段 12.92、1.055、0.055、指数 2.4）。**对已编码值再编码一次（双伽马）会让画面整体过亮；指数用 2.2 替代 1/2.4 会系统性色偏；丢掉线性段会压坏暗部对比度。**

## 输入规格

- Python 签名（UE C++/HLSL 对应：`FLinearColor LinearToSrgb(FLinearColor Linear)` / `float3 LinearToSrgb(float3 c)`（Common.ush））

```python
def linear_to_srgb(c: tuple[float, float, float]) -> tuple[float, float, float]: ...
```

## Golden 解

见 `solutions/rendering_03_linear_srgb/golden.py`。要点：常数提为模块级具名常量；`_encode_single` 单通道分段（阈值分支严格 `<=`）；越界先 Clamp 再编码；返回 tuple——结构与 UE shader 的逐通道宏一一对应，Stage 1 迁移为逐通道表达式即可。

## Hidden tests

- 容差：数值比对 **1e-4**（绝对，逐通道）
- 4 例（golden 预计算硬编码）：
  - `(0.5, 0.1, 0.25)` → `(0.7353569831, 0.3491902126, 0.5370987305)`
  - 暗部 `(0.001, 0.0, 0.0031308)` → `(0.0129200000, 0.0, 0.0404499360)`（线性段 + 阈值点）
  - 越界 Clamp `(1.7, -0.3, 0.0)` → `(1.0, 0.0, 0.0)`
  - 端点 `(1.0, 1.0, 1.0)` → `(1.0, 1.0, 1.0)`

## Judge rubric（L4 维度，每维 0-10）

| 维度 | 说明 | 权重 |
|---|---|---|
| 正确性 | 分段正确、指数 1/2.4、线性段 12.92、Clamp 防御 | 高 |
| API 正确性 | sRGB 标准常数与 UE 语义正确（单次编码、[0,1] 约定） | 高 |
| 工程化 | 常数具名、单通道函数复用、无魔法数 | 中 |
| 性能意识 | 无 pow 滥用（仅必要分支）、无多余分配 | 中 |

加权分 = 0.35×正确性 + 0.35×API + 0.15×工程化 + 0.15×性能；PASS 门槛：加权 ≥ 7 且 正确性 ≥ 6。

## 播种失败解（3 个）

| # | 类型（取自失败簇预测表） | 描述 | 文件 |
|---|---|---|---|
| 1 | sRGB vs linear 双伽马 | 对已编码值再编码一次（输入被 sRGB 两次）：整体过亮，0.5 → ~0.879（应 0.735） | `fail1_double_gamma.py` |
| 2 | 指数 2.2/2.4 颠倒 | gamma 分支用 `1/2.2` 替代标准 `1/2.4`：中高亮度系统性偏差，仅 0/1 端点正确 | `fail2_wrong_exponent.py` |
| 3 | 分段/常数错 | 丢弃 `12.92*c` 线性段，全区间走 gamma 曲线：暗部约 3 倍偏差（0.001 → 0.0043，应 0.0129） | `fail3_no_linear_segment.py` |
