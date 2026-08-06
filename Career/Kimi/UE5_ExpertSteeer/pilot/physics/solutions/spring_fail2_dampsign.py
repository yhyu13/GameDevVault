"""阻尼弹簧步进 —— 播种失败解 #2：阻尼项符号反（失败簇：冲量符号/能量无界）。

阻尼力写成 +c*v：阻尼变"泵"（pump），能量每步注入，
200 步后 x 发散到数千 cm。弹簧力项正确，单步在小 v 时几乎看不出来。
"""
def spring_step(x, v, k, c, rest, m, dt):
    # BUG: 阻尼项应为 -c*v，这里写成 +c*v，能量不降反升
    a = (-k * (x - rest) + c * v) / m
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new
