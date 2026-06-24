---
tags: [routine/AI-tasks, topic/ChaosPhysics, day/Thursday]
aliases: []
---

# 周四：AI 任务清单 — Chaos Physics 工程化与工具链

> **人类目标**：理解 Chaos 的底层工程实现（多线程求解、ECS 集成、工具链），为自研引擎做准备。  
> **AI 任务**：生成工具脚本、解释概念、review 架构，绝不替你做核心设计。

---

## 任务 1：物理数据分析工具生成（AI 执行，你 review）

**输入**："写一个 Python 脚本，解析 Chaos 的物理模拟日志，统计：每帧刚体数量、碰撞对数、约束求解迭代次数、求解器耗时"

**AI 输出**：完整的 Python 脚本

**你必须做**：
1. 逐行阅读代码
2. 检查引擎特定假设
3. 添加可视化（matplotlib 图表）
4. 运行并验证输出

---

## 任务 2：ECS + Physics 集成概念（AI 执行，你实践）

**输入**："Chaos 如何与 UE5 的 ECS（Mass）系统协同？物理组件如何设计？"

**AI 输出**：
1. 概念解释：ECS 的 Position/Velocity 组件与 Chaos 的 Rigid Body 映射
2. 数据流：GameThread → PhysicsThread → 渲染同步
3. 与 Unity DOTS Physics 的对比

**你必须做**：写一个简化版 ECS + Physics 集成示例。

---

## 任务 3：Chaos 架构 Review（AI 执行，你决策）

**AI 审查清单**：
- [ ] 是否支持确定性回放？（网络同步需求）
- [ ] 多线程求解的 race condition 处理？
- [ ] 大规模场景（10000+ 刚体）的内存优化？
- [ ] 与 Niagara 粒子的碰撞交互？
- [ ] 平台兼容性（Console/Mobile）？

**你必须做**：评估建议，记录决策。

---

## 任务 4：Rigid Body 内存布局分析（AI 计算，你验证）

**输入**：Chaos 的 `FRigidBody` 结构体

```cpp
struct FRigidBody {
    FVector Position;           // 12 bytes
    FQuat Orientation;          // 16 bytes
    FVector Velocity;           // 12 bytes
    FVector AngularVelocity;    // 12 bytes
    float Mass;                 // 4 bytes
    float InvMass;              // 4 bytes
    float Restitution;           // 4 bytes
    float Friction;             // 4 bytes
};
```

**AI 输出**：总大小、padding、Cache Line 分析、SoA 重排序建议

**你必须做**：用 `sizeof()` 验证。

---

## 今日 AI 禁区

- ❌ 让 AI 替你设计物理架构
- ❌ 直接运行脚本不 review
- ❌ 解释概念后不写代码实践

---

## 完成检查清单

- [ ] 工具脚本已 review、修改、运行验证
- [ ] ECS + Physics 集成已用迷你代码实践
- [ ] 架构审查报告已阅读，决策已记录
- [ ] 内存布局分析已验证
- [ ] 所有代码和文档已写入 Obsidian

---

*AI 执行时间：约 25 分钟*  
*人类执行时间：约 2 小时*
