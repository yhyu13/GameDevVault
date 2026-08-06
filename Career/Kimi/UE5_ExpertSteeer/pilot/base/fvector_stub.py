"""FVector/FMath 最小 Python 桩 —— 模仿 UE 语义，供 pilot 数学核任务使用。

与 UE 的对应关系（Stage 1 迁移目标）：
- FVector -> 此类的 UE 等价物（float 三元组，成员 X/Y/Z）
- FMath::Clamp / FMath::Lerp / FMath::IsNearlyEqual（容差 KINDA_SMALL_NUMBER=1e-4）
- 单位约定：UE 世界单位是 cm，质量 kg，力 N；重力加速度 -980 cm/s^2
"""

KINDA_SMALL_NUMBER = 1e-4


class FVector:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, o):
        return FVector(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o):
        return FVector(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, s):
        return FVector(self.x * s, self.y * s, self.z * s)

    __rmul__ = __mul__

    def __neg__(self):
        return FVector(-self.x, -self.y, -self.z)

    def Dot(self, o):
        return self.x * o.x + self.y * o.y + self.z * o.z

    def Cross(self, o):
        return FVector(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x,
        )

    def SizeSquared(self):
        return self.Dot(self)

    def Size(self):
        return self.SizeSquared() ** 0.5

    def Normalize(self):
        s = self.Size()
        if s < KINDA_SMALL_NUMBER:
            return FVector(0, 0, 0)
        return self * (1.0 / s)

    def Equals(self, o, tolerance=KINDA_SMALL_NUMBER):
        return (abs(self.x - o.x) <= tolerance and
                abs(self.y - o.y) <= tolerance and
                abs(self.z - o.z) <= tolerance)

    def __repr__(self):
        return f"FVector({self.x}, {self.y}, {self.z})"


class FMath:
    @staticmethod
    def Clamp(v, lo, hi):
        return max(lo, min(v, hi))

    @staticmethod
    def Lerp(a, b, t):
        return a + (b - a) * t

    @staticmethod
    def IsNearlyEqual(a, b, tol=KINDA_SMALL_NUMBER):
        return abs(a - b) <= tol

    @staticmethod
    def SqrtSafe(v):
        return v ** 0.5 if v >= 0 else 0.0
