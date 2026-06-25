---
tags: [perf/tools, perf/methodology]
aliases: [Insights, Unreal Insights 教程]
---

# Unreal Insights 帧分析实战

> **声明：本文档通道、面板、CVars 全部 [D] 来自 UE 官方文档，但"trace 自身开销 60→30fps"等是 [U] 推论。**
> - **[D]** Documented — UE 官方文档
> - **[H]** Heuristic — 行业普遍共识
> - **[U]** Unverified — 我的推断

---

## 一、为什么 Insights（而不是老 stat / ProfileGPU）[D]

> **来源**：UE 官方 "Unreal Insights Overview" 文档（`https://docs.unrealengine.com/5.7/en-US/unreal-insights-overview`）

| 工具 | 能看到什么 | 不能看到什么 |
|------|-----------|-------------|
| `stat unit` | 当前帧各线程总时间 [D] | 函数级别调用栈 [D] |
| `profilegpu` | 当前 GPU Pass 列表 [D] | 跨帧对比、历史趋势 [D] |
| **Unreal Insights** | 任意线程任意时段的完整调用栈、内存变化、IO、Bookmarks、Counter [D] | 实时性差（事后分析）[D] |
| RenderDoc | 单帧 GPU 指令级 [D] | 跨线程、内存、IO 视角 [D] |

**实战组合：** [H]
- 现场调试：`stat unit`、`stat game`、`stat gpu`、`stat unitgraph`
- 性能调优：**Unreal Insights**（必录一段 utrace）
- 像素级问题：RenderDoc 单帧捕获
- 移动端：Unreal Insights 远程 + adb pull utrace

---

## 二、5 分钟上手 — 录制与分析

### 录制（Windows / 独立进程）[D]

```bash
# 1. 启动 Insights（编辑器自带或 Engine/Binaries/Win64/UnrealInsights.exe）

# 2. 启动游戏时加命令行参数（UE5 推荐用 Trace 通道）
YourGame.exe -trace=cpu,frame,gpu,bookmark,counters,memory

# 3. 也可以在 PIE / Standalone 时通过编辑器右下角
#    Window → Trace → 勾选通道 → Start
```

- [D] `-trace=...` 通道列表来自 UE 官方文档

### 录制（Android）[D]

```bash
# 1. USB 调试连上，端口转发
adb reverse tcp:1980 tcp:1980
adb shell setprop debug.ue.commandline -tracehost=127.0.0.1

# 2. 启动游戏（Unreal Insights 会自动连接）
```

- [D] 端口 1980 来自 Oculus 官方教程（`https://developer.oculus.com/blog/...`）

### 必开的通道（按需组合）[D]

> **来源**：UE 官方 Insights 文档

| 通道 | 适用 | 代价 |
|------|------|------|
| `cpu` | 通用，必开 | 小 |
| `frame` | 帧时间线，必开 | 小 |
| `gpu` | GPU Pass 分析 | 中 |
| `bookmark` | 标记关键时刻 | 极小 |
| `memory` | 内存分配 | 中 |
| `loadtime` | 加载流送 | 小 |
| `file` | 文件 IO | 中 |
| `rhicommands` | RHI 命令录制 | 大 |
| `rendercommands` | 渲染命令录制 | 大 |

> **金科玉律 [H]**：调试哪个子系统就开对应通道，不要无脑全开。
> - [U] "全开会让游戏从 60fps 跌到 30fps" — 我推的，**没找到具体数据**

---

## 三、5 个高频分析场景

> ⚠️ 分析方法 [D]，但具体的"火焰图顶端有 X" 等是 [H] 经验。

### 场景 1：哪一帧最慢？[D]（流程官方）

- [D] 打开 Insights → 选 utrace → **Timing Insights** 面板
- [D] 顶部时间线，每个 tick = 一帧，色块高度 = 帧耗时
- [D] 找最高的色块，双击跳到那一帧
- [D] 切到 **Frames** 模式看 GT / RT / RHI 三个泳道
- [H] 诊断问题：整段高 vs 单帧高 vs 离散卡顿 — 经验

### 场景 2：GameThread 那个函数慢？[D]（流程官方）

- [D] 跳到最慢的帧 → 顶部选 **Game Thread** 泳道
- [D] 中间面板是 GT 的调用栈火焰图，最长的就是瓶颈
- [D] 滚轮放大缩小，右键 "Filter to selection"

- [H] 诊断问题：
  - "火焰图里 `UWorld::Tick` → `TickGroup` 哪个组最久？" — 经验
  - "TG_PrePhysics / TG_DuringPhysics / TG_PostPhysics 各自管什么" — UE 官方文档

### 场景 3：GPU Pass 哪个慢？[D]（流程官方）

- [D] Timing Insights 切到 **GPU** 泳道
- [D] Pass 列表按耗时倒序
- [D] 双击某个 Pass → 跳到 **GPU Track**

- [H] 诊断问题：
  - "哪个 Pass 占了 50% 以上？" — 经验
  - "多个相似 Pass 耗时差不多" — 经验

### 场景 4：CPU 等待 GPU（GT 闲置但帧时间高）[D]（机制真实）

- [D] 跳到慢帧
- [D] 看 GT 泳道：GT 是不是很快就结束了
- [D] 看 RT 泳道：RT 在干什么
- [D] 看 RHI 泳道：RHI 在等 GPU Present？

- [H] **这意味着：瓶颈在 GPU，但 CPU 因为 FrameEndSync 在等。** — 行业共识

### 场景 5：内存泄漏（越跑越卡）[D]（流程官方）

- [D] 录制时开 `memory` 通道
- [D] **Memory Insights** 面板
- [D] 选 **LLM Tags** 分类
- [D] 切到 Trends 模式，看每个 Tag 随时间的曲线
- [H] 单调上涨的 Tag → 泄漏源 — 经验

---

## 四、专家级 — 几个被忽视的技巧

### 1. Bookmarks 标记关键时刻 [D]

```cpp
TRACE_BOOKMARK(TEXT("BossSpawn"));
```

- [D] `TRACE_BOOKMARK` 来自 UE Trace 文档
- [H] 方便跨帧定位 — 经验

### 2. 计数器 Counter [D]

```cpp
TRACE_COUNTER_SET(TEXT("EnemyCount"), Enemies.Num());
```

- [D] `TRACE_COUNTER_SET` 来自 UE Trace 文档

### 3. 范围事件 Scope [D]

```cpp
TRACE_CPUPROFILER_EVENT_SCOPE(MyExpensiveFunction);
```

- [D] `TRACE_CPUPROFILER_EVENT_SCOPE` 来自 UE Trace 文档
- [H] 比 stat 简单 — 经验

### 4. 加载追踪 [D]
- [D] 开 `loadtime` 通道
- [D] **LoadTime Insights** 面板

### 5. 对比两次 trace [H]
- [H] 录"修复前"+"修复后"两个 utrace 并排打开 — 经验
- [H] 这是验证优化效果的最硬核方式 — 经验

---

## 五、肌肉记忆（速查）[H]

> ⚠️ 整张表是 [H] 经验整合，**不是官方建议**。

| 看到 | 第一件事 | 标记 |
|------|---------|------|
| 帧率高但 CPU/GPU 时间不高 | 是不是 VSync？Present 等待？ | [H] |
| GT 高，火焰图顶端有 `UWorld::Tick` | 展开 `TickGroup` 看哪一组耗时最多 | [H] |
| 单帧高，前后帧正常 | GC / 同步加载 / Shader 编译 | [H] |
| RT 高，火焰图顶端 `FDeferredShadingSceneRenderer` | 是 BasePass / Lighting / Lumen 哪一段 | [H] |
| GPU 高，`BeginRendering` 很长 | VSM / Nanite build / Lumen scene update | [H] |
| 移动端帧率波动大 | 是不是热降频？`adb shell dumpsys thermalservice` | [D] 热降频命令来自 Android 官方 |

---

## 关联 / 输出产物

- [[性能优化方法论]] — 上层思维框架（含 [U] 条目警示）
- [[渲染线程瓶颈诊断]] — 多线程架构细节（多 [D]）
- [[Lumen 性能调优]] — Lumen 专项（已加 [U] 警示）
- 官方：https://docs.unrealengine.com/5.7/en-US/unreal-insights-overview
- Oculus 教程（移动端录制）：`https://developer.oculus.com/blog/...`

---

*Create date: 2026-06-25*
*Last modified: 2026-06-25（添加可靠度标记）*
*Status: ✅ 通道/CVar/流程 [D] 官方文档；⚠️ "Trace 开销"、"诊断问题"等 [H] 经验*
