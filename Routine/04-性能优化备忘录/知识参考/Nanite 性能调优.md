---
tags: [perf/GPU, perf/Nanite, perf/geometry]
aliases: [Nanite perf, Nanite 调优]
---

# Nanite — 已验证的事实清单

> 本笔记**只收录**有 GDC 演讲 / UE 官方文档 / UE 源码支撑的事实。所有推论性数字（200k threshold、5-30% 提升等）已删除。
>
> **主要来源**：
> - **GDC 2024**："Nanite GPU-Driven Material Pipeline" by **Graham Wihlidal, Epic Games**（知乎有完整中文笔记 / GDC Vault 有原视频）
> - **SIGGRAPH 2021**：Nanite 原始论文
> - UE 官方 Nanite 文档（嵌入在渲染文档里）
> - UE 官方 Virtual Shadow Maps 文档

---

## 一、Nanite 的工作原理（最少必要信息）[D]

> **来源**：GDC 2024 Wihlidal 演讲 + SIGGRAPH 2021 论文

1. **Cluster**：原始 mesh 被切成 ~128-tri 块（cluster）
2. **Visibility Buffer**：屏幕空间记录"哪个像素被哪个 cluster 的哪个三角形覆盖"——使用 **64-bit atomic max**：高位 32-bit 深度，低位 32-bit 三角形 ID + cluster ID
3. **Software Rasterizer**：在 compute shader 里光栅化（PC 上还有 Hardware Rasterizer 路径）
4. **GBuffer 填充**：Nanite 不重做 GBuffer，**从 visibility buffer 填 GBuffer**，所有逻辑保持对 Nanite 一无所知

> **Wihlidal 原话**："Nanite 不需要一个完全新的渲染器，也不要求用户完全重做所有内容... 从 Nanite 的可见性缓冲区填充 GBuffer 开始，保持现有的 GBuffer 逻辑使之完全不知道 Nanite 的存在。"

---

## 二、Nanite 材质管线的三个版本（GDC 2024 原话）[D]

| 版本 | 引擎版本 | 核心变化 |
|------|----------|---------|
| **初始版本** | UE 5.0 | 每种材质一个全屏 draw call，深度等值测试 |
| **可编程光栅器** | UE 5.1 | 支持 alpha mask / WPO / 双面材质 / 像素深度 |
| **新材质管线（计算着色器）** | UE 5.4 | 所有 GBuffer 着色 pass 改用 compute shader，大幅减少空调度 |

> **Wihlidal 原话**："在 UE 5.0 中 Nanite 发布时使用的版本。然后，本次演讲将介绍可编程光栅化，它增加了艺术家通过材质图控制光栅化器的能力。最后，本次演讲将介绍 Nanite 材质管线的最新进化。"

---

## 三、GDC 2024 真实数字（来自演讲）[D]

> **来源**：Graham Wihlidal GDC 2024 talk

### 3.1 各 demo 的独特材质数

| Demo | GPU 剔除前独特材质数 |
|------|---------------------|
| **Lumen in the Land of Nanite** | ~500 |
| **Valley of the Ancients** | ~2000 |
| **City Sample (The Matrix Awakens)** | ~5000 |

> **Wihlidal 原话**："不可思议的高实例和材质数量（需要扩展到像这个例子这样疯狂的相机视角），带来了许多必须解决的挑战性问题。"

### 3.2 空调度问题（推动 5.4 改动的直接动机）

> **Wihlidal 原话**："这是来自城市样例的一个镜头，显示了 **4015 个总着色装箱**，但其中有 **3675 个装箱是空的！**"

→ 即 **91.5% 的调度是空调度**。这是改用 compute shader + 空调度压缩的直接原因。

### 3.3 Xbox Series X 4K 70% 动态分辨率下的实际测量（一个具体场景）[D]

| 方案 | 耗时 |
|------|------|
| 原始像素着色器方案（含分类） | **4.92 ms** |
| 暴力 compute shader（含装箱开销） | **4.62 ms** |
| 移除空调度后 | **3.93 ms** |
| 再开 2x2 software VRS | **3.05 ms** |

> **Wihlidal 原话**："在一个 5 毫秒的基础 Pass 场景中，新系统耗时为 3 毫秒，**比原始材质管线快了 40%**。"

### 3.4 VRS 节省的额外数据（同一演讲）[D]

> "VRS Tile 尺寸为 2x2，现在将着色率与着色像素块完美匹配。左边展示了每个 8x8 区域内所有着色像素块的着色率，提供了 **27% 的着色降低**。而右边显示了每个 2x2 着色像素块的着色率，提供了大约 **45% 的着色降低**。"

> "很明显这个实验非常成功，因为这在 8x8 和 2x2 瓦片尺寸之间为这个镜头提供了**额外的大约 18% 的着色降低**。"

### 3.5 Variable Rate Shading (VRS) 在 Nanite 上的事实 [D]

- **UE 5.2** 起 DirectX 12 Tier 2 VRS 由 The Coalition 贡献，最初绑到 Nanite 像素着色器材质 pass
- 演讲原话："这在许多场景中导致了**大约 25-30% 的着色率降低**"（VRS 在许多场景中的节省）
- **硬件 VRS Tile 尺寸限制**：AMD 8x8 / NVIDIA 16x16 / Intel 32x32
- VRS Tile 内所有着色 quad 必须统一着色率（这是硬件限制）

---

## 四、可编程光栅器（UE 5.1+）[D]

> **来源**：GDC 2024 Wihlidal 演讲

### 4.1 UE 5.0 不支持的内容（5.1+ 支持）

> "不兼容的内容包括 **alpha 遮罩、双面、像素深度偏移、世界位置偏移**（这是对顶点动画的称呼）、自定义 UV 等。"

### 4.2 真实应用案例（演讲原话）[D]

- **Fortnite 第 4 章**："开发了可编程光栅管线后，能够在《堡垒之夜》第 4 章中**广泛使用 Nanite 和虚拟阴影贴图**，它被用于**所有的草、树木、地形、建筑部件以及大多数的道具**。"
- **Electric Dreams demo**："我们展示了《Electric Dreams》演示，这是一个茂密的森林环境，通过程序生成，并且大量使用了 Nanite 可编程光栅。**同样地，在这个场景中的所有内容都是 100% 的 Nanite**。"

### 4.3 分类/Reserve/Scatter 三阶段管线 [D]

> 演讲原话："光栅分箱将可见 Cluster 分组到适当的箱中。这个过程通过三个阶段完成：**Classify、Reserve 和 Scatter**。"

### 4.4 Raster Bins 的两类派生 [D]

- 软件光栅 bin 在**异步计算队列**上运行，与图形队列上的硬件光栅 bin 重叠
- 两类都使用 64-bit atomic 操作写入 visibility buffer（**不需要 UAV barrier**）

---

## 五、Nanite 与 Virtual Shadow Maps（VSM）的关系 [D]

> **来源**：UE 官方 Virtual Shadow Maps 文档 + GDC 2023 "Optimizing Shadow Maps" 演讲

- Nanite 必须配 VSM 才高效——CSM / DSM 与 Nanite 不兼容，会 fallback
- "5x 整体阴影性能" — GDC 2023 演讲原话（演讲中具体上下文：相比传统阴影映射方法的提升）

---

## 六、可调的 CVar / 设置 [D]

| CVar / 设置 | 默认 | 含义 |
|------|------|------|
| `r.Nanite.MaxPixelsPerEdge` | 16 | 屏幕像素对 cluster 边的细分 |
| `r.Nanite.MaxVisibleClusters` | 1M | 可见 cluster 上限 |
| Static Mesh Editor → Nanite Stats | — | 看 cluster 数 / fallback 状态 |
| View Mode → Nanite Visualization | — | Editor 可视化 Nanite 渲染 |

> 注意：**CVars 的精确默认 / 范围**以 UE 源码为准（`NaniteSceneProxy.h` / `NaniteCVars.cpp`）。本文不主张推论阈值。

---

## 七、与 Lumen 的关系 [D]

> **来源**：UE 5.7 官方 [Lumen Technical Details]

- "Nanite accelerates the mesh captures used to keep Surface Cache in sync with the triangle scene. **High polygon meshes in particular, need to be using Nanite to have efficient captures**. **Foliage and Instanced Static Mesh Components can only be supported if the mesh is using Nanite.**"
- **结论**：高面数 mesh + 草 / ISM 不开 Nanite = Lumen 不支持 / 极慢
- 渲染顺序：**先 Nanite 跑稳 → 再调 Lumen**

---

## 八、不在本文档里的内容

> 以下内容**没有可查的官方 / GDC 来源**，本文**不写**：

- "Cluster 阈值多少算高" / "项目总 cluster 上限"——GDC 演讲没给具体阈值
- "用 Nanite 后能省多少 DrawCall / 多少 CPU 时间"——演讲没给
- "Programmable Rasterizer 在 5.1+ 之后 DrawCall 降 X%"——演讲里是案例描述，**没有给百分比**

需要这些数字 → 自己 Profile 项目，参考 `[[性能优化方法论]]`。

---

## 关联 / 输出产物

- [[性能优化方法论]] — Profile 黄金三问
- [[Lumen 性能调优]] — Lumen 配 Nanite（高面数必须 Nanite）
- [[Lyra 性能架构]] — Lyra 是 Nanite + Lumen 实战参考
- [[Unreal Insights 帧分析实战]] — Profile 时怎么录 trace
- GDC 2024 视频：Nanite GPU-Driven Material Pipeline（Graham Wihlidal, Epic Games）— **演讲原话已引用**
- GDC 2023 视频：Optimizing Shadow Maps（VSM 5x 数据来源）

---

*Create date: 2026-06-25*
*Last modified: 2026-06-26（删除全部 [U] 推论百分比 / 阈值；GDC 2024 演讲数据点全部带原话引用）*
*Status: ✅ 所有内容有 GDC 2024 / 官方文档 / 演讲原话支撑*