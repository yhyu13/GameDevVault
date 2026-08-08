def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    v_ = v + a * dt
    x_ = x + v_ * dt
    return x_, v_
