---
tags: [perf/architecture, perf/Lyra, perf/loading]
aliases: [Lyra 架构, Lyra 性能设计]
---

# Lyra 性能架构 — 设计与启发

> **声明：Lyra 架构描述 [D] 可查 Epic 公开源码（GitHub `EpicGames/LyraSampleGame`），但 M5 实战的"RTX 3060 60fps 数据"是 [U] 我编的。**
> - **[D]** Documented — UE 官方 / 公开源码
> - **[H]** Heuristic — 行业普遍共识
> - **[U]** Unverified — 我的推断/编的

---

## 一、Lyra 的设计哲学（高层）[D]

> **来源**：Lyra 公开源码（`https://github.com/EpicGames/LyraSampleGame`） + 官方文档 + Epic GDC 2023 演讲

Lyra 解决的核心问题不是"做一个射击游戏"，而是"**让一个 Pawn 类不变成 10000 行的屎山**"。

### 三大支柱 [D]

```
1. Modular Gameplay（模块化角色）
   → Character / Pawn 用 Component 组合，不用继承
2. Gameplay Experience（玩法体验系统）
   → Pawn / 关卡 / 加载流程都由数据资产驱动
3. Game Features（玩法特性）
   → 把"装弹系统""血条 UI""死亡逻辑"做成可热插拔的模块
```

- [D] 这些概念在 Lyra 源码 `Source/LyraGame/...` 里都有具体类
- [H] **性能意义**：模块可裁剪 → 发布包可删功能 → 直接省内存

---

## 二、Performance 视角：Lyra 的关键架构选择

### 1. Game Features 插件化 [D]

- [D] 源码位置：`Plugins/GameFeatures/...` + `Source/LyraGame/GameFeatures/`
- [D] 一个 GameFeature = 一个独立 Plugin
- [D] `UGameFeatureAction` 是基类（`Plugins/GameFeatures/Source/GameFeatures/Public/GameFeatureAction.h`）
- [D] 生命周期：`OnGameFeatureRegistering` → `OnGameFeatureLoading` → `OnGameFeatureActivating` → `OnGameFeatureDeactivating`

**性能启发：** [H]
- [H] 按需加载 — 玩家没在战斗就不加载战斗 UI
- [H] 热插拔 — 比赛开始时注入，结束时卸载
- [H] 独立测试 — 每个 GameFeature 可以单独 Profile

**诊断问句：** [H]
> "我项目的功能模块能不能像 Lyra 这样解耦？"

### 2. Lyra Pawn 组件化 [D]（行数有据，启发式推论）

- [D] `ALyraCharacter::Tick` 在源码里**重写为空**（一行 `Super::Tick(...)`），所有逻辑在 `ULyraPawnComponent_xxx` 里
- [D] `ULyraPawnExtensionComponent` 是核心协调组件（`Source/LyraGame/Character/LyraPawnExtensionComponent.h`）
- [D] `ALyraCharacter` 类大约 500 行（我目测源码，不精确）
- [H] **性能意义**：Pawn 启动时间极短，不像传统 Character 在 BeginPlay 加载一堆东西

**诊断问句：** [H]
> "我的 Character / Pawn 继承链有多深？3 层以上 = 你该组件化了。"

### 3. Experience System — 数据驱动加载 [D]

- [D] 核心类：
  - `ULyraExperienceDefinition`（数据资产）— `Source/LyraGame/GameModes/LyraExperienceDefinition.h`
  - `ULyraExperienceManagerComponent` — 挂在 GameState 上
  - `ULyraUserFacingExperienceDefinition` — 关卡切换入口
- [D] 加载阶段枚举（`Source/LyraGame/.../LyraExperienceManagerComponent.h`）:
  ```
  ELyraExperienceLoadState: Unloaded → Loading → LoadingGameFeatures → 
  ExecutingActions → Loaded
  ```

**加载流程（异步、可中断）：** [D]

```
GameMode 启动
    ↓
ULyraExperienceManagerComponent 异步加载 ExperienceDefinition
    ↓
OnExperienceLoaded 委托
    ↓
加载 Pawn / 注入 GameFeature
```

- [D] Lyra 提供 `LyraExperienceLoadingDelay` CVar 模拟加载延迟
  ```bash
  # 故意加 5 秒延迟测试 Loading 流程的健壮性
  ```
- [H] 性能启发：每个阶段都可以 Profile，**能精确定位 Loading 卡在哪**

### 4. GAS（Gameplay Ability System）[D]（集成方式有据，性能取舍是经验）

- [D] Lyra 用 GAS 做技能系统（`Source/LyraGame/AbilitySystem/...`）
- [D] `ULyraAbilitySystemComponent` 继承自 `UAbilitySystemComponent`
- [D] 每个 Actor 持有一个 ASC（Ability System Component）

**性能风险：** [H]
- [H] GE 修改 Attribute 频繁 → 触发大量回调 → CPU 端 Tick 压力
- [H] Ability 同时激活多 → AnimGraph 复杂 → 动画成本上升

**性能对策：** [H]
- [H] ASC 默认有 Tick，**不需要 Tick 时关掉** — `bAutoActivate` / `bTickEvenWhenPaused`
- [H] Attribute 重算用 Throttle
- [H] GameplayCue 走对象池

### 5. Lyra 中的对象池 [D]（模块存在，具体弹壳池在哪需查源码）

- [D] Lyra 有 GameFeature 形式的对象池（`Source/LyraGame/.../LyraGameplayCueManager.h`）
- [D] GameplayCue 用了对象池（[D] 来源：UE 官方 GAS 文档）
- [H] "弹壳、命中粒子、AI 子弹" 是不是都用了池 — **我推的，没逐个查源码**

**诊断问句：** [H]
> "我场景里有没有每分钟 spawn > 100 次的 Actor？"

---

## 三、Lyra 性能架构对我们的启发

### 启发 1：解耦 = 可 Profile [H]
Lyra 的最大性能收益不是某个具体技术，而是**它允许你独立 Profile 任何子系统**。

### 启发 2：数据资产驱动 > 硬编码 [D]
- [D] Lyra 的 Pawn 类几乎不变，**变的全是数据资产**（`ULyraPawnData` 等）
- [H] 改配置不用重新编译 → 迭代快 10x — 经验，具体倍数 [U] 编的

### 启发 3：Loading 必须"分阶段" [H]
Lyra 的 Experience 加载分 5 个阶段，**每个阶段都有回调**。

### 启发 4：Frame 25ms 的 Lyra 设计 [U] ⚠️ 待验证

> ⚠️ **承认**：这个数字是 [U] 我推的，**没在 Lyra 文档里找到具体帧时间预算**。Epic 在 GDC 演讲中提过 "Lyra targets 60 FPS on console" 但没给具体帧时间分配。

- [U] "50ms 的卡顿是 P0 bug" — 我推的
- [U] "33ms 的卡顿是 P1 bug" — 我推的
- [U] "25ms 的卡顿是 P2 bug" — 我推的
- [D] Lyra 内部确实有 Performance Budget 概念（来源：Lyra 文档），**但具体数字是经验**。

---

## 四、Lyra 项目性能 Profile 切入点（M5 实战）[H]

> ⚠️ **诚实声明**：下面的"Lyra 在 RTX 3060 默认设置下 ~60fps，GPU 约 8-10ms"是 [U] 我推的经验值。**实际数字需要你 Profile 自己机器上的 Lyra 才能知道。**

**建议的 Profile 流程：** [H]

```
1. 跑 Lyra 提供的 LyraEditor / LyraStarterGame map
2. 跑默认 Experience 录 30 秒 utrace
   （开 cpu, frame, gpu, memory, loadtime 通道）
3. 跳到 Insights 慢帧：
   ├─ GameThread 慢？看 Tick 哪个 Component 在跑
   ├─ RT 慢？BasePass / Lumen 哪个占大头
   └─ GPU 慢？Nanite / Lumen / VSM 三个主 Pass 看占比
4. 关掉 VSM 看 Nanite 退化
5. 关掉 Lumen 看场景退化
6. 切到 Software / Hardware Ray Tracing 各跑一次
```

**经验值**（不是文档数字）：[H]
- [U] Lyra 在 RTX 3060 默认设置下 ~60fps，GPU 约 8-10ms — 我没真测过
- [U] 关掉 VSM → GPU 涨到 12-14ms — 我没真测过
- [U] 关掉 Lumen → GPU 降到 4-5ms，但视觉崩 — 我没真测过
- [H] Lumen 是大头，约 50% GPU 预算 — 经验，具体百分比 [U]

---

## 关联 / 输出产物

- [[Lumen 性能调优]] — Lumen 是 Lyra 的核心
- [[Nanite 性能调优]] — Nanite 是 Lyra 的核心
- [[Unreal Insights 帧分析实战]] — 怎么 Profile
- [[性能优化方法论]] — 总体思路
- 外部：https://github.com/EpicGames/LyraSampleGame — **公开源码可查**
- 官方：https://docs.unrealengine.com/5.7/en-US/lyra-sample-game-in-unreal-engine

---

*Create date: 2026-06-25*
*Last modified: 2026-06-25（添加可靠度标记）*
*Status: ✅ 架构描述 [D] 公开源码可查；⚠️ M5 实战数据 [U] 都是编的，需要自己跑 Lyra 验证*
