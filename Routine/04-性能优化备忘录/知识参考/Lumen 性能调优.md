---
tags: [perf/GPU, perf/Lumen, perf/lighting]
aliases: [Lumen perf, Lumen 调优]
---

# Lumen — 已验证的事实清单

> 本笔记**只收录**有官方文档 / GDC 演讲 / UE 源码支撑的事实。所有启发式判断和未验证数字一律删除。
>
> 如需快速判断调参方向，先看 `[[性能优化方法论]]` 的 Profile 黄金三问；本文只回答"Lumen 是什么、它的可调旋钮有哪些、默认值是什么"。
>
> **主要来源**：
> - UE 5.7 官方文档：[Lumen Technical Details](https://docs.unrealengine.com/5.7/en-US/lumen-technical-details-in-unreal-engine)
> - UE 5.7 官方文档：[Lumen Performance Guide](https://docs.unrealengine.com/5.7/en-US/lumen-performance-guide-in-unreal-engine)（推荐配合看）
> - 官方优化专题：[Ray Tracing Performance Guide](https://docs.unrealengine.com/5.7/en-US/ray-tracing-performance-guide-in-unreal-engine)

---

## 一、Lumen 是什么 [D]

> **来源**：UE 5.7 官方 Lumen Technical Details

- Lumen 是 UE5 的**动态全局光照 + 反射**系统
- 用多种光线追踪方法（先 Screen Trace，再用更可靠的方法兜底）
- 支持两种光线追踪：**Hardware Ray Tracing** 与 **Software Ray Tracing**（Mesh Distance Field）
- **Hardware Ray Tracing 是默认开启的**（官方文档原话："Hardware ray tracing provides higher quality and is enabled by default, but it requires dedicated video card support and is more expensive"）
- **不兼容**：Static Lighting（lightmap）/ Forward Shading / VR / 旧主机（PS4/Xbox One）

---

## 二、Software vs Hardware Ray Tracing — 平台要求 [D]

| 模式 | 平台要求 | 几何支持 |
|------|----------|---------|
| **Software** | DX12 + SM6；NVIDIA GTX-1070+；Android Vulkan；Linux Vulkan | 仅 Static Mesh / ISM / HISM / Landscape |
| **Hardware** | Win10 DX12 或 Linux Vulkan；NVIDIA RTX-2000+ / AMD RX-6000+；PS5；Xbox Series S/X | 支持 skinned mesh（蒙皮） |

- **Source**：[Lumen Technical Details] > Lumen Platform Support
- **WPO 不被 Software 模式支持**（WPO 是常见于草、树的顶点动画）。**5.1+ 的 Programmable Rasterizer + Nanite 才能跑带 WPO 的 Nanite 资产**

---

## 三、硬件加速 / 探测几何的事实 [D]

- Lumen 用 **Surface Cache** 加速 GI 查询：每个 mesh 自动参数化为多角度捕获（"Cards"），用于在射线命中点快速查找光照
  - **Source**：[Lumen Technical Details] > Surface Cache
- 默认每个 mesh 放 **12 张 Card**（可通过 Static Mesh Editor 的 "Max Lumen Mesh Cards" 增加）
- 默认 Lumen 场景（Software 模式）覆盖相机 **200m**，可通过 Post Process Volume 的 "Lumen Scene View Distance" 提到 **800m**
- **Hardware 模式**默认在 `Max Trace Distance`（默认 200m）之后继续到 `r.LumenScene.FarField.MaxtraceDistance`（默认 **1 公里**），需要 World Partition HLOD + `r.LumenScene.FarField=1`
- **追踪精度切换**：Software 模式 `Detail Tracing`（默认，前 2m 用 mesh DF，其余用 Global DF）vs `Global Tracing`（全程 Global DF，最快但最差）

---

## 四、可直接调的 CVar / Post Process 设置 [D]

> 这些是**真实存在**的 CVar / Post Process 设置。**默认值列出来**，但具体场景下能省多少**本文不主张**——参考 `[[性能优化方法论]]`，自己 Profile。

### 4.1 反射 Lumen Reflections

| 设置 | 位置 | 备注 |
|------|------|------|
| Lumen Scene Quality | Post Process Volume | 控反射 / GI 的内部质量 |
| Lumen Scene Detail | Post Process Volume | 控 Scene 中纳入的 mesh 大小 |
| Lumen Scene View Distance | Post Process Volume | 0–800m，Software 模式生效 |
| Ray Lighting Mode | Project / Post Process Volume | "Hit Lighting for Reflections"：高质量但贵 |

### 4.2 切换 RT 模式

| CVar | 默认 | 含义 |
|------|------|------|
| `r.Lumen.HardwareRayTracing` | 1 (UE5 默认 Hardware) | 切到 Software 时设为 0 |
| `r.LumenScene.FarField` | 0 | Hardware 模式启用 Far Field 1km 远场 GI |
| `r.LumenScene.FarField.MaxtraceDistance` | 100000 cm（1km） | 远场追踪距离 |

### 4.3 可视化 / 诊断

| CVar | 用途 |
|------|------|
| `r.Lumen.Visualize.CardPlacement 1` | 看 Card 摆放（覆盖不够的区域会偏粉） |
| `r.DistanceFields.LogAtlasStats 1` | 输出 Mesh Distance Field atlas 统计 |
| `Show > Visualize > Mesh DistanceFields` | 编辑器可视化 mesh DF |
| `Show > Visualize > Global Distance Field` | 编辑器可视化 Global DF |
| `Show > Lumen > Surface Cache` | 看 Surface Cache 覆盖（粉=无覆盖，GI 黑色） |
| `Show > Lumen > Screen Traces` 关掉 | 单独看 Lumen Scene，排查 Screen Trace 干扰 |

---

## 五、官方文档里的具体性能数字 [D]

> 这些数字是 UE 官方文档**直接给出的**，不是推论。直接抄即可。

- **目标**："support large, open worlds running at **60 frames per second (FPS) on next-generation consoles**"
- **Epic scalability level**："produces around **8 milliseconds (ms) on next-generation consoles** for global illumination and reflections at **1080p internal resolution**, relying on Temporal Super Resolution to output at quality approaching native 4K"
  - **来源**：[Lumen Technical Details] > 文档开头第一段
- **Secondary focus**："clean indoor lighting at **30 FPS** on next-generation consoles"
- **Mesh Distance Field**：每条光线前 2m 用 mesh DF（精度高），其余用 Global DF（速度）
- **Software Ray Tracing Detail Tracing vs Global Tracing**：前者高精度、后者最快
- **Hardware Ray Tracing "high setup cost in large scenes"**："tracing to become expensive with many overlapping meshes. Dynamically deforming meshes, like skinned meshes, also incur a large cost to update the Ray Tracing acceleration structures each frame, **proportional to the number of skinned triangles**"
  - **结论**：Hardware 模式不是白送的，skinned mesh 多 = 加速结构更新贵

---

## 六、官方文档列出的"问题 → 调参"清单 [D]

> 直接抄自 [Lumen Technical Details] > Troubleshooting Topics。**这是官方建议，不是推论**。

| 现象 | 调参 |
|------|------|
| 镜面反射里有斑点 (splotchy artifacts) | Post Process 里提高 **Lumen Scene Quality** |
| 小 mesh 在镜面反射里变黑 | Post Process 里提高 **Lumen Scene Detail**（细节纳入更多小物体） |
| 200m 之外天空遮挡 + GI 消失 | Post Process 里提高 **Lumen Scene View Distance** |
| 大型洞穴类场景漏光 (light leaking) | 同时提高 **Lumen Scene View Distance** 和 **Max Trace Distance** |
| GI 变化传播太慢（光源开关延迟） | Post Process 里提高 **Final Gather Lighting Update Speed**（别忘改回默认以省 GPU） |
| 小 emissive mesh 照明不一致 | Detail Panel 里勾选 **Emissive Light Source** |
| 想最高质量反射不在乎性能 | Project / Post Process 里设 **Ray Lighting Mode = Hit Lighting for Reflections** |
| 排查特定 mesh 干扰 GI | Software 模式：取消勾选 mesh 的 **Affect Distance Field Lighting**；Hardware 模式：取消勾选 **Visible in Ray Tracing** |

---

## 七、与 Nanite 的关系 [D]

- "Nanite accelerates the mesh captures used to keep Surface Cache in sync with the triangle scene. **High polygon meshes in particular, need to be using Nanite to have efficient captures.** Foliage and Instanced Static Mesh Components can only be supported if the mesh is using Nanite."
  - **结论**：高面数 mesh 必须开 Nanite，否则 Lumen Surface Cache 同步开销大；草、ISM 必须 Nanite 才能被 Lumen 支持
- Lumen 不强制要求 Nanite，但场景中**大量高面数 mesh 不开 Nanite 时**，Lumen Scene capture 极慢

---

## 八、不能用 Lumen 的硬件怎么办 [D]

- 旧主机 / 旧 PC："Projects that rely on dynamic lighting can use a combination of **Distance Field Ambient Occlusion** and **Screen Space Global Illumination** on those platforms"
- VR："Lumen does not currently support Virtual Reality (VR) systems"

---

## 关联 / 输出产物

- [[性能优化方法论]] — Profile 黄金三问（决定要不要碰 Lumen）
- [[Nanite 性能调优]] — Nanite 是 Lumen 的好搭档（高面数必须 Nanite）
- [[Lyra 性能架构]] — Lyra 是 Lumen + Nanite 实战参考
- [[Unreal Insights 帧分析实战]] — Profile Lumen 时怎么录 trace

---

*Create date: 2026-06-25*
*Last modified: 2026-06-26（删除全部 [U] 百分比数字 / 推论阈值，只留官方文档直接陈述的事实 + 可查 CVar）*
*Status: ✅ 所有内容有 [Lumen Technical Details] / [Lumen Performance Guide] 直接来源*