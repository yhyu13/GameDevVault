---
tags: [routine/AI-tasks, topic/VGM, day/Friday]
aliases: []
---

# 周五：AI 任务清单 — VGM 轻量复盘与整理

> **人类目标**：整理本周 VGM 学习笔记，更新知识库，规划下周。  
> **AI 任务**：生成测验、建议链接、总结数据，绝不替你思考。

---

## 任务 1：VGM 知识测验生成（AI 执行）

**AI 输出**：结构化测验

```markdown
## Q1 (TF)
Mesh Shader 完全取代了 Vertex Shader 和 Fragment Shader。
Answer: False
Explanation: Mesh Shader 取代了 Vertex Shader 和 Geometry Shader 的部分功能，但 Fragment Shader 仍然保留。

## Q2 (SC)
在 GPU-Driven 管线中，哪个阶段负责可见性剔除？
Options:
- A. Mesh Shader
- B. Task Shader
- C. Fragment Shader
- D. Compute Shader
Answer: B

## Q3 (MC)
以下哪些是 Mesh Shader 相比传统管线的优势？
Options:
- A. 更少的 CPU 开销
- B. 可编程的三角形生成
- C. 更好的 GPU 利用率
- D. 支持所有旧 GPU
- E. 更简单的调试
Answer: A, B, C

## Q4 (FB)
NVidia 推荐的 Meshlet 大小是 ______ 个顶点和 ______ 个三角形。
Answer: 64, 128
```

**然后**：使用 `quiz-html-generator` 转 HTML。

**你必须做**：完成测验，复习错题。

---

## 任务 2：笔记链接建议（AI 执行，你确认）

**AI 建议**：
- [[VGM-MeshShader]] → [[Nanite-ClusterLOD]]：两者都是虚拟几何方案，对比学习
- [[VGM-GPUDriven]] → [[Lumen-GI]]：GPU-Driven 渲染与 GI 的协同
- [[VGM-Meshlet工具]] → [[C++-内存布局]]：Meshlet 数据结构的 cache 优化
- [[VGM-TaskShader]] → [[Shader-计算着色器]]：Task Shader 与 Compute Shader 的职责对比

**你必须做**：检查合理性，手动添加链接。

---

## 任务 3：下周规划（AI 执行，你补充）

**AI 建议**：
- 周一：Mesh Shader 在自研引擎中的集成方案
- 周二：写一个完整的 Meshlet 渲染 Demo（多 Meshlet、Task Shader 剔除）
- 周三：对比观察 Nanite vs Mesh Shader 的游戏表现
- 周四：性能优化（subgroup、memory coalescing）
- 周末：mini-VGM 渲染器（Meshlet + GPU-Driven + 简单材质）

**你必须做**：根据实际工作负荷调整。

---

## 完成检查清单

- [ ] VGM 知识测验已完成（得分 ≥80）
- [ ] 错题已复习
- [ ] 笔记链接已手动添加
- [ ] 下周计划已写入 Obsidian 周模板

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 1 小时*
