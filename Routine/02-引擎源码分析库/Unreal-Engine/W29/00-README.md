---
tags: [source/周归档, source/W29, source/UE5.8, source/Lumen, source/Nanite, source/VSM, source/MCP]
aliases: [W29 Mini-Index, W29 渲染三特性 + day-job 协议]
---

# W29 (2026-07-13 ~ 2026-07-19) — 渲染三特性 + day-job 协议

> 本周 **4 个新主题**：① Lumen Surface Cache 源码深挖（微观） ② Nanite 论文笔记 ③ VSM 论文笔记 ④ Unreal MCP / Copilot 集成论文笔记。
> 是 W28 README 提到"下个周期补 Nanite / VSM / Mac"的兑现，也是 day-job RAG 索引的高质量语料。

---

## 产出清单

| 主题 | MD | 卡牌 | 大小 | 核心要点 |
|------|:--:|:--:|-----|----------|
| **Lumen Surface Cache + Mesh Card 源码分析** | ✅ | — | 57 KB | 4 层 Atlas (Albedo/BC7 + Normal/BC5 + Depth/G16 + Emissive/BC6H) + 128x128 Page + 8x8 Sub-alloc + 6 方向 OBB Card + 9 级 Mip + 21 个 CVar → 源码函数映射 + 4 类闪烁诊断 |
| **Nanite 论文笔记 (Karis 2021)** | ✅ | ✅ | 12 KB + 32 KB 卡牌 | 128-tri Cluster + GPU-Driven Culling + Visibility Buffer + 5.4 材质 Bin 调度 + 5 大模块 + 12 题 QA |
| **VSM 论文笔记 (Karis 2020)** | ✅ | ✅ | 13 KB + 28 KB 卡牌 | 128x128 Page Table + Mip 链 + Directional Clipmap + Contact Shadow + MegaLights 5.4+ 集成 + 10 题 QA |
| **Unreal MCP / Copilot 集成** | ✅ | ✅ | 15 KB + 31 KB 卡牌 | MCP 协议 3 类端点 + UE 5.7+ 内置 server + 双重信任验证 + Agent 模式 + day-job Harness 4 件套 + 12 题 QA |

**总计**：8 个新文件（4 MD + 3 HTML 卡牌 + 本 README），~190 KB 知识增量

## 文件清单

### 源码分析
- [[UE5-Lumen-SurfaceCache-MeshCard-源码分析]] · 57 KB

### 论文笔记 + 卡牌（v1.3 紧贴 MD 约定）
- `Routine/01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry.md` · 12 KB
- `Routine/01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry.html` · 32 KB · 12 题
- `Routine/01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps.md` · 13 KB
- `Routine/01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps.html` · 28 KB · 10 题
- `Routine/01-论文笔记库/UnrealMCP/Epic-2025-Unreal-MCP-Copilot-Integration.md` · 15 KB
- `Routine/01-论文笔记库/UnrealMCP/Epic-2025-Unreal-MCP-Copilot-Integration.html` · 31 KB · 12 题

---

## 4 主题与 W28 / Lumen 三角闭环的关系

| 主题 | 层级 | 跟既有笔记的关系 |
|------|------|-----------------|
| **Lumen Surface Cache** | 源码（微观） | W26 高层 call chain 的"下钻" |
| **Nanite 论文** | 理论（一手 PDF） | 跟 W26 既有 `UE5-Nanite-虚拟几何shader.md` 形成"理论 + 源码"配对 |
| **VSM 论文** | 理论（一手 PDF） | 跟 W29 Lumen Surface Cache + 既有 `VSM-页溢出` 性能笔记形成"理论 + 操作 + 源码"三层 |
| **MCP / Copilot** | 协议理论 + day-job 落地 | 跟 W26 `UE5-ModelContextProtocol-调用链路` + W27 `缺失的捡漏使用指南` + GDC 2026 `VS2026 Copilot` 三件套 + day-job `UE5_Training_MCP/` 项目配套 |

### Lumen 三件套（W29 闭环）

| 层级 | 笔记 | 视角 |
|------|------|------|
| 理论 | [[../../01-论文笔记库/Lumen/Lumen-SIGGRAPH-2021]] | SIGGRAPH 论文 |
| 操作 | [[../../01-论文笔记库/Lumen/Lumen-实战手册：调试-Profile-定制-跨场景适配指南]] | 10 大段 + 速查 |
| 源码（宏观） | [[../W26/UE5-Lumen-源码调用链]] | 4 Pass 入口 |
| **源码（微观）** | [[UE5-Lumen-SurfaceCache-MeshCard-源码分析]] (本文) | Surface Cache 21 CVar |

### Nanite 双件套（新增）

| 层级 | 笔记 | 视角 |
|------|------|------|
| **理论（新增）** | [[../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry]] | SIGGRAPH 2021 论文 + Journey to Nanite |
| 源码 | [[../W26/UE5-Nanite-虚拟几何shader]] | W26 写的源码分析 |
| 卡牌 | [[../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry]] (HTML) | 12 题面试自测 |
| 性能 | [[../../04-性能优化备忘录/知识参考/Nanite 性能调优]] | 知识参考 + 实战 profile |

### VSM 双件套（新增）

| 层级 | 笔记 | 视角 |
|------|------|------|
| **理论（新增）** | [[../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] | SIGGRAPH 2020 course + UE 官方文档 |
| 性能瓶颈 | [[../../04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影质量瑕疵]] | VSM 实战 profile |
| 卡牌 | [[../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps]] (HTML) | 10 题面试自测 |
| 集成 | [[../W28/UE5.8-MegaLights-随机光照]] | 5.4+ 跟 MegaLights 集成 |

### MCP / Copilot 四件套（新增 + 既有）

| 层级 | 笔记 | 视角 |
|------|------|------|
| **理论（新增）** | [[../../01-论文笔记库/UnrealMCP/Epic-2025-Unreal-MCP-Copilot-Integration]] | Anthropic MCP spec + UE 5.7+ + Copilot Agent |
| 源码（既有） | [[../W26/UE5-ModelContextProtocol-调用链路]] | W26 写的 MCP 源码分析 |
| 实战（既有） | [[../W27/UE5-ModelContextProtocol-缺失的捡漏使用指南]] | W27 写的 MCP 捡漏指南 |
| 关联（既有） | [[../../01-论文笔记库/GDC/2026-Microsoft-VS2026-Copilot-GameDev]] | GDC 2026 VS2026 + Copilot |
| 卡牌（新增） | [[../../01-论文笔记库/UnrealMCP/Epic-2025-Unreal-MCP-Copilot-Integration]] (HTML) | 12 题面试自测 |
| 项目 | [[../../../Career/Kimi/UE5_Training_MCP/]] | day-job MCP-grounded 训练 pipeline |

---

## 与 day-job 的对接（RAG 训练价值）

day-job = **RAG + Mac Game Harness,目标"提到 LLM 对 UE 特性的使用"**。W29 4 主题对应的 LLM 训练价值：

| 内容 | 适合喂给 LLM 的形式 | day-job 落地 |
|------|---------------------|----------------|
| Lumen 4 层 Atlas 像素格式 + 21 CVar | "BC5 = 法线专用,BC6H = HDR,BC7 = 高质量" + "r.LumenScene.SurfaceCache.CardCapturesPerFrame 控制每帧 capture 预算" | 工具描述:LLM 选 Lumen 配置 / 调参时直接查 |
| Nanite 5 大模块 + 4.0 → 5.4 演进 | "128-tri Cluster + Visibility Buffer + 材质 Bin 调度 5.4 减少 80% 空调度" | 训练数据:LLM 调 Nanite 时知道"5.4 是分水岭" |
| VSM Page Table 跟 Lumen/Nanite 同源 | "VSM 128x128 page + LRU evict + Contact Shadow + MegaLights 5.4+ 集成" | RAG 检索:LLM 调阴影时知道 VSM / Lumen / Nanite 一致范式 |
| MCP 3 类端点 + Trust 4 件套 | "MCP = client-server 协议 (LLM 无关), tools/resources/prompts + 双重信任验证" | 工具描述:day-job harness 必须按 MCP 暴露所有工具 |

---

## 本周彩蛋

- **Lumen 源码 typo**:`LumenSceneData.h:174` 的 `FLumenCardSharingInfo::bAxisXFlipped:1` —— 用了 `b` 前缀 + `Flipped` 拼写一致,但**位字段是 1 bit 而不是 bool**
- **`LumenSceneData.h:698-699` static_assert** 明确 `MinResLevel == 3` + `PhysicalPageSize == 128` —— Epic 工程严谨度
- **`LumenSurfaceCache.cpp:59-78` BC 格式检查** 隐式表达 BC5/BC6H/BC7 三种都得支持 —— Mac Metal 部分早期版本不支持 BC6H
- **Nanite 5.0 → 5.4 跃迁**:4015 bin → 3675 空 bin 浪费 90% → 5.4 减少 80% 空调度
- **VSM 5.4+ MegaLights 集成** 阈值:n lights >= 8 走 VSM
- **MCP 双重信任验证** 是 VS 2026 2026-06 加入 —— 比 Anthropic 官方 spec 提前 6 个月

---

## 待办 / 后续

- [ ] **W30 候选**（按 P0 雷达顺序）:MegaLights 论文笔记 / Substrate 论文笔记 / HeterogeneousVolumes 论文笔记
- [ ] **LumenScreenProbeGather 单独拆** — 跟 W29 Lumen Surface Cache 配对的另一个微观深挖
- [ ] **LumenRadiosity 单独拆** — 多次迭代 Gather/Scatter 算法核心
- [ ] **LumenHardwareRayTracing 在 Lumen 全栈里的边界** — HWRT 跟 SWRT 分流
- [ ] **Mac 平台缺位** — Lumen / Nanite / VSM 在 Mac Metal RHI 的实际跑通路径
- [ ] **Lumen 5.6+ 是否有大重构** — Diffuse Color Boost 那一批 cvar 是 5.4 引入还是 5.6
- [ ] **同步进 day-job RAG 索引** — chunked-MD 格式,W29 这 4 篇先试喂 1-2 篇
- [ ] **W26 mini-README 补齐** — 模板已成型,本周没补

---

## 关联

- [[../../00-README|02-引擎源码分析库 根 README]] — 全库索引
- [[../W28/00-README|W28 README]] — 上一周,4 个 UE5.8 重头戏
- [[../W26/UE5-Lumen-源码调用链]] — Lumen 高层 call chain
- [[../W26/UE5-Nanite-虚拟几何shader]] — Nanite 既有源码分析
- [[../../01-论文笔记库/Lumen/Lumen-SIGGRAPH-2021]] — Lumen 论文笔记
- [[../../01-论文笔记库/Lumen/Lumen-HowItActuallyWorks-UE5]] — Lumen 实战向笔记
- [[../../01-论文笔记库/GDC/2026-Microsoft-VS2026-Copilot-GameDev]] — VS2026 Copilot GDC 笔记
- [[../../../05-技术雷达/00-README|技术雷达]] — P0 雷达（仍待补 Lumen/Nanite/VSM 渲染三特性到 P0 雷达）

---

*W29 mini-README 模板:延续 W28 模板,4 主题 = 1 源码 + 3 论文 (Nanite / VSM / MCP) = 兑现"下周期补渲染三特性"的承诺*
