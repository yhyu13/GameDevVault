# 🎨 Shader 与特效案例集

> **对应周计划：周二晚 — 专项技能突破（深度）**
>
> **2026-07-15 调整**：本目录按 **C01~C09 案例号 (Case 01-09)** 组织（不再用 W1~W9 "周次" 编号——历史 W1/W2 跟归档的体积云/SSR 撞号，且 9 篇都是 2026-07-09 同一天落盘，套"周次"不合理）。每篇 case study 是一个独立 `.md`，frontmatter 带 `case: Cn` 字段便于 Obsidian Dataview 排序。历史"体积云 / SSR"两篇归档到 `99-归档/` 保留。
>
> 编号含义：**C = Case**（案例）；数字 = 入库序号，01 是最早入库（神经材质），09 是最近入库（NRC）。

---

## 写作风格 (2026-07-01 锁定，2026-07-09 加 4 个初学者 section)

每篇 shader 案例必须 **双轨交付**：

1. **可跑代码** — 完整 HLSL/GLSL，能直接拷进项目，配合参数面板就能跑出效果
2. **概念拆解** — 为什么这样写、为什么这个参数、为什么这样降级，把"手感"也写下来

**只给代码不给推导 = 没灵魂；只给推导不给代码 = 用不上。**

> 2026-07-09 统一追加 4 个 section：**概念链 / 代码逐行讲解 / 指标手册 / 常见误读**。覆盖"业务痛点 → 传统局限 → 神经解法 → 落地路径"的完整链路。

---

## 主题优先级 (2026-07-15 锁定)

按 `feat` 优先级（高→低）排列：

| 案例号 | 主题 | 状态 | 类别 | day-job 关联 |
|--------|------|------|------|--------------|
| **C01** | 神经材质 NeuralPBR | ✅ | AI 神经材质 | **day-job 主线 1** |
| **C02** | 神经 BRDF NeuralGGX | ✅ | AI 神经 BRDF | **day-job 主线 2** |
| **C03** | Lumen 反射降级 | ✅ + AI 加速 | UE 硬技术 | 神经反射 lookup |
| **C04** | Lumen GI 漫反射 | ✅ + AI 加速 | UE 硬技术 | 神经 GI / NRC |
| **C05** | Nanite 材质管线 | ✅ + AI 加速 | UE 硬技术 | 神经材质参数化 |
| **C06** | VSM Virtual Shadow Map | ✅ + AI 加速 | UE 硬技术 | 神经阴影降噪 |
| **C07** | DLSS 神经超分 + 时域重建 | ✅ | AI 神经降噪 DLSS | **day-job 主线 3** |
| **C08** | 神经降噪 RT Denoiser | ✅ | AI 神经降噪 | day-job 副线 |
| **C09** | 神经辐射缓存 NRC | ✅ | AI 神经 GI | day-job 副线 |
| **C10** | 3D Gaussian Splatting 实时渲染 | ☐ 待做 | AI 神经辐射场 | **day-job P0 关键** (技术雷达 3DGS) |
| **C11** | 神经 SDF / Neural Implicit Surfaces | ☐ 待做 | AI 神经隐式 | 虚拟几何 / Nanite 替代 |
| **C12** | 神经 BSSRDF / 皮肤 | ☐ 待做 | AI 神经材质 | 角色渲染 |
| **C13** | 神经各向异性头发 (Marschner + MLP) | ☐ 待做 | AI 神经材质 | 替换原 P2 H 计划 |
| **C14** | 实时 AI 纹理生成 (Stable Diffusion → PBR) | ☐ 待做 | AI 神经材质 | day-job RAG 工具链 |
| **C15** | 神经体积云 (Neural Volumetric) | ☐ 待做 | AI 神经体积 | 替换历史 99-归档 体积云 |
| **C16** | 神经 SSR (NeRF-based reflection) | ☐ 待做 | AI 神经反射 | 替换历史 99-归档 SSR |
| **P1** | Mass / NNE / PCG (UE5 AI 系统) | ☐ 待做 | UE5 AI 系统 | 非 shader，集群专题 |
| **P1** | UE5.6 / UE5.7 新 feature (SM5/6 差异) | 持续 | UE 跟踪 | 工具链 |
| **P2** | W3 程序化地形 (噪声 + 顶点动画) | 归档/取消 | 历史经典 | 已合并到 C15 神经体积云路线 |
| **P2** | W4 各向异性头发 (Marschner 模型) | 归档/取消 | 历史经典 | 已合并到 C13 神经各向异性头发 |

> **引擎范围**：Unreal + Godot 优先，Unity 例外（除非有 UE/Godot 对照）。
>
> **day-job 适配（2026-07-15 锁定）**：9 篇已完成（C01-C09）+ 7 篇待做（C10-C16 神经化新案）= 16 篇 case study 完全覆盖 day-job 三件套（神经材质 / 神经 BRDF / 神经降噪 DLSS 风格）+ 神经辐射场 / 神经隐式 / 神经 BSSRDF 等补位。
>
> **编号逻辑（2026-07-15 解释）**：
> - C01-C09 = 已落盘（9 篇）
> - C10-C16 = 待做（7 篇 AI shader 新案，按 day-job 关键度排）
> - 老的 W1/W2 = 历史归档的"体积云 / SSR"（在 99-归档/），不再属于主编号序列
> - P1/P2 = 非 shader 专题（Mass/NNE/UE5.6 跟踪/历史经典），不占 C 编号

---

## 收集策略

Shader 是需要手感的技能。本库记录：

1. **自己写的** — 带完整代码和参数解释
2. **网上看到的优秀案例** — 注明来源，分析为什么好
3. **工作中复用的** — 可快速拷贝的片段

---

## 目录结构（按案例号组织）

```
03-Shader与特效案例集/
├── 00-README.md                       # 本文件
├── TODO-Shader-案例队列.md              # 工作队列 (P0-C16 排序)
├── C01/                                # 神经材质 NeuralPBR (AI 神经)
├── C02/                                # 神经 BRDF NeuralGGX (AI 神经)
├── C03/                                # Lumen 反射降级 + AI 加速 (UE 硬)
├── C04/                                # Lumen GI 漫反射 + AI 加速 (UE 硬)
├── C05/                                # Nanite 材质管线 + AI 加速 (UE 硬)
├── C06/                                # VSM Virtual Shadow Map + AI 加速 (UE 硬)
├── C07/                                # DLSS 神经超分 + 时域重建 (AI 神经)
├── C08/                                # 神经降噪 RT Denoiser (AI 神经)
├── C09/                                # 神经辐射缓存 NRC (AI 神经)
├── C10/                                # [待做] 3D Gaussian Splatting 实时渲染
├── C11/                                # [待做] 神经 SDF / Neural Implicit Surfaces
├── C12/                                # [待做] 神经 BSSRDF / 皮肤
├── C13/                                # [待做] 神经各向异性头发
├── C14/                                # [待做] 实时 AI 纹理生成 (Stable Diffusion → PBR)
├── C15/                                # [待做] 神经体积云
├── C16/                                # [待做] 神经 SSR
└── 99-归档/                            # 历史归档
    ├── 体积云-Volumetric-Cloud.md       # 原"历史 W1" 2025-01-07
    └── 屏幕空间反射-SSR.md              # 原"历史 W2" 2026-07-01
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
8. **4 个初学者 section**（2026-07-09 加）：
   - 概念链（业务痛点 → 传统局限 → 神经解法 → 落地路径）
   - 代码逐行讲解（意图表格 + 关键参数 + 边界条件）
   - 指标手册（CVar 全展开 + 反直觉误用）
   - 常见误读（5 条初学者陷阱）

> UE 硬技术（C03/C04/C05/C06）+ AI shader（C01/C02/C07/C08/C09）额外加 **"AI 加速角度"** 或 **"与 day-job RAG 的关联"** section，对应 day-job 训练数据生成路径。

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
| `#shader/3DGS` | 3D Gaussian Splatting |
| `#shader/SDF` | 有符号距离场 / 神经隐式 |
| `#shader/BSSRDF` | 次表面散射 |
| `#shader/hair` | 头发 / 各向异性 |

---

## 快速链接

- [[99-Templates/Shader案例]] — 新建案例模板
- [[01-论文笔记库]] — 论文中的渲染技术转化为 Shader
- [[04-性能优化备忘录]] — Shader 性能陷阱记录
- [[C01/神经材质-NeuralPBR]] — day-job 神经材质主线入口
- [[C02/神经BRDF-NeuralGGX]] — day-job 神经 BRDF 主线入口
- [[C07/DLSS-神经超分-时域重建]] — day-job 神经降噪 DLSS 主线入口
- [[99-归档/体积云-Volumetric-Cloud]] — 历史归档 (原 W1)
- [[99-归档/屏幕空间反射-SSR]] — 历史归档 (原 W2)

---

## 手感维持计划（按案例号）

| 案例号 | 主题 | 类别 | 完成 | 质量自评 |
|--------|------|------|------|----------|
| C01 | 神经材质 NeuralPBR | AI 神经材质 | ✅ 2026-07-09 | 优 |
| C02 | 神经 BRDF NeuralGGX | AI 神经 BRDF | ✅ 2026-07-09 | 优 |
| C03 | Lumen 反射降级 + AI 加速 | UE 硬技术 | ✅ 2026-07-01 + 2026-07-09 | 优 |
| C04 | Lumen GI 漫反射 + AI 加速 | UE 硬技术 | ✅ 2026-07-01 + 2026-07-09 | 优 |
| C05 | Nanite 材质管线 + AI 加速 | UE 硬技术 | ✅ 2026-07-02 + 2026-07-09 | 优 |
| C06 | VSM Virtual Shadow Map + AI 加速 | UE 硬技术 | ✅ 2026-07-09 | 优 |
| C07 | DLSS 神经超分 + 时域重建 | AI 神经降噪 DLSS | ✅ 2026-07-09 | 优 |
| C08 | 神经降噪 RT Denoiser | AI 神经降噪 | ✅ 2026-07-09 | 优 |
| C09 | 神经辐射缓存 NRC | AI 神经 GI | ✅ 2026-07-09 | 优 |
| C10 | 3DGS 实时渲染 | AI 神经辐射场 | ☐ 待做 | — |
| C11 | 神经 SDF | AI 神经隐式 | ☐ 待做 | — |
| C12 | 神经 BSSRDF | AI 神经材质 | ☐ 待做 | — |
| C13 | 神经各向异性头发 | AI 神经材质 | ☐ 待做 | — |
| C14 | Stable Diffusion → PBR | AI 神经材质 | ☐ 待做 | — |
| C15 | 神经体积云 | AI 神经体积 | ☐ 待做 | — |
| C16 | 神经 SSR | AI 神经反射 | ☐ 待做 | — |
| 历史 W1 | 体积云 Volumetric Cloud | 历史经典 | ✅ 2025-01-07 → 99-归档 | — |
| 历史 W2 | 屏幕空间反射 SSR | 历史经典 | ✅ 2026-07-01 → 99-归档 | — |

> C03-C05 原文件保留，仅在末尾追加 "AI 加速角度" section（2026-07-09）。
> 历史 W1/W2 归档到 `99-归档/`，保留为传统实现对照。
> **2026-07-15 编号重组**：W1-W9 全部改 C01-C09，原 W1/W2 = 体积云/SSR 改名为"历史 W1/W2"避免编号冲突。

---

*Last updated: 2026-07-15 (W1-W9 → C01-C09 案例号重组 + C10-C16 AI shader 7 个新案入列)*
