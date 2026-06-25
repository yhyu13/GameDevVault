---
tags: [routine/master-index, topic/NeuralRendering, system/reference]
aliases: [NeuralRendering-AI-Master]
---

# Neural Rendering 主题 — AI 任务总览

> 这是 Neural Rendering（ML Deformer / Neural Rendering）学习周期的「AI 任务控制塔」。
> **核心原则**：AI 只做脚手架，你来做硬工作。

---

## 快速导航

| 日期 | 主题 | AI 任务文件 | 人类核心任务 |
|------|------|------------|-------------|
| [[周一]] | 前沿技术输入 | [[01_Monday/AI-Tasks]] | 精读 ML Deformer 论文 + UE5.8 源码追踪 |
| [[周二]] | 专项技能突破 | [[02_Tuesday/AI-Tasks]] | 神经网络数学 + 最小 Deformer 实现 |
| [[周三]] | 强制游玩观察 | [[03_Wednesday/AI-Tasks]] | 观察 ML 驱动动画的游戏案例 |
| [[周四]] | 工程化与工具链 | [[04_Thursday/AI-Tasks]] | C++ Neural 模块 + ONNX 工具脚本 |
| [[周五]] | 轻量复盘 | [[05_Friday/AI-Tasks]] | 测验 + 整理 + 跨主题链接 |
| [[周末]] | 项目实战 | [[06_Weekend/AI-Tasks]] | Mini ML Deformer + ONNX Inference |
| [[周日]] | 项目收尾 | [[07_Sunday/AI-Tasks]] | 集成测试 + 性能 Benchmark + 复盘 |
| [[每周]] | 外部接触 | [[08_Weekly/AI-Tasks]] | 技术社交 + 开源贡献 |

---

## Neural Rendering 是什么

Neural Rendering 是 UE5.8 中引入的 **AI 驱动几何与动画** 技术体系，核心是通过神经网络学习高保真模拟/动画，然后在运行时以极低开销进行 Inference：

- **ML Deformer**：用神经网络学习 mesh deformation，从高精度模拟（Chaos Physics / FEM / 肌肉模拟）生成训练数据，训练后在 runtime 以 MLP Inference 替代昂贵模拟
- **NeuralNetworkEngine**：UE5.8 内置的 ONNX Runtime 集成模块，提供通用神经网络推理能力
- **核心模块**：
  - `MLDeformer` — 运行时 ML Deformer 骨架（Skeletal + Vertex Deformer）
  - `NeuralNetworkEngine` — ONNX Runtime 封装层，跨平台（PC/Console/Mobile）
  - `SkeletalDeformer` — 骨骼驱动变形，输入 bone transforms，输出 vertex offsets
  - `GeometryDeformer` — 通用几何变形，支持静态 mesh / procedural mesh
- **使用场景**：
  - 肌肉与皮肤变形（高保真角色动画）
  - 布料动态模拟（替代离线布料解算）
  - 面部表情动画（从 blendshape 到 neural blendshape）
  - 基于物理的动画（Physics-based animation compression）

---

## 与现有 7 个主题的关系

```
        ┌─────────────────────────────────────┐
        │      Neural Rendering (#8)          │
        │    AI 驱动几何 / 动画压缩 / 推理    │
        │   （连接物理模拟与实时渲染的桥梁）   │
        └─────────────────────────────────────┘
                      │
    ┌─────────┬───────┼───────┬─────────┐
    ▼         ▼       ▼       ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Lumen  │ │ Nanite │ │  VGM   │ │  VSM   │ │ Chaos  │
│ 光照   │ │ 几何   │ │ 植被   │ │ 阴影   │ │ 物理   │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
┌────────────┐     ┌────────────┐
│ WaterPlugins │     │  UnrealMCP │
│ 水体         │     │  AI 工具链 │
└────────────┘     └────────────┘
```

Neural Rendering 是 **桥梁型主题** 而非独立渲染特性：
- **Chaos Physics**（#5）：为 ML Deformer 提供训练数据（高保真模拟序列 → 训练样本）
- **Nanite**（#2）：Neural Rendering 输出的变形 mesh 可以被 Nanite 进一步细分和 LOD
- **Lumen**（#1）：神经渲染的角色/物体仍然参与 Lumen 全局光照，变形后的顶点位置影响 GI 计算
- **VSM**（#4）：ML Deformer 变形后的 mesh 使用 VSM 生成阴影，变形精度影响 shadow bias
- **UnrealMCP**（#7）：可通过 MCP 查询 ML Deformer 的 training status、inference latency、model accuracy
- **VGM**（#3）：植被 wind animation 可以用类似 ML Deformer 的方式压缩（instance 级别 neural animation）
- **WaterPlugins**（#6）：水体模拟的离线训练数据可以喂给 Neural Network Engine 做实时 wave inference

---

## 相关参考

- [[../References/AI-Augmentation-Reference]] — AI 辅助学习完整参考手册
- [[../UE58-Topic-Exploration-Report]] — UE58 主题探索完整报告（优先级评分）
- [[../ChaosPhysics/00-Master-Index]] — Chaos 物理模拟是 ML Deformer 训练数据的主要来源
- [[../UnrealMCP/00-Master-Index]] — 可用 MCP 查询 Neural Rendering 状态
- [[../../01-论文笔记库]] — ML Deformer / Neural Animation 论文笔记
- [[../../02-引擎源码分析库]] — MLDeformer / NeuralNetworkEngine 源码分析
- [[../../99-Templates/论文笔记]] — 论文/规范笔记模板

---

## 每周更新日志

| 周 | 主题 | 状态 |
|----|------|------|
| W1 | ML Deformer 基础：Training Data Generation + MLP Architecture + UE5.8 Plugin | 🔄 进行中 |
| W2 | NeuralNetworkEngine 源码：ONNX Runtime 集成 + 跨平台推理管线 | ☐ 待开始 |
| W3 | 自定义 ML Deformer：训练 → 导出 ONNX → 导入 UE5 → 运行时 Inference | ☐ 待开始 |
| W4 | 集成实战：肌肉/皮肤 Mini-Project + 性能 Benchmark + 与 Chaos 联合训练 | ☐ 待开始 |

---

## 推荐学习路径

**如果你同时学多个主题**：
- **并行**：Neural Rendering 作为 "副线"，每天 30 分钟学习 ML 基础，周末集中训练模型和实验
- **串行**：先完成 Chaos Physics（#5），因为 ML Deformer 的训练数据来自物理模拟；再学 Neural Rendering，理解如何把模拟压缩成神经网络

**Neural Rendering 的特殊性**：
- 需要 **ML 基础**（神经网络、反向传播、损失函数）+ **图形学基础**（vertex deformation、skinning、mesh topology）
- 不像纯渲染主题需要大量 GPU 管线知识，更像 "ML + 动画 + 工程优化"
- 学习曲线：中高（比 Lumen 概念简单，但需理解 training pipeline 和 inference optimization）

---

*This is a living document. Update it as the Neural Rendering topic progresses.*
