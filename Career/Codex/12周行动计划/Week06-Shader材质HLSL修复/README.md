---
tags: [career/AI训练, career/UE5, career/week06]
aliases: [Week06 Shader HLSL 修复]
---

# Week 06 - Shader / 材质 / HLSL 修复

## 目标

训练 AI 写和修 Shader 时关注数学、采样、平台和性能。

- 人类必须学会：HLSL、材质图、采样空间、精度、移动端限制。
- AI 必须学会：Shader 代码必须解释输入输出和边界条件。

## AI 支持边界

- AI 做：任务草稿、参数解释、错误版本候选、错误模式汇总。
- 人类做：确认数学目标、采样空间、平台限制、根因解释。
- AI 不能替代：视觉验收、平台编译、性能实测。

## Day-by-day Action Plan

| Day | Action | AI Support | Test | Result | Self Evaluate |
|-----|--------|------------|------|--------|---------------|
| D1 | 选择 Shader 任务：后处理、边缘检测、PCF、UV 采样错误 | 生成任务草稿 | 确认数学目标 | `UE-Shader-001-task.md` | 是否有可视化验收 |
| D2 | 写专家参考实现或伪代码 | 补参数解释 | 确认坐标空间和采样 | `UE-Shader-001-reference.md` | 是否说明输入输出 |
| D3 | 让 AI 生成或修复 HLSL | 作为被测对象 | 检查语义、性能、平台限制 | `UE-Shader-001-model-output.md` | 是否发现隐藏错误 |
| D4 | 写 Shader Rubric | 起草评分表 | 加入数学和平台扣分项 | `UE-Shader-rubric.md` | 是否覆盖精度和采样 |
| D5 | 构造错误 Shader 样本 | 提供错误版本候选 | 确认错误真实 | `UE-Shader-002-bugfix-task.md` | 是否能测调试能力 |
| D6 | 跑修复任务 | 修复代码 | 判断是否解释根因 | `UE-Shader-002-error-analysis.md` | 是否有根因解释 |
| D7 | 周复盘 | 汇总 Shader 错误模式 | 链接 [[Shader]]、[[PBR]]、[[后处理效果]] | `Week06-review.md` | 是否形成训练价值 |

## Weekly Test

同一个 Shader 任务要求 AI 给“代码 + 数学解释 + 性能注意”，三者缺一扣分。

## Outcome Checklist

- [ ] 1 个 Shader 生成任务
- [ ] 1 个 Shader 修复任务
- [ ] 1 份 Shader Rubric
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
- [[Shader]]
- [[PBR]]
- [[后处理效果]]

