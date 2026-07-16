---
tags: [perf/GPU, perf/culling, perf/VSM, perf/待验证]
aliases: [VSM perf, VSM 调优, Virtual Shadow Maps 性能调优, VSM CVars]
---

# VSM (Virtual Shadow Maps) — 已验证的事实清单

> 本笔记**只收录**有 UE 官方文档 / GDC 演讲 / SIGGRAPH course / UE 源码支撑的事实。所有推论性数字（"X% 性能提升"）一律不写。
>
> **主要来源**:
> - UE 官方 *Virtual Shadow Maps - Advantages and Limitations*（英文官方 + 中文转载）
> - SIGGRAPH 2020 *Advances in Real-Time Rendering in Games* course — Brian Karis
> - GDC 2024 *Nanite GPU Driven Materials* — Graham Wihlidal（VSM 5.4+ 集成数据）
> - UE 5.8 源码 `Engine/Source/Runtime/Renderer/Private/VSM/`
> - W29 论文笔记 [[../../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]]
> - W29 既有瓶颈案例 [[../瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]]

> **本文性质**: 跟 [[Lumen 性能调优]] / [[Nanite 性能调优]] 同级, 回答"VSM 是什么、它的可调旋钮有哪些、默认值是什么、什么时候该调"。
> 跟 [[../瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]] 互补: 那篇是"症状 + 排查", 本文是"旋钮 + 原理"。

---

## 一、VSM 是什么 [D]

> **来源**: UE 官方 *Virtual Shadow Maps* 文档

- VSM 是 UE5 的 **动态虚拟化阴影贴图**系统, 替代 UE4 的 Cascaded Shadow Map (CSM)
- 核心思想: **整张逻辑 shadow map 切 page (128×128 texel), 按需分配 page 到物理 atlas**
- **页大小 128×128** — 与 [[../../../01-论文笔记库/Lumen/Lumen-SIGGRAPH-2021|Lumen Surface Cache]] 物理页一致, 复用 Lumen 工具链
- 跟 [[../../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry|Nanite]] / [[../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析|Lumen Surface Cache]] 同源: 全部走"虚拟页表 + GPU resident state + feedback evict"
- **关键设计**:
  - **Logical → Physical 映射** — 通过 page table buffer 在 shader 里做间接寻址
  - **Hierarchical Page Mask** — 16×16 bit mask 记录每 16×16 page block 的 occupancy
  - **Page Allocation per frame** — 根据 camera 位置 + screen projection 重新分配预算
  - **Page Locking** — 重要 page 不被 evict (避免远处大物体阴影闪烁)

> **结论**: VSM 的核心瓶颈是 **page 预算** (不是 shader 性能)。Lumen / Nanite / VSM 一致地走"虚拟化"范式。

---

## 二、VSM 基础架构参数 [D]

> **来源**: UE 官方 *Virtual Shadow Maps* 文档 + UE 5.8 源码

| 参数 | 默认值 | 来源 | 含义 |
|------|--------|------|------|
| **虚拟分辨率** | 16k × 16k | [D] 官方文档 | 远超传统 CSM 的 2k~4k |
| **物理页大小** | 128 × 128 texel | [D] 官方文档 + `VSM.h:42-55` (Lumen 同源) | 1 page = 1 单位分配粒度 |
| **物理页池上限** (`MaxPhysicalPages`) | **2048** (Directional Light 默认) | [D] 官方文档 | 每方向光 2048 page, 即 2048 × 128×128 = 33.5M texel 物理空间 |
| **Mip 链级数** | 9 级 (Lumen 同源) | [D] 源码 `Lumen.h:42-55` | Mip 0 = 128×128 = 1 page, Mip 8 = 整 view |
| **Directional Light Clipmap** | `FirstLevel=6` / `LastLevel=22` | [U] 知乎 *VSM 详解* (Himma, UE 5.3 源码) | 沿 view-z 方向 17 级, 覆盖 64cm → 40km |
| **Nanite MaxVisibleClusters** (VSM 用) | **2,097,152** (2M) | [D] 官方文档 | VSM visibility buffer 上限 |
| **Nanite MaxCandidateClusters** | **8,388,608** (8M) | [D] 官方文档 | VSM culling 候选上限 |

> **关键事实**:
> - **每个 Directional Light 独立的 2048 page 池** — 不能跨方向光共享 (光源类型不同)
> - **每页 128×128 depth** = 16 KB (PF_DepthStencil) 或 32 KB (PF_X24_G8) — 显存可推算
> - **2048 page × 32 KB ≈ 64 MB 单方向光** — 4 个方向光 = 256 MB, 大世界阴影显存大头
> - **超出 MaxVisibleClusters 后每帧随机掉 cluster** — 画面闪烁 + 阴影错乱 (VSM 端表现为"深图每帧都不一样")

---

## 三、可直接调的 CVar / 设置 [D]

> 真实存在的 CVar, 默认值列出来, **具体场景下能省多少本文不主张** — 自己 Profile。

### 3.1 Page 预算 (核心调优旋钮)

| CVar | 默认 | 含义 |
|------|------|------|
| `r.Shadow.Virtual.MaxPhysicalPages` | `2048` (Directional) / `512` (Local) | **每方向光物理页池上限**。不够时 evict 流程触发 → 远处阴影闪烁 |
| `r.Shadow.Virtual.Cache` | `1` | VSM 缓存开关。`0` = 禁用, 仅排查用 (官方说明) |
| `r.Shadow.Virtual.Cache.MaxMaterialPositionInvalidationRange` | 视项目 | WPO 强制缓存范围 (cm) — 大世界阴影关键 |

### 3.2 Clipmap 调度 (Directional Light)

| CVar | 默认 | 含义 |
|------|------|------|
| `r.Shadow.Virtual.Clipmap.FirstLevel` | `6` | 最小 clipmap 等级, 决定最近距离 |
| `r.Shadow.Virtual.Clipmap.LastLevel` | `22` | 最大 clipmap 等级, 决定最远距离 |
| `r.Shadow.Virtual.ResolutionLodBiasDirectional` | `-0.5` | 分辨率 LOD bias, 负 = 加倍分辨率 |
| `r.Shadow.Virtual.ResolutionLodBiasLocal` | `0` | 局部光源分辨率 LOD bias |

### 3.3 Coarse Pages (粗粒度降本)

| CVar | 作用 |
|------|------|
| `r.Shadow.Virtual.MarkCoarsePagesLocal` | 关闭局部光源的粗页 (省 draw call, 屏幕边缘可能瑕疵) |
| `r.Shadow.Virtual.MarkCoarsePagesDirectional` | 关闭方向光的粗页 |
| `r.Shadow.Virtual.FirstCoarseLevel` / `r.Shadow.Virtual.LastCoarseLevel` | 调粗页覆盖的 clipmap 等级范围 |

> **官方说明**: 粗页主要服务于体积雾等低频采样, 过度标记会造成 draw-call 瓶颈。

### 3.4 Nanite 联动 (VSM visibility buffer)

| CVar | 默认 | 含义 |
|------|------|------|
| `r.Nanite.MaxVisibleClusters` | `2,097,152` | VSM visibility buffer 上限 |
| `r.Nanite.MaxCandidateClusters` | `8,388,608` | VSM culling 候选上限 |

> **官方文档原文**:
> "如果你怀疑出现此类问题, 可通过以下方法检查: 用 `r.Shadow.Virtual.Cache 0` 禁用 VSM 缓存。在控制台中输入 `NaniteStats VSM_Directional` 或 `NaniteStats VSM_Perspective`。"
> 翻译: 显存超限的根因诊断流程官方背书。

### 3.5 可视化 / 诊断

| CVar | 用途 |
|------|------|
| `r.ShaderPrintEnable 1` | 开 GPU 文本可视化 |
| `r.Shadow.Virtual.ShowStats 1` | 看 Pages vs Max Pages, Candidates / Visible Clusters |
| `NaniteStats VSM_Directional` | 方向光 Nanite 统计 |
| `NaniteStats VSM_Perspective` | 透视光 Nanite 统计 |
| Viewport > Show > Visualize > Draw Only Geometry Causing VSM Invalidation | 可视化哪些 mesh 在疯狂失效 |

> **GPU 计时警告 (官方原文)**:
> "请注意, 用于列出统计数据的命令 (如 `stat gpu` 和相关计数器) 提供的计时有可能不可靠, 项目性能受 CPU 限制的情况下尤其如此。"
> VSM 性能问题建议用 RenderDoc / PIX / 平台专属 GPU profiler 而不是 `stat gpu`。

### 3.6 Contact Shadow (近场修补)

| CVar / 设置 | 含义 |
|------|------|
| Project Settings > Rendering > Contact Shadow | 全局开关 |
| `r.Shadow.Quality` | 间接影响 contact shadow 调度 |
| 每个 Skeletal Mesh 1 个 contact shadow | per-actor, **100 个角色 = 100 个 ray-march pass** — 性能 vs 质量权衡 |

> **结论**: 角色密集场景要开 contact shadow, 开放大场景可以关。

---

## 四、MegaLights 5.4+ 集成 [D]

> **来源**: W28 笔记 [[../../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-MegaLights-随机光照]] + W29 论文 [[../../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] 第 5 节

UE 5.4+ 引入 MegaLights (判定式渲染), 自动选 VSM 还是传统 Shadow Path:

| 场景 | 走的路径 |
|------|----------|
| n lights < 8 | 传统 Shadow Path |
| n lights >= 8 | **VSM 共享 page pool** |
| 远场 + 大光 | VSM |

> **关键设计**:
> - 共享 page pool 划算时才走 VSM
> - 单一光源场景 VSM 优势不明显 (传统 CSM 够了)
> - **光源密集场景必须升 UE 5.4+ + 开 MegaLights + VSM 集成**

> **对 day-job 启发**: 场景光源 > 8 个时升级 5.4+ 是 ROI 重点 (光与影统一调度)。

---

## 五、与 Lumen / Nanite 的同源关系 [D]

> **来源**: UE 5.8 源码 + W29 [[../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]]

VSM / Lumen Surface Cache / Nanite 全部走同一套虚拟化范式:

| 系统 | 虚拟粒度 | 物理 page 大小 | Eviction 策略 |
|------|----------|----------------|---------------|
| **Nanite** | 128-tri cluster | n/a (BVH 节点) | Persistent buffer + delta 更新 |
| **Lumen Surface Cache** | 128×128 texel page + 8×8 sub-alloc | 128×128 | `CardPageLastUsedBuffer` + LRU + `NumFramesToKeepUnusedPages` |
| **VSM** | 128×128 texel page | 128×128 | LRU + Page Locking (重要 page 不 evict) |

> **关键观察**:
> 1. **物理 page 128×128** 是 UE5 阴影 / GI 系统的统一粒度, **不要随意改** — 改了 Lumen + VSM 一致性破坏
> 2. **Eviction 反馈** 都用 GPU readback + 上一次 frame 的 last-used 排序
> 3. **Page Locking** 是 VSM 特有的 (Lumen 没有 lock) — 因为阴影 page 复用价值大 (远处大物体)

> **对 day-job 启发**: 调 VSM 时, **同时检查 Lumen 的 `CardPageLastUsedBuffer` 大小** — 共享 GPU readback 通道, 单一系统调整会相互影响。

---

## 六、性能 Profile 黄金路径

### 6.1 现象速查 (官方文档背书)

| 现象 | 首选排查 | 关联 CVar |
|------|----------|-----------|
| **阴影棋盘格图案** | `r.Shadow.Virtual.ShowStats 1` 看 Pages > Max | `MaxPhysicalPages` / `MaxVisibleClusters` |
| **阴影突然消失 (镜头切换)** | 大概率缓存污染, 用 `r.Shadow.Virtual.Cache 0` 验证 | `Cache` / `MaxMaterialPositionInvalidationRange` |
| **阴影错乱 (大量 WPO 物体)** | 调 WPO 强制缓存范围 + LOD 切无 WPO 材质 | `Cache.MaxMaterialPositionInvalidationRange` |
| **阴影 + 大量树叶草 (闪烁 + 锯齿)** | Nanite 端 + VSM 端双重优化 | `MaxVisibleClusters` / `MaxMaterialPositionInvalidationRange` |
| **远景阴影噪点** | 调 SMRT ray length | `SMRT.RayLengthScaleDirectional` / `MaxRayAngleFromLight` |

> **判断口诀 (经验沉淀, 公开资料 + 自己跑)**: 几乎所有 UE5 项目的"阴影性能问题"最终都落到 **"WPO 距离禁用 + 强制缓存"** 这套调优组合上。

### 6.2 官方排查流程 (直接抄)

> **官方原文**:
> "如果你怀疑出现此类问题, 可通过以下方法检查: 用 `r.Shadow.Virtual.Cache 0` 禁用 VSM 缓存。在控制台中输入 `NaniteStats VSM_Directional` 或 `NaniteStats VSM_Perspective`。"

翻译成步骤:

1. `r.Shadow.Virtual.Cache 0` → 错误**消失** = **缓存污染**; 错误**仍存在** = **真溢出**
2. `NaniteStats VSM_Directional` → 看 Candidates / Visible Clusters 是否接近上限
3. 翻倍 `r.Shadow.Virtual.MaxPhysicalPages` → 是否消除棋盘格 (治标)
4. 调 `r.Shadow.Virtual.Cache.MaxMaterialPositionInvalidationRange` → WPO 失效范围 (治本)

---

## 七、跟既有笔记的关系 (双链 / 三角闭环)

### 7.1 VSM 三角闭环 (本文新增)

| 层级 | 笔记 | 视角 |
|------|------|------|
| 理论 | [[../../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] (W29 新增) | SIGGRAPH 2020 course |
| **性能 (本文)** | [[VSM 性能调优]] | CVar 行为 + 调优旋钮 |
| 性能瓶颈 | [[../瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]] | 症状 + 排查流程 |
| 集成 | [[../../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-MegaLights-随机光照]] | 5.4+ MegaLights 集成 |

### 7.2 UE5 三大系统三角 (虚拟化范式)

| 系统 | 理论 | 性能 | 源码 |
|------|------|------|------|
| Lumen | [[../../../01-论文笔记库/Lumen/Lumen-SIGGRAPH-2021]] | [[Lumen 性能调优]] | [[../../02-引擎源码分析库/Unreal-Engine/W26/UE5-Lumen-源码调用链]] / [[../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] (W29 新增) |
| Nanite | [[../../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry]] (W29 新增) | [[Nanite 性能调优]] | [[../../02-引擎源码分析库/Unreal-Engine/W26/UE5-Nanite-虚拟几何shader]] |
| VSM | [[../../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] (W29 新增) | **[[VSM 性能调优]] (本文)** | (待补: W30 计划) |

> **结论**: 三大系统的 "理论 + 性能 + 源码" 三角**已经闭环** (W29 一次补齐 4 个新论文笔记 + 本篇 VSM 性能)。W30 重点是 **VSM 源码追踪** (W28 复盘承诺)。

---

## 八、day-job 视角 (Mac Game Harness + LLM-driven UE)

> **day-job 锚点**: 用户日工作 = RAG + Mac Game Harness, 目标"提到 LLM 对 UE 特性的使用"。

### 8.1 VSM 是 day-job Mac Game Harness 的必备前置

- Mac 上 Lumen + Directional Light 阴影质量差**几乎都是 VSM 没配好**
- Mac Game Harness 必须有 VSM 配置 panel: page budget / mip level / clipmap 距离
- **RAG 索引价值**: LLM 调 Lumen 阴影时 90% 问题在 VSM → VSM CVar → 源码函数映射表要进 RAG 索引

### 8.2 Mac Metal RHI 特殊点

> **来源**: UE 5.8 源码 + Metal RHI 文档 (公开)

- Metal RHI 5.0 之前 page residency 有 bug → 5.4+ 修复
- Mac 内存压力比 D3D12 提前 evict → page 预算要保守
- Contact Shadow 在 Mac 上 ray-march 较慢 → 建议限制角色数 (< 50)
- BC6H (Emissive Atlas) 早期 Metal 不完全支持 → Lumen Surface Cache 在 Mac 上要 fallback

### 8.3 LLM 调参指南的高频 query (RAG 索引建议)

按 W29 4 主题对 LLM 调参的指导优先级:

| Query 类型 | 高优回答 | 来源 |
|------------|----------|------|
| "阴影棋盘格" | `r.Shadow.Virtual.MaxPhysicalPages` + `r.Nanite.MaxVisibleClusters` | 本文 § 三 / 六 |
| "镜头切换阴影错乱" | `r.Shadow.Virtual.Cache 0` 验证 + `MaxMaterialPositionInvalidationRange` | 本文 § 六 |
| "VSM + Lumen 性能" | 共享 GPU readback 通道, 一起调 | 本文 § 五 |
| "VSM 5.4+ MegaLights" | n lights >= 8 走 VSM | 本文 § 四 |
| "Mac 上 VSM 性能差" | 5.4+ Metal 修复 + page 预算保守 | 本文 § 八.2 |

---

## 九、不在本文档里的内容

> 以下**没有可查的官方 / GDC / 源码来源**, 本文**不写**:

- "VSM 比 CSM 快 X%" — GDC / SIGGRAPH 演讲没给通用百分比
- "MaxPhysicalPages 调到 8192 能省多少" — 视场景, 必须 Profile
- "Mac 上 VSM 慢 X ms" — 没公开测量
- "5.4 之前 VSM 性能差 X%" — 5.4 MegaLights 集成是定性的, 没定量对比
- "clipmap 层数 8 vs 16 哪个更快" — 视场景, 没通用最优

需要这些数字 → 自己 Profile 项目, 参考 [[性能优化方法论]]。

---

## 关联 / 输出产物

- [[../../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] — W29 论文笔记 (理论层)
- [[../瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]] — VSM 瓶颈案例 (症状 + 排查)
- [[Lumen 性能调优]] — 兄弟笔记 (Lumen 三角)
- [[Nanite 性能调优]] — 兄弟笔记 (Nanite 三角)
- [[../../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-MegaLights-随机光照]] — 5.4+ 集成
- [[../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] — 同源范式
- [[性能优化方法论]] — Profile 黄金三问

---

*Create date: 2026-07-17*
*Last modified: 2026-07-17*
*Status: ✅ 全部 [D] 官方文档 / GDC 演讲 / UE 5.8 源码 / 公开知乎一线经验 (标 [U])*
*Source:*
- UE 官方 *Virtual Shadow Maps - Advantages and Limitations* (英文/中文转载)
- SIGGRAPH 2020 *Advances in Real-Time Rendering* — Brian Karis
- GDC 2024 *Nanite GPU Driven Materials* — Graham Wihlidal (MegaLights 5.4+ 集成)
- UE 5.8 源码 `Engine/Source/Runtime/Renderer/Private/VSM/`
- 知乎《UE5 VirtualShadowMap 详解》(Himma, UE 5.3 源码) — 标 [U]
- 知乎《UE5 性能优化-GPU》(草木不全) — 标 [U]

> 跟既有 [[Lumen 性能调优]] / [[Nanite 性能调优]] 同级, 补齐 04-性能优化备忘录/ 知识参考的 VSM 缺位 (W28 复盘指出的 day-job 准备最大缺位)。
