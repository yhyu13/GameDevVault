---
tags: [routine/master-index, topic/MassAI, topic/LearningAgents, system/reference]
aliases: [MassAI-AI-Master]
---

# MassAI & Learning Agents 主题 — AI 任务总览

> 这是 MassAI / Learning Agents 学习周期的「AI 任务控制塔」。  
> **核心原则**：AI 只做脚手架，你来做硬工作。

---

## 快速导航

| 日期 | 主题 | AI 任务文件 | 人类核心任务 |
|------|------|------------|-------------|
| [[周一]] | 前沿技术输入 | [[01_Monday/AI-Tasks]] | 精读 ECS 论文 + MassEntity 源码追踪 |
| [[周二]] | 专项技能突破 | [[02_Tuesday/AI-Tasks]] | ECS 概念练习 + Fragment/Processor 代码 |
| [[周三]] | 强制休息/游玩 | [[03_Wednesday/AI-Tasks]] | 观察大型 AI 游戏（Fortnite、City Sample） |
| [[周四]] | 工程化与工具链 | [[04_Thursday/AI-Tasks]] | MassEntity 数据结构 + 工具脚本 |
| [[周五]] | 轻量复盘 | [[05_Friday/AI-Tasks]] | 测验 + 整理 + 规划 |
| [[周末]] | 项目实战 | [[06_Weekend/AI-Tasks]] | 自定义 Processor + StateTree 行为 |
| [[周日]] | 项目收尾 | [[07_Sunday/AI-Tasks]] | 集成测试 + 性能基准 + 复盘 |
| [[每周]] | 外部接触 | [[08_Weekly/AI-Tasks]] | AI 社区社交 + 开源贡献 |

---

## MassAI 是什么

MassAI（Mass Entity AI）是 UE5.8 的 **Data-Oriented ECS 框架**，用于驱动数千个 AI Agent 的高性能模拟，取代传统的 Actor-Based AI：

- **MassEntity**：核心 ECS 框架（Entity = ID, Fragment = 数据, Processor = 逻辑）
- **MassAI**：AI 行为层（LOD AI、Behavior States、Spatial Hashing）
- **MassGameplay**：Gameplay 集成（与 Gameplay Ability System、Pawn 的桥接）
- **MassSpawner**：基于 PCG 的大规模生成系统
- **SmartObjects**：可交互对象（椅子、门、工作台），AI 通过 SO 查询发现可用交互
- **StateTree**：分层状态机（Hierarchical State Machine），融合 Behavior Tree + State Machine
- **LearningAgents**：UE5 内置的 RL（Reinforcement Learning）训练框架，在引擎内直接训练 AI Agent
- **核心模块**：
  - `MassEntity` — ECS 核心（Entity、Fragment、Processor、Query）
  - `MassAI` — AI 行为与 LOD
  - `MassGameplay` — Gameplay 桥接
  - `MassSpawner` — 基于 PCG 的生成
  - `SmartObjects` — 交互对象系统
  - `StateTree` — 状态树
  - `LearningAgents` — 强化学习
- **使用场景**：
  - 城市人群（City Sample 中的数千行人）
  - 野生动物模拟（鸟群、鱼群）
  - 战场 AI（大量士兵、载具）
  - 环境生活（Ambient Life）

---

## 与现有 8 个主题的关系

```
        ┌─────────────────────────────────────────────┐
        │         MassAI & Learning Agents (#9)       │
        │    大规模实体 AI / 强化学习 / 智能对象          │
        │    (横切关注点——需要渲染、物理、生成支撑)        │
        └─────────────────────────────────────────────┘
                      │
    ┌─────────┬───────┼───────┬─────────┐
    ▼         ▼       ▼       ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Lumen  │ │ Nanite │ │  VGM   │ │  VSM   │ │ Chaos  │
│ (#1)   │ │ (#2)   │ │ (#3)   │ │ (#4)   │ │ (#5)   │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
┌────────────────┐    ┌────────────────┐    ┌────────────────┐
│ WaterPlugins   │    │   UnrealMCP    │    │ NeuralRendering│
│    (#6)      │    │    (#7)        │    │    (#8)        │
└────────────────┘    └────────────────┘    └────────────────┘
```

MassAI 是 **消费者** 而非 **独立系统**：
- **Chaos** (#5)：MassAI Agent 的物理碰撞、布娃娃、载具交互
- **VGM** (#3)：MassAI 的渲染LOD（Virtualized Geometry 处理大量 Instance）
- **VSM** (#4)：MassAI 的阴影（Virtual Shadow Maps 支持大量移动 Agent）
- **Lumen** (#1)：MassAI 的 GI（Ambient Life 的间接光照）
- **UnrealMCP** (#7)：AI 助手通过 MCP 查询 MassEntity 世界状态
- **NeuralRendering** (#8)：Neural Rendering 可为 MassAI 生成逼真的 Agent 外观
- **PCG** (#3/相关)：MassSpawner 使用 PCG 生成城市人群分布

---

## 相关参考

- [[../References/AI-Augmentation-Reference]] — AI 辅助学习完整参考手册
- [[../UE58-Topic-Exploration-Report]] — UE58 主题探索完整报告（优先级评分）
- [[../01-AI-GameDev-Resources/00-AI-GameDev-Resource-Index]] — AI 游戏开发资源总索引（2026-06 刷新）
- [[../ChaosPhysics/00-Master-Index]] — MassAI 的物理基础
- [[../VGM/00-Master-Index]] — MassAI 的渲染基础
- [[../../01-论文笔记库]] — ECS / Data-Oriented Design 论文笔记
- [[../../02-引擎源码分析库]] — MassEntity 源码分析
- [[../../99-Templates/论文笔记]] — 论文/规范笔记模板
- **官方参考**：
  - Epic 官方文档：Mass Entity System Overview
  - City Sample 工程（UE5 官方示例）
  - StateTree Plugin 文档
  - LearningAgents Plugin 文档

---

## 每周更新日志

| 周 | 主题 | 状态 |
|----|------|------|
| W1 | MassEntity 基础：Fragment / Processor / Entity Query | 🔄 进行中 |
| W2 | SmartObjects + StateTree：交互对象与状态机 | ☐ 待开始 |
| W3 | LearningAgents：RL 训练、Observation / Action / Reward | ☐ 待开始 |
| W4 | 集成实战：完整 MassAI 系统（Crowd + SO + StateTree + RL）| ☐ 待开始 |

---

## 推荐学习路径

**如果你同时学多个主题**：
- **并行**：MassAI 作为 "主线"，每天 1-2 小时，周末集中写 Processor + StateTree
- **串行**：先完成一个渲染主题（如 VGM），理解 LOD 后再学 MassAI 的 AI LOD

**MassAI 的特殊性**：
- 需要 **Data-Oriented Design** 思维（与传统 OOP 的 Actor 完全不同）
- 需要 **C++ 源码阅读**（蓝图支持有限，核心逻辑在 C++）
- 更像 **系统编程 + 架构设计**（而非单纯算法）
- 学习曲线：陡峭（ECS 思维转换需要时间）

---

*This is a living document. Update it as the MassAI topic progresses.*
