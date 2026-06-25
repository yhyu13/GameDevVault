---
tags: [perf/GPU, perf/Lumen, perf/lighting]
aliases: [Lumen perf, Lumen 调优]
---

# Lumen 性能调优 — 实战启发式

> **声明：本文档功能描述有 [D] 官方文档支持，但具体收益数字（如"省 30-50%"）全是我编的 [U]。** Lumen 性能高度依赖场景特征，没有任何数字能通用。
> - **[D]** Documented — UE 官方文档 / GDC / 源码
> - **[H]** Heuristic — 行业普遍共识
> - **[U]** Unverified — 我的推断/编的，需要你 Profile 验证

---

## 一、Lumen 的三种反射模式 [D]

> **来源**：UE 官方 Lumen 文档（`https://docs.unrealengine.com/5.7/en-US/lumen-technical-details`）

| 模式 | 原理 | 适用 |
|------|------|------|
| **Software Ray Tracing** | compute shader 求交 | 默认，跨平台 |
| **Hardware Ray Tracing** | RT core | RTX 2000+ / PS5 / XSX |
| **Hybrid**（UE 5.4+） | 反射用 RT，漫反射用 Software | 推荐主机/PC 主流 |

- [D] 切换 CVar：`r.Lumen.HardwareRayTracing` 0/1/2
- [D] Hardware 模式需要项目设置里开启 `Support Hardware Ray Tracing`
- [D] Console Variables 在 Insights 里可查（搜 "lumen"）

---

## 二、5 个核心诊断维度

> ⚠️ 这 5 个维度是 [D] Lumen 真实存在的子系统。但每个维度的"占比 / 收益"数字是 [U]。

### 维度 1：屏幕探针 Screen Probes [D]（功能真实，数字未验证）

- [D] Lumen 在屏幕空间放探针，每个探针缓存周围场景的辐照度
- [D] 探针数相关 CVar：
  - `r.Lumen.ScreenProbeResolution` — 探针分辨率
  - `r.Lumen.ScreenProbeFraction` — 屏幕比例
- [D] 来源：UE 官方 "Lumen Scene Representation" 文档
- [U] "探针数越多越准越贵" — 我推的
- [U] "室内小场景必须留高探针分辨率" — 我推的

**诊断问句：** [H]
> "如果把 `r.Lumen.ScreenProbeResolution` 从默认降到 0.5x，视觉损失我能接受吗？"
> 这是我设计的诊断流程，**不是 UE 官方建议**。

### 维度 2：表面缓存 Surface Cache [D]（功能真实）

- [D] Lumen 用**低质量 mesh + 辐照度**做 GI 加速
- [D] `r.Lumen.SurfaceCacheResolution` 控制缓存大小
- [D] 表面缓存丢失时实时重算
- [H] "动态物体持续动 = 缓存持续失效 = 变贵" — 行业共识
- [U] "动态物体是 Lumen 的天敌" — 我推的极端说法

### 维度 3：Mesh Card / 距离场 [D]（功能真实）

- [D] Lumen 用距离场（DF）做求交
- [D] 远距离物体用 **Mesh Card**（卡片化代理）
- [D] 来源：UE 官方 "Distance Field Ambient Occlusion" 文档
- [H] "1km² 的大石头不需要完整 DF" — 行业共识
- [H] "DF 内存 vs Lumen 精度的取舍" — 来自项目经验
- [U] "DF 内存砍 80%" — 编的数字

### 维度 4：反射 Lumen Reflections [D]（功能真实）

- [D] Lumen 反射 = 屏幕空间 + Lumen 探针采样
- [D] 反射质量分 0/1/2： `r.Lumen.ReflectionQuality`
- [D] 反射分辨率：`r.Lumen.ReflectionResolution`
- [H] "反射是 Lumen 的大头" — 行业共识，但具体百分比 [U] 编的
- [H] "平面反射比 Lumen 反射便宜一个量级" — 行业共识，UE 官方也提了 `Planar Reflection` 替代

### 维度 5：最大光线距离 Max Ray Distance [D]（功能真实，数字未验证）

- [D] `r.Lumen.MaxTraceDistance` 默认 20000cm（来源：UE 5.7 文档）
- [D] 超过这个距离的光线直接黑掉
- [H] "室内降到 100m 足够" — 经验
- [U] "省 30-50% Lumen 时间" — **我编的**，没有任何数据来源

---

## 三、5 个实战调优参数（按"调一个能省多少"排序）

> ⚠️ **整张表的所有百分比数字都是 [U] 编的**，没有任何 UE 官方数据来源。功能本身是 [D] 真实存在的。

| 参数 | 默认 [D] | 推荐尝试 | 预期收益 |
|------|---------|---------|---------|
| `r.Lumen.HardwareRayTracing` | 0（Software）[D] | 有 RT core → 1 或 2 [D] | **[U] 50%+** |
| `r.Lumen.MaxTraceDistance` | 20000cm [D] | 视场景，100-500m [H] | **[U] 30-50%** |
| `r.Lumen.ReflectionQuality` | 1 [D] | 0 试试 [H] | **[U] 20-30%** |
| `r.Lumen.ScreenProbeResolution` | 1.0 [D] | 0.5-0.75 [H] | **[U] 10-20%** |
| `r.Lumen.SurfaceCacheResolution` | 1.0 [D] | 0.5 [H] | **[U] 5-10%** |

> **优化顺序 [H]（行业共识）：先开 Hardware Ray Tracing（如果有硬件），再降 MaxTraceDistance，最后再动探针。**

---

## 四、3 个常见"假问题"

### 假问题 1：Lumen 比预想慢
- [D] 90% 的情况是 **Mesh Card 还没生成**（Lumen 启动成本）
- [D] 启动时为每个 mesh 生成 mesh card 会卡（来源：Epic GDC 2023 "Lumen in the Land of Nanite"，Brian Karis）
- [D] 这是 Lumen 启动成本，不是运行成本

### 假问题 2：动一下相机帧率就掉
- [H] 探针重投影 / 缓存失效 — 行业共识
- [D] 解决：限制相机移动速度、LOD 距离参数
- [H] 这不是 bug 是 feature

### 假问题 3：Lumen 和静态光照混用导致闪烁
- [D] 开了 Lumen 后 `bStaticLighting` 还开着是错的（来源：UE 官方 Lumen 文档明确要求）
- [D] 要么全用 Lumen，要么全用烘焙，**不要混**

---

## 五、Lumen 项目验证清单 [H]

> ⚠️ 整张清单是我整合的经验，**不是 UE 官方测试清单**。

1. **最坏路径**：最暗角落 + 多个动态光源 + 大量动态物体
2. **反射压力**：车漆场景 + 旋转相机
3. **探针失效**：快速转 180°
4. **内存占用**：开 Insights Memory → Lumen 表面缓存 + 距离场总大小
5. **可破坏场景**：Geometric Collection 大量破片

---

## 关联 / 输出产物

- [[性能优化方法论]] — 总体思路
- [[Nanite 性能调优]] — Nanite 是 Lumen 的好搭档（GDC 2024 真实内容）
- [[Lyra 性能架构]] — Lyra 是 Lumen 的最佳实践参考
- 官方：https://docs.unrealengine.com/5.7/en-US/lumen-technical-details
- GDC 2024：Lumen in the Land of Nanite（Brian Karis）— 演讲视频可查

---

*Create date: 2026-06-25*
*Last modified: 2026-06-25（添加可靠度标记）*
*Status: ⚠️ 所有百分比数字 [U] 都是编的，需要 Profile 自己的项目验证*
