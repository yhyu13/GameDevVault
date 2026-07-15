# 📋 Shader 案例工作队列 (TODO)

> 配合 `00-README.md` 的 "主题优先级" 使用。本文件按 C01~C16 案例号 + P1/P2 持续项 顺序记录待写 / 进行中 / 已完成 的案例。
>
> **2026-07-15 重大更新**：
> 1. 编号从 A/B/C/D + W# 改为 **C01~C16 案例号**（与目录同步）
> 2. 7 个新 AI shader 案入列：C10-C16 (3DGS / 神经SDF / 神经BSSRDF / 神经头发 / SD→PBR / 神经体积云 / 神经SSR)
> 3. 关闭 gap：原 TODO 的 P2 W3=程序化地形 / W4=各向异性头发 被 C13 (神经各向异性头发) 吸收 + 99-归档 体积云/SSR 被 C15/C16 神经化重做
>
> **维护规则**：
> - 每完成一篇，把对应行的 ☐ 改成 ☑，并把完成日期补到 "完成" 列
> - 启动新案例前，先翻本队列确认是否有更高优先级未做
> - 中途打断时，在 "备注" 列写当前进度，下一个 session 接续

---

## 队列总览 (P0 优先, C01 → C16)

| 案例号 | 主题 | 优先级 | 状态 | 完成 | 文件路径 | 备注 |
|--------|------|--------|------|------|----------|------|
| C01 | **神经材质 NeuralPBR** (从图像预测 PBR 参数) | P0 神经 | ☑ 完成 | 2026-07-09 | `C01/神经材质-NeuralPBR.md` | day-job 主线 1 (35.4 KB / 783 行) |
| C02 | **神经 BRDF NeuralGGX** (MLP 拟合 GGX/Disney BRDF) | P0 神经 | ☑ 完成 | 2026-07-09 | `C02/神经BRDF-NeuralGGX.md` | day-job 主线 2 (33.2 KB / 771 行) |
| C03 | **Lumen 反射降级** (SSR → Screen Probe → Surface Cache → HW RT) | P0 硬 | ☑ 完成 | 2026-07-01 + 2026-07-09 | `C03/Lumen-反射降级.md` | 4 档降级 + AI 增强 (34.8 KB / 742 行) |
| C04 | **Lumen GI 漫反射** (Surface Cache + Voxel Cone Tracing) | P0 硬 | ☑ 完成 | 2026-07-01 + 2026-07-09 | `C04/Lumen-GI-漫反射.md` | 户外/室内两套参数 (35.2 KB / 806 行) |
| C05 | **Nanite 材质管线** (虚拟几何 + Material AtributeId + Persistent Buffer) | P0 硬 | ☑ 完成 | 2026-07-02 + 2026-07-09 | `C05/Nanite-材质管线.md` | 5-bin 分类 + WorkGraph 路径 (36.3 KB / 789 行) |
| C06 | **VSM Virtual Shadow Map** (页表 + Moments + Moment Bias) | P0 硬 | ☑ 完成 | 2026-07-09 | `C06/VSM-Virtual-Shadow-Map.md` | 与 CSM 对照 (33.4 KB / 763 行) |
| C07 | **DLSS 神经超分 + 时域重建** (TAA-Upsample + Neural Net) | P0 神经 | ☑ 完成 | 2026-07-09 | `C07/DLSS-神经超分-时域重建.md` | day-job 主线 3 (32.1 KB / 771 行) |
| C08 | **神经降噪 RT Denoiser** (NRD 4 阶段降噪) | P1 神经 | ☑ 完成 | 2026-07-09 | `C08/神经降噪-RT-Denoiser.md` | NRD 4 阶段 + history clamp (34.7 KB / 876 行) |
| C09 | **神经辐射缓存 NRC** (MLP 编码 GI + Frequency Encoding) | P1 神经 | ☑ 完成 | 2026-07-09 | `C09/神经辐射缓存-Neural-Radiance-Cache.md` | Lumen GI 的 AI 替代 (34.2 KB / 832 行) |
| **C10** | **3D Gaussian Splatting 实时渲染** (3DGS → 实时 splat shader) | **P0 神经** | ☐ 待做 | — | `C10/3DGS-实时渲染.md` (待建) | **day-job 关键** — 技术雷达 3DGS P0, 现成引擎 3DGS Renderer / gsplat 源码可参考 |
| **C11** | **神经 SDF / Neural Implicit Surfaces** (DeepSDF / NeRF) | **P0 神经** | ☐ 待做 | — | `C11/神经SDF-Neural-Implicit.md` (待建) | 虚拟几何 / Nanite 替代路线 |
| **C12** | **神经 BSSRDF / 皮肤** (BSSRDF 公式 → MLP) | **P1 神经** | ☐ 待做 | — | `C12/神经BSSRDF-皮肤.md` (待建) | 角色渲染主流方案 |
| **C13** | **神经各向异性头发** (Marschner + MLP 拟合散射) | **P1 神经** | ☐ 待做 | — | `C13/神经各向异性头发.md` (待建) | 替换原 P2 W4 计划 |
| **C14** | **实时 AI 纹理生成** (Stable Diffusion → PBR 材质) | **P1 神经** | ☐ 待做 | — | `C14/AI纹理生成-SD-PBR.md` (待建) | day-job RAG 工具链 — Material GPT / MatAtlas 思路 |
| **C15** | **神经体积云** (Neural Volumetric — NeRF 路径) | **P2 神经** | ☐ 待做 | — | `C15/神经体积云.md` (待建) | 替换 99-归档 体积云 (历史 W1) |
| **C16** | **神经 SSR** (NeRF-based reflection lookup) | **P2 神经** | ☐ 待做 | — | `C16/神经SSR.md` (待建) | 替换 99-归档 SSR (历史 W2) |
| P1 | **Mass / NNE / PCG** (UE5 AI 系统) | P1 系统 | ☐ 待做 | — | 不入 C 编号 (集群专题) | UE5 AI 框架, 非 shader |
| P1 | **UE5.6 / UE5.7 新 feature** (SM5/6 差异) | P1 持续 | ☐ 持续 | — | 不入 C 编号 (工具链) | 长期跟踪 |
| P2 | **程序化地形** (噪声 + 顶点动画) | P2 历史 | ⊗ 取消 | — | 合并到 C15 神经体积云路线 | 已被 C15 覆盖 |
| P2 | **各向异性头发** (Marschner 模型) | P2 历史 | ⊗ 取消 | — | 合并到 C13 神经各向异性头发 | 已被 C13 覆盖 |

---

## 完成历史

| 案例号 | 主题 | 完成日 | 文件 |
|--------|------|--------|------|
| C01 | 神经材质 NeuralPBR | 2026-07-09 | `C01/神经材质-NeuralPBR.md` |
| C02 | 神经 BRDF NeuralGGX | 2026-07-09 | `C02/神经BRDF-NeuralGGX.md` |
| C03 | Lumen 反射降级 | 2026-07-01 + 2026-07-09 (AI 增强) | `C03/Lumen-反射降级.md` |
| C04 | Lumen GI 漫反射 | 2026-07-01 + 2026-07-09 (AI 增强) | `C04/Lumen-GI-漫反射.md` |
| C05 | Nanite 材质管线 | 2026-07-02 + 2026-07-09 (AI 增强) | `C05/Nanite-材质管线.md` |
| C06 | VSM Virtual Shadow Map | 2026-07-09 | `C06/VSM-Virtual-Shadow-Map.md` |
| C07 | DLSS 神经超分 + 时域重建 | 2026-07-09 | `C07/DLSS-神经超分-时域重建.md` |
| C08 | 神经降噪 RT Denoiser | 2026-07-09 | `C08/神经降噪-RT-Denoiser.md` |
| C09 | 神经辐射缓存 NRC | 2026-07-09 | `C09/神经辐射缓存-Neural-Radiance-Cache.md` |
| 历史 W1 | 体积云 Volumetric Cloud | 2025-01-07 | `99-归档/体积云-Volumetric-Cloud.md` |
| 历史 W2 | 屏幕空间反射 SSR | 2026-07-01 | `99-归档/屏幕空间反射-SSR.md` |

---

## Gap 关闭说明 (2026-07-15)

之前 (老 TODO) 的悬空 / 漂移项处理：

| 老编号 | 老主题 | 新编号 | 处理 |
|--------|--------|--------|------|
| D | VSM | C06 | ✅ 已完成 |
| E | Mass / NNE / PCG | P1 系统 | ☐ 保留, 标"非 shader"不占 C 编号 |
| F | UE5.6 / UE5.7 新 feature | P1 持续 | ☐ 保留, 标"长期跟踪" |
| G | W3 程序化地形 | C15 神经体积云 | ⊗ 取消, 合并到 C15 |
| H | W4 各向异性头发 | C13 神经各向异性头发 | ⊗ 取消, 合并到 C13 |
| (无) | — | C10 3DGS | ➕ 新增 (day-job P0 关键) |
| (无) | — | C11 神经 SDF | ➕ 新增 (虚拟几何补位) |
| (无) | — | C12 神经 BSSRDF | ➕ 新增 (角色渲染) |
| (无) | — | C14 AI 纹理生成 | ➕ 新增 (day-job RAG 工具链) |
| (无) | — | C16 神经 SSR | ➕ 新增 (替换 99-归档 SSR) |

**新 7 个待做 AI shader 案按 day-job 关键度排序**：
1. C10 3DGS — **最高优**, 直接对应技术雷达 P0
2. C11 神经 SDF — Nanite 替代路线, 未来 LLM 可能调用
3. C12 神经 BSSRDF — 角色渲染刚需
4. C13 神经各向异性头发 — 角色渲染刚需
5. C14 AI 纹理生成 — day-job 工具链 (Material GPT 思路)
6. C15 神经体积云 — 经典案例的 AI 升级
7. C16 神经 SSR — 经典案例的 AI 升级

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
3. **4 个初学者 section**（2026-07-09 加）：
   - 概念链（业务痛点 → 传统局限 → 神经解法 → 落地路径）
   - 代码逐行讲解（意图表格 + 关键参数 + 边界条件）
   - 指标手册（CVar 全展开 + 反直觉误用）
   - 常见误读（5 条初学者陷阱）

> 只给代码不给推导 = 没灵魂；只给推导不给代码 = 用不上。

引擎范围：Unreal + Godot 优先，Unity 例外（除非有 UE/Godot 对照）。

---

*Last updated: 2026-07-15 (C10-C16 新案入列 + 关闭 gap + 编号 A/B/C/D → C01-C16 重组)*
