---
tags: [paper/signed, paper/engineering-blog, paper/AI-harness, paper/agentic-AI, paper/已应用到工作]
aliases: [Anthropic-Building-Effective-Agents, Anthropic-Agent-Patterns, Anthropic-Workflows-vs-Agents, Anthropic-Orchestrator-Workers]
---

# Anthropic — Building Effective Agents: AI Agent 设计模式元方法论 (Engineering Blog, 2024-12)

| 字段 | 内容 |
|------|------|
| **文章标题** | Building Effective Agents |
| **作者/机构** | Anthropic Engineering (Erik Shurtz, Barry Zhang 等) |
| **发布** | 2024-12-19 (Anthropic engineering research blog) |
| **类型** | **Engineering blog / 工业 playbook**（非 arXiv 论文；anthropic.com/research/building-effective-agents）|
| **核心内容** | 5 个工作流模式 + 2 个 building block + agents vs workflows 决策框架 |
| **配套生态** | Anthropic Console / Agent SDK / MCP / Claude Computer Use |
| **同源 short note** | (待 cron curator 落 `GDC/Minimax/2024/`) — 本文是其深度展开 |
| **阅读日期** | 2026-07-27 |
| **精读时长** | ~35 min |

---

## 一句话总结

> Anthropic 在 2024-12-19 发布的 **agent design playbook** —— **把 LLM agent 系统拆成「5 个工作流模式 (prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer) + 2 个 building block (augmented LLM / autonomous agent)」+「workflows vs agents 决策框架」**，**核心论断**：「**从最简单开始，按需加复杂度**」「**默认 workflows，agents 只在真正需要时用**」「**autonomous agent 慎用，成本 / 可靠性 / 安全性三高风险**」。**对 day-job 的启发**：**day-job Mac Game Harness v0.1 架构决策的元方法论依据** —— **每个 MCP 工具调用该用哪种 pattern，每个子任务该派给谁，每个失败该怎么重试**——**全部能从这 5 个 pattern 推出来**；**这与 paper 6 (Anthropic Computer Use) 形成完整族**（paper 6 = 单个 GUI agent 范式，本文 = agent 系统级设计模式）。

---

## 核心创新点

### 0. 最重要的元论断 (放在最前面)

**Anthropic 明确区分两件事**：

- **Workflows**：「**通过预定义代码路径编排 LLM 和工具的系统**」—— **控制流是开发者写的，LLM 只是其中一个节点**。**可预测 / 可调试 / 成本可控**。
- **Agents**：「**LLM 动态决定自己的 process 和 tool usage，保留对'如何完成任务'的控制**」—— **控制流是 LLM 自主产生的**。**灵活 / 涌现 / 但成本 / 可靠性 / 安全性难管**。

**关键判断**：**「agent」这个词被市场滥用了**——**大多数自称「agent」的产品其实是 workflows**。**Anthropic 自己说：能不用 agent 就不用 agent**。**对 day-job 启发**：**day-job Mac Game Harness v0.1 应该 90% 是 workflows + 10% autonomous agent**——**别上来就搞 autonomous agent**。

### 1. **Augmented LLM — 一切的起点**

> An **augmented LLM** is the foundation. It has access to retrieval, tools, and memory to expand its capabilities.

**Anthropic 的最小可工作单元**——一个 **LLM** + 三个增强：
- **Retrieval**（RAG / 知识库）—— 让 LLM 看到 domain context
- **Tools**（API / 函数 / MCP）—— 让 LLM 行动
- **Memory**（对话 / 长期）—— 让 LLM 累积经验

**对 day-job 启发**：**day-job Mac Game Harness 的 base = Augmented LLM (Claude Sonnet) + MCP tools (UE editor / Xcode / git) + RAG (engine API docs / coding style) + Memory (per-task scratchpad)**。**任何 agent 模式都跑在这个 base 上**。

### 2. **Pattern 1: Prompt Chaining — 顺序 LLM 调用链**

> Split a task into fixed sequence of steps. Each LLM call processes the output of the previous.

**典型场景**：
```
Input → LLM₁ (提取关键信息) → LLM₂ (按 schema 格式化) → LLM₃ (翻译成目标语言) → Output
```

**关键技术点**：
- **每步可以加「gate」**（断言 / 评分）—— 不满足就 fallback
- **典型 usage**：UE error log → extract C++ class name → query MCP for class definition → format as commit message
- **优点**：**简单 / 可调试 / 成本可控**（每步独立计费）
- **缺点**：**不灵活**（pipeline 写死了）

**对 day-job 启发**：**Mac Game Harness 30% 任务是 prompt chaining**——**编译 → analyze → format → commit message**这种固定 pipeline。**用 LangChain LCEL / Anthropic Prompt Caching 优化成本**。

### 3. **Pattern 2: Routing — 分类 + 分发**

> Classify input, then route to specialized handler.

**典型场景**：
```
Input → Classifier (LLM) → {UE_Code_Agent | Git_Agent | Doc_Agent | Test_Agent | Human_Escalation}
```

**关键技术点**：
- **Classifier 用 cheap model**（Haiku 3.5 / Sonnet-mini）—— **不要用旗舰模型做分类**
- **每个 route 一个 specialized prompt / tool set** —— 不互相干扰
- **典型 usage**：用户说「编译 UE」→ 路由到 UE_Build_Agent；说「commit」→ 路由到 Git_Agent；说「解释这段 C++」→ 路由到 Doc_Agent
- **优点**：**模块化**（每个 route 独立维护 / 升级）
- **缺点**：**classifier 错就全错**（**要求 classifier 准确率 >99%**）

**对 day-job 启发**：**Mac Game Harness 的 Task Router = Routing pattern**——**classifier 决定走 MCP-first / GUI-fallback / Human-escalation**（这跟 paper 6 的 Tool Router 是一个东西，只是 pattern 名称不同）。**Anthropic 推荐用 cheap classifier (Haiku 3.5 $1/1M token) 而不是旗舰**。

### 4. **Pattern 3: Parallelization — 并行 LLM 调用**

> Multiple LLM calls in parallel, aggregate results. Two sub-patterns: **sectioning** (parallel tasks) / **voting** (parallel same task for consensus).

**Sectioning 典型场景**：
```
Input → LLM₁ (分析语法)   ↘
      → LLM₂ (分析语义)   → Aggregator → Output
      → LLM₃ (分析性能)   ↗
```

**Voting 典型场景**：
```
Input → LLM₁ (独立评分)  ↘
      → LLM₂ (独立评分)  → Aggregator (取一致答案) → Output
      → LLM₃ (独立评分)  ↗
```

**关键技术点**：
- **Sectioning 用于「把大任务拆 3-5 块并行」**——**用 Sonnet 而不是 Opus 加速**（Sonnet 已经够好，便宜 5x）
- **Voting 用于「提高准确率」**——**3-5 个独立 LLM call 投票，牺牲成本换准确率**
- **典型 usage**：PR review = parallel lint + parallel test + parallel style-check + parallel security-scan → aggregate
- **优点**：**快**（N 个 LLM 并行 = 1 个时间）/ **准**（voting）
- **缺点**：**贵**（N 倍 token）/ **不能处理依赖任务**

**对 day-job 启发**：**Mac Game Harness 30% 任务是 parallelization**——**「编译 + lint + test + security-scan 4 件并行」**比顺序快 4x。**Voting pattern 用于「评估 / 评分」**——**Code Review Score 跑 3 个独立 Claude 投票取中位数**。

### 5. **Pattern 4: Orchestrator-Workers — 中央调度 + 多个 worker**

> Orchestrator LLM dynamically breaks down task, dispatches to worker LLMs, synthesizes results.

**典型场景**：
```
User Goal → Orchestrator (LLM, Sonnet/Opus)
              ├─ Worker₁: Research Agent (search docs)
              ├─ Worker₂: Code Agent (write UE C++ class)
              ├─ Worker₃: Test Agent (write test cases)
              └─ Worker₄: Deploy Agent (git commit + push)
            → Synthesizer → Final Output
```

**关键技术点**：
- **Orchestrator 决定「拆不拆 / 怎么拆 / 派给谁」**——**不是 fixed pipeline，是 dynamic 的**
- **每个 worker 可以用不同 model**（orchestrator Opus 4.1 / worker Sonnet 4.5 / cheap tasks Haiku 3.5）
- **Worker 之间可以通信**（via shared scratchpad / message bus）
- **典型 usage**：agentic IDE（VS 2026 Copilot Agent Mode / Devin / Cursor Agent）—— 跟 paper 4 (Microsoft VS 2026) 是**同构**（paper 4 描述实现，本文描述 pattern 分类）
- **优点**：**复杂任务可处理**（拆 5-10 个 worker 协调）
- **缺点**：**orchestrator 难调**（拆错 / 派错 / 综合错 都让整个系统失败）/ **成本高**（orchestrator 用 Opus + workers 用 Sonnet = 一次任务几美元）

**对 day-job 启发**：**Mac Game Harness v0.2 演进方向 = Orchestrator-Workers**——**当前 v0.1 是单 agent + 多个 tool，v0.2 升级到 1 orchestrator (Opus 4.1) + 5 workers (UE / Git / Test / Build / Doc)**。**但 v0.1 别上来就这么搞，先把单 agent 跑稳**。

### 6. **Pattern 5: Evaluator-Optimizer — 生成 + 评估闭环**

> Generator LLM produces output, Evaluator LLM provides feedback, loop until quality threshold met.

**典型场景**：
```
Input → Generator (LLM) → Output → Evaluator (LLM) → {pass → final | fail → feedback → Generator 2.0 → ...}
```

**关键技术点**：
- **Evaluator 必须独立于 Generator**（**不能 self-evaluate**——LLM 评估自己会 bias）
- **Evaluator 可以基于规则**（regex / schema check / test pass）—— **不一定要 LLM**
- **Loop 有 max iterations**（默认 3-5）—— 防止 infinite loop
- **典型 usage**：Code generation（generator 写代码 → evaluator 跑 test + lint + type-check → fail 就反馈 → generator 改）
- **优点**：**质量上限高**（多轮打磨）/ **可观察**（每轮有 evaluator 评分）
- **缺点**：**慢 + 贵**（N 轮 × Generator + N 轮 × Evaluator）

**对 day-job 启发**：**Mac Game Harness 关键代码生成任务 = Evaluator-Optimizer**——**Generator (Sonnet) 写 C++ class → Evaluator (编译 + UE lint + UE test) 跑 → fail 把 stderr 反馈给 generator → 下一轮**。**这是 paper 5 (SIMA 2) "self-improvement loop" 的具象化实现**。

### 7. **Autonomous Agent — 慎用**

> Agent dynamically directs its own process and tool usage. Retains control over how to accomplish task.

**关键论断**（Anthropic 自己强调）：
> 「**We recommend that developers start with the simplest solution possible and only increase complexity when needed. ... Agents are often implemented as just a tool calls in a loop with a prompt template. ... Wait. Do you really need agents? ... agents typically cost more, take longer to complete tasks, and may be less reliable than workflows.**」

**自主 agent 风险**：
- **成本**：单 task 5-50 USD（5-50 轮 LLM call + 截图 / tool 调用）
- **可靠性**：Computer Use 24% 准确率（paper 6）—— **3/4 任务会失败**
- **安全性**：prompt injection（paper 6 §4 mitigation）/ 不可预测行为
- **可控性**：agent 行为难 trace / 难 replay / 难 pause

**对 day-job 启发**：**Mac Game Harness v0.1 应该避免 autonomous agent**——**用 workflows 覆盖 90%，只在「用户明确说'你来搞定'」时进入 agent 模式**。**paper 6 (Computer Use) 就是 autonomous agent 的代表**——**它就是 Anthropic 自己说"慎用"的那个范式**。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按 day-job "LLM-driven UE on Mac" + "Mac Game Harness" 视角）：**

1. **5 个 pattern 是 day-job Mac Game Harness v0.1 架构决策的元方法论**。**每个 pattern 对位 harness 的具体组件**：
   - **Augmented LLM** = harness 的 base 架构（Claude Sonnet + MCP + RAG + Memory）
   - **Prompt Chaining** = 固定 dev workflow（compile → analyze → format → commit message）
   - **Routing** = Task Router（classifier 决定走哪个 specialized agent / tool）
   - **Parallelization** = 多件并行（lint + test + security-scan + format-check）
   - **Orchestrator-Workers** = v0.2 演进（1 Opus orchestrator + 5 Sonnet workers）
   - **Evaluator-Optimizer** = 关键代码生成（generator + 编译/lint/test 评估闭环）
   - **LLM RAG 训练**：harness 工程相关的 Q&A 应该挂 "5 patterns" 框架

2. **「从最简单开始」原则是 day-job v0.1 的元决策**。**Anthropic 自己强调**：「**start with the simplest solution possible and only increase complexity when needed**」「**agents are often implemented as just a tool calls in a loop**」「**Wait. Do you really need agents?**」—— **Anthropic 反对"上来就 autonomous agent"**。**对 day-job 启发**：
   - **v0.1 = 90% workflows + 10% agent**——**别上来就 agentic IDE**
   - **先跑通 Augmented LLM + Prompt Chaining + Routing**——**3 个最简单 pattern**
   - **再升级 Parallelization + Evaluator-Optimizer**——**中等复杂度**
   - **最后才上 Orchestrator-Workers + Autonomous Agent**——**高复杂度**
   - **LLM RAG 训练**：harness 架构相关的 Q&A 应该明确 "v0.1 应该 workflows 为主"

3. **Routing pattern 的 cheap classifier 建议直接照搬**。**Anthropic 推荐用 Haiku 3.5 ($1/1M token) 做 routing classifier**——**不要用旗舰模型 (Opus 4.1 $15/1M token) 做分类**。**对 day-job 启发**：
   - **Mac Game Harness 的 Task Router 用 Claude Haiku 3.5**——**classifier 15x 便宜**
   - **每个 route 的 specialized agent 才用 Sonnet 4.5 或 Opus 4.1**——**只在真需要时升级**
   - **LLM RAG 训练**：harness 架构相关的 Q&A 应该挂 "cheap classifier + expensive executor" 原则

4. **Evaluator-Optimizer 是 paper 5 (SIMA 2) self-improvement 的具象化**。**Anthropic pattern 5 (evaluator-optimizer) = SIMA 2 (paper 5) "self-improvement loop"**——**是同一件事的不同表述**。**对 day-job 启发**：
   - **Mac Game Harness 关键代码生成 = evaluator-optimizer**——**generator 写代码 → 编译/lint/test 评估 → fail 反馈 → 下一轮**
   - **Evaluator 可以是 LLM 也可以是规则**——**编译 / lint / type-check 是规则 evaluator**，**code review / 风格评分是 LLM evaluator**
   - **max_iterations = 3-5**——**防止 infinite loop**
   - **LLM RAG 训练**：harness 训练相关的 Q&A 应该挂 "evaluator-optimizer loop"

5. **Autonomous agent 风险约束 = paper 6 (Computer Use) 4 步 mitigation 的元理论依据**。**Anthropic 自己说 autonomous agent「cost more / take longer / less reliable」**——**paper 6 4 步 mitigation (VM 隔离 / 工具白名单 / human-in-loop / 全 trace) 正是为这些风险设的护栏**。**对 day-job 启发**：
   - **Mac Game Harness 走 agent 模式时**——**4 步 mitigation 必须全套照搬**（paper 6 详述）
   - **关键操作（commit / push / delete / deploy）必须 human-in-loop**——**agent 不可全权委托**
   - **agent 单 task 成本 5-50 USD**——**月度预算必须设上限**
   - **LLM RAG 训练**：harness 安全相关的 Q&A 应该挂 "agent 风险约束 + 4 步 mitigation"

6. **Orchestrator-Workers 是 v0.2 演进的明确方向**。**当前 v0.1 = 1 agent + 多个 tool**；**v0.2 = 1 orchestrator + 5 workers**。**对 day-job 启发**：
   - **v0.1 不要上来就 orchestrator-workers**——**先把 single agent 跑稳**
   - **v0.2 升级路径**：Opus 4.1 orchestrator (复杂任务拆分) + Sonnet 4.5 workers (UE / Git / Test / Build / Doc)
   - **每个 worker 可以独立演化**——**比如 UE worker 后续可以升级到 multi-agent (UE editor + UE compile + UE debug)**
   - **LLM RAG 训练**：harness 架构相关的 Q&A 应该挂 "v0.1 → v0.2 演进路径"

7. **"Workflows vs Agents" 决策框架是 harness UX 的元命题**。**Anthropic 说「大多数自称 agent 的产品其实是 workflows」**——**Bitmagic (paper 2) 自我定位"prompt-玩-迭代" 是 workflow，不是 autonomous agent**。**对 day-job 启发**：
   - **day-job Mac Game Harness 应该明确定位为 "workflows-first harness"**——**不是"agentic IDE"**
   - **UX 上要明确告诉用户"这是 workflow 还是 agent"**——**别让用户误以为 agent 能全权搞定**
   - **OSWorld 24% (paper 6) 就是 agent 真实水平**——**用户预期管理很关键**
   - **LLM RAG 训练**：harness UX 相关的 Q&A 应该挂 "workflows vs agents 决策框架"

---

## 实现难点

| 难点 | 详细 | 缓解 |
|------|------|------|
| **Pattern 选择错误** | 简单任务上 agent 浪费 50x 成本，复杂任务上 workflow 写死跑不通 | 先用 prompt chaining / routing 试，不行再加 parallelization / evaluator-optimizer，**避免一上来 orchestrator-workers** |
| **Routing classifier 准确率** | classifier 错路由就全错 | ① 用 cheap model (Haiku 3.5) 但**配高阈值**（>0.95 confidence 才自动路由，<0.95 转 human）② classifier 失败 fallback 到 "all routes" 并行 |
| **Orchestrator 死循环** | orchestrator 派 worker → worker 失败 → orchestrator 再派 → infinite loop | ① max_iterations = 5-10 ② 每个 worker 失败 3 次转 human ③ 整 task 失败 3 次 abort |
| **Evaluator 评分 bias** | LLM evaluator 自评自己代码会 bias（"我觉得我写得不错"） | ① evaluator 用独立 prompt（看不到 generator 推理过程）② 优先用规则 evaluator（编译 / lint / test）③ LLM evaluator 只用于"软指标"（风格 / 可读性） |
| **Parallelization 成本** | 5 个并行 LLM call = 5x token | ① cheap task 用 Haiku 3.5 ($1/1M) ② prompt caching (Anthropic 2024-08 feature) 减少 80% input token ③ batch API 异步跑 |
| **Autonomous agent 成本** | 单 task 5-50 USD | ① max_steps = 50 ② total_budget 硬上限（per task + per day）③ 任何 >10 USD 操作前 human 确认 |
| **State 共享** | 多 worker 之间共享 context（scratchpad / memory） | 用 Redis / Postgres 做 shared state，**不要 in-memory**（进程崩溃就丢） |
| **可观测性** | 多 pattern 嵌套后 trace 难 | 每个 pattern 配 trace_id，**所有 LLM call + tool call 落 log**，出事故能 replay |

---

## 是否值得复现

**强烈建议复现 P0**。**5 个 pattern 是 day-job Mac Game Harness 架构的「设计模式目录」**——**没有这个目录，每个子任务都从零设计**。

**最小复现路径（估 3-5 天）：**

- [ ] **Step 1 (0.5 天)**：用 LangGraph / Anthropic Agent SDK 搭 Augmented LLM base（Claude Sonnet + MCP tools + 简单 RAG）
- [ ] **Step 2 (0.5 天)**：实现 Prompt Chaining pattern（compile → analyze → format → commit message demo）
- [ ] **Step 3 (0.5 天)**：实现 Routing pattern（Task Router + 4-5 个 specialized sub-agents）
- [ ] **Step 4 (0.5 天)**：实现 Parallelization pattern（lint + test + format + security-scan 4 件并行）
- [ ] **Step 5 (1 天)**：实现 Evaluator-Optimizer pattern（generator + 编译/lint/test evaluator + max_iterations=3）
- [ ] **Step 6 (1 天)**：（可选）实现 Orchestrator-Workers pattern（1 Opus orchestrator + 5 Sonnet workers）
- [ ] **Step 7 (0.5 天)**：写 README + 5 个 pattern 的 case study + 发到 vault

**产出物**：
- `Career/Kimi/UE5_Training_MCP/agent-patterns/` —— 5 个 pattern 的 reference implementation
- `Routine/05-技术雷达/P0-必看/Anthropic-5-Patterns-Reference.md` —— 中文版 playbook
- `Routine/06-职业复盘日志/interview-card-5-patterns.html` —— 面试 QA 卡牌

---

## 关键术语表

| 术语 | 解释 |
|------|------|
| **Augmented LLM** | LLM + retrieval + tools + memory，最小可工作单元 |
| **Workflows** | 预定义代码路径编排 LLM / 工具，**控制流是开发者写的** |
| **Agents** | LLM 动态决定自己的 process / tool usage，**控制流是 LLM 自主产生** |
| **Prompt Chaining** | 顺序 LLM 调用链，每步处理上一步输出 |
| **Routing** | 分类 + 分发到 specialized handler |
| **Parallelization** | 并行 LLM 调用（sectioning 拆任务 / voting 取共识）|
| **Orchestrator-Workers** | 中央 LLM 拆任务 + 多个 worker LLM 并行 + synthesizer 汇总 |
| **Evaluator-Optimizer** | Generator LLM + Evaluator LLM 闭环，max_iterations 防止死循环 |
| **Autonomous Agent** | 完全自主 agent，**Anthropic 自己说慎用** |
| **cheap classifier** | 路由分类用便宜模型（Haiku 3.5 $1/1M），不要用旗舰（Opus 4.1 $15/1M）|
| **gate** | Prompt Chaining 中间加的断言 / 评分点，不满足就 fallback |
| **max_iterations** | Evaluator-Optimizer 闭环的最大轮数，默认 3-5 |
| **scratchpad** | 多 agent 间共享的 context / memory（Redis / Postgres）|
| **shared state** | 多 worker 共享的状态存储 |
| **trace_id** | 单个 task 的可观测 ID，所有 LLM/tool call 落 log |

---

## 整体架构图（伪代码）

```
┌──────────────────────────────────────────────────────────────┐
│  Day-Job Mac Game Harness v0.1 / v0.2                       │
│  (按 Anthropic Building Effective Agents 5 patterns 搭建)     │
└──────────────────────────────────────────────────────────────┘

                          ┌──────────────────┐
                          │   User Request   │
                          └────────┬─────────┘
                                   │
                          ┌────────▼─────────┐
                          │  Pattern 2:      │  ← cheap classifier (Haiku 3.5)
                          │  Routing         │     决定走哪个 pattern / agent
                          │  (Task Router)   │
                          └────────┬─────────┘
                                   │
                ┌──────────────────┴──────────────────┐
                │                                     │
       ┌────────▼────────┐                   ┌────────▼────────┐
       │  Pattern 1:     │                   │  Pattern 4:     │
       │  Prompt Chaining│                   │  Orchestrator-  │
       │  (固定 pipeline)│                   │  Workers        │
       │                 │                   │  (v0.2 演进)    │
       │ compile →       │                   │                 │
       │ analyze →       │                   │ Opus Orchestrator
       │ format →        │                   │  ├─ Worker: UE
       │ commit msg      │                   │  ├─ Worker: Git
       └────────┬────────┘                   │  ├─ Worker: Test
                │                             │  └─ Worker: Doc
                │                             └────────┬────────┘
                │                                      │
       ┌────────▼────────┐                              │
       │  Pattern 3:     │                              │
       │  Parallelization│  ← 多个 LLM 并行 (lint/test/  │
       │  (multi-check)  │     format/security-scan)      │
       │                 │                              │
       │ Lint   ↘        │                              │
       │ Test    → merge │                              │
       │ Format ↗        │                              │
       └────────┬────────┘                              │
                │                                      │
                └──────────────────┬───────────────────┘
                                   │
                          ┌────────▼─────────┐
                          │  Pattern 5:      │  ← 关键代码生成
                          │  Evaluator-      │
                          │  Optimizer       │
                          │                 │
                          │ Generator (Sonnet) → Code
                          │ Evaluator (compile + lint + test)
                          │ fail → feedback → Generator v2
                          │ max_iterations = 3-5
                          └────────┬─────────┘
                                   │
                          ┌────────▼─────────┐
                          │  Building Block: │
                          │  Augmented LLM   │
                          │                 │
                          │ Claude Sonnet 4.5
                          │  + MCP tools     │
                          │  + RAG (docs)    │
                          │  + Memory        │
                          └────────┬─────────┘
                                   │
                          ┌────────▼─────────┐
                          │  Optional:       │
                          │  Autonomous      │  ← 慎用 (paper 6 4 步 mitigation)
                          │  Agent (Computer │
                          │  Use fallback)   │
                          │                 │
                          │ OrbStack VM      │
                          │  + Tool whitelist
                          │  + Human-in-loop │
                          │  + Full trace    │
                          └──────────────────┘
```

---

## 相关论文 / 参考

| 引用 | 关系 |
|------|------|
| [[arxiv/2024-Anthropic-ComputerUse-OSAgent]] | **同源同主题** —— paper 6 = Computer Use 是「单个 GUI agent 范式」；本文 = 5 个 pattern 是「agent 系统级设计模式」；**两者形成完整族**（paper 6 是 pattern 7 "autonomous agent" 的工业代表） |
| [[GDC/2026-GoogleDeepMind-SIMA2-GenericGameAgent]] | **同主题** —— paper 5 "self-improvement loop" = 本文 Pattern 5 (Evaluator-Optimizer) 的具象化 |
| [[GDC/2026-Microsoft-VS2026-Copilot-GameDev]] | **同主题** —— paper 4 描述 VS 2026 Copilot Agent Mode 实现 = 本文 Pattern 4 (Orchestrator-Workers) 的工业实现 |
| [[GDC/2026-Bitmagic-AINativeGameEngine]] | **同主题** —— paper 2 "prompt-玩-迭代" 是 Workflows（不是 Agents）—— **本文元框架明确这一点** |
| [[GDC/2026-Tencent-Timi-AgenticAI-GameDev-98pct]] | **同主题** —— paper 1 "98% 自动化" 实际是 Orchestrator-Workers 模式（不是 single autonomous agent） |
| [[GDC/2026-GlassBeadGames-MultiAgentGameStudio]] | **同主题** —— paper 3 "4 人 + 8 agents" 实际是 Routing + Orchestrator-Workers 模式 |
| [[arxiv/Wang-2026-Agentopia]] | **同主题扩展** —— Agentopia 是 agent 社会长期模拟，对位本文 Pattern 4 (Orchestrator-Workers) 长期运行场景 |
| Anthropic Computer Use (2024-10) | **同源** —— paper 6 详述 |
| OpenAI Operator (2025-01) | **同源** —— paper 6 对比 |
| MemGPT (arXiv:2310.08560) | **相关方向** —— agent memory 持久化（本文 Augmented LLM "memory" 的深度展开） |
| Voyager (arXiv:2305.16291) | **相关方向** —— Minecraft skill-library agent，对位本文 Pattern 4 (Orchestrator-Workers) 长期运行场景 |
| Anthropic Prompt Caching (2024-08) | **同源优化** —— 本文 Parallelization pattern 的成本优化关键 |
| LangGraph / Anthropic Agent SDK | **落地工具** —— 5 个 pattern 的工程实现框架 |
| AWS Strands Agents / Google ADK | **对比实现** —— 5 个 pattern 的另一种工程化 |

---

## 输出 / 借鉴

**1. day-job Mac Game Harness v0.1 架构决策元方法论**
- **明确 v0.1 范围**：Augmented LLM + Prompt Chaining + Routing + Parallelization + Evaluator-Optimizer（**5 个 pattern 中的前 5 个**），**不**上 Orchestrator-Workers / Autonomous Agent
- **Routing classifier 用 Haiku 3.5**——**15x 便宜**
- **关键代码生成任务用 Evaluator-Optimizer**——**generator + 编译/lint/test 评估闭环**
- **v0.2 演进路径**：加 Orchestrator-Workers（1 Opus + 5 Sonnet workers）
- **v0.3 演进路径**：在 user 明确说"你来搞定"时启用 Autonomous Agent（Computer Use fallback，paper 6 4 步 mitigation）

**2. LLM RAG 训练语料增量**
- **新增 Q&A 主题**：
  - "Mac Game Harness 应该是 agent 还是 workflow？" → 答：90% workflows + 10% agent，Anthropic 自己说慎用 agent
  - "Routing 用什么 model 做 classifier？" → 答：Haiku 3.5 ($1/1M)，不用 Opus 4.1 ($15/1M)
  - "Evaluator-Optimizer 的 max_iterations 设多少？" → 答：3-5 轮
  - "什么时候用 Orchestrator-Workers？" → 答：v0.2，单 agent 跑稳后再升级
  - "Autonomous agent 最大风险是什么？" → 答：成本 / 可靠性 / 安全性 3 高，Anthropic 自己说慎用
- **新加 SOP/skills**：
  - "choose-agent-pattern-by-task.skill.md" — 根据任务选 5 个 pattern 之一
  - "setup-routing-classifier.skill.md" — Routing 模式 + Haiku 3.5
  - "setup-evaluator-optimizer-loop.skill.md" — 关键代码生成闭环

**3. 05-技术雷达 增量更新**
- **新加 P0 条目**："Anthropic 5 patterns as harness design playbook" —— 长期跟 Anthropic / OpenAI / Google 的 agent framework 演进
- **新加 P1 条目**："LangGraph / Anthropic Agent SDK / Google ADK" (P1 工具) —— 5 个 pattern 的工程实现
- **新加 P2 条目**："AWS Strands / OpenAI Swarm" (P2 工具) —— 对比框架

**4. 03-Shader与特效案例集 增量更新**
- (无直接关联) —— 保持原样

---

## 个人评价

**这篇是 day-job Mac Game Harness 架构的「设计模式目录」**。前 6 篇 AI Harness paper 都在讲"具体怎么做"（团队 / UX / IDE / 训练 / GUI fallback），**没一篇讲"该用哪种 pattern"**。**Anthropic 这篇 = 元方法论**。

**最有价值的 3 个 takeaway：**

1. **「从最简单开始」原则是 day-job v0.1 的元决策**。**Anthropic 自己强调**：「**start with the simplest solution possible**」「**Wait. Do you really need agents?**」—— **90% workflows + 10% agent**。**别上来就 autonomous agent**（paper 6 / Computer Use 就是 autonomous agent 的代表 —— **它就是 Anthropic 自己说"慎用"的那个范式**）。
2. **Routing 的 cheap classifier 建议直接照搬**——**Haiku 3.5 ($1/1M token) vs Opus 4.1 ($15/1M token)，15x 便宜**。**classifier 用便宜模型，executor 才用贵模型**。
3. **Evaluator-Optimizer 是 paper 5 (SIMA 2) self-improvement 的具象化**——**Generator (Sonnet) 写代码 → Evaluator (编译 / lint / test) 跑 → fail 反馈 → 下一轮**。**max_iterations = 3-5 防 infinite loop**。

**最被低估的 takeaway**：

**「Workflows vs Agents」决策框架** —— **Anthropic 说「大多数自称 agent 的产品其实是 workflows」**——**Bitmagic (paper 2) "prompt-玩-迭代" 是 workflow，不是 autonomous agent**。**day-job Mac Game Harness 应该明确定位为 "workflows-first harness"**。

**最被高估的 takeaway**：

**「Autonomous Agent = AI 未来」** 的市场宣传 —— **Anthropic 自己说"慎用"**——**5x-50x 成本 + 24% 准确率（paper 6）**。**真实场景 70%+ 失败率**。**别被 demo 视频骗了**。

---

## 面试谈资

**30 秒版（电梯演讲）：**

> "Anthropic 在 2024-12 发了《Building Effective Agents》playbook —— **把 LLM agent 系统拆成 5 个工作流模式 (prompt chaining / routing / parallelization / orchestrator-workers / evaluator-optimizer) + 2 个 building block (augmented LLM / autonomous agent)**。**核心论断**：「从最简单开始，按需加复杂度」「默认 workflows，agents 只在真正需要时用」「autonomous agent 慎用，成本 / 可靠性 / 安全性三高风险」。**对 day-job Mac Game Harness 的启发是 v0.1 架构决策的元方法论**——**5 个 pattern 中先实现前 4 个（augmented LLM / prompt chaining / routing / parallelization），关键代码生成用 evaluator-optimizer，v0.2 再加 orchestrator-workers**——**autonomous agent 只在 user 明确说'你来搞定'时启用**。**Routing 用 Haiku 3.5 classifier（$1/1M token），executor 才用 Sonnet 4.5**。"

**2 分钟版（深聊）：**

> "Building Effective Agents 是 Anthropic 在 2024-12 发的 agent design playbook。**最关键的元论断是 workflows vs agents 区分**——**workflows 是开发者预定义代码路径编排 LLM（控制流是开发者写的），agents 是 LLM 动态决定自己的 process 和 tool usage（控制流是 LLM 自主产生）**。**Anthropic 自己强调：「能不用 agent 就不用 agent」「agent 成本高 / 慢 / 可靠性差」**——**很多自称 agent 的产品其实是 workflows**。**5 个 workflow patterns**：① prompt chaining（顺序 LLM 调用）② routing（分类 + 分发）③ parallelization（并行 LLM 调用，sectioning 拆任务 / voting 取共识）④ orchestrator-workers（中央调度 + 多个 worker）⑤ evaluator-optimizer（generator + evaluator 闭环，max_iterations=3-5 防死循环）。**对 day-job Mac Game Harness 的架构影响**：**v0.1 = augmented LLM base + prompt chaining + routing + parallelization + evaluator-optimizer（前 4 个 pattern），不上 orchestrator-workers 和 autonomous agent**；**v0.2 加 orchestrator-workers（1 Opus orchestrator + 5 Sonnet workers：UE / Git / Test / Build / Doc）**；**v0.3 才在 user 明确说'你来搞定'时启用 autonomous agent（Computer Use fallback，paper 6 详述）**。**Routing classifier 用 Claude Haiku 3.5（$1/1M token），比 Opus 4.1（$15/1M token）便宜 15x**——**classifier 用便宜模型，executor 才用贵模型**。**Evaluator-Optimizer 是 paper 5 (SIMA 2) self-improvement loop 的具象化**——**Generator 写 C++ class → Evaluator 跑编译/lint/test → fail 把 stderr 反馈给 Generator → 下一轮**。**这是我看到的 day-job Mac Game Harness 架构的'设计模式目录'**——**前 6 篇 AI Harness paper 都在讲'具体怎么做'，没一篇讲'该用哪种 pattern'**——**本文补上这块**。"

---

## 输出产物

- [x] 本 paper note 落盘 `Routine/01-论文笔记库/arxiv/2024-Anthropic-BuildingEffectiveAgents.md`
- [x] 00-README.md 增量：第 7 篇 AI Harness 条目 + 1 段 day-job P0 主线对照表
- [ ] (后续) 5 pattern reference implementation → `Career/Kimi/UE5_Training_MCP/agent-patterns/`
- [ ] (后续) Mac Game Harness v0.1 架构决策元方法论 → `Routine/05-技术雷达/P0-必看/`
- [ ] (后续) 面试 QA 卡牌 → `Routine/06-职业复盘日志/interview-card-5-patterns.html`
- [ ] (后续) 7 篇 AI Harness 综合 detail HTML → `Routine/06-职业复盘日志/ai-harness-7-detail.html`

---

## Changelog

- 2026-07-27 23:42 — 初稿落盘（v0.1），基于 Anthropic engineering blog "Building Effective Agents" (2024-12-19) + Claude 4.5 family 模型价格 (2025-11 update)
