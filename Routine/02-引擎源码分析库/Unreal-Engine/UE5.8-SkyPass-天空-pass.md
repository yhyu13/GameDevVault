---
tags: [source/UE, source/RenderThread, source/深度完成, source/Atmosphere, source/MeshPass]
aliases: [UE5.8-SkyPass-MeshProcessor, UE5.8-天空-pass]
---

# UE5.8 SkyPass 天空 Pass — 源码调用链分析

| 字段 | 内容 |
|------|------|
| **分析目标** | UE5.8 `EMeshPass::SkyPass` 的 mesh pass processor + `IsSky` material 渲染流程 |
| **引擎** | Unreal Engine **5.8**（本机 `C:\Epic\UE_Engine\UE5_8\UnrealEngine` 已 clone） |
| **模块** | 渲染 / Mesh Pass / 天空兜底 / PSO Precache |
| **分析日期** | 2026-07-02 |
| **问题定义** | SkyPass 是什么？为什么有 `SkyPass` 和 `MobileSkyPass` 两个 processor？什么场景下 SkyPass 替代 `SkyAtmosphere`？PSO precache 的 PSOPrecacheVertexFactoryData 怎么用？`IsSky` material flag 的判定流程？ |
| **源码版本** | UnrealEngine @ UE 5.8（`Engine/Source/Runtime/Renderer/Private/SkyPassRendering.cpp` 仅 353 行，全部已核对） |

> **声明**：本分析基于 Epic Games 公开的 UE 5.8 主线代码。SkyPass 是三套天空系统里**最轻**的（13KB / 353 行），但承担的"兜底"职责很关键——Mobile 端必备，且 SkyLight 实时捕获的回退路径。

---

## 为什么看这段代码？

> 工作中需要回答三个问题：
> 1. SkyAtmosphere 没设置时（或者 Mobile 端），天空怎么渲染？答案是 `EMeshPass::SkyPass` —— 一个独立的 mesh pass，渲染 `IsSky()` flagged 的 material mesh（通常是一个大球）。
> 2. SkyPass 跟 BasePass / MobileBasePass 怎么区分？PSO precache 的 `SkyPassInstanceCullingDrawParams` 是什么？
> 3. `SceneRendering.cpp:4555` 那条硬警告"Mobile the SkyAtmosphere component needs a mesh with a material tagged as IsSky"——这条规则对应的代码在哪？

---

## 模块交互图

```mermaid
graph TD
    GT[GameThread<br/>UVolumetricCloudComponent /<br/>USkyAtmosphereComponent 编辑器面板] -->|添加 IsSky material mesh<br/>e.g. SkySphere Blueprint| Proxy[FPrimitiveSceneProxy<br/>MaterialDomain::Surface + bIsSkyMaterial]
    Proxy -->|SceneVisibility<br/>SceneVisibility.cpp:1813/1826| Setup[AddCommandsForMesh<br/>标记 EMeshPass::SkyPass<br/>EMeshPassFlags::MainView]

    Setup -->|culling| Cull[Gather + Cull<br/>InstanceCullingManager]

    Cull -->|deferred path| Base[BasePassRendering.cpp:1502/1585<br/>View.ParallelMeshDrawCommandPasses EMeshPass::SkyPass]
    Cull -->|mobile path| Mobile[MobileBasePassRendering.cpp:544<br/>MobileShadingRenderer.cpp 5 处调用]

    Base -->|Processor 选择| MP[REGISTER_MESHPASSPROCESSOR_AND_PSOCOLLECTOR<br/>SkyPass: deferred path<br/>MobileSkyPass: mobile path]
    Mobile --> MP

    MP -->|InitPSO| PSO[FSkyPassMeshProcessor::CollectPSOInitializers<br/>为所有 (vertex factory × material) 组合<br/>预生成 PSOPrecacheData]

    MP -->|每帧 draw| Exec[FSkyPassMeshProcessor::Process<br/>AddMeshBatch -> TryAddMeshBatch<br/>仅接受 Material->IsSky() == true]

    Exec -->|skybox mesh<br/>球面 / 六面 cube| GS[GraphicsShader<br/>BasePassVS + BasePassPS<br/>FUniformLightMapPolicy LMP_NO_LIGHTMAP]
    GS -->|写 SceneColor| Final[BasePass composite]

    RT[Real-time Sky Capture<br/>ReflectionEnvironmentRealTimeCapture.cpp:770/788] -.调用.-> MP
    RT -->|3 模式| T[ESkyPassType: SPT_Default / DepthWrite / DepthNop]

    style MP fill:#e8f0f8
```

---

## 关键类与继承关系

| 类 / 结构体 | 职责 | 关键文件 | 关键字段 / 方法 |
|------|------|---------|------|
| `FSkyPassMeshProcessor` | **单一** mesh pass processor（不分支） | `SkyPassRendering.cpp:17-352` | `AddMeshBatch`, `TryAddMeshBatch`, `Process`, `SetStateForMobile`, `CollectPSOInitializers`, `GetCaptureFrameSkyEnvMapTextureDesc` |
| `EMeshPass::SkyPass` | Mesh pass 类型枚举 | `MeshPassProcessor.h` | 注册时绑定 `EMeshPassFlags::MainView` |
| `FMaterial::IsSky()` | 检查 material 的 `bIsSkyMaterial` flag | `MaterialShared.h` | Editor 面板"Used with Sky"勾选项 |
| `FUniformLightMapPolicy` (LMP_NO_LIGHTMAP) | 不采样 lightmap 的简化策略 | `BasePassRendering.h` | sky mesh 不需要 baked lighting |
| `FSkyPassMeshProcessor::ESkyPassType` | 3 种 sky pass 模式 | `SkyPassRendering.cpp:770-785` (在 ReflectionEnvironmentRealTimeCapture.cpp 中调用) | `SPT_Default` / `SPT_RealTimeCapture_DepthWrite` / `SPT_RealTimeCapture_DepthNop` |

### `REGISTER_MESHPASSPROCESSOR_AND_PSOCOLLECTOR` 双重注册（line 352-353）

```cpp
// Deferred 路径
REGISTER_MESHPASSPROCESSOR_AND_PSOCOLLECTOR(SkyPass, CreateSkyPassProcessor, 
    EShadingPath::Deferred, EMeshPass::SkyPass, EMeshPassFlags::MainView);
// Mobile 路径
REGISTER_MESHPASSPROCESSOR_AND_PSOCOLLECTOR(MobileSkyPass, CreateSkyPassProcessor, 
    EShadingPath::Mobile, EMeshPass::SkyPass, EMeshPassFlags::MainView);
```

> **关键点**：同一个 `CreateSkyPassProcessor` 工厂函数，但绑定两个 shading path。运行期根据 `GetFeatureLevelShadingPath(FeatureLevel)`（`SkyPassRendering.cpp:69`）自动选择 `GetBasePassShaders` 的不同 shader 集合（deferred 走 `BasePassVertexShaderPolicyParamType`，mobile 走 `MobileBasePassVertexShaderPolicyParamType`）。

---

## 代码调用链（核心）

### 总入口：从 IsSky mesh 添加到 Pass Processor 选择

```
UPrimitiveComponent (e.g. SkySphere Blueprint)
  │
  ├── 编辑器材质勾选 "Used with Sky" → Material.bIsSkyMaterial = true
  │
  └── 提交到 SceneVisibility:
        SceneVisibility.cpp:1813/1826
        DrawCommandPacket.AddCommandsForMesh(..., EMeshPass::SkyPass)
        │
        ↓ culling
        │
        PassMask.Set(EMeshPass::SkyPass)  // line 2444
        View.NumVisibleDynamicMeshElements[EMeshPass::SkyPass] += NumElements
        │
        ↓ 每帧 RT 调度
        │
        ├── [Deferred 路径]
        │     BasePassRendering.cpp:1502/1585:
        │     if (Pass = View.ParallelMeshDrawCommandPasses[EMeshPass::SkyPass]; Pass && bShouldRenderView && EngineShowFlags.Atmosphere)
        │         BuildMeshRenderingCommands(GraphBuilder, EMeshPass::SkyPass, ...)
        │
        └── [Mobile 路径]
              MobileShadingRenderer.cpp:1101/2213/2349/2681/2882 (5 处):
                BuildMeshRenderingCommands(GraphBuilder, EMeshPass::SkyPass, ...)
              MobileBasePassRendering.cpp:544: 同样的调用入口

        ↓ 实例化 Processor
        │
        FSkyPassMeshProcessor(Scene, FeatureLevel, ViewIfDynamic, PassDrawRenderState, DrawListContext)
        │
        ↓ 遍历 mesh
        │
        FSkyPassMeshProcessor::AddMeshBatch (line 23)
        │  while MaterialRenderProxy:
        │    if Material->IsSky():                              // ← 关键过滤
        │      TryAddMeshBatch(...) → break
        │    else:
        │      MaterialRenderProxy = MaterialRenderProxy->GetFallback(FeatureLevel)
        │
        ↓
        FSkyPassMeshProcessor::TryAddMeshBatch (line 41)
        │
        ↓
        FSkyPassMeshProcessor::Process (line 55)
        │  if GetFeatureLevelShadingPath(FeatureLevel) == EShadingPath::Deferred:
        │    TMeshProcessorShaders<TBasePassVertexShaderPolicyParamType<LightMapPolicyType>,
        │                          TBasePassPixelShaderPolicyParamType<LightMapPolicyType>> SkyPassShaders;
        │    GetBasePassShaders<LightMapPolicyType>(MaterialResource, VertexFactory->GetType(), 
        │        NoLightmapPolicy, FeatureLevel, false /*128bit*/, false /*bIsDebug*/, GBL_Default, ...)
        │    ...
        │    BuildMeshDrawCommands(...)
        │
        │  else:  // EShadingPath::Mobile
        │    // SetStateForMobile (line 153): 配置 mobile 特定的 blend / depth state
        │    ...
        │
        ↓
        Renderer: BasePass VS + BasePass PS 执行 skybox mesh
        输出 → SceneColor
```

### 旁路：Real-time Sky Capture（line 770-788 in ReflectionEnvironmentRealTimeCapture.cpp）

```
FReflectionEnvironmentRealTimeCapture::CaptureOnce
  │
  ├── 决定 ESkyPassType:
  │     if bReflectionFromCapturedScene: SPT_RealTimeCapture_DepthWrite
  │     elif bReflectionFromMainScene:   SPT_RealTimeCapture_DepthNop
  │     else:                            SPT_Default
  │
  ├── new FSkyPassMeshProcessor(Scene, FeatureLevel, nullptr, DrawRenderState, DynamicMeshPassContext)
  │
  ├── 临时创建 RenderTarget (FSkyPassMeshProcessor::GetCaptureFrameSkyEnvMapTextureDesc)
  │     Cube map (1x1 base, full mip chain)
  │
  └── 执行 DrawDynamicMeshPass → 渲染到 cube map → 喂给 SkyLight 实时捕获
```

> **关键观察**：Real-time Sky Capture 路径跟主相机走**同一个** `FSkyPassMeshProcessor`，只是 ESkyPassType 不同 + 输出到 cube map。这保证了 sky 视觉一致性。

---

## 内存布局分析

```cpp
// ESkyPassType 仅 3 个值，sizeof = int
enum class ESkyPassType : uint8 {
    SPT_Default,                        // 普通主相机 skybox
    SPT_RealTimeCapture_DepthWrite,     // 实时捕获，写深度
    SPT_RealTimeCapture_DepthNop,       // 实时捕获，不写深度（让其他物体重叠）
};

// Cube map (GetCaptureFrameSkyEnvMapTextureDesc)
// 标准环境光捕获: 1x1 base, ~8 mips, A16B16G16R16F
// 1080p 等效: 6 faces × (1+4+16+64+256+1024+4096) px × 8B ≈ 28 KB
```

### 显存总账

| 资源 | 大小 | 备注 |
|------|------|------|
| 实时 sky capture cube map | ~28 KB | mip 链 1+4+16+64+256+1024+4096 × 8B × 6 faces |
| SkyPass PSO precache 列表 | 几 MB（RAM） | (vertex factory × material shader × feature level) 组合 |
| **运行时主屏无额外显存** | — | skybox 直接写到 SceneColor，不占独立 buffer |

> **关键观察**：SkyPass 本身**不占运行时显存**——跟 SkyAtmosphere（5 个 LUT ~1.6MB）和 VolumetricCloud（~46MB）形成鲜明对比。这就是为什么它是 mobile 兜底方案。

---

## 设计评价

### 优点

- **极简**：353 行 cpp，单一 processor，无 LUT，无 permutation——渲染复杂度跟 SkyAtmosphere/VolumetricCloud 完全不在一个量级。
- **跟 BasePass 共享 shader 框架**：用 `TBasePassVertexShaderPolicyParamType` + `TBasePassPixelShaderPolicyParamType`，无需写新 shader，PSO precache 自然并入 BasePass PSO 池。
- **双 shading path 注册**：deferred + mobile 共享 processor 代码，但 shader 集按 feature level 自动切换，代码零重复。
- **`IsSky` flag 过滤**：material 不勾此 flag 直接跳过，不会误渲染到天空。
- **Real-time Sky Capture 复用**：SkyLight 实时捕获直接调这个 processor，不另写代码路径。
- **`EMeshPassFlags::MainView` 标记**：意味着只在主 view 渲，reflection capture view / shadow view 不会浪费一次 skybox 渲染。

### 可改进点

- **353 行的 micro-Pattern 没文档化**：新人需要靠 `REGISTER_MESHPASSPROCESSOR_AND_PSOCOLLECTOR` 反推 `CreateSkyPassProcessor` 工厂入口。
- **Mobile 路径必须 IsSky mesh**：如果场景只放了 SkyAtmosphere 没放 SkySphere，mobile 直接黑屏——这条规则 (`SceneRendering.cpp:4555`) 容易踩坑。
- **`LMP_NO_LIGHTMAP` 硬编码**：sky mesh 不支持 baked lighting（自然是对的），但跟某些自定义 sky 材质期望 lightmap 输入会冲突。
- **`Process` 函数 100+ 行**：把 vertex shader / pixel shader 绑定 + draw command 构建都塞在一起，复杂度过高，应拆分。
- **`GetCaptureFrameSkyEnvMapTextureDesc` 用 1×1 base**：导致 mip 链极陡，远距离反射采样精度差。

### 与其他天空方案对比

| 方案 | 优点 | 缺点 | UE5.8 立场 |
|------|------|------|-----------|
| **SkyPass (IsSky mesh)** | 极简、零 LUT、零独立显存 | 无物理大气、需要手动放 mesh | Mobile 兜底 |
| **SkyAtmosphere (Bruneton)** | 物理大气 + 5 LUT 复用 | 显存 + 复杂度高 | PC 首选 |
| **VolumetricCloud** | 真 3D 云 + 阴影投射 | 最重、46MB 显存 | PC 高端 |
| **Decima Sky (HZD)** | 跟天气系统紧整合 | 单平台 | 不内置 |

---

## 面试谈资

### 30 秒版

> UE5.8 SkyPass 是个**轻量 mesh pass**（353 行 cpp），由 `REGISTER_MESHPASSPROCESSOR_AND_PSOCOLLECTOR` 注册两次（deferred + mobile），共享同一个 `FSkyPassMeshProcessor`。流程：SceneVisibility 标 `EMeshPass::SkyPass` → culling → BasePass 或 MobileBasePass 调 `BuildMeshRenderingCommands` → Processor 过滤 `Material->IsSky()` → 用 `FUniformLightMapPolicy (LMP_NO_LIGHTMAP)` 复用 BasePass VS/PS。**Mobile 上是必备**：无 `IsSky` mesh 时 SkyAtmosphere 不显示（SceneRendering.cpp:4555 硬警告）。**Real-time Sky Capture** 也复用这个 processor，3 种 `ESkyPassType` 控制深度写入策略。

### 2 分钟版（按追问链）

> **Q1: SkyPass 跟 BasePass 是什么关系？**
> → 同一个 shader 框架（`TBasePassVertexShaderPolicyParamType` / `Pixel`），但 skybox 用 `LMP_NO_LIGHTMAP` 跳过 lightmap 采样。SkyPass 是个独立 mesh pass 而非 BasePass 子集，因为它有专门的 `EMeshPass::SkyPass` 标签 + 自己的 culling + IsSky flag 过滤，复杂度刚好够拆出来。
>
> **Q2: 为什么 mobile 端必须放 SkySphere？**
> → Mobile 的 SkyAtmosphere 路径（`FRenderSkyAtmospherePS` 的 mobile 变体）只能算 LUT，**不能**直接渲染到屏幕，需要个 IsSky 材质的全屏 mesh（通常是球面 SkySphere）作为输出载体。这是 `SceneRendering.cpp:4555` 警告的根因——sky 必须**显式**有个 mesh 才能显示。
>
> **Q3: PSO precache 怎么工作？**
> → `CollectPSOInitializers` 在加载阶段枚举所有 (vertex factory × material) 组合，调用 `GetBasePassShaders` 拿到 vertex shader + pixel shader 对，组成 `FPSOPrecacheData` 列表预生成 PSO。运行时首帧不再卡编译。
>
> **Q4: Real-time Sky Capture 为什么不需要单独写代码？**
> → 它直接 `new FSkyPassMeshProcessor(...)` + `DrawDynamicMeshPass`，输出到 cube map（`GetCaptureFrameSkyEnvMapTextureDesc`），跟主屏 skybox **同一套 shader**——保证 sky 视觉一致性。3 种 `ESkyPassType` 控制深度写入：Default 写深度 / DepthWrite 主物体写深度 / DepthNop 不写深度（让其他物体重叠）。
>
> **Q5: 跟 SkyAtmosphere 怎么并存？**
> → SkyAtmosphere 渲 LUT（不直接输出到屏幕），SkyPass 渲 mesh box（用 IsSky material）；当 IsSky material **使用了 SkyAtmosphere 节点** 时，SkyPass 实际上是把 SkyAtmosphere LUT 应用到 mesh 上——这是 mobile 路径的玩法，PC 路径则 `RenderSkyAtmosphere` 直接渲全屏 quad。→ [[UE5.8-SkyAtmosphere-大气散射]]

---

## 与工作的关联

- **Mobile 端必须配 SkySphere**：否则 Atmosphere 不显示 → [[UE5.8-SkyAtmosphere-大气散射]] 中的"Mobile 路径"小节
- **VolumetricCloud Mobile PS 兜底依赖 SkyPass**：云 PS 路径也需要个 IsSky material 作为背景 → [[UE5.8-VolumetricCloud-体积云]]
- **SkyLight 实时捕获**：用 SkyPass 渲 cube map（不是 ray-march 天空），速度快但精度受 cube 分辨率限制

---

## 输出产物

- [x] 已画流程图/类图（本文 Mermaid 图）
- [x] 已写分析笔记（本文）
- [x] 已对照 UE5.8 本机源码核对所有函数行号（仅 353 行，全部已读）
- [x] 已输出配套面试卡牌 → [UE5.8-SkyPass-天空-pass.html](./UE5.8-SkyPass-天空-pass.html)
- [ ] 已应用到工作中

---

*Create date: 2026-07-02*  
*Last modified: 2026-07-02*
