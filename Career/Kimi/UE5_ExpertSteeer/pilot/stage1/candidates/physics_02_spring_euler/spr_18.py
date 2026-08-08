def spring_step(x0, v0, kk, cc, rest, m, dt):
    a = (-kk * (x0 - rest) - cc * v0) / m
    v_new = v0 + a * dt
    x_new = x0 + v_new * dt
    return x_new, v_new
