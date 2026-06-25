---
tags: [career/AI训练, career/UE5, career/week11]
aliases: [Week11 UE 训练数据包]
---

# Week 11 - 训练数据包和偏好数据包

## 目标

把样本整理成更接近训练使用的格式。

- 人类必须学会：SFT、Preference、Error Correction 数据分别适合什么问题。
- AI 必须学会：通过好坏对比学习专家偏好。

## AI 支持边界

- AI 做：完整样本筛选建议、JSONL 草稿、chosen/rejected 配对、dataset card 草稿。
- 人类做：确认答案质量、字段脱敏、偏好方向、数据适用边界。
- AI 不能替代：训练样本入库质量审查。

## Day-by-day Action Plan

| Day | Action | AI Support | Test | Result | Self Evaluate |
|-----|--------|------------|------|--------|---------------|
| D1 | 选择适合 SFT 的样本 | 筛选完整样本 | 确认答案质量 | `sft-candidates.md` | 是否排除低质量样本 |
| D2 | 转 SFT 格式 | 转 JSONL 草稿 | 检查字段和脱敏 | `ue-sft-v1.jsonl` | 是否可追溯到原任务 |
| D3 | 选择偏好样本 | 配对 chosen/rejected | 确认偏好理由 | `preference-candidates.md` | 理由是否具体可学习 |
| D4 | 转 Preference 格式 | 转 JSONL 草稿 | 检查 chosen/rejected 无反 | `ue-preference-v1.jsonl` | 是否避免错误答案被标好 |
| D5 | 选择 Error Correction 样本 | 归类错误代码/错误推理 | 确认修复答案 | `error-correction-candidates.md` | 是否覆盖常见错误 |
| D6 | 写数据卡 | 起草 dataset card | 补充来源、限制、风险 | `ue-ai-dataset-card-v1.md` | 是否说明适用边界 |
| D7 | 周复盘 | 汇总数据包 | 抽查 20% 样本 | `Week11-review.md` | 是否能交给他人复核 |

## Weekly Test

随机抽 3 条样本，检查别人是否能理解任务、答案和评分。

## Outcome Checklist

- [ ] SFT 草包
- [ ] Preference 草包
- [ ] Error Correction 候选
- [ ] 数据卡 v1
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
- [[面试与职业复盘日志]]

