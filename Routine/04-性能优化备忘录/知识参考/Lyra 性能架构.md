---
tags: [perf/architecture, perf/Lyra, perf/loading]
aliases: [Lyra 架构, Lyra 性能设计]
---

# Lyra — 已验证的事实清单（公开源码）

> 本笔记**只收录**Lyra 公开源码 / Epic 官方文档可查的类名、文件路径、状态机、API。所有"RTX 3060 60fps"、"25ms P0 bug" 等编的数字一律删除。
>
> **Lyra 仓库**：[EpicGames/LyraStarterGame](https://github.com/EpicGames/LyraStarterGame)（GitHub 公开，需 Epic 账号）
>
> **主要来源**：
> - UE 官方 [Lyra Sample Game 文档](https://docs.unrealengine.com/5.7/en-US/lyra-sample-game-in-unreal-engine)
> - 知乎/掘金系列 Lyra 源码解析（已交叉验证类名和调用顺序）

---

## 一、Lyra 的定位 [D]

> **来源**：UE 官方 Lyra 文档

- "Lyra is a **learning resource designed as a sample game project** to help you understand the frameworks of Unreal Engine 5 (UE5)."
- 架构设计目标是 **modular**：包含核心系统 + 多个 plugin，随 UE5 主线一起更新
- 三个 Game Mode：Elimination（团队死斗）、Control（占点）、Exploder（俯视派对）

---

## 二、可在源码里查到的核心类（路径 + 用途）[D]

> **来源**：Lyra 公开源码 `Source/LyraGame/`、`Plugins/GameFeatures/`、`Source/LyraGame/AbilitySystem/`

### 2.1 Gameplay Experience 系统

| 类 | 头文件 | 作用 |
|----|--------|------|
| `ULyraExperienceDefinition` | `LyraGameModes/LyraExperienceDefinition.h` | `UPrimaryDataAsset`，定义要启用的 GameFeatures / 默认 PawnData / Actions |
| `ULyraExperienceActionSet` | `LyraGameModes/LyraExperienceActionSet.h` | `UPrimaryDataAsset`，抽象"多个 ExperienceDefinition 共用的 Actions" |
| `ULyraExperienceManagerComponent` | `LyraGameModes/LyraExperienceManagerComponent.h` | 挂在 GameState 上，负责 Experience 加载 + GameFeature 激活 |
| `ULyraUserFacingExperienceDefinition` | `LyraGameModes/LyraUserFacingExperienceDefinition.h` | 关卡切换入口（地图 ID + Experience ID + Loading widget） |

### 2.2 角色 / 玩家

| 类 | 头文件 | 作用 |
|----|--------|------|
| `ALyraCharacter` | `LyraGame/Character/LyraCharacter.h` | 角色类 |
| `ULyraPawnExtensionComponent` | `LyraGame/Character/LyraPawnExtensionComponent.h` | Pawn 核心协调组件 |
| `ULyraHeroComponent` | `LyraGame/Components/LyraHeroComponent.h` | 玩家控制相关组件，处理输入 / GAS 初始化 |
| `ULyraPawnData` | `LyraGame/Character/LyraPawnData.h` | `UPrimaryDataAsset`，定义 PawnClass / AbilitySets / InputConfig |

### 2.3 GAS

| 类 | 头文件 | 作用 |
|----|--------|------|
| `ULyraAbilitySystemComponent` | `LyraGame/AbilitySystem/LyraAbilitySystemComponent.h` | GAS 主组件（继承自 `UAbilitySystemComponent`） |
| `ULyraGameplayAbility` | `LyraGame/AbilitySystem/LyraGameplayAbility.h` | 技能基类 |
| `ULyraHealthSet` / `ULyraCombatSet` | `LyraGame/AbilitySystem/Attributes/` | AttributeSet：血量 / 战斗属性 |
| `ULyraGameplayCueManager` | `LyraGame/AbilitySystem/LyraGameplayCueManager.h` | GameplayCue 管理（用对象池） |

### 2.4 库存 / 装备

| 类 | 头文件 | 作用 |
|----|--------|------|
| `ULyraInventoryManagerComponent` | `LyraGame/Inventory/LyraInventoryManagerComponent.h` | 挂在 Controller 上 |
| `ULyraEquipmentManagerComponent` | `LyraGame/Equipment/LyraEquipmentManagerComponent.h` | 装备管理 |
| `ULyraInventoryItemDefinition` | `LyraGame/Inventory/LyraInventoryItemDefinition.h` | 物品定义（持有 Fragments） |
| `ULyraInventoryItemInstance` | `LyraGame/Inventory/LyraInventoryItemInstance.h` | 物品实例 |

### 2.5 输入

| 类 | 头文件 | 作用 |
|----|--------|------|
| `ULyraInputConfig` | `LyraGame/Input/LyraInputConfig.h` | `UDataAsset`，输入动作 → Gameplay Tag 映射 |
| `ULyraInputComponent` | `LyraGame/Input/LyraInputComponent.h` | 输入组件（增强输入） |

---

## 三、Experience 加载状态机 [D]

> **来源**：Lyra 公开源码 `LyraExperienceManagerComponent.h`

`ELyraExperienceLoadState` 枚举（5 个状态）：

```
Unloaded
  ↓
Loading
  ↓
LoadingGameFeatures
  ↓
ExecutingActions
  ↓
Loaded
```

另有 `Deactivating` 和 `LoadingChaosTestingDelay`（用 `LyraExperienceLoadingDelay` CVar 模拟加载延迟来测 loading 流程健壮性）。

### 3.1 关键函数（已验证存在于源码）[D]

```cpp
// 公开源码中的真实函数签名
void ULyraExperienceManagerComponent::SetCurrentExperience(FPrimaryAssetId ExperienceId);
void ULyraExperienceManagerComponent::StartExperienceLoad();
void ULyraExperienceManagerComponent::OnExperienceLoadComplete();
void ULyraExperienceManagerComponent::OnGameFeaturePluginLoadComplete(const UE::GameFeatures::FResult& Result);
void ULyraExperienceManagerComponent::OnExperienceFullLoadCompleted();
```

### 3.2 三种优先级的加载完成委托 [D]

```cpp
// LyraExperienceManagerComponent.h 真实签名
void CallOrRegister_OnExperienceLoaded_HighPriority(FOnLyraExperienceLoaded::FDelegate&& Delegate);
void CallOrRegister_OnExperienceLoaded(FOnLyraExperienceLoaded::FDelegate&& Delegate);
void CallOrRegister_OnExperienceLoaded_LowPriority(FOnLyraExperienceLoaded::FDelegate&& Delegate);
```

- **HighPriority**：GameMode（RestartPlayer）、PlayerState（SetPawnData）、FrontendStateComponent
- **NormalPriority**：BotCreation、UAsyncAction_ExperienceReady
- **LowPriority**：BotCreation 等非核心功能

### 3.3 网络复制 [D]

```cpp
// LyraExperienceManagerComponent.h 真实签名
UPROPERTY(ReplicatedUsing = OnRep_CurrentExperience)
const ULyraExperienceDefinition* CurrentExperience;

void ULyraExperienceManagerComponent::OnRep_CurrentExperience();
```

→ 服务器设 `CurrentExperience` 后自动同步到客户端，客户端在 `OnRep_CurrentExperience` 里调 `StartExperienceLoad()`。

### 3.4 Loading Screen 集成 [D]

```cpp
// LyraExperienceManagerComponent.h 真实继承
class ULyraExperienceManagerComponent final :
    public UGameStateComponent,
    public ILoadingProcessInterface
{
    virtual bool ShouldShowLoadingScreen(FString& OutReason) const override;
};
```

→ 因继承 `ILoadingProcessInterface`，loading 期间引擎自动显示 Loading Screen（每帧 `FTickableGameObject` 检查）。

---

## 四、GameFeatures 插件化 [D]

> **来源**：Lyra 公开源码 `Plugins/GameFeatures/` + `Source/LyraGame/GameFeatures/`

- 一个 GameFeature = 一个独立 Plugin
- `UGameFeatureAction` 是基类（`Plugins/GameFeatures/Source/GameFeatures/Public/GameFeatureAction.h`）
- 生命周期：

```
OnGameFeatureRegistering → OnGameFeatureLoading → 
OnGameFeatureActivating → OnGameFeatureDeactivating
```

- 核心 Lyra GameFeatures：
  - `ShooterCore`：角色 / 武器 / 玩法
  - `ShooterMaps`：地图
  - `TopDownArena`：俯视玩法
  - `LyraExampleContent`：共享材质

---

## 五、不在本文档里的内容

> 以下内容**没有可查的官方 / 公开源码支撑**，本文**不写**：

- "Lyra 在 RTX 3060 上 60fps"——本文不主张
- "Lyra 默认设置下 GPU X ms / CPU Y ms"——本文不主张
- "Lyra 的角色类只有 500 行"——目测估算，不精确
- "每个 ExperienceDefinition 平均 Z 个 Action"——本文不主张
- "Lyra Performance Budget 是 X ms"——官方仅说 "Lyra targets 60 FPS on console" 但没给具体帧时间分配
- 任何"用 Lyra 后能省 X% 内存" 类比——本文不主张

需要这些数字 → 自己 Profile Lyra（按 `[[Unreal Insights 帧分析实战]]` 流程录 utrace）。

---

## 六、对工作有用的入口（不是性能数据，是工作流）[D]

> 这些是**源码可见的工作流事实**，可参考。

1. **从 WorldSettings 入口**：Default Gameplay Experience 字段选 `ULyraExperienceDefinition` 资产
2. **调试日志关键函数**：`ALyraGameMode::HandleStartingNewPlayer`、`ULyraHeroComponent::InitializePlayerInput`、`ULyraGameplayAbility::ActivateAbility`（知乎教程建议加 `UE_LOG` 看调用栈）
3. **可视化 ASC**：`ShowDebug AbilitySystem` 控制台命令（来自 Lyra 教程系列）
4. **Lyra 内置追踪点**：Lyra 项目自带 Unreal Insights 追踪（具体调用 `TRACE_CPUPROFILER_EVENT_SCOPE` 的位置需要查源码确认）

---

## 关联 / 输出产物

- [[Lumen 性能调优]] — Lyra 用 Lumen + Nanite 作为默认渲染
- [[Nanite 性能调优]] — Lyra 是 Nanite + Lumen 实战参考
- [[Unreal Insights 帧分析实战]] — 怎么 Profile Lyra
- [[性能优化方法论]] — 总体思路
- 外部：
  - [EpicGames/LyraStarterGame](https://github.com/EpicGames/LyraStarterGame) — 公开源码
  - [Lyra Sample Game 官方文档](https://docs.unrealengine.com/5.7/en-US/lyra-sample-game-in-unreal-engine)

---

*Create date: 2026-06-25*
*Last modified: 2026-06-26（删除全部 [U] 性能数字；类名 / 文件路径 / 状态机 / 函数签名全部基于公开源码）*
*Status: ✅ 架构 / 类名 / API 有 Lyra 公开源码支撑；⚠️ 任何性能数字必须自己 Profile*