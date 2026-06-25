---
tags: [career/AI训练, career/UE5, career/行动计划]
aliases: [UE5 AI训练12周计划, 游戏开发AI训练行动计划]
---

# UE5 + AI 训练方向 12 周行动计划

## 目标

这份计划服务于“[[UE5]] 专家如何提升 AI 在真实 [[游戏开发]] 任务中的输出质量”。

它不是普通学习计划，而是一个 12 周训练资产生产计划。每周都要产出可复用资产：

- 真实 UE 场景任务
- 输入材料
- 专家参考答案
- AI 原始输出
- 错误分析
- Rubric
- 改进建议
- 复测结果

最终目标是形成一个小型 Portfolio：证明你不仅会 UE，也能系统性评估和改进 AI 的 UE 能力。

---

## AI 支持边界

### AI 应该为人类做什么

AI 可以做提效动作：

- 把长日志、Profile 文本、源码片段整理成结构化摘要。
- 根据人类给出的真实场景生成任务卡草稿。
- 生成候选 Rubric，让人类审定。
- 生成错误答案样例，帮助构造反例。
- 对比专家答案和模型答案，列出差异点。
- 把零散笔记整理成训练样本、评测样本、偏好样本。
- 生成复测 prompt、检查清单、报告模板。
- 作为“被测模型”暴露当前 AI 在 UE 任务上的失败模式。

### AI 不应该替人类做什么

AI 不能替代这些判断：

- 判断 UE 代码是否真的能在项目里编译和运行。
- 判断日志证据是否足以证明因果关系。
- 判断性能瓶颈是否真实存在。
- 判断源码调用链是否符合当前 UE 版本。
- 判断项目约束、平台约束、商业约束。
- 最终打分和训练数据入库决策。

### 人类必须知道、必须学会什么

人类专家必须掌握：

- UE 生命周期、UObject/GC、模块依赖、Build.cs、反射宏。
- GameThread、RenderThread、RHIThread、TaskGraph 的边界。
- Lumen、Nanite、Virtual Shadow Maps、RDG、Shader 编译链路。
- Cook、Package、Asset Registry、IoStore、Streaming 工作流。
- Unreal Insights、Stat GPU、RenderDoc、MemReport、LLM 的读法。
- 网络同步、动画、物理、Gameplay 的基本排查路径。
- 如何把“感觉不对”转成可验证证据和评分标准。

### AI 必须学会什么

被优化的 AI 最终必须学会：

- 先确认上下文，再给结论。
- 引用输入证据，而不是泛泛解释。
- 区分事实、推测、缺失信息。
- 给出可执行验证步骤。
- 避免编造 UE API、类名、配置项。
- 知道 UE 版本、平台、项目约束会改变答案。
- 写出的代码要包含文件结构、模块依赖、生命周期和测试方法。
- 在证据不足时明确说“不足以证明”，并提出下一步收集什么。

---

## 每日通用节奏

每天都按这个小闭环推进：

```text
人类选题或判断 -> AI 辅助整理/生成 -> 人类验证 -> 产出资产 -> 自评打分
```

每日自评分 10 分：

| 维度 | 分值 | 说明 |
|------|------|------|
| 真实性 | 2 | 是否来自真实 UE 场景或可复现实验 |
| 证据链 | 2 | 是否引用日志、源码、Profile、配置等证据 |
| 可执行性 | 2 | 是否有明确命令、代码、检查步骤 |
| AI 训练价值 | 2 | 是否能转成训练/评测/偏好数据 |
| 连接性 | 2 | 是否链接到已有笔记和下一个任务 |

低于 7 分：当天产物只能算草稿，不能入 Portfolio。

---

## 12 周阶段设计

| 阶段 | 周数 | 目标 |
|------|------|------|
| Phase 1 | 第 1-4 周 | 建立 UE-AI 任务、Rubric、错误分类基础 |
| Phase 2 | 第 5-8 周 | 覆盖 Debug、CodeGen、Perf、Render、Shader、Workflow |
| Phase 3 | 第 9-12 周 | 做复测、改进建议、Portfolio、面试表达 |

## 执行目录

每周执行面板已经拆到 [[12周行动计划/README]]。总文档保留路线图，周目录用于填写任务卡、专家答案、AI 原始输出、错误分析、Rubric、复测结果和周复盘。

---

## Week 1：建立任务模板和基线评测

目标：建立统一任务格式，拿到第一个模型基线。

人类必须学会：如何把真实 UE 问题拆成可评测任务。

AI 必须学会：任务回答不能跳过上下文、证据和验证步骤。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 选 3 个真实 UE 任务候选：Debug、CodeGen、Perf 各 1 个 | AI 帮你把候选整理成任务卡草稿 | 人类检查是否可复现、是否脱敏 | `任务候选清单` | 候选是否来自真实工作，而不是凭空想象 |
| D2 | 固化任务模板：背景、输入、期望输出、Rubric、错误类型 | AI 生成模板字段和示例 | 用一个旧问题填一遍模板 | `UE任务模板.md` | 模板是否足够指导别人复测 |
| D3 | 选择第一个任务：例如 Cook 内存诊断 | AI 帮你列输入材料清单 | 检查输入材料是否足够支持专家判断 | `UE-Debug-001-task.md` | 是否避免泄露项目敏感信息 |
| D4 | 写专家参考答案 | AI 只能帮整理结构，不负责最终结论 | 人类逐条验证证据是否成立 | `UE-Debug-001-answer.md` | 结论是否超出证据 |
| D5 | 跑 AI 原始输出 | AI 作为被测对象回答任务 | 不改 prompt，保留原始输出 | `UE-Debug-001-model-output.md` | 是否保留了未加工输出 |
| D6 | 对比专家答案和模型答案 | AI 可帮做差异表 | 人类确认每个错误类型 | `UE-Debug-001-error-analysis.md` | 错误是否具体到句子或判断 |
| D7 | 周复盘 | AI 汇总本周资产 | 用 10 分制给任务包打分 | `Week01-review.md` | 是否能说清楚模型最主要短板 |

本周测试：同一个任务让 AI 回答 2 次，检查是否稳定犯同类错误。

本周成果标准：至少完成 1 个完整 Debug 任务包。

---

## Week 2：UE Debug 日志诊断

目标：训练 AI 从日志中建立证据链。

人类必须学会：Crash、Cook、Shader 编译、Asset 加载日志的关键证据。

AI 必须学会：不能看到关键词就直接归因。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 收集 2 类日志任务：真错误和干扰样本 | AI 帮你做日志摘要 | 人类标注关键证据行 | `UE-Debug-log-cases.md` | 是否有正例和反例 |
| D2 | 写 Crash 或 Cook 诊断专家流程 | AI 整理成决策树 | 用旧日志走一遍流程 | `UE-Debug-decision-tree.md` | 流程是否能落到具体搜索词 |
| D3 | 构造任务 002：日志中有高内存但不一定 OOM | AI 生成题面草稿 | 人类检查诱导项是否合理 | `UE-Debug-002-task.md` | 是否能暴露过早归因 |
| D4 | 写专家答案和 Rubric | AI 起草评分项 | 人类删掉泛泛项 | `UE-Debug-002-rubric.md` | Rubric 是否可评分而非主观感觉 |
| D5 | 跑 AI 并记录输出 | AI 作为被测对象 | 检查是否引用证据 | `UE-Debug-002-model-output.md` | 是否有明确失败模式 |
| D6 | 生成偏好样本：好答案 vs 差答案 | AI 帮转成 JSONL 草稿 | 人类确认 chosen/rejected 理由 | `UE-Debug-002-preference.jsonl` | 偏好理由是否具体 |
| D7 | 周复盘和连接 | AI 整理链接建议 | 人类链接到 [[Cook]]、[[内存管理]]、[[Unreal Insights]] | `Week02-review.md` | 是否沉淀可复用日志诊断原则 |

本周测试：给 AI 缺失关键证据的日志，看它是否会承认信息不足。

本周成果标准：2 个 Debug 任务、1 个日志决策树、1 条偏好样本。

---

## Week 3：UE C++ CodeGen 任务

目标：让 AI 生成更可靠的 UE C++ 工程代码。

人类必须学会：UE 代码生成的生命周期、反射、模块依赖、线程和 GC 限制。

AI 必须学会：不能只给片段，要给可编译、可接入、可测试的工程答案。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 选一个小功能：ActorComponent、Subsystem 或 Editor Utility | AI 生成方案候选 | 人类选择最贴近真实项目的题 | `UE-CodeGen-001-task.md` | 题目是否有明确验收标准 |
| D2 | 人类写最小参考实现结构 | AI 帮补文件清单和注释 | 检查 Build.cs、头文件、宏 | `UE-CodeGen-001-reference.md` | 是否包含模块依赖 |
| D3 | 让 AI 生成代码 | AI 作为被测对象 | 人类检查编译风险和 UE 约束 | `UE-CodeGen-001-model-output.md` | 是否找到具体不可编译点 |
| D4 | 写 CodeGen Rubric | AI 起草评分表 | 人类加入 UE 专项扣分项 | `UE-CodeGen-rubric.md` | 是否覆盖 UPROPERTY、GC、线程 |
| D5 | 构造错误代码修复任务 | AI 生成有缺陷代码候选 | 人类确认错误真实且常见 | `UE-CodeGen-002-bugfix-task.md` | 错误是否不是玩具错误 |
| D6 | 跑修复任务并对比 | AI 修复代码 | 人类判断是否引入新问题 | `UE-CodeGen-002-error-analysis.md` | 是否能识别“修了表面没修根因” |
| D7 | 周复盘 | AI 汇总 CodeGen 常见失败模式 | 人类整理成检查清单 | `Week03-review.md` | 是否形成可复用 CodeGen Gate |

本周测试：AI 输出必须通过“文件结构 + Build.cs + 生命周期 + 测试方法”四项检查。

本周成果标准：1 个生成任务、1 个修复任务、1 份 UE C++ CodeGen Rubric。

---

## Week 4：性能诊断基础

目标：让 AI 根据 Profile 信息判断瓶颈，而不是泛泛建议优化。

人类必须学会：CPU/GPU/内存/IO 诊断入口和证据边界。

AI 必须学会：先定位 bound 类型，再谈优化方案。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 准备 Stat Unit、Stat GPU、Unreal Insights 或 RenderDoc 样例 | AI 整理指标含义 | 人类标注关键瓶颈 | `UE-Perf-input-cases.md` | 是否包含足够上下文 |
| D2 | 写性能诊断决策树 | AI 帮格式化 | 用 2 个样例验证流程 | `UE-Perf-decision-tree.md` | 是否先判断 CPU/GPU/内存/IO |
| D3 | 构造 UE-Perf-001 任务 | AI 生成题面草稿 | 人类确认输入不泄露项目 | `UE-Perf-001-task.md` | 题目是否能区分高手和泛泛回答 |
| D4 | 写专家答案 | AI 帮拆分为证据和建议 | 人类核对每个优化建议的副作用 | `UE-Perf-001-answer.md` | 是否说明风险 |
| D5 | 跑 AI 输出 | AI 作为被测对象 | 检查是否直接套模板 | `UE-Perf-001-model-output.md` | 是否有空泛建议 |
| D6 | 写 Rubric 和失败模式 | AI 做对比表 | 人类确认评分标准 | `UE-Perf-rubric.md` | Rubric 是否能惩罚无证据建议 |
| D7 | Phase 1 复盘 | AI 汇总前 4 周资产 | 人类判断下一阶段补什么 | `Phase01-review.md` | 是否已有 Debug/CodeGen/Perf 三类基础资产 |

本周测试：给 AI 一个 GPU bound 样例，看它是否错误建议优化 GameThread。

本周成果标准：1 个 Perf 任务包、1 个性能诊断决策树。

---

## Week 5：渲染系统和 Lumen/Nanite/VSM

目标：把 UE5 现代渲染特性转成可评测任务。

人类必须学会：Lumen、Nanite、VSM 的适用条件、限制和排查入口。

AI 必须学会：不要把通用图形学概念直接套到 UE5 项目。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 选一个渲染现象：漏光、阴影闪烁、Nanite 不生效 | AI 帮整理可能原因树 | 人类标注 UE5 特有证据 | `UE-Render-001-task.md` | 是否有具体项目配置 |
| D2 | 写特性限制卡：Lumen/Nanite/VSM 三选一 | AI 汇总公开概念 | 人类校准为 UE5 实战约束 | `UE-Render-feature-card.md` | 是否避免只写百科 |
| D3 | 写专家排查答案 | AI 帮组织为步骤 | 人类补充验证命令或开关 | `UE-Render-001-answer.md` | 是否能指导实际排查 |
| D4 | 让 AI 回答并打分 | AI 作为被测对象 | 人类按 Rubric 评分 | `UE-Render-001-score.md` | 分数是否有证据 |
| D5 | 构造错误推理样例 | AI 生成 plausible wrong answers | 人类筛选真实常见错误 | `UE-Render-failure-modes.md` | 错误是否足够迷惑 |
| D6 | 写偏好样本 | AI 转 JSONL 草稿 | 人类确认 chosen/rejected | `UE-Render-001-preference.jsonl` | 是否强调 UE 特有边界 |
| D7 | 周复盘 | AI 汇总渲染任务资产 | 人类链接到 [[Lumen]]、[[Nanite]]、[[Virtual Shadow Maps]] | `Week05-review.md` | 是否能讲清 AI 错在哪里 |

本周测试：AI 必须给出“验证开关/控制变量”，否则渲染答案不合格。

本周成果标准：1 个渲染诊断任务包、1 个 UE5 特性限制卡。

---

## Week 6：Shader / 材质 / HLSL 修复

目标：训练 AI 写和修 Shader 时关注数学、采样、平台和性能。

人类必须学会：HLSL、材质图、采样空间、精度、移动端限制。

AI 必须学会：Shader 代码不能只“看起来像”，必须解释输入输出和边界条件。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 选择一个 Shader 任务：后处理、边缘检测、PCF、UV 采样错误 | AI 生成任务草稿 | 人类确认数学目标 | `UE-Shader-001-task.md` | 是否有可视化验收 |
| D2 | 写专家参考实现或伪代码 | AI 帮补参数解释 | 人类确认坐标空间和采样 | `UE-Shader-001-reference.md` | 是否说明输入输出 |
| D3 | 让 AI 生成或修复 HLSL | AI 作为被测对象 | 人类检查语义、性能、平台限制 | `UE-Shader-001-model-output.md` | 是否发现隐藏错误 |
| D4 | 写 Shader Rubric | AI 起草评分表 | 人类加入数学和平台扣分项 | `UE-Shader-rubric.md` | 是否覆盖精度和采样 |
| D5 | 构造错误 Shader 样本 | AI 提供错误版本候选 | 人类确认错误真实 | `UE-Shader-002-bugfix-task.md` | 是否能测出 AI 的调试能力 |
| D6 | 跑修复任务 | AI 修复 | 人类判断是否解释根因 | `UE-Shader-002-error-analysis.md` | 是否有根因解释 |
| D7 | 周复盘 | AI 汇总 Shader 错误模式 | 人类连接到 [[Shader]]、[[PBR]]、[[后处理效果]] | `Week06-review.md` | 是否形成 Shader 训练价值 |

本周测试：同一个 Shader 任务要求 AI 给“代码 + 数学解释 + 性能注意”，三者缺一扣分。

本周成果标准：1 个 Shader 生成任务、1 个 Shader 修复任务、1 份 Shader Rubric。

---

## Week 7：源码追踪和线程边界

目标：训练 AI 在解释 UE 源码时不编造调用链。

人类必须学会：如何从现象追到源码、线程、关键类和调用点。

AI 必须学会：源码解释要标明证据来源和不确定点。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 选一个源码主题：GC、Async Loading、RenderCommand、RDG Pass | AI 帮列候选入口 | 人类确认真实源码路径 | `UE-SourceTrace-001-task.md` | 路径是否真实 |
| D2 | 人类追源码并写调用链 | AI 帮整理层级图 | 人类核对每个函数/类 | `UE-SourceTrace-001-answer.md` | 是否有源码证据 |
| D3 | 让 AI 解释调用链 | AI 作为被测对象 | 检查是否编造不存在类名 | `UE-SourceTrace-001-model-output.md` | 是否捕获幻觉 |
| D4 | 写 SourceTrace Rubric | AI 起草 | 人类加入“必须引用路径”规则 | `UE-SourceTrace-rubric.md` | 是否能惩罚伪调用链 |
| D5 | 构造线程边界问题 | AI 生成题面 | 人类确认 GameThread/RenderThread/RHIThread 边界 | `UE-ThreadBoundary-001-task.md` | 是否有明确边界 |
| D6 | 跑线程任务并分析 | AI 回答 | 人类检查是否违规操作 UObject 或渲染资源 | `UE-ThreadBoundary-001-error-analysis.md` | 是否识别危险建议 |
| D7 | 周复盘 | AI 汇总源码追踪模板 | 人类连接到 [[RenderThread]]、[[RHI]]、[[Task Graph]] | `Week07-review.md` | 是否能用于真实源码分析 |

本周测试：如果 AI 说出类名/函数名，必须标注来源或提示需查证。

本周成果标准：1 个源码追踪任务、1 个线程边界任务。

---

## Week 8：Workflow / Cook / Package / 工具链

目标：训练 AI 处理 UE 工程工作流，而不是只写玩法或渲染答案。

人类必须学会：Cook、Build、Package、CI、资源审计的真实链路。

AI 必须学会：工作流问题要考虑平台、配置、命令行、缓存和环境。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 选一个工作流问题：Cook 失败、Pak 异常、CI 构建失败 | AI 整理现象分类 | 人类确认输入材料 | `UE-Workflow-001-task.md` | 是否有命令和日志 |
| D2 | 写专家排查流程 | AI 帮转检查清单 | 人类补充平台和配置约束 | `UE-Workflow-checklist.md` | 是否能实际执行 |
| D3 | 让 AI 回答 | AI 作为被测对象 | 检查是否忽略环境约束 | `UE-Workflow-001-model-output.md` | 是否捕获泛化错误 |
| D4 | 写 Rubric | AI 起草 | 人类加入命令、路径、版本检查 | `UE-Workflow-rubric.md` | 是否可用于 CI 类任务 |
| D5 | 构造工具脚本任务 | AI 生成 Python/Editor Utility 候选 | 人类检查安全性和项目适配 | `UE-Tooling-001-task.md` | 是否避免危险命令 |
| D6 | 跑工具脚本任务并分析 | AI 写代码 | 人类检查文件操作、路径、异常处理 | `UE-Tooling-001-error-analysis.md` | 是否符合工程安全 |
| D7 | Phase 2 复盘 | AI 汇总第 5-8 周资产 | 人类选出 Portfolio 候选 | `Phase02-review.md` | 是否覆盖 Render/Shader/Source/Workflow |

本周测试：AI 的工作流建议必须包含“当前环境信息不足时要补什么”。

本周成果标准：1 个 Workflow 任务、1 个工具脚本任务、Phase 2 复盘。

---

## Week 9：综合评测集 v1

目标：把前 8 周材料整理成一个小型 UE-AI 评测集。

人类必须学会：评测集组织、样本去重、难度分层。

AI 必须学会：在不同任务类型下使用不同回答结构。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 整理所有任务包 | AI 生成目录和索引 | 人类确认每个任务状态 | `UE-AI-evalset-index.md` | 是否能一眼看清覆盖面 |
| D2 | 给任务分层：Easy/Medium/Hard | AI 提建议 | 人类按真实项目难度校准 | `UE-AI-evalset-levels.md` | 难度是否合理 |
| D3 | 统一 Rubric 格式 | AI 合并草稿 | 人类保留各类任务差异 | `UE-AI-rubric-v1.md` | 是否既统一又不粗糙 |
| D4 | 跑一次全量基线 | AI 作为被测对象 | 人类记录每题分数 | `baseline-run-01.md` | 是否保留原始输出 |
| D5 | 分析错误分布 | AI 做统计摘要 | 人类确认错误类型 | `baseline-error-summary.md` | 是否能定位最大短板 |
| D6 | 写数据改进建议 | AI 帮组织成条目 | 人类决定优先级 | `training-improvement-v1.md` | 建议是否能变成数据需求 |
| D7 | 周复盘 | AI 汇总 v1 评测集 | 人类写展示摘要 | `Week09-review.md` | 是否可对外讲清方法 |

本周测试：至少 6 个任务可被同一套评测流程跑完。

本周成果标准：UE-AI 评测集 v1、一次完整基线、错误分布报告。

---

## Week 10：Prompt / RAG / Tool-use 改进实验

目标：不直接假设训练，先验证 prompt、检索和工具流程能提升多少。

人类必须学会：把改进手段和失败模式对应起来。

AI 必须学会：需要查证时用资料和工具，不凭空回答。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 选择 3 个高频失败模式 | AI 汇总候选 | 人类按业务价值排序 | `failure-priority.md` | 是否优先处理高价值问题 |
| D2 | 设计 Prompt 改进 | AI 起草系统提示和输出格式 | 人类检查是否过拟合 | `prompt-experiment-01.md` | 是否明确预期提升 |
| D3 | 设计 RAG 输入材料 | AI 帮整理知识片段 | 人类确认资料真实和版本 | `rag-pack-01.md` | 是否避免脏知识进入 |
| D4 | 设计 Tool-use 流程 | AI 起草步骤 | 人类定义何时查日志/源码/命令 | `tool-use-flow-01.md` | 是否有工具触发条件 |
| D5 | 复测 3 个任务 | AI 作为改进后被测对象 | 人类同 Rubric 打分 | `rerun-01-results.md` | 是否同标准复测 |
| D6 | 对比基线和复测 | AI 生成差异表 | 人类判断提升是否真实 | `baseline-vs-rerun-01.md` | 是否避免主观乐观 |
| D7 | 周复盘 | AI 汇总实验结论 | 人类决定下一步训练需求 | `Week10-review.md` | 是否能说清 prompt/RAG/tool-use 各自作用 |

本周测试：同一个任务前后评分至少提升 2 分，才算实验有效。

本周成果标准：1 个 prompt 实验、1 个 RAG 包、1 个 Tool-use 流程、复测对比。

---

## Week 11：训练数据包和偏好数据包

目标：把样本整理成更接近训练使用的格式。

人类必须学会：SFT、Preference、Error Correction 数据分别适合什么问题。

AI 必须学会：通过好坏对比学习专家偏好。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 选择适合 SFT 的样本 | AI 帮筛选完整样本 | 人类确认答案质量 | `sft-candidates.md` | 是否排除低质量样本 |
| D2 | 转 SFT 格式 | AI 转 JSONL 草稿 | 人类检查字段和脱敏 | `ue-sft-v1.jsonl` | 是否可追溯到原任务 |
| D3 | 选择偏好样本 | AI 帮配对 chosen/rejected | 人类确认偏好理由 | `preference-candidates.md` | 理由是否具体可学习 |
| D4 | 转 Preference 格式 | AI 转 JSONL 草稿 | 人类检查 chosen/rejected 无反 | `ue-preference-v1.jsonl` | 是否避免错误答案被标好 |
| D5 | 选择 Error Correction 样本 | AI 帮归类错误代码/错误推理 | 人类确认修复答案 | `error-correction-candidates.md` | 是否覆盖常见错误 |
| D6 | 写数据卡 | AI 起草 dataset card | 人类补充来源、限制、风险 | `ue-ai-dataset-card-v1.md` | 是否说明适用边界 |
| D7 | 周复盘 | AI 汇总数据包 | 人类抽查 20% 样本 | `Week11-review.md` | 是否能交给他人复核 |

本周测试：随机抽 3 条样本，检查别人是否能理解任务、答案和评分。

本周成果标准：SFT 草包、Preference 草包、Error Correction 候选、数据卡 v1。

---

## Week 12：Portfolio 和面试/汇报表达

目标：把 12 周资产变成可展示成果。

人类必须学会：讲清“我如何让 AI 更懂 UE”。

AI 必须学会：通过评测、错误分析和复测来证明进步。

| Day | Action | AI 支持 | Test | Result | Self Evaluate |
|-----|--------|---------|------|--------|---------------|
| D1 | 整理 12 周资产索引 | AI 生成目录 | 人类确认文件完整 | `12-week-asset-index.md` | 是否能快速导航 |
| D2 | 写方法论总结 | AI 帮组织结构 | 人类补充真实案例 | `UE-AI-methodology.md` | 是否不是空泛方法论 |
| D3 | 写 3 个代表案例 | AI 帮压缩表达 | 人类保留证据和数据 | `portfolio-case-studies.md` | 案例是否能展示判断力 |
| D4 | 写面试回答脚本 | AI 模拟面试官追问 | 人类修正夸大表述 | `interview-script.md` | 是否能抗追问 |
| D5 | 做最终复测 | AI 作为被测对象 | 人类用 v1 Rubric 打分 | `final-rerun-results.md` | 是否和 Week 9 基线可比 |
| D6 | 写最终复盘 | AI 汇总数据 | 人类写不足和下一步 | `12-week-final-review.md` | 是否承认局限 |
| D7 | 选择下一轮主题 | AI 提候选 | 人类按职业目标排序 | `next-12-week-plan-seed.md` | 是否有明确下一步 |

本周测试：用 5 分钟讲清一个案例，用 15 分钟讲清完整方法论。

本周成果标准：Portfolio 索引、3 个代表案例、最终复测、面试表达脚本。

---

## 代表性周成果示例

### 示例：Week 2 Debug 周

输入：

```text
Cook log 片段
MemoryStats
命令行参数
Cook 阶段信息
AI 原始回答
```

专家结论：

```text
当前证据只能证明系统内存压力高，不能直接证明 UE 进程 OOM。
需要检查 allocation failure、Fatal error、退出码、ShaderCompileWorker 状态和 Cook 阶段。
```

AI 失败模式：

```text
看到 SystemCommitUsedPct 高就直接归因 OOM。
没有区分 high memory、allocation failure、process killed。
没有提出下一步验证命令。
```

改进建议：

```text
增加日志证据链训练样本。
用偏好数据强化“证据不足时不下结论”。
在 Debug 类任务中强制输出：结论、证据、缺失信息、验证步骤。
```

自评：

| 项目 | 分数 |
|------|------|
| 真实性 | 2 |
| 证据链 | 2 |
| 可执行性 | 2 |
| AI 训练价值 | 2 |
| 连接性 | 1 |
| 总分 | 9 |

---

## 每周交付物清单

每周结束前至少检查：

- [ ] 1 个正式任务卡
- [ ] 1 份专家答案
- [ ] 1 份 AI 原始输出
- [ ] 1 份错误分析
- [ ] 1 份 Rubric 或对既有 Rubric 的修订
- [ ] 1 条训练或偏好样本
- [ ] 1 份周复盘
- [ ] 至少 3 个 Obsidian 双向链接

---

## 关联 / 输出产物

- [[UE5 + AI 训练方向学习计划]]
- [[UE5]]
- [[游戏开发]]
- [[性能优化]]
- [[Shader]]
- [[Cook]]
- [[Unreal Insights]]
- [[Lumen]]
- [[Nanite]]
- [[面试与职业复盘日志]]
