# AI Agent 编码开发 Routine 体系

> **定位**：本目录是 GameDevVault 的 AI Agent 编码开发 Routine 分支，专注于 Kimi Work / Daimon Agent 的日常维护、技能开发、工具集成与子智能体编排的周期性工作流。
> 
> **与主 Routine 的关系**：主 Routine（01-07）聚焦图形引擎技术成长；本 AI Routine 聚焦智能体本身的能力建设与运维。

---

## 目录结构速览

| 编号 | 目录 | 说明 |
|------|------|------|
| `00` | `AI-Agent-Routine-Overview.md` | 本文件，总览与索引 |
| `10` | `Daily-Routines/` | 每日智能体运维任务 |
| `20` | `Weekly-Routines/` | 每周深度维护任务 |
| `30` | `Monthly-Routines/` | 每月能力评估与规划 |
| `40` | `Agent-Coding-Tasks/` | 具体编码开发任务池 |
| `50` | `Knowledge-Management/` | 知识库管理与 Prompt 工程 |
| `60` | `Templates/` | 可复用的开发模板 |
| `70` | `References/` | 工具注册表与参考架构 |
| `80` | `Experiments/` | 实验性 Agent 项目沙盒 |

---

## 日常执行节奏

### 晨间启动 (2-5 min)
1. 打开 `10-Daily-Routines/Morning-Agent-Health-Check.md`
2. 检查昨日 Cron 执行状态与日志
3. 确认工具链可用性 (MCP / WebBridge / DataSource)

### 编码时段 (核心工作时间)
1. 从 `40-Agent-Coding-Tasks/` 选择当前 Sprint 任务
2. 使用 `60-Templates/` 规范开发流程
3. 记录问题到 `50-Knowledge-Management/Error-Pattern-Library.md`

### 晚间收尾 (5-10 min)
1. 执行 `10-Daily-Routines/Agent-Log-Review.md`
2. 更新今日 `Memory/Vault` 记忆
3. 标记完成的任务，移动到下一天的待办

---

## 核心原则

1. **Agent-First**：所有工具、技能、模板优先服务于 Agent 自身的能力进化
2. **Routine-First**：像编译引擎一样编译 Routine，固定节奏 > 随机灵感
3. **Evidence-Based**：所有诊断、评估、改进必须有日志/数据支撑
4. **Composable**：技能、工具、子智能体必须可组合、可复用

---

## 快速入口

- [今日待办 → 10-Daily-Routines/Today-TODO.md](Today-TODO.md)
- [本周 Sprint → 20-Weekly-Routines/Current-Sprint.md](Current-Sprint.md)
- [开发任务池 → 40-Agent-Coding-Tasks/Task-Backlog.md](Task-Backlog.md)
- [技能模板 → 60-Templates/New-Skill-Template.md](New-Skill-Template.md)
- [MCP 注册表 → 70-References/MCP-Server-Registry.md](MCP-Server-Registry.md)
