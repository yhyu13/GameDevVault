---
tags: [routine/AI-tasks, topic/NeuralRendering, day/Friday]
aliases: []
---

# 周五：AI 任务清单 — Neural Rendering 轻量复盘与整理

> **人类目标**：整理本周 Neural Rendering 学习笔记，更新知识库，建立跨主题链接，规划下周。  
> **AI 任务**：生成测验、建议链接、总结数据，绝不替你思考。

---

## 任务 1：Neural Rendering 知识测验生成（AI 执行）

**AI 输出**：结构化测验

```markdown
## Q1 (TF)
ML Deformer 在 Runtime 阶段需要实时运行 Chaos Physics 模拟来生成 vertex offsets。
Answer: False
Explanation: ML Deformer 的 Runtime 阶段只执行 ONNX Inference（MLP forward pass），不需要实时物理模拟。物理模拟仅在离线训练阶段生成训练数据。

## Q2 (SC)
UE5.8 NeuralNetworkEngine 使用的底层推理框架是？
Options:
- A. TensorFlow Lite
- B. PyTorch Mobile
- C. ONNX Runtime
- D. NVIDIA TensorRT
Answer: C

## Q3 (MC)
以下哪些是 ML Deformer 训练数据生成的关键步骤？
Options:
- A. 运行 Chaos Physics / FEM 高保真模拟
- B. 提取每帧的 bone transforms 和 vertex offsets
- C. 数据归一化（normalization）和清洗
- D. 在 Runtime 中实时收集玩家输入数据
- E. 使用 PCA 降维（可选）
Answer: A, B, C, E

## Q4 (FB)
ML Deformer 的典型网络架构是 ______（网络类型），输入通常是 ______（骨骼变换/顶点位置），输出是 ______（顶点偏移/骨骼旋转），在 UE5.8 中通过 ______ 模块执行推理。
Answer: MLP (Multi-Layer Perceptron), 骨骼变换 (bone transforms), 顶点偏移 (vertex offsets), NeuralNetworkEngine

## Q5 (MC)
Bone-driven deformer 相比 Vertex-driven deformer 的优势包括？
Options:
- A. 输入维度更低（bone count << vertex count）
- B. 与现有 Animation Blueprint 兼容性好
- C. 可以处理拓扑变化（mesh 结构改变）
- D. 泛化到未见过的 pose 能力更强
- E. 训练数据更容易获取
Answer: A, B, D

## Q6 (SC)
ML Deformer 的 Inference 结果通常以什么方式应用到 mesh 上？
Options:
- A. Replace mode：直接用预测值替换顶点位置
- B. Additive mode：将预测值作为偏移叠加到 skinned position
- C. Multiplicative mode：将预测值乘以原始位置
- D. Blend mode：与 blendshape 插值混合
Answer: B
```

**然后**：使用 `quiz-html-generator` 转 HTML。

**你必须做**：完成测验，复习错题。

---

## 任务 2：笔记跨主题链接建议（AI 执行，你确认）

**AI 建议**：
- [[MLDeformer-训练数据]] → [[ChaosPhysics/00-Master-Index]]：ML Deformer 的训练数据来自 Chaos Physics 模拟
- [[MLDeformer-ONNX导出]] → [[UnrealMCP/00-Master-Index]]：可通过 MCP 查询模型加载状态和 inference latency
- [[NeuralNetworkEngine-内存]] → [[VSM/00-Master-Index]]：变形后的顶点位置影响 VSM 阴影生成
- [[NeuralRendering-性能]] → [[Nanite/00-Master-Index]]：ML Deformer 变形后的 mesh 可以送入 Nanite 进行细分
- [[NeuralRendering-布料]] → [[WaterPlugins/00-Master-Index]]：水体和布料都可用类似 neural compression 技术优化
- [[MLDeformer-面部]] → [[VGM/00-Master-Index]]：植被 wind animation 也可以用 bone-driven neural network 压缩

**你必须做**：检查合理性，手动添加 `[[链接]]`。

---

## 任务 3：周数据总结 + 下周规划（AI 执行，你补充）

**AI 建议下周重点**：
- 周一：ML Deformer 源码深入（`MLDeformerComponent::UpdateDeformer` 调用链）
- 周二：训练一个真实角色的 ML Deformer（使用 Mixamo 或 Daz3D 角色）
- 周三：观察 2-3 个游戏中 ML deformation 的实际效果，写对比分析
- 周四：NeuralNetworkEngine 跨平台测试（PC DirectML vs Console NPU）
- 周末：Mini-Project：ML Deformer + Chaos Physics 联合训练管线

**你必须做**：根据实际工作负荷调整。

---

## 任务 4：快速复习闪卡（AI 生成，你背诵）

**AI 输出**：

| 正面 | 背面 |
|------|------|
| ML Deformer 的核心思想 | 用 MLP 学习 bone transforms → vertex offsets 的映射，runtime 只 inference |
| Training Data Pipeline | Chaos Physics → 缓存模拟序列 → 提取 (bone, vertex) 对 → 归一化 → 训练 |
| UE5.8 关键模块 | MLDeformer（运行时）、NeuralNetworkEngine（ONNX Runtime）、SkeletalDeformer（骨骼接口） |
| Bone-driven vs Vertex-driven | Bone-driven：输入 bone transforms，维度低，兼容 Animation Blueprint；Vertex-driven：输入相邻顶点，能捕捉局部细节但维度高 |
| Latent Space 作用 | 压缩高维 vertex offsets 到低维表示，减少网络参数量，提升泛化能力 |
| ONNX Runtime EP | CPU / DirectML (PC) / CUDA (NVIDIA) / CoreML (Apple) |
| Additive vs Replace | Additive：offset 叠加到 skinned position（常用）；Replace：直接替换顶点位置（风险高） |
| 性能优化方向 | Batch inference、FP16、persistent buffer、LOD culling、GPU 直接生成 input |

**你必须做**：用 Anki 或 Obsidian 闪卡插件导入，每天复习。

---

## 今日 AI 禁区

- ❌ 让 AI 替你完成测验并直接给答案
- ❌ 让 AI 替你做跨主题链接决策（必须自己理解关联）
- ❌ 让 AI 替你决定下周计划
- ❌ 让 AI 生成闪卡但不背诵

---

## 完成检查清单

- [ ] Neural Rendering 知识测验已完成（得分 ≥80）
- [ ] 错题已复习，薄弱点已标记
- [ ] 笔记双向链接已手动添加（至少 3 条）
- [ ] 周数据总结已补充主观信息
- [ ] 下周计划已调整并写入 Obsidian 周模板
- [ ] 闪卡已导入并开始复习

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 1 小时*
