---
tags: [radar/P1, radar/AI-NPC, radar/工具链]
aliases: [Inworld, Convai, Charisma.AI, Character.AI, LLM NPC, AI NPC 平台]
quarterly_review: 2026-Q3
---

# LLM-NPC 平台 — Inworld / Convai / Charisma.AI(产品形态)

| 字段 | 内容 |
|------|------|
| **技术名称** | LLM-NPC 产品平台(Inworld AI / Convai / Charisma.AI / Character.AI) |
| **类别** | AI-NPC / 工具链(产品形态) |
| **当前优先级** | P1 |
| **发现日期** | 2026-06-25 |
| **最后评估日期** | 2026-06-25 |

---

## 一句话简介

> 把"有性格、有记忆、能对话、能调函数"的 LLM-NPC 做成"产品级 SDK",你只需要写 system prompt + 接 API — **Inworld 已经做到"长期记忆 + 情绪 + 性格"生产可用,NVIDIA ACE 的 partner 名单里 4 家都是这个赛道**(Convai / Charisma.AI / Inworld / UneeQ)。

---

## 成熟度评估

| 维度 | 评分 (1-5) | 说明 |
|------|------------|------|
| 生产可用性 | 4 | 多家商用,NVIDIA ACE 官方合作,有 UE/Unity SDK |
| 文档完善度 | 4 | Inworld Studio 文档 + 视频教程齐全,Convai 有示例工程 |
| 社区活跃度 | 4 | Discord 活跃,Twitter 案例分享多 |
| 学习资源 | 4 | Inworld Studio 可视化配置 + Unity/UE SDK 接入,门槛低 |
| 与现有栈兼容性 | 4 | UE 插件 / Unity 资产 / REST API,主流引擎全覆盖 |

**2026 年 6 月主流产品对比:**

| 平台 | 核心能力 | UE 集成 | 价格模型 | 特色 |
|------|----------|---------|----------|------|
| **Inworld AI** | 性格 + 记忆 + 情绪 + 动作 | 有 SDK | 按使用量 | 长期记忆最强 |
| **Convai** | 实时对话 + NVIDIA 深度集成 | 有插件 | 按使用量 | NVIDIA 拉面 demo |
| **Charisma.AI** | 故事驱动 NPC | 有 SDK | 按项目 | 互动叙事强 |
| **Character.AI** | 消费级角色对话 | 主要是消费产品 | 免费 + 订阅 | 角色最丰富 |
| **UneeQ** | 数字人 + 实时对话 | 有 SDK | 按使用量 | 营销向数字人 |

**和 [[NVIDIA-ACE-AI-NPC]] 的关系:**
- ACE 是**底层微服务**(ASR/LLM/TTS/A2F 拆开卖)
- 这些平台是**包装好的产品**,对中小项目更友好
- 大厂可能 ACE + 自研,中小项目直接用 Inworld / Convai 更划算

---

## 学习成本估算

| 阶段 | 时间 | 产出 |
|------|------|------|
| 上手入门 | 2 天 | 注册 Inworld Studio,做 1 个有性格的 NPC,导出到 UE |
| 熟练应用 | 1 周 | 掌握 system prompt 写作 + 知识库(RAG)接入 + 行为树 fallback |
| 深度掌握 | 1 月 | 能做"AI NPC 行为系统设计",理解 NPC 性格 / 记忆 / 情绪 / 行为的工程化抽象 |

**关键技能点:**
- **System Prompt 写作**:定义 NPC 的"人格 + 知识边界 + 说话风格 + 决策规则"
- **RAG(检索增强)**:把游戏世界的 lore / 任务 / 物品知识喂给 NPC,让他真的"知道"
- **Fallback 设计**:LLM 输出不合规 / 超时 / 敏感内容时怎么降级 — 这是产品稳定性关键
- **成本控制**:LLM 调一次 1-3 美分,100 个并发 NPC 持续对话 1 小时 ≈ $30-100,**做产品必须算账**

---

## 与当前工作的关联

- [ ] 直接相关 — 当前项目可用(取决于项目类型)
- [x] 间接相关 — 未来项目可能用
- [x] 知识拓展 — 拓宽技术视野

**具体关联点:**
- **UE 项目集成**:Inworld / Convai 都有 UE 插件,接 Lyra 的 GameFeature 框架很顺
- **NPC 行为替代**:把"Behavior Tree 写死的状态机"逐步替换成"LLM 决策 + BT 兜底",这是行业大趋势
- **NPC 设计模式**:从"写死对话树"转向"定义 NPC 人格 + 知识 + 行为约束" — 这是新的设计 discipline
- **协同 ACE**:如果项目需要自托管 LLM(保密/低延迟),ACE + 自研;如果可以走云,Inworld/Convai 更快

**对你 day-job 的真实杠杆:**
- 读 Lyra / GAS 代码时,理解 "AI Controller + Behavior Tree" 怎么替换成 LLM 决策
- 给 demo 做"会说话的 NPC" 不再是 1-2 周的工作,1 天就能出
- 面试时讲"我用 Inworld Studio 做了 X NPC,接到了 UE 里" — 这是新兴能力

---

## 评估记录

| 日期 | 评估人 | 结论 | 次回顾 |
|------|--------|------|----------|
| 2026-06-25 | 我 | P1 持续关注 — 跑通 1 个 Inworld demo 就足够 | 1个月后 |
| 2026-07-03 | 我 | Q3 启动 — 纳入季度复盘 Routine | 2026-07-25 |

---

## 关键资源

- Inworld AI:https://inworld.ai/(推荐先玩这个)
- Convai:https://convai.com/
- Charisma.AI:https://charisma.ai/
- a16z 关于 AI-NPC 的报告:https://a16z.com/the-generative-ai-craze-in-gaming/
- 推荐阅读:Stanford Generative Agents 论文(2023)— https://arxiv.org/abs/2304.03442

---

## 状态迁移

- [x] P0 → 正在学习中 → 已掌握 → 移出雷达
- [x] P1 → 评估后降为 P2 / 升为 P0
- [ ] P2 → 评估后放弃 / 升为 P1

---

## 我的判断(只对你说)

**对你来说,这和 ACE 的区别是:ACE 是"我会做",Inworld/Convai 是"我会用"**。  
跑通一个 Inworld Studio demo(2 小时) + 接到 UE 里(2 天) = 简历上多一个能讲的技能。  
**警惕:别陷入"哪个平台更好"的工具党争论** — 选定一个,跑通 demo,知道 LLM-NPC 是什么、怎么用、未来在哪。**核心能力是 prompt 工程 + RAG + 行为系统设计**,平台只是载体。  
最值钱的练习:**用 Inworld Studio 做一个有"3 个弱点 + 5 句口头禅 + 2 段过去"的 NPC**,导出到 UE 里让他真的能对话 — 这个体验是"读 10 篇博客" 替代不了的。

---

*Create date: 2026-06-25*  
*Last modified: 2026-06-25*
