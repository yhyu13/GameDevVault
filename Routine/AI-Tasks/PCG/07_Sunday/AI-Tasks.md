---
tags: [routine/AI-tasks, topic/PCG, day/Sunday]
aliases: []
---

# 周日：AI 任务清单 — PCG 项目收尾与周复盘

> **人类目标**：完成 mini-PCG 项目的最终集成，输出文档，做周复盘。  
> **AI 任务**：协助 debug、润色文档、生成复盘模板，绝不写核心代码。

---

## 上午：项目收尾（2h）

### 任务 1：集成测试辅助（AI 执行）

**AI 输出**：测试矩阵

| 测试场景 | 输入 | 预期输出 | 验证方法 |
|----------|------|----------|---------|
| 低地生成 | Z < 0 | 生成湿地植被（芦苇、灌木） | 视口检查 + CSV 验证 |
| 森林生成 | 0 <= Z < 500 | 生成森林植被（橡树、松树） | 视口检查 + CSV 验证 |
| 山地生成 | Z >= 500 | 生成山地植被（岩石、矮松） | 视口检查 + CSV 验证 |
| 边界测试 | Z = 0 或 Z = 500 | 明确属于某一生物群系（无重叠） | 断言 |
| Density 筛选 | Density = 0.3，Filter 阈值 = 0.5 | 该点被剔除 | 计数对比 |
| Attribute 传递 | BiomeType 设置后 | 下游 Spawn Node 正确读取 | 断点/日志 |
| 确定性测试 | 相同 Seed + 相同参数 | 两次生成结果完全相同（Point 位置一致） | 哈希对比 |
| 多线程安全 | 大规模生成（50,000 Point） | 无崩溃、无数据竞争 | 重复运行 10 次 |
| CSV 导出 | 1000 Point | CSV 文件含 1000 行，列正确 | 文件解析 |
| 性能测试 | 10,000 Point | 生成时间 < 2s | 计时 |

**你必须做**：运行每个测试，记录实际结果。

---

### 任务 2：性能 Baseline（AI 执行，你测量）

**AI 输出**：Benchmark 方案

| 指标 | 测量方法 | 目标 |
|------|----------|------|
| Graph 执行时间 | `UPCGComponent::ExecuteGraph` 前后 `FPlatformTime::Cycles64()` | < 2s（10,000 Point） |
| Point 生成速率 | 总 Point 数 / 执行时间 | > 5,000 Point/s |
| 内存占用 | `LLM` 或 `Memory Insights` 测量 PCG 峰值 | < 50MB（10,000 Point） |
| Attribute 查询时间 | 遍历 10,000 Point 读取 Attribute | < 10ms |
| 实例化时间 | Static Mesh Spawner 生成 ISM 实例 | < 1s |
| CSV 导出时间 | Python 解析并导出 10,000 Point | < 3s |

**你必须做**：实际运行 benchmark，记录数据。

---

## 下午：文档与复盘（1-2h）

### 任务 3：项目文档生成（AI 执行，你填充）

**AI 输出**：README 模板

```markdown
# mini-pcg-forest
> 一个 UE5.8 PCG 程序化森林生成器，支持按高度分层的生物群系混合

## 功能
- 基于 Landscape 的 `Surface Sampler` 生成初始点云
- 自定义 `Biome Mixer` C++ 节点按高度分区（湿地/森林/山地）
- 根据 `BiomeType` Attribute 自动选择对应的 Static Mesh
- 支持 `Density` 筛选和随机变换（旋转/缩放）
- Python 工具将生成结果导出为 CSV

## 快速开始
```bash
# 1. 克隆项目到 UE5 Plugins 或独立项目
git clone [repo]

# 2. 打开项目，在关卡中放置 PCG Volume
# 3. 指定 PCG_ForestMaster Graph
# 4. 调整 Landscape 和 Biome Mixer 参数
# 5. 点击 Generate 或运行时自动执行

# 6. 导出点云数据
python Tools/export_pcg_points.py --input [exported.json] --output forest.csv
```

## 性能
| 指标 | 数值 |
|------|------|
| Graph 执行时间 | _ms |
| Point 生成速率 | _ Point/s |
| 内存占用 | _MB |
| CSV 导出时间 | _s |

## PCG Graph 结构
```
Landscape Surface Sampler → Biome Mixer → Density Filter → Transform Points → Static Mesh Spawner
```

## 学习笔记
见 [Obsidian Vault](link)
```

**你必须做**：填写所有数据和测量结果。

---

### 任务 4：周复盘辅助（AI 执行，你补充）

**AI 输出**：数据总结 + 模式发现 + 下周建议

**数据总结**：
- 本周完成：PCG 架构学习、自定义 Node 开发、Graph 搭建、Python 工具
- 代码量：_ 行 C++、_ 行 Python、_ 个 Blueprint 节点
- 发现的关键概念：Attribute 系统、Graph 拓扑排序、Deterministic Generation

**模式发现**：
- 周一/周二的概念学习如何体现在周三/周末的实践中？
- 哪些技术决策在回头看来是正确的？哪些需要修正？

**下周建议**：
- 周一：PCG Spline 节点（道路/河流生成）
- 周二：Houdini Engine 集成（外部点云导入）
- 周三：运行时生成（World Partition + Streaming）
- 周四：与 MassAI 集成（PCG Point → Mass Entity Spawn）
- 周末：完整项目——程序化城市（道路 + 建筑 + 街景）

**你必须做**：补充主观体验（能量、顿悟、困难、意外发现）。

---

## 今日 AI 禁区

- ❌ 让 AI 替你运行测试和 benchmark
- ❌ 让 AI 替你写项目文档的核心技术描述
- ❌ 让 AI 替你写周复盘日记
- ❌ 让 AI 替你决定下周计划

---

## 完成检查清单

- [ ] mini-PCG Forest 集成测试全部通过（10/10）
- [ ] 性能 benchmark 已运行，数据已记录
- [ ] README 文档已填写并发布到 GitHub
- [ ] 周复盘已完成，主观体验已补充
- [ ] 下周计划已调整并写入 Obsidian
- [ ] 所有链接（GitHub、博客、Obsidian）已更新到知识库

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 3-4 小时*  
*产出：1 个完整 PCG 生成器 + 1 份文档 + 1 次周复盘 + 下周计划*
