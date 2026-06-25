---
tags: [routine/AI-tasks, topic/PCG, day/Weekend]
aliases: []
---

# 周末：AI 任务清单 — PCG 项目实战与深度输出

> **人类目标**：完成一个 PCG 相关的 mini-project（自定义 PCG Graph 或程序化生成器）。  
> **AI 任务**：Debug 辅助、Blog 润色、架构 review，绝不写核心算法。

---

## 周六上午：项目实战（3h 集中块）

### 任务 1：项目脚手架（AI 生成，你确认）

**输入**："我要做一个 mini-PCG 生成器，包含：1 个 UE5 PCG Graph（程序化森林生成）+ 自定义 C++ Node（Biome Mixer，按高度混合不同植被类型）+ 1 个 Python 导出工具（将生成的 Point 数据导出为 CSV）。生成项目结构"

**AI 输出**：目录结构 + 文件框架 + TODO 标记

```
mini-pcg-forest/
├── Content/
│   ├── PCG/
│   │   ├── PCG_ForestMaster.uasset       # 主 PCG Graph
│   │   ├── PCG_BiomeMixer.uasset         # 自定义 Biome Mixer Node（C++ 实现）
│   │   └── PCG_ForestVolume.uasset       # PCG Volume 配置
│   └── Meshes/
│       ├── SM_Tree_Oak.uasset
│       ├── SM_Tree_Pine.uasset
│       └── SM_Rock_Small.uasset
├── Source/
│   ├── MiniPCGForest/
│   │   ├── Private/
│   │   │   └── PCGBiomeMixer.cpp       # TODO(HUMAN): 实现 Biome Mixer 逻辑
│   │   └── Public/
│   │       └── PCGBiomeMixer.h
│   └── MiniPCGForest.Build.cs
├── Tools/
│   └── export_pcg_points.py            # TODO(HUMAN): 解析 PCG 输出并导出 CSV
├── README.md
└── MiniPCGForest.uproject
```

**AI 输出的 Biome Mixer Node 框架**：

```cpp
// PCGBiomeMixer.h
#pragma once
#include "CoreMinimal.h"
#include "PCGNode.h"
#include "PCGBiomeMixer.generated.h"

UCLASS(BlueprintType, ClassGroup = (PCG))
class UPCGBiomeMixerSettings : public UPCGSettings
{
    GENERATED_BODY()

public:
    UPCGBiomeMixerSettings();

    // 高度阈值（决定生物群系分界）
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = Settings, meta = (PCG_Overridable))
    float LowlandHeight = 0.0f;

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = Settings, meta = (PCG_Overridable))
    float HighlandHeight = 500.0f;

    // 每种高度的植被类型（对应不同 Static Mesh）
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = Settings, meta = (PCG_Overridable))
    TMap<FString, TSoftObjectPtr<UStaticMesh>> BiomeMeshes;
};

// TODO(HUMAN): 实现 FPCGBiomeMixerElement 的 ExecuteInternal
// 逻辑：读取输入 Point 的 Z 高度 → 按 Lowland/Highland 阈值分类 → 
//       设置 Attribute "BiomeType" 和 "MeshPath" → 输出修改后的 Point Data
```

**你必须做**：确认结构，填充所有 TODO。

---

### 任务 2：核心实现（AI 辅助，你手写）

**AI 辅助**：提供实现提示和代码片段

**核心实现要点**：
1. **Biome Mixer Node**：
   - 遍历输入 Point Data 的所有 Point
   - 读取 `Transform.Location.Z`
   - 如果 Z < LowlandHeight → 设置 `BiomeType = "Wetland"`, `MeshPath = ...`
   - 如果 LowlandHeight <= Z < HighlandHeight → 设置 `BiomeType = "Forest"`, `MeshPath = ...`
   - 如果 Z >= HighlandHeight → 设置 `BiomeType = "Mountain"`, `MeshPath = ...`
   - 输出带新 Attribute 的 Point Data

2. **PCG Graph**：
   - `Landscape Surface Sampler` → `Biome Mixer` → `Filter by Density` → `Static Mesh Spawner`
   - 在 `Static Mesh Spawner` 中根据 `MeshPath` Attribute 选择对应的 Mesh

3. **Python 导出工具**：
   - 读取 PCG 生成的 Point 数据（通过 UE 的 JSON 导出或 CSV 导出）
   - 输出为 `forest_points.csv`（包含 X, Y, Z, BiomeType, MeshPath, ScaleX, ScaleY, ScaleZ）

**你必须做**：手写所有核心代码，在 UE 编辑器中搭建 Graph，测试生成效果。

---

### 任务 3：Debug 辅助（AI 执行，你验证）

**输入**：运行时错误日志（如 "Point Data is empty"、"Attribute not found"、"Mesh not loaded"、"Graph execution failed"）

**AI 诊断**：错误分类 → 3 个可能原因 → 验证步骤 → 修复建议

**常见错误**：
| 错误 | 可能原因 | 验证步骤 | 修复 |
|------|---------|---------|------|
| Point Data is empty | Sampler 没有正确连接 Surface | 检查 Sampler 的输入 Surface 是否有效 | 重新选择 Landscape 或 Mesh |
| Attribute not found | Attribute 名拼写错误或在错误的 Metadata 中 | 在 Blueprint 中打印所有 Attribute 名 | 核对 Attribute 名大小写 |
| Mesh not loaded | SoftObjectPtr 没有 Resolve | 检查 `FSoftObjectPath::TryLoad()` 或 `FStreamableManager` | 使用硬引用或确保资产已加载 |
| Graph execution failed | 循环依赖或缺少输入 | 检查 Graph 的拓扑结构 | 确保没有循环，所有必要输入已连接 |
| 生成结果不自然 | 采样密度过高或过低 | 调整 Sampler 的间距参数 | 使用 Poisson Disk 或降低密度 |

**你必须做**：按步骤排查，确认根因，手动修复。

---

## 周日下午：输出与复盘

### 任务 4：Blog 初稿润色（AI 执行，你提供内容）

**AI 输出**：3 个候选标题、结构重组、代码格式化、社交摘要

**示例标题**：
> 1. 「从零写 UE5 PCG 自定义节点：程序化森林生物群系生成器」
> 2. 「UE5.8 PCG 实战：一个 Biome Mixer 节点的设计与实现」
> 3. 「程序化内容生成入门：用 PCG Graph 搭建可扩展的植被系统」

**建议结构**：
- 背景（为什么需要 PCG？手摆关卡 vs 程序化生成）
- 需求分析（我们要生成什么：多生物群系森林）
- 技术方案（PCG Graph + 自定义 C++ Node + Python 导出工具）
- 核心实现（Biome Mixer 的算法、Attribute 系统、Mesh 选择）
- 踩坑与收获（调试过程、性能优化、Deterministic 验证）
- 下一步（扩展到城市生成、运行时加载、与 MassAI 集成）

**你必须做**：检查技术准确性，保留个人风格。

---

## 今日 AI 禁区

- ❌ 让 AI 写核心算法（Biome Mixer 的分区逻辑、Attribute 变换、Mesh 选择）
- ❌ 直接 copy AI 的 bug 修复而不验证根因
- ❌ 让 AI 替写博客技术内容
- ❌ 让 AI 替你准备演示而不排练

---

## 完成检查清单

- [ ] mini-PCG Forest 核心代码已全部手写完成（C++ Node + Graph + Python 工具）
- [ ] Debug 问题已用 AI 辅助定位，手动修复
- [ ] Blog 初稿已润色，技术准确性已验证
- [ ] 所有产出已归档到 Obsidian（笔记 + 代码链接 + 博客链接）
- [ ] 至少生成了 1 个可运行的 PCG 场景（有截图）

---

*AI 执行时间：约 30 分钟*  
*人类执行时间：约 4 小时（3h 项目 + 1h 输出）*  
*产出：1 个可运行的 PCG 生成器 + 1 篇技术博客 + 1 份截图集*
