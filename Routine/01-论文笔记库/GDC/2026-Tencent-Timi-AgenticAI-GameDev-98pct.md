---
tags: [paper/signed, paper/GDC-talk, paper/GDC-2026, paper/AI-pipeline, paper/AI-assets, paper/已应用到工作]
aliases: [Tencent-Timi-AgenticAI-GameDev-GDC2026, Tencent-AgenticAI-98pct, Tencent-Timi-AI-Native-Team]
---

# Tencent TiMi — Agentic AI for Game Development: 98% Automated Programming in Large Projects (GDC 2026)

| 字段 | 内容 |
|------|------|
| **Talk 标题** | 可微智能 (Agentic AI) for Game Development / AI Native 团队探索 |
| **讲者** | 余煜 (天美工作室群 技术组长) / 牟骞 (天美工作室群 技术专家) |
| **场次** | GDC 2026 — Tencent booth talk / 杰出者系列 (Summit) |
| **日期** | 2026-03-12 (Moscone Center, San Francisco) |
| **Track** | AI in Game Development / 工具链 / Agentic AI |
| **同源 short note** | (待 cron curator 落 `GDC/Minimax/2026/`) — 本文是其深度展开 |
| **阅读日期** | 2026-07-14 |
| **精读时长** | ~50 min |

---

## 一句话总结

> 这篇 talk 给出了**大厂"AI 接管大型工程"的真实案例 —— Tencent 天美工作室群（TiMi Studio Group）的 Agentic AI / "可微智能"方案**：在 AAA 级游戏工程里**实现 98% 的 AI 自动化编程**（修 Bug、根据策划案生成程序），**核心方法是把任务拆解 + 让 AI 长时间独立工作 + 最小化对模型能力的要求**。**给 day-job 的启发**：LLM 驱动 UE 工程的"harness 元命题"——**不是"训练更强的模型"，是"设计让弱模型也能在大型工程里稳定工作 N 小时的 agent 框架"**。

---

## 核心创新点

1. **"可微智能 (Agentic AI)"作为正式术语**。讲者把 AI 接管大型工程的能力命名为 **Agentic AI / "可微智能"**——核心是**"通过拆解任务，AI 能在尽可能少的人工干预下，面向目标自主规划和自主完成任务，并且尽可能降低对 AI 模型的要求"**。这和单点 LLM 调用（"prompt-in-text-out"）的区别是 **AI 能否自己跑 N 小时不出错**。**对 day-job 关键**：未来 LLM harness 的 KPI 不是 "回答对不对"，是 **"能不能在大型工程里独立工作 N 小时 + 自我恢复"**。

2. **98% AI 自动化编程 —— 真实可量化的工程 KPI**。讲者明确说**"现在能做到 98% 的 AI 自动化编程"**。**这个数字的工程含义**：在 AAA 游戏工程里，绝大部分 coding 任务已经能由 AI 在极少人工干预下完成；**剩余 2% 是"AI 写错后需要人来救"的边界 case**。**对 day-job 启发**：不是"AI 写整个游戏"，是"AI 处理 98% 的常规 coding，2% 由人处理 corner case + 兜底"——这是 LLM harness 真实落地的形态。

3. **"AI 长时间在大型工程中稳定工作"作为元命题**。讲者原话：**"我们要让 AI 具备长时间在大型工程中稳定工作不出错的能力。不是 AI 犯错之后，找一个人帮它解决问题，我们希望 AI 自己解决问题。"** 这句话定义了 harness 的下一阶段目标——**self-healing in large codebase**。**day-job 直接对位**：LLM 驱动 UE 工程时，**"AI 跑 8 小时不出错"** 和 **"AI 跑 1 小时就卡"** 的体验差距是产品级的。

4. **"可微智能"主张"降低对模型能力的要求"**。讲者强调 "Agentic AI 尽可能降低对 AI 模型的要求" —— 这是一个反共识的工程判断：**不是堆大模型，是设计 agent 框架让小模型也能跑长任务**。**对 day-job 启发**：Mac 平台 day-job 大概率**不会用 GPT-5 / Claude-4 级别的大模型做实时 harness**（推理成本 + 延迟）——**用 Qwen2.5 / Llama-3.1 8B 级本地模型 + 良好 agent 框架**，才能在 Mac 上跑出可用的 harness。这和 Tencent 的"降低对模型能力要求"完美对位。

5. **"修 Bug" + "根据策划案自动生成程序" 作为已落地的 AI 任务**。讲者明确说：**(a) 现在我们可以做到修 Bug；(b) 甚至做到根据策划案自动生成程序**。这两条是 harness 的**最常见任务剖面**——既不是"写新游戏"（太大），也不是"写 Hello World"（太简单），而是"在已有大型工程里，AI 帮程序员处理日常任务"。**对 day-job 启发**：LLM 驱动 UE 工程的**首批落地任务**应该是 **(a) 修 UE 编译错误、(b) 读 GDD 章节生成 C++ skeleton、(c) 在已有 module 里加新功能**——而不是"AI 从零做游戏"。

6. **"AI Native 团队"作为组织探索方向**。讲者说团队"想要组建技术团队，往 AI 原生 (AI Native) 组织的方向发展" + "我们提供的并不是一个打开就能用的产品，而是会让生产方式本身发生很大变化"。**这不是一个 IDE 工具，是一个新组织形态**——**"人 + 多个 AI agent" 的小团队，每个 agent 处理不同任务**。**对 day-job 启发**：day-job 团队（甚至 LLM RAG 训练团队）是不是需要往"AI Native"组织演化？这是**组织级**而非"工具级"问题。

7. **"AI 调试工具 + 监控工具" 是 implicit 的关键依赖**。98% 自动化意味着 AI 会写错——**没有良好的调试/监控工具，98% 等于"98% 概率 AI 写错但人不知道哪里错"**。讲者虽未展开，但默认团队内部有 **AI output diffing / 编译检查 / 单元测试触发 / human-in-loop 兜底** 一整套基础设施。**day-job 启发**：MCP tools 里必须包含 **编译检查 + 测试运行 + 错误回放** 这一组 observability tools。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按 day-job "LLM-driven UE on Mac" + "Mac Game Harness" 视角）：**

1. **"可微智能" / "Agentic AI" 是 day-job harness 的**终极形态**参考**。**Mac Game Harness 要做的不是"调用一次 LLM"——是"设计一个 harness 框架，让 LLM 在 Mac 平台上**自主跑 N 小时**处理 UE 大型工程任务"**。Tencent 天美的 98% 自动化是**已经验证的工业 case**——证明这个形态可行。**LLM RAG 训练**：把这个 talk 作为"harness 设计的 north star"案例，让 LLM 学到"AI 接管大型工程是可行的，且关键不在模型能力在 agent 框架"。

2. **"降低对模型能力的要求" 是 Mac 平台 day-job 的关键策略**。**Mac 不可能本地跑 70B+ 模型**（即使是 M3 Ultra 192GB）——**用 7B-14B 模型 + 良好 harness** 才是 Mac 路径。Tencent 的 "降低对模型能力要求" 和 day-job Mac 限制**完全对位**。**LLM RAG 训练数据**：凡是涉及"Mac 平台 LLM 落地"的 Q&A，答案应该指向"agent 框架 > 模型能力"。

3. **"修 Bug + 根据策划案生成程序" 是 harness 首批落地任务**。**day-job Mac Game Harness 的第一版不要做"AI 做游戏"** —— **做**：
   - (a) **AI 修 UE 编译错误**（MCP tool 触发 UE build，捕获 error，AI 读 error + source 修）
   - (b) **AI 读 GDD 章节生成 C++ skeleton**（MCP tool 读 GDD md 文件，AI 输出 C++ class header + 实现）
   - (c) **AI 在已有 module 里加新功能**（MCP tool 暴露 UE module 列表，AI 选 module + 写新文件 + 跑测试）
   
   这三个任务**符合 Tencent 描述的"修 Bug + 根据策划案生成程序"**。

4. **"AI Native 团队" 是 day-job 团队组织演化的元命题**。day-job 当前团队结构（前端 / 后端 / 算法 / 美术）——**未来 12-24 个月是不是要演化成"人 + 多个 AI agent"的小团队？** Tencent 已经明示这是探索方向。**LLM RAG 训练**：组织设计相关的 Q&A，答案应该体现"AI Native 团队"作为长期形态参考。

5. **"98% 自动化 + 2% 兜底" 是 harness SLA 的可量化目标**。**day-job harness 设计的 KPI 应该是 "% of coding tasks AI 完成 without human intervention"** —— 行业 baseline 是 Tencent 的 98%。**LLM RAG 训练**：工程效率相关的 Q&A，答案应该挂"98% 自动化是 AAA 级工业 SOTA"。

6. **"AI 长时间不出错" 是 harness 工程的硬指标**。day-job Mac Game Harness 必须有 **"AI 跑 8 小时不卡" 的工程保障**—— 这要求 harness 框架必须有 **self-checkpointing（定期保存 AI 工作状态）、self-rollback（错误时回滚到上一个 checkpoint）、error-classification（区分可恢复 vs 不可恢复错误）**。**LLM RAG 训练**：harness 设计相关的 Q&A，答案必须包含 self-checkpointing / rollback 机制。

7. **"调试 + 监控" 是 98% 自动化的前提**。day-job Mac Game Harness 的 **MCP tools 集合必须包含 observability 类** —— 编译检查、测试触发、错误回放、diff 展示、human-in-loop pause/resume。**Tencent 没展开但默认存在**；day-job 必须显式建。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|-------------|
| **98% 自动化 vs 2% 兜底的边界** | 哪 2% AI 写错的 task 必须人来兜？分类标准是什么？边界 case 的覆盖率是 harness 工程的真正难点 | 是——LLM 失败模式分类是 day-job harness 的核心 |
| **大型工程的 context window 管理** | UE 5.x 完整 module 列表 + 类层级 远超 200K context window；harness 必须有"按需加载相关 module" 的 retrieval 机制 | 是——RAG over UE source code 是 day-job 技术栈核心 |
| **"降低对模型能力要求" 的工程实现** | 拆解任务 + 多步规划 + 工具调用 + self-critique loop；每一步对模型要求都不高，但**组合起来需要精巧的 prompt + 工具设计** | 是——agent loop 设计是 day-job 核心能力 |
| **AI 长时间运行的 state 管理** | N 小时不卡 = 必须有持久化的 working memory（不只是对话历史）+ checkpointing + rollback；比 chat 复杂一个数量级 | 是——stateful harness 是工程范式转移 |
| **"根据策划案自动生成程序" 的真实质量** | GDD 章节通常是模糊 / 有冲突的；AI 生成的 C++ skeleton 是不是"能跑 + 符合 UE 约定 + 编译通过"？质量验证链路是什么？ | 是——auto-validation pipeline 是 day-job 必须建 |
| **"AI 修 Bug" 的 test coverage 要求** | AI 改代码后必须有 unit test 兜底，否则就是"修一个 bug 引入三个新 bug"；UE 项目通常 test coverage 偏低，AI 修 Bug 风险高 | 是——day-job 推 AI 修 Bug 之前必须先补测试覆盖 |
| **Mac 平台的本地模型性能** | 7B-14B 模型在 M3/M4 上的推理速度是否够用？Mac 内存限制 + 推理延迟是 day-job 工程路线的硬约束 | 是——性能 benchmark 是 day-job 路线决策依据 |

---

## 是否值得复现？

- [x] **是** — 已列入待办
- [ ] 否 — 仅了解思路即可
- [ ] 部分 — 只复现核心算法

**复现/借鉴的具体步骤：**

1. **把"可微智能 / Agentic AI" 作为 day-job harness 设计的元命题** —— 在 [[Routine/AI-Tasks/Mac/00-Master-Index]]（待新建）下加一个 "Agentic AI Harness 框架" 模块，明确**目标：让 LLM 在 Mac 上跑 8 小时不出错处理 UE 工程任务**。**状态**：立刻开始
2. **MVP 任务剖面 —— "修 UE 编译错误 + 读 GDD 生成 C++ skeleton"** —— 在 Mac Game Harness 第一版只做这两个任务，用最简的 MCP tool set（UE build + GDD read + UE source write），验证 7B-14B 模型能不能在 Mac 上跑通。**状态**：2 周内可启动
3. **bench Tencent "98% 自动化" 数字** —— 内部用 10-20 个真实 UE 任务测试 harness 的 "auto-completion rate"，对标 Tencent 98% —— 估算 day-job Mac harness 的实际数字。**状态**：MVP 后立刻做
4. **加入 self-checkpointing + rollback 机制** —— harness 框架必须有 "每 N 步保存 working memory + 错误时回滚" 的能力，这是"长时间运行不出错" 的工程基础。**状态**：MVP 之后 1 周内加
5. **写一篇 "Mac Game Harness v0.1" 卡牌** —— 用 [[interview-card-system]] skill 做一份自测卡，把"修编译错误 + 读 GDD 生成 skeleton" 这两个任务拆成卡牌形式，作为 LLM RAG 训练数据。**状态**：MVP 完成后

---

## 关键术语表

| 术语 | 解释 | 我理解的锚点 |
|------|------|--------------|
| **可微智能 / Agentic AI** | 通过拆解任务让 AI 自主规划/执行，**最小化对模型能力要求** | day-job harness 的 north star，不是"调用 LLM"，是"设计 agent 框架" |
| **AI Native 团队** | 人 + 多个 AI agent 的小团队，**不是工具升级是组织演化** | day-job 团队 12-24 个月内的演化方向 |
| **98% 自动化编程** | AAA 工程里 98% coding task 由 AI 完成，2% corner case 兜底 | 工业 SOTA 数字；day-job harness 目标 baseline |
| **拆解任务 / 任务分解** | Agentic AI 核心方法：把大任务拆成 N 个小子任务，**每步对模型要求都不高** | day-job harness 工程的核心方法论 |
| **self-checkpointing** | Agent 定期保存 working state，错误时 rollback | "跑 8 小时不出错" 的工程基础 |
| **human-in-loop** | 关键决策点 pause 让人介入，AI 不全权决定 | harness 的兜底机制，对应 2% corner case |
| **auto-validation pipeline** | AI 写代码后自动跑 build + test + lint | "修一个 bug 引入三个新 bug" 的工程防线 |
| **降低对模型能力要求** | 不是堆大模型，是用精巧 agent 框架让小模型跑长任务 | Mac 平台 day-job 的核心策略（Mac 跑不动 70B+） |
| **策划案 / GDD (Game Design Document)** | 描述游戏设计的文档，通常是 markdown / docx | AI 读 GDD 生成 C++ skeleton 是 day-job MVP 任务 |

---

## 整体架构图 / 流程（伪代码）

```
# Agentic AI / 可微智能 Harness 框架 — Mac Game Harness v0.1 蓝图

# ===== Task 1: 修 UE 编译错误 =====
Task = "Fix UE compile error in ValidateProject.uproject"
Agent.run(Task):
    # Step 1: 触发 UE build，捕获错误
    build_output = MCP.ue_build(project="ValidateProject")
    # 解析 error
    errors = parse_errors(build_output)  # List[UError]
    if not errors:
        return "No errors, done"
    
    # Step 2: 对每个 error，拆解为子任务
    for error in errors:
        sub_task = SubTask(
            file=error.file,
            line=error.line,
            description=error.message,
            context=error.context_lines
        )
        # Step 3: AI 修复单 file 单 error
        fixed = fix_one_error(sub_task, harness=Agent)
        # Step 4: 写回文件
        MCP.ue_write_file(error.file, error.line, fixed)
    
    # Step 5: 重新 build 验证
    new_build = MCP.ue_build(project="ValidateProject")
    if has_errors(new_build):
        # Step 6: 自我修复 — checkpoint + 回滚
        if new_build.errors == old_build.errors:
            Agent.escalate_to_human(error)  # 2% 兜底
        else:
            Agent.recurse(Task)  # 减少到剩余 errors
    return "Done"

# ===== Task 2: 读 GDD 生成 C++ skeleton =====
Task = "Generate C++ skeleton for Enemy AI from GDD chapter 3"
Agent.run(Task):
    # Step 1: 读 GDD
    gdd_text = MCP.read_gdd(file="gdd/chapter-3-enemy-ai.md")
    # Step 2: 解析关键概念
    concepts = LLM.extract_concepts(gdd_text)  # ["state machine", "patrol", "attack", ...]
    # Step 3: 生成 UE class header
    header = LLM.generate_ue_class(
        class_name="AEnemyAIController",
        base_class="AAIController",
        methods=concepts,
        style="UE5.6+"
    )
    # Step 4: 生成 cpp skeleton
    cpp = LLM.generate_ue_cpp(header, methods=concepts)
    # Step 5: 写到 UE module
    MCP.ue_write_file(
        "Source/ValidateProject/EnemyAIController.h", 
        content=header
    )
    MCP.ue_write_file(
        "Source/ValidateProject/EnemyAIController.cpp", 
        content=cpp
    )
    # Step 6: auto-validation
    build = MCP.ue_build(project="ValidateProject")
    if build.success:
        return "Skeleton generated and compiled"
    else:
        return Agent.recurse("Fix compile errors in generated skeleton")

# ===== Harness 内部基础设施 =====
class AgenticHarness:
    def __init__(self, model="qwen2.5-coder-7b-instruct", max_steps=200):
        self.model = model
        self.working_memory = []  # 跨 N 步的 state
        self.checkpoints = []     # self-checkpointing
        self.human_pause_points = ["after_N_errors", "before_overwrite_file"]
    
    def checkpoint(self):
        self.checkpoints.append(self.working_memory.copy())
    
    def rollback(self, n=1):
        self.working_memory = self.checkpoints[-n].copy()
    
    def run_with_observability(self, task):
        for step in range(self.max_steps):
            # 1. 思考
            thought = LLM.think(self.working_memory, task)
            # 2. 决定动作
            action = LLM.decide_action(thought, available_tools)
            # 3. 执行
            result = action.execute()
            # 4. 自我审视
            if not self.validate(result):
                if self.is_recoverable(result):
                    self.rollback(1)
                    continue
                else:
                    return self.escalate_to_human(result)
            # 5. checkpoint 每 N 步
            if step % 10 == 0:
                self.checkpoint()
            # 6. human pause points
            if step in self.human_pause_points:
                if not self.wait_for_human_approval():
                    return "Paused by human"
            # 7. 更新 working memory
            self.working_memory.append({"thought": thought, "action": action, "result": result})
        return "Done"
```

---

## 相关论文/前置知识

- [[2026-Tencent-HaoYang-AIDrivenPrototype]] (GDC/Minimax/2026) — 光子工作室 Hao Yang 的 C.A.T framework 互补：**Hao Yang 是"AI 驱动制作 3D 原型"的工具栈视角**，本文是"AI 驱动大型工程"的 agent 框架视角；两者是 LLM harness 的"前端 + 后端"
- [[2026-Tencent-MagicStudio-RealTimeMotionGeneration]] (GDC/Minimax/2026) — 实时 AI 动作生成；和本文互补：**MagicStudio 是"AI 替代美术工序"，本文是"AI 替代编程工序"**——大厂用 AI 替代不同工序的同源探索
- [[2026-Tencent-VISVISE-FullPipeline]] (GDC/Minimax/2026) — Tencent AIGC 美术管线；同公司互补：**VISVISE 是 AI 接入美术管线**，本文是 **AI 接入编程管线**——同一 vendor 的"AI 接入各工程环节"双案例
- [[2025-NVIDIA-AdvancesInRTX-NeuralRendering]] (GDC/Minimax/2025) — 神经渲染；和本文无关但同属 "AI 接管 game dev" 大趋势的姊妹篇
- `Routine/05-技术雷达/P2-了解即可/WorldModels-Genie3-Hunyuan.md` — World model 跟踪；和本文无关
- `Career/Kimi/UE5_Training_MCP/` — day-job LLM 训练数据；本文给的"AI 修 UE 编译错误 + 读 GDD 生成 skeleton"是 day-job 训练数据的首批目标场景

---

## 输出 / 借鉴（forward — 启发到的工程实践）

- **[[05-技术雷达]] P0 加一行** —— "Agentic AI / 可微智能 for Game Dev"，明确 "harness 元命题是让 AI 长时间在大型工程中稳定工作" + "降低对模型能力要求"。**状态**：立刻补到 P0
- **Mac Game Harness MVP 任务剖面** —— 第一版只做 "修 UE 编译错误 + 读 GDD 生成 C++ skeleton"；用 7B-14B 本地模型 + 简单 MCP tools，验证 harness 框架可行性。**状态**：2 周内启动
- **Harness SLA 量化目标** —— 内部 benchmark "% auto-completion" 目标 70% (v0.1) → 90% (v1.0) → 95% (v2.0)，对标 Tencent 98% SOTA。**状态**：MVP 完成后立刻开始 bench
- **Self-checkpointing + rollback 机制** —— Harness 框架的核心基础设施；**比 chat 复杂一个数量级的 state 管理**。**状态**：MVP 同期实现
- **AI Native 团队 探索** —— day-job 团队 12-24 个月内是否演化成"人 + 多 AI agent"结构；和 [[05-技术雷达]] 联动跟踪。**状态**：季度评估
- **"降低对模型能力要求" 策略** —— 7B-14B 本地模型 + 良好 harness > 70B+ 云端模型 + 简单 prompt；这是 Mac 平台 day-job 的核心策略。**状态**：v0.1 MVP 验证
- **LLM RAG 训练数据补充** —— 把"可微智能 / Agentic AI for game dev"作为 day-job LLM 训练数据的新主线；和 [[Career/Kimi/UE5_Training_MCP]] 联动。**状态**：季度更新训练语料

---

## 个人评价

**优点：**

- **真实工业 case，可量化** —— 98% 这个数字非常关键，让"AI 接管大型工程"从 PPT 愿景变成可衡量目标。**对 day-job 是"目标 baseline" 而非 "理想值"**
- **反共识判断"降低对模型能力要求"** —— 主流叙事都是"模型越强越能"，Tencent 反过来主张"agent 框架 > 模型能力" —— 这和 day-job Mac 限制完全对位，是**关键的工程策略锚点**
- **明确"修 Bug + 策划案生成程序"作为首批任务** —— 不是"AI 做游戏"这种 PPT 级愿景，是**最常见的工程任务**；**给 day-job MVP 任务剖面**指明了方向
- **"AI Native 团队"是组织级洞察** —— 提示 harness 不是工具升级，是组织演化；**给 day-job 团队规划提供长期方向感**
- **腾讯天美的工业地位** —— 天美是王者荣耀 / 三角洲行动 等 AAA 项目的开发团队，**98% 自动化不是 demo，是生产环境数据**——可信度高

**局限性：**

- **没给"98% 自动化"的任务分类细节** —— 哪些 coding 任务被自动化了？network code? UI code? shader? AI? —— 没说；**day-job 无法直接抄作业**
- **没展开"2% corner case"的处理细节** —— 哪些 case 一定会失败？怎么 detect？怎么 escalate to human？—— 没说；**day-job 必须自己建 failure mode 分类**
- **"AI Native 团队"没具体说组织结构** —— 几个人 + 几个 agent？agent 怎么分工？怎么决策？—— 没说；**只有方向感，没有可复制的 pattern**
- **没谈模型具体选择** —— 用什么模型？Qwen? Claude? GPT? — 没说；**对 day-job Mac 平台的模型选择参考有限**
- **没给 harness 框架的开源/复用可能性** —— 是 Tencent 内部框架还是商业产品？**外部能不能用？** —— 没说；**对 day-job 直接借鉴是 black box**
- **没谈"AI 修 Bug 引入新 Bug" 的 risk control** —— 98% 自动化不等于 "AI 不会引入新 bug"；**风险 mitigation 没说**
- **没谈 UE 引擎具体 version** —— Tencent 天美用的是 UE 5.x 哪个版本？**对 day-job 同 version 适配的细节没说**

**启发：**

1. **"可微智能 / Agentic AI"作为术语直接借用** —— 在 day-job 的内部文档 / vault 笔记里，用 "可微智能 / Agentic AI" 替代 "AI 编程" / "AI 写代码" 这种模糊表述，**更准确也更工程化**
2. **"98% 自动化"作为 baseline KPI** —— day-job Mac Game Harness 的 SLA 目标直接对标 98% —— 不是"AI 100% 取代人"，是"AI 处理 98% 常规，人处理 2% corner case"
3. **"降低对模型能力要求" 是关键策略** —— 主流叙事 "模型越强越能" 忽略了一个事实：**agent 框架的边际收益在 14B 模型上比 70B 模型大得多**。Mac 平台 day-job 押注 7B-14B + 良好 harness 是**反共识但更可行**的策略
4. **"修 Bug + 读 GDD 生成 skeleton" 是 MVP 任务剖面** —— 不要做"AI 做游戏"，做"AI 处理常规 coding 任务"。这是 day-job MVP 的最务实入口
5. **"AI Native 团队" 是 12-24 个月组织演化方向** —— day-job 团队结构未来会变；不是"工具升级是组织演化"。这个长期方向感值得季度评估
6. **"AI 长时间不出错"是 harness 的硬指标** —— 比 "AI 单次回答对不对" 复杂一个数量级；需要 self-checkpointing + rollback + human-in-loop 整套基础设施
7. **98% 的可信度来源是天美的工业地位** —— 引用 98% 这个数字时，**强调来源（天美 AAA 项目真实数据）** 比"AI 公司说 AI 多强" 有说服力

---

## 面试谈资准备

**30 秒版（"知道这篇 + 能说清贡献"）：**

> GDC 2026 Tencent 天美工作室（王者荣耀 / 三角洲行动 开发团队）的余煜 / 牟骞讲 "可微智能 / Agentic AI for Game Development"。**核心贡献是给出 AAA 级工业 case —— 在大型游戏工程里实现 98% AI 自动化编程（修 Bug + 根据策划案生成程序）**。**关键判断是"降低对 AI 模型能力的要求"** —— 不靠堆大模型，靠 agent 框架让弱模型也能跑长任务。**对 day-job 启发**：Mac Game Harness 的 north star 就是这个形态 —— 用 7B-14B 本地模型 + 良好 harness，让 AI 跑 8 小时不出错处理 UE 工程任务，2% corner case 兜底。

**2 分钟版（"追问实现细节"）：**

> 第一，**"可微智能 / Agentic AI" 是新术语**。讲者把"AI 接管大型工程"的能力命名为 **Agentic AI / 可微智能** —— 核心是 **"通过拆解任务，AI 自主规划/执行 + 最小化对模型能力要求"**。这和单点 LLM 调用（prompt-in-text-out）的本质区别是 **AI 能否自己跑 N 小时不出错**。**day-job 直接对位**：未来 LLM harness 的 KPI 不是 "回答对不对"，是 **"能不能在大型工程里独立工作 N 小时 + 自我恢复"**。

> 第二，**98% 自动化编程 —— 真实工业数字**。讲者明确说 **"现在能做到 98% 的 AI 自动化编程"**。**这个数字的工程含义**：AAA 项目里绝大部分 coding 任务已经能由 AI 在极少人工干预下完成，**剩余 2% 是 corner case 兜底**。**不是"AI 写整个游戏"，是"AI 处理 98% 常规 + 人处理 2% 兜底"**——这是 LLM harness 真实落地的形态。**day-job 启发**：Mac Game Harness 的 SLA 目标直接对标 98% 作为 SOTA baseline。

> 第三，**"降低对模型能力要求" 是反共识关键判断**。讲者强调 "Agentic AI 尽可能降低对 AI 模型能力的要求" —— 主流叙事都是"模型越强越能"，Tencent 反过来主张"agent 框架 > 模型能力"。**和 day-job Mac 限制完全对位**：Mac 不可能本地跑 70B+ 模型，**用 7B-14B + 良好 harness** 才是 Mac 路径。**LLM RAG 训练**：凡是涉及"Mac 平台 LLM 落地"的 Q&A，答案应该指向"agent 框架 > 模型能力"。

> 第四，**"修 Bug + 读 GDD 生成程序"是首批任务剖面**。讲者说 **现在 AI 能修 Bug，能根据策划案自动生成程序**。**day-job MVP 不要做"AI 做游戏"，做这两件事**：(a) AI 修 UE 编译错误（MCP tool 触发 build → 捕获 error → AI 修）；(b) AI 读 GDD 章节生成 C++ skeleton（MCP tool 读 GDD md → AI 输出 C++ class）。这是最务实的入口。

> 第五，**"AI Native 团队"是组织级洞察**。讲者说团队 "往 AI 原生组织方向演化" —— **不是工具升级是组织演化**。**day-job 12-24 个月内是不是要演化成"人 + 多 AI agent"的小团队**？这是组织级而非工具级问题。**LLM RAG 训练**：组织设计相关的 Q&A 应该挂"AI Native 团队"作为长期形态参考。

> 第六，**"AI 长时间不出错"是工程硬指标**。**day-job harness 必须有 self-checkpointing + rollback + human-in-loop 整套基础设施**。**比 chat 复杂一个数量级** —— 不只是对话历史，是持久化 working memory + checkpoint + error-classification。**LLM RAG 训练**：harness 设计相关 Q&A 必须包含 self-checkpointing / rollback 机制。

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] 已补到 [[05-技术雷达]] P0 列表 "Agentic AI / 可微智能" → 本周加
- [ ] Mac Game Harness MVP 任务剖面定义（"修 UE 编译错误 + 读 GDD 生成 skeleton"）→ 2 周内启动
- [ ] Harness SLA 量化目标 70%/90%/95% → MVP 后定义
- [ ] Self-checkpointing + rollback 机制实现 → MVP 同期
- [ ] AI Native 团队探索 → 季度评估
- [ ] LLM RAG 训练数据补充 → 季度更新

---

*Create date: 2026-07-14*
*Last modified: 2026-07-14*
