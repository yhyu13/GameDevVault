---
tags: [routine/master-index, topic/PCG, system/reference]
aliases: [PCG-AI-Master]
---

# PCG（Procedural Content Generation）主题 — AI 任务总览

> 这是 PCG 学习周期的「AI 任务控制塔」。  
> **核心原则**：AI 只做脚手架，你来做硬工作。

---

## 快速导航

| 日期 | 主题 | AI 任务文件 | 人类核心任务 |
|------|------|------------|-------------|
| [[周一]] | 前沿技术输入 | [[01_Monday/AI-Tasks]] | 精读 PCG 架构 + 源码追踪 |
| [[周二]] | 专项技能突破 | [[02_Tuesday/AI-Tasks]] | 图遍历 + Attribute 数学 + 节点实现 |
| [[周三]] | 强制观察/游玩 | [[03_Wednesday/AI-Tasks]] | 观察游戏 PCG 实例 + UE5 样例 |
| [[周四]] | 工程化与工具链 | [[04_Thursday/AI-Tasks]] | 数据结构 + Python 工具 + 内存布局 |
| [[周五]] | 轻量复盘 | [[05_Friday/AI-Tasks]] | 测验 + 整理 + 规划 |
| [[周末]] | 项目实战 | [[06_Weekend/AI-Tasks]] | 迷你 PCG 图表 + 博客 |
| [[周日]] | 项目收尾 | [[07_Sunday/AI-Tasks]] | 集成测试 + 复盘 |
| [[每周]] | 外部接触 | [[08_Weekly/AI-Tasks]] | PCG 社区社交 + 开源贡献 |

---

## PCG 是什么

**Procedural Content Generation**（程序化内容生成）是 UE5.8 内置的节点化框架，用于在编辑器或运行时通过程序化方式生成关卡内容：

- **PCG 框架**：基于 Graph 的可视化编程系统，节点表示数据操作（采样、过滤、变换、生成），边表示 Point/Attribute 数据流
- **核心模块**：
  - `PCG` — 核心框架（Graph 执行、Point 数据、Attribute 系统、Spatial 查询）
  - `PCGGeometryScriptInterop` — 与 Geometry Script 的桥接（程序化网格生成）
  - `PCGExternalDataInterop` — 外部数据导入（Houdini、地形、点云）
- **关键概念**：
  - **Point**：空间位置 + 属性字典（Transform、Density、Color、自定义属性）
  - **Attribute**：键值对附加在 Point 上，支持 float/int/bool/vector/string
  - **Graph 执行**：确定性执行管线，Input → Node 链 → Output
  - **Node 类型**：Sampler（采样表面/体积）、Filter（条件筛选）、Transform（变换）、Spawn（生成实例/Actors）
- **使用场景**：
  - 程序化生物群系（植被散布、岩石分布）
  - 城市布局（道路、建筑、街景）
  - 地下城生成（房间连接、走廊布局）
  - 运行时内容（大世界动态加载点云）
  - 与 Houdini Engine 协同工作流

---

## 与现有 9 个主题的关系

```
        ┌─────────────────────────────────────┐
        │         PCG (#10)                     │
        │    程序化内容生成 / 关卡自动化          │
        │    (生成器——为多个主题提供内容)        │
        └─────────────────────────────────────┘
                      │
    ┌─────────┬───────┼───────┬─────────┐
    ▼         ▼       ▼       ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Lumen  │ │ Nanite │ │  VGM   │ │  VSM   │ │ Chaos  │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
┌────────────────────┐     ┌────────────────────┐
│   WaterPlugins     │     │    NeuralRendering  │
└────────────────────┘     └────────────────────┘
        │
        ▼
┌────────────────────┐
│    UnrealMCP (#7)  │  ← AI 助手通过 MCP 调用 PCG 工具
└────────────────────┘
        │
        ▼
┌────────────────────┐
│    MassAI (#9)     │  ← PCG 生成 Mass Entity 的 Spawn Point
└────────────────────┘
```

PCG 是 **生成器** 而非 **渲染器**：
- 为 **MassAI** 生成大规模 Entity 的 Spawn Point 和初始分布
- 与 **Nanite** 协同：PCG 生成的 Instanced Static Mesh 实例可由 Nanite 高效渲染
- 被 **UnrealMCP** 增强：AI 助手通过 MCP 调用 PCG 工具，自动分析场景并生成内容
- 为 **VGM**（虚拟几何体）提供程序化数据输入

---

## 相关参考

- [[../References/AI-Augmentation-Reference]] — AI 辅助学习完整参考手册
- [[../UE58-Topic-Exploration-Report]] — UE58 主题探索完整报告（优先级评分）
- [[../MassAI/00-Master-Index]] — MassAI Spawn Point 与 PCG 的关系
- [[../Nanite/00-Master-Index]] — Nanite Instancing 与 PCG 输出
- [[../UnrealMCP/00-Master-Index]] — 通过 MCP 调用 PCG 工具
- [[../../01-论文笔记库]] — PCG 算法论文（Poisson Disk Sampling、WFC、BSP）
- [[../../02-引擎源码分析库]] — PCG 源码分析（Graph Execution、Point Data、Attribute System）
- [[../../99-Templates/论文笔记]] — 论文/规范笔记模板

---

## 每周更新日志

| 周 | 主题 | 状态 |
|----|------|------|
| W1 | PCG 基础：Graph 架构 + Point 数据 + Attribute 系统 + 执行管线 | 🔄 进行中 |
| W2 | PCG 节点深入：Sampler → Filter → Transform → Spawn 全链路 | ☐ 待开始 |
| W3 | 外部集成：Houdini Engine + Geometry Script + 地形数据 | ☐ 待开始 |
| W4 | 运行时生成：大世界动态加载 + 性能优化 + MassAI 集成 | ☐ 待开始 |

---

## 推荐学习路径

**如果你同时学多个主题**：
- **并行**：PCG 作为 "内容生成器"，与渲染主题（Lumen/Nanite）互补。学习 PCG 时生成的内容可以直接用 Lumen 光照、Nanite 渲染
- **串行**：先完成一个渲染主题（如 Lumen），然后用 PCG 为其生成测试场景（程序化植被、地形细节）

**PCG 的特殊性**：
- 需要一定的 **3D 空间直觉**（Point 分布、Density 场、采样策略）
- 需要 **图遍历思维**（Graph 节点执行顺序、数据依赖、惰性求值）
- 不像纯渲染需要大量数学推导，更像 "数据流编程 + 空间算法"
- 学习曲线：中等（概念密集但数学门槛低，比 Chaos 容易，比 Lumen 更工具化）

---

*This is a living document. Update it as the PCG topic progresses.*
