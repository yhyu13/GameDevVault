---
tags: [routine/AI-tasks, topic/PCG, day/Wednesday]
aliases: []
---

# 周三：AI 任务清单 — PCG 游戏观察与体验

> **人类目标**：以开发者视角观察游戏中 PCG 的实际应用，分析设计决策与技术取舍。  
> **AI 任务**：帮你结构化观察、生成对比表格，绝不替你做体验。

---

## 任务 1：游戏 PCG 实例观察清单（AI 执行）

**输入**："我要观察游戏中 PCG 的实际应用（No Man's Sky、Minecraft、Hades、UE5 样例项目）。生成结构化观察清单"

**AI 输出**：

### PCG 游戏实例观察清单

| 观察维度 | 具体观察点 | 记录方式 |
|----------|-----------|---------|
| **生成类型** | 使用什么 PCG 技术？（噪声地形、WFC、房间连接、植被散布） | 截图 + 笔记 |
| **输入约束** | 玩家/设计师提供了哪些输入？（Seed、生物群系参数、手工放置的关键点） | 截图 |
| **输出多样性** | 同一参数下重复生成的变化程度？（Deterministic vs 随机变化） | 多次重启对比 |
| **玩家感知** | 玩家是否能察觉程序化生成？（是否感觉 "自然" 或 "重复"） | 主观评价 |
| **性能表现** | 生成时是否有卡顿？加载时间是多长？ | 计时/录屏 |
| **可控性** | 玩家或设计师能在多大程度上控制生成结果？（微调参数 vs 完全自动生成） | 功能测试 |
| **与手工结合** | 哪些部分是 PCG 的，哪些是手工的？（混合工作流） | 分析 |

**推荐观察对象**：
- **No Man's Sky**：星球地形 + 植被生态的完整 PCG 管线（噪声 + 生物群系规则）
- **Minecraft**：基于 Perlin Noise 的地形 + 洞穴生成（结构生成器）
- **Hades**：房间布局的 WFC（Wave Function Collapse）风格生成（受约束的伪随机）
- **UE5 PCG 样例项目**：官方演示的森林、城市程序化生成（可直接分析 Node Graph）

---

## 任务 2：PCG 截图分析与 AI 辅助（AI 辅助）

**AI 输出**：分析框架

当你上传截图后，AI 帮你分析：

### 植被散布分析（UE5 PCG 森林样例）
| 分析项 | 观察结果 | 推测的 PCG Node 链 |
|--------|---------|-------------------|
| 分布密度 | 近密远疏 | `Surface Sampler` + `Density Filter`（距离衰减） |
| 规模变化 | 大树在空地，小树在密林 | `Transform Points`（Scale 按 Density 反比） |
| 颜色差异 | 向阳面更绿，背阴面偏暗 | `Attribute Noise` / `Color Attribute`（基于法线） |
| 群落模式 | 成群分布而非完全随机 | `Point Cluster` 或 `Poisson Disk Sampling` |
| 地形适配 | 树根贴合斜坡 | `Project To Surface` + `Align To Normal` |

### 城市布局分析（UE5 PCG 城市样例）
| 分析项 | 观察结果 | 推测的 PCG Node 链 |
|--------|---------|-------------------|
| 道路网格 | 有主路、支路、死胡同 | `Spline Sampler` + `Branching` |
| 建筑间距 | 沿街有退界，空地有填充 | `Transform`（Offset）+ `Filter`（Intersection） |
| 建筑类型 | 市中心高楼，郊区低层 | `Attribute`（按 DistanceToCenter 设置 BuildingType） |
| 绿化分布 | 道路两侧有行道树 | `Edge Sampler` + `Static Mesh Spawner` |

**你必须做**：上传至少 3 张 PCG 场景截图，填写上表，并尝试在 UE5 编辑器中复现类似效果。

---

## 任务 3：UE5 样例项目观察（AI 辅助）

**AI 输出**：UE5 PCG 样例项目分析模板

```markdown
## UE5 PCG 样例项目：_[样例名称]_

### 项目信息
- 来源：UE5 Marketplace / Epic Games GitHub / 官方文档示例
- 版本：UE5.4+ / UE5.8
- 场景类型：森林 / 城市 / 洞穴 / 地形

### Graph 结构分析
- 总节点数：_
- 主要节点类型：Sampler（_个）、Filter（_个）、Transform（_个）、Spawn（_个）
- 最复杂的子图：_
- 使用的自定义节点：_

### 关键设计模式
1. _ → 为什么这样设计？
2. _ → 如果我来改，会怎么优化？

### 性能观察
- 生成时间：_ ms
- Point 总数：_
- 是否使用 `Partition Actor` 或 `Grid Partition`？

### 与 Monday/Tuesday 的关联
- 周一学到的 Graph 执行顺序在这里的体现：_
- 周二练习的 Attribute 变换在这里的使用：_
```

**你必须做**：打开 UE5 PCG 样例（如 Electric Dreams、Lyra 或官方 PCG Demo），逐节点分析 Graph，填写上表。

---

## 任务 4：概念关联笔记（AI 辅助）

**AI 输出**：关联模板

```markdown
## PCG 观察与理论关联

### 周一理论 → 周三观察
- **理论**：PCG Graph 是节点化的数据流管线
- **观察**：样例中的 `Surface Sampler` → `Density Filter` → `Transform` → `Spawn` 正好验证了这一点
- **顿悟**：_

### 周二练习 → 周三观察
- **练习**：我设计的 `PointScaler` 节点修改了 Scale Attribute
- **观察**：样例中的树木大小不一，正是通过类似 Attribute 变换实现的
- **新发现**：_

### 未解答的问题
- 样例中的 `_` 现象，我还无法解释，需要查文档或源码
```

**你必须做**：补充主观判断和顿悟。

---

## 今日 AI 禁区

- ❌ 让 AI 替你体验（你必须亲自打开 UE5 编辑器、运行样例、截图）
- ❌ 盲目相信 AI 的对比分析（必须自己验证 Node 链的推测）
- ❌ 不做自己观察（这是 experiential learning，必须亲眼看到生成效果）
- ❌ 不与周一/周二内容关联（观察必须与理论学习闭环）

---

## 完成检查清单

- [ ] 至少观察了 2 个游戏/样例的 PCG 实例（1 个游戏 + 1 个 UE5 样例）
- [ ] 已截图/录屏 ≥3 张 PCG 场景，并做了结构化分析
- [ ] UE5 样例的 Graph 节点结构已记录（至少 5 个关键节点的功能）
- [ ] 概念关联笔记已写入 Obsidian，包含至少 1 个 "顿悟"
- [ ] 记录了至少 1 个 "我还无法解释" 的问题（下周学习目标）

---

*AI 执行时间：约 10 分钟*  
*人类执行时间：约 1.5 小时（观察 + 分析 + 整理）*
