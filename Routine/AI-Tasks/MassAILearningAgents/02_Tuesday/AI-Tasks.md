---
tags: [routine/AI-tasks, topic/MassAI, topic/LearningAgents, day/Tuesday]
aliases: []
---

# 周二：AI 任务清单 — MassAI 专项技能突破

> **人类目标**：通过 ECS 概念练习和 Fragment/Processor 代码实现，内化 MassAI 的核心机制。  
> **AI 任务**：生成练习题、解释架构、review 代码、提供直觉，绝不替写核心实现。

---

## 任务 1：ECS / MassEntity 概念练习题生成（AI 执行）

**输入**："给我生成 5 道关于 MassEntity ECS 的练习题，涵盖：Entity Composition、Fragment Query、Processor 调度、Spatial Hashing、LOD 计算"

**AI 输出**：5 道练习题

**示例题目**：
> **Q1 (Easy)**：一个 Entity 拥有 `FTransformFragment`、`FVelocityFragment`、`FMassLODFragment` 三个 Fragment。另一个 Entity 拥有 `FTransformFragment`、`FVelocityFragment`。它们会被分配到同一个 Archetype 吗？为什么？
>
> **Q2 (Medium)**：一个 Processor 的 `ConfigureQueries` 中注册了 `FTransformFragment` 和 `FVelocityFragment` 的 Read/Write 需求。当该 Processor 执行时，它会遍历哪些 Archetype？如果一个 Archetype 只有 `FTransformFragment` 但没有 `FVelocityFragment`，会被遍历吗？
>
> **Q3 (Medium)**：MassEntity 的 Processor 使用 Task Graph 并行执行。假设你有 3 个 Processor：A（读 FTransform）、B（写 FTransform）、C（读 FTransform + FVelocity）。哪些 Processor 可以并行执行？哪些必须串行？
>
> **Q4 (Hard)**：Spatial Hashing 将世界划分为 10m × 10m 的 Cell。一个 Agent 位于 (25, 48)，查询半径为 15m 的邻居。需要查询哪些 Cell？如果 Agent 移动到 Cell 边界（如 x=29.9），如何处理跨 Cell 查询的重复/遗漏？
>
> **Q5 (Hard)**：MassAI 的 LOD 系统有 4 级（Full / Medium / Low / Off）。1000 个 Agent 在摄像机距离分布为：100m 内 200 个，100-300m 500 个，300-500m 250 个，>500m 50 个。Full LOD 每 Agent 消耗 0.5ms CPU，Medium 0.2ms，Low 0.05ms，Off 0ms。当前帧预算为 150ms。计算最佳 LOD 分配，并讨论「视觉重要性」如何影响这个分配（如近处 but 被遮挡的 Agent）。

**你必须做**：在纸上或代码中完成所有题目，再核对答案。

---

## 任务 2：MassEntity 代码脚手架（AI 生成，你填充）

**输入**："我想写一个最小可运行的 MassEntity 自定义 Processor（C++），处理带有 FTransformFragment 和 FVelocityFragment 的 Entity，每帧更新位置。生成脚手架"

**AI 输出**：
```cpp
// TODO(HUMAN): 在 Build.cs 中添加 MassEntity 模块依赖
// PrivateDependencyModuleNames.AddRange(new string[] { "MassEntity" });

UCLASS()
class MYGAME_API UMyMovementProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyMovementProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context) override;

private:
    // TODO(HUMAN): 定义 EntityQuery，要求 Entity 拥有 FTransformFragment 和 FVelocityFragment
    FMassEntityQuery EntityQuery;
};
```

```cpp
#include "MyMovementProcessor.h"
#include "MassEntitySubsystem.h"
#include "MassExecutionContext.h"
#include "MassCommonFragments.h"

UMyMovementProcessor::UMyMovementProcessor()
{
    // TODO(HUMAN): 设置执行参数
    // bRequiresGameThreadExecution = ?
    // ExecutionFlags = ?
    // ExecutionOrder.ExecuteInGroup = ?
}

void UMyMovementProcessor::ConfigureQueries()
{
    // TODO(HUMAN): 配置 EntityQuery
    // 要求 Entity 拥有 FTransformFragment (ReadWrite) 和 FVelocityFragment (ReadOnly)
    // 使用 EntityQuery.AddRequirement<>()
}

void UMyMovementProcessor::Execute(UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context)
{
    // TODO(HUMAN): 实现核心逻辑
    // 1. 通过 EntityQuery.ForEachEntityChunk() 遍历匹配的 Chunk
    // 2. 获取 FTransformFragment 的数组视图 (GetMutableFragmentView)
    // 3. 获取 FVelocityFragment 的数组视图 (GetFragmentView)
    // 4. 对每个 Entity：Position += Velocity * DeltaTime
    // 5. 注意：Velocity 是 ReadOnly，Transform 是 ReadWrite
}
```

**你必须做**：填充所有 `TODO(HUMAN)`，编译并在编辑器中运行。

**验证步骤**：
1. 在 Editor 中创建 Mass Spawner，配置包含 `FTransformFragment` 和 `FVelocityFragment` 的 Entity
2. 观察 Processor 是否正确更新位置
3. 用 `UE_LOG` 输出 Entity 数量，确认 Chunk 遍历正确

---

## 任务 3：你的 Processor 代码 Review（AI 执行）

**AI 检查清单**：
- [ ] 是否正确配置了 `AddRequirement<>()` 的访问权限（ReadOnly vs ReadWrite）？
- [ ] 是否使用了 `ForEachEntityChunk` 而不是逐 Entity 遍历？（Chunk 处理是 MassEntity 的核心优化）
- [ ] `GetMutableFragmentView` 和 `GetFragmentView` 是否用对？
- [ ] 是否考虑了 `DeltaTime`？（`Context.GetDeltaTimeSeconds()`）
- [ ] `ConfigureQueries` 是否在构造函数中被调用？（或依赖默认行为）
- [ ] 是否避免了在 Execute 中分配内存（如 FString、TArray 的动态增长）？
- [ ] 是否处理了 Velocity 为零的 Entity 的短路退出？（DOD 的 branchless 优化）

**AI 输出**：发现的 bug 列表 + 修复建议（逐行）

**你必须做**：理解每个 bug 的根因，手动修复。

---

## 任务 4：概念直觉（AI 解释，你内化）

| 概念 | AI 解释类比 |
|------|------------|
| **ECS / Entity** | "就像学校的学生管理系统。Entity 是学生 ID（学号），没有任何信息。所有信息（成绩、身高、班级）都写在单独的表格（Fragment）里。按学号查找，就知道去哪个表格看哪一行。" |
| **Fragment vs Component** | "传统 Component 像学生的个人档案袋（每个 Actor 一个袋子，里面有各种文件）。Fragment 像全校的分栏表格（所有学生的成绩在一张表、所有学生的身高在另一张表）。要找 '成绩前 10% 的学生'，只需扫描成绩表，不需要拆开每个档案袋。" |
| **Archetype** | "就像学生的课程组合。选 '数学+物理+化学' 的学生都在一个教室（Archetype），选 '数学+生物+地理' 的在另一个教室。同一个教室的学生，所有课程的作业（Fragment）都按科目分栏存放。" |
| **Processor** | "就像全校广播。校长要通知 '所有选了数学的学生'，不需要逐个班级找人，只需在数学课的广播频道里播放。Processor 只遍历拥有所需 Fragment 的 Entity Chunk，跳过无关的 Archetype。" |
| **StateTree vs BehaviorTree** | "BehaviorTree 像流程图（从上到下执行，每个节点决定下一步）。StateTree 像手机的多任务界面（每个状态是一个 App，你可以快速切换，状态内部有子任务列表）。StateTree 的状态切换是 O(1)，而 BehaviorTree 的深层嵌套需要 O(n) 遍历。" |
| **SmartObject** | "就像餐厅里的座位系统。椅子是 SmartObject，注册到餐厅（Subsystem）。顾客（AI Agent）查询 '有没有空座位？'，餐厅返回可用的椅子（Slot）。顾客坐下后，椅子被标记为占用。顾客离开后，椅子释放。" |
| **LearningAgents** | "就像训练狗狗。Observation 是你看到的（球在哪里），Action 是你做的（跑、跳、咬），Reward 是好/坏反馈（咬到球 = +1，咬到沙发 = -1）。神经网络学习 '看到什么 → 做什么 → 得到奖励' 的映射。" |

**你必须做**：用你自己的话向一个假想的初级 UE 开发者解释这些概念。

---

## 今日 AI 禁区

- ❌ 让 AI 写完整 Processor 实现（必须自己填充 TODO）
- ❌ 让 AI 直接给 ECS 题答案（必须自己算 Spatial Hashing 和 LOD）
- ❌ 不做费曼输出（不解释 = 不理解）
- ❌ 直接应用修复不理解根因（如为什么 Chunk 遍历比 Entity 遍历快）

---

## 完成检查清单

- [ ] 5 道 ECS 练习题已完成并核对（尤其是 Q4 Spatial Hashing 和 Q5 LOD 分配）
- [ ] Processor 核心逻辑已填充，编译通过
- [ ] AI code review 的 bug 已理解并手动修复
- [ ] 6 个核心概念已用自己的话解释（给初级 UE 开发者）
- [ ] 代码和笔记已写入 Obsidian

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 2.5 小时*  
*产出：5 道 ECS 练习 + 1 个自定义 Processor + 1 次 Code Review*
