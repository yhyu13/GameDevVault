def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest)) / m
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new
