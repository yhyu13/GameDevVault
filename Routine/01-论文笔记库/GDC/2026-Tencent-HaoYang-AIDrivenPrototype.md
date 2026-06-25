---
tags: [paper/signed, paper/GDC-talk, paper/GDC-2026, paper/AI-pipeline, paper/game-tooling, paper/待复现]
aliases: [CATFramework-GDC2026, HaoYang-AIDrivenPrototyping-GDC2026]
---

# Tencent Photon — AI-Driven 3D Game Prototyping (C.A.T framework) (GDC 2026)

| 字段 | 内容 |
|------|------|
| **Talk 标题** | AI-Driven 3D Game Prototyping — How the C.A.T Principle Lets Language Models Ship Playable 3D Prototypes |
| **讲者** | Hao Yang (郝阳), Senior Engineer, Tencent Photon Studio Group (光子工作室群 首席工程师) |
| **场次** | GDC 2026 — AI Summit (talk 排队从开始前 1 小时排到满员) |
| **日期** | 2026-03 (Moscone Center, San Francisco) |
| **Track** | AI Summit |
| **来源 PPT** | `Routine/01-论文笔记库/GDC/AI-Driven 3D Game Prototyping - GDC 2026/` (13 张 PptxGenJS 源码 + 编译后 .pptx + 56 行 summary.md) |
| **同源 short note** | `GDC/MiniMax/2026/2026-Tencent-HaoYang-AIDrivenPrototype.md` (cron curator 的精简版) |
| **阅读日期** | 2026-06-25 |
| **精读时长** | ~1h (summary.md + 13 张 slide 源码) |

---

## 一句话总结

> 这篇讲的是 **AI 在 3D 游戏引擎里做不到 prototyping 的根本原因**——不是 AI 不够强，是 **3D 工具栈是为人类 GUI 设计的，AI 看不见像素**——并提出 **C.A.T 三原则**作为解药：**C**ode Reuse（TypeScript 在 Web 和 Engine 之间共享同一份源码）、**A**dapter Design（Core 规则 vs 平台 adapter 分离，AI 只摸 Core）、**T**oken-Friendly（**最重要**：先把 3D 世界 tokenize 成 bounding box / marker / domain rule，AI 才操作得了）。整套方案在 Unreal 上落地，三场 demo 跑通（8-Ball Pool 100% 功能、Top-down RPG 单 prompt 40 分钟生成 70% 内容、Action Combat 多个 boss 机制）。

---

## 核心创新点

1. **正确定位问题——3D prototyping 的瓶颈不在 LLM 智力，在 3D 工具栈的"非文本化"**。Web 2D 游戏 AI 早就能 ship——DOM / CSS / JS 是文本规范，LLM native 处理。但 3D 引擎：渲染层跨引擎不标准化（Unreal ≠ Unity ≠ 自研）、几十年的 GUI 工具面向人类艺术家、物理碰撞光照全是"非文本表面"、每个工作室代码库都是定制雪花。**所以问题不是"训练更强的 LLM"，是"重构 3D 工具栈让 LLM 能 native 处理"**——这是 O'Reilly 教科书级 problem framing。

2. **C = Code Reuse —— TypeScript 共享一份源码，两个 runtime**。Web prototype 用 TypeScript，Unreal prototype 也用 TypeScript，**不是两份代码**——通过 **Puerts**（Tencent 开源的 TypeScript-to-engine bridge，no C++ / no Blueprint）调用引擎 API；UI 通过 Unreal 内置的 **Web Browser widget** 渲染，"**pixel-perfect parity**"——你在 Web 看到的什么样子，进 engine 就什么样子。**好处**：AI 学一个 codebase（不是两个）、context window 更小、UI 与 Web 原型一致。**本质是"AI-friendly language（TypeScript）替换 AI-hostile language（C++）"**。

3. **A = Adapter Design —— Core vs Adapter 分层**。游戏逻辑（state、规则、行为树）抽出来叫 **Core**，每个平台（Web、Unreal）写自己的 **Adapter**。Web adapter 包 DOM + Canvas；Engine adapter 包 Unreal ECS + Puerts。**AI 只被允许碰 Core，绝对不碰 Adapter**——Adapter 是平台 native 的（渲染、物理、引擎 I/O），LLM 处理不了也不应该处理。**这是 hexagonal architecture / ports-and-adapters 在游戏 AI 场景的具体应用**——工程上是常见模式，但讲者明确"AI only writes Core"是工程边界的硬约束。

4. **T = Token-Friendly —— 整个 talk 最 critical 的原则**。"**Game tools were built for humans. AI reads tokens. Stop expecting AI to see pixels.**" 三条具体战术：
   - **注入 domain rules** —— 把"标准台球桌尺寸 / 球的轨迹 / 物理常量"作为 text prompt 喂给 AI，**这些知识 AI 不能 Google 到**。
   - **暴露 asset metadata** —— bounding box、collider、tag、label **全部以文本形式呈现**，AI 操纵的是 3D 世界的**文本投影**，不是 3D 原语。
   - **Designer markers** —— 设计师在场景里留**命名标记**，AI 读 marker 名字当 token 用，**把 GUI 操作转译成"程序员 console 命令"那种工作方式**。
   
   **这是最重要的设计哲学转变**：3D 工具栈的设计目标从"服务人类视觉 + 鼠标"切换到"服务 LLM 文本流"。**短期内这两套 UI 会并存，长期 token-first 会赢**。

5. **三场 demo 验证"70% prototype from one prompt"是新的 baseline**。
   - **8-Ball Pool**：物理确定性 + 规则简单 → AI 工具压测沙盒，**100% 功能**。
   - **Top-down RPG**：单 prompt 喂给 AI，**40 分钟产出最终游戏 ~70% 内容**——这是**单个 prompt 一次性产出的天花板数字**。
   - **Action Combat**：多角色、多 boss、多种机制——**最有野心的 test case**，大部分 boss 机制都跑通。
   
   **核心数字不是某个 demo 的完成度，是"单 prompt → 70% RPG"的 metric**——它重新定义了 "AI productivity 在 3D 游戏场景下的下限"。

---

## 与我当前工作的关联度

- [ ] P0 — 直接相关，立即能应用
- [x] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按"游戏引擎程序员 + 当前在做的读项目代码工作"角度排）：**

1. **"Tokenize before AI touches it" 是读项目代码的元方法论**。我现在的工作是**用 LLM 读别人的 UE 项目代码**——而 LLM 对 UE 项目代码的最大痛点是：**UE 项目是 3D 视觉 + C++ native + Blueprint GUI + 资产引用的混合体**。LLM 看不见 PIE 跑起来什么样，看不见 Blueprint 节点的连接，看不见 AnimGraph 节点的拓扑。C.A.T 的 **T** 原则给的就是这个问题的解药：**先把 3D / 视觉 / GUI 转译成文本（domain rule、metadata、marker），LLM 才能高效工作**。**对读项目代码的直接应用**：写"项目导览笔记"时，先用一句话 tokenize 这个项目（"这是 Lyra / 团队死斗模板 / 用 ALS 做动画 / 用 SMC 做移动"），再让 LLM 沿着 token 化的骨架深入；不要直接 dump 整个 codebase 让 LLM 自己 parse。**比 raw 代码 dump 节省 50%+ context**。

2. **"AI 只写 Core，Adapter 留给平台 native"是 subsystem 边界划分的硬约束**。在 Lyra / 自研引擎项目里，**最大的可读性问题不是单个模块，是模块边界**——哪些模块"业务逻辑"该被外部工具/AI 编辑？哪些模块"基础设施"该对外部只读？**A 原则给的硬约束**："AI writes Core; Platform handles I/O"。**对项目代码阅读的直接应用**：看到一个项目，**先识别 Core 层和 Adapter 层**——Core 是常被改的业务逻辑、Adapter 是稳定的平台适配。**这是 LLM 辅助阅读的"语义地图"**，比纯按目录结构理解快 3 倍。

3. **Puerts + TypeScript 替代 C++/Blueprint 是值得验证的尝试**。Lyra / 自研项目里，**新手读 C++ + Blueprint 双语言的 learning curve** 是真实瓶颈。Puerts 让 TypeScript 同时跑 Web 和 Engine，**降低 prototype 阶段的语言摩擦**——但 production 性能是否 OK、UE 5.x 兼容度、团队接受度都是问题。**对 day job 的启发**：如果项目组愿意承担 prototype 阶段的语言切换成本，Puerts 是值得探索的工具；不建议 production 上船。

4. **"GUI-first → token-first"是工具栈演化的方向感**。讲者预言的"短期内 GUI 和 token-first 共存、长期 token-first 赢"是个**值得记住的工具栈演化论**。**对 UE5 / 自研引擎的启发**：当 Epic 推出新编辑器功能（UE 5.7+ 的新 AnimGraph 编辑器、新 Material Editor、AI Assistant）时，**判断哪些是 GUI 增强、哪些是 token-first 转型**，有助于识别哪些是未来 3-5 年的方向、哪些是当下补丁。

5. **不要复现整篇，但要复现 "tokenize project before reading" 的工作流**。具体步骤：(1) 用一句话 tokenize 项目骨架；(2) 列出 domain rule（"这是 Lyra / 用 ALS / 用 SMC / GAS / replication 走 push model"）；(3) 暴露关键模块的 metadata（"GameMode 用 LGGameMode、Character 用 LGCharacter、Component 用 LGXxxComponent"）；(4) 用 designer markers 思路做"读代码时的导航标记"。**这是 reusable 的元工作流**，可以直接抄。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|-------------|
| **Puerts 与 UE 5.x 的兼容性** | Puerts 是 Tencent 开源，但跟 Epic 主线的 UE 版本同步是持续工作 | 否——Puerts 维护团队管，跟进 release notes 即可 |
| **TypeScript 在 Unreal 引擎层的运行效率** | 解释执行 vs JIT vs AOT；是否够 production | 是——prototype 阶段 OK，production 需 benchmark |
| **Adapter 层的设计粒度** | Core 抽多深？Adapter 包多少 native 接口？太深 Core 就空了，太浅 Adapter 重复 | 否——这是软件设计常识，按需调整 |
| **Tokenization 策略的工程化** | 哪些 asset metadata 必须暴露？哪些 designer marker 必须有？这是 design system 级别的决策 | 是——任何一个真实 3D 项目做这套 token-first 改造都需要 2-3 周设计 |
| **AI 写出来的 prototype 怎么 verify** | 跑得起来 ≠ 跑得对；需要设计师手动 play-test 30 分钟一轮 | 否——这是 prototype workflow 的常态 |
| **Web 2D → 3D 的能力迁移** | 单 prompt 70% RPG 这个数字是 2D-like 场景；3D 真实复杂场景（multi-level、multi-system）能到多少？ | 是——3D 真实复杂度的 tokenization 工作量比讲者 demo 大一个数量级 |

---

## 是否值得复现？

- [ ] 是 — 已列入待办
- [ ] 否 — 仅了解思路即可
- [x] 部分 — 只复现核心工作流

**复现计划：**
- **不复现 Puerts + Unreal 集成**（需要真实的 UE 工程 + Tencent 内部知识，超出个人复现能力）
- **不复现完整 token-first 工具栈**（涉及编辑器层改造，2-3 周工作量，且需要团队决策）
- **可复现的部分**：
  1. **"Tokenize project before LLM reading" 工作流** —— 立刻可用：每周读新项目代码前，先写 1 页 "tokenized project map"（一句话骨架 + domain rule + 关键模块 metadata + 读代码 navigation marker），然后用 LLM 沿 token 化骨架深入。预期：节省 30-50% context、加速 2x code reading
  2. **"Core vs Adapter" 项目分解** —— 把正在读的 Lyra（或任何 UE 项目）按"业务逻辑（Core）"vs "平台适配（Adapter）"分层标注，画一张子系统 boundary 图，验证 C.A.T 框架的可读性提升效果
  3. **Adapter Pattern 在自研引擎模块的应用** —— 如果未来要写可被 AI 辅助编辑的工具子系统，套用 "AI writes Core; Platform handles Adapter" 的硬约束

---

## 关键术语表

| 术语 | 解释 | 我理解的锚点 |
|------|------|-------------|
| **C.A.T framework** | Code reuse / Adapter design / Token-friendly 三原则；讲者自创术语 | 类似 SOLID 的工程原则集合 |
| **Puerts** | Tencent 开源 TypeScript-to-Unreal bridge | 替代 C++/Blueprint 调用引擎 API；类似 Unity 的 C# binding |
| **Tokenize 3D** | 把 3D 场景转译为文本（bounding box / collider / tag / domain rule） | LLM native 工作在 token 流；3D 原语是 GUI 时代产物 |
| **Designer markers** | 设计师在场景里留的命名锚点；AI 当 token 用 | 类似 UE 的 Actor tag / folder 命名约定 |
| **Hexagonal architecture** | 软件架构模式：核心业务 vs 平台适配分离；A 原则借用此概念 | 又称 ports-and-adapters；游戏引擎模块设计的常见模式 |
| **Pixel-perfect parity** | Web 端 UI 和引擎内 UI 视觉一致；Puerts + Unreal Web Browser widget 实现 | 设计师在 Web prototype 改的 UI，进 engine 不用重做 |
| **Web 2D vs 3D engine AI capability gap** | LLM 已经能 ship Web 2D 游戏，但 3D engine 是下一个 bottleneck | 讲者全文 problem framing 的核心 |

---

## 整体架构图 / 流程（伪代码）

```
# AI-Driven 3D Prototyping 的 prompt → playable 流程

# ===== T 原则: 先 tokenize 3D 世界 =====
TokenizedScene = Tokenize(World):
    return {
        domain_rules: [                    # 注入的领域知识
            "Standard pool table: 2.84m x 1.42m, pockets at corners + middle of long sides",
            "Ball physics: friction coeff 0.2, restitution 0.95",
            ...
        ],
        asset_metadata: [                  # 3D 资产以文本呈现
            { name: "cue_ball",  bbox: [...], collider: "sphere r=0.028m", tag: "ball" },
            { name: "table",     bbox: [...], collider: "box",            tag: "static" },
            ...
        ],
        designer_markers: [                # 设计师标注的命名锚点
            { name: "SpawnPoint_Player1", position: (0, 0, 1.5), tag: "spawn" },
            ...
        ]
    }

# ===== C 原则: 同一份 TypeScript 源码 =====
# Core game logic (AI writes this, both Web and Engine run it)
class PoolGameCore:
    def on_strike(self, ball_id: str, force: Vec3):
        # 物理逻辑 + 状态机
        ...
        return GameState(...)

# Web adapter (DOM + Canvas)
WebAdapter = createDOMAdapter(PoolGameCore)

# Engine adapter (Unreal + Puerts)
EngineAdapter = createUnrealAdapter(PoolGameCore, PuertsBridge)

# ===== A 原则: AI writes Core, Platform handles I/O =====
LLMPrompt = f"""
  Given this 3D scene (tokenized):
  {TokenizedScene.toText()}
  
  Write a PoolGameCore.on_strike implementation that:
  - applies realistic friction
  - handles ball-ball collisions
  - detects pocket entry and updates score
"""

GeneratedCoreCode = LLM.complete(LLMPrompt)

# 验证 + 迭代（设计师手动 play-test）
while not DesignerSatisfied(GeneratedCoreCode):
    Feedback = Designer.play_test()  # 30-min iteration
    GeneratedCoreCode = LLM.complete(refine(LLMPrompt, Feedback))
```

---

## 相关论文/前置知识

本笔记是 `Routine/01-论文笔记库/GDC/` 子目录下的**第一篇深度 paper note**——同目录还有姊妹 talk [[2026-Tencent-MagicStudio-RealTimeMotionGeneration]]（Magic Studio 的实时 AI 动作生成，和本篇一起从 `GDC/MiniMax/` 复制过来；本篇偏工具链侧，那篇偏运行时侧）。

- [[00-README]] — 论文库入口；`Routine/01-论文笔记库/GDC/` 用于归位 GDC talk 的深度 paper note
- `GDC/MiniMax/2026/2026-Tencent-HaoYang-AIDrivenPrototype.md` — cron curator 的精简版（1 页），本文是它的深度展开
- `GDC/MiniMax/2026/2026-Tencent-VISVISE-FullPipeline.md` — Tencent VISVISE 全栈 AI 美术管线（同年的姊妹 talk，聚焦 asset 生成；本篇聚焦 prototyping workflow）
- `GDC/MiniMax/2026/2026-Panel-TripoBitmagicGlassBead.md` — Tripo/Bitmagic/Glass Bead AI-native engine panel（panel 中多位创始人讲 prompt-to-game 的工具哲学；和本篇"tokenize 3D for AI"思路同源）

---

## 输出 / 借鉴（forward — 区别于上方"相关论文/前置知识"的 backward）

> 下面三条**不是**本篇的相关文献，而是本篇**启发到的自己的工程实践**——反向借鉴，从 talk 到自己的笔记。

- **"Tokenize project before LLM reading" 元工作流** — 每周读新 UE 项目代码前，先写 1 页 tokenized project map（一句话骨架 + domain rule + 关键模块 metadata + navigation marker），再让 LLM 沿 token 化骨架深入。**这是 C.A.T 的 **T** 原则在 code reading 上的直接迁移**，比 raw codebase dump 节省 30-50% context。**状态**：立刻可落地，下周开始用。
- [[Routine/AI-Tasks/Lumen/00-Master-Index]] — **A 原则（"AI writes Core, Platform handles Adapter"）可以直接迁移到 Lyra 子系统分解** —— 读 Lyra 时把模块按"业务逻辑（会被改的）"vs "平台适配（稳定不动）"分层画 boundary 图。这是 LLM 辅助阅读的"语义地图"。**状态**：可在 Lyra code reading 周应用。
- **"GUI-first → token-first" 演化方向感** — 当 Epic 推出新编辑器功能时，识别哪些是 GUI 增强、哪些是 token-first 转型，有助于判断 3-5 年方向。**状态**：作为 long-term 技术雷达条目跟踪。

---

## 个人评价

**优点：**
- **Problem framing 极准** —— "LLM 不能做 3D 不是智力问题，是工具栈问题"是 O'Reilly 教科书级的 framing。直接把锅从"训练更强的模型"挪到"重构工具栈"，**问题换一种问法就解了**。
- **C.A.T 三原则命名好记 + 工程可落地** —— 不像有些 AI 论文起名 "Foundation Model X"，**C.A.T 是工程设计原则**——可以直接在项目里 checklist：① 代码能不能跨 runtime 共享？② Core/Adapter 分了没？③ 3D 场景 tokenize 了没？
- **T 原则的"domain rules + asset metadata + designer markers"三条战术是 production 级别的** —— 不是 PPT-level 高论，是真的能写进 design doc 的具体动作。**每条战术都是 ~1 周工作量**，合起来是 ~3 周项目。
- **三场 demo 覆盖不同难度** —— 8-Ball（简单规则）/ RPG（中等复杂度）/ Action Combat（多系统）—— 不是只挑最有利的 demo，**梯度展示了 token-first 方法在不同复杂度下的边界**。

**局限性：**
- **没说 production 性能** —— Puerts 的 TypeScript 在 Unreal 上的 runtime 开销？三场 demo 都是 prototype 级别，没说"这套方案 ship 到一个真实的 3D 商业游戏会损失多少性能"？Lyra / AAA 项目能不能直接套用？
- **"单 prompt 70% RPG" 这个数字的边界没说清** —— 是 30% 还是要设计师大量补？还是 70% 已经可玩？讲者含糊带过。**真实工程的数字必须给 boundary condition**。
- **没说 token-first 工具栈的演进成本** —— 把 3D 工具栈从 GUI-first 改造到 token-first **需要整个团队改工作流**——不是某个 Epic release 就能解决的；讲者没给"团队 adoption 的阻力来自哪里 / 怎么解决"。
- **没给 "AI 写错 Core code" 的兜底机制** —— LLM 生成的 TypeScript 有 bug 怎么办？讲者含糊说"设计师 play-test 30 分钟迭代"，**这是 prototype 阶段 OK，但 production 阶段需要更系统的 verification pipeline**。
- **从 engine dev 角度**：整套方案对**真实项目代码的可借鉴性高**（A 原则、T 原则的元工作流），但对**性能/渲染/网络层零贡献**——和 [[2026-Tencent-MagicStudio-RealTimeMotionGeneration]] 比，更偏工具链侧。

**启发：**
1. **"问题换一种问法就解了"是 AI 时代最值钱的能力** —— 不是"训更强的 LLM"，是"重构工具栈让 LLM 能工作"。同样的精力花在"换问法"上比"换模型"上 ROI 高得多。
2. **"Tokenize before AI touches it"是 LLM 时代的元工作流** —— 不只 3D 项目，**任何 LLM 工作**（读代码、写代码、debug、研究论文）都先 tokenize 再让 LLM 深入。这是和 LLM 协作的核心 mental model。
3. **Core vs Adapter 分层 + "AI 只写 Core" 硬约束** —— 这是 LLM 时代软件架构的标准答案。**任何新设计的子系统，问自己："AI 该被允许碰哪些层？"**
4. **GUI-first → token-first 是工具栈演化的方向感** —— Epic、Unity、自研引擎都在向 token-first 演化。**作为引擎程序员，识别这条趋势是 3-5 年技术选型的关键**。
5. **"70% prototype from one prompt"重新定义了 productivity 下限** —— 不再是"AI 能写多少代码"，而是"AI 一次性产出多少可玩游戏内容"。**这是衡量 AI 时代生产力的新 metric**。

---

## 面试谈资准备

**30 秒版（"知道这篇 + 能说清贡献"）：**

> GDC 2026 光子工作室 Hao Yang 的 talk，AI-Driven 3D Game Prototyping。**核心贡献是把"3D 引擎不支持 AI prototyping" 的原因从"LLM 不够强" 重新定位到"工具栈是为人类 GUI 设计的，AI 看不见像素"**——问题换一种问法就解了。给的是 **C.A.T 三原则**：**C**ode Reuse（TypeScript 共享 Web / Engine，Puerts 桥）、**A**dapter Design（Core vs Adapter 分层，AI 只写 Core）、**T**oken-Friendly（**最 critical**：把 3D 场景 tokenize 成 bounding box / marker / domain rule）。三场 demo 验证——**单 prompt 40 分钟产出 RPG 原型 70% 内容**，重新定义了 AI 时代 prototyping 的 productivity baseline。**对读项目代码的直接启发**：先把项目 tokenize 再让 LLM 深入，节省 30-50% context。

**2 分钟版（"追问实现细节"）：**

> 我把它拆两块讲——**第一，问题 framing**。AI 已经能 ship Web 2D 游戏，但 3D 引擎不行。常见误判是"LLM 不够强"，讲者的判断是"3D 工具栈是为人类 GUI 设计的——渲染层跨引擎不标准、几十年 GUI 工具面向艺术家、物理光照全是'非文本表面'、每个工作室代码库是定制雪花"。**问题不在智力，在工具栈**——这是 O'Reilly 教科书级的 framing，把锅从"训更强模型"挪到"重构工具栈"。
>
> **第二，C.A.T 解药**。**C**ode Reuse——TypeScript 共享 Web / Engine 两份 runtime，通过 Tencent 开源 **Puerts** 桥调用引擎 API，UI 通过 Unreal Web Browser widget 渲染，pixel-perfect 一致。**A**dapter Design——游戏逻辑抽成 **Core**，平台（Web / Unreal）写自己的 **Adapter**，**AI 只被允许碰 Core**——硬约束。**T**oken-Friendly（**最 critical**）——三条战术：(1) 注入 **domain rules**（标准台球桌尺寸 / 物理常量，AI 不能 Google 到的）；(2) 暴露 **asset metadata**（bounding box / collider / tag 当文本）；(3) **Designer markers**（命名锚点，AI 当 token 读）。**这三步把 3D GUI 操作转译成"程序员 console 命令" 那种工作方式**——AI 操纵 3D 世界的**文本投影**，不是 3D 原语。
>
> **第三，demo 验证**。8-Ball Pool 100% 功能（确定性沙盒），Top-down RPG **单 prompt 40 分钟产出 70% 内容**（一次性产出的天花板），Action Combat 多 boss 机制大部分跑通。**核心数字不是某个 demo 的完成度，是"单 prompt → 70% RPG" 的 metric**——它重新定义了 AI 时代 prototyping 的下限。
>
> **对读项目代码的直接启发**：T 原则可以迁移到 LLM 辅助 code reading——**先写 1 页 tokenized project map**（一句话骨架 + domain rule + 关键模块 metadata + navigation marker），再让 LLM 沿 token 化骨架深入。比 raw codebase dump 节省 30-50% context。A 原则可以迁移到 subsystem boundary 划分——识别 Core（业务逻辑）vs Adapter（平台适配），画语义地图。

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] 已复用工作流 → 待做：[tokenize project before LLM reading](#) 元工作流模板
- [ ] 已写博客 → 暂不写
- [ ] 已分享/交流 → 可在 [[Routine/AI-Tasks/Lumen/00-Master-Index]] 周会同步 "Core vs Adapter 子系统分解" 主题

---

*Create date: 2026-06-25*
*Last modified: 2026-06-25*