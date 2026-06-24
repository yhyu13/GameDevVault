---
tags: [routine/AI-tasks, topic/Lumen, day/Monday]
aliases: []
---

# 周一：AI 任务清单 — Lumen 前沿技术输入

> **人类目标**：精读 Lumen 论文，理解核心创新点，准备面试谈资。  
> **AI 任务**：提供脚手架、解释障碍、生成问题，绝不替读论文。

---

## 任务 1：论文预读引导（AI 执行）

**输入**：Lumen 论文 PDF 或你的 Obsidian 笔记 [[Lumen-SIGGRAPH-2021]]

**AI 输出**：
1. 一段 **150 字摘要**（核心问题 + 方法 + 结果）
2. **3 个引导问题**用于精读时回答：
   - Q1: Lumen 的三层结构分别解决什么问题？
   - Q2: Software Ray Tracing vs Hardware RT 的权衡是什么？
   - Q3: Radiance Cache 的更新频率与 Light Probe 有何本质区别？
3. **重点章节标记**：先读 Section 4 (SDF Tracing)，再读 Section 5 (Radiance Cache)，最后读 Section 7 (Performance)

**交付物**：`Lumen-Reading-Guide.md`（AI 生成，你打印或分屏对照）

---

## 任务 2：公式推导解释（AI 执行，你验证）

**输入**：论文中你卡住的公式（拍照或截图粘贴给 AI）

**AI 输出**：
1. 公式中每个符号的含义表
2. 从上一式到本式的变换步骤（一步一行）
3. 一个数值代入示例（假数据走一遍）

**你必须做**：用纸笔跟着推导一遍，确认理解后再继续。

---

## 任务 3：面试谈资生成（AI 执行，你 rehearse）

**输入**：你的精读笔记（核心创新点 + 实现难点 + 个人评价）

**AI 输出**：
1. **30 秒版本**：1 句话问题 + 1 句话方法 + 1 句话结果
2. **2 分钟版本**：背景 → 三层结构详解 → 软件光追优势 → 局限与启发
3. **3 个可能的追问及建议回答**：
   - "Radiance Cache 和 Light Probe 的区别？"
   - "Surface Cache 的更新频率？"
   - "Lumen 在植被场景下的表现？"

**你必须做**：对着镜子大声说 3 遍，计时。

---

## 任务 4：源码地图绘制（AI 执行，你验证）

**输入**：你想追踪的 UE5 源码问题，如 "Lumen 的 Software Ray Tracing 入口在哪？"

**AI 输出**：
1. 从 `FSceneRenderer::Render()` 到 `FLumenCardTracing` 的调用链（文件路径 + 函数名）
2. 每个函数的一句话职责说明

**你必须做**：在 UE5 工程中打开这些文件，用 debugger 或 IDE 的 Call Hierarchy 验证 AI 给出的路径。修正 AI 的幻觉。

---

## 今日 AI 禁区（绝对禁止）

- ❌ 让 AI 直接读论文并告诉你 "这篇论文讲了什么"
- ❌ 让 AI 替你写论文笔记（Obsidian 中的笔记必须是你自己的话）
- ❌ 让 AI 生成完整代码路径而不验证（AI 会编造函数名）
- ❌ 让 AI 替你准备面试回答而不自己 rehearse

---

## 完成检查清单

- [ ] AI 阅读指南已生成并打印
- [ ] 公式推导已手动验证
- [ ] 面试谈资已 rehearse  aloud
- [ ] 源码路径已用 debugger 验证
- [ ] 所有内容已写入 Obsidian 笔记（你写的，不是 AI 写的）

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2 小时*  
*产出：1 篇论文笔记 + 1 篇源码分析 + 面试谈资 ready*
