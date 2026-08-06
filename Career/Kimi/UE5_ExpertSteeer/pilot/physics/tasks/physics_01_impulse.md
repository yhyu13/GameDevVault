# 任务：两球碰撞冲量解算（restitution）

## 元信息

- **id**: `physics_01_impulse`
- **域**: physics
- **目标模型尺寸**: 0.8B（单函数级）
- **UE C++ 形态**（Stage 1 迁移目标）: `FVector`（UE::Math::TVector<float>）上的相对速度投影与冲量计算；对应 Chaos 刚体求解器中 ApplyImpulse 前的约束求解核（如 `FChaosSolver` 的 impulse 步骤）。迁移后函数形如 `void ResolveImpulse(float MassA, float MassB, const FVector& VA, const FVector& VB, const FVector& Normal, float Restitution, FVector& OutVA, FVector& OutVB)`。

## 任务描述（prompt，中文）

> 实现两球碰撞的冲量解算函数 `resolve_impulse`。输入为 A、B 两球的质量 `m_a`、`m_b`（kg，正有限值），碰撞前速度 `v_a`、`v_b`（cm/s，FVector），碰撞法线 `normal`（从 A 指向 B 的**已归一化**单位向量），恢复系数 `restitution`（0~1）。
>
> 要求：
> 1. 用标准冲量公式计算法向冲量：`j = -(1 + e) * (v_rel . n) / (1/m_a + 1/m_b)`，其中 `v_rel = v_a - v_b`，`.` 为点乘；
> 2. 仅当两球正在接近（`v_rel . n < 0`）时施加冲量；正在分离时直接返回原速度（不产生"拉回"冲量）；
> 3. 冲量施加方向必须正确：A 获得 `+j/m_a * n`，B 获得 `-j/m_b * n`；
> 4. 返回 `(v_a', v_b')` 两个 FVector，**不要修改输入对象**；
> 5. 单位遵循 UE 约定：速度 cm/s、质量 kg、冲量 kg·cm/s；不得自行换算单位。
>
> 可用 `from fvector_stub import FVector`（提供 `+ - *` 运算与 `.Dot`、`.x/.y/.z` 成员）。不得使用随机数、IO 或第三方库。

## 输入规格

- Python 签名：`def resolve_impulse(m_a: float, m_b: float, v_a: FVector, v_b: FVector, normal: FVector, restitution: float) -> tuple[FVector, FVector]`
- 参数顺序与命名**固定**（L1 API 表面检查以此为准）
- 实现文件：`solutions/impulse_*.py`；验证：`verifiers/verify_physics.py`

## Golden 解

```python
"""两球碰撞冲量解算（restitution）—— 黄金解。

UE C++ 形态（Stage 1 迁移目标）：
- FVector 对应 UE::Math::TVector<float>（UE5 中 FVector）
- 对应 Chaos 刚体求解器中 ApplyImpulse 前的相对速度投影与冲量计算

单位约定（UE 世界单位）：速度 cm/s，质量 kg，冲量 kg*cm/s，法线为归一化单位向量。
"""
from fvector_stub import FVector


def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    """两球碰撞后速度 (v_a', v_b')。

    冲量公式：j = -(1 + e) * (v_rel . n) / (1/m_a + 1/m_b)
    仅当两球相向运动（v_rel . n < 0）时施加冲量；分离情形直接返回原速度。
    normal 为从 A 指向 B 的归一化法线。
    """
    vrel_n = (v_a - v_b).Dot(normal)

    # 正在分离：不施加冲量（物理上已离开碰撞阶段）
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)

    # 约化质量的倒数 = 1/m_a + 1/m_b（调和平均）
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_mass

    v_a_new = v_a + normal * (j / m_a)
    v_b_new = v_b - normal * (j / m_b)
    return v_a_new, v_b_new
```

## Hidden tests

容差：`FMath::IsNearlyEqual` 级别 `KINDA_SMALL_NUMBER = 1e-4`（分量级）。期望值由闭式公式独立计算（非与解共用实现）。

| # | 输入 (m_a, m_b, v_a, v_b, normal, e) | 期望 (v_a', v_b') | 目的 |
|---|---|---|---|
| 1 | (1, 1, (-100,0,0), (100,0,0), (1,0,0), 1.0) | ((100,0,0), (-100,0,0)) | e=1 弹性对撞：速度完全交换 |
| 2 | (1, 1, (-100,0,0), (100,0,0), (1,0,0), 0.0) | ((0,0,0), (0,0,0)) | e=0 完全非弹性：黏在一起 |
| 3 | (1, 1000, (-100,0,0), (0,0,0), (1,0,0), 0.5) | ((49.85014985,0,0), (-0.14985015,0,0)) | 质量悬殊：约化质量主导 |
| 4 | (2, 3, (-50,50,0), (10,20,0), (½√2,½√2,0), 0.7) | ((-34.7,65.3,0), (-0.2,9.8,0)) | 斜碰：切向速度保持 |
| 5 | (1, 1, (100,0,0), (-100,0,0), (1,0,0), 0.9) | ((100,0,0), (-100,0,0)) | 分离情形：不施加冲量 |
| 6 | (1, 1, (0,50,0), (0,0,0), (1,0,0), 0.5) | ((0,50,0), (0,0,0)) | 纯切向：法向分量为 0 |
| 7 | (1, 1, (-1e5,-1e5,0), (1e5,1e5,0), (½√2,½√2,0), 0.5) | ((5e4,5e4,0), (-5e4,-5e4,0)) | 高速斜碰：float32 截断在此量级误差 > 1e-4 |

## Judge rubric（L4 维度，每维 0-10）

| 维度 | 说明 | 权重 |
|---|---|---|
| 正确性 | 冲量公式、分离守卫、质量处理、边界 | 0.40 |
| API 正确性 | 单位（cm/kg）、FVector 语义、不动输入 | 0.20 |
| 工程化 | 结构清晰、可复用、防御性 | 0.25 |
| 性能意识 | 无冗余分配、复杂度合理 | 0.15 |

PASS 阈值：加权分 ≥ 6.0 且 正确性 ≥ 6。

## 播种失败解（3 个）

| # | 类型（取自失败簇预测表） | 描述 | 期望拦截层 |
|---|---|---|---|
| 1 | 冲量符号反 | A 得到 `-j/m_a*n`、B 得到 `+j/m_b*n`，碰撞后互相穿过 | L3 |
| 2 | 质量与速度尺度 | 用 `min(m_a, m_b)` 代替约化质量；等质量时恰好正确，质量悬殊时冲量严重低估 | L3 |
| 3 | 数值精度（质量与速度尺度变体） | 中间量全部截断到 float32：低速下误差 < 1e-5，高速 1e5 cm/s 或非整数法线时误差达 1e-2 | L3（静态读码与 judge 均易放行） |

实现文件：`solutions/impulse_fail1_sign.py`、`impulse_fail2_massscale.py`、`impulse_fail3_f32.py`（与上方 hidden tests 配套，可独立运行）。
