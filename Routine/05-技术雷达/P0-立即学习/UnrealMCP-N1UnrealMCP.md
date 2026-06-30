---
tags: [radar/P0, radar/AI-生产力, radar/工具链]
aliases: [UnrealMCP, N1UnrealMCP, DandyDay UnrealMCP, UE MCP, MCP for UE, AI 控制 UE Editor]
---

# UnrealMCP(N1) — 让 AI Agent 直接操控 UE Editor

| 字段 | 内容 |
|------|------|
| **技术名称** | UnrealMCP(N1UnrealMCP)— MCP 协议让 Claude Code / AI Agent 控制 Unreal Editor |
| **类别** | 工具链 / AI 编程生产力 |
| **当前优先级** | P0 |
| **发现日期** | 2026-06-26 |
| **最后评估日期** | 2026-06-26 |

---

## 一句话简介

> 在 UE 项目里装一个 MCP 插件,让 Claude Code / Cursor 之类的 AI Agent **直接操控 Unreal Editor** — spawn actor、编译 Blueprint、创建材质、批量改资源、调用 Console — **你 day-job 的"读项目代码"升级成"读 + 改 + 验证"全闭环,不是 IDE 提示词级别的辅助**。

---

## 成熟度评估

| 维度 | 评分 (1-5) | 说明 |
|------|------------|------|
| 生产可用性 | 4 | UE 5.7 已稳定,GitHub 12 commits + 持续活跃,Demo 项目齐全 |
| 文档完善度 | 4 | README 详尽,100+ 命令分 11 类清晰列出,自带 Demo |
| 社区活跃度 | 4 | DandyDay 开源,MCP 协议生态在 2026 H1 是爆发期;NVIDIA / Microsoft Build 2026 都推 MCP |
| 学习资源 | 4 | 配合 Claude Code 现有文档,无需重新学 — 装上就能用 |
| 与现有栈兼容性 | 5 | UE 5.7+ 原生支持;Python 3.11+;Claude Code 直接走 MCP 协议 |

**核心能力(100+ 命令,11 类):**
- **Editor**(19):spawn/delete/transform actor、开 level、截图、视口操作
- **Blueprint**(12):创建 BP、加 component/variable、编译
- **Blueprint Node**(15):event/function/branch 节点、引脚连线
- **Material**(11):创建材质、加 expression、连节点
- **UMG**(7):widget BP、加/删 widget、布局
- **Project**(5):Enhanced Input 映射、项目设置、插件管理
- **Asset**(8):查找/导入/重命名/移动/删除/复制资源
- **Landscape**(8):创建 landscape、分配材质、地层
- **PIE**(5):Play/Stop、控制台命令(带黑名单)
- **Data**(10):DataTable CRUD、CurveFloat / CurveLinearColor / DataAsset
- **Meta**(4):ping、list_commands、describe_command、list_categories

**架构亮点:**
- **MCP(stdio)** → **Python Bridge(TCP:55558)** → **UE Plugin(MCP Client)** → **EditorSubsystem(MCP Server)**
- TMap-based Command Registry — 加新命令只需要"一个函数 + 一行注册"
- 请求 ID 关联(UUID),并发 MCP tool call 自动匹配
- 握手协议(版本检查 + capabilities 协商)
- 所有 mutation 命令包在 `FScopedTransaction` 里 — **自动 Undo/Redo**
- Perforce 自动 checkout + `MarkPackageDirty` + 可选 save

---

## 学习成本估算

| 阶段 | 时间 | 产出 |
|------|------|------|
| 上手入门 | 1 天 | clone 插件 → 装到 Plugins 文件夹 → 配置 `~/.claude.json` → 跑通 ping |
| 熟练应用 | 1 周 | 能用 spawn_actor / create_blueprint / add_component 这套,改自己项目代码 |
| 深度掌握 | 1 月 | 能写自定义命令(handler + bridge tool),能搭"AI 帮我写完一整个 GameFeature"的流水线 |

**关键技能点:**
- **MCP 协议基础**:stdio / TCP / JSON-RPC 通信模型,跟 LLM tool call 一致
- **UE Editor Subsystem**:扩展 Editor 能力的标准入口
- **Python Bridge**:用 FastMCP 把 TCP 转 MCP,Python 是 agent 端 — 这块不用你写,clone 下来用就行
- **Perforce / Git 工作流**:`MarkPackageDirty` + 自动 checkout 是 AI 改 UE 资源的标配,别手动忽略

---

## 与当前工作的关联

- [x] 直接相关 — 当前项目可用
- [x] 间接相关 — 未来项目可能用
- [x] 知识拓展 — 拓宽技术视野(从"用 AI 写代码"升级到"用 AI 跑 Editor")

**具体关联点:**
- **day-job 读项目代码**:Claude Code 的 `Read` + `Grep` 是"看",**UnrealMCP 是"看 + 立刻试"** — 你可以 `claude` 一下:`"在 LyraGameMode 里加一个自定义 GameState 初始化步骤,要求在 BeginPlay 后第 5 秒输出 Log"`,AI 直接 spawn actor / 改蓝图 / 编译 / 跑 PIE 给你看,不用你切 IDE
- **新项目快速搭骨架**:`create_blueprint` + `add_component` + `compile_blueprint` 这一套,**AI 一次性能搭出 80% 的项目骨架**,你只调 20%
- **跨模块批量重构**(引擎模块间同步签名):AI 改完 C++,自动调 UnrealMCP 编译 + 检查 BP 编译错误 + 截图验证
- **Lyra 项目实测**:用 UnrealMCP 让 AI 自己读 Lyra 的 GameFeature → 创建一个自定义 GameFeature 子类 → 加 1 个 Ability → 跑 PIE 截图,全程 5 分钟
- **MetaHuman / Audio2Face 集成**:3DGS / ACE 这些 P0 条目的"实测验证"都能靠 UnrealMCP 自动化

**对你 day-job 的真实杠杆:**
- **把"读代码"升级成"读 + 改 + 验证"** — 这是 2026 年 AI 编程从 IDE 提示词到 Agent 化的标志性能力
- 你不用再"读 100 个 .h 文件然后自己改",而是"AI 读 + 改 + 我审 + AI 跑 PIE 验证"
- **MCP 协议是 2026 H1 的爆点**:Microsoft Build 2026 / NVIDIA Computex 2026 都明确推 MCP — 这是未来 12-24 个月 AI × 工具的通用接口标准

---

## 评估记录

| 日期 | 评估人 | 结论 | 下次回顾 |
|------|--------|------|----------|
| 2026-06-26 | 我 | P0 立即学习 — day-job 直接闭环加速 | 1个月后 |

---

## 关键资源

- GitHub(DandyDay/UnrealMCP):https://github.com/DandyDay/UnrealMCP
- MCP 协议官方:https://modelcontextprotocol.io/
- Claude Code MCP 配置文档:https://docs.anthropic.com/en/docs/claude-code/mcp
- NVIDIA + Microsoft Build 2026(2026 H1)均把 MCP 列为 Agent 工具标准接口

**上手步骤(给一个 UE 5.7 + Claude Code 的人):**
1. `git clone https://github.com/DandyDay/UnrealMCP.git YourProject/Plugins/N1UnrealMCP`
2. `cd YourProject/Plugins/N1UnrealMCP/Bridge && uv sync`(装 Python 依赖)
3. 在 `~/.claude.json` 加 mcpServers 配置(参考 README)
4. 启动 UE Editor,插件自动起 TCP server on port 55558
5. 启动 Claude Code,`ping` 验证连接
6. 跑 `spawn_actor` 或 `create_blueprint` 验证链路

---

## 状态迁移

- [x] P0 → 正在学习中 → 已掌握 → 移出雷达
- [ ] P1 → 评估后降为 P2 / 升为 P0
- [ ] P2 → 评估后放弃 / 升为 P1

---

## 我的判断(只对你说)

**这是 2026 H1 最值得加进 P0 的工具 — 直接命中你的 day-job**。  
之前 Cursor / Claude Code 是"代码侧 AI",UnrealMCP 是"引擎侧 AI" — 加上它,你的"读项目代码"工作流从"看 + 想"变成"看 + 改 + 跑 + 截图"完整闭环,**这是 senior 程序员的单兵能力边界外推**。  
警惕:**别只用 ping / spawn_actor 这种浅命令** — 真正的杠杆是用它做"AI 帮我跑 30 个 PIE 验证场景,我审 log",这才是 2026 年 AI × 引擎的正确打开方式。  
**MCP 协议本身**:Microsoft Build 2026 / NVIDIA Computex 2026 都把 MCP 推成 Agent 工具标准 — 学会 UnrealMCP 之后,UE 之外(Unity MCP / Blender MCP / Godot MCP)的同类工具都是一个模式。

---

*Create date: 2026-06-26*
*Last modified: 2026-06-26*