---
tags: [routine/AI-tasks, topic/NeuralRendering, day/Wednesday]
aliases: []
---

# 周三：AI 任务清单 — Neural Rendering 游戏观察与体验

> **人类目标**：以开发者视角观察 ML 驱动动画在游戏中的实际表现，理解技术如何落地。  
> **AI 任务**：帮你结构化观察、生成对比表格，绝不替你做体验。

---

## 任务 1：ML 驱动动画游戏观察清单（AI 执行）

**输入**："我要观察游戏中 ML 驱动或数据驱动的高级 deformation 效果。生成结构化观察清单"

**AI 输出**：

### ML Deformation 观察清单

| 观察维度 | 具体观察点 | 记录方式 |
|----------|-----------|---------|
| **肌肉变形** | 角色发力时肌肉是否有隆起/收缩？变形是否自然？ | 截图/慢动作 |
| **皮肤拉伸** | 关节弯曲时皮肤是否有褶皱或拉伸？ | 截图/录屏 |
| **布料动态** | 披风/裙子是否随身体运动产生可信 secondary motion？ | 录屏/帧分析 |
| **面部动画** | 表情变化时是否有 micro-expressions（细微抽搐）？ | 特写截图 |
| **性能指标** | 复杂角色场景中是否掉帧？ deformation 是否延迟？ | 帧率计数器 |
| **物理衔接** | 角色与物体交互时（如碰撞、抓握），变形是否一致？ | 录屏 |

**推荐观察对象**：
- FIFA 24/25（EA SPORTS FC）— ML-driven 球员面部和肌肉动画
- NBA 2K24/25 — 球员面部扫描 + neural animation
- Hellblade II — 高保真面部表情（可能使用 blendshape + ML 混合）
- UE5 Lyra / Content Examples — 官方 ML Deformer Demo
- Avatar: Frontiers of Pandora — 复杂生物动画和植被 deformation

---

## 任务 2：Screenshot 分析引导（AI 辅助）

**AI 输出**：分析框架

| 截图场景 | 分析要点 | 判断标准 |
|----------|---------|----------|
| 角色 T-pose vs 动作 pose | 同一角色在静息和发力状态下的 mesh 变化 | 是否有明显的体积变化？ |
| 关节特写（肘/膝） | 弯曲角度 > 90° 时的皮肤褶皱 | 是否有 compression wrinkle？ |
| 面部特写 | 说话时的嘴型和面颊变化 | 是否有逐 vertex 级别的细微变化？ |
| 布料特写 | 奔跑时的披风摆动 | 是简单的 bone-driven 还是有 secondary motion？ |

**你必须做**：上传 ≥3 张截图，AI 引导你分析每个区域。但最终的判断（这是 ML Deformer 还是传统 blendshape/physics）必须由你做出。

---

## 任务 3：UE5 ML Deformer 示例项目观察（如果可用）

**AI 输出**：观察清单

如果你可以访问 UE5.8 ML Deformer 示例项目或 Marketplace Demo：

| 观察项 | 问题 | 预期发现 |
|--------|------|----------|
| 训练数据可视化 | 项目中是否展示了 training data（模拟序列）？ | 应该有 Chaos Physics 缓存的 alembic / vertex cache |
| 网络资产 | Content Browser 中是否有 `.onnx` 或 `.mldeformer` 资产？ | 应该有 `UMLDeformerModel` 衍生资产 |
| 组件配置 | `SkeletalMeshComponent` 上是否附加了 `MLDeformerComponent`？ | Details Panel 中检查 |
| 性能面板 | 使用 `stat unit` 和 `stat neuralnetwork` 查看 inference cost | 应该在 0.05-0.2ms 范围内 |
| LOD 行为 | 远距离时 ML Deformer 是否关闭？ | 应该有距离/LOD 驱动的开关 |

**你必须做**：如果无法访问 UE5.8，观看官方视频或 GDC 演讲录屏，记录上述观察点。

---

## 任务 4：概念笔记连接（AI 辅助）

**AI 输出**：笔记模板

```markdown
## Neural Rendering 观察笔记：_[游戏名]_
### 观察日期：_

#### 周一/周二概念验证
1. 我观察到的 [现象] 对应论文中的 [概念]：_
2. 这个 deformation 可以用 [bone-driven / vertex-driven] 解释，因为：_
3. 训练数据可能来自 [Chaos / Maya / 手工雕刻]，证据：_

#### 技术判断
- 这是 ML Deformer 还是传统 blendshape？ 判断依据：_
- 如果是 ML，网络容量可能是多大？（观察 deformation 复杂度）_
- 性能开销是否可接受？（帧率、平台）_

#### 与 Chaos Physics 的关联
- 这个效果如果用实时 Chaos 模拟，能达到同样的质量吗？_
- 为什么开发者选择了 ML Deformer 而不是实时物理？（性能？质量？可控性？）_
```

**你必须做**：补充主观判断和创意想法。

---

## 今日 AI 禁区

- ❌ 让 AI 替你体验（你必须亲自玩游戏或看录屏）
- ❌ 盲目相信 AI 的技术分析（必须自己判断是 ML 还是传统方法）
- ❌ 不做自己观察（这是 experiential learning）

---

## 完成检查清单

- [ ] 至少观察了 1 个游戏或 1 个 UE5 Demo 的 deformation 效果
- [ ] 已截图/录屏 ≥3 张关键场景
- [ ] 结构化笔记已写入 Obsidian
- [ ] 至少记录了 1 个 "这个效果用 ML Deformer 实现，需要..." 的技术判断

---

*AI 执行时间：约 10 分钟*  
*人类执行时间：约 1 小时（体验）+ 30 分钟（整理）*
