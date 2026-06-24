---
tags: [routine/AI-tasks, topic/ChaosPhysics, day/Friday]
aliases: []
---

# 周五：AI 任务清单 — Chaos Physics 轻量复盘与整理

> **人类目标**：整理本周 Chaos 学习笔记，更新知识库，规划下周。  
> **AI 任务**：生成测验、建议链接、总结数据，绝不替你思考。

---

## 任务 1：Chaos Physics 知识测验生成（AI 执行）

**AI 输出**：结构化测验

```markdown
## Q1 (TF)
Chaos 的约束求解器使用的是纯 Jacobi 迭代法。
Answer: False
Explanation: Chaos 使用改进的 Gauss-Seidel（PGS）或其变体，允许一定程度的并行化，但不是纯 Jacobi。

## Q2 (SC)
Geometry Collection 在破坏时，碎片之间的连接关系由什么数据结构维护？
Options:
- A. 简单的刚体数组
- B. 隐式图（Implicit Graph）
- C. 显式树（Explicit Tree）
- D. BVH
Answer: B

## Q3 (MC)
以下哪些是 Chaos 相比 PhysX 的优势？
Options:
- A. 内置破坏系统（Geometry Collection）
- B. 大规模刚体并行求解
- C. 源码完全开源可见
- D. 支持所有平台（包括低端 Mobile）
- E. 更现代的约束求解算法
Answer: A, B, C, E

## Q4 (FB)
在刚体模拟中，______ 积分法先更新 ______ 再更新位置，这是游戏物理引擎中最常用的方法。
Answer: Semi-implicit Euler, velocity
```

**然后**：使用 `quiz-html-generator` 转 HTML。

**你必须做**：完成测验，复习错题。

---

## 任务 2：笔记链接建议（AI 执行，你确认）

**AI 建议**：
- [[Chaos-论文笔记]] → [[Lumen-论文笔记]]：物理破坏与光照的交互（碎片的光照更新）
- [[Chaos-刚体求解]] → [[C++-多线程]]：物理求解器的 Job System 并行化
- [[Chaos-GeometryCollection]] → [[03-Shader与特效案例集]]：破坏特效的粒子渲染
- [[Chaos-ECS集成]] → [[02-引擎源码分析库]]：Mass Entity 系统的源码分析

**你必须做**：检查合理性，手动添加链接。

---

## 任务 3：下周规划（AI 执行，你补充）

**AI 建议**：
- 周一：Chaos Cloth / 布料模拟原理
- 周二：写一个简单的布料模拟（Verlet 积分 + 约束）
- 周三：观察游戏中布料和毛发的物理表现
- 周四：物理工具链（自动化物理测试、回放系统）
- 周末：mini-Physics 引擎（刚体 + 碰撞 + 简单破坏）

**你必须做**：根据实际工作负荷调整。

---

## 完成检查清单

- [ ] Chaos 知识测验已完成（得分 ≥80）
- [ ] 错题已复习
- [ ] 笔记链接已手动添加
- [ ] 下周计划已写入 Obsidian 周模板

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 1 小时*
