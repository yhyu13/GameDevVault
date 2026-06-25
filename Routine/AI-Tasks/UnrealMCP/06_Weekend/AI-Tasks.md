---
tags: [routine/AI-tasks, topic/UnrealMCP, day/Weekend]
aliases: []
---

# 周末：AI 任务清单 — Unreal MCP 项目实战与深度输出

> **人类目标**：完成一个 MCP 相关的 mini-project（自定义 MCP Toolset + Server + 与 UE 编辑器集成）。  
> **AI 任务**：Debug 辅助、Blog 润色、架构 review，绝不写核心算法。

---

## 周六上午：项目实战（3h 集中块）

### 任务 1：项目脚手架（AI 生成，你确认）

**输入**："我要做一个 mini-MCP 工具集，包含：1 个 Python MCP Server + 5 个自定义工具（查询场景对象、修改蓝图属性、启动构建、检查资产命名规范、生成关卡报告）。生成项目结构"

**AI 输出**：目录结构 + 文件框架 + TODO 标记

```
mini-mcp-toolset/
├── server.py              # MCP Server 入口
├── tools/
│   ├── __init__.py
│   ├── scene_tools.py     # 查询场景对象
│   ├── blueprint_tools.py # 修改蓝图属性
│   ├── build_tools.py     # 启动构建
│   ├── asset_tools.py     # 检查资产命名
│   └── report_tools.py    # 生成关卡报告
├── tests/
│   └── test_mcp_server.py
├── README.md
└── pyproject.toml
```

**你必须做**：确认结构，填充所有 TODO。

---

### 任务 2：Debug 辅助（AI 执行，你验证）

**输入**：运行时错误日志（如 "Tool not found"、"Schema validation failed"、"Connection refused"）

**AI 诊断**：错误分类 → 3 个可能原因 → 验证步骤 → 修复建议

**你必须做**：按步骤排查，确认根因，手动修复。

---

## 周日下午：输出与复盘

### 任务 3：Blog 初稿润色（AI 执行，你提供内容）

**AI 输出**：3 个候选标题、结构重组、代码格式化、社交摘要

**示例标题**：
> 1. 「从零写 MCP 工具集：让 AI 助手控制 Unreal Engine」
> 2. 「MCP 协议实战：5 个自定义工具让 AI 成为 UE 编辑器助手」
> 3. 「AI 辅助游戏开发：Model Context Protocol 与 Unreal Engine 的集成之路」

**你必须做**：检查技术准确性，保留个人风格。

---

### 任务 4：架构 Review（AI 执行，你决策）

**AI 审查**：代码质量、与官方 MCP SDK 的对比、性能、可扩展性、安全性

**AI 输出**：审查报告 + 3 个优先级排序的改进建议

**你必须做**：决定哪些改进值得做，记录到技术雷达。

---

## 任务 5：演示准备（AI 执行，你练习）

**AI 输出**：5 分钟演示脚本 + 可能被问的问题

**示例脚本**：
- 0:00-0:30 问题：为什么 AI 需要工具？
- 0:30-1:30 MCP 协议简介（JSON-RPC + Tool Schema）
- 1:30-3:00 Demo：AI 通过 MCP 查询 UE 场景、修改蓝图、启动构建
- 3:00-4:00 技术实现：自定义 Tool 的注册和执行
- 4:00-5:00 踩坑与收获

**可能被问**：
- "MCP 与 UE 的 PythonScriptPlugin 有什么区别？"
- "安全性如何保证？AI 不会误删我的项目吧？"
- "这个方案能用于生产环境吗？"

**你必须做**：排练 ≥2 次，计时。

---

## 今日 AI 禁区

- ❌ 让 AI 写核心算法（Tool 执行逻辑、Schema 生成）
- ❌ 直接 copy AI 的 bug 修复而不验证根因
- ❌ 让 AI 替写博客技术内容
- ❌ 让 AI 替你准备演示而不排练

---

## 完成检查清单

- [ ] mini-MCP Toolset 核心代码已全部手写完成
- [ ] Debug 问题已用 AI 辅助定位，手动修复
- [ ] Blog 初稿已润色，技术准确性已验证
- [ ] 架构 review 已阅读，改进计划已记录
- [ ] 演示脚本已排练 2 次以上
- [ ] 所有产出已归档到 Obsidian（笔记 + 代码链接 + 博客链接）

---

*AI 执行时间：约 30 分钟*  
*人类执行时间：约 4 小时（3h 项目 + 1h 输出）*  
*产出：1 个可运行的 MCP Toolset + 1 篇技术博客 + 1 份演示 ready*
