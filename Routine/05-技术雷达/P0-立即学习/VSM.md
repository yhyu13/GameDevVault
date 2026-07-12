---
tags: [radar/P0, radar/图形渲染, radar/引擎特性, radar/缺源码分析, radar/阴影]
aliases: [UE5 VSM, Virtual Shadow Map, 虚拟阴影映射, VSM 页表, VSM 阴影]
quarterly_review: 2026-Q3
---

# VSM — UE5 虚拟阴影映射（day-job 阴影 LRU 调优主轴）

| 字段 | 内容 |
|------|------|
| **技术名称** | UE5 VSM（Virtual Shadow Map，虚拟阴影映射） |
| **类别** | 图形渲染 / 引擎特性 / 阴影 |
| **当前优先级** | P0-渲染特性（day-job 必考） |
| **首次加入雷达** | 2026-07-12（由 [[2026-07-05-三能力对账]] 推动） |
| **最后评估日期** | 2026-07-12 |

---

## 一句话简介

> UE5 虚拟化阴影贴图系统，**用页表 + Cluster + Moments 解决传统 CSM 在大场景下的分辨率浪费**。day-job 三大渲染特性之三，W28 刚从"极薄"补到"中"（W6 shader 763 行），**W29 必升到 source-analysis 级**。

---

## 当前 vault 状态 ⚠️ 中（补完中）

| 类型 | 文件 | 行数 / 摘要 |
|------|------|-------------|
| Shader 案例 | [[03-Shader与特效案例集/W6/VSM-Virtual-Shadow-Map]] | 页表 + Moments + Neural Variance Filter（763 行）⭐ W28 落盘 |
| 性能瓶颈 | [[04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]] | 页溢出案例 |
| QA 卡牌 | `03-Shader与特效案例集/W6/VSM-Virtual-Shadow-Map.html` | 12 题互动卡（711 行）|

> **历史状态**：W28 前**只有 1 篇性能瓶颈**，无完整技术笔记 → [[2026-07-05-三能力对账]] 评为"极薄、最大缺位"
> **当前状态**：W28 落盘 W6 shader 763 行 + QA 卡，补到"中" → **仍缺源码分析**

---

## Day-job 关联

- **阴影 LRU 调优**：day-job = RAG + Mac Game Harness（LLM-driven UE on Mac），VSM 是 LLM 理解 UE 阴影管线的**关键节点**
- **Mac Metal RHI 适配**：UE5.4+ Mac 支持 VSM，但 Page Table 内存布局在 Metal vs DX12 上的差异需要实测
- **关键风险**：VSM 页溢出在 Mac Apple Silicon 上的 LRU 行为可能与 DX12 不一致 → [[04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]] 已有先例

---

## 待补缺位 ⚠️

| 缺口 | 优先级 | 计划 |
|------|--------|------|
| **页表 / Cache / Nanite 集成 完整源码分析** | P0 | **W29 必做**：`02-引擎源码分析库/Unreal-Engine/W29/UE5-VSM-源码追踪.md`（≥ 600 行）|
| **移动端 / Mac 平台 VSM 降级策略** | P0 | W29 Mac 子目录起头时纳入 |
| **VSM 与 Lumen 反射 / Nanite WPO 协同** | P1 | 8/7 月度回顾时评估是否需要专题 |

---

## 升"已掌握"门槛

**Q3 末（9/25）**复评。门槛：
- [ ] source-analysis 笔记 ≥ 600 行（覆盖页表 / Cache / Nanite 集成）
- [ ] Mac Metal RHI 上跑通 VSM 阴影 demo（验证页溢出处理）
- [ ] 至少 1 次 VSM CVAR 调优实战

**达成后**：移入 `Routine/05-技术雷达/已掌握/` bucket。

---

## W29 硬计划

> [[2026-07-12-W28周复盘-2026-07-06至07-12]] 的"承诺兑现率 30%"自爆里，VSM 升 source-analysis 是**唯一**能在 W29 兑现的承诺。**不可再拖**。

---

## 关联

- [[2026-07-05-三能力对账-是否满足-AI训练pipeline-UE5垂直领域-工程化]] — 推动 VSM 入 P0（极薄 → 必补）
- [[Lumen]] / [[Nanite]] — 渲染三大特性同批次入 P0
- [[03-Shader与特效案例集/W6/VSM-Virtual-Shadow-Map]] — W28 落盘起点

---

*Create date: 2026-07-12*
*Last modified: 2026-07-12*
