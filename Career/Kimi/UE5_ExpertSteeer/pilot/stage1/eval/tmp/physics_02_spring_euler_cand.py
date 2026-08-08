def spring_step(x, v, k, c, rest, m, dt):
    """阻尼弹簧半隐式欧拉单步：a -> v' -> x'（用新速度更新位置）。"""
    a = (-k * (x - rest) - c * v) / m
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new

