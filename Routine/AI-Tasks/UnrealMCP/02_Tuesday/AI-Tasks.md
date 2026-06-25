---
tags: [routine/AI-tasks, topic/UnrealMCP, day/Tuesday]
aliases: []
---

# 周二：AI 任务清单 — Unreal MCP 专项技能突破

> **人类目标**：通过协议实现和 Tool Schema 设计，内化 MCP 的核心机制。  
> **AI 任务**：生成练习题、解释协议、review 代码、提供直觉，绝不替写核心实现。

---

## 任务 1：MCP 协议练习题生成（AI 执行）

**输入**："给我生成 5 道关于 MCP 协议的练习题，涵盖：JSON-RPC 2.0 消息格式、Tool Schema 定义、生命周期状态机、错误码、Context 管理"

**AI 输出**：5 道练习题

**示例题目**：
> **Q1 (Easy)**：一个 MCP Client 向 Server 发送了 `{"jsonrpc":"2.0","id":1,"method":"tools/list"}`。Server 返回了 3 个工具：`get_scene_objects`、`modify_blueprint`、`build_project`。请写出 Client 调用 `get_scene_objects` 并传入参数 `{"type": "StaticMeshActor"}` 的完整 JSON-RPC 请求。

**你必须做**：在纸上或代码中完成所有题目，再核对答案。

---

## 任务 2：MCP Server 脚手架（AI 生成，你填充）

**输入**："我想写一个最小可运行的 MCP Server（Python），只暴露一个 `get_ue_version` 工具。生成脚手架"

**AI 输出**：
```python
#!/usr/bin/env python3
"""Minimal MCP Server for Unreal Engine"""

import json
import sys

class UnrealMCPServer:
    def __init__(self):
        self.tools = {
            "get_ue_version": {
                "description": "Get the current Unreal Engine version",
                "inputSchema": {"type": "object", "properties": {}}
            }
        }
    
    def handle_initialize(self, params):
        # TODO(HUMAN): 实现 initialize 响应
        # 返回 protocolVersion, capabilities, serverInfo
        pass
    
    def handle_tools_list(self, params):
        # TODO(HUMAN): 返回工具列表
        pass
    
    def handle_tool_call(self, tool_name, tool_args):
        # TODO(HUMAN): 根据 tool_name 分发到对应处理器
        # get_ue_version -> 返回 "5.8"
        pass
    
    def run(self):
        # TODO(HUMAN): 实现 stdio 循环读取 JSON-RPC 请求
        # 解析 -> 路由 -> 处理 -> 响应
        pass

if __name__ == "__main__":
    server = UnrealMCPServer()
    server.run()
```

**你必须做**：填充所有 `TODO(HUMAN)`，运行并用 `echo` 发送 JSON-RPC 消息测试。

**测试命令**：
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python my_mcp_server.py
```

---

## 任务 3：你的 MCP Server 代码 Review（AI 执行）

**AI 检查清单**：
- [ ] 是否正确处理了 JSON-RPC 的 `id` 字段（请求必须带回相同的 id）
- [ ] 是否实现了完整的生命周期（initialize → initialized → tools/list → tools/call）
- [ ] 错误响应是否符合 JSON-RPC 规范（error.code, error.message, error.data）
- [ ] 是否处理了并发请求（id 不重复，响应顺序可能乱序）
- [ ] 是否实现了 `notifications/initialized`（Server 能力变更时通知 Client）
- [ ] 是否防御了非法 JSON 输入（try/except JSONDecodeError）

**AI 输出**：发现的 bug 列表 + 修复建议（逐行）

**你必须做**：理解每个 bug 的根因，手动修复。

---

## 任务 4：概念直觉（AI 解释，你内化）

| 概念 | AI 解释类比 |
|------|------------|
| MCP 协议 | "就像餐厅点餐系统。你（AI）是顾客，MCP Server 是厨房。菜单（Tool Schema）告诉你有什么菜，点菜（JSON-RPC 请求）时告诉厨房你要什么，厨房（Server）做好后送回（响应）。不同的餐厅（UE、VS Code、文件系统）有不同的菜单。" |
| Tool Schema | "就像函数签名。Schema 告诉 AI：这个工具叫什么，需要什么参数（类型、必填/可选），返回什么。AI 看了 Schema 就知道怎么 '调用' 这个工具，不需要提前知道具体实现。" |
| Context 管理 | "就像你和朋友的聊天记录。MCP 的 Context 是 AI 与 Server 之间的对话历史。如果聊天记录太长，需要 '总结'（压缩）或 '分页'（分段发送），否则 token 会溢出。" |

**你必须做**：用你自己的话向一个假想的初级游戏开发者解释这些概念。

---

## 今日 AI 禁区

- ❌ 让 AI 写完整 MCP Server 实现
- ❌ 让 AI 直接给协议题答案
- ❌ 不做费曼输出
- ❌ 直接应用修复不理解根因

---

## 完成检查清单

- [ ] 5 道协议题已完成并核对
- [ ] MCP Server 核心逻辑已填充
- [ ] AI code review 的 bug 已理解并手动修复
- [ ] 3 个核心概念已用自己的话解释
- [ ] 代码和笔记已写入 Obsidian

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 2.5 小时*  
*产出：5 道协议练习 + 1 个 MCP Server + 1 次 Code Review*
