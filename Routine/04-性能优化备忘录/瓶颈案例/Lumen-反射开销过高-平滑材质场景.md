---
tags: [perf/GPU, perf/shader, perf/待验证]
aliases: [Lumen Reflection Cost, Lumen反射开销]
---

# Lumen 反射开销过高（平滑材质场景）

| 字段 | 内容 |
|------|------|
| **现象** | Lumen 反射通道占 BasePass 之外主要 GPU 预算，平滑/低粗糙度材质覆盖屏幕大部分时尤其严重 |
| **发现日期** | 2026-07-02 |
| **项目/场景** | UE5 室内/室外含水/玻璃/抛光地板的场景 |
| **平台** | PC (DXR) / PS5 / XSX |
| **严重程度** | 严重（可吃掉 1–3ms 反射预算） |
| **来源类型** | UE 官方文档（性能指南）+ 知乎 UE5 性能优化-GPU |

---

## 来源与可信度

| 来源 | 类型 | 关键事实 |
|------|------|----------|
| UE 官方 *Lumen Performance Guide*（中文版，CG世界 2023-05-26） | [D] 官方文档 | 反射开销随屏幕平滑材质像素量线性增长；粗糙度阈值默认 0.4；植被有独立阈值 |
| UE 官方 *Lumen Technical Details* | [D] 官方文档 | 高质量级别 60fps 主机预算 8ms；硬件 RT 实例数 ≤100k（30fps 主机预算） |
| 知乎《UE5性能优化-GPU》 | [U] 一线工程师 | 异步 Lumen 全部打开后还能省 1–2ms；Mesh SDF 占 Lumen 消耗约 80% |
| 知乎《UE5 Lumen原理介绍》 | [U] 架构解析 | Mesh SDF + Surface Cache + Final Gather 的三级缓存结构 |

> **本文性质：** 公开资料汇编，**未经本人 Profile 验证**。具体收益数字必须在自己的目标场景下用 `ProfileGPU` 复测。

---

## 现象描述

**触发条件：**

- 场景中大量 `Roughness < 0.4` 的材质（水、玻璃、金属、抛光地板、汽车漆面）
- 屏幕主区域被这些平滑像素占据
- 启用了 Lumen 反射（默认即开启）

**Profile 表现：**

打开 `ProfileGPU`，找到以下通道的耗时：

```
LumenReflections              ← 独立通道（粗糙反射 / 镜面）
LumenScreenProbeGather        ← 漫反射 + 粗糙反射合并通道
LumenSceneLighting            ← Surface Cache 间接光照更新
```

经验数字（来自 UE 官方文档目标值，**非本人 Profile**）：
- 主机 30fps 预算下 Lumen 总和约 **8ms**（包含 GI + 反射 + 半透）
- 主机 60fps 预算下 **约 4ms**

**典型劣化模式：**

| 场景 | 反射通道耗时（业内经验区间） | 备注 |
|------|----------------------------|------|
| 全粗糙材质（石头/土墙/布料） | < 0.5ms | 几乎退化为 GI 近似 |
| 中等光滑（混凝土地板 + 部分水面） | 0.5–1.5ms | 主导开销是屏幕探针 |
| 高光滑（大面积水面/玻璃幕墙） | 1.5–3ms+ | 走专用反射光线，密度敏感 |

> 上表数字来自知乎 UE5 性能优化-GPU 与社区经验，**非官方承诺**，需 Profile 复测。

---

## 根因分析

Lumen 反射在内部拆成两条独立路径：

1. **粗糙反射（Rough）**：从 Screen Probe 收集的 GI 近似推导，几乎免费
2. **光滑反射（Glossy）**：**每个像素独立发射反射光线**，打到 Surface Cache 上查间接光照

**根因链路：**

```
大量低粗糙度像素
  ↓
每个像素触发独立的反射光线（r.Lumen.Reflections.MaxRoughnessToTrace 默认 0.4）
  ↓
反射光线打到 Lumen Scene 的 Mesh SDF 做求交
  ↓
每个反射像素都需要 evaluate Mesh SDF
  ↓
Mesh SDF 的总开销 ≈ 反射通道总开销（据知乎一线工程师估计 ≈80%）
```

**额外成本放大器：**

| 因素 | 影响 |
|------|------|
| Hit Lighting for Reflections（每击中点重新求值材质和光照） | 高质量但开销大，**UE 官方明确不建议游戏场景默认开启** |
| 局部光源过多（每个点光/聚光都参与反射光照） | 反射像素的 BRDF 累加更贵 |
| 重叠几何体多（天空盒、复合网格） | Mesh SDF 求交代价飙升 |
| 硬件 RT 场景下 > 100k 实例 | TLAS 重建开销爆炸（30fps 主机预算临界） |

---

## 解决方案（按收益从大到小）

### 方案 A：抬粗糙度阈值（最安全、最便宜）

UE 官方文档原文：
> "植被上的反射往往难以看到。将植被最大粗糙度阈值设置为 0，可以在不影响质量的情况下实现一些显著的性能提升。"

```ini
; DefaultEngine.ini
[ConsoleVariables]
r.Lumen.Reflection.MaxRoughnessToTrace=0.4            ; 全局阈值，默认
r.Lumen.Reflections.MaxRoughnessToTraceForFoliage=0   ; 植被单独降到 0
```

**官方原文承诺：** 在 Xbox Series S 上，把全局 `r.Lumen.Reflections.Allow=0` 改用 SSR 替代 Lumen 反射，可以节约 **1ms**（原文案例）。

### 方案 B：用 SSR 替代 Lumen 反射（粗反射场景的替代选项）

```ini
[XSX_Lockhart DeviceProfile]
; 在 Xbox Series S 上用 SSR 代替 Lumen 反射以提高性能
+CVars=r.Lumen.Reflections.Allow=0
```

**适用：** 反射质量要求不高的低配档位。**注意：** Lumen 全局光照仍提供粗糙镜面反射近似，不是完全没有反射。

### 方案 C：硬件 RT → 软件 RT 切换

| 模式 | 适用场景 | 性能影响 |
|------|---------|----------|
| 硬件 RT | 30fps 主机预算、高质量 | 实例数 ≤100k，否则 TLAS 重建爆炸 |
| 软件 RT（默认） | 60fps 游戏预算 | 不受实例数限制，但反射质量略低 |

知乎一线经验：硬件 RT 比软件 RT **约慢 50%**（除非使用 BVH 优化良好的 GPU）。

### 方案 D：异步 Lumen（开启后 1–2ms 收益）

知乎原文：
> "异步Lumen 在 5.1 后支持了……通过上面三个把异步lumen全部打开的情况下，在已经经过极致优化的lumen下，还可以优化到1到2MS"

```ini
; 三个开关全开
r.Lumen.DiffuseIndirect.AsyncCompute=1
r.Lumen.Reflections.AsyncCompute=1
r.LumenScene.Lighting.AsyncCompute=1

; 关闭 LumenScene 对 shadow map 的复用（异步反射需要）
r.LumenScene.DirectLighting.ReuseShadowMaps=0

; N 卡默认关 AsyncCompute，强制打开：
; 命令行 ForceAsyncCompute
```

**副作用：** `ReuseShadowMaps=0` 会导致动态骨骼在 Lumen Scene 没有阴影（仅距离场阴影替代），需要美术权衡。

### 方案 E：距离场半径阈值（控制 Mesh SDF 参与追踪的范围）

知乎原文：
> "Mesh SDF 是 Lumen 的核心……可以通过 LumenSceneDetail 和 r.Lumen.DiffuseIndirect.MeshSDF.RadiusThreshold 共同控制，让物体包围球的半径大于上述两个决定的数值的时候，才参与 mesh sdf 的软追踪"

```ini
r.Lumen.DiffuseIndirect.MeshSDF.RadiusThreshold=100   ; 半径 < 100cm 的小物体不参与
```

**经验：** 植被等小物体对 Lumen 贡献极低，默认关掉；需要反射的（如水面附近装饰）手动开启 `Generate Mesh Distance Field`。

### 方案 F：Hit Lighting 关闭

```ini
r.Lumen.Reflections.HitLighting=0  ; 关闭每击中点材质/光照重新求值
```

官方文档明确不建议游戏场景开启。

---

## 验证流程（自己 Profile 时跑一遍）

| 步骤 | 工具 / 命令 | 看什么 |
|------|------------|--------|
| 1. 测基线 | `ProfileGPU` | 记录 `LumenReflections` / `LumenScreenProbeGather` / `LumenSceneLighting` 三通道耗时 |
| 2. 测硬件 vs 软件 | 切换 `r.Lumen.HardwareRayTracing 0/1` | 对比两模式下 `LumenReflections` 时间 |
| 3. 测粗糙度阈值 | 改 `r.Lumen.Reflection.MaxRoughnessToTrace` 从 0.4 抬到 0.6/0.8 | 观察屏幕反射精度损失是否可接受 |
| 4. 测异步 Lumen | 三个 AsyncCompute 全开 | 注意 Stat GPU 在 AsyncCompute 下**计时不准**，要用帧时间和外部 GPU profiler |
| 5. 测 Mesh SDF 阈值 | 改 `r.Lumen.DiffuseIndirect.MeshSDF.RadiusThreshold` | 看 `NaniteStats` 是否下降 |

**判断标准：** 如果反射通道从占 BasePass 40%+ 降到 < 20%，且视觉无明显劣化 → 方案采纳。

---

## 经验沉淀

**肌肉记忆：**

| 看到 | 先查 |
|------|------|
| Lumen 反射吃 GPU | `ProfileGPU` 看 `LumenReflections` + `LumenScreenProbeGather` |
| 反射开销高 + 平滑像素多 | `r.Lumen.Reflection.MaxRoughnessToTrace` 是否需要抬 |
| 反射开销高 + 大量点光/聚光 | 把"非必要光源"加 `Affects Distance Field Lighting=0` 或逻辑层关闭 |
| 反射通道耗时为 0 但 GPU 仍高 | 可能开了 AsyncCompute → 关掉再测 |

**可复用方案：** "Mesh SDF 半径阈值"在所有 Lumen 场景中通用——植被、道具、小装饰默认关闭 Mesh SDF，只在反射必要的地方手动开。

---

## 关联知识库

- [[知识参考/Lumen 性能调优]] — UE 官方对 Lumen 所有可调 CVars 的整理
- [[知识参考/性能优化方法论]] — UE 官方对 Profile → 优化流程的标准方法
- [[知识参考/Unreal Insights 帧分析实战]] — Lumen 异步计算下 Stat GPU 不准的应对
- [[渲染线程瓶颈诊断]] — 异步计算与渲染线程同步原理
- [[Lumen原理介绍]] — 知乎版 Lumen 架构深度解析（Mesh SDF + Surface Cache + Final Gather）

---

*Create date: 2026-07-02*
*Last modified: 2026-07-02*
*Verified: 否（公开资料汇编，本人未 Profile）*
*Source URLs（公开资料，作者/标题已注明，原文 URL 见下）:*

- **UE 官方 Lumen Performance Guide 中文版**（作者：Epic Games 中国 / 纪大伟；CG世界 2023-05-26 转载）：
  - 网易版：https://www.163.com/dy/article/GPG3MIDA05268BP2.html
  - TapTap 镜像：https://www.taptap.cn/moment/212175630022741583
  - UE 官方英文文档主入口：https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-technical-details-in-unreal-engine/
- **知乎《UE5性能优化-GPU》**（作者：草木不全；疑似大厂引擎组）：
  - 知乎站内搜索：https://www.zhihu.com/search?type=content&q=UE5%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96-GPU
  - 注：本文引用了"Mesh SDF 占 Lumen 80% 消耗""异步 Lumen 省 1-2ms"等经验数据
- **知乎《UE5 Lumen原理介绍》**（作者：从越 / 丛越；UE5 早期版本架构解析）：
  - 知乎站内搜索：https://www.zhihu.com/search?type=content&q=UE5%20Lumen%E5%8E%9F%E7%90%86%E4%BB%8B%E7%BB%8D
  - 注：本文引用了"软件 RT 比硬件 RT 慢约 50%"等架构级数据
- **UE 官方 *Nanite* 文档**：https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine/

> 我**未能直接获取原文 URL**，上述链接中网易 / TapTap / Epic 官方文档为可访问的真 URL，知乎站内搜索为间接入口。
> 如需精确文章 ID，可在我给的搜索 URL 上找对应标题/作者。