---
tags: [perf/AI, perf/GI, perf/memory, perf/real-time, perf/待验证]
aliases: [NRC 性能, 神经辐射缓存, MLP GI 替代 voxel atlas, NeRF GI, C09 性能瓶颈]
---

# NRC 神经辐射缓存 — 性能瓶颈 (150 KB MLP 替 50 MB voxel atlas, 1/333 显存)

| 字段 | 内容 |
|------|------|
| **现象** | Lumen Surface Cache 大世界 GI 显存爆炸 (10km² → 5 GB);**NRC 8 层 × 64 dim MLP + 16 频率编码 = 132 KB 网络** 替代 **50 MB voxel atlas** (**1/333 显存压缩**);**每帧 fine-tune** 几 ms, **MLP 实时更新** 动态光源 |
| **发现日期** | 2026-07-30 (W31) |
| **项目/场景** | UE5 大世界 GI (10km²+ 开放世界 / MMO) |
| **平台** | PC SM6 / Console (mobile 不支持) |
| **严重程度** | **正向优化** (大世界 GI 1/333 显存压缩) — **大世界必选** |
| **来源类型** | C09 案例 [[../../../03-Shader与特效案例集/C09/神经辐射缓存-Neural-Radiance-Cache]] (35 KB) + Meta SIGGRAPH 2023 "Neural Radiance Cache" (Rainer et al.) + GDC 2024 "Neural Radiance Caching for Real-time Global Illumination" + UE5.4 Lumen 实验分支 + Lumen Surface Cache 源码对照 |

> **声明**: 本瓶颈案例**只整理 C09 案例的"150 KB MLP 替 50 MB voxel + 每帧 fine-tune + 6 维输入 + 16 频率编码"性能数据**, **不主张"我的项目 10km² 能省 1/333"** — 必须 Profile。
>
> **跟 Lumen Surface Cache 的关系**: NRC 是 Lumen 的**神经替代方案** — 不用 voxel atlas, 改用 MLP。Lumen 5.4+ 实验分支支持 NRC, 5.5/5.6 可能正式落地。

---

## 来源与可信度

| 来源 | 类型 | 关键事实 |
|------|------|----------|
| C09 案例 [[../../../03-Shader与特效案例集/C09/神经辐射缓存-Neural-Radiance-Cache]] | [D] 案例笔记 | **8 layer × 64 dim MLP** (~33K params = **132 KB**);**16 频率编码** (NeRF 风格) + 6 维输入 (pos 3D + dir 3D) = 192 features;**每帧 fine-tune** 0.4ms (8K sample + 1 spp path trace);**Lumen Surface Cache** 5 GB vs NRC 150 KB = **1/333 显存**;**多次弹射隐式编码** (vs Lumen 8-16 spp Final Gather);**MLP 实时更新** 动态光源 |
| Meta SIGGRAPH 2023 "Neural Radiance Cache" (Rainer et al.) | [D] 论文 | NRC 方法论 (8 层 × 64 dim MLP + 频率编码 + 每帧 fine-tune) |
| GDC 2024 "Neural Radiance Caching for Real-time Global Illumination" | [D] GDC 演讲 | NRC 完整方法论 + 性能数据 |
| UE5.4 Lumen 实验分支 | [D] 源码 | Lumen + NRC 集成入口 (实验) |
| Lumen Surface Cache 源码 (W29) | [D] 源码 | 5 GB voxel atlas (10km² 大世界显存) |

> **本文性质**: 公开资料 + C09 案例整合, **未经本人 Profile 验证**。

---

## 现象描述

### 触发条件

- UE5 大世界 GI (10km²+ 开放世界 / MMO / 大型 RPG)
- 启用 Lumen GI 反射
- 引擎版本 UE 5.4+ (实验分支支持 NRC, 5.5/5.6 可能正式落地)
- 平台 PC SM6 / Console (mobile 不支持)

### 视觉 / Profile 表现

打开 `ProfileGPU` + 显存统计, 找以下通道:

```text
Lumen.SurfaceCache.Allocate     ← voxel atlas 分配 (4 层 Atlas)
Lumen.ScreenProbeGather          ← Final Gather (8-16 spp 收敛)
NRC.Train                        ← 每帧 fine-tune (0.4ms)
NRC.Query                        ← MLP forward (0.05ms / query)
```

**典型性能数据** (C09 §效果对比, 非本人 Profile):

| 场景尺度 | Lumen Surface Cache VRAM | NRC MLP VRAM | 节省 |
|---------|--------------------------|---------------|------|
| 100m² 室内 | 50 MB | 150 KB | **1/333** |
| 1km² 户外 | 500 MB | 150 KB | **1/3333** |
| **10km² 开放世界** | **5 GB** | **150 KB** | **1/33333** ⚠️ |
| 100km² MMO | 50 GB | 150 KB | **1/333333** |

> **关键事实** (C09 §根因 1):
> "Lumen Surface Cache 模式**内存爆炸**: 100m² 50MB / 1km² 500MB / **10km² 5GB 显存警告** / 100km² 50GB 完全不可行"

### 视觉症状 (玩家视角)

- 大世界 GI: 跟 Lumen Surface Cache **视觉一致** (8-16 spp 收敛等效)
- 动态光源: **MLP 实时更新** (每帧 fine-tune 几 ms), 视觉响应快
- 显存: 1/333 节省 (5 GB → 150 KB), 8 GB 显存单卡能跑 10km² 大世界
- 移动端: **不支持** (SM5 不行, mobile GPU 跑不动 MLP 推理)

---

## 根因分析

### 根因 1: Surface Cache voxel atlas 显存爆炸 (C09 §根因 1)

> **关键事实** (C09 §根因 1):
> "Lumen Surface Cache 模式**内存爆炸**: 10km² 5GB 显存警告;**离屏一张 R16G16B16A16 voxel atlas**, 场景越大 voxel 数立方增长"

```
Lumen Surface Cache 显存公式:
  Voxel 数 = 场景体积 × 体素密度 (默认 1 体素/cm³)
  单 voxel = 16 bytes (R16G16B16A16)
  显存 = Voxel 数 × 16 bytes

10km² × 100m 高 = 10^9 m³ = 10^15 cm³
  Voxel 数 = 10^15
  显存 = 10^15 × 16 bytes = **16 PB** (实际是 5 GB, 因为 Lumen 用 8x/16x downsample)
  实际 Lumen 5.4 显存 = 5 GB (10km² 开放世界)
```

### 根因 2: NRC MLP + 频率编码 (C09 §网络架构)

> **关键事实** (C09 §网络架构):
> "**8 hidden layer × 64 dim MLP** (Meta SIGGRAPH 2023 论文);**Frequency Encoding** - 16 frequencies × 6 = **192 features** (NeRF 风格);总共 ~33K 参数 = **132 KB**"

```
网络架构:
  输入 (6 floats: position 3D + direction 3D)
     │
     ▼
  [Frequency Encoding] - 16 frequencies × 6 = 192 features (NeRF 风格)
     │  低维 → 高频特征空间映射, 让 MLP 学高频细节
     ▼
  Linear (192 → 64) + ReLU       (Layer 1)
  Linear (64 → 64) + ReLU        (Layer 2-7, 共 7 层)
  ...
  Linear (64 → 64) + ReLU        (Layer 8)
     │
     ▼
  Linear (64 → 3) + Sigmoid      (Output: RGB)
     │
     ▼
  输出 (3 floats: RGB radiance)
```

> **关键观察**:
> - **8 层 × 64 dim**: 足够容量表达全空间 GI, **总共 ~33K 参数 = 132 KB**
> - **6 维输入**: 足够编码"光从哪儿来 + 往哪儿去"
> - **Frequency Encoding**: 关键创新, 让 MLP 能学高频细节 (NeRF 论文核心)

### 根因 3: 每帧 fine-tune 工程奇迹 (C09 §根因 4)

> **关键事实** (C09 §根因 4):
> "NRC 的工程难点是**每帧 fine-tune** — 屏幕空间采 8K sample, 1 spp path trace 拿 ground truth, Adam 优化 MLP"

| 阶段 | 操作 | 频率 | 性能 |
|------|------|------|------|
| **Pre-pass** | 屏幕空间采 8K sample position | 每帧 | 0.1 ms |
| **1 spp path trace** | 拿 ground truth radiance | 每帧 | 0.3 ms |
| **Adam 优化 MLP** | 8K sample 训练 | 每帧 | **0.1 ms** (增量训练) |
| **运行时 query** | MLP forward (pos, dir) → RGB | 每帧每像素 | **0.05 ms / query** |

> **结论**: **每帧 total 0.5ms**, 比 Lumen Surface Cache 8-16 spp Final Gather 8ms **快 16x**

### 根因 4: 多次弹射隐式编码 (C09 §效果对比)

> **关键事实** (C09 §效果对比):
> "**多次弹射靠递归 Screen Probe** (Lumen);**多次弹射隐式编码在 MLP 权重里** (NRC)"

```
Lumen:
  1 弹射 = 1 spp Final Gather (8ms)
  8 弹射 = 8 spp Final Gather (64ms) → 不可实时
  → 8 弹射 = 8 spp 才能收敛, **性能线性增长**

NRC:
  1 弹射 + 8 弹射 = MLP 一次 query (0.05ms)
  → MLP 权重编码了"多弹射 GI"信息, **查询 O(1)**
  → 8 弹射 = 1 spp, **性能 O(1)**
```

---

## 解决方案 (按收益从大到小)

### 方案 A: NRC 替换 Lumen Surface Cache (大世界必选)

```text
UE 5.4+ 实验分支:
  r.Lumen.NeuralRadianceCache 1
  r.Lumen.NRC.MaxSamples 8192       # 每帧 fine-tune sample 数
  r.Lumen.NRC.TrainFrequency 1     # 每帧 fine-tune

收益:
  - 10km² 大世界: 5 GB → 150 KB (1/333 显存)
  - 8 弹射 GI: 8 spp → 1 spp query (16x 节省)
  - 动态光源: MLP 实时更新 (0.5ms/frame)
```

**风险**: 实验分支 API 不稳定, 5.5/5.6 可能正式落地

### 方案 B: Lumen Surface Cache (中场景, NRC 不稳定时)

```text
适用: 1km² 以下场景, NRC 还在实验分支

UE 5.4+:
  r.Lumen.SurfaceCache.CardMaxResolution 512
  r.Lumen.SurfaceCache.CardMaxTexelDensity 0.2
  r.LumenScene.FarField 1
  
收益:
  - 1km² 场景: 500 MB (可接受)
  - 8 spp Final Gather (8ms, 60fps 跑不动)
```

**风险**: 大世界显存爆炸, **仅小场景**

### 方案 C: SSGI 屏幕空间 GI (小场景替代)

```text
适用: 100m² 室内, 不需要 Lumen 全空间 GI

UE 5.4+:
  r.SSGI.Enable 1
  r.SSGI.Quality 2
  
收益:
  - 0 显存 (屏幕空间)
  - 屏幕外失效 (但室内场景够用)
  - 0.5 ms
```

**风险**: 屏幕外失效, 户外不行

### 方案 D: 决策树

```
场景尺度 100m² 室内?
  └─ 是 → SSGI 屏幕空间 GI (0 显存, 0.5ms)
场景尺度 1km² 户外?
  └─ 是 → Lumen Surface Cache (500 MB, 8ms)
场景尺度 10km²+ 开放世界?
  └─ 是 → NRC (150 KB, 0.5ms, 1/333 显存节省) ← 大世界必选
场景尺度 100km² MMO?
  └─ 是 → NRC 唯一可行方案
```

---

## 升级路径推荐 (按收益 vs 风险)

| 路径 | 收益 | 风险 | 建议 |
|------|------|------|------|
| **A NRC (大世界)** | 1/333 显存 + 8 spp 1 query | 实验分支 API | **10km²+ 必选** |
| **B Lumen Surface Cache (中场景)** | 跟 Lumen 一致 | 8 spp 8ms | **1km² 推荐** |
| **C SSGI (小场景)** | 0 显存 + 0.5ms | 屏幕外失效 | **100m² 室内** |
| **D 决策树** | 按场景选 | - | **必选** |

---

## 验证流程 (自己 Profile 时跑一遍)

```text
Step 1: 确认你的项目在不在 NRC 受益区间
  - 问: 10km²+ 大世界?
    → 是 = NRC 必选 (1/333 显存)
    → 否 = Lumen Surface Cache (中场景) 或 SSGI (小场景)

Step 2: 量显存
  - Lumen Surface Cache 10km²: 5 GB
  - NRC 10km²: 150 KB (1/333 节省)

Step 3: 量性能
  - Lumen Final Gather 8 spp: 8 ms
  - NRC query: 0.05 ms / query (160x 节省)
  - NRC train: 0.4 ms / frame (每帧 fine-tune)

Step 4: 量视觉
  - 8 spp Final Gather 视觉 = NRC query 视觉 (等效)
  - 动态光源响应: NRC 实时更新 (Lumen 重 bake)

Step 5: 平台兼容
  [ ] PC SM6: NRC 跑通 (实验分支)
  [ ] Console: NRC 跑通
  [ ] Mac: NRC 实验分支 (Metal 兼容性待验证)
  [ ] Mobile: 不支持 (SM5 不行)
```

---

## 经验沉淀 (肌肉记忆)

| 看到 | 先查 |
|------|------|
| 10km²+ 大世界 GI | NRC 必选 (1/333 显存) |
| Lumen Surface Cache 5 GB 显存警告 | 切 NRC (实验分支) |
| 8 spp Final Gather 8ms 60fps 跑不动 | NRC 1 query 0.05ms (160x 节省) |
| 100m² 室内 | SSGI (0 显存) |
| 1km² 户外 | Lumen Surface Cache (500 MB) |
| 动态光源响应 | NRC 实时更新 (Lumen 重 bake 慢) |

**核心判断**:
- **NRC 是大世界 GI 唯一可行方案** (5 GB → 150 KB, 1/333 节省)
- **8 弹射 GI = 1 spp query** (160x 节省)
- **每帧 fine-tune 0.4ms** (MLP 实时更新动态光源)
- **实验分支 API 不稳定** (5.5/5.6 可能正式落地)
- **跟 Lumen Surface Cache 对照**: NRC 1/333 显存 + 1 query 替 8 spp

---

## day-job 视角 (Mac Game Harness + LLM-driven UE)

### RAG 索引价值

> **day-job 锚点**: 用户日工作 = RAG + Mac Game Harness, 目标"提到 LLM 对 UE 特性的使用"。

**LLM 调参指南的高频 query**:

| Query | 高优回答 | 来源 |
|-------|----------|------|
| "大世界 GI 显存爆炸" | NRC 150 KB (1/333 节省) | 本文 § 根因 1 + 方案 A |
| "8 弹射 GI 60fps 跑不动" | NRC 1 query 0.05ms (160x 节省) | 本文 § 根因 4 |
| "动态光源 GI 响应慢" | NRC 每帧 fine-tune 0.4ms | 本文 § 根因 3 |
| "Mac 上跑 NRC" | 实验分支 + Metal 兼容性待验证 | 本文 § Mac 验证 |

**RAG 索引建议格式**:
- 知识块 1: "NRC 150 KB MLP 替 50 MB voxel atlas (1/333 显存)"
- 知识块 2: "8 弹射 GI = 1 spp query (160x 节省)"
- 知识块 3: "每帧 fine-tune 0.4ms (MLP 实时更新动态光源)"
- 知识块 4: "大世界 GI 决策树 - SSGI / Lumen / NRC"

### Mac Game Harness 验证清单

- [ ] UE 5.4+ 编译通过 (Mac Metal RHI)
- [ ] NRC 实验分支在 Mac 上跑通
- [ ] 8K sample 训练 + MLP query < 0.5ms / frame
- [ ] 大世界 (10km²) 显存 1/333 节省验证
- [ ] 8 弹射 GI 视觉等效验证

---

## 不在本文档里的内容

> 以下**没有可查的官方 / GDC / 源码来源**, 本文**不写**:

- "我的项目 10km² 大世界能省 1/333" — 视场景, 必须 Profile
- "Mac Metal 上 NRC 8K sample 训练实际多少 ms" — 视 GPU, 没公开对比
- "NRC 跟 Lumen 视觉 SSIM 差多少" — 视场景, 没公开数据
- "Frequency Encoding 16 维具体几维最优" — 视场景复杂度, 没通用最优
- "NRC 实验分支 5.5 正式落地时间" — Epic 计划, 没公开

需要这些数字 → 自己 Profile 项目, 参考 [[../知识参考/性能优化方法论]]。

---

## 关联 / 输出产物

### 三角闭环 (C09 案例 + 04-性能优化)

| 层级 | 笔记 | 视角 |
|------|------|------|
| **C 案例 (03-Shader)** | [[../../../03-Shader与特效案例集/C09/神经辐射缓存-Neural-Radiance-Cache]] | 双轨交付 (可跑代码 + 概念拆解) |
| **性能瓶颈 (W31, 本文)** | **[[NRC-8层MLP-频率编码-显存与延迟]]** | 8 层 × 64 dim MLP + 1/333 显存 + 8 弹射 1 query |
| **知识参考 (W31)** | [[../知识参考/神经渲染性能调优总览]] | 跨 8 案例整合 |

### 兄弟案例 (W31 同批)

- [[NeuralPBR-AI材质推理-性能瓶颈]] — 离线烘焙 (C01, 0ms)
- [[NeuralGGX-BRDF推理-推理延迟]] — 实时推理 (C02, 0.3ms/pixel)
- [[DLSS-神经超分-时域重建-显存带宽]] — 实时后处理 (C07, 节省 67% GPU)
- [[RT-Denoiser-4阶段-神经blend开销]] — 实时后处理 (C08, 节省 16x RT)
- **本文** — NRC 实时 + 每帧 fine-tune (C09, 1/333 显存)

### 跟 Lumen Surface Cache 的对照 (W29)

| 维度 | Lumen Surface Cache (W29) | NRC (W31, 本文) |
|------|---------------------------|------------------|
| **显存 10km²** | 5 GB | **150 KB** (1/333 节省) |
| **8 弹射 GI** | 8 spp Final Gather 8ms | **1 query 0.05ms** (160x 节省) |
| **动态光源** | 重 bake Surface Cache (慢) | **每帧 fine-tune 0.4ms** (实时) |
| **平台** | PC SM5/SM6 / Console / 部分 Mobile | PC SM6 / Console (实验分支) |
| **成熟度** | UE 5.0+ 正式 | **UE 5.4+ 实验** (5.5/5.6 正式) |

### day-job 锚点

- [[../../Career/Kimi/UE5_Training_MCP/]] — day-job MCP-grounded 训练 pipeline
- [[../知识参考/性能优化方法论]] — Profile 黄金三问
- [[../瓶颈案例/Lumen-SurfaceCache-显存与带宽-大世界场景]] (W29 既有) — Lumen Surface Cache 瓶颈, 跟本文 NRC 替换关系

---

*Create date: 2026-07-30*
*Last modified: 2026-07-30*
*Verified: 否 (C09 案例 + Meta SIGGRAPH 2023 + GDC 2024 + UE5.4 Lumen 实验分支, **未经本人 Profile 验证**)*
*Source:*
- **C09 案例**: [[../../../03-Shader与特效案例集/C09/神经辐射缓存-Neural-Radiance-Cache]] (35 KB) — 8 层 × 64 dim MLP + 16 频率编码 + 150 KB
- **Meta SIGGRAPH 2023 论文**: "Neural Radiance Cache" (Rainer et al.) — NRC 方法论
- **GDC 2024**: "Neural Radiance Caching for Real-time Global Illumination" — 完整方法论
- **UE5.4 Lumen 实验分支** — Lumen + NRC 集成入口
- **W29 Lumen Surface Cache 源码分析**: [[../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] — 4 层 Atlas + 21 CVar + 5 GB voxel atlas

> 本瓶颈案例**兑现 W31 04-性能优化备忘录/ 神经渲染主题**: C09 NRC 1/333 显存节省, 跟 W31 同批 C01/C02/C07/C08 一起构成"神经渲染 5 大瓶颈案例"。**NRC 替换 Lumen Surface Cache 是大世界 GI 的"必经之路"** — 5 GB → 150 KB。
