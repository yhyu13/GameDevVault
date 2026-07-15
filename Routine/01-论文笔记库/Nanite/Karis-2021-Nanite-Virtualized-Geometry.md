---
tags: [paper/signed, paper/SIGGRAPH, paper/Nanite, paper/UE5, paper/rendering, paper/P0]
aliases: [Karis-2021-Nanite, Nanite-SIGGRAPH-2021, Journey-to-Nanite, Virtualized-Geometry-Pipeline]
---

# Karis-2021-Nanite-Virtualized-Geometry

> Nanite: A Pipeline for Photorealistic Real-Time Geometry Pipeline（虚拟几何管线）

| 字段 | 内容 |
|------|------|
| **论文标题** | Nanite: A Pipeline for Photorealistic Real-Time Geometry |
| **作者** | Brian Karis (Epic Games) |
| **发表年份/会议** | 2021 / SIGGRAPH 2021 Courses |
| **原始链接** | [本地 PDF](file:///C:/Git-repo-my/GameDevVault/Rendering/Document/UnrealEngine/Nanite/SIGGRAPH2021_Nanite.pdf) · [Journey to Nanite PDF](file:///C:/Git-repo-my/GameDevVault/Rendering/Document/MeshClusterShading/Journey_to_Nanite.pdf) · [公开 dev blog](https://www.unrealengine.com/en-US/blog/nanite-a-virtual-geometry-pipeline-advanced-in-real-time) |
| **阅读日期** | 2026-07-15 |
| **精读时长** | ~2.5 h（三份 PDF + UE5.8 源码交叉） |

---

## 一句话总结

> 这篇论文 + 配套 GDC/SIGGRAPH talk 解决了 **"实时渲染十亿级多边形的高 LOD 模型"** 的问题，通过 **"Mesh Cluster 树 + 软光栅 + GPU-Driven Culling + 材质 Bin 调度"** 的方法，实现了 **"UASS 资产 0 LOD pop、无距离衰减、亚像素 micro-triangle 正确处理"** 的效果，**是 UE5 一切 GPU-Driven 渲染的范式起点**。

---

## 核心创新点

1. **Mesh Cluster 树（Bounding Volume Hierarchy, BVH）作为几何数据组织**。原始 mesh 在导入时（UV 通道 / 离线构建）被切分成 **128-triangle Cluster**（典型 64-256 不等），多个 Cluster 形成 BVH 树。**关键设计**：Cluster 是 **coherent**（邻接 + 法线连续 + LOD 兼容）的，**不是简单地按三角形数切**——这点跟传统 quad-tree LOD / meshlet（NVIDIA Mesh Shading）有本质区别。**对 day-job 启发**：day-job Mac Game Harness 如果要做实时场景流式加载，应该照搬"Cluster 树 + LOD 元数据一起 bake"的范式。
2. **GPU-Driven Culling**（Visibility Buffer 范式）。LOD 选择 + Frustum / Occlusion 裁剪 + Backface 裁剪 **全部在 GPU 上并行完成**，CPU 不参与。**关键技术点**：
   - **HZB（Hierarchical Z-Buffer）裁剪**——从上一帧的 depth 构造 mip 链，本帧做 conservative occlusion
   - **Software Rasterization**——亚像素 micro-triangle（< 1 pixel）专用路径，避免硬件光栅的 quad overdraw
   - **Persistent Threads + Atomic Counter**——每 cluster 1 线程，命中后 atomic add 到 visible list
   **对 day-job 启发**：day-job LLM-driven UE on Mac 走 GPU-Driven 路径是必然，HZB 裁剪可以无缝迁移到 Metal RHI。
3. **Visibility Buffer（vs G-Buffer）**。传统 deferred shading 把 material attribute 写进 G-Buffer，Nanite 改成 **只写 (PrimitiveID, TriangleID, Barycentric) 三个标量**到 Visibility Buffer，然后 **material shading 阶段从 VS 中拿到三角形的实际 vertex 重新计算 material attribute**。**关键优势**：
   - **显存** G-Buffer 5-8 个 MRT → Visibility Buffer 1 个 32-bit，**省 5-8x 显存 + 带宽**
   - **可绘制性** 硬件光栅化在 micro-triangle 时 quad overdraw 严重，Visibility Buffer + software 路径规避
   **对 day-job 启发**：day-job Mac 上做大量 distant geometry 渲染时，Visibility Buffer 范式可以省一半带宽。
4. **材质 Bin 调度（GDC 2024 Karis 更新）**。UE 5.0 时期 Nanite 材质管线 **每种材质 1 个全屏 draw call**——City Sample 4015 个 shading bin 中 3675 个是空的（90% 浪费）。UE 5.4+ 引入 **Compute Shader + Bin 算法**把空调度降低 80%。**关键设计**：
   - 把所有可见三角形按 (Mesh, Material, TriBin) 分桶
   - 同一桶内三角形合并成 1 个 draw
   - Bin 大小由 triangle count × material cost 决定
   **对 day-job 启发**：LLM 调 Lumen/Nanite 时要知道"5.4 之前 4015 个 draw → 5.4 之后 ~340 个 draw"这种量级跃迁。
5. **Persistent Culling State + Feedback Loop**。每帧的 visible cluster 列表 **保留在 GPU buffer**，下一帧从同一 buffer 出发做 delta 更新（增量 HZB）。**关键设计**：
   - 不需要 CPU 同步
   - 跨帧 TAA temporal 复用
   - 内存 ~ 几 MB（百亿级三角形每帧 1-2 万 visible cluster）
   **对 day-job 启发**：跟 [[Lumen Surface Cache 笔记]] 的 `CardPageLastUsedBuffer` 同源——UE5 一致地走 "GPU-resident state + feedback"。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按 day-job "LLM-driven UE on Mac" + "Mac Game Harness" 视角）：**

1. **Nanite 知识是 day-job RAG 语料的高频入口**。LLM 在 RAG 检索时遇到"Lumen / 性能 / 高 LOD / 巨量多边形"问题会先调取 Nanite 知识。**对 day-job 启发**：把本文 + [[../Nanite\|既有 W26 Nanite 源码分析笔记]] + [[../Nanite-Card-Pack\|W27 Nanite 卡牌]] 进 RAG 索引，LLM 能理解"为什么 Nanite 在 5.4 之前 draw 多 / 5.4 之后 draw 少"。

2. **GPU-Driven Culling 范式 = day-job Mac Game Harness 的渲染决策模式**。Nanite 的 "CPU 离线构建 BVH + GPU 运行时 cull" 范式是 UE5 一切 GPU-Driven 系统的"祖先"——Lumen 的 [[../02-引擎源码分析库/Unreal-Engine/W26/UE5-Lumen-源码调用链\|Screen Probe Gather]] / [[../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-InstanceCulling-GPU裁剪\|InstanceCulling]] / [[../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-MegaLights-随机光照\|MegaLights]] 全都走这条路径。**对 day-job 启发**：Mac Game Harness 的所有 GPU 路径决策都按"CPU 离线 + GPU 在线"切分。

3. **Visibility Buffer 范式 = day-job Mac 上节省带宽的金钥匙**。Mac Metal RHI 带宽敏感，Visibility Buffer 节省的 5-8x 带宽是落地关键。**对 day-job 启发**：day-job Mac 上 Lumen/Nanite 集成时，**优先验证 Visibility Buffer 路径**而不是 legacy G-Buffer。

4. **Cluster 树 + LOD 兼容性 = day-job 流式加载的范式参考**。Nanite 的"128-tri cluster + coherent"切分可以推广到 day-job 任何"动态资产流式加载"场景。**对 day-job 启发**：Mac Game Harness 如果做 UE project 的 streaming 工具，cluster + coherent 切分是关键——能保证 LOD 切换不 pop、不闪烁。

5. **材质 Bin 调度的 90% 浪费历史 = day-job 性能 profile 的教训**。Nanite 5.0 时期 4015 个 bin 中 3675 个是空的（90% 浪费）——这种"算法对了但调度错"的性能陷阱，正是 day-job 调 LLM RAG 索引时要识别 / 解释的常见 case。**对 day-job 启发**：LLM 调参指南要包含"5.4 之前的项目升级 5.4 后自动收益 / 复杂场景 2x+"。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|--------------|
| **Cluster 切分算法** | Karis 自己说这是整个 Nanite 最难的部分，**不是简单按三角形数切**，要保证 cluster 内邻接 + 法线连续 + LOD 兼容（不同 LOD 间 cluster 边界对齐）。具体是 Raster-oriented cluster 算法（基于 UV 通道）。 | 是 — 写"流式加载"工具必学 |
| **HZB 构造开销** | HZB 需要从上一帧 depth 构造 mip chain，5x5 downsample pass × log2(resolution) 层。**实际开销 < 0.1ms** 但要小心 resolution 变化（视角切换 / window resize）。 | 否 — 引擎自动处理 |
| **Software Raster 微三角形** | Karis 用 SW 路径处理 < 1 像素三角形，**实际占比 50-80% 三角形都是 micro-triangle**（distant + small material detail），硬件光栅 quad overdraw 灾难。SW 路径的 SIMD lane mask 是关键。 | 是 — 写自定义 mesh shading 时要懂 |
| **Material Bin 调度的 cache miss** | Bin 排序按 (MeshID, MaterialID, TriBin)，排序不当会 GPU L1/L2 命中率低。**实测** 5.0 → 5.4 提升 80% 但要 material schema 稳定。 | 否 — 引擎自动排序 |
| **GPU-Driven Persistent State 与 CPU 同步** | 跨帧 visible cluster 在 GPU buffer，**CPU 读不到**——这影响 debug 工具。Epic 提供 `r.Nanite.ShowStats` 把 GPU 状态 readback 到 UI，但有 1-2 帧延迟。 | 否 — 用 cvar 即可 |

---

## 是否值得复现？

- [ ] 是 — 已列入待办
- [ ] 否 — 仅了解思路即可
- [x] **部分** — 只在 **"GPU-Driven Culling 范式"** + **"Cluster 切分算法"** + **"Visibility Buffer 设计"** 这三个核心概念做记录

**复现计划（如选是）：**

1. **Cluster 切分算法**（最重要）—— 在 [[Unreal/Engine/Source/Runtime/Renderer/Private/Nanite/`NaniteCluster.cpp`]] 直接读 Epic 实现，**不要从零写**（Karis 自己说 6 个月才稳定）
2. **HZB 裁剪**（中等）—— 用 [[Unreal/Engine/Source/Runtime/Renderer/Private/SceneVisibility.cpp]] 的 `BuildHZB` 做参考
3. **Visibility Buffer shading**（进阶）—— [[Unreal/Engine/Shaders/Private/Nanite/NaniteVisBuffer.ush]] 是真实 shader，可以从抄起手
4. **不直接复现**：material bin 调度（太工程化，Epic 已经把 80% 调度搞定了）

---

## 关键公式/伪代码

```cpp
// Nanite 核心 cull loop (简化版 — 真实代码在 NaniteVisibility.cpp)
void Nanite::CullInstances(GraphBuilder, View)
{
    // 1. 准备 HZB（上一帧 depth 的 mip 链）
    FRDGTextureRef HZB = BuildHZB(GraphBuilder, View.PreviousDepth);

    // 2. 启动 Persistent Culling CS
    AddClearUAVPass(GraphBuilder, VisibleClustersUAV, 0);
    AddPass<FCullCS>(GraphBuilder, [...]);  // 每个 cluster 1 线程

    // CullCS 内部伪代码:
    // [NumThreads(64, 1, 1)]
    // void MainCS(uint3 DispatchThreadId : SV_DispatchThreadID) {
    //     uint ClusterIdx = ...;  // persistent thread index
    //
    //     // (a) 早期 exit: 不可见
    //     FCluster Cluster = LoadCluster(ClusterIdx);
    //     if (CullByFrustum(Cluster, View)) return;
    //     if (CullByOcclusion(Cluster, HZB)) return;
    //     if (CullByDistance(Cluster, View)) return;
    //
    //     // (b) 递归到子 cluster
    //     if (Cluster.HasChildren()) {
    //         for (Child in Cluster.Children) EnqueueCulling(Child);
    //     } else {
    //         // 叶子 cluster,加入 visible list
    //         uint Slot = AtomicAdd(VisibleClustersCounter, 1);
    //         VisibleClusters[Slot] = ClusterIdx;
    //     }
    // }
}

// Visibility Buffer 渲染伪代码 (Shaders/Private/Nanite/NaniteVisBufferPixelShader.usf)
void Nanite::RenderVisibilityBuffer(GraphBuilder, View)
{
    // 1. 渲染所有 visible cluster 到 visibility buffer
    // 每个 cluster 1 draw,只有 depth + primitiveID + triangleID + barycentric 输出
    AddPass<FRenderVisibilityBufferPS>(GraphBuilder, VisibleClusters);

    // 2. 单独 stage 做 material shading
    // 复用 visibility buffer 里的 (PrimID, TriID, Barycentric)
    // 从 VS 重新计算 vertex attributes
    AddPass<FMaterialShadingCS>(GraphBuilder, VisibilityBuffer);
}
```

> **关键观察**：
> - Nanite 把"渲染"切成 **2 步**——VB raster + Material shading——**这是 visibility buffer 范式的核心**
> - 2 步之间有 **dependency buffer**（或者直接按 cluster 顺序做 single-pass）
> - Persistent thread + atomic counter 模式 = GPU-Driven 通用 pattern（不只 Nanite）

---

## 相关论文/前置知识

- [[../../../02-引擎源码分析库/Unreal-Engine/W26/UE5-Nanite-虚拟几何shader]] — W26 写的 Nanite 源码分析笔记（中文）
- [[../../../02-引擎源码分析库/Unreal-Engine/W27/Nanite-Card-Pack]] — W27 写的 Nanite 面试卡牌
- [[../../../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-InstanceCulling-GPU裁剪]] — W28 写的 UE5.8 GPU Culling 笔记（Nanite 范式的延伸）
- [[../../../02-引擎源码分析库/Unreal-Engine/W26/UE5-Lumen-源码调用链]] — Lumen 笔记（Nanite 是 Lumen 的几何源）
- [[../../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] — W29 写的 Lumen Surface Cache（Nanite 范式在 GI 上的应用）
- [[../../../04-性能优化备忘录/知识参考/Nanite 性能调优]] — Nanite 性能 profile 笔记
- [[../../../04-性能优化备忘录/瓶颈案例/Nanite-WPO材质降级-穿模修复]] — Nanite WPO bug
- [[../../../04-性能优化备忘录/瓶颈案例/DrawCall-爆炸-植被渲染]] — 植被场景 draw call 爆炸（Nanite 不直接解决）
- [[Visibility Buffer paper\|Aila-2013-Visibility-Buffer (论文)]] — Visibility Buffer 原始论文（待补）
- [GDC 2024 Karis "Nanite 5.4 Update"](https://www.gdcvault.com/) — 5.4 材质 Bin 调度的演讲（公开 vault 收录）

---

## 个人评价

**优点：**
- **范式创新**——Nanite 不是"更好的 LOD 系统"，是"完全不同的几何处理范式"。Lumen / MegaLights / Substrate / InstanceCulling 全都走 Nanite 这条路
- **公开深度**——Epic 罕见的"把生产管线完整讲出来"——PDF + talk + dev blog + GDC 演讲全公开
- **跨平台考虑**——从 SIGGRAPH 论文到 UE5 落地，**考虑到了 D3D12 / Vulkan / Metal 三大 RHI**（Mac 兼容性是 day-job 关键）

**局限性：**
- **Cluster 切分工具是商业闭源**（UnrealEditor 内置），学术界无法直接复现
- **WPO（World Position Offset）支持有限**——Nanite 5.0 之前不支持 WPO，5.4+ 支持但有性能 cost
- **透明材质不友好**——Visibility Buffer 范式对 Alpha Test 勉强支持，**对 Alpha Blend 完全不友好**——这个洞被 [[../../../04-性能优化备忘录/瓶颈案例/Nanite-WPO材质降级-穿模修复\|WPO 穿模修复笔记]] 验证过
- **5.0 → 5.4 跨度大**——5.0 时期材质 bin 90% 浪费的问题，5.4 才解决，**升级要谨慎**

**启发：**
- **"GPU 离线 + GPU 在线"是 UE5 一切新系统的范式**——从 Nanite 到 Lumen 到 Substrate 全走这条
- **Visibility Buffer 是带宽关键**——Mac 上 Nanite 集成要重点关注这个
- **Cluster 切分是真正的工程难点**——比 BVH 构建、HZB 构造都难

---

## 面试谈资准备

如果被问到这篇论文，我会这样说：

> **30 秒版本：**
> Nanite 解决的是"实时渲染十亿级多边形"问题，核心是 4 件事：① 离线切 Cluster 树（128-tri coherent）；② GPU 做 HZB 裁剪；③ Visibility Buffer 替代 G-Buffer（省 5-8x 带宽）；④ 材质 Bin 调度（5.4 减少 80% 空调度）。最终实现 UE5 "0 LOD pop、无距离衰减"——Lumen / Substrate 全都走这条范式。
>
> **2 分钟版本（按追问链）：**
>
> **Q1: 为什么用 Cluster 切分而不是传统 Meshlet？**
> → Meshlet（NVIDIA Mesh Shading）是 GPU primitive pipeline 的最小单元，**Nanite Cluster 跟 Meshlet 不是同一层概念**。Nanite Cluster = "BHV 节点 + 128-tri + 邻接 + LOD 兼容"，Meshlet = "SIMD-coherent 三角形组"。**Nanite Cluster 比 Meshlet 多 LOD 元数据**，所以可以做"运行时 GPU 选 LOD"。
>
> **Q2: Visibility Buffer 比 G-Buffer 强在哪？**
> → G-Buffer 5-8 个 MRT (Albedo / Normal / Roughness / Metallic / Emissive / Depth) → 5-8x 带宽。Visibility Buffer 1 个 32-bit (PrimID + TriID + Barycentric) → material shading 阶段从 VS 重新计算 attribute。**省 5-8x 带宽**（Mac / mobile 关键）+ **micro-triangle 友好**（避免 quad overdraw）。
>
> **Q3: 5.0 时期 90% 浪费怎么来的？**
> → UE 5.0 时期材质管线"每种材质 1 个全屏 draw call"——City Sample 4015 个 shading bin 中 3675 个是空的（90% 浪费，因为有些 bin 三角形数极少）。5.4+ Compute Shader + Bin 合并算法把空调度降低 80%。**5.0 → 5.4 升级**场景如果材质多样性 > 1000，自动 2x+ 性能提升。
>
> **Q4: HZB 怎么工作？**
> → 从上一帧 depth 构造 mip chain（5x5 downsample × log2 层）。本帧做 conservative occlusion query——若 cluster 在屏幕投影后被 HZB 中更近的 depth 遮挡，剔除。**实际开销 < 0.1ms**，是 Nanite 性能的核心优化。
>
> **Q5: Mac 上跑 Nanite 有什么坑？**
> → ① Metal RHI 5.0 之前没有硬件光栅的 wave intrinsics，**Software Raster 路径必须支持**（Karis 自己说 SW 路径处理 50-80% micro-triangle）。② 带宽敏感 → **优先选 Visibility Buffer 路径**。③ 5.4 之前的版本材质 bin 调度浪费严重 → 升级 5.4+。

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] 已复现代码 → 链接到 [[../../../03-Shader与特效案例集]]
- [ ] 已写博客 → 链接
- [ ] 已分享/交流
- [ ] 已进 day-job RAG 索引（待确认 JSONL 格式）
- [x] 已配套 QA 卡牌 → [[Karis-2021-Nanite-Virtualized-Geometry|Nanite 卡牌 HTML]]（同目录）

---

*Create date: 2026-07-15*  
*Last modified: 2026-07-15*
