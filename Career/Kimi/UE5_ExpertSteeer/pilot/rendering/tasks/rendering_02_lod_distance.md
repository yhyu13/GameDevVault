# 任务 rendering_02_lod_distance：LOD 距离选择（带 hysteresis）

## 元信息

- **id**: `rendering_02_lod_distance`
- **域**: rendering
- **目标模型尺寸**: 0.8B（单函数有状态数值逻辑）
- **UE C++/shader 形态**（Stage 1 迁移目标）: C++ 侧 `UStaticMeshComponent::ComputeDesiredLODLevel` / `GetLODForScreenSize`（`FLODSettings::ScreenSize` 数组降序 + `bUseHysteresis`），骨骼网格 `FSkeletalMeshRenderData` 同理；Nanite/常规网格的 LOD 切换都依赖 screen-size 阈值 + 迟滞防抖动。pilot 用 Python 软件求值，Stage 1 迁移为 `FLODSettings` + 同一判定逻辑。

## 任务描述（prompt，中文）

> 你是 UE5 渲染工程师。实现 LOD 距离选择：给定当前 LOD、屏幕占比 `screen_size`（0~1，越大越近越精细）、降序阈值数组 `thresholds`（`t[0] > t[1] > ...`，`screen_size >= t[i]` 选 LOD i，低于末级阈值选最后一级），返回应显示的 LOD 索引。
>
> 必须实现 **hysteresis（迟滞）** 以抑制阈值附近来回切换（pop/抖动）：
> - **升级**（变精细，i → i-1）：仅当 `screen_size >= t[i-1] * (1 + hysteresis)`
> - **降级**（变粗糙，i → i+1）：仅当 `screen_size <  t[i]   * (1 - hysteresis)`
> - `current_lod=None`（首次调用/状态丢失）时不施加迟滞，直接返回基础选择。
>
> 实现 `select_lod(current_lod, screen_size, thresholds, hysteresis=0.1)`，返回 int。
>
> 约束：`thresholds` 可为空（返回 0）；`hysteresis` ∈ [0, 1)。**无迟滞的解会在阈值附近每帧来回跳（画面抖动）；迟滞带方向做反会放大抖动而不是抑制它。**

## 输入规格

- Python 签名（UE C++ 对应：`int32 UStaticMeshComponent::GetLODForScreenSize(float ScreenSize, bool bUseHysteresis, int32 PrevLOD)`）

```python
def select_lod(current_lod: int | None, screen_size: float, thresholds: list[float], hysteresis: float = 0.1) -> int: ...
```

## Golden 解

见 `solutions/rendering_02_lod_distance/golden.py`。要点：先求无状态基础选择 `base`，再与 `current_lod` 比较方向——升级侧用目标 LOD 上界 `t[base]*(1+hyst)`、降级侧用当前 LOD 下界 `t[current]*(1-hyst)`；`current_lod` 越界/None 直接返回 `base`。

## Hidden tests

- 容差：LOD 为整数，精确相等；阈值/hysteresis 与 spec 完全一致
- 13 例（golden 预计算硬编码）：首帧 None ×3、迟滞带内停留 ×3（0.46 应留 LOD0、0.52 应留 LOD1、0.19 应留 LOD1）、升级/降级过带 ×3、跨级升级 ×1、hysteresis=0 退化为纯阈值 ×1、末级保持 ×2

## Judge rubric（L4 维度，每维 0-10）

| 维度 | 说明 | 权重 |
|---|---|---|
| 正确性 | 升级/降级带边界正确、迟滞方向正确、None/越界状态处理正确 | 高 |
| API 正确性 | UE 语义正确（ScreenSize 降序约定、hysteresis 定义、int 返回） | 高 |
| 工程化 | 状态参数显式传入、阈值表降序不变量、无魔法数 | 中 |
| 性能意识 | O(n) 一次线性扫描、无分配 | 中 |

加权分 = 0.35×正确性 + 0.35×API + 0.15×工程化 + 0.15×性能；PASS 门槛：加权 ≥ 7 且 正确性 ≥ 6。

## 播种失败解（3 个）

| # | 类型（取自失败簇预测表） | 描述 | 文件 |
|---|---|---|---|
| 1 | 无 hysteresis | 完全忽略 `current_lod` 与迟滞，永远返回基础选择：迟滞带内 3 例全错（阈值附近必抖） | `fail1_no_hysteresis.py` |
| 2 | 阈值索引错（off-by-one） | 降级带边界误用 `t[base]*(1-hyst)` 而非 `t[current_lod]*(1-hyst)`：降级迟滞带过宽，该降级不降 | `fail2_offbyone_threshold.py` |
| 3 | 迟滞方向反 | 升级用 `(1-hyst)`、降级用 `(1+hyst)`：迟滞带反向，切换被加速而非抑制 | `fail3_inverted_hysteresis.py` |
