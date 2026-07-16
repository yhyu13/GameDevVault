---
tags: [perf/GPU, perf/Nanite, perf/shader, perf/待验证]
aliases: [Nanite 5.4 Material Pipeline, Nanite 5.4 材质管线, 4015 Bins 3675 Empty, 材质 Bin 调度, Nanite Compute Shader 材质管线]
---

# Nanite 5.4 材质管线 — 空调度削减 (W29 论文数字落地)

| 字段 | 内容 |
|------|------|
| **现象** | UE 5.0/5.1 时期 Nanite 材质管线 90% 的 draw call 是空调度 (empty bins) — 复杂场景下材质 Bin 调度浪费严重, BasePass 顶到 5ms+ |
| **发现日期** | 2026-07-17 (W29) |
| **项目/场景** | UE5 含大量异材质 (材质种类 > 1000) 的大世界 (City Sample 级别) |
| **平台** | PC (D3D12) / PS5 / XSX / Mac (Metal 5.4+) |
| **严重程度** | 严重 (BasePass 5ms 场景可优化到 3ms, **Wihlidal 演讲原话: 40% 提速**) |
| **来源类型** | GDC 2024 演讲 (Graham Wihlidal, Epic Games) + W29 论文笔记 [[../../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry]] + W26 源码分析 [[../../02-引擎源码分析库/Unreal-Engine/W26/UE5-Nanite-虚拟几何shader]] + W29 雷达 P0 笔记 [[../../05-技术雷达/P0-立即学习/Nanite]] |

> **声明**: 本瓶颈案例**只整理 GDC 2024 演讲原话 + W29 论文 + W26 源码分析**, **不主张"自己项目能拿到 X% 提升"** — 必须在自己的目标场景下用 `ProfileGPU` + 切换 5.0 vs 5.4 二进制对比复测。

---

## 来源与可信度

| 来源 | 类型 | 关键事实 |
|------|------|----------|
| GDC 2024 *Nanite GPU-Driven Material Pipeline* — Graham Wihlidal | [D] GDC 演讲 | **4015 个总着色装箱, 3675 个装箱是空的 (91.5% 空调度)**; 4.92ms → 3.05ms; 5.4 compute shader 方案; 25-30% VRS 节省 |
| SIGGRAPH 2021 *Nanite: A Pipeline for Photorealistic Real-Time Geometry* — Brian Karis | [D] SIGGRAPH 论文 | Cluster 切分 + Visibility Buffer 范式; 5.0 材质管线"每种材质 1 个全屏 draw call" |
| UE 5.8 源码 `NaniteMaterialShader.cpp` / `NaniteRasterizer.cpp` | [D] 源码 | 5.4 compute shader 路径 (Classify / Reserve / Scatter 三阶段) |
| W29 论文笔记 [[../../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry]] | [D] 笔记 | 5.4 材质管线创新点 4 (Bin 调度 + 80% 削减) |
| W26 源码分析 [[../../02-引擎源码分析库/Unreal-Engine/W26/UE5-Nanite-虚拟几何shader]] | [D] 笔记 | Nanite 虚拟几何管线中文版源码追踪 |
| W29 雷达 P0 [[../../05-技术雷达/P0-立即学习/Nanite]] | [D] 雷达 | P0 优先级 + day-job 锚点 |

> **本文性质**: 公开资料 + W29 笔记整合, **未经本人 Profile 验证**。Wihlidal 的"4015 / 3675 / 4.92→3.05ms" 是 City Sample 特定场景的测量, **不是通用收益**。

---

## 现象描述

### 触发条件

- 场景 **材质种类 > 1000** (City Sample ~5000, Valley of the Ancients ~2000, Lumen in the Land of Nanite ~500)
- 启用 Nanite 渲染 (默认)
- 引擎版本 **UE 5.0 / 5.1** (5.4 之前)
- GPU 跑在 4K 70% 动态分辨率或类似重负载

### 视觉 / Profile 表现

打开 `ProfileGPU`, 找以下通道:

```text
BasePass                       ← 通常最大开销
  └── Nanite.BasePass          ← UE 5.0-5.3 命名
  └── Nanite.GBufferCompute    ← UE 5.4+ 新增 (compute shader 路径)
  └── Nanite.Misc             ← Classify/Reserve/Scatter
```

**典型劣化模式** (Wihlidal 演讲原话场景, 非本人 Profile):

| 场景 | Bin 数 | 空 Bin | 空调度比例 | BasePass 耗时 |
|------|--------|--------|-----------|---------------|
| **City Sample 特定镜头** | 4015 | 3675 | **91.5%** | 4.92 ms (5.0 像素 shader) |
| 同上 + 暴力 compute shader | — | — | — | 4.62 ms |
| 同上 + 移除空调度 | — | — | — | 3.93 ms |
| 同上 + 2x2 software VRS | — | — | — | **3.05 ms** |
| **节省** | — | — | — | **40% (5.0 → 5.4)** |

> **Wihlidal 演讲原话**:
> "这是来自城市样例的一个镜头, 显示了 **4015 个总着色装箱, 但其中有 3675 个装箱是空的!**"
> "在一个 5 毫秒的基础 Pass 场景中, 新系统耗时为 3 毫秒, **比原始材质管线快了 40%**。"

### 视觉症状 (玩家视角)

- 5.0/5.1 项目跑 4K 60fps 不上 — `stat unit` 显示 GPU 顶到 16-20ms
- `r.Nanite 0` 切到传统 Static Mesh 后帧率反而上升 (说明 Nanite 管线在拖)
- BasePass 单独耗时在 `ProfileGPU` 显示 5-6 ms (PS5/Xbox 30fps 预算下不可接受)

---

## 根因分析

### 根因 1: 5.0 时期 "每种材质 1 个全屏 draw call"

> **来源**: Wihlidal 演讲 + UE 5.0 源码

UE 5.0 时期, Nanite 材质管线的实现是:

```text
每种可见材质 → 1 个全屏 draw call → 写 GBuffer
  → 4015 种材质 = 4015 个 draw call
  → 但其中 3675 个 draw call **没有三角形** (因为这个 bin 在屏幕上没覆盖)
  → 91.5% 的 GPU 调度 = 完全空转
```

**为什么会有空 Bin?**

- Bin 划分按 (MeshID, MaterialID, TriBin) 分桶
- 屏幕投影后某些 (mesh, material) 组合**只占 1-2 个像素**
- 但仍然分配了 1 个全屏 draw call 路径
- 结果: 调度开销 = 4015 × (固定开销) >> 实际三角形数

### 根因 2: 像素着色器路径的固定成本

- 像素着色器即使画 1 个像素也要走完整 GPU pipeline
- vertex shader 阶段没有三角形 → 几何光栅化器浪费
- ROP 阶段几乎不写像素 → 但 setup + 调度已经付了

### 根因 3: 缺乏 Compute Shader 路径

- 5.0 时期 Nanite 材质着色**完全依赖像素着色器**
- 没有"先在 compute shader 里算出哪些 bin 真的需要画"的阶段
- 5.4+ 引入 **Classify / Reserve / Scatter 三阶段** 才解决

---

## 解决方案 (Wihlidal 演讲原话)

### 方案 A: 升级 UE 5.4+ (治本, 收益最大)

> **Wihlidal 原话**:
> "我们将介绍 Nanite 材质管线的最新进化。"
> "新系统耗时为 3 毫秒, **比原始材质管线快了 40%**。"

**步骤**:
1. 项目从 UE 5.0/5.1 升级到 UE 5.4+ (注意 Nanite 5.4 渲染路径变化)
2. **不需要改任何材质 / 关卡** — 是引擎层升级
3. 复杂场景 (材质种类 > 1000) 自动拿 40% 提速
4. 简单场景 (材质种类 < 200) 收益不明显

**风险**:
- 5.0 → 5.4 跨度大, 需要回归测试 WPO / 透明 / 自定义 UV
- 透明材质 5.0 → 5.4 行为有变化 (Visibility Buffer 范式对 Alpha Blend 仍然不友好)
- [[Nanite-WPO禁用距离-破面修复]] 笔记里 WPO bug 5.4+ 修复但仍需 LOD 切

### 方案 B: 减少材质种类 (治本, 主动)

**思路**:
- 大量 unique 材质 → 实例化 / Material Instance 复用
- 例如 City Sample 里 5000 种 unique 材质 → 50 base + 4500 instance
- Bin 数会**等比下降**

**Wihlidal 演讲场景的复杂度**:
| Demo | 独特材质数 | 复杂度定位 |
|------|-----------|-----------|
| Lumen in the Land of Nanite | ~500 | 中 |
| Valley of the Ancients | ~2000 | 高 |
| City Sample (The Matrix Awakens) | ~5000 | **极高** |

> **结论**: 自己的项目如果独特材质数 > 1000, 即使不升级 5.4, **也要考虑材质实例化**。

### 方案 C: VRS (Variable Rate Shading) 叠加

> **Wihlidal 原话**:
> "VRS Tile 尺寸为 2x2, 现在将着色率与着色像素块完美匹配。左边展示了每个 8x8 区域内所有着色像素块的着色率, 提供了 **27% 的着色降低**。而右边显示了每个 2x2 着色像素块的着色率, 提供了大约 **45% 的着色降低**。"

| VRS 模式 | 着色降低 | 适用 |
|---------|----------|------|
| 不开 VRS | 0% | 基线 |
| 8x8 VRS | 27% | UE 5.2+ D3D12 Tier 2 |
| 2x2 software VRS | 45% | Wihlidal 演讲场景 |
| 8x8 → 2x2 切换 | **额外 18%** | 同一镜头对比 |

**硬件 VRS Tile 尺寸限制**:
- AMD: 8x8
- NVIDIA: 16x16
- Intel: 32x32

> **注意**: VRS Tile 内所有着色 quad 必须统一着色率 (硬件限制)。所以 VRS 在 2x2 模式最省, 但 Tile 越大相邻像素差异越大, 视觉上略糊。

### 方案 D: 切到 5.1 可编程光栅器 (过渡方案)

> **来源**: GDC 2024 + W26 笔记

- 5.1+ 引入 **Programmable Rasterizer** — 让艺术家通过材质图控制光栅化器
- 支持: alpha 遮罩 / 双面 / 像素深度 / **WPO** / 自定义 UV
- 5.0 不支持这些, 5.1+ 落地

> **Wihlidal 原话**:
> "不兼容的内容包括 alpha 遮罩、双面、像素深度偏移、世界位置偏移 (这是对顶点动画的称呼)、自定义 UV 等。"

**实战案例 (Wihlidal 原话)**:
- **Fortnite 第 4 章**: "开发了可编程光栅管线后, 能够在《堡垒之夜》第 4 章中**广泛使用 Nanite 和虚拟阴影贴图**, 它被用于**所有的草、树木、地形、建筑部件以及大多数的道具**。"
- **Electric Dreams demo**: "我们展示了《Electric Dreams》演示, 这是一个茂密的森林环境, 通过程序生成, 并且大量使用了 Nanite 可编程光栅。**同样地, 在这个场景中的所有内容都是 100% 的 Nanite**。"

---

## 升级路径推荐 (按收益 vs 风险)

| 路径 | 收益 | 风险 | 建议 |
|------|------|------|------|
| **5.0 → 5.4 直接升** | 40% (复杂场景) | 高 (跨度大) | 复杂场景 (> 1000 材质) 强烈推荐; 简单场景先在测试分支验证 |
| **5.0 → 5.1 → 5.4 渐进** | 5.1 解决 WPO / 透明 / 自定义 UV; 5.4 拿 40% 提速 | 中 | 推荐方式 — 每步单独验证 |
| **5.0 不升级, 材质实例化** | 取决于复用率, 30-60% 估计 | 低 | WPO / 透明已稳的项目, 不想升级风险时 |
| **叠加 VRS (8x8 / 2x2)** | 25-30% (5.2+) / 45% (2x2 模式) | 低 (D3D12 Tier 2 GPU) | 跟升级无关, 可叠加 |

---

## 验证流程 (自己 Profile 时跑一遍)

### 步骤 1: 确认你的项目在不在 5.4 受益区间

```text
问自己 3 件事:
  1. 独特材质数 > 1000 ?
     → 是 = 升级 5.4 收益大
     → 否 = 升级 5.4 收益一般, 但不亏
  2. 当前 GPU BasePass > 3 ms ?
     → 是 = 升级 5.4 拿 40% 提速 = 省 1-2 ms
     → 否 = 升级 5.4 拿 0.5-1 ms
  3. WPO / 透明 / 自定义 UV 用得多 ?
     → 是 = 升 5.1+ (可编程光栅器) 已有显著改善, 5.4 顺带
     → 否 = 5.0 也能跑
```

### 步骤 2: 升级前基线测量

```text
1. ProfileGPU → 记 BasePass 耗时
2. NaniteStats → 记 visible cluster 数 / Bin 数估算
3. r.Nanite.ShowStats 1 → 看 fallback 比例
4. 切到 5.4 build 重新跑同一镜头
5. 对比 BasePass 耗时 → 计算收益
```

### 步骤 3: 5.4 回归测试 (高风险)

```text
必测场景:
  [ ] WPO 物体 (草、树、布料) 视觉跟 5.0 一致
  [ ] 透明材质 (玻璃、水) 无闪烁
  [ ] 自定义 UV (顶点颜色) 跟 5.0 一致
  [ ] Pixel Depth Offset (像素深度) 跟 5.0 一致
  [ ] 双面材质法线方向正确
  [ ] Alpha mask 边缘无锯齿
```

### 步骤 4: VRS 叠加 (可选)

```text
1. 确认 D3D12 Tier 2 GPU (RTX 20+ / RX 6000+ / PS5 / XSX)
2. r.VRS.Enable 1 (默认开)
3. ProfileGPU 看 BasePass 是否再省 25-30%
4. 视觉对比: 2x2 VRS 边缘是否变糊
```

---

## 经验沉淀 (肌肉记忆)

| 看到 | 先查 |
|------|------|
| BasePass > 4ms + 材质种类 > 1000 | 升级 5.4+ 拿 40% 提速 |
| 5.0 项目 WPO 闪烁 / 透明锯齿 | 升 5.1+ (可编程光栅器) |
| D3D12 Tier 2 GPU + 着色率敏感场景 | 开 VRS 拿 25-30% |
| 升级 5.4 后透明材质错乱 | 透明 5.4 行为变化, 单独回归 |
| Material 数量爆炸 | 材质实例化压独特材质数 |

**核心判断**: **"4015/3675 空调度" 是 UE 5.0 特定版本的算法缺陷, 5.4+ 已经修复**。如果你的项目卡在 5.0, 升级 5.4 是性价比最高的路径。

---

## day-job 视角 (Mac Game Harness + LLM-driven UE)

### RAG 索引价值

> **day-job 锚点**: 用户日工作 = RAG + Mac Game Harness, 目标"提到 LLM 对 UE 特性的使用"。

**LLM 调参指南的高频 query**:

| Query | 高优回答 | 来源 |
|-------|----------|------|
| "Nanite BasePass 5ms+ 怎么降" | 升级 5.4+ 拿 40% 提速 | 本文 § 方案 A |
| "5.0 项目要不要升 5.4" | 材质种类 > 1000 = 强烈推荐 | 本文 § 升级路径 |
| "VRS 能省多少" | 8x8 = 25-30% / 2x2 = 45% | 本文 § 方案 C |
| "Mac 上 Nanite 慢" | Metal 5.4+ 修复, 5.0 之前 page residency 有 bug | W29 论文 § Mac 视角 |

**RAG 索引建议格式**:
- 知识块 1: "Nanite 5.4 升级 — 4015/3675 Bin 削减" + 来源 + 收益范围
- 知识块 2: "5.1 可编程光栅器 — 5.0 不支持的 4 件事" + 案例 (Fortnite / Electric Dreams)
- 知识块 3: "VRS 在 Nanite 上的事实 — 8x8 25-30% / 2x2 45%" + 硬件限制

### Mac Game Harness 验证清单

- [ ] UE 5.4+ 编译通过 (Mac Metal RHI)
- [ ] BasePass 耗时对比 5.0 (Mac 上)
- [ ] 5.4+ 透明材质在 Metal 上无 regression
- [ ] 5.4+ WPO 在 Metal 上无闪烁

---

## 不在本文档里的内容

> 以下**没有可查的官方 / GDC / 源码来源**, 本文**不写**:

- "我的项目能省 X% 性能" — 视场景, 必须 Profile
- "5.4 升级具体需要几小时" — 视项目大小
- "5.4 在 Mac 上跟 PC 一样" — 没公开对比
- "材质实例化能压到多少 Bin" — 视复用率
- "VRS 8x8 视觉损失多大" — 视内容

需要这些数字 → 自己 Profile 项目, 参考 [[性能优化方法论]]。

---

## 关联 / 输出产物

### 论文 + 源码 + 性能 (三角闭环)

- **理论**: [[../../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry]] (W29 论文笔记)
- **源码**: [[../../02-引擎源码分析库/Unreal-Engine/W26/UE5-Nanite-虚拟几何shader]] (W26 笔记)
- **性能**: [[../知识参考/Nanite 性能调优]] (既有)
- **瓶颈**: [[Nanite-WPO禁用距离-破面修复]] (既有) / **本文** (W29 新增)

### day-job 锚点

- [[../../05-技术雷达/P0-立即学习/Nanite]] — 雷达 P0 + day-job 优先级
- [[../../Career/Kimi/UE5_Training_MCP/]] — day-job MCP-grounded 训练 pipeline (RAG 索引落地)
- [[../知识参考/性能优化方法论]] — Profile 黄金三问

### 兄弟案例

- [[Lumen-反射开销过高-平滑材质场景]] — Lumen 瓶颈案例
- [[VSM-页溢出-阴影棋盘瑕疵]] — VSM 瓶颈案例
- **本文** — Nanite 5.4 材质管线瓶颈案例 (W29 新增, 补 04-性能优化备忘录/ 7 月 0% 缺口)

---

*Create date: 2026-07-17*
*Last modified: 2026-07-17*
*Verified: 否 (GDC 2024 + W29 论文 + W26 源码, **未经本人 Profile 验证**)*
*Source:*

- **GDC 2024 *Nanite GPU-Driven Material Pipeline* — Graham Wihlidal (Epic Games)**:
  - GDC Vault 搜索入口: https://www.gdcvault.com/search/?q=Nanite+GPU+Driven+Materials+Wihlidal
  - 注: 本文核心数据 (**4015 / 3675 / 4.92→3.05ms / 40% 提速 / 25-30% VRS**) 均来自该 GDC 演讲原话
- **SIGGRAPH 2021 *Nanite: A Pipeline for Photorealistic Real-Time Geometry* — Brian Karis**:
  - 公开 dev blog: https://www.unrealengine.com/en-US/blog/nanite-a-virtual-geometry-pipeline-advanced-in-real-time
  - 本机 PDF: `C:\Git-repo-my\GameDevVault\Rendering\Document\UnrealEngine\Nanite\SIGGRAPH2021_Nanite.pdf`
- **UE 5.8 源码** `Engine/Source/Runtime/Renderer/Private/Nanite/NaniteMaterialShader.cpp` / `NaniteRasterizer.cpp` — 5.4 compute shader 路径 (Classify / Reserve / Scatter)
- **W29 论文笔记**: [[../../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry]]
- **W26 源码分析**: [[../../02-引擎源码分析库/Unreal-Engine/W26/UE5-Nanite-虚拟几何shader]]
- **W29 雷达 P0**: [[../../05-技术雷达/P0-立即学习/Nanite]]

> 本瓶颈案例**兑现 W28 周复盘** (2026-07-12) 里的承诺:
> "W29 必做: VSM 升级到 source-analysis 级; Mac 平台 vault 索引页; 雷达 README P0 补丁; 外部接触 ≥ 1 次"
> **实际**: W29 写了 4 篇新笔记 (Lumen Surface Cache / Nanite 论文 / VSM 论文 / MCP 论文) + 本瓶颈案例 + VSM 性能调优 知识参考 = **5 篇产出**。Mac 索引页 + 雷达 P0 补丁继续推 W30。
