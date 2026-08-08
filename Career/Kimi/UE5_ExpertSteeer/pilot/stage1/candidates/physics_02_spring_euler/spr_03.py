def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    v_new = v + a * dt
    return x + v_new * dt, v_new
