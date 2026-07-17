---
tags: [weekly-log/W28, weekly-log/2026-Q3, routine/周复盘, routine/历史归档]
aliases: [W28 weekly snapshot, 2026-07-12 W28 复盘]
quarterly_review: 2026-Q3
---

# W28 周复盘(2026-07-06 ~ 2026-07-12)— 历史快照

> **W28 状态**:渲染三大特性(Lumen / Nanite / VSM)正式加入 P0;承诺兑现率 30%,W29 决心补到 70%。
> **本文件性质**:历史快照,只在 Weekly-Log/ 保留,W29+ 复盘见 [[../W29-2026-07-19/W29-周复盘]]

---

## 一、本周产出

### A. P0 雷达补全:渲染三大特性

| 项 | 来源 | vault 状态 |
|----|------|------------|
| [[../../../Routine/05-技术雷达/P0-立即学习/Lumen\|Lumen]] | W28 新加 P0 | 厚(SIGGRAPH 2021 + 实战手册 + W3/W4 shader + 性能) |
| [[../../../Routine/05-技术雷达/P0-立即学习/Nanite\|Nanite]] | W28 新加 P0 | 中(C05 shader + W26 源码 + 性能,缺源码追踪) |
| [[../../../Routine/05-技术雷达/P0-立即学习/VSM\|VSM]] | W28 新加 P0 | 极薄 → 中(C06 shader 763 行 + 页溢出案例,缺源码追踪) |

### B. 渲染三特性论文笔记(后续产出,登记到 W29)

| 论文 | 笔记 |
|------|------|
| Karis 2021 — Nanite | [[../../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry]] |
| Karis 2020 — VSM | [[../../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] |

### C. 02-引擎源码分析库 W28 4 主题

| 主题 | 笔记 | 卡牌 | 大小 |
|------|------|------|------|
| MegaLights 随机光照 | [[../../../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-MegaLights-随机光照\|UE5.8-MegaLights]] | ✅ | 35 KB / 41 KB |
| Substrate 材质系统 | [[../../../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-Substrate-材质系统\|UE5.8-Substrate]] | ✅ | 31 KB / 43 KB |
| InstanceCulling GPU 裁剪 | [[../../../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-InstanceCulling-GPU裁剪\|UE5.8-InstanceCulling]] | ✅ | 35 KB / 53 KB |
| HeterogeneousVolumes 体素体积 | [[../../../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-HeterogeneousVolumes-体素体积\|UE5.8-HeterogeneousVolumes]] | ✅ | 39 KB / 50 KB |

**W28 总产出**:8 文件,~138 KB 源码笔记 + 互动卡牌

---

## 二、Q3 计划与实际

| 计划 | 实际 | 状态 |
|------|------|------|
| 复评 AI-Code-Assistant | ❌ 没动 | 推 W29 |
| 复评 NVIDIA-ACE | ❌ 没动 | 推 W29 |
| 复评 DLSS-FSR | ❌ 没动 | 推 W29 |
| 复评 3DGS | ❌ 没动 | 推 W29 |
| Hunyuan3D:注册 + 跑 5 张图 | ❌ 没动 | 推 W29 |
| **雷达 P0 渲染特性补丁** | ✅ Lumen / Nanite / VSM 入 P0 | **完成** |
| 下周(W29)起补 VSM 源码 | ❌ | 推 W29(见 W29 README) |
| 下周(W29)起补 Nanite 源码 | ❌ | 推 W29(见 W29 README) |
| 下周(W29)起补 Mac 平台 | ❌ | 推 W29(见 W29 README) |

**W28 兑现率**:1/10 显式完成 + 0/3 "下周起头" 完成 = **~10%**(硬数字)

**W28 README 自爆"30%"**:
- 包括 4 主题源码追踪(算渲染三大特性的间接支撑)+ 渲染特性入 P0(算 OKR O1 进展)
- 计入后 ~30%

---

## 三、雷达状态(W28 末)

| 桶 | 数量 | 备注 |
|----|------|------|
| P0-立即学习 | 10 | 7 工具 + 3 渲染特性(新增) |
| P1-持续关注 | 3 | SD-FLUX / Meshy-Luma / LLM-NPC |
| P2-了解即可 | 3 | ElevenLabs / Rust / WorldModels |
| 已掌握 | 0 | 等待首次升档 |
| 已放弃 | 0 | 等待首次降档 |

---

## 四、关联

- [[../W29-2026-07-19/W29-周复盘|W29 复盘]] — 接续
- [[../../../Routine/05-技术雷达/00-README|技术雷达 00-README]]
- [[../../../Routine/02-引擎源码分析库/Unreal-Engine/W28/00-README|W28 源码 README]]

---

*Snapshot date: 2026-07-12(W28 末)*
*Last modified: 2026-07-18(归档到 Weekly-Log)*
