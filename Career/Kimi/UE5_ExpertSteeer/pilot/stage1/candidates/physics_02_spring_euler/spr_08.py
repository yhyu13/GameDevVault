def spring_step(x, v, k, c, rest, m, dt):
    """单步积分。弹簧力 Fs=-k(x-rest)，阻尼力 Fd=-c*v，a=(Fs+Fd)/m。"""
    a = (-k * (x - rest) - c * v) / m
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new
