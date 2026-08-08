def spring_step(x, v, k, c, rest, m, dt):
    """弹簧+阻尼合力产生加速度，半隐式更新次序（速度先行）。"""
    force = -k * (x - rest) - c * v
    a = force / m
    vp = v + a * dt
    xp = x + vp * dt
    return xp, vp
