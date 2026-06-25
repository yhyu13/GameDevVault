---
tags: [routine/AI-tasks, topic/UnrealMCP, day/Monday]
aliases: []
---

# 周一：AI 任务清单 — Unreal MCP 前沿技术输入

> **人类目标**：理解 Model Context Protocol (MCP) 标准，精读 Unreal MCP 实现，掌握 AI 助手与引擎交互的协议层。  
> **AI 任务**：提供脚手架、解释协议、生成问题，绝不替读文档。

---

## 任务 1：MCP 协议预读引导（AI 执行）

**输入**：Anthropic MCP 规范文档 + Unreal MCP `.uplugin` 描述

**AI 输出**：
1. 一段 **150 字摘要**：MCP 是 AI 助手与外部工具之间的 "USB-C" 标准，通过 JSON-RPC 交换结构化请求/响应，让 AI 能查询文件系统、执行命令、操作编辑器
2. **3 个引导问题**：
   - Q1: MCP 的 Tool Schema 如何定义？与 OpenAPI 规范有何异同？
   - Q2: MCP Server 与 Client 之间的 JSON-RPC 消息流是怎样的？（初始化 → 工具发现 → 调用 → 结果）
   - Q3: Unreal MCP 如何暴露引擎内部（资产、场景、蓝图）为 MCP Tools？
3. **重点章节标记**：先读 MCP Core Concepts（Resources/Tools/Prompts），再读 JSON-RPC Transport，最后读 Unreal MCP 的 ToolsetRegistry 集成

**交付物**：`MCP-Reading-Guide.md`

---

## 任务 2：JSON-RPC 消息流解释（AI 执行，你验证）

**输入**：MCP 规范中的生命周期示例

**AI 输出**：
1. 完整的握手流程（initialize → initialized → tools/list → tools/call）
2. 每个消息的结构（jsonrpc, id, method, params）
3. 错误处理模型（-32700 Parse Error / -32600 Invalid Request / -32601 Method Not Found）

**你必须做**：用 `curl` 或 Python `requests` 手动发送 JSON-RPC 消息到一个小型 MCP Server（如官方示例），观察响应。

**示例实验**：
```bash
# 向一个 MCP Server 发送 tools/list 请求
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

---

## 任务 3：面试谈资生成（AI 执行，你 rehearse）

**AI 输出**：
1. **30 秒版本**：MCP 是 AI 与工具之间的开放标准，Unreal MCP 让 AI 助手能直接查询场景、修改蓝图、启动构建。我在学习它的 Server 架构和自定义 Tool 开发。
2. **2 分钟版本**：背景（AI 助手需要工具）→ MCP 协议核心（JSON-RPC + Tool Schema）→ Unreal MCP 实现（6 个模块：Runtime/Engine/Editor/Tests）→ 使用场景（场景查询、蓝图自动化、资产检查）→ 局限与安全问题
3. **3 个追问**：
   - "MCP 与 VS Code 的 LSP 或 Copilot 的 Function Calling 有什么区别？"
   - "Unreal MCP 的权限模型如何防止 AI 误删资产？"
   - "MCP 的 Context 窗口如何管理？长场景描述会溢出吗？"

**你必须做**：rehearse aloud。

---

## 任务 4：Unreal MCP 源码地图（AI 执行，你验证）

**输入**："Unreal MCP 的 6 个模块职责是什么？从 Editor 入口到 Tool 执行的调用链？"

**AI 输出**：
1. **ModelContextProtocol** (Runtime) — 核心协议解析器
2. **ModelContextProtocolEngine** (Runtime) — 引擎层工具注册
3. **ModelContextProtocolEditor** (Editor) — 编辑器工具暴露（资产浏览器、场景大纲、蓝图编辑器）
4. **Tests** 系列 — 单元测试和集成测试

**调用链**：
```
Editor AI Assistant
  → MCP Client (外部 AI)
  → JSON-RPC over stdio/HTTP
  → ModelContextProtocol (解析)
  → ToolsetRegistry (路由)
  → ModelContextProtocolEditor (执行编辑器命令)
  → UE Editor API
  → 结果回传
```

**你必须做**：在 UE58 源码中打开这些模块，找到 `HandleInitialize`、`HandleToolsList`、`HandleToolCall` 等关键函数。

---

## 今日 AI 禁区

- ❌ 让 AI 替你读 MCP 规范而不自己看消息格式
- ❌ 让 AI 替写笔记（MCP 是协议，必须自己理解每条消息的语义）
- ❌ 让 AI 生成代码路径而不验证（UE 源码可能已更新）
- ❌ 让 AI 替你准备面试回答而不理解协议本质

---

## 完成检查清单

- [ ] MCP 阅读指南已生成并打印
- [ ] JSON-RPC 消息流已手动验证（用 curl 或 Python）
- [ ] 面试谈资已 rehearse aloud
- [ ] Unreal MCP 源码路径已验证（找到 Initialize/ToolList/ToolCall 函数）
- [ ] 所有内容已写入 Obsidian 笔记（你写的，不是 AI 写的）

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2 小时*  
*产出：1 篇协议笔记 + 1 篇源码分析 + 面试谈资 ready*
