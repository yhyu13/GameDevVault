---
tags: [source/周归档, source/W31, source/UE5.8, source/Substrate, source/Lumen, source/VSM, source/Nanite, source/PageTable, source/day-job]
aliases: [W31 Mini-Index, W31 跨特性联动]
---

# W31 (2026-07-27 ~ 2026-08-02) — 渲染三特性跨模块宏观联动 + day-job RAG 抽象

> 本周 **1 个新方向**:Substrate(材质) + Lumen(GI) + VSM(阴影)的**跨特性宏观联动**,从"分页范式同源"角度抽出 day-job RAG 可复用的统一抽象。
> **不是微观**——按用户约定走宏观档:3 篇 11-14KB MD + 1 个总览 HTML 卡牌(32 题跨 3 主题)+ 本 README。

---

## 产出清单

| 主题 | MD | 卡牌 | 大小 | 核心要点 |
|------|:--:|:--:|-----|----------|
| **Substrate 材质闭环** | ✅ | 共享 | 12.7 KB | 12 核心 CVar 全表 + FSubstrateSceneData 7 个 RDG texture + 4 stencil bit 三路径分流 + Lumen 探针接口 (`GetSubstrateMaxClosureCount`) |
| **Lumen GI 全景** | ✅ | 共享 | 11.5 KB | ScreenProbe + Radiosity + SurfaceCache 三子系统 + 12 CVar(6+4+5+5 拆分) + DiffuseIndirect[ClosureCount] 产出 + Radiosity 反向更新 SurfaceCache |
| **VSM/Lumen/Nanite Page Table 同源** | ✅ | 共享 | 13.5 KB | 128x128 物理页 + 8x8 sub-alloc bitfield 范式 + LRU 跨帧 feedback + 3 class 不共享的结构同源 + `static_assert(MinResLevel=3, PhysicalPageSize=128)` |
| **总览卡牌(跨 3 主题)** | — | ✅ | 36.9 KB · 32 题 | TF / MC / DRAG 三题型跨 3 chapter + chapter 颜色分隔(粉/青/绿) + overview 总览面板 + 错题回顾 |

**总计**:5 个新文件(3 MD + 1 总览 HTML 卡牌 + 本 README),~110 KB 知识增量

---

## 文件清单

### 源码分析(与论文笔记按 v1.3 紧贴 MD 约定)
- `Routine/02-引擎源码分析库/Unreal-Engine/W31/UE5-Substrate-材质闭环-源码分析.md` · 12.7 KB
- `Routine/02-引擎源码分析库/Unreal-Engine/W31/UE5-Lumen-GI-全景-源码分析.md` · 11.5 KB
- `Routine/02-引擎源码分析库/Unreal-Engine/W31/UE5-VSM-Lumen-Nanite-PageTable-同源-源码分析.md` · 13.5 KB
- `Routine/02-引擎源码分析库/Unreal-Engine/W31/UE5-Substrate-Lumen-VSM-跨特性联动-总览卡牌.html` · 36.9 KB · 32 题

---

## W31 跟既有笔记的关系

### Substrate 4 件套("理论 + 升级 + 高层 + 微观")
| 层级 | 笔记 | 视角 |
|------|------|------|
| 理论 | (W27) Epic-2024-Substrate-GDC 演讲笔记 | GDC 演讲 + 工程价值 |
| 5.4 升级 | [[../W28/UE5-Substrate-5.4-升级特性]] | 5.4 新增 / 性能数据 |
| **跨特性 (W31)** | [[UE5-Substrate-材质闭环-源码分析]] | 12 CVar + 4 RDG texture + Lumen 接口 |

### Lumen 4 件套("论文 + 高层 + 微观 + 跨特性")
| 层级 | 笔记 | 视角 |
|------|------|------|
| 论文 | [[../../01-论文笔记库/Lumen/SIGGRAPH2021_Lumen_20230220002724]] | SIGGRAPH 2021 论文 |
| 高层 | [[../W26/UE5-Lumen-全景入口]] | Lumen 主入口 4 阶段 |
| 微观 (W29) | [[UE5-Lumen-SurfaceCache-MeshCard-源码分析]] | 4 层 Atlas + 21 CVar |
| **跨特性 (W31)** | [[UE5-Lumen-GI-全景-源码分析]] | 三子系统入口 + 数据流 |

### VSM 4 件套("理论 + 性能 + 微观 + 跨特性")
| 层级 | 笔记 | 视角 |
|------|------|------|
| 论文 | [[../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] | SIGGRAPH 2020 course |
| 性能 | [[../../04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影质量瑕疵]] | VSM 实战 profile |
| 微观 (W30) | [[UE5-VSM-Page-Table-源码分析]] | 30+ CVar + BuildPageAllocations |
| **跨特性 (W31)** | [[UE5-VSM-Lumen-Nanite-PageTable-同源-源码分析]] | 128x128 + 8x8 sub-alloc 同源范式 |

### 总览卡牌(W31)
- 32 题跨 3 chapter:Ch1 Substrate(11 题) + Ch2 Lumen(10 题) + Ch3 Page Table(11 题)
- 题型分布:TF 5 / MC 25 / DRAG 2
- 配套 3 篇 MD,任一篇读完后用卡牌自测

---

## 跟 day-job 的对接

day-job = **RAG + Mac Game Harness,目标"提到 LLM 对 UE 特性的使用"**。W31 3 主题对应的 LLM 训练价值:

| 内容 | 适合喂给 LLM 的形式 | day-job 落地 |
|------|---------------------|----------------|
| Substrate 12 CVar + 4 RDG texture | "材质复杂度 → Lumen slice 数" 公式 | RAG chunk: LLM 评估"Substrate 改 → Lumen 怎么变" |
| Lumen 三子系统数据流 | "Radiosity 反向更新 SurfaceCache" + "ScreenProbe 产 DiffuseIndirect" | RAG chunk: LLM 答"GI 怎么算多 bounce" |
| Page Table 同源 128x128 + 8x8 | "VSM / Lumen / Nanite 共享分页范式" | **统一 index entry**——LLM 看到 3 个特性共享上下文,不分别查 3 个 chunk |
| Substrate closure count ≤ 8u | "材质层数硬上限 8" | validator: "材质 layer >8 → reject" |
| Lumen 显存估算公式 | "1080p × 8 closure × 16B ≈ 67MB" | tool desc: "估算 Lumen 显存" |

**跟 W30 的区别**:
- W30 是**微观**——具体 CVar / 调用链 / 诊断 Checklist
- W31 是**宏观**——跨特性抽象 / 数据流 / day-job RAG 价值
- **RAG 价值**:W30 喂 LLM 具体调参,W31 喂 LLM"特性间如何联动"。两个层都覆盖,RAG 才完整。

---

## 关键技术发现

1. **Substrate 直接决定 Lumen 探针 slice 数**——`Substrate::GetSubstrateMaxClosureCount(View)` 在 LumenScreenProbeGather.cpp:2672 调用,材质复杂度反过来驱动 GI 内存成本。`SUBSTRATE_MAX_CLOSURE_COUNT ≤ 8u` 是全局硬上限,8 closure + 1080p + PF_FloatRGBA ≈ 67MB Lumen 显存。
2. **Lumen Radiosity 不是独立输出,反向更新 SurfaceCache**——这是 W31 主题 2 的核心数据流发现。Radiosity 算 multi-bounce,产出重新写入 SurfaceCache 的 Irradiance 层,给下一帧 ScreenProbe 喂更好数据。
3. **VSM / Lumen SurfaceCache / Nanite 物理页都是 128x128,sub-alloc 都是 8x8**——`FPageBinAllocation` (Lumen) / `FPageTableUpdate` (VSM) / `FClusterPage` (Nanite) 是三个 class 但**结构同源**。`static_assert(Lumen::MinResLevel == 3)` + `static_assert(Lumen::PhysicalPageSize == 128)` 是 Lumen 内部硬约束,跟 VSM / Nanite 不共享(类级别)但同值(常量级别)。
4. **8x8 sub-alloc 范式胜在多维度**——CUDA warp (64 elem = 1 warp) + bitfield 紧凑 (uint64) + mip 0/1/2/3 自然金字塔 + Substrate tile classification 同样 8x8 粒度。**整个 UE5 渲染栈都用 8x8**。
5. **Substrate AllocationMode 1 是生产档最优**——"只能增长不回收"避免 view 切换 hitch,但代价是长时间游戏"内存只增不减"。

---

## 待办 / 后续

- [ ] **W32 候选**(选一):
  - LumenCardRepresentation 跨模块集成(W29 SurfaceCache 微观 + W31 主题 3 同源 + W31 CardRepresentation)→ 4 模块交叉
  - MegaLights / Lumen Hardware Ray Tracing / Lumen Scene Lightning 三个新兴子系统的微观
  - Mac Metal RHI 在 Substrate/Lumen/VSM 三特性上的兼容性专题(补 day-job 缺位)
- [ ] **day-job RAG 索引化 W31 3 主题**——chunked-MD 格式,每篇按 6 主题块切(为什么看 / 模块交互图 / 关键类 / CVar / 调用链 / day-job)
- [ ] **W31 总览卡牌 32 题 → 多选题化**——目前 MC 多,TF/DRAG 偏少,如果需要可以加 5-10 题提升题库质量
- [ ] **W30 MCP 笔记里 "MCP server 端点 实际跑通" 待办**——上周末完成的待办,本周末没动
- [ ] **P0 雷达补 Lumen/Nanite/VSM**——Mavis 7.5 提的待办,W30/W31 两周都聚焦了源码,雷达还停在 7.5 之前的"工具链轴"版本
- [ ] **W31 笔记复现状态 v0.1 修正**——已识别 3 处叙事偏差需在 day-job RAG 索引化前修正:
  1. 主题 2:"Radiosity 反向更新 SurfaceCache" → 应为"Radiosity 更新 RadianceCache,ScreenProbe 间接受益"
  2. 主题 3:"三特性 8x8 完全共享" → 应为"128x128 物理页共享,8x8 是 Lumen 独有 sub-alloc 粒度"
  3. 主题 3:"FPageBinAllocation 复用" → 应为"范式同源但 struct 各特性独立"
- [ ] **W32 之前补 1:1 行号验证**——核心 3 处偏差涉及的具体行号(LumenScreenProbeGather.cpp:2660-2683 / VirtualShadowMapArray.cpp:3227 / LumenSceneData.h:693-740)在公开 UE 5.4 fork (NVIDIA-RTX 等) 可对,行号会漂移但类/函数名应可对得上

---

## 关联

- [[Routine/02-源码分析库/00-README|02-引擎源码分析库 根 README]] — 全库索引
- [[Routine/02-源码分析库/Unreal-Engine/W30/00-README|W30 README]] — 上周,微观档(11/11/11 CVar)
- [[Routine/02-源码分析库/Unreal-Engine/W29/00-README|W29 README]] — 上上周,4 主题(Lumen 微观 + 3 论文笔记)
- [[Routine/02-源码分析库/Unreal-Engine/W28/00-README|W28 README]] — 上上上周,4 个 UE5.8 重头戏
- [[../W27/00-README|W27 README]] — UE5.7 vs 5.8 + 缺漏使用指南 + GDC 笔记
- [[../W26/00-README|W26 README]] — UE 5.4+ 渲染架构(Nanite / Lumen / MCP 高层)
- [[../../../05-技术雷达/00-README|技术雷达]] — P0 雷达(待补 Lumen/Nanite/VSM 渲染三特性)

---

*W31 mini-README 模板:延续 W30 模板,3 主题 = 3 跨特性宏观 = 兑现 "Substrate + Lumen + VSM 跨特性联动"*
*W31 跟 W30 形成"宏观 + 微观"配对:W30 微观档 + W31 宏观档 = 双层覆盖,跟 day-job RAG 训练价值匹配*
