---
tags: [paper/signed, paper/GDC-talk, paper/GDC-2026, paper/AI-pipeline, paper/已应用到工作]
aliases: [GlassBeadGames-MultiAgentStudio-GDC2026, KuangyeGuo-4People-8Agents, GlassBead-AI-Agent-Studio]
---

# Glass Bead Games — 4 People + 8 AI Agents: Multi-Agent Game Studio Workflow (GDC 2026)

| 字段 | 内容 |
|------|------|
| **Talk 标题** | Building a Game Studio with AI Agents / 4-Person + Multi-Agent Workflow |
| **讲者** | Kuangye Guo (Glass Bead Games 联合创始人兼 CEO) |
| **场次** | GDC 2026 — AI in Game Development Summit / San Francisco SOMArts 圆桌（GenAI Assembling × Tripo AI 联合举办） |
| **日期** | 2026-03-12 (Moscone Center, San Francisco) |
| **Track** | AI in Game Development / 创业 / Multi-Agent 团队工作流 |
| **同源 short note** | (待 cron curator 落 `GDC/Minimax/2026/`) — 本文是其深度展开 |
| **阅读日期** | 2026-07-14 |
| **精读时长** | ~40 min |

---

## 一句话总结

> Glass Bead Games 的 Kuangye Guo 给出**"4 人 + 8 AI agents"小团队**做游戏的真实工作流：团队 4 人**"每个人都像在带一支队伍，使用多个 agents 并行推进不同的事"**——从单 Claude 任务 → 8 agents 并行 8 个功能 → agents 自己排查 bug / 消化研究论文。**关键洞察是"知识被清晰地写进文档时，agents 的表现会好很多"——这反过来逼着团队追问"游戏的核心原则是什么？它到底想表达什么？"**。**对 day-job 启发**：day-job 团队组织（无论 LLM 训练团队还是 harness 团队）应该**显式建立"人 + 多 agent"的小团队结构 + 知识文档化优先**——**这是 day-job 12-24 个月内组织演化的真实参考**。

---

## 核心创新点

1. **"4 人 + 8 agents"作为明确团队结构**。Kuangye 明确说：**"我们刻意保持小团队。每个人在某种程度上都像在带一支队伍，使用多个 agents 并行推进不同的事情。"**——**这是 4 个人做原本需要 30-50 人团队的工作**。**关键数字**：**4 人 + 8 agents = 实际产出 = 8× 人力**（粗估，因为 agent 不等于人）。**对 day-job 启发**：day-job harness 团队是不是也能用 "人 + 多 agent" 结构？4 个工程师 + 8 agents **能覆盖整个 LLM training pipeline + harness development + R&D**。

2. **"9 个月里工作流几乎每隔一两个月就要重新发明一次" —— 工作流演化节奏**。Kuangye 描述团队在过去 9 个月的工作流演化：
   - **阶段 1**：单 Claude 任务
   - **阶段 2**：8 agents 同时推进 8 个不同功能
   - **阶段 3**：让 agents 自己排查 bug + 消化研究论文
   
   **关键洞察**：**"我们对任何一件事都会先问：这个 agent 能不能搞定？哪个环节需要我们介入？"** —— 这是一个**显式的"AI 接管决策树"**。**对 day-job 启发**：day-job harness 团队应该有 **"AI 接管决策表"**——每个任务类型都有 "agent 能搞定 / 需要人介入" 的明确分流。

3. **"知识清晰写进文档时，agents 表现好很多" —— 文档化是 agent 性能的关键**。Kuangye 关键断言：**"当知识被清晰地写进文档时，agents 的表现会好很多。这反过来逼着你去追问那些根本问题：游戏的核心原则是什么？它到底想表达什么？不然 agent 就会各自为政、方向混乱。"**——**这是 day-job 必须内化的核心原则**：**agents 性能 = 文档质量**。**对 day-job 启发**：day-job LLM 训练数据 / harness 文档 / UE 项目文档，**全部要按 "agents 能读懂" 的标准重写**——**这是 day-job LLM RAG 训练数据策略的元命题**。

4. **"prompt 清晰度检验"作为质量保证手段**。Kuangye 给出一个**实操检验标准**："**如果我把这个 prompt 交给一个人，然后再也没机会和他沟通，他能搞清楚我想要什么吗？如果答案是否，那就继续打磨。反复来回，最终会到达你真正想要的结果。**"——**这是 prompt 工程的 hard standard**。**对 day-job 启发**：day-job harness 内部对 prompt 的 quality bar：**"把 prompt 交给一个人 + 不准追问，他能做对吗？"**——不能的 prompt 必须重写。

5. **"每个人能力被放大很多" 是小团队的核心优势**。Kuangye 说：**(a) 信息噪音很低；(b) 每个人的能力都被放大了很多；(c) 能力提升的速度非常快**——**不是 4 人做 4 人的事，是 4 人 × 放大系数做 N×4 人的事**。**关键洞察**：**小团队的"信息密度" 远高于大团队**——4 个人之间的 context 共享 + agent 协作 = 比 30 人团队决策更快。**对 day-job 启发**：day-job harness 团队**保持小（≤5 人）+ 高信息密度**是组织设计的关键。

6. **"AI 主动推送 vs 玩家自我表达" 的 UX 平衡**。Kuangye 提示：早期版本游戏"基本上是在不断地向玩家强塞内容。技术上跑得很顺，但玩家告诉我们他们感到沮丧，因为没有办法表达自己"——**这是 day-job harness UX 的关键警示**：**AI harness 自动做事不等于好事**。**对 day-job 启发**：Mac Game Harness 必须有 **"human-in-loop pause points"**——AI 自动做 ≠ AI 一直做；**关键决策点必须 pause 让工程师确认**。

7. **"游戏设计核心逻辑没根本性改变" —— 反 hype 洞察**。Kuangye 关键断言：**"游戏设计的核心逻辑并没有根本性的改变，依然是满足玩家的幻想、理解他们的需求、大量测试。但你现在拥有了更强的能力。以前做 10 个模型或行为树，现在可以做 100 个。"**——**AI 不改变 game design 的元命题，AI 改变的是"可做的事的数量"**。**对 day-job 启发**：LLM 训练数据 / harness 设计的**元命题不变**（让 UE 工程更高效），**能力倍增**（以前 1 个工程师管 10 个 module，现在能管 50 个）——**不**要"AI 改变一切"叙事。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按 day-job "LLM-driven UE on Mac" + "Mac Game Harness" 视角）：**

1. **"4 人 + 8 agents" 是 day-job harness 团队组织演化的真实参考**。**Kuangye 团队的 4 人 + 8 agents = 8-10× 产出**。**对 day-job 启发**：
   - **day-job harness 团队 ≤ 5 人**（保持小）
   - **每个工程师 + 2-3 个 agents**（并行推进不同 task）
   - **总 agent 数 8-15 个**（agent 数量 < 团队人力的 3-5×）
   - **agents 接管**：文档撰写 / 测试运行 / PR review / dependency update / code refactor
   - **人接管**：架构设计 / 关键决策 / 跨团队协作 / 复杂调试

   **LLM RAG 训练**：组织设计相关的 Q&A 答案应该挂 "4 人 + 8 agents" 作为"AI Native 团队"参考案例。

2. **"agents 性能 = 文档质量" 是 day-job LLM 训练数据策略的元命题**。Kuangye 关键断言："**当知识被清晰地写进文档时，agents 的表现会好很多。这反过来逼着你去追问那些根本问题。**"——**对 day-job 启发**：
   - **day-job LLM 训练数据必须按"agents 能读懂" 的标准重写**——每条 RAG 索引都要有 clear context + clear expected output
   - **day-job harness 文档必须按"agent 可执行" 的标准重写**——每个 MCP tool 都要有 clear description + clear input/output schema
   - **day-job UE 项目文档必须按"agent 可读" 的标准重写**——每个 module / class / function 都要有明确 docstring
   - **元命题**：**day-job 文档质量 = day-job agent 性能 = day-job AI 化进度**

3. **"prompt 清晰度检验" 是 day-job prompt 工程的 hard standard**。Kuangye 给的检验："**如果我把这个 prompt 交给一个人，然后再也没机会和他沟通，他能搞清楚我想要什么吗？**"——**对 day-job 启发**：
   - **Mac Game Harness 内部 prompt 必须通过 "single-shot human test"**——把 prompt 给一个不参与项目的工程师，看他能不能不追问就做对
   - **测试不通过 → 重写 prompt，不允许"prompt 模糊但人能脑补"**
   - **这是 day-job LLM 训练数据 quality bar 的一部分**

4. **"AI 接管决策表" 是 day-job harness 的核心管理工具**。Kuangye 说：**"我们对任何一件事都会先问：这个 agent 能不能搞定？哪个环节需要我们介入？"**——**对 day-job 启发**：
   - **day-job harness 团队应该有显式的 "AI 接管决策表"**：
     - 文档撰写 → agent
     - 测试运行 → agent
     - PR review → agent
     - Dependency update → agent
     - Code refactor (低风险) → agent + 人 review
     - Code refactor (高风险) → 人 + agent 辅助
     - 架构设计 → 人
     - 跨团队协作 → 人
     - 复杂调试 → 人 + agent 并行
   - **季度更新这张决策表**

5. **"AI 主动推送 vs 玩家/工程师自我表达" 平衡 —— human-in-loop pause points**。Kuangye 提示 "AI 一直做事" 让用户感到挫败——**对 day-job 启发**：
   - **Mac Game Harness 必须有显式的 human-in-loop pause points**：
     - **(a) "before overwrite file"**——改写前确认
     - **(b) "after N errors"**——连续 N 个错误后 escalate
     - **(c) "before refactor >100 lines"**——大改动前确认
     - **(d) "before commit"**——commit 前 review
   - **不是"AI 自动做所有"，是"AI 自动做 + 关键决策 pause"**

6. **"游戏设计核心逻辑没根本改变" 是 LLM 训练数据的元命题澄清**。Kuangye 关键断言：**"游戏设计的核心逻辑并没有根本性的改变，依然是满足玩家的幻想、理解他们的需求、大量测试"**——**对 day-job 启发**：
   - **day-job LLM 训练数据的元命题不变**：让 UE 工程更高效 + 让 LLM 理解 UE 特性
   - **能力倍增**：以前 1 个工程师管 10 个 module，现在能管 50 个
   - **不要"AI 改变一切"叙事**——是"AI 放大 5-10× 现有能力"
   - **LLM 训练数据要保留 UE 工程的核心知识**（Lumen / Nanite / VSM / Slate / GAS / replication），**不**被"AI Native"叙事冲掉

7. **"以前做 10 个，现在可以做 100 个" 是 AI 时代工程师的能力倍增曲线**。Kuangye 关键断言："**以前做 10 个模型或行为树，现在可以做 100 个。不要再把自己框死在某个狭窄的专业分工里，你可以去做更多的事了。**"——**对 day-job 启发**：
   - **day-job 工程师的能力倍增**：(a) 1 个 harness engineer 现在能维护 5 个 MCP tool sets（以前只能 1 个）；(b) 1 个 LLM trainer 现在能管理 10 个 RAG index（以前只能 2 个）；(c) 1 个 UE engineer 现在能 cross 5 个 module（以前只能 1 个 deep expertise）
   - **LLM 训练数据要支持 "cross-module 知识"**——不只 deep Lumen，要 Lumen + Nanite + VSM + replication 跨 module 知识

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|-------------|
| **"人 + 多 agent" 团队的具体管理机制** | agent 怎么分配？人 review 节奏？冲突解决？谁负责 prompt 调优？—— Glass Bead 没说 | 是——day-job harness 团队组织设计需要 |
| **"agents 性能 = 文档质量" 的工程实现** | UE 项目文档要按"agent 可读"标准重写，工作量巨大 | 是——day-job 长期投入 |
| **"prompt 清晰度检验" 的可量化标准** | "single-shot human test" 是 qualitative 的；怎么 quantify？ | 部分——先做 qualitative，后续 quantify |
| **"AI 接管决策表" 的演进机制** | 决策表是动态的——新任务出现要更新；agent 能力提升后要"回收"任务给人 | 是——季度 review 机制 |
| **"human-in-loop pause points" 的 UI/UX** | 工程师怎么方便地 approve/reject AI 的动作？MCP tool 是不是需要 "preview before execute" 模式？ | 是——Mac Game Harness UX 设计核心 |
| **"以前 10 个现在 100 个" 的能力倍增是真的吗** | Kuangye 是 qualitative 描述；具体数字需要 day-job 自己 benchmark | 部分——先 qualitative 推断，后续定量 |
| **9 个月工作流重发明 5 次 的稳定性风险** | 工作流频繁重发明 = 团队不停在转型；这在 enterprise 环境下是不可接受的（enterprise 要 stability） | 是——day-job 在 startup-like 和 enterprise-like 之间选型 |

---

## 是否值得复现？

- [x] **是** — 已列入待办（部分）
- [ ] 否 — 仅了解思路即可
- [ ] 部分 — 只复现核心算法

**复现/借鉴的具体步骤：**

1. **day-job harness 团队结构按 "≤5 人 + 8-15 agents" 重组** —— 内部发起 "AI Native 团队" 试点，1 个 5 人小组按 "人 + agent" 结构工作 3 个月。**状态**：3 个月内启动
2. **建立"AI 接管决策表"** —— Mac Game Harness 文档顶部维护一张决策表："哪些任务 agent 接管 / 哪些人接管 / 哪些混合"。**状态**：v0.1 同期
3. **建立"prompt 清晰度检验" 机制** —— day-job harness 团队内部 prompt 必须通过 "single-shot human test"。**状态**：v0.1 同期
4. **建立"human-in-loop pause points" 清单** —— Mac Game Harness 关键决策点必须 pause：before overwrite / after N errors / before big refactor / before commit。**状态**：v0.1 同期
5. **按"agent 可读" 标准重写 LLM 训练数据** —— day-job LLM 训练数据要从"工程师能读懂"升级到"agent 能读懂"——每条 RAG 索引都要有 clear context + clear expected output。**状态**：季度投入
6. **建立"季度失败案例分享" 机制** —— 借鉴 Kuangye 诚实复盘文化，harness 团队季度分享失败案例。**状态**：季度启动
7. **元命题澄清** —— LLM 训练数据保留 UE 工程核心知识（Lumen / Nanite / VSM / GAS），不被"AI Native"叙事冲掉。**状态**：持续

---

## 关键术语表

| 术语 | 解释 | 我理解的锚点 |
|------|------|--------------|
| **4 人 + 8 agents** | 小团队 + 多 AI agent 并行；**8-10× 产出放大** | day-job harness 团队组织演化的真实参考 |
| **AI 接管决策表** | 显式的 "agent 接管 / 人接管 / 混合" 任务分类表 | day-job harness 团队核心管理工具 |
| **"agents 性能 = 文档质量"** | 文档清晰 → agent 表现好；模糊文档 → agent 各自为政 | day-job LLM 训练数据策略的元命题 |
| **prompt 清晰度检验** | "single-shot human test"：把 prompt 交给不参与项目的人 + 不准追问，能做对吗？ | day-job prompt 工程的 hard standard |
| **human-in-loop pause points** | AI 自动化 + 关键决策点 pause 让工程师确认 | Mac Game Harness UX 关键 |
| **能力倍增曲线** | 以前 1 个工程师管 10 个 module，现在能管 100 个 | AI 时代工程师价值的核心叙事 |
| **AI 主动推送 vs 玩家/工程师自我表达** | AI 一直做事 ≠ 好事；用户需要表达空间 | harness UX 的关键平衡 |
| **AI Native 团队** | 人 + 多 agent 的小团队，**不是工具升级是组织演化** | day-job 12-24 个月内组织演化方向 |
| **知识文档化优先** | agents 性能 = 文档质量；先把文档写好，agents 自然好 | day-job 长期投入方向 |

---

## 整体架构图 / 流程（伪代码）

```
# Glass Bead Games 4 人 + 8 agents 工作流 — day-job 蓝图

# ===== 团队结构 =====
team = {
    "human_1_ceo": Kuangye,           # 架构设计 + 关键决策
    "human_2_engineer": "engineer_A", # 复杂调试 + 跨模块
    "human_3_artist": "artist_B",     # 美术方向 + 视觉决策
    "human_4_designer": "designer_C", # 游戏设计 + 玩法
    "agents": {
        "agent_code_writer_1": "写新 module C++",
        "agent_code_writer_2": "修 compile error",
        "agent_doc_writer": "写 UE module docstring",
        "agent_tester": "跑 unit test + report",
        "agent_pr_reviewer": "review PR + comment",
        "agent_bug_digger": "排查已知 bug",
        "agent_paper_reader": "读 SIGGRAPH/GDC 论文做摘要",
        "agent_dependency_updater": "更新 UE module 依赖",
    }
}

# ===== "AI 接管决策表" =====
AI_HANDOFF_TABLE = {
    # 任务类型 → agent / 人 / 混合
    "write_module_docstring": "agent",
    "run_unit_test": "agent",
    "review_pr": "agent",
    "update_dependency_low_risk": "agent",
    "refactor_low_risk": "agent + human_review",
    "refactor_high_risk": "human + agent_assist",
    "design_architecture": "human",
    "cross_team_collaboration": "human",
    "complex_debug": "human + agent_parallel",
    "implement_new_feature_large": "human + agent_assist",
    "implement_new_feature_small": "agent + human_review",
    "write_design_doc": "human",
    "research_paper_summarize": "agent",
    "research_paper_insight": "human + agent_summarize",
}

# ===== "prompt 清晰度检验" 流程 =====
class PromptQualityTest:
    def test_prompt(self, prompt, task):
        # 1. 找一个不参与项目的工程师
        tester = find_random_engineer(not_in_project=True)
        # 2. 把 prompt 给他
        # 3. 规则：不许追问，只能基于 prompt 做
        result = tester.execute(prompt, task, no_clarification=True)
        # 4. 评估：做对了吗？
        if result.is_correct:
            return "PASS — prompt is clear"
        else:
            return "FAIL — prompt needs clarification. Issues: " + result.issues
            # → 改进 prompt，循环

# ===== "human-in-loop pause points" 列表 =====
HUMAN_PAUSE_POINTS = {
    "before_overwrite_file": True,         # 改写前确认
    "after_n_errors": 3,                   # 连续 3 个错误后 escalate
    "before_refactor_>_100_lines": True,   # 大改动前确认
    "before_commit": True,                 # commit 前 review
    "before_delete_module": True,          # 删除 module 前确认
    "before_breaking_api_change": True,    # 破坏性 API 改动前确认
    "after_8_hours_continuous_run": True,  # 8 小时连续运行后让人确认
}

# ===== 实际工作流（"以前做 10 个现在做 100 个" 范例） =====
# 任务：为一个 open world 写 100 个 NPC 的 behavior tree
def generate_100_npc_behavior_trees():
    # 以前：1 个工程师写 10 个，要 5 天
    # 现在：1 个工程师 + agent 并行写 100 个，要 1 天
    
    # Step 1: 工程师设计模板（human）
    template = human_design_template(npc_archetypes=["patrol", "merchant", "guard", "quest_giver", ...])
    # Step 2: Agent 按模板生成 100 个变体（agent）
    behavior_trees = []
    for archetype in template.archetypes:
        for variant_i in range(20):
            bt = agent_code_writer_1.generate(
                archetype=archetype,
                variant_seed=variant_i,
                context=template
            )
            behavior_trees.append(bt)
    # Step 3: Agent 跑 unit test（agent）
    test_results = agent_tester.run_all(behavior_trees)
    # Step 4: Agent review（agent）
    pr = agent_pr_reviewer.review(behavior_trees)
    # Step 5: 工程师 review 关键 PR（human + agent）
    critical_prs = pr.filter(importance="critical")
    for p in critical_prs:
        human_review(p)  # human-in-loop
    # Step 6: Commit（human + agent）
    # Step 7: Agent 写文档（agent）
    doc = agent_doc_writer.write(behavior_trees, template)
    return behavior_trees
```

---

## 相关论文/前置知识

- [[2026-Tencent-Timi-AgenticAI-GameDev-98pct]] (GDC/Minimax/2026) — Tencent 天美 Agentic AI；**和本文是"AI Native 团队"两种实现路径**：
  - **Tencent 路径**：在 AAA 大型工程里 98% 自动化编程
  - **Glass Bead 路径**：4 人 + 8 agents 小团队做整个游戏
  - **day-job 启发**：两条路径对位不同规模——**大厂走 Tencent 路径，小团队走 Glass Bead 路径**
- [[2026-Bitmagic-AINativeGameEngine]] (GDC/Minimax/2026) — Bitmagic AI-native engine；**和本文是"AI Native"两种实现**：
  - **Bitmagic**：从零建 AI-native 引擎
  - **Glass Bead**：4 人 + 8 agents 跑在现有引擎上
  - **day-job 启发**：day-job 路线是 "UE 加固 + Glass Bead 团队结构"（不是 Bitmagic 路线）
- [[2026-Tencent-HaoYang-AIDrivenPrototype]] (GDC/Minimax/2026) — Hao Yang C.A.T framework；**和本文是"AI 团队工作流"两种视角**：
  - **Hao Yang**：单 LLM + 工具栈（具体技术）
  - **Glass Bead**：人 + 多 agent（团队组织）
  - **day-job 启发**：技术 (C.A.T) + 组织 (Glass Bead) 都学
- [[2026-GoogleDeepMind-SIMA2-GenericGameAgent]] (GDC/Minimax/2026) — SIMA 2；**和本文是"AI 接管什么"两种视角**：
  - **SIMA 2**：AI 玩 3D 游戏（AI as player）
  - **Glass Bead**：AI 帮人做游戏（AI as creator）
  - **day-job 启发**：day-job 押注"AI as creator" 路线

---

## 输出 / 借鉴（forward — 启发到的工程实践）

- **"AI Native 团队" 试点** —— day-job harness 团队按 "≤5 人 + 8-15 agents" 重组试点。**状态**：3 个月内启动
- **"AI 接管决策表"** —— Mac Game Harness 文档顶部维护显式决策表。**状态**：v0.1 同期
- **"prompt 清晰度检验" 机制** —— 内部 prompt 必须通过 "single-shot human test"。**状态**：v0.1 同期
- **"human-in-loop pause points" 清单** —— Mac Game Harness 关键决策点 pause。**状态**：v0.1 同期
- **"agent 可读" LLM 训练数据重写** —— day-job 训练数据从"工程师能读懂" 升级到"agent 能读懂"。**状态**：季度投入
- **"季度失败案例分享" 机制** —— 借鉴 Kuangye 诚实复盘文化。**状态**：季度启动
- **"能力倍增曲线" LLM 训练数据** —— 训练数据要支持 cross-module 知识（Lumen + Nanite + VSM + GAS 跨 module）。**状态**：持续
- **[[05-技术雷达]] P0 加一行** —— "4 人 + 8 agents / AI Native 团队"。**状态**：本周
- **元命题澄清** —— LLM 训练数据保留 UE 工程核心知识，不被"AI Native"叙事冲掉。**状态**：持续

---

## 个人评价

**优点：**

- **真实小团队案例，可信度高** —— 4 人 + 8 agents 是 1 个 indie studio 真实在跑的工作流，**不是大厂 PPT**；**对 day-job 中小团队组织设计参考价值高**
- **"agents 性能 = 文档质量" 是元命题** —— 这条洞察对 day-job LLM 训练数据策略有直接指导意义
- **"prompt 清晰度检验" 是可操作的 hard standard** —— "single-shot human test" 是具体的、可执行的 prompt 质量检验；**比 "be clear" 这种 vague 指导强 100×**
- **"AI 主动推送 vs 玩家自我表达" 平衡是关键 UX 警示** —— day-job harness 容易掉进 "AI 一直做事" 陷阱，Kuangye 提示了危险
- **"游戏设计核心逻辑没根本改变" 是反 hype 洞察** —— 主流叙事都说"AI 改变游戏设计"，Kuangye 明确反对——**day-job LLM 训练数据应该挂这条反 hype 立场**
- **"以前 10 个现在 100 个" 是 AI 时代工程师价值倍增曲线** —— 这是 day-job 工程师职业规划的关键洞察
- **"知识文档化优先" 是 day-job 长期投入方向** —— 不是"买更好模型"，是"写更好文档"

**局限性：**

- **Kuangye 是创业团队 CEO 视角，不是 enterprise 视角** —— "9 个月工作流重发明 5 次" 在 enterprise 不可接受；**day-job 路线选择时要参考但不能全抄**
- **"4 人 + 8 agents" 的具体 agent 是什么没说** —— 用什么模型？Claude / GPT / 本地模型？—— 没说；**day-job Mac 平台模型选择参考有限**
- **"agent 接管决策" 的判断标准没说** —— "这个 agent 能不能搞定" 的判断标准是什么？靠经验？靠 benchmark？—— 没说
- **"agent 排查 bug" 的成功率没说** —— 9 个月里 agent 修 bug 成功率多少？人 review 占比多少？—— 没说
- **"4 人 + 8 agents = 8× 人力" 是粗估** —— 实际可能是 3-4×（agent 不等于人）；**day-job 评估团队规模时要折扣**
- **"agent 消化研究论文" 的质量没说** —— agent 读 SIGGRAPH 论文总结的质量 vs 工程师读的差距多大？—— 没说
- **没谈"AI 失控" 的 risk control** —— 4 人 + 8 agents 里，agent 做了 1 个错误决策谁 catch？怎么 catch？—— 没说
- **没谈"AI 创作 vs AI 取代人" 的伦理** —— Kuangye 是创业团队，自然乐观；**但 enterprise 环境下会有"AI 取代人"的工会/HR 风险**

**启发：**

1. **"4 人 + 8 agents" 是 day-job harness 团队组织演化的真实参考** —— 不是"AI 改变一切"，是"人 + agent 协作"——可立刻试点
2. **"agents 性能 = 文档质量" 是 day-job LLM 训练数据策略的元命题** —— 不是"买更好模型"，是"写更好文档"——day-job 应该按"agent 可读" 重写训练数据
3. **"prompt 清晰度检验" 是 day-job prompt 工程的 hard standard** —— "single-shot human test" 是可执行的标准——立刻可落地
4. **"AI 接管决策表" 是 day-job harness 团队核心管理工具** —— 显式的决策表比"靠默契"好 100×——v0.1 同期建立
5. **"human-in-loop pause points" 是 harness UX 关键** —— 不是"AI 一直做事"，是"AI 自动做 + 关键决策 pause"——v0.1 同期建清单
6. **"游戏设计核心逻辑没根本改变" 是 LLM 训练数据的反 hype 立场** —— 训练数据要保留 UE 核心知识，不被"AI Native"叙事冲掉
7. **"以前 10 个现在 100 个" 是 day-job 工程师价值倍增曲线** —— LLM 训练数据要支持 cross-module 知识，**不**只 deep Lumen
8. **"9 个月工作流重发明 5 次" 是 day-job 在 startup-like vs enterprise-like 之间的路线选择** —— 选 enterprise-like 就要降速到"每 6 个月重发明"

---

## 面试谈资准备

**30 秒版（"知道这篇 + 能说清贡献"）：**

> GDC 2026 Glass Bead Games 的 Kuangye Guo 讲 "4 人 + 8 agents" 小团队做游戏。**核心贡献是给出"AI Native 团队" 的真实工作流**——团队 4 人刻意保持小，每人带 2-3 个 agents 并行推进不同 task。**关键洞察是"agents 性能 = 文档质量"**——知识清晰写进文档时，agents 表现好很多，这反过来逼着团队追问"游戏的核心原则是什么"。**还给出 "prompt 清晰度检验" 的 hard standard**："把 prompt 交给一个人 + 不准追问，他能搞清楚我想要什么吗？" —— 不能的 prompt 必须重写。**对 day-job 启发**：harness 团队按 "≤5 人 + 8-15 agents" 重组 + 训练数据按"agent 可读"重写 + prompt 必过"single-shot human test"。

**2 分钟版（"追问实现细节"）：**

> 第一，**"4 人 + 8 agents"作为明确团队结构**。Kuangye 说"我们刻意保持小团队。每个人在某种程度上都像在带一支队伍，使用多个 agents 并行推进不同的事情"——4 个人 + 8 agents 做原本 30-50 人团队的工作。**9 个月里工作流每隔一两个月重新发明一次**：从单 Claude 任务 → 8 agents 并行 8 个功能 → agents 自己排查 bug + 消化研究论文。**对 day-job 启发**：harness 团队按 "≤5 人 + 8-15 agents" 重组——每个工程师 + 2-3 个 agents，agent 接管文档/测试/PR review/依赖更新，人接管架构/跨团队/复杂调试。

> 第二，**"agents 性能 = 文档质量" 是元命题**。Kuangye 关键断言："**当知识被清晰地写进文档时，agents 的表现会好很多。这反过来逼着你去追问那些根本问题：游戏的核心原则是什么？它到底想表达什么？不然 agent 就会各自为政、方向混乱。**" —— **对 day-job 启发**：**LLM 训练数据 / harness 文档 / UE 项目文档全部要按"agent 可读" 标准重写**——每条 RAG 索引都要有 clear context + clear expected output；每个 MCP tool 都要有 clear description + input/output schema；每个 UE module/class 都要有明确 docstring。**元命题**：**day-job 文档质量 = day-job agent 性能 = day-job AI 化进度**。

> 第三，**"prompt 清晰度检验" 是 hard standard**。Kuangye 给的检验标准：**"如果我把这个 prompt 交给一个人，然后再也没机会和他沟通，他能搞清楚我想要什么吗？如果答案是否，那就继续打磨。"** —— **对 day-job 启发**：Mac Game Harness 内部 prompt 必须通过 "single-shot human test"——把 prompt 给一个不参与项目的工程师，看他能不能不追问就做对。**测试不通过 → 重写 prompt，不允许"prompt 模糊但人能脑补"**。**这是 day-job LLM 训练数据 quality bar 的一部分**。

> 第四，**"AI 接管决策表"是核心管理工具**。Kuangye 说"我们对任何一件事都会先问：这个 agent 能不能搞定？哪个环节需要我们介入？"——**对 day-job 启发**：harness 团队建立显式 "AI 接管决策表"：
>   - 文档撰写/测试运行/PR review/依赖更新 → **agent**
>   - 低风险 refactor → **agent + 人 review**
>   - 高风险 refactor → **人 + agent 辅助**
>   - 架构设计/跨团队协作/复杂调试 → **人**
>   - 大型新功能 → **人 + agent 辅助**
>   - 小型新功能 → **agent + 人 review**
>   **季度更新这张决策表**。

> 第五，**"human-in-loop pause points" 是 harness UX 关键**。Kuangye 提示"AI 主动推送 vs 玩家自我表达" 平衡——AI 一直做事 ≠ 好事。**对 day-job 启发**：Mac Game Harness 必须有显式 pause points：
>   - **before overwrite file**（改写前确认）
>   - **after N errors**（连续 3 个错误后 escalate）
>   - **before refactor >100 lines**（大改动前确认）
>   - **before commit**（commit 前 review）
>   - **after 8 hours continuous run**（8 小时连续运行后让人确认）

> 第六，**"以前 10 个现在 100 个"是能力倍增曲线**。Kuangye 关键断言："**以前做 10 个模型或行为树，现在可以做 100 个。不要再把自己框死在某个狭窄的专业分工里。**" —— **对 day-job 启发**：LLM 训练数据要支持 cross-module 知识（Lumen + Nanite + VSM + GAS 跨 module）——不只 deep Lumen，要"广度 + 深度"—— 工程师能力倍增 = LLM 训练数据的广度要求。

> 第七，**"游戏设计核心逻辑没根本改变" 是反 hype 立场**。Kuangye 关键断言："**游戏设计的核心逻辑并没有根本性的改变，依然是满足玩家的幻想、理解他们的需求、大量测试。**"——**对 day-job 启发**：LLM 训练数据**保留 UE 核心知识**（Lumen / Nanite / VSM / Slate / GAS / replication），**不**被"AI Native"叙事冲掉。**元命题不变**：让 UE 工程更高效 + 让 LLM 理解 UE 特性。

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] "AI Native 团队" 试点 day-job harness 团队重组 → 3 个月内启动
- [ ] "AI 接管决策表" v0.1 文档 → v0.1 同期
- [ ] "prompt 清晰度检验" 机制 → v0.1 同期
- [ ] "human-in-loop pause points" 清单 → v0.1 同期
- [ ] "agent 可读" LLM 训练数据重写 → 季度投入
- [ ] "季度失败案例分享" 机制 → 季度启动
- [ ] [[05-技术雷达]] P0 加 "4 人 + 8 agents / AI Native 团队" → 本周
- [ ] 元命题澄清 — LLM 训练数据保留 UE 核心知识 → 持续

---

*Create date: 2026-07-14*
*Last modified: 2026-07-14*
