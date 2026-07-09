---
tags: [paper/signed, paper/GDC-talk, paper/GDC-2025, paper/neural-rendering, paper/已应用到工作, paper/AI-assets]
aliases: [AdvancesInRTX-NeuralRendering-GDC2025, NVIDIA-RTX-NeuralRendering-Roadmap-2025]
---

# NVIDIA — Advances in RTX: Neural Rendering (GDC 2025)

| 字段 | 内容 |
|------|------|
| **Talk 标题** | Advances in RTX: Neural Rendering |
| **讲者** | John Spitzer (NVIDIA VP Dev & Perf Tech) / Martin Stich (NVIDIA Director of Engineering) / Aaron Lefohn (NVIDIA VP Graphics Research) |
| **场次** | GDC 2025 — NVIDIA Information Booth C1819 session |
| **日期** | 2025-03-19 (Moscone Center, San Francisco) |
| **Track** | Graphics / Real-Time Rendering |
| **同源 short note** | `GDC/Minimax/2025/2025-NVIDIA-AdvancesInRTX-NeuralRendering.md` (cron curator 精简版，本文是其深度展开) |
| **阅读日期** | 2026-07-07 |
| **精读时长** | ~45 min |

---

## 一句话总结

> 这篇 talk 给出了**整个 NVIDIA RTX 未来 5-10 年的渲染技术大方向 ——"神经渲染 (Neural Rendering)"作为新范式**：以 Blackwell GPU + DirectX Cooperative Vectors 为基础，把**实时路径追踪 + 神经辐射缓存 (Neural Radiance Cache) + Mega Geometry (100× triangles) + RTX Hair (LSS 原语) + DLSS 4 多帧生成** 全部串成一条"every pixel touched by AI"的渲染流水线，配套工具链覆盖 RTX Kit / NvRTX / RTX Remix；本质上**重定义了"实时图形学"——从 ray tracing 改名到 neural rendering**。

---

## 核心创新点

1. **正名：把"ray tracing era"换成"neural rendering era"**。讲者给出的核心命题 **"every pixel of a future game will be touched by AI"**——不是加成，是替换。Neural rendering = compute + AI prediction，**用学习的近似替代完整的实时计算**。这是 NVIDIA 把"硬件光追"叙事升级到"硬件 + 神经网络"的临界点——判断未来 3-5 年图形学技术雷达的元命题。

2. **Zorah demo 一站式展示 RTX Kit 全家桶**。同一 demo 内**首次同时启用路径追踪 + 神经辐射缓存 + Mega Geometry (100× triangles) + RTX Hair (sub-strand hair)**——**关键不是单项性能数据，是这些技术**首次**在同一帧内协同工作**。Zorah 不是某个新算法的 demo，是 **"neural rendering 工作流长什么样"的可视化原型**。这是判断 UE5 NvRTX 分支未来能力上限的基线。

3. **Cooperative Vectors — DirectX 把神经网络做进 shader pipeline 的标准化 API**。DirectX 预览版（April 2025）加入 **Cooperative Vectors**——**GPU scheduler 同一帧调度 vector + tensor 运算**。这是 NVIDIA + Microsoft 联手的跨厂商标准：**任何 DirectX 12 GPU 都能跑 neural shading，AMD / Intel 跟进相同 API**。**对 engine dev 关键**：未来 shader 不再是纯算着色，**会混合 vector (传统数学) + tensor (小 NN forward) 两种运算类型**——shader 工具/编译/优化器都需要新增 tensor pass。

4. **DLSS 4 跨厂商落地，100+ 游戏首发**。**DLSS 4 Multi Frame Generation 在 100+ 游戏首发**（GDC 2025 时点），覆盖 God of War Ragnarok / Alan Wake 2 / Diablo IV / THE FINALS / 影之刃零 / 失落之魂 / 湮灭之潮 等。**关键数字**：**画质提升 + 帧生成**首次成为工业标准 pattern 而不是 NVIDIA-only trick。

5. **RTX Mega Geometry —— 100× triangle 密度，开世界几何爆炸首次有解**。Zorah 内 100× 当前标准的 triangle 密度，open world **billions of triangles** 而不是 millions。**与 Nanite 是同源问题（远超引擎预算的几何密度）的 NVIDIA 解**——Nanite 用 virtualized geometry + cluster streaming，Mega Geometry 用 AI-driven geometry processing pipeline。两个解法在 open world AAA 场景上是竞争关系。

6. **RTX Hair + LSS (Linear-Swept Spheres) —— 头发/毛发 sub-strand 渲染首次实时**。**LSS 是新的 GPU 原语**——一条 strand 一个 LSS primitive，硬件加速 on RTX 50 series。**与 UE5 的 Hair Cards / Strands 体系并行**：UE 5.6+ 已有 groom asset + Niagara hair，但 NVIDIA LSS 走的是"sub-strand 精度"的另一条路线。**两个头发体系谁能胜出是未来 2-3 年观察点**。

7. **RTX Remix + Half-Life 2 RTX —— AI 增强的经典 remaster 蓝本**。2025-03-18 RTX Remix + HL2 RTX 在 Steam 免费 demo。**关键 pattern**：用 neural rendering **重制老 IP**而不是从零开发。**对 engine dev 的可借鉴性**：给已有 10-20 年老游戏加 neural shading + path tracing + AI denoising 的工具链路径，是 NVIDIA 给出的"AI remaster SDK"模板。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按 day-job "LLM-driven UE on Mac" 视角）：**

1. **"Every pixel touched by AI" 是 Lumen / Nanite / VSM 的下一篇章**。Lumen 是 surface cache + indirect lighting、Nanite 是 virtualized geometry、VSM 是 virtual shadow map——三条都还在"光追 + 缓存"的旧范式。**NVIDIA 给出的下个范式方向是"光追 + 神经网络的近实时近似"**。**对 LLM RAG 索引**：未来 LLM 需要回答"UE5 Lumen 和 RTX Neural Rendering 的关系"这个问题——本文给的 answer 是"**Lumen 是 surface cache 范式的当前 SOTA，neural rendering 是 NVIDIA 押的下个范式；引擎程序员跟踪 NvRTX 演进 + Cooperative Vectors 落地进度**"。

2. **Mega Geometry vs Nanite 是 day-job 一个清晰的"竞争技术对照表"**。两个解法都解决"open world 几何密度爆炸"——**Nanite 是软件路线（cluster streaming + cluster LOD）+ 引擎 deep integration**，**Mega Geometry 是 AI 路线 + 硬件加速**。**LLM RAG 可给 LLM 准备**：问"我有一个 1km² 城市 open world、有 50 亿三角形需求，选 Nanite 还是等 NVIDIA Mega Geometry？"——答"等不到 Mega Geometry 就 Nanite，能在 NvRTX 跑就 Mega Geometry"。

3. **Cooperative Vectors 是 Mac 平台 day-job 的关键技术雷达项**。UE5 在 Windows / Linux 用 DirectX / Vulkan，**在 Mac 上走 Metal**——**Cooperative Vectors 是否会被 Metal 跟进**是 Mac 平台 day-job 工程挑战的关键。**跟踪项**：(a) Metal 3 是否在 2026-2027 加入 tensor ops in shader 的等价 API；(b) UE5 Metal RHI 是否实现 Cooperative Vectors 适配；(c) Mac M3/M4 GPU 的 neural engine 是否向 shader 暴露 tensor ops。

4. **DLSS 4 Multi Frame Generation 在 100+ 游戏首发——**对 day-job LLM 训练**来说是高质量语料**：已经被工业验证的 pattern，每个 shipping 案例都是"AI inference + frame interpolation"的范例。**训练数据角度**：可以从 100+ DLSS-4 shipping 游戏中提取 frame timing + upscaling quality 数据，让 LLM 学到"哪些场景适合 MFG、哪些适合 single frame upscaling"的判断。

5. **"Every pixel touched by AI"是 day-job 雷达的元命题**。整个 vault 的 P0 雷达要把这条作为长期方向感跟踪。**对 engine dev**：未来 3 年的引擎演进判断都需要挂在"是否往 neural rendering 演化"这个轴上评估——比如 UE5.7 / UE5.8 的新渲染特性，本质上是不是在往 neural rendering 收敛？

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|-------------|
| **Neural Radiance Cache 的 per-scene training** | NRC 需要 per-scene 训练，不跨场景迁移；训练成本 + 工程链路是主要瓶颈 | 是——和 UE Lumen 的 surface cache 范式互为对照，跟进 NvRTX + UE NvRTX branch |
| **Mega Geometry 的 dynamic geometry 处理** | 100× triangles 对静态几何 OK，**dynamic / skeletal mesh 的成本未明**；day-job 做 skeletal animation 时会遇到 | 是——open world 项目必踩的坑 |
| **Cooperative Vectors 的 shader 集成** | shader 编译需要新增 tensor pass；HLSLcc / DXC / SPIRV-Cross 都要跟进 | 部分——Mac Metal 路径单独评估 |
| **DLSS 4 MFG 的低帧基线 artifact** | 已报道 MFG 在 <30fps 基线下明显 artifact；和目标帧率强相关 | 否——属于产品配置决策，工程上 QA 即可 |
| **RTX Hair LSS 的 UE5 integration** | UE 已有 groom asset + hair strands；**LSS 是否集成进 UE5 mainline / 仅 NvRTX 分支**是观察点 | 是——UE5.x release note 跟踪 |
| **RTX 30 系跑不全 Zorah** | 全 RTX Kit 需要 RTX 50 系列；RTX 30 系用户跑不动——低端硬件未来 3 年的 mobile gaming 演化路径会被这部分限制 | 否——属于硬件 outlook，不在个人工程范围内 |

---

## 是否值得复现？

- [ ] 是 — 已列入待办
- [x] **否** — 仅了解思路即可
- [ ] 部分 — 只复现核心算法

**不复现的原因：**
- 这篇 talk 主要是"路线图 + 工具链可用性"——不是单一可独立复现的算法。Mega Geometry / NRC / Cooperative Vectors 都在 NvRTX 分支直接可用，不需要个人复现。
- **可借鉴的不是"算法"，是"如何识别神经渲染时代的工程决策框架"**——这套框架作为技术雷达条目跟踪，不需要写代码。

**借鉴的具体步骤：**
1. 把"Every pixel touched by AI"作为 [[05-技术雷达]] P0 条目长期跟踪
2. 跟进 NvRTX release note —— 每季度评估哪些 Cooperative Vectors / NRC 增强能进 day-job 项目
3. Mac 平台独立跟踪线 —— Apple 是否跟 Metal 等价 API（**这是 day-job 工程路线图的最大变量**）

---

## 关键术语表

| 术语 | 解释 | 我理解的锚点 |
|------|------|-------------|
| **Neural rendering** | compute + AI prediction 替代完整实时计算 | 范式级别的新概念，覆盖 ray tracing 全栈 |
| **Cooperative Vectors** | DirectX 12 新 API，shader 内 vector + tensor ops 同时调度 | 神经 shading 跨厂商标准化的关键抽象 |
| **RTX Mega Geometry** | AI-driven geometry processing，100× triangle count | 与 Nanite 同源问题（open world 几何爆炸）的 NVIDIA 解 |
| **RTX Hair (LSS)** | Linear-Swept Spheres 原语；sub-strand hair 实时 | 与 UE groom asset 并行的另一条头发路线 |
| **NRC (Neural Radiance Cache)** | 神经辐射缓存；per-scene 训练的间接光照近似 | Lumen surface cache 的 NVIDIA 等价物 |
| **DLSS 4 MFG (Multi Frame Generation)** | 跨多帧的 AI 帧生成；100+ 游戏首发 | NVIDIA 光追 + AI 的产品化代表 |
| **Zorah demo** | GDC 2025 演示场景，全 RTX Kit 协同 | "neural rendering 工作流长什么样"的可视化原型 |
| **RTX Kit** | NVIDIA 神经渲染工具集（mega geometry / hair / skin / NRC / dlss / remix） | UE5 NvRTX 分支对应的工具集 |

---

## 整体架构图 / 流程（伪代码）

```
# NVIDIA Neural Rendering 时代的渲染管线（Zorah demo）

# ===== Frame setup =====
Frame = SetupFrame()
    # 几何：Mega Geometry AI 驱动，100× triangles
    GeometryCluster = MegaGeometry.Stream(WorldGeometry, budget=100x_normal)
    # 头发：LSS 原语
    HairAssets = LSS.Load(strands_count=200_000)
    # GI cache：NRC（per-scene 训练好的）
    RadianceCache = NRC.Load(scene_id=CurrentScene)

# ===== Per-pixel pipeline =====
for each Pixel in Screen:
    # 光追：path tracing with neural denoising
    RawRadiance = PathTrace(Pixel, GeometryCluster, depth=8)
    # NRC 间接光补全
    IndirectRadiance = NRC.Query(Pixel.position, Pixel.normal)
    # DLSS 4 MFG 帧生成
    FinalRadiance = DLSS4_MFG.combine(
        current=RawRadiance + IndirectRadiance,
        prev_frame=PrevFrame,
        motion_vectors=Pixel.motion
    )
    # Hair LSS 单独处理
    HairContribution = LSS.Render(Pixel, HairAssets)

    FinalPixel = FinalRadiance + HairContribution

# ===== Neural shading（Cooperative Vectors — DirectX 12）=====
@shader_entry("neural_brdf")
def NeuralBRDF(normal, view, roughness):
    # shader 内嵌一个小 NN forward
    # tensor ops 走 Cooperative Vector API
    # vector ops 走传统 HLSL 数学
    nn_input = concat(normal, view, roughness)
    brdf = CooperativeVector.MatMul(W1, nn_input) + b1
    brdf = CooperativeVector.MatMul(W2, ReLU(brdf)) + b2
    return Sigmoid(brdf)  # bounded BRDF output
```

---

## 相关论文/前置知识

- [[2026-Tencent-MagicDawn-AIGlobalIllumination]] (GDC/Minimax/2026) — Tencent (魔方) MagicDawn AI GI，和 NRC 是同代竞品；同源问题（间接光照的神经化近似）的不同 vendor 解
- [[2025-NVIDIA-RTXKit-UE5]] (GDC/Minimax/2025) — 本文姊妹 talk，Nvidia 把 Mega Geometry + Hair 直接做到 UE5 NvRTX 分支；具体落地的工程细节
- [[2025-NVIDIA-NeuralShading-DirectX]] (GDC/Minimax/2025) — 本文姊妹 talk，Cooperative Vectors 这条 shader pipeline 内 tensor 路径的标准化详情
- `Routine/02-引擎源码分析库/` — 跟进 UE 5.6/5.7 mainline Lumen / Nanite / VSM 的源码演进，对照 NvRTX branch 的实现差异
- [[05-技术雷达]] — 把"Every pixel touched by AI + Cooperative Vectors 跨厂商标准化"作为 P0 长期方向感跟踪

---

## 输出 / 借鉴（forward — 启发到的工程实践）

- **[[05-技术雷达]] P0 加一行** —— "Neural rendering: Mega Geometry / NRC / Cooperative Vectors"，明确"future UE rendering stack 会逐步向 NvRTX 对齐"作为 day-job 长期方向感。**状态**：立刻补到 05-技术雷达 P0 列表
- **Lumen / Nanite / VSM 三特性 vault 的"下一代"层** —— 在 [[Routine/02-引擎源码分析库/Lumen]] / Nanite / VSM 各笔记下加一个"Next-gen: NVIDIA neural rendering"模块，记录 NvRTX branch 的同步状态。**状态**：下周开始补
- **Mac 平台 day-job 风险评估** —— 把"Apple 是否跟进 Cooperative Vectors 等价 API"作为 Mac Game Harness 的关键技术风险项。**状态**：列入 [[Routine/AI-Tasks/Mac/00-Master-Index]]（待新建）

---

## 个人评价

**优点：**
- **范式级别正名** —— "neural rendering"作为命名把整个行业未来 5-10 年的方向感钉死了。比 "ray tracing" 更宽、更准确，**给了整个 graphics community 一个 common north star**
- **工具链齐整** —— NvRTX / RTX Kit / RTX Remix / DLSS 4 + DirectX Cooperative Vectors + Mega Geometry + Hair 全套同时到位，不是 PPT 愿景，是 production-grade 工具链
- **跨厂商策略** —— Cooperative Vectors 是 NVIDIA + Microsoft 联手推的开放 API；**主动放弃 NVIDIA 独享优势换行业标准**——这是高段位战略
- **Demo 选取精当** —— Zorah 不是炫技场景，是**实时神经渲染工作流的最小可用范例**，所有 talk 主张都能在 Zorah 一帧内看到

**局限性：**
- **没说 per-scene NRC training 的成本** —— "per-scene 训练"意味着每个 open world 场景都要 train 一遍；成本 / 工程链路都没量化。和 Lumen surface cache 的"无训练 zero-cost"比是 trade-off
- **RTX 30 系跑不全 Zorah** —— 跨硬件代际的能力落差；老硬件用户被抛下
- **Mega Geometry 对 dynamic / skeletal mesh 的性能数据缺失** —— 演示的是静态 / cinematic 场景；dynamic 物体（角色 / 物理对象）的成本未公开
- **没给 "neural shading 写错"的兜底** —— Cooperative Vectors 的 NN 可以写错 / 训练不足；debug / validation 工具未提及
- **没谈 mobile / console 适配** —— Zorah demo 是 PC 上 RTX 50 系列 + 4K + path tracing；**移动端 / 主机端的神经渲染路径完全未触及**

**启发：**
1. **"神经渲染"作为新范式名**值得在自己的笔记体系内沿用 —— 不只跟踪 Lumen / Nanite / VSM 这些旧范式 SOTA，还要跟踪"是否往 NvRTX / Cooperative Vectors 对齐"作为长期方向感
2. **Cooperative Vectors 的跨厂商标准化**是 GPU API 演化的方向感 —— 长期看，shader 内 tensor ops 会成为标配；Mac Metal 是否跟进是 day-job Mac 平台的最大变量
3. **Mega Geometry vs Nanite 是观察"同一问题两种解法演化"的范例** —— 5 年后回看，两条路线谁赢 / 合并 / 分化都是 tech radar 必追踪项
4. **AI remaster（RTX Remix + HL2 RTX）是 low-cost 高 ROI 的工程模板** —— 给老 IP 加神经渲染重新上架，比从零开发便宜得多；这个 pattern 值得在 day-job 提示给产品团队
5. **"Every pixel touched by AI" 是 day-job LLM RAG 的方向感锚点** —— 未来给 LLM 训练数据时，凡是涉及 UE 渲染的 Q&A 都应该挂这条主轴，避免 LLM 学到"光追时代"的旧答案

---

## 面试谈资准备

**30 秒版（"知道这篇 + 能说清贡献"）：**

> GDC 2025 NVIDIA 的 **Advances in RTX: Neural Rendering**，Spitzer / Stich / Lefohn 三位 NVIDIA VP 给路线图。**核心贡献是把"神经渲染"正名为整个行业的下个范式** —— 替代 ray tracing 作为未来 5-10 年的 north star。给出五大组件：**Mega Geometry (100× triangles，对标 Nanite)、RTX Hair (LSS 原语)、NRC (神经辐射缓存，对标 Lumen)、Cooperative Vectors (DirectX 跨厂商 API，把 NN 做进 shader)、DLSS 4 MFG (100+ 游戏首发)**，并用 Zorah demo 一站式 showcase。**对 day-job 启发**：把 Cooperative Vectors 是否被 Metal 跟进的跟踪作为 Mac 平台关键技术风险。

**2 分钟版（"追问实现细节"）：**

> 第一，**范式正名**。讲者开局就抛 **"every pixel of a future game will be touched by AI"** —— 不是 ray tracing 的延伸，是替代。**Neural rendering = compute + AI prediction**，用学习的近似替代完整实时计算。这是 NVIDIA 把行业叙事从"硬件光追"升级到"硬件 + 神经网络"的临界点。

> 第二，**Zorah demo —— 五大组件一站式协同**。同一帧内：(1) **Mega Geometry** AI 驱动的 geometry processing，同场景 100× triangles，对标 Nanite 的同源问题但路线不同（Nvidia AI 路线 vs Unreal 软件路线）；(2) **RTX Hair + LSS** —— 新 GPU 原语 Linear-Swept Spheres，sub-strand hair 首次实时；(3) **NRC (Neural Radiance Cache)** —— per-scene 训练的间接光照近似，对标 Lumen surface cache；(4) **Cooperative Vectors** —— DirectX 12 shader pipeline 内的跨厂商 NN 标准 API，**这是最重要的一条**：AMD / Intel 用户通过同一 API 享受神经 shading，**active 放弃 NVIDIA 独享优势换行业标准**；(5) **DLSS 4 Multi Frame Generation** —— 100+ games 首发，已是产品化 pattern。

> 第三，**对 day-job 的直接启发**。**Lumen / Nanite / VSM 是 surface-cache + virtualized-geometry + virtual-shadow 旧范式 SOTA**，**NVIDIA 的下个范式方向是"光追 + 神经网络近实时近似"** —— vault 三特性的"下一代"层需要跟踪 NvRTX 演进。**Mac 平台**是 day-job 最大变量：Cooperative Vectors 是否被 Metal 等价跟进、Apple M-series GPU 是否暴露 tensor ops 给 shader，是 Mac Game Harness 工程路线图的关键决策点。LLM 训练数据凡是涉及 UE 渲染的 Q&A 都应挂在"Every pixel touched by AI"这条主轴上，避免学到"光追时代"的旧答案。

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] 已补到 [[05-技术雷达]] P0 列表 → 下周加
- [ ] 已补到 Lumen / Nanite / VSM 三特性的"Next-gen: NVIDIA neural rendering"模块 → 下周开始
- [ ] Mac 平台 Cooperative Vectors 风险评估 → 待建 [[Routine/AI-Tasks/Mac/00-Master-Index]]

---

*Create date: 2026-07-07*
*Last modified: 2026-07-07*
