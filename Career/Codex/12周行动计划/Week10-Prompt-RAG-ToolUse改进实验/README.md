---
tags: [career/AI训练, career/UE5, career/week10]
aliases: [Week10 Prompt RAG ToolUse]
---

# Week 10 - Prompt / RAG / Tool-use 改进实验

## 目标

不直接假设训练，先验证 Prompt、检索和工具流程能提升多少。

- 人类必须学会：把改进手段和失败模式对应起来。
- AI 必须学会：需要查证时用资料和工具，不凭空回答。

## AI 支持边界

- AI 做：失败模式汇总、Prompt 草稿、RAG 材料整理、Tool-use 流程草案、差异表。
- 人类做：排序失败模式、确认资料版本、定义工具触发条件、判断提升是否真实。
- AI 不能替代：实验设计有效性和提升真实性判断。

## Day-by-day Action Plan

| Day | Action | AI Support | Test | Result | Self Evaluate |
|-----|--------|------------|------|--------|---------------|
| D1 | 选择 3 个高频失败模式 | 汇总候选 | 按业务价值排序 | `failure-priority.md` | 是否优先高价值问题 |
| D2 | 设计 Prompt 改进 | 起草系统提示和输出格式 | 检查是否过拟合 | `prompt-experiment-01.md` | 是否明确预期提升 |
| D3 | 设计 RAG 输入材料 | 整理知识片段 | 确认资料真实和版本 | `rag-pack-01.md` | 是否避免脏知识进入 |
| D4 | 设计 Tool-use 流程 | 起草步骤 | 定义何时查日志/源码/命令 | `tool-use-flow-01.md` | 是否有工具触发条件 |
| D5 | 复测 3 个任务 | 作为改进后被测对象 | 同 Rubric 打分 | `rerun-01-results.md` | 是否同标准复测 |
| D6 | 对比基线和复测 | 生成差异表 | 判断提升是否真实 | `baseline-vs-rerun-01.md` | 是否避免主观乐观 |
| D7 | 周复盘 | 汇总实验结论 | 决定下一步训练需求 | `Week10-review.md` | 是否说清三类改进作用 |

## Weekly Test

同一个任务前后评分至少提升 2 分，才算实验有效。

## Outcome Checklist

- [ ] 1 个 Prompt 实验
- [ ] 1 个 RAG 包
- [ ] 1 个 Tool-use 流程
- [ ] 1 份复测对比
- [ ] 1 份周复盘

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
- [[技术雷达与工具栈]]
- [[UE5]]

