---
tags: [routine/AI-tasks, topic/NeuralRendering, day/Sunday]
aliases: []
---

# 周日：AI 任务清单 — Neural Rendering 项目收尾与周复盘

> **人类目标**：完成 mini-ML Deformer 项目的最终集成，输出文档，做周复盘。  
> **AI 任务**：协助 debug、润色文档、生成复盘模板，绝不写核心代码。

---

## 上午：项目收尾（2h）

### 任务 1：集成测试辅助（AI 执行）

**AI 输出**：测试矩阵

| 测试场景 | 输入 | 预期输出 | 验证方法 |
|----------|------|----------|---------|
| ONNX 模型加载 | 有效 `.onnx` 文件 | Session 创建成功，无 error log | 断言 + UE_LOG |
| ONNX 模型加载（无效） | 损坏/不兼容 `.onnx` | 返回 false，输出 error code | 断言 |
| 输入维度正确 | 64 bones × 12 float = 768 dim | Inference 成功，输出非 NaN | 断言 + 数值检查 |
| 输入维度错误 | 63 bones × 12 float = 756 dim | 返回 dimension mismatch error | 断言 |
| 推理输出范围 | 正常 bone transforms | Vertex offsets 在 [-1, 1] 范围内（归一化后） | 数值检查 |
| 叠加到 mesh | 正常 vertex offsets | Skinned position + offset 正确应用 | RenderDoc 抓帧 |
| 多帧稳定性 | 连续 100 帧相同 pose | 输出完全一致（无随机性） | 对比 |
| 性能测试 | 1 角色 / 10 角色 | Inference latency < 0.5ms / < 5ms | `stat unit` |
| 内存测试 | 加载 1 个模型 | 内存增长 < 5MB | `stat memory` |
| 边界测试 | 极端 pose（T-pose / 极限旋转） | 输出合理，无顶点爆炸 | 视觉检查 |

**你必须做**：运行每个测试，记录实际结果。

---

### 任务 2：性能 Baseline（AI 执行，你测量）

**AI 输出**：Benchmark 方案

| 指标 | 测量方法 | 目标 |
|------|----------|------|
| 模型加载时间 | `BeginPlay` 到 `RunInference` 首次调用 | < 100ms |
| 单角色 Inference latency | `Tick` 中 `RunInference` 耗时 | < 0.5ms |
| 10 角色 Inference latency | 10 个独立 `Session` 或 1 个 batched | < 5ms |
| 内存占用（模型） | ONNX 模型加载后 RSS 增长 | < 10MB（FP32）/ < 5MB（FP16） |
| 内存占用（运行时） | 每帧 input/output tensor + vertex buffer | < 1MB |
| 顶点变形精度 | 对比 PyTorch 输出 vs ONNX Runtime 输出 | MSE < 1e-5 |
| 跨平台一致性 | PC DirectML vs CPU EP | 输出差异 < 1e-4 |

**你必须做**：实际运行 benchmark，记录数据。

---

## 下午：文档与复盘（1-2h）

### 任务 3：项目文档生成（AI 执行，你填充）

**AI 输出**：README 模板

```markdown
# mini-ml-deformer
> 一个最小可运行的 ML Deformer 实验项目，从 PyTorch 训练到 UE5.8 ONNX Runtime 推理

## 原理
- 使用 PyTorch 训练一个 MLP，学习 bone transforms → vertex offsets 的映射
- 训练数据来自弹簧-质量系统模拟（可替换为 Chaos Physics）
- 导出 ONNX，在 UE5.8 中通过 NeuralNetworkEngine 执行推理

## 工具清单
| 工具 | 描述 | 示例 |
|------|------|------|
| `train.py` | 训练 MLP 并导出 ONNX | `python train.py --bones 64 --verts 1000` |
| `test_inference.py` | 验证 ONNX 与 PyTorch 输出一致 | `python test_inference.py` |
| `UE5 Test Project` | 加载 ONNX 并运行推理 | 打开 `MLDeformerTest.uproject` |

## 快速开始
```bash
# 训练
pip install -r requirements.txt
python training/train.py
python training/export_onnx.py

# 验证
python tests/test_inference.py

# UE5：将生成的 ml_deformer.onnx 放入 Content/Models/，编译运行
```

## 性能
| 指标 | 数值 |
|------|------|
| 模型加载时间 | _ms |
| 单角色 Inference | _ms |
| 10 角色 Inference | _ms |
| 模型内存 | _MB |
| 运行时内存 | _MB |
| 精度 MSE | _ |

## 学习笔记
见 [Obsidian Vault](link)
```

**你必须做**：填写所有数据和测量结果。

---

### 任务 4：周复盘辅助（AI 执行，你补充）

**AI 输出**：数据总结 + 模式发现 + 下周建议

**数据总结模板**：
- 本周完成：_ 篇论文笔记、_ 个数学练习、_ 个代码实现、_ 次测验
- 技术掌握度（自评 1-10）：ML Deformer Pipeline _、ONNX Runtime _、UE5 C++ 集成 _
- 时间投入：_ 小时（目标 _ 小时）

**模式发现**：
- 最困难的部分：_（通常是 dimension mismatch / normalization / memory layout）
- 最有价值的发现：_
- 最需要加强的：_

**下周建议**：
- 真实角色训练（Mixamo / Daz3D）
- 布料/皮肤专项
- 与 Chaos Physics 联合训练管线
- 多角色 batch inference 优化

**你必须做**：补充主观体验（能量、顿悟、困难、意外发现）。

---

## 今日 AI 禁区

- ❌ 让 AI 替你运行测试和 benchmark
- ❌ 让 AI 替你写项目文档的核心技术描述
- ❌ 让 AI 替你写周复盘日记
- ❌ 让 AI 替你决定下周计划

---

## 完成检查清单

- [ ] Mini-ML Deformer 集成测试全部通过（10/10）
- [ ] 性能 benchmark 已运行，数据已记录
- [ ] README 文档已填写并发布到 GitHub
- [ ] 周复盘已完成，主观体验已补充
- [ ] 下周计划已调整并写入 Obsidian
- [ ] 所有链接（GitHub、博客、Obsidian）已更新到知识库

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 3-4 小时*  
*产出：1 个完整 ML Deformer 实验 + 1 份文档 + 1 次周复盘 + 下周计划*
