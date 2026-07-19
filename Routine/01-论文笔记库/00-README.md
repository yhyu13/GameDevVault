# 📚 图形学与算法论文笔记库

> **对应周计划：周一晚 — 前沿技术与论文复现（输入）**

---

## 收集策略

不要收藏夹吃灰。论文进入此库前，必须回答：

1. **这篇论文解决什么问题？**（一句话）
2. **核心创新点是什么？**（与其他方案的区别）
3. **对我当前工作是否有直接帮助？**（P0/P1/P2）
4. **是否值得复现？**（时间成本 vs 收益）

---

## 文件夹结构

- **[[SIGGRAPH]]** — 实时渲染、图形学顶会
- **[[GDC]]** — 游戏开发者大会技术演讲
- **[[IEEE-VR]]** — 虚拟现实相关
- **未分类** — 待整理的新论文（每周五清理）

### GDC 子目录索引（深度 paper note）

> GDC talk 不是论文，但因为 industry-shaping 的技术密度，作为 paper-style 笔记落盘。tag 用 `paper/signed` + `paper/GDC-YYYY`。

#### GDC 2026 — AI / 神经渲染 / World Model

- [[GDC/2026-Tencent-HaoYang-AIDrivenPrototype]] — 光子工作室 Hao Yang 的 C.A.T framework；token-first 工具栈
- [[GDC/2026-Tencent-MagicStudio-RealTimeMotionGeneration]] — 实时 AI 动作生成；INT8 0.4ms / frame
- [[GDC/2026-GoogleDeepMind-Genie3-PlayableWorlds]] — DeepMind Genie 3；world model boundaries
- [[GDC/2026-Tencent-VISVISE-FullPipeline]] — Tencent AIGC 美术管线；90+ shipping games

#### GDC 2025 — 神经渲染 / RTX Kit / DirectX Cooperative Vectors

- [[GDC/2025-NVIDIA-AdvancesInRTX-NeuralRendering]] — Spitzer/Stich/Lefohn 神经渲染路线图
- [[GDC/2025-NVIDIA-RTXKit-UE5]] — Mega Geometry + RTX Hair (LSS) 在 NvRTX 分支
- [[GDC/2025-NVIDIA-NeuralShading-DirectX]] — Cooperative Vectors shader pipeline 跨厂商标准化

> **新增 5 篇对应 day-job "LLM-driven UE on Mac" P0：**
> 1. **2026-GoogleDeepMind-Genie3** — world model boundaries（demo vs shipping）作为 LLM hype-cycle 管理框架
> 2. **2026-Tencent-VISVISE** — "engine-ready output" 作为 LLM tool design 元命题
> 3. **2025-NVIDIA-AdvancesInRTX** — 神经渲染范式锚点；Lumen/Nanite/VSM 的下个范式
> 4. **2025-NVIDIA-RTXKit-UE5** — Mega Geometry vs Nanite 对照；AI 资产的下游解放
> 5. **2025-NVIDIA-NeuralShading-DirectX** — Mac 平台 CoopVec 跟进是关键风险点

#### GDC 2026 — AI Harness / LLM 驱动游戏引擎 (6 篇，2026-07 累计)

> 这组把视角从**"AI 在游戏里的内容（神经渲染 / 资产生成 / world model）"切换到"AI 接管/驱动游戏开发本身（harness / agent / 工具链）"**——是 day-job "LLM-driven UE on Mac" 主线的直接参考。每篇都给出 day-job Mac Game Harness 的具体启发（P0）。**前 5 篇是 GDC 2026 talks，第 6 篇 (Anthropic Computer Use) 是 arXiv 工业参考**——**两者形成 "GDC 演讲叙事 + arXiv 工程底座" 双层 anchor**。

- [[GDC/2026-Tencent-Timi-AgenticAI-GameDev-98pct]] — **天美工作室 (余煜/牟骞) 可微智能 Agentic AI**：AAA 工程 98% 自动化编程；"降低对模型能力要求" 反共识判断；"AI Native 团队"组织探索
- [[GDC/2026-Bitmagic-AINativeGameEngine]] — **Bitmagic (Jani Penttinen) AI-Native 引擎**："prompt-玩-迭代" 闭环 UX；"创作者 vs 消费用户" 明确分流；"99% 的人不会编程" 产品定位元命题
- [[GDC/2026-GlassBeadGames-MultiAgentGameStudio]] — **Glass Bead Games (Kuangye Guo) 4 人 + 8 agents**："agents 性能 = 文档质量" 元命题；"prompt 清晰度检验" hard standard；"AI 接管决策表" 团队管理工具
- [[GDC/2026-Microsoft-VS2026-Copilot-GameDev]] — **微软 Visual Studio 2026 + Copilot Agent Mode + MCP**："AI-Native IDE" 范式；MCP 协议作为 harness 工具暴露事实标准；MCP 双重信任验证 + Token 用量追踪
- [[GDC/2026-GoogleDeepMind-SIMA2-GenericGameAgent]] — **DeepMind SIMA 2 通用游戏 agent**：基于 Gemini 2.5 Flash-lite 轻量模型；"理解从未见过的环境" 范式；"self-improvement loop" 作为 day-job harness 核心机制；SIMA 2 + Genie 3 组合 = day-job 长期 "AI 测试 harness" vision
- [[GDC/2024-Anthropic-ComputerUse-OSAgent]] — **Anthropic Computer Use (arXiv 2410.08193, 2024-10)**：**LLM 工业界第一个 GUI-agent 范式**；**MCP-first + GUI-fallback 双轨制**作为 day-job Mac Game Harness 架构补完的"最后一公里"；**OSWorld 24% 准确率**作为 GUI-agent 期望管理硬约束；**4 步 mitigation (VM 隔离 + 工具白名单 + 关键操作 human-in-loop + 全 trace)** 作为 prompt injection 防护基线；**vendor-neutral 抽象**避免绑死 Anthropic / OpenAI

> **6 篇对应的 day-job P0 主线（按"AI harness in game engine"维度）：**
> 1. **Tencent 天美 (98% 自动化)** — harness 终极形态参考；"可微智能"作为术语直接借用
> 2. **Bitmagic (AI-native 引擎)** — 路线选择论据（day-job 押 UE 加固，不押 AI-native 引擎）；"prompt-玩-迭代" 作为 harness UX 核心
> 3. **Glass Bead (4 人 + 8 agents)** — day-job harness 团队组织演化的真实参考；"agents 性能 = 文档质量" 提示 LLM 训练数据策略
> 4. **Microsoft (VS 2026 + MCP)** — MCP 作为 day-job harness 工具暴露事实标准；Agent 模式 = harness 目标架构
> 5. **DeepMind (SIMA 2)** — "RAG > fine-tune" + "self-improvement loop" + "轻量模型 + 良好 harness" 三件套作为 day-job 训练策略元命题
> 6. **Anthropic Computer Use** — **MCP-first + GUI-fallback 双轨制**作为 harness 架构补完；**OSWorld 24% 准确率**作为 human-in-loop 兜底必要性硬约束；**4 步 mitigation**作为 prompt injection 防护基线；**vendor-neutral GUIAgent interface**作为长期不绑死策略

---

## 标签体系

| 标签 | 含义 |
|------|------|
| `#paper/signed` | 已精读并做笔记 |
| `#paper/reproduced` | 已复现或部分实现 |
| `#paper/lumen` | 与全局光照相关 |
| `#paper/nanite` | 与几何流送/虚拟几何相关 |
| `#paper/path-tracing` | 路径追踪 |
| `#paper/AI-assets` | AI生成资产生成 |
| `#paper/AI-pipeline` | AI 生产管线 / generation pipeline |
| `#paper/neural-rendering` | 神经渲染 / neural shading |
| `#paper/world-model` | World model / 可探索 AI 世界 |
| `#paper/GDC-talk` | GDC talk 笔记（与论文笔记并列） |
| `#paper/GDC-YYYY` | GDC 年份（例 `paper/GDC-2025` / `paper/GDC-2026`） |
| `#paper/已应用到工作` | 笔记内容已迁移到 routine / 输出 |
| `#paper/待复现` | 标记为后续实现目标 |
| `#paper/已放弃` | 评估后不值得深入（如 world model shipping-grade） |
| `#paper/AI-harness` | AI 接管/驱动游戏开发的 harness / agent / 工具链 |
| `#paper/agentic-AI` | Agentic AI / 可微智能 / multi-agent 系统 |
| `#paper/MCP` | Model Context Protocol / harness 工具暴露协议 |
| `#paper/AI-native-engine` | AI-Native 引擎（从头为 AI 集成设计） |
| `#paper/team-org` | 团队组织演化（AI Native 团队 / 4人+8 agents） |

---

## 快速链接

- [[99-Templates/论文笔记]] — 新建论文笔记模板
- [[05-技术雷达]] — 评估是否值得投入
- [[03-Shader与特效案例集]] — 论文成果转化为可运行代码

---

## 月度目标追踪

| 月份 | 目标精读数 | 已完成 | 复现数 |
|------|-----------|--------|--------|
| {{date:YYYY-MM}} | 4 | 0 | 0 |

---

*Create new paper note: `Ctrl+N` → apply template [[99-Templates/论文笔记]]*
