---
tags: [routine/AI-tasks, topic/UnrealMCP, day/Weekly]
aliases: []
---

# 每周：AI 任务清单 — Unreal MCP 技术社交

> **人类目标**：与 MCP 社区和 AI 工具开发者交流，验证技术路线。  
> **AI 任务**：润色措辞、生成问题、准备资料，绝不替代社交互动。

---

## 任务 1：技术问题润色（AI 执行）

**输入**：你的 raw 问题，如 "mcp 的 roots 怎么限制 AI 访问范围"

**AI 输出**：知乎版 / Twitter 版 / Discord 版

**示例（知乎版）**：
> 标题：MCP 的 Roots 机制如何限制 AI 的文件系统访问范围？
> 正文：我正在设计一个 MCP Server，需要确保 AI 只能访问用户指定的目录。MCP 的 Roots 规范说 Client 可以声明允许访问的资源，但我对 Server 端的实现细节有些困惑：
> 1. Roots 是静态声明还是可以动态更新？
> 2. Server 应该在哪个层级做权限检查（解析层还是业务层）？
> 3. 是否有官方推荐的 Roots 验证实现？
> 感谢指点！

**你必须做**：确认润色后仍表达你的真实问题，自己发帖。

---

## 任务 2：冷消息起草（AI 执行，你个性化）

**输入**：你想联系一位在 MCP 领域活跃的大佬（如 Anthropic 的 MCP 团队开发者、或 Cursor 的 MCP 集成负责人）

**AI 输出**：礼貌模板（150 字内，展示你做过的功课）

**示例**：
> 您好 [名字]，
> 
> 我是 [你的名字]，正在研究 MCP 协议在游戏开发中的应用。我搭建了一个连接 Unreal Engine 的 MCP Server，实现了场景查询和蓝图修改工具。
> 
> 想请教您关于 MCP 的 Roots 安全模型：在多人协作场景下，如何设计更细粒度的权限控制？不知道您是否有 15 分钟时间交流？
> 
> 我的项目仓库：[GitHub 链接]
> 
> 期待您的回复，谢谢！
> [你的名字]

**你必须做**：添加具体细节（引用对方的博客/论文/演讲），自己发送。

---

## 任务 3：开源贡献（AI 执行）

**AI 建议**：匹配你的 MCP 技能到开源项目

| 项目 | 匹配度 | 建议贡献方向 |
|------|--------|-------------|
| [anthropics/anthropic-mcp](https://github.com/anthropics) | 高 | 添加新的 MCP Server 示例（UE 方向） |
| [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol) | 高 | 修复 bug 或添加文档 |
| [Cursor](https://cursor.com) 社区 | 中 | 分享自定义 MCP Tool 配置 |
| [Unreal Engine GitHub](https://github.com/EpicGames) | 中 | 反馈 Unreal MCP 的 Issue/PR |

**你必须做**：自己找 issue、读代码、写修复、提 PR。

---

## 完成检查清单

- [ ] 至少发了 1 个技术问题（关于 MCP 协议或安全模型）
- [ ] 至少与 1 位行业人士交流（MCP 社区或 AI 工具开发者）
- [ ] 至少给 1 个开源项目提了 Issue/PR/Comment（MCP SDK 或示例）
- [ ] 交流收获已整理到 Obsidian 职业复盘日志
- [ ] 技术雷达已更新（如有新的 MCP 工具或框架发现）

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2-3 小时（参加活动 + 社交 + 整理）*  
*产出：N 个新联系 + 1 次开源贡献 + 技术路线验证*
