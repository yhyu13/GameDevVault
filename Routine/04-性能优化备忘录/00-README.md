# ⚡ 性能优化与 Profile 备忘录

> **对应周计划：周四晚 — 工程化与工具链（效率）**

---

## 记录策略

性能优化是肌肉记忆。遇到任何性能问题，按此格式记录：

```
现象 → 工具 → 根因 → 解决方案 → 验证结果
```

目标是：下次看到同样的现象，不用重新 Profile 就知道查哪里。

---

## 文件夹结构

- **[[瓶颈案例]]** — 按现象分类（DrawCall 过高、GC 卡顿、纹理带宽等）
- **[[Profile 记录]]** — 具体项目的 Profile 数据截图与分析
- **[[知识参考]]** — 从在线资源整理的方法论 / 工具 / 专项调优笔记（持续扩充）

---

## 现象速查表

| 现象 | 首选工具 | 常见根因 | 解决方案 | 知识参考 |
|------|----------|----------|----------|----------|
| DrawCall 过高 | RenderDoc / Pix | 材质未合批 | GPU Instancing / SRP Batcher | [[Lumen 性能调优]] |
| 卡顿 spikes | Unity Profiler / UE Insights | GC / 同步加载 | 对象池 / 异步加载 | [[Lyra 性能架构]] |
| 纹理带宽高 | RenderDoc Texture Viewer | 纹理过大/未压缩 | ASTC/BC7 压缩、Mipmap | — |
| 顶点处理瓶颈 | GPU Profiler | 模型面数过高 | Nanite / LOD | [[Nanite 性能调优]] |
| Lumen 反射卡 | profilegpu | 反射 Pass 太多 | 降反射质量 / 平面反射替代 | [[Lumen 性能调优]] |
| RT 等 GT 同步 | Insights Timing | RT Pass 慢 | 优化最长的 RT 阶段 | [[渲染线程瓶颈诊断]] |
| 物理卡顿 | Insights + Chaos Visual | 同步物理 | 异步物理 / LOD 碰撞 | — |
| 移动端发烫 | 厂商 SDK (PerfHUD) | GPU 持续满 | 降分辨率 / 简化材质 | [[渲染线程瓶颈诊断]] |
| 加载卡顿 | Insights LoadTime | 同步加载 / Shader 编译 | AsyncLoad / 预流送 | [[Lyra 性能架构]] |

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
| `#perf/已验证` | 方案已验证有效 |
| `#perf/待验证` | 方案仅为假设 |

---

## 工具链备忘

| 工具 | 场景 | 快捷键/技巧 |
|------|------|-------------|
| RenderDoc | 帧捕获分析 | Ctrl+Shift+Print 捕获 |
| Pix | DirectX 12 调试 | GPU 时间线分析 |
| UE Insights | Unreal 性能分析 | stat unit / stat gpu |
| Unity Profiler | Unity 全链路 | Deep Profile 慎用 |
| Tracy | C++ 手动插桩 | ZoneScoped |
| Superluminal | Windows 采样 | 无侵入式分析 |

---

## 知识参考索引

从在线资源（官方文档、GDC 演讲、Lyra 源码、团队博客）整理的方法论与实战笔记：

- **方法论**：
  - [[性能优化方法论]] — Profile 思维框架、黄金三问、诊断流程图
  - [[Unreal Insights 帧分析实战]] — 工具实操（5 步上手 + 5 个高频场景）

- **专项调优**：
  - [[Lumen 性能调优]] — Lumen 三种反射模式 + 5 个诊断维度
  - [[Nanite 性能调优]] — Nanite 5 维度 + GDC 2024 material binning
  - [[渲染线程瓶颈诊断]] — GT/RT/RHI 三线程 + 4 个最常见多线程坑

- **架构参考**：
  - [[Lyra 性能架构]] — Lyra 的性能设计哲学 + 5 大支柱

---

## 关联知识库

- [[02-引擎源码分析库]] — 引擎底层性能设计
- [[99-Templates/性能优化]] — 新建瓶颈案例记录的模板

---

## 本月 Profile 目标

- [ ] 完成至少 1 次完整的帧分析（RenderDoc）
- [ ] 记录至少 3 个可复用的优化方案
- [ ] M5 专项：跑 Lyra 默认 map 录 30 秒 utrace，按 [[Lumen 性能调优]] 流程做一遍诊断
