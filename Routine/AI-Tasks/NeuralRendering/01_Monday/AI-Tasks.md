---
tags: [routine/AI-tasks, topic/NeuralRendering, day/Monday]
aliases: []
---

# 周一：AI 任务清单 — Neural Rendering 前沿技术输入

> **人类目标**：理解 ML Deformer 论文与 UE5.8 实现，掌握神经网络驱动 mesh deformation 的完整管线。
> **AI 任务**：提供脚手架、解释架构、生成问题，绝不替读论文。

---

## 任务 1：ML Deformer 论文预读引导（AI 执行）

**输入**："ML Deformer: Neural Mesh Deformation for Real-Time Character Animation"（Epic Games 2022 / UE5.4+）+ UE5.8 `MLDeformer` Plugin 文档

**AI 输出**：
1. 一段 **150 字摘要**：ML Deformer 是一种用多层感知机（MLP）学习高保真 mesh deformation 的技术。通过离线运行 Chaos Physics / FEM 模拟生成 (bone transforms, vertex offsets) 训练对，训练一个小型 MLP 网络。Runtime 时，只需输入 bone transforms，网络即可预测高精度 vertex offsets，以极低开销（<0.1ms/character）实现肌肉抖动、皮肤拉伸等复杂效果，无需实时物理模拟。
2. **3 个引导问题**：
   - Q1: ML Deformer 的 training data 如何从 Chaos Physics 生成？时间步长、帧采样策略、数据归一化如何处理？
   - Q2: 网络架构通常是几层 MLP？输入输出维度如何对应 bone count / vertex count？Latent space 维度如何选择？
   - Q3: Bone driver vs Vertex driver 的区别是什么？为什么 Epic 选择 bone-driven（输入 bone transforms）而非 vertex-driven（输入相邻顶点位置）？
3. **重点章节标记**：先读 Training Data Generation（理解模拟 → 样本），再读 Network Architecture（MLP 结构、激活函数、损失函数），最后读 UE5.8 Plugin 文档（UmlDeformerComponent、ONNX Runtime 集成）

**交付物**：`MLDeformer-Reading-Guide.md`

---

## 任务 2：ML Deformer 架构解释（AI 执行，你验证）

**输入**：UE5.8 `MLDeformer` 模块架构

**AI 输出**：
1. 完整的 pipeline：
   - **离线阶段**：Chaos Physics / Maya FEM / Houdini 模拟 → 导出 (bone transforms, vertex deltas) 序列 → 数据清洗（归一化、去噪）→ 训练 MLP（PyTorch / TensorFlow）→ 导出 ONNX
   - **导入阶段**：UE5 Editor → `MLDeformer` 导入 ONNX → 生成 `UMLDeformerModel` 资产 → 绑定到 `USkeletalMeshComponent`
   - **Runtime 阶段**：Animation Blueprint 输出 bone transforms → `UMLDeformerComponent` 收集 → `NeuralNetworkEngine` 调用 ONNX Runtime Inference → 输出 vertex offsets → 叠加到 skinned position
2. 关键数据流：
   ```
   Bone Transforms (N×4×4 float) → Flatten (N×12 float) → MLP Input
   MLP Output (M×3 float) → Vertex Offsets → Add to Base Vertex Position
   ```
3. 网络架构参考：
   - Input: 64 (bone count) × 12 (rotation+translation) = 768 dim
   - Hidden: [512, 256, 128] with ReLU / Swish
   - Output: V×3 (vertex count × XYZ offset)
   - Latent: 可选 bottleneck layer（压缩表示）

**你必须做**：在 UE58 源码中找到 `MLDeformer` 模块，打开 `MLDeformerModel.h`、`MLDeformerComponent.h`，验证 AI 描述的架构。

---

## 任务 3：面试谈资生成（AI 执行，你 rehearse）

**AI 输出**：
1. **30 秒版本**：ML Deformer 是 UE5.8 的神经网络驱动 mesh deformation 技术。我用 Chaos Physics 生成训练数据，训练一个 MLP 来预测顶点偏移。Runtime 时只需 inference，开销极低，能实现高保真肌肉/皮肤动画。我正在学习它的 ONNX Runtime 集成和训练数据管线。
2. **2 分钟版本**：背景（实时角色动画需要高保真变形，但 Chaos Physics 太昂贵）→ ML Deformer 核心（训练数据生成 + MLP 推理）→ 网络架构（bone-driven MLP，输入 bone transforms 输出 vertex offsets）→ UE5.8 实现（MLDeformer Plugin + NeuralNetworkEngine ONNX Runtime）→ 使用场景（肌肉、皮肤、布料）→ 局限（训练数据质量决定效果、网络容量与 latency 的权衡、不支持拓扑变化）
3. **3 个追问**：
   - "ML Deformer 与 Blendshape 相比有什么优势？什么时候应该用一个，什么时候用另一个？"
   - "训练数据不足时如何提升泛化能力？Data Augmentation 在 deformation 中怎么做？"
   - "ONNX Runtime 在 UE5 中的跨平台支持如何？Console 和 Mobile 上 Inference 延迟是多少？"

**你必须做**：rehearse aloud。

---

## 任务 4：UE5.8 Neural Rendering 源码地图（AI 执行，你验证）

**输入**："UE5.8 Neural Rendering 相关的模块和关键函数？"

**AI 输出**：
1. **MLDeformer** (Runtime/Editor) — ML Deformer 核心运行时与编辑器支持
2. **NeuralNetworkEngine** (Runtime) — ONNX Runtime 封装，跨平台推理引擎
3. **SkeletalDeformer** (Runtime) — 骨骼驱动变形接口，与 Animation Blueprint 集成
4. **GeometryDeformer** (Runtime) — 通用几何变形，支持静态 mesh

**调用链**：
```
Animation Blueprint
  → USkeletalMeshComponent::UpdateSkinnedMesh()
  → UMLDeformerComponent::UpdateDeformer()
  → FMLDeformerModel::RunInference()
  → NeuralNetworkEngine::ONNXRuntimeSession::Run()
  → ONNX Runtime (CPU/GPU EP)
  → 输出 Vertex Offsets
  → Apply to Skinned Vertex Positions
  → Render (Lumen / VSM / Nanite)
```

**关键函数**：
- `FMLDeformerModel::LoadModel()` — 加载 ONNX 模型
- `FMLDeformerModel::RunInference()` — 执行推理
- `FNeuralNetworkEngineModule::CreateSession()` — 创建 ONNX Runtime Session
- `FSkeletalDeformer::ApplyDeformation()` — 应用变形到 skeletal mesh

**你必须做**：在 UE58 源码中打开这些模块，找到上述关键函数并验证调用链。

---

## 今日 AI 禁区

- ❌ 让 AI 替你读 ML Deformer 论文而不自己理解 training data pipeline
- ❌ 让 AI 替写笔记（神经网络架构必须自己理解每层的意义）
- ❌ 让 AI 生成代码路径而不验证（UE 源码模块名可能已更新）
- ❌ 让 AI 替你准备面试回答而不理解 bone-driven vs vertex-driven 的本质区别

---

## 完成检查清单

- [ ] ML Deformer 阅读指南已生成并打印
- [ ] 论文核心章节已精读（Training Data + Network Architecture）
- [ ] 面试谈资已 rehearse aloud
- [ ] UE5.8 Neural Rendering 源码路径已验证（找到 LoadModel/RunInference/CreateSession）
- [ ] 所有内容已写入 Obsidian 笔记（你写的，不是 AI 写的）

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2 小时*  
*产出：1 篇论文笔记 + 1 篇源码分析 + 面试谈资 ready*
