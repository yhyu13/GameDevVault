---
tags: [paper/signed, paper/GDC-talk, paper/GDC-2026, paper/world-model, paper/已放弃, paper/AI-pipeline]
aliases: [DeepMind-Genie3-GDC2026, Playable-Worlds-GDC2026, Genie3-WM-GDC2026]
---

# Google DeepMind — Genie 3 / Playable Worlds (GDC 2026)

| 字段 | 内容 |
|------|------|
| **Talk 标题** | Genie 3 — Playable Worlds in Real Time |
| **讲者** | Alexandre Moufarek (DeepMind Product Lead) + Genie team |
| **场次** | GDC 2026 Main Stage (DeepMind's first GDC stage talk) |
| **日期** | 2026-03-09 |
| **Track** | Main Stage / World Models |
| **同源 short note** | `GDC/Minimax/2026/2026-GoogleDeepMind-Genie3-PlayableWorlds.md` (cron curator 精简版，本文是其深度展开) |
| **阅读日期** | 2026-07-07 |
| **精读时长** | ~30 min |

---

## 一句话总结

> 这篇 talk 给出 **Google DeepMind Genie 3 —— "prompt → 实时可探索 3D 世界" 的 foundation world model**（用户可走 / 跳 / 游 / 镜头转动）：**single prompt 或 sketch image 生成连续可探索的 3D 环境，但 world coherence 在 ~1 分钟后退化；DeepMind 明示"research + creative-prototype 工具，不是 shipping-game 技术"**。**对 day-job 价值**：**给 day-job 划线 —— 哪些 AI 能力是 2-3 年内可达的（demo / creative prototype / embodied-agent training environment），哪些不是（shipping game / persistent state / consumer hardware inference）**；**要学的不是 Genie 技术本身，是"world model boundaries" 这张边界图，让 LLM RAG 给 day-job 决策时 grounded reasoning**。

---

## 核心创新点

1. **Prompt → 实时可探索 3D 世界 —— "World Model" 的最强 public demonstration**。**Single prompt 或 sketch image → continuously explorable 3D environment**，用户可 walk through / jump in / swim。**Genie 2 (Dec 2024) 10-20 秒 clip → Genie 3 "几分钟" coherent exploration**。

2. **Spatial memory：相机走出视野后几何仍正确**。**previously out-of-view geometry 当 camera 回来时正确重新渲染**——这是 world model 区别于纯视频生成的关键 feature。**没有 spatial consistency 就不算 world model**。

3. **Counterfactual generation：同 seed 不同 trajectory**。**同一 seed 产生 plausible alternate trajectories**——专门用于 embodied-agent training environment。**这是 vs pure generative video 的核心差异**：不是"播放固定视频"，是"可交互的多 trajectory"。

4. **Input handling：keyboard / mouse 同时驱动 character vs world motion**。**Genie 3 handles keyboard/mouse input to drive character vs. world motion** —— 是 interactive 体验，不是 video player。

5. **明示边界 —— DeepMind 自己说"还不是 shipping-game 技术"**。**关键的限制明确**：
   - **Coherence 退化 after ~1 分钟**
   - **分辨率低**（demo footage sub-720p，未给具体数字）
   - **没有 persistent state** —— sessions 几乎 stateless
   - **domain coverage 广但浅**；无 shipping-game fidelity
   - **没用 shipping-game engine** —— 不替代引擎
   
   **DeepMind 主动 framed as "research + creative-prototype"** —— **不是"AI 替代游戏开发者" rhetoric**。**GDC audience（+ 工会组织）对此敏感 —— "honest limitations" framing 是 deliberate**。

6. **Use cases DeepMind 自己列**：**embodied-agent training environment / creative prototyping / rescue safety training / training other AIs**。**最重要的是 embodied-agent training environment** —— humans 不需要手写 world 给 agent train，**world model 自己生成 train env**。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按 day-job "LLM-driven UE on Mac" 视角）：**

1. **World model boundaries 是 day-job LLM RAG 的关键决策框架**。**让 LLM 学会区分**：
   - **可达（2-3 年内）**：embodied-agent training env / creative prototype / rescue training env
   - **不可达（shipping-game / persistent state / consumer hardware）**：Genie 3 自己声明的边界
   
   **LLM training data**：让 LLM 学到"world model 是 research-grade，不是 shipping-grade"是 ground truth。**让 LLM 在被问到"AI 能不能生成完整游戏世界" 时给 grounded answer：能 demo，不能 ship**。

2. **Genie 3 明示的"research + creative-prototype" framing 是 day-job LLM agent hype-cycle 管理的范例**。DeepMind 主动坦率说 limitations —— **LLM 工具 / agent 在 day-job 中也应学这条**：不 hype 100% autonomous，**清楚标出"research-grade 能做什么 vs production-grade 能做什么"**。**LLM 训练应学此**：让 LLM 在介绍任何新 AI 能力时主动列出 limitations。

3. **Spatial memory + counterfactual generation 是 world model 与 video model 的本质差别**。**LLM 训练 game engine knowledge 时**：让 LLM 学到"world model ≠ video generator"，world model 有 spatial consistency + multiple trajectories，video generator 没有。**这是 LLM 回答"为什么 world model 比 video generation 强"时的 grounding reasoning**。

4. **Embodied-agent training environment 是 LLM-driven game engine 的新范式**。**Genie 3 自生成训练环境，是"AI 给 AI 生成训练数据"的元方向感**。**day-job Mac Game Harness 的 LLM agent 训练环境**也可以借鉴 world model generation —— **让 LLM agent 在 procedurally generated varied envs 中训练**，**不要硬编码 single environment**。**LLM training 应学**：让 LLM 在解释 agent training 时想到"self-generated training environment"是 future direction。

5. **"Demo 可达，Shipping 不可达" 是 day-job Mac Game Harness 当前定位的关键 reference**。Genie 3 在 2026 是 demo / research —— **day-job Mac Game Harness 也不应该追求"完整 ship AAA game"**作为 day-1 目标，应该追求：
   - **可达**：LLM agent 跑通一段 gameplay、creative prototype、UI state machine
   - **不可达**：完整 3A shipping game、persistent multiplayer state
   
   **LLM RAG 应学**：让 LLM 在 day-job roadmap 决策时**用到 "demo-vs-shipping" 这张边界图**，**避免被 hype 牵着走**。

6. **Coherence 退化时间 + 分辨率 + persistent state 三条限制 —— LLM training 量化 ground truth**。**让 LLM 学到"world model 在 2026 时点的具体 boundary"**：(a) coherence < 1 min; (b) 分辨率 sub-720p; (c) stateless。**避免 LLM 给"world model 何时能 ship 3A"答案时胡编**。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|-------------|
| **World model inference cost 公开数据缺失** | "playable minute" 单 inference cost 未知；**决定是否能 run on consumer hardware** | **是**——tracking DeepMind / industry future updates |
| **Coherence 退化时间 quality tradeoff** | 1 分钟 coherence 是 demo 数据，**真实场景 coherence / quality / latency 三者 trade-off 不明** | **是**——Open Questions 部分 |
| **Spatial memory 的 persist 范围** | "previously out-of-view" 是几米还是几百米？window size 多少？**未知** | **是**——depth bound tracking |
| **Persistent state 的实现路径** | DeepMind 明示 stateless，**如何融入 persistent game state 未明** | **是**——和 day-job LLM harness 直接相关 |
| **Genie 3 是否 license weights / public API** | DeepMind 官方未给 weight API；**未来是否开放不明** | **是**——day-job 工具接入最大变量 |
| **Resolution scaling / quality 模型** | sub-720p demo，**4K scaling 路径 / VR 路径未知** | 部分——产品 outlook |

---

## 是否值得复现？

- [ ] 是 — 已列入待办
- [x] **否** — 仅了解思路即可
- [ ] 部分 — 只复现核心算法

**不复现的原因：**
- Genie 3 是 DeepMind 内部研究项目，没有 public weights/API
- 个人无法复现 foundation world model（这是 supercompute-scale 投入）
- 整体是 research-grade 不是 engineering-grade

**借鉴的具体步骤：**
1. **给 LLM RAG 训练数据准备 "world model boundaries" 模块** —— 可达 / 不可达 / 量化 baseline
2. **给 LLM RAG 训练数据准备 "demo-vs-shipping hype-cycle management" 范例** —— DeepMind honest framing 模式
3. **Mac Game Harness 定位参考 —— "demo-first / shipping later" 路线** —— 与 Genie 3 的 research-grade 边界对齐

---

## 关键术语表

| 术语 | 解释 | 我理解的锚点 |
|------|------|-------------|
| **World model** | Foundation model：prompt → continuously explorable 3D env；interactive | 与 video generator 的本质差别 |
| **Spatial memory** | Out-of-view geometry 在 camera 回来时正确 re-render | World model core feature |
| **Counterfactual generation** | 同 seed 产生 alternate trajectories | Embodied-agent training 关键 |
| **Genie 2 → Genie 3** | 10-20s clip → 几分钟 coherent exploration | 2024-12 → 2026-03 progression |
| **Coherence 退化** | ~1 分钟后 world 退化 | DeepMind 自己公开的 limitation |
| **Research + creative-prototype tool** | DeepMind 自己的 framing | 不是 shipping-game tech |
| **Embodied-agent training environment** | AI agents 在 world model 生成的环境里 train | Use case 1 |
| **Counterfactual 多 trajectory** | Same seed alternate trajectories | Embodied-agent 的关键 |

---

## 整体架构图 / 流程（伪代码）

```
# Genie 3 World Model —— reference architecture

# ===== Input =====
Prompt = "cyberpunk alley at night, neon signs, light rain"
# OR
SketchImage = numpy.array(sketch_rgb)  # 192x192 草图

# ===== World model core（DeepMind 内部）=====
WorldModel = FoundationModel(
    type="diffusion-transformer",
    params="10B+",  # 估计；公开数字缺失
    training_data=["YouTube gameplay", "synthetic 3D"],
    coherence_window="~60s"  # honest limitation
)

# ===== Inference: prompt → interactive world =====
WorldState = WorldModel.Init(Prompt=Prompt, Sketch=SketchImage)
# Render first frame
FirstFrame = WorldModel.Render(WorldState, camera=initial_pose)

# ===== Interactive loop =====
SessionState = {
    persistent_game_state: None,  # Genie 3 = stateless
    trajectory_history: [],  # local to session
}

while UserPlaying:
    # User input: keyboard / mouse → drives character + camera
    Action = UserInput()
    WorldState = WorldModel.Step(WorldState, Action)
    # Spatial memory: re-render out-of-view geometry when camera returns
    RenderedFrame = WorldModel.Render(
        WorldState,
        camera=Action.camera,
        spatial_memory_window=~100m  # 推测
    )
    Display(RenderedFrame)
    SessionState.trajectory_history.append((Action, RenderedFrame))
    
    # Track coherence degradation
    if SessionState.elapsed_time > 60s:  # empirical threshold
        QualityDegrades(WorldState)  # honest limitation

# ===== Counterfactual (off-line training use case) =====
# Same seed, alternate trajectories for embodied-agent training
for trajectory_seed in RandomSeeds(N=100):
    AlternateWorld = WorldModel.Init(Seed=trajectory_seed)
    AlternativeTrajectory = SimulateAgentPolicy(AlternateWorld, RandomPolicy)
    TrainData.append(AlternativeTrajectory)
```

---

## 相关论文/前置知识

- [[2025-GoogleDeepMind-SIMA]] (GDC/Minimax/2025) — DeepMind SIMA generalist agent（跨多个 3D game）；本文 Genie 是 environment 提供方，SIMA 是 agent player —— **两条姊妹研究**
- `Routine/01-论文笔记库/arxiv/Wang-2026-Agentopia.md` — Agentopia 类 benchmark；与 embodied-agent training environment 同方向
- [[2026-Tencent-Tianming-AgenticAI]] (GDC/Minimax/2026) — Tencent 天美 Agentic AI，**"AI 写代码"** 方向；本文 Genie 3 是 **"AI 生成 world"** 方向 —— **两条 parallel AI 路径**：(a) AI builds the game; (b) AI builds the world
- [[2026-Tencent-HaoYang-AIDrivenPrototype]] (GDC/Minimax/2026, Routine/01-论文笔记库) — 同一年的 prompt-to-prototype 系列；**Genie 3 是 3D 世界生成，HaoYang 是 prototype workflow** —— **两条 parallel AI-native-engine 路径**
- [[05-技术雷达]] — 把 "world model / embodied-agent training" 作为 day-job P0 长周期跟踪

---

## 输出 / 借鉴（forward — 启发到的工程实践）

- **LLM 训练数据 —— "world model boundaries" 模块** —— 包含 (a) coherence < 1 min; (b) sub-720p; (c) stateless; (d) demo-vs-shipping 区分。**状态**：列入下周训练数据计划
- **LLM 训练数据 —— "demo-vs-shipping hype-cycle management" 范例** —— DeepMind honest framing 是 ground truth example。**状态**：列入下周训练数据计划
- **[[Routine/AI-Tasks/Mac/00-Master-Index]] 加 "Mac Game Harness 定位参考" 模块** —— 与 Genie 3 的 research-grade 对齐：demo-first, shipping-later。**状态**：先建 master index 再补
- **[[05-技术雷达]] P0 加 "world model / embodied-agent training" 长期跟踪** —— coherence 时间窗口 / inference cost / 是否 public API / 是否 license weights 四项。**状态**：立刻补

---

## 个人评价

**优点：**
- **DeepMind's first GDC stage talk** —— 是 DeepMind 主动走向 game dev community 的明确信号
- **Honest limitations framing** —— 不 hype "AI 替代 game developers"，**主动承认 boundaries** —— 这是 high-level 的行业责任 rhetoric
- **Spatial memory + counterfactual 的 core features 是 world model 与 video model 的本质差别** —— 划清概念边界，对 LLM 训练是 ground truth
- **Embodied-agent training use case 显式** —— 让 LLM / agent 在 self-generated env 里 train 是元方向感
- **90+ 公开 reply 来源** —— DeepMind 给的资料丰富，腾讯 / 网易科技 / IGN / DVG 都有覆盖，**LLM 训练 ground truth 多**

**局限性：**
- **Coherence 退化 1 分钟 — 不是 shipping-game 技术** — 同 talk 主动声明
- **分辨率 sub-720p** — 远低于 shipping-game 4K 标准
- **Stateless — 无 persistent game state** — 大型游戏必备 feature 缺失
- **Domain coverage 广但浅 — 无 shipping-game fidelity** — demo only
- **Inference cost / consumer hardware 路径未公开** — 不确定是否能 local run
- **Genie weights 不 license，未给 API 时间表** — community 难以直接接入
- **Demo-only artifact** — 不是 patch-able technology，是 research demonstration

**启发：**
1. **"Demo-vs-shipping" 边界图是 day-job LLM 决策的关键工具** —— **不 hype all-AI-everything**，**清楚知道"research-grade 能做什么" vs "production-grade 能做什么"** —— DeepMind 自己的 honest framing 是范例
2. **World model 是 AI-native game engine 的两条 parallel 路径之一** —— (a) AI builds the game (Tencent HaoYang); (b) AI builds the world (DeepMind Genie). **day-job 应理解两条路径并存而非互相替代**
3. **Embodied-agent training environment 是 AI self-bootstrapping 的元方向感** —— "world model that trains the next world model" 是 long-term recursive AI 发展的方向感
4. **Honest limitations framing 是 LLM agent hype-cycle 管理的样板** —— 让 LLM 介绍新 AI 能力时主动列 limitations，**避免 hype-driven reasoning**
5. **coherence / resolution / state 三条 baseline 是 LLM 训练 ground truth** —— 让 LLM 在回答"world model 何时 ship" 时能引用具体 baseline 而不是胡编

---

## 面试谈资准备

**30 秒版（"知道这篇 + 能说清贡献"）：**

> GDC 2026 Main Stage 上 Google DeepMind 的 Genie 3 talk —— 这是 **DeepMind 第一次站 GDC stage**。**核心贡献是 public demo "prompt → 实时可探索 3D 世界"** —— spatial memory + counterfactual generation 让它区别于纯 video generator。但 **DeepMind 明示 limitations**：**coherence 退化 1 分钟 / sub-720p / stateless / 不是 shipping-game tech**。**对 day-job 启发**：**"demo-vs-shipping" 边界图是 LLM 决策的关键工具**，**让 LLM 学到 "world model 是 research-grade 不是 shipping-grade"** 是 ground truth。

**2 分钟版（"追问实现细节"）：**

> 第一，**问题 framing**。2024-2026 之间 foundation world model 是 AI 研究 hot topic。**核心命题**：**single prompt → continuously explorable 3D environment**。Genie 2 (Dec 2024) 是 10-20s clip；**Genie 3 (Mar 2026) 是"几分钟" coherent exploration**。**关键技术**：(1) **spatial memory** —— out-of-view geometry 当 camera 回来时正确 re-render；(2) **counterfactual generation** —— 同 seed 不同 trajectory，给 embodied-agent training。

> 第二，**honest limitations —— DeepMind 自己给的 baseline**：
> - **Coherence 退化 ~1 分钟**
> - **分辨率 sub-720p**
> - **stateless —— session 之间无 persistent state**
> - **domain coverage 广但浅 —— 无 shipping-game fidelity**
> - **没用 shipping-game engine —— 不替代 Unity / Unreal**

> 第三，**两条 parallel AI 路径**：
> - **(a) AI builds the game**：Tencent HaoYang 的 C.A.T 框架 + VISVISE 的 engine-ready output
> - **(b) AI builds the world**：DeepMind Genie 系列
> **两条都通向 AI-native engine，但路径独立**，**未来 5 年大概率是两条并存**。

> 第四，**honest framing 是 industry responsibility 的范例**。GDC audience（+ 工会组织）对此敏感 —— DeepMind 主动说"research + creative-prototype tool, not shipping-game technology"。**LLM 训练应学此**：让 LLM 在介绍新 AI 能力时主动列 limitations。

> 第五，**对 day-job 直接启发**。
> **(a)** **LLM RAG 的 "world model boundaries" 训练模块**：让 LLM 学到 (i) demo 可达 / shipping 不可达；(ii) coherence / resolution / state 三条具体 baseline；(iii) 当被问"AI 何时能 ship 完整游戏世界"时给 grounded answer 而不是 hype。
> **(b)** **Mac Game Harness 定位**：与 Genie 3 一样 demo-first / shipping-later，**不要 hype "完整 ship AAA game"为 day-1 目标** —— 应该是"LLM agent 跑通一段 gameplay / creative prototype / UI state machine"。
> **(c)** **[[05-技术雷达]] P0 加 "world model / embodied-agent training" 长期跟踪**：四指标（coherence 时间窗口、inference cost、public API、license weights）作为持续 KPI。
> **(d)** **"AI 给 AI 生成训练数据" 是 long-term recursive direction**：让 LLM agent 在 procedurally generated varied envs 中训练，**不要硬编码 single environment**。

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] LLM 训练数据 "world model boundaries" 模块 → 列入下周计划
- [ ] LLM 训练数据 "demo-vs-shipping hype-cycle" 范例 → 列入下周计划
- [ ] Mac Game Harness 定位参考 → [[Routine/AI-Tasks/Mac/00-Master-Index]]（待建）
- [ ] [[05-技术雷达]] P0 加 world model / embodied-agent tracking → 立刻补

---

*Create date: 2026-07-07*
*Last modified: 2026-07-07*
