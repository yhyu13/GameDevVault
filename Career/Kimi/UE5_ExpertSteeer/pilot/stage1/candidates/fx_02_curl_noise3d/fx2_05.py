import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def curl_noise3d(p, t):
    """v = curl(Psi)。每分量 = 两次偏导之差，divergence-free。"""
    vx = 0.0
    vy = 0.0
    vz = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        w = DIRS[k]
        dot = w[0] * p[0] + w[1] * p[1] + w[2] * p[2]
        c = 2.0 * math.pi * FREQS[k]
        base = c * dot + t * SPEEDS[k]
        vx += amp * c * w[1] * math.cos(base + PHASES[2][k])
        vx -= amp * c * w[2] * math.cos(base + PHASES[1][k])
        vy += amp * c * w[2] * math.cos(base + PHASES[0][k])
        vy -= amp * c * w[0] * math.cos(base + PHASES[2][k])
        vz += amp * c * w[0] * math.cos(base + PHASES[1][k])
        vz -= amp * c * w[1] * math.cos(base + PHASES[0][k])
    return (vx, vy, vz)
