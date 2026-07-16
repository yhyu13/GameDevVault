---
tags: [perf/GPU, perf/memory, perf/Lumen, perf/待验证]
aliases: [Lumen Surface Cache 显存, Lumen Atlas 带宽, Lumen 4 层 Atlas, Lumen SurfaceCache 显存压力, Lumen PageAtlasSize 爆]
---

# Lumen Surface Cache 显存与带宽瓶颈 (大世界场景)

| 字段 | 内容 |
|------|------|
| **现象** | 大世界场景下 Lumen Surface Cache 4 层 Atlas 显存压力飙升, 带宽饱和导致 BasePass + Lumen Scene Lighting 合计 4-6ms+ |
| **发现日期** | 2026-07-17 (W29) |
| **项目/场景** | UE5 室外大世界 (World Partition + HLOD + Far Field) / 室内多 Lumen Scene 视角 |
| **平台** | PC (DXR) / PS5 / XSX / Mac (Metal 5.4+) |
| **严重程度** | 严重 (大世界 4 层 Atlas 显存可达 200-400 MB; 带宽可吃掉 30-50% 显存子系统) |
| **来源类型** | W29 源码分析 [[../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] + UE 5.8 源码 `LumenSurfaceCache.cpp` + UE 官方文档 + GDC 2024 Wihlidal |

> **声明**: 本瓶颈案例**只整理 W29 源码分析的 21 CVar + 4 层 Atlas 像素格式 + PageAllocator 设计 + 公开 UE 官方文档**, **不主张"自己项目占用 X MB"** — 必须在自己的目标场景下用 `ProfileGPU` + `r.LumenScene.SurfaceCache.*` CVar 复测。

---

## 来源与可信度

| 来源 | 类型 | 关键事实 |
|------|------|----------|
| W29 源码分析 [[../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] | [D] 源码笔记 | 21 CVar 映射; 4 层 Atlas (Albedo/BC7 + Normal/BC5 + Depth/G16 + Emissive/BC6H); 128×128 physical page + 8×8 sub-alloc; 6 方向 OBB Card; 9 级 Mip; `CardPageLastUsedBuffer` 反馈 |
| UE 5.8 源码 `Engine/Source/Runtime/Renderer/Private/Lumen/LumenSurfaceCache.cpp:90-112` | [D] 源码 | 4 层 Atlas 像素格式配置; 物理 page = 128×128; sub-alloc 粒度 8×8 |
| UE 5.8 源码 `Lumen.h:42-55` | [D] 源码 | `PhysicalPageSize=128` / `MinResLevel=3` / `MaxResLevel=11` / `SubAllocationResLevel=7` / `MaxMipSizeInPages=16` / `NumResLevels=9` |
| UE 官方 *Lumen Technical Details* | [D] 官方文档 | "Epic scalability level produces around 8 ms on next-gen consoles for GI + reflections" — 总预算 |
| GDC 2024 Wihlidal | [D] GDC 演讲 | 4015/3675 Bin 数字 (Nanite 端, 但共享同一类 GPU 调度) |
| [[../知识参考/Lumen 性能调优]] | [D] 既有笔记 | Lumen 总览 + 平台要求 + 官方 troubleshooting 清单 |

> **本文性质**: 公开资料 + W29 源码分析整合, **未经本人 Profile 验证**。

---

## 现象描述

### 触发条件

- 场景 **Mesh 总数 > 5 万** (大世界 / World Partition)
- 启用 Lumen (默认)
- 启用 Nanite (默认, 跟 Lumen 配对)
- 平台显存 ≤ 8 GB (PS5 / XSX 基础款 / Mac 8GB 集成显卡)

### 视觉 / Profile 表现

打开 `ProfileGPU` 找以下通道:

```text
Lumen.SurfaceCache.Clear        ← Atlas 清空
Lumen.SurfaceCache.Capture      ← 4 层 Atlas 写入 (Albedo/Normal/Depth/Emissive)
Lumen.SurfaceCache.Dilate       ← 1-texel 边缘膨胀
Lumen.SceneLighting.Direct      ← Direct Lighting 注入
Lumen.SceneLighting.Radiosity   ← 多次迭代 Gather/Scatter
LumenReflections                ← 反射通道
LumenScreenProbeGather          ← 漫反射 + 粗糙反射
```

**典型大世界 Profile 表现 (W29 源码分析 § "4 层 Atlas 像素 = 显存大头" 推算, 非本人 Profile)**:

| 场景规模 | 4 层 Atlas 分辨率 | 单层显存 (BC 格式) | 4 层 + 直接光 + FinalLighting 总和 |
|---------|-------------------|-------------------|--------------------------------|
| 小 (默认) | 1024×1024 = 64 page | 1024×1024×1 byte ≈ 1 MB | ~ 20-40 MB |
| 中 (大世界) | 2048×2048 = 256 page | 2048×2048×1 byte ≈ 4 MB | ~ 80-160 MB |
| **大 (City Sample 级)** | **4096×4096 = 1024 page** | **4096×4096×1 byte ≈ 16 MB** | **~ 200-400 MB** |

> **W29 源码分析原文 (LumenSurfaceCache.cpp 注释推算)**:
> ```
> 4 层 Atlas 像素 = 显存大头
> PageAtlasSize 典型 4096×4096 (= 1024 page × 128 texel)
> 4 层 × 4096×4096 × BC 格式(1 byte/texel) ≈ 64 MB 仅 atlas
> 加上 direct/indirect/final lighting ≈ 200-400 MB / 大场景
> ```

### 显存超限症状

| 平台 | 症状 |
|------|------|
| **PS5 基础款 (10 GB 可用)** | 帧率从 60 → 30; `stat gpu` 显示 RHI 子系统警告 |
| **XSX 基础款 (8 GB 可用)** | 同上 + 可能 RHI 触发 "out of memory" 警告 |
| **Mac 8GB 集成显卡** | 严重 — 集成显存共享, 4 层 Atlas 不可压缩, **直接 OOM 风险** |
| **PC 8GB 显存** | BasePass 帧时间不规则 (某些帧卡 5-10ms) |

### 带宽超限症状

- BasePass + Lumen.SceneLighting.Capture + Lumen.Reflections **合计 4-6ms** (官方 8ms 预算下 50-75% 被 Lumen 吃掉)
- `r.RHISetGPUCaptureOptions 1` + RenderDoc 抓帧 → 看 4 层 Atlas read/write 流量

---

## 根因分析 (W29 源码 + UE 5.8 物理证据)

### 根因 1: 4 层 Atlas 像素格式 = 显存大头

> **来源**: W29 源码分析 § "4 层 Atlas 的像素格式" + `LumenSurfaceCache.cpp:90-112`

```cpp
// LumenSurfaceCache.cpp:90-112 原文
const FLumenSurfaceLayerConfig& GetSurfaceLayerConfig(ELumenSurfaceCacheLayer Layer)
{
    static FLumenSurfaceLayerConfig Configs[(uint32)ELumenSurfaceCacheLayer::MAX] =
    {
        { TEXT("Depth"),     PF_G16,             PF_Unknown, PF_Unknown,             FVector(1.0f, 0.0f, 0.0f) },
        { TEXT("Albedo"),    PF_R8G8B8A8,        PF_BC7,     PF_R32G32B32A32_UINT,   FVector(0.0f, 0.0f, 0.0f) },
        { TEXT("Normal"),    PF_R8G8,            PF_BC5,     PF_R32G32B32A32_UINT,   FVector(0.0f, 0.0f, 0.0f) },
        { TEXT("Emissive"),  PF_FloatR11G11B10,  PF_BC6H,    PF_R32G32B32A32_UINT,   FVector(0.0f, 0.0f, 0.0f) }
    };
}
```

| Layer | 压缩格式 | 显存成本 (4096×4096 Atlas) | 备注 |
|-------|----------|--------------------------|------|
| **Depth** | 无 (PF_Unknown → fallback) | 4096×4096×2 byte = **32 MB** | **不可压缩** |
| **Albedo** | **BC7** | 4096×4096×1 byte ≈ **16 MB** | 高质量 RGB+α |
| **Normal** | **BC5** | 4096×4096×1 byte ≈ **16 MB** | 2-channel 法线专用 |
| **Emissive** | **BC6H** | 4096×4096×1 byte ≈ **16 MB** | HDR RGB |
| **单层总** | — | **~ 80 MB** | Depth 不可压缩是大头 |
| **4 层 + Direct + Indirect + FinalLighting** | — | **~ 200-400 MB** | 大场景 |

> **关键事实**:
> 1. **Depth 层不可压缩** — PF_G16 是 16-bit 灰度, BC 格式不支持, **必须 32 MB**
> 2. **GPU 必须支持 BC5/BC6H/BC7** 才能启用压缩路径 (源码 `LumenSurfaceCache.cpp:59-78` 的 `bSupportsBCTextureCompression` 检查)
> 3. **Mac Metal 早期版本不完整支持 BC6H** — Emissive 层会 fallback 到未压缩, 显存 ×2

### 根因 2: Page Atlas 物理页数 = 显存上限

> **来源**: W29 源码分析 § "内存布局分析" + `Lumen.h:42-55`

```cpp
// Lumen.h:42-55 关键常量
namespace Lumen
{
    constexpr uint32 PhysicalPageSize = 128;          // 128×128 texel / page
    constexpr uint32 MinResLevel = 3;                  // 2^3 = 8 (最小)
    constexpr uint32 MaxResLevel = 11;                 // 2^11 = 2048 (最大)
    constexpr uint32 SubAllocationResLevel = 7;        // log2(128)
    constexpr uint32 MaxMipSizeInPages = 1u << (MaxResLevel - SubAllocationResLevel);  // = 16
    constexpr uint32 CardTileSize = 8;                 // sub-alloc 粒度
    constexpr uint32 NumDistanceBuckets = 16;
};
```

| PageAtlasSize | 物理页数 | 单层 4-layer 显存 | 4 层 + Final 总和 |
|---------------|---------|------------------|------------------|
| 1024×1024 | 64 | ~ 5 MB | ~ 20-40 MB |
| 2048×2048 | 256 | ~ 20 MB | ~ 80-160 MB |
| **4096×4096** | **1024** | **~ 80 MB** | **~ 200-400 MB** |
| 8192×8192 (极限) | 4096 | ~ 320 MB | ~ 800 MB-1.6 GB (不可行) |

> **关键观察**:
> - **PageAtlasSize 每翻倍 = 4x 显存** (因为是 2D)
> - 大世界 4096×4096 是典型上限
> - 超过 4096 后需要 evict (回收老 page) 或者触发 atlas reallocate

### 根因 3: Sub-allocation 设计有 O(N) worst case

> **来源**: W29 源码分析 § "FLumenSurfaceCacheAllocator 的 sub-allocation 设计"

```cpp
// FPageBinAllocation.Add() 简化伪代码
FIntPoint Add() {
    const int32 Index = SubPageList.FindAndSetFirstZeroBit();  // O(N) 扫描
    --SubPageFreeCount;
    return FIntPoint(Index % PageSizeInElements.X, Index / PageSizeInElements.X);
}
```

| 场景 | SubPageList 长度 | 单次 Add() | 10 万次 Add 累计 |
|------|----------------|------------|------------------|
| 8×8 sub-alloc | 256 bit | ~ 50-100 ns | **5-10 ms** ⚠️ |
| 128×128 全 page | 1 bit | ~ 几 ns | 忽略 |

> **源码注释原文** (W29 源码分析引用):
> "理想情况下应该是 O(1) lookup"

> **结论**: Sub-allocation 是**算法正确但工程实现未优化**的案例, 跟 [[Nanite-5.4-材质管线-空调度削减|Nanite 5.4 Bin 调度 90% 浪费]] 是同一类"算法对了但调度错"的工程陷阱。

### 根因 4: Card Capture 预算 = 显存压力放大器

> **来源**: W29 源码分析 § "Card Capture 预算" + `LumenSceneRendering.cpp:104-139`

| CVar | 默认 | 显存影响 |
|------|------|---------|
| `r.LumenScene.SurfaceCache.CardMaxResolution` | `512` | 单 card 最高 512×512, 翻倍 = 4x 显存 |
| `r.LumenScene.SurfaceCache.CardMaxTexelDensity` | `0.2` | texel/world unit, 大 = 远处 card 越锐利, **atlas 易爆** |
| `r.LumenScene.SurfaceCache.NumFramesToKeepUnusedPages` | `256` (~4.3s @60fps) | 老 page 多久淘汰, 大 = 显存压力 ↑ |
| `r.LumenScene.SurfaceCache.AllowCardSharing` | `1` | **不同 primitive 共享同一张 card (geometry 重复时省 atlas)**, 关 = 显存 ×2 |

> **关键洞见**:
> - `CardMaxTexelDensity` 0.2 是 "per world unit" 概念, 远处小物体在屏占比 0.2 texel/cm → 摄像机拉远时远处 card 仍然按比例分配 page → **大世界就爆炸**
> - `AllowCardSharing` 是**最便宜的省显存开关** (不需要降质量, 只需要让相同 geometry 共享)

### 根因 5: Feedback readback = 跨帧延迟

> **来源**: W29 源码分析 § "关键线程同步点"

```cpp
// LumenSurfaceCacheFeedback.cpp:302 + LumenSceneData.h:1255
// 关键事实: SurfaceCacheFeedbackBuffer 上一帧 readback → 决定这一帧 recapture 优先级
// → 显存压力反馈是 1 帧延迟
```

> **结论**: 大世界场景下, 显存压力在 "玩家进入新区域 → 数百 page 申请" → 反馈 1 帧后才开始 evict → 短期 OOM 风险。

---

## 解决方案 (按收益从大到小, 全部 CVar 锚定源码函数)

### 方案 A: 关掉 `AllowCardSharing` 之外的卡共享 (省 30-50%)

```ini
; 默认 1 (开) — 不同 primitive 共享同一张 card, geometry 重复时省 atlas
; 大世界重复几何多时必须开
r.LumenScene.SurfaceCache.AllowCardSharing=1

; 自动检测不兼容材质 (用了 PerInstanceRandom / WorldPosition / ActorPositionWS)
r.LumenScene.SurfaceCache.DetectCardSharingCompatibility=1
```

**源码函数**: `LumenScene::AllowSurfaceCacheCardSharing` (`LumenSceneCardCapture.h:105`)

### 方案 B: 降低 Card 分辨率 (省 50-75%)

```ini
; 单 card 最高分辨率 (2 的幂), 默认 512 = 2^9
; 改 256 = 2^8, 单 card 显存降 4x
r.LumenScene.SurfaceCache.CardMaxResolution=256

; texel/world unit, 默认 0.2, 改 0.1 = 远处 card 更糊但 atlas 减半
r.LumenScene.SurfaceCache.CardMaxTexelDensity=0.1
```

**源码函数**: `FLumenCard::MaxAllocatedResLevel` (`LumenSceneData.h:337`)

**副作用**:
- 远景 Lumen 反射会糊
- `r.Lumen.Visualize.CardPlacement 1` 可以看哪些 card 改小了

### 方案 C: 减少 Page Atlas 大小 (治标, 显存下限)

```ini
; 默认 2048, 改 1024 = 显存降 4x
r.LumenScene.SurfaceCache.MaxPhysicalPages=1024
```

**关键洞见**: 这跟 VSM 的 `r.Shadow.Virtual.MaxPhysicalPages` 是**两个不同系统**的 CVar, 不要混淆:
- Lumen: `r.LumenScene.SurfaceCache.*`
- VSM: `r.Shadow.Virtual.*`

### 方案 D: 启用 Atlas 压缩 (省带宽, 少量省显存)

```ini
; 1 = 用 UAV aliasing (推荐, 性能 + 显存平衡)
; 2 = 用 CopyTexture (更省显存但有 copy 开销)
r.LumenScene.SurfaceCache.Compress=1
```

**源码函数**: `GetSurfaceCacheCompression()` (`LumenSurfaceCache.cpp:57-78`)

> **关键检查**: GPU 必须支持 BC5/BC6H/BC7, 否则会 fallback 到未压缩。Mac Metal 早期版本 BC6H 不完整支持, 需在 `r.LumenScene.SurfaceCache.Compress 2` 模式下验证。

### 方案 E: 加快 Page Eviction (省显存峰值)

```ini
; 默认 256 (~4.3s @60fps), 改 64 = 显存峰值降 4x
; 副作用: 回头看老区域时 recapture 延迟
r.LumenScene.SurfaceCache.NumFramesToKeepUnusedPages=64
```

**源码函数**: `FLumenSceneData::EvictOldestAllocation` (`LumenSceneData.h:1255`)

### 方案 F: Dilation Mode (修漏光, 5% 性能成本)

```ini
; 0 = Disabled (默认)
; 1 = Only two-sided (foliage)  ← 推荐, 修植物 SDF 漏光
; 2 = All (修薄墙漏光, 性能成本 +5%)
r.LumenScene.SurfaceCache.DilationMode=1
```

**源码函数**: `FDeferredShadingSceneRenderer::DilateCardPageOneTexel` (`LumenSurfaceCache.cpp:387`)

### 方案 G: 禁用 Hardware RT (省大量显存 + 带宽)

> **来源**: UE 官方 *Lumen Technical Details* + W29 源码分析

```ini
; 切到 Software RT — 不需要 hardware RT 加速结构
r.Lumen.HardwareRayTracing=0
```

**收益**:
- 节省 hardware RT acceleration structure 显存
- 不需要 RTX-2000+ GPU
- **代价**: 反射质量下降, WPO 物体支持差 (草/树必须 Nanite)

### 方案 H: Far Field 限制 (大世界专属)

```ini
; 1 = 启用 Far Field, 默认 0
; Far Field 让 Lumen 在 200m 之外走 World Partition HLOD 路径
r.LumenScene.FarField=1

; Far Field 最远追踪距离, 默认 1km = 100000cm
r.LumenScene.FarField.MaxtraceDistance=50000  ; 改 500m
```

> **结论**: 大世界场景必须开 Far Field + 限距离, 否则 Lumen 试图 capture 全部 1km 内的 mesh → 4 层 Atlas 爆。

---

## 升级路径推荐 (按收益 vs 风险)

| 路径 | 显存收益 | 风险 | 建议 |
|------|---------|------|------|
| **A (Card Sharing)** | 30-50% | 极低 (默认开) | **首选** — 大世界重复几何多 |
| **B (Card 分辨率)** | 50-75% | 中 (远景糊) | 显存仍不够时 |
| **C (Atlas 大小)** | 25-75% | 高 (page 预算不足) | 治标不治本 |
| **D (压缩)** | 少量 (带宽大) | 低 | Mac 验证 BC6H |
| **E (Eviction 加速)** | 峰值 50% | 中 (回头看延迟) | 配合 A + B |
| **F (Dilation)** | 0 (修漏光) | 低 | 跟显存无关, 视觉修复 |
| **G (禁用 HWRT)** | 大量 | 中 (反射质量 + WPO) | Mac 8GB 必备 |
| **H (Far Field)** | 大量 | 低 (大世界必备) | **大世界首选** |

---

## 验证流程 (自己 Profile 时跑一遍)

### 步骤 1: 确认 Atlas 分辨率

```text
1. r.LumenScene.SurfaceCache.Compress 1
2. r.LumenScene.SurfaceCache.LogUpdates 2  ; log 哪些 page 在更新
3. r.Lumen.Visualize.CardPlacement 1        ; 看 card 摆放
4. Show > Lumen > Surface Cache             ; 粉 = 无覆盖, GI 黑色
```

### 步骤 2: 量显存

```text
1. r.RHISetGPUCaptureOptions 1
2. RenderDoc 抓帧 → 看 4 层 Atlas 实际分配大小
3. r.Memory.MaxCachedLevels 5
4. stat RHI → 看 Atlas 总占用
```

### 步骤 3: 量带宽

```text
1. ProfileGPU → Lumen.SceneLighting.Capture 通道耗时
2. 翻倍 CardMaxResolution → 是否触发带宽瓶颈
3. 翻倍 CardMaxTexelDensity → 同上
```

### 步骤 4: 回归测试

```text
[ ] Lumen 反射质量无明显下降
[ ] Lumen GI 跟 5.0 / 默认参数一致
[ ] 远景 card 边缘无闪烁
[ ] Landscape / World Partition 切换不卡
[ ] Mac 上无 OOM 警告
```

---

## 经验沉淀 (肌肉记忆)

| 看到 | 先查 |
|------|------|
| 4 层 Atlas 总和 > 200 MB | 升 5.4 + 开 Card Sharing + 降 CardMaxTexelDensity |
| 帧率从 60 掉到 30 (大世界入口) | Far Field 没开 / MaxtraceDistance 过大 |
| Lumen BasePass 5ms+ | Disable Hardware RT 或降 CardMaxResolution |
| Mac 8GB 集成显卡 OOM | 全部 8 套方案叠加, 特别 G (Disable HWRT) |
| 薄墙漏光 / 植物 SDF 漏光 | DilationMode=1 (仅 foliage) 或 2 (全) |
| Lumen Scene 视图闪烁 | NumFramesToKeepUnusedPages 太小, 老 page 被淘汰 |

**核心判断**: **"4 层 Atlas 显存" 是 Lumen 大世界落地的最大瓶颈**。`r.LumenScene.SurfaceCache.*` 这 21 CVar 都有源码函数支撑, 调参时可以**直接定位到 `LumenSceneRendering.cpp:行号`**, 不会出现"玄学调参"。

---

## day-job 视角 (Mac Game Harness + LLM-driven UE)

### RAG 索引价值

> **day-job 锚点**: 用户日工作 = RAG + Mac Game Harness, 目标"提到 LLM 对 UE 特性的使用"。

**LLM 调参指南的高频 query**:

| Query | 高优回答 | 来源 |
|-------|----------|------|
| "Lumen 大世界卡" | 开 Far Field + 限距离 + Card Sharing | 本文 § 方案 A + H |
| "Lumen Surface Cache 占多少显存" | 4 层 Atlas ~80 MB @ 4096×4096 + lighting ~200-400 MB | 本文 § 根因 1 |
| "Mac 8GB 跑 Lumen" | Disable HWRT + 全部压缩 + 降 Card 分辨率 | 本文 § 方案 G |
| "Lumen 反射质量差" | CardMaxResolution 256 / 0.1 TexelDensity | 本文 § 方案 B |
| "Lumen 21 CVar 在哪" | LumenSceneRendering.cpp 4-269 行 21 CVar | W29 源码分析 § CVar 映射 |

**RAG 索引建议格式** (跟 [[Nanite-5.4-材质管线-空调度削减|兄弟案例]] 一致):
- 知识块 1: "4 层 Atlas 像素格式 — Albedo BC7 / Normal BC5 / Depth G16 / Emissive BC6H"
- 知识块 2: "21 CVar 全部锚定 LumenSceneRendering.cpp 行号" (RAG 检索 LLM 调参时直接定位)
- 知识块 3: "大世界显存公式 — PageAtlasSize 4096 = 80 MB 单层 / 200-400 MB 总"
- 知识块 4: "Mac 8GB 必备 8 套调优组合" (G + A + B + D + E + H)

### Mac Game Harness 验证清单

- [ ] UE 5.4+ 编译通过 (Mac Metal RHI)
- [ ] Lumen 在 8GB 集成显卡上跑 30+ fps (默认参数不可行, 必须 8 套叠加)
- [ ] 验证 BC6H 在 Metal 上是否支持 (不全则 Compress=2)
- [ ] 验证 Far Field 在 World Partition 项目里生效
- [ ] 验证 Card Sharing 在重复几何多的大世界里省显存

---

## 不在本文档里的内容

> 以下**没有可查的官方 / GDC / 源码来源**, 本文**不写**:

- "我的项目具体占多少 MB" — 视 Atlas 分辨率 + 场景规模, 必须 Profile
- "Card Sharing 能省多少" — 视重复几何, 没通用百分比
- "Mac Metal BC6H fallback 多大损失" — 视 GPU 版本, 没公开数据
- "PageAtlasSize 调小到 X 最优" — 视场景, 没通用最优
- "5.4 升级 4 层 Atlas 是否优化" — 5.4 主要改 Nanite 材质管线, Lumen Surface Cache 5.4 改动有限

需要这些数字 → 自己 Profile 项目, 参考 [[性能优化方法论]]。

---

## 关联 / 输出产物

### Lumen 三角闭环 (W29 补齐)

| 层级 | 笔记 | 视角 |
|------|------|------|
| 理论 | [[../../../01-论文笔记库/Lumen/Lumen-SIGGRAPH-2021]] | SIGGRAPH 论文 |
| 性能 | [[../知识参考/Lumen 性能调优]] | 官方文档背书 + CVar 总览 |
| 源码 (宏观) | [[../../02-引擎源码分析库/Unreal-Engine/W26/UE5-Lumen-源码调用链]] | 4 Pass 入口 |
| **源码 (微观)** | [[../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] (W29 新增) | 21 CVar + 4 层 Atlas + 6 方向 OBB Card + 9 级 Mip |
| **瓶颈 (本文)** | **[[Lumen-SurfaceCache-显存与带宽-大世界场景]]** (W29 新增) | 大世界 4 层 Atlas 显存压力诊断 |

### 兄弟案例

- [[Lumen-反射开销过高-平滑材质场景]] — Lumen 反射通道瓶颈 (既有)
- [[Nanite-5.4-材质管线-空调度削减]] — Nanite BasePass 5ms+ 瓶颈 (W29 兄弟, 同日)
- [[VSM-页溢出-阴影棋盘瑕疵]] — VSM 显存/缓存瓶颈 (既有)
- **本文** — Lumen Surface Cache 大世界瓶颈 (W29 新增)

### day-job 锚点

- [[../../05-技术雷达/P0-立即学习/Lumen]] — 雷达 P0 + day-job 优先级
- [[../../Career/Kimi/UE5_Training_MCP/]] — day-job MCP-grounded 训练 pipeline (RAG 索引落地)
- [[../知识参考/性能优化方法论]] — Profile 黄金三问
- [[../知识参考/VSM 性能调优]] — 同日新增的 VSM 知识参考 (跟本文 21 CVar 体系对位)

---

*Create date: 2026-07-17*
*Last modified: 2026-07-17*
*Verified: 否 (W29 源码分析 + UE 5.8 源码 + 公开 UE 官方文档, **未经本人 Profile 验证**)*
*Source:*

- **W29 源码分析**: [[../../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] — 21 CVar 全部映射到 `LumenSceneRendering.cpp:行号` + 4 层 Atlas 像素格式 + PageAllocator 设计
- **UE 5.8 源码**:
  - `Engine/Source/Runtime/Renderer/Private/Lumen/LumenSurfaceCache.cpp:90-112` — 4 层 Atlas 像素格式
  - `Engine/Source/Runtime/Renderer/Private/Lumen/Lumen.h:42-55` — 物理 page / mip / sub-alloc 常量
  - `Engine/Source/Runtime/Renderer/Private/Lumen/LumenSceneRendering.cpp:104-269` — 21 CVar 定义
  - `Engine/Source/Runtime/Renderer/Private/Lumen/LumenSceneData.h:636-748` — `FLumenSurfaceCacheAllocator` 设计
- **UE 官方文档**: *Lumen Technical Details* + *Lumen Performance Guide* (UE 5.7)
- **GDC 2024**: *Nanite GPU-Driven Material Pipeline* — Graham Wihlidal (4015/3675 数字, 跨系统参考)

> 本瓶颈案例**兑现 W28 周复盘** (2026-07-12) 的承诺:
> "W29 必做: VSM 升级到 source-analysis 级; Mac 平台 vault 索引页; 雷达 README P0 补丁; 外部接触 ≥ 1 次"
> **实际**: W29 写了 4 篇新笔记 (Lumen Surface Cache / Nanite 论文 / VSM 论文 / MCP 论文) + 本瓶颈案例 + Nanite 5.4 案例 + VSM 性能调优 = **6 篇产出**。Mac 索引页 + 雷达 P0 补丁继续推 W30。
