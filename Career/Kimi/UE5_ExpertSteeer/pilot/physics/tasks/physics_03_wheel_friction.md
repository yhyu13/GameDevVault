# 任务：载具轮纵向力 / 摩擦圆

## 元信息

- **id**: `physics_03_wheel_friction`
- **域**: physics
- **目标模型尺寸**: 0.8B~2B（单函数级）
- **UE C++ 形态**（Stage 1 迁移目标）: 对应 `FChaosVehicleWheel` 纵向力计算（纵向 slip 力受摩擦圆约束），`FMath::Clamp` / `FMath::SqrtSafe` 对应 UE 同名静态函数。迁移后形如 `float ComputeLongitudinalForce(float Slip, float NormalForce, float LateralForce, float Mu, float SlipStiffness)`。

## 任务描述（prompt，中文）

> 实现载具轮胎纵向力计算函数 `wheel_longitudinal_force`，遵守**摩擦圆**（friction circle）约束：
> 1. 总抓地预算 `grip = mu * fz`（mu 为摩擦系数，fz 为法向载荷 N）；
> 2. 横向力 `fy` 会占用部分抓地：纵向剩余预算 `fmax = sqrt(grip² - fy²)`；当 `fy >= grip` 时抓地耗尽，`fmax` 必须为 0——**不得对负数开方**（返回 NaN 即失败），可用 `FMath.SqrtSafe`；
> 3. 纵向力 `Fx = clamp(ks * slip, -fmax, fmax)`（`ks` 为纵向滑移刚度 N）；
> 4. 无接触（`fz <= 0`）时返回 0；
> 5. 符号约定：`slip > 0` 输出正力（驱动），`slip < 0` 输出负力（制动），符号不可反转。
>
> 单位：力 N、载荷 N、slip 无量纲、mu 无量纲。可用 `from fvector_stub import FMath`（提供 `Clamp` / `SqrtSafe`）。不得使用随机数、IO 或第三方库。

## 输入规格

- Python 签名：`def wheel_longitudinal_force(slip: float, fz: float, fy: float, mu: float, ks: float) -> float`
- 参数顺序与命名**固定**（L1 API 表面检查以此为准）
- 实现文件：`solutions/wheel_*.py`；验证：`verifiers/verify_physics.py`

## Golden 解

```python
"""载具轮纵向力 / 摩擦圆 —— 黄金解。

UE C++ 形态（Stage 1 迁移目标）：
- 对应 FChaosVehicleWheel 纵向力计算（slip 力受摩擦圆约束）
- FMath::Clamp / FMath::SqrtSafe 对应 UE 同名静态函数

物理模型：
- slip 无量纲滑移率；ks 为纵向滑移刚度（N）；Fz 法向载荷（N）；Fy 横向力（N）；
  mu 为轮胎摩擦系数（无量纲）
- 摩擦圆：总抓地预算为 mu*Fz，横向力 Fy 占用一部分后，纵向剩余预算
  Fmax = sqrt((mu*Fz)^2 - Fy^2)；Fy >= mu*Fz 时纵向预算为 0（抓地耗尽）
- Fx = clamp(ks*slip, -Fmax, Fmax)
"""
from fvector_stub import FMath


def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    """返回纵向力 Fx（N）。无接触（fz<=0）时返回 0。"""
    if fz <= 0.0:
        return 0.0

    grip = mu * fz
    # SqrtSafe：根号内为负（fy 超过总抓地）时返回 0，而不是 NaN
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
```

## Hidden tests

容差：`KINDA_SMALL_NUMBER = 1e-4`。

| # | 输入 (slip, fz, fy, mu, ks) | 期望 Fx | 目的 |
|---|---|---|---|
| 1 | (0.3, 1000, 0, 1.0, 2000) | 600.0 | 纯纵向：ks·slip 未超预算 |
| 2 | (0.9, 1000, 0, 1.0, 2000) | 1000.0 | 纵向 clamp 上限 |
| 3 | (-0.9, 1000, 0, 1.0, 2000) | -1000.0 | 纵向 clamp 下限（制动符号） |
| 4 | (0.9, 1000, 800, 1.0, 2000) | 600.0 | 摩擦圆耦合：Fy 占用后预算 = 600 |
| 5 | (0.9, 1000, 1000, 1.0, 2000) | 0.0 | 抓地耗尽：Fy == mu·Fz |
| 6 | (0.9, 1000, 1200, 1.0, 2000) | 0.0 | Fy > mu·Fz：sqrt 负值必须安全为 0 |
| 7 | (0.5, 0, 0, 1.0, 2000) | 0.0 | 零载荷：无接触返回 0 |
| 8 | (0.5, -100, 0, 1.0, 2000) | 0.0 | 负载荷守卫 |
| 9 | (-0.3, 1000, 0, 1.0, 2000) | -600.0 | 制动符号保持 |
| 10 | (0.5, 2000, 0, 0.5, 3000) | 1000.0 | mu 缩放：预算 = mu·Fz = 1000 |
| 11 | (0.15, 800, 100, 1.2, 2500) | 375.0 | 混合参数：小 slip 不触预算 |

## Judge rubric（L4 维度，每维 0-10）

| 维度 | 说明 | 权重 |
|---|---|---|
| 正确性 | 摩擦圆公式、sqrt 负值处理、clamp、零载荷边界 | 0.40 |
| API 正确性 | 单位（N）、FMath 语义、符号约定 | 0.20 |
| 工程化 | 结构清晰、可复用、防御性 | 0.25 |
| 性能意识 | 无冗余计算、复杂度合理 | 0.15 |

PASS 阈值：加权分 ≥ 6.0 且 正确性 ≥ 6。

## 播种失败解（3 个）

| # | 类型（取自失败簇预测表） | 描述 | 期望拦截层 |
|---|---|---|---|
| 1 | 载具轮模型误用（预算误用） | 忽略摩擦圆：`fmax = mu*fz` 不含 Fy 占用；横向力大时纵向力被高估，代码中无 Fy 参与痕迹 | L3 |
| 2 | 轴约定/符号反 | 返回值整体取负：驱动变制动；输出 0 的测试不受影响，其余全部反号 | L3 |
| 3 | 过拟合/硬编码（断言全过但错误，计划 §3.1 形态） | 对测试输入硬编码输出，其余输入一律返回 0：L3 全过但未学到物理，只能由 judge 意图层裁决 | L4（L3 盲区演示） |

实现文件：`solutions/wheel_fail1_circle.py`、`wheel_fail2_sign.py`、`wheel_fail3_hardcoded.py`（与上方 hidden tests 配套，可独立运行）。
