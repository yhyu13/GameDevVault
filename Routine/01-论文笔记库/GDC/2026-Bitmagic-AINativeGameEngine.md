---
tags: [paper/signed, paper/GDC-talk, paper/GDC-2026, paper/AI-pipeline, paper/已应用到工作]
aliases: [Bitmagic-AINativeEngine-GDC2026, Jani-Penttinen-AI-Native-Game-Engine, Bitmagic-Prompt-Play-Iterate]
---

# Bitmagic — AI-Native Game Engine: Prompt-Play-Iterate Loop (GDC 2026)

| 字段 | 内容 |
|------|------|
| **Talk 标题** | Building an AI-Native Game Engine / Why Unity Can't Keep Up |
| **讲者** | Jani Penttinen (Bitmagic 联合创始人兼 CEO) |
| **场次** | GDC 2026 — AI in Game Development Summit / San Francisco SOMArts 圆桌（GenAI Assembling × Tripo AI 联合举办） |
| **日期** | 2026-03-12 (Moscone Center, San Francisco) |
| **Track** | AI in Game Development / 引擎架构 / 创业视角 |
| **同源 short note** | (待 cron curator 落 `GDC/Minimax/2026/`) — 本文是其深度展开 |
| **阅读日期** | 2026-07-14 |
| **精读时长** | ~40 min |

---

## 一句话总结

> Bitmagic 的 Jani Penttinen 给出**"AI-native game engine"的完整创业论证**：传统引擎（Unity / Unreal）受历史代码架构约束**"很难跟上 AI 研究的迭代节奏"**；**从头原生构建一个为 AI 集成的引擎**才能**实时整合最新 AI 技术**（游戏内实时推理、数据效率优化）。**核心方法论是 "prompt-玩-迭代" 闭环**：在 build 游戏的同时**就能玩到它**，**速度不是目的，得到最好结果才是**。**给 day-job 的启发**："Mac Game Harness 是把 UE 改造得 AI-native" 还是 "从零建一个 AI-native 引擎"——是 day-job Mac 路线的两条根本路线选择，**Bitmagic 给出了后者的完整论证 + 失败教训**。

---

## 核心创新点

1. **"AI-native engine" 作为明确技术立场**。Jani 核心论点：**"Unity 这样的老牌引擎很难跟上 AI 研究的迭代节奏。从头开始原生构建，就意味着我们能立刻整合最新技术，比如游戏内的实时推理或数据效率优化。"**——**这不是"AI 加到现有引擎"，是"为 AI 重写一个引擎"**。**对 day-job 关键**：day-job Mac Game Harness 押注"改造 UE"还是"建新引擎"，Bitmagic 给出了后者的完整论据。

2. **"prompt-玩-迭代" 闭环作为核心方法论**。Jani 给出 Bitmagic 的核心理念 **"prompt-玩-迭代"**：**"你在构建游戏的同时，就能马上看到并玩到它"**。**这不是 "先 build 后 play"，是 build + play 同步**——LLM 输出 C++ / GDScript 的同时，**游戏实例已经在跑**。**对 day-job 启发**：Mac Game Harness 应该有 **"MCP tool 改一行 UE 代码 → 自动 trigger Play in Editor → LLM 看到实际效果再决定下一步"** 的能力，**不是"改代码 → 改完 build → 人去看"**。

3. **"速度不是最终目的，得到最好结果才是"**。Jani 强调 **"你可能会花整整一天时间反复调整 prompt 和测试，AI 让创作变得更易上手，但要做出真正好的东西，依然需要付出大量心血"**——**反快消主义**。**对 day-job 启发**：Mac Game Harness 的 UX 不要追求"快"，**追求"AI 跑一天能拿到 SOTA 结果"**——这个 SLA 不同于"AI 1 分钟给个 demo"。

4. **明确的"AI 接管什么 / 不接管什么"边界**。Jani 反复强调 Bitmagic 目标用户是 **"靠写 prompt 来做游戏的 AI-native 创作者"**，**不是 Unity / Unreal 开发者**。**这是市场定位的清晰性**——Bitmagic **不和 UE 抢市场**，抢的是"AI-native 创作工具"这条新赛道。**对 day-job 启发**：day-job Mac Game Harness 的目标用户**是"UE 工程师 + LLM"，不是"AI-native 创作者"**——**不应该走 Bitmagic 路线，应该走"AI 加固 UE 工程"路线**。这是 day-job 必须明确的策略。

5. **"实时推理 + 数据效率"作为引擎 native 能力**。Jani 提到 Bitmagic 能 **"立刻整合最新技术，比如游戏内的实时推理或数据效率优化"**。**关键技术点**：游戏内实时推理（on-device LLM / diffusion / neural rendering inference）和数据效率优化（针对 AI 工作流的数据 pipeline 优化）。**对 day-job 启发**：Mac Game Harness 应当**支持在 Mac 平台上跑 LLM 推理**（不是云端 API），且**优化 LLM 训练数据 pipeline**——这是"AI-native 引擎"的两条核心技术 axis。

6. **"去年失败教训" 的诚实复盘**。Jani 透露 **2025 年 Bitmagic 做了一个产品，让用户输入 prompt 就能生成整个游戏 —— 几乎没人用**。**关键洞察**：**"真正的创作者想要的是反复迭代和打磨，而不是丢一个 prompt 了事。而偏消费型的用户根本不想写 prompt"**——**创作者要 prompt-power + iteration，消费用户要 zero-prompt 的一键开始**。**对 day-job 启发**：Mac Game Harness 的 UX 必须在**"prompt-power 给创作者" + "zero-prompt 一键 demo 给消费用户"** 之间做明确分流。**"输入 prompt 生成游戏"是 dead end**。

7. **"99% 的人都不会编程，不管你把工具做得多简单"**。Jani 的关键断言：**"世界正在分化成创作者和消费者两类人"** + **"99% 的人都不会编程，不管你把工具做得多简单"**。**关键洞察**：**降低编程门槛 ≠ 让人人做创作者**，**绝大多数人想要的是"消费"，不是"创作"**。**对 day-job 启发**：Mac Game Harness 的目标用户是**"会用 prompt 的创作者"，不是"消费用户"**——**LLM 训练数据应该聚焦"如何用 prompt 做出好游戏"，而不是"让零基础用户做游戏"**。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按 day-job "LLM-driven UE on Mac" + "Mac Game Harness" 视角）：**

1. **"AI-native engine vs 加固 UE" 是 day-job 的根本路线选择**。Jani 的 Bitmagic 给出**"从头建 AI-native 引擎"**的论据。**day-job 的选择是"加固 UE"还是"建新引擎"**：
   - **路线 A (Bitmagic 路径)**：从零建一个为 AI 集成的轻量引擎，Mac 平台 native；放弃 UE 生态；目标用户是 AI-native 创作者
   - **路线 B (day-job 现行路径)**：把 UE 改造得 AI-friendly；保留 UE 生态；目标用户是 UE 工程师 + LLM
   
   **两条路线 trade-off**：
   - 路线 A：开发效率高（不用背负 UE 历史包袱），但失去 UE 生态（Nanite / Lumen / VSM / 大型 marketplace）
   - 路线 B：保留 UE 生态（day-job 终极产品跑在 UE 上），但每次 UE 升级都要做适配
   
   **LLM RAG 训练**：day-job 路线选择相关的 Q&A 答案应该明确**"day-job 押注路线 B（UE + AI harness）"** + **"Bitmagic 路径是参考而非抄作业"**。

2. **"prompt-玩-迭代" 闭环 是 harness UX 的核心创新**。Jani 提的"build 同时就能 play"——**对 day-job 启发**：
   - **现状**：MCP tool 改 UE C++ 代码 → trigger rebuild → 人去 Play in Editor 看效果
   - **目标**：MCP tool 改 UE C++ 代码 → **自动 trigger Play in Editor** → LLM 通过 screenshot/状态反馈看到实际效果 → 自动决定下一步
   
   **这是 Mac Game Harness 区别于"普通 LLM + UE"的根本**——**build + play 同步**。**LLM RAG 训练**：harness UX 相关的 Q&A 答案应该包含"build-play feedback loop"。

3. **"速度不是目的"是 harness SLA 设计的反共识**。Jani 强调"花一天调 prompt"是常态——**对 day-job 启发**：
   - **不要把 harness SLA 设为"1 分钟给答案"**——这是 chat 心态
   - **harness SLA 应该是"AI 跑 N 小时拿到 SOTA 结果"**——这是 agent 心态
   - **用户（工程师）的耐心预算远高于 chat 用户**——可以等"AI 跑一下午"
   
   **LLM RAG 训练**：harness 设计相关的 Q&A 应该包含"AI 长时间运行"作为 expected use case。

4. **"AI-native 创作者 vs 消费用户" 的明确分流**。Jani 提示 **"输入 prompt 生成整个游戏" 是 dead end**——**对 day-job 启发**：
   - **Mac Game Harness 目标用户**：会用 prompt 的工程师（创作者）
   - **不目标用户**：消费玩家（他们要的是玩游戏，不是做游戏）
   - **LLM 训练数据**：聚焦"如何用 prompt 做出好游戏"，**不**做"让零基础用户做游戏"
   - **UX 必须明确**："这是给会用 prompt 的人用的工具"——不要假装消费用户友好

5. **"游戏内实时推理 + 数据效率" 是 AI-native 引擎两大 axis**。Jani 提到的两个 native 能力：
   - **(a) 游戏内实时推理**：Mac 平台上 on-device LLM / diffusion / neural rendering inference
   - **(b) 数据效率优化**：针对 AI 工作流的数据 pipeline 优化
   
   **对 day-job 启发**：Mac Game Harness 必须支持 **(a) Mac 平台本地 LLM 推理**（如 MLX 框架）+ **(b) UE source code RAG 索引优化**（不是把整个 UE 灌进 context window，是按 task 检索相关 module）。**LLM RAG 训练**：技术栈相关的 Q&A 应该挂这两条 axis。

6. **"诚实复盘失败" 是判断 talk 价值的关键信号**。Jani 直接说 "去年我们做了一个让用户输入 prompt 生成整个游戏，几乎没人用"——**愿意公开失败 = talk 真实可信**。**对 day-job 启发**：LLM 训练数据要**包含明确的"什么不做"**——和"做什么"同样重要。**Mac Game Harness 应当**有"明确不做"的清单（不做一键游戏生成 / 不做消费用户 UX / 不做云端推理）。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|-------------|
| **"build-玩-迭代" 闭环在 UE 上的实现** | UE 不像 web 框架支持 hot-reload 全栈；Play in Editor 是专门的 editor mode；MCP tool 自动 trigger PIE 需要 UE Automation / Python API 集成 | 是——Mac Game Harness 的核心 UX 创新 |
| **UE C++ 改动的 LLM 反馈** | LLM 改 C++ 后怎么"看到"实际效果？截图？日志？状态？需要 MCP 工具提供 UE runtime introspection | 是——harness 反馈机制的核心 |
| **Mac 平台本地 LLM 推理** | MLX 框架 / llama.cpp / ollama — 哪个最稳？7B-14B 模型在 M3/M4 上的 token/s 够用吗？ | 是——Mac 平台 day-job 的关键技术风险 |
| **UE source code RAG 索引** | UE 5.6+ 的 module/class 层级超过 200K token；按 task 检索相关 module 是 harness 的关键 | 是——day-job LLM 训练数据核心 |
| **"AI-native 引擎" vs "UE 加固" 的工程量对比** | 从零建引擎：3-5 年团队；UE 加固：3-6 个月团队；trade-off 巨大 | 是——路线决策的关键输入 |
| **"创作者 vs 消费用户" UX 分流** | 一个工具怎么同时服务两类用户？要么明确目标只做一类，要么做两套 UX | 是——day-job 目标用户明确的依据 |

---

## 是否值得复现？

- [ ] 是 — 已列入待办
- [x] **否** — 不复现，吸收思路即可
- [ ] 部分 — 只复现核心算法

**不复现的原因：**

- **Bitmagic 的 AI-native 引擎是商业产品，不开源**——无法直接抄
- **day-job 路线是"UE 加固"不是"建新引擎"**——Bitmagic 的引擎架构不能直接搬
- **可借鉴的是方法论不是实现**：prompt-玩-迭代闭环、明确目标用户分流、诚实复盘失败——这些是 day-job harness 设计的指导原则
- **day-job 应该走 UE 加固路线**——保留 UE 生态（Nanite / Lumen / VSM / Marketplace）+ 把 AI harness 加上去

**借鉴的具体步骤：**

1. **明确 day-job 路线** —— 在 [[Routine/AI-Tasks/Mac/00-Master-Index]] 顶部加 "路线声明"：**day-job 押注"UE 加固"路线**，**不**走"建新 AI-native 引擎"路线。**状态**：本周
2. **prompt-玩-迭代 闭环作为 Mac Game Harness 核心 UX** —— MCP tool 改 C++ → 自动 trigger PIE → LLM 看到反馈 → 自动决定下一步。**状态**：MVP v0.2 实现
3. **明确目标用户分流** —— Mac Game Harness 文档顶部声明："**目标用户：会用 prompt 的 UE 工程师**；不目标用户：消费玩家"。**状态**：v0.1 文档同期
4. **"明确不做" 清单** —— 维护一份 "Mac Game Harness 不做什么" 列表：不做一键游戏生成、不做消费用户 UX、不做云端推理。**状态**：v0.1 同期
5. **诚实复盘文化** —— Mac Game Harness 内部建立"季度失败案例分享"机制——Jani 的 talk 价值一半在技术一半在诚实。**状态**：季度启动

---

## 关键术语表

| 术语 | 解释 | 我理解的锚点 |
|------|------|--------------|
| **AI-native engine** | 从零建一个为 AI 集成的引擎，**不**在 UE/Unity 上加 AI 工具 | Bitmagic 的核心立场；day-job 不走这条路线但吸收思路 |
| **prompt-玩-迭代** | 在 build 游戏的同时就能玩到它；**build + play 同步** | day-job Mac Game Harness 的核心 UX 创新 |
| **AI-native 创作者** | 靠写 prompt 做游戏的人；**会 prompt + 不愿手写代码** | Bitmagic 目标用户；day-job 目标用户也是这类（UE 工程师 + LLM） |
| **消费用户** | 只想玩游戏不想做游戏的人；99% 的人属于这类 | 不是 day-job 目标用户 |
| **游戏内实时推理** | 在游戏运行时本地跑 LLM / diffusion / neural rendering | Mac 平台 day-job 的核心技术 axis |
| **数据效率优化** | 针对 AI 工作流的数据 pipeline 优化 | UE source code RAG 是 day-job 的核心 |
| **UE 加固 vs 建新引擎** | 把 AI harness 加到 UE 上 vs 从零建 AI-native 引擎 | day-job 押注前者，Bitmagic 走后者 |
| **"99% 的人不会编程"** | 降低编程门槛 ≠ 让人人做创作者 | day-job 路线决策的关键依据 |

---

## 整体架构图 / 流程（伪代码）

```
# Bitmagic AI-Native Engine vs day-job UE+AI Harness 两条路线对照

# ===== 路线 A: Bitmagic (从零建 AI-native 引擎) =====
# 不开源，仅描述架构概念
class BitmagicEngine:
    """Bitmagic-style 引擎：build + play 同步，AI 在 loop 内"""
    def __init__(self):
        self.runtime = AINativeRuntime()  # 原生支持 LLM 推理
        self.data_pipeline = AIOptimizedPipeline()  # 优化过的 data flow
        self.build_play_loop = PromptPlayIterateLoop()  # 核心 loop
    
    def prompt_play_iterate(self, user_prompt):
        # 1. LLM 解析 prompt → 生成 game logic
        game_code = self.llm.parse_prompt(user_prompt)
        # 2. 立即 hot-reload 到 runtime
        self.runtime.hot_reload(game_code)
        # 3. 同时启动 game instance
        instance = self.runtime.spawn_instance()
        # 4. 用户立刻 play
        user.play(instance)
        # 5. 用户调 prompt，loop 继续
        # ... (迭代 N 次，直到用户满意)

# ===== 路线 B: day-job Mac Game Harness (UE 加固) =====
# 押注路线：保留 UE 生态 + 加 AI harness
class MacGameHarness:
    """UE + MCP tools + LLM agent"""
    def __init__(self):
        self.ue_project = UEProject("MyGame.uproject")
        self.mcp_tools = {
            "ue_read_file": MCP.ue_read_file,
            "ue_write_file": MCP.ue_write_file,
            "ue_build": MCP.ue_build,
            "ue_play_in_editor": MCP.ue_play_in_editor,  # ★ 关键
            "ue_screenshot": MCP.ue_screenshot,  # ★ 关键
            "ue_log": MCP.ue_log,  # ★ 关键
        }
        self.llm = LocalLLM("qwen2.5-coder-14b-instruct-mlx")
    
    def agent_loop(self, user_request):
        # 1. LLM 理解 user request
        plan = self.llm.plan(user_request)
        for step in plan:
            # 2. LLM 决定动作
            action = self.llm.decide_action(step, available_tools=self.mcp_tools)
            # 3. 执行（改 C++ 文件）
            result = action.execute()
            # 4. 自动 build（关键：build-play 同步）
            build = self.mcp_tools["ue_build"](self.ue_project)
            if not build.success:
                # AI 修编译错误
                self.agent_loop(f"Fix compile errors: {build.errors}")
                continue
            # 5. 自动 trigger Play in Editor（★ prompt-玩-迭代 核心）
            self.mcp_tools["ue_play_in_editor"](self.ue_project, mode="auto")
            # 6. LLM 看到实际效果（截图 + 日志）
            screenshot = self.mcp_tools["ue_screenshot"]()
            log = self.mcp_tools["ue_log"](last_n=100)
            # 7. LLM 自我评估
            feedback = self.llm.evaluate(screenshot, log, expected=step.expected)
            if feedback.is_good:
                continue
            else:
                # 8. 调 prompt/改代码，重来
                self.agent_loop(f"Refine based on feedback: {feedback.notes}")
        return "Done"
    
    # ★ 核心区别 vs Bitmagic:
    # - Bitmagic: build + play 是同一回事（AI-native runtime）
    # - day-job: build + play 是两步 (UE build → PIE)
    #   但通过 MCP tools 串联，UX 上达到"接近同步"
```

---

## 相关论文/前置知识

- [[2026-Tencent-Timi-AgenticAI-GameDev-98pct]] (GDC/Minimax/2026) — Tencent 天美 Agentic AI；**和本文是 day-job harness 的"两条路线"对照**：
  - **Tencent 路线**：在 UE 现有引擎上**加固 Agentic AI**（98% 自动化编程）
  - **Bitmagic 路线**：**从零建 AI-native 引擎**
  - **day-job 选择**：和 Tencent 同路线（UE 加固），参考 Bitmagic 的 prompt-玩-迭代 UX
- [[2026-Tencent-HaoYang-AIDrivenPrototype]] (GDC/Minimax/2026) — Hao Yang 的 C.A.T framework；和本文有 UX 交叉（C.A.T 的迭代循环 ≈ prompt-玩-迭代）
- [[2026-GoogleDeepMind-Genie3-PlayableWorlds]] (GDC/Minimax/2026) — Genie 3 world model；**和本文是"AI-native engine"两种实现路径**：
  - **Bitmagic**：从零建能跑 prompt-玩-迭代 的引擎
  - **DeepMind Genie**：建一个能从 prompt 生成可玩世界的模型（不需要传统引擎）
  - **day-job 选择**：UE 加固 + Genie 是 inspiration
- `Routine/05-技术雷达/P2-了解即可/WorldModels-Genie3-Hunyuan.md` — World model 跟踪；和本文对照（AI-native engine vs world model）

---

## 输出 / 借鉴（forward — 启发到的工程实践）

- **路线声明** —— 在 [[Routine/AI-Tasks/Mac/00-Master-Index]] 顶部加 "day-job 押注 UE 加固路线，不走 AI-native engine 路线"。**状态**：本周
- **prompt-玩-迭代 闭环 列入 Mac Game Harness 核心 UX** —— MCP tool 改 C++ → 自动 build → 自动 PIE → LLM 看到反馈。**状态**：v0.2 MVP 实现
- **"明确不做" 清单** —— Mac Game Harness v0.1 文档顶部声明不做什么（不做一键游戏生成 / 不做消费用户 UX / 不做云端推理）。**状态**：v0.1 同期
- **目标用户声明** —— Mac Game Harness 文档顶部声明目标用户是 "UE 工程师 + LLM"，不目标用户是"消费玩家"。**状态**：v0.1 同期
- **诚实复盘文化** —— day-job harness 团队建立"季度失败案例分享"机制。**状态**：季度启动
- **[[05-技术雷达]] P0 加一行** —— "AI-native engine 创业潮（Bitmagic / Tripo / Glass Bead）作为 LLM 驱动引擎路线的市场信号"。**状态**：本周
- **LLM RAG 训练数据补充** —— "AI-native engine vs UE 加固"作为路线决策的 RAG 训练样本。**状态**：季度更新

---

## 个人评价

**优点：**

- **路线选择的清晰论据** —— "Unity 难跟上 AI 迭代节奏" 这句话直击要害；**给 day-job 路线决策提供了"反面论据"**——day-job 押注 UE 加固必须能反驳这个论点
- **prompt-玩-迭代 UX 创新** —— "build 同时就能 play" 是 AI-native 引擎的**根本 UX 优势**；day-job Mac Game Harness 必须在 UE 上逼近这个体验
- **诚实失败复盘** —— 直接说"去年我们做了 prompt-to-game，没人用"——**talk 价值一半在技术一半在诚实**
- **"99% 的人不会编程" 关键断言** —— 给 day-job 路线决策明确"不目标用户"——**避免 day-job 把工具做成"假装消费用户友好"**
- **创作者 vs 消费用户 分流** —— 是产品定位的根本洞察
- **创业视角的稀缺** —— 主流 talk 都是大厂（Tencent / NVIDIA / Microsoft），Bitmagic 给出了**AI-native engine 创业视角**

**局限性：**

- **Bitmagic 引擎本身不开源** —— 具体架构 / runtime 性能 / 数据 pipeline 实现全 black box；**day-job 无法直接抄代码**
- **"游戏内实时推理" 的硬件假设没说** —— 7B-14B 模型在什么硬件跑？延迟预算？—— 没说；**对 day-job Mac 平台参考有限**
- **"数据效率优化" 是 vague claim** —— 没具体说优化了什么、数据 pipeline 长什么样
- **没给"prompt-玩-迭代"的具体延迟预算** —— 1 秒？10 秒？1 分钟？—— 没说；**day-job UE 路径的 PIE trigger 时间需要自己测**
- **Bitmagic 商业数据没说** —— 用户数？融资？项目数？—— 没说；**对"AI-native engine 市场是否真的成立"无法独立判断**
- **没给"AI-native 创作者"的市场规模** —— "靠 prompt 做游戏"的人群到底多大？—— 没说；**可能是 niche market**
- **"去年失败"具体细节没说** —— 是 UX 问题？技术问题？市场问题？—— 没说；**day-job 没法直接 avoid**

**启发：**

1. **"AI-native engine vs UE 加固"作为 day-job 路线决策的明确框架** —— Bitmagic 给了"AI-native engine 路线" 的完整论据，**day-job 必须能反驳"Unity 难跟上 AI 节奏"才能押注 UE 加固**——这条论据要在内部技术评审里拿出来对质
2. **"prompt-玩-迭代"是 harness UX 的核心创新** —— 不是"AI 一次性给答案"，是"AI 跑 build-play-feedback loop 持续逼近最优"——day-job MVP 必须有这条 loop
3. **"创作者 vs 消费用户"是产品定位的根本** —— 99% 是消费者不是创作者—— day-job Mac Game Harness 文档必须明确"目标创作者用户，不假装消费友好"
4. **"明确不做"是产品成熟度信号** —— 敢说"我们不做 X" 比 "我们什么都做" 更可信——v0.1 文档顶部就写
5. **"诚实复盘失败"是 talk / 文档 / 团队文化的关键** —— Jani 直接说"去年我们失败了"—— day-job harness 团队季度分享失败案例
6. **"build + play 同步"是 AI-native 的根本 UX 优势** —— day-job Mac Game Harness 必须在 UE 上逼近（auto build + auto PIE + LLM 看到反馈）——这是 harness 区别于"普通 LLM + UE" 的关键

---

## 面试谈资准备

**30 秒版（"知道这篇 + 能说清贡献"）：**

> GDC 2026 Bitmagic 的 Jani Penttinen 讲 "AI-Native Game Engine"。**核心贡献是给出"从头建 AI-native 引擎" vs "在 UE 加固" 两条路线的明确论据**——Bitmagic 押前者，**核心 UX 是 "prompt-玩-迭代" 闭环（build 同时就能 play）**。**还诚实复盘去年失败**：让用户输入 prompt 生成整个游戏几乎没人用——**创作者要 prompt-power + iteration，消费用户要 zero-prompt 一键开始**。**对 day-job 启发**：押注"UE 加固"路线，但**必须把 prompt-玩-迭代 闭环作为 harness 核心 UX**（MCP tool 改 C++ → 自动 build → 自动 PIE → LLM 看到反馈），且**明确目标用户是 UE 工程师而非消费玩家**。

**2 分钟版（"追问实现细节"）：**

> 第一，**"AI-native engine"作为明确技术立场**。Jani 核心论点：**"Unity 这样的老牌引擎很难跟上 AI 研究的迭代节奏。从头开始原生构建，就意味着我们能立刻整合最新技术"**——这不是"AI 加到现有引擎"，是"为 AI 重写一个引擎"。**对 day-job 关键**：day-job 押注"UE 加固"还是"建新引擎"？Bitmagic 给了后者的完整论据。**day-job 必须能反驳"Unity 难跟上 AI 节奏"**——论据是 **(a) UE 生态太值钱（Nanite / Lumen / VSM / Marketplace）；(b) day-job 终极产品跑在 UE 上；(c) 适配 UE 升级是 3-6 个月工程量，建新引擎是 3-5 年**。

> 第二，**"prompt-玩-迭代" 闭环是 UX 核心创新**。Jani 提的 "你在构建游戏的同时，就能马上看到并玩到它" —— **不是"先 build 后 play"，是 build + play 同步**。**day-job Mac Game Harness 必须在 UE 上逼近这个体验**：
>   - **MCP tool 改 C++** → **自动 trigger UE build** → **自动 trigger Play in Editor** → **LLM 通过 screenshot/日志看到实际效果** → **自动决定下一步**
>   **这是 day-job harness 区别于"普通 LLM + UE"的根本**——**build-play feedback loop**。

> 第三，**"速度不是最终目的"是 SLA 设计的反共识**。Jani 强调"花一天调 prompt 是常态"——**对 day-job 启发**：harness SLA 不是"1 分钟给答案"（chat 心态），是"AI 跑 N 小时拿到 SOTA 结果"（agent 心态）。**LLM RAG 训练**：harness SLA 相关 Q&A 答案应该包含"AI 长时间运行"作为 expected use case。

> 第四，**"AI 接管什么 / 不接管什么"边界 + 失败复盘**。Jani 直接说"去年让用户输入 prompt 生成整个游戏，几乎没人用"——**创作者要 prompt-power + iteration，消费用户要 zero-prompt 一键开始**。**关键洞察**：**降低编程门槛 ≠ 让人人做创作者**——99% 的人不会编程也不想学。**对 day-job**：Mac Game Harness 文档顶部必须明确"目标用户是会用 prompt 的 UE 工程师" + **"明确不做"清单**（不做一键游戏生成 / 不做消费用户 UX / 不做云端推理）。

> 第五，**"游戏内实时推理 + 数据效率"两大 axis**。Jani 提到 Bitmagic 能"立刻整合最新技术，比如游戏内的实时推理或数据效率优化"。**对 day-job 启发**：Mac Game Harness 必须支持 **(a) Mac 本地 LLM 推理**（MLX / llama.cpp / ollama）+ **(b) UE source code RAG 索引优化**。**LLM RAG 训练**：技术栈相关 Q&A 答案应该挂这两条 axis。

> 第六，**"诚实复盘失败"是 talk 价值的关键信号**。Jani 愿意公开"去年我们失败"——**给 day-job 的启发是 harness 团队季度分享失败案例**。**LLM RAG 训练**：训练数据应该包含"什么不做"——和"做什么"同样重要。

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] 已加 day-job 路线声明到 [[Routine/AI-Tasks/Mac/00-Master-Index]]（UE 加固 vs AI-native engine）→ 本周
- [ ] prompt-玩-迭代 闭环 列入 Mac Game Harness v0.2 核心 UX → MVP v0.2
- [ ] "明确不做"清单 v0.1 文档 → v0.1 同期
- [ ] 目标用户声明 → v0.1 同期
- [ ] 诚实复盘季度分享 → 季度启动
- [ ] [[05-技术雷达]] P0 加 "AI-native engine 创业潮" → 本周
- [ ] LLM RAG 训练数据补充"AI-native engine vs UE 加固" 路线决策样本 → 季度

---

*Create date: 2026-07-14*
*Last modified: 2026-07-14*
