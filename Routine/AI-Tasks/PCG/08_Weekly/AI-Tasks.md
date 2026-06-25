---
tags: [routine/AI-tasks, topic/PCG, day/Weekly]
aliases: []
---

# 每周：AI 任务清单 — PCG 技术社交

> **人类目标**：与 PCG 社区和程序化生成专家交流，验证技术路线。  
> **AI 任务**：润色措辞、生成问题、准备资料，绝不替代社交互动。

---

## 任务 1：技术问题润色（AI 执行）

**输入**：你的 raw 问题，如 "pcg 的 attribute 怎么在 runtime 改"

**AI 输出**：知乎版 / Twitter 版 / Discord 版

**示例（知乎版）**：
> 标题：UE5.8 PCG 的 Attribute 系统在运行时如何动态修改？
> 正文：我正在开发一个运行时大世界生成系统，使用 UE5.8 的 PCG 框架。目前 PCG Graph 在编辑器下工作良好，但希望在运行时根据玩家位置动态修改某些 Point 的 Attribute（如 Density、BiomeType）。
> 我查阅了文档，发现 `UPCGComponent` 有 `Generate` 接口，但不确定：
> 1. 运行时修改 Attribute 后，是否需要重新执行整个 Graph？
> 2. 是否有部分重执行（Partial Re-execution）的机制，只更新受影响的下游节点？
> 3. 在 World Partition 场景下，PCG Volume 的按 Cell 生成是否与运行时修改冲突？
> 感谢指点！

**示例（Twitter 版）**：
> 学习 UE5.8 PCG 的第 3 周：做了一个 Biome Mixer 节点，按地形高度自动切换植被类型。发现 Attribute 系统比想象中灵活——每个 Point 都可以携带自定义数据，下游节点按 Attribute 做筛选和变换。下一步：运行时生成 + World Partition 分区。有在做 PCG runtime 生成的朋友吗？#UE5 #PCG #ProceduralGeneration

**你必须做**：确认润色后仍表达你的真实问题，自己发帖。

---

## 任务 2：冷消息起草（AI 执行，你个性化）

**输入**：你想联系一位在 PCG 领域活跃的大佬（如 Epic Games 的 PCG 开发团队成员、或知名 PCG 技术美术）

**AI 输出**：礼貌模板（150 字内，展示你做过的功课）

**示例**：
> 您好 [名字]，
> 
> 我是 [你的名字]，正在深入学习 UE5.8 的 PCG 框架。我实现了一个自定义的 `Biome Mixer` 节点，通过高度阈值自动分发植被类型，并写了 Python 工具导出点云数据做离线分析。
> 
> 想请教您关于 PCG 的运行时生成策略：在开放世界场景下，如何平衡 "全量预生成" 和 "按需运行时生成"？World Partition 的 Cell 加载与 PCG Volume 的分区策略如何协同？
> 
> 我的项目仓库：[GitHub 链接]
> 
> 期待您的回复，谢谢！
> [你的名字]

**你必须做**：添加具体细节（引用对方的博客/演讲/论文/GitHub），自己发送。

---

## 任务 3：开源贡献（AI 执行）

**AI 建议**：匹配你的 PCG 技能到开源项目

| 项目 | 匹配度 | 建议贡献方向 |
|------|--------|-------------|
| [EpicGames/UnrealEngine](https://github.com/EpicGames) | 高 | 反馈 PCG 相关 Issue（Bug 报告、文档改进） |
| [UE5 PCG 社区插件](https://github.com/search?q=ue5+pcg) | 高 | 提交自定义 Node 示例或工具脚本 |
| [Houdini Engine for UE](https://github.com/sideeffects) | 中 | 改进 Houdini → PCG 的数据桥接文档 |
| [Awesome-Procedural-Generation](https://github.com/topics/procedural-generation) | 中 | 添加 UE5 PCG 学习资源 |

**具体贡献建议**：
1. 给 Unreal Engine 提一个 PCG 文档改进 Issue：补充 `PCGExternalDataInterop` 的使用示例
2. 在 GitHub 上分享你的 `export_pcg_points.py` 脚本，写清楚使用说明
3. 在 UE 论坛回答一个关于 "自定义 PCG Node 编译失败" 的问题（用你周二踩坑的经验）

**你必须做**：自己找 issue、读代码、写修复、提 PR 或评论。

---

## 任务 4：社区参与（AI 执行，你行动）

**AI 建议**：

| 平台 | 行动 | 内容 |
|------|------|------|
| Twitter/X | 发技术推文 | 分享 PCG 学习进展（截图 + 关键代码片段） |
| LinkedIn | 发学习总结 | "本周学习了 UE5.8 PCG 框架，做了 X、Y、Z" |
| Discord（UE 开发者社区） | 回答问题或提问 | 分享 Biome Mixer 实现经验，或请教运行时生成问题 |
| 知乎/博客园 | 写文章 | 发布 Blog 初稿的精简版 |
| Bilibili/YouTube | 发视频 | 录制 5 分钟 PCG Graph 搭建演示 |

**你必须做**：选择至少 1 个平台，实际发布内容。

---

## 完成检查清单

- [ ] 至少发了 1 个技术问题（关于 PCG 运行时生成、Attribute 系统或 World Partition 集成）
- [ ] 至少与 1 位行业人士交流（PCG 开发者、技术美术或引擎工程师）
- [ ] 至少给 1 个开源项目提了 Issue/PR/Comment（UE 引擎或 PCG 社区项目）
- [ ] 至少在 1 个社交平台分享了学习成果（Twitter/LinkedIn/Discord/知乎）
- [ ] 交流收获已整理到 Obsidian 职业复盘日志
- [ ] 技术雷达已更新（如有新的 PCG 工具或框架发现）

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2-3 小时（参加活动 + 社交 + 整理）*  
*产出：N 个新联系 + 1 次开源贡献 + 技术路线验证*
