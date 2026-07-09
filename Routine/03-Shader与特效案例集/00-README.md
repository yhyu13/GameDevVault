# 🎨 Shader 与特效案例集

> **对应周计划：周二晚 — 专项技能突破（深度）**
>
> **2026-07-09 大重构**：本目录按 **W1~W9 周次** 组织（不再按 后处理效果/反射效果/... 分类）。每篇 case study 是一个独立 `.md`，frontmatter 带 `week: Wn` 字段便于 Obsidian Dataview 排序。历史"体积云 / SSR"两篇归档到 `99-归档/` 保留。

---

## 写作风格 (2026-07-01 锁定，2026-07-09 加 AI 加速 section)

每篇 shader 案例必须 **双轨交付**：

1. **可跑代码** — 完整 HLSL/GLSL，能直接拷进项目，配合参数面板就能跑出效果
2. **概念拆解** — 为什么这样写、为什么这个参数、为什么这样降级，把"手感"也写下来

**只给代码不给推导 = 没灵魂；只给推导不给代码 = 用不上。**

> 2026-07-09 加：UE 硬技术（Lumen / Nanite / VSM）三篇末尾追加 **"AI 加速角度"** section，描述该特性如何被神经网络改造、对应 day-job RAG 工具描述。这是 day-job 主线（神经材质 / 神经 BRDF / 神经降噪 DLSS 风格）的核心数据源。

---

## 主题优先级 (2026-07-09 锁定)

按 `feat` 优先级（高→低）排列：

| 优先级 | 主题 | 状态 | 类别 | day-job 关联 |
|--------|------|------|------|--------------|
| **P0** | Lumen 反射降级 | ✅ W3 + AI 加速 | UE 硬技术 | 神经反射 lookup |
| **P0** | Lumen GI 漫反射 | ✅ W4 + AI 加速 | UE 硬技术 | 神经 GI / NRC |
| **P0** | Nanite 材质管线 | ✅ W5 + AI 加速 | UE 硬技术 | 神经材质参数化 |
| **P0** | VSM Virtual Shadow Map | ✅ W6 + AI 加速 | UE 硬技术 | 神经阴影降噪 |
| **P0 神经** | 神经材质 NeuralPBR | ✅ W1 | AI 神经材质 | **day-job 主线 1** |
| **P0 神经** | 神经 BRDF NeuralGGX | ✅ W2 | AI 神经 BRDF | **day-job 主线 2** |
| **P0 神经** | DLSS 神经超分 + 时域重建 | ✅ W7 | AI 神经降噪 DLSS | **day-job 主线 3** |
| **P1** | 神经降噪 RT Denoiser | ✅ W8 | AI 神经降噪 | day-job 副线 |
| **P1** | 神经辐射缓存 Neural Radiance Cache | ✅ W9 | AI 神经 GI | day-job 副线 |
| **P2** | UE5.6 / UE5.7 新 feature（SM5/6 差异） | 持续 | UE 跟踪 | 工具链 |

> **引擎范围**：Unreal + Godot 优先，Unity 例外（除非有 UE/Godot 对照）。
>
> **day-job 适配（2026-07-09 锁定）**：5 篇 AI shader（W1/W2/W7/W8/W9）+ 4 篇 UE 硬技术带 AI 加速 section（W3/W4/W5/W6）= 9 篇 case study 完全覆盖 day-job 三件套（神经材质 / 神经 BRDF / 神经降噪 DLSS 风格）。

---

## 收集策略

Shader 是需要手感的技能。本库记录：

1. **自己写的** — 带完整代码和参数解释
2. **网上看到的优秀案例** — 注明来源，分析为什么好
3. **工作中复用的** — 可快速拷贝的片段

---

## 目录结构（按周组织）

```
03-Shader与特效案例集/
├── 00-README.md                       # 本文件
├── TODO-Shader-案例队列.md              # 工作队列
├── W1/                                # 神经材质 NeuralPBR (P0 神经)
├── W2/                                # 神经 BRDF NeuralGGX (P0 神经)
├── W3/                                # Lumen 反射降级 + AI 加速 (P0 硬)
├── W4/                                # Lumen GI 漫反射 + AI 加速 (P0 硬)
├── W5/                                # Nanite 材质管线 + AI 加速 (P0 硬)
├── W6/                                # VSM Virtual Shadow Map + AI 加速 (P0 硬)
├── W7/                                # DLSS 神经超分 + 时域重建 (P0 神经)
├── W8/                                # 神经降噪 RT Denoiser (P1)
├── W9/                                # 神经辐射缓存 NRC (P1)
└── 99-归档/                            # 历史归档
    ├── 体积云-Volumetric-Cloud.md       # W1 历史版
    └── 屏幕空间反射-SSR.md              # W2 历史版
```

---

## 案例记录标准

每个案例必须包含：

1. **效果截图** — 正面/反面教材都要有
2. **核心 HLSL/GLSL 代码** — 注释清晰
3. **参数解释** — 每个 uniform 的含义和推荐范围
4. **性能分级** — 移动端能用吗？需要降采样吗？
5. **变体版本** — 低配/高配两种实现
6. **已知问题与限制** — 6 条起步
7. **调参 SOP** — 7 步起步（按踩坑顺序）

> UE 硬技术（W3/W4/W5/W6）+ AI shader（W1/W2/W7/W8/W9）额外加 **"AI 加速角度"** 或 **"与 day-job RAG 的关联"** section，对应 day-job 训练数据生成路径。

---

## 标签体系

| 标签 | 含义 |
|------|------|
| `#shader/AI` | AI 神经 shader（神经网络推理） |
| `#shader/AI-accelerated` | UE 硬技术追加 AI 加速 section |
| `#shader/post-process` | 后处理效果 |
| `#shader/pbr` | PBR 材质 |
| `#shader/volumetric` | 体积效果（云、雾、光） |
| `#shader/compute` | 计算着色器 |
| `#shader/vertex` | 顶点/几何阶段 |
| `#shader/performance` | 含性能优化讨论 |
| `#shader/自研` | 自己从零写的 |
| `#shader/参考` | 从外部学习/改编的 |
| `#shader/UE` | UE 材质/HLSL |
| `#shader/lumen` | Lumen 相关 |
| `#shader/nanite` | Nanite 相关 |
| `#shader/virtual-geometry` | 虚拟几何（Nanite / VSM） |
| `#shader/shadow` | 阴影相关 |
| `#shader/denoise` | 降噪 |
| `#shader/temporal` | 时域重建 |
| `#shader/GI` | 全局光照 |
| `#shader/BRDF` | BRDF |
| `#shader/PBR` | PBR 材质 |
| `#shader/material` | 材质 |
| `#shader/neural-network` | 神经网络 |
| `#shader/upsample` | 超采样 |
| `#shader/raytracing` | 光线追踪 |

---

## 快速链接

- [[99-Templates/Shader案例]] — 新建案例模板
- [[01-论文笔记库]] — 论文中的渲染技术转化为 Shader
- [[04-性能优化备忘录]] — Shader 性能陷阱记录
- [[W1/神经材质-NeuralPBR]] — day-job 神经材质主线入口
- [[W2/神经BRDF-NeuralGGX]] — day-job 神经 BRDF 主线入口
- [[W7/DLSS-神经超分-时域重建]] — day-job 神经降噪 DLSS 主线入口
- [[99-归档/体积云-Volumetric-Cloud]] — 历史归档
- [[99-归档/屏幕空间反射-SSR]] — 历史归档

---

## 手感维持计划（按周次）

| 周 | 主题 | 类别 | 完成 | 质量自评 |
|----|------|------|------|----------|
| W1 | 神经材质 NeuralPBR | AI 神经材质 | ✅ 2026-07-09 | 优 |
| W2 | 神经 BRDF NeuralGGX | AI 神经 BRDF | ✅ 2026-07-09 | 优 |
| W3 | Lumen 反射降级 + AI 加速 | UE 硬技术 | ✅ 2026-07-01 + 2026-07-09 | 优 |
| W4 | Lumen GI 漫反射 + AI 加速 | UE 硬技术 | ✅ 2026-07-01 + 2026-07-09 | 优 |
| W5 | Nanite 材质管线 + AI 加速 | UE 硬技术 | ✅ 2026-07-02 + 2026-07-09 | 优 |
| W6 | VSM Virtual Shadow Map + AI 加速 | UE 硬技术 | ✅ 2026-07-09 | 优 |
| W7 | DLSS 神经超分 + 时域重建 | AI 神经降噪 DLSS | ✅ 2026-07-09 | 优 |
| W8 | 神经降噪 RT Denoiser | AI 神经降噪 | ✅ 2026-07-09 | 优 |
| W9 | 神经辐射缓存 NRC | AI 神经 GI | ✅ 2026-07-09 | 优 |
| 历史 W1 | 体积云 Volumetric Cloud | 历史经典 | ✅ 2025-01-07 → 99-归档 |
| 历史 W2 | 屏幕空间反射 SSR | 历史经典 | ✅ 2026-07-01 → 99-归档 |

> W3-W5 原文件保留，仅在末尾追加 "AI 加速角度" section（2026-07-09）。
> 历史 W1/W2 归档到 `99-归档/`，保留为传统实现对照。

---

*Last updated: 2026-07-09 (按周次重组 + day-job 三件套 AI shader 落盘)*