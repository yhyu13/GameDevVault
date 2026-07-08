# 📋 Shader 案例工作队列 (TODO)

> 配合 `00-README.md` 的 "主题优先级" 使用。本文件按 P0 → P1 顺序记录待写 / 进行中 / 已完成 的案例。
>
> **2026-07-09 大重构**：目录按 W1~W9 周次组织（不再按 后处理效果/反射效果/...）。5 篇 AI shader + 4 篇 UE 硬技术（带 AI 加速 section）= 9 篇完成，覆盖 day-job 三件套（神经材质 / 神经 BRDF / 神经降噪 DLSS 风格）。
>
> **维护规则**：
> - 每完成一篇，把对应行的 ☐ 改成 ☑，并把完成日期补到 "完成" 列
> - 启动新案例前，先翻本队列确认是否有更高优先级未做
> - 中途打断时，在 "备注" 列写当前进度，下一个 session 接续

---

## 队列总览 (P0 优先, A → B → C → ... → H)

| 序 | 主题 | 优先级 | 状态 | 完成 | 文件路径 | 备注 |
|----|------|--------|------|------|----------|------|
| A | **Lumen 反射降级** (SSR → Screen Probe → Surface Cache → HW RT) | P0 | ☑ 完成 | 2026-07-01 + 2026-07-09 | `W3/Lumen-反射降级.md` | 接 W2 SSR；演进链路；2026-07-09 追加 AI 加速 section |
| B | **Lumen GI 漫反射** (Surface Cache + Voxel Cone Tracing) | P0 | ☑ 完成 | 2026-07-01 + 2026-07-09 | `W4/Lumen-GI-漫反射.md` | 户外 / 室内两套参数；2026-07-09 追加 NRC 替代方案 |
| C | **Nanite 材质管线** (虚拟几何 + Material AtributeId + Persistent Buffer) | P0 | ☑ 完成 | 2026-07-02 + 2026-07-09 | `W5/Nanite-材质管线.md` | FNaniteShadingPipeline 去重 + 5-bin + UE5.8 WorkGraph；2026-07-09 追加 Neural Material Eval |
| D | **VSM Virtual Shadow Map** (页表 + Moments + Moment Bias) | P0 | ☑ 完成 | 2026-07-09 | `W6/VSM-Virtual-Shadow-Map.md` | 与 CSM 对照 + 5 性能档 + Neural Variance Filter |
| E | **DLSS 神经超分 + 时域重建** (NSR, 神经降噪 DLSS 风格) | P0 神经 | ☑ 完成 | 2026-07-09 | `W7/DLSS-神经超分-时域重建.md` | 替原 Mass/NNE/PCG；Halton jitter + 5x5 Feature + MLP forward |
| F | **神经材质 NeuralPBR** (图像预测 PBR 4 通道) | P0 神经 | ☑ 完成 | 2026-07-09 | `W1/神经材质-NeuralPBR.md` | 替原 体积云；U-Net 离线训练 + 实时推理 |
| G | **神经降噪 RT Denoiser** (NRD / OIDN / SVGF) | P1 | ☑ 完成 | 2026-07-09 | `W8/神经降噪-RT-Denoiser.md` | 替原 程序化地形；4 stage pipeline + 神经 blend weight |
| H | **神经 BRDF NeuralGGX** (神经网络拟合 GGX/Disney) | P0 神经 | ☑ 完成 | 2026-07-09 | `W2/神经BRDF-NeuralGGX.md` | 替原 SSR；5→64→64→64→3 MLP + 离线训练 |
| (H+) | **神经辐射缓存 NRC** (NeRF 替代 Surface Cache) | P1 | ☑ 完成 | 2026-07-09 | `W9/神经辐射缓存-Neural-Radiance-Cache.md` | 替原 各向异性头发；8 layer MLP + frequency encoding |
| I | **UE5.6 / UE5.7 新 feature** (SM5/6 差异) | P1 | ☐ 持续 | — | 待拆 | 长期跟踪 |

---

## 完成历史（按完成日逆序）

| 周次 | 主题 | 完成日 | 文件 | 类别 |
|------|------|--------|------|------|
| 历史 W1 | 体积云 Volumetric Cloud | 2025-01-07 | `99-归档/体积云-Volumetric-Cloud.md` | 历史经典（已归档） |
| 历史 W2 | 屏幕空间反射 SSR | 2026-07-01 | `99-归档/屏幕空间反射-SSR.md` | 历史经典（已归档） |
| A / W3 | Lumen 反射降级 | 2026-07-01 | `W3/Lumen-反射降级.md` | UE 硬技术 |
| B / W4 | Lumen GI 漫反射 | 2026-07-01 | `W4/Lumen-GI-漫反射.md` | UE 硬技术 |
| C / W5 | Nanite 材质管线 | 2026-07-02 | `W5/Nanite-材质管线.md` | UE 硬技术 |
| F / W1 | 神经材质 NeuralPBR | 2026-07-09 | `W1/神经材质-NeuralPBR.md` | AI 神经材质 |
| H / W2 | 神经 BRDF NeuralGGX | 2026-07-09 | `W2/神经BRDF-NeuralGGX.md` | AI 神经 BRDF |
| (W3-W5 AI) | Lumen / Nanite AI 加速追加 | 2026-07-09 | W3-W5 各文件末尾 | UE 硬技术 + AI |
| D / W6 | VSM Virtual Shadow Map | 2026-07-09 | `W6/VSM-Virtual-Shadow-Map.md` | UE 硬技术 |
| E / W7 | DLSS 神经超分 + 时域重建 | 2026-07-09 | `W7/DLSS-神经超分-时域重建.md` | AI 神经降噪 DLSS |
| G / W8 | 神经降噪 RT Denoiser | 2026-07-09 | `W8/神经降噪-RT-Denoiser.md` | AI 神经降噪 |
| H+ / W9 | 神经辐射缓存 NRC | 2026-07-09 | `W9/神经辐射缓存-Neural-Radiance-Cache.md` | AI 神经 GI |

---

## 中途恢复指引

如果一个 session 没写完就断了：

1. 打开本文件，看哪行是 "进行中" 状态
2. 读对应路径下正在写的文件（一般文件末尾会有 `// TODO: continue here` 标记）
3. 接续写完后，更新本文件：状态 → ☑ 完成，补完成日
4. 写 README 的 "主题优先级" 表格对应行同步勾选

---

## 写作风格硬约束 (来自 README)

每篇必须 **双轨交付**：

1. **可跑代码** — 完整 HLSL/GLSL，能直接拷进项目，配合参数面板就能跑出效果
2. **概念拆解** — 为什么这样写、为什么这个参数、为什么这样降级，把"手感"也写下来

> 只给代码不给推导 = 没灵魂；只给推导不给代码 = 用不上。

**UE 硬技术（W3/W4/W5/W6）** 末尾追加 **"AI 加速角度"** section，描述：
- 该特性如何被神经网络改造（L1/L2/L3 三层次）
- 与 day-job RAG 工具描述的对应关系
- 已知问题与限制（AI 加速版）

**AI shader（W1/W2/W7/W8/W9）** 加 **"与 day-job RAG 的关联"** section，描述：
- 工具描述模板（喂给 LLM 的 RAG 索引）
- SFT 数据生成路径（如何训练 + 时长）
- RAG 检索应用场景（用户问什么 → LLM 答什么）

引擎范围：Unreal + Godot 优先，Unity 例外（除非有 UE/Godot 对照）。

---

*Last updated: 2026-07-09 (按周次重组 + day-job 三件套 AI shader 落盘 + W3-W5 AI 加速追加)*