---
tags: [career/AI训练, career/UE5, career/week05]
aliases: [Week05 UE5 渲染系统]
---

# Week 05 - 渲染系统和 Lumen / Nanite / VSM

## 目标

把 UE5 现代渲染特性转成可评测任务。

- 人类必须学会：Lumen、Nanite、Virtual Shadow Maps 的适用条件、限制和排查入口。
- AI 必须学会：不要把通用图形学概念直接套到 UE5 项目。

## AI 支持边界

- AI 做：可能原因树、特性限制卡草稿、错误推理样例、偏好样本格式化。
- 人类做：校准 UE5 实战约束、确认验证开关、判断错误是否真实常见。
- AI 不能替代：项目渲染配置和实际画面验证。

## Day-by-day Action Plan

| Day | Action | AI Support | Test | Result | Self Evaluate |
|-----|--------|------------|------|--------|---------------|
| D1 | 选渲染现象：漏光、阴影闪烁、Nanite 不生效 | 整理可能原因树 | 标注 UE5 特有证据 | `UE-Render-001-task.md` | 是否有具体项目配置 |
| D2 | 写特性限制卡：Lumen/Nanite/VSM 三选一 | 汇总公开概念 | 校准为 UE5 实战约束 | `UE-Render-feature-card.md` | 是否避免百科化 |
| D3 | 写专家排查答案 | 组织为步骤 | 补充验证命令或开关 | `UE-Render-001-answer.md` | 是否能指导实际排查 |
| D4 | 让 AI 回答并打分 | 作为被测对象 | 按 Rubric 评分 | `UE-Render-001-score.md` | 分数是否有证据 |
| D5 | 构造错误推理样例 | 生成 plausible wrong answers | 筛选真实常见错误 | `UE-Render-failure-modes.md` | 错误是否足够迷惑 |
| D6 | 写偏好样本 | 转 JSONL 草稿 | 确认 chosen/rejected | `UE-Render-001-preference.jsonl` | 是否强调 UE 特有边界 |
| D7 | 周复盘 | 汇总渲染任务资产 | 链接 [[Lumen]]、[[Nanite]]、[[Virtual Shadow Maps]] | `Week05-review.md` | 是否能讲清 AI 错在哪里 |

## Weekly Test

AI 必须给出“验证开关/控制变量”，否则渲染答案不合格。

## Outcome Checklist

- [ ] 1 个渲染诊断任务包
- [ ] 1 个 UE5 特性限制卡
- [ ] 1 组错误推理样例
- [ ] 1 条偏好样本
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
- [[Lumen]]
- [[Nanite]]
- [[Virtual Shadow Maps]]
- [[渲染管线]]

