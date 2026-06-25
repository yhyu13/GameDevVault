---
tags: [routine/AI-tasks, topic/MassAI, topic/LearningAgents, day/Weekend]
aliases: []
---

# 周末：AI 任务清单 — MassAI 项目实战与深度输出

> **人类目标**：完成一个 MassAI 相关的 mini-project（自定义 Processor + SmartObject 交互 + StateTree 状态或 LearningAgents 训练）。  
> **AI 任务**：Debug 辅助、Blog 润色、架构 review，绝不写核心算法。

---

## 周六上午：项目实战（3h 集中块）

### 任务 1：项目脚手架（AI 生成，你确认）

**输入**："我要做一个 mini-MassAI 系统，包含：1 个自定义 Processor（移动 + 避障）+ 1 个 SmartObject（长椅坐下）+ 1 个 StateTree（Idle → Walk → Sit）。生成项目结构"

**AI 输出**：目录结构 + 文件框架 + TODO 标记

```
MiniMassAI/
├── Source/
│   ├── MiniMassAI/
│   │   ├── MiniMassAI.Build.cs
│   │   ├── MiniMassAI.h
│   │   ├── MiniMassAI.cpp
│   │   ├── Processors/
│   │   │   ├── MiniMassMovementProcessor.h    // TODO(HUMAN): 移动 + 避障
│   │   │   ├── MiniMassMovementProcessor.cpp
│   │   │   ├── MiniMassAvoidanceProcessor.h     // TODO(HUMAN): 基于 Spatial Hash 的避障
│   │   │   └── MiniMassAvoidanceProcessor.cpp
│   │   ├── Fragments/
│   │   │   ├── MiniMassFragments.h             // TODO(HUMAN): 自定义 Fragment（如 FHealthFragment）
│   │   │   └── MiniMassFragments.cpp
│   │   ├── SmartObjects/
│   │   │   ├── MiniMassBenchSmartObject.h      // TODO(HUMAN): 长椅 SmartObject
│   │   │   └── MiniMassBenchSmartObject.cpp
│   │   └── StateTree/
│   │       ├── MiniMassAgentStateTree.h        // TODO(HUMAN): StateTree 状态定义
│   │       └── MiniMassAgentStateTree.cpp
│   └── MiniMassAIEditor/
│       └── ...
├── Content/
│   ├── MassSpawner/
│   │   └── BP_MiniMassSpawner.uasset           // TODO(HUMAN): 配置 MassSpawner
│   ├── StateTree/
│   │   └── ST_AgentBehavior.uasset             // TODO(HUMAN): 可视化 StateTree 资产
│   └── SmartObjects/
│       └── BP_BenchSmartObject.uasset          // TODO(HUMAN): SmartObject 蓝图
└── README.md
```

**你必须做**：确认结构，填充所有 TODO。

---

### 任务 2：核心实现（AI 辅助，你编码）

**输入**："实现 MiniMassMovementProcessor：遍历所有有 FTransformFragment 和 FVelocityFragment 的 Entity，更新位置，并添加一个简单的边界检查（如果 x > 1000，反转速度方向）"

**AI 输出**：核心逻辑提示（不直接给完整代码）

```cpp
void UMiniMassMovementProcessor::Execute(UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context)
{
    // 提示：
    // 1. 使用 EntityQuery.ForEachEntityChunk() 遍历
    // 2. 获取 MutableTransformView 和 VelocityView
    // 3. 对 Chunk 中的每个 Entity：
    //    Transform.GetMutable().SetLocation(NewPos);
    // 4. 边界检查：NewPos.X > 1000 → Velocity.X = -Velocity.X
    // 5. 避免在循环中调用虚函数或分配内存
}
```

**你必须做**：手写代码，编译，运行。

---

### 任务 3：Debug 辅助（AI 执行，你验证）

**常见 MassAI 错误**：

| 错误症状 | 可能原因 | 排查步骤 |
|----------|----------|---------|
| Processor 不执行 | EntityQuery 未正确配置 / 没有 Entity 匹配 Archetype | 检查 `stat mass`，确认 Entity 数量和 Fragment 组成 |
| Agent 不移动 | Fragment 访问权限错误（ReadOnly vs ReadWrite）| 检查 `AddRequirement` 的 `EMassFragmentAccess` |
| 崩溃 / Assert | `GetMutableFragmentView` 用于 ReadOnly 的 Fragment | 检查 AddRequirement 和 View 的匹配 |
| SmartObject Slot 不分配 | SO 未正确注册 / Slot 已满 | 检查 `RegisterSmartObject` 和 `GetAvailableSlots` |
| StateTree 不切换 | 条件评估未满足 / Transition 未配置 | 检查 StateTree 的 Transition 条件和 Evaluate 频率 |
| 性能下降 | Processor 在 Game Thread 执行 / 未使用 Chunk 遍历 | 检查 `bRequiresGameThreadExecution` 和循环结构 |

**AI 诊断**：错误分类 → 3 个可能原因 → 验证步骤 → 修复建议

**你必须做**：按步骤排查，确认根因，手动修复。

---

## 周日下午：输出与复盘

### 任务 4：Blog 初稿润色（AI 执行，你提供内容）

**AI 输出**：3 个候选标题、结构重组、代码格式化、社交摘要

**示例标题**：
> 1. 「从零写 MassEntity Processor：UE5 ECS 框架实战」
> 2. 「5000 人同屏的幕后：UE5 MassAI 的 Fragment-Processor 架构解析」
> 3. 「SmartObject + StateTree：UE5 下一代 AI 交互系统实战」

**结构建议**：
- 问题：传统 Actor AI 的瓶颈（1000 个 Actor = 卡顿）
- 方案：MassEntity ECS（Entity-Fragment-Processor）
- 实战：写一个自定义 Processor（代码 + 截图）
- 发现：SmartObject 的 Slot 分配竞争
- 总结：ECS 思维转换的难点与收获

**你必须做**：检查技术准确性，保留个人风格。

---

### 任务 5：架构 Review（AI 执行，你决策）

**AI 审查**：代码质量、与官方 MassAI 的对比、性能、可扩展性、调试便利性

**AI 输出**：审查报告 + 3 个优先级排序的改进建议

**示例建议**：
1. **高优先级**：将 Movement 和 Avoidance 合并为单个 Processor，减少 Chunk 遍历次数（Cache 友好）
2. **中优先级**：添加 `FMassLODFragment`，实现距离 LOD（近距离 Full、远距离 每 N 帧更新）
3. **低优先级**：将 StateTree 集成到 MassAgent，实现状态驱动的速度变化（Idle=0, Walk=100, Run=300）

**你必须做**：决定哪些改进值得做，记录到技术雷达。

---

## 今日 AI 禁区

- ❌ 让 AI 写核心 Processor 逻辑（Fragment 遍历、避障算法、StateTree 评估）
- ❌ 直接 copy AI 的 bug 修复而不验证根因（如为什么 AddRequirement 权限错会导致崩溃）
- ❌ 让 AI 替写博客技术内容（必须用自己的代码和经验）
- ❌ 让 AI 替你准备演示而不排练

---

## 完成检查清单

- [ ] Mini-MassAI 核心代码已全部手写完成（Processor + SmartObject + StateTree）
- [ ] Debug 问题已用 AI 辅助定位，手动修复（记录根因）
- [ ] Blog 初稿已润色，技术准确性已验证
- [ ] 架构 review 已阅读，改进计划已记录到技术雷达
- [ ] 所有产出已归档到 Obsidian（笔记 + 代码链接 + 博客链接）

---

*AI 执行时间：约 30 分钟*  
*人类执行时间：约 4 小时（3h 项目 + 1h 输出）*  
*产出：1 个可运行的 Mini-MassAI 系统 + 1 篇技术博客 + 1 份演示 ready*
