---
tags: [routine/AI-tasks, topic/PCG, day/Thursday]
aliases: []
---

# 周四：AI 任务清单 — PCG 工程化与工具链

> **人类目标**：理解 PCG 的数据结构、编写工具脚本、分析内存布局。  
> **AI 任务**：生成工具脚本、解释架构、review 安全模型，绝不替你做核心设计。

---

## 任务 1：PCG 数据结构 C++ 概念学习（AI 执行，你 review）

**输入**："UE5 PCG 中 Point 数据、Graph 数据、执行上下文的核心数据结构是什么？"

**AI 输出**：

### 1. FPCGPoint（Point 数据）

```cpp
struct FPCGPoint
{
    FTransform Transform;      // 位置、旋转、缩放
    float Density;           // 密度/优先级（0~1+，用于筛选和混合）
    int32 Seed;              // 随机种子（Deterministic 生成）
    // 注意：Attribute 不直接存储在 Point 中，而是存储在 FPCGPointData 的 Metadata 中
};
```

### 2. FPCGPointData（Point 集合 + Attribute）

```cpp
class FPCGPointData : public FPCGData
{
    TArray<FPCGPoint> Points;           // Point 数组
    FPCGMetadata* Metadata;              // Attribute 字典（TMap<FName, AttributeColumn>）
    // 继承自 FPCGData 的 Spatial Data 接口（用于空间查询）
};
```

### 3. FPCGGraph（Graph 数据结构）

```cpp
class UPCGGraph : public UObject
{
    TArray<UPCGNode*> Nodes;            // 所有节点
    TArray<FPCGEdge> Edges;             // 边（InputPin → OutputPin）
    
    // 执行时：拓扑排序 → 确定节点执行顺序
    // 缓存：每个节点的 Output 可被下游复用
};
```

### 4. FPCGContext（执行上下文）

```cpp
struct FPCGContext
{
    FPCGDataCollection InputData;       // 输入数据（按 Pin 名索引）
    FPCGDataCollection OutputData;      // 输出数据
    const UPCGSettings* InputSettings;  // 用户参数（Node Settings）
    
    // 缓存：上游节点的输出被缓存，避免重复计算
    TMap<FPCGNode*, FPCGDataCollection> CachedData;
    
    // 参数：Seed、Graph 参数、World 上下文
    int32 Seed;
    UWorld* World;
};
```

**你必须做**：
1. 在 UE58 源码中找到这些结构体的实际定义（`PCGPoint.h`、`PCGData.h`、`PCGGraph.h`）
2. 对比 AI 输出与源码，检查字段差异（UE 版本更新可能导致字段变化）
3. 画出 `FPCGPointData` 的内存布局（Points 数组 + Metadata 指针 + 基类虚表指针）

---

## 任务 2：PCG 工具脚本生成（AI 执行，你 review）

**输入**："写一个 Python 脚本，解析 PCG Graph 的 JSON 导出（或 UE 资产的 uasset 解析），提取节点类型、连接关系和 Attribute 使用情况，输出为 Graphviz DOT 格式以便可视化"

**AI 输出**：完整的 Python 脚本

```python
#!/usr/bin/env python3
"""PCG Graph 可视化工具：解析 PCG 配置并生成 DOT 图"""

import json
import sys
from pathlib import Path


def parse_pcg_graph(json_path: str) -> dict:
    """解析 PCG Graph 的 JSON 导出（假设从 UE 编辑器导出）"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data


def generate_dot(graph_data: dict) -> str:
    """生成 Graphviz DOT 格式"""
    nodes = graph_data.get('Nodes', [])
    edges = graph_data.get('Edges', [])
    
    lines = ['digraph PCGGraph {', '    rankdir=LR;']
    
    # 节点定义
    for node in nodes:
        node_id = node['Id']
        node_type = node.get('Type', 'Unknown')
        node_label = node.get('Label', node_type)
        color = {
            'Sampler': 'lightgreen',
            'Filter': 'lightyellow',
            'Transform': 'lightblue',
            'Spawn': 'lightcoral'
        }.get(node_type, 'white')
        lines.append(f'    {node_id} [label="{node_label}", style=filled, fillcolor={color}];')
    
    # 边定义
    for edge in edges:
        src = edge['SourceNodeId']
        dst = edge['TargetNodeId']
        label = edge.get('Label', '')
        lines.append(f'    {src} -> {dst} [label="{label}"];')
    
    lines.append('}')
    return '\n'.join(lines)


def analyze_attributes(graph_data: dict) -> dict:
    """分析 Graph 中使用的 Attribute"""
    attributes = set()
    for node in graph_data.get('Nodes', []):
        for attr in node.get('UsedAttributes', []):
            attributes.add(attr)
    return {
        'total_attributes': len(attributes),
        'attributes': sorted(attributes)
    }


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <pcg_graph.json>")
        sys.exit(1)
    
    json_path = sys.argv[1]
    graph = parse_pcg_graph(json_path)
    
    # 生成 DOT
    dot = generate_dot(graph)
    dot_path = Path(json_path).with_suffix('.dot')
    with open(dot_path, 'w') as f:
        f.write(dot)
    print(f"DOT file written to: {dot_path}")
    
    # 分析 Attribute
    attr_info = analyze_attributes(graph)
    print(f"\nAttribute Analysis:")
    print(f"  Total attributes used: {attr_info['total_attributes']}")
    for attr in attr_info['attributes']:
        print(f"    - {attr}")


if __name__ == '__main__':
    main()
```

**你必须做**：
1. 从 UE 编辑器导出一个 PCG Graph 为 JSON（或使用 `PCGEditor` 的导出功能）
2. 运行脚本，生成 DOT 文件
3. 用 Graphviz 渲染为 PNG：`dot -Tpng pcg_graph.dot -o pcg_graph.png`
4. 检查输出是否与编辑器中的 Graph 一致

**进阶**：添加功能：
- 检测孤立节点（没有输入/输出的节点）
- 计算 Graph 的拓扑排序并标注执行顺序
- 统计每种 Node 类型的数量

---

## 任务 3：PCG 执行管线架构 Review（AI 执行，你决策）

**AI 审查清单**：
- [ ] 是否支持部分 Graph 重执行？（只修改一个 Node 的参数时，是否只重新执行下游节点）
- [ ] 缓存策略是否高效？（大数据量时 CachedData 的内存占用是否可控）
- [ ] 是否支持异步执行？（Editor 下是否阻塞主线程，运行时是否可异步生成）
- [ ] Point 数据在多线程间的传递是否安全？（FPCGPointData 的引用计数或拷贝语义）
- [ ] 与 World Partition 的集成（大世界场景下，PCG Volume 是否按 Cell 分区生成）
- [ ] 与 MassAI 的数据接口（PCG 输出的 Point 如何转为 Mass Entity Spawn Point）

**你必须做**：评估每个建议，记录决策。

---

## 任务 4：PCG Point 数据内存布局分析（AI 计算，你验证）

**输入**：PCG Point 数据结构（简化版）

```cpp
struct FPCGPoint {
    FTransform Transform;      // 包含 FQuat(16B) + FVector(12B) + FVector(12B) = 40B（对齐后 48B）
    float Density;             // 4B
    int32 Seed;                // 4B
    // 注意：实际可能有额外字段，此处简化
};

struct FPCGPointData {
    // 基类 FPCGData 虚表指针 + 引用计数
    TArray<FPCGPoint> Points;           // TArray 头（3 × 8B = 24B）+ 堆上数组
    FPCGMetadata* Metadata;              // 8B 指针
};

struct FPCGMetadata {
    TMap<FName, FPCGMetadataAttributeBase*> AttributeMap;  // TMap 桶数组
};
```

**AI 输出**：

| 场景 | Point 数量 | 原始 Point 数组大小 | 含 Attribute 总估算 | 说明 |
|------|-----------|--------------------|--------------------|------|
| 小型植被散布 | 1,000 | ~48KB | ~100KB | 少量 Attribute（Density + TreeType） |
| 中型森林 | 50,000 | ~2.4MB | ~8MB | 中等 Attribute（Color、Scale、Biome） |
| 大型城市 | 500,000 | ~24MB | ~120MB | 大量 Attribute（BuildingType、Floor、Material） |
| 超大世界 | 5,000,000 | ~240MB | ~1.5GB+ | 需要 Streaming/Partition 策略 |

**TSharedPtr/FPCGData 开销**：
- `TSharedPtr<FPCGPointData>` 引用计数：8B（对象指针）+ 16B（控制块）= 24B
- Graph 中每个中间节点的缓存都持有 `TSharedPtr`，20 个节点 × 50,000 Point = 大量引用计数操作

**优化建议**：
- 使用 `TSharedPtr` 的 `MakeShared` 避免额外分配
- 对于只读传递，考虑 `TSharedRef` 或原始指针（确保生命周期安全）
- 大世界场景下使用 `Partition Actor` 将 Point 数据分块，避免单帧全量加载

**你必须做**：用 UE 的 `Memory Insights` 或 `LLM`（Low Level Memory Tracker）实际测量一个 PCG Graph 的内存占用，对比 AI 估算。

---

## 今日 AI 禁区

- ❌ 让 AI 替你设计内存优化方案（内存布局必须自己验证）
- ❌ 直接运行脚本不 review（PCG 工具脚本可能影响编辑器数据）
- ❌ 解释概念后不写代码实践
- ❌ 不验证 AI 的内存估算（必须用实际工具测量）

---

## 完成检查清单

- [ ] PCG 核心数据结构已对照源码验证（找到实际头文件，对比字段）
- [ ] Python 工具脚本已 review、修改、运行验证（成功生成 DOT 图）
- [ ] 架构审查报告已阅读，决策已记录（是否支持部分重执行、缓存策略等）
- [ ] 内存布局分析已用实际工具验证（Memory Insights 或 LLM）
- [ ] 所有代码和文档已写入 Obsidian

---

*AI 执行时间：约 25 分钟*  
*人类执行时间：约 2 小时*
