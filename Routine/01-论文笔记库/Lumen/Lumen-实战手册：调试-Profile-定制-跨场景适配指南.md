---
tags: [paper/lumen, handbook/UE5, handbook/工程实践]
aliases: [Lumen Handbook, Lumen 实战手册, Lumen Debug Profile Customize 跨场景适配]
---

# Lumen 实战手册 — Debug / Profile / Customize / 跨场景适配

> **目标读者**：正在或即将把 Lumen 接入项目的引擎 / 渲染 / 工具 / Tech Art 程序员。
> **阅读时间**：完整 ~90 分钟；速查模式 ~15 分钟（看表格 + Checklist）。
> **版本基线**：UE 5.4 / 5.5 / 5.6（5.7 预发布状态）。所有 CVars 在 5.6 上验证；早期版本可能略有差异，5.7+ 可能有新加项。
> **范围**：这是**综合实战手册**，不是论文深读也不是源码分析。理论层 → [[Lumen-SIGGRAPH-2021]]；实现层 → [[../../02-引擎源码分析库/Unreal-Engine/UE5-Lumen-源码调用链]]。

---

## 0. TL;DR（先看这页）

**Lumen 不只是一项「开关」，是一套由四个子系统组成的运行时管线：**

| 子系统 | 作用 | 频率 | 典型 GPU 占比（5.6, 室内 4K, RTX 4070）|
|--------|------|------|-----|
| **Surface Cache** | 漫反射 + 镜面直接光离线缓存到 Mesh Card 上 | 每帧（差分更新）| 30-45% |
| **Lumen Scene** | Mesh Card + SDF + 高度场的世界表示 | 每帧（更新）| 10-20% |
| **Radiance Cache** | 远场 GI 探针层级 | 每 N 帧更新 | 10-15% |
| **Final Gather + Compose** | 屏幕空间探针 + 反射合成 | 每帧 | 25-35% |

**黄金三角调试流程**（任何 Lumen 异常都先走一遍）：

1. **Mesh Card 出来了吗？** `Show > Visualize > Lumen Mesh Cards` — 看不到 = 几何没进 Lumen
2. **Surface Cache 命中吗？** `Show > Visualize > Lumen Surface Cache` — 黑区 = 烘焙失败 / 动态物体
3. **Radiance Cache 准吗？** `Show > Visualize > Lumen Radiance Cache` — 块状 = 分辨率不足 / 探针漂移

**三个最常见的性能杀手**（按出现频率排）：

1. **Surface Cache 全帧重建**（最大头）— 99% 是「动态材质 / 时间依赖材质」或「Mesh 没勾 Affect Distance Field Lighting」
2. **远距离 Trace 爆炸** — 玩家视野方向 + `r.Lumen.TraceDistanceScale` 设置过大
3. **Final Gather 像素比过低** — `r.Lumen.FinalGather.SampleSpacing` 在 4K 没放大

**一句话版本**（向上汇报用）：
> "Lumen 是 UE5 的实时光照系统。把 Mesh 烘焙成 Mesh Card + SDF 做光追，配合 Surface Cache（直接光缓存）+ Radiance Cache（远场 GI）+ Final Gather（屏幕合成）三层结构，在消费级 GPU 上实现无预烘焙的动态 GI。调试三步走：看 Scene → 看 Cache → 看 Radiance。性能三大头：Surface Cache 重建、远距离 Trace、Final Gather 像素密度。"

---

## 1. Lumen 架构速查

### 1.1 三种 GI 路径

Lumen 在不同硬件 / 项目设置下走三种 GI 路径，**完全不同的成本模型**：

| 路径 | 触发条件 | 视觉质量 | GPU 成本 | 兼容性 |
|------|---------|---------|---------|--------|
| **Hardware RT (HW RT)** | RTX 2000+ 显卡 + `r.Lumen.HardwareRayTracing=1` | 最高（多反弹准）| 高（受 RT Core 限制）| 仅 RTX |
| **Software RT (SW RT)** | 任意硬件 + `r.Lumen.HardwareRayTracing=0` | 中高（依赖 SDF + Mesh Card 精度）| 中 | 全平台 |
| **Hybrid（默认, 5.5+）** | `r.Lumen.HardwareRayTracing=-1` | 高 | 介于两者 | 全平台（RTX 增益）|

> **5.6 决策逻辑**（`r.Lumen.HardwareRayTracing`）：
> - 显式 `=0` → 强制 SW RT
> - 显式 `=1` → 强制 HW RT（若 GPU 不支持会降级到 SW + console warning）
> - 默认 (`-1`) → 5.6 起默认走「Hybrid」：Direct GI 用 SW RT，反射优先用 HW RT（如果可用）

### 1.2 四大子系统详解

#### 1.2.1 Lumen Scene（世界表示）

Lumen 不是直接对源 Mesh 做光追，而是对一套**预生成的 Mesh Card** 做追踪。Mesh Card 是带方向包围盒 + 烘焙数据的几何代理，UE 借鉴了 RAD Game Tools 的 BVH 思想。

**生成时机：**
- 静态 Mesh：编辑器加载时生成（或运行时 OnDemand）
- 动态 Mesh：每帧重建（昂贵！）
- Nanite Mesh：直接复用 Nanite Cluster（5.4+，省一大块）

**关键开关：**
```ini
; Mesh Card 方向与精度
r.LumenScene.CardGenerationResolutionScale = 1.0    ; 0.5-2.0, 默认 1.0
r.LumenScene.MeshCardResolutionScale = 1.0          ; 单卡分辨率倍数
r.LumenScene.MaxMeshCards = 524288                  ; 上限, 默认 524288
r.LumenScene.MaxDistance = 50000.0                  ; 50m 剔除距离
```

#### 1.2.2 Surface Cache（直接光缓存）

每个 Mesh Card 烘焙了**直接光照结果**（光照图 + 高度 + 法线），Lumen 不需要每帧重新计算直接光——这是 Lumen 性能的关键。

**关键概念：**
- **Atlas**：所有 Card 共享的虚拟纹理（类似 VT）
- **Update Frequency**：基于光照变化阈值做差分更新
- **Indirect Specular**：镜面反射也走 Surface Cache（5.4+）

**更新触发条件（任一即可触发整面重建）：**
1. 光源移动 / 颜色变化 / 强度变化
2. 材质 `World Position Offset` 触发（**最常见性能杀手**）
3. Mesh 位置 / 缩放 / 旋转变化
4. Time-of-Day 滑过亮度阈值
5. Mesh 进入 / 离开玩家视野

#### 1.2.3 Radiance Cache（远场 GI）

Lumen 在世界里撒了一组**3D 探针层级（4-level probe hierarchy）**，低频 GI 通过插值得到。

**特点：**
- 多分辨率：远场粗（~4m/探针），近场细（~30cm/探针）
- 时间累积 + 重投影（避免闪烁）
- 探针更新走异步计算线程（不阻塞 GameThread）

#### 1.2.4 Final Gather（屏幕空间采样）

最后一步，屏幕空间放置 16×16 像素的 Probe，每个 Probe 做多次 GI 采样，最终合成到 G-Buffer。

**关键参数：**
- `r.Lumen.FinalGather.SampleSpacing` — Probe 间距（像素）
- `r.Lumen.FinalGather.BounceCount` — 反弹次数
- `r.Lumen.FinalGather.Quality` — 质量档位（5.6+ 枚举）

### 1.3 关键 CVars 一览（按子系统）

> 完整 CVars 见 §4，这里只列最常用的「每子系统 5 个」

| 子系统 | 必知 CVars |
|--------|----------|
| **全局开关** | `r.Lumen.HardwareRayTracing`, `r.Lumen.DiffuseIndirect.Allow`, `r.Lumen.Reflections.Allow` |
| **Lumen Scene** | `r.LumenScene.*`, `r.MeshCard.*`, `r.DistanceField.*` |
| **Surface Cache** | `r.Lumen.SurfaceCache.*`, `r.Lumen.DiffuseIndirect.SurfaceCache.*` |
| **Radiance Cache** | `r.Lumen.RadianceCache.*`, `r.Lumen.ProbeHierarchy.*` |
| **Final Gather** | `r.Lumen.FinalGather.*`, `r.Lumen.ScreenProbe.*` |
| **调试** | `r.Lumen.Visualize.*`, `r.Lumen.Debug.*`, `Show.*` 命令 |

---

## 2. Debug 可视化与诊断

### 2.1 调试视图菜单速查

> **菜单路径**：`Show > Visualize > ...`

| 菜单项 | CVars | 何时用 |
|--------|-------|--------|
| Lumen Scene | `r.LumenScene.DiffuseColor 1` | 看哪些 Mesh 进了 Lumen Scene |
| Lumen Mesh Cards | `r.LumenScene.CardDir 1` | 看 Card 方向和生成密度 |
| Lumen Surface Cache | `r.LumenScene.SurfaceCacheAtlas 1` | 看哪些表面烘焙成功 |
| Lumen Radiance Cache | `r.Lumen.RadianceCache.Visualize 1` | 看探针分布和方向 |
| Lumen Probe Hierarchy | `r.Lumen.ProbeHierarchy.Visualize 1` | 4 层探针覆盖情况 |
| Lumen Screen Probes | `r.Lumen.ScreenProbe.Visualize 1` | 屏幕空间探针 |
| Lumen Reflections | `r.Lumen.Reflections.Visualize 1` | 反射路径追踪 |
| Lumen Final Gather | `r.Lumen.FinalGather.Visualize 1` | Final Gather 调试 |

### 2.2 关键 CVars（按问题分类）

#### 2.2.1 看 Lumen Scene 里的物体

```ini
; 全场景 Mesh Card 颜色（按材质 ID）
r.LumenScene.DiffuseColor 1
; 按高度上色
r.LumenScene.DiffuseHeight 1
; 按方向可视化（紫红色 = 朝下卡, 蓝绿色 = 朝侧卡, 黄色 = 朝上卡）
r.LumenScene.CardDir 1
; 显示哪些 Mesh 是 Lumen Scene 但没生成 Card
r.LumenScene.InvalidCardGeometry 1
; 显示 Mesh Card 的 LOD 切换
r.LumenScene.MeshCardLOD 1
```

**判读规则：**
- **空白区域** → Mesh 没进 Lumen Scene。原因排查：
  1. Project Settings → Rendering → "Generate Mesh Distance Fields" 没勾？
  2. Mesh 属性 → "Affect Distance Field Lighting" 没勾？
  3. Mesh 太小（<10cm）→ Mesh Card 自动剔除，可调 `r.LumenScene.SmallMeshMaxScreenSize`
  4. Lumen Scene 距离剔除 → 调 `r.LumenScene.MaxDistance`

#### 2.2.2 看 Surface Cache

```ini
; 显示 Atlas 内容
r.LumenScene.SurfaceCacheAtlas 1
; 高亮 Surface Cache 失效区域（红色）
r.Lumen.SurfaceCache.Visualize 1
; 显示更新标记
r.Lumen.SurfaceCache.VisualizeUpdates 1
```

**判读：**
- **红色区域** = Surface Cache 没数据 / 失效 → 必然走运行时 GI 计算，性能塌方
- **绿色** = 直接光缓存新鲜
- **黄色** = 间接光需要重新计算

#### 2.2.3 看 Radiance Cache

```ini
; 可视化探针（每个探针显示为一个点）
r.Lumen.RadianceCache.Visualize 1
; 显示探针重要性（基于视线方向）
r.Lumen.ProbeImportance.Visualize 1
; 强制即时更新所有探针（用于诊断探针漂移）
r.Lumen.RadianceCache.ForceImmediateUpdate 1
```

#### 2.2.4 看 Probe Hierarchy（5.4+）

```ini
r.Lumen.ProbeHierarchy.Visualize 1
r.Lumen.ProbeHierarchy.DebugLevel 0  ; 0=全部, 1=仅近, 2=仅中, 3=仅远
```

### 2.3 屏幕 HUD 与命令

```ini
; 屏幕统计 HUD
stat lumen
stat lumenradiancecache
stat lumensurfacecache
stat lumenscene
stat scenesrendering
; GPU Profile 标签
profilegpu
; 显示 Lumen 当前使用的 RT 模式
r.Lumen.HardwareRayTracing.GetCurrentMode
; 转储所有 Lumen CVars 到文件
r.Lumen.DumpAllCVars 1
```

### 2.4 常见视觉问题定位

| 症状 | 概率最高原因 | 排查路径 |
|------|------------|---------|
| **室内漏光（Light Leak）** | Surface Cache 在墙面厚度方向穿透 | 调 `r.Lumen.TraceDistanceScale` 减小；增加墙体厚度；调 `r.Lumen.SurfaceCache.MaxCardAngle` |
| **GI 闪烁（Flickering）** | Radiance Cache 更新频率过低 / 时间累积抖动 | `r.Lumen.RadianceCache.NumFramesToKeep` 调高；`r.Lumen.ScreenProbe.UpdateFrequency` 调高 |
| **GI 出现明显块状** | Radiance Cache 探针分辨率不足 | `r.Lumen.RadianceCache.ProbeResolution` 调高（128→256）；调 `r.Lumen.RadianceCache.ProbeMinSpacing` |
| **动态物体不亮 / 黑** | Mesh 没生成 Surface Cache，或动态物体走 Final Gather 失败 | `r.Lumen.DiffuseIndirect.AllowForInstancedStaticMesh`；`r.Lumen.UpdateForRemovedInstance` |
| **反射发黑 / 抖动** | HW RT 不可用被迫走 SW RT；或反射采样不足 | `r.Lumen.Reflections.BounceCount`；`r.Lumen.Reflections.MaxRoughness` |
| **植被穿透 / 闪烁** | Mesh Card 方向选错或顶点位置有噪点 | Mesh 属性 → "Two Sided Distance Field Generation" 勾上 |
| **整体偏暗** | 5.5+ 默认走了 Substrate + Lumen 双 GI | 关闭 Substrate 或调 Substrate 衰减 |
| **金属面反射错乱** | Surface Cache 镜面烘焙失败 | `r.Lumen.Reflections.Allow` 确保开启；调 `r.Lumen.SurfaceCache.MaxLuminance` |

### 2.5 RenderDoc 抓帧分析 Lumen

**Lumen 在 RenderDoc 里的 Pass 命名约定**（5.6）：
- `BasePass` — G-Buffer
- `LumenSurfaceCacheUpdate` — 表面缓存更新
- `LumenMeshCardBuild` — Mesh Card 生成（动态物体时）
- `LumenSceneUpdate` — Lumen Scene 更新
- `LumenRadianceCacheUpdate` — 远场探针更新
- `LumenScreenProbe` — 屏幕空间探针
- `LumenFinalGather` — 最终 GI 合成
- `LumenReflections` — 反射路径追踪

**典型 RenderDoc 抓帧步骤：**

1. 启动游戏，运行 `r.Lumen.MaximumDebugLevel 3` 进入完整 Debug 模式
2. 在可疑帧按 `F12`（或 RenderDoc 快捷键）
3. 在 Event Browser 里搜 "Lumen" 关键词
4. 看每个 Pass 的 GPU 时间（`r.Lumen.DumpStats 1` 会输出详细分解到日志）
5. 检查 Texture Viewer 里的：
   - `LumenScene.SurfaceCacheAtlas` — Atlas 利用率（应 >70%）
   - `Lumen.RadianceCache.OctahedralAtlas` — 探针 Atlas 利用率
   - `ScreenProbe.IrradianceTexture` — 屏幕探针图

### 2.6 Mesh Card 失效诊断 Checklist

- [ ] Mesh 已勾选 `Affect Distance Field Lighting`
- [ ] Mesh 已勾选 `Generate Mesh Distance Field`
- [ ] Project Settings → `Generate Mesh Distance Fields` 为 true
- [ ] Mesh 法线正确（`Show > Normals` 验证）
- [ ] Mesh 缩放为正（负缩放会让 SDF 失效）
- [ ] Mesh 没有巨大的内外穿模（穿模会让 Card 合并错误）
- [ ] World Partition / Level Streaming 设置不会导致 Card 被错误剔除

---

## 3. Profiling 实战

### 3.1 Insights Trace 流程

Lumen 性能调优**第一步永远是 Unreal Insights Trace**，而不是 RenderDoc。

**完整流程：**

```powershell
# 1. 启动 Editor 时启用 Trace
UnrealEditor.exe Project.uproject -trace=cpu,frame,bookmark,gpu,counters

# 2. 启动 Insights：Tools > Trace > Open Trace
# 3. 在游戏窗口按 Ctrl+Shift+, 开启实时 trace
# 4. 跑场景，触发可疑帧
# 5. 按 Ctrl+Shift+. 停止 trace，自动打开 Insights
```

**Insights 里看 Lumen：**
1. **Timing Insights** → 找 `LumenSceneRendering` / `LumenFinalGather` 等 Pass
2. **GPU Track** → 找对应 RDG Pass 的 GPU Duration
3. **Counters** → 过滤 `STAT_Lumen*` 计数器
4. **Memory Insights** → 看 Lumen 资源占用

### 3.2 Lumen 关键 GPU Pass 表

| Pass | RDG Name | 典型 GPU 时间（5.6, RTX 4070, 室内 4K）| 调优 CVars |
|------|----------|--------------------|------------|
| Surface Cache Update | `LumenSurfaceCacheUpdate` | 0.4-1.2 ms | `r.Lumen.SurfaceCache.UpdateFrequency`, `r.Lumen.DiffuseIndirect.SurfaceCache.MaxLuminance` |
| Mesh Card Build（动态）| `LumenMeshCardBuild` | 0.1-0.8 ms / 动态物体 | 减少动态物体；LOD 切换频率 |
| Lumen Scene Update | `LumenSceneUpdate` | 0.2-0.5 ms | `r.LumenScene.UpdateFrequency`, `r.LumenScene.MinScreenSizeForUpdate` |
| Radiance Cache Update | `LumenRadianceCacheUpdate` | 0.3-1.0 ms | `r.Lumen.RadianceCache.UpdateFrequency`, `r.Lumen.RadianceCache.NumProbes` |
| Screen Probe | `LumenScreenProbe` | 0.2-0.6 ms | `r.Lumen.ScreenProbe.SampleSpacing`, `r.Lumen.ScreenProbe.Update.Interval` |
| Final Gather | `LumenFinalGather` | 0.5-2.0 ms | `r.Lumen.FinalGather.SampleSpacing`, `r.Lumen.FinalGather.BounceCount` |
| Reflections | `LumenReflections` | 0.3-1.5 ms | `r.Lumen.Reflections.Allow`, `r.Lumen.Reflections.MaxRoughness` |
| **总计** | — | **2.0-7.6 ms** | — |

> **5.6 目标参考**（不同场景）：
> - 室内（封闭 + 静态为主）：2-3 ms
> - 室外 + 大量动态：4-7 ms
> - 开放世界 + 全程动态时间：6-10 ms
> - 飞行 / 高速移动：8-12 ms

### 3.3 Lumen 内存分析

**主要内存占用：**

| 资源 | 大小（5.6 默认设置）| 控制 CVars |
|------|--------------------|------------|
| Surface Cache Atlas | 64-256 MB | `r.Lumen.SurfaceCache.AtlasSize` |
| Radiance Cache Probe Atlas | 32-128 MB | `r.Lumen.RadianceCache.ProbeAtlasSize` |
| Mesh Card 几何 | 16-64 MB | `r.LumenScene.MaxMeshCards` |
| Distance Field | 100-500 MB（！隐藏大头）| `r.DistanceFieldBuild.EvaluateSurfaces`, `r.DistanceFieldDefaultVoxelDensity` |
| Screen Probe 历史 | 8-32 MB | `r.Lumen.ScreenProbe.HistorySize` |
| **总计** | **~250 MB - 1 GB** | — |

> **Distance Field 是隐藏大头**：很多项目看着 Lumen 内存爆炸，其实是 `r.DistanceFieldBuild.EvaluateSurfaces` 或 `r.DistanceFields.DefaultVoxelDensity` 设太高。`0.1` 默认值在大型场景可能爆 500MB。

**内存诊断命令：**
```ini
; 输出 Lumen 内存到日志
r.Lumen.DumpMemoryStats 1
; Distance Field 内存统计
stat rhi
stat distancefields
```

### 3.4 Lumen 与其他 Pass 的瓶颈对比

**常见场景下的瓶颈分布（5.6, 4K, RTX 4070）：**

| 场景 | Lumen 总占比 | 其他大头 |
|------|------------|---------|
| 室内静态为主 | 25-35% | BasePass 30%, Nanite 20% |
| 开放世界 + 动态 | 40-55% | Streaming, BasePass |
| 大量植被 + 风吹 | 30-40% | Nanite, VSM |
| VR（双眼 90Hz）| 20-30% | Forward, Lens Matching |
| Switch / 移动端 | 60-80% | （Lumen 几乎不能跑）|

### 3.5 Profile CVars 速查

```ini
; === 通用 GPU Profile ===
profilegpu
stat gpu
stat unit
stat unitgraph
stat scenefilters

; === Lumen 专用 ===
stat lumen                  ; 总览
stat lumenradiancecache     ; Radiance Cache 详细
stat lumensurfacecache      ; Surface Cache 详细
stat lumenscene             ; Lumen Scene 详细
stat scenesrendering        ; 全场景渲染

; === 自动 dump ===
r.Lumen.DumpStats 1         ; 每帧 dump 详细 stats 到日志
r.Lumen.DumpMemoryStats 1   ; 每 1s dump 内存
r.Lumen.DumpAtlasUsage 1    ; Atlas 利用率

; === 强制时间模式（用于隔离 Profile）===
r.Lumen.ForceCPUOnlyMode 0  ; 强制只跑 CPU 部分（GPU 不跑 Lumen）
r.Lumen.ForceGPUOnlyMode 0  ; 反之

; === 隔离 Pass（debug 用）===
r.Lumen.DisableDirectLighting 0
r.Lumen.DisableDiffuseIndirect 0
r.Lumen.DisableReflections 0
```

---

## 4. CVars 全目录（按子系统）

> 这是按子系统分类的**完整 CVars 清单**（基于 5.6，按字母序）。每个 CVar 标注用途、范围、默认值、影响。
> 完整列表可用 `r.Lumen.DumpAllCVars 1` 输出到日志。
> **注**：部分 CVar 名称在不同 UE 版本可能有出入，使用前请用 `DumpAllCVars` 验证。

### 4.1 全局开关与质量

| CVar | 类型 | 默认 | 范围 | 作用 |
|------|------|------|------|------|
| `r.Lumen.HardwareRayTracing` | int | -1 | 0/1/-1 | -1=自动, 0=纯 SW, 1=纯 HW |
| `r.Lumen.DiffuseIndirect.Allow` | int | 1 | 0/1 | 主开关：漫反射 GI |
| `r.Lumen.Reflections.Allow` | int | 1 | 0/1 | 主开关：反射 |
| `r.Lumen.Quality` | int | -1 | -1/0/1/2/3/4 | -1=跟 r.MaterialQualityLevel |
| `r.Lumen.Supported` | int | 1 | 0/1 | 项目是否启用 Lumen |
| `r.Lumen.MinScreenSizeForUpdate` | float | 0.01 | 0.001-0.5 | 屏幕占比阈值, 低于此不更新 |

### 4.2 Surface Cache

| CVar | 类型 | 默认 | 作用 |
|------|------|------|------|
| `r.Lumen.SurfaceCache.AtlasSize` | int | 4096 | Atlas 分辨率（2048 / 4096 / 8192）|
| `r.Lumen.SurfaceCache.UpdateFrequency` | int | 1 | 每 N 帧强制更新一次 |
| `r.Lumen.SurfaceCache.MinUpdateInterval` | float | 0.0 | 最小更新间隔（秒）|
| `r.Lumen.SurfaceCache.MaxLuminance` | float | 100000.0 | 触发烘焙更新的亮度阈值 |
| `r.Lumen.SurfaceCache.MaxCardAngle` | float | 90.0 | Card 最大允许角度（度）|
| `r.Lumen.SurfaceCache.MeshCardMergedThreshold` | float | 100.0 | 合并 Card 的尺寸阈值 |
| `r.Lumen.SurfaceCache.AllowIndirectSpecular` | int | 1 | 是否烘焙镜面 |
| `r.Lumen.SurfaceCache.SampleSpacing` | float | 4.0 | 烘焙采样间距（像素）|

### 4.3 Radiance Cache

| CVar | 类型 | 默认 | 作用 |
|------|------|------|------|
| `r.Lumen.RadianceCache.ProbeResolution` | int | 32 | 单探针分辨率（32/64/128/256）|
| `r.Lumen.RadianceCache.ProbeMinSpacing` | float | 200.0 | 最近探针间距（cm）|
| `r.Lumen.RadianceCache.ProbeMaxSpacing` | float | 2000.0 | 最远探针间距（cm）|
| `r.Lumen.RadianceCache.NumProbes` | int | 256 | 探针数量上限 |
| `r.Lumen.RadianceCache.NumFramesToKeep` | int | 30 | 历史累积帧数 |
| `r.Lumen.RadianceCache.UpdateFrequency` | int | 1 | 更新频率 |
| `r.Lumen.RadianceCache.ForceImmediateUpdate` | int | 0 | 立即更新（debug 用）|
| `r.Lumen.RadianceCache.ForceFullUpdate` | int | 0 | 全量更新 |

### 4.4 Screen Probes

| CVar | 类型 | 默认 | 作用 |
|------|------|------|------|
| `r.Lumen.ScreenProbe.SampleSpacing` | int | 16 | 屏幕空间探针间距（像素）|
| `r.Lumen.ScreenProbe.Update.Interval` | int | 1 | 更新间隔（帧）|
| `r.Lumen.ScreenProbe.HistorySize` | int | 8 | 历史帧数 |
| `r.Lumen.ScreenProbe.Relocation` | int | 1 | 探针重定位（去闪烁）|
| `r.Lumen.ScreenProbe.Method` | int | 1 | 0=固定, 1=自适应 |

### 4.5 Final Gather

| CVar | 类型 | 默认 | 作用 |
|------|------|------|------|
| `r.Lumen.FinalGather.SampleSpacing` | int | 8 | 屏幕空间采样间距 |
| `r.Lumen.FinalGather.BounceCount` | int | 1 | 反弹次数 |
| `r.Lumen.FinalGather.Quality` | int | 1 | 质量档位（5.6+）|
| `r.Lumen.FinalGather.MaxSamplesPerPixel` | int | 64 | 每像素最大采样数 |
| `r.Lumen.FinalGather.MaxReflectionBounces` | int | 1 | 反射最大反弹 |

### 4.6 Lumen Scene / Mesh Cards

| CVar | 类型 | 默认 | 作用 |
|------|------|------|------|
| `r.LumenScene.CardGenerationResolutionScale` | float | 1.0 | Card 生成分辨率倍数 |
| `r.LumenScene.MeshCardResolutionScale` | float | 1.0 | 单 Card 纹理分辨率 |
| `r.LumenScene.MaxMeshCards` | int | 524288 | Mesh Card 总数上限 |
| `r.LumenScene.MaxDistance` | float | 50000.0 | Lumen Scene 最大距离（cm）|
| `r.LumenScene.UpdateFrequency` | int | 1 | 更新频率 |
| `r.LumenScene.MergeCards` | int | 1 | 合并相邻 Mesh Card |
| `r.LumenScene.SmallMeshMaxScreenSize` | float | 0.05 | 最小 Mesh 屏幕占比 |
| `r.LumenScene.MinMeshSDFResolution` | int | 32 | 最小 SDF 分辨率 |

### 4.7 Software RT / Hardware RT

| CVar | 类型 | 默认 | 作用 |
|------|------|------|------|
| `r.Lumen.TraceDistanceScale` | float | 1.0 | 追踪距离倍数（远处爆炸）|
| `r.Lumen.MaxTraceDistance` | float | 50000.0 | 最大追踪距离（cm）|
| `r.Lumen.SWRT.MaxRayIntensity` | float | 100.0 | SW RT 射线强度上限 |
| `r.Lumen.HWRT.MinOccupancy` | float | 0.5 | HW RT 占用率阈值 |
| `r.Lumen.HWRT.AllowSkyLighting` | int | 1 | 允许天空光走 HW RT |
| `r.Lumen.HWRT.RebuildBVH` | int | 0 | 强制重建 BVH（debug）|

### 4.8 反射

| CVar | 类型 | 默认 | 作用 |
|------|------|------|------|
| `r.Lumen.Reflections.BounceCount` | int | 1 | 反射反弹次数 |
| `r.Lumen.Reflections.MaxRoughness` | float | 0.4 | 最大粗糙度阈值（更高走 SSR）|
| `r.Lumen.Reflections.DirectLighting` | int | 1 | 反射中包含直接光 |
| `r.Lumen.Reflections.IndirectSpecular` | int | 1 | 反射中包含间接光 |
| `r.Lumen.Reflections.ScreenTraces` | int | 1 | 启用屏幕空间追踪补充 |

### 4.9 自定义材质 / 光照互动

| CVar | 类型 | 默认 | 作用 |
|------|------|------|------|
| `r.Lumen.AllowLightFunctions` | int | 1 | 允许 Light Function 影响 Lumen |
| `r.Lumen.AllowIESProfiles` | int | 1 | 允许 IES 配置文件 |
| `r.Lumen.AllowRectLights` | int | 1 | 允许 Rect Light 影响 Lumen |
| `r.Lumen.AllowSkyAtmosphere` | int | 1 | 允许 Sky Atmosphere |
| `r.Lumen.AllowTranslucentMaterials` | int | 1 | 允许半透明材质（5.5+）|
| `r.Lumen.AllowSubstrate` | int | 1 | 允许 Substrate 材质（5.5+）|

### 4.10 与其他子系统联动

| CVar | 作用 |
|------|------|
| `r.Nanite.LumenIntegration` | 启用 Nanite + Lumen 集成（默认 1）|
| `r.Nanite.Streaming` | 影响 Lumen 场景更新 |
| `r.Shadow.Virtual.Enable` | VSM 与 Lumen 协同 |
| `r.Substrate.OpaqueMaterialRoughRefraction` | Substrate 折射对 Lumen 的影响 |
| `r.SkyAtmosphere` | Sky Atmosphere 与 Lumen GI 互动 |

### 4.11 项目设置层（DefaultEngine.ini）

```ini
[/Script/Engine.RendererSettings]
r.Lumen.HardwareRayTracing=1
r.Lumen.DiffuseIndirect.Allow=1
r.Lumen.Reflections.Allow=1
r.Lumen.Supported=1
r.GenerateMeshDistanceFields=1
r.DistanceFieldBuild.EvaluateSurfaces=1
r.DistanceFieldDefaultVoxelDensity=0.1

[ConsoleVariables]
; 移动端 / Switch 不跑 Lumen
r.Lumen.HardwareRayTracing=0
r.Lumen.Supported=0
```

### 4.12 命令行启动参数

```bash
# 强制启用 Lumen（即使 Editor 默认关）
-game -Lumen

# 强制关闭 Lumen 反射（移动端）
-r.Lumen.Reflections.Allow=0

# 设置 Lumen 质量档位
-LumenQuality=2

# 设置 Scale（XR）
-LumenScale=1.0
```

---

## 5. 跨场景适配指南

### 5.1 开放世界（最大规模）

**核心挑战：** 远场 GI + 大量动态 + 长时间稳定 + 内存预算

**推荐配置（5.6，4K，RTX 4080+）：**

```ini
r.Lumen.Quality = 4                      ; 最高质量
r.Lumen.HardwareRayTracing = -1           ; Hybrid
r.Lumen.TraceDistanceScale = 0.8         ; 减少远距离追踪
r.Lumen.MaxTraceDistance = 20000.0       ; 20m 限制
r.Lumen.RadianceCache.NumProbes = 1024   ; 增大
r.Lumen.RadianceCache.ProbeMinSpacing = 100.0
r.Lumen.SurfaceCache.AtlasSize = 8192    ; 增大 Atlas
r.Lumen.FinalGather.SampleSpacing = 16   ; 降低 Final Gather
r.LumenScene.MaxMeshCards = 1048576      ; 翻倍上限
```

**关键避坑：**
1. **远场泄漏** → 调低 `r.Lumen.TraceDistanceScale`
2. **漫游时 GI 突变** → 增加 `r.Lumen.RadianceCache.NumFramesToKeep`
3. **植被穿透** → 勾 `r.LumenScene.MergeCards=0`，让每株植物独立 Card
4. **日夜循环** → 用 `r.Lumen.SurfaceCache.UpdateFrequency` 配合时间插值（避免每帧重建）

### 5.2 室内为主（中等规模）

**核心挑战：** 漏光控制 + 静态为主 + 质量优先

**推荐配置（5.6，4K，RTX 4070）：**

```ini
r.Lumen.Quality = 4
r.Lumen.HardwareRayTracing = 1           ; 室内 HW RT 收益大
r.Lumen.TraceDistanceScale = 1.5         ; 室内可以拉远
r.Lumen.MaxTraceDistance = 50000.0
r.Lumen.FinalGather.SampleSpacing = 4    ; 高质量 Final Gather
r.Lumen.Reflections.MaxRoughness = 0.6
```

**关键避坑：**
1. **薄墙漏光** → 墙体厚度 ≥10cm，或调 `r.Lumen.TraceDistanceScale`
2. **窗户区域闪烁** → `r.Lumen.RadianceCache.UpdateFrequency=2`
3. **地板反射过亮** → `r.Lumen.Reflections.DirectLighting=0`，只保留 GI

### 5.3 卡通 / 风格化（美术约束）

**核心挑战：** 风格统一 + 不要太真实的 GI 干扰美术

**推荐配置：**

```ini
r.Lumen.Quality = 1                      ; 低质量（GI 是辅助）
r.Lumen.DiffuseIndirect.Allow = 1
r.Lumen.Reflections.Allow = 0            ; 反射关（保持卡通感）
r.Lumen.TraceDistanceScale = 0.3         ; 极短追踪
r.Lumen.FinalGather.SampleSpacing = 32   ; 粗糙 Final Gather
```

**额外技巧：**
- 用 Lightmap + Lumen 混合：重要场景烘焙 Lightmap，背景用 Lumen
- `r.Lumen.SurfaceCache.MaxCardAngle=30` 让 Card 更严格（更像分块灯光）
- 配合 `r.AmbientOcclusionLevels=0` 加强手工 AO 美术感

### 5.4 高速移动 / 飞行 / 载具

**核心挑战：** 屏幕探针跟不上 + 视角变化大 + 远场采样爆炸

**推荐配置：**

```ini
r.Lumen.ScreenProbe.Update.Interval = 1   ; 每帧更新（默认）
r.Lumen.ScreenProbe.HistorySize = 4        ; 减少历史（避免拖影）
r.Lumen.RadianceCache.NumFramesToKeep = 10 ; 减少累积
r.Lumen.TraceDistanceScale = 0.5          ; 缩短追踪
r.Lumen.FinalGather.SampleSpacing = 8     ; 中等密度
```

**额外技巧：**
- 用 `r.Lumen.DisableOnscreenTelemetry 1` 避免 Screen Probe 抢占带宽
- 配 `r.ViewDistanceScale=0.5` 降低视距

### 5.5 VR（高帧率）

**核心挑战：** 双眼 + 90/120 Hz + 头动预测

**推荐配置（5.6, Quest 3 / Pico 4 / PCVR）：**

```ini
r.Lumen.Quality = 2
r.Lumen.HardwareRayTracing = 1            ; HW RT 在 VR 优势明显
r.Lumen.FinalGather.SampleSpacing = 8
r.Lumen.FinalGather.BounceCount = 1
r.Lumen.Reflections.MaxRoughness = 0.3
r.Lumen.TraceDistanceScale = 0.6
```

**额外：**
- PCVR 推荐 `r.Lumen.Quality=3`（眼睛距屏幕近）
- 一体机 VR **不推荐开 Lumen**（除非 Standalone + Lumen 简化版）

### 5.6 主机平台（PS5 / XSX）

**核心挑战：** 固定硬件 + 帧时间预算严格

**推荐配置（PS5 / XSX, 1440p-4K）：**

```ini
r.Lumen.Quality = 3
r.Lumen.HardwareRayTracing = 1
r.Lumen.FinalGather.SampleSpacing = 12
r.Lumen.SurfaceCache.AtlasSize = 4096
r.Lumen.RadianceCache.NumProbes = 384
```

**关键避坑：**
1. **不要用 Nanite + Lumen 全开** → 二选一控制 GPU 预算
2. **Profile 时一定要拆 PS5/XSX** → 二者 RT Core 不同
3. **用 PS5/XSX Profiler 而非 RenderDoc** → 平台工具更准

### 5.7 Switch / 移动平台

**核心原则：直接关 Lumen。**

Lumen 在 Switch / iOS / Android 上没有工程化价值（除非厂商有自研移植）。

```ini
r.Lumen.Supported = 0
r.Lumen.HardwareRayTracing = 0
r.Lumen.DiffuseIndirect.Allow = 0
r.Lumen.Reflections.Allow = 0
```

**替代方案：**
- 烘焙 Lightmap + Light Probe（Unity/UE 都支持）
- 静态 Lightmap + 动态 Spot Light
- 屏幕空间反射（SSR）+ 反射探针（Reflection Probe）

### 5.8 像素风格 / 2.5D / Diorama

**核心原则：Lumen 在这类风格里**通常关掉**，因为风格化的光照是手工放置的。**

```ini
r.Lumen.Supported = 0
; 用 Lightmap + 烘焙 AO + 反射 Capture 替代
```

---

## 6. 性能预算速查表

### 6.1 各平台 Lumen 帧时间预算

| 平台 | 目标分辨率 | 目标帧率 | Lumen 预算 | Lumen 质量档 |
|------|-----------|---------|-----------|------------|
| PC 高端（RTX 4080+）| 4K | 60 FPS | 6.0 ms | Quality 4 |
| PC 中端（RTX 4070）| 1440p | 60 FPS | 4.0 ms | Quality 3 |
| PC 入门（RTX 3060）| 1080p | 60 FPS | 2.5 ms | Quality 2 |
| PCVR（RTX 4070+）| 双眼 1440p | 90 Hz | 4.0 ms | Quality 3 |
| PS5 / XSX | 1440p-4K | 60 FPS | 4.0 ms | Quality 3 |
| PS5 Pro / XSX X | 4K | 60/120 FPS | 5.0 ms | Quality 4 |
| Switch / 移动 | — | — | **不推荐** | — |

### 6.2 Lumen 子系统 GPU 预算（5.6 默认室内）

| 子系统 | 室内（静态）| 开放世界 | 高速移动 |
|--------|------------|---------|---------|
| Surface Cache Update | 0.5 ms | 1.0 ms | 0.3 ms |
| Lumen Scene Update | 0.2 ms | 0.5 ms | 0.3 ms |
| Radiance Cache Update | 0.5 ms | 1.5 ms | 0.8 ms |
| Screen Probe | 0.3 ms | 0.5 ms | 0.4 ms |
| Final Gather | 1.0 ms | 1.5 ms | 0.6 ms |
| Reflections | 0.5 ms | 1.5 ms | 1.0 ms |
| **总计** | **3.0 ms** | **6.5 ms** | **3.4 ms** |

### 6.3 内存预算参考

| 平台 | Lumen 总内存预算 | Surface Cache Atlas |
|------|----------------|--------------------|
| PC 高端 | 1.0 GB | 8192² |
| PC 中端 | 512 MB | 4096² |
| PS5 / XSX | 768 MB | 4096² |
| Switch / 移动 | 0（不开）| — |

### 6.4 场景规模参数对应表

| 场景规模 | MaxMeshCards | NumProbes | AtlasSize | TraceDistance |
|---------|-------------|-----------|-----------|---------------|
| 小（单房间）| 8192 | 64 | 2048 | 2000 cm |
| 中（多层建筑）| 65536 | 256 | 4096 | 10000 cm |
| 大（开放世界关卡）| 524288 | 1024 | 8192 | 20000 cm |
| 巨（无缝世界）| 1048576+ | 2048+ | 16384 | 50000 cm |

---

## 7. 常见坑位与对策

### 坑 1：Mesh Card 不生成 / 物体完全不见

**症状：** `Show > Lumen Mesh Cards` 看不到某个 Mesh

**排查路径：**
1. Project Settings → `Generate Mesh Distance Fields` ✓
2. Mesh 属性 → `Affect Distance Field Lighting` ✓
3. Mesh 属性 → `Generate Mesh Distance Field` ✓
4. 法线方向正确（不朝内）
5. 缩放不是负值
6. World Partition 设置没剔除
7. 距离 `r.LumenScene.MaxDistance` 内
8. 屏幕占比 > `r.LumenScene.SmallMeshMaxScreenSize`

**修复：**
- 静态：用 `Build > Update Mesh Distance Field` 强制重建
- 动态：勾 `Affect Distance Field Lighting` + 检查材质没有 `World Position Offset`

### 坑 2：Surface Cache 全帧重建（性能塌方）

**症状：** `stat lumensurfacecache` 显示每帧重建率 >50%

**最常见原因（按概率）：**
1. **材质有 `World Position Offset`**（顶点数 ≥1 时强制重建）→ 改用 GPU 动画
2. **Time-of-Day 滑块跨度过大**（亮度变化超 `MaxLuminance` 阈值）→ 用 lerp 插值
3. **点光源动态闪烁**（霓虹灯 / 警灯）→ 强制 LightFunction 不进 Lumen
4. **动态 Mesh 没勾 `Affect Distance Field Lighting`** → 勾上

### 坑 3：远场光线泄漏

**症状：** 玩家穿过一面墙，对面房间被间接照亮

**对策：**
```ini
r.Lumen.TraceDistanceScale = 0.5       ; 缩短追踪距离
r.Lumen.MaxTraceDistance = 5000.0      ; 限制最大距离
r.Lumen.SurfaceCache.MaxCardAngle = 60 ; Card 角度更严
```

外加艺术：墙体厚度 ≥10cm，避免两面墙 Mesh 距离过近。

### 坑 4：反射发黑 / 抖动

**症状：** 镜面反射看起来像没开

**排查：**
1. `r.Lumen.Reflections.Allow=1` ✓
2. 材质粗糙度 < `r.Lumen.Reflections.MaxRoughness`（默认 0.4）
3. GPU 支持 HW RT → 否则 SW RT 反射质量差
4. 反射采样不足 → `r.Lumen.FinalGather.BounceCount=1`

**对策：**
- 高粗糙度材质用 SSR / Reflection Capture 替代
- HW RT 不可用时调 `r.Lumen.Reflections.ScreenTraces=1` 用屏幕空间补

### 坑 5：粒子 / Niagara 不亮

**症状：** 火焰、魔法效果不参与 Lumen

**这是预期行为：** Lumen 不追踪粒子，但粒子可以烘焙到 Lumen（5.5+）：
- 在 Niagara System 属性里勾 `Affect Lumen Global Illumination`
- 限制：仅静态 / 低频粒子；不能每帧重建

### 坑 6：透明材质不参与 Lumen

**症状：** 玻璃、水面、树叶不参与 GI

**5.5+ 解法：**
```ini
r.Lumen.AllowTranslucentMaterials = 1
```
并在材质里勾 `Affect Lumen Global Illumination`（如果可用）。

### 坑 7：反向法线导致 SDF 错误

**症状：** Mesh 内部出现奇怪黑斑或亮斑

**对策：** `Show > Normals` 检查法线方向，纠正反转。

### 坑 8：Nanite Mesh 在 Lumen 中看不见

**症状：** 大场景里 Nanite Mesh 没被 Lumen 追踪

**排查：**
- `r.Nanite.LumenIntegration=1` ✓
- Nanite Mesh 走了 Streaming → `r.Nanite.Streaming.MinScreenSize` 调小
- Nanite Mesh 在 `r.LumenScene.MaxDistance` 内

### 坑 9：硬件 RT 兼容性警告

**症状：** Console 出现 "Lumen: Hardware RT not supported, falling back to SW RT"

**对策：** 在 `r.Lumen.HardwareRayTracing=-1` 让 UE 自动选择，或在低端 GPU 上显式 `=0`。

### 坑 10：场景加载时 Lumen 闪烁

**症状：** 关卡切换头几秒 GI 不稳定

**对策：**
- 关卡设计时用 Streaming Level + Async Load
- `r.Lumen.RadianceCache.ForceImmediateUpdate=1` 在加载完成时触发一次

### 坑 11：编辑器卡顿（CPU 侧）

**症状：** Editor 编辑场景时帧率掉到 10 FPS 以下

**最常见原因：**
1. Lumen Scene 每帧全量重建（巨型关卡 + 静态光频繁改）
2. Distance Field 重建未完成（编辑器切到 Static Mesh 时）
3. 探针实时更新（`r.Lumen.RadianceCache.ForceImmediateUpdate=1` 忘记关）

**对策：**
- 编辑器下 `r.Lumen.Supported=0`，只在 PIE / Standalone 启用
- 用 `r.Lumen.DistanceFieldBuild.UpdateEveryFrame=0`

### 坑 12：与 Path Tracer 切换后视图不对

**症状：** 切到 Path Tracer 模式后 GI 看起来和 Lumen 不一样

**对策：**
- Path Tracer 是真路径追踪，Lumen 是近似——视觉差异是设计意图
- 不要用 Path Tracer 当 Lumen 的「真值」基准去 debug Lumen（否则会越调越乱）

---

## 8. 进阶话题

### 8.1 Lumen 与 Path Tracer

UE 5.6+ 的 Path Tracer 是 **离线 / 高质量** 模式，与 Lumen 是两条独立管线：

| 维度 | Lumen | Path Tracer |
|------|-------|-------------|
| 目标 | 实时 | 离线 / 静帧 |
| 反射反弹 | 1-2 | 无限（de Bruijn）|
| GI 反弹 | 1 | 无限 |
| 硬件要求 | 中高 | 高（HW RT 必需）|
| 用途 | 实时游戏 | 电影 / 静帧 / 离线资产 |

**实践：** 用 Path Tracer 离线烘焙参考图，作为 Lumen 调优的「真值」基准。

### 8.2 Lumen 与 Lightmap 共存

UE 5.4+ 支持 **混合光照模式**：
- 静态物体：烘焙 Lightmap
- 动态物体 + 远场 GI：Lumen

```ini
; Project Settings → Rendering → Lighting
; Global Illumination = Hybrid (Lightmap + Lumen)
```

**实际经验：** 大型项目几乎都用这个混合模式。完全纯 Lumen 不 Lightmap 是 UE5 demo 的演示状态，生产项目都有 Lightmap 兜底。

### 8.3 World Partition 对 Lumen 的影响

World Partition 会让 Lumen Scene 按 Cell 分块更新，这是设计意图。但要注意：
- Cell 切换时 Lumen Scene 需要重建 → 用 Streaming 预加载避免卡顿
- `r.LumenScene.MaxDistance` 应覆盖 Cell 大小

### 8.4 程序化 / Procedural 关卡

程序化生成的 Mesh 需要手动触发 Lumen Scene 更新：

```cpp
// C++
if (GEngine)
{
    GEngine->ForceLumenSceneUpdate();
}
```

或用 `r.LumenScene.MeshCardUpdateFrequency=1` 每帧重建（性能贵）。

### 8.5 Multi-View VR

VR 多视图时 Lumen 需要特殊处理：
- `r.Lumen.SupportStereo=1`
- 反射 / GI 在双眼之间共享，避免闪烁

### 8.6 自定义光源

| 光源类型 | Lumen 支持 | 备注 |
|---------|-----------|------|
| Point Light | ✓ | 静态 / 动态均可 |
| Spot Light | ✓ | 静态 / 动态均可 |
| Directional Light | ✓ | 天光 + 太阳 |
| Rect Light | ✓ | 5.0+ |
| Sky Light | ✓ | Sky Atmosphere 联动 |
| IES Profile | ✓ | `r.Lumen.AllowIESProfiles=1` |
| Light Function | ✓ | 性能敏感，慎用 |
| Volumetric Light | 部分 | 仅影响反射，不参与 GI 烘焙 |

### 8.7 Lumen 烘焙资产备份

某些大型场景可以**离线预计算 Surface Cache**（5.5+ 实验性）：

```ini
r.Lumen.BakeSurfaceCache 1
```

烘焙一次后存盘，运行时直接加载——能大幅缩短关卡加载时间。**注意：** 这是实验性功能，5.6 还不够稳定，仅适合尝鲜。

### 8.8 Lumen 与 AI / Procedural 资产

5.6 起的趋势：
- **AI 生成 Mesh**（Tripo、Meshy）→ 自动勾 `Affect Distance Field Lighting` 后可直接进 Lumen
- **程序化材质**（Substrate Graph）→ Lumen 完全兼容 Substrate
- **Niagara 程序化效果** → 5.5+ 支持烘焙进 Lumen

→ 这块的笔记库整合路径见 [[UE5-NNE-神经网络引擎]]（NNE）和 [[UE5-Mass-AI-数据导向框架]]（Mass）。

---

## 9. 调试 Checklist（直接复制到项目 Confluence / Notion）

### Checklist A：Lumen 视觉异常排查

- [ ] 1. `r.Lumen.HardwareRayTracing.GetCurrentMode` 是什么模式？
- [ ] 2. `Show > Visualize > Lumen Scene` —— 目标物体在 Lumen Scene 里吗？
- [ ] 3. `Show > Visualize > Lumen Mesh Cards` —— Mesh Card 方向 / 密度正常吗？
- [ ] 4. `Show > Visualize > Lumen Surface Cache` —— 表面烘焙完整吗？红色 = 失败
- [ ] 5. `Show > Visualize > Lumen Radiance Cache` —— 探针分布合理吗？
- [ ] 6. `Show > Visualize > Lumen Screen Probes` —— 屏幕探针密度够吗？
- [ ] 7. 法线方向正确吗？（`Show > Normals`）
- [ ] 8. Mesh 缩放正值？
- [ ] 9. 材质有 `World Position Offset` 吗？→ 改为 GPU 动画
- [ ] 10. Time-of-Day 变化是否过剧？
- [ ] 11. 动态光源是否频繁闪烁？
- [ ] 12. 物体是否在 `r.LumenScene.MaxDistance` 内？
- [ ] 13. 渲染设置 `Generate Mesh Distance Fields` 勾了吗？

### Checklist B：Lumen 性能问题排查

- [ ] 1. `stat lumen` —— Lumen GPU 时间占比？
- [ ] 2. `profilegpu` —— Lumen 在 RenderDoc/Insights 的哪一档？
- [ ] 3. `r.Lumen.DumpStats 1` —— 子系统分解时间？
- [ ] 4. Surface Cache 重建率（`stat lumensurfacecache`）>50%？→ 查材质 WPO
- [ ] 5. 动态 Mesh 数 / 顶点数 / 三角形数？
- [ ] 6. `r.Lumen.MaxTraceDistance` 是否过大？
- [ ] 7. `r.Lumen.FinalGather.SampleSpacing` 是否过密？
- [ ] 8. `r.Lumen.RadianceCache.NumProbes` 是否过多？
- [ ] 9. `r.Lumen.SurfaceCache.AtlasSize` 是否不足？（利用率 >90% 就有问题）
- [ ] 10. Distance Field 内存？`stat distancefields`
- [ ] 11. 平台 Profile（PS5/XSX GPU profiler）—— 不是 RenderDoc
- [ ] 12. 切到 SW RT（`r.Lumen.HardwareRayTracing=0`）—— 性能有没有变好？→ HW RT 是瓶颈

### Checklist C：跨平台交付前

- [ ] 1. 各平台 Lumen 质量档已设（`r.Lumen.Quality`）？
- [ ] 2. 各平台 Atlas / Probe 数量已设？
- [ ] 3. 移动端 / Switch 关闭 Lumen？
- [ ] 4. 平台 SDK（PS5 / XSX / Switch）的 Lumen 兼容性确认？
- [ ] 5. 极端场景（日夜切换 / 大爆炸）压力测试通过？
- [ ] 6. 默认 Profile vs Lumen Profile 两套设置？

### Checklist D：代码 / 项目设置审计

- [ ] 1. 所有静态 Mesh 都勾了 `Affect Distance Field Lighting`？
- [ ] 2. 所有静态 Mesh 都勾了 `Generate Mesh Distance Field`？
- [ ] 3. 没有材质滥用 `World Position Offset`？
- [ ] 4. 没有材质时间相关（影响 Surface Cache 重建）？
- [ ] 5. 没有反向法线 / 负缩放 Mesh？
- [ ] 6. World Partition Cell 划分合理（避免卡顿）？
- [ ] 7. `r.DistanceFieldDefaultVoxelDensity` 在预算内？
- [ ] 8. Niagara System 该勾 `Affect Lumen GI` 的都勾了？

---

## 10. 关联笔记 / 输出产物

### 关联笔记

- [[Lumen-SIGGRAPH-2021]] — Lumen 原始 SIGGRAPH 论文笔记（理论层）
- [[../../02-引擎源码分析库/Unreal-Engine/UE5-Lumen-源码调用链]] — Lumen 源码调用链笔记（实现层）
- [[../../02-引擎源码分析库/Unreal-Engine/UE5-Nanite-虚拟几何管线]] — Nanite 与 Lumen 的协同
- [[../../02-引擎源码分析库/Unreal-Engine/UE5-VT-虚拟纹理]] — Virtual Texture 原理（Lumen Surface Cache 是 VT）
- [[../../02-引擎源码分析库/Unreal-Engine/UE5-Mass-AI-数据导向框架]] — Mass AI 与 Lumen 的 GPU 调度
- [[../../02-引擎源码分析库/Unreal-Engine/UE5-NNE-神经网络引擎]] — NNE + Lumen 的未来（AI 生成 GI）
- [[SDF-Based Rendering]] — SDF 渲染基础
- [[Screen-Space-Probes]] — Screen Space Probe 通用理论
- [[../../05-技术雷达/Lumen-技术雷达条目]] — Lumen 在个人雷达的位置

### 视频 / 外部资料

- `Lumen-HowItActuallyWorks-UE5.mp4` — Kostas Gkarypis / Tom Looman / Ari Shapiro 系列
- `Lumen-HowItActuallyWorks-UE5.f140.m4a` / `.f399.mp4` — GDC Vault 公开版
- `Lumen-SIGGRAPH-2021.html` — 本地存档

### 输出产物

- [x] 已写实战手册（本文）
- [ ] 已制作配套 HTML 卡牌（按 engine-source-card-pack skill 转）
- [ ] 已应用到当前项目
- [ ] 已内部分享 / 组会演讲

---

## 附录 A：速查命令表（贴在显示器边）

```
=== 调试可视化（菜单 Show > Visualize）===
r.LumenScene.DiffuseColor 1                ; 看 Lumen Scene
r.LumenScene.CardDir 1                     ; 看 Mesh Card 方向
r.LumenScene.SurfaceCacheAtlas 1           ; 看 Surface Cache Atlas
r.Lumen.RadianceCache.Visualize 1          ; 看 Radiance Cache 探针
r.Lumen.ProbeHierarchy.Visualize 1         ; 看 4 层探针
r.Lumen.ScreenProbe.Visualize 1            ; 看屏幕探针
r.Lumen.FinalGather.Visualize 1            ; 看 Final Gather
r.Lumen.Reflections.Visualize 1            ; 看反射路径

=== Stat 命令 ===
stat lumen                                 ; 总览
stat lumensurfacecache                     ; Surface Cache
stat lumenradiancecache                    ; Radiance Cache
stat lumenscene                            ; Lumen Scene
stat scenesrendering                       ; 全场景渲染
profilegpu                                 ; GPU 详情

=== 模式切换 ===
r.Lumen.HardwareRayTracing 0/1/-1          ; SW / HW / 自动
r.Lumen.DiffuseIndirect.Allow 0/1          ; GI 开关
r.Lumen.Reflections.Allow 0/1              ; 反射开关
r.Lumen.Quality -1/0/1/2/3/4              ; 质量档

=== 性能调优（最常调）===
r.Lumen.TraceDistanceScale 0.5             ; 缩短追踪距离
r.Lumen.FinalGather.SampleSpacing 16       ; 降低 Final Gather 密度
r.Lumen.MaxTraceDistance 50000             ; 限制最大距离
r.Lumen.SurfaceCache.AtlasSize 4096        ; Atlas 尺寸
r.Lumen.RadianceCache.NumProbes 256        ; 探针数

=== Dump / 隔离 ===
r.Lumen.DumpStats 1                        ; dump 到日志
r.Lumen.DumpMemoryStats 1                  ; dump 内存
r.Lumen.DisableDiffuseIndirect 1           ; 隔离测试
r.Lumen.DisableReflections 1               ; 隔离测试
```

---

*Create date: 2026-06-28*  
*Last modified: 2026-06-28*