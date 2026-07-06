---
tags: [perf/GPU, perf/LOD, perf/shader, perf/待验证]
aliases: [Nanite WPO, Nanite Cluster Loss, Nanite破面]
---

# Nanite WPO / Mask 导致 Cluster 丢失与画面闪烁

| 字段 | 内容 |
|------|------|
| **现象** | Nanite 场景出现随机破面、画面闪烁、阴影错乱 |
| **发现日期** | 2026-07-02 |
| **项目/场景** | UE5 大世界 Nanite 网格（植被、建筑、道具） |
| **平台** | PC / PS5 / XSX |
| **严重程度** | 中等→严重（视觉 bug + 阴影连锁错误） |
| **来源类型** | GDC 2024 Wihlidal + 知乎 UE5 性能优化-GPU + UE 官方文档 |

---

## 来源与可信度

| 来源 | 类型 | 关键事实 |
|------|------|----------|
| GDC 2024 *Nanite GPU Driven Materials* — Graham Wihlidal | [D] GDC 演讲 | 可编程光栅器 + 解析 UV 导数 + 辅助通道（helper lanes）数据 |
| 知乎《UE5性能优化-GPU》 | [U] 一线工程师 | WPO 让 visibility buffer 生成翻倍；mask 性能减半；平滑法线组的重要性 |
| UE 官方 *Nanite* 文档 | [D] 官方文档 | `r.Nanite.MaxCandidateClusters=8388608`、`r.Nanite.MaxVisibleClusters=2097152` 默认值 |

> **本文性质：** GDC 演讲 + UE 官方文档 + 一线经验三路交叉，**未经本人 Profile 验证**。具体上限与项目实例数强相关。

---

## 现象描述

### 四种典型破面模式（来自知乎一线经验）

知乎原文分类：

| 模式 | 现象 | 根因 |
|------|------|------|
| **实例数超限** | 场景每帧随机掉面 | Nanite raster 时限制 BVH node 数量 |
| **Candidate cluster 超限** | 整个画面在闪烁 | `r.Nanite.MaxCandidateClusters` 溢出 |
| **Visible cluster 超限** | 整个画面在闪烁 | `r.Nanite.MaxVisibleClusters` 溢出 |
| **流送池显存不足** | 整个场景面数非常低且破面 | CPU feedback 反馈异常 |

### VSM 下的连锁反应

知乎原文：
> "这里要注意一点，当使用 VSM 的时候，如果在 VSM 的 view 这些数量超过了，会导致深度生成每帧都不一样，阴影会错乱。"

### 不可见的 cluster ID 上限

知乎原文：
> "当上述所有条件都足够的情况下，仍然会出现随机破面，画面闪烁的问题。当场景存在大量的 nanite，而且每个 nanite 实例都是分离的，最后退化一个 cluster 的时候，这个 cluster 仍然很多……主要出现在植被非常多的时候。"

——这是一个还没彻底定位的 cluster ID 上限问题。

---

## 根因分析

### Nanite 材质管线的两次进化（GDC 2024）

| 版本 | 阶段 | 限制 |
|------|------|------|
| **UE 5.0** | 初始版本 | 每个独特材质一个全屏 draw call，材质深度 HiZ 优化（HTILE） |
| **UE 5.1** | 可编程光栅器 | 光栅化由材质图驱动；支持 WPO、Mask、UV 接缝处理 |
| **UE 5.4** | 全部计算着色器 | 抛弃所有 SV_Depth / 模板 / 2x2 着色块 |

### WPO 的双重伤害

知乎原文：
> "WPO 非常影响性能，当 cluster 剔除后，光栅化后出来的面数也不低，全开 WPO，会让 visibility buffer 生成性能翻倍。"

——WPO 影响 visibility buffer 生成（CPU/预处理），不只是 GPU shader。

### Mask 材质的性能悬崖

知乎原文：
> "对于 nanite 的材质，最好禁用 mask 材质。使用 mask 材质性能非常低，之前有测试过，有 mask 性能直接减半。"

GDC 2024 数据：Mask 路径下像素 shader 退化（dynamic branch 跳过 64 位原子写入），helper lane 上升。

### 平滑法线组的隐形影响

知乎原文：
> "nanite 的减面是要依赖平滑法线组去决定三角面是否能合并，如果一个模形导出的时候没有平滑法线组，UE 会有 warning，这个要特别注意，如果没有平滑法线组，面数非常爆裂。"

——DCC 导出阶段的设置问题，运行时调参解决不了。

### GDC 2024 实测数据（Wihlidal 在 City Sample 上）

| 阶段 | 耗时 | 说明 |
|------|------|------|
| 初始像素着色器路径（含分类） | **4.92 ms** | 基线 |
| 暴力计算着色器 + 减少 helper lane | **4.62 ms** | 移除 2x2 着色块 |
| 移除空调度 | **3.93 ms** | 着色装箱压缩 |
| 开启 2×2 软件 VRS | **3.05 ms** | 总收益 |

——**总收益 ≈ 38%（4.92 → 3.05）**，但需要 UE 5.4+ + 主机平台。

---

## 解决方案（按 UE 官方文档 + 知乎推荐顺序）

### 方案 A：调高 Nanite 上限（治标）

```ini
r.Nanite.MaxCandidateClusters=16777216   ; 默认 8388608，×2
r.Nanite.MaxVisibleClusters=4194304      ; 默认 2097152，×2
```

**副作用：** 显存占用上升。知乎经验：用于 VSM 时若超过上限会导致阴影深度图每帧不一样。

### 方案 B：WPO 距离禁用（关键）

```ini
; 通过材质 ParameterCollection 或 per-instance custom data
; 距离 > X 时 WPO = 0
```

**实现路径：**

1. 用 `Material Parameter Collection` 暴露全局 `CameraDistance`
2. 在材质里用 `if (CameraDistance > 5000) WPO = 0` （单位 cm）
3. 配合 `LOD` 切换远处用无 WPO 的简化材质

知乎验证：
> "使用世界位置偏移禁用距离调整，超过距离后 WPO 禁用"

### 方案 C：Mask 材质 → 实体模型

知乎原文：
> "对于 mask 材质，建议走实体模型。"

——Mask 镂空改用实体 mesh（多几何体替换），性能可提升 2 倍。

### 方案 D：DCC 导出检查（治本）

知乎原文：
> "nanite 的减面是要依赖平滑法线组……如果一个模形导出的时候没有平滑法线组，UE 会有 warning，这个要特别注意。"

**具体操作：**
- Maya / Blender 导出前检查 normals
- UE 导入时 Console 看 `LogStaticMesh: Warning: ...`
- 缺平滑法线组的网格重新 DCC 端处理

### 方案 E：升级引擎版本（如果还在 5.0）

GDC 2024 Wihlidal 强调：

| 版本 | 推荐场景 |
|------|----------|
| 5.0 | 仅限老项目维护 |
| 5.1 | 引入可编程光栅器 → WPO / Mask 支持 |
| 5.4+ | 全计算着色器 → 空调度压缩 + 2×2 软件 VRS |

知乎原文佐证：
> "UE5 主推的 VSM，性能最好，但是 bug 多，有噪点……对于那些远处，又或者自投影细节比较少的网格体，可以使用代理 nanite 阴影去解决。"

### 方案 F：Nanite 流送池监控

```bash
; 监控流送池状态
r.Nanite.ShowStats 1
```

观察：
- `Streamed Pages` vs `Max Pages`
- 流送池不足时 → 整个场景面数非常低

### 方案 G：VSM 端的 Nanite 协同（VSM 用例）

如果用 VSM 渲染阴影，需要额外考虑：
- 加大 `r.Nanite.MaxVisibleClusters` 避免阴影深度图每帧不一致
- 考虑代理 nanite 阴影（关闭某些 pass）

知乎原文：
> "对于那些远处，又或者自投影细节比较少的网格体，可以使用代理 nanite 阴影去解决。修改引擎支持 proxyshadow component，只设置影响深度 pass，其它 pass 都不绘制。"

---

## 验证流程（自己 Profile 时跑一遍）

| 步骤 | 工具 / 命令 | 看什么 |
|------|------------|--------|
| 1. 检查上限 | `NaniteStats` | Candidates / Visible Clusters vs 上限 |
| 2. 检查 WPO 距离 | 用 `r.MaterialQualityLevel 0/1` 对比 | 是否 WPO 在远处禁用 |
| 3. 检查 Mask 使用 | 场景里搜 `Material Domain = Surface`, `Blend Mode = Masked` | 是否能改实体模型 |
| 4. 检查平滑法线组 | 选中 SM → 检查 warning | DCC 端修复 |
| 5. 看 GPU 耗时 | `ProfileGPU` 看 base pass + visibility buffer | 是否随 WPO 翻倍 |

**判断标准：** Candidates / Visible Clusters 接近但不超过上限的 80%；WPO 在 < 100m 外禁用；Mask 材质占比 < 10%。

---

## 经验沉淀

**肌肉记忆：**

| 看到 | 先查 |
|------|------|
| 画面随机闪烁 + 大世界 | `NaniteStats` 看 Candidates / Visible Clusters |
| 阴影错乱 + Nanite 场景 | VSM 模式下 Nanite 上限溢出 |
| basepass 翻倍 + 有 WPO 物体 | WPO 距离禁用 |
| 某些 mesh 性能差 + Mask | 改实体模型 |
| 一些 mesh 面数爆裂 | DCC 端平滑法线组 |

**可复用方案：** "WPO 距离禁用"几乎所有大世界 Nanite 项目必备；"Mask → 实体"是近景植被的硬性约束。

---

## 关联知识库

- [[知识参考/Nanite 性能调优]] — Nanite 三版本时间线 + GDC 2024 实测数据
- [[VSM-页溢出-阴影棋盘瑕疵]] — Nanite 上限溢出在 VSM 下的连锁反应
- [[植被-过度绘制-Cluster-Tree粒度问题]] — ISM 端的姊妹篇
- [[Lumen-反射开销过高-平滑材质场景]] — Nanite 给 Lumen 提供 Surface Cache 的依赖关系

---

*Create date: 2026-07-02*
*Last modified: 2026-07-02*
*Verified: 否（公开资料汇编，本人未 Profile）*
*Source URLs（公开资料，作者/标题已注明）:*

- **GDC 2024 *Nanite GPU Driven Materials* — Graham Wihlidal（Epic Games）**：
  - GDC Vault 搜索（演讲录像/幻灯片付费）：https://www.gdcvault.com/search/?q=Nanite+GPU+Driven+Materials+Wihlidal
  - 注：本文核心数据（4015 bins/3675 empty、4.92→3.05ms 的 Pixel→Compute→Empty Bin Compression→2×2 VRS 四阶段演化、可编程光栅器版本变化）均来自该演讲
- **UE 官方 *Nanite* 文档**：
  - 英文官方文档：https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine/
  - 注：本文 `r.Nanite.MaxCandidateClusters=8388608`、`r.Nanite.MaxVisibleClusters=2097152` 默认值来自 UE 官方文档
- **知乎《UE5性能优化-GPU》**（作者：草木不全）：
  - 知乎站内搜索：https://www.zhihu.com/search?type=content&q=UE5%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96-GPU
  - 注：本文"WPO 让 visibility buffer 翻倍""Mask 性能减半""平滑法线组缺失导致面数爆裂""cluster ID 上限未定位问题"四条破面分析均引自此文

> 我**未能直接获取原文精确 URL**。GDC 演讲付费，知乎文章需在搜索结果中定位。

> **重要修正提示：** 这篇笔记早期版本曾引用"https://docs.unrealengine.com/..."作为 UE 官方 Nanite 文档 URL —— **这是占位符、不存在**。真实入口为上方 `dev.epicgames.com/documentation/...`（UE 5.x 之后官方文档已迁移至 dev.epicgames.com 域名）。