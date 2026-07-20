---
tags: [source/周归档, source/W30, source/UE5.8, source/Nanite, source/VSM, source/MCP, source/day-job]
aliases: [W30 Mini-Index, W30 微观深挖]
---

# W30 (2026-07-20 ~ 2026-07-26) — 渲染三特性 + day-job 协议 微观源码深挖

> 本周 **3 个新主题**：① Nanite CullRaster + 5.4 材质 Bin 调度 ② VSM Page Table + Page Allocation + Clipmap ③ MCP 3 类端点 + Trust 验证 + Agent Loop。
> **全部是 source analysis（不是 paper note）**——跟 W26/W27/W28 的"源码调用链"配对，形成"高层 + 微观"双层覆盖。

---

## 产出清单

| 主题 | MD | 卡牌 | 大小 | 核心要点 |
|------|:--:|:--:|-----|----------|
| **Nanite CullRaster + 5.4 材质 Bin** | ✅ | ✅ | 21.4 KB + 36 KB 卡牌 | Persistent Culling CS + Atomic Counter + 5.4 材质 Bin 合并（4015→340 bin / 80% 减少）+ 20+ CVar → 源码函数映射 + 10 题 QA |
| **VSM Page Table + Page Allocation** | ✅ | ✅ | 20.3 KB + 36 KB 卡牌 | 128x128 physical page + 4-5 mip 链 + BuildPageAllocations:3227 + 30+ CVar 全表 + 5 类问题诊断 Checklist + 10 题 QA |
| **MCP 3 类端点 + Trust + Agent Loop** | ✅ | ✅ | 22.6 KB + 38 KB 卡牌 | Anthropic MCP 1.1 协议 + UE 5.7+ 集成入口 + 双重 Trust 验证 4 件套 + Agent Loop 模式 + day-job Harness 移植代码 + 10 题 QA |

**总计**：7 个新文件（3 MD + 3 HTML 卡牌 + 本 README），~210 KB 知识增量

## 文件清单

### 源码分析（与论文笔记按 v1.3 紧贴 MD 约定）
- `Routine/02-引擎源码分析库/Unreal-Engine/W30/UE5-Nanite-CullRaster-5.4-材质Bin-源码分析.md` · 21 KB
- `Routine/02-引擎源码分析库/Unreal-Engine/W30/UE5-Nanite-CullRaster-5.4-材质Bin-源码分析.html` · 36 KB · 10 题
- `Routine/02-引擎源码分析库/Unreal-Engine/W30/UE5-VSM-Page-Table-源码分析.md` · 20 KB
- `Routine/02-引擎源码分析库/Unreal-Engine/W30/UE5-VSM-Page-Table-源码分析.html` · 36 KB · 10 题
- `Routine/02-引擎源码分析库/Unreal-Engine/W30/UE5-MCP-3Endpoints-Trust-AgentLoop-源码分析.md` · 22.6 KB
- `Routine/02-引擎源码分析库/Unreal-Engine/W30/UE5-MCP-3Endpoints-Trust-AgentLoop-源码分析.html` · 38 KB · 10 题

---

## W30 跟既有笔记的关系

### Nanite 四件套（"理论 + 论文 + 高层 + 微观"）

| 层级 | 笔记 | 视角 |
|------|------|------|
| 理论 | [[../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry]] | SIGGRAPH 2021 paper + Journey to Nanite 视频 |
| 论文 | (W29) Karis-2021-Nanite-Virtualized-Geometry.html (12 题 QA) | 概念自测 |
| 高层源码 | [[../W26/UE5-Nanite-虚拟几何shader]] | 4 Pass 入口 + 关键类表 |
| **微观源码（W30）** | [[UE5-Nanite-CullRaster-5.4-材质Bin-源码分析]] | CullRaster + 5.4 Bin 调度 + 20+ CVar |
| 卡牌 (W30) | UE5-Nanite-CullRaster-5.4-材质Bin-源码分析.html (10 题) | 源码级 QA |

### VSM 三件套（"理论 + 性能 + 微观"）

| 层级 | 笔记 | 视角 |
|------|------|------|
| 理论 | [[../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] | SIGGRAPH 2020 course + UE 官方文档 |
| 性能 | [[../../04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影质量瑕疵]] | VSM 实战 profile |
| **微观源码（W30）** | [[UE5-VSM-Page-Table-源码分析]] | 30+ CVar + BuildPageAllocations + Nanite/Non-Nanite 双路径 |
| 卡牌 (W30) | UE5-VSM-Page-Table-源码分析.html (10 题) | 源码级 QA |

### MCP 五件套（"理论 + 调用链 + 捡漏 + 协议 + day-job"）

| 层级 | 笔记 | 视角 |
|------|------|------|
| 理论 | [[../../01-论文笔记库/UnrealMCP/Epic-2025-Unreal-MCP-Copilot-Integration]] | Anthropic MCP spec + UE 5.7+ 集成 |
| 高层源码 | [[../W26/UE5-ModelContextProtocol-调用链路]] | MCP 高层 call chain |
| 实战 | [[../W27/UE5-ModelContextProtocol-缺失的捡漏使用指南]] | 哪些 UE 能力没暴露 |
| **协议级源码（W30）** | [[UE5-MCP-3Endpoints-Trust-AgentLoop-源码分析]] | 3 类端点 + Trust 4 件套 + Agent Loop |
| 卡牌 (W30) | UE5-MCP-3Endpoints-Trust-AgentLoop-源码分析.html (10 题) | 协议级 QA |

### Lumen Surface Cache（跟 W29 配对）

| 层级 | 笔记 | 视角 |
|------|------|------|
| 微观源码 | [[../W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析]] | 4 层 Atlas + 21 CVar |

---

## 跟 day-job 的对接

day-job = **RAG + Mac Game Harness,目标"提到 LLM 对 UE 特性的使用"**。W30 3 主题对应的 LLM 训练价值：

| 内容 | 适合喂给 LLM 的形式 | day-job 落地 |
|------|---------------------|----------------|
| Nanite 5.0 → 5.4 Bin 演进 | "4015 → 340 bin 减少 80%" + 5.4 默认开启 WPO | RAG 检索:LLM 评估"5.x 升级"时直接给量化数据 |
| VSM 30+ CVar 全表 | "r.Shadow.Virtual.MaxPhysicalPages 控制 atlas 大小" + "BuildPageAllocations 决定 page evict" | 工具描述:day-job harness 调阴影时精确说"改 X cvar → 影响 Y 函数" |
| MCP 3 类端点 + Trust 4 件套 + Agent Loop | 完整 Python 代码（trust verifier + agent loop） | **直接复用**——day-job harness 按这个 pattern 实现 |

---

## 关键技术发现

1. **Nanite 5.4 材质 Bin 合并是真实可量化的升级**——`NaniteShading.cpp:2711` `AllocateFixedFunctionBins` 把 4015 bin 合并到 340 bin（City Sample），空调度减少 80%
2. **VSM 跟 Lumen/Nanite Page Table 完全同源**——128x128 page + sub-alloc + LRU evict + cross-frame feedback
3. **MCP server 端点实现在 Epic 闭源代码**——day-job 不能假装看到了 30+ 端点实现细节，但**通过 `FAutomationCommand` 框架** + 公开 Anthropic spec 可以完整还原架构
4. **Trust 4 件套是 day-job Harness 安全基线**——启动前 manifest + 启动后 periodic + 变更 confirm + manifest 持久化

---

## 待办 / 后续

- [ ] **W31 候选**：LumenScreenProbeGather 微观 / LumenRadiosity 微观 / Substrate 微观 / LumenCardRepresentation 跨模块集成
- [ ] **MCP server 端点 实际跑通**：day-job harness 跑 1-2 个 mock 端点（spawn_actor / compile_blueprint）验证流程
- [ ] **VSM Directional Light 8-16 层 clipmap 微观**：W30 写的高层，详细每层 page 分配
- [ ] **Nanite 5.4+ Tessellation 路径**：W30 提到但没展开
- [ ] **Mac Metal RHI 上 VSM 5.4+ 实际跑通测试**：W28 提的 Mac Game Harness 关键
- [ ] **同步进 day-job RAG 索引**——chunked-MD 格式先做 W30 这 3 篇

---

## 关联

- [[../../00-README|02-引擎源码分析库 根 README]] — 全库索引
- [[../W29/00-README|W29 README]] — 上周,4 主题（Lumen 微观 + 3 论文笔记）
- [[../W28/00-README|W28 README]] — 上上周,4 个 UE5.8 重头戏
- [[../W26/UE5-Nanite-虚拟几何shader]] — W30 Nanite 的"高层"
- [[../W26/UE5-ModelContextProtocol-调用链路]] — W30 MCP 的"高层"
- [[../../../05-技术雷达/00-README|技术雷达]] — P0 雷达（待补 Lumen/Nanite/VSM 渲染三特性）

---

*W30 mini-README 模板:延续 W28 模板,3 主题 = 3 源码分析 (Nanite / VSM / MCP) = 兑现"dive deeper into 3 features"*
