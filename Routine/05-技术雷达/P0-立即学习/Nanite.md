---
tags: [radar/P0, radar/图形渲染, radar/引擎特性, radar/缺源码分析]
aliases: [UE5 Nanite, Nanite 虚拟几何, Nanite 材质管线, Nanite Mesh Pass]
quarterly_review: 2026-Q3
---

# Nanite — UE5 虚拟几何 + 材质管线（day-job 虚拟几何 shader 适配）

| 字段 | 内容 |
|------|------|
| **技术名称** | UE5 Nanite（虚拟几何 + 材质管线） |
| **类别** | 图形渲染 / 引擎特性 |
| **当前优先级** | P0-渲染特性（day-job 必考） |
| **首次加入雷达** | 2026-07-12（由 [[2026-07-05-三能力对账]] 推动） |
| **最后评估日期** | 2026-07-12 |

---

## 一句话简介

> UE5 虚拟化微多边形几何系统，**用 Cluster DAG + Page Streaming 在 GPU 上实时渲染电影级 mesh 资产**。day-job 三大渲染特性之二，**vault 积累中等**——shader + 性能覆盖到位，**但缺源码分析**（W29/W30 必补）。

---

## 当前 vault 状态 ⚠️ 中

| 类型 | 文件 | 行数 / 摘要 |
|------|------|-------------|
| Shader 案例 | [[03-Shader与特效案例集/W5/Nanite-材质管线]] | 5-bin material + Neural Eval + Latent Code（763 行）|
| 性能优化 | [[04-性能优化备忘录/知识参考/Nanite 性能调优]] | 性能调优方法论 |
| 性能瓶颈 | [[04-性能优化备忘录/瓶颈案例/Nanite-WPO禁用距离-破面修复]] | WPO 距离问题 |
| 源码分析 | [[02-引擎源码分析库/Unreal-Engine/W27/Nanite-Card-Pack]] | W27 mini-README（卡片集）|

> **缺位**：**没有正式的 source-analysis 笔记**（Mesh Pass / Cluster DAG / Page Streaming 三件套源码追踪）

---

## Day-job 关联

- **虚拟几何 shader 适配**：day-job = RAG + Mac Game Harness（LLM-driven UE on Mac），Nanite 是 LLM 调用 UE 高密度场景的**第二道门槛**
- **Mac Metal RHI 适配**：UE5.4+ Mac 支持 Nanite，但 Page Streaming 在 Apple Silicon 上的内存压力 vs DX12 差异需要实测
- **关键风险**：Nanite WPO（World Position Offset）禁用距离逻辑在 Mac 上的 CVAR 兼容性

---

## 待补缺位 ⚠️

| 缺口 | 优先级 | 计划 |
|------|--------|------|
| **Mesh Pass / Cluster DAG / Page Streaming 源码分析** | P0 | **W29-W30 两周**写 `02-引擎源码分析库/Unreal-Engine/W29-Nanite-源码追踪.md`（≥ 800 行）|
| **Mac 平台 Nanite 性能基线** | P0 | W29 Mac 子目录起头时纳入 |
| **Nanite 材质管线完整拆解** | P1 | 已被 W5 shader 部分覆盖，可补完 |

---

## 升"已掌握"门槛

**Q3 末（9/25）**复评。门槛：
- [ ] source-analysis 笔记 ≥ 800 行（覆盖 Mesh Pass / Cluster DAG / Page Streaming）
- [ ] Mac Metal RHI 上跑通 Nanite 高密度场景 demo
- [ ] 至少 1 次 WPO 实战调优案例

**达成后**：移入 `Routine/05-技术雷达/已掌握/` bucket。

---

## 关联

- [[2026-07-05-三能力对账-是否满足-AI训练pipeline-UE5垂直领域-工程化]] — 推动 Nanite 入 P0
- [[Lumen]] / [[VSM]] — 渲染三大特性同批次入 P0
- [[UnrealMCP-N1UnrealMCP]] — 用 MCP 让 AI Agent 调用 Nanite 工具的潜在路径

---

*Create date: 2026-07-12*
*Last modified: 2026-07-12*
