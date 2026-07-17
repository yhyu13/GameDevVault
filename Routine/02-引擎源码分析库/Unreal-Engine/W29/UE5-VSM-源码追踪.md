---
tags: [source/UE5.8, source/VSM, source/W29, source/虚拟阴影, source/页表, source/源码追踪]
aliases: [UE5 VSM 源码追踪, Virtual Shadow Map 源码分析, VSM 页表 + Cache, VSM 物理池]
quarterly_review: 2026-Q3
---

# UE5 VSM (Virtual Shadow Maps) 源码追踪 — W29 起头

> **W29 状态**:骨架完成,核心数据结构 + 关键流程已落地;Mac Metal RHI 适配 + 部分 Clipmap 细节待补。
> **目标行数**:≥ 600 行(W29 起头 → W30 补完,跟 W29 README "下个周期补 VSM 源码" 承诺对齐)。
> **承接**:[[../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps|论文笔记]] 提供理论 + [[../../../03-Shader与特效案例集/C06/VSM-Virtual-Shadow-Map|W6 shader 763 行]] 提供 shader 视角,本文档补**引擎源码**维度。

---

## 1. 文档定位

VSM (Virtual Shadow Maps) 是 UE5 替代传统 CSM 的核心阴影方案:**用页表 + Cluster + 物理页池 + LRU Cache,在大场景下保持阴影分辨率稳定**,避免 CSM 的"近处过采样、远处欠采样"问题。

本文档从引擎源码角度追踪 VSM 的核心数据流,目标读者是 day-job 里需要给 LLM 写 RAG 语料、需要在 Mac Metal RHI 上调 VSM 的引擎程序员。

**本文档不覆盖**:
- VSM 理论推导(见 Karis 2020 论文笔记)
- Shader 内部细节(见 W6 shader 案例 763 行)
- Lumen / Nanite 怎么用 VSM(见各自专题)

---

## 2. VSM 数据流概览(从源码反向梳理)

下图来自 `Engine/Source/Runtime/Renderer/Private/VirtualShadowMaps/` 9 个文件的依赖关系:

```
┌─────────────────────────────────────────────────────────────┐
│  FVirtualShadowMapArray (主类)                              │
│  ├── FVirtualShadowMapArrayCacheManager (ISceneExtension)   │
│  │   ├── 物理页池 (PhysicalPagePool, RDG 资源)              │
│  │   ├── HZB 物理页池 (HZBPhysicalPagePoolArray)             │
│  │   └── 帧数据 (FVirtualShadowMapArrayFrameData, ping-pong) │
│  ├── FVirtualShadowMap (静态常量类)                         │
│  │   └── PageSize=128, MaxMipLevels≤8, PhysAddrBits=16     │
│  ├── FVirtualShadowMapCacheEntry (per-shadow cache)         │
│  │   ├── Update() — 通用更新                                 │
│  │   ├── UpdateClipmapLevel() — clipmap 更新                 │
│  │   └── FClipmapInfo — clipmap Z 范围 + WPO 阈值            │
│  ├── FVirtualShadowMapPerLightCacheEntry (per-light)        │
│  │   ├── RenderedPrimitives (BitArray, MaxPrimIndex)        │
│  │   ├── LocalCacheKey / ClipmapCacheKey                    │
│  │   └── ShadowMapEntries (TArray<FVirtualShadowMapCacheEntry>)│
│  └── FVirtualShadowMapInstanceRange (per-primitive)         │
│      ├── PersistentPrimitiveIndex                           │
│      ├── InstanceSceneDataOffset + NumEntries               │
│      └── bMarkAsDynamic — 切到 dynamic cache                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
        ┌───────────────────────────────────────┐
        │  FVirtualShadowMapProjectionShaderData  │  →  RDG Uniform Buffer
        │  (GPU 端读取)                            │
        │  ShadowViewToClip, LightDirection,     │
        │  ClipmapWorldOriginOffset, etc.        │
        └───────────────────────────────────────┘
```

**核心数据流(单帧)**:
1. 场景更新阶段:`FVirtualShadowMapArrayCacheManager::UpdateUnreferencedCacheEntries()` 复用过期但未失效的页
2. Setup 阶段:对每个活动光,`FindCreateLightCacheEntry()` 拿到 / 创建 `FVirtualShadowMapPerLightCacheEntry`
3. 标记阶段:把需要渲染的 page 标记到 `PageRequestFlags` 纹理
4. 渲染阶段:对 marked pages 调用 Nanite::EmitShadowMap() 或传统深度 pass
5. 回收阶段:`ExtractFrameData()` 把数据从 RDG 持久化到下一帧的 ping-pong buffers

---

## 3. 核心常量与几何(`FVirtualShadowMap` 静态类)

`Engine/Source/Runtime/Renderer/Private/VirtualShadowMaps/VirtualShadowMapArray.h:55-100`:

```cpp
class FVirtualShadowMap
{
public:
    // PageSize * Level0DimPagesXY = 虚拟地址空间
    // 128 * 128 = 16k 虚拟页
    static constexpr uint32 PageSize = VSM_PAGE_SIZE;             // = 128
    static constexpr uint32 PageSizeMask = VSM_PAGE_SIZE_MASK;    // = 0x7F
    static constexpr uint32 Log2PageSize = VSM_LOG2_PAGE_SIZE;    // = 7
    static constexpr uint32 Level0DimPagesXY = VSM_LEVEL0_DIM_PAGES_XY; // = 128
    static constexpr uint32 Log2Level0DimPagesXY = VSM_LOG2_LEVEL0_DIM_PAGES_XY;
    static constexpr uint32 MaxMipLevels = VSM_MAX_MIP_LEVELS;    // ≤ 8
    static constexpr uint32 VirtualMaxResolutionXY = VSM_VIRTUAL_MAX_RESOLUTION_XY;
    static constexpr uint32 RasterWindowPages = VSM_RASTER_WINDOW_PAGES;

    // 物理页寻址 = 16 bit = 65536 物理页上限
    static constexpr uint32 PhysicalPageAddressBits = 16U;
    static constexpr uint32 MaxPhysicalTextureDimPages = 1U << PhysicalPageAddressBits;
    static constexpr uint32 MaxPhysicalTextureDimTexels = MaxPhysicalTextureDimPages * PageSize;

    static constexpr uint32 NumHZBLevels = Log2PageSize;  // = 7 (HZB mips = log2(128))

    static_assert(MaxMipLevels <= 8, ">8 mips requires more PageFlags bits. See VSM_PAGE_FLAGS_BITS_PER_HMIP");
};
```

**关键设计**:
- **虚拟地址空间** = `Level0DimPagesXY² × PageSize² = 128² × 128² = 16384 × 16384` 像素(等效 16K 阴影贴图)
- **物理页池** = `MaxPhysicalTextureDimTexels² = 65536² = 4G` 像素(等于 32 GB depth,实际由物理显存约束)
- **HZB mip 数** = 7(128 = 2^7,所以 HZB 有 7 级 mip)
- **MaxMipLevels 限制** = 8(超过 8 mip 需要 `VSM_PAGE_FLAGS_BITS_PER_HMIP` 加位)

**PageFlags 是什么**:每页 1 bit 标记该页是否"marked for render this frame" + 1 bit 标记 receiver mask + 1 bit 标记 dynamic。 8 mip × 3 bit = 24 bit packed in `uint32` 页表项。

---

## 4. 核心数据结构

### 4.1 `FVirtualShadowMapProjectionShaderData`

`VirtualShadowMapArray.h:104-150`(approx) — GPU uniform buffer 数据源:

```cpp
struct FVirtualShadowMapProjectionShaderData
{
    FMatrix44f ShadowViewToClipMatrix;
    FMatrix44f TranslatedWorldToShadowUVMatrix;
    FMatrix44f ShadowUVToTranslatedWorldMatrix;
    FMatrix44f TranslatedWorldToShadowUVNormalMatrix;

    FVector3f LightDirection;
    uint32 LightType = ELightComponentType::LightType_Directional;

    FVector3f PreViewTranslationHigh;
    float LightRadius;

    FVector3f PreViewTranslationLow;
    float ResolutionLodBias = 0.0f;  // clipmap: pixel size scale; local: raw bias

    FVector3f ClipmapWorldOriginOffset;
    float LightSourceRadius;
    // ... 还有 SMRT 参数
};
```

**为什么有 High / Low PreViewTranslation**:`PreViewTranslationHigh` + `PreViewTranslationLow` 拆分 `FVector3d` 为 32-bit float,避免大场景下精度丢失。GPU shader 端 `WorldPos = TranslatedWorld + (High - Low)` 重建。

### 4.2 `FVirtualShadowMapUniformParameters` (RDG Uniform Buffer)

`VirtualShadowMapArray.h:~200`(SHADER_PARAMETER_STRUCT 块):

```cpp
BEGIN_GLOBAL_SHADER_PARAMETER_STRUCT(FVirtualShadowMapUniformParameters, )
    // ... SMRT 参数(Sample Mask Ray Tracing) ...
    SHADER_PARAMETER(uint32, SMRTHairRayCount)

    SHADER_PARAMETER_RDG_BUFFER_SRV(ByteAddressBuffer, ProjectionData)

    // Page table: 虚拟页 → 物理页的映射
    SHADER_PARAMETER_RDG_TEXTURE(Texture2D<uint>, PageTable)
    SHADER_PARAMETER_RDG_TEXTURE(Texture2D<uint>, PageFlags)
    SHADER_PARAMETER_RDG_TEXTURE(Texture2D<uint>, PageReceiverMasks)
    SHADER_PARAMETER_BUFFER_SRV(StructuredBuffer<uint4>, AllocatedPageRectBounds)
    SHADER_PARAMETER_BUFFER_SRV(StructuredBuffer<uint4>, UncachedPageRectBounds)
    SHADER_PARAMETER_RDG_TEXTURE(Texture2DArray<uint>, PhysicalPagePool)

    // Dynamic 切换标记
    SHADER_PARAMETER_BUFFER_SRV(StructuredBuffer<uint>, CachePrimitiveAsDynamic)

    SHADER_PARAMETER_STRUCT_INCLUDE(FVirtualShadowMapPerViewParameters, PerViewData)
END_GLOBAL_SHADER_PARAMETER_STRUCT()
```

**5 个 RDG 资源**:
- `PageTable` — 虚拟页 (x, y, mip) → 物理页 index(每页 1 个 `uint32` packed)
- `PageFlags` — 标记位(marked / dirty / dynamic / page table 是否需要更新)
- `PageReceiverMasks` — 哪些页是"接收阴影面"(用于局部光 early-out)
- `PhysicalPagePool` — 真正的 depth 数据,GPU 端只读 / 写
- `AllocatedPageRectBounds` / `UncachedPageRectBounds` — `uint4` 包围盒,用于清零 + 渲染

### 4.3 `FVirtualShadowMapInstanceRange` — per-primitive 范围

`VirtualShadowMapCacheManager.h:~30`:

```cpp
struct FVirtualShadowMapInstanceRange
{
    FPersistentPrimitiveIndex PersistentPrimitiveIndex;
    int32 InstanceSceneDataOffset;
    int32 NumInstanceSceneDataEntries;
    bool bMarkAsDynamic;  // true → swap primitive/instance to dynamic caching
};
```

**`bMarkAsDynamic` 是关键**:动态物体不进静态 LRU,直接进 dynamic page pool(每帧重渲)。避免"动态物体在静态 LRU 里找不到 page"。

---

## 5. 物理页池 + Cache 管理

### 5.1 `FVirtualShadowMapArrayCacheManager` 概览

`VirtualShadowMapCacheManager.h:280-380`(approx):

```cpp
class FVirtualShadowMapArrayCacheManager : public ISceneExtension
{
    DECLARE_SCENE_EXTENSION(RENDERER_API, FVirtualShadowMapArrayCacheManager);

public:
    using FEntryMap = TMap<FVirtualShadowMapCacheKey, TSharedPtr<FVirtualShadowMapPerLightCacheEntry>>;

    static constexpr uint32 MaxStatFrames = 512 * 1024U;

    // 物理池 resize — 如果请求尺寸变化,丢所有 cache,resize
    void SetPhysicalPoolSize(FRDGBuilder& GraphBuilder, FIntPoint RequestedSize, int RequestedArraySize, uint32 MaxPhysicalPages);
    void FreePhysicalPool(FRDGBuilder& GraphBuilder);
    TRefCountPtr<IPooledRenderTarget> GetPhysicalPagePool() const;
    TRefCountPtr<FRDGPooledBuffer> GetPhysicalPageMetaData() const;

    // HZB 池(为 virtual receiver mask 加速)
    void SetHZBPhysicalPoolSize(FRDGBuilder& GraphBuilder, FIntPoint RequestedSize, int32 RequestedArraySize, const EPixelFormat Format);

    // 全局失效
    void Invalidate(FRDGBuilder& GraphBuilder);

    // 复用过期但未失效的页
    void UpdateUnreferencedCacheEntries(FVirtualShadowMapArray& VirtualShadowMapArray);

    // 帧末持久化
    void ExtractFrameData(FRDGBuilder& GraphBuilder, FVirtualShadowMapArray&, const FSceneRenderer&, bool bAllowPersistentData);

    // 关键: 创建 / 复用 per-light cache
    TSharedPtr<FVirtualShadowMapPerLightCacheEntry> FindCreateLightCacheEntry(
        FLightSceneId LightSceneId, uint32 ViewUniqueID, uint32 NumShadowMaps, uint32 TypeIdTag = 0u);

    bool IsCacheEnabled();
    bool IsCacheDataAvailable();
    bool IsHZBDataAvailable();

    FRHIGPUMask GetCacheValidGPUMask() const;  // mGPU 支持
};
```

**`FVirtualShadowMapCacheKey` 决定 cache 复用**:
```cpp
struct FVirtualShadowMapCacheKey
{
    uint32 ViewUniqueID;
    FLightSceneId LightSceneId;
    uint32 ShadowTypeId;
};
// HashCombineFast(ViewUniqueID, ShadowTypeId) + LightSceneId
```

**`TypeIdTag` 用途**:同一 light + view 可能有多个 shadow map(eg 静态 + 动态各一张),用 TypeIdTag 区分。

### 5.2 `FVirtualShadowMapCacheEntry` — 单个 shadow map 的缓存

`VirtualShadowMapCacheManager.h:60-130`:

```cpp
class FVirtualShadowMapCacheEntry
{
public:
    // 通用更新(本地光、inactive 光)
    void Update(const FVirtualShadowMapPerLightCacheEntry& PerLightEntry);

    // Clipmap 专属更新(带 Z 范围 + WPO 阈值)
    void UpdateClipmapLevel(
        const FVirtualShadowMapPerLightCacheEntry& PerLightEntry,
        FInt64Point PageSpaceLocation,
        double LevelRadius,
        double ViewCenterZ,
        double ViewRadiusZ,
        double WPODistanceDisabledThreshold);

    void SetHZBViewParams(Nanite::FPackedViewParams& OutParams);
    void UpdateHZBMetadata(const FViewMatrices&, const FIntRect&, uint32 TargetLayerIndex);
    void UpdatePrevHZBMetadata();

    FVirtualShadowMapHZBMetadata PrevHZBMetadata;
    FVirtualShadowMapHZBMetadata CurrentHZBMetadata;

    FNextVirtualShadowMapData NextData;  // 跟踪映射到之前的 cached 数据
    FVirtualShadowMapProjectionShaderData ProjectionData;

    struct FClipmapInfo
    {
        FInt64Point PageSpaceLocation = FInt64Point(0, 0);
        double ViewCenterZ = 0.0;
        double ViewRadiusZ = 0.0;
        double WPODistanceDisableThresholdSquared = 0.0;
    };
    FClipmapInfo Clipmap;
};
```

**关键设计**:
- **`ProjectionData` 缓存** — 同一 light + view 的 projection matrix 不每帧重算,大幅节省 CPU
- **双 HZB 缓冲**(Prev / Current) — 帧间一致性,TAA-like 历史回滚
- **`FClipmapInfo`** 单独存 `WPODistanceDisableThresholdSquared` — squared 是为了 shader 端 1 次 mul

### 5.3 `FVirtualShadowMapPerLightCacheEntry` — per-light 容器

`VirtualShadowMapCacheManager.h:150-260`(approx):

```cpp
class FVirtualShadowMapPerLightCacheEntry
{
public:
    FVirtualShadowMapPerLightCacheEntry(int32 MaxPersistentScenePrimitiveIndex, uint32 NumShadowMaps)
        : RenderedPrimitives(false, MaxPersistentScenePrimitiveIndex)  // false = 初始全 0
    {
        ShadowMapEntries.SetNum(NumShadowMaps);
    }

    // ... 关键 public state:

    // 标记哪些 primitive 在本帧被这个 light 渲染过
    // BitArray,bit index = PersistentPrimitiveIndex
    TBitArray<> RenderedPrimitives;

    FLocalLightCacheKey LocalCacheKey;
    FClipmapCacheKey ClipmapCacheKey;

    FVector LightOrigin = FVector(0, 0, 0);
    float LightRadius = -1.0f;  // 负数 = 无限(方向光)

    TArray<FVirtualShadowMapCacheEntry> ShadowMapEntries;  // per-shadow cache

    void Update(const FVirtualShadowMapCacheKey&, bool bForceInvalidate, bool bInUseReceiverMask, FVirtualShadowMapCacheKey& OutCacheKey);
};
```

**`RenderedPrimitives` 的用法**:
- 帧初全部 reset
- 渲染阶段:每渲染一个 primitive,设对应 bit
- 帧末:用 `RenderedPrimitives` 跟上一帧对比,决定哪些 page 失效
- 这是 VSM 失效追踪的核心 — 没有这个,Cache 就退化成"全帧重渲"

---

## 6. 帧数据 Ping-Pong 持久化

`VirtualShadowMapCacheManager.h:230-260`:

```cpp
struct FVirtualShadowMapArrayFrameData
{
    TRefCountPtr<IPooledRenderTarget> PageTable;
    TRefCountPtr<IPooledRenderTarget> PageFlags;
    TRefCountPtr<IPooledRenderTarget> PageReceiverMasks;

    TRefCountPtr<FRDGPooledBuffer> UncachedPageRectBounds;
    TRefCountPtr<FRDGPooledBuffer> AllocatedPageRectBounds;
    TRefCountPtr<FRDGPooledBuffer> ProjectionData;
    TRefCountPtr<FRDGPooledBuffer> PhysicalPageLists;
    TRefCountPtr<IPooledRenderTarget> PageRequestFlags;
    TRefCountPtr<FRDGPooledBuffer> NanitePerformanceFeedback;
    TRefCountPtr<FRDGPooledBuffer> ThrottleBuffer;
    TRefCountPtr<IPooledRenderTarget> PrevPrefilteredDistantPhysicalPagePoolSeparate;

    uint64 GetGPUSizeBytes(bool bLogSizes) const;
};
```

**为什么 ping-pong**:RDG 资源是 transient 的,跨帧需要 `TRefCountPtr<IPooledRenderTarget>`(RHI 池化)持久化。Cache Manager 持有前一帧的 pooled target,新帧在 RDG 里用别名(externally-pooled)引入。

**9 个 RDG 资源**:
- 3 个 Texture:`PageTable` / `PageFlags` / `PageReceiverMasks` + 1 个 `PageRequestFlags` (UAV)
- 5 个 Buffer:`UncachedPageRectBounds` / `AllocatedPageRectBounds` / `ProjectionData` / `PhysicalPageLists` / `NanitePerformanceFeedback` / `ThrottleBuffer`
- 1 个 `PrevPrefilteredDistantPhysicalPagePoolSeparate` — 5.4+ 远距离光专用物理池(避免抢占主池)

`ThrottleBuffer` 是什么:VSM 渲染开销过大时,GPU 写入 throttle 信号,CPU 下一帧减少 VSM 数量。

---

## 7. Clipmap 子系统

> 方向光的"虚化 CSM" — 多个 level 沿光方向堆叠,每级有独立的 Z 范围 + Page space location。

`Engine/Source/Runtime/Renderer/Private/VirtualShadowMaps/VirtualShadowMapClipmap.h`:

```cpp
class FVirtualShadowMapClipmap
{
    // ... 详见 VirtualShadowMapClipmap.cpp
    // 核心概念: 每级 (level) 维护自己的 PageSpaceLocation
    //           camera 移动时,PageSpaceLocation 滑动,
    //           老的 page 自然被 LRU 替换
};
```

**`UpdateClipmapLevel()` 为什么单独写**:clipmap 跟 local light 不一样,需要传:
- `PageSpaceLocation` — 该 level 在虚拟地址空间的 (X, Y) 位置(可以超大,跨越虚拟地址边界)
- `LevelRadius` — 该 level 的世界空间半径
- `ViewCenterZ` / `ViewRadiusZ` — 视点 Z 范围(决定该 level 覆盖哪段 Z)
- `WPODistanceDisabledThreshold` — 该 level 的 WPO 禁用距离(避免 WPO 动画物体在远处乱跳)

**page space 滑动策略**:
- 视点移动 → page space origin 移动 → 新 page 进 LRU,老 page 出 LRU
- 物理页池 LRU 由 `FVirtualShadowMapArrayCacheManager` 集中管理
- 这就是 VSM 比 CSM 强的核心 — 移动视点时不需要"重新分配 shadow map 内存",只需滑动虚拟地址

---

## 8. 与 Nanite 集成

`VirtualShadowMapArray.h:30-50`:

```cpp
// Generally only one pass, but we collect this to handle exceptional cases
struct FNaniteVirtualShadowMapRenderPass
{
    FSceneInstanceCullingQuery* SceneInstanceCullingQuery = nullptr;
    TArray<FProjectedShadowInfo*, SceneRenderingAllocator> Shadows;
    uint32 TotalPrimaryViews = 0u;
    uint32 MaxCullingViews = 0u;
    Nanite::FPackedViewArray* VirtualShadowMapViews = nullptr;
    Nanite::FExplicitChunkDrawInfo* ExplicitChunkDrawInfo = nullptr;
};
```

**集成路径**:
1. `FSceneInstanceCullingQuery` — 复用 UE5.4+ GPU 裁剪的 query,避免重复 culling
2. `Nanite::FPackedViewArray*` — 给 Nanite 的 packed views(每个 VSM 一份)
3. `Nanite::EmitShadowMap()` 在 `Nanite.h:33-44` 定义,作为 Nanite → VSM 的入口
4. `FExplicitChunkDrawInfo` — explicit material chunks(老式 VSM fallback,不走 Nanite 路径的物体)

**为什么 Nanite 必须用 VSM**:Nanite 用 visibility buffer(深度 + ID)直接生成阴影,没有传统 depth pre-pass。VSM 的 page-based 架构正好契合 visibility buffer 的"按需渲染" — 只渲染当前 VSM 实际命中的 page。

---

## 9. 与 Lumen 集成

`VirtualShadowMapArray.h:50-58`:

```cpp
namespace Froxel
{
    class FRenderer;
}

bool DoesVSMWantFroxels(EShaderPlatform ShaderPlatform);
bool IsVirtualShadowMapLocalReceiverMaskEnabled();
```

**Froxel 是什么**:Lumen 用的"体素 frustum"表示 — 视锥被分成 3D 体素,每体素记录距离场。VSM 的 local receiver mask 直接喂给 Froxel renderer,让 Lumen 在 froxel 层面知道"哪些表面是 shadow receiver",跳过远处无意义的光追。

**VSM + Lumen 协同**:
- VSM 提供"shadow mask"(已渲染的 page → 已 cast 阴影的表面)
- Lumen GI 在 GI gather 时用 shadow mask 跳过已被 VSM 遮挡的 ray
- 避免双计算:已 VSM 阴影的不再 Lumen 光追一次

---

## 10. 关键 CVar(从源码逆向摘出)

来源:`Engine/Source/Runtime/Renderer/Private/VirtualShadowMaps/VirtualShadowMapArray.cpp` / `VirtualShadowMapCacheManager.cpp`(cvar 散落各处,需要逐个 .cpp 翻):

| CVar | 默认值 | 作用 | 风险 |
|------|--------|------|------|
| `r.Shadow.Virtual.Enable` | 1 | 总开关 | 关 → 走传统 CSM 路径 |
| `r.Shadow.Virtual.Cache` | 1 | LRU cache 开关 | 关 → 每帧全重渲 |
| `r.Shadow.Virtual.MaxPhysicalPages` | 2048 | 物理页池上限(单位: 1024 页) | 调小 → 页溢出 → 阴影棋盘瑕疵 |
| `r.Shadow.Virtual.Clipmap.FirstLevel` | 4 | clipmap 第一级从第几级开始 | 影响最内层精度 |
| `r.Shadow.Virtual.Clipmap.MaxLevel` | 10 | clipmap 最大级数 | 影响最远距离精度 |
| `r.Shadow.Virtual.AllowHZB` | 1 | HZB 加速 local receiver mask | 关 → CPU 端算 receiver mask |
| `r.Shadow.Virtual.Debug` | 0 | 调试可视化(物理池 / 页表 / 失效页) | — |
| `r.Shadow.Virtual.Throttle` | 1 | 自动 throttle 开关 | 帧率高 → 关 throttle |
| `r.Shadow.Virtual.MegaLights` | 0 | 5.4+ MegaLights 集成(>=8 light 走 VSM) | — |

> **CVar 完整列表待补** — W30 在每个 .cpp 里系统性 grep 一次,补全。

---

## 11. Mac Metal RHI 适配

**已知问题**(从 [[04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影棋盘瑕疵]] 笔记 + UE5.4+ Mac release notes 推断):

| 维度 | DX12 / Vulkan | Metal |
|------|---------------|-------|
| BC6H 压缩 | ✅ | ⚠️ Apple Silicon 部分早期不支持,5.4+ 已加 fallback |
| 物理页池 atomic | ✅ | ⚠️ MTLBuffer atomic 行为差异,需 `r.Shadow.Virtual.MaxPhysicalPages` 调小 |
| Async compute pass | ✅ (parallel) | ⚠️ Mac 上是 sequential,需要 `r.Shadow.Virtual.Throttle` 主动控 |
| Multithreaded command encoding | ✅ | ⚠️ Metal 强制单线程,需要不同的 dispatch 策略 |
| Apple Silicon unified memory | N/A | ✅ VSM 物理页池可分配到 unified memory,实际可用 32GB+ |

**Mac 调优建议**(待 W30 在 Mac 上跑通 demo 后校准):
- `r.Shadow.Virtual.MaxPhysicalPages` 从 2048 → 1024(避免 Apple Silicon GPU atomic 争用)
- `r.Shadow.Virtual.AllowHZB=0`(HZB 在 Metal 上偶尔 hang,workaround)
- `r.Shadow.Virtual.MegaLights=0`(MegaLights 跟 Metal 的 threadgroup 不兼容,5.4+ 已修)
- 启用 `r.Shadow.Virtual.Throttle=1`(让 GPU 自适应)

---

## 12. day-job 落地

day-job = **RAG + Mac Game Harness(LLM-driven UE on Mac)**,VSM 源码追踪对应的 LLM 训练价值:

| 内容 | 适合喂 LLM 的形式 |
|------|---------------------|
| `FVirtualShadowMap::PageSize=128` 含义 | "VSM 虚拟页 = 128 像素,虚拟地址空间 = 128² × 128² = 16K 阴影贴图" |
| `FVirtualShadowMapArrayCacheManager::FindCreateLightCacheEntry` | "per-light cache,key = (ViewUniqueID, LightSceneId, ShadowTypeId)" |
| `RenderedPrimitives` BitArray 作用 | "用 BitArray 跟踪哪些 primitive 在本帧渲染过,失效追踪的核心" |
| Clipmap `UpdateClipmapLevel` 参数 | "5 个参数:PageSpaceLocation + LevelRadius + ViewCenterZ + ViewRadiusZ + WPODistanceDisabledThreshold" |
| Mac Metal CVar 调优 | "Apple Silicon 上 MaxPhysicalPages 减半,AllowHZB=0" |

---

## 13. 已知坑 + 待补(W30 续)

- [ ] **完整 CVar 列表** — 逐个 .cpp 翻,本文档当前只列主要 9 个
- [ ] **HZB 物理池子系统的 source trace** — `HZBPhysicalPagePoolArray` 来源没深挖
- [ ] **VirtualShadowMapArray.h:300-623**(剩 323 行)— `FVirtualShadowMapArray` 主类实现没拆
- [ ] **VirtualShadowMapArray.cpp** — 主要 entry 函数(`InitRendering()` / `Render()`)没追
- [ ] **mGPU 路径** — `GetCacheValidGPUMask` / `UpdateCacheValidGPUMask` 实际用法没追
- [ ] **Throttle buffer 的反馈循环** — GPU → CPU 信号怎么影响下一帧的 VSM 数量
- [ ] **Mac Metal 实测** — 上面 CVar 调优建议是推断,等真机跑 demo 后校准
- [ ] **接触阴影 / ContactShadow 集成** — 跟 VSM 的协作路径
- [ ] **SMRT (Sample Mask Ray Tracing)** — 头发 / 透明物体的 VSM 路径(`SMRTHairRayCount` 等参数)

---

## 14. 关联

- [[../../01-论文笔记库/VSM/Karis-2020-Virtual-Shadow-Maps|论文笔记 Karis 2020]] — 理论 + SIGGRAPH course
- [[../../../03-Shader与特效案例集/C06/VSM-Virtual-Shadow-Map|W6 shader 763 行]] — shader 视角
- [[../../W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析|Lumen Surface Cache 源码]] — 渲染三大特性之二
- [[../../../04-性能优化备忘录/瓶颈案例/VSM-页溢出-阴影棋盘瑕疵|页溢出案例]] — 实际生产问题
- [[../W28/UE5.8-MegaLights-随机光照|MegaLights 集成]] — 5.4+ 多光源走 VSM 阈值
- [[../../../05-技术雷达/P0-立即学习/VSM|VSM 雷达条目]] — W28 升级到 P0
- [[../../W29/00-README|W29 README]] — 本周全部产出索引

---

*Create date: 2026-07-18(W29)*
*Last modified: 2026-07-18(W29)*
*W30 待续: HZB 子系统 + 完整 CVar + Mac 实测校准 + ContactShadow 集成*
