---
tags: [perf/CPU, perf/culling, perf/LOD, perf/待验证]
aliases: [Foliage Cluster Tree, 植被Cluster-Tree粒度]
---

# 植被过度绘制 — Cluster Tree 粒度配置

| 字段 | 内容 |
|------|------|
| **现象** | 植被密集场景 basepass / prepass 的 VS 阶段 overdraw 严重，Render 线程 occlusion query 耗时飙升 |
| **发现日期** | 2026-07-02 |
| **项目/场景** | UE5 开放世界 / 大场景植被（草、灌木、树） |
| **平台** | PC / Console |
| **严重程度** | 中等→严重（basepass 上 1–2ms 浪费） |
| **来源类型** | 知乎 UE5 性能优化-GPU（深度一线经验） |

---

## 来源与可信度

| 来源 | 类型 | 关键事实 |
|------|------|----------|
| 知乎《UE5性能优化-GPU》 | [U] 一线工程师（疑似腾讯/网易等大厂引擎组） | 完整列出 3 个核心 CVar 与调优逻辑；经验数字"basepass 省 2MS 预算" |
| 知乎《UE5场景优化相关》 | [U] 综合 | LOD 系统 / PrecomputedVisibilityVolume / Merge Actors |
| 知乎《UE5性能优化-Render线程》 | [U] 同作者 | occlusion feedback 时序 / GPU Scene 更新 |

> **本文性质：** 知乎一线工程师经验，**未经本人 Profile 验证**。具体粒度参数与项目实际密度强相关。

---

## 现象描述

**触发条件：**

- 大场景植被（PCG 散布 / Foliage Tool / 手动 ISM 放置）
- 单个 `Foliage Actor` / `ISMC` 下密集分布（同一 tile 内上千实例）
- 摄像机俯视/远景看大量植被区域

**Profile 表现：**

```bash
stat gpu
stat rhi
stat sceneRendering
```

观察到：
- **basepass / prepass** 的 **Vertex Shader** 阶段耗时异常高（overdraw 堆积）
- **render thread** 在 occlusion 阶段 spike（feedback 回读慢）

**知乎原文：**
> "如果一个 tile 下有大量的植被，而且植被密度非常浓密的时候，这里不仅会引起分区流送引起 cluster tree 构建的卡顿，也会导致 gpu 下 prepass 和 basspass 消耗过高，因为默认的剔除盒子太大，导致 prepass 和 basspass 存在大量的 vs 的 overdraw。"

---

## 根因分析

### Cluster Tree 剔除的盒子大小问题

UE 用 cluster tree 做 hierarchical occlusion culling：

```
Foliage Actor 内部按 box 划分 cluster
↓
每个 cluster 内部放置若干实例
↓
每个 cluster 发起一次 occlusion query
↓
CPU 读取上一帧 GPU feedback → 决定整个 cluster 整体绘制/剔除
```

**盒子粒度的矛盾：**

| 盒子大小 | 影响 |
|----------|------|
| **太大** | 少量被遮挡的实例"拖累"整个 cluster 整体绘制 → VS overdraw 爆炸 |
| **太小** | cluster 数太多 → occlusion query 次数爆炸 → render thread 耗时高，draw call 也多 |

### 三个核心 CVar（控制 cluster tree 盒子粒度）

知乎原文：
> "引起 cluster tree 盒子的因素有点多，这里主要聊三个。"
>
> - `foliage.MaxOcclusionQueriesPerComponent` — 每个 component 最多盒子数
> - `foliage.MinOcclusionQueriesPerComponent` — 每个 component 最少盒子数
> - `foliage.MinInstancesPerOcclusionQuery` — 每个盒子最小包含的实例数

### Foliage Actor 的 Tile 大小

知乎原文：
> "foliage actor 的默认 tile 的大小是 256"

tile = 256cm = 2.56m。如果一个 tile 里有大量密集植被，会同时放大 cluster tree 构造开销 + GPU basepass 开销。

---

## 解决方案（按收益从大到小）

### 方案 A：调整三个核心 CVar（主要优化手段）

知乎经验：
> "如果这个盒子粒度控制好，在植被比较多的情况下，可以在 prepass 和 basspass 省下 2MS 的预算。"

```ini
; DefaultEngine.ini
[ConsoleVariables]
; 每个 component 的最少盒子数（防止单 component 盒子过少→剔除粒度太粗）
foliage.MinOcclusionQueriesPerComponent=8

; 每个 component 的最多盒子数（防止盒子爆炸→query 太多）
foliage.MaxOcclusionQueriesPerComponent=128

; 每个盒子最少包含的实例数（盒子过小→盒子内实例太少→query 浪费）
foliage.MinInstancesPerOcclusionQuery=4
```

**调优逻辑：**

| 植被密度 | 推荐配置 |
|----------|----------|
| 稀疏（每平米 1–3 株） | 降 `MaxOcclusionQueriesPerComponent`，提 `MinInstancesPerOcclusionQuery` |
| 中等（每平米 5–15 株） | 用默认值 |
| 极密（每平米 30+ 株） | 提 `MaxOcclusionQueriesPerComponent`，降 `MinInstancesPerOcclusionQuery` |

> ⚠️ 注意：这三个 CVar 是**全局生效**，不能 per-component 调。知乎原文："引擎对于 cluster tree 的控制参数都是全局的，有一些 component 适用，也一些则不合适。"
>
> **进阶方案：** 修改引擎源码让这些参数支持 per-component（"因为,如果植被特别影响性能的时候,可以修改引擎支持让这些参数跟着 component 走"）。

### 方案 B：Nanite 植被 vs ISM 植被（UE5 重大决策）

知乎原文：
> "nanite 植被 当植被开启 nanite 后，性能可以提高一倍以上，就算面数非常高，不可视的面都在 nanite culling 阶段剔除掉。"

**两种方案对比：**

| 维度 | Nanite 植被 | ISM/HISM 普通植被 |
|------|------------|------------------|
| 性能上限 | 面数非常高也高效 | 受 cluster tree 盒子配置影响大 |
| WPO（风动） | 影响很大，需要远处禁用 | 支持良好 |
| Mask（镂空/clip） | **影响很大**（知乎："有 mask 性能直接减半"） | 支持良好 |
| 实例数上限 | 受 `r.Nanite.MaxVisibleClusters` 影响（默认 2097152） | 受 cluster tree 盒子数影响 |
| 适用 | 远景、装饰、固定姿态草 | 近景、动画草、必须 mask 的对象 |

**关键约束：**

知乎原文：
> "nanite 植被有两个问题非常影响性能，wpo 和 mask"
> "对于 mask 材质，建议走实体模型。另外，当植被数量到达一定程度，nanite cluster 会随机丢失造成画面闪烁。"

### 方案 C：Mask / WPO 的 Nanite 端优化

```ini
; Mask 材质镂空 → 走实体模型（性能提升显著）
; 或在材质内控制镂空范围

; WPO 距离禁用（用 material parameter collection 或 per-instance custom data 控制）
; 超过某距离 → WPO=0
```

知乎原文（Nanite 端 WPO 影响）：
> "WPO 非常影响性能，当 cluster 剔除后，光栅化后出来的面数也不低，全开 WPO，会让 visibility buffer 生成性能翻倍"

### 方案 D：Single Layer Water 优化（衍生点）

知乎原文：
> "如果水材质的效果不是用面表达的，是用法线贴图去做的话，可以把材质的 mesh 换成一个 quad，高面的 plane，在 singlelayerwater 里非常耗时。"

——非植被但同属"过度几何面数"问题，归类在此备忘。

### 方案 E：LOD 系统（老方案，仍有效）

- 模型导出时设 LOD0–LOD4
- 近景高模、远景蓝/黄低模
- 用 `r.ForceLODShadow` 强制阴影用低 LOD（节省阴影开销）

知乎经验：
> "强制使用 LOD 可以通过 r.ForceLODShadow 调用生成阴影深度的 LOD，这个是个大优化。"

### 方案 F：Merge Actors（碎片模型合并）

知乎原文：
> "能 Merge Actors 就 Merge，Draw Calls 是针对场景中一个个对象去做的。避免损耗，尽量把多的杂碎模型整合成一个大模型，比如说一栋楼。"

——适合静态装饰植被（不可动画、不可 WPO）。

---

## 验证流程（自己 Profile 时跑一遍）

| 步骤 | 工具 / 命令 | 看什么 |
|------|------------|--------|
| 1. 测基线 | `stat gpu` + `stat rhi` | basepass / prepass 的 vertex shader 时间 |
| 2. 关植被做对照 | 在编辑器把所有植被隐藏 | 同样的视角下帧时间差异 = 植被开销 |
| 3. 测三个 CVar | 改 `foliage.MaxOcclusionQueriesPerComponent` 等 | basepass 下降幅度 |
| 4. 测 Nanite 方案 | 把密集植被改 Nanite | 帧时间 vs 视觉（闪烁风险） |
| 5. 测 WPO 距离禁用 | 把 WPO 在 50m 外禁用 | basepass 改善 + 视觉差异 |

**判断标准：** basepass/prepass 的 VS 阶段降到占总 GPU 时间 < 15%。

---

## 经验沉淀

**肌肉记忆：**

| 看到 | 先查 |
|------|------|
| 植被多 + basepass 高 | `foliage.MaxOcclusionQueriesPerComponent` 等三个 CVar |
| 植被多 + render thread occlusion spike | 同上 |
| 植被有 WPO 动画 | Nanite 端距离禁用 WPO |
| 植被有 mask 镂空 | 改实体模型或改 Nanite 时考虑性能减半 |
| 远处植被 + 闪烁 | `r.Nanite.MaxVisibleClusters` 上限溢出 |

**可复用方案：** 三个 `foliage.*` CVar 在所有大世界植被场景中通用——一次调好长期受益。Nanite vs ISM 的取舍需要项目早期决策。

---

## 关联知识库

- [[知识参考/Nanite 性能调优]] — Nanite 上限与植被的相互作用
- [[知识参考/渲染线程瓶颈诊断]] — occlusion feedback 时序
- [[知识参考/Lyra 性能架构]] — Lyra 的 vegetation 流送 / 加载策略
- [[Nanite-WPO禁用距离-破面修复]] — 同主题的 Nanite 端姊妹篇
- [[场景优化]] — 知乎版综合场景优化（含 LOD、Merge Actors、PrecomputedVisibilityVolume）

---

*Create date: 2026-07-02*
*Last modified: 2026-07-02*
*Verified: 否（公开资料汇编，本人未 Profile）*
*Source URLs（公开资料，作者/标题已注明）:*

- **知乎《UE5性能优化-GPU》**（作者：草木不全；本文核心来源）：
  - 知乎站内搜索：https://www.zhihu.com/search?type=content&q=UE5%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96-GPU
  - 注：本文 90% 内容直接引用自该文，包括三个 `foliage.*` CVar 的具体作用、basepass 省 2ms 的经验、Nanite 植被 vs ISM 植被对比
- **知乎《UE5性能优化-Render线程》**（作者：草木不全，同系列）：
  - 知乎站内搜索：https://www.zhihu.com/search?type=content&q=UE5%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96-Render%E7%BA%BF%E7%A8%8B
  - 注：本文"occlusion feedback 时序""GPU Scene 上传"小节引用了同作者的姊妹篇
- **知乎《UE5场景优化相关》**（作者：综合 / 自用备忘）：
  - 知乎站内搜索：https://www.zhihu.com/search?type=content&q=UE5%20%E5%9C%BA%E6%99%AF%E4%BC%98%E5%8C%96%E7%9B%B8%E5%85%B3
  - 注：本文 LOD / PrecomputedVisibilityVolume / Merge Actors 部分引用自此

> 我**未能直接获取原文精确 URL**。如需定位原文，请在知乎站内搜索结果中找标题/作者名匹配的文章。