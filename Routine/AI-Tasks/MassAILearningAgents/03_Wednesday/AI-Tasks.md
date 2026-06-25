---
tags: [routine/AI-tasks, topic/MassAI, topic/LearningAgents, day/Wednesday]
aliases: []
---

# 周三：AI 任务清单 — MassAI 游戏观察与体验

> **人类目标**：以开发者视角观察大型游戏中 Mass AI 的实际表现，体验 UE5 官方示例。  
> **AI 任务**：帮你结构化观察、生成对比表格，绝不替你做体验。

---

## 任务 1：Mass AI 游戏观察清单（AI 执行）

**输入**："我要观察大型游戏中 Mass AI 的实际表现。生成结构化观察清单"

**AI 输出**：

### Mass AI 游戏观察清单

| 观察维度 | 具体观察点 | 记录方式 |
|----------|-----------|---------|
| **密度与 LOD** | 同屏最多多少 Agent？远距离是否简化？是否突然消失？ | 截图/计数 |
| **行为多样性** | Agent 行为是否重复？（如行人走路动画是否同步）| 录屏 |
| **交互丰富度** | 是否有 SmartObject 交互？（坐下、买东西、交谈）| 录屏 |
| **避障与路径** | 人群是否穿模？是否自动避让？路径是否自然？ | 录屏 |
| **物理交互** | Agent 与物理对象（门、车）的交互是否流畅？ | 录屏 |
| **视觉质量** | 近距离 Agent 是否有细节？远距离是否 Instance 化？ | 截图 |
| **性能指标** | 大量 Agent 时帧率变化？（用 stat fps 或 MSI Afterburner）| 数据记录 |
| **StateTree 痕迹** | 能否观察到状态切换？（Idle → Walk → Sit → Talk）| 录屏 |

**推荐体验游戏/项目**：
- **Fortnite（UE5 版本）**：大逃杀后期的 NPC 群体、战场 AI
- **UE5 City Sample**：官方城市人群演示（5000+ 行人）
- **Lyra（UE5 官方示例）**：AI Bot 行为
- **The Matrix Awakens**：城市人群与车辆（早期 UE5 展示）
- **Star Wars Jedi: Survivor**：野生动物群（鸟群、虫群）
- **Assassin's Creed Unity**（历史参考）：万人同屏的人群系统
- **Cyberpunk 2077**：城市人群（虽然非 MassAI，但可对比）

---

## 任务 2：截图分析 + AI 辅助（AI 辅助）

**AI 输出**：分析框架

### 截图分析框架

| 截图编号 | 场景描述 | 观察到的 Mass AI 特征 | 推测的技术实现 |
|----------|----------|----------------------|---------------|
| 1 | 城市广场远景 | 数百人移动、无重动画 | LOD 0: 简化 Skeleton Mesh → LOD 2: Billboard/Instance |
| 2 | 近距离行人 | 有骨骼动画、面部细节 | LOD 0 Full、可能仍用 MassEntity + Actor 桥接 |
| 3 | 人群交互 | 两人对话、一人坐下 | SmartObject Slot 分配、StateTree 状态切换 |
| 4 | 车辆与行人 | 行人避让车辆 | MassAvoidance Processor、Spatial Hash 查询邻居 |

**你必须做**：
1. 截取至少 4 张截图（远景、近景、交互、异常）
2. 用 AI 辅助分析，但 **自己判断** 技术实现是否合理
3. 特别观察：是否存在「LOD 跳变」（Agent 从远处走近时突然加载细节）

---

## 任务 3：UE5 官方示例观察（City Sample / Lyra）

**AI 输出**：观察指南

### City Sample 观察指南

1. **下载**：从 Epic Launcher 下载 City Sample（或 GitHub）
2. **启动**：打开 `CitySampleMass` 地图
3. **观察点**：
   - 打开 `stat mass` 查看 MassEntity 统计信息（Entity 数量、Processor 耗时）
   - 打开 `stat game` 查看 AI 逻辑耗时
   - 在 World Settings 中调整 `MassSpawner` 的生成数量，观察性能变化
   - 用 `showflag.mass 1` 可视化 MassEntity 的 Debug 信息
4. **寻找 SmartObject**：
   - 场景中的长椅、售货机、公交站是否注册了 SmartObject？
   - Agent 如何发现并使用这些交互点？
5. **StateTree 观察**：
   - 选中一个 Mass Agent，观察它的状态变化（如 `Idle` → `Walk` → `UseSmartObject`）

### Lyra 观察指南

1. 观察 AI Bot 的 StateTree 使用（vs 传统的 Behavior Tree）
2. 对比 Lyra AI 与 City Sample 人群的技术差异

**你必须做**：实际打开 Editor，观察并记录。

---

## 任务 4：结构化笔记（AI 辅助）

**AI 输出**：笔记模板

```markdown
## Mass AI 游戏体验：_[游戏名]_
### 体验日期：_

#### 观察到的 Mass AI 特征
1. _ → 为什么好/不好？

#### 技术推测（基于周一/周二知识）
- 这个场景可能用了哪些 Processor？_
- SmartObject 可能如何配置？_
- LOD 策略可能是什么？_

#### 与 MassAI 学习的关系
- 周一学到的 _ 在这里表现为 _
- 周二写的 Processor 与之对比：_ vs _
- 我的 Processor 缺少的功能：_

#### 创意想法
- 如果我要做一个类似系统，我会改进 _
- 一个有趣的扩展：_
```

**你必须做**：补充主观判断和创意想法。

---

## 今日 AI 禁区

- ❌ 让 AI 替你体验游戏（你必须亲自打开 City Sample）
- ❌ 盲目相信 AI 的技术分析（必须自己观察 LOD 切换、SmartObject 使用）
- ❌ 不做自己观察（这是 experiential learning）
- ❌ 截图后不写分析（截图是数据，分析是洞察）

---

## 完成检查清单

- [ ] 至少体验了 1 个 Mass AI 游戏（City Sample 或 Fortnite 或类似）
- [ ] 已截图/录屏 ≥4 张（远景、近景、交互、异常）
- [ ] 结构化笔记已写入 Obsidian（包含技术推测和创意想法）
- [ ] 至少记录了 1 个 "如果我要做，我会改进..." 的创意想法
- [ ] 周一/周二的知识已与实际观察建立连接

---

*AI 执行时间：约 10 分钟*  
*人类执行时间：约 1 小时（体验）+ 30 分钟（整理）*
