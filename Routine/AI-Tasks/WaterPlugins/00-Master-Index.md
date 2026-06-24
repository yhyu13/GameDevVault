---
tags: [routine/master-index, topic/WaterPlugins, system/reference]
aliases: [WaterPlugins-AI-Master]
---

# Water Plugins 主题 — AI 任务总览

> 这是 Water Plugins（水体渲染与模拟）学习周期的「AI 任务控制塔」。  
> **核心原则**：AI 只做脚手架，你来做硬工作。

---

## 快速导航

| 日期 | 主题 | AI 任务文件 | 人类核心任务 |
|------|------|------------|-------------|
| [[周一]] | 前沿技术输入 | [[01_Monday/AI-Tasks]] | 精读论文 + 源码追踪 |
| [[周二]] | 专项技能突破 | [[02_Tuesday/AI-Tasks]] | Gerstner Wave Shader + 数学 |
| [[周三]] | 强制休息/游玩 | [[03_Wednesday/AI-Tasks]] | 带开发者视角玩游戏 |
| [[周四]] | 工程化与工具链 | [[04_Thursday/AI-Tasks]] | Buoyancy + 工具开发 |
| [[周五]] | 轻量复盘 | [[05_Friday/AI-Tasks]] | 测验 + 整理 + 规划 |
| [[周末]] | 项目实战 | [[06_Weekend/AI-Tasks]] | Demo 制作 + 博客输出 |
| [[周日]] | 项目收尾 | [[07_Sunday/AI-Tasks]] | 集成测试 + 复盘 |
| [[每周]] | 外部接触 | [[08_Weekly/AI-Tasks]] | 技术社交 + 开源贡献 |

---

## Water Plugins 是什么

Water Plugins 是 UE5 的水体渲染与模拟系统，核心特性包括：
- **Gerstner Waves**：基于物理的波浪模拟，适合开放海洋
- **Water Body 组件**：支持 Ocean / Lake / River / Pond 多种水体类型
- **Buoyancy 系统**：与 Chaos Physics 协同，实现真实的浮力交互
- **反射与折射**：SSR + 平面反射 + 水下折射
- **焦散（Caustics）**：水下光线会聚效果
- **Shoreline 交互**：海浪与岸边的自然过渡和泡沫
- **与 Lumen/Nanite 协同**：水面的全局光照和几何细节

---

## 相关参考

- [[../References/AI-Augmentation-Reference]] — AI 辅助学习完整参考手册
- [[../Lumen/00-Master-Index]] — Lumen 主题（水面反射与 GI）
- [[../ChaosPhysics/00-Master-Index]] — Chaos Physics 主题（浮力与物理交互）
- [[../../01-论文笔记库]] — 论文笔记
- [[../../02-引擎源码分析库]] — 源码分析

---

## 每周更新日志

| 周 | 主题 | 状态 |
|----|------|------|
| W1 | Water 基础：Gerstner Waves + 水体渲染 | 🔄 进行中 |
| W2 | FFT Ocean：频谱模拟 + Compute Shader | ☐ 待开始 |
| W3 | 高级效果：焦散、泡沫、 underwater rendering | ☐ 待开始 |
| W4 | 集成实战：mini-Ocean 渲染器完整版 | ☐ 待开始 |

---

*This is a living document. Update it as the Water Plugins topic progresses.*
