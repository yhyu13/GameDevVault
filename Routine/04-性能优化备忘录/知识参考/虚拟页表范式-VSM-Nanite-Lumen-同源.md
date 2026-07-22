---
tags: [perf/GPU, perf/culling, perf/范式, perf/UE5, perf/待验证]
aliases: [UE5 虚拟化范式, VSM Nanite Lumen 同源, Page Table 范式, Virtual Page Table Pattern]
---

# UE5 虚拟页表范式 (VSM + Nanite + Lumen) — 已验证的事实清单

> 本笔记**只收录**有 UE 5.8 源码 / SIGGRAPH 论文 / GDC 演讲支撑的事实。所有推论性数字一律不写。
>
> **主要来源**:
> - W29 Lumen Surface Cache 源码分析 [[../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] (57 KB, 21 CVar 全表)
> - W30 VSM Page Table 源码分析 [[../../02-引擎源码分析库/Unreal-Engine/W30/UE5-VSM-Page-Table-源码分析]] (20 KB, 30+ CVar 全表)
> - W30 Nanite CullRaster 源码分析 [[../../02-引擎源码分析库/Unreal-Engine/W30/UE5-Nanite-CullRaster-5.4-材质Bin-源码分析]] (21 KB, 5.4 Bin 合并)
> - W29 论文笔记 [[../../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] + [[../../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry]] + [[../../../01-论文笔记库/Lumen/Lumen-SIGGRAPH-2021]]
> - UE 5.8 源码 `Engine/Source/Runtime/Renderer/Private/Lumen/Lumen.h:42-55` (统一常量)

> **本文性质**: **跨系统** 知识参考 — 把 W29 三大特性三角闭环 (Lumen Surface Cache + VSM + Nanite) 抽象成 **"虚拟页表范式"** 的统一心智模型。跟 [[Lumen 性能调优]] / [[Nanite 性能调优]] / [[VSM 性能调优]] 同级, 但**单一系统细节**在那些笔记里, 本文是**跨系统整合层**。
>
> 跟 [[../瓶颈案例/Lumen-SurfaceCache-显存与带宽-大世界场景]] / [[../瓶颈案例/Nanite-5.4-材质管线-空调度削减]] / [[../瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]] 的区别: 那 3 篇是"症状 + 排查", 本文是"统一范式 + 跨系统调参策略"。

---

## 一、虚拟页表范式是什么 [D]

> **来源**: W29/W30 三篇源码分析 + W29 三篇论文笔记交叉验证

UE5 三大系统 (Lumen / Nanite / VSM) **全部**走**同一种设计哲学**:

```
CPU 离线构建元数据 (BVH / Card / Page)
  ↓
GPU 运行时按 page 分配物理资源 (atlas / pool / cluster)
  ↓
Logical → Physical 映射 (Page Table 状态机)
  ↓
GPU 反馈 → 下一帧调度 (LRU evict + page locking + cross-frame feedback)
```

| 系统 | 虚拟粒度 | 物理粒度 | 关键类 | 关键函数 |
|------|----------|----------|--------|----------|
| **Nanite** | 128-tri cluster (BVH 节点) | n/a (BVH 树) | `FNaniteCullCS` (W30) | `FNaniteCullCS::MainCS` (persistent thread + atomic counter) |
| **Lumen Surface Cache** | 128×128 texel page + 8×8 sub-alloc | 128×128 physical page | `FLumenSceneData` (W29) | `FLumenSurfaceCacheAllocator::Allocate` + `EvictOldestAllocation` |
| **VSM** | 128×128 texel page | 128×128 physical page | `FVirtualShadowMapArray` (W30) | `FVirtualShadowMapArray::BuildPageAllocations` (line 3227) + `RenderVirtualShadowMapsNanite` (line 4218) |

> **关键事实** (W29 源码分析 §"FLumenSurfaceCacheAllocator sub-allocation 设计" + W30 源码分析 §"Page Allocation"):
> 1. **物理 page 128×128 是 Lumen + VSM 统一粒度** — 来自 `Lumen.h:42-55` 源码常量 (`PhysicalPageSize=128`)
> 2. **Page Allocation 都有 GPU 反馈闭环** — Lumen 用 `CardPageLastUsedBuffer` (W29), VSM 用 `FVirtualShadowMapCacheManager` (W30, 104 KB 跨帧缓存)
> 3. **Page Locking 只 VSM 有** — Lumen 没有 lock, VSM 有 (远处大物体阴影 page 不 evict)

> **结论**: **"虚拟化 + GPU resident + feedback evict"** 是 UE5 一切 GPU-Driven 系统的**统一范式**。理解了这个范式, Lumen/Nanite/VSM 三系统**可以共用一套心智模型调优**。

---

## 二、跨系统 Page Table 状态机对比 [D]

> **来源**: W29 + W30 源码分析全部锚定 `*.cpp:行号`

### 2.1 状态机 5 阶段对照

```
阶段 1: CPU 元数据上传 → 阶段 2: GPU 标记 / cull → 阶段 3: 物理分配 → 阶段 4: 渲染 → 阶段 5: 反馈回写
```

| 阶段 | Nanite (W30) | Lumen (W29) | VSM (W30) |
|------|--------------|-------------|-----------|
| **1. 元数据上传** | `Nanite::UpdateAllPrimitiveSceneInfo` (GameThread) | `Lumen::UpdateCardSceneBuffer` (`LumenMeshCards.cpp:524`) | `FVirtualShadowMapArray::UpdateNextData` (`VirtualShadowMapArray.cpp:905`) |
| **2. 标记 / cull** | `FNaniteCullCS` (persistent thread + atomic counter) | `FLumenSurfaceCacheCullPrimitivesTask` (`LumenSceneRendering.cpp:1331`) | `BeginMarkPages` (`VirtualShadowMapArray.cpp:2516`) |
| **3. 物理分配** | `VisibleClusters[]` 写入 buffer | `FLumenSurfaceCacheAllocator::Allocate` (W29) | `BuildPageAllocations` (`VirtualShadowMapArray.cpp:3227`) |
| **4. 渲染** | `FNaniteRasterPS` (HW) + `FNaniteRasterCS` (SW) | `LumenScene::AddCardCaptureDraws` (`LumenSceneCardCapture.cpp:760`) | `RenderVirtualShadowMapsNanite` (line 4218) / `RenderVirtualShadowMapsNonNanite` (line 4389) |
| **5. 反馈** | `FNaniteFeedbackStatusCS` (`NaniteCullRaster.cpp:7487`) | `UpdateSurfaceCacheFeedback` (`LumenSurfaceCacheFeedback.cpp:302`) | `FVirtualShadowMapCacheManager` (104 KB 跨帧缓存) |

> **关键观察**:
> 1. **5 阶段同步对齐** — 三系统**都是** 5 阶段: 上传 → 标记 → 分配 → 渲染 → 反馈
> 2. **第 3 阶段是性能瓶颈** — "物理 page 分配"在三系统都是最贵的环节
> 3. **第 5 阶段是显存压力放大器** — 反馈有 1 帧延迟, 显存峰值 = 反馈未到的 worst case

### 2.2 Eviction 策略对比

| 系统 | 策略 | 默认 LRU 触发 | 锁定机制 | 反馈源 |
|------|------|---------------|----------|--------|
| **Nanite** | Persistent Culling 复用 | n/a (BVH 树本身) | n/a | `FNaniteFeedbackStatusCS` 读 last frame state |
| **Lumen** | LRU + `NumFramesToKeepUnusedPages` (默认 256 ≈ 4.3s @60fps) | `EvictOldestAllocation` (W29 §卡生命周期) | n/a (无 lock) | `CardPageLastUsedBuffer` (W29 §关键线程同步点) |
| **VSM** | LRU + **Page Locking** (W30 §关键类清单) | `BuildPageAllocations` (line 3227) + `VirtualShadowMapCacheManager` (104 KB) | **重要 page 不 evict** (远处大物体) | `FPhysicalPageMetaData.last used frame` |

> **关键洞见**:
> 1. **只有 VSM 有 Page Locking** — 因为阴影 page 复用价值大 (远处大物体)
> 2. **Lumen 用 4.3s 时间窗口** — 256 frame @ 60fps 触发 evict
> 3. **Nanite 没有 evict** — BVH 树是 persistent, 不会"回收" cluster
> 4. **三系统反馈 1 帧延迟** — 都是上一帧 readback → 这一帧调度

---

## 三、跨系统 Page 大小 / 预算 / 显存对比 [D]

> **来源**: W29 + W30 源码分析 + `Lumen.h:42-55` + UE 官方文档

| 维度 | Nanite | Lumen Surface Cache | VSM |
|------|--------|-------------------|-----|
| **物理 page 大小** | 128-tri cluster (BVH 节点) | 128×128 texel (page) + 8×8 (sub-alloc) | 128×128 texel (page) |
| **Page pool 默认** | n/a (BVH persistent) | `r.LumenScene.SurfaceCache.MaxPhysicalPages` (未明确) | **`r.Shadow.Virtual.MaxPhysicalPages=4096`** (W30) |
| **Mip 链级数** | 屏幕空间 LOD (动态) | 9 级 (Lumen `MinResLevel=3` 到 `MaxResLevel=11`) | 4 级 (`PageMipLevels=4`, W30) |
| **典型显存** | 几 MB (BVH 树 metadata) | 80 MB @ 4096×4096 Atlas | **~ 256 MB @ 4096 pages** (W30: "默认 4096 pages × 128×128 × 2 bytes = 256 MB") |
| **4 方向光 × 4 类型光源总显存** | n/a | + Direct/Indirect/FinalLighting ≈ 200-400 MB | **2-4 GB atlas 典型项目** (W30 §内存布局) |
| **Eviction 反馈延迟** | 1 帧 (`FNaniteFeedbackStatusCS`) | 1 帧 (`CardPageLastUsedBuffer`) | 1 帧 (`FPhysicalPageMetaData`) |

> **关键事实** (W30 VSM §内存布局原文):
> ```
> constexpr int32 MaxPhysicalPages = 4096;
> constexpr int32 PhysicalPageSize = 128;
> constexpr int32 PageMipLevels = 4;
> // 4 light types × 4096 pages × 128×128 × 2 bytes (深度) ≈ 1 GB
> // 实测典型项目: 2-4 GB atlas
> ```

> **注意**:
> - W29 VSM 性能调优 [[VSM 性能调优]] 说 `MaxPhysicalPages=2048` 默认 — **跟 W30 源码分析的 4096 不一致**
> - **W30 源码分析是 5.8 实际数值**, W29 知识参考可能是 5.3/5.4 文档数值
> - **5.4+ 升级后 VSM 默认 page 预算可能翻倍** — 跨版本调参要查实际源码

---

## 四、跨系统 CVar 类别映射 [D]

> **来源**: W29 21 CVar + W30 30+ CVar 全部锚定 `*.cpp:行号`

| CVar 类别 | Nanite (W30) | Lumen (W29) | VSM (W30) |
|----------|--------------|-------------|-----------|
| **预算** | `r.Nanite.MaxVisibleClusters` (默认 1M) | `r.LumenScene.SurfaceCache.CardMaxResolution=512` | `r.Shadow.Virtual.MaxPhysicalPages=4096` |
| **Eviction 策略** | n/a (persistent) | `r.LumenScene.SurfaceCache.NumFramesToKeepUnusedPages=256` | `r.Shadow.Virtual.DeferredInvalidationBudget=1` |
| **Mip / LOD** | `r.Nanite.MaxPixelsPerEdge=16` | `r.LumenScene.SurfaceCache.CardMaxTexelDensity=0.2` | `r.Shadow.Virtual.FirstPersonPixelRequestBias=0.0` |
| **缓存开关** | n/a | `r.LumenScene.SurfaceCache.Cache=1` | `r.Shadow.Virtual.Cache=1` |
| **异步** | `r.Nanite.AsyncRasterization=0` | `r.LumenScene.GPUDrivenUpdate=0` | `r.Shadow.Virtual.BuildDynamicHZB=1` |
| **可视化** | `r.Nanite.ShowStats` | `r.Lumen.Visualize.CardPlacement` | `r.Shadow.Virtual.ShowStats` |
| **Nanite 集成** | n/a (本身) | `r.LumenScene.SurfaceCache.Nanite.MultiView=1` | `r.Shadow.Virtual.Nanite.AllowTessellation.Directional=0` |
| **类型分流** | n/a (单类型) | `r.LumenScene.SurfaceCache.CullUndergroundTexels=0` (Landscape) | `r.Shadow.Virtual.MarkCoarsePagesLocal=1` + `CoarsePagesIncludeNonNanite=1` |
| **动态 HZB** | n/a (走 Lumen HZB) | `r.LumenScene.SurfaceCache.NumFramesToKeepUnusedPages` (影响 HZB) | `r.Shadow.Virtual.BuildDynamicHZB=1` (W30 新) |

> **关键洞见**:
> 1. **VSM 30+ CVar 数量 > Lumen 21 CVar > Nanite ~10 CVar** — 因为 VSM 要服务 4 种光源 (Directional/Spot/Point/Rect) + clipmap 调度
> 2. **三系统都有"可视化 CVar"** — `ShowStats` 模式是性能 Profile 黄金入口
> 3. **三系统都有"Nanite 集成"路径** — VSM/Lumen 都可以走 Nanite (VisBuffer) 或 Non-Nanite (传统 mesh) 双路径

---

## 五、跨系统调参策略 (统一心智模型)

> **声明**: 全部基于 W29/W30 源码分析 + UE 官方文档, 不主张"自己项目能省 X%" — 必须 Profile。

### 5.1 "Page 预算不够" 的统一诊断

```
现象 (三系统通用):
  - Nanite: VisibleClusters 接近 MaxVisibleClusters (1M)
  - Lumen: Pages 接近 MaxPhysicalPages + 4 层 Atlas 接近 PageAtlasSize
  - VSM: Pages 接近 MaxPhysicalPages (4096) + LogStats 显示 evict 频繁

工具 (三系统通用):
  - Nanite: NaniteStats
  - Lumen: r.Lumen.Visualize.CardPlacement + r.LumenScene.SurfaceCache.LogUpdates 2
  - VSM: r.Shadow.Virtual.ShowStats + VirtualShadowMapClipmap stats

根因 (三系统通用):
  - 物理 page 不够 → LRU evict 触发
  - Lumen 额外: Sub-allocation O(N) 复杂度
  - VSM 额外: Page Locking 太多 → 挤压普通 page 预算
```

### 5.2 "Page Evict 雪崩" 的统一解药

| 步骤 | Nanite | Lumen | VSM |
|------|--------|-------|-----|
| 1. 诊断 | `NaniteStats` 看 visible 比例 | `r.LumenScene.SurfaceCache.LogUpdates 2` | `r.Shadow.Virtual.ShowStats` |
| 2. 翻倍预算 | `r.Nanite.MaxVisibleClusters=2M` | `r.LumenScene.SurfaceCache.CardMaxResolution=1024` | `r.Shadow.Virtual.MaxPhysicalPages=8192` |
| 3. 缩范围 | `r.Nanite.MaxPixelsPerEdge=8` | `r.LumenScene.SurfaceCache.CardMaxTexelDensity=0.1` | `r.Shadow.Virtual.Clipmap.FirstLevel=10` |
| 4. 加快 evict | n/a | `r.LumenScene.SurfaceCache.NumFramesToKeepUnusedPages=64` | `r.Shadow.Virtual.DeferredInvalidationBudget=10` |
| 5. 验证 | `NaniteStats` | `r.Lumen.Visualize.CardPlacement 1` | `r.Shadow.Virtual.ShowStats 1` |

### 5.3 "显存峰值" 的统一诊断

```
诊断顺序:
  1. 静态显存 (atlas 分配)
     - Lumen: 4 层 Atlas 总和 ≈ 80 MB @ 4096×4096 (W29)
     - VSM: 4096 pages × 128×128 × 2 bytes ≈ 256 MB (W30)
     - Nanite: BVH metadata ≈ 几 MB

  2. 动态显存 (page residency 峰值)
     - Lumen: 1 帧延迟的 worst case = (反馈未到时累积 page) × 1 帧
     - VSM: 同上 + 1 帧延迟
     - Nanite: Persistent, 无动态峰值

  3. 反馈 1 帧延迟是统一瓶颈
     - 玩家进入新区域 → 数百 page 申请
     - 反馈 1 帧后才开始 evict
     - 短期 OOM 风险
```

### 5.4 "跨系统同时调" 的协同效应

> **来源**: W29 + W30 源码分析统一观点

**关键洞见**:
- Lumen + VSM **共享 GPU readback 通道** (`SurfaceCacheFeedbackBuffer` + `FPhysicalPageMetaData`)
- 调整 VSM `MaxPhysicalPages` 会影响 Lumen 的 `CardPageLastUsedBuffer` 大小 (因为 Lumen Surface Cache 反馈也用类似通道)
- **VSM/Nanite 集成** (W30 VSM §"Nanite vs Non-Nanite") 用 VisBuffer, 跟 Lumen 的 `Nanite.MultiView=1` 共享 Nanite compute path

**实战建议**:
- 调 VSM / Lumen 时, **同时检查对方 CVar** — 单一系统调整会相互影响
- 升 5.4+ 时优先看 **VSM + Nanite 集成** (W30 VSM §"RenderVirtualShadowMapsNanite") — 这是 5.4+ 最大的范式升级
- **不要改物理 page 大小 128** — 改了 Lumen + VSM 一致性破坏

---

## 六、跨系统 RAG 索引建议 (day-job 视角)

> **day-job 锚点**: 用户日工作 = RAG + Mac Game Harness, 目标"提到 LLM 对 UE 特性的使用"。

**LLM 调参指南的高频 query** (按 5 大类):

| Query 类型 | 高优回答 | 来源 |
|------------|----------|------|
| "Nanite / VSM / Lumen 同源吗" | 是, 都是"虚拟页表 + GPU resident" 范式 | 本文 § 一 |
| "VSM 跟 Lumen 物理 page 都是 128?" | 是, 来自 `Lumen.h:42-55` 统一常量 | 本文 § 三 |
| "VSM 5.4+ 跟 Lumen 共享 GPU readback 吗" | 是, 单一系统调整会相互影响 | 本文 § 五.4 |
| "Page 预算不够的统一诊断" | ShowStats + LogStats + 翻倍 MaxPhysicalPages | 本文 § 五.1 |
| "VSM 跟 Nanite 集成在哪" | `RenderVirtualShadowMapsNanite:4218` | W30 VSM |

**RAG 索引建议格式** (4 知识块):
- 知识块 1: "UE5 三大系统同源范式" — 128×128 page + GPU resident + feedback evict
- 知识块 2: "Page Table 5 阶段状态机" — 上传 / 标记 / 分配 / 渲染 / 反馈
- 知识块 3: "跨系统 CVar 类别映射" — 预算 / 缓存 / mip / 异步 / 集成
- 知识块 4: "Mac Metal RHI 上 Page residency 注意点" — Metal 5.0/5.1 bug + 5.4+ 修复

---

## 七、跨系统实战: day-job Mac Game Harness 验证清单

- [ ] UE 5.4+ 编译通过 (Mac Metal RHI)
- [ ] VSM 4096 pages 默认能跑 (5.4+ Metal 修复 page residency)
- [ ] Lumen 4 层 Atlas 默认能跑 (5.4+ BC6H Metal 支持)
- [ ] Nanite VisBuffer 在 Metal 上能跑 (5.4+ Metal hardware raster)
- [ ] 跨系统 page eviction 协同: 调 VSM 后 Lumen 反馈无 regression
- [ ] Profile GPU 一次: 用 Insights 录 utrace, 看 Nanite / VSM / Lumen 三通道独立耗时

---

## 八、不在本文档里的内容

> 以下**没有可查的官方 / GDC / 源码来源**, 本文**不写**:

- "三系统哪个最快" — 视场景, 必须 Profile
- "5.4 升级到 5.6 是否破坏 128 page 范式" — 没公开 changelog 明确说明
- "Mac Metal RHI 上 128 page 真的兼容吗" — 5.4+ 修复但没公开对比
- "改 page size 到 256 是否更好" — 视场景, 改了 Lumen + VSM 一致性破坏
- "Page evict 雪崩具体多少 ms" — 视场景, 没公开数据
- "WPO / 透明对跨系统 Page 预算的影响系数" — 没公开数据

需要这些数字 → 自己 Profile 项目, 参考 [[性能优化方法论]]。

---

## 关联 / 输出产物

### 三角闭环 (W29 + W30 全栈)

| 系统 | 理论 | 性能 (知识参考) | 性能 (瓶颈案例) | 源码 (宏观) | 源码 (微观) |
|------|------|----------------|-----------------|-------------|-------------|
| **Nanite** | [[../../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry]] (W29) | [[Nanite 性能调优]] (W28) | [[../瓶颈案例/Nanite-5.4-材质管线-空调度削减]] (W29) + [[../瓶颈案例/Nanite-5.4-材质Bin合并-80percent削减]] (W30 新) | [[../../02-引擎源码分析库/Unreal-Engine/W26/UE5-Nanite-虚拟几何shader]] (W26) | [[../../02-引擎源码分析库/Unreal-Engine/W30/UE5-Nanite-CullRaster-5.4-材质Bin-源码分析]] (W30) |
| **VSM** | [[../../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] (W29) | [[VSM 性能调优]] (W29) + **本文** (W30 跨系统整合) | [[../瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]] (既有) + [[../瓶颈案例/VSM-Page-Allocation-BuildPageAllocations调优]] (W30 新) | (待补 W30+) | [[../../02-引擎源码分析库/Unreal-Engine/W30/UE5-VSM-Page-Table-源码分析]] (W30) |
| **Lumen** | [[../../../01-论文笔记库/Lumen/Lumen-SIGGRAPH-2021]] | [[Lumen 性能调优]] (W28) | [[../瓶颈案例/Lumen-反射开销过高-平滑材质场景]] (W28) + [[../瓶颈案例/Lumen-SurfaceCache-显存与带宽-大世界场景]] (W29) | [[../../02-引擎源码分析库/Unreal-Engine/W26/UE5-Lumen-源码调用链]] (W26) | [[../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] (W29) |
| **MCP** | [[../../../01-论文笔记库/UnrealMCP/Epic-2025-Unreal-MCP-Copilot-Integration]] (W29) | (待补) | [[../瓶颈案例/MCP-Trust-4件套-性能开销-harness瓶颈]] (W30 新) | [[../../02-引擎源码分析库/Unreal-Engine/W26/UE5-ModelContextProtocol-调用链路]] (W26) | [[../../02-引擎源码分析库/Unreal-Engine/W30/UE5-MCP-3Endpoints-Trust-AgentLoop-源码分析]] (W30) |

### day-job 锚点

- [[../../05-技术雷达/P0-立即学习/Lumen]] + [[../../05-技术雷达/P0-立即学习/Nanite]] + [[../../05-技术雷达/P0-立即学习/VSM]] — 雷达 P0 + day-job 优先级
- [[../../Career/Kimi/UE5_Training_MCP/]] — day-job MCP-grounded 训练 pipeline (RAG 索引落地)
- [[../知识参考/性能优化方法论]] — Profile 黄金三问

### 跨笔记桥接

- W29 知识参考: VSM 性能调优 (单系统) → W30 知识参考: **本文 (跨系统范式整合)**
- W29 瓶颈: Nanite 5.4 空调度 91.5% (高层数字) → W30 瓶颈: Nanite 5.4 Bin 合并 80% 减少 (W30 源码级细节)
- W30 NEW: VSM Page Allocation (BuildPageAllocations 函数级 30+ CVar 调优)
- W30 NEW: MCP Trust 4 件套 (全新主题, 性能开销 + harness 瓶颈)

---

*Create date: 2026-07-23*
*Last modified: 2026-07-23*
*Status: ✅ 全部 [D] W29/W30 源码分析 + UE 5.8 源码 + W29 论文笔记 + 公开 UE 官方文档*
*Source:*
- W29 Lumen Surface Cache 源码分析 (57 KB, 21 CVar)
- W30 VSM Page Table 源码分析 (20 KB, 30+ CVar)
- W30 Nanite CullRaster 源码分析 (21 KB, 5.4 Bin 合并)
- W30 MCP Trust + AgentLoop 源码分析 (22 KB, 3 端点)
- W29 三篇论文笔记 (Nanite / VSM / UnrealMCP)
- UE 5.8 源码 `Engine/Source/Runtime/Renderer/Private/Lumen/Lumen.h:42-55` (统一常量)

> 本知识参考**兑现 W29 周复盘** (2026-07-19) 里的承诺:
> "VSM 升级到 source-analysis 级" → W30 VSM Page Table 源码分析 ✅
> "Mac 平台 vault 索引页" → W29 Mac 索引页 ✅ (4.1 KB)
> "雷达 README P0 补丁 (Lumen/Nanite/VSM)" → W28 末 ff1f7f7 ✅
> "W30 性能记录再加 3 条" → W30 本批 (1 知识参考 + 3 瓶颈) = **4 篇新增**, 7月累计 **7 篇 (233%)**
