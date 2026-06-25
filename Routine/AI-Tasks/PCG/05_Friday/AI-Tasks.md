---
tags: [routine/AI-tasks, topic/PCG, day/Friday]
aliases: []
---

# 周五：AI 任务清单 — PCG 轻量复盘与整理

> **人类目标**：整理本周 PCG 学习笔记，更新知识库，规划下周。  
> **AI 任务**：生成测验、建议链接、总结数据，绝不替你思考。

---

## 任务 1：PCG 知识测验生成（AI 执行）

**AI 输出**：结构化测验

```markdown
## Q1 (TF)
PCG 的 Graph 执行是 Lazy Evaluation（惰性求值），只有下游节点需要数据时才会执行上游节点。
Answer: False
Explanation: PCG 使用 Eager Evaluation（即时求值）配合缓存。Graph 执行时按拓扑排序顺序逐个执行节点，每个节点的输出被缓存供下游使用。不是惰性求值，而是预计算+缓存模型。

## Q2 (SC)
以下哪个 Node 类型最适合从 Landscape 地形表面生成初始 Point 云？
Options:
- A. Point Filter
- B. Surface Sampler
- C. Transform Points
- D. Static Mesh Spawner
Answer: B
Explanation: Surface Sampler 专门用于从表面（如 Landscape、Static Mesh）采样点，生成初始 Point Data。其他节点分别用于筛选、变换和生成实例。

## Q3 (MC)
以下哪些是 PCG Point 的合法 Attribute 数据类型？
Options:
- A. Float
- B. Integer
- C. FVector
- D. FString
- E. UObject*
Answer: A, B, C, D
Explanation: PCG 的 Attribute 系统支持 float、int32、bool、FVector、FString 等基础类型。不支持 UObject 指针（Attribute 是纯数据，不应包含对象引用）。

## Q4 (FB)
PCG 的 Deterministic Generation 依赖于两个核心要素：______ 和 ______。如果 Seed 相同且 ______ 不变，则输出结果完全相同。
Answer: Seed（种子）, Graph 参数/输入数据（或拓扑结构）, 输入数据/参数
Explanation: PCG 的确定性由固定的随机种子（Seed）和稳定的输入数据（包括 Graph 参数和输入表面/体积）共同保证。任何输入变化都会导致输出变化，但相同输入+相同 Seed 总是产生相同输出。

## Q5 (SC)
在 PCG Graph 中，`Density` Attribute 的主要作用是：
Options:
- A. 控制 Point 的渲染透明度
- B. 作为筛选条件（Filter Node 可按 Density 阈值筛选）和混合权重
- C. 表示 Point 到相机的距离
- D. 控制 Static Mesh 的 LOD 级别
Answer: B
Explanation: Density 是 PCG 的核心概念，用于表示 Point 的"存在强度"。Filter 节点可按 Density 阈值筛选（如只保留 Density > 0.5 的点），多个 Sampler 的叠加也可使用 Density 作为混合权重。
```

**然后**：使用 `quiz-html-generator` 转 HTML（可选）。

**你必须做**：完成测验，复习错题。

---

## 任务 2：笔记链接建议（AI 执行，你确认）

**AI 建议**：
- [[PCG-Graph执行]] → [[Nanite-实例化]]：PCG 生成的 Instanced Static Mesh 可由 Nanite 高效渲染
- [[PCG-Attribute系统]] → [[MassAI-SpawnPoint]]：PCG 输出的 Point 和 Attribute 可直接驱动 Mass Entity 的初始分布
- [[PCG-Deterministic]] → [[Chaos-物理同步]]：确定性生成与物理同步都依赖稳定的 Seed 和输入
- [[PCG-ExternalDataInterop]] → [[Houdini-Engine]]：PCG 可通过外部数据桥接导入 Houdini 生成的点云
- [[PCG-运行时生成]] → [[VSM-虚拟阴影]]：运行时生成的内容需要 VSM 支持动态阴影更新
- [[PCG-Graph设计]] → [[UnrealMCP-工具调用]]：AI 助手可通过 MCP 调用 PCG 工具，自动生成和修改 Graph

**你必须做**：检查合理性，手动添加 `[[链接]]`。

---

## 任务 3：周数据总结 + 下周规划（AI 执行，你补充）

**AI 建议下周重点**：
- 周一：PCG 高级节点深入（Spline Sampler、Volume Sampler、Point Cluster）
- 周二：自定义 PCG Node 开发（C++ 扩展，实现一个完整的 `PCGBuildingPlacer`）
- 周三：Houdini Engine 与 PCG 的集成工作流（外部数据导入）
- 周四：PCG 运行时生成 + World Partition 分区策略
- 周末：完整项目——程序化城市生成器（道路 + 建筑 + 植被 + 街景）

**你必须做**：根据实际工作负荷调整。

---

## 任务 4：快速复习闪卡（AI 生成）

**AI 输出**：Anki/闪卡格式

| 正面 | 背面 |
|------|------|
| PCG 是什么的缩写？ | Procedural Content Generation（程序化内容生成） |
| PCG 的 3 个核心模块？ | PCG（核心）、PCGGeometryScriptInterop（几何桥接）、PCGExternalDataInterop（外部数据） |
| FPCGPoint 包含什么字段？ | Transform（位置/旋转/缩放）、Density（密度）、Seed（种子） |
| Attribute 存储在哪里？ | FPCGPointData 的 FPCGMetadata 中（TMap<FName, Column>） |
| Graph 执行顺序如何确定？ | 拓扑排序（依赖分析） |
| 为什么 PCG 是 Deterministic？ | 相同 Seed + 相同输入 → 相同输出 |
| Sampler / Filter / Transform / Spawn 的分工？ | Sampler 生成点、Filter 筛选点、Transform 修改点、Spawn 输出到世界 |
| Density 的作用？ | 筛选阈值 + 混合权重 |

**你必须做**：导入 Anki 或手写复习。

---

## 完成检查清单

- [ ] PCG 知识测验已完成（得分 ≥80）
- [ ] 错题已复习，薄弱点已标记
- [ ] 笔记双向链接已手动添加（至少 3 条）
- [ ] 周数据总结已补充主观信息
- [ ] 下周计划已调整并写入 Obsidian 周模板

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 1 小时*
