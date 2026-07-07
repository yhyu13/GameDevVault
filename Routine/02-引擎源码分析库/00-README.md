# 🔧 引擎源码与架构分析库

> **对应周计划：周一晚 — 源码分析（输入）**

---

## 分析策略

**带着问题看源码**，不要通读。推荐的问题模板：

- "UE5 的虚拟纹理系统具体是如何调度显存的？"
- "RenderThread 和 GameThread 的交互机制是什么？"
- "Unity 的 ECS 架构如何做到 Cache Friendly？"
- "Godot 的渲染器抽象层设计有什么特点？"

---

## 文件夹结构

- **[[Unreal-Engine]]** — UE4/UE5 源码分析,按 ISO 周归档为 `W##/` 子目录(以**开始**那一周为准)
  - **[[Unreal-Engine/W26|W26]]** (2026-06-22 ~ 06-28)— 11 个文件,Lumen / Nanite / MCP / NNE / Mass / VT
  - **[[Unreal-Engine/W27|W27]]** (2026-06-29 ~ 07-05)— 10 个文件,Cook 流水线 + MCP 改进 + UE5.8 天空系(SkyAtmosphere / VolumetricCloud / SkyPass)
  - **[[Unreal-Engine/W28|W28]]** (2026-07-06 ~ 07-12)— 8 个文件,UE5.8 重头戏(MegaLights / Substrate / InstanceCulling / HeterogeneousVolumes)
- **[[Unity]]** — Unity DOTS/ECS/Render Pipeline
- **[[Godot]]** — Godot 开源引擎学习
- **通用架构** — 跨引擎设计模式（如 Job System、内存池、资源热更）

---

## 记录格式标准

每篇源码分析必须包含：

1. **问题定义** — 为什么看这段代码？
2. **模块图** — 涉及哪些线程/模块的交互
3. **关键类继承关系** — 用文字或 Mermaid 图表示
4. **内存布局分析** — 关键结构体的字段对齐
5. **代码路径** — 从入口到核心逻辑的调用链
6. **个人评价** — 设计优劣、可改进点

---

## 标签体系

| 标签 | 含义 |
|------|------|
| `#source/UE` | Unreal Engine 相关 |
| `#source/Unity` | Unity 相关 |
| `#source/Godot` | Godot 相关 |
| `#source/RenderThread` | 渲染线程相关 |
| `#source/GameThread` | 游戏线程相关 |
| `#source/Memory` | 内存管理 |
| `#source/JobSystem` | 多线程/任务系统 |
| `#source/Resource` | 资源加载/热更 |
| `#source/深度完成` | 已完整分析并输出笔记 |
| `#source/浅度浏览` | 仅了解大概，待深入 |

---

## 关联知识库

- [[01-论文笔记库]] — 论文中的理论如何在引擎中落地
- [[04-性能优化备忘录]] — 源码中发现的性能陷阱
- [[99-Templates/源码分析]] — 新建分析笔记模板

---

## 当前分析目标

按 ISO 周归档,每行 = MD + 卡牌 HTML(若有)。

### W26 (2026-06-22 ~ 06-28) — UE5 经典三大件 + 周边工具

| 目标 | 引擎 | 状态 | 笔记 | 卡牌 |
|------|------|------|------|------|
| 虚拟纹理系统 | UE5 | ✅ | [[Unreal-Engine/W26/UE5-VT-显存调度]] | [卡牌](./Unreal-Engine/W26/UE5-VT-显存调度.html) |
| Lumen 调用链 | UE5 | ✅ | [[Unreal-Engine/W26/UE5-Lumen-源码调用链]] | [[../../../Career/Kimi/html/lumen/callchain]] |
| Nanite 虚拟几何管线 | UE5 (5.3) | ✅ | [[Unreal-Engine/W26/UE5-Nanite-虚拟几何管线]] | [[../../../Career/Kimi/html/nanite/callchain]] · [精简版](./Unreal-Engine/W27/Nanite-Card-Pack.html) |
| ModelContextProtocol 完整调用链路 | UE5 | ✅ | [[Unreal-Engine/W26/UE5-ModelContextProtocol-完整调用链路]] | [卡牌](./Unreal-Engine/W26/UE5-ModelContextProtocol-完整调用链路.html) |
| NNE 神经网络引擎（UE 5.8 实测） | UE5.8 | ✅ | [[Unreal-Engine/W26/UE5-NNE-神经网络引擎]] | [卡牌](./Unreal-Engine/W26/UE5-NNE-神经网络引擎.html) |
| Mass 数据导向 AI（UE 5.8 实测） | UE5.8 | ✅ | [[Unreal-Engine/W26/UE5-Mass-AI-数据导向框架]] | [卡牌](./Unreal-Engine/W26/UE5-Mass-AI-数据导向框架.html) |

### W27 (2026-06-29 ~ 07-05) — Cook 流水线 + UE5.8 天空系

| 目标 | 引擎 | 状态 | 笔记 | 卡牌 |
|------|------|------|------|------|
| Cook 流水线（Shader + 纹理 + 速度 + 配置 + 并行度） | UE5.3/5.4/5.5 | ✅ | [[Unreal-Engine/W27/UE5-Cook-流水线源码分析]] | [卡牌](./Unreal-Engine/W27/UE5-Cook-流水线源码分析.html) |
| MCP 缺点改进与使用指南 | UE5 | ✅ | [[Unreal-Engine/W27/UE5-ModelContextProtocol-缺点改进与使用指南]] | — |
| SkyAtmosphere 大气散射（5 LUT + Bruneton + State Versioning） | UE5.8 | ✅ | [[Unreal-Engine/W27/UE5.8-SkyAtmosphere-大气散射]] | [卡牌](./Unreal-Engine/W27/UE5.8-SkyAtmosphere-大气散射.html) |
| VolumetricCloud 体积云（3 GPU 路径 + 8 permutation + Reproject + AP） | UE5.8 | ✅ | [[Unreal-Engine/W27/UE5.8-VolumetricCloud-体积云]] | [卡牌](./Unreal-Engine/W27/UE5.8-VolumetricCloud-体积云.html) |
| SkyPass 天空 Pass（Mesh Pass 兜底 + IsSky flag + Mobile） | UE5.8 | ✅ | [[Unreal-Engine/W27/UE5.8-SkyPass-天空-pass]] | [卡牌](./Unreal-Engine/W27/UE5.8-SkyPass-天空-pass.html) |

### W28 (2026-07-06 ~ 07-12) — UE5.8 重头戏

| 目标 | 引擎 | 状态 | 笔记 | 卡牌 |
|------|------|------|------|------|
| MegaLights 随机光照（7 步 pipeline + 13 TileType + HWRT/VSM 双模式 + History guide） | UE5.8 | ✅ | [[Unreal-Engine/W28/UE5.8-MegaLights-随机光照]] | [卡牌](./Unreal-Engine/W28/UE5.8-MegaLights-随机光照.html) |
| Substrate 材质系统（4 TileType + Stencil 分类 + DBuffer/RoughRefraction + Tile-based Closure） | UE5.8 | ✅ | [[Unreal-Engine/W28/UE5.8-Substrate-材质系统]] | [卡牌](./Unreal-Engine/W28/UE5.8-Substrate-材质系统.html) |
| InstanceCulling GPU 裁剪（LoadBalancer 位打包 + Bin 多 HZB + DeferredContext 批处理） | UE5.8 | ✅ | [[Unreal-Engine/W28/UE5.8-InstanceCulling-GPU裁剪]] | [卡牌](./Unreal-Engine/W28/UE5.8-InstanceCulling-GPU裁剪.html) |
| HeterogeneousVolumes 体素体积（7 Pipeline + SparseVoxel + VoxelGrid + LiveShading + HWRT） | UE5.8 | ✅ | [[Unreal-Engine/W28/UE5.8-HeterogeneousVolumes-体素体积]] | [卡牌](./Unreal-Engine/W28/UE5.8-HeterogeneousVolumes-体素体积.html) |

### Godot

| 目标 | 引擎 | 状态 | 笔记 | 卡牌 |
|------|------|------|------|------|
| Jolt Physics 模块（AI 集成点） | Godot 4.8-dev | ✅ | [[Godot/Godot-Jolt-Physics-AI集成点源码分析]] | — |

### 待开始

| 目标 | 引擎 | 状态 |
|------|------|------|
| ECS Job System | Unity | 待开始 |
| Godot 渲染器抽象层（RenderingServer / RendererCompositor） | Godot | 待开始 |
