---
tags: [radar/P0, radar/AI-生产力, radar/工具链]
aliases: [Cursor, Claude Code, GitHub Copilot, AI 编程助手, 配对编程]
---

# AI 编程助手 — Cursor / Claude Code / Copilot(直接吃产能)

| 字段 | 内容 |
|------|------|
| **技术名称** | AI 代码助手(Cursor / Claude Code / GitHub Copilot) |
| **类别** | 工具链 / 编程生产力 |
| **当前优先级** | P0 |
| **发现日期** | 2026-06-25 |
| **最后评估日期** | 2026-06-25 |

---

## 一句话简介

> 把 LLM 嵌进 IDE/终端,让你写 C++/Python/Blueprint 的时候,**单次按键出一个"值得看的"补全或重构** — **GDC 2026 上 Claude Code 是演讲者最高频提到的工具,已经变成行业基线而不是尝鲜**。

---

## 成熟度评估

| 维度 | 评分 (1-5) | 说明 |
|------|------------|------|
| 生产可用性 | 5 | 已被 Epic / 暴雪 / 米哈游等大厂团队作为日常工具 |
| 文档完善度 | 5 | 三家文档/教程极完善,Cursor 自身带 onboarding |
| 社区活跃度 | 5 | r/ChatGPTCoding、Cursor 论坛、Claude Code 文档站极度活跃 |
| 学习资源 | 4 | B 站 / YouTube 一大堆"我用 Cursor 写 UE C++"教程 |
| 与现有栈兼容性 | 5 | 通用 IDE,VSCode 派生,UE 调试链直连 |

**2026 年 6 月三家横向对比:**

| 工具 | 形态 | 优势场景 | 短板 |
|------|------|----------|------|
| **Cursor** | IDE(VSCode fork) | 跨文件编辑、Composer 模式、多文件重构 | 重,资源占用大 |
| **Claude Code** | 终端 Agent | 读大工程、批量改文件、跑命令、写测试 | 需要明确的"做什么"指令 |
| **GitHub Copilot** | IDE 插件 | 行内补全、轻量集成 | 上下文理解弱于 Cursor/Claude Code |

**对于 UE C++ 工程的实际表现:**
- `UCLASS/UPROPERTY/UFUNCTION` 宏 + 头文件互相引用 → Cursor 表现最好
- 跨模块批量重构(比如改一个接口签名同步所有 override)→ Claude Code 表现最好
- 单纯行内补全 → Copilot 速度最快,延迟最低

---

## 学习成本估算

| 阶段 | 时间 | 产出 |
|------|------|------|
| 上手入门 | 2 天 | 装好,会在注释里写"// TODO: 实现 X"然后 Tab 接受补全 |
| 熟练应用 | 2 周 | 学会用 `@codebase` / `#file` 这样的指令让 AI 真正懂 UE 模块 |
| 深度掌握 | 1-2 月 | 学会写"AI 友好的工程结构" — 文件小、依赖清晰、接口明确,AI 改起来又快又准 |

**关键技能点(技能大于工具):**
- **拆任务**:把"给 Lyra 加一个技能"拆成"先看 LyraAbilitySystem 的接口,再设计 DataAsset,再写一个 GA 子类" — AI 在每一步都很强,但一次性甩 5 步给它就崩
- **写规约**:给 AI 的 system prompt / `.cursorrules` 里写清"UE5 C++ 风格、不要用裸指针、必须用 TObjectPtr<>、头文件按字母序"
- **读 diff**:AI 给的代码 80% 编译能过,**真正的功夫是 5 秒内扫出错的 20%** — 这是 senior 和 junior 拉开差距的地方
- **避免幻觉**:LLM 会编造不存在的 UE API,必须对照引擎源码验证

---

## 与当前工作的关联

- [x] 直接相关 — 当前项目可用
- [x] 间接相关 — 未来项目可能用
- [x] 知识拓展 — 拓宽技术视野

**具体关联点:**
- **读项目代码(day job 核心任务)**:Claude Code 适合"读一个陌生模块,问它每个类在做什么";Cursor 适合"读完之后想改一下试试"
- **写引擎工具/Editor Subsystem**:UE 的 `UEditorUtilityWidget` + C++ 这类"边角"代码,AI 写起来又快又准
- **Shader 编写**:虽然 HLSL 也能让 AI 帮写,但要注意 UE 宏(`#include "/Engine/Public/...`")经常让 AI 卡住
- **Gameplay 框架样板**:PlayerController/GameMode/Pawn 的 `SetupPlayerInputComponent` 之类,AI 写一遍后复制粘贴最划算

**对你 day-job 的真实杠杆:**
- 读 100 个 `Lyra*.h` 文件:用 Claude Code,`claude` 起一个会话,然后"读 LyraGameMode,告诉我它的初始化顺序"
- 写一个新的 GameFeature:用 Cursor,把头文件结构先画出来,AI 写实现
- 修一个崩溃:用 Cursor + `// 这里是栈,这是崩溃前的最后状态` + 上下文粘贴,大多数时候能给到正确的方向

---

## 评估记录

| 日期 | 评估人 | 结论 | 下次回顾 |
|------|--------|------|----------|
| 2026-06-25 | 我 | P0 立即学习 — 已经是行业基线,不用就落后 | 1个月后 |

---

## 关键资源

- Cursor 官方:https://cursor.com/
- Claude Code 官方:https://docs.anthropic.com/en/docs/claude-code/overview
- GitHub Copilot:https://github.com/features/copilot
- GDC 2026 上关于 AI 编程的演讲合集:https://www.gdcvault.com/
- 推荐:在工程里加一个 `.cursorrules` 文件,把 UE 编码规范写进去 — AI 改代码时会自动遵守

**推荐上手顺序(给一个会写 UE C++ 的人):**
1. 先装 Cursor,免费试用 14 天,用它写一个 Lyra 的小修改
2. 同时装 Claude Code,用 `claude` 命令读你正在看的项目代码
3. 一周内选定主力工具,卸载另一个,别两个都用

---

## 状态迁移

- [x] P0 → 正在学习中 → 已掌握 → 移出雷达
- [ ] P1 → 评估后降为 P2 / 升为 P0
- [ ] P2 → 评估后放弃 / 升为 P1

---

## 我的判断(只对你说)

**这玩意儿不是"会不会用"的问题,是"现在用 vs 等别人用"的问题** — GDC 2026 报告里,资深从业者(也就是你这种)的 AI 工具使用率显著高于初级,你已经晚了一步。  
你 day job 的核心是"读项目代码",**Claude Code 的 `Read` + `Grep` 组合就是为你这种场景设计的** — 把整个工程喂进去问"这俩类怎么通信的",比你手动翻 5 分钟快 10 倍。  
别陷入"哪个 AI 更好"的工具党争论,**选定一个,每天用,2 周后回来看**。

---

*Create date: 2026-06-25*  
*Last modified: 2026-06-25*
