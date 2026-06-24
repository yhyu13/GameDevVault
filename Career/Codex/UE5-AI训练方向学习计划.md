---
tags: [career/AI训练, career/UE5, career/游戏开发]
aliases: [游戏开发专家AI训练方向, UE5 AI提效计划]
---

# UE5 + AI 训练方向学习计划

## 一句话定位

这个方向不是单纯要求“会用 [[UE5]]”，而是要求人类专家把真实 [[游戏开发]] 工作拆成 AI 可学习、可评估、可纠错、可迭代的数据资产。

目标不是让 AI 背诵 Unreal 名词，而是让 AI 更像一个可靠的引擎程序员：

- 能理解任务背景，而不是泛泛解释概念。
- 能基于日志、Profile、源码和配置给出证据链。
- 能写可运行、可维护、符合 UE 工程约束的代码。
- 能承认不确定性，并给出下一步验证方法。
- 能从错误答案中学习，逐步减少幻觉和无效建议。

---

## 岗位真实目标

JD 表面要求：

- 熟悉 UE5、Nanite、Lumen、Virtual Shadow Maps。
- 熟悉渲染、物理、动画、特效、网络、Gameplay。
- 熟悉性能优化、问题排查、工程实现。
- 对 AI 有兴趣和实践。

实际目标更接近：

> 用 UE 专家经验，持续优化 AI 在真实游戏开发任务中的输出质量。

因此，人类专家的价值不只是“自己能做”，而是能把“自己为什么这么做”沉淀成训练资产：

- 任务场景
- 输入材料
- 参考实现
- 标准答案
- 评分 Rubric
- 常见错误
- 专家点评
- 改进建议

---

## 能力模型

### 1. 场景定义能力

把泛泛的“游戏开发能力”拆成可训练场景。

优先场景：

| 场景 | 典型任务 | AI 提效重点 |
|------|----------|-------------|
| 问题排查 | Crash、Cook 失败、Shader 编译失败、渲染异常 | 证据链、假设排序、验证步骤 |
| 工程实现 | ActorComponent、Subsystem、Editor Utility、异步加载 | UE 生命周期、模块组织、边界条件 |
| 性能优化 | Stat GPU、Unreal Insights、RenderDoc、MemReport | CPU/GPU/内存瓶颈区分 |
| 源码理解 | RenderThread、RHI、RDG、GC、Replication | 调用链、线程边界、关键类职责 |
| Shader/VFX | HLSL、材质函数、后处理、采样错误 | 数学、渲染管线、平台限制 |
| 工作流工具 | Cook、Build、CI、资源审计、批处理脚本 | 自动化、可复用、项目约束 |
| 评审纠错 | 代码 Review、配置 Review、蓝图逻辑 Review | 找风险、给修复方案、说明代价 |

### 2. 数据构造能力

每个训练样本都应尽量包含：

```text
任务背景
输入材料
期望输出
专家参考答案
评分标准
常见错误
验证方法
可复用标签
```

高价值样本不是“解释 Lumen 是什么”，而是：

```text
给一段 Lumen 漏光现象、项目配置、截图描述和相关日志，
要求 AI 判断可能原因、排序、给验证步骤，并指出当前证据不足之处。
```

### 3. 评测能力

没有评测，训练效果只能靠感觉。

建议建立 UE 专属评测集：

| 评测集 | 内容 |
--------|------|
| UE-CodeGen | 生成 UE C++、Blueprint、Python、Commandlet、Editor Utility |
| UE-Debug | 根据日志、Crash、Cook 输出定位问题 |
| UE-Perf | 根据 Profile 数据判断瓶颈和优化路径 |
| UE-Render | 分析渲染管线、Lumen、Nanite、VSM、RDG |
| UE-Shader | 编写或修复 HLSL、GLSL、材质逻辑 |
| UE-SourceTrace | 根据源码路径解释调用链和线程边界 |
| UE-Review | 审查代码、配置、资源风险 |
| UE-Workflow | 处理 Cook、Package、CI、版本管理问题 |

### 4. 训练改进能力

不同问题用不同训练方式：

| 方式 | 适合问题 | 示例 |
|------|----------|------|
| SFT | 标准任务学习 | 输入问题，输出专家答案 |
| Preference / DPO | 学会选择更好答案 | 泛泛答案 vs 证据充分答案 |
| Error Correction | 修正错误输出 | 给错误 UE 代码，让模型指出问题并修复 |
| RAG | 补充版本和项目知识 | UE API、项目规范、内部工具文档 |
| Tool-use | 学会查证 | 读日志、搜源码、跑命令、看 Profile |
| Agent Workflow | 多步任务执行 | 收集信息 -> 提假设 -> 验证 -> 输出结论 |

---

## 专家工作流模板

### Debug 类任务

AI 输出应遵循：

```text
结论
证据
可能原因排序
当前证据不足点
下一步验证
修复方案
风险和副作用
```

评分重点：

- 是否引用输入中的证据。
- 是否区分“现象证明”和“因果证明”。
- 是否避免无根据归因。
- 是否给出可执行验证步骤。
- 是否能说明版本差异和项目配置限制。

### 性能优化类任务

专家流程：

```text
先判断 CPU bound / GPU bound / 内存 bound / IO bound
再定位具体阶段
再提出最小验证实验
最后给出优化方案和副作用
```

例如：

- BasePass 高：材质复杂度、overdraw、instance、draw call。
- ShadowDepths 高：动态光源、阴影距离、VSM page、角色数量。
- RHIThread 高：提交压力、PSO、资源创建、同步点。
- GameThread 高：Tick、蓝图、AI、动画、GC、任务调度。

### 代码生成类任务

AI 输出应包含：

```text
文件结构
Build.cs 依赖
核心代码
生命周期说明
线程和 GC 注意事项
测试方法
常见坑
```

扣分项：

- 忘记 UCLASS / UPROPERTY / GENERATED_BODY。
- 在非 GameThread 直接操作 UObject。
- 错用 Constructor、BeginPlay、Initialize、Deinitialize。
- 忘记模块依赖。
- 给出无法编译的伪代码却不说明。

---

## 每周固定节奏

### 周一：场景采样和任务定义

目标：从真实 UE 工作里选出可训练任务。

输入：

- 项目日志
- Crash 片段
- Profile 数据
- 代码 Review 问题
- Shader 编译错误
- Cook / Package 失败记录

输出：

```text
3 个候选任务
1 个正式任务卡
任务输入材料清单
```

示例任务卡：

```text
任务：根据 UE5 Cook 日志判断是否存在真实 OOM
输入：Cook log、MemoryStats、命令行参数、阶段信息
期望：区分高内存现象和 OOM 证据，给出下一步验证
标签：UE-Debug、Cook、Memory、LogAnalysis
```

### 周二：专家答案和参考实现

目标：写出 AI 应该学习的高质量答案。

输出：

```text
1 份专家参考答案
1 份可复用代码或命令
1 组边界条件说明
```

示例：

```text
参考答案结构：
1. 当前日志只能证明 SystemCommitUsedPct 偏高。
2. 不能直接证明 OOM，除非看到 allocation failure 或进程被系统终止。
3. 需要补充 MemoryStats 全段、进程退出码、Cook 阶段、Shader 编译器模式。
4. 下一步搜索关键词：Ran out of memory allocating、MemoryStats、Fatal error、ShaderCompileWorker。
```

### 周三：当前模型试跑和错误收集

目标：让 AI 先答，再记录它错在哪里。

输出：

```text
模型原始回答
错误点列表
错误类型标签
```

错误类型示例：

- 概念幻觉：编造不存在的 UE API。
- 证据不足：没有日志证据就下结论。
- 版本混淆：把 UE4 行为套到 UE5。
- 工程不可用：代码无法编译或缺模块依赖。
- 过度泛化：只给“降低材质复杂度”这类空泛建议。
- 忽略约束：没有考虑平台、线程、GC、Cook、Pak、网络同步。

### 周四：Rubric 和改进建议

目标：把专家判断变成可评分规则。

输出：

```text
评分 Rubric
正例 / 反例
训练改进建议
```

Rubric 示例：

```text
满分 10 分：
2 分：准确识别任务类型和上下文
2 分：引用输入证据
2 分：区分事实、推测和缺失信息
2 分：给出可执行验证步骤
1 分：给出合理修复建议
1 分：说明风险和副作用
```

### 周五：整理为训练资产

目标：把本周材料沉淀成可复用资产。

输出：

```text
1 条训练样本
1 条评测样本
1 条偏好样本
1 条失败模式记录
```

建议文件归档：

```text
Career/Codex/UE5-AI训练方向学习计划.md
08-AI游戏开发训练集/评测任务/
08-AI游戏开发训练集/参考实现/
08-AI游戏开发训练集/失败模式/
08-AI游戏开发训练集/Rubric评分标准/
```

### 周末：端到端任务包

目标：做一个完整闭环。

输出：

```text
任务包
输入材料
专家答案
AI 错误样例
Rubric
改进建议
复测记录
```

任务包例子：

- UE5 Lumen 漏光排查包
- Shader 编译错误修复包
- Unreal Insights 性能诊断包
- Editor Utility 资源审计工具包
- Replication Bug 排查包
- Cook / Package 失败分析包

---

## Day-by-day Routine 示例

### Day 1：UE Debug 任务定义

时间：60-90 分钟

行动：

1. 选一个真实 UE 问题，例如 Cook 失败、Crash、Shader 编译失败。
2. 截取最小输入材料。
3. 写任务卡。
4. 标注任务类型和难度。

产出：

```text
任务卡：UE-Debug-Cook-OOM-001
输入材料：Cook log 片段、MemoryStats、命令行
期望输出：判断是否 OOM，并给验证步骤
```

完成标准：

- 任务描述清楚。
- 输入材料足够让专家开始判断。
- 没有泄露项目敏感信息。

### Day 2：专家参考答案

时间：90 分钟

行动：

1. 自己按专家流程解题。
2. 写出结论、证据、缺失信息、验证步骤。
3. 补充错误答案示例。

产出：

```text
专家答案：UE-Debug-Cook-OOM-001-answer.md
错误答案：UE-Debug-Cook-OOM-001-bad-answer.md
```

完成标准：

- 结论不超出证据。
- 验证步骤能实际执行。
- 至少列出 3 个常见误判。

### Day 3：AI 试跑

时间：60 分钟

行动：

1. 把 Day 1 的任务输入给 AI。
2. 保存模型原始输出。
3. 不立即改 prompt，先记录自然表现。
4. 对照专家答案标注问题。

产出：

```text
模型输出：UE-Debug-Cook-OOM-001-model-output.md
错误标注：UE-Debug-Cook-OOM-001-error-analysis.md
```

完成标准：

- 保留原始回答。
- 错误点具体到句子或判断。
- 每个错误都有类型标签。

### Day 4：Rubric 和偏好样本

时间：90 分钟

行动：

1. 为任务写 10 分制 Rubric。
2. 把专家答案和模型答案组成偏好样本。
3. 写清楚为什么 A 优于 B。

产出：

```text
Rubric：UE-Debug-Cook-OOM-001-rubric.md
偏好样本：UE-Debug-Cook-OOM-001-preference.jsonl
```

完成标准：

- Rubric 可复用到同类问题。
- 偏好理由不是“更专业”，而是具体指出证据、流程、可验证性差异。

### Day 5：训练改进建议

时间：45-60 分钟

行动：

1. 总结模型失败模式。
2. 判断适合 SFT、DPO、RAG 还是 Tool-use。
3. 写一条改进建议。

产出：

```text
失败模式：过早归因 OOM
建议：增加日志证据链任务；训练模型区分 high memory、allocation failure、process killed
```

完成标准：

- 改进建议能转成数据需求。
- 不是泛泛地说“加强 UE 知识”。

### Day 6：端到端任务包

时间：3-4 小时

行动：

1. 整理本周所有材料。
2. 补齐输入、答案、错误样例、Rubric。
3. 用同一任务再次测试优化后的 prompt 或流程。

产出：

```text
完整任务包：UE-Debug-Cook-OOM-001/
复测记录：优化前 4/10，优化后 7/10
```

完成标准：

- 其他人拿到任务包也能复测。
- 输入、答案、评分标准彼此一致。
- 明确下一轮要补什么数据。

### Day 7：轻量复盘和连接

时间：30-60 分钟

行动：

1. 写本周复盘。
2. 更新技术雷达。
3. 把任务包链接到相关 UE 概念、源码、性能笔记。
4. 选择下周主题。

产出：

```text
周复盘：本周完成 1 个 UE Debug 任务包
连接：[[Cook]]、[[内存管理]]、[[Unreal Insights]]、[[AI游戏开发评测]]
下周主题：UE Shader 编译错误修复
```

完成标准：

- 至少 3 个双向链接。
- 写出“对我的工作/项目有什么启发”。
- 下周任务具体到可执行场景。

---

## Example Week Outcome

### 本周主题

UE5 Cook 内存问题诊断。

### 本周资产

```text
任务卡：UE-Debug-Cook-OOM-001
专家答案：1 份
模型原始输出：1 份
错误分析：1 份
Rubric：1 份
偏好样本：1 条
训练建议：1 条
复测记录：1 份
```

### 模型问题

当前模型看到 `SystemCommitUsedPct` 高就直接判断 OOM，但没有检查：

- 是否存在 allocation failure。
- 是否存在进程被系统杀死。
- 是否存在 UE Fatal error。
- Cook 当前阶段。
- Shader 编译器模式。
- 内存增长来源。

### 专家改进建议

增加一组 UE Cook 日志诊断训练样本，重点训练模型：

```text
区分高内存现象、OOM 证据、OOM 原因。
```

训练数据应覆盖：

- 真 OOM。
- 高内存但未 OOM。
- Shader 编译导致内存高。
- Package 阶段积压导致内存高。
- 外部进程导致系统 commit 高。

### 可展示成果

面试或工作汇报时可以这样表达：

> 我不是只让模型学习 UE5 概念，而是把真实 Cook 内存问题拆成评测任务、专家答案、错误样例和 Rubric。通过对比模型原始输出和专家答案，可以明确发现模型过早归因 OOM 的失败模式，并进一步转化为训练数据需求。

---

## 长期里程碑

### 2 周

- 完成 2 个 UE Debug 任务包。
- 建立统一任务模板。
- 沉淀第一版 Rubric。

### 4 周

- 覆盖 Debug、CodeGen、Perf 三类任务。
- 每类至少 3 个样本。
- 能稳定指出模型 5 种以上失败模式。

### 8 周

- 建成一个小型 UE-AI 评测集。
- 每个任务都有专家答案和评分标准。
- 能证明 prompt、RAG 或训练数据带来的提升。

### 12 周

- 形成可展示 Portfolio：
  - UE 任务评测集
  - 专家参考实现
  - 模型失败模式分析
  - 训练改进建议
  - 端到端复测报告

---

## 关联 / 输出产物

- [[UE5]]
- [[游戏开发]]
- [[性能优化]]
- [[Shader]]
- [[Cook]]
- [[Unreal Insights]]
- [[技术雷达与工具栈]]
- [[面试与职业复盘日志]]

