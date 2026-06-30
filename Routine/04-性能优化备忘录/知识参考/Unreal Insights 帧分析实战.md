---
tags: [perf/tools, perf/methodology]
aliases: [Insights, Unreal Insights 教程]
---

# Unreal Insights — 已验证的事实清单（官方文档）

> 本笔记**只收录**UE 官方文档可查的通道、面板、CVar、API。所有"trace 自身开销 60→30fps"等推论删除。
>
> **主要来源**：UE 官方 [Unreal Insights Overview](https://docs.unrealengine.com/5.7/en-US/unreal-insights-overview-in-unreal-engine)（如需 5.6 路径换成 `5.6` 即可，5.7 文档路径类似）

---

## 一、四种 Profile 工具的分工 [D]

> **来源**：UE 官方 Insights Overview 文档

| 工具 | 能看到什么 | 不能看到什么 |
|------|-----------|-------------|
| `stat unit` | 当前帧各线程总时间 | 函数级别调用栈 |
| `profilegpu` | 当前 GPU Pass 列表 | 跨帧对比、历史趋势 |
| **Unreal Insights** | 任意线程任意时段的完整调用栈、内存变化、IO、Bookmarks、Counter | 实时性差（事后分析） |
| RenderDoc | 单帧 GPU 指令级 | 跨线程、内存、IO 视角 |

> **现场调试**：`stat unit` / `stat game` / `stat gpu` / `stat unitgraph`（实时看）
> **性能调优**：Unreal Insights（事后分析 utrace）
> **像素级问题**：RenderDoc 单帧捕获

---

## 二、Unreal Insights 可启动方式 [D]

> **来源**：UE 官方文档

1. **独立进程**：`Engine/Binaries/Win64/UnrealInsights.exe`
2. **编辑器内置**：Window → Trace → 勾通道 → Start
3. **命令行参数**：`YourGame.exe -trace=cpu,frame,gpu,bookmark,counters,memory`

> 路径以你安装的 UE 引擎版本为准。

---

## 三、可录制的 Trace 通道 [D]

> **来源**：UE 官方 Insights 文档 + UE 源码 `Trace/Trace.h`

| 通道 | 适用 | 备注 |
|------|------|------|
| `cpu` | 通用调用栈 | 必开 |
| `frame` | 帧时间线 | 必开 |
| `gpu` | GPU Pass 分析 | 中等开销 |
| `bookmark` | 标记关键时刻 | 极小 |
| `memory` | 内存分配（LLM） | 中等开销 |
| `loadtime` | 加载流送 | 小 |
| `file` | 文件 IO | 中 |
| `counters` | 自定义计数器 | 极小 |
| `rhicommands` | RHI 命令录制 | **大** |
| `rendercommands` | 渲染命令录制 | **大** |

> 注意：`rhicommands` / `rendercommands` 通道开销很大，**只在排查 RHI / 渲染命令问题时开**。

---

## 四、Android 设备录制（UE 官方 + Oculus 教程）[D]

```bash
# USB 调试连上，端口转发
adb reverse tcp:1980 tcp:1980
adb shell setprop debug.ue.commandline -tracehost=127.0.0.1

# 启动游戏（Unreal Insights 会自动连接）
```

> 端口 **1980** 是 Trace 默认端口（来自 UE Trace 文档）。

---

## 五、Insights 提供的面板 [D]

> **来源**：UE 官方 Insights Overview

| 面板 | 用法 |
|------|------|
| **Timing Insights** | 主面板，看 GT/RT/RHI/GPU 各泳道；找最慢帧 |
| **Memory Insights** | 看 LLM Tags 内存分配 / 趋势 / 泄漏 |
| **LoadTime Insights** | 加载包、Shader 编译、Async Loading |
| **Asset Loading Insights** | 资源加载时间线 |
| **Network Insights** | 网络流量 / RPC |
| **Bookmarks** | 关键事件标记 |
| **Counters** | 自定义计数器趋势 |

---

## 六、录制 / 分析流程（基于面板分工）[D]

### 6.1 录 utrace

```bash
# 启动游戏 + 录 trace
YourGame.exe -trace=cpu,frame,gpu,bookmark,counters,memory

# 停止录制：直接退出游戏，utrace 自动落盘
# Windows 默认路径：<Project>/Saved/Profiling/UnrealTrace/
```

### 6.2 分析 5 步（按面板用）

1. 打开 `.utrace` → **Timing Insights**
2. **顶部时间线**：每个 tick = 一帧，色块高度 = 帧耗时（**机制官方**）
3. **找最慢帧**：双击最高的色块
4. **切到 Frames 模式**：看 GT / RT / RHI / GPU 泳道
5. **下钻**：滚轮放大，右键 "Filter to selection" 过滤调用栈

---

## 七、自定义追踪 API（C++）[D]

> **来源**：UE 官方 Trace 文档 + `Trace/Trace.h`

```cpp
// 标记关键时刻
TRACE_BOOKMARK(TEXT("BossSpawn"));

// 设置自定义计数器
TRACE_COUNTER_SET(TEXT("EnemyCount"), Enemies.Num());

// CPU profiler 范围事件
TRACE_CPUPROFILER_EVENT_SCOPE(MyExpensiveFunction);

// CPU profiler 瞬时事件
TRACE_CPUPROFILER_EVENT_SCOPE_TEXT(*FString::Printf(TEXT("ProcessActor %s"), *ActorName));
```

→ 这些宏在 `Trace/Trace.h` 和 `ProfilingDebugging/CpuProfilerTrace.h` 里（具体路径以 UE 版本为准）。

---

## 八、`stat unit` 显示的列（标准输出）[D]

> **来源**：UE 官方 stat 命令文档

`stat unit` 显示的列：

| 列 | 含义 |
|----|------|
| Frame | 整帧时间（含 Present） |
| Game | GameThread 时间 |
| Draw | 渲染线程准备时间 |
| GPU | GPU 时间 |
| RHI | RHI 时间 |
| RHIT | RHI Thread 时间（PC/主机） |
| Present | 帧缓冲交换 / VSync 等待 |

→ 这是 UE 内置 stat 的标准输出，**每一列名都有官方文档支撑**。

---

## 九、移动端热降频诊断命令 [D]

> **来源**：Android 官方 `dumpsys` 文档

```bash
adb shell dumpsys thermalservice
```

→ 查看设备热状态。**这是 Android 系统命令，不是 UE 专用**。

---

## 十、不在本文档里的内容

> 以下**没有可查的官方 / 文档来源**，本文**不写**：

- "全开 trace 会让游戏从 60fps 跌到 30fps"——本文不主张
- "Insights 加载 1GB utrace 要 X 秒"——本文不主张
- 任何"trace 的运行时开销 X%"——本文不主张

需要这些数字 → 在自己的目标项目上 **录一段 trace、看 Performance 对比**。

---

## 关联 / 输出产物

- [[性能优化方法论]] — Profile 黄金三问（决定录哪些通道）
- [[渲染线程瓶颈诊断]] — Insights 看到的 GT/RT/RHI 来自哪里
- [[Lumen 性能调优]] — Lumen 性能调优时怎么 Profile
- [[Nanite 性能调优]] — Nanite 性能调优时怎么 Profile
- [[Lyra 性能架构]] — Lyra 是 Lumen + Nanite 实战参考

---

*Create date: 2026-06-25*
*Last modified: 2026-06-26（删除全部 [U] 推论 / "trace 开销" 数字；通道 / 面板 / CVar / API 全部基于 UE 官方文档）*
*Status: ✅ 通道 / 面板 / CVar / API 全部 [D] 官方文档；⚠️ 任何性能数字必须自己 Profile*