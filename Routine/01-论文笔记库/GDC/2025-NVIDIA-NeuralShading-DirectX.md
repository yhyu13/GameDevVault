---
tags: [paper/signed, paper/GDC-talk, paper/GDC-2025, paper/neural-rendering, paper/待复现, paper/已应用到工作]
aliases: [NeuralShading-CooperativeVectors-GDC2025, DirectX-Cooperative-Vectors-GDC2025]
---

# NVIDIA + Microsoft — Neural Shading in DirectX (Cooperative Vectors) (GDC 2025)

| 字段 | 内容 |
|------|------|
| **Talk 标题** | Neural Shading in DirectX — Cooperative Vectors |
| **讲者** | John Spitzer (NVIDIA) / Shawn Hargreaves (Microsoft Direct3D) / Andrew Burnes (NVIDIA) |
| **场次** | GDC 2025 — joint NVIDIA + Microsoft session |
| **日期** | 2025-03 |
| **Track** | Graphics / API Standard |
| **同源 short note** | `GDC/Minimax/2025/2025-NVIDIA-NeuralShading-DirectX.md` (cron curator 精简版，本文是其深度展开) |
| **阅读日期** | 2026-07-07 |
| **精读时长** | ~35 min |

---

## 一句话总结

> 这篇 talk 是 **GDC 2025 上 NVIDIA + Microsoft 联手官宣"神经 shading 跨厂商标准化"** —— **April 2025 DirectX preview 加入 Cooperative Vectors API**，让 **shader pipeline 同一帧内可以调度 vector + tensor 两种 ops**，**任何 DirectX 12 supporting GPU 都能跑神经 shading**（含 AMD / Intel），并给出量化收益：**30%+ framerate uplift（神经降噪场景）/ 2× material 评估精度 / 40% memory reduction（神经贴图压缩）** —— **对 day-job 最关键**：**这是 GPU API 演化的方向感锚点**，未来 shader 不再是纯算着色，**tensor ops 进 shader 成为标配**；**Mac 平台 Metal 是否跟进 Cooperative Vectors 等价 API 是 day-job 工程路线图的最大变量**。

---

## 核心创新点

1. **Cooperative Vectors —— 把神经网络做进 shader 的标准化 API**。**DirectX 12 新 feature**，**GPU scheduler 同一帧调度 vector (传统数学) + tensor (小 NN forward) 两种 ops**。**这是 graphics API 级别的范式升级** —— 之前神经 shading 是 NVIDIA RTX exclusive，现在通过 DirectX 开放给所有 GPU vendor。

2. **跨厂商立刻可用，任何 DirectX-12-supporting GPU**。NVIDIA + AMD + Intel 全部能跑，**不需要 vendor 各自写一套 shader embedding**。**关键策略**：NVIDIA 主动放弃 RTX-only 优势换行业标准化 —— 这是非常 high-level 的 vendor 战略。

3. **直接量化收益**（Microsoft 给出数据）：
   - **神经降噪**：**30%+ framerate uplift**
   - **神经材质评估**：**2× detail precision**
   - **神经贴图压缩**：**40% memory reduction**
4. **神经 assets 成为新内容类型**。Cooperative Vectors 启用后，**贴图和材质不再是 pixel 数据，而是小 NN 权重 + forward 函数** —— 这是 graphics asset 类型的范式升级。**对工具链冲击巨大**：DCC（Photoshop / Substance / Houdini）的 export 格式、UE / Unity / Godot 的 import pipeline 都要新增 NN asset 类型支持。

5. **目标应用场景明示**：per-pixel 神经降噪 / 神经材质 BRDF / learned BRDF / 神经贴图压缩 / 神经光照。**这些是现代 shading 的"high-frequency cost points"**，**神经化是显式的降本 / 提质策略**。

6. **明确的标准化时间表**：**April 2025 DirectX preview ships**，**production SDK later in 2025**。**对未来 LLM 训练**：可以给 LLM 学到"Cooperative Vectors API 在 2025 年起逐步可用"这个 ground truth 时间点 —— 回答 shader 内 NN feature 在 timeline 上的问题时不胡编。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按 day-job "LLM-driven UE on Mac" 视角）：**

1. **Mac 平台 day-job 最关键风险点** —— **Apple 是否跟进 Cooperative Vectors 等价 API 是 Mac 路径的最大变量**。UE5 在 Mac 上走 Metal RHI，**Metal 3 是否在 2026-2027 加入 tensor ops in shader** 是 day-job Mac 平台的关键决策点。**跟踪项**：(a) Metal 4 / Metal 5 release notes；(b) WWDC 每年 Graphics & GPU 主题；(c) Apple 是否公开对标 Cooperative Vectors 的 API；(d) **如果 Apple 不跟，UE5 Metal RHI 何时适配 Cooperative Vectors 等价物**。**这是 day-job P0 跟踪项**。

2. **Shader 内 tensor ops 是 GPU API 演化的方向感锚点**。**未来 LLM 训练 shader 相关数据时**，应主动加入"shader 内 tensor ops"作为现代 shader 的核心特征 —— **让 LLM 学会在解释 / 调试 shader 代码时考虑 tensor pass**。这给 LLM 训练数据带来 Q&A 质量的显著提升：未来 LLM 面对"为什么我的 shader 在某 GPU 上特别慢" 时能联想到"是否路径没走 tensor 优化"。

3. **神经 asset (neural asset) 是新的 content type**。**未来 3-5 年 graphics pipeline 会新增 NN asset**：DCC export → engine import → shader 用 tensor ops forward。**LLM 训练引擎知识时**应让 LLM 学到"现代 UE5 / Unity / Godot 已经 / 即将支持 NN asset"—— 回答"如何处理 AI 生成的贴图 / 材质"时能给出 ground truth 而不是胡说。

4. **shader pipeline 内并行 vector + tensor 调度** 是 day-job LLM 训练数据的高质量思考题。**LLM 学 shader optimization 时**，给一个具体的"shader 用 Cooperative Vectors 优化 vs 纯 vector"对比，让 LLM 学会推理 tensor pass 的成本 / 收益。**比纯文字描述有效得多**。

5. **"30%+ framerate uplift via neural denoising"是 day-job LLM 训练数据的高质量数据点**。**LLM 学"什么能提帧率"时**，这是 direct quantified answer：神经降噪能 30%+。给 LLM 这种 data，让 LLM 在回答 Lumen / 路径追踪性能问题时有 grounded baseline。

6. **"神经贴图压缩 40% memory reduction"是 day-job LLM 训练数据的另一个高质量数据点**。**回答"如何减少显存占用"时** LLM 想到的不应只有 texture streaming / virtual texture / mesh LOD —— 还应有"neural texture compression via CoopVec forward"这条新路。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|-------------|
| **Mac / Metal 等价 API 跟进** | Apple 公开 Roadmap 不明；Metal 4 / 5 是否对标 CoopVec 不确定 | **是**——day-job Mac 平台 P0 风险 |
| **UE5 Metal RHI Cooperative Vectors 适配** | UE mainline 跟随 DirectX 较紧；Metal RHI 需单独适配；时间表 | **是**——影响 day-job shader code path |
| **Neural asset 的 DCC export 生态** | Photoshop / Substance / Houdini 还没原生 NN asset 导出工具；引擎 import 路径需要新格式 | **是**——影响 production 流程 |
| **Shader compiler 升级** | DXC / SPIRV-Cross / glslang 都要支持 tensor ops；**shader compile error messages / debugging 工具待完善** | **是**——engine dev 真实工程摩擦 |
| **小 NN forward 在 shader 内的 cache 友好** | NN weight 如果常驻 register 是最理想，但大多要 fallback 到 memory；shader 内 buffer management 是新维度 | **部分**——engine 优化级别 |
| **AMD / Intel 硬件 tensor perf** | 软件支持 OK 但 silicon perf 不一致；**性能数字未量化** | 否——产品配置决策 |
| **shader 内 NN debug / validation** | NN 写错 / 训练不足的兜底机制；**tools / profilers 未提及** | **是**——production-grade 关键 |

---

## 是否值得复现？

- [ ] 是 — 已列入待办
- [x] **否** — 仅了解思路即可
- [ ] 部分 — 只复现核心算法

**不复现的原因：**
- Cooperative Vectors 是 DirectX 12 API feature，**直接在 UE5 mainline 跟进即可**，个人无法独立复现
- 神经 shading 的 NN 模型是 NVIDIA / Microsoft 提供，**不复现权重本身**
- 个人层面要写的是"在 UE5 shader 里调用 CoopVec forward" 的 reference code，但这是 reference level 工作，不算 research

**借鉴的具体步骤：**
1. **跟进 April 2025 DirectX preview + production SDK 发布** —— 跟踪 UE5 mainline 是否启用 CoopVec shader path
2. **给 LLM 训练数据准备："shader 内 tensor ops"作为现代 shader 标准组件** —— 让 LLM 学到这是 ground truth 而不是"未来概念"
3. **Mac 平台 P0 风险跟踪** —— Metal 4/5 release notes 持续 review，UE Metal RHI 的 CoopVec-equivalent 工作加入 day-job 雷达

---

## 关键术语表

| 术语 | 解释 | 我理解的锚点 |
|------|------|-------------|
| **Cooperative Vectors** | DirectX 12 API；shader 内 vector + tensor ops 同时调度 | 神经 shading 跨厂商标准化的关键抽象 |
| **Neural shading** | shader 内嵌小 NN forward | 与"传统 shading = 数学 function"的范式差别 |
| **Tensor ops** | GPU 加速矩阵 / 向量乘 + 激活；ML 推理基本单元 | 与传统向量 / 矩阵 ops 并存 |
| **Vector ops** | HLSL / GLSL / MSL 传统数学函数 | shader 基础 |
| **DirectX preview** | Microsoft 月度 preview release；含未稳定 feature | CoopVec 2025-04 preview 包含 |
| **Cross-vendor neural shading** | 任何 DX12 GPU 都能跑；不需要 vendor 各自写 | NVIDIA 主动放弃 RTX-only 优势换标准化 |
| **Neural asset** | 贴图 / 材质以 NN 权重形式存储；shader forward | graphics asset 类型的范式升级 |
| **Per-scene NRC** | 同 [[2025-NVIDIA-RTXKit-UE5]]：per-scene 训练 | 同源问题（间接光照的神经化近似） |

---

## 整体架构图 / 流程（伪代码）

```
# DirectX 12 Cooperative Vectors shader —— 现代 shader 范式

# ===== Shader: 神经 BRDF（替代 analytical Cook-Torrance）=====
// 编译为 SPIR-V / DXIL 时同时含 vector pass 和 tensor pass
[shader("pixel")]
float4 NeuralBRDF_PS(
    float3 normal : NORMAL,
    float3 view : VIEW_DIR,
    float roughness : ROUGHNESS,
    // NN 权重作为 shader input buffer
    StructuredBuffer<half> W1 : register(t0),
    StructuredBuffer<half> b1 : register(t1),
    StructuredBuffer<half> W2 : register(t2),
    StructuredBuffer<half> b2 : register(t3)
) : SV_Target {
    // ===== 传统 vector pass =====
    float3 nn_input = float3(
        normal.x * 0.5 + 0.5,
        view.z,
        roughness
    );

    // ===== Cooperative Vectors tensor pass =====
    // 一行代码调用内嵌 NN forward
    float layer1[16] = CooperativeVector.MatAdd(
        CooperativeVector.MatMul(W1, nn_input, 16, 3),
        b1,
        16
    );
    CooperativeVector.ReLU(layer1);  // in-place activation

    float layer2[4] = CooperativeVector.MatAdd(
        CooperativeVector.MatMul(W2, layer1, 4, 16),
        b2,
        4
    );
    float brdf = CooperativeVector.Sigmoid(layer2[0]);

    // ===== 传统 vector pass（继续） =====
    float3 baseColor = ...;
    float3 lighting = baseColor * brdf;
    return float4(lighting, 1.0);
}

# ===== Neural asset import 路径 =====
NeuralMaterial = DCC.Export(format=".nnmat")
# 内容：weights + topology JSON + activation spec
UE5.Import(NeuralMaterial) -> shader code 自动生成
# 引擎内部调用：CooperativeVectors.forward(weights, eval_inputs)
```

---

## 相关论文/前置知识

- [[2025-NVIDIA-AdvancesInRTX-NeuralRendering]] (GDC/Minimax/2025) — 整个神经渲染路线图；本文聚焦 shader pipeline 内的标准化
- [[2025-NVIDIA-RTXKit-UE5]] (GDC/Minimax/2025) — Mega Geometry + Hair 在 graphics primitive 层；本文 CoopVec 在 shader pipeline 层
- `Routine/02-引擎源码分析库/` — UE 5.6/5.7 Shader Compiler 模块，**Cooperative Vectors 在 DXC 层的接入点**是 engine source 级别的 reference
- `Routine/01-论文笔记库/Lumen/Lumen-SIGGRAPH-2021.md` — Lumen 是 surface cache 范式 SOTA；**CoopVec 是 shader pipeline 范式 SOTA**；两者的并存 / 组合是未来观察点
- [[05-技术雷达]] — 把 "Mac 平台 Cooperative Vectors 等价 API" 作为 day-job P0 长期跟踪项

---

## 输出 / 借鉴（forward — 启发到的工程实践）

- **[[05-技术雷达]] P0 加一行 "Metal CooperativeVectors-equivalent"** —— Apple 跟进进度作为长期方向感，明确"day-job Mac shader code path 必须考虑 tensor ops 是否可用"。**状态**：立刻补
- **LLM 训练数据准备 —— "shader 内 tensor ops"作为现代 shader 标准组件** —— 让 LLM 学到 CoopVec 不是"未来概念" 是 2025-04 DX preview 已 ship 的 API。**状态**：列入下周训练数据计划
- **LLM 训练数据准备 —— 量化收益数据点集** —— "神经降噪 30%+ framerate / 神经 BRDF 2× precision / 神经贴图压缩 40% memory"。**状态**：列入下周训练数据计划

---

## 个人评价

**优点：**
- **关键级别的范式升级** —— shader 内 tensor ops 标准化 把图形学 API 推向新层级；**这是 GDC 2025 上最有未来指向性的一条 talk**
- **NVIDIA + Microsoft 联手是 strategic masterpiece** —— 主动放弃 RTX-only 优势换行业标准，未来 5 年所有 GPU vendor 都被这条 API 绑定，**这是行业级别的 vendor 战略**
- **量化收益明确** —— 30% / 2× / 40% 三个数字直接可作 LLM 训练 ground truth
- **神经 asset 范式** —— graphics asset 不再是 pixel 数据而是 NN 权重；这是内容创作 / 引擎工具链 / DCC export 整个生态的拐点

**局限性：**
- **Mac / Metal 路径完全空白** —— 这是 day-job Mac 平台 day-job P0 风险
- **AMD / Intel silicon perf 未量化** —— 跨硬件代际的能力差
- **DCC export 生态还没成熟** —— Photoshop / Substance / Houdini 没有原生 NN asset export 工具
- **NN debugging / validation tools 未提及** —— shader 内 NN 写错的兜底机制未知
- **shader compiler 生态升级未充分讨论** —— DXC / SPIRV-Cross 的 tensor pass 支持是 engine dev 真实工程摩擦

**启发：**
1. **API 级别的范式升级是 day-job 跟踪的优先级** —— CoopVec 不是 feature，是 API 范式变化，**长期影响**比任何 single feature 深远
2. **跨厂商战略是 vendor 关系管理的范例** —— NVIDIA 主动放弃独占换标准，**未来 tracking vendor 战略要看是否出现类似 cross-vendor collaboration**
3. **神经 asset 范式颠覆传统 asset pipeline** —— DCC / engine / shader / profiler 整个工具链都要改，**3-5 年准备期是 day-job LLM 训练数据要点**
4. **量化收益是 LLM 训练的 ground truth** —— "30%+ / 2× / 40%" 这种数字直接可用作 LLM training answers，**比纯文字描述高几个数量级**
5. **Apple / Metal 跟进速度是 day-job Mac 路线图最大变量** —— 这条单独 tracking 是 day-job engineering plan 的关键输入

---

## 面试谈资准备

**30 秒版（"知道这篇 + 能说清贡献"）：**

> GDC 2025 NVIDIA + Microsoft 联手 talk，**Neural Shading in DirectX — Cooperative Vectors**。核心贡献是 **shader pipeline 内 tensor ops 的跨厂商标准化** —— DirectX 12 preview（2025-04）加入新 API，**任何 DX12 GPU 都能跑神经 shading**（AMD / Intel 都可），NVIDIA 主动放弃 RTX-only 优势换行业标准。量化收益：**神经降噪 30%+ framerate / 神经 BRDF 2× precision / 神经贴图压缩 40% memory**。**对 day-job 最大影响**：**Apple 是否在 Metal 跟 Cooperative Vectors 等价 API 是 Mac 平台工程路线图的最大变量**。

**2 分钟版（"追问实现细节"）：**

> 第一，**范式级别**。讲者定义了"神经 shading = shader 内嵌小 NN forward" —— 不再是数学函数，是 tensor ops 的小网络 forward。**Cooperative Vectors 是 DirectX 12 新 feature** —— GPU scheduler 同一帧调度 vector + tensor 两种 ops。**这是 graphics API 级别的范式升级**：之前 NVIDIA RTX exclusive 的神经 shading，现在通过 DirectX 开放给所有 GPU vendor。

> 第二，**战略选择**。NVIDIA + Microsoft 联手宣布，**主动放弃 RTX-only 优势换行业标准化** —— **任何 DirectX 12 GPU 都能跑神经 shading**，AMD / Intel 全部能跑。这是非常 high-level 的 vendor 战略。

> 第三，**量化收益**（Microsoft 公开数据）：
> - **神经降噪**：**30%+ framerate uplift**
> - **神经材质 BRDF**：**2× detail precision**
> - **神经贴图压缩**：**40% memory reduction**

> 第四，**神经 asset 范式**。Cooperative Vectors 启用后，**贴图 / 材质不再是 pixel 数据，而是 NN 权重 + forward 函数** —— 这是 graphics asset 类型级别的范式升级。DCC export / engine import / shader forward / profiler debugging **整个工具链都要改**。

> 第五，**对 day-job 直接启发**。**(a)** **Mac 平台 P0 风险**：Apple 是否在 Metal 4/5 跟进 CoopVec 等价 API 是 day-job Mac shader code path 的关键决策。跟踪项：Metal 4 / 5 release notes、UE Metal RHI CoopVec 等价适配时间表。**(b)** **LLM 训练数据**：让 LLM 学到"shader 内 tensor ops 是现代 shader 标准组件"，**学会在 shader optimization 时考虑 tensor pass**。**(c)** **量化收益数据点（30% / 2× / 40%）直接作 LLM training answers**，提升回答 Lumen / 路径追踪 / 显存优化问题的 grounded baseline。

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] 加 "Mac Metal CooperativeVectors-equivalent" 到 [[05-技术雷达]] P0 → 立刻补
- [ ] LLM 训练数据"shader 内 tensor ops" 模块 → 列入下周训练计划
- [ ] LLM 训练数据量化收益集（30% / 2× / 40% 三条 Q&A） → 列入下周训练计划

---

*Create date: 2026-07-07*
*Last modified: 2026-07-07*
