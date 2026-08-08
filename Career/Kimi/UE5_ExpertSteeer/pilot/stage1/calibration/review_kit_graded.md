# Judge 校准评审包（盲测 v1）— 已评审

## 评审协议

- 共 **36 条**候选（9 任务 × 4 条），每条都是模型对给定任务的实现
- 对每条给出三个字段：**判定**（PASS/FAIL）、**分数**（0-10，≥7 为 PASS）、**理由**（一句话，指出问题或亮点）
- 评分维度（按权重）：正确性（逻辑与边界处理，最重要）→ UE/API 语义 → 工程化（结构/可读/防御性）→ 性能
- 参考：L1 = 导入/签名/禁用模式门禁结果，L3 = 隐藏测试执行结果（L3 失败 ≠ 直接 FAIL，你判断是否可救/是否训练毒药；L3 通过 ≠ 直接 PASS，你判断是否存在测试外错误）
- 填完保存为 `review_kit_graded.md`（在每条的判定行后填），或按序号另存为 JSON 返回
- 注意：**评审人看不到 agent 的自动评分**（防锚定）；填完由流水线算一致性（kappa）

---

## #1 [ PASS ] 两球碰撞冲量解算 —— 候选 `phys_01`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python

from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    if vrel_n > 0.0:
        return FVector(v_a.x, v_a.y, v_a.z), FVector(v_b.x, v_b.y, v_b.z)
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_mass
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
```

**你的判定**：判定: PASS　分数: 9/10　理由: 标准冲量公式 + 分离守卫 + FVector 构造正确，仅缺极端 m=0 的零除防御。

---

## #2 [ PASS ] 两球碰撞冲量解算 —— 候选 `phys_11`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python

from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vn=(v_a-v_b).Dot(normal)
    if vn>0:
        return FVector(v_a.x,v_a.y,v_a.z),FVector(v_b.x,v_b.y,v_b.z)
    j=-(1+restitution)*vn/(1/m_a+1/m_b)
    return v_a+normal*(j/m_a),v_b-normal*(j/m_b)
```

**你的判定**：判定: PASS　分数: 8/10　理由: 与 #1 等价正确但全压一行 + 单字母变量，牺牲可读性无收益。

---

## #3 [ FAIL ] 两球碰撞冲量解算 —— 候选 `phys_16`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`FAIL(1 用例)`

```python

from fvector_stub import FVector

def resolve_impulse(m_a, m_b, v_a, v_b, normal, restitution):
    vrel_n = (v_a - v_b).Dot(normal)
    inv_mass = 1.0 / m_a + 1.0 / m_b
    j = -(1.0 + restitution) * vrel_n / inv_mass
    return v_a + normal * (j / m_a), v_b - normal * (j / m_b)
```

**你的判定**：判定: FAIL　分数: 4/10　理由: 缺分离守卫 `vrel_n > 0`，分离场景仍施加冲量会把已分开物体再次推开（能量注入 bug）。

---

## #4 [ FAIL ] 两球碰撞冲量解算 —— 候选 `phys_24`

- L1（导入/签名门禁）：`FAIL`　L3（隐藏测试执行）：`FAIL(0 用例)`

```python

from fvector_stub import FVector

def resolve_impulse(m1, m2, v1, v2, n, e):
    vrel_n = (v1 - v2).Dot(n)
    if vrel_n > 0.0:
        return FVector(v1.x, v1.y, v1.z), FVector(v2.x, v2.y, v2.z)
    inv = 1.0 / m1 + 1.0 / m2
    j = -(1.0 + e) * vrel_n / inv
    return v1 + n * (j / m1), v2 - n * (j / m2)
```

**你的判定**：判定: FAIL　分数: 3/10　理由: 参数改名 m1/m2/v1/v2/n/e 违反任务签名契约，逻辑对但 L1 必拒，调用方按位置/关键字都解不出。

---

## #5 [ PASS ] 视锥剔除 6 平面 —— 候选 `rend_01`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python

import math

TOL = 1e-9

def _norm(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if s < TOL:
        return (0.0, 0.0, 0.0)
    return (v[0]/s, v[1]/s, v[2]/s)

def _dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _norm(forward)
    upv = _norm(up)
    right = _norm(_cross(fwd, upv))
    upv = _norm(_cross(right, fwd))
    tan_half = math.tan(math.radians(fov_deg) * 0.5)
    tan_h = tan_half * aspect
    tan_v = tan_half
    eye = (float(eye[0]), float(eye[1]), float(eye[2]))

    def make_plane(n_vec, point_on_plane):
        n = _norm(n_vec)
        d = -_dot(n, point_on_plane)
        return (n[0], n[1], n[2], d)

    near_c = (eye[0]+fwd[0]*near_dist, eye[1]+fwd[1]*near_dist, eye[2]+fwd[2]*near_dist)
    far_c = (eye[0]+fwd[0]*far_dist, eye[1]+fwd[1]*far_dist, eye[2]+fwd[2]*far_dist)
    return [
        make_plane(fwd, near_c),
        make_plane((-fwd[0], -fwd[1], -fwd[2]), far_c),
        make_plane((right[0]+tan_h*fwd[0], right[1]+tan_h*fwd[1], right[2]+tan_h*fwd[2]), eye),
        make_plane((-right[0]+tan_h*fwd[0], -right[1]+tan_h*fwd[1], -right[2]+tan_h*fwd[2]), eye),
        make_plane((upv[0]+tan_v*fwd[0], upv[1]+tan_v*fwd[1], upv[2]+tan_v*fwd[2]), eye),
        make_plane((-upv[0]+tan_v*fwd[0], -upv[1]+tan_v*fwd[1], -upv[2]+tan_v*fwd[2]), eye),
    ]

def point_inside_frustum(planes, point, radius=0.0):
    px, py, pz = float(point[0]), float(point[1]), float(point[2])
    for (nx, ny, nz, d) in planes:
        if nx*px + ny*py + nz*pz + d < -radius:
            return False
    return True
```

**你的判定**：判定: PASS　分数: 9/10　理由: 6 平面完整 + 正交基 + 半径偏移 + TOL 防零 + 双段 upv 重新正交，教科书实现。

---

## #6 [ PASS ] 视锥剔除 6 平面 —— 候选 `rend_11`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python

import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward); upv = _n(up)
    right = _n(_c(fwd, upv)); upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    def mk(n, p):
        n = _n(n); return (n[0], n[1], n[2], -sum(n[i]*p[i] for i in range(3)))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
        return True

def _n(v):
    s = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
```

**你的判定**：判定: PASS　分数: 8/10　理由: 等价 #5 正确 + 保留 radius 支持，缺点是分号拼接 + 单字母辅助函数，三个月后自己都读不动。

---

## #7 [ FAIL ] 视锥剔除 6 平面 —— 候选 `rend_17`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`FAIL(3 用例)`

```python

import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, e[2]+fwd[2]*far_dist)
    def mk(nv, p):
        nv = _n(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2]))
    return [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
            mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
            mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
            mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e),
            mk((-upv[0]+t*fwd[0], -upv[1]+t*fwd[1], -upv[2]+t*fwd[2]), e)]

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < 0.0:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
```

**你的判定**：判定: FAIL　分数: 4/10　理由: `point_inside_frustum` 阈值写死 `< 0.0` 丢弃 radius 参数，球体/包围球测试全错，API 签名撒了谎。

---

## #8 [ FAIL ] 视锥剔除 6 平面 —— 候选 `rend_23`

- L1（导入/签名门禁）：`FAIL`　L3（隐藏测试执行）：`FAIL(0 用例)`

```python

import math

def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist):
    fwd = _n(forward)
    upv = _n(up)
    right = _n(_c(fwd, upv))
    upv = _n(_c(right, fwd))
    t = math.tan(math.radians(fov_deg) * 0.5)
    e = (float(eye[0]), float(eye[1]), float(eye[2]))
    nc = (e[0]+fwd[0]*near_dist, e[1]+fwd[1]*near_dist, e[2]+fwd[2]*near_dist)
    fc = (e[0]+fwd[0]*far_dist, e[1]+fwd[1]*far_dist, eye[2]+fwd[2]*far_dist)
    def mk(nv, p):
        nv = _n(nv)
        return (nv[0], nv[1], nv[2], -(nv[0]*p[0] + nv[1]*p[1] + nv[2]*p[2]))
    planes = [mk(fwd, nc), mk((-fwd[0], -fwd[1], -fwd[2]), fc),
              mk((right[0]+t*aspect*fwd[0], right[1]+t*aspect*fwd[1], right[2]+t*aspect*fwd[2]), e),
              mk((-right[0]+t*aspect*fwd[0], -right[1]+t*aspect*fwd[1], -right[2]+t*aspect*fwd[2]), e),
              mk((upv[0]+t*fwd[0], upv[1]+t*fwd[1], upv[2]+t*fwd[2]), e)]
    return planes

def point_inside_frustum(planes, point, radius=0.0):
    for (nx, ny, nz, d) in planes:
        if nx*point[0] + ny*point[1] + nz*point[2] + d < -radius:
            return False
    return True

def _n(v):
    s = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    return (v[0]/s, v[1]/s, v[2]/s) if s > 1e-9 else (0.0, 0.0, 0.0)

def _c(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
```

**你的判定**：判定: FAIL　分数: 2/10　理由: 只返 5 平面（漏 `upv - fwd` 那条），视锥顶/底开放，所有靠近天顶地底的物体会被错判。

---

## #9 [ PASS ] 阻尼弹簧半隐式欧拉步进 —— 候选 `spr_01`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python
def spring_step(x, v, k, c, rest, m, dt):
    """阻尼弹簧半隐式欧拉单步：a -> v' -> x'（用新速度更新位置）。"""
    a = (-k * (x - rest) - c * v) / m
    v_new = v + a * dt
    x_new = x + v_new * dt
    return x_new, v_new
```

**你的判定**：判定: PASS　分数: 9/10　理由: 半隐式欧拉标准写法 a→v'→x'，docstring 与实现一致，签名清晰。

---

## #10 [ PASS ] 阻尼弹簧半隐式欧拉步进 —— 候选 `spr_10`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python
def spring_step(x,v,k,c,rest,m,dt):
    a=(-k*(x-rest)-c*v)/m
    v=v+a*dt
    x=x+v*dt
    return x,v
```

**你的判定**：判定: PASS　分数: 8/10　理由: 与 #9 等价正确，扣 1 分因无 docstring 且单字母参数 + 原地修改 v/x 增加调试成本。

---

## #11 [ FAIL ] 阻尼弹簧半隐式欧拉步进 —— 候选 `spr_14`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`FAIL(4 用例)`

```python
def spring_step(x, v, k, c, rest, m, dt):
    a = (-k * (x - rest) - c * v) / m
    x_new = x + v * dt
    v_new = v + a * dt
    return x_new, v_new
```

**你的判定**：判定: FAIL　分数: 3/10　理由: 用 OLD 速度 `v*dt` 更新 x_new，是显式（symplectic）欧拉不是半隐式，任务名/合同都未满足；高温发散就是它的下场。

---

## #12 [ FAIL ] 阻尼弹簧半隐式欧拉步进 —— 候选 `spr_18`

- L1（导入/签名门禁）：`FAIL`　L3（隐藏测试执行）：`FAIL(0 用例)`

```python
def spring_step(x0, v0, kk, cc, rest, m, dt):
    a = (-kk * (x0 - rest) - cc * v0) / m
    v_new = v0 + a * dt
    x_new = x0 + v_new * dt
    return x_new, v_new
```

**你的判定**：判定: FAIL　分数: 3/10　理由: 参数改名 x0/v0/kk/cc 违反签名契约，逻辑对但 L1 不放过；不可救的训练毒药（鼓励改 API 命名）。

---

## #13 [ PASS ] 载具轮纵向力/摩擦圆 —— 候选 `whl_01`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python

from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    """摩擦圆纵向力：剩余预算 sqrt((mu*fz)^2 - fy^2)，抓地耗尽归零。"""
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
```

**你的判定**：判定: PASS　分数: 9/10　理由: 摩擦圆公式正确 + SqrtSafe 防御负数（抓地耗尽时返 0 而非 nan）+ docstring 解释清。

---

## #14 [ PASS ] 载具轮纵向力/摩擦圆 —— 候选 `whl_10`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python

from fvector_stub import FMath

def wheel_longitudinal_force(slip,fz,fy,mu,ks):
    if fz<=0.0:
        return 0.0
    fmax=FMath.SqrtSafe((mu*fz)**2-fy*fy)
    return FMath.Clamp(ks*slip,-fmax,fmax)
```

**你的判定**：判定: PASS　分数: 8/10　理由: 与 #13 等价正确（含 ** 优先级正确），扣分因全压一行 + 无 docstring。

---

## #15 [ FAIL ] 载具轮纵向力/摩擦圆 —— 候选 `whl_14`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`FAIL(3 用例)`

```python

from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    return FMath.Clamp(ks * slip, -grip, grip)
```

**你的判定**：判定: FAIL　分数: 3/10　理由: 完全忽略 fy² 项，grip 简化为 μ·fz，违反摩擦圆定义；大侧向力时仍给满纵向力，会穿透抓地。

---

## #16 [ FAIL ] 载具轮纵向力/摩擦圆 —— 候选 `whl_18`

- L1（导入/签名门禁）：`FAIL`　L3（隐藏测试执行）：`FAIL(0 用例)`

```python

import random
from fvector_stub import FMath

def wheel_longitudinal_force(slip, fz, fy, mu, ks):
    if fz <= 0.0:
        return 0.0
    grip = mu * fz
    fmax = FMath.SqrtSafe(grip * grip - fy * fy)
    return FMath.Clamp(ks * slip, -fmax, fmax)
```

**你的判定**：判定: FAIL　分数: 3/10　理由: 逻辑正确但 `import random` 触发 L1（禁用模式/无关依赖），且引入未使用的随机源属于训练毒药。

---

## #17 [ PASS ] LOD 距离选择（迟滞） —— 候选 `lod_01`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python
def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    """LOD 选择（带迟滞）。升级需越过 t[i-1]*(1+hyst)，降级需跌破 t[i]*(1-hyst)。"""
    if not thresholds:
        return 0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    if current_lod is None:
        return base
    lod = current_lod
    while lod > 0 and screen_size >= thresholds[lod - 1] * (1.0 + hysteresis):
        lod -= 1
    if lod < len(thresholds) - 1 and screen_size < thresholds[lod] * (1.0 - hysteresis):
        lod += 1
    return lod
```

**你的判定**：判定: PASS　分数: 9/10　理由: 升级/降级双带迟滞 + base 默认 + current_lod None 分支，docstring 解释清上下带规则。

---

## #18 [ PASS ] LOD 距离选择（迟滞） —— 候选 `lod_10`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python
def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    base=len(thresholds)-1
    for i,t in enumerate(thresholds):
        if screen_size>=t:
            base=i; break
    if current_lod is None:
        return base
    lod=current_lod
    while lod>0 and screen_size>=thresholds[lod-1]*(1.0+hysteresis):
        lod-=1
    if lod<len(thresholds)-1 and screen_size<thresholds[lod]*(1.0-hysteresis):
        lod+=1
    return lod
```

**你的判定**：判定: PASS　分数: 8/10　理由: 与 #17 等价正确，扣分因全压一行 + 无 docstring。

---

## #19 [ FAIL ] LOD 距离选择（迟滞） —— 候选 `lod_14`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`FAIL(3 用例)`

```python
def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    return base
```

**你的判定**：判定: FAIL　分数: 4/10　理由: 完全丢掉迟滞逻辑直接返 base，`current_lod` / `hysteresis` 两个参数形同虚设，任务完成度 0%。

---

## #20 [ FAIL ] LOD 距离选择（迟滞） —— 候选 `lod_17`

- L1（导入/签名门禁）：`FAIL`　L3（隐藏测试执行）：`FAIL(0 用例)`

```python
def select_lod(current_lod, screen_size, thresholds, hysteresis=0.1):
    if not thresholds:
        return 0.0
    base = len(thresholds) - 1
    for i, t in enumerate(thresholds):
        if screen_size >= t:
            base = i
            break
    return float(base)
```

**你的判定**：判定: FAIL　分数: 3/10　理由: 返 `float(base)` 而非 int（LOD 应为整数索引）+ 空列表返 0.0 类型不一致，契约违例。

---

## #21 [ PASS ] linear→sRGB（IEC 61966-2-1） —— 候选 `srgb_01`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python
import math

THRESHOLD = 0.0031308
LINEAR_COEF = 12.92
A = 1.055
B = 0.055
GAMMA = 2.4


def linear_to_srgb(c):
    """IEC 61966-2-1：线性段 + 幂段，越界先 clamp。"""
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        if v <= THRESHOLD:
            out.append(LINEAR_COEF * v)
        else:
            out.append(A * v ** (1.0 / GAMMA) - B)
    return tuple(out)
```

**你的判定**：判定: PASS　分数: 9/10　理由: 完整双段 + clamp + 命名常量 + tuple 返回，docstring 标标准编号，教科书。

---

## #22 [ PASS ] linear→sRGB（IEC 61966-2-1） —— 候选 `srgb_10`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python
import math

def linear_to_srgb(c):
    out=[]
    for v in c:
        v=max(0.0,min(1.0,v))
        out.append(12.92*v if v<=0.0031308 else 1.055*v**(1.0/2.4)-0.055)
    return tuple(out)
```

**你的判定**：判定: PASS　分数: 8/10　理由: 与 #21 等价正确，扣分因全压一行 + 常量内联（无命名）。

---

## #23 [ FAIL ] linear→sRGB（IEC 61966-2-1） —— 候选 `srgb_14`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`FAIL(2 用例)`

```python
import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        out.append(1.055 * v ** (1.0 / 2.4) - 0.055)
    return tuple(out)
```

**你的判定**：判定: FAIL　分数: 4/10　理由: 丢线性段 `v ≤ 0.0031308` 的 12.92*v 分支，低亮度区被 1.055*v^0.417 压得过暗，黑位失真。

---

## #24 [ FAIL ] linear→sRGB（IEC 61966-2-1） —— 候选 `srgb_17`

- L1（导入/签名门禁）：`FAIL`　L3（隐藏测试执行）：`FAIL(0 用例)`

```python
import math

def linear_to_srgb(c):
    out = []
    for v in c:
        v = max(0.0, min(1.0, v))
        out.append(12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055)
    return out[:2]
```

**你的判定**：判定: FAIL　分数: 2/10　理由: 末尾 `out[:2]` 把结果硬截到 2 分量，RGBA 通道直接砍；任何 RGB 输入返 tuple 长度都不匹配。

---

## #25 [ PASS ] Niagara 配置校验+预算 —— 候选 `fx1_01`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python

BUDGET = 67108864


def validate_niagara_config(cfg):
    errors = []
    for name, typ in (("emitter_name", str), ("spawn_rate", float), ("particle_lifetime", float),
                      ("max_particles", int), ("bytes_per_particle", int)):
        if name not in cfg:
            errors.append(f"缺少字段 {name}")
        elif not isinstance(cfg[name], typ):
            errors.append(f"字段 {name} 类型应为 {typ.__name__}")
    if "spawn_rate" in cfg and isinstance(cfg["spawn_rate"], (int, float)) and not (0 < cfg["spawn_rate"] <= 1e6):
        errors.append("字段 spawn_rate 范围应为 (0, 1e6]")
    if "particle_lifetime" in cfg and isinstance(cfg["particle_lifetime"], (int, float)) and not (0 < cfg["particle_lifetime"] <= 60):
        errors.append("字段 particle_lifetime 范围应为 (0, 60]")
    if "max_particles" in cfg and isinstance(cfg["max_particles"], int) and not (1 <= cfg["max_particles"] <= 1e7):
        errors.append("字段 max_particles 范围应为 [1, 1e7]")
    if "bytes_per_particle" in cfg and isinstance(cfg["bytes_per_particle"], int) and not (16 <= cfg["bytes_per_particle"] <= 4096):
        errors.append("字段 bytes_per_particle 范围应为 [16, 4096]")
    if errors:
        return {"valid": False, "errors": errors, "peak_particles": 0.0, "memory_bytes": 0.0}
    peak, memory = compute_niagara_budget(cfg["spawn_rate"], cfg["particle_lifetime"], cfg["bytes_per_particle"])
    if peak > cfg["max_particles"]:
        errors.append(f"峰值粒子数 {peak} 超过 max_particles {cfg['max_particles']}")
    if memory > BUDGET:
        errors.append(f"内存 {memory} 字节超过默认预算 64 MiB")
    return {"valid": not errors, "errors": errors, "peak_particles": peak, "memory_bytes": memory}


def compute_niagara_budget(spawn_rate, particle_lifetime, bytes_per_particle):
    peak = spawn_rate * particle_lifetime
    return peak, peak * bytes_per_particle
```

**你的判定**：判定: PASS　分数: 9/10　理由: 字段存在/类型/范围/预算四检 + 错误优先短路 + 拆出独立 compute 函数，结构清晰易测。

---

## #26 [ PASS ] Niagara 配置校验+预算 —— 候选 `fx1_10`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python

BUDGET=67108864

def validate_niagara_config(cfg):
    errors=[]
    for name,typ in (("emitter_name",str),("spawn_rate",float),("particle_lifetime",float),("max_particles",int),("bytes_per_particle",int)):
        if name not in cfg:
            errors.append(f"缺少字段 {name}")
        elif not isinstance(cfg[name],typ):
            errors.append(f"字段 {name} 类型应为 {typ.__name__}")
    if "spawn_rate" in cfg and isinstance(cfg["spawn_rate"],(int,float)) and not (0<cfg["spawn_rate"]<=1e6):
        errors.append("字段 spawn_rate 范围应为 (0, 1e6]")
    if "particle_lifetime" in cfg and isinstance(cfg["particle_lifetime"],(int,float)) and not (0<cfg["particle_lifetime"]<=60):
        errors.append("字段 particle_lifetime 范围应为 (0, 60]")
    if "max_particles" in cfg and isinstance(cfg["max_particles"],int) and not (1<=cfg["max_particles"]<=1e7):
        errors.append("字段 max_particles 范围应为 [1, 1e7]")
    if "bytes_per_particle" in cfg and isinstance(cfg["bytes_per_particle"],int) and not (16<=cfg["bytes_per_particle"]<=4096):
        errors.append("字段 bytes_per_particle 范围应为 [16, 4096]")
    if errors:
        return {"valid":False,"errors":errors,"peak_particles":0.0,"memory_bytes":0.0}
    peak,memory=compute_niagara_budget(cfg["spawn_rate"],cfg["particle_lifetime"],cfg["bytes_per_particle"])
    if peak>cfg["max_particles"]:
        errors.append(f"峰值粒子数 {peak} 超过 max_particles {cfg['max_particles']}")
    if memory>BUDGET:
        errors.append(f"内存 {memory} 字节超过默认预算 64 MiB")
    return {"valid":not errors,"errors":errors,"peak_particles":peak,"memory_bytes":memory}

def compute_niagara_budget(spawn_rate,particle_lifetime,bytes_per_particle):
    peak=spawn_rate*particle_lifetime
    return peak,peak*bytes_per_particle
```

**你的判定**：判定: PASS　分数: 8/10　理由: 与 #25 等价正确，扣分因全压一行 + 难快速扫读 if 链。

---

## #27 [ FAIL ] Niagara 配置校验+预算 —— 候选 `fx1_15`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`FAIL(3 用例)`

```python

BUDGET = 67108864


def validate_niagara_config(cfg):
    errors = []
    for name, typ in (("emitter_name", str), ("spawn_rate", float), ("particle_lifetime", float),
                      ("max_particles", int), ("bytes_per_particle", int)):
        if name not in cfg:
            errors.append(f"缺少字段 {name}")
        elif not isinstance(cfg[name], typ):
            errors.append(f"字段 {name} 类型应为 {typ.__name__}")
    if "spawn_rate" in cfg and isinstance(cfg["spawn_rate"], (int, float)) and not (0 < cfg["spawn_rate"] <= 1e6):
        errors.append("字段 spawn_rate 范围应为 (0, 1e6]")
    if "particle_lifetime" in cfg and isinstance(cfg["particle_lifetime"], (int, float)) and not (0 < cfg["particle_lifetime"] <= 60):
        errors.append("字段 particle_lifetime 范围应为 (0, 60]")
    if "max_particles" in cfg and isinstance(cfg["max_particles"], int) and not (1 <= cfg["max_particles"] <= 1e7):
        errors.append("字段 max_particles 范围应为 [1, 1e7]")
    if "bytes_per_particle" in cfg and isinstance(cfg["bytes_per_particle"], int) and not (16 <= cfg["bytes_per_particle"] <= 4096):
        errors.append("字段 bytes_per_particle 范围应为 [16, 4096]")
    if errors:
        return {"valid": False, "errors": errors, "peak_particles": 0.0, "memory_bytes": 0.0}
    peak, memory = compute_niagara_budget(cfg["spawn_rate"], cfg["particle_lifetime"], cfg["bytes_per_particle"])
    if peak > cfg["max_particles"]:
        errors.append(f"峰值粒子数 {peak} 超过 max_particles {cfg['max_particles']}")
    if memory > BUDGET:
        errors.append(f"内存 {memory} 字节超过默认预算 64 MiB")
    return {"valid": not errors, "errors": errors, "peak_particles": peak, "memory_bytes": memory}


def compute_niagara_budget(spawn_rate, particle_lifetime, bytes_per_particle):
    peak = int(spawn_rate * particle_lifetime)
    return peak, peak * bytes_per_particle
```

**你的判定**：判定: FAIL　分数: 4/10　理由: `peak = int(...)` 强转整数，与早返 0.0 / 文档暗示的浮点类型契约不一致，下游按浮点处理会偶现类型断言。

---

## #28 [ FAIL ] Niagara 配置校验+预算 —— 候选 `fx1_17`

- L1（导入/签名门禁）：`FAIL`　L3（隐藏测试执行）：`FAIL(0 用例)`

```python

BUDGET = 67108864


def validate_niagara_config(cfg):
    errors = []
    for name, typ in (("emitter_name", str), ("spawn_rate", float), ("particle_lifetime", float),
                      ("max_particles", int), ("bytes_per_particle", int)):
        if name not in cfg:
            errors.append(f"缺少字段 {name}")
        elif not isinstance(cfg[name], typ):
            errors.append(f"字段 {name} 类型应为 {typ.__name__}")
    if "spawn_rate" in cfg and isinstance(cfg["spawn_rate"], (int, float)) and not (0 < cfg["spawn_rate"] <= 1e6):
        errors.append("字段 spawn_rate 范围应为 (0, 1e6]")
    if "particle_lifetime" in cfg and isinstance(cfg["particle_lifetime"], (int, float)) and not (0 < cfg["particle_lifetime"] <= 60):
        errors.append("字段 particle_lifetime 范围应为 (0, 60]")
    if "max_particles" in cfg and isinstance(cfg["max_particles"], int) and not (1 <= cfg["max_particles"] <= 1e7):
        errors.append("字段 max_particles 范围应为 [1, 1e7]")
    if "bytes_per_particle" in cfg and isinstance(cfg["bytes_per_particle"], int) and not (16 <= cfg["bytes_per_particle"] <= 4096):
        errors.append("字段 bytes_per_particle 范围应为 [16, 4096]")
    if errors:
        return {"valid": False, "errors": errors, "peak_particles": 0.0, "memory_bytes": 0.0}
    peak, memory = cfg["spawn_rate"] * cfg["particle_lifetime"], cfg["spawn_rate"] * cfg["particle_lifetime"] * cfg["bytes_per_particle"]
    if peak > cfg["max_particles"]:
        errors.append(f"峰值粒子数 {peak} 超过 max_particles {cfg['max_particles']}")
    if memory > BUDGET:
        errors.append(f"内存 {memory} 字节超过默认预算 64 MiB")
    return {"valid": not errors, "errors": errors, "peak_particles": peak, "memory_bytes": memory}
```

**你的判定**：判定: FAIL　分数: 5/10　理由: 逻辑正确但未提供 `compute_niagara_budget` 公共函数（L1 期望其存在以便复用/单测），任务契约缺失。

---

## #29 [ PASS ] 3D curl noise —— 候选 `fx2_01`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python

import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    """v = curl(Psi)：vx = dpsi_z/dy - dpsi_y/dz 等，divergence-free。"""
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
```

**你的判定**：判定: PASS　分数: 9/10　理由: curl 三轴符号/索引全对 + 标 divergence-free 性质 + 辅助函数 + docstring 自洽。

---

## #30 [ PASS ] 3D curl noise —— 候选 `fx2_10`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python

import math

DIRS=((0.6,0.8,0.0),(0.0,0.6,0.8),(0.8,0.0,0.6))
FREQS=(1.0,2.0,4.0)
SPEEDS=(0.5,1.0,1.5)
PHASES=((0.1,0.7,1.3),(2.1,0.3,1.7),(1.1,2.3,0.9))

def _dpsi(axis,j,p,t):
    acc=0.0
    for k in range(3):
        amp=1.0/(k+1.0)
        dot=DIRS[k][0]*p[0]+DIRS[k][1]*p[1]+DIRS[k][2]*p[2]
        arg=2.0*math.pi*FREQS[k]*dot+t*SPEEDS[k]+PHASES[axis][k]
        acc+=amp*2.0*math.pi*FREQS[k]*DIRS[k][j]*math.cos(arg)
    return acc

def curl_noise3d(p,t):
    return (_dpsi(2,1,p,t)-_dpsi(1,2,p,t),_dpsi(0,2,p,t)-_dpsi(2,0,p,t),_dpsi(1,0,p,t)-_dpsi(0,1,p,t))
```

**你的判定**：判定: PASS　分数: 8/10　理由: 与 #29 等价正确，扣分因全压一行（_dpsi 内部三行压一行尤其难读）+ 无 docstring。

---

## #31 [ FAIL ] 3D curl noise —— 候选 `fx2_14`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`FAIL(6 用例)`

```python

import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) + _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    vz = _dpsi(1, 0, p, t) - _dpsi(0, 1, p, t)
    return (vx, vy, vz)
```

**你的判定**：判定: FAIL　分数: 3/10　理由: vx 写成 `+` 号（应为 `-`），curl 公式符号错，divergence-free 性质被破坏；6 用例全挂说明是普遍偏差不是边界。

---

## #32 [ FAIL ] 3D curl noise —— 候选 `fx2_18`

- L1（导入/签名门禁）：`FAIL`　L3（隐藏测试执行）：`FAIL(0 用例)`

```python

import math

DIRS = ((0.6, 0.8, 0.0), (0.0, 0.6, 0.8), (0.8, 0.0, 0.6))
FREQS = (1.0, 2.0, 4.0)
SPEEDS = (0.5, 1.0, 1.5)
PHASES = ((0.1, 0.7, 1.3), (2.1, 0.3, 1.7), (1.1, 2.3, 0.9))


def _dpsi(axis, j, p, t):
    acc = 0.0
    for k in range(3):
        amp = 1.0 / (k + 1.0)
        dot = DIRS[k][0] * p[0] + DIRS[k][1] * p[1] + DIRS[k][2] * p[2]
        arg = 2.0 * math.pi * FREQS[k] * dot + t * SPEEDS[k] + PHASES[axis][k]
        acc += amp * 2.0 * math.pi * FREQS[k] * DIRS[k][j] * math.cos(arg)
    return acc


def curl_noise3d(p, t):
    vx = _dpsi(2, 1, p, t) - _dpsi(1, 2, p, t)
    vy = _dpsi(0, 2, p, t) - _dpsi(2, 0, p, t)
    return (vx, vy)
```

**你的判定**：判定: FAIL　分数: 2/10　理由: 返 2 元组缺 vz，"3D curl noise" 名存实亡；任何下游解包 `x,y,z` 必抛 ValueError。

---

## #33 [ PASS ] flipbook 帧号→行列+UV —— 候选 `fx3_01`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python
def flipbook_uv(frame, cols, rows, wrap):
    """帧号 -> (col, row)。wrap 取模总帧数，否则钳到末帧。"""
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)


def flipbook_uv_rect(frame, cols, rows, wrap):
    """UV 矩形 (u0, v0, u1, v1)，v 向下约定。"""
    col, row = flipbook_uv(frame, cols, rows, wrap)
    u0 = col / cols
    u1 = (col + 1) / cols
    v1 = 1.0 - row / rows
    v0 = 1.0 - (row + 1) / rows
    return (u0, v0, u1, v1)
```

**你的判定**：判定: PASS　分数: 9/10　理由: 行列公式正确 + UV 矩形 + v 向下约定明确 + wrap/non-wrap 双分支 + 两个函数 docstring 完整。

---

## #34 [ PASS ] flipbook 帧号→行列+UV —— 候选 `fx3_10`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`PASS`

```python
def flipbook_uv(frame,cols,rows,wrap):
    total=cols*rows
    f=frame%total if wrap else min(frame,total-1)
    return (f%cols,f//cols)

def flipbook_uv_rect(frame,cols,rows,wrap):
    col,row=flipbook_uv(frame,cols,rows,wrap)
    return (col/cols,1.0-(row+1)/rows,(col+1)/cols,1.0-row/rows)
```

**你的判定**：判定: PASS　分数: 8/10　理由: 与 #33 等价正确（含 col,row=... 临时变量名保留语义），扣分因全压一行 + 无 docstring。

---

## #35 [ FAIL ] flipbook 帧号→行列+UV —— 候选 `fx3_14`

- L1（导入/签名门禁）：`PASS`　L3（隐藏测试执行）：`FAIL(5 用例)`

```python
def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f // rows, f % rows)


def flipbook_uv_rect(frame, cols, rows, wrap):
    col, row = flipbook_uv(frame, cols, rows, wrap)
    return (col / cols, 1.0 - (row + 1) / rows, (col + 1) / cols, 1.0 - row / rows)
```

**你的判定**：判定: FAIL　分数: 3/10　理由: `(f // rows, f % rows)` 行列写反，flipbook 帧序约定是 (col, row) = (f%cols, f//cols)；UV 矩形跟着错位，所有 5 用例挂在最基本映射上。

---

## #36 [ FAIL ] flipbook 帧号→行列+UV —— 候选 `fx3_17`

- L1（导入/签名门禁）：`FAIL`　L3（隐藏测试执行）：`FAIL(0 用例)`

```python
def flipbook_uv(frame, cols, rows, wrap):
    total = cols * rows
    f = frame % total if wrap else min(frame, total - 1)
    return (f % cols, f // cols)
```

**你的判定**：判定: FAIL　分数: 3/10　理由: 只实现 `flipbook_uv`，缺 `flipbook_uv_rect` 整个函数（L1 期望两 API 都存在），任务完成一半。

---

## 评审完成摘要

- PASS: 18 条（#1, #2, #5, #6, #9, #10, #13, #14, #17, #18, #21, #22, #25, #26, #29, #30, #33, #34）
- FAIL: 18 条（#3, #4, #7, #8, #11, #12, #15, #16, #19, #20, #23, #24, #27, #28, #31, #32, #35, #36）

PASS 集中在「优」(9/10) 与「中」(8/10) 候选；FAIL 集中在「失败」(3-4/10) 与「API 违例」(2-3/10) 候选。
