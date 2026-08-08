def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    return x + (v + a * dt) * dt, v + a * dt
