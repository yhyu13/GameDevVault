---
tags: [routine/AI-tasks, topic/NeuralRendering, day/Tuesday]
aliases: []
---

# 周二：AI 任务清单 — Neural Rendering 专项技能突破

> **人类目标**：通过数学推导和最小实现，内化 ML Deformer 的核心机制。  
> **AI 任务**：生成练习题、解释公式、review 代码、提供直觉，绝不替写核心实现。

---

## 任务 1：Neural Deformation 数学练习题生成（AI 执行）

**输入**："给我生成 5 道关于 ML Deformer 的数学/ML 练习题，涵盖：神经网络基础、矩阵运算、deformation math、loss function、inference pipeline"

**AI 输出**：5 道练习题

**示例题目**：
> **Q1 (Easy)**：一个角色有 64 根骨骼，每根骨骼的 transform 是 4×4 矩阵。ML Deformer 通常将矩阵展平为 12 维向量（去掉最后一行 [0,0,0,1]）。请计算输入层维度。
> Answer: 64 × 12 = 768

> **Q2 (Medium)**：一个 mesh 有 10000 个顶点。ML Deformer 输出每个顶点的 XYZ offset。隐藏层为 [512, 256, 128]，输出层为 linear。请计算网络总参数量（忽略 bias）。
> Answer: 768×512 + 512×256 + 256×128 + 128×30000 = 393,216 + 131,072 + 32,768 + 3,840,000 = 4,397,056 ≈ 4.4M params

> **Q3 (Medium)**：训练数据有 1000 帧，每帧 bone transforms 和 vertex offsets。我们使用 MSE Loss：L = (1/N) Σ||y_pred - y_target||²。如果某个顶点在 frame 0 和 frame 1000 的 offset 差异很大，说明什么？如何处理这种 high-frequency 变化？
> Answer: 说明该顶点对 pose 变化高度敏感（如面部顶点）。处理：增加网络 capacity、添加 temporal smoothing loss、使用 PCA 预压缩 vertex space。

> **Q4 (Hard)**： bone-driven deformer 中，输入是 bone transforms B，输出是 vertex offsets V。证明：如果 B 经过 global rotation R（即 B' = R·B），输出的 V 应该不变（因为 mesh 和 skeleton 一起旋转）。如何让网络学习这种 equivariance？
> Answer: 在输入前将 bone transforms 转换到 local space / root-relative space；或在网络中加入 rotation-invariant features（如 bone lengths + relative angles）。

> **Q5 (Hard)**：ONNX Runtime 在 UE5 中使用 GPU Execution Provider。Inference  latency 为 0.5ms，但 CPU 拷贝到 GPU 需要 0.3ms。如果每帧有 10 个角色同时使用 ML Deformer，如何优化总延迟？
> Answer: Batch inference（合并多个角色的 bone transforms 为一个 batch）、使用 GPU 持久化内存（避免每帧 alloc/free）、将 bone data 直接生成在 GPU（避免 CPU→GPU 拷贝）。

**你必须做**：在纸上或代码中完成所有题目，再核对答案。

---

## 任务 2：ML Deformer 最小实现脚手架（AI 生成，你填充）

**输入**："我想写一个最小可运行的 ML Deformer（Python + PyTorch），训练数据从简单的弹簧-质量系统生成。生成脚手架"

**AI 输出**：
```python
#!/usr/bin/env python3
"""Minimal ML Deformer: Train a simple MLP to predict vertex offsets from bone angles."""

import torch
import torch.nn as nn
import numpy as np

class SimpleMLDeformer(nn.Module):
    """MLP: bone angles -> vertex offsets"""
    def __init__(self, n_bones, n_vertices, hidden_dims=[64, 128, 64]):
        super().__init__()
        self.n_bones = n_bones
        self.n_vertices = n_vertices
        # TODO(HUMAN): 构建 MLP 层
        # Input: n_bones * 3 (Euler angles or quaternion)
        # Hidden: hidden_dims
        # Output: n_vertices * 3 (XYZ offsets)
        pass
    
    def forward(self, bone_angles):
        # TODO(HUMAN): 实现前向传播
        # bone_angles: (batch, n_bones*3)
        # return: (batch, n_vertices*3)
        pass

def generate_training_data(n_samples=1000, n_bones=4, n_vertices=100):
    """Generate synthetic training data from a spring-mass system."""
    # TODO(HUMAN): 实现训练数据生成
    # 1. 随机生成 bone angles
    # 2. 根据物理模型（弹簧-质点或简单三角函数）计算 vertex offsets
    # 3. 返回 X (bone angles), Y (vertex offsets)
    pass

def train(model, X, Y, epochs=100, lr=1e-3):
    """Train the deformer with MSE loss."""
    # TODO(HUMAN): 实现训练循环
    # 1. 定义 optimizer (Adam) 和 loss (MSELoss)
    # 2. 训练 epochs 次
    # 3. 每 10 个 epoch 打印 loss
    # 4. 返回训练后的 model
    pass

def export_to_onnx(model, n_bones, output_path="ml_deformer.onnx"):
    """Export trained model to ONNX for UE5 import."""
    # TODO(HUMAN): 使用 torch.onnx.export 导出模型
    # 注意：input_names, output_names, dynamic_axes 设置
    pass

if __name__ == "__main__":
    # TODO(HUMAN): 主流程
    # 1. generate_training_data
    # 2. instantiate SimpleMLDeformer
    # 3. train
    # 4. export_to_onnx
    pass
```

**你必须做**：填充所有 `TODO(HUMAN)`，运行并验证训练 loss 下降。

**测试命令**：
```bash
python minimal_ml_deformer.py
# 检查：loss 是否收敛？ONNX 文件是否生成？
```

---

## 任务 3：你的 ML Deformer 代码 Review（AI 执行）

**AI 检查清单**：
- [ ] 是否处理了 batch dimension？（训练时是 batch，Inference 时可能是 single sample）
- [ ] 是否对输入数据进行了归一化？（bone angles 和 vertex offsets 的 scale 差异巨大）
- [ ] 是否过拟合？（训练 loss 很低但测试 loss 很高 → 需要 regularization / dropout）
- [ ] 是否考虑了拓扑信息？（相邻顶点应该有相似的 offset，网络是否隐式学习到了？）
- [ ] ONNX 导出时是否设置了正确的 opset version？（UE5.8 ONNX Runtime 通常要求 opset ≥ 11）
- [ ] 输入输出维度是否与 UE5.8 `MLDeformer` 期望的一致？

**AI 输出**：发现的 bug 列表 + 修复建议（逐行）

**你必须做**：理解每个 bug 的根因，手动修复。

---

## 任务 4：概念直觉（AI 解释，你内化）

| 概念 | AI 解释类比 |
|------|------------|
| **ML Deformer** | "就像学开车。你先在模拟器（Chaos Physics）里开 1000 小时，收集所有转向-轨迹数据。然后训练一个神经网络，让它记住 '方向盘转到这个角度，车应该走到这个位置'。真正上路时，你不再需要模拟器，只需看方向盘角度，网络就能预测车的轨迹。" |
| **Latent Space** | "就像压缩文件。原始 vertex offsets 有 10000×3=30000 个数字，但大部分变化是有规律的（肌肉一起收缩、皮肤一起拉伸）。Latent space 把这些规律提炼成 128 个数字，网络先在 latent space 计算，再解码成 30000 个偏移。" |
| **Inference vs Training** | "Training 是期末考试前的复习——你反复做题、对答案、改错。Inference 是考试本身——你只做一遍，不能回头看答案。Training 需要 backward pass（计算梯度），Inference 只需要 forward pass。" |
| **Bone Driver** | "就像木偶戏。骨骼是木偶的操纵杆（bone transforms），顶点是木偶的表面（mesh）。Bone driver 就是学习 '操纵杆怎么动，表面就怎么变形'。这样 runtime 只需要知道操纵杆位置，不需要计算表面物理。" |

**你必须做**：用你自己的话向一个假想的初级动画师解释这些概念。

---

## 今日 AI 禁区

- ❌ 让 AI 写完整 ML Deformer 训练代码（数据生成和 loss 计算必须自己理解）
- ❌ 让 AI 直接给数学题答案（矩阵运算和 loss 推导必须自己算）
- ❌ 不做费曼输出（必须用自己的话解释 latent space 和 bone driver）
- ❌ 直接应用修复不理解根因（每个 bug 都要理解为什么发生）

---

## 完成检查清单

- [ ] 5 道数学/ML 题已完成并核对
- [ ] 最小 ML Deformer 核心逻辑已填充（训练 + ONNX 导出）
- [ ] AI code review 的 bug 已理解并手动修复
- [ ] 4 个核心概念已用自己的话解释
- [ ] 代码和笔记已写入 Obsidian

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 2.5 小时*  
*产出：5 道数学练习 + 1 个最小 ML Deformer + 1 次 Code Review*
