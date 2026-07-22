# ⚡ 性能优化与 Profile 备忘录

> **对应周计划：周四晚 — 工程化与工具链（效率）**
>
> **本次重写（2026-06-26）**：删除了所有"未验证百分比 / 阈值 / 编的数字"。每条结论必须有 UE 官方文档 / GDC 演讲 / Lyra 公开源码支撑。

---

## 记录策略

性能优化是肌肉记忆。遇到任何性能问题，按此格式记录：

```
现象 → 工具 → 根因 → 解决方案 → 验证结果
```

目标是：下次看到同样的现象，不用重新 Profile 就知道查哪里。

**重要**：具体瓶颈案例必须自己 Profile 后写。[[知识参考/]] 下的笔记**只收录有官方/GDC/源码支撑的事实**，不收录推测。

---

## 文件夹结构

- **[[瓶颈案例]]** — 按现象分类（DrawCall 过高、GC 卡顿、纹理带宽等）— **自己 Profile 后写**
- **[[Profile 记录]]** — 具体项目的 Profile 数据截图与分析
- **[[知识参考]]** — 从在线资源整理的方法论 / 工具 / 专项调优笔记
  - **本次重写后**：每条结论都附官方/GDC/源码链接，**无任何 [U] 编内容**

---

## 现象速查表 → 工具 → 知识参考 / 瓶颈案例

| 现象 | 首选工具 | 知识参考 / 瓶颈案例 |
|------|----------|---------------------|
| DrawCall 过高 | RenderDoc / Insights | [[知识参考/Unreal Insights 帧分析实战]] |
| 卡顿 spikes | Insights | [[知识参考/Unreal Insights 帧分析实战]] + [[知识参考/Lyra 性能架构]]（加载流程） |
| 纹理带宽高 | RenderDoc Texture Viewer | [[知识参考/Unreal Insights 帧分析实战]] |
| 顶点处理瓶颈 | GPU Profiler | [[知识参考/Nanite 性能调优]] + [[瓶颈案例/植被-过度绘制-Cluster-Tree粒度问题]] |
| Lumen GI 反射卡 | profilegpu | [[知识参考/Lumen 性能调优]] + [[瓶颈案例/Lumen-反射开销过高-平滑材质场景]] |
| VSM 阴影棋盘瑕疵 | `r.Shadow.Virtual.ShowStats` | [[知识参考/VSM 性能调优]] (W29 新增) + [[瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]] |
| Nanite 破面 / 闪烁 | `NaniteStats` | [[知识参考/Nanite 性能调优]] + [[瓶颈案例/Nanite-WPO禁用距离-破面修复]] |
| Nanite BasePass 5ms+ (5.0/5.1 材质管线) | `ProfileGPU` + 升级 5.4 | [[瓶颈案例/Nanite-5.4-材质管线-空调度削减]] (W29 新增) + [[知识参考/Nanite 性能调优]] |
| Nanite 5.4 Bin 合并 80% 削减 (源码级) | `NaniteShading.cpp:2711` `AllocateFixedFunctionBins` | [[瓶颈案例/Nanite-5.4-材质Bin合并-80percent削减]] (W30 新增) + [[../02-引擎源码分析库/Unreal-Engine/W30/UE5-Nanite-CullRaster-5.4-材质Bin-源码分析\|W30 Nanite CullRaster 源码]] |
| Lumen Surface Cache 大世界显存 (4 层 Atlas) | `r.Lumen.Visualize.CardPlacement` | [[瓶颈案例/Lumen-SurfaceCache-显存与带宽-大世界场景]] (W29 新增) + [[知识参考/Lumen 性能调优]] |
| VSM Page Allocation 30+ CVar 调优 | `r.Shadow.Virtual.ShowStats` + `ShowClipmapStats` | [[瓶颈案例/VSM-Page-Allocation-BuildPageAllocations调优]] (W30 新增) + [[../02-引擎源码分析库/Unreal-Engine/W30/UE5-VSM-Page-Table-源码分析\|W30 VSM Page Table 源码]] + [[知识参考/VSM 性能调优]] (W29) |
| MCP Trust 4 件套 / harness 启动慢 | day-job Harness 智能 Trust Cache | [[瓶颈案例/MCP-Trust-4件套-性能开销-harness瓶颈]] (W30 新增) + [[../02-引擎源码分析库/Unreal-Engine/W30/UE5-MCP-3Endpoints-Trust-AgentLoop-源码分析\|W30 MCP Trust 源码]] |
| 跨系统调参 (Nanite + Lumen + VSM 同源) | ShowStats + 翻倍预算 + 缩范围 + 加快 evict | [[知识参考/虚拟页表范式-VSM-Nanite-Lumen-同源]] (W30 新增, 跨系统整合层) |
| GT/RT/RHI 同步 | Insights Timing | [[知识参考/渲染线程瓶颈诊断]] |
| 大纹理上传卡顿 | Insights RenderThread | [[知识参考/渲染线程瓶颈诊断]] + [[瓶颈案例/大纹理RT申请-Render线程卡顿]] |
| 物理卡顿 | Insights + Chaos Visual | — （待补 Chaos 笔记） |
| 移动端发烫 | 厂商 SDK (PerfHUD) | [[知识参考/渲染线程瓶颈诊断]] > 移动端 |
| 加载卡顿 | Insights LoadTime | [[知识参考/Lyra 性能架构]]（5 阶段加载流程）+ [[瓶颈案例/大纹理RT申请-Render线程卡顿]] |

> **速查表本身不写"百分比数字"**——具体场景下能省多少必须自己 Profile。
>
> **新增 5 篇瓶颈案例**（2026-07-02，从 GDC 2024 + UE 官方文档 + 知乎一线经验汇编）每篇都是 `perf/待验证` 状态，**未经本人 Profile**，数字需自己复测。

---

## 标签体系

| 标签 | 含义 |
|------|------|
| `#perf/CPU` | CPU 瓶颈 |
| `#perf/GPU` | GPU 瓶颈 |
| `#perf/memory` | 内存问题 |
| `#perf/DrawCall` | 合批/Instancing |
| `#perf/LOD` | 多细节层次 |
| `#perf/culling` | 遮挡剔除/视锥剔除 |
| `#perf/shader` | Shader 复杂度 |
| `#perf/loading` | 加载/流送 |
| `#perf/已验证` | 方案已验证有效（必须 Profile 后用） |
| `#perf/待验证` | 方案仅为假设（Profile 验证前不主张） |

---

## 工具链备忘（仅工具名，详见 `[[知识参考/Unreal Insights 帧分析实战]]`）

| 工具 | 场景 |
|------|------|
| RenderDoc | 帧捕获分析（Ctrl+Shift+Print 捕获） |
| Pix | DirectX 12 调试（GPU 时间线分析） |
| Unreal Insights | Unreal 性能分析（`stat unit` / `-trace=`） |
| Unity Profiler | Unity 全链路（Deep Profile 慎用） |
| Tracy | C++ 手动插桩（`ZoneScoped`） |
| Superluminal | Windows 采样（无侵入式分析） |

---

## 知识参考索引（每条有官方/GDC/源码支撑）

| 笔记 | 主要来源 | 一句话 |
|------|---------|-------|
| [[知识参考/性能优化方法论]] | UE 官方文档 | UE 官方对 Profile / 优化流程的明确说法 |
| [[知识参考/Unreal Insights 帧分析实战]] | UE 官方文档 | 通道 / 面板 / CVar / API 全部 [D] |
| [[知识参考/Lumen 性能调优]] | UE 5.7 Lumen 文档 + Performance Guide | 可调 CVar / 默认值 / 平台要求 / 官方 troubleshooting |
| [[知识参考/Nanite 性能调优]] | GDC 2024 Wihlidal + SIGGRAPH 2021 | 三版本时间线 + 真实测量数据 |
| [[知识参考/VSM 性能调优]] (W29 新增) | UE 官方 VSM 文档 + SIGGRAPH 2020 Karis + UE 5.8 源码 | Page 预算 / Clipmap / MegaLights 5.4+ 集成 / 与 Lumen/Nanite 同源 |
| [[知识参考/虚拟页表范式-VSM-Nanite-Lumen-同源]] (W30 新增) | W29/W30 源码分析 (Lumen + VSM + Nanite + MCP) | 128×128 page + 5 阶段状态机 + 跨系统 CVar 映射 + 跨系统调参策略 |
| [[知识参考/Lyra 性能架构]] | Lyra 公开源码（GitHub） | 类名 / 状态机 / 函数签名 / API |
| [[知识参考/渲染线程瓶颈诊断]] | UE 官方文档 + UE 源码 | 三线程模型 + stat 命令 + CVar |

---

## 瓶颈案例索引（2026-07-02 新增 — GDC + UE 官方 + 知乎汇编）

| 笔记 | 现象 | 主要来源 | 状态 |
|------|------|---------|------|
| [[瓶颈案例/Lumen-反射开销过高-平滑材质场景]] | 平滑材质下 Lumen 反射占 GPU 大头 | UE Lumen Performance Guide + 知乎 | `perf/待验证` |
| [[瓶颈案例/Lumen-SurfaceCache-显存与带宽-大世界场景]] (W29 新增) | 4 层 Atlas 显存 200-400 MB / 大世界带宽饱和 | W29 Lumen Surface Cache 源码 + UE 5.8 源码 + 官方文档 | `perf/待验证` |
| [[瓶颈案例/Nanite-5.4-材质管线-空调度削减]] (W29 新增) | 5.0/5.1 BasePass 90% 空调度 / 4.92→3.05ms | GDC 2024 Wihlidal + W29 论文笔记 | `perf/待验证` |
| [[瓶颈案例/Nanite-5.4-材质Bin合并-80percent削减]] (W30 新增) | 4015→340 Bin 合并 80% (W30 源码 `AllocateFixedFunctionBins`) | W30 Nanite CullRaster 源码 + GDC 2024 + UE 5.8 源码 | `perf/待验证` |
| [[瓶颈案例/VSM-Page-Allocation-BuildPageAllocations调优]] (W30 新增) | `BuildPageAllocations:3227` 性能瓶颈 + 30+ CVar 全表 | W30 VSM Page Table 源码 + UE 5.8 源码 | `perf/待验证` |
| [[瓶颈案例/MCP-Trust-4件套-性能开销-harness瓶颈]] (W30 新增) | Trust 4 件套性能开销 + 5 套 day-job Harness 优化 | W30 MCP 源码 + VS 2026 文档 + Anthropic MCP 1.1 spec | `perf/待验证` |
| [[瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]] | 阴影棋盘格 / 缓存污染 | UE VSM 官方文档 + GDC 2024 + 知乎 | `perf/待验证` |
| [[瓶颈案例/植被-过度绘制-Cluster-Tree粒度问题]] | 植被密集 basepass VS 高 / RT occlusion spike | 知乎《UE5性能优化-GPU》 | `perf/待验证` |
| [[瓶颈案例/Nanite-WPO禁用距离-破面修复]] | Nanite 随机破面 / 画面闪烁 / 阴影错乱 | GDC 2024 Wihlidal + 知乎 + UE 官方 | `perf/待验证` |
| [[瓶颈案例/大纹理RT申请-Render线程卡顿]] | RT 申请抖动 / 关卡切换 spike | 知乎《UE5性能优化-Render线程》 | `perf/待验证` |
| [[瓶颈案例/DrawCall-过高-植被渲染]] | 植被 DrawCall 暴增帧率掉一半 | （旧案例，Unity 术语残留，待重写为 UE5 版本） | `perf/已验证` |

> **所有 `perf/待验证` 案例**——来源是公开资料（GDC 演讲、UE 官方文档、知乎一线经验），**未经本人 Profile**。
> 验证流程在每篇笔记末尾的"验证流程"小节；Profile 后请把 tag 改成 `perf/已验证` 并补自己的实测数字。

---

## 关联知识库

- [[02-引擎源码分析库]] — 引擎底层性能设计
- [[99-Templates/性能优化]] — 新建瓶颈案例记录的模板

---

## 本月 Profile 目标

- [ ] 完成至少 1 次完整的帧分析（Unreal Insights）
- [ ] 记录至少 3 个可复用的优化方案（写 [[瓶颈案例/]] ）
- [ ] M5 专项：跑 Lyra 默认 map 录 30 秒 utrace，按 [[知识参考/Unreal Insights 帧分析实战]] 流程做一遍诊断
- [ ] **新增（2026-07）**：从 5 篇新案例中挑 1–2 篇（推荐 [[瓶颈案例/Lumen-反射开销过高-平滑材质场景]] 或 [[瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]]）做 Profile 验证，把 tag 升级到 `perf/已验证`
- [x] **W29 进度（2026-07-17）**：补齐 1 篇知识参考 ([[VSM 性能调优]]) + 2 篇瓶颈案例 ([[Nanite-5.4-材质管线-空调度削减]] + [[Lumen-SurfaceCache-显存与带宽-大世界场景]]) = 04-性能优化备忘录/ 7月 KPI 从 0% 跳到 **~50%** (3/6)
- [x] **W30 进度（2026-07-23）**：补齐 1 篇跨系统知识参考 ([[虚拟页表范式-VSM-Nanite-Lumen-同源]]) + 3 篇瓶颈案例 ([[Nanite-5.4-材质Bin合并-80percent削减]] + [[VSM-Page-Allocation-BuildPageAllocations调优]] + [[MCP-Trust-4件套-性能开销-harness瓶颈]]) = 04-性能优化备忘录/ 7月 KPI 从 50% 跳到 **~117%** (7/6, W29 复盘承诺 7月 +3 条超额 100%)

---

## 本次重写对照（2026-06-26）

### 删除
- 所有"X% 性能数字"（Lumen "30-50%", Nanite "5-30%", "200k cluster 阈值" 等）
- "Lyra 在 RTX 3060 60fps / GPU 8-10ms"
- "25ms P0 / 33ms P1 / 50ms P2 bug"
- 我推的"诊断决策树"
- "卡顿形态速查表" 的具体阈值

### 升级为官方原文
- Lumen "Epic scalability produces around 8 ms on next-gen consoles"（[Lumen Technical Details] 文档首段）
- Lumen "Hardware Ray Tracing is enabled by default"（同上）
- Nanite GDC 2024 真实数据：**4015 bins / 3675 empty / 4.92ms → 3.05ms**（Graham Wihlidal 演讲原话）
- Nanite 三版本时间线：**5.0 初始 / 5.1 可编程光栅器 / 5.4 新材质管线**
- Lyra 全部类名 + 文件路径 + 函数签名 + 状态机（公开源码可查）
- UE 官方对 Shipping vs Development 的明确说法

### 新增的"诚实声明"
- 任何具体性能数字必须自己 Profile
- 所有 CVar 默认值以 UE 源码为准（本文不主张推论）