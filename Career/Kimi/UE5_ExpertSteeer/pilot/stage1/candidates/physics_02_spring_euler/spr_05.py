def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    v_next = v + a * dt
    x_next = x + v_next * dt
    return (x_next, v_next)
