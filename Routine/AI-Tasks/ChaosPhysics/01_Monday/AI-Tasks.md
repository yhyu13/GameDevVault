---
tags: [routine/AI-tasks, topic/ChaosPhysics, day/Monday]
aliases: []
---

# 周一：AI 任务清单 — Chaos Physics 前沿技术输入

> **人类目标**：精读 Chaos Physics 相关论文/演讲，理解 UE5 物理引擎的核心架构。  
> **AI 任务**：提供脚手架、解释障碍、生成问题，绝不替读论文。

---

## 任务 1：论文预读引导（AI 执行）

**输入**：Chaos Physics 相关论文（如 GDC 2020 《Chaos: Physics for Modern Games》）或 PhysX 对比文档

**AI 输出**：
1. 一段 **150 字摘要**
2. **3 个引导问题**：
   - Q1: Chaos 的刚体求解器（Rigid Body Solver）相比 PhysX 的改进点？
   - Q2: 破坏系统（Destruction）中，Geometry Collection 的数据结构是怎样的？
   - Q3: Chaos 的约束求解器（Constraint Solver）使用 PGS 还是更现代的算法？
3. **重点章节标记**：先读 Architecture Overview，再读 Destruction System，最后读 Solver Details

**交付物**：`Chaos-Reading-Guide.md`

---

## 任务 2：刚体动力学概念解释（AI 执行，你验证）

**输入**：Chaos 的刚体模拟管线描述

**AI 输出**：
1. 刚体状态（position, orientation, velocity, angular velocity）的更新流程
2. 约束求解（contact constraints, joint constraints）的迭代过程
3. 时间积分：Semi-implicit Euler vs Runge-Kutta 的取舍

**你必须做**：手写一个简化版 2D 刚体求解器（Python 或 C++），验证理解。

---

## 任务 3：面试谈资生成（AI 执行，你 rehearse）

**AI 输出**：
1. **30 秒版本**：Chaos 是 UE5 的新一代物理引擎，支持大规模刚体模拟和电影级破坏效果，核心创新是...
2. **2 分钟版本**：背景 → PhysX 局限 → Chaos 架构 → Geometry Collection → 约束求解 → 与 Niagara 的协同
3. **3 个追问**：
   - "Chaos 和 PhysX 的架构差异？"
   - "Geometry Collection 的内存布局？"
   - "Chaos 的确定性如何保证？"

**你必须做**：rehearse aloud。

---

## 任务 4：源码地图绘制（AI 执行，你验证）

**输入**："Chaos 的物理模拟入口在哪？从 GameThread 到 Physics Thread 的完整调用链？"

**AI 输出**：
1. `FChaosSolversModule::CreateSolver()` 调用链
2. 关键文件：`ChaosSolver.cpp`, `PBDRigidsSolver.cpp`, `GeometryCollection.cpp`
3. GameThread 与 Physics Thread 的同步机制

**你必须做**：在 UE5 源码中验证。

---

## 今日 AI 禁区

- ❌ 让 AI 替读论文
- ❌ 让 AI 替写笔记
- ❌ 让 AI 生成代码路径不验证
- ❌ 让 AI 替准备面试回答

---

## 完成检查清单

- [ ] AI 阅读指南已生成并打印
- [ ] 刚体动力学概念已手写代码验证
- [ ] 面试谈资已 rehearse aloud
- [ ] 源码路径已验证
- [ ] 所有内容已写入 Obsidian 笔记

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2 小时*
