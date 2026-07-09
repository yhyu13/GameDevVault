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
