---
tags: [routine/AI-tasks, topic/PCG, day/Monday]
aliases: []
---

# 周一：AI 任务清单 — PCG 前沿技术输入

> **人类目标**：理解 PCG 框架架构，精读 UE5.8 源码实现，掌握节点化数据流管线。  
> **AI 任务**：提供脚手架、解释架构、生成问题，绝不替读文档。

---

## 任务 1：PCG 技术预读引导（AI 执行）

**输入**：UE5.8 PCG 官方文档 + PCG `.uplugin` 描述 + PCG 白皮书

**AI 输出**：
1. 一段 **150 字摘要**：PCG 是 UE5.8 内置的节点化程序化生成框架，通过 Graph 节点链操作 Point 数据（位置+属性），实现从表面采样到实例生成的完整管线。核心模块 PCG 负责图执行，PCGGeometryScriptInterop 桥接程序化网格，PCGExternalDataInterop 导入外部点云。其确定性执行模型保证同一输入产生相同输出，适用于植被散布、城市布局、运行时大世界生成。
2. **3 个引导问题**：
   - Q1: PCG Graph 的执行模型是 Eager 还是 Lazy？Node 如何缓存中间结果以避免重复计算？
   - Q2: Point 的 Attribute 系统支持哪些数据类型？Attribute 如何在 Graph 节点之间传递和变换？
   - Q3: PCG 的 Deterministic Generation 如何保证跨平台一致性？与 Seed 和随机数生成器的关系是什么？
3. **重点章节标记**：先读 PCG Overview（Graph 概念、Point、Attribute），再读 Node Reference（Sampler/Filter/Transform/Spawn），最后读 Execution Pipeline（执行顺序、缓存、多线程）

**交付物**：`PCG-Reading-Guide.md`

---

## 任务 2：PCG Graph 管线解释（AI 执行，你验证）

**输入**：UE5.8 PCG 文档中的 Graph Execution 章节

**AI 输出**：
1. **Graph 执行流程**：Input → Sampler Node（生成初始 Point 云）→ Filter Node（按条件筛选）→ Transform Node（变换/修改属性）→ Spawn Node（输出到 World：ISM、Actor、Decal）
2. **Node 内部结构**：Settings（用户参数）→ Execute 函数（接收 Input Point Data → 处理 → 输出 Point Data/Context）→ 输出 Pin 连接下一个 Node
3. **数据流类型**：
   - **Point Data**：位置、旋转、缩放 + Attribute 字典
   - **Spline Data**：曲线数据（用于道路、河流）
   - **Surface Data**：表面/体积数据（用于采样约束）
   - **Spatial Data**：空间查询结构（Octree、Grid）

**你必须做**：在 UE58 编辑器中创建一个简单 PCG Graph，添加 `Surface Sampler` → `Density Filter` → `Transform Points` → `Static Mesh Spawner`，观察每个节点的输出。

**实验步骤**：
```
1. 创建 PCG Graph 资产（右键 → Procedural Content → PCG Graph）
2. 添加 Surface Sampler，选择 Landscape 作为输入表面
3. 添加 Density Filter，设置 Min/Max Density 阈值
4. 添加 Transform Points，随机旋转和缩放
5. 添加 Static Mesh Spawner，选择一颗树模型
6. 在 PCG Volume 中应用 Graph，观察视口中的生成结果
```

---

## 任务 3：面试谈资生成（AI 执行，你 rehearse）

**AI 输出**：
1. **30 秒版本**：PCG 是 UE5.8 的程序化内容生成框架，通过节点图操作 Point 数据，实现从采样到实例生成的自动化管线。我在学习它的 Graph 执行模型、Attribute 系统和与 Nanite/MassAI 的集成。
2. **2 分钟版本**：
   - 背景（传统手摆关卡 vs 程序化生成）
   - PCG 核心（Graph 节点 + Point 数据 + Attribute 系统）
   - 执行管线（Sampler → Filter → Transform → Spawn）
   - 使用场景（植被散布、城市布局、运行时大世界）
   - 与其他系统关系（Nanite 渲染实例、MassAI 接收 Spawn Point、MCP AI 调用）
   - 局限（性能开销、调试复杂度、艺术家可控性）
3. **3 个追问**：
   - "PCG 与 Houdini Engine 有什么区别？什么时候选 PCG 内置方案？"
   - "PCG 的 Graph 执行是单线程还是多线程？如何优化大规模点云的生成性能？"
   - "PCG 的 Deterministic Generation 在运行时如何与动态加载（World Partition）配合？"

**你必须做**：rehearse aloud。

---

## 任务 4：PCG 源码地图（AI 执行，你验证）

**输入**："PCG 的 3 个模块职责是什么？从 Graph 执行入口到 Node 调用的完整调用链？"

**AI 输出**：
1. **PCG** (Runtime + Editor) — 核心框架：
   - `FPCGGraph` — Graph 数据结构（节点数组、边数组）
   - `FPCGNode` — 节点基类（Settings、Input/Output Pins）
   - `UPCGComponent` — 运行时组件（执行 Graph、管理 Volume）
   - `FPCGContext` — 执行上下文（缓存、依赖、参数）
   - `FPCGPoint` — Point 数据结构（Transform + Attribute Set）
   - `FPCGMetadata` — Attribute 系统（键值对存储）
2. **PCGGeometryScriptInterop** — Geometry Script 桥接：
   - 将 PCG Point 数据转为程序化网格（Dynamic Mesh）
   - 支持 Mesh Boolean、Voxel Merge 等操作
3. **PCGExternalDataInterop** — 外部数据：
   - Houdini Engine 数据导入
   - 点云（Point Cloud）数据读取
   - 地形高度图采样

**调用链**：
```
UPCGComponent::ExecuteGraph()
  → FPCGGraphExecutor::Execute()
  → 拓扑排序确定 Node 执行顺序
  → FPCGNode::ExecuteNode(FPCGContext)
  → 具体 Node 实现（如 FPCGSurfaceSampler::Execute）
  → 生成 FPCGPointData（Point 数组 + Attribute）
  → 输出到下一个 Node 的 Input Pin
  → 最终 Node（如 FPCGStaticMeshSpawner）
  → 调用 UHierarchicalInstancedStaticMeshComponent::AddInstance()
  → 或 SpawnActor()
```

**你必须做**：在 UE58 源码中打开这些模块，找到 `ExecuteGraph`、`ExecuteNode`、`FPCGPoint`、`FPCGMetadata` 等关键类型和函数。

---

## 今日 AI 禁区

- ❌ 让 AI 替你读 PCG 文档而不自己看 Node 参数和 Pin 类型
- ❌ 让 AI 替写笔记（PCG 是数据流系统，必须自己理解每个 Node 的输入输出）
- ❌ 让 AI 生成代码路径而不验证（UE 源码可能已更新，Node 类名可能变化）
- ❌ 让 AI 替你准备面试回答而不理解 Graph 执行本质

---

## 完成检查清单

- [ ] PCG 阅读指南已生成并打印
- [ ] 已手动在 UE 编辑器中搭建简单 PCG Graph（Sampler → Filter → Spawn）
- [ ] 面试谈资已 rehearse aloud
- [ ] PCG 源码路径已验证（找到 ExecuteGraph/ExecuteNode/FPCGPoint/FPCGMetadata）
- [ ] 所有内容已写入 Obsidian 笔记（你写的，不是 AI 写的）

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2 小时*  
*产出：1 篇架构笔记 + 1 篇源码分析 + 面试谈资 ready*
