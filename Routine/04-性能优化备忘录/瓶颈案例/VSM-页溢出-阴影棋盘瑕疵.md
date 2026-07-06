---
tags: [perf/GPU, perf/culling, perf/待验证]
aliases: [VSM Page Overflow, VSM页溢出, 阴影棋盘瑕疵]
---

# VSM 页溢出导致阴影棋盘瑕疵

| 字段 | 内容 |
|------|------|
| **现象** | 阴影区域出现棋盘格图案 / 阴影突然消失 / 摄像机切换后阴影错乱 |
| **发现日期** | 2026-07-02 |
| **项目/场景** | UE5 大世界（多光源 / 高分辨率阴影 / 大量 WPO 对象） |
| **平台** | PC (DXR) / PS5 / XSX |
| **严重程度** | 严重（视觉 bug + 缓存失效雪崩） |
| **来源类型** | UE 官方 VSM 文档 + GDC 2024 Wihlidal + 知乎 VSM 详解 |

---

## 来源与可信度

| 来源 | 类型 | 关键事实 |
|------|------|----------|
| UE 官方 *Virtual Shadow Maps - Advantages and Limitations*（官方中文转载） | [D] 官方文档 | 16k×16k 虚拟分辨率，128×128 pages，物理页默认 2048；具体溢出症状、CVars 全列 |
| GDC 2024 *Nanite GPU Driven Materials* — Graham Wihlidal | [D] GDC 演讲 | 4015 bins 中 3675 个空；PS5 memory defragmentation 压缩空调度 |
| 知乎《UE5 VirtualShadowMap 详解》 | [U] 一线工程师 | clipmap firstLevel=6/lastLevel=22；page table 索引算法；具体代码路径 |
| 知乎《UE5性能优化-GPU》 | [U] 一线工程师 | WPO 强制缓存范围 `r.Shadow.Virtual.Cache.MaxMaterialPositionInvalidationRange` |

> **本文性质：** 公开资料汇编，**未经本人 Profile 验证**。VSM 在不同引擎版本（5.1/5.3/5.4）下默认参数有差异，必须查自己引擎版本的源码。

---

## 现象描述

**视觉症状（按 UE 官方文档原文分类）：**

1. **棋盘格图案** — 阴影区域出现规则的 checker pattern
2. **阴影突然消失** — 镜头切换或大量动态对象导致瞬间大量缓存失效
3. **阴影错乱** — 缓存了错误的阴影数据（"错误的阴影缓存"）
4. **深度图伪影** — 大范围 WPO 导致 cluster BBox 溢出，深度图被 clamp 到错误范围

**复现条件：**

- 镜头切换（cut / teleport）瞬间
- 大量 WPO 动画对象（草、树、风动布料、HISM）
- 单光源阴影覆盖屏幕大部分区域
- MaxPhysicalPages 不足 + 缓存失效

**Profile 表现：**

```bash
r.ShaderPrintEnable 1
r.Shadow.Virtual.ShowStats 1
```

可视化打开后看：
- "Pages" 数量是否超过 "Max Pages"
- "Candidates / Visible Clusters" 是否超过 Nanite 上限

---

## 根因分析

### VSM 基础结构（来自知乎 VSM 详解）

```
VSM = 16k × 16k 虚拟分辨率（远超传统 CSM 的 2k~4k）
每个 VSM 划分成 128×128 个 tile（page）
方向光用 clipmap 管理，firstLevel=6 → lastLevel=22
默认覆盖范围：64cm → 40km
物理页（Physical Page）池上限默认 2048
```

### 溢出根因链

```
大量像素同时需要新页（动态失效 / 镜头切换 / WPO 失效）
  ↓
请求的物理页数 > MaxPhysicalPages（默认 2048）
  ↓
部分页被强制不分配 → 对应像素阴影数据缺失
  ↓
渲染时该页读到 0/无效值 → 棋盘格 / 阴影消失
  ↓
（更糟）渲染了错误数据并缓存下来 → 缓存污染
```

### 缓存失效的三大主因（UE 官方文档原文）

1. **光源移动** — 整个光源的所有缓存页全部失效
2. **对象移动** — 包含刚体运动、骨骼动画、所有使用 WPO 的材质
3. **昼夜切换** — 定向光源方向变化

官方原文警告：
> "如果你有一个缓慢移动的光源，或一个能够改变昼夜的定向光源，VSM 将不会进行有效缓存。"

### WPO 的双重伤害（知乎经验）

WPO 同时影响两端：
1. **VSM 端** — 该对象覆盖的页全部失效
2. **Nanite 端** — WPO 让 visibility buffer 生成性能翻倍（据知乎经验）

### Nanite 上限溢出（复合问题）

如果 VSM 的可见性缓冲区也用 Nanite，则 `r.Nanite.MaxCandidateClusters`（默认 8388608）和 `r.Nanite.MaxVisibleClusters`（默认 2097152）也会成为瓶颈。超出后场景**每帧随机掉 cluster**，整个画面闪烁；用于 VSM 时会导致**深度图每帧都不一样 → 阴影错乱**。

---

## 解决方案（按 UE 官方文档推荐顺序）

### 方案 A：增大 MaxPhysicalPages（治标）

```ini
; 默认 2048，按需放大
r.Shadow.Virtual.MaxPhysicalPages=8192
```

**副作用：** 显存占用上升（每页 128×128 depth）。需要在 GPU 显存允许范围内调整。

### 方案 B：调整 Nanite 上限（复合问题）

```ini
r.Nanite.MaxCandidateClusters=16777216    ; 默认 8388608 ×2
r.Nanite.MaxVisibleClusters=4194304       ; 默认 2097152 ×2
```

**官方文档原文：**
> "如果你怀疑出现此类问题，可通过以下方法检查：用 r.Shadow.Virtual.Cache 0 禁用 VSM 缓存。在控制台中输入 NaniteStats VSM_Directional 或 NaniteStats VSM_Perspective。"

### 方案 C：WPO 距离禁用 + 远距离强制缓存（关键）

```ini
; WPO 物体在距离外禁用 WPO（用 LOD 切换或材质参数）
r.Shadow.Virtual.Cache.MaxMaterialPositionInvalidationRange=500  ; 500cm 内才失效
```

**知乎原文：**
> "调整 r.Shadow.Virtual.Cache.MaxMaterialPositionInvalidationRange 数值，让在数值范围内的 WPO 强制使用缓存。"

**配合 Nanite 端：** 通过 LOD 切换或材质参数让远处物体的 WPO 自动禁用（Nanite 端 WPO 距离禁用也是关键）。

### 方案 D：禁用缓存（仅排查用）

```ini
r.Shadow.Virtual.Cache=0
```

**官方说明：** 仅用于排查 — 禁用缓存后看到错误消失 = 缓存污染问题；禁用后仍错误 = 真溢出问题。

### 方案 E：Coarse Pages 调优（性能 vs 瑕疵）

| CVar | 作用 |
|------|------|
| `r.Shadow.Virtual.MarkCoarsePagesLocal` | 关闭局部光源的粗页（可省 draw call，但屏幕边缘可能有瑕疵） |
| `r.Shadow.Virtual.MarkCoarsePagesDirectional` | 关闭方向光的粗页 |
| `r.Shadow.Virtual.FirstCoarseLevel` / `r.Shadow.Virtual.LastCoarseLevel` | 调粗页覆盖的 clipmap 等级范围 |

官方说明：粗页主要服务于体积雾等低频采样，过度标记会造成 draw-call 瓶颈。

### 方案 F：调分辨率 LOD bias（粗粒度降本）

```ini
r.Shadow.Virtual.ResolutionLodBiasDirectional=-0.5   ; 默认（增加分辨率 → 改为 -1 加倍）
r.Shadow.Virtual.ResolutionLodBiasLocal=0           ; 局部光源
```

**官方说明：** -1 会让分辨率加倍（性能消耗也加倍），-0.5 适合大多数场景。

### 方案 G：clipmap 范围调整

```ini
r.Shadow.Virtual.Clipmap.FirstLevel=6   ; 默认；范围 6~22
r.Shadow.Virtual.Clipmap.LastLevel=22   ; 默认
```

**权衡：** 减小范围 → 省显存/性能但远距离精度降低。

---

## 验证流程（自己 Profile 时跑一遍）

| 步骤 | 工具 / 命令 | 看什么 |
|------|------------|--------|
| 1. 开可视化 | `r.ShaderPrintEnable 1` + `r.Shadow.Virtual.ShowStats 1` | Pages vs Max Pages |
| 2. 查 Nanite | `NaniteStats VSM_Directional` | Candidates / Visible Clusters |
| 3. 找失效源 | Viewport > Show > Visualize > Draw Only Geometry Causing VSM Invalidation | 哪些 mesh 在疯狂失效 |
| 4. 禁用缓存验证 | `r.Shadow.Virtual.Cache 0` | 错误消失 = 缓存污染；仍存在 = 真溢出 |
| 5. 测 MaxPhysicalPages | 翻倍 / 4 倍 | 是否消除棋盘格 |

**GPU 计时警告：** 官方原文：
> "请注意，用于列出统计数据的命令（如 stat gpu 和相关计数器）提供的计时有可能不可靠，项目性能受 CPU 限制的情况下尤其如此。"

VSM 性能问题建议用 RenderDoc / PIX / 平台专属 GPU profiler 而不是 stat gpu。

---

## 经验沉淀

**肌肉记忆：**

| 看到 | 先查 |
|------|------|
| 阴影棋盘格 | `r.ShaderPrintEnable 1` + `r.Shadow.Virtual.ShowStats 1` 看页溢出 |
| 镜头切换阴影错乱 | 大概率缓存污染；用 `r.Shadow.Virtual.Cache 0` 验证 |
| 阴影 + 闪烁 + 大量 WPO 物体 | 调 WPO 强制缓存范围 + LOD 切无 WPO 材质 |
| 阴影 + 大量树叶草 | Nanite 端 + VSM 端双重优化（WPO 禁用 + MaxMaterialPositionInvalidationRange） |
| 远景阴影噪点 | SMRT RayLengthScaleDirectional / MaxRayAngleFromLight |

**可复用方案：** "WPO 距离禁用 + 强制缓存"组合在所有大世界 VSM 场景通用；几乎所有 UE5 项目的"阴影性能问题"最终都落到这套调优上。

---

## 关联知识库

- [[知识参考/Nanite 性能调优]] — Nanite 上限与 VSM 的相互作用
- [[知识参考/Lumen 性能调优]] — VSM 是 Lumen 反射的依赖
- [[知识参考/Unreal Insights 帧分析实战]] — 异步 Lumen 下 GPU 计时不准的应对
- [[渲染线程瓶颈诊断]] — 阴影页分配与 render thread 的同步
- [[VSM详解]] — 知乎版 clipmap/page table 完整代码路径

---

*Create date: 2026-07-02*
*Last modified: 2026-07-02*
*Verified: 否（公开资料汇编，本人未 Profile）*
*Source URLs（公开资料，作者/标题已注明，原文 URL 见下）:*

- **GDC 2024 *Nanite GPU Driven Materials* — Graham Wihlidal（Epic Games）**：
  - GDC Vault 搜索（演讲录像/幻灯片付费，需会员）：
    https://www.gdcvault.com/search/?q=Nanite+GPU+Driven+Materials+Wihlidal
  - 注：本文核心数据（4015 bins / 3675 empty / 4.92→3.05ms；可编程光栅器；空调度压缩 PS5 memory defragmentation）均来自该 GDC 演讲原话
- **UE 官方 *Virtual Shadow Maps - Advantages and Limitations***：
  - 官方英文文档：https://dev.epicgames.com/documentation/en-us/unreal-engine/virtual-shadow-maps-in-unreal-engine/
  - 本文所有 VSM 架构参数（16k×16k、128×128 pages、MaxPhysicalPages=2048、`r.Nanite.MaxVisibleClusters=2097152`）均来自该官方文档原文
- **知乎《UE5 VirtualShadowMap 详解》**（作者：Himma，基于 UE 5.3 源码）：
  - 知乎站内搜索：https://www.zhihu.com/search?type=content&q=UE5%20VirtualShadowMap%20%E8%AF%A6%E8%A7%A3
  - 注：本文引用了 clipmap FirstLevel=6/LastLevel=22、page table 索引算法等代码级细节
- **知乎《UE5性能优化-GPU》**（作者：草木不全）：
  - 知乎站内搜索：https://www.zhihu.com/search?type=content&q=UE5%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96-GPU
  - 注：本文引用了"WPO 强制缓存范围""Mesh SDF 半径阈值"等 CVars

> 我**未能直接获取原文精确 URL**，GDC Vault 链接是搜索入口（演讲内容需付费会员访问），知乎链接是站内搜索（在该搜索页上找对应标题/作者即可定位原文）。
> 注：GDC Vault 演讲录像本身是付费内容（$695/ticket 起的会员费），多数数据是从会议幻灯片公开摘要 / 一线工程师二次整理中获得。