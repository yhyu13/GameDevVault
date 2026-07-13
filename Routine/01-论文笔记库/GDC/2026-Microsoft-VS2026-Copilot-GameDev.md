---
tags: [paper/signed, paper/GDC-talk, paper/GDC-2026, paper/AI-pipeline, paper/已应用到工作]
aliases: [Microsoft-VS2026-Copilot-GameDev-GDC2026, VS2026-AI-Native-IDE, Copilot-Agent-Mode-MCP, Microsoft-Windows-GameDev-GDC2026]
---

# Microsoft — Visual Studio 2026 + GitHub Copilot Agent Mode + MCP: AI-Native IDE for Game Development (GDC 2026)

| 字段 | 内容 |
|------|------|
| **Talk 标题** | Windows Game Development with Visual Studio 2026 / AI-Native IDE for C++ & C# |
| **讲者** | Microsoft Visual Studio / GitHub Copilot 团队 (GDC 2026 Festival of Gaming 场次) |
| **场次** | GDC 2026 — Windows / Microsoft Tools 赛道 (与 cppblog 2026-03 微软场次对齐) |
| **日期** | 2026-03-13 (Moscone Center, San Francisco) |
| **Track** | Developer Tools / AI-Native IDE / MCP |
| **同源 short note** | (待 cron curator 落 `GDC/Minimax/2026/`) — 本文是其深度展开 |
| **阅读日期** | 2026-07-14 |
| **精读时长** | ~45 min |

---

## 一句话总结

> 微软在 GDC 2026 上把 **Visual Studio 2026（2025-11 GA，2026-06 月度更新）** 定位为 **"全球首款 AI-Native IDE"**——**GitHub Copilot 不再是侧边栏玩具，而是从编码→调试→性能分析→代码评审全流程的"智能副驾驶"**，配套 **C# / C++ Agent 用于调试/性能分析/代码现代化 + 全面 MCP（Model Context Protocol）服务器支持 + 双重信任验证机制 + Token 用量追踪**。**对 day-job 的启发**：**MCP 已经成为 IDE 集成的开放标准**——**day-job Mac Game Harness 必须用 MCP 作为 harness 工具的暴露协议**，**不**要发明私有协议；**MCP 双重信任验证是 harness 安全的参考实现**；**VS 2026 的 Copilot Agent 模式是 harness 工程的工业级 pattern**。

---

## 核心创新点

1. **"AI-Native IDE"作为微软的正式定位**。微软明确把 **VS 2026 定位为 "AI-Native" / "the world's first smart IDE"**——**Copilot 不再是附加组件，是 IDE 的核心体验**。**关键判断**：**这是 IDE 范式从 "text editor + debugger" 到 "AI co-pilot + agent runner" 的转移**。**对 day-job 启发**：未来 12-24 个月，"AI-native harness" 是 LLM 工具集成的默认形态——**不是"在 IDE 外挂一个 LLM 工具"，是"IDE 内嵌 LLM + agent runtime"**。

2. **GitHub Copilot 深度集成 —— 不再是侧边栏**。VS 2026 的 Copilot **理解整个解决方案结构**（从项目文件、Git 仓库到所用工具链）+ **智能重构与测试生成**（自动识别冗余代码、推荐优化方案、一键生成单元测试）+ **函数解释与调试辅助**（自然语言解释复杂逻辑，预测潜在错误根源）+ **"Did You Mean?"功能**（拼错名称时主动提示）。**关键工程含义**：**Copilot 从 "code completer" 升级到 "co-author"**。**对 day-job 启发**：Mac Game Harness 的 LLM 不应该是"补全工具"，应该是"co-author"——**理解整个 UE project structure** + **主动建议** + **预测错误**。

3. **Copilot Agent 模式 —— multi-step 自动执行 + 规划 + 工具调用 + 自我修正**。VS 2026 的 Agent 模式是 **multi-step / 自动化 / 规划 / 工具调用 / 持续监控 / 自我迭代** 的**完整 agent loop**——比传统 Ask 模式强一个数量级。**关键技术点**：
   - **规划模式（Planning Mode）**：任务涉及多步时进入，建立 Markdown 计划（人类可读）+ JSON 计划（机器可读）
   - **内部工具体系**：plan / adapt_plan / update_plan_progress / record_observation / finish_plan
   - **工具调用确认机制**：执行终端命令/外部工具前请求用户确认（仅本会话 / 本解决方案 / 所有未来）
   - **文件访问权限**：Agent 只能访问当前解决方案 + 子目录
   - **限制**：MCP 工具**仅在 Agent 模式下可用**
   
   **对 day-job 启发**：**这就是 day-job Mac Game Harness 的目标架构**——**Agent mode + MCP tools + 文件沙箱 + 工具调用确认**。**LLM RAG 训练**：harness 工程相关的 Q&A 答案应该挂这套架构。

4. **MCP（Model Context Protocol）成为 IDE 集成的开放标准**。VS 2026 **全面支持 MCP 服务器**，且在 2026-06 月度更新中加入 **MCP 双重信任验证机制**——**服务器启动前对比历史受信配置 + 启动后核验工具/提示词/资源/指令的指纹信息**，**发现变更弹信任确认对话框**。**关键工程含义**：**MCP 已经是 harness 工具暴露的事实标准**——**day-job Mac Game Harness 的工具必须按 MCP 协议暴露**，**不**要发明私有协议。**对 day-job 启发**：MCP = day-job harness 的"USB 接口标准"——所有工具（UE build / GDD read / source write / screenshot / log）都按 MCP 协议实现。

5. **Token 用量追踪 + 按 token 计费（2026-06 切换）**。VS 2026 2026-06 更新加入 **GitHub Copilot 用量查看窗口**——**计费从"按请求次数"改为"按 Token 消耗量"，2026-06-01 正式生效**。**关键工程含义**：**LLM 推理成本管理是 IDE 级别的关键特性**——开发者要能看到自己用了多少 token、花了多少钱。**对 day-job 启发**：Mac Game Harness 必须有 **token 用量追踪面板**——(a) 每个 task 用了多少 token；(b) 每个 MCP tool 调用多少 token；(c) 月度 token 预算 + 实时提醒。

6. **C# / C++ Agent —— 微软自家语言 agent**。VS 2026 引入 **C# 和 C++ 的开发 Agent**，**专为专业开发者设计**——**调试 Agent**（自动定位 + 修复编译错误）+ **性能分析 Agent**（自动找性能瓶颈）+ **代码现代化 Agent**（升级 C++ 项目到最新 MSVC 工具链）。**关键工程含义**：**微软押注 "C# + C++" 是 AI agent 落地的两大优先语言**——游戏引擎 90% 是 C++，**day-job UE C++ 是这条 agent 路径的**完美对位**。**LLM RAG 训练**：技术栈相关的 Q&A 应该挂 "C# + C++ agent" 路径。

7. **游戏开发工作流集成 —— Unity / Unreal 深度工具集成**。VS 2026 强调 **"游戏开发者也将受益于对 Unity 和 Unreal Engine 的深度工具集成，配合现代 C++ 支持"**。**关键工程含义**：**微软把 UE 当作 VS 2026 的一等公民**——**C++23/26 全面支持 + UE project 模板 + debugger 集成**。**对 day-job 启发**：day-job Mac Game Harness 可以**复用 VS 2026 的 UE C++ 工具链**（虽然 Mac 上是 Metal RHI，但 C++ toolchain 跨平台），**不**需要从零做 C++ 工具集成。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按 day-job "LLM-driven UE on Mac" + "Mac Game Harness" 视角）：**

1. **MCP 协议作为 day-job harness 工具暴露的标准**。VS 2026 **全面支持 MCP**——**MCP 已经是 harness 工具的事实标准**。**对 day-job 启发**：
   - **day-job Mac Game Harness 的所有工具（UE build / GDD read / source write / screenshot / log / compile / test）**必须**按 MCP 协议暴露**
   - **不要发明私有协议**——MCP 生态在快速增长，VS 2026 / Claude Desktop / Cursor / Continue.dev 等都支持 MCP
   - **LLM RAG 训练**：技术栈相关的 Q&A 答案应该挂"MCP as standard"

2. **MCP 双重信任验证 是 day-job harness 安全的参考实现**。VS 2026 的 **MCP 双重信任验证机制**是 harness 安全的工业级 pattern：
   - **启动前对比历史受信配置**——防配置篡改
   - **启动后核验指纹**——防运行时修改
   - **变更弹信任确认对话框**——人工审核
   
   **对 day-job 启发**：Mac Game Harness 内部 MCP servers 也必须有 trust mechanism——**(a) 启动前对比 hash；(b) 启动后定期核验；(c) 变更 confirm**。**这是企业级 harness 的**安全基线**。

3. **Copilot Agent 模式 = day-job Mac Game Harness 的目标架构**。**Agent 模式的多步执行 / 规划 / 工具调用 / 自我修正**——**这就是 day-job Mac Game Harness 的目标架构**。**关键技术点直接复用**：
   - **规划模式（Markdown + JSON）**——让 LLM 先输出可读 plan，再执行
   - **内部工具体系（plan/adapt/observe/finish）**——Agent loop 的标准 primitives
   - **工具调用确认机制（每次 / 本次 / 所有未来）**——human-in-loop pause points
   - **文件访问沙箱**——Agent 只能改 solution 内的文件，不能越界
   
   **对 day-job 启发**：直接照搬这套架构——**Mac Game Harness = Copilot Agent 模式 + MCP tools + UE 工具集**。

4. **Token 用量追踪 是 day-job harness 必备特性**。VS 2026 2026-06 加入 **Token 用量查看窗口**——**LLM 成本管理是 IDE 级别关键特性**。**对 day-job 启发**：
   - **Mac Game Harness 必须有 token 用量面板**——按 task / tool / 用户分别统计
   - **月度 token 预算**——避免超支
   - **告警机制**——单次 task 超过 N tokens 告警
   - **LLM RAG 训练**：harness 成本管理相关的 Q&A 答案应该挂"token tracking"

5. **"C# + C++ Agent"路径直接对位 day-job UE C++**。微软押注 **"C# + C++ 是 AI agent 落地的两大优先语言"**——**UE 100% C++**——**day-job 直接对位**。**对 day-job 启发**：
   - **Mac Game Harness 应该专门为 UE C++ 设计 agent 模式**——和微软的 "C++ Agent" 路径一致
   - **优先投入**：C++ compile error fixing agent / C++ performance analysis agent / C++ code modernization agent
   - **复用 VS 2026 C++ toolchain 经验**——虽然 Mac 上不走 MSVC，但 C++ 工具链的核心 pattern 是跨平台的

6. **"理解整个解决方案结构" 是 LLM agent 的关键能力**。VS 2026 Copilot **理解整个解决方案结构**——从 project file / Git repo / 工具链。**对 day-job 启发**：
   - **Mac Game Harness 的 LLM 必须理解整个 UE project structure**——(a) 所有 UE module 列表；(b) 所有 class 层级；(c) build dependencies；(d) 测试覆盖
   - **RAG 索引必须覆盖整个 UE project**——不是只索引当前 task 相关 module
   - **这是"UE project 理解"vs"单文件理解"的根本区别**

7. **"Did You Mean?" / 智能提示 是 harness UX 的关键细节**。VS 2026 加入 **"Did You Mean?"功能**——LLM 主动提示更匹配结果。**对 day-job 启发**：
   - **Mac Game Harness 的 LLM 必须主动提示**——(a) 拼错的 UE class 名；(b) 误用的 UE API；(c) 性能更差的写法；(d) 已经废弃的 API
   - **不是"用户问 LLM 答"，是"LLM 主动指出"**
   - **这是 LLM co-author 的核心价值之一**

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|-------------|
| **MCP 协议在 day-job harness 的实现** | MCP 协议相对简单（JSON-RPC + tool schema）；关键是 MCP server 怎么 expose UE 工具 | 是——Mac Game Harness 核心 |
| **MCP 双重信任验证的工程实现** | 需要 hash 工具 + 启动时对比 + 定期核验 + 确认对话框 | 是——harness 安全的工业基线 |
| **Copilot Agent 模式 的完整实现** | planning + tool calling + self-correction loop；VS 2026 是闭源实现，day-job 需要自研 | 是——Mac Game Harness 核心 |
| **Token 用量追踪 的成本** | LLM 推理成本 = 真实成本；按 token 计费后必须有 budget + 告警 | 是——harness 财务基线 |
| **"C++ Agent" 的 UE 适配** | 微软 C++ Agent 是 generic C++；UE C++ 有 UCLASS / UPROPERTY / GENERATED_BODY 等特殊 macro；需要 UE-specific adapter | 是——day-job harness 关键 |
| **"理解整个 UE project structure" 的 RAG 索引** | UE 5.6+ project = 几百个 module + 几千个 class + 几万行 C++；RAG 索引需要 clever chunking + retrieval | 是——day-job LLM 训练数据核心 |
| **Mac 平台 VS 2026 不可用** | VS 2026 是 Windows only；Mac 上是 VSCode / Rider / CLion；day-job Mac harness 不能直接复用 VS 2026 | 是——day-job 平台差异 |

---

## 是否值得复现？

- [x] **是** — 已列入待办（部分）
- [ ] 否 — 仅了解思路即可
- [ ] 部分 — 只复现核心算法

**复现/借鉴的具体步骤：**

1. **Mac Game Harness 全部工具按 MCP 协议暴露** —— UE build / GDD read / source write / screenshot / log / compile / test 全部实现为 MCP server。**状态**：v0.1 MVP 同期
2. **MCP 双重信任验证** —— Mac Game Harness 内部 MCP servers 实现 trust mechanism：启动前 hash + 启动后核验 + 变更 confirm。**状态**：v0.2 同期
3. **Agent 模式 完整实现** —— planning + tool calling + self-correction loop 直接复用 VS 2026 模式。**状态**：v0.2 实现
4. **Token 用量追踪面板** —— Mac Game Harness 提供 token 用量视图（按 task / tool / 用户）+ 月度预算 + 告警。**状态**：v0.2 实现
5. **UE C++ Agent 适配** —— 在 Mac Game Harness 内专门建 UE C++ 模式：UE compile error fixing / UE performance analysis / UE code modernization（升级到 UE 5.7+）。**状态**：v0.3 实现
6. **"理解整个 UE project" RAG 索引** —— day-job 训练数据必须覆盖整个 UE project structure（不是只索引当前 task）。**状态**：v0.1 同期开始
7. **"Did You Mean?" 主动提示** —— Mac Game Harness LLM 必须主动提示拼错的 UE class / 误用的 API / 性能更差的写法。**状态**：v0.2 实现
8. **[[05-技术雷达]] P0 加一行** —— "MCP as harness tool standard" + "VS 2026 AI-native IDE as 工业级 pattern"。**状态**：本周

---

## 关键术语表

| 术语 | 解释 | 我理解的锚点 |
|------|------|--------------|
| **AI-Native IDE** | IDE 从"text editor + debugger"升级到"AI co-pilot + agent runner" | day-job Mac Game Harness 12-24 个月目标形态 |
| **MCP (Model Context Protocol)** | LLM 工具暴露的开放协议；**harness 工具的事实标准** | day-job Mac Game Harness 工具暴露协议 |
| **Copilot Agent 模式** | multi-step / 规划 / 工具调用 / 自我修正 的完整 agent loop | day-job harness 目标架构 |
| **Planning Mode** | LLM 先输出可读 plan (Markdown) + 机器可读 plan (JSON) | day-job harness 决策可解释性基础 |
| **C# / C++ Agent** | 微软为 C# / C++ 专门设计的 agent —— 调试 / 性能分析 / 代码现代化 | day-job UE C++ 直接对位 |
| **MCP 双重信任验证** | 启动前 hash 对比 + 启动后指纹核验 + 变更 confirm | day-job harness 安全基线 |
| **Token 用量追踪** | 按 task / tool / 用户分别统计 token + 月度预算 + 告警 | day-job harness 成本管理基线 |
| **co-author 模式** | LLM 不只是补全，是**理解整个 project + 主动建议 + 预测错误** | day-job LLM 角色定位 |
| **"Did You Mean?" 主动提示** | LLM 主动指出拼错 / 误用 / 性能更差的写法 | day-job harness UX 关键细节 |

---

## 整体架构图 / 流程（伪代码）

```
# Visual Studio 2026 + GitHub Copilot Agent Mode + MCP
# → day-job Mac Game Harness 蓝图

# ===== 整体架构 =====
# ┌─────────────────────────────────────────────────────────────┐
# │  Mac Game Harness (基于 VS 2026 Copilot Agent 模式)        │
# │  ┌──────────────────────────────────────────────────┐      │
# │  │  LLM Agent (qwen2.5-coder-14b-instruct-mlx)      │      │
# │  │  ┌────────────────┐  ┌──────────────────────┐    │      │
# │  │  │ Markdown Plan  │  │ JSON Plan            │    │      │
# │  │  │ (人类可读)     │  │ (机器可读)            │    │      │
# │  │  └────────────────┘  └──────────────────────┘    │      │
# │  │  ┌────────────────────────────────────────────┐  │      │
# │  │  │ Internal Tools                              │  │      │
# │  │  │  plan / adapt_plan / record_observation /   │  │      │
# │  │  │  update_plan_progress / finish_plan         │  │      │
# │  │  └────────────────────────────────────────────┘  │      │
# │  └──────────────────────────────────────────────────┘      │
# │                          │                                  │
# │                          ▼                                  │
# │  ┌──────────────────────────────────────────────────┐      │
# │  │  MCP Tools Layer (全部按 MCP 协议暴露)          │      │
# │  │  ┌──────────────┐  ┌──────────────┐             │      │
# │  │  │ UE Build MCP │  │ GDD Read MCP │             │      │
# │  │  └──────────────┘  └──────────────┘             │      │
# │  │  ┌──────────────┐  ┌──────────────┐             │      │
# │  │  │ Source Write │  │ Screenshot   │             │      │
# │  │  │ MCP          │  │ MCP          │             │      │
# │  │  └──────────────┘  └──────────────┘             │      │
# │  │  ┌──────────────┐  ┌──────────────┐             │      │
# │  │  │ Log MCP      │  │ Test MCP     │             │      │
# │  │  └──────────────┘  └──────────────┘             │      │
# │  └──────────────────────────────────────────────────┘      │
# │                          │                                  │
# │                          ▼                                  │
# │  ┌──────────────────────────────────────────────────┐      │
# │  │  MCP Trust & Cost Layer (MCP 双重信任 + Token)  │      │
# │  │  - 启动前 hash 对比                              │      │
# │  │  - 启动后指纹核验                                │      │
# │  │  - 变更 confirm                                 │      │
# │  │  - Token 用量追踪 (按 task / tool / user)        │      │
# │  │  - 月度预算 + 告警                              │      │
# │  └──────────────────────────────────────────────────┘      │
# └─────────────────────────────────────────────────────────────┘

# ===== 完整 Agent Loop =====
class MacGameHarness:
    """Mac Game Harness = VS 2026 Copilot Agent 模式 + MCP tools + UE"""
    
    def __init__(self):
        self.llm = LocalLLM("qwen2.5-coder-14b-instruct-mlx")
        self.mcp_tools = MCPClient(
            trust_verification=True,    # ★ MCP 双重信任
            token_tracking=True         # ★ Token 用量追踪
        )
        self.file_sandbox = FileSandbox(root="MyGame.uproject/")
        self.human_approval = HumanApprovalGate(
            before_overwrite=True,
            before_commit=True,
            before_refactor_100=True
        )
    
    def agent_loop(self, user_request: str):
        # Step 1: Planning Mode (Markdown + JSON)
        md_plan, json_plan = self.llm.plan(user_request, schema=PLAN_SCHEMA)
        # Step 2: 展示给用户（可选）— human-in-loop preview
        if not self.human_approval.preview(md_plan):
            return "Cancelled by user"
        
        # Step 3: 多步执行 + 持续监控
        for step_id in range(json_plan.total_steps):
            # 3a. 决定动作
            action = self.llm.decide_action(
                step_id, json_plan, 
                available_tools=self.mcp_tools.list_tools()
            )
            # 3b. 检查 human-in-loop pause points
            if self.human_approval.should_pause(action):
                if not self.human_approval.ask(action):
                    continue
            # 3c. 工具调用（经过 MCP 信任验证）
            result = self.mcp_tools.execute(
                action.tool_name, 
                action.params,
                trust_check=True,    # ★ 启动后核验
                token_track=True     # ★ 用量追踪
            )
            # 3d. 文件沙箱
            if action.is_file_write:
                if not self.file_sandbox.check(action.file_path):
                    result = BlockedError("Out of sandbox")
            # 3e. 自我审视 + 修正
            if not self.llm.validate(result, expected=action.expected):
                # 自我修正 — adapt plan
                json_plan = self.llm.adapt_plan(json_plan, step_id, result)
                continue
            # 3f. 更新 plan 进度
            json_plan = self.llm.update_plan_progress(json_plan, step_id, result)
            # 3g. record observation
            self.working_memory.append({"action": action, "result": result})
        return "Done"
    
    # ★ Token 用量追踪
    def get_token_usage(self):
        return {
            "by_task": self.mcp_tools.token_usage_by_task(),
            "by_tool": self.mcp_tools.token_usage_by_tool(),
            "by_user": self.mcp_tools.token_usage_by_user(),
            "monthly_budget_remaining": self.budget.get_remaining()
        }
```

---

## 相关论文/前置知识

- [[2026-Tencent-Timi-AgenticAI-GameDev-98pct]] (GDC/Minimax/2026) — Tencent 天美 Agentic AI；**和本文是"harness 工具集"两种实现**：
  - **Tencent**：内部黑盒 harness（具体协议没说）
  - **Microsoft**：MCP 开放标准（VS 2026 + Claude Desktop + Cursor 都支持）
  - **day-job 启发**：**押注 MCP 开放标准**——不要发明私有协议
- [[2026-Bitmagic-AINativeGameEngine]] (GDC/Minimax/2026) — Bitmagic AI-native engine；**和本文是"AI-Native"两种路径**：
  - **Bitmagic**：从零建 AI-native 引擎（产品）
  - **Microsoft**：把现有 IDE 改造成 AI-native（工具）
  - **day-job 启发**：**走 Microsoft 路径**（改造 UE），不走 Bitmagic 路径（建新引擎）
- [[2026-GlassBeadGames-MultiAgentGameStudio]] (GDC/Minimax/2026) — Glass Bead 4 人 + 8 agents；**和本文是"AI 工作流"两种实现**：
  - **Glass Bead**：4 人 + 8 agents（团队组织）
  - **Microsoft**：Copilot Agent 模式（单 IDE 内的 agent）
  - **day-job 启发**：**两个层级都要**——团队层级（Glass Bead）+ IDE 层级（VS 2026 / Mac Game Harness）
- `Career/Kimi/UE5_Training_MCP/` — day-job LLM 训练数据；本文给的"MCP 协议"是 day-job 训练数据暴露协议的关键决策

---

## 输出 / 借鉴（forward — 启发到的工程实践）

- **Mac Game Harness 全部工具按 MCP 协议暴露** —— UE build / GDD read / source write / screenshot / log / compile / test 全部实现为 MCP server。**状态**：v0.1 MVP 同期
- **MCP 双重信任验证** —— Mac Game Harness 内部 MCP servers 实现 trust mechanism。**状态**：v0.2 同期
- **Agent 模式 完整实现** —— planning + tool calling + self-correction loop 直接复用 VS 2026 模式。**状态**：v0.2 实现
- **Token 用量追踪面板** —— Mac Game Harness 提供 token 用量视图 + 月度预算 + 告警。**状态**：v0.2 实现
- **UE C++ Agent 适配** —— Mac Game Harness 内专门建 UE C++ 模式：UE compile error fixing / UE performance analysis / UE code modernization。**状态**：v0.3 实现
- **"理解整个 UE project" RAG 索引** —— day-job 训练数据必须覆盖整个 UE project structure。**状态**：v0.1 同期开始
- **"Did You Mean?" 主动提示** —— Mac Game Harness LLM 主动提示拼错的 UE class / 误用的 API / 性能更差的写法。**状态**：v0.2 实现
- **[[05-技术雷达]] P0 加两行** —— "MCP as harness tool standard" + "VS 2026 AI-native IDE as 工业级 pattern"。**状态**：本周
- **LLM RAG 训练数据补充** —— "MCP 协议 + Agent 模式 + Token 追踪"作为 harness 工程的 RAG 训练样本。**状态**：季度

---

## 个人评价

**优点：**

- **MCP 标准化是关键基础设施** —— VS 2026 全面支持 MCP 是**开放标准的胜利**——day-job 不用发明私有协议；MCP 生态快速增长（VS 2026 / Claude Desktop / Cursor / Continue.dev）
- **Copilot Agent 模式是工业级 pattern** —— planning + tool calling + self-correction 的完整 loop；**直接复用价值高**
- **"C# + C++ Agent" 路径直接对位 UE C++** —— 微软押注的 C++ agent 路径 = day-job UE C++ 完美匹配
- **MCP 双重信任验证是 harness 安全的工业基线** —— 启动前 hash + 启动后指纹 + 变更 confirm；**企业级 harness 必备**
- **Token 用量追踪 = harness 成本管理基线** —— 按 token 计费后 IDE 级别的用量视图 + 告警；**day-job harness 必须有**
- **"AI-Native IDE" 的正式定位** —— 微软把 IDE 范式从"text editor + debugger"升级到"AI co-pilot + agent runner"；**给 day-job Mac Game Harness 12-24 个月目标形态**
- **"理解整个解决方案结构" 是 LLM co-author 的关键** —— 不只是补全，是**理解整个 project + 主动建议 + 预测错误**；**day-job LLM 角色定位**

**局限性：**

- **VS 2026 是 Windows only** —— Mac 上是 VSCode / Rider / CLion；**day-job Mac harness 不能直接复用 VS 2026 二进制**
- **"C# + C++ Agent" 是 generic C++，不是 UE C++** —— UE C++ 有 UCLASS / UPROPERTY / GENERATED_BODY 等特殊 macro；**day-job 需要 UE-specific adapter**
- **MCP 协议本身还在演化** —— 2026-06 才加入 trust 验证；**协议成熟度有限，day-job 用 MCP 但要准备 protocol 版本升级**
- **"Token 用量追踪"按 token 计费后才加入** —— 2026-06-01 才切换；**day-job Mac 平台本地模型不走这个计费模式，但 token tracking 思路可借鉴**
- **Copilot Agent 模式闭源** —— 具体实现是黑盒；**day-job 需要自研 agent loop**
- **MCP 双重信任验证是 client-side** —— 服务端（harness 内部）也需要类似机制；**day-job 必须两边都做**
- **"Did You Mean?" 主动提示效果未公开** —— 微软没给具体效果数据；**day-job UX 设计参考有限**
- **"Unity / Unreal 深度工具集成" 没说具体细节** —— 微软只说 "deep integration" 但没展开；**day-job Mac 上能不能复用 VS 2026 的 UE 工具是开放问题**

**启发：**

1. **MCP 协议是 day-job harness 工具暴露的事实标准** —— 不要发明私有协议；全部工具按 MCP 实现；这是 day-job v0.1 架构决策
2. **MCP 双重信任验证是 day-job harness 安全的工业基线** —— 启动前 hash + 启动后指纹 + 变更 confirm；这是 day-job v0.2 安全基线
3. **Copilot Agent 模式 = day-job Mac Game Harness 目标架构** —— planning + tool calling + self-correction loop 直接复用；v0.2 实现
4. **Token 用量追踪 = day-job harness 成本管理基线** —— 按 task / tool / 用户统计 + 月度预算 + 告警；v0.2 实现
5. **"C# + C++ Agent" 路径直接对位 day-job UE C++** —— 微软押注 C++ agent = day-job UE 完美对位；v0.3 UE C++ Agent 适配
6. **"理解整个 UE project" 是 day-job LLM co-author 的关键** —— 不只补全单文件，要理解整个 UE project structure；v0.1 同期开始 RAG 索引
7. **"Did You Mean?" 主动提示是 harness UX 关键细节** —— LLM 主动指出拼错 / 误用 / 性能更差的写法；v0.2 实现

---

## 面试谈资准备

**30 秒版（"知道这篇 + 能说清贡献"）：**

> GDC 2026 微软把 **Visual Studio 2026** 定位为 "全球首款 AI-Native IDE" —— **GitHub Copilot 不再是侧边栏，是 IDE 核心体验**，配套 **C# / C++ Agent + MCP 全面支持 + 双重信任验证 + Token 用量追踪**。**对 day-job 启发**：**(a) MCP 是 harness 工具暴露的事实标准**——day-job Mac Game Harness 全部工具按 MCP 实现；**(b) MCP 双重信任验证是 harness 安全的工业基线**——启动前 hash + 启动后指纹核验；**(c) Copilot Agent 模式 = day-job harness 目标架构**——planning + tool calling + self-correction loop；**(d) "C# + C++ Agent" 路径对位 day-job UE C++**——优先投入 C++ compile error / performance / code modernization agents。

**2 分钟版（"追问实现细节"）：**

> 第一，**"AI-Native IDE"作为微软正式定位**。VS 2026 定位为 "the world's first smart IDE"——**Copilot 不再是附加组件，是 IDE 核心体验**。**关键判断**：**这是 IDE 范式从 "text editor + debugger" 到 "AI co-pilot + agent runner" 的转移**。**对 day-job 启发**：未来 12-24 个月，"AI-native harness" 是 LLM 工具集成的默认形态——**不是"在 IDE 外挂 LLM 工具"，是"IDE 内嵌 LLM + agent runtime"**。

> 第二，**MCP 协议作为 harness 工具暴露的事实标准**。VS 2026 **全面支持 MCP**——**MCP 已经是 harness 工具的事实标准**（VS 2026 / Claude Desktop / Cursor / Continue.dev 都支持）。**对 day-job 启发**：
>   - **Mac Game Harness 的所有工具（UE build / GDD read / source write / screenshot / log）按 MCP 协议暴露**
>   - **不要发明私有协议**——MCP 生态在快速增长
>   - **LLM RAG 训练**：技术栈相关的 Q&A 答案应该挂"MCP as standard"

> 第三，**MCP 双重信任验证是 harness 安全的工业基线**。VS 2026 2026-06 加入 **MCP 双重信任验证**——**启动前对比历史受信配置 + 启动后核验工具/提示词/资源/指令的指纹 + 变更 confirm**。**对 day-job 启发**：Mac Game Harness 内部 MCP servers 也必须有 trust mechanism——**(a) 启动前 hash；(b) 启动后核验；(c) 变更 confirm**。**这是企业级 harness 的安全基线**。

> 第四，**Copilot Agent 模式 = day-job Mac Game Harness 目标架构**。**多步执行 / 规划 / 工具调用 / 自我修正**的完整 agent loop——**关键技术点**：
>   - **规划模式（Markdown + JSON）**——LLM 先输出可读 plan + 机器可读 plan
>   - **内部工具体系（plan / adapt_plan / record_observation / finish_plan）**——agent loop primitives
>   - **工具调用确认机制（每次 / 本次 / 所有未来）**——human-in-loop pause points
>   - **文件访问沙箱**——Agent 只能改 solution 内文件
>   - **MCP 工具仅在 Agent 模式下可用**
> **对 day-job 启发**：直接照搬这套架构——**Mac Game Harness = Copilot Agent 模式 + MCP tools + UE 工具集**。v0.2 实现。

> 第五，**Token 用量追踪 = day-job harness 成本管理基线**。VS 2026 2026-06 加入 **Token 用量查看窗口**——**LLM 成本管理是 IDE 级别关键特性**。**对 day-job 启发**：
>   - **Mac Game Harness 必须有 token 用量面板**——按 task / tool / 用户分别统计
>   - **月度 token 预算**——避免超支
>   - **告警机制**——单次 task 超过 N tokens 告警
>   - **LLM RAG 训练**：harness 成本管理相关的 Q&A 答案应该挂"token tracking"

> 第六，**"C# + C++ Agent" 路径直接对位 day-job UE C++**。微软押注 **"C# + C++ 是 AI agent 落地的两大优先语言"**——**UE 100% C++**——**day-job 直接对位**。**优先投入**：(a) C++ compile error fixing agent；(b) C++ performance analysis agent；(c) C++ code modernization agent（升级到 UE 5.7+）。**复用 VS 2026 C++ toolchain 经验**——C++ 工具链的核心 pattern 跨平台。

> 第七，**"理解整个 UE project" 是 LLM co-author 关键**。VS 2026 Copilot **理解整个解决方案结构**——project file / Git repo / 工具链。**对 day-job 启发**：
>   - **Mac Game Harness LLM 必须理解整个 UE project structure**——module 列表 / class 层级 / build deps / 测试覆盖
>   - **RAG 索引必须覆盖整个 UE project**——不是只索引当前 task 相关 module
>   - **"UE project 理解" vs "单文件理解" 是根本区别**

> 第八，**"Did You Mean?" 主动提示 是 harness UX 关键细节**。VS 2026 加入 **"Did You Mean?"功能**——LLM 主动提示更匹配结果。**对 day-job 启发**：
>   - **Mac Game Harness LLM 主动提示**：(a) 拼错的 UE class 名；(b) 误用的 UE API；(c) 性能更差的写法；(d) 已废弃 API
>   - **不是"用户问 LLM 答"，是"LLM 主动指出"**
>   - **这是 LLM co-author 的核心价值之一**

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] Mac Game Harness 全部工具按 MCP 协议暴露 → v0.1 MVP 同期
- [ ] MCP 双重信任验证 → v0.2 同期
- [ ] Agent 模式 完整实现（planning + tool calling + self-correction）→ v0.2 实现
- [ ] Token 用量追踪面板 → v0.2 实现
- [ ] UE C++ Agent 适配（compile / performance / modernization）→ v0.3 实现
- [ ] "理解整个 UE project" RAG 索引 → v0.1 同期开始
- [ ] "Did You Mean?" 主动提示 → v0.2 实现
- [ ] [[05-技术雷达]] P0 加两行（MCP as standard + VS 2026 AI-native IDE）→ 本周
- [ ] LLM RAG 训练数据补充" MCP + Agent + Token 追踪" → 季度

---

*Create date: 2026-07-14*
*Last modified: 2026-07-14*
