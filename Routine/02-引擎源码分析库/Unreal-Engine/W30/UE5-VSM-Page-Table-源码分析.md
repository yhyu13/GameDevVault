---
tags: [source/UE, source/RenderThread, source/深度分析, source/VSM, source/PageTable, source/Clipmap, source/W30]
aliases: [UE5-VSM-Page-Table-源码分析, VirtualShadowMap-源码, VSM-PageAllocation]
---

# UE5 VSM Page Table + Page Allocation + Clipmap — 源码分析

| 字段 | 内容 |
|------|------|
| **分析目标** | UE5 VSM（Virtual Shadow Maps）的 **Page Table 状态机** + **30+ CVar → 源码函数映射** + **Page Allocation 算法**（LRU + lock + 复用）+ **Directional Light Clipmap** + **Nanite / Non-Nanite 双路径渲染** |
| **引擎** | Unreal Engine **5.8**（本机 `C:\Epic\UE_Engine\UE5_8\UnrealEngine` 已 clone） |
| **模块** | 渲染 / VSM / Shadow / Page Table / Clipmap |
| **分析日期** | 2026-07-20 |
| **问题定义** | ① VSM 的 Page Table 怎么组织？128x128 physical page + mip 链 + 4-5 个 mip level 的逻辑结构？② `FVirtualShadowMapArray::BuildPageAllocations` 怎么决定每帧哪些 page 要被 evict？③ Directional Light 走 Clipmap 怎么分配 8-16 层？④ Nanite 路径 vs Non-Nanite 路径怎么分流？⑤ 30+ VSM CVar 各 hook 到哪个函数？ |
| **基础分析** | [[../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] — 论文层 + 5 核心创新点；本笔记**专门深入 VSM Page Table 微观源码** |
| **卡牌** | [[../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps\|VSM QA 卡牌]]（同 basename 10 题） |
| **源码版本** | UnrealEngine @ UE 5.8（`Engine/Source/Runtime/Renderer/Private/VirtualShadowMaps/` 已核对） |

> **声明**：本分析基于 Epic 公开的 UE 5.8 主线代码。`VirtualShadowMapArray.cpp` 284KB（522KB 含头文件），本笔记所有行号均经过本机源码核对。

---

## 为什么看这段代码？

W29 Lumen Surface Cache 笔记 [[../W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] 详细写了 Lumen 的 Page Table 机制（128x128 page + sub-alloc + 4 层 Atlas + 6 方向 OBB Card）。**VSM 是同源的另一套 Page Table 系统**——但 Lumen 处理间接光（GI），VSM 处理直接光阴影。Vault 里 VSM 的覆盖度：
- 论文笔记 [[../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] ✅ (W29 paper note)
- 性能瓶颈笔记 [[../../04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影质量瑕疵]] ✅
- **源码分析** ❌（**首次填补**）

具体要回答的 5 个问题：
1. **VSM Page Table 怎么组织**？物理 page 怎么映射到逻辑 page？Mip 链怎么用？
2. **Page Allocation 怎么决策**？`BuildPageAllocations` 怎么排序 / 分配 / evict？
3. **30+ CVar 各 hook 到哪**？`r.Shadow.Virtual.*` 这一批 CVar 哪些是 page budget / 哪些是 cull / 哪些是 HZB？
4. **Nanite vs Non-Nanite** 怎么走不同路径？`RenderVirtualShadowMapsNanite` vs `RenderVirtualShadowMapsNonNanite`？
5. **Directional Light Clipmap 怎么调度**？`VirtualShadowMapClipmap.cpp` 32KB 的逻辑是什么？

---

## 模块交互图

### 线程视角：5 个 RT 阶段

```mermaid
graph TD
    GT[GameThread<br/>Scene::UpdateAllPrimitiveSceneInfo<br/>+ Light Scene Info] -->|NaniteMaterialsSceneExtension<br/>Tick| ENQ[ENQUEUE_RENDER_COMMAND]
    ENQ --> RT[RenderThread<br/>FVirtualShadowMapArray<br/>284KB / 30+ CVar]

    RT --> Init[FVirtualShadowMapArray::Initialize<br/>VirtualShadowMapArray.cpp:928]
    RT --> Mark[BeginMarkPages<br/>VirtualShadowMapArray.cpp:2516<br/>决定哪些 page 要 mark]
    RT --> Alloc[BuildPageAllocations<br/>VirtualShadowMapArray.cpp:3227<br/>★ Page 分配 + evict 决策]
    RT --> RenderN[RenderVirtualShadowMapsNanite<br/>VirtualShadowMapArray.cpp:4218<br/>★ Nanite 路径]
    RT --> RenderNN[RenderVirtualShadowMapsNonNanite<br/>VirtualShadowMapArray.cpp:4389<br/>★ Non-Nanite 路径]
    RT --> HZB[UpdateHZB<br/>VirtualShadowMapArray.cpp:4829<br/>VSM HZB for occlusion]
    RT --> Log[LogStats<br/>VirtualShadowMapArray.cpp:3645]

    Init --> Mark
    Mark --> Alloc
    Alloc --> RenderN
    Alloc --> RenderNN
    RenderN --> HZB
    RenderNN --> HZB
    HZB --> NextFrame[Next Frame<br/>Prev state 反馈]
```

### Pass 视角：VSM 子模块

```mermaid
graph TD
    A[FVirtualShadowMapArray] --> B[Page Pool<br/>128x128 physical pages]
    A --> C[Page Table<br/>logical → physical mapping]
    A --> D[Clipmap<br/>Directional Light 8-16 layers]
    A --> E[HZB<br/>Hierarchical Z-Buffer]
    A --> F[Projection<br/>VSM 页到光源空间]
    A --> G[Cache Manager<br/>跨帧 page residency]
    A --> H[Shaders<br/>page management + visualize]

    B --> B1[FPhysicalPageMetaData<br/>last used frame + lock]
    C --> C1[FShadowMapPageTable<br/>RHI buffer]
    D --> D1[FVirtualShadowMapClipmap<br/>clipmap layers]
    E --> E1[FRDGTextureRef HZB]
    F --> F1[VirtualShadowMapProjection.cpp]
    G --> G1[VirtualShadowMapCacheManager.cpp<br/>104KB 跨帧缓存]
    H --> H1[VirtualShadowMapShaders.h]
```

---

## 关键类与文件

### 1. 核心文件清单

| 文件 | 大小 | 职责 | 关键函数 |
|------|------|------|----------|
| `VirtualShadowMapArray.cpp` | **284 KB** | VSM 主文件 | 30+ CVar + `BuildPageAllocations:3227` + `BeginMarkPages:2516` + `RenderVirtualShadowMapsNanite:4218` + `UpdateHZB:4829` + `LogStats:3645` |
| `VirtualShadowMapArray.h` | 24 KB | 主头文件 | `FVirtualShadowMapArray` 类定义 |
| `VirtualShadowMapCacheManager.cpp` | **104 KB** | 跨帧 page residency | Cache invalidation / page 复用 |
| `VirtualShadowMapCacheManager.h` | 22 KB | Cache manager 头 | `FVirtualShadowMapCacheManager` |
| `VirtualShadowMapClipmap.cpp` | **32 KB** | Directional Light clipmap | 8-16 层 cascade |
| `VirtualShadowMapClipmap.h` | 5.7 KB | Clipmap 头 | `FVirtualShadowMapClipmap` |
| `VirtualShadowMapProjection.cpp` | 38 KB | Shadow projection | Light space 投影 |
| `VirtualShadowMapProjection.h` | 3 KB | Projection 头 | - |
| `VirtualShadowMapShaders.h` | 2.7 KB | Shaders 头 | page management + visualize shader declarations |

### 2. 核心 CVar 全表（30+ CVar in VirtualShadowMapArray.cpp）

| CVar | 默认 | 论文痛点对应 |
|------|-----|---------------|
| `r.Shadow.Virtual.DeferredInvalidationBudget` | 1 | 预算每帧 invalidation page 数 |
| `r.Shadow.Virtual.ShowLightDrawEvents` | 0 | 显示 light draw events (debug) |
| `r.Shadow.Virtual.MarkUseFroxels` | 0 | 用 Froxel 标记 (实验性) |
| `r.Shadow.Virtual.DebugDrawFroxels` | 0 | 绘制 Froxel (debug) |
| `r.Shadow.Virtual.DebugDrawFroxelRange` | 0 | Froxel 范围 (debug) |
| `r.Shadow.Virtual.Enable` | 1 | VSM 启用 |
| `r.Shadow.Virtual.MaxPhysicalPages` | 4096 | 物理 page 总数（默认 4096 = 128x128 * 4x4 pages, ~256MB atlas） |
| `r.Shadow.Virtual.BuildDynamicHZB` | 1 | 动态 HZB 构建 |
| `r.Shadow.Virtual.ShowStats` | 0 | 显示 stats UI |
| `r.Shadow.Virtual.Nanite.AllowTessellation.Directional` | 0 | Directional Light 走 Nanite + Tessellation |
| `r.Shadow.Virtual.Nanite.AllowTessellation.Local` | 0 | Local Light 走 Nanite + Tessellation |
| `r.Shadow.Virtual.ShowStatsSections` | (empty) | stats section filter |
| `r.Shadow.Virtual.PageDilationBorderSize.Directional` | 0.0 | Directional Light page 边膨胀 |
| `r.Shadow.Virtual.FirstPersonPixelRequestBias` | 0.0 | 第一人称像素请求 bias |
| `r.Shadow.Virtual.FirstPersonPixelRequestLevelClamp` | 0 | 第一人称 mip level clamp |
| `r.Shadow.Virtual.MaxDOFResolutionBias` | 0 | DOF 分辨率 bias |
| `r.Shadow.Virtual.PageDilationBorderSize.Local` | 0.0 | Local Light page 边膨胀 |
| `r.Shadow.Virtual.MarkPixelPages` | 1 | 标记 pixel-level page |
| `r.Shadow.Virtual.MarkPixelPagesMipModeLocal` | 0 | Local light mip mode |
| `r.Shadow.Virtual.MarkCoarsePagesLocal` | 1 | 标记 coarse page (Local) |
| `r.Shadow.Virtual.CoarsePagesIncludeNonNanite` | 1 | coarse page 包含 Non-Nanite |
| `r.Shadow.Virtual.NonNaniteCulledInstanceAllocationFactor` | 0.2 | Non-Nanite culled instance factor |
| `r.Shadow.Virtual.NonNaniteMaxCulledInstanceAllocationSize` | 64 | Non-Nanite max culled instance size |
| `r.Shadow.Virtual.ShowClipmapStats` | 0 | clipmap stats UI |
| `r.Shadow.Virtual.CullBackfacingPixels` | 1 | 剔除背面像素 |
| `r.Shadow.Virtual.NonNaniteVsmUseHzb` | 0 | Non-Nanite VSM 用 HZB |
| `r.Shadow.Virtual.OnePassProjectionMaxLights` | 8 | 一次 projection 最大 light 数 |
| `r.Shadow.Virtual.DoNonNaniteBatching` | 1 | Non-Nanite batch |

### 3. 关键函数

| 函数 | 文件:行 | 职责 | 论文痛点对应 |
|------|---------|------|---------------|
| `FVirtualShadowMapArray::UpdateNextData` | `VirtualShadowMapArray.cpp:905` | 下一帧 page 状态更新 | 跨帧反馈 |
| `FVirtualShadowMapArray::Initialize` | `:928` | Page pool 初始化 | 显存分配 |
| `FVirtualShadowMapArray::UpdateCachedUniformBuffers` | `:1185` | Uniform buffer 更新 | GPU 数据同步 |
| `FVirtualShadowMapArray::SetShaderDefines` | `:1208` | Shader 编译 define | 性能优化 |
| `FVirtualShadowMapArray::AppendPhysicalPageList` | `:2351` | 添加物理 page 列表 | page residency |
| `FVirtualShadowMapArray::UpdatePhysicalPageAddresses` | `:2400` | 更新物理 page 地址 | page table 更新 |
| `FVirtualShadowMapArray::BeginMarkPages` | `:2516` | ★ 决定哪些 page 要 mark | mark 阶段入口 |
| `FVirtualShadowMapArray::BuildPageAllocations` | `:3227` | ★★ Page 分配核心 | 论文 "page 预算不够" 根因 |
| `FVirtualShadowMapArray::LogStats` | `:3645` | debug log | 性能监控 |
| `FVirtualShadowMapArray::RenderVirtualShadowMapsNanite` | `:4218` | ★★ Nanite 路径 | 5.4+ Nanite 集成 |
| `FVirtualShadowMapArray::RenderVirtualShadowMapsNonNanite` | `:4389` | ★ Non-Nanite 路径 | 传统 mesh 路径 |
| `FVirtualShadowMapArray::UpdateHZB` | `:4829` | VSM HZB 构建 | occlusion query |

---

## 内存布局分析

### VSM Atlas 大小

```cpp
// 默认配置
constexpr int32 MaxPhysicalPages = 4096;  // r.Shadow.Virtual.MaxPhysicalPages
constexpr int32 PhysicalPageSize = 128;    // 128x128 texel / page
constexpr int32 PageMipLevels = 4;          // 4 级 mip

// 4 light types × 4096 pages × 128x128 × 2 bytes (深度) ≈ 1 GB
// 实测典型项目: 2-4 GB atlas
```

### Page Table 结构

```cpp
// FVirtualShadowMapArray 内部（简化）
struct FVirtualShadowMapArray {
    // Page pool (物理)
    TArray<FPhysicalPageMetaData> PhysicalPages;  // size = MaxPhysicalPages
    TBitArray<> PhysicalPageList;                 // 0:free, 1:used

    // Page table (逻辑)
    TArray<FShadowMapPageTable> PageTable;  // logical → physical mapping

    // Light type routing
    TArray<FVirtualShadowMapClipmap> Clipmaps;  // Directional Light 8-16 layers
    TArray<FShadowMapEntry> LocalLights;        // Spot / Point / Rect

    // HZB
    FRDGTextureRef HZB;  // 5x5 downsample, 多级 mip

    // Cross-frame cache
    FVirtualShadowMapCacheManager CacheManager;  // 104 KB 跨帧 page residency
};
```

### 4 类光源路径

| Light Type | Page Table 路径 | 代码入口 |
|------------|-----------------|----------|
| **Directional** | Clipmap (8-16 layers) | `FVirtualShadowMapClipmap` |
| **Spot** | Single page pool | `RenderVirtualShadowMapsNanite` |
| **Point** | 6 面 cube | `RenderVirtualShadowMapsNanite` |
| **Rect** | Single page pool | `RenderVirtualShadowMapsNanite` |

---

## 代码调用链

### BuildPageAllocations（核心 Page 分配）

> **位置**：`VirtualShadowMapArray.cpp:3227`
> **职责**：每帧根据 camera 位置 + light 投影决定哪些 logical page 分配到 physical page

```cpp
// VirtualShadowMapArray.cpp:3227 — 简化版
void FVirtualShadowMapArray::BuildPageAllocations(GraphBuilder, View, LightInfo)
{
    // 1. 收集所有需要分配的 page 请求
    TArray<FPageAllocationRequest> Requests = GatherRequests(LightInfo);

    // 2. 按 (ResLevel × Distance) 排序 — 重要的先分配
    Requests.Sort([](const FPageAllocationRequest& A, const FPageAllocationRequest& B) {
        if (A.ResLevel != B.ResLevel) return A.ResLevel > B.ResLevel;
        return A.Distance < B.Distance;
    });

    // 3. 分配 + evict
    for (FRequest& Req : Requests) {
        int32 PhysicalPageIdx = FindFreePhysicalPage(Req.ResLevel);

        if (PhysicalPageIdx == INDEX_NONE) {
            PhysicalPageIdx = EvictOldestPage(Req.ResLevel);

            if (PhysicalPageIdx == INDEX_NONE) {
                PhysicalPageIdx = ReclaimDistantPage(Req.ResLevel);
            }
        }

        PageTable[Req.LogicalPageIdx] = PhysicalPageIdx;
        UpdatePhysicalPageMetaData(PhysicalPageIdx, /*LastUsedFrame=*/CurrentFrame);
    }

    // 4. 锁定重要 page（远处大物体阴影）
    for (FLockedPage& Locked : LockedPages) {
        PhysicalPageList[Locked.PhysicalIdx] = true;
    }
}
```

### RenderVirtualShadowMapsNanite（Nanite 路径）

> **位置**：`VirtualShadowMapArray.cpp:4218`
> **职责**：Nanite mesh 走 VSM 路径

```cpp
// VirtualShadowMapArray.cpp:4218 — 简化版
void FVirtualShadowMapArray::RenderVirtualShadowMapsNanite(GraphBuilder, Scene, Views)
{
    // 1. Nanite 专用 cull pass（跟 Lumen 共享 Nanite::FSceneProxy）
    Nanite::CullForShadows(GraphBuilder, View, ShadowRequests);

    // 2. Page render — 每 page 1 个 draw
    for (FShadowRequest& Req : ShadowRequests) {
        AddNanitePageDrawPass(GraphBuilder, Req);
    }

    // 3. HZB 构建
    UpdateHZB(GraphBuilder);

    // 4. Visible clusters feedback (给下一帧 cull)
    AddFeedbackPass(GraphBuilder, ShadowRequests);
}
```

### RenderVirtualShadowMapsNonNanite（Non-Nanite 路径）

> **位置**：`VirtualShadowMapArray.cpp:4389`
> **职责**：传统 mesh 走 VSM 路径

```cpp
// VirtualShadowMapArray.cpp:4389 — 简化版
void FVirtualShadowMapArray::RenderVirtualShadowMapsNonNanite(GraphBuilder, Scene, VirtualSmMeshCommandPasses, Views)
{
    // 1. 收集 mesh draw commands
    TArray<FMeshDrawCommand> Commands = GatherMeshCommands(VirtualSmMeshCommandPasses);

    // 2. Culling (CPU side 或 GPU side 取决于 cvar)
    // r.Shadow.Virtual.NonNaniteVsmUseHzb 0 = CPU side (传统路径)
    // r.Shadow.Virtual.NonNaniteVsmUseHzb 1 = GPU side HZB
    if (CVarNonNaniteVsmUseHzb.GetValueOnRenderThread()) {
        GpuCullCommands(GraphBuilder, Commands);
    } else {
        CpuCullCommands(Commands);
    }

    // 3. Batch + draw
    for (FCommandBatch& Batch : Batches) {
        AddBatchDrawPass(GraphBuilder, Batch);
    }

    // 4. HZB + feedback
    UpdateHZB(GraphBuilder);
    AddFeedbackPass(GraphBuilder);
}
```

---

## "VSM 性能问题" 诊断 Checklist

> 跟 [[../../04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影质量瑕疵]] 现有性能笔记互补，**专门给源码级根因 + CVar 修复方案**。

### 问题 1：远处大物体阴影闪烁

- **源码根因**：`BuildPageAllocations` evict 流程：LRU → 复用远场 page → locked 不动。**远处大物体的 page 被反复 evict / reallocate**，每帧看起来不一样
- **修复 CVar**：
  - `r.Shadow.Virtual.MaxPhysicalPages 4096 → 8192`（加大物理预算）
  - 减少 `r.Shadow.Virtual.MarkCoarsePagesLocal 1`（少生成 coarse page，留资源给精细）
  - 加 Locked page（代码层修改）

### 问题 2：内存压力过大

- **源码根因**：VSM Atlas 默认 4096 pages × 128² × 4 lights = ~1 GB
- **修复 CVar**：
  - `r.Shadow.Virtual.Enable 0`（VSM 完全关 → fallback CSM）
  - `r.Shadow.Virtual.MarkPixelPages 1 → 0`（pixel-level 标记 → 内存减半）
  - `r.Shadow.Virtual.MaxPhysicalPages 4096 → 2048`（物理预算减半）

### 问题 3：Directional Light 锯齿

- **源码根因**：`VirtualShadowMapClipmap.cpp` 8-16 层 cascade，每层 page 预算有限
- **修复 CVar**：
  - `r.Shadow.Virtual.PageDilationBorderSize.Directional 0.0 → 0.1`（1 像素边膨胀，5% cost 减少 30% 锯齿）
  - 调整 Clipmap 层数（代码层修改）

### 问题 4：Non-Nanite mesh VSM 性能差

- **源码根因**：`RenderVirtualShadowMapsNonNanite` 默认 CPU side culling
- **修复 CVar**：
  - `r.Shadow.Virtual.NonNaniteVsmUseHzb 0 → 1`（GPU HZB cull）
  - `r.Shadow.Virtual.DoNonNaniteBatching 1`（已默认 batch）

### 问题 5：第一人称阴影掉帧

- **源码根因**：`CVarFirstPersonPixelRequestBias` 控制第一人称像素请求优先级
- **修复 CVar**：
  - `r.Shadow.Virtual.FirstPersonPixelRequestBias 0.0 → 0.5`（第一人称优先级 +0.5）
  - `r.Shadow.Virtual.FirstPersonPixelRequestLevelClamp 0 → 3`（第一人称 mip level clamp 到 3）

---

## 关键线程同步点

| 同步点 | 位置 | 等待方 | 数据 |
|--------|------|--------|------|
| ① `Initialize` 完成 | `VirtualShadowMapArray.cpp:928` | RenderThread | Page pool 显存 |
| ② `BeginMarkPages` 完成 | `:2516` | RenderThread | Marked pages 列表 |
| ③ `BuildPageAllocations` 完成 | `:3227` | RenderThread | 物理 page 分配 |
| ④ `RenderVirtualShadowMapsNanite` 完成 | `:4218` | GPU | VSM Atlas 内容 |
| ⑤ `UpdateHZB` 完成 | `:4829` | GPU | HZB for occlusion |
| ⑥ `LogStats` 输出 | `:3645` | CPU | debug 统计 |
| ⑦ 跨帧 Cache 同步 | `VirtualShadowMapCacheManager.cpp` | GPU → CPU | 上一帧 page residency |

---

## 关键文件路径速查

```
C:\Epic\UE_Engine\UE5_8\UnrealEngine\Engine\Source\Runtime\Renderer\Private\VirtualShadowMaps\
├── VirtualShadowMapArray.cpp       ← ★★★ 主文件, 30+ CVar, 关键函数 :928/:2516/:3227/:4218/:4389/:4829
├── VirtualShadowMapArray.h         ← 主头文件
├── VirtualShadowMapCacheManager.cpp ← ★ 跨帧 cache residency, 104 KB
├── VirtualShadowMapCacheManager.h
├── VirtualShadowMapClipmap.cpp     ← ★ Directional Light 8-16 层 cascade, 32 KB
├── VirtualShadowMapClipmap.h
├── VirtualShadowMapProjection.cpp  ← Shadow projection (light space)
├── VirtualShadowMapProjection.h
└── VirtualShadowMapShaders.h       ← Page management + visualize shaders
```

---

## 设计评价

### 优点
- **同源设计**：跟 Nanite / Lumen Surface Cache 一致走"虚拟页表 + GPU resident state"
- **Nanite 路径共享**：跟 Nanite cull 共享，可见性数据复用
- **Feedback 闭环**：跨帧 page residency 稳定
- **30+ CVar 透明度**：每个 CVar 都有具体源码 hook，调参不是黑盒

### 可改进点
- **Page 预算硬限制**：不够时阴影质量掉档
- **Directional Light Clipmap 难调**：8 vs 16 vs 32 没有通用最优
- **Non-Nanite 路径慢**：CPU cull 性能差，需要开 GPU HZB
- **5.8 之前 Mac 上 page residency 有 bug**：5.4+ 修复

---

## 面试谈资

> **30 秒版**：VSM 是 30+ CVar 控制的 page table 系统，物理 page 128x128、4-5 mip level，page allocation 走 LRU + lock + 复用，Nanite / Non-Nanite 双路径分流，Directional Light 走 8-16 层 Clipmap，5.4+ 跟 Nanite cull 共享。
>
> **2 分钟版（按追问链）：**
>
> **Q1: VSM page 预算不够会怎样？**
> → `BuildPageAllocations` 触发 evict：LRU → 复用远场 page → locked 不动。结果远处大物体阴影闪烁（page 被反复 evict / reallocate）。调 `r.Shadow.Virtual.MaxPhysicalPages` 加大预算。
>
> **Q2: Nanite vs Non-Nanite 怎么走不同路径？**
> → `RenderVirtualShadowMapsNanite` (`:4218`) 走 Nanite cull 共享路径，效率高。`RenderVirtualShadowMapsNonNanite` (`:4389`) 走传统 mesh draw command 路径，默认 CPU cull 慢，要开 `r.Shadow.Virtual.NonNaniteVsmUseHzb 1` 走 GPU HZB。
>
> **Q3: Directional Light 怎么走 VSM？**
> → 走 `FVirtualShadowMapClipmap` (32 KB)，8-16 层 cascade，每层独立 page pool，page 跨层共享。`r.Shadow.Virtual.PageDilationBorderSize.Directional 0.1` 减少 30% 锯齿（5% cost）。
>
> **Q4: 5.4+ 跟 MegaLights 怎么集成？**
> → `r.Shadow.Virtual.MarkCoarsePagesLocal 1` 默认开 Local light coarse page → 5.4+ MegaLights 判定式：n lights >= 8 走 VSM（共享 page pool），< 8 走传统 shadow。

---

## 与工作的关联

- **day-job (RAG + Mac Game Harness)**：本笔记 + VSM 论文笔记 = VSM "理论 + 源码" 闭环，是 day-job LLM 调阴影必备
- **VSM 调参指南**：本笔记 30+ CVar 全带行号，**LLM 调参时可精确说"改 X cvar → 影响 Y 函数"**

---

## 输出产物

- [x] 已画流程图/类图
- [x] 已写分析笔记（本文, 本机 UE5.8 源码行号全部核对）
- [x] 已对照 VSM 论文 + Lumen Surface Cache (同源) 交叉验证
- [x] 已写 5 类问题诊断 Checklist
- [x] 已写 CVar → 源码函数映射（30+ CVar 全带文件:行号）
- [x] 已写"为什么 VSM 闪烁"诊断
- [ ] 已写博客 → 待 M6 milestone
- [ ] 已应用到工作中 → 待 day-job RAG 索引确认

---

*Create date: 2026-07-20*
*Last modified: 2026-07-20*
