---
tags: [radar/P0, radar/图形渲染, radar/引擎特性, radar/已可掌握候选]
aliases: [UE5 Lumen, Lumen GI, Lumen 反射, Lumen 实战手册, Lumen 全局光照]
quarterly_review: 2026-Q3
---

# Lumen — UE5 全局光照 + 反射（day-job RAG 渲染知识主轴）

| 字段 | 内容 |
|------|------|
| **技术名称** | UE5 Lumen（全局光照 + 反射） |
| **类别** | 图形渲染 / 引擎特性 |
| **当前优先级** | P0-渲染特性（day-job 必考） |
| **首次加入雷达** | 2026-07-12（由 [[2026-07-05-三能力对账]] 推动） |
| **最后评估日期** | 2026-07-12 |

---

## 一句话简介

> UE5 实时的全局光照（GI）+ 动态反射系统，**替代传统烘焙光照 + SSR**，是 Lyra / UE5 项目默认渲染管线核心。**day-job 三大渲染特性之首**，vault 积累最厚，是 Q3 末升"已掌握"的首选目标。

---

## 当前 vault 状态 ✅ 厚

| 类型 | 文件 | 行数 / 摘要 |
|------|------|-------------|
| 论文笔记 | [[Lumen/Lumen-SIGGRAPH-2021]] | 官方 SIGGRAPH 2021 演讲 + 10 张 slide + 完整 transcript |
| 论文笔记 | [[Lumen/Lumen-HowItActuallyWorks-UE5]] | 内部实现机制拆解 |
| 论文笔记 | [[Lumen/Lumen-实战手册：调试-Profile-定制-跨场景适配指南]] | 工程实战指南 |
| Shader 案例 | [[03-Shader与特效案例集/C03/Lumen-反射降级]] | 4 档降级 + AI 增强（NeRF Reflection Cache）|
| Shader 案例 | [[03-Shader与特效案例集/C04/Lumen-GI-漫反射]] | Surface Cache + NRC 替代 |
| 性能优化 | [[04-性能优化备忘录/知识参考/Lumen 性能调优]] | 性能调优方法论 |
| 性能瓶颈 | [[04-性能优化备忘录/瓶颈案例/Lumen-反射开销过高-平滑材质场景]] | 反射开销案例 |

---

## Day-job 关联

- **RAG 索引主轴**：day-job = RAG + Mac Game Harness（LLM-driven UE on Mac），Lumen 是 LLM 能否正确调用 UE 渲染管线的**第一道门槛**
- **Mac Metal RHI 适配**：UE5.4+ Mac 支持 Lumen，需要评估 Metal vs DX12 路径差异
- **关键风险**：Mac Metal RHI 上 Lumen 反射 tier 降级可能与 DX12 不一致

---

## 待补缺位 ⚠️

| 缺口 | 优先级 | 计划 |
|------|--------|------|
| **Mac 平台 Lumen 性能基线** | P0 | W29 建 `Routine/Mac-平台/` 子目录时纳入 |
| **Surface Cache / Probe Densification 源码追踪** | P1 | W30+ 写 source-analysis |
| **反射 tier L1/L2/L3 详细降级链** | P2 | 已被 W3 shader 部分覆盖 |

---

## 升"已掌握"门槛

**8/7 月度回顾**复评。门槛：
- [ ] Mac Metal RHI 上跑通 Lumen 反射降级 / GI 漫反射 demo
- [ ] 至少 1 次性能调优实战（验证 Surface Cache 调参有效）
- [ ] 至少 1 个 source-analysis 笔记（Surface Cache / Probe）

**达成后**：移入 `Routine/05-技术雷达/已掌握/` bucket，从活跃雷达移除。

---

## 关联

- [[2026-07-05-三能力对账-是否满足-AI训练pipeline-UE5垂直领域-工程化]] — 推动 Lumen 入 P0 的源动力
- [[2026-07-12-W28周复盘-2026-07-06至07-12]] — W28 复盘里把 Lumen 标为"最厚候选"
- [[Nanite]] / [[VSM]] — 渲染三大特性同批次入 P0

---

*Create date: 2026-07-12*
*Last modified: 2026-07-12*
