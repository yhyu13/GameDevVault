---
tags: [routine/AI-tasks, topic/Nanite, day/Friday]
aliases: []
---

# 周五：AI 任务清单 — Nanite 轻量复盘与整理

> **人类目标**：整理本周 Nanite 学习笔记，更新知识库，规划下周。  
> **AI 任务**：生成测验、建议链接、总结数据，绝不替你思考。

---

## 任务 1：Nanite 知识测验生成（AI 执行）

**输入**：你本周的 Nanite 笔记

**AI 输出**：结构化测验内容：

```markdown
## Q1 (TF)
Nanite 的 Cluster 合并只考虑几何误差，不考虑材质属性。
Answer: False
Explanation: Nanite 的合并需保证材质一致性，不同材质的三角形不能合并到同一 Cluster。

## Q2 (SC)
Nanite 渲染管线的核心特点是？
Options:
- A. CPU 逐物体提交 Draw Call
- B. GPU 自主决定绘制哪些 Cluster
- C. 预计算所有 LOD 级别并存储
- D. 使用 Tessellation 动态细分
Answer: B

## Q3 (MC)
以下哪些是 Nanite 目前的限制？
Options:
- A. 不支持动态骨骼动画
- B. 不支持透明材质
- C. 不支持非流形网格
- D. 不支持多光源
- E. 不支持小物体（< 2000 triangles）
Answer: A, B, C, E

## Q4 (FB)
Nanite 使用 ______ 作为渲染目标来存储每个像素对应的 ______，从而实现延迟着色。
Answer: Visibility Buffer, primitive ID and barycentrics
```

**然后**：使用 `quiz-html-generator` skill 转 HTML 测验。

**你必须做**：亲自完成测验，记录得分，复习错题。

---

## 任务 2：笔记链接建议（AI 执行，你确认）

**AI 建议**：
- [[Nanite-论文笔记]] → [[Lumen-论文笔记]]：两者在 UE5 中协同工作
- [[Nanite-源码分析]] → [[UE5-VT-显存调度]]：Nanite 的虚拟几何流送与 VT 类似
- [[Nanite-Cluster构建]] → [[C++-内存布局]]：Cluster 结构的 cache 优化
- [[Nanite-VisibilityBuffer]] → [[Shader-后处理]]：VB 的解码与 shading 阶段

**你必须做**：检查合理性，手动添加 `[[链接]]`。

---

## 任务 3：周数据总结 + 下周规划（AI 执行，你补充）

**AI 建议下周重点**：
- 周一：Mesh Shader（DirectX 12 Ultimate）对比 Nanite
- 周二：GPU-Driven 渲染的 Indirect Draw 实践
- 周三：观察非 UE5 游戏的 LOD 方案（对比学习）
- 周四：写 Nanite 风格的 Cluster 构建器（完整版）
- 周末：mini-Nanite Demo（简化版，只支持静态 Mesh）

**你必须做**：根据实际工作负荷调整。

---

## 完成检查清单

- [ ] Nanite 知识测验已完成（得分 ≥80）
- [ ] 错题已复习，薄弱点已标记
- [ ] 笔记双向链接已手动添加
- [ ] 下周计划已调整并写入 Obsidian 周模板

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 1 小时*
