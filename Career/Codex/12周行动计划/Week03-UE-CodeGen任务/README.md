---
tags: [career/AI训练, career/UE5, career/week03]
aliases: [Week03 UE CodeGen]
---

# Week 03 - UE C++ CodeGen 任务

## 目标

让 AI 生成更可靠的 UE C++ 工程代码。

- 人类必须学会：生命周期、反射、模块依赖、线程和 GC 限制。
- AI 必须学会：不能只给代码片段，要给可编译、可接入、可测试的工程答案。

## AI 支持边界

- AI 做：方案候选、文件清单、注释、评分表草稿、错误代码候选。
- 人类做：选择真实题目、确认 Build.cs/宏/生命周期、判断代码是否可编译。
- AI 不能替代：真实编译、运行验证、项目集成判断。

## Day-by-day Action Plan

| Day | Action | AI Support | Test | Result | Self Evaluate |
|-----|--------|------------|------|--------|---------------|
| D1 | 选小功能：ActorComponent、Subsystem 或 Editor Utility | 生成方案候选 | 选择贴近真实项目的题 | `UE-CodeGen-001-task.md` | 是否有明确验收标准 |
| D2 | 写最小参考实现结构 | 补文件清单和注释 | 检查 Build.cs、头文件、宏 | `UE-CodeGen-001-reference.md` | 是否包含模块依赖 |
| D3 | 让 AI 生成代码 | 作为被测对象 | 检查编译风险和 UE 约束 | `UE-CodeGen-001-model-output.md` | 是否找到不可编译点 |
| D4 | 写 CodeGen Rubric | 起草评分表 | 加入 UE 专项扣分项 | `UE-CodeGen-rubric.md` | 是否覆盖 UPROPERTY、GC、线程 |
| D5 | 构造错误代码修复任务 | 生成有缺陷代码候选 | 确认错误真实且常见 | `UE-CodeGen-002-bugfix-task.md` | 错误是否不是玩具错误 |
| D6 | 跑修复任务并对比 | 修复代码 | 判断是否引入新问题 | `UE-CodeGen-002-error-analysis.md` | 是否识别表面修复 |
| D7 | 周复盘 | 汇总 CodeGen 失败模式 | 整理检查清单 | `Week03-review.md` | 是否形成 CodeGen Gate |

## Weekly Test

AI 输出必须通过“文件结构 + Build.cs + 生命周期 + 测试方法”四项检查。

## Outcome Checklist

- [ ] 1 个生成任务
- [ ] 1 个修复任务
- [ ] 1 份 UE C++ CodeGen Rubric
- [ ] 1 份 CodeGen Gate 检查清单
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
- [[UE5]]
- [[C++]]
- [[GameThread]]

