---
tags: [career/AI训练, career/UE5, career/week02]
aliases: [Week02 UE Debug 日志诊断]
---

# Week 02 - UE Debug 日志诊断

## 目标

训练 AI 从日志中建立证据链，而不是看到关键词就直接归因。

- 人类必须学会：Crash、Cook、Shader 编译、Asset 加载日志的关键证据。
- AI 必须学会：区分事实、推测、缺失信息。

## AI 支持边界

- AI 做：日志摘要、决策树格式化、题面草稿、偏好样本 JSONL 草稿。
- 人类做：标注关键证据行、写最终结论、确认诱导项是否真实。
- AI 不能替代：判断日志证据是否足以证明因果。

## Day-by-day Action Plan

| Day | Action | AI Support | Test | Result | Self Evaluate |
|-----|--------|------------|------|--------|---------------|
| D1 | 收集 2 类日志任务：真错误和干扰样本 | 做日志摘要 | 标注关键证据行 | `UE-Debug-log-cases.md` | 是否有正例和反例 |
| D2 | 写 Crash 或 Cook 诊断专家流程 | 整理成决策树 | 用旧日志走一遍流程 | `UE-Debug-decision-tree.md` | 是否能落到搜索词 |
| D3 | 构造任务 002：高内存但不一定 OOM | 生成题面草稿 | 检查诱导项是否合理 | `UE-Debug-002-task.md` | 是否能暴露过早归因 |
| D4 | 写专家答案和 Rubric | 起草评分项 | 删除泛泛项 | `UE-Debug-002-rubric.md` | Rubric 是否可评分 |
| D5 | 跑 AI 并记录输出 | 作为被测对象 | 检查是否引用证据 | `UE-Debug-002-model-output.md` | 是否有明确失败模式 |
| D6 | 生成偏好样本：好答案 vs 差答案 | 转 JSONL 草稿 | 确认 chosen/rejected 理由 | `UE-Debug-002-preference.jsonl` | 偏好理由是否具体 |
| D7 | 周复盘和连接 | 整理链接建议 | 链接 [[Cook]]、[[内存管理]]、[[Unreal Insights]] | `Week02-review.md` | 是否沉淀日志诊断原则 |

## Weekly Test

给 AI 缺失关键证据的日志，看它是否会承认信息不足。

## Outcome Checklist

- [ ] 2 个 Debug 任务
- [ ] 1 个日志决策树
- [ ] 1 条偏好样本
- [ ] 1 份错误模式总结
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
- [[Cook]]
- [[内存管理]]
- [[Unreal Insights]]

