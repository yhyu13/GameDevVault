---
tags: [routine/AI-tasks, topic/Nanite, day/Monday]
aliases: []
---

# 周一：AI 任务清单 — Nanite 前沿技术输入

> **人类目标**：精读 Nanite 论文/演讲，理解虚拟几何化的核心创新，准备面试谈资。  
> **AI 任务**：提供脚手架、解释障碍、生成问题，绝不替读论文。

---

## 任务 1：论文预读引导（AI 执行）

**输入**：Nanite 论文或演讲（《A Deep Dive into Nanite Virtualized Geometry》或 GDC 2021 演讲）

**AI 输出**：
1. 一段 **150 字摘要**（核心问题 + 方法 + 结果）
2. **3 个引导问题**用于精读时回答：
   - Q1: Nanite 的 Cluster 和 Cluster Group 层级结构是如何解决 LOD 切换的？
   - Q2: Visibility Buffer 与 Deferred Shading 的权衡是什么？
   - Q3: Nanite 如何处理动态物体？是否支持骨骼动画？
3. **重点章节标记**：先读 Section 4 (Cluster Hierarchy)，再读 Section 5 (GPU-Driven Pipeline)，最后读 Section 6 (Streaming)

**交付物**：`Nanite-Reading-Guide.md`（AI 生成，你打印或分屏对照）

---

## 任务 2：Cluster LOD 算法解释（AI 执行，你验证）

**输入**：论文中关于 Cluster Group 合并/拆分的算法描述

**AI 输出**：
1. 每个步骤的伪代码（Cluster 构建 → Group 形成 → Parent 生成）
2. 误差度量（Screen-space Error）如何计算
3. 为什么 Nanite 的 LOD 是**无级**的（区别于传统离散的 LOD0/1/2）

**你必须做**：用 Python 或 C++ 写一个简化版 Cluster 构建器，验证理解。

---

## 任务 3：面试谈资生成（AI 执行，你 rehearse）

**输入**：你的 Nanite 精读笔记（核心创新点 + 实现难点 + 个人评价）

**AI 输出**：
1. **30 秒版本**：1 句话问题 + 1 句话方法 + 1 句话结果
2. **2 分钟版本**：背景 → Cluster LOD 详解 → GPU-Driven 渲染 → 与 Lumen 的联动 → 局限
3. **3 个可能的追问及建议回答**：
   - "Nanite 和传统的 LOD 有什么区别？"
   - "Visibility Buffer 的优缺点？"
   - "Nanite 在开放世界中的流送策略？"

**你必须做**：对着镜子大声说 3 遍，计时。

---

## 任务 4：源码地图绘制（AI 执行，你验证）

**输入**："Nanite 的渲染管线入口在哪？从 RenderThread 到 GPU 的完整调用链？"

**AI 输出**：
1. 从 `FSceneRenderer::RenderNanite()` 到 `Nanite::Rasterize` 的调用链
2. 关键文件：`NaniteRender.cpp`, `ClusterCulling.cpp`, `VisibilityBuffer.cpp`
3. 每步的一句话职责说明

**你必须做**：在 UE5 工程中打开这些文件，用 debugger 或 IDE 的 Call Hierarchy 验证。修正 AI 的幻觉。

---

## 今日 AI 禁区

- ❌ 让 AI 直接读论文并告诉你 "这篇论文讲了什么"
- ❌ 让 AI 替你写论文笔记（Obsidian 中的笔记必须是你自己的话）
- ❌ 让 AI 生成完整代码路径而不验证（AI 会编造函数名）
- ❌ 让 AI 替你准备面试回答而不自己 rehearse

---

## 完成检查清单

- [ ] AI 阅读指南已生成并打印
- [ ] Cluster LOD 算法已手动验证（简化代码）
- [ ] 面试谈资已 rehearse aloud
- [ ] 源码路径已用 debugger 验证
- [ ] 所有内容已写入 Obsidian 笔记（你写的，不是 AI 写的）

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2 小时*  
*产出：1 篇论文笔记 + 1 篇源码分析 + 面试谈资 ready*
