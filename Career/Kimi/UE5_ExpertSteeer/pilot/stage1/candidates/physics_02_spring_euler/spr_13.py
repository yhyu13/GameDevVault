def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    vp = v + a * dt
    xp = x + vp * dt
    return xp, vp
