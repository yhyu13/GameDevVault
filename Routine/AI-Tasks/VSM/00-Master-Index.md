---
tags: [routine/master-index, topic/VSM, system/reference]
aliases: [VSM-AI-Master]
---

# VSM 主题 — AI 任务总览

> 这是 VSM（Virtual Shadow Maps）学习周期的「AI 任务控制塔」。  
> **核心原则**：AI 只做脚手架，你来做硬工作。

---

## 快速导航

| 日期 | 主题 | AI 任务文件 | 人类核心任务 |
|------|------|------------|-------------|
| [[周一]] | 前沿技术输入 | [[01_Monday/AI-Tasks]] | 精读论文 + 源码追踪 |
| [[周二]] | 专项技能突破 | [[02_Tuesday/AI-Tasks]] | Shadow Shader + 数学 |
| [[周三]] | 强制休息/游玩 | [[03_Wednesday/AI-Tasks]] | 带开发者视角玩游戏 |
| [[周四]] | 工程化与工具链 | [[04_Thursday/AI-Tasks]] | Page Table + 工具开发 |
| [[周五]] | 轻量复盘 | [[05_Friday/AI-Tasks]] | 测验 + 整理 + 规划 |
| [[周末]] | 项目实战 | [[06_Weekend/AI-Tasks]] | Demo 制作 + 博客输出 |
| [[周日]] | 项目收尾 | [[07_Sunday/AI-Tasks]] | 集成测试 + 复盘 |
| [[每周]] | 外部接触 | [[08_Weekly/AI-Tasks]] | 技术社交 + 开源贡献 |

---

## VSM 是什么

VSM（Virtual Shadow Maps）是 UE5 的虚拟化阴影系统，核心思想包括：
- **Virtual Texture 应用于阴影**：将 Shadow Map 虚拟化，按需分配物理页
- **Page Table 管理**：类似 VT 的页表，映射虚拟阴影 UV 到物理纹理池
- **按需分配**：只有被光源照射的区域才分配物理页，大幅节省内存
- **无级过渡**：消除传统 CSM 的级间裂缝，实现连续阴影精度
- **与 Lumen/Nanite 协同**：VSM 为 Lumen 提供精确阴影，Nanite 为 VSM 提供几何细节

---

## 相关参考

- [[../References/AI-Augmentation-Reference]] — AI 辅助学习完整参考手册
- [[../Lumen/00-Master-Index]] — Lumen 主题（GI 与 VSM 协同）
- [[../Nanite/00-Master-Index]] — Nanite 主题（几何细节与阴影精度）
- [[../../01-论文笔记库]] — 论文笔记
- [[../../02-引擎源码分析库]] — 源码分析

---

## 每周更新日志

| 周 | 主题 | 状态 |
|----|------|------|
| W1 | VSM 基础：Virtual Shadow Map 原理 + Page Table | 🔄 进行中 |
| W2 | 软阴影算法：PCF/PCSS/VSM 方差/ESM 指数 | ☐ 待开始 |
| W3 | 与 GI 协同：VSM 如何影响 Lumen 的间接光 | ☐ 待开始 |
| W4 | 集成实战：mini-VSM 渲染器完整版 | ☐ 待开始 |

---

*This is a living document. Update it as the VSM topic progresses.*
