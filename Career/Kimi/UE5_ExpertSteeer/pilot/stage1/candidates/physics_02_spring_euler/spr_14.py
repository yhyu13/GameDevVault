def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    x_new = x + v * dt
    v_new = v + a * dt
    return x_new, v_new
