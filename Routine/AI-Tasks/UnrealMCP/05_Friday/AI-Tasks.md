---
tags: [routine/AI-tasks, topic/UnrealMCP, day/Friday]
aliases: []
---

# 周五：AI 任务清单 — Unreal MCP 轻量复盘与整理

> **人类目标**：整理本周 MCP 学习笔记，更新知识库，规划下周。  
> **AI 任务**：生成测验、建议链接、总结数据，绝不替你思考。

---

## 任务 1：MCP 协议知识测验生成（AI 执行）

**AI 输出**：结构化测验

```markdown
## Q1 (TF)
MCP 的 Tool Schema 使用 OpenAPI 3.0 规范定义。
Answer: False
Explanation: MCP 使用 JSON Schema 定义 Tool Schema，与 OpenAPI 类似但独立标准。MCP 的 Schema 更简洁，专注于工具参数描述。

## Q2 (SC)
MCP Server 向 Client 暴露工具列表时，使用什么方法？
Options:
- A. tools/discover
- B. tools/list
- C. capabilities/tools
- D. get_available_tools
Answer: B

## Q3 (MC)
以下哪些是 MCP 协议的核心概念？
Options:
- A. Resources（AI 可读取的数据源）
- B. Tools（AI 可调用的函数）
- C. Prompts（预定义的提示模板）
- D. Functions（OpenAI 风格函数调用）
- E. Sampling（AI 请求 Server 采样内容）
Answer: A, B, C, E

## Q4 (FB)
MCP 使用 ______ 作为传输协议，消息格式遵循 ______ 规范。Unreal MCP 额外支持通过 ______ 与编辑器交互。
Answer: JSON-RPC, JSON-RPC 2.0, Editor Scripting API / PythonScriptPlugin
```

**然后**：使用 `quiz-html-generator` 转 HTML。

**你必须做**：完成测验，复习错题。

---

## 任务 2：笔记链接建议（AI 执行，你确认）

**AI 建议**：
- [[MCP-协议笔记]] → [[Python-工具链]]：MCP Server 通常用 Python 实现
- [[MCP-JSONRPC]] → [[C++-网络编程]]：JSON-RPC 的 C++ 实现与网络传输
- [[MCP-安全模型]] → [[04-性能优化备忘录]]：安全边界与性能权衡
- [[MCP-自定义工具]] → [[02-引擎源码分析库]]：暴露编辑器内部需要理解源码
- [[MCP-UE集成]] → [[PythonScriptPlugin]]：Python 脚本与 MCP 的协同

**你必须做**：检查合理性，手动添加 `[[链接]]`。

---

## 任务 3：周数据总结 + 下周规划（AI 执行，你补充）

**AI 建议下周重点**：
- 周一：Unreal MCP 源码深入（ToolsetRegistry 路由机制）
- 周二：写一个自定义 MCP Tool（如 "查询场景中所有 Nanite Mesh"）
- 周三：观察现有 AI 工具（Cursor、Claude Code）的 MCP 使用模式
- 周四：MCP Server 性能优化（异步、并发、缓存）
- 周末：mini-MCP 工具集（5-10 个自定义工具 + 完整 Server）

**你必须做**：根据实际工作负荷调整。

---

## 完成检查清单

- [ ] MCP 知识测验已完成（得分 ≥80）
- [ ] 错题已复习，薄弱点已标记
- [ ] 笔记双向链接已手动添加（至少 3 条）
- [ ] 周数据总结已补充主观信息
- [ ] 下周计划已调整并写入 Obsidian 周模板

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 1 小时*
