---
tags: [routine/AI-tasks, topic/NeuralRendering, day/Weekly]
aliases: []
---

# 每周：AI 任务清单 — Neural Rendering 技术社交

> **人类目标**：与 ML 图形学社区和 UE5 开发者交流，验证技术路线。  
> **AI 任务**：润色措辞、生成问题、准备资料，绝不替代社交互动。

---

## 任务 1：技术社交媒体帖子（AI 执行）

**输入**：你的 raw 内容，如 "这周学了 ML Deformer，从 chaos physics 训练数据到 onnx inference"

**AI 输出**：LinkedIn 版 / Twitter 版 / 知乎版

**示例（LinkedIn 版）**：
> 🧠 本周完成：从零搭建一个 ML Deformer 实验项目
>
> 用 Chaos Physics 生成训练数据 → PyTorch 训练 MLP → 导出 ONNX → 在 UE5.8 中通过 NeuralNetworkEngine 实时推理。
>
> 关键发现：
> 1. 归一化（normalization）是精度关键—— bone transforms 和 vertex offsets 的 scale 差异巨大
> 2. ONNX Runtime 的 DirectML EP 在 PC 上延迟 < 0.5ms，完全可以用于实时角色
> 3. Dimension mismatch 是最大坑点——PyTorch 和 UE5 的 matrix flatten 顺序必须一致
>
> 下一步：尝试真实角色（Mixamo）和布料模拟。
>
> #GameDev #UnrealEngine #MachineLearning #NeuralRendering #MLDeformer

**你必须做**：确认润色后仍表达你的真实发现，自己发帖。

---

## 任务 2：冷消息起草（AI 执行，你个性化）

**输入**：你想联系一位在 ML Deformer / Neural Rendering 领域活跃的开发者或研究者（如 Epic Games ML 团队、GDC 演讲者、论文作者）

**AI 输出**：礼貌模板（150 字内，展示你做过的功课）

**示例**：
> 您好 [名字]，
>
> 我是 [你的名字]，正在研究 UE5.8 的 ML Deformer 和 Neural Rendering 管线。我搭建了一个从 Chaos Physics 训练数据生成到 ONNX Runtime 实时推理的完整实验项目，遇到了一些关于 bone-driven vs vertex-driven architecture 的选型困惑。
>
> 想请教您：在真实角色（>100 bones, >10000 vertices）上，如何平衡 network capacity 和 inference latency？不知道您是否有 15 分钟时间交流？
>
> 我的项目仓库：[GitHub 链接]
>
> 期待您的回复，谢谢！
> [你的名字]

**你必须做**：添加具体细节（引用对方的论文/演讲/博客），自己发送。

---

## 任务 3：开源贡献（AI 执行）

**AI 建议**：匹配你的 Neural Rendering 技能到开源项目

| 项目 | 匹配度 | 建议贡献方向 |
|------|--------|-------------|
| [EpicGames/UnrealEngine](https://github.com/EpicGames) | 高 | 反馈 MLDeformer / NeuralNetworkEngine 的 Issue，提交文档改进 PR |
| [microsoft/onnxruntime](https://github.com/microsoft/onnxruntime) | 中 | 修复与 UE5 集成相关的 bug，或添加 DirectML 优化文档 |
| [PyTorch/TensorFlow 社区](https://github.com/pytorch) | 中 | 分享从 PyTorch 到 UE5 ONNX 的导出 best practice |
| [GDC Vault / UE5 社区](https://dev.epicgames.com) | 中 | 回答论坛上关于 ML Deformer 的问题，分享实验结果 |
| [Godot Engine](https://github.com/godotengine) | 低 | 比较 Godot vs UE5 的 neural animation 支持，写分析报告 |

**你必须做**：自己找 issue、读代码、写修复、提 PR 或评论。

---

## 任务 4：社区资源分享（AI 执行）

**AI 建议**：根据你本周学习，推荐 3 个资源

| 资源 | 类型 | 适合谁 | 你的评价 |
|------|------|--------|----------|
| Epic Games ML Deformer 官方文档 | 文档 | UE5 开发者入门 | 结构清晰，但缺少 troubleshooting |
| "Neural Animation: A Survey" (论文) | 论文 | 想理解全貌的人 | 覆盖全面，从 character 到 fluid 都有 |
| ONNX Runtime 官方示例 | 代码 | 需要跨平台推理的人 | 与 UE5 集成时需要额外处理 memory layout |

**你必须做**：在 Twitter / 知乎 / Discord 上分享你的评价，引发讨论。

---

## 今日 AI 禁区

- ❌ 让 AI 替你发帖（社交互动必须自己完成）
- ❌ 让 AI 替你联系行业人士（必须自己发送和跟进）
- ❌ 让 AI 替你写开源贡献代码（必须自己读 issue 和写修复）
- ❌ 让 AI 生成虚假评价（必须基于自己的真实学习体验）

---

## 完成检查清单

- [ ] 至少发了 1 个技术社交媒体帖子（关于 ML Deformer / Neural Rendering）
- [ ] 至少与 1 位行业人士交流（ML 图形学或 UE5 开发者）
- [ ] 至少给 1 个开源项目提了 Issue/PR/Comment（UE5 / ONNX Runtime / PyTorch）
- [ ] 交流收获已整理到 Obsidian 职业复盘日志
- [ ] 技术雷达已更新（如有新的 neural rendering 工具或论文发现）

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2-3 小时（参加活动 + 社交 + 整理）*  
*产出：N 个新联系 + 1 次开源贡献 + 技术路线验证*
