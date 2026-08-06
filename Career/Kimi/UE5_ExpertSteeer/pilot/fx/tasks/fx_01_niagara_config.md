# 任务 fx_01_niagara_config：Niagara 发射器配置校验 + 预算计算

## 元信息

- **id**: `fx_01_niagara_config`
- **域**: fx
- **目标模型尺寸**: 2B（单模块：配置 Schema + 规则 + 预算数学的组合）
- **UE C++ 形态**（Stage 1 迁移目标）: 真实工程中对应编辑器/烘焙管线的配置审查——读取 `UNiagaraSystem` 各发射器的 `SpawnRate`（FNiagaraFloat）、`ParticleLifetime`、`MaxParticles` 等参数做校验（`UEditorValidator` / 自定义 `FNiagaraModule` 检查）；pilot 中配置以 JSON(dict) 转义，L2 校验层即外部 Schema 校验器的等价物，L3 为纯数学核（峰值/内存）。

## 任务描述（prompt，中文）

> 你是 UE5 特效工程师。Niagara 发射器配置以 JSON 对象给出，你需要实现**配置校验器 + 预算计算器**两个函数：
>
> 1. `validate_niagara_config(cfg)`：校验必填字段与类型（`emitter_name`: str 非空；`spawn_rate`: float；`particle_lifetime`: float；`max_particles`: int；`bytes_per_particle`: int），再做范围校验（`spawn_rate ∈ (0, 1e6]`、`particle_lifetime ∈ (0, 60]`、`max_particles ∈ [1, 1e7]`、`bytes_per_particle ∈ [16, 4096]`），最后做预算规则检查：
>    - 峰值粒子数 `peak = spawn_rate × particle_lifetime`（GPU 发射器按连续速率分配）；若 `peak > max_particles` 报错（发射器会丢粒子）。
>    - 内存 `memory = peak × bytes_per_particle`；若超过默认预算 **64 MiB**（67108864 字节）报错。
>    返回 dict：`{"valid": bool, "errors": [str], "peak_particles": float, "memory_bytes": float}`。
> 2. `compute_niagara_budget(spawn_rate, particle_lifetime, bytes_per_particle)`：返回 `(peak, memory)`。**必须保留浮点精度，禁止取整**（截断会让预算失真）。
>
> 约束：不用第三方库；错误消息用中文并指明字段；结构性错误（缺字段/类型/范围）时 `peak_particles`/`memory_bytes` 返回 0.0，预算错误时返回计算值（便于调参）。

## 输入规格

- Python 签名（UE C++ 对应：`TMap<FString, FJsonValue>` 解析 → 校验函数；`FFloatRange` 语义）

```python
def validate_niagara_config(cfg: dict) -> dict: ...
def compute_niagara_budget(spawn_rate: float, particle_lifetime: float, bytes_per_particle: int) -> tuple[float, float]: ...
```

## Golden 解

见 `solutions/fx_01_niagara_config/golden.py`（与任务同目录交付，可直接运行）。

要点：必填/类型 → 范围 → 预算三层顺序检查；预算数学独立成 `compute_niagara_budget`（职责单一，便于单独验证）；峰值/内存保持 float 精度。

## Hidden tests

- 容差：数值断言用 `FMath::IsNearlyEqual` 级别 **1e-4**
- L2（Schema 行为）：缺 `particle_lifetime` 必须报错；`spawn_rate=-5` 必须报错；`rate=1000, lifetime=50, max=10000`（峰值 50000 超限）必须报错；合法配置必须放行
- L3（执行）：
  - `compute(100.0, 3.0, 64) == (300.0, 19200.0)`
  - `compute(150.5, 2.3, 128) == (346.15, 44307.2)`（非整数乘积，专抓截断）
  - `compute(10000.0, 10.0, 4096) == (100000.0, 409600000.0)`
  - 有效配置 `validate` 返回值峰值/内存与数学核一致
  - 缺字段 / 内存超限（rate=1000, lifetime=100, bytes=4096 → 409.6 MB > 64 MiB）必须报错

## Judge rubric（L4 维度，每维 0-10）

| 维度 | 说明 | 权重 |
|---|---|---|
| 正确性 | Schema 覆盖（缺字段/类型/范围/预算）、边界处理 | 高 |
| API 正确性 | UE 语义：连续速率不取整、内存单位字节、64 MiB 预算约定 | 高 |
| 工程化 | 检查顺序清晰、错误消息指明字段、职责单一 | 中 |
| 性能意识 | 无冗余分配/重复计算 | 中 |

加权分 = 0.35×正确性 + 0.35×API + 0.15×工程化 + 0.15×性能；PASS 门槛：加权 ≥ 7 且 正确性 ≥ 6。

## 播种失败解（3 个）

| # | 类型（取自失败簇预测表） | 描述 | 文件 |
|---|---|---|---|
| 1 | 配置缺字段检查遗漏 | `REQUIRED_FIELDS` 漏掉 `particle_lifetime`，缺失该字段的配置被错误判定合法 | `fail1_missing_lifetime_check.py` |
| 2 | 配置越界值/预算检查遗漏 | 只查必填字段与类型，负生成率、峰值超限、内存超限全部放行 | `fail2_no_range_budget_checks.py` |
| 3 | 粒子寿命数学错（精度） | 校验逻辑全对，但 `compute_niagara_budget` 用 `int()` 截断：150.5×2.3=346.15 被算成 346 | `fail3_int_truncation.py` |
