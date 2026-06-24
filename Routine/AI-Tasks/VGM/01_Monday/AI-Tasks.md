---
tags: [routine/AI-tasks, topic/VGM, day/Monday]
aliases: []
---

# 周一：AI 任务清单 — VGM 前沿技术输入

> **人类目标**：精读 VGM（Virtual Geometry & Mesh）相关论文/演讲，理解 Mesh Shader、Meshlet 和 GPU-Driven 管线的核心创新。  
> **AI 任务**：提供脚手架、解释障碍、生成问题，绝不替读论文。

---

## 任务 1：论文预读引导（AI 执行）

**输入**：VGM 相关论文（如《Mesh Shaders and the Future of Geometry Processing》或《Meshlet-Based Rendering》）

**AI 输出**：
1. 一段 **150 字摘要**（核心问题 + 方法 + 结果）
2. **3 个引导问题**：
   - Q1: Mesh Shader 与传统 Vertex Shader + Tessellation 的管线区别是什么？
   - Q2: Meshlet 的划分策略（如 NVidia 的 64-vertex / 128-primitive 标准）如何影响性能？
   - Q3: GPU-Driven 管线中，Task Shader 和 Mesh Shader 的职责分工？
3. **重点章节标记**：先读 Mesh Shader 管线概述，再读 Task Shader Culling，最后读 Performance Analysis

**交付物**：`VGM-Reading-Guide.md`

---

## 任务 2：Mesh Shader 管线概念解释（AI 执行，你验证）

**输入**：论文中 Mesh Shader 管线图或伪代码

**AI 输出**：
1. 传统管线 vs Mesh Shader 管线的对比图（文字版）
2. 每个阶段的数据流：Task Shader → Mesh Shader → Fragment Shader
3. 为什么 Mesh Shader 比传统管线更适合 GPU-Driven 渲染？

**你必须做**：画一张自己的管线对比图（手绘或 digital），确认理解。

---

## 任务 3：面试谈资生成（AI 执行，你 rehearse）

**AI 输出**：
1. **30 秒版本**：Mesh Shader 是新一代 GPU 几何管线，用 Task Shader 做剔除、Mesh Shader 生成三角形，相比传统管线的优势是...
2. **2 分钟版本**：背景 → 传统管线瓶颈 → Mesh Shader 解决方案 → Task Shader 剔除 → 与 Nanite 的对比 → 局限（硬件要求）
3. **3 个追问**：
   - "Mesh Shader 和 Compute Shader 做几何生成有什么区别？"
   - "Task Shader 的 Work Group 大小怎么选？"
   - "Mesh Shader 在 Mobile 上的前景如何？"

**你必须做**：rehearse aloud。

---

## 任务 4：源码地图绘制（AI 执行，你验证）

**输入**："Vulkan/DirectX 12 中 Mesh Shader 的 API 入口在哪？给一个最小可运行的调用链"

**AI 输出**：
1. Vulkan: `vkCmdDrawMeshTasksEXT` 调用链
2. DirectX 12: `DispatchMesh` 调用链
3. 关键文件/函数名（如 `D3D12MeshShader` 或 Vulkan Extension 示例）

**你必须做**：在 SDK 示例或引擎源码中验证这些入口点。

---

## 今日 AI 禁区

- ❌ 让 AI 替读论文
- ❌ 让 AI 替写笔记
- ❌ 让 AI 生成代码路径不验证
- ❌ 让 AI 替准备面试回答

---

## 完成检查清单

- [ ] AI 阅读指南已生成并打印
- [ ] Mesh Shader 管线概念已手绘验证
- [ ] 面试谈资已 rehearse aloud
- [ ] 源码路径已验证
- [ ] 所有内容已写入 Obsidian 笔记

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2 小时*
