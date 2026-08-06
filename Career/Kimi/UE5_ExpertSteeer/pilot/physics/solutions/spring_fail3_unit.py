"""阻尼弹簧步进 —— 播种失败解 #3：单位错 cm/m（失败簇：UE 单位是 cm）。

把输入的 k（规格为 N/cm，UE cm 世界单位）当成 N/m，先除以 100 再使用。
k 被缩小 100 倍 → 弹簧软 100 倍：低频、慢收敛、轨迹整体错位。
力/质量换算不清是 UE 物理接入最经典的坑。
"""
def spring_step(x, v, k, c, rest, m, dt):
    # BUG: k 规格是 N/cm（UE 单位），这里误当 N/m 并除以 100 换算
    k = k / 100.0
    a = (-k * (x - rest) - c * v) / m
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new
