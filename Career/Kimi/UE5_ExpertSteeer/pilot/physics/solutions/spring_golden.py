"""阻尼弹簧半隐式欧拉步进 —— 黄金解。

UE C++ 形态（Stage 1 迁移目标）：
- 悬架弹簧/约束的逐帧积分核（Chaos 车辆 SuspensionSpring、布料约束投影）
- 对应 C++ 中形如 `float A = (-K*(X-Rest) - C*V) / Mass; V += A*Dt; X += V*Dt;` 的热循环

半隐式欧拉（symplectic Euler）：先按当前状态算加速度，再更新速度，
最后用【新】速度更新位置——这是固定步长下能量有界的标准选择。

单位约定（UE 世界单位）：x 为 cm，k 为 N/cm，c 为 N*s/cm，m 为 kg，dt 为 s。
"""
def spring_step(x, v, k, c, rest, m, dt):
    """单步半隐式欧拉，返回 (x', v')。

    a = (-k*(x-rest) - c*v) / m  弹簧力 + 阻尼力
    v' = v + a*dt
    x' = x + v'*dt               用新速度更新位置（半隐式的关键）
    """
    a = (-k * (x - rest) - c * v) / m
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new
