---
tags: [routine/milestone, milestone/lumen-perf, plan/active, milestone/m5, engine/unreal, source/待精读]
aliases: [Lumen 性能分析, Lyra-Lumen-Profile, Lyra-Lumen-Perf, M5-Lumen-Perf]
---

# M5 — Lyra 场景下 Lumen 全局光照性能分析

> 90 天 milestones 中 M5（60 天阶段）的具体落地：用 **Lyra** 作为真实测试场景，对 **Lumen 全局光照**做端到端性能分析。
> 测试项目：Lyra（`LyraGame`）
> 工具栈：Unreal Insights（CPU/GPU/Memory 三轨）+ `r.Lumen.*` 控制台调参 + RenderDoc（可选）

---

## 为什么是 Lyra + Lumen

- Lumen 是 UE5 全局光照的代表实现，工作项目大概率会用到
- Lyra 是 Epic 官方 sample，规模适中、公开可获取，是合格的 benchmark 场景
- 对应 [[../../00-README|90 天 milestones]] M5 的硬指标：CPU + GPU + Memory 三轨跑通 + 至少定位一个真实瓶颈 + 给出可执行优化方案
- 与 [[../../../AI-Tasks/Lumen/00-Master-Index|Routine/AI-Tasks/Lumen]] 输入侧资料直接衔接

---

## 范围

### 测什么
- **Lumen 模块**：`LumenScene` / `LumenSurfaceCache` / `LumenRadianceCache` / `LumenScreenProbeGather` / `LumenHardwareRayTracing` / `MeshCardRepresentation`
- **渲染管线**：RenderThread / RHIThread / GPU 各 Pass 分布

### 不测什么
- 不做整帧 100% 优化——只聚焦 Lumen 相关 Pass
- 不深入 Lumen 源码（这是 profile 任务，不是源码分析任务 → 那部分走 [[../../../02-引擎源码分析库]]）
- 不扩展到 Nanite、虚拟阴影、Lumen 反射等周边系统（除非 trace 数据指向它们）

### 测试场景（候选）
- `L_Expanse`（户外大场景，GI 负载重）
- `L_Sandbox`（小场景对照）
- 同地图两版本：默认 Lumen vs Lumen 关（屏幕空间 GI 兜底）→ 做 diff

---

## 工具栈

| 工具 | 用途 | 关键命令/参数 |
|------|------|--------------|
| Unreal Insights | CPU + GPU + Memory 三轨 | `Trace.Start cpu,gpu,memory,frame,bookmark` |
| `stat unit` / `stat gpu` | 实时快速检查 |  |
| `r.Lumen.*` 控制台 | 切 Lumen 内部参数 | `r.Lumen.TraceDistance`、`r.Lumen.ScreenProbeGather.RadianceCache.ProbeResolution` |
| RenderDoc | 单帧捕获 + Draw Call 检查（可选） |  |
| `csv profiler` | 长时统计导出 |  |

### Lyra 端准备
- Project Settings → Engine → Rendering → 启用 Lumen（默认已启用）
- Insights channels 全勾上
- 关 vsync、关 frame rate cap，让 profile 数据稳定

---

## 行动步骤

### Phase 1：环境与基线（Day 1-2）
- [ ] 拉 Lyra：`Generate Project Files` + build（Development Editor + Test）
- [ ] 跑 `L_Expanse`，记录 baseline：CPU / RT / RHI / GPU 各轨平均帧时间
- [ ] 跑 5 分钟 gameplay（AI 移动 + 武器开火），记录 trace
- [ ] 输出 → `01-baseline.md`：平均帧时间、最大帧时间、瓶颈初步定位

### Phase 2：Lumen Pass 调参（Day 3-7）
- [ ] Insights GPU track 过滤 Lumen 相关 Pass（搜 `Lumen*` / `ScreenProbe*`）
- [ ] 切 `r.Lumen.TraceDistance` = 1m / 10m / 100m 三档，记录 trace diff
- [ ] 切 `r.Lumen.ScreenProbeGather.RadianceCache.ProbeResolution` = 32 / 64 / 128 三档
- [ ] 输出 → `02-lumen-tuning.md`：每档 CPU/GPU 开销表 + 视觉质量变化描述

### Phase 3：内存分析（Day 8-10）
- [ ] Insights Memory track 跟踪 `LumenScene` 增长、`LumenSurfaceCache` 大小
- [ ] 长时游玩（>30 分钟），观察泄漏 / 持续增长
- [ ] 输出 → `03-memory.md`：稳态内存分布 + 异常项

### Phase 4：综合分析（Day 11-14）
- [ ] 把 Phase 1-3 合成 1 页综合分析 → `99-final-analysis.md`
- [ ] 必须包含：
  - Lumen 在 Lyra 场景下的典型瓶颈（哪些 Pass / 哪些参数）
  - 硬件 RT Lumen vs 软件 fallback 对比（如硬件支持）
  - 可落地的优化建议（参数调整 / Pass 关闭 / 场景光照改造）
  - 工作项目中可借鉴的点（不一定直接套用）

---

## 交付物

| 内容 | 落点 |
|------|------|
| Baseline 测量 | `../../../04-性能优化备忘录/瓶颈分析/Lyra-Lumen-Baseline-<日期>.md` |
| Lumen 调参分析 | `../../../04-性能优化备忘录/瓶颈分析/Lyra-Lumen-Tuning-<日期>.md` |
| 内存分析 | `../../../04-性能优化备忘录/瓶颈分析/Lyra-Lumen-Memory-<日期>.md` |
| 综合分析 | `../../../04-性能优化备忘录/瓶颈分析/Lyra-Lumen-Final-Analysis-<日期>.md` |
| 配套源码分析（如深入到 Lumen 源码） | `../../../02-引擎源码分析库/Unreal-Engine/UE5-Lumen-<子系统>.md` |

---

## 成功标准

- [ ] CPU + GPU + Memory 三轨全跑过
- [ ] 至少定位一个真实瓶颈（不是猜，是 trace 数据指向）
- [ ] 综合分析笔记 ≥ 1 页，含 trace 截图 / 数据表
- [ ] ≥ 3 条可落地的优化建议
- [ ] vault 里新增 tag 至少 `perf/复现` 或 `perf/已应用到项目`

---

## AI 辅助度

| 步骤 | AI 辅助度 | 正确用法 | 禁止行为 |
|------|----------|---------|----------|
| Insights 启动 / 配置 | ★★★★☆ | AI 给命令清单，你执行 | 不理解就复制 |
| 数据收集 | ☆☆☆☆☆ | **你自己跑** | 让 AI 替你跑 profile |
| 数据解读 | ★★★☆☆ | 你贴 trace 摘要，AI 给解读假设；你自己用 Insights UI 验证 | 不验证就采纳 |
| 优化建议生成 | ★★★☆☆ | AI 扩展选项，你评估 GPU 成本 | 直接 copy AI 建议 |
| 写笔记 | ★★☆☆☆ | 你写主体，AI 润色结构 | AI 替你写技术内容 |

完整 AI 辅助判定见 [[../../../References/AI-Augmentation-Reference]]。

---

## 周日晚自查

- [ ] 本周 trace 数据是否已导出 / 备份
- [ ] 是否亲手在 Insights UI 里看过每张关键 trace（不是只看 AI 总结）
- [ ] 当前 Phase 的 [ ] 是否至少勾上 30%
- [ ] 输出笔记是否已 commit 到 vault

---

## 关联

- [[../../00-README|90 天 milestones 总入口]] —— 本 milestone 属于 M5（60 天阶段）
- [[../../../AI-Tasks/Lumen/00-Master-Index|Lumen AI 任务总览]] —— 输入侧资料准备
- [[../../../References/AI-Augmentation-Reference|AI 辅助学习参考]]
- [Lyra 官方仓库](https://github.com/EpicGames/LyraStarterGame)
- [Lumen 技术文档](https://docs.unrealengine.com/5.0/en-US/lumen-global-illumination-and-reflections-in-unreal-engine/)

---

*Created by AI (Mavis) on 2026-06-24*  
*Status: ready to start*