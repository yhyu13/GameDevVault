---
tags: [career/AI训练, career/UE5, career/week08]
aliases: [Week08 UE Workflow 工具链]
---

# Week 08 - Workflow / Cook / Package / 工具链

## 目标

训练 AI 处理 UE 工程工作流，而不是只写玩法或渲染答案。

- 人类必须学会：Cook、Build、Package、CI、资源审计的真实链路。
- AI 必须学会：工作流问题要考虑平台、配置、命令行、缓存和环境。

## AI 支持边界

- AI 做：现象分类、检查清单、Rubric 草稿、工具脚本候选。
- 人类做：确认命令、路径、平台、配置、文件操作安全性。
- AI 不能替代：真实构建、真实 Cook、危险文件操作判断。

## Day-by-day Action Plan

| Day | Action | AI Support | Test | Result | Self Evaluate |
|-----|--------|------------|------|--------|---------------|
| D1 | 选工作流问题：Cook 失败、Pak 异常、CI 构建失败 | 整理现象分类 | 确认输入材料 | `UE-Workflow-001-task.md` | 是否有命令和日志 |
| D2 | 写专家排查流程 | 转检查清单 | 补充平台和配置约束 | `UE-Workflow-checklist.md` | 是否能实际执行 |
| D3 | 让 AI 回答 | 作为被测对象 | 检查是否忽略环境约束 | `UE-Workflow-001-model-output.md` | 是否捕获泛化错误 |
| D4 | 写 Rubric | 起草评分表 | 加入命令、路径、版本检查 | `UE-Workflow-rubric.md` | 是否可用于 CI 类任务 |
| D5 | 构造工具脚本任务 | 生成 Python/Editor Utility 候选 | 检查安全性和项目适配 | `UE-Tooling-001-task.md` | 是否避免危险命令 |
| D6 | 跑工具脚本任务并分析 | 写代码 | 检查文件操作、路径、异常处理 | `UE-Tooling-001-error-analysis.md` | 是否符合工程安全 |
| D7 | Phase 2 复盘 | 汇总第 5-8 周资产 | 选出 Portfolio 候选 | `Phase02-review.md` | 是否覆盖 Render/Shader/Source/Workflow |

## Weekly Test

AI 的工作流建议必须包含“当前环境信息不足时要补什么”。

## Outcome Checklist

- [ ] 1 个 Workflow 任务
- [ ] 1 个工具脚本任务
- [ ] 1 份 Workflow Rubric
- [ ] 1 份 Phase 2 复盘

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
- [[Package]]
- [[工具链]]

