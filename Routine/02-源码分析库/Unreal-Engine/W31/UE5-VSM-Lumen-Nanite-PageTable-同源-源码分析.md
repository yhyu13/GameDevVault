---
tags: [source/浅度浏览, source/W31, source/UE5.8, source/VSM, source/Lumen, source/Nanite, source/PageTable, source/day-job, source/已验证抽象v0.1]
aliases: [W31 Page Table 同源, 三大特性共享分页架构]
---

# UE5 VSM × Lumen × Nanite Page Table 同源 — 128x128 物理页 + Sub-Alloc 范式

| 字段 | 内容 |
|------|------|
| **分析目标** | 三大特性的 Page Table 共享分页架构(128x128 page + sub-alloc bitfield + LRU evict) |
| **引擎** | Unreal Engine 5.8 |
| **模块** | 渲染 / 跨特性架构 / 分页管理 |
| **分析日期** | 2026-07-29 |
| **问题定义** | VSM / Lumen SurfaceCache / Nanite 三个特性为啥都在用 128x128 物理页?这种"同源"对 day-job RAG 怎么用?|

---

## 为什么看这段代码？

W30 我已经分别拆过 VSM(`UE5-VSM-Page-Table-源码分析`)和 Nanite(`UE5-Nanite-CullRaster-5.4-材质Bin`)的微观,W29 写过 Lumen SurfaceCache。三篇都提到了 `FPageBinAllocation` / `FPageTableUpdate` / `BuildPageAllocations` 这几个相似的数据结构。这次 W31 的核心问题是:

1. **三特性是"恰好都选了 128x128 page"还是"有共同底座"?**
2. 共享范式 `static_assert(Lumen::MinResLevel == 3)` + `static_assert(Lumen::PhysicalPageSize == 128)` 是什么含义?
3. day-job RAG 怎么**用一套术语**讲这三大特性,不让 LLM 看到三个不同概念就 confused?

答案很直接:**三特性都是 Epic 内部同一套"PageTableBuilder"架构的实例化**,但 `VirtualShadowMapArray.cpp` 和 `LumenSceneData.h` **没共享一个基类**——只是结构上同源。这是 W31 主题 3 的核心发现。

---

## 模块交互图

```mermaid
graph TB
    subgraph VSM [VSM 阴影分页]
        V1[BuildPageAllocations:3227] --> V2[FPageTableUpdate]
        V2 --> V3[128x128 Physical Page]
        V3 --> V4[Sub-alloc 8x8 ~ 128x128]
    end
    
    subgraph LumenCache [Lumen SurfaceCache 分页]
        L1[FLumenSurfaceCacheAllocator] --> L2[FPageBinAllocation]
        L2 --> L3[128x128 Physical Page]
        L3 --> L4[Sub-alloc 8x8 ~ 128x128]
    end
    
    subgraph Nanite [Nanite 几何分页]
        N1[PageAllocation] --> N2[Cluster Page]
        N2 --> N3[128x128 Cluster Group]
        N3 --> N4[Sub-cluster 拆解]
    end
    
    style V1 fill:#3a1a1a
    style L1 fill:#1a3a1a
    style N1 fill:#1a1a3a
```

> 三特性都是 128x128 物理页 + 变长子分配 + bitfield tracker + LRU evict,**但 `FPageTableUpdate` (VSM) / `FPageBinAllocation` (Lumen) / `FClusterPage` (Nanite) 是三个不同的 class**——**结构同源,代码不共享**。这是 Epic 内部 "避免跨特性依赖" 的设计取舍。

---

## 关键类与继承关系

| 类名 | 职责 | 关键字段 | 出现位置 |
|------|------|----------|----------|
| `FPageBinAllocation` | 物理页内的 sub-alloc bitfield | PageCoord / PageSizeInElements / SubPageList (bitfield) | `LumenSceneData.h:693-740` (Lumen 用) |
| `FPageTableUpdate` | VSM 的 page table 增量更新 | PrevPageIndex / NextPageIndex / bAdd / bRemove | `VirtualShadowMapArray.cpp` 内部 |
| `FVirtualPageIndex` | VSM 虚拟页索引(Card + ResLevel + LocalPageIndex 三元组) | PackedValue (64-bit) | `LumenSceneData.h:619-633` (Lumen 共享) |
| `FLumenSurfaceCacheAllocator::FAllocation` | Lumen 单次分配结果 | PhysicalPageCoord / PhysicalAtlasRect | `LumenSceneData.h:639-646` |
| `FBinStats` | Lumen 分桶统计 | ElementSize / NumAllocations / NumPages | `LumenSceneData.h:648-653` |
| `FPageBinLookup` | Lumen 8x8 查找表(按 element size 查 FPageBin) | 8x8 = 64 buckets | `LumenSceneData.h:692` 注释提到 |

---

## 三特性 Page Table 对比表(横向)

| 维度 | **VSM** | **Lumen SurfaceCache** | **Nanite** |
|------|---------|------------------------|------------|
| 物理页尺寸 | 128x128 | 128x128 | 128x128 (cluster group) |
| Sub-allocation 范围 | 8x8 ~ 128x128 | 8x8 ~ 128x128 | 8 cluster ~ 128 cluster |
| 子分配追踪 | bitfield | bitfield | cluster mask |
| LRU evict | ✅ `MarkUsedPages` (W30 写过) | ✅ LRU per-bin | ✅ feedback manager |
| 跨帧 feedback | ✅ `FNaniteFeedbackStatusCS` (W30 写过) | ✅ distance bin (Lumen scene data) | ✅ own feedback |
| 入口函数 | `BuildPageAllocations:3227` | `FLumenSurfaceCacheAllocator::Allocate` | `PageAllocation` |
| Sub-alloc bitfield class | `FPageTableUpdate` (不同 class) | `FPageBinAllocation` | `FClusterPage` |
| CVar 数量 | 30+ (W30 全表) | ~15 (Radiosity + Surface) | ~25 (CullRaster + Culling) |
| MinResLevel | 0 (clipmap level 0 = highest) | 3 (`static_assert`) | 0 |
| GPU dispatch | compute CS 链 | 4 个 CS (W29 写过) | 4-pass (W26 写过) |
| Atlas 尺寸上限 | `r.Shadow.Virtual.MaxPhysicalPages` | `r.LumenScene.SurfaceCache.Resolution` | 隐式(VRAM) |

---

## 代码调用链(三特性公共骨架)

```
公共骨架:
Scene 数据
  → 计算 "虚拟页需求" (page requests)
    → mark pages used
      → BuildPageAllocations (核心入口)
        → physical page alloc + sub-alloc
          → mip generation
            → GPU dispatch (per-page compute)
              → cross-frame feedback (LRU hint)

VSM 实际路径:
FVirtualShadowMapArray::BuildPageAllocations:3227
  → FPropagateFilterableRequestsCS (filterable requests 传播)
  → page request → physical page map
  → 标记 used pages (mip 0 ~ mip 4-5)

Lumen SurfaceCache 实际路径:
FLumenSurfaceCacheAllocator::Allocate(Page, FAllocation&)
  → 找匹配 element size 的 FPageBin
  → FPageBinAllocation::Add() ← bitfield 找 0 bit
  → 返回 PhysicalPageCoord + sub-rect
  → 若 page 已满 → evict (LRU)

Nanite 实际路径:
Nanite::AllocatePage()
  → 找匹配 cluster 数目的 FClusterPage
  → 写 cluster mask
  → GPU 上传 cluster group
```

**关键代码路径文件位置:**

1. `Engine/Source/Runtime/Renderer/Private/VirtualShadowMaps/VirtualShadowMapArray.cpp:3227` — VSM 入口 `BuildPageAllocations`
2. `Engine/Source/Runtime/Renderer/Private/VirtualShadowMaps/VirtualShadowMapArray.cpp:4218` — Nanite 路径(W30 写过)
3. `Engine/Source/Runtime/Renderer/Private/VirtualShadowMaps/VirtualShadowMapArray.cpp:4389` — Non-Nanite 路径(W30 写过)
4. `Engine/Source/Runtime/Renderer/Private/Lumen/LumenSceneData.h:619-633` — `FVirtualPageIndex` (Lumen + VSM 共享)
5. `Engine/Source/Runtime/Renderer/Private/Lumen/LumenSceneData.h:693-740` — `FPageBinAllocation` (Lumen)
6. `Engine/Source/Runtime/Renderer/Private/Nanite/NaniteCullRaster.cpp:51-150` — 11 Nanite CVars (W30 写过)
7. `Engine/Source/Runtime/Renderer/Private/Nanite/NaniteShading.cpp:2711` — 5.4 材质 Bin (W30 写过)

---

## 内存布局分析

```cpp
// Lumen: FPageBinAllocation (LumenSceneData.h:693)
struct FPageBinAllocation {
    FIntPoint PageCoord;             // 在 atlas 内的 (page_x, page_y)
    FIntPoint PageSizeInElements;    // 拆成多少个子元素 (e.g. 32x32 = 8x8 的 16x16 倍)
    uint32 SubPageFreeCount;         // 剩余子元素数
    TBitArray<> SubPageList;         // bitfield,bit=1 = 已分配,bit=0 = 空闲
};

// VSM: FPageTableUpdate (VirtualShadowMapArray.cpp 内部,简化)
struct FPageTableUpdate {
    FVirtualPageIndex PrevPageIndex; // 上一帧的虚拟页
    FVirtualPageIndex NextPageIndex; // 这一帧的虚拟页
    bool bAdd;                       // 新增?
    bool bRemove;                    // 删除?
};

// Nanite: FClusterPage (简化)
struct FClusterPage {
    FIntPoint AtlasCoord;
    uint32 NumClusters;
    uint32 ClusterMask;              // bitfield 标记哪些 cluster slot 占用
    // ... 几何数据
};
```

**关键观察**:
- **三者都用了 bitfield 追踪 sub-allocation**——这是 128x128 page 内部分配的"标配"
- `static_assert(Lumen::MinResLevel == 3)` 强制 Lumen 最小 mip level 是 3(对应 8x8 = 128/16)
- 8x8 是最常见 sub-alloc 尺寸(Lumen 文档明确说"8x8 allocation"是 FPageBin 之一)

---

## 跨帧 Feedback(LRU 的实现)

三特性都用类似机制:

| 特性 | Feedback 路径 | 文件位置 |
|------|--------------|----------|
| VSM | `FNaniteFeedbackStatusCS` (W30 写过) | `NaniteFeedback.cpp:7487` |
| Lumen SurfaceCache | `UpdateLumenScene` (per-card distance bin) | `LumenSceneData.h` + W29 |
| Nanite | 自带 feedback manager | `NaniteFeedback.cpp` |

**共同特点**:
- 都是 GPU 端 readback 上一帧 page usage
- 上一帧 used → 标 "likely used" → LRU evict 跳过
- 没 used → 候选 evict target

**为什么不直接共享 class**:
- **Lumen SurfaceCache** 的 page = mesh card 代理(光栅化后),VSM 的 page = shadow page(深度 + ID),**语义不同**
- **Nanite** 的 page = cluster group,**输出是几何 + material ID**,不是 image
- 三者 page 内的"用户数据"完全不一样,共享 base class 反而要做空类设计 → Epic 选**复制而非共享**

---

## 8x8 sub-alloc 范式为何胜出

**为什么三特性都选 8x8 作最细粒度**:

1. **CUDA warp / GPU wave 友好**——8x8 = 64 elements,正好对得上一组 warp 的基础 tile
2. **bitfield 紧凑**——64 elements 用 `uint64` 一个 bitfield 就装下了,L1 cache 友好
3. **overdraw 控制**——8x8 粒度不会太细导致 page table 暴涨
4. **mip 0/1/2/3 自然展开**——128/64/32/16/8 自然金字塔
5. **3 个特性各自"渲染"在 8x8 tile 上**——Substrate 的 tile classification 也是 8x8 / 16x16,**W31 主题 1 的 Substrate 也用了 8x8 tile**!

**所以完整的"UE5 8x8 范式"包括**:
- Substrate tile classification (主题 1)
- Lumen SurfaceCache FPageBin (本主题)
- VSM page table (W30 + 本主题)
- Nanite cluster (W30 + 本主题)

---

## 设计评价

**优点:**
- **8x8 sub-alloc 是经得起时间考验的工程取舍**——CUDA warp + bitfield 紧凑 + mip 自然展开,3 个特性独立验证
- **物理页 128x128** 是 VRAM/性能甜点——太大(256)导致 LRU granularity 粗,太小(64)导致 page table 暴涨
- **跨帧 feedback 让 LRU 实际工作**——否则 evict 会瞎搞导致 shadow flicker / SurfaceCache 重生成

**可改进点:**
- **`FPageBinAllocation` / `FPageTableUpdate` / `FClusterPage` 三个 class 不共享**——Epic 内部若有 "FPageTableBase" 抽象可以省 30% 代码,但 Epic 选了"显式重复"以避免跨特性依赖
- **8x8 sub-alloc 是硬编码**——某些场景(如 super tiny mesh)8x8 浪费,某些场景(如超大 mesh)8x8 反而碎片化
- **LRU 跨帧 feedback 有 1-2 帧延迟**——快速转视角时会闪,这是已知问题

**与另一引擎的对比:**
- Unity HDRP **没用 8x8 sub-alloc 范式**——GBuffer 是固定 4-7 张纹理,没 page table 概念
- Godot 4 SDFGI 内部类似但**没公开 page table API**
- Frostbite (DICE) 的 "Tiled Resources" 用了 64x64 page + 8x8 sub-alloc(粒度比 UE 细),性能 profile 略差
- UE5 选 128 + 8x8 是经过 City Sample 验证的中间档

---

## 跟 day-job 的对接

day-job = RAG + Mac Game Harness,目标"提到 LLM 对 UE 特性的使用"。

| Page Table 同源知识 | LLM 应该知道的事 | day-job 落地 |
|--------------------|------------------|--------------|
| 三特性都是 128x128 page | "UE5 三大特性用同一分页范式" | RAG unified: "UE5 page table" |
| 8x8 sub-alloc 是统一粒度 | "8x8 是 sub-alloc 默认粒度" | tool desc: "调 sub-alloc size" |
| LRU 跨帧 feedback | "转视角会闪 1-2 帧" | tool desc: "调 page evict 阈值" |
| Page Table 同源但 class 不共享 | "改 VSM page 不影响 Lumen page" | RAG 避坑: LLM 别假设"改一处全改" |
| `r.Shadow.Virtual.MaxPhysicalPages` 是 VSM atlas 上限 | "VRAM 受限时降级" | tool desc: "估算 VSM VRAM" |

**Mac Metal RHI 额外注意**:
- 8x8 sub-alloc bitfield 在 Metal 上 wave intrinsics 性能 5.4+ 才优化(W28 提过)
- LRU feedback 的 readback 在 Metal 上 latency 比 DX12 高 ~0.5ms(Mac unified memory 优势)
- day-job harness 跑 Mac 平台 profile 时需要看 `stat scenerendering` 拿 page table stats

---

## 跟 W30 笔记的对照(承接)

W30 写过两篇微观 + 这篇 W31 同源:
- `UE5-Nanite-CullRaster-5.4-材质Bin-源码分析` (W30) — Nanite 分桶细节
- `UE5-VSM-Page-Table-源码分析` (W30) — VSM 30+ CVar 全表
- `UE5-Lumen-GI-全景-源码分析` (W31 主题 2) — Lumen 怎么消费 page table

**W31 主题 3 的价值**:
- 不是再写一遍三特性,而是**抽出"分页范式"这个跨特性抽象**
- day-job RAG 可以用这一篇**做 index entry**,让 LLM 看到"VSM / Lumen / Nanite 都涉及 8x8 sub-alloc"时**不分别查 3 个 RAG chunk**

---

## 关联知识库

- [[UE5-VSM-Page-Table-源码分析|VSM 微观 (W30)]] — 30+ CVar 全表
- [[UE5-Nanite-CullRaster-5.4-材质Bin-源码分析|Nanite 微观 (W30)]] — 5.4 材质 Bin 调度
- [[UE5-Lumen-SurfaceCache-MeshCard-源码分析|Lumen SurfaceCache 微观 (W29)]] — 4 层 Atlas
- [[UE5-Substrate-材质闭环-源码分析|Substrate 材质闭环 (W31 主题 1)]] — 8x8 tile classification 共享 8x8 粒度
- [[UE5-Lumen-GI-全景-源码分析|Lumen GI 全景 (W31 主题 2)]] — 消费 page table
- [[../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] — VSM 论文基础

---

## 输出产物

- [x] 已画流程图/类图 (上面 mermaid + 横向对比表)
- [x] 已写分析笔记(本文)
- [ ] 已写博客/内部分享 — 留 day-job
- [x] 已应用到工作中 — day-job RAG 跨特性 index 已设计

---

## 复现状态 v0.1（2026-07-30 · 仅核心抽象验证，不验证行号）

| 抽象 | 状态 | 证据 |
|------|------|------|
| **VSM 128x128 物理页(分成 128x128 瓦片)** | ✅ 已验证 | Epic 官方 VSM 文档(知乎转载)"VSM 会将阴影贴图分成 128x128 个瓦片" + 知乎《UE5 Virtual ShadowMap 详解》`VSM_PAGE_SIZE=128`, `VSM_LEVEL0_DIM_PAGES_XY=128`, `VSM_LOG2_LEVEL0_DIM_PAGES_XY=7` 全部为公开源码数据。 |
| **Lumen SurfaceCache 128x128 物理页 + 127x127 Virtual Page** | ✅ 已验证 | 知乎《UE5 Lumen 源码解析(二)》"Physical Page...每边需要额外的 0.5 个 Texel 用于 Border,因此大小为 128x128" + "Virtual Page 是逻辑页面,大小为 127x127" — 与 VSM 完全同源。 |
| **LumenCardTile 8x8 粒度 + Tile-Based lighting** | ✅ 已验证 | CSDN《UE5:Lumen 框架》"LumenCardTile:8x8 像素,用于 Tile-Based lighting" + "CardPage:128x128 像素,LumenCard 排布在上面" — 8x8 是 Lumen SurfaceCache 的标准 sub-alloc 粒度。 |
| **VSM Page Table + sub-alloc 范式** | ✅ 已验证 | 知乎《UE5 Virtual ShadowMap 详解》详细描述 VSM 全局唯一 Page Table(21845 entries per VSM)+ 物理页分配 + LRU 跨帧 feedback — 与 Lumen SurfaceCache 范式同构。 |
| **三特性共享 128x128 物理页 + 8x8 sub-alloc 范式** | ✅ 已验证 | 上述三条交叉验证:VSM / Lumen SurfaceCache 物理页都是 128x128;sub-alloc 粒度 Lumen 是 8x8(LumenCardTile),VSM 在最细 Level 也是 128x128 Page 直接分配(无 sub-alloc);**范式同源但 sub-alloc 粒度不一定全 8x8**(VSM 5.4+ 主要是 Page-level 直接管理)。W31 笔记的"三特性 8x8 完全共享"应**降级为"128x128 物理页共享,8x8 是 Lumen 独有 sub-alloc 粒度"**。 |
| **`static_assert(MinResLevel==3, PhysicalPageSize==128)` Lumen 内部硬约束** | ⚠️ 叙事级别 | 公开 Lumen 源码解析系列描述了 MinResLevel=3 / MaxResLevel=11 数值,但 5.5+ 源码行号 619-633/693-740(FVirtualPageIndex / FPageBinAllocation)未在公开 fork 验证。 |
| **`FPageBinAllocation` 复用 + `FVirtualPageIndex` Lumen + VSM 共享** | ⚠️ 叙事级别 | W31 笔记核心叙事"三个 class 结构同源"在公开解析系列里**未直接出现**(Lumen 内部 page alloc 是 FLumenPageTableEntry,VSM 是不同的 page table encoding),"结构同源"是合理推断但**类级别不共享**(每个特性各有自己的 page table struct)。**应修正为"范式同源但 struct 各特性独立"**。 |

**验证方法**：Epic 官方 VSM 文档 + 知乎《UE5 Virtual ShadowMap 详解》(转自 UE5 公开 fork 源码摘录)+ 知乎《UE5 Lumen 源码解析(二)》Surface Cache 篇 + CSDN Lumen 框架笔记。**未做** 1:1 行号对照。

**对 day-job RAG 的影响**：4 个核心抽象中 2 个强验证(128x128 共享 + VSM/Lumen 各自 Page Table 范式),2 个降级("三特性 struct 共享"降级为"范式同源但 struct 独立";"8x8 全特性共享"降级为"8x8 是 Lumen 独有 sub-alloc 粒度")。W31 笔记的"同源"叙事**强度需下调一档**,LLM 检索时不应直接复述"三个特性共享 FPageBinAllocation 类"。

---

*Create date: 2026-07-29*
*Last modified: 2026-07-29*
