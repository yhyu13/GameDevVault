---
tags: [routine/milestone, plan/active, role/entry-to-mid]
aliases: [90天milestones, 输出milestones, entry-到-mid-90天计划]
---

# 90 天输出 milestones — entry-level → mid-level 跨越

> 本文件是「我接下来 90 天要交付什么」的活文档。每个 milestone 完成后，新增一条日志到 `m1-xxx.md` / `m2-xxx.md` / ...
> 框架：矫正 consume → produce 的不对称。诊断力 + 产物量 = entry → mid 的真正分水岭。

---

## 现状快照

| 维度 | 现状 | 目标（90 天后） |
|------|------|----------------|
| 角色 | entry-level game engine programmer | 至少够格 mid-level 面谈 |
| 引擎 | Unreal（工作中读别人项目代码为主） | Unreal generalist，能独立交付一个子系统 |
| 产出习惯 | consume 多、produce 少 | 每周有可被他人 review 的 artifact |
| 公共资产 | 几乎没有 | 2-3 篇外部可读文章 + 1 次小 PR |
| Diagnostic 能力 | 偶发 | 用 `Unreal Insights` / `RenderDoc` 跑端到端 profile |

**核心洞察**：entry → mid 的真正分水岭不是「我知道多少」，是「我能交付什么 + 我能多快定位 bug 根因」。

---

## 30 天（建立产出习惯）

> 目标：从「只读」变成「读 + 改 + 写」三件套并行。

### M1. 真实项目 fork 改造（每周 1 个子系统）
- 选一个：Lyra / Valley of the Ancient / 当前工作项目 fork
- 每周挑一个子系统改造（不是只读）
- 每改一处 → commit + 写一条 `Routine/02-引擎源码分析库/<子系统>.md`
- **完成标准**：3-4 周后有 3-4 个被你亲手改过的真实子系统笔记

### M2. 自建 Game Feature Plugin
- 建 `UMyGameFeature` + `UGameFeatureAction`，逼自己过 Lyra 风格的生命周期
- 完成后写笔记 `unreal-gameplay-gamefeature-plugin-lifecycle.md`
- **完成标准**：插件能注册 / 启停 / 配置加载全套跑通

### M3. 30 分钟复盘纪律（**最重要的一条**）
- 每次读完一段代码 → **关掉 IDE**
- 手画一张调用链图 + 写 ≤100 字「如果我要改它，我会动哪 3 处」
- 这是 mid-level 思维的核心动作：先有假设，再去看代码
- **完成标准**：连续 21 天不中断（习惯固化需要 3 周）

---

## 60 天（练诊断肌肉）

> 目标：从「看代码」变成「能定位 bug + 能 profile 系统」。

### M4. 抓 3 个真实 bug
- 来源：Lyra / Valley / 工作项目 / 任一开源 Unreal 项目 issue 列表
- 流程：reproduce → `Unreal Insights` / `RenderDoc` / log 跑出来 → 定位根因 → 修 → 写笔记
- 输出：3 条笔记，分布在 `Routine/04-性能优化备忘录/` 或 `Routine/02-引擎源码分析库/`
- **完成标准**：3 个 bug 全闭环，至少 1 个跨模块根因

### M5. Unreal Insights 全程 profile 一个真场景
- CPU + GPU + 内存三轨都要看
- 输出 1 页「指标 / 瓶颈 / 优化方案」笔记到 `Routine/04-性能优化备忘录/`
- **完成标准**：三轨指标全跑过 + 至少定位一个真实瓶颈 + 给出可执行的优化方案

### M6. 深度分析一个当前项目里的引擎子系统
- 候选：`ReplicationGraph` / `GameplayMessageRouter` / `Mass Entity` / `AnimGraph`
- 读 `Unreal/Engine/Source/` 原始实现 + 1 篇 Epic 官方 blog + 写深度笔记
- tag 必须是 `source/深度分析`，不是 `浅度浏览`
- **完成标准**：能向同事讲清「它为什么这么设计」+「如果我重写我会怎么取舍」

---

## 90 天（把积累变成公共资产）

> 目标：从「个人学习」变成「能被他人看到的输出」。

### M7. 写 2-3 篇短文
- 发布渠道：知乎 / 博客 / 工作 wiki
- 每篇 = vault 里一条笔记的精炼版 + 一张你自己画的图
- **写作是终极过滤器**：写不出来 = 没真懂
- **完成标准**：2-3 篇已发布 + 至少 1 篇有外部反馈（评论 / 点赞 / 转发）

### M8. 给一个 OSS Unreal 插件 / 公共 sample 提个小 PR
- 哪怕 typo / doc 改进都算
- 重点不是 PR 被合，是走完 fork → branch → 提交 → review → 改 → 合的完整流程
- **完成标准**：PR 已开 + 经过至少一轮 review 反馈（不管最终是否合）

### M9. 一次 15-30 分钟技术分享
- 主题 = vault 里你最熟的一个子系统
- 受众：工作团队 / 学习群 / 线上 meetup
- **核心指标**：「我能讲 30 分钟」是 entry → mid 的硬指标
- **完成标准**：讲完 + 有录音 / 录像 / 文档留档

---

## 跨阶段横切

### M10. 跨引擎对比思维（贯穿 90 天）
- 主题：Unreal / Unity / Godot / 自研引擎的「同一类问题怎么解」
- 推荐切入点：网络同步、资产加载、LOD、动画系统
- Generalist 升得最快的人 = 能把任意引擎子系统放进统一分类法
- **做法**：每读完一个 Unreal 子系统，顺手在笔记里加一栏「Unity / Godot 是怎么做的」（哪怕只是简单列点）

---

## 这个 vault 团队怎么帮我

| Rein | 用法 |
|------|------|
| [[paper-reader]] | 给它 PDF / GDC 链接，让它产出 `Routine/01-论文笔记库/` 笔记；要求 tag 是 `paper/signed` —— 签名 = 真过了一遍 |
| [[source-tracker]] | 把 M1 / M4 / M6 每一步的代码分析交给它；它会按 `99-Templates/源码分析.md` 写笔记，强制「代码位置」段列真实文件路径，逼你读到具体行 |
| [[vault-curator]] | 每月跑一次：扫 `Routine/02-` `04-` 目录下有没有 `tag/source/浅度浏览` + 0 出链的笔记，列给你决定补深度 / 合并 / 删 |

---

## 单点最关键

**先做 M3（30 分钟复盘）**。它是免费的、每天都能做的、且 30 天后会让你回头看自己代码笔记完全不同。其它都需要时间或环境，M3 只需要你下班后关掉 IDE。

---

## 自查清单（每周日晚勾选）

- [ ] 本周至少 commit + 笔记 1 处代码改造（M1 滚动）
- [ ] 本周有至少 3 次 30 分钟复盘（M3 滚动）
- [ ] vault 里新增笔记的 tag 没有「待精读 / 浅度浏览」停留在 4 周以上
- [ ] 本周读过 1 段真实工作项目代码（不仅是引擎源码）
- [ ] 如果 M4 / M5 / M6 启动，对应 bug / 场景已经选定

---

## 已完成 milestones 索引

> 完成后追加：`m1-lyra-gamefeature-completed.md`、`m2-replicationgraph-deepdive.md` ...
> 每个 milestone 文件夹用 `done/<milestone-id>/<日期>.md` 记录完成日期 + 总结。

- _暂无_

---

## 关联

- [[../References/AI-Augmentation-Reference|AI 辅助学习参考手册]] —— 每周任务 AI 辅助度总表
- [[../AI-Tasks/Lumen/00-Master-Index|Lumen AI 任务总览]] —— 当前学习主题的 AI 任务编排
- [[../00-README|Routine 目录说明]] —— Routine/ 整体使用方式
- [[../../../AGENTS|AGENTS.md]] —— Vault 顶层 agent 约定

---

*Created by AI (Mavis) on 2026-06-24 as the entry-to-mid growth roadmap.*  
*Last modified: 2026-06-24*