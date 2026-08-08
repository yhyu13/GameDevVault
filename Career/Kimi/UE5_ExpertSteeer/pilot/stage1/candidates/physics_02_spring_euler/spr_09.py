def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    v = v + a * dt
    x = x + v * dt
    return x, v
