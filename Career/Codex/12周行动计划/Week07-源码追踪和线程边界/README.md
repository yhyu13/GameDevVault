---
tags: [career/AI训练, career/UE5, career/week07]
aliases: [Week07 UE 源码追踪]
---

# Week 07 - 源码追踪和线程边界

## 目标

训练 AI 在解释 UE 源码时不编造调用链。

- 人类必须学会：如何从现象追到源码、线程、关键类和调用点。
- AI 必须学会：源码解释要标明证据来源和不确定点。

## AI 支持边界

- AI 做：候选入口、层级图整理、Rubric 草稿、线程题面草稿。
- 人类做：确认真实源码路径、核对每个函数/类、判断线程边界。
- AI 不能替代：源码真实性查证和当前 UE 版本校准。

## Day-by-day Action Plan

| Day | Action | AI Support | Test | Result | Self Evaluate |
|-----|--------|------------|------|--------|---------------|
| D1 | 选源码主题：GC、Async Loading、RenderCommand、RDG Pass | 列候选入口 | 确认真实源码路径 | `UE-SourceTrace-001-task.md` | 路径是否真实 |
| D2 | 人类追源码并写调用链 | 整理层级图 | 核对每个函数/类 | `UE-SourceTrace-001-answer.md` | 是否有源码证据 |
| D3 | 让 AI 解释调用链 | 作为被测对象 | 检查是否编造类名 | `UE-SourceTrace-001-model-output.md` | 是否捕获幻觉 |
| D4 | 写 SourceTrace Rubric | 起草评分表 | 加入“必须引用路径”规则 | `UE-SourceTrace-rubric.md` | 是否惩罚伪调用链 |
| D5 | 构造线程边界问题 | 生成题面 | 确认 GameThread/RenderThread/RHIThread 边界 | `UE-ThreadBoundary-001-task.md` | 是否有明确边界 |
| D6 | 跑线程任务并分析 | 回答任务 | 检查是否违规操作 UObject 或渲染资源 | `UE-ThreadBoundary-001-error-analysis.md` | 是否识别危险建议 |
| D7 | 周复盘 | 汇总源码追踪模板 | 链接 [[RenderThread]]、[[RHI]]、[[Task Graph]] | `Week07-review.md` | 是否能用于真实源码分析 |

## Weekly Test

如果 AI 说出类名/函数名，必须标注来源或提示需查证。

## Outcome Checklist

- [ ] 1 个源码追踪任务
- [ ] 1 个线程边界任务
- [ ] 1 份 SourceTrace Rubric
- [ ] 1 份源码追踪模板
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
- [[RenderThread]]
- [[RHI]]
- [[Task Graph]]

