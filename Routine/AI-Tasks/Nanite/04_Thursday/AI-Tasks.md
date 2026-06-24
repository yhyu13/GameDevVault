---
tags: [routine/AI-tasks, topic/Nanite, day/Thursday]
aliases: []
---

# 周四：AI 任务清单 — Nanite 工程化与工具链

> **人类目标**：理解 Nanite 的底层工程实现（GPU-Driven、流送、内存池），为自研引擎做准备。  
> **AI 任务**：生成工具脚本、解释概念、review 架构，绝不替你做核心设计。

---

## 任务 1：Mesh 分析工具生成（AI 执行，你 review）

**输入**："写一个 Python 脚本，分析一个 Mesh 的 triangle 数量、边界框大小、是否适合 Nanite 化（closed mesh、无透明材质）"

**AI 输出**：完整的 Python 脚本（使用 trimesh 或 assimp）

**你必须做**：
1. 逐行阅读代码，确保理解每个函数
2. 检查引擎特定假设
3. 添加你自己的需求（如检查材质类型、骨骼权重）
4. 运行并验证输出

---

## 任务 2：GPU-Driven Rendering 概念解释（AI 执行，你实践）

**输入**："Nanite 的 GPU-Driven Pipeline 中，ExecuteIndirect 是如何工作的？"

**AI 输出**：
1. 概念解释：CPU 只提交一个 command buffer，GPU 自己生成 draw calls
2. 与传统 CPU culling 的区别
3. UE5 源码中的具体实现：`ExecuteIndirect` 调用点

**你必须做**：写一个小型 DX12/Vulkan 示例，验证 `ExecuteIndirect` 或 `MultiDrawIndirect`。

---

## 任务 3：Nanite 架构 Review（AI 执行，你决策）

**AI 审查清单**：
- [ ] 是否支持动态加载/卸载 Cluster？
- [ ] 内存池是否可动态扩容？
- [ ] 如何处理非 Nanite 物体的混合渲染？
- [ ] 阴影管线是否也走 Nanite？
- [ ] 平台兼容性（PC/Console/Mobile fallback）？

**你必须做**：评估每个建议，记录决策。

---

## 任务 4：Cluster 内存布局分析（AI 计算，你验证）

**输入**：Nanite 的 `FCluster` 结构体定义

**AI 输出**：字段大小、padding、Cache Line 分析、重排序建议

**你必须做**：用 `sizeof()` 和 `offsetof()` 验证。

---

## 今日 AI 禁区

- ❌ 让 AI 替你设计虚拟几何架构
- ❌ 直接运行 AI 生成的脚本而不 review
- ❌ 让 AI 解释概念后你不写代码实践

---

## 完成检查清单

- [ ] 工具脚本已 review、修改、运行验证
- [ ] GPU-Driven 概念已用迷你代码实践
- [ ] 架构审查报告已阅读，决策已记录
- [ ] 内存布局分析已用 `sizeof()` 验证
- [ ] 所有代码和文档已写入 Obsidian

---

*AI 执行时间：约 25 分钟*  
*人类执行时间：约 2 小时*  
*产出：1 个工具脚本 + 1 个 C++ 实践 + 1 份架构审查 + 1 次内存分析*
