---
tags: [routine/AI-tasks, topic/MassAI, topic/LearningAgents, day/Friday]
aliases: []
---

# 周五：AI 任务清单 — MassAI 轻量复盘与整理

> **人类目标**：整理本周 MassAI 学习笔记，更新知识库，规划下周。  
> **AI 任务**：生成测验、建议链接、总结数据，绝不替你思考。

---

## 任务 1：MassAI / ECS 知识测验生成（AI 执行）

**AI 输出**：结构化测验

```markdown
## Q1 (TF)
MassEntity 中的 Fragment 可以包含成员函数（Method），与 UActorComponent 类似。
Answer: False
Explanation: Fragment 是纯 POD 数据，不允许包含函数。所有逻辑必须在 Processor 中实现。这是 ECS 的核心设计：数据与逻辑分离。

## Q2 (SC)
一个 MassEntity Processor 要遍历所有同时拥有 FTransformFragment 和 FVelocityFragment 的 Entity，应该在 ConfigureQueries 中使用什么方法？
Options:
- A. EntityQuery.AddFilter<FTransformFragment>()
- B. EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly)
- C. EntityQuery.AddSharedRequirement<FTransformFragment>()
- D. EntityQuery.AddConstSharedRequirement<FTransformFragment>()
Answer: B
Explanation: AddRequirement 用于声明 Processor 需要访问的 Fragment。AddFilter 仅过滤但不提供访问。SharedRequirement 用于所有 Entity 共享的 Fragment（如 World State）。

## Q3 (MC)
以下哪些是 MassAI 系统中 SmartObject 的核心功能？
Options:
- A. 在场景中注册可交互对象（如椅子、门）
- B. 为 AI Agent 分配交互 Slot（如座位、工作台位置）
- C. 管理交互的生命周期（请求 → 占用 → 释放）
- D. 定义交互的动画（PlayMontage）
- E. 自动寻路（NavMeshPathfinding）
Answer: A, B, C
Explanation: SmartObject 负责注册、查询、分配 Slot 和管理生命周期。动画播放和寻路是其他系统（Animation Blueprint、Navigation System）的职责。

## Q4 (FB)
MassEntity 的 Archetype 系统通过 ______ 将相同 Fragment 组合的 Entity 分组，在内存中使用 ______ 布局存储，以提高 ______ 命中率。Processor 通过 ______ 声明需要访问的 Fragment，运行时只遍历匹配的 ______。
Answer: Fragment 组合签名, SOA (Structure of Arrays), Cache, EntityQuery (AddRequirement), ArchetypeChunk

## Q5 (MC)
StateTree 与 BehaviorTree 相比，以下哪些是 StateTree 的优势？
Options:
- A. 状态切换是 O(1)（直接跳转）
- B. 支持分层状态机（状态内嵌子状态）
- C. 天然支持状态持久化（ resume 到上次状态）
- D. 每个 Tick 只需评估当前状态分支，无需遍历整棵树
- E. 蓝图可视化编辑比 BehaviorTree 更直观
Answer: A, B, C, D
Explanation: StateTree 是状态机 + 行为树的混合。状态切换直接跳转（O(1)），支持分层，Tick 只评估当前分支。E 是主观判断，且 StateTree 目前蓝图支持有限。
```

**然后**：使用 `quiz-html-generator` 转 HTML。

**你必须做**：完成测验，复习错题。

---

## 任务 2：笔记链接建议（AI 执行，你确认）

**AI 建议**：
- [[MassAI-ECS-笔记]] → [[ChaosPhysics-00-Master-Index]]：MassAI Agent 的物理碰撞使用 Chaos
- [[MassAI-LOD-笔记]] → [[VGM-00-Master-Index]]：MassAI 的渲染 LOD 与 VGM 的 Nanite LOD 协同
- [[MassAI-SpatialHashing]] → [[VSM-00-Master-Index]]：大量 Agent 的阴影使用 VSM
- [[MassAI-SmartObject]] → [[../PCG/00-Master-Index]]：PCG 生成城市，MassSpawner 在 PCG 点上生成 Agent
- [[MassAI-StateTree]] → [[UnrealMCP-00-Master-Index]]：通过 MCP 查询 StateTree 运行状态
- [[MassAI-LearningAgents]] → [[NeuralRendering-00-Master-Index]]：Neural Rendering 为 RL Agent 提供视觉 Observation
- [[MassAI-Fragment]] → [[../../02-引擎源码分析库]]：Fragment 内存布局源码分析

**你必须做**：检查合理性，手动添加 `[[链接]]`。

---

## 任务 3：周数据总结 + 下周规划（AI 执行，你补充）

**AI 建议下周重点**：
- 周一：SmartObjects 深入（注册 → 查询 → Slot 分配 → 释放的完整生命周期）
- 周二：StateTree 实战（将周二写的 Processor 与 StateTree 状态切换结合）
- 周三：观察 StateTree 在实际游戏中的应用（City Sample 的 SmartObject 交互）
- 周四：LearningAgents 入门（设置 Observation、Action、Reward，训练第一个 RL Agent）
- 周末：集成 mini-MassAI 系统（Crowd + SmartObject + StateTree）

**你必须做**：根据实际工作负荷调整。

---

## 任务 4：快速复习（AI 生成 flashcards）

**AI 输出**：Anki / Obsidian flashcards

```markdown
Q: Fragment 与 Component 的 3 个根本区别？
A: 1. Fragment 无函数，纯数据；2. SOA 内存布局 vs AOS；3. 由 EntityManager 统一生命周期管理

Q: MassEntity 的 Chunk 大小通常是多少？为什么？
A: 128 或 256 个 Entity。为了匹配 CPU Cache Line（64 bytes），使遍历单个 Fragment 时 Cache 命中最大化。

Q: Processor 的 Execute 函数接收什么参数？
A: UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context

Q: SmartObject 的 Slot 分配竞争如何解决？
A: 通过 USmartObjectSubsystem 的原子操作或排队机制，先到先得。

Q: StateTree 的 3 种状态类型？
A: State（普通状态）、Linked State（链接状态，复用）、Subtree（子树，嵌套）

Q: LearningAgents 的 3 个核心概念？
A: Observation（观察状态）、Action（执行动作）、Reward（反馈奖励）
```

**你必须做**：导入到 Obsidian 或 Anki，每天复习。

---

## 完成检查清单

- [ ] MassAI 知识测验已完成（得分 ≥80）
- [ ] 错题已复习，薄弱点已标记（如 StateTree 状态类型）
- [ ] 笔记双向链接已手动添加（至少 5 条，连接到 Chaos/VGM/PCG/MCP/NeuralRendering）
- [ ] 周数据总结已补充主观信息
- [ ] Flashcards 已导入并开始复习
- [ ] 下周计划已调整并写入 Obsidian 周模板

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 1 小时*
