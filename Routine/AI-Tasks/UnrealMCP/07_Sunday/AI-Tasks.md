---
tags: [routine/AI-tasks, topic/UnrealMCP, day/Sunday]
aliases: []
---

# 周日：AI 任务清单 — Unreal MCP 项目收尾与周复盘

> **人类目标**：完成 mini-MCP 项目的最终集成，输出文档，做周复盘。  
> **AI 任务**：协助 debug、润色文档、生成复盘模板，绝不写核心代码。

---

## 上午：项目收尾（2h）

### 任务 1：集成测试辅助（AI 执行）

**AI 输出**：测试矩阵

| 测试场景 | 输入 | 预期输出 | 验证方法 |
|----------|------|----------|---------|
| 初始化握手 | `initialize` 请求 | 返回 protocolVersion + capabilities | 断言 |
| 工具发现 | `tools/list` 请求 | 返回 5 个工具 + 正确 Schema | 断言 |
| 场景查询 | `get_scene_objects` + `{"type":"StaticMeshActor"}` | 返回对象列表 | 断言 |
| 蓝图修改 | `modify_blueprint` + 参数 | 返回成功/失败 | 断言 |
| 构建启动 | `build_project` + 参数 | 返回构建进程 ID | 断言 |
| 资产检查 | `check_asset_naming` | 返回违规资产列表 | 断言 |
| 报告生成 | `generate_level_report` | 返回 Markdown 报告 | 断言 |
| 错误处理 | 调用不存在的工具 | 返回 -32601 Method Not Found | 断言 |
| 并发测试 | 同时发送 10 个请求 | 所有请求正确响应，无乱序 | 断言 |

**你必须做**：运行每个测试，记录实际结果。

---

### 任务 2：性能 Baseline（AI 执行，你测量）

**AI 输出**：Benchmark 方案

| 指标 | 测量方法 | 目标 |
|------|----------|------|
| 初始化延迟 | `initialize` 往返时间 | < 100ms |
| 工具调用延迟 | `tools/list` 往返时间 | < 50ms |
| 并发吞吐量 | 100 请求/秒 | 无错误 |
| 内存占用 | `psutil` 测量 RSS | < 50MB |
| Schema 序列化耗时 | 5 个工具 → JSON | < 10ms |

**你必须做**：实际运行 benchmark，记录数据。

---

## 下午：文档与复盘（1-2h）

### 任务 3：项目文档生成（AI 执行，你填充）

**AI 输出**：README 模板

```markdown
# mini-mcp-toolset
> 一个自定义 MCP 工具集，让 AI 助手通过 Model Context Protocol 控制 Unreal Engine

## 工具清单
| 工具 | 描述 | 示例调用 |
|------|------|----------|
| `get_scene_objects` | 查询场景对象 | ... |
| `modify_blueprint` | 修改蓝图属性 | ... |
| `build_project` | 启动项目构建 | ... |
| `check_asset_naming` | 检查资产命名规范 | ... |
| `generate_level_report` | 生成关卡报告 | ... |

## 快速开始
```bash
pip install -e .
python server.py
# 在 Claude Desktop 或 Cursor 中配置 MCP Server
```

## 性能
| 指标 | 数值 |
|------|------|
| 初始化延迟 | _ms |
| 工具调用延迟 | _ms |
| 并发吞吐量 | _req/s |

## 学习笔记
见 [Obsidian Vault](link)
```

**你必须做**：填写所有数据和测量结果。

---

### 任务 4：周复盘辅助（AI 执行，你补充）

**AI 输出**：数据总结 + 模式发现 + 下周建议

**你必须做**：补充主观体验（能量、顿悟、困难、意外发现）。

---

## 今日 AI 禁区

- ❌ 让 AI 替你运行测试和 benchmark
- ❌ 让 AI 替你写项目文档的核心技术描述
- ❌ 让 AI 替你写周复盘日记
- ❌ 让 AI 替你决定下周计划

---

## 完成检查清单

- [ ] mini-MCP 集成测试全部通过（9/9）
- [ ] 性能 benchmark 已运行，数据已记录
- [ ] README 文档已填写并发布到 GitHub
- [ ] 周复盘已完成，主观体验已补充
- [ ] 下周计划已调整并写入 Obsidian
- [ ] 所有链接（GitHub、博客、Obsidian）已更新到知识库

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 3-4 小时*  
*产出：1 个完整 MCP Toolset + 1 份文档 + 1 次周复盘 + 下周计划*
