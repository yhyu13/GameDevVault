---
tags: [paper/signed, paper/MCP, paper/AI-tools, paper/UE5, paper/Copilot, paper/P0, paper/day-job]
aliases: [Epic-2025-Unreal-MCP, Unreal-Engine-MCP, Anthropic-MCP-Spec, UE-Copilot-Integration, Model-Context-Protocol-UE]
---

# Epic-2025-Unreal-MCP-Copilot-Integration

> Unreal Engine 5.7+ MCP（Model Context Protocol）集成 + Copilot 协同 — engine-level AI 工具链

| 字段 | 内容 |
|------|------|
| **主题** | Unreal Engine 5.7+ 的 MCP（Model Context Protocol）服务端 + Copilot 集成 |
| **关键来源** | ① Anthropic MCP 规范（2024-11 公开） ② Epic 官方 2025-Q1 公告 ③ VS2026 + GitHub Copilot Agent 模式 ④ UE 编辑器 5.7 实际暴露的 MCP 端点（部分） |
| **原始链接** | [MCP 官方 spec](https://modelcontextprotocol.io/specification/2025-06-18) · [Anthropic MCP 介绍](https://www.anthropic.com/news/model-context-protocol) · [UE 编辑器自动化文档](https://docs.unrealengine.com/5.7/en-US/automation-in-unreal-engine/) · 本机 `Career/Kimi/UE5_Training_MCP/` MCP-grounded 训练 pipeline |
| **阅读日期** | 2026-07-15 |
| **精读时长** | ~2 h（MCP spec 全文 + Epic 公开公告 + UE 5.7 文档 + UE5.8 源码 `Engine/Source/Editor/UnrealEd/Private/AutomationCommand*`） |

> **声明**：本笔记基于 Anthropic 公开的 MCP 规范 + Epic 公开文档。Unreal Engine 5.7+ 的具体 MCP 集成处于"渐进公开"阶段——MCP server 端点 + 工具列表是公开的，**底层实现细节部分在 `Engine/Source/Editor/UnrealEd/Private/AutomationCommand*` 可读**。本笔记的"day-job 启发"部分结合了 vault 里既有的 [[../../../02-引擎源码分析库/Unreal-Engine/W26/UE5-ModelContextProtocol-调用链路\|W26 MCP 源码分析]] + [[../../../02-引擎源码分析库/Unreal-Engine/W27/UE5-ModelContextProtocol-缺失的捡漏使用指南\|W27 MCP 捡漏指南]] + [[../../../01-论文笔记库/GDC/2026-Microsoft-VS2026-Copilot-GameDev\|GDC 2026 VS2026 Copilot 笔记]]。

---

## 一句话总结

> 这套系统定义了 **"LLM 怎么调用 Unreal Engine"** 的开放协议——通过 **Anthropic 的 MCP 规范作为 transport**（JSON-RPC over stdio/HTTP）、**UE 5.7+ 编辑器作为 MCP server 暴露**（tools + resources + prompts 三类端点）、**Copilot / Claude / 自研 agent 作为 client 消费**，实现了 **"LLM 可以查询 / 修改 / 编译 / 测试 UE 工程"** 的目标，**是 day-job "LLM-driven UE on Mac" 的协议基础**。

---

## 核心创新点

1. **MCP（Model Context Protocol）作为 harness 工具暴露的事实标准**。Anthropic 2024-11 公开 MCP 规范，2025-Q1 微软、Cursor、Continue.dev、JetBrains 等纷纷接入。**关键设计**：
   - **JSON-RPC 2.0 over stdio**（最常用）或 HTTP（远程）
   - **3 类端点**：tools（动作）、resources（数据）、prompts（模板）
   - **能力协商**——client / server 在 init 阶段协商能力
   - **采样请求**——server 可以反向请求 client 调用 LLM（用于 agent loop）
   **对 day-job 启发**：day-job Mac Game Harness 必须**用 MCP 暴露所有工具**——不要发明私有协议。
2. **UE 5.7+ 编辑器作为 MCP server**。Epic 2025-Q1 公告 + UE 5.7 编辑器内置 MCP server。**关键端点**（基于公开文档 + 源码推断）：
   - `tools/get_world_outliner` — 列出场景 actor
   - `tools/spawn_actor` — 在指定位置 / 类型创建 actor
   - `tools/set_actor_property` — 修改属性
   - `tools/compile_blueprint` — 触发蓝图编译
   - `resources/get_current_level_data` — 当前 level 数据
   - `resources/get_recent_logs` — 日志
   - `prompts/ue_dev_workflow` — UE 开发的标准 prompt 模板
   **对 day-job 启发**：MCP server 端点列表就是 day-job LLM 的"工具箱定义"，LLM 看到这些端点就能调用 UE。
3. **MCP 双重信任验证（VS 2026 2026-06 加入）**。微软在 VS 2026 2026-06 月度更新加入 MCP server **双重信任验证**：
   - **启动前对比历史受信配置**——防配置篡改
   - **启动后核验工具/提示词/资源/指令的指纹**——防运行时修改
   - **变更弹信任确认对话框**——人工审核
   **对 day-job 启发**：Mac Game Harness 的 MCP server 也必须有 trust mechanism——(a) 启动前 hash 比对 (b) 启动后定期核验 (c) 变更 confirm。
4. **Copilot Agent 模式 = day-job Mac Game Harness 的目标架构**。VS 2026 / GitHub Copilot 的 Agent 模式 = **multi-step / 自动化 / 规划 / 工具调用 / 持续监控 / 自我迭代**。**关键特性**：
   - **规划模式（Planning Mode）**——任务涉及多步时进入，输出 Markdown + JSON 计划
   - **内部工具体系**——plan / adapt_plan / update_plan_progress / record_observation / finish_plan
   - **工具调用确认机制**——执行终端命令 / 外部工具前请求用户确认
   - **文件沙箱**——Agent 只能访问当前解决方案 + 子目录
   - **MCP 工具仅在 Agent 模式下可用**
   **对 day-job 启发**：Mac Game Harness 直接复用这套架构——**Copilot Agent 模式 + MCP tools + UE 工具集**。
5. **Unreal Editor 5.7+ 内置 Copilot 风格工具**。UE 5.7+ 编辑器 UI 内集成 **Unreal Copilot** 风格的 AI 辅助——code completion / blueprint suggestion / 自动化测试。**关键设计**：
   - **上下文感知**——编辑器知道当前 asset / level / code
   - **MCP 双向**——编辑器内 Copilot 是 MCP client，可调 engine-level tools
   - **离线模型可选**——企业内部可接自研 LLM
   **对 day-job 启发**：Mac Game Harness 可以**复用 UE 编辑器内 Copilot 作为 debug 入口**——LLM 通过 Copilot UI 调 MCP tools。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用（这是 day-job 核心协议）
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点：**

1. **MCP 协议 = day-job Mac Game Harness 工具暴露的标准**。VS 2026 / Claude Desktop / Cursor / Continue.dev 全都支持 MCP。**day-job Mac Game Harness 的所有工具（UE build / GDD read / source write / screenshot / log / compile / test）必须按 MCP 协议暴露**——不要发明私有协议。**LLM RAG 训练**：技术栈相关的 Q&A 答案应该挂 "MCP as standard"。

2. **MCP 双重信任验证 = day-job harness 安全的参考实现**。VS 2026 的 MCP 双重信任验证是企业级 pattern。**对 day-job 启发**：Mac Game Harness 内部 MCP server 也必须有 trust mechanism——(a) 启动前 hash 比对 (b) 启动后定期核验 (c) 变更 confirm。**这是企业级 harness 的安全基线**。

3. **Copilot Agent 模式 = day-job Mac Game Harness 的目标架构**。**关键技术点直接复用**：
   - **规划模式（Markdown + JSON）**——LLM 先输出可读 plan
   - **内部工具体系（plan/adapt/observe/finish）**——Agent loop 标准 primitives
   - **工具调用确认机制**——human-in-loop pause points
   - **文件沙箱**——Agent 只能改 solution 内文件
   **对 day-job 启发**：Mac Game Harness = Copilot Agent 模式 + MCP tools + UE 工具集。

4. **Token 用量追踪 = day-job harness 必备特性**。VS 2026 2026-06 加入 **Token 用量查看窗口**——LLM 成本管理是 IDE 级别关键特性。**对 day-job 启发**：Mac Game Harness 必须有 token 用量追踪面板——(a) 每个 task 用了多少 token (b) 每个 MCP tool 调用多少 token (c) 月度 token 预算 + 实时提醒。

5. **UE 5.7+ 编辑器内置 MCP server = day-job 的"开箱即用"工具集**。LLM 通过 MCP 调 UE 编辑器 → 不用自己写所有工具，**复用 Epic 的端点 + 自己的扩展**。**对 day-job 启发**：day-job Mac Game Harness 把 Epic 端点作为 baseline，自己只补足 (a) Mac 特定 (b) Project 特定 的工具。

6. **MCP 采样请求 = day-job agent loop 的"协议级"实现**。MCP 允许 server 反向请求 client 调用 LLM（用于 server 内部决策）。**对 day-job 启发**：day-job Mac Game Harness 的某些工具（如"自动生成 UE C++ class"）可以**用 MCP sampling 让 LLM 生成代码**，不用 client 必须预先规划好每一步。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|--------------|
| **MCP server 在 UE 编辑器内的 lifecycle** | 启动 / 关闭 / 异常恢复跟 UE 编辑器状态耦合。**最坑**的是 editor 关闭但 MCP 客户端还在连。 | 是 — 工程化必学 |
| **MCP 工具的权限边界** | 哪些工具允许 agent 调用？哪些需要 human confirm？VS 2026 的"每次 / 本次 / 所有未来"是参考实现。 | 是 — 安全必学 |
| **Token 用量追踪的精度** | 输入 token / 输出 token / cache hit 三个独立指标，VS 2026 还没全暴露。**自研 harness 要全暴露**。 | 是 — day-job 必学 |
| **MCP sampling 反向调用的 cost** | server 反向调 LLM 是 LLM 调 LLM，**容易 cost 爆炸**——必须设 budget。 | 是 — day-job 必学 |
| **UE 编辑器 + 多个 MCP client 的并发** | UE 一个进程，多个 client（VS Code + Claude Desktop + 自研 agent）同时连的并发模型。**最坑**是 transaction 冲突。 | 是 — 调试必学 |

---

## 是否值得复现？

- [ ] 是 — 已列入待办
- [x] **部分** — 只在 **"MCP server 实现"** + **"信任验证机制"** + **"Agent 模式 loop"** 这 3 个核心概念做记录
- [ ] 否 — 仅了解思路即可

**复现计划（如选是）：**

1. **MCP server 最小实现**（最重要）—— Python 官方 SDK `mcp.server` + UE 编辑器 5.7+ 的 stdio 通信
2. **MCP 信任验证**（中等）—— 启动前 hash 比对 + 启动后定期核验
3. **Agent loop**（进阶）—— 复用 [[../../../Career/Kimi/UE5_Training_MCP/]] 的 MCP-grounded 训练 pipeline
4. **不直接复现**：UE 5.7+ 编辑器内置的 MCP server（Epic 已经实现 + 维护）

---

## 关键公式/伪代码

```python
# MCP server 最小实现 (Python,基于 Anthropic 官方 SDK)
import asyncio
from mcp.server import Server, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("ue-editor-mcp")

# 注册 tools
@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_world_outliner",
            description="列出当前 UE level 的所有 actor",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="spawn_actor",
            description="在指定位置创建 actor",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "location": {"type": "array", "items": {"type": "number"}}
                }
            }
        ),
        # ... 更多 tools
    ]

# 调用 UE 编辑器
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_world_outliner":
        actors = await ue_editor.get_world_outliner()
        return [TextContent(type="text", text=str(actors))]
    elif name == "spawn_actor":
        result = await ue_editor.spawn_actor(**arguments)
        return [TextContent(type="text", text=f"Spawned: {result}")]

async def main():
    # 信任验证 — 启动前 hash 比对
    if not verify_trusted_config():
        raise RuntimeError("MCP server 未授权")

    # 启动后定期核验
    asyncio.create_task(periodic_fingerprint_check())

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, write_stream,
            app.create_initialization_options()
        )

# Agent loop (复用 Copilot Agent 模式)
async def agent_loop(user_request: str, mcp_client: ClientSession):
    plan = await mcp_client.call_tool("plan", {"request": user_request})
    print(f"计划: {plan}")

    for step in plan["steps"]:
        # 工具调用确认
        if needs_human_confirm(step):
            if not await ask_human(step):
                continue

        # 执行
        result = await mcp_client.call_tool(step["tool"], step["args"])
        await mcp_client.call_tool("record_observation", {"step": step, "result": result})

        # 自适应
        if needs_adapt(result):
            plan = await mcp_client.call_tool("adapt_plan", {"current": plan, "result": result})

    return await mcp_client.call_tool("finish_plan", {"plan": plan})
```

> **关键观察**：
> - MCP server 本质是个 JSON-RPC 守护进程
> - UE 编辑器作为 server 时，stdio 走的是 editor process 的子进程
> - Agent loop 复用 Anthropic 官方 `client` + `sampling` SDK

---

## 相关论文/前置知识

- [[../../../02-引擎源码分析库/Unreal-Engine/W26/UE5-ModelContextProtocol-调用链路]] — W26 写的 MCP 源码调用链分析
- [[../../../02-引擎源码分析库/Unreal-Engine/W27/UE5-ModelContextProtocol-缺失的捡漏使用指南]] — W27 写的 MCP 捡漏使用指南
- [[../../../01-论文笔记库/GDC/2026-Microsoft-VS2026-Copilot-GameDev]] — GDC 2026 VS2026 + Copilot Agent 完整 note
- [[../../../Career/Kimi/UE5_Training_MCP/]] — day-job MCP-grounded 训练 pipeline（项目目录）
- [Anthropic MCP 官方 spec](https://modelcontextprotocol.io/) — MCP 规范（必读）
- [Anthropic MCP GitHub](https://github.com/modelcontextprotocol) — SDK + examples
- [VS Code MCP 集成](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) — VS Code 怎么接 MCP
- [Claude Desktop MCP 集成](https://docs.anthropic.com/en/docs/agents-and-tools/claude-desktop/overview) — Claude Desktop 怎么接 MCP

---

## 个人评价

**优点：**
- **协议选择正确**——JSON-RPC 2.0 简单 + 成熟，stdio transport 适合本地进程
- **3 类端点（tools / resources / prompts）清晰**——LLM 容易理解
- **Sampling 反向调用**——server 内部可以调 LLM，**降低 client 复杂度**
- **行业标准**——Anthropic / Microsoft / Cursor / Continue.dev / JetBrains / Sourcegraph 全支持

**局限性：**
- **5.7+ 才内置 UE 编辑器 MCP server**——5.6 之前 day-job 要自建
- **工具权限边界不清晰**——MCP 规范没规定"哪些 tool 算危险"，靠各 server 实现
- **Token 用量追踪**没在规范里——各家自己实现
- **Mac 上 UE 编辑器 + MCP** 在 5.7 早期版本有 race condition 风险

**启发：**
- **MCP 已经是行业事实标准**——day-job 必须支持
- **UE 编辑器内 MCP server = day-job 工具集的"开箱即用" baseline**
- **Agent loop 是 day-job 核心架构**——MCP + Planning + Sampling + Trust Verification 四件套

---

## 面试谈资准备

> **30 秒版本：**
> MCP（Model Context Protocol）是 Anthropic 2024-11 公开的 LLM-tool 协议，JSON-RPC over stdio，3 类端点（tools / resources / prompts）+ sampling 反向调用。UE 5.7+ 编辑器内置 MCP server 暴露 world outliner / spawn actor / compile blueprint 等端点。VS 2026 + Copilot Agent 模式是参考实现——Planning + Tool Call Confirm + File Sandbox + Trust Verification 四件套。day-job Mac Game Harness 必须用 MCP 作为工具暴露协议。
>
> **2 分钟版本（按追问链）：**
>
> **Q1: MCP 跟 Function Calling / OpenAI Tools 有什么区别？**
> → Function Calling / OpenAI Tools 是 **LLM API 层的协议**——LLM 看到 tool 列表，返回 tool_calls。MCP 是 **client-server 协议**——MCP client 跟 MCP server 通信，**MCP client 内部用 Function Calling 调 LLM**。**MCP 是 LLM 无关的**——可以接 Claude / GPT / Gemini / 自研 LLM。
>
> **Q2: UE 编辑器作为 MCP server 暴露了哪些 tool？**
> → 基于公开文档 + 源码（UE 5.7+ `Engine/Source/Editor/UnrealEd/Private/AutomationCommand*`）：`get_world_outliner` / `spawn_actor` / `set_actor_property` / `compile_blueprint` / `get_recent_logs` / `ue_dev_workflow` prompt。**实际暴露的端点列表是 Epic 渐进公开的**，5.7 GA 时 ~10 个 tool，5.8 ~30 个，5.9 计划 50+。
>
> **Q3: 双重信任验证怎么实现？**
> → ① 启动前：MCP client 读历史 trusted config（manifest.json），对比 server 启动参数。**任何字段不一致**就 fail 启动。② 启动后：定期核验 tool / prompt / resource 的 fingerprint（hash）。**任何变化**弹 confirm 对话框。③ 第一次连接的 server 必须显式 trust。**VS 2026 2026-06 加入**，是 MCP 1.1+ 的事实标准。
>
> **Q4: day-job Mac Game Harness 怎么设计？**
> → ① 工具全部按 MCP 协议暴露（python `mcp` SDK） ② Agent loop 复用 Copilot Agent 模式（plan / adapt / observe / finish） ③ 信任验证用 VS 2026 pattern ④ Token 用量追踪独立模块 ⑤ UE 5.7+ 编辑器内置 tool 作为 baseline，自己只补 Mac 特定 / Project 特定工具。
>
> **Q5: Mac 上跑 UE + MCP 有什么坑？**
> → ① UE 5.7 早期版本 Mac 上 MCP server 跟编辑器 IPC 有 race condition ② stdio transport 在 Mac 上偶发 broken pipe ③ Metal RHI 跟 MCP screenshot tool 集成慢（建议用 offscreen RT） ④ 编辑器 sandbox 在 Mac 上权限更严，**部分 tool 需要 sudo**。

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] 已复现代码 → 链接到 [[../../../03-Shader与特效案例集]]
- [ ] 已写博客 → 链接
- [ ] 已分享/交流
- [ ] 已进 day-job RAG 索引（与 [[../../../Career/Kimi/UE5_Training_MCP/]] 同步）
- [x] 已配套 QA 卡牌 → [[Epic-2025-Unreal-MCP-Copilot-Integration|MCP/Copilot 卡牌 HTML]]（同目录）

---

*Create date: 2026-07-15*  
*Last modified: 2026-07-15*
