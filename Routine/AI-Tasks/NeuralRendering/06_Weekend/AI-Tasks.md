---
tags: [routine/AI-tasks, topic/NeuralRendering, day/Weekend]
aliases: []
---

# 周末：AI 任务清单 — Neural Rendering 项目实战与深度输出

> **人类目标**：完成一个 Neural Rendering 相关的 mini-project（最小 ML Deformer 实验或 ONNX Inference 在 UE5 中的集成）。  
> **AI 任务**：Debug 辅助、Blog 润色、架构 review，绝不写核心算法。

---

## 周六上午：项目实战（3h 集中块）

### 任务 1：项目脚手架（AI 生成，你确认）

**输入**："我要做一个 mini-ML Deformer 实验项目，包含：1 个 Python 训练脚本（PyTorch）+ 1 个 ONNX 导出脚本 + 1 个 UE5.8 最小集成测试（C++ 或 Blueprint）。生成项目结构"

**AI 输出**：目录结构 + 文件框架 + TODO 标记

```
mini-ml-deformer/
├── training/
│   ├── __init__.py
│   ├── model.py          # SimpleMLDeformer (PyTorch MLP)
│   ├── data_generator.py # 弹簧-质量系统训练数据生成
│   ├── train.py          # 训练循环
│   └── export_onnx.py    # ONNX 导出
├── ue5_integration/
│   ├── MLDeformerTest.uproject
│   ├── Content/
│   │   ├── Models/
│   │   │   └── ml_deformer.onnx
│   │   └── Blueprints/
│   │       └── BP_MLDeformerCharacter.uasset
│   └── Source/
│       └── MLDeformerTest/
│           ├── MLDeformerTest.h
│           ├── MLDeformerTest.cpp
│           └── MLDeformerTestCharacter.cpp  # TODO: 加载 ONNX 并运行推理
├── tests/
│   └── test_inference.py  # 验证 ONNX 输出与 PyTorch 一致
├── README.md
└── requirements.txt
```

**你必须做**：确认结构，填充所有 TODO。

---

### 任务 2：核心实现（AI 辅助，你手写）

**输入**："实现 `SimpleMLDeformer` 的 PyTorch 训练 + ONNX 导出，并写一个最小 UE5.8 C++ 测试类加载 ONNX 模型"

**AI 输出**：骨架代码（关键接口已标注，核心逻辑为 TODO）

```cpp
// MLDeformerTestCharacter.cpp (UE5.8)
#include "MLDeformerTestCharacter.h"
#include "NeuralNetworkEngine/Public/NeuralNetworkEngine.h"
#include "MLDeformer/Public/MLDeformerModel.h"

void AMLDeformerTestCharacter::BeginPlay()
{
    Super::BeginPlay();
    
    // TODO(HUMAN): 加载 ONNX 模型
    // 1. 获取 NeuralNetworkEngine 模块
    // 2. 创建 ONNX Runtime Session
    // 3. 加载 .onnx 文件到 UMLDeformerModel
    // 4. 绑定输入输出张量
}

void AMLDeformerTestCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // TODO(HUMAN): 每帧执行推理
    // 1. 从 SkeletalMeshComponent 获取 Bone Transforms
    // 2. 转换为 MLP 输入格式（flatten, normalize）
    // 3. 调用 NeuralNetworkEngine::Run()
    // 4. 将输出 Vertex Offsets 应用到 SkinnedMesh
}
```

**你必须做**：填充所有 `TODO(HUMAN)`，编译并运行。

---

### 任务 3：Debug 辅助（AI 执行，你验证）

**输入**：运行时错误日志（如 "ONNX model load failed"、"Input dimension mismatch"、"Inference returns NaN"、"Vertex offsets not applied"）

**AI 诊断**：错误分类 → 3 个可能原因 → 验证步骤 → 修复建议

| 错误 | 可能原因 | 验证步骤 | 修复建议 |
|------|----------|----------|----------|
| ONNX model load failed | 1. ONNX Runtime 版本不匹配<br>2. 模型路径错误<br>3. 模型包含不支持的算子 | 1. 检查 ONNX Runtime 版本<br>2. 用 `FPaths::ProjectContentDir()` 验证路径<br>3. 用 netron 查看模型 | 1. 使用 UE5.8 对应 ONNX opset<br>2. 使用绝对路径或正确相对路径<br>3. 替换不支持算子 |
| Input dimension mismatch | 1. PyTorch 导出时 batch dim 处理错误<br>2. UE5 中 bone transforms 展平方式不同<br>3. dynamic_axes 设置错误 | 1. 打印 PyTorch input shape<br>2. 打印 UE5 input tensor shape<br>3. 对比 ONNX 模型 input 定义 | 1. 确保 ONNX 的 fixed batch size = 1<br>2. 统一展平顺序（row-major vs column-major）<br>3. 检查 FTransform 到 float array 的转换 |
| Inference returns NaN | 1. 输入未归一化，值域过大<br>2. 训练时梯度爆炸<br>3. 权重初始化问题 | 1. 检查输入值范围<br>2. 重新训练并监控梯度 norm<br>3. 检查 weight 分布 | 1. 添加 input normalization（mean/std）<br>2. 使用 gradient clipping<br>3. 使用 Kaiming/Xavier 初始化 |
| Vertex offsets not applied | 1. MLDeformerComponent 未正确附加<br>2. 输出未写入 VertexBuffer<br>3. Apply mode 设置错误 | 1. 检查 Component 的 Owner<br>2. 用 RenderDoc 抓帧查看 vertex position<br>3. 检查 OutputInfo.ApplyMode | 1. 确认 Component 在 SkeletalMeshComponent 之后初始化<br>2. 使用正确 buffer 写入 API<br>3. 使用 Additive 模式 |

**你必须做**：按步骤排查，确认根因，手动修复。

---

### 任务 4：Blog 初稿润色（AI 执行，你提供内容）

**AI 输出**：3 个候选标题、结构重组、代码格式化、社交摘要

**示例标题**：
> 1. 「从零训练 ML Deformer：用 PyTorch 和 UE5.8 实现神经网络驱动角色动画」
> 2. 「ML Deformer 实战：Chaos Physics 模拟 → ONNX 导出 → UE5 Runtime Inference 完整管线」
> 3. 「游戏开发中的 Neural Rendering：我用 UE5.8 做了第一个 ML Deformer 实验」

**建议结构**：
1. 背景：为什么需要 ML Deformer（实时 vs 离线质量差距）
2. 原理：Training Data → MLP → ONNX → Runtime Inference
3. 实现：Python 训练 + ONNX 导出 + UE5 C++ 集成
4. 踩坑：dimension mismatch、normalization、memory layout
5. Benchmark：Inference latency、memory usage、quality comparison
6. 展望：下一步（真实角色、布料、面部）

**你必须做**：检查技术准确性，保留个人风格。

---

## 今日 AI 禁区

- ❌ 让 AI 写核心训练代码或 UE5 C++ 集成代码（网络结构和推理调用必须自己理解）
- ❌ 直接 copy AI 的 bug 修复而不验证根因
- ❌ 让 AI 替写博客技术内容
- ❌ 让 AI 替你准备演示而不排练

---

## 完成检查清单

- [ ] Mini-ML Deformer 核心代码已全部手写完成（Python 训练 + UE5 集成）
- [ ] Debug 问题已用 AI 辅助定位，手动修复
- [ ] Blog 初稿已润色，技术准确性已验证
- [ ] 至少 1 个 ONNX 模型成功在 UE5.8 中加载并运行推理
- [ ] 所有产出已归档到 Obsidian（笔记 + 代码链接 + 博客链接）

---

*AI 执行时间：约 30 分钟*  
*人类执行时间：约 4 小时（3h 项目 + 1h 输出）*  
*产出：1 个可运行的 mini-ML Deformer + 1 篇技术博客草稿*
