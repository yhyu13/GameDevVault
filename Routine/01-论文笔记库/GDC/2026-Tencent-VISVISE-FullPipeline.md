---
tags: [paper/signed, paper/GDC-talk, paper/GDC-2026, paper/AI-pipeline, paper/AI-assets, paper/已应用到工作]
aliases: [Tencent-VISVISE-GDC2026, MotionGen-MeshgenO-AutoRigging-GDC2026]
---

# Tencent — VISVISE: Full AIGC Game-Art Pipeline (GDC 2026)

| 字段 | 内容 |
|------|------|
| **Talk 标题** | VISVISE: Full AIGC Game-Art Pipeline — text-to-animation, video-to-motion, MIB, Meshgen-O, auto-rigging |
| **讲者** | 葛诚 (Tencent Games AIGC Product Director) + VISVISE team |
| **场次** | GDC 2026 — Tencent booth theatre + dedicated session |
| **日期** | 2026-03 |
| **Track** | AI Summit / Production Pipeline |
| **同源 short note** | `GDC/Minimax/2026/2026-Tencent-VISVISE-FullPipeline.md` (cron curator 精简版，本文是其深度展开) |
| **阅读日期** | 2026-07-07 |
| **精读时长** | ~50 min |

---

## 一句话总结

> 这篇 talk 给出 **Tencent VISVISE —— 已部署在 90+ shipping games（《和平精英》《PUBG Mobile》+ 88 款）的 full-lifecycle AIGC 游戏美术管线** —— 包括 **text-to-animation（MotionGen 100B 参数，300+ 动作类别）/ video-to-motion（无 mocap 工作室也能用）/ MIB 关键帧 AI 补帧（10 秒产出）/ Meshgen-O（image / text-to-engine-ready quad mesh + 6 LOD）/ auto-rigging（80% 自动化绑定 + 蒙皮）** —— 设计哲学核心是 **"engine-ready output"**：**quad-dominant topology + LOD + 部件分离，drop-in Unreal / Unity 不需要重做**；**对 day-job 启发** —— **"engine-ready" 是 LLM 工具设计的关键产品决策**：不优化视觉 fidelity，**优化"是否能 drop-in 到真实 production 项目"**，**这是和 [[2026-Tencent-HaoYang-AIDrivenPrototype]] 的 C.A.T 框架互补的"输出工程"维度**。

---

## 核心创新点

1. **MotionGen —— 10B 参数 multimodal text-to-animation 模型**。**输入 natural-language action description（"character climbs, waves forward, dances"）**，**输出 3D animation clip + 300+ action categories + 3D-coherent**。**关键 engineering choice**：production-grade，**artist types prompt + gets back clip + edits keyframes** —— 不是 demo-only，是 artist 在 timeline 工具里直接用的 pipeline。

2. **Video-to-motion —— 无 mocap 工作室也能用的"动捕"**。**输入 any reference video（YouTube 上的 taekwondo kick 录像等）**，**输出 retargeted + engine-ready 3D 动画**。**Pipeline**：human-pose estimation → trajectory tracking → skeleton mapping → standardised BVH / FBX。**解决 "we don't have a mocap studio" 问题** —— 独立小团队 / indie studio 能直接用。

3. **MIB (Motion In-Betweening) —— 关键帧 AI 补帧**。**输入 3-5 keyframes**，**输出 full animation sequence in ~10s**。**解决"动画师画 extremes 但不想 tween"瓶颈**。**关键量化**：内部 benchmark 显示质量对标光 mocap。**和 text-to-animation 互补**：MIB 让 animator 保留创作意图（只画关键 frame），AI 接管中间 frames。

4. **Meshgen-O —— image / text-to-engine-ready 3D mesh**。**关键设计选择是"engine-ready output"，不是"visual fidelity"**。**具体输出 spec**：
   - **quad-dominant topology**（不是 triangle soup）
   - **up to 6 LODs** 自动生成
   - **部件分离**（character 拆 body / head / accessories）
   - **drop-in Unreal / Unity 不需要重做**
   
   **这是 vs 学术 / startup 工具的核心差异**：90% 学术 3D generation 模型输出"sealed visual husk" —— 看着像但拓扑 / LOD 都不可用。**Meshgen-O 把这两个 non-negotiables 当作 first-class 输出**。

5. **Auto-rigging + skinning —— 80% 自动化**。**300+ action categories 同 vocabulary** 复用。**Defect rate（sliding feet / jitter）<10%**。**关键数据点**：**"5-8 person 团队能做任何 30-50 艺术家的工作"**——讲者给出的 productivity 倍数。

6. **Decision-AI vs Generative-AI 同一平台**。**继承 [[2024-Tencent-GiiNEX-Launch]] GiiNEX 引擎的双轮驱动**：**决策 AI（NPC / bot / player modeling）+ 生成 AI（asset / animation / texture）两条 pipeline 同平台**。**90+ shipping games 是 quantized production evidence** —— 不是 demo 不是 pilot，是已经在生产管线里跑的。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按 day-job "LLM-driven UE on Mac" 视角）：**

1. **"Engine-ready output" 是 LLM 工具设计的产品决策核心**。**LLM RAG / agent training pipeline 的工具设计应学习这条**：不在 demo 上炫耀 fidelity，**优化"是否能 drop-in 到真实 production 项目"**。**这是 day-job 设计 LLM 工具的元命题** —— 给 LLM 的工具（function calls / MCP / skills）应该设计成"engine-ready"：清晰的 input schema、明确的 output contract、不需要的 intermediate state in tool。**这是 [[2026-Tencent-HaoYang-AIDrivenPrototype]] 的 C / A 原则在 LLM 工具维度的延伸**：Core 不要 Adapter 干扰。

2. **Meshgen-O 的拓扑 + LOD + 部件分离 spec 是 LLM-driven 3D 生成的产品决策模板**。**未来 day-job 给 LLM 调"生成 UE5 mesh" 工具时**，**工具的 output 应该 match Meshgen-O spec**：(a) quad-dominant topology；(b) multiple LODs；(c) part separation。**让 LLM 学到这些是 ground truth rules 而不是"任意 3D mesh"**。

3. **MotionGen + MIB + Auto-rigging 同 vocabulary 的设计** 是 day-job LLM 训练的高质量 ground truth。**LLM 学"动画 pipeline"时**，应学到这套完整 character-level animation pipeline 不只有"生成" 还有"补帧 + 蒙皮 + 绑定" —— **完整 lifecycle 才能 ship**。**对训练数据**：让 LLM 学会在解释 game animation AI 工具时**自动覆盖完整 pipeline 维度**，**不要只看 text-to-anim 单点**。

4. **80% automation vs 100% automation 的 trade-off** 是 day-job LLM agent 设计的关键决策。**讲者明示**：**80% 自动化 + 缺陷率 <10%** 比"100% automation 但缺陷率高"更 production-friendly。**LLM agent tool design 应学习**：允许 20% human-in-loop，**不要追求 100% autonomous**。**让 LLM 在 tool calling 时主动生成"需 human review 的检查点"**。

5. **90+ shipping games 是 LLM training 的最强说服力 ground truth**。**对 day-job LLM 训练**：让 LLM 学到"VISVISE 已经 production 在 90+ games 用了" 是直接可信的 production evidence —— **回答"AI 资产生成管线现在 production 化到什么程度" 时能给 grounded 答案**。

6. **decision-AI vs generative-AI 同平台** 是 LLM-driven game engine 的范例。**GiiNEX 同平台支撑两条 AI pipeline** 是**LLM-driven UE on Mac day-job 的直接对标**：Mac Game Harness 也应是"AI 决策 + AI 生成"同平台 —— **LLM agent decision + LLM asset generation 在同一 engine harness 上跑**，**不要分两个独立系统**。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|-------------|
| **LLM tool design 的"engine-ready output" 落地** | tool output contract 要清晰可 drop-in；目前 LLM 工具输出多在 demo level | **是**——day-job LLM 工具设计主命题 |
| **Quad-dominant topology + LOD 在 LLM 工具的 spec** | 给 LLM 的 3D generation tool 应该 enum 这些 output fields | **是**——直接影响 LLM training quality |
| **80% automation + 20% human review 在 LLM agent 的 checkpoint 设计** | LLM agent 应该自动生成"review point" 让 human 介入，**不是 100% autonomous** | **是**——LLM agent UX 设计 |
| **"90+ shipping games" 在 Mac 平台 day-job 可借鉴性** | Tencent 90+ games 是 Windows + 自研引擎 + 中国 studio 协同；day-job Mac 是 single-team 单平台 | 否——组织规模 / 平台异同 |
| **Auto-rigging 的缺陷率（<10%）** | sliding feet / jitter 在 production 中仍需 QC；**Mac day-job 是否容忍同样缺陷率** | 部分——产品配置决策 |
| **Action category 局限** | 主要覆盖 combat / locomotion；**subtle facial / multi-character / long-tail verb 较弱** | 否——属于产品定位 |
| **VISVISE 没有 public API** | 2026-03 as of partner-only；**无法直接接入 LLM toolchain** | 是——tracking public API 时间表 |

---

## 是否值得复现？

- [ ] 是 — 已列入待办
- [x] **否** — 仅了解思路即可
- [ ] 部分 — 只复现核心工作流

**不复现的原因：**
- VISVISE 是 Tencent partner-only 产品，没有 public API
- 个人无法独立复现 10B 参数 multimodal animation model
- 整体管线是 Tencent 量级的工程投入

**借鉴的具体步骤：**
1. **"Engine-ready output" 原则直接应用到 day-job LLM tool design** —— 给 LLM 的工具（function calls / MCP / skills）以"清晰 input schema + 明确 output contract + 不需要中间状态"为目标
2. **为 LLM 训练数据准备"3D mesh generation output spec" 模块** —— 包含 quad-dominant topology + multi-LOD + part separation 三条 ground truth
3. **"80% automation + 20% human review" 原则应用到 LLM agent UX** —— agent 自动生成 review checkpoint 让 human 介入

---

## 关键术语表

| 术语 | 解释 | 我理解的锚点 |
|------|------|-------------|
| **VISVISE** | Tencent AIGC 美术管线；涵盖动画 / rigging / 补帧 / 3D 生成 | 90+ shipping games production-deployed |
| **MotionGen** | 10B 参数 multimodal text-to-animation 模型 | 300+ action categories；artist-editable output |
| **MIB (Motion In-Betweening)** | 3-5 keyframes → full animation ~10s | 关键帧补帧；动画师保留创作意图 |
| **Meshgen-O** | image / text → engine-ready 3D mesh | **quad-dominant topology + 6 LODs + 部件分离** |
| **Engine-ready output** | output spec 对齐真实 production 需要；不是 visual fidelity | VISVISE 设计哲学核心 |
| **Quad-dominant topology** | mesh 主要四边形；不是 triangle soup | **传统引擎 import path friendly** |
| **Auto-rigging** | 自动 skeleton + skinning；80% automation | 与 text-to-anim 同 vocabulary（300+ action categories） |
| **Decision-AI vs Generative-AI** | GiiNEX 平台支撑两条 AI pipeline | LLM-driven game engine 的产品决策模板 |
| **C.A.T framework** | 同 [[2026-Tencent-HaoYang-AIDrivenPrototype]]；Core / Adapter / Token-friendly | VISVISE 的"engine-ready"是 C.A.T 的具体落实 |

---

## 整体架构图 / 流程（伪代码）

```
# VISVISE full AIGC pipeline（视角：artist in production）

# ===== Input: from artist =====
ArtistGoal = {
    character_description: "fantasy warrior with staff",
    action_prompt: "spinning strike with forward momentum",
    style_reference: Image("character_concept.png"),
    skeleton_target: UnrealSkeleton.LyraHumanoid,
}

# ===== Pipeline: VISVISE full lifecycle =====

# Phase 1: 3D Character (Meshgen-O)
Character3D = MeshgenO.Generate(
    prompt=ArtistGoal.character_description,
    reference_image=ArtistGoal.style_reference,
    output_spec={
        topology: "quad-dominant",
        lods: 6,
        part_separation: ["body", "head", "staff", "accessories"],
        target_engine: "Unreal",
        lod_quality_curve: "logarithmic"
    }
)
# Output: drop-in Unreal compatible mesh + auto-generated 6 LODs + 部件分块

# Phase 2: Auto-rigging + skinning
CharacterRigg = AutoRig.Generate(
    mesh=Character3D,
    skeleton_template=ArtistGoal.skeleton_target,  # Lyra humanoid
    vocabulary="visvise_300+",  # 与 text-to-anim 同 vocabulary
    coverage_target=0.80,  # 80% 自动化
    defect_tolerance=0.10  # sliding feet < 10%
)

# Phase 3: Animation (MotionGen + MIB)
Keyframes = ArtistAuthor("strike_extreme_1", "strike_extreme_2", "strike_extreme_3")
# MIB: keyframes → full animation
FullAnimation = MIB.Generate(
    keyframes=Keyframes,
    inbetweening_time_target=10.0  # seconds
)

# Phase 4 (alternative): Text-to-animation directly
DirectAnimation = MotionGen.Generate(
    action_prompt=ArtistGoal.action_prompt,
    edit_mode=True,  # artist can edit keyframes
    output_format="unreal_anim_clip"
)

# ===== Output: drop into Unreal =====
Unreal.AssetImport(
    mesh=Character3D,
    rig=CharacterRigg,
    animations=[FullAnimation, DirectAnimation]
)
# 在 UE5 中直接可见使用；不需要再手动 retopo / LOD / rig
```

---

## 相关论文/前置知识

- [[2026-Tencent-HaoYang-AIDrivenPrototype]] (GDC/Minimax/2026, Routine/01-论文笔记库) — 姊妹 talk；C.A.T 框架（Code reuse / Adapter / Token-friendly）讲 prototyping workflow，**本文 VISVISE 讲产出 engine-ready asset**；两篇互补 —— **C.A.T 是 input/processing 维度，VISVISE 是 output spec 维度**
- `GDC/Minimax/2024/2024-Tencent-GiiNEX-Launch.md` — GiiNEX 平台双轮驱动（Decision-AI + Generative-AI）的源头
- `GDC/Minimax/2025/2025-Meshy-3DAssetWorkflow.md` — Meshy AI 3D asset workflow；与 Meshgen-O 同赛道
- [[2025-NVIDIA-RTXKit-UE5]] (GDC/Minimax/2025, Routine/01-论文笔记库) — Mega Geometry 是 engine 端解放，**Meshgen-O 是 AI 端产出**；**两端共同让 "AI 生成的 dense mesh 能在 UE5 中被 hold 住"**
- [[05-技术雷达]] P0-立即学习：把 "VISVISE-style engine-ready output" 作为 day-job LLM tool design 的元原则

---

## 输出 / 借鉴（forward — 启发到的工程实践）

- **day-job LLM tool design 原则** —— 工具以"engine-ready output"为目标：清晰 input schema、明确 output contract、不需要 intermediate state。**状态**：作为 day-job LLM tool design guideline 立即应用
- **LLM 训练数据准备 —— "3D mesh generation output spec" 模块** —— 包含 quad-dominant topology + multi-LOD + part separation 三条 ground truth。**状态**：列入下周训练数据计划
- **LLM agent UX —— "80% automation + 20% human review"** —— agent 自动生成 review checkpoint 让 human 介入。**状态**：作为 day-job LLM agent design principle
- **Mac Game Harness 双轮驱动 reference** —— Mac harness 应当也是"AI decision + AI generation" 同平台。**状态**：列入 [[Routine/AI-Tasks/Mac/00-Master-Index]]（待新建）

---

## 个人评价

**优点：**
- **最-shipped AIGC 工具链** —— 90+ games 是行业最强的 production evidence，**这比任何单 demo 都更具说服力**
- **"Engine-ready output" 是 production-grade 关键设计选择** —— 把"是否能 drop-in Unreal" 当 first-class output spec，而不是 afterthought。**这是 vs 学术 / startup 工具的核心差异**
- **完整 lifecycle 覆盖** —— text-to-anim + video-to-motion + MIB + Meshgen + rigging + skinning 不是单点，是全 lifecycle。artist 真实工作流能完整闭包。
- **80% automation + 缺陷率 <10% 是 realistic 目标设定** —— 不追求 100% autonomous，留 human review 余地，**production-grade 务实做法**

**局限性：**
- **VISVISE partner-only**，public API 时间表未明；**day-job 无法直接接入** —— 但设计哲学可借鉴
- **action category 局限** —— combat / locomotion 强，facial / multi-character / long-tail verb 弱
- **80% 自动化范围有限** —— 主要 humanoid + common weapons + modular environments；stylized art（cartoon / painterly / anime）覆盖弱
- **没公开 decision-AI 在 90+ games 的具体数据** —— generative-AI 部分讲透了，decision-AI 部分较薄
- **没说 AI 资产版权 / ownership** —— 90+ games 用 VISVISE 生成的资产版权属于谁？studio / artist / Tencent / shared？**生产管线长期问题**

**启发：**
1. **"Engine-ready output" 是 LLM 工具设计的元命题** —— 不优化 demo fidelity，**优化"是否能 drop-in production"**。这条原则跨领域适用，所有 AI-driven tools 都该走这条
2. **完整 lifecycle 设计** —— 不做单点（text-to-anim 或 text-to-3D single tool），**做 full pipeline**。**对 LLM 工具设计的启示**：单个 MCP tool 不能解决完整 workflow，**要用 multi-tool pipeline**
3. **80% automation + 20% human review** —— LLM agent 不应 100% autonomous，**reviewable checkpoint 是 production-friendly pattern**
4. **Production evidence > academic benchmarks** —— 90+ shipping games 是最强 ground truth，**LLM 训练 "AI 资产生成实际可用性" 时应优先 production-deployed evidence**
5. **Mac Game Harness 双轮驱动** —— day-job Mac harness 应 match GiiNEX 的"decision-AI + generative-AI 同平台"设计

---

## 面试谈资准备

**30 秒版（"知道这篇 + 能说清贡献"）：**

> GDC 2026 腾讯葛诚的 talk，**VISVISE —— full AIGC game-art pipeline**。**核心贡献是把 AIGC 工具做到了 production-deployed**：**90+ shipping games**（《和平精英》《PUBG Mobile》+ 88 款）。涵盖 **text-to-anim (MotionGen, 100B params, 300+ action) / video-to-motion / MIB 关键帧补帧 / Meshgen-O engine-ready quad topology + 6 LOD + 部件分离 / auto-rigging 80% 自动化**。**最关键的 design choice 是 "engine-ready output"——不优化 visual fidelity，**优化"是否能 drop-in Unreal 不需要重做"**。**对 day-job 启发**：**LLM tool design 应学这条"engine-ready" 原则**。

**2 分钟版（"追问实现细节"）：**

> 第一，**问题 framing**。2024-2026 之间 AI 资产生成工具很多（Meshy / Rodin / Tripo / Meshy AI / Tencent MeshGen 等），**90% 是"看着像但 topological soup"**——视觉 fidelity 高但 topology 不可用、LOD 必须手工重做、rigging 必须手工重做。**industry gap 不是"AI 能不能生成"，是"AI 生成能不能直接进 production"**。

> 第二，**VISVISE 的解药 —— "engine-ready output" 作为 first-class spec**。四个 component：
> - **Meshgen-O**：image / text → mesh，**quad-dominant topology + 6 LODs + 部件分离**。**关键**：output spec 是引擎 import path friendly，**不是 visual fidelity max**
> - **MotionGen**：10B 参数 multimodal text-to-animation，**300+ action categories**，artist-editable（可改 keyframes）
> - **MIB**：3-5 keyframes → full animation in ~10s
> - **Auto-rigging + skinning**：80% automation，sliding feet / jitter < 10%
>
> 配合 **video-to-motion**（无 mocap studio 也能用）和 **decision-AI**（继承自 GiiNEX），构成 full lifecycle。

> 第三，**关键 design choice**：**"engine-ready output"**。**不优化 demo fidelity，优化"是否能 drop-in Unreal 不需要重做"**。**这是和 [[2026-Tencent-HaoYang-AIDrivenPrototype]] 的 C.A.T 互补**：C.A.T 讲 prototyping workflow 的 input / processing 维度，**VISVISE 讲 output spec 维度**。**两者共同 = "engine-ready 工作流的 full lifecycle"**。

> 第四，**量化收益**。**"5-8 person 团队能做任何 30-50 艺术家的工作"**——这是 Tencent 公开的 productivity 倍数。**90+ shipping games 是 production evidence**——这是行业最强的 deployment success metric。

> 第五，**对 day-job 直接启发**。**(a)** **LLM tool design 元命题**：给 LLM 的工具（function calls / MCP / skills）应以"engine-ready output"为目标——清晰 input schema、明确 output contract、不需要 intermediate state。**(b)** **80% automation + 20% human review**：LLM agent 不追求 100% autonomous，应自动生成 review checkpoint 让 human 介入。**(c)** **Mac Game Harness 双轮驱动**：day-job Mac harness 应 match GiiNEX 的"AI decision + AI generation 同平台"设计。**(d)** **LLM 训练数据**：让 LLM 学到"3D mesh generation output spec" = quad-dominant topology + multi-LOD + part separation 三条 ground truth；**让 LLM 在解释 game animation AI 时覆盖完整 lifecycle 维度**（不只 text-to-anim 单点）。

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] LLM tool design guideline "engine-ready output" 写为 day-job 内部规范 → 本周完成
- [ ] LLM 训练数据 "3D mesh output spec" 模块 → 列入下周计划
- [ ] Mac Game Harness 双轮驱动 reference → 列入 [[Routine/AI-Tasks/Mac/00-Master-Index]]（待新建）

---

*Create date: 2026-07-07*
*Last modified: 2026-07-07*
