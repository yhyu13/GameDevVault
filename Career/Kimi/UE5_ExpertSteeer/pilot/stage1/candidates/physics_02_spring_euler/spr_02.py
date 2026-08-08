def spring_step(x, v, k, c, rest, m, dt):
    """半隐式欧拉。单位：x cm、k N/cm、c N*s/cm、m kg、dt s。"""
    accel = (-k * (x - rest) - c * v) / m
    v1 = v + accel * dt
    x1 = x + v1 * dt
    return x1, v1
