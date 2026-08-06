"""载具轮纵向力 / 摩擦圆 —— 播种失败解 #1：摩擦圆被忽略（失败簇：载具轮模型/预算误用）。

只按纵向单独 clamp 到 ±mu*Fz，完全没有考虑横向力 Fy 对抓地预算的占用。
横向力大（转弯中急刹）时纵向力被高估：错误的"方摩擦"替代了"圆摩擦"。
代码里找不到 Fy 的使用痕迹——读码可见，但 LLM-judge 经常漏看。
"""
from fvector_stub import FMath


def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    # BUG: 应 Fmax = sqrt((mu*fz)^2 - fy^2)，这里忽略了 fy 占用
    fmax = mu * fz
    return FMath.Clamp(ks * slip, -fmax, fmax)
