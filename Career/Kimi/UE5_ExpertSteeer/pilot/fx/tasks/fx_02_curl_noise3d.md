# 任务 fx_02_curl_noise3d：3D curl noise 数值核（正弦叠加势场 → curl）

## 元信息

- **id**: `fx_02_curl_noise3d`
- **域**: fx
- **目标模型尺寸**: 0.8B（单函数/单表达式数值核）
- **UE C++ 形态**（Stage 1 迁移目标）: Niagara 模块 HLSL 中的 curl noise 函数（如 `CustomHLSL`/Niagara 模块里对粒子施加湍流速度）；pilot 用 Python 软件求值做数值比对（Stage 1 换 DXC 编译 + 同一数值比对）。

## 任务描述（prompt，中文）

> 你是 UE5 特效工程师。实现 3D curl noise：速度场 `v = curl(Psi)`，其中 `Psi = (psi_x, psi_y, psi_z)` 是三个标量势场（正弦叠加近似），`p = (x, y, z)` 为世界坐标（cm），`t` 为时间（秒）。
>
> 势场定义（必须与此规格一致）：
> ```
> psi_i(p, t) = sum_{k=0}^{2} amp_k * sin(2*pi*f_k*(w_k . p) + t*s_k + phase[i][k])
> amp_k = 1/(k+1)   f_k = 2^k   s_k = (0.5, 1.0, 1.5)
> w_0=(0.6,0.8,0.0)  w_1=(0.0,0.6,0.8)  w_2=(0.8,0.0,0.6)
> phase = ((0.1,0.7,1.3), (2.1,0.3,1.7), (1.1,2.3,0.9))
> ```
> 速度场（curl 标准符号约定，**符号错会破坏 divergence-free**）：
> ```
> vx = ∂psi_z/∂y − ∂psi_y/∂z
> vy = ∂psi_x/∂z − ∂psi_z/∂x
> vz = ∂psi_y/∂x − ∂psi_x/∂y
> ```
> 实现 `curl_noise3d(p, t)` 返回 `(vx, vy, vz)`。约束：只用 `math`；幅度衰减 `1/(k+1)` 必须保留（高频项压不掉会撕裂画面）；时间项 `t*s_k` 必须参与（静止场不是 curl noise）。

## 输入规格

- Python 签名（UE C++ 对应：`FVector CurlNoise3D(const FVector& P, float Time)`，Stage 1 迁移到 HLSL 标量版本）

```python
def curl_noise3d(p: tuple[float, float, float], t: float) -> tuple[float, float, float]: ...
```

## Golden 解

见 `solutions/fx_02_curl_noise3d/golden.py`。要点：`_dpsi(axis, j, p, t)` 统一求偏导（`d psi_i/d p_j = sum_k amp_k * 2π f_k * (w_k)_j * cos(arg_k)`），curl 三分量各由两次偏导相减构成——结构上保证 divergence-free。

## Hidden tests

- 容差：数值比对 **1e-4**（绝对）
- 已知输入/输出对（由 golden 预计算硬编码）：
  - `(0.3, 0.7, 0.2), t=0.0` → `(0.5221411308, -1.1468744115, 2.0423511095)`
  - `(1.1, -0.4, 0.9), t=2.0` → `(2.2067505074, -3.3493523517, 3.7620677580)`
  - `(0, 0, 0), t=0.5` → `(-2.0816721902, -0.7915578656, -13.8991641125)`
  - `(3.7, 2.9, -1.8), t=-1.25` → `(6.4357722364, -2.2936853908, 2.4879074241)`
- 性质测试：divergence-free，中心差分（h=1e-4）在 `(0.5,0.5,0.5) t=1.0` 与 `(1.7,-0.9,0.3) t=0.3` 两点 `|div| ≤ 1e-2`

## Judge rubric（L4 维度，每维 0-10）

| 维度 | 说明 | 权重 |
|---|---|---|
| 正确性 | 数值与规格一致、时间项与幅度衰减正确、divergence-free | 高 |
| API 正确性 | 数学约定正确（curl 符号、cm 单位、时间秒） | 高 |
| 工程化 | 势场/偏导参数化（DIRS/FREQS/PHASES 常量），无魔法数硬编码 | 中 |
| 性能意识 | O(octave) 复杂度、无重复计算 | 中 |

加权分 = 0.35×正确性 + 0.35×API + 0.15×工程化 + 0.15×性能；PASS 门槛：加权 ≥ 7 且 正确性 ≥ 6。

## 播种失败解（3 个）

| # | 类型（取自失败簇预测表） | 描述 | 文件 |
|---|---|---|---|
| 1 | 符号错误 | `vx = ∂psi_z/∂y + ∂psi_y/∂z`（应为相减），数值偏差大且 divergence 达 ~188 | `fail1_sign_error.py` |
| 2 | 时间/寿命数学错 | `t` 被冻结为 0.0（静态场）；t=0 时侥幸正确，t≠0 全错 | `fail2_frozen_time.py` |
| 3 | 数值/幅度错 | octave 衰减 `1/(k+1)` 丢失（全部等权），高频项放大，数值系统性偏差 | `fail3_no_amplitude_falloff.py` |
