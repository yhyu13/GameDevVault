---
tags: [routine/master-index, topic/ChaosPhysics, system/reference]
aliases: [ChaosPhysics-AI-Master]
---

# Chaos Physics 主题 — AI 任务总览

> 这是 Chaos Physics（UE5 物理引擎）学习周期的「AI 任务控制塔」。  
> **核心原则**：AI 只做脚手架，你来做硬工作。

---

## 快速导航

| 日期 | 主题 | AI 任务文件 | 人类核心任务 |
|------|------|------------|-------------|
| [[周一]] | 前沿技术输入 | [[01_Monday/AI-Tasks]] | 精读论文 + 源码追踪 |
| [[周二]] | 专项技能突破 | [[02_Tuesday/AI-Tasks]] | 刚体求解器 + 物理数学 |
| [[周三]] | 强制休息/游玩 | [[03_Wednesday/AI-Tasks]] | 带开发者视角玩游戏 |
| [[周四]] | 工程化与工具链 | [[04_Thursday/AI-Tasks]] | ECS + Physics + 工具开发 |
| [[周五]] | 轻量复盘 | [[05_Friday/AI-Tasks]] | 测验 + 整理 + 规划 |
| [[周末]] | 项目实战 | [[06_Weekend/AI-Tasks]] | Demo 制作 + 博客输出 |
| [[周日]] | 项目收尾 | [[07_Sunday/AI-Tasks]] | 集成测试 + 复盘 |
| [[每周]] | 外部接触 | [[08_Weekly/AI-Tasks]] | 技术社交 + 开源贡献 |

---

## Chaos Physics 是什么

Chaos Physics 是 UE5 的新一代物理引擎，核心特性包括：
- **刚体动力学**：大规模并行刚体模拟（10000+ 刚体）
- **破坏系统**：内置 Geometry Collection，支持电影级破坏效果
- **约束求解器**：改进的 Gauss-Seidel（PGS）及其并行化变体
- **ECS 集成**：与 UE5 Mass Entity 系统协同
- **布料系统**：Chaos Cloth，替代 PhysX Cloth
- **与 Niagara 协同**：粒子与物理的碰撞交互
- **源码可见**：完全开源在 UE5 引擎中

---

## 相关参考

- [[../References/AI-Augmentation-Reference]] — AI 辅助学习完整参考手册
- [[../Lumen/00-Master-Index]] — Lumen 主题（光照与物理破坏的交互）
- [[../Nanite/00-Master-Index]] — Nanite 主题（几何碎片与物理碰撞）
- [[../../01-论文笔记库]] — 论文笔记
- [[../../02-引擎源码分析库]] — 源码分析

---

## 每周更新日志

| 周 | 主题 | 状态 |
|----|------|------|
| W1 | Chaos 基础：刚体动力学 + 约束求解 | 🔄 进行中 |
| W2 | 破坏系统：Geometry Collection + 碎裂算法 | ☐ 待开始 |
| W3 | 布料与粒子：Chaos Cloth + Niagara 交互 | ☐ 待开始 |
| W4 | 集成实战：mini-Physics 引擎完整版 | ☐ 待开始 |

---

*This is a living document. Update it as the Chaos Physics topic progresses.*
