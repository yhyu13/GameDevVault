def spring_step(x, v, k, c, rest, m, dt):
    """symplectic Euler：先速度后位置，能量有界。"""
    acc = (-k * (x - rest) - c * v) / m
    v2 = v + acc * dt
    x2 = x + v2 * dt
    return x2, v2
