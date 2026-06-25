---
tags: [routine/AI-tasks, topic/MassAI, topic/LearningAgents, day/Sunday]
aliases: []
---

# 周日：AI 任务清单 — MassAI 项目收尾与周复盘

> **人类目标**：完成 Mini-MassAI 项目的最终集成，输出文档，做周复盘。  
> **AI 任务**：协助 debug、润色文档、生成复盘模板，绝不写核心代码。

---

## 上午：项目收尾（2h）

### 任务 1：集成测试辅助（AI 执行）

**AI 输出**：测试矩阵

| 测试场景 | 输入 | 预期输出 | 验证方法 |
|----------|------|----------|---------|
| Entity 生成 | Spawner 配置 100 个 Agent | 场景中生成 100 个可见 Agent | 肉眼 + `stat mass` |
| 移动处理器 | 运行 100 帧 | Agent 位置变化，无穿模 | 录屏 + 位置日志 |
| 边界反弹 | Agent 移动到 X=1000 | 速度方向反转，不越界 | 断点 + UE_LOG |
| 避障处理器 | 两个 Agent 相向而行 | 接近时偏移路径，不重叠 | 录屏 |
| SmartObject 注册 | 放置 Bench SO | SO Subsystem 显示已注册 | 断点 |
| Slot 分配 | Agent 靠近 Bench | Agent 获得 Slot，开始 Sit 动画 | 录屏 + 状态日志 |
| Slot 释放 | Agent 离开 Bench | Slot 释放，下一个 Agent 可占用 | 状态日志 |
| StateTree 切换 | Agent 从 Idle 到 Walk | 状态评估正确，速度变化 | 断点 + StateTree Debug |
| 性能测试 | 1000 个 Agent | 帧率 ≥ 60fps | `stat fps` |
| 内存测试 | 运行 5 分钟 | 内存无泄漏 | `stat memory` |

**你必须做**：运行每个测试，记录实际结果。

---

### 任务 2：性能 Benchmark（AI 执行，你测量）

**AI 输出**：Benchmark 方案

| 指标 | 测量方法 | 目标 |
|------|----------|------|
| Entity 数量 | `stat mass` 中的 Entity Count | 支持 1000+ |
| Processor 耗时 | `stat mass` 中的 Processor 时间 | Movement < 0.5ms, Avoidance < 1ms |
| 帧率 | `stat fps` | ≥ 60fps @ 1000 Agents |
| 内存占用 | `LLM` 或 `stat memory` | 每 Agent < 1KB（不含渲染） |
| Chunk 遍历效率 | 自定义 `UE_LOG` | 每个 Chunk 处理时间 < 0.01ms |
| SmartObject 查询延迟 | 自定义计时 | 查询最近 Bench < 0.1ms |
| StateTree 评估耗时 | 自定义计时 | 每 Agent 每帧 < 0.01ms |

**你必须做**：实际运行 benchmark，记录数据。

---

## 下午：文档与复盘（1-2h）

### 任务 3：项目文档生成（AI 执行，你填充）

**AI 输出**：README 模板

```markdown
# Mini-MassAI
> 一个基于 UE5 MassEntity 的 Mini AI 系统，演示自定义 Processor、SmartObject 和 StateTree

## 功能清单
| 功能 | 描述 | 技术要点 |
|------|------|----------|
| 移动处理器 | 批量更新 Agent 位置 | SOA Chunk 遍历、Cache 友好 |
| 避障处理器 | 基于距离的邻居避让 | Spatial Hash 查询 |
| 长椅 SmartObject | 可坐下的交互对象 | Slot 分配与释放 |
| 状态树 | Idle → Walk → Sit | StateTree 条件评估 |

## 快速开始
1. 将插件复制到 Projects/YourProject/Plugins/
2. 在 Build.cs 中添加 `MassEntity`, `MassAI`, `SmartObjects`, `StateTree` 依赖
3. 在场景中放置 `BP_MiniMassSpawner` 和 `BP_BenchSmartObject`
4. 运行游戏

## 性能
| 指标 | 数值 |
|------|------|
| 最大 Agent 数量 | _ |
| 帧率（1000 Agents）| _ fps |
| Movement Processor 耗时 | _ ms |
| 每 Agent 内存占用 | _ bytes |

## 学习笔记
见 [Obsidian Vault](link)

## 架构图
[插入你的 Processor/SmartObject/StateTree 关系图]
```

**你必须做**：填写所有数据和测量结果。

---

### 任务 4：周复盘辅助（AI 执行，你补充）

**AI 输出**：数据总结 + 模式发现 + 下周建议

**数据总结模板**：
```markdown
## 本周 MassAI 学习数据

### 量化数据
- 源码阅读：_ 个文件
- 代码产出：_ 行 C++（Processor + Fragment + SmartObject + StateTree）
- 测验得分：_%（周五）
- 性能基准：1000 Agents @ _ fps
- 博客：_ 篇（草稿/发布）

### 质量数据
- 最困难的概念：_
- 最大的顿悟：_
- 最意外的发现：_
- 最耗时的 bug：_
```

**下周建议（AI 生成）**：
- 如果 StateTree 还没跑通：下周重点 StateTree 调试
- 如果 LearningAgents 还没开始：下周开始 RL 训练
- 如果性能不够：下周优化 Spatial Hashing 和 LOD

**你必须做**：补充主观体验（能量、顿悟、困难、意外发现）。

---

## 今日 AI 禁区

- ❌ 让 AI 替你运行测试和 benchmark（必须自己操作 Editor）
- ❌ 让 AI 替你写项目文档的核心技术描述（必须用自己的代码）
- ❌ 让 AI 替你写周复盘日记（必须自己的感受）
- ❌ 让 AI 替你决定下周计划（必须自己评估优先级）

---

## 完成检查清单

- [ ] Mini-MassAI 集成测试全部通过（10/10）
- [ ] 性能 benchmark 已运行，数据已记录（帧率、Processor 耗时、内存）
- [ ] README 文档已填写并发布到 GitHub
- [ ] 周复盘已完成，主观体验已补充
- [ ] 下周计划已调整并写入 Obsidian
- [ ] 所有链接（GitHub、博客、Obsidian）已更新到知识库

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 3-4 小时*  
*产出：1 个完整 Mini-MassAI 系统 + 1 份文档 + 1 次周复盘 + 下周计划*
