---
tags: [routine/平台, routine/Mac, routine/Metal-RHI, routine/day-job, radar/图形渲染, radar/引擎架构]
aliases: [Mac 平台 vault, Apple Silicon UE5, Metal RHI 适配, day-job Mac Harness]
quarterly_review: 2026-Q3
---

# Mac 平台 vault — UE5 on Apple Silicon

> **W29 状态**:索引页起头,5 个 anchor 已立;W30 补每个 anchor 的实际工程笔记。
> **为什么单独建索引页**:day-job = RAG + Mac Game Harness(LLM-driven UE on Mac),Mac 平台是 LLM "理解并调用 UE 特性" 的关键约束,缺位 1 个季度。W29 必建,即使先填 5 行也行。

---

## 1. 为什么需要这个 vault

day-job 主线 = **"提到 LLM 对 UE 特性的使用"**。LLM 训练 / RAG 检索时,需要回答的"Mac 相关"问题包括:

- 哪些 UE 渲染特性在 Mac Metal RHI 上是**完整支持**的?
- 哪些是**有 fallback** 的(需要 CVar 调优)?
- 哪些是**完全不支持**的(应该用替代方案)?
- Apple Silicon unified memory 怎么影响 GPU 内存预算?

vault 缺位时,LLM 训练数据里没有 Mac 相关的工程实践,会"盲目建议" DX12 / Vulkan 的优化 → day-job 实际项目跑不通。

---

## 2. 5 个 anchor(待 W30 起头每个写 1 篇)

### Anchor 1: [[Mac-Metal-RHI-适配清单|Mac Metal RHI 适配清单]]
- **状态**:✅ **W30 完成**(15.5 KB / 280 行 + 主表 1 张 + 11 特性详解)
- **范围**:UE 5.4+ 渲染特性 × Metal RHI 兼容性矩阵(11 特性: Lumen GI / Lumen 反射 / Final Gather / Surface Cache / Nanite culling / Nanite streaming / Nanite 5.4 Bin / VSM pool / VSM HZB / VSM Clipmap / VSM BC6H / Substrate 全家 / MegaLights / HeterogeneousVolumes / Mass / NNE 4 后端)
- **已落地**:主表 21 行 + 11 个特性详解(每个含 Mac 状态 / 关键 CVar / 已知问题 / day-job 落地)+ 4 个 NNE 后端 × 3 平台对比 + Mac 调优 CVar 速查 + RAG 索引格式示例
- **目标读者**:在 Mac 上跑 UE5 项目的引擎程序员 + day-job RAG 索引编辑

### Anchor 2: [[Apple-Silicon-Unified-Memory-对-GPU-预算的影响|Apple Silicon Unified Memory 对 GPU 预算的影响]]
- **状态**:待 W30 起头
- **范围**:M1 / M2 / M3 / M4 各代 unified memory 带宽、访问延迟、跟传统 GPU 显存的差异
- **预期大小**:200-300 行
- **目标读者**:评估 Mac 项目显存预算的 TA

### Anchor 3: [[Metal-Shader-MSLL-编译坑|Metal Shader (MSLL) 编译坑]]
- **状态**:待 W30 起头
- **范围**:HLSLcc → MSLL 转换的常见问题(精度丢失、UB alignment、atomic、wave intrinsics)
- **预期大小**:200-300 行
- **目标读者**:写自定义 UE shader + Mac 兼容的 TA

### Anchor 4: [[LLM-对-UE-Mac-项目-RAG-语料切分策略|LLM 对 UE Mac 项目 RAG 语料切分策略]]
- **状态**:待 W30 起头
- **范围**:chunked-MD 格式怎么分块、Mac 平台特定 chunk 怎么标记、embedding 怎么过滤
- **预期大小**:200-300 行
- **目标读者**:day-job 团队做 RAG 的人(可能就是我)

### Anchor 5: [[Lyra-on-Mac-跑通-Demo-记录|Lyra on Mac 跑通 Demo 记录]]
- **状态**:待 W30 起头
- **范围**:Lyra 5.4+ 在 Mac 上的 PIE 跑通、关键 CVar、性能 baseline
- **预期大小**:200-300 行 + 截图
- **目标读者**:需要 demo 验证的引擎程序员

---

## 3. 已知关键差异(DX12 / Vulkan vs Metal)速查

> **W29 临时起头版**,W30 在每个 anchor 里逐项展开

| 维度 | DX12 / Vulkan | Metal | UE 适配策略 |
|------|---------------|-------|--------------|
| 着色器编译 | DXC / glslc | MSLL (Metal Shading Language) | HLSLcc 转换,部分高级特性需 fallback |
| 显存模型 | 独立 GPU 显存 | Unified Memory(共享 CPU+GPU) | 预算可放大,但 atomic 行为差异 |
| 异步计算 | parallel | sequential(部分) | `r.AsyncCompute=0` / 拆分 pipeline |
| Multithreaded encoding | ✅ | ⚠️ 单线程 | 优化 command buffer 切分 |
| Wave intrinsics | 全平台 | 仅 Apple GPU | `FCommonShaderUtils::GetWaveSize()` 适配 |
| BC6H 压缩 | ✅ | ⚠️ 部分早期不支持 | 5.4+ fallback 到 RGBA16F |
| Mesh shader | ✅ | ✅ (Metal 3.0+) | UE 5.4+ 完整支持 |
| Ray tracing | ✅ | ✅ (Metal 3.0+) | UE 5.4+ Mac 完整支持 |
| 调试工具 | PIX / RenderDoc | Xcode GPU Frame Capture | 跨平台调试是痛点 |

---

## 4. day-job 集成点

day-job = RAG + Mac Game Harness,Mac vault 喂 LLM 的 3 种形式:

1. **RAG 检索语料**:每个 anchor 是一篇 chunked-MD,LLM 查询"Mac 上 Lumen 怎么跑"时检索
2. **训练数据**:把 anchor 喂给 LLM 微调,让它学到"Mac 上的 UE 跟 PC 不一样"
3. **工具描述**:day-job 的 Mac Harness 工具集,每个工具的 `description` 引用 Mac 兼容性

**3 个优先级 P0 anchor**:
- Anchor 1(渲染特性 × Metal 兼容矩阵)— W30 必做,跟 Lumen / Nanite / VSM 升"已掌握"门槛绑定
- Anchor 4(RAG 语料切分)— W30 必做,day-job 落地直接依赖
- Anchor 5(Lyra on Mac 跑通)— 8/7 月度回顾前必做,Lumen 升"已掌握"门槛

---

## 5. W29 兑现状态

| 计划项 | 状态 | 备注 |
|--------|------|------|
| 建 `Routine/Mac-平台/00-README.md` 索引 | ✅ | 本文档 |
| 5 个 anchor(每行 stub) | ✅ | 见 §2,W30 展开 |
| 速查表(差异矩阵) | ✅ | 见 §3,W30 逐项展开 |
| 第 1 篇 anchor 实质内容 | ❌ | W30 起头,优先 Anchor 1 + 4 |

---

## 6. 关联

- [[../05-技术雷达/00-README|技术雷达 00-README]] — Mac 缺位是 W28 三能力对账的"日结遗留"
- [[../05-技术雷达/P0-立即学习/Lumen|Lumen 雷达]] — Mac 上跑通 Lumen 是"已掌握"门槛
- [[../05-技术雷达/P0-立即学习/Nanite|Nanite 雷达]] — Mac 上跑通 Nanite 是"已掌握"门槛
- [[../05-技术雷达/P0-立即学习/VSM|VSM 雷达]] — Mac 上跑通 VSM 是"已掌握"门槛
- [[../02-引擎源码分析库/Unreal-Engine/W29/UE5-VSM-源码追踪|VSM 源码]] — §11 Mac Metal 适配小节
- [[../02-引擎源码分析库/Unreal-Engine/W29/UE5-Nanite-MeshPass-ClusterDAG-PageStreaming-源码追踪|Nanite 源码]] — Mac 缺位提示
- [[../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析|Lumen Surface Cache 源码]] — Mac 缺位提示
- [[../2026-07-05-三能力对账|三能力对账]] — Mac 缺位是"日结遗留"项之一

---

*Create date: 2026-07-18(W29)*
*Last modified: 2026-07-18(W29)*
*W30 待续: 5 个 anchor 各写一篇实质内容*
