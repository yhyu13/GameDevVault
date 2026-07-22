---
tags: [perf/GPU, perf/culling, perf/VSM, perf/待验证]
aliases: [VSM Page Allocation 调优, BuildPageAllocations 3227, VSM 30+ CVar, VSM MaxPhysicalPages 4096, VirtualShadowMapArray 调优]
---

# VSM Page Allocation (BuildPageAllocations) 调优 — 30+ CVar 全表 + Page 预算诊断

| 字段 | 内容 |
|------|------|
| **现象** | 大世界 VSM 阴影 page 预算不够 / 频繁 evict / 远处阴影闪烁 — 根因在 `FVirtualShadowMapArray::BuildPageAllocations` (`VirtualShadowMapArray.cpp:3227`) + 30+ CVar 全部 hook 在 `VirtualShadowMapArray.cpp` 284KB 主文件 |
| **发现日期** | 2026-07-23 (W30) |
| **项目/场景** | UE5 大世界 (多光源 / 高分辨率阴影 / 大量 WPO 对象) / 4 类光源 (Directional/Spot/Point/Rect) 全部启用 |
| **平台** | PC (DXR) / PS5 / XSX / Mac (Metal 5.4+) |
| **严重程度** | 严重 (默认 4096 pages × 128×128 × 2 bytes ≈ 256 MB; **典型项目 2-4 GB atlas 显存**) |
| **来源类型** | W30 源码分析 [[../../02-引擎源码分析库/Unreal-Engine/W30/UE5-VSM-Page-Table-源码分析]] (20 KB, 30+ CVar 全表) + W29 VSM 性能调优 [[VSM 性能调优]] + W29 瓶颈 [[VSM-页溢出-阴影棋盘瑕疵]] + UE 5.8 源码 `VirtualShadowMapArray.cpp` |

> **声明**: 本瓶颈案例**只整理 W30 源码分析的 30+ CVar 全表 + `BuildPageAllocations:3227` 函数机制 + `RenderVirtualShadowMapsNanite:4218` 双路径分流**, **不主张"自己项目占用 X MB"** — 必须在自己的目标场景下用 `ProfileGPU` + `r.Shadow.Virtual.ShowStats` 复测。
>
> **跟 [[VSM-页溢出-阴影棋盘瑕疵]] (既有) 的区别**: 既有是 W28 时期"症状 + 排查"高层方法论; 本篇是 W30 源码级 **30+ CVar 全表 + `BuildPageAllocations` 函数机制**。两篇互为"高层+微观"双层覆盖。

---

## 来源与可信度

| 来源 | 类型 | 关键事实 |
|------|------|----------|
| W30 源码分析 [[../../02-引擎源码分析库/Unreal-Engine/W30/UE5-VSM-Page-Table-源码分析]] | [D] 源码笔记 | **`VirtualShadowMapArray.cpp:3227` `BuildPageAllocations`** + 30+ CVar 全表 + `BeginMarkPages:2516` + `RenderVirtualShadowMapsNanite:4218` + `RenderVirtualShadowMapsNonNanite:4389` + `UpdateHZB:4829` + 4 类光源路径分流 + `VirtualShadowMapCacheManager` 104 KB 跨帧缓存 |
| W29 VSM 性能调优 [[VSM 性能调优]] | [D] 笔记 | VSM 基础架构参数 + Page 预算 + Clipmap 调度 + MegaLights 5.4+ 集成 + Lumen/Nanite 同源 |
| W29 VSM 瓶颈 [[VSM-页溢出-阴影棋盘瑕疵]] | [D] 笔记 | 症状 + 排查流程 + 7 套方案 |
| UE 5.8 源码 `Engine/Source/Runtime/Renderer/Private/VirtualShadowMaps/VirtualShadowMapArray.cpp` | [D] 源码 | 284 KB 主文件 + 30+ CVar 全部 `*.cpp` 锚定 |
| UE 官方 *Virtual Shadow Maps* 文档 | [D] 官方 | 16k×16k 虚拟分辨率 + 128×128 page + MaxPhysicalPages 默认 4096 (5.4+ 升级, 5.3 之前是 2048) |

> **本文性质**: 公开资料 + W30 源码整合, **未经本人 Profile 验证**。

---

## 现象描述

### 触发条件

- 场景 **Mesh 总数 > 5 万** (大世界 / World Partition)
- VSM 启用 (UE5 默认)
- 4 类光源 (Directional/Spot/Point/Rect) 全部启用
- 平台显存 ≤ 8 GB (PS5 / XSX 基础款 / Mac 8GB 集成显卡)

### 视觉 / Profile 表现

打开 `ProfileGPU` 找以下通道:

```text
VSM.MarkPages            ← BeginMarkPages:2516
VSM.BuildPageAllocations ← ★ 3227 性能瓶颈
VSM.Render.Nanite        ← 4218
VSM.Render.NonNanite     ← 4389
VSM.HZB                  ← 4829
```

**典型大世界 Profile 表现** (W30 源码分析 §"内存布局" 原文):

| 场景 | MaxPhysicalPages | 单方向光 atlas 显存 | 4 类型光源总和 |
|------|-----------------|---------------------|---------------|
| 小 (默认) | 2048 (5.3-) | 64 MB | ~ 256 MB |
| 中 (大世界) | 4096 (5.4+) | **256 MB** | ~ 1 GB |
| **大 (City Sample 级)** | **4096** | **256 MB** | **2-4 GB** |

> **W30 源码分析原文**:
> ```
> constexpr int32 MaxPhysicalPages = 4096;
> constexpr int32 PhysicalPageSize = 128;
> constexpr int32 PageMipLevels = 4;
> // 4 light types × 4096 pages × 128×128 × 2 bytes (深度) ≈ 1 GB
> // 实测典型项目: 2-4 GB atlas
> ```

### 显存超限症状

| 平台 | 症状 |
|------|------|
| **PS5 基础款 (10 GB 可用)** | 帧率从 60 → 30; `stat gpu` 显示 VSM 通道警告 |
| **XSX 基础款 (8 GB 可用)** | 同上 + 可能 RHI 触发 "out of memory" 警告 |
| **Mac 8GB 集成显卡** | 严重 — 集成显存共享, VSM atlas 不可压缩, **直接 OOM 风险** |
| **PC 8GB 显存** | BasePass 帧时间不规则 (某些帧卡 5-10ms) |

### 性能瓶颈症状

- `r.Shadow.Virtual.ShowStats 1` 显示 **Pages 接近 Max Pages** → BuildPageAllocations 频繁 evict
- `NaniteStats VSM_Directional` 显示 **Candidates / Visible Clusters 接近上限**
- 镜头切换瞬间: **BuildPageAllocations 1 帧延迟 → 远处阴影闪烁** (`FPhysicalPageMetaData.last used frame` 反馈)
- 大量 WPO 物体: **page 失效雪崩** → `r.Shadow.Virtual.DeferredInvalidationBudget` 触发

---

## 根因分析 (W30 源码 `VirtualShadowMapArray.cpp:3227`)

### 根因 1: `BuildPageAllocations:3227` 物理分配核心

> **来源**: W30 源码分析 §"关键函数"

```cpp
// VirtualShadowMapArray.cpp:3227 - 5.4+ 关键函数
FVirtualShadowMapArray::BuildPageAllocations
{
    // 输入: BeginMarkPages:2516 标记的 page 列表
    // 输出: 实际分配的物理 page 索引
    // 算法: LRU evict + page lock + 复用
    // 反馈: FVirtualShadowMapCacheManager 跨帧 (104 KB)
};
```

> **关键事实** (W30 源码分析 §"关键函数" 原文):
> "`FVirtualShadowMapArray::BuildPageAllocations` ★★ Page 分配核心 — 论文 'page 预算不够' 根因"

### 根因 2: 默认 4096 page 池在 5.4+ 翻倍 (W30 升级版发现)

> **W30 源码分析 §"内存布局" 原文**:
> ```
> constexpr int32 MaxPhysicalPages = 4096;  // r.Shadow.Virtual.MaxPhysicalPages
> ```

> **W29 知识参考 [[VSM 性能调优]]**:
> "`MaxPhysicalPages` (Directional) 默认 **2048**"

> **结论**: **5.4+ 升级后默认 page 预算翻倍** (2048 → 4096) — 跨版本调参要查实际源码, 不能依赖旧文档

### 根因 3: 4 类光源路径分流不均 (W30 源码 §"4 类光源路径")

| Light Type | Page Table 路径 | 代码入口 | 默认 page 数 |
|------------|-----------------|----------|--------------|
| **Directional** | Clipmap (8-16 layers) | `FVirtualShadowMapClipmap` | 4096 |
| **Spot** | Single page pool | `RenderVirtualShadowMapsNanite` | 共享 |
| **Point** | 6 面 cube | `RenderVirtualShadowMapsNanite` | 共享 |
| **Rect** | Single page pool | `RenderVirtualShadowMapsNonNanite` | 共享 |

> **关键观察** (W30 源码分析 §"4 类光源路径"):
> - Directional Light 用 **clipmap** (8-16 层 cascade)
> - Spot/Point/Rect 共享 single page pool
> - **4 类型光源总显存 = 2-4 GB** (典型项目)

### 根因 4: `RenderVirtualShadowMapsNanite:4218` vs `NonNanite:4389` 双路径分流

> **来源**: W30 源码分析 §"线程视角: 5 个 RT 阶段"

```cpp
// VirtualShadowMapArray.cpp:4218 - Nanite 路径
FVirtualShadowMapArray::RenderVirtualShadowMapsNanite
{
    // VisBuffer + Visibility Buffer 路径
    // 5.4+ 默认开启, 跟 Nanite 5.4 Bin 合并协同
    // page 预算消耗: 4096 × 128×128
};

// VirtualShadowMapArray.cpp:4389 - Non-Nanite 路径
FVirtualShadowMapArray::RenderVirtualShadowMapsNonNanite
{
    // 传统 mesh 路径
    // r.Shadow.Virtual.NonNaniteCulledInstanceAllocationFactor=0.2 控制
    // 5.0 时期默认走这条
};
```

> **关键事实**: **5.4+ 默认走 Nanite 路径** — 配合 W30 Nanite CullRaster 的 5.4 Bin 合并, 整套 5.4 升级收益叠加

### 根因 5: `UpdateHZB:4829` 跨帧缓存 104 KB

> **来源**: W30 源码分析 §"Pass 视角"

```cpp
// VirtualShadowMapCacheManager.cpp - 104 KB 跨帧 page residency
FVirtualShadowMapCacheManager {
    // FPhysicalPageMetaData.last used frame
    // 反馈: 1 帧延迟
    // 触发条件: page 不被 mark 超过 N 帧 → evict
};
```

> **关键观察**: 跨帧缓存 104 KB 是 Page Evict 决策的基础, 反馈 1 帧延迟是**所有 page evict 雪崩的统一根因**

---

## 解决方案 (按 W30 源码分析 30+ CVar 全表分类)

### 方案 A: Page 预算调节 (核心调优)

```ini
; 默认 4096 (5.4+ 升级后, 5.3 之前 2048)
; 单方向光 4096 × 128×128 × 2 bytes ≈ 256 MB
r.Shadow.Virtual.MaxPhysicalPages=4096

; 缩 page 预算 (大世界显存压力)
r.Shadow.Virtual.MaxPhysicalPages=2048   ; -50% 显存
```

**副作用**: 触发 LRU evict 频率增加, **远处阴影闪烁**

### 方案 B: Clipmap 调度 (Directional Light 专属)

```ini
; 决定每帧 mark 多少 page
r.Shadow.Virtual.DeferredInvalidationBudget=1   ; 默认 1, 改 10 加快 invalidation
r.Shadow.Virtual.MarkUseFroxels=0              ; 实验性, 默认关
r.Shadow.Virtual.MarkPixelPages=1              ; 标记 pixel-level page (默认 1)
r.Shadow.Virtual.MarkPixelPagesMipModeLocal=0  ; Local light mip mode
r.Shadow.Virtual.MarkCoarsePagesLocal=1        ; 标记 coarse page (Local) - 默认 1
r.Shadow.Virtual.CoarsePagesIncludeNonNanite=1 ; coarse page 包含 Non-Nanite
```

### 方案 C: Nanite 集成 (5.4+ 默认开, W30 升级版)

```ini
; 5.4+ 默认开启, 走 VisBuffer 路径
r.Shadow.Virtual.Nanite.AllowTessellation.Directional=0  ; 默认 0
r.Shadow.Virtual.Nanite.AllowTessellation.Local=0        ; 默认 0
r.Shadow.Virtual.NonNaniteVsmUseHzb=0                   ; Non-Nanite VSM 用 HZB
r.Shadow.Virtual.NonNaniteCulledInstanceAllocationFactor=0.2  ; Non-Nanite culled instance factor
r.Shadow.Virtual.NonNaniteMaxCulledInstanceAllocationSize=64  ; Non-Nanite max culled instance size
```

### 方案 D: 第一人称 / DOF 优化

```ini
r.Shadow.Virtual.FirstPersonPixelRequestBias=0.0
r.Shadow.Virtual.FirstPersonPixelRequestLevelClamp=0
r.Shadow.Virtual.MaxDOFResolutionBias=0
```

### 方案 E: Page 边膨胀 (修漏光, 5% 性能成本)

```ini
r.Shadow.Virtual.PageDilationBorderSize.Directional=0.0  ; 默认 0, 改 1-2 修漏光
r.Shadow.Virtual.PageDilationBorderSize.Local=0.0
```

### 方案 F: HZB 构建 (5.4+ 默认开)

```ini
r.Shadow.Virtual.BuildDynamicHZB=1   ; 默认 1, 改 0 禁用 (省 page 预算, 远景阴影质量下降)
```

### 方案 G: One Pass Projection

```ini
r.Shadow.Virtual.OnePassProjectionMaxLights=8   ; 一次 projection 最大 light 数, 默认 8
r.Shadow.Virtual.DoNonNaniteBatching=1         ; Non-Nanite batch, 默认 1
r.Shadow.Virtual.CullBackfacingPixels=1        ; 剔除背面像素, 默认 1
```

### 方案 H: 调试 CVar (排查用)

```ini
r.Shadow.Virtual.ShowStats=0                 ; 默认 0, 改 1 显示 stats UI
r.Shadow.Virtual.ShowClipmapStats=0          ; 默认 0, 改 1 显示 clipmap stats
r.Shadow.Virtual.ShowLightDrawEvents=0       ; 默认 0
r.Shadow.Virtual.ShowStatsSections=(empty)   ; stats section filter
r.Shadow.Virtual.DebugDrawFroxels=0          ; 绘制 Froxel (debug)
r.Shadow.Virtual.DebugDrawFroxelRange=0      ; Froxel 范围 (debug)
r.Shadow.Virtual.Enable=1                    ; VSM 启用 (默认 1, 改 0 完全禁用 VSM 排查)
```

---

## 升级路径推荐 (按收益 vs 风险, W30 升级版)

| 路径 | 收益 | 风险 | 建议 |
|------|------|------|------|
| **5.0 → 5.4 升级** | Nanite 路径默认开 + 5.4 Bin 合并 + page 预算翻倍 | 中 (跨度大) | **大世界场景强烈推荐** |
| **MaxPhysicalPages 翻倍** | 4096 → 8192 (256 MB → 512 MB 单方向光) | 显存 ×2 | 显存还够时 |
| **MaxPhysicalPages 减半** | 4096 → 2048 (256 MB → 128 MB) | 远处阴影闪烁 | Mac 8GB / 显存不够时 |
| **关闭 Nanite 集成** | `r.Shadow.Virtual.Nanite.AllowTessellation.*=1` | 复杂场景性能下降 | 5.0 旧项目保留 |
| **BuildDynamicHZB=0** | 省 page 预算 | 远景阴影质量下降 | 显存极致紧张时 |

---

## 验证流程 (W30 源码分析补)

### 步骤 1: 确认 VSM 默认配置

```text
1. r.Shadow.Virtual.ShowStats 1
2. r.Shadow.Virtual.ShowClipmapStats 1
3. 看控制台输出:
   - MaxPhysicalPages: 4096 (5.4+) / 2048 (5.3 之前)
   - 当前页数 vs Max 页数
   - Evict 频率
4. r.Shadow.Virtual.LogUpdates 2
5. 看哪些 mesh 在疯狂失效
```

### 步骤 2: 量显存

```text
1. r.RHISetGPUCaptureOptions 1
2. RenderDoc 抓帧 → 看 VSM atlas 实际分配大小
3. stat RHI → 看 atlas 总占用
4. 计算: 4 类型光源 × 4096 pages × 128×128 × 2 bytes = 2 GB (典型)
```

### 步骤 3: 量性能

```text
1. ProfileGPU → VSM.BuildPageAllocations 通道耗时
2. 翻倍 MaxPhysicalPages → 是否触发 BuildPageAllocations 性能瓶颈
3. 翻倍 DeferredInvalidationBudget → 是否缓解 page 雪崩
```

### 步骤 4: 回归测试

```text
[ ] 阴影质量无明显下降 (远处大物体)
[ ] 镜头切换无 1-2 帧延迟
[ ] 大量 WPO 物体 (草/树) 无 page 失效雪崩
[ ] Directional Light 8-16 层 clipmap 正常工作
[ ] Mac 上无 OOM 警告 (Metal 5.4+ 修复 page residency)
```

---

## 经验沉淀 (肌肉记忆, W30 升级版)

| 看到 | 先查 |
|------|------|
| VSM atlas 总和 > 1 GB | 升 5.4+ + 减 MaxPhysicalPages |
| 帧率从 60 掉到 30 (大世界入口) | DeferredInvalidationBudget 改 10 |
| 镜头切换阴影错乱 | `r.Shadow.Virtual.Cache 0` 验证 |
| 阴影 + 大量树叶草 | Nanite 路径 + WPO 强制缓存 |
| 远景阴影噪点 | SMRT RayLengthScaleDirectional / MaxRayAngleFromLight |
| 5.4 vs 5.3 默认 page 数差 | 5.3 之前 2048, 5.4+ 4096 (W30 升级版) |

**核心判断** (W30 升级版):
- **`BuildPageAllocations:3227` 是 VSM 性能瓶颈的根因** — Page 预算不够时频繁 evict
- **5.4+ 默认 4096 pages** (W29 知识参考说的 2048 是 5.3 之前) — 跨版本调参要查实际源码
- **Nanite 路径默认开** — 配合 W30 Nanite CullRaster 5.4 Bin 合并, 整套 5.4 升级收益叠加

---

## day-job 视角 (Mac Game Harness + LLM-driven UE)

### RAG 索引价值

> **day-job 锚点**: 用户日工作 = RAG + Mac Game Harness, 目标"提到 LLM 对 UE 特性的使用"。

**LLM 调参指南的高频 query**:

| Query | 高优回答 | 来源 |
|-------|----------|------|
| "VSM atlas 占多少显存" | 4 类型光源 × 4096 pages × 128×128 × 2 bytes ≈ 2 GB | 本文 § 根因 3 |
| "VSM page 预算不够" | `r.Shadow.Virtual.MaxPhysicalPages` 翻倍 + DeferredInvalidationBudget 10 | 本文 § 方案 A + B |
| "VSM 5.4+ 默认 page 数" | **4096** (5.3 之前 2048) | 本文 § 根因 2 |
| "VSM BuildPageAllocations 在哪" | `VirtualShadowMapArray.cpp:3227` | 本文 § 根因 1 |
| "Mac 上 VSM 慢" | Metal 5.4+ 修复 page residency + 保守 MaxPhysicalPages | W30 源码 + W29 论文 |
| "VSM Nanite 集成" | 5.4+ 默认走 `RenderVirtualShadowMapsNanite:4218` | 本文 § 根因 4 |

**RAG 索引建议格式** (跟 W29 瓶颈 + 本文 形成"高层+微观"双层):
- 知识块 1: "VSM atlas 显存公式 — 4 类型光源 × 4096 pages × 128×128 × 2 bytes ≈ 2 GB (典型)"
- 知识块 2: "BuildPageAllocations:3227 是 VSM 性能瓶颈根因" + 30+ CVar 全表
- 知识块 3: "5.4+ vs 5.3 之前 page 预算对比 — 4096 vs 2048 (W30 升级版发现)"
- 知识块 4: "Mac Metal RHI 上 VSM — 5.4+ 修复 page residency + 保守 MaxPhysicalPages"

### Mac Game Harness 验证清单

- [ ] UE 5.4+ 编译通过 (Mac Metal RHI)
- [ ] VSM 4096 pages 默认能跑 (5.4+ Metal 修复 page residency)
- [ ] Mac 8GB 集成显卡: MaxPhysicalPages=2048 验证 (256 MB → 128 MB 单方向光)
- [ ] 验证 `BuildPageAllocations:3227` 性能可接受 (避免 page 雪崩)
- [ ] Directional Light clipmap 8-16 层在 Metal 上工作正常
- [ ] Profile GPU 一次: Insights → VSM 通道独立耗时

---

## 不在本文档里的内容

> 以下**没有可查的官方 / GDC / 源码来源**, 本文**不写**:

- "我的项目 VSM 具体占多少 MB" — 视光源数 + page 预算, 必须 Profile
- "5.4 → 5.6 page 预算是否改变" — 没公开 changelog 明确
- "Mac Metal 上 4096 pages 跟 D3D12 性能差多少" — 没公开对比
- "BuildPageAllocations 调优具体多少 ms" — 视场景, 必须 Profile
- "WPO 对 VSM page 预算影响系数" — 没公开数据
- "Clipmap 8 vs 16 层实际 page 占用" — 视场景, 没公开数据

需要这些数字 → 自己 Profile 项目, 参考 [[性能优化方法论]]。

---

## 关联 / 输出产物

### 双层覆盖 (W29 高层 + W30 微观)

| 层级 | 笔记 | 视角 |
|------|------|------|
| **高层 (W29, 既有)** | [[VSM-页溢出-阴影棋盘瑕疵]] | 症状 + 排查流程 + 7 套方案 |
| **知识参考 (W29, 既有)** | [[VSM 性能调优]] | VSM 基础架构 + Page 预算 + Clipmap + MegaLights 5.4+ 集成 |
| **微观 (W30, 本文)** | **[[VSM-Page-Allocation-BuildPageAllocations调优]]** | W30 源码 `BuildPageAllocations:3227` + 30+ CVar 全表 + 4 类光源路径分流 + 5.4+ vs 5.3 page 预算对比 |

### 三角闭环 (W29 + W30 全栈)

- **理论**: [[../../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] (W29)
- **源码 (宏观)**: (待补 W30+)
- **源码 (微观, W30)**: [[../../02-引擎源码分析库/Unreal-Engine/W30/UE5-VSM-Page-Table-源码分析]] (W30)
- **卡牌 (W30)**: [[../../02-引擎源码分析库/Unreal-Engine/W30/UE5-VSM-Page-Table-源码分析]] (HTML, 10 题) — 配套 W30 源码分析
- **性能 (知识参考)**: [[VSM 性能调优]] (W29) + [[../知识参考/虚拟页表范式-VSM-Nanite-Lumen-同源]] (W30 跨系统)
- **性能 (瓶颈, W28 既有)**: [[VSM-页溢出-阴影棋盘瑕疵]] (W28 高层)
- **性能 (瓶颈, W30, 本文)**: **[[VSM-Page-Allocation-BuildPageAllocations调优]]** (W30 微观)
- **跨系统整合**: [[../知识参考/虚拟页表范式-VSM-Nanite-Lumen-同源]] (W30 跨系统)

### day-job 锚点

- [[../../05-技术雷达/P0-立即学习/VSM]] — 雷达 P0 + day-job 优先级
- [[../../Career/Kimi/UE5_Training_MCP/]] — day-job MCP-grounded 训练 pipeline (RAG 索引落地)
- [[../知识参考/性能优化方法论]] — Profile 黄金三问

### 兄弟瓶颈案例

- [[Lumen-反射开销过高-平滑材质场景]] — Lumen 反射通道瓶颈 (W28 既有)
- [[Lumen-SurfaceCache-显存与带宽-大世界场景]] — Lumen Surface Cache 大世界瓶颈 (W29)
- [[Nanite-5.4-材质管线-空调度削减]] — Nanite BasePass 5ms+ 瓶颈 (W29 高层)
- [[Nanite-5.4-材质Bin合并-80percent削减]] — Nanite 5.4 Bin 合并 (W30 微观, 同批)
- [[MCP-Trust-4件套-性能开销-harness瓶颈]] — MCP Trust 开销 (W30, 同批)
- **本文** — VSM Page Allocation 调优 (W30 微观)

---

*Create date: 2026-07-23*
*Last modified: 2026-07-23*
*Verified: 否 (W30 源码分析 + W29 性能调优 + UE 5.8 源码 + UE 官方文档, **未经本人 Profile 验证**)*
*Source:*

- **W30 源码分析**: [[../../02-引擎源码分析库/Unreal-Engine/W30/UE5-VSM-Page-Table-源码分析]] — 30+ CVar 全表 + `BuildPageAllocations:3227` + `BeginMarkPages:2516` + `RenderVirtualShadowMapsNanite:4218` + `RenderVirtualShadowMapsNonNanite:4389` + `UpdateHZB:4829`
- **UE 5.8 源码**:
  - `Engine/Source/Runtime/Renderer/Private/VirtualShadowMaps/VirtualShadowMapArray.cpp` (284 KB) — 30+ CVar 主文件
  - `VirtualShadowMapCacheManager.cpp` (104 KB) — 跨帧 page residency
  - `VirtualShadowMapClipmap.cpp` (32 KB) — Directional Light 8-16 层 cascade
  - `VirtualShadowMapProjection.cpp` (38 KB) — Shadow projection
  - `VirtualShadowMapArray.cpp:3227` — **`FVirtualShadowMapArray::BuildPageAllocations`** (Page 分配核心)
  - `VirtualShadowMapArray.cpp:4218` — `RenderVirtualShadowMapsNanite` (5.4+ 默认路径)
  - `VirtualShadowMapArray.cpp:4389` — `RenderVirtualShadowMapsNonNanite` (5.0 时期路径)
- **W29 知识参考**: [[VSM 性能调优]] (VSM 基础架构参数 + Page 预算 + Clipmap 调度)
- **W29 瓶颈案例**: [[VSM-页溢出-阴影棋盘瑕疵]] (W28 高层症状 + 排查)
- **UE 官方文档**: *Virtual Shadow Maps - Advantages and Limitations*

> 本瓶颈案例**兑现 W29 周复盘** (2026-07-19) 里的承诺:
> "W30 性能记录再加 3 条" → W30 本批 (1 知识参考 + 3 瓶颈) = **4 篇新增**, 7月累计 **7 篇 (233%)**
> 特别**W30 升级版关键发现**: 5.4+ VSM `MaxPhysicalPages` 默认 **4096** (5.3 之前是 2048) — W29 知识参考需要更新
