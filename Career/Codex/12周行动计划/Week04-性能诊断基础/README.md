---
tags: [career/AI训练, career/UE5, career/week04]
aliases: [Week04 UE 性能诊断]
---

# Week 04 - 性能诊断基础

## 目标

让 AI 根据 Profile 信息判断瓶颈，而不是泛泛建议优化。

- 人类必须学会：CPU/GPU/内存/IO 诊断入口和证据边界。
- AI 必须学会：先定位 bound 类型，再谈优化方案。

## AI 支持边界

- AI 做：指标摘要、决策树格式化、题面草稿、对比表。
- 人类做：标注真实瓶颈、确认优化建议副作用、按 Rubric 打分。
- AI 不能替代：判断性能瓶颈是否真实存在。

## Day-by-day Action Plan

| Day | Action | AI Support | Test | Result | Self Evaluate |
|-----|--------|------------|------|--------|---------------|
| D1 | 准备 Stat Unit、Stat GPU、Unreal Insights 或 RenderDoc 样例 | 整理指标含义 | 标注关键瓶颈 | `UE-Perf-input-cases.md` | 是否包含足够上下文 |
| D2 | 写性能诊断决策树 | 帮格式化 | 用 2 个样例验证流程 | `UE-Perf-decision-tree.md` | 是否先判断 bound 类型 |
| D3 | 构造 UE-Perf-001 任务 | 生成题面草稿 | 确认输入不泄露项目 | `UE-Perf-001-task.md` | 是否能区分高手和泛泛回答 |
| D4 | 写专家答案 | 拆分证据和建议 | 核对优化建议副作用 | `UE-Perf-001-answer.md` | 是否说明风险 |
| D5 | 跑 AI 输出 | 作为被测对象 | 检查是否直接套模板 | `UE-Perf-001-model-output.md` | 是否有空泛建议 |
| D6 | 写 Rubric 和失败模式 | 做对比表 | 确认评分标准 | `UE-Perf-rubric.md` | 是否惩罚无证据建议 |
| D7 | Phase 1 复盘 | 汇总前 4 周资产 | 判断下一阶段补什么 | `Phase01-review.md` | 是否已有三类基础资产 |

## Weekly Test

给 AI 一个 GPU bound 样例，看它是否错误建议优化 GameThread。

## Outcome Checklist

- [ ] 1 个 Perf 任务包
- [ ] 1 个性能诊断决策树
- [ ] 1 份 Perf Rubric
- [ ] 1 份 Phase 1 复盘

## Self Evaluate

| 维度 | 分数 | 备注 |
|------|------|------|
| 真实性 |  |  |
| 证据链 |  |  |
| 可执行性 |  |  |
| AI 训练价值 |  |  |
| 连接性 |  |  |
| 总分 |  |  |

## 关联

- [[UE5-AI训练方向12周行动计划]]
- [[性能优化]]
- [[Unreal Insights]]
- [[RenderDoc]]

