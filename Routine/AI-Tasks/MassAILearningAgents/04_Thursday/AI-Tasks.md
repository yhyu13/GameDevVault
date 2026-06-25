---
tags: [routine/AI-tasks, topic/MassAI, topic/LearningAgents, day/Thursday]
aliases: []
---

# 周四：AI 任务清单 — MassAI 工程化与工具链

> **人类目标**：理解 MassEntity 的数据结构、Fragment 内存布局、Processor 注册机制，开发辅助工具。  
> **AI 任务**：生成工具脚本、解释架构、review 内存模型，绝不替你做核心设计。

---

## 任务 1：MassEntity C++ 数据结构研究（AI 执行，你实践）

**输入**：MassEntity 源码中的核心数据结构

**AI 输出**：

### 核心数据结构解析

**1. FMassEntityHandle**
```cpp
struct FMassEntityHandle
{
    int32 Index;        // 在 EntityManager 中的索引
    int32 SerialNumber; // 防 ABA 问题的序列号
};
// 大小：8 bytes（轻量级！）
```

**2. FMassFragment / Archetype 内存布局**
```cpp
// Archetype 内部使用 SOA（Structure of Arrays）
// 一个 Chunk 包含固定数量的 Entity（如 128 个）
struct FMassArchetypeChunk
{
    TArray<uint8> FragmentData; // 每个 Fragment 类型的连续数组
    int32 NumEntities;          // 当前 Chunk 中的 Entity 数量
};
```

**3. FMassEntityQuery**
```cpp
// Processor 通过 Query 声明需要的 Fragment
EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
EntityQuery.AddRequirement<FVelocityFragment>(EMassFragmentAccess::ReadOnly);
EntityQuery.AddSharedRequirement<FMassLODFragment>(EMassFragmentAccess::ReadOnly);
// 运行时：EntitySubsystem 只遍历匹配此 Query 的 Archetype Chunk
```

**4. Processor 注册与执行顺序**
```cpp
// 通过 UCLASS 元数据标记执行组
UCLASS()
class UMyProcessor : public UMassProcessor
{
    // 在构造函数中设置
    ExecutionOrder.ExecuteInGroup = TEXT("UpdateWorld");
    ExecutionOrder.ExecuteBefore = { TEXT("OtherProcessor") };
    ExecutionOrder.ExecuteAfter = { TEXT("SpawnProcessor") };
};
```

**你必须做**：
1. 在源码中找到 `FMassEntityHandle`、`FMassArchetypeChunk`、`FMassEntityQuery` 的定义
2. 用 `sizeof()` 或 `UE_LOG` 测量实际大小
3. 验证 SOA 内存布局：一个 Chunk 中 `FTransformFragment` 的存储是连续的吗？

---

## 任务 2：MassEntity 工具脚本（AI 生成，你 review）

**输入**："写一个 Python 脚本，自动生成 MassEntity Fragment 的 C++ 代码框架，从 JSON 配置中读取 Fragment 名称和字段"

**AI 输出**：完整的 Python 脚本

```python
#!/usr/bin/env python3
"""MassEntity Fragment 代码生成器"""

import json
import sys
from pathlib import Path

FRAGMENT_TEMPLATE = """
USTRUCT()
struct FMass{FragmentName}Fragment : public FMassFragment
{
    GENERATED_BODY()
{Fields}
};
"""

FIELD_TEMPLATE = "    UPROPERTY(EditAnywhere, Category=\"Mass\")\n    {Type} {Name};\n"

def generate_fragment(name: str, fields: list) -> str:
    """从 JSON 配置生成 Fragment C++ 代码"""
    field_lines = []
    for f in fields:
        # TODO(HUMAN): 添加更多类型映射（ FVector, FQuat, int32, bool, etc. ）
        cpp_type = f["type"]
        field_lines.append(FIELD_TEMPLATE.format(Type=cpp_type, Name=f["name"]))
    
    return FRAGMENT_TEMPLATE.format(
        FragmentName=name,
        Fields="\n".join(field_lines)
    )

def main():
    # TODO(HUMAN): 实现 JSON 读取和批量生成
    # 输入格式：[{"name": "Health", "fields": [{"name": "Current", "type": "float"}]}]
    pass

if __name__ == "__main__":
    main()
```

**示例输入**：
```json
[
  {
    "name": "Health",
    "fields": [
      {"name": "Current", "type": "float"},
      {"name": "Max", "type": "float"}
    ]
  },
  {
    "name": "Stamina",
    "fields": [
      {"name": "Value", "type": "float"},
      {"name": "RegenRate", "type": "float"}
    ]
  }
]
```

**你必须做**：
1. 逐行阅读代码
2. 添加更多类型映射（`FVector`, `FQuat`, `uint8`, `TEnumAsByte`）
3. 添加 Processor 的配套生成（自动生成查询此 Fragment 的 Processor 脚手架）
4. 运行并验证输出

---

## 任务 3：MassAI 架构 Review（AI 执行，你决策）

**AI 审查清单**：
- [ ] MassEntity 的 Archetype 管理是否支持运行时动态添加/移除 Fragment？（性能开销？）
- [ ] Processor 的依赖声明（ExecuteBefore/After）是否足够表达复杂 DAG？
- [ ] MassAI 的 Spatial Hashing 与 Chaos 的 Broad Phase 碰撞检测是否可以共享数据结构？
- [ ] SmartObject 的 Slot 分配在高并发下是否安全？（多个 Agent 同时争夺同一个 Slot）
- [ ] StateTree 的评估频率是否可配置？（每帧 vs 每 N 帧 vs 事件驱动）
- [ ] LearningAgents 的 Neural Network 推理是否运行在 Game Thread？是否可以异步？
- [ ] MassEntity 与 Niagara 的集成（粒子系统驱动大量 Agent 的视觉效果）是否成熟？

**你必须做**：评估每个建议，记录决策。

---

## 任务 4：ECS 内存布局可视化（AI 计算，你验证）

**输入**：MassEntity Chunk 的内存布局（简化版）

```cpp
struct FMassArchetypeChunk
{
    // 假设 Archetype 包含：FTransformFragment + FVelocityFragment + FMassLODFragment
    // Chunk 容量 = 128 Entities
    // FTransformFragment = 48 bytes (FVector + FQuat + FVector Scale)
    // FVelocityFragment = 12 bytes (FVector)
    // FMassLODFragment = 1 byte (uint8 LODLevel)
};
```

**AI 输出**：内存布局分析

| 数据 | 大小 | 每 Chunk 总大小 | 注释 |
|------|------|----------------|------|
| FTransformFragment × 128 | 48 × 128 = 6,144 bytes | 6 KB | SOA 连续存储 |
| FVelocityFragment × 128 | 12 × 128 = 1,536 bytes | 1.5 KB | SOA 连续存储 |
| FMassLODFragment × 128 | 1 × 128 = 128 bytes | 128 bytes | 填充至 4 bytes 对齐？ |
| Entity 活跃位图 | 128 bits = 16 bytes | 16 bytes | 标记哪些 Entity 有效 |
| Chunk 元数据 | ~32 bytes | ~32 bytes | NumEntities 等 |
| **Chunk 总计** | ~8 KB | ~8 KB | Cache Line 友好 |

**对比 AOS（Array of Structures）**：
```cpp
struct FAgentData {
    FTransformFragment Transform;  // 48
    FVelocityFragment Velocity;    // 12
    FMassLODFragment LOD;          // 1 (+3 padding)
}; // 64 bytes per entity
// Chunk (128 entities) = 64 × 128 = 8,192 bytes
// 但遍历 Transform 时，每 64 bytes 只读 48 bytes，Cache 利用率 75%
// SOA 遍历 Transform 时，48 bytes 连续，Cache 利用率 ~100%
```

**你必须做**：用 `UE_LOG` 或 `LLM` 测量实际 Chunk 大小，对比 AI 估算。

---

## 今日 AI 禁区

- ❌ 让 AI 替你设计 Fragment 结构（数据结构必须自己思考访问模式）
- ❌ 直接运行脚本不 review（生成代码可能影响编译）
- ❌ 解释概念后不写代码实践
- ❌ 让 AI 替你评估架构 trade-off（必须自己理解 Archetype vs Sparse Set）

---

## 完成检查清单

- [ ] 工具脚本已 review、修改、运行验证（至少生成 2 个 Fragment）
- [ ] MassEntity 核心数据结构已在源码中定位并验证大小
- [ ] 架构审查报告已阅读，决策已记录（特别是 Archetype 动态变更和 NN 异步）
- [ ] 内存布局分析已验证（SOA vs AOS 的 Cache 效率）
- [ ] 所有代码和文档已写入 Obsidian

---

*AI 执行时间：约 25 分钟*  
*人类执行时间：约 2 小时*
