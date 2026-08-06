# 任务 rendering_01_frustum_cull：视锥剔除点/包围球测试（6 平面）

## 元信息

- **id**: `rendering_01_frustum_cull`
- **域**: rendering
- **目标模型尺寸**: 0.8B（单函数数值核，视锥平面构建 + 点/球测试）
- **UE C++/shader 形态**（Stage 1 迁移目标）: C++ 侧 `FConvexVolume`（`UWorld::IsPointInFrustum`、`FConvexVolume::IntersectSphere`），视锥 6 平面来自 `UGameViewportClient`/`ViewFrustum`（`FPlane FrustumPlanes[6]`）；shader 侧对应 `Common.ush` 的 `View.SFrustumLeftPlane/RightPlane/TopPlane/BottomPlane/NearPlane/FarPlane`，渲染器实际剔除路径为 `RendererPrivate` 的 frustum cull 内核。pilot 用 Python 软件求值，Stage 1 迁移为 `FPlane`/`FConvexVolume` + 同一数值比对。

## 任务描述（prompt，中文）

> 你是 UE5 渲染工程师。实现视锥剔除的数学核：给定相机参数构建 6 个视锥平面，并实现点/包围球 vs 视锥的可见性测试。
>
> 相机参数：`eye` 相机位置（cm），`forward` 视线方向（单位向量），`up` 上方向（单位向量），`fov_deg` 竖直 FOV（度），`aspect` 宽高比，`near_dist`/`far_dist` 近远裁剪距离（cm，均 > 0）。
>
> 实现：
> - `build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist)`：返回 6 个平面 `(nx, ny, nz, d)`，顺序为 近/远/左/右/下/上，**内法线约定**：点 `p` 在视锥内当且仅当对所有平面 `dot(n, p) + d >= 0`（与 UE `FPlane` 的 W 分量语义一致）。
> - `point_inside_frustum(planes, point, radius=0.0)`：`radius=0` 做点测试；`radius>0` 做包围球测试（平面距离 `>= -radius` 即相交，对应 `FConvexVolume::IntersectSphere`）。
>
> 约束：只用 `math`；右手系与 UE 一致（forward=视线=视深 Z，up=视高 Y，right = forward × up）；FOV 为竖直 FOV；坐标单位为 cm。**平面法线符号错会让"内"“外”整体颠倒；近平面距离错会让相机与近平面之间的物体错误可见。**

## 输入规格

- Python 签名（UE C++ 对应：`FConvexVolume FConvexVolume::GetFrustumFromCamera(...)` + `bool IntersectSphere(...)` / `bool IsPointInFrustum(FVector)`）

```python
def build_frustum_planes(eye, forward, up, fov_deg, aspect, near_dist, far_dist) -> list[tuple[float, float, float, float]]: ...
def point_inside_frustum(planes, point, radius=0.0) -> bool: ...
```

## Golden 解

见 `solutions/rendering_01_frustum_cull/golden.py`。要点：视空间不等式 `near <= dot(fwd, p-eye) <= far`、`|dot(right,p-eye)| <= z*tanH`、`|dot(up,p-eye)| <= z*tanV`（tanH=tanV*aspect），用点法式 `dot(n,p)+d=0` 统一构造 6 平面（侧平面过 eye），`d = -dot(n, p_on_plane)`；测试端一次循环 6 平面、`radius` 偏移即完成球测试——O(6) 无分配。

## Hidden tests

- 平面系数容差：**1e-4**（绝对，逐分量）；判定比对：布尔相等
- 两组相机配置（golden 预计算硬编码，不与解共享代码）：
  - canonical：eye=(0,0,0), fwd=(0,1,0), up=(0,0,1), fov=90, aspect=4/3, near=1, far=100 → 6 平面期望值硬编码（近 (0,1,0,-1)、远 (0,-1,0,100)、左 (0.6,0.8,0,0)、右 (-0.6,0.8,0,0)、下 (0,0.7071067812,0.7071067812,0)、上 (0,0.7071067812,-0.7071067812,0)）
  - rotated：eye=(2,-1,0.5), fwd=(0,0,-1), up=(0,1,0), fov=60, aspect=2, near=0.5, far=40 → 6 平面期望值硬编码（见 verifier）
- 点判定 17 例（含近/远/左右/上下内外、边界附近）、包围球判定 4 例（球心在外但半径相交、球心在 near 前但半径相交、球远外剔除、大球贯穿）

## Judge rubric（L4 维度，每维 0-10）

| 维度 | 说明 | 权重 |
|---|---|---|
| 正确性 | 6 平面系数正确、内外判定正确、球测试语义正确 | 高 |
| API 正确性 | UE 约定正确（内法线/FPlane W 语义、右手系、cm、竖直 FOV、近远>0） | 高 |
| 工程化 | 平面构造参数化（无魔法数）、结构清晰、防御性（正交化修正 up） | 中 |
| 性能意识 | O(6) 逐平面测试、无冗余分配 | 中 |

加权分 = 0.35×正确性 + 0.35×API + 0.15×工程化 + 0.15×性能；PASS 门槛：加权 ≥ 7 且 正确性 ≥ 6。

## 播种失败解（3 个）

| # | 类型（取自失败簇预测表） | 描述 | 文件 |
|---|---|---|---|
| 1 | 符号错误 | 6 个平面 (n,d) 整体取反（外法线），内外判定整体颠倒：视锥内点全部误报剔除 | `fail1_plane_normal_sign.py` |
| 2 | 近平面距离错 | 近平面建在相机原点（near=0）：相机与近平面之间的物体被错误可见 | `fail2_near_plane_distance.py` |
| 3 | 只测中心点漏包围球 | `point_inside_frustum` 忽略 radius：球心在视锥外但球与视锥相交的物体被误剔除（典型闪烁/漏帧） | `fail3_ignore_sphere_radius.py` |
