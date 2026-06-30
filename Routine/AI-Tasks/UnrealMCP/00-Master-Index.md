---
tags: [routine/master-index, topic/UnrealMCP, system/reference]
aliases: [UnrealMCP-AI-Master]
---

# Unreal MCP 主题 — AI 任务总览

> 这是 Unreal MCP（Model Context Protocol）学习周期的「AI 任务控制塔」。  
> **核心原则**：AI 只做脚手架，你来做硬工作。

---

## 快速导航

| 日期 | 主题 | AI 任务文件 | 人类核心任务 |
|------|------|------------|-------------|
| [[周一]] | 前沿技术输入 | [[01_Monday/AI-Tasks]] | 精读 MCP 规范 + 源码追踪 |
| [[周二]] | 专项技能突破 | [[02_Tuesday/AI-Tasks]] | JSON-RPC 协议 + Server 实现 |
| [[周三]] | 强制休息/游玩 | [[03_Wednesday/AI-Tasks]] | 体验 AI 助手 MCP 交互模式 |
| [[周四]] | 工程化与工具链 | [[04_Thursday/AI-Tasks]] | 安全模型 + 自定义工具开发 |
| [[周五]] | 轻量复盘 | [[05_Friday/AI-Tasks]] | 测验 + 整理 + 规划 |
| [[周末]] | 项目实战 | [[06_Weekend/AI-Tasks]] | 自定义 MCP Toolset + 博客 |
| [[周日]] | 项目收尾 | [[07_Sunday/AI-Tasks]] | 集成测试 + 复盘 |
| [[每周]] | 外部接触 | [[08_Weekly/AI-Tasks]] | MCP 社区社交 + 开源贡献 |

---

## Unreal MCP 是什么

Unreal MCP 是 UE5.8 实验性功能，将 Anthropic 的 **Model Context Protocol (MCP)** 引入 Unreal Engine：

- **MCP 协议**：AI 助手与外部工具之间的开放标准，通过 JSON-RPC 交换结构化消息
- **Unreal MCP**：在 UE 编辑器内实现 MCP Server，暴露引擎内部为 AI 可调用的 Tools
- **核心模块**：
  - `ModelContextProtocol` — 协议解析器
  - `ModelContextProtocolEngine` — 引擎层工具注册
  - `ModelContextProtocolEditor` — 编辑器工具暴露（资产、场景、蓝图）
  - `ModelContextProtocolTests` — 测试套件
- **使用场景**：
  - AI 查询场景对象列表
  - AI 修改蓝图属性
  - AI 启动项目构建
  - AI 检查资产命名规范
  - AI 生成关卡报告

---

## 与现有 7 个主题的关系

```
        ┌─────────────────────────────────────┐
        │         Unreal MCP (#7)               │
        │    AI 工具链 / 编辑器自动化           │
        │    (横切关注点——增强所有主题)         │
        └─────────────────────────────────────┘
                      │
    ┌─────────┬───────┼───────┬─────────┐
    ▼         ▼       ▼       ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ Lumen  │ │ Nanite │ │  VGM   │ │  VSM   │ │ Chaos  │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
┌────────────────────┐
│   WaterPlugins     │
└────────────────────┘
```

MCP 是 **增强器** 而非 **竞争者**：
- 学习 MCP 后，你可以为 **Lumen** 写调试工具、为 **Nanite** 写分析工具
- MCP 让 AI 成为你的 **开发助手**，加速所有其他主题的学习

---

## 相关参考

- [[../References/AI-Augmentation-Reference]] — AI 辅助学习完整参考手册
- [[../UE58-Topic-Exploration-Report]] — UE58 主题探索完整报告（优先级评分）
- [[../01-AI-GameDev-Resources/00-AI-GameDev-Resource-Index]] — AI 游戏开发资源总索引（2026-06 刷新）
- [[../Lumen/00-Master-Index]] — 可用 MCP 查询 Lumen 场景
- [[../../01-论文笔记库]] — MCP 规范笔记
- [[../../02-引擎源码分析库]] — Unreal MCP 源码分析
- [[../../99-Templates/论文笔记]] — 论文/规范笔记模板

---

## 每周更新日志

| 周 | 主题 | 状态 |
|----|------|------|
| W1 | MCP 基础：协议 + JSON-RPC + Tool Schema | 🔄 进行中 |
| W2 | Unreal MCP 源码：Server 架构 + Editor 集成 | ☐ 待开始 |
| W3 | 自定义工具：5-10 个 MCP Tool 开发 | ☐ 待开始 |
| W4 | 集成实战：mini-MCP Toolset 完整版 + 安全模型 | ☐ 待开始 |

---

## 推荐学习路径

**如果你同时学多个主题**：
- **并行**：MCP 作为 "副线"，每天 30 分钟学习协议，周末集中开发工具
- **串行**：先完成一个渲染主题（如 Lumen），然后用 MCP 为其写分析工具

**MCP 的特殊性**：
- 不像渲染/物理需要大量数学推导
- 更像 "软件工程 + 协议设计 + 安全模型"
- 学习曲线：中等（比 Lumen 容易，比 Shader 更概念化）

---

*This is a living document. Update it as the Unreal MCP topic progresses.*
