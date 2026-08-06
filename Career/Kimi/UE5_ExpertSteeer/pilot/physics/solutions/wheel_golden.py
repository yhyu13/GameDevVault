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
