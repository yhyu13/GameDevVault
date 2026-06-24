---
tags: [routine/master-index, topic/VGM, system/reference]
aliases: [VGM-AI-Master]
---

# VGM 主题 — AI 任务总览

> 这是 VGM（Virtual Geometry & Mesh）学习周期的「AI 任务控制塔」。  
> **核心原则**：AI 只做脚手架，你来做硬工作。

---

## 快速导航

| 日期 | 主题 | AI 任务文件 | 人类核心任务 |
|------|------|------------|-------------|
| [[周一]] | 前沿技术输入 | [[01_Monday/AI-Tasks]] | 精读论文 + 源码追踪 |
| [[周二]] | 专项技能突破 | [[02_Tuesday/AI-Tasks]] | Mesh Shader 编程 + 数学 |
| [[周三]] | 强制休息/游玩 | [[03_Wednesday/AI-Tasks]] | 带开发者视角玩游戏 |
| [[周四]] | 工程化与工具链 | [[04_Thursday/AI-Tasks]] | Meshlet 工具 + API 实践 |
| [[周五]] | 轻量复盘 | [[05_Friday/AI-Tasks]] | 测验 + 整理 + 规划 |
| [[周末]] | 项目实战 | [[06_Weekend/AI-Tasks]] | Demo 制作 + 博客输出 |
| [[周日]] | 项目收尾 | [[07_Sunday/AI-Tasks]] | 集成测试 + 复盘 |
| [[每周]] | 外部接触 | [[08_Weekly/AI-Tasks]] | 技术社交 + 开源贡献 |

---

## VGM 是什么

VGM（Virtual Geometry & Mesh）是下一代 GPU 几何渲染技术，包括：
- **Mesh Shader**（DirectX 12 Ultimate / Vulkan）：取代传统 VS/GS 的可编程几何管线
- **Meshlet**：将 Mesh 拆分为固定大小的小块，GPU 独立处理
- **Task Shader**：在 GPU 端执行可见性剔除，减少 CPU 瓶颈
- **GPU-Driven Rendering**：CPU 只提交少量 Draw Calls，GPU 自主管理几何
- **与 Nanite 的关系**：Nanite 是 UE5 的虚拟几何**实现**，VGM 是**通用技术栈**

---

## 相关参考

- [[../References/AI-Augmentation-Reference]] — AI 辅助学习完整参考手册
- [[../Nanite/00-Master-Index]] — Nanite 主题（UE5 的具体实现）
- [[../../01-论文笔记库]] — 论文笔记
- [[../../02-引擎源码分析库]] — 源码分析
- [[../../99-Templates/论文笔记]] — 论文笔记模板

---

## 每周更新日志

| 周 | 主题 | 状态 |
|----|------|------|
| W1 | VGM 基础：Mesh Shader 管线 + Meshlet 构建 | 🔄 进行中 |
| W2 | Task Shader：GPU 剔除 + LOD 管理 | ☐ 待开始 |
| W3 | GPU-Driven 渲染：Indirect Draw + 内存布局 | ☐ 待开始 |
| W4 | 集成实战：mini-VGM 渲染器完整版 | ☐ 待开始 |

---

*This is a living document. Update it as the VGM topic progresses.*
