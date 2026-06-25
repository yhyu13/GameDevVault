---
tags: [routine/AI-tasks, topic/PCG, day/Tuesday]
aliases: []
---

# 周二：AI 任务清单 — PCG 专项技能突破

> **人类目标**：通过数学练习和代码实现，内化 PCG 的核心机制（采样、空间查询、噪声、图遍历、属性变换）。  
> **AI 任务**：生成练习题、解释算法、review 代码、提供直觉，绝不替写核心实现。

---

## 任务 1：PCG 数学/算法练习题生成（AI 执行）

**输入**："给我生成 5 道关于 PCG 核心算法的练习题，涵盖：Point 采样策略、空间查询、噪声函数、Graph 拓扑排序、Attribute 变换"

**AI 输出**：5 道练习题

**示例题目**：
> **Q1 (Easy)**：一个 Landscape 地形大小为 4096×4096，使用 `Surface Sampler` 以 100 单位间距进行均匀网格采样。计算总采样点数（不考虑边界剔除）。然后说明如果改用 Poisson Disk Sampling（最小间距 80），为什么总点数会更少但分布更自然？

> **Q2 (Medium)**：一个 PCG Graph 有 5 个 Node：A(Sampler) → B(Filter) → C(Transform) → D(Filter) → E(Spawn)。每个 Node 的输入输出如下：
> - A 输出 10,000 Points
> - B 按 Density > 0.5 筛选，保留 40%
> - C 对每个 Point 的 Scale 属性乘 2.0
> - D 按 Scale > 1.5 筛选
> - E 将剩余 Point 生成 Static Mesh Instance
> 计算最终 E 接收的 Point 数量。如果交换 B 和 C 的顺序，结果会变化吗？为什么？

> **Q3 (Medium)**：编写一个伪代码函数 `ApplyPerlinNoiseToDensity(points, seed, frequency)`，对输入的 Point 数组，根据每个 Point 的 World Position 采样 3D Perlin Noise，将结果写入 `Density` Attribute（范围 0~1）。说明为什么 Seed 相同则输出相同（Deterministic）。

> **Q4 (Hard)**：一个 PCG Graph 需要按以下规则生成城市街区：
> - 先沿 Spline 生成道路点（间距 50m）
> - 在每个道路点两侧偏移 20m 生成建筑点
> - 建筑点需检查与最近道路点的距离 < 25m，否则剔除
> - 最终建筑点按 `BuildingType` Attribute（ Residential/Commercial）分组， Residential 占 70%
> 设计这个 Graph 的 Node 链（用 Spline/Transform/Filter/Attribute 节点），并说明每一步的数据流变化。

> **Q5 (Hard)**：PCG 的 Attribute 系统需要支持运行时修改。设计一个数据结构 `FPCGMetadata`，支持以下操作，要求时间复杂度均为 O(1) 或均摊 O(1)：
> - `AddAttribute<T>(Name)` — 添加类型为 T 的属性列
> - `SetValue<T>(PointIndex, Name, Value)` — 为指定 Point 设置属性值
> - `GetValue<T>(PointIndex, Name)` — 读取属性值
> - `RemoveAttribute(Name)` — 删除属性列
> 说明你的设计与 UE 实际的 `FPCGMetadata`（基于 `TMap<FName, FPCGMetadataAttributeBase*>`）有何异同。

**你必须做**：在纸上或代码中完成所有题目，再核对答案。

---

## 任务 2：PCG Node 代码脚手架（AI 生成，你填充）

**输入**："我想写一个最小可运行的自定义 PCG Node（C++），名为 `PCGPointScaler`，功能：读取输入 Point 的 `Scale` Attribute，乘以一个用户参数 `ScaleMultiplier`，输出修改后的 Point Data。生成 UE5 C++ 脚手架"

**AI 输出**：
```cpp
// PCGPointScaler.h
#pragma once
#include "CoreMinimal.h"
#include "PCGNode.h"
#include "PCGPointScaler.generated.h"

UCLASS(BlueprintType, ClassGroup = (PCG))
class PCG_API UPCGPointScalerSettings : public UPCGSettings
{
    GENERATED_BODY()

public:
    UPCGPointScalerSettings();

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = Settings, meta = (PCG_Overridable))
    float ScaleMultiplier = 1.0f;

    // TODO(HUMAN): 实现 GetEdgeLabels、NodeTypeOverride 等必要接口
};

UCLASS()
class PCG_API FPCGPointScalerElement : public FPCGNode
{
    GENERATED_BODY()

public:
    virtual bool ExecuteInternal(FPCGContext* Context) const override;

protected:
    // TODO(HUMAN): 实现 Point 遍历逻辑
    // 1. 从 Context 获取 Input Point Data
    // 2. 读取 Settings->ScaleMultiplier
    // 3. 遍历每个 Point，找到 Scale Attribute
    // 4. 将 Scale 乘以 ScaleMultiplier
    // 5. 输出修改后的 Point Data
};
```

```cpp
// PCGPointScaler.cpp
#include "PCGPointScaler.h"
#include "PCGComponent.h"
#include "Data/PCGPointData.h"
#include "Metadata/PCGMetadata.h"

bool FPCGPointScalerElement::ExecuteInternal(FPCGContext* Context) const
{
    // TODO(HUMAN): 实现完整逻辑
    // 步骤 1: 获取 Input Data
    // const FPCGDataCollection& InputData = Context->InputData;
    
    // 步骤 2: 获取 Settings
    // const UPCGPointScalerSettings* Settings = Context->GetInputSettings<UPCGPointScalerSettings>();
    
    // 步骤 3: 遍历 Point 并修改 Scale Attribute
    // for (FPCGPoint& Point : PointData->GetPoints())
    // {
    //     FVector Scale = Point.Transform.GetScale3D();
    //     Scale *= Settings->ScaleMultiplier;
    //     Point.Transform.SetScale3D(Scale);
    // }
    
    // 步骤 4: 输出到 Context->OutputData
    
    return true;
}
```

**你必须做**：填充所有 `TODO(HUMAN)`，编译并在一个 PCG Graph 中测试。

**测试步骤**：
```
1. 在 UE 编辑器中创建 C++ 类，继承 UPCGSettings
2. 实现 FPCGPointScalerElement 的 ExecuteInternal
3. 在 PCG Graph 中添加自定义节点
4. 连接输入 Point Data，设置 ScaleMultiplier = 2.0
5. 观察输出 Point 的 Scale 是否变为原来的 2 倍
```

---

## 任务 3：你的 PCG Node 代码 Review（AI 执行）

**AI 检查清单**：
- [ ] 是否正确处理了输入 Pin 为空的边界情况（无 Point Data 输入时返回空）
- [ ] 是否检查 Attribute 存在性（`Scale` 属性不存在时如何降级？默认 FVector(1,1,1)？）
- [ ] 是否支持 `PCG_Overridable`（运行时通过参数覆盖 Settings）
- [ ] 是否遵循 PCG 的惰性求值原则（只在需要时执行，不重复计算）
- [ ] 是否正确填充 `OutputData`（Data 类型、Pin 标签匹配）
- [ ] 是否处理了 `Deterministic` 要求（相同 Seed 产生相同输出）
- [ ] 多线程安全（PCG 可能在后台线程执行，Attribute 读写是否线程安全）

**AI 输出**：发现的 bug 列表 + 修复建议（逐行）

**你必须做**：理解每个 bug 的根因，手动修复。

---

## 任务 4：概念直觉（AI 解释，你内化）

| 概念 | AI 解释类比 |
|------|------------|
| PCG Graph | "就像工厂流水线。每个 Node 是一个工位：Sampler 是原材料投放（把地形变成点云），Filter 是质检（把不合格的点剔除），Transform 是加工（修改点的位置/旋转/大小），Spawn 是包装出货（把点变成游戏世界里的树、石头、房子）。流水线有固定顺序，但你可以随时插入新工位。" |
| Point + Attribute | "就像快递包裹。Point 是包裹的地址（Transform = 位置+旋转+大小），Attribute 是包裹里的物品清单（Density = 优先级，Color = 颜色，TreeType = 树的种类）。每个 Node 可以读取清单、修改内容、甚至添加新的条目。" |
| Deterministic Generation | "就像食谱。只要原料（Seed + 参数 + 输入地形）一样，厨师（Graph 节点）一样，做出来的菜（生成的内容）就一模一样。这对于多人协作和版本控制至关重要——同一张地图，所有玩家看到的是同一个世界。" |

**你必须做**：用你自己的话向一个假想的初级关卡设计师解释这些概念。

---

## 今日 AI 禁区

- ❌ 让 AI 写完整 PCG Node 实现（核心逻辑必须自己写）
- ❌ 让 AI 直接给算法题答案（尤其是 Attribute 数据结构设计和图拓扑排序）
- ❌ 不做费曼输出（必须用自己的话解释，不是复述 AI 的类比）
- ❌ 直接应用修复不理解根因（每个 bug 必须追溯到 PCG 执行模型或数据流原理）

---

## 完成检查清单

- [ ] 5 道算法题已完成并核对（尤其是 Q4 的 Graph 设计题和 Q5 的数据结构题）
- [ ] PCG Node 核心逻辑已填充（`ExecuteInternal` 完整实现）
- [ ] AI code review 的 bug 已理解并手动修复
- [ ] 3 个核心概念已用自己的话解释（写进笔记）
- [ ] 代码和笔记已写入 Obsidian

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 2.5 小时*  
*产出：5 道算法练习 + 1 个自定义 PCG Node + 1 次 Code Review*
