---
tags: [source/UE5.8, source/Nanite, source/W29, source/虚拟几何, source/ClusterDAG, source/PageStreaming, source/MeshPass, source/源码追踪]
aliases: [UE5 Nanite 源码追踪, Nanite Mesh Pass 源码, Nanite Cluster DAG 源码, Nanite Page Streaming 源码]
quarterly_review: 2026-Q3
---

# UE5 Nanite — Mesh Pass + Cluster DAG + Page Streaming 源码追踪(W29 起头)

> **W29 状态**:三件套起头 — 顶层入口 + 关键数据结构已落地;W30 补全渲染主循环、Cluster 切分算法、Page eviction 策略。
> **目标行数**:≥ 800 行(W29 起头 → W30 续写,这是 README 公开承诺的两周工作量)。
> **承接**:[[../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry|论文笔记]] 提供理论 + [[../../../03-Shader与特效案例集/C05/Nanite-材质管线|C05 shader 763 行]] 提供材质视角 + [[../W26/UE5-Nanite-虚拟几何shader|W26 shader 源码]] 提供历史积累,本文档补**Mesh Pass / Cluster DAG / Page Streaming 三大子系统**源码维度。

---

## 1. 文档定位

Nanite 是 UE5 的虚拟化微多边形几何系统 — **用 Cluster DAG + Page Streaming 在 GPU 上实时渲染电影级 mesh 资产**,替代传统 LOD + Draw Call 范式。核心是"GPU-Driven 渲染管线":CPU 只负责调度,所有 culling / LOD / 遮挡 / 几何处理都在 GPU 上完成。

**三大子系统**(本文档聚焦):
1. **Mesh Pass** — Nanite 怎么集成到 UE 渲染主循环的各个 pass(Nanite::Emit* 入口)
2. **Cluster DAG** — 128-tri cluster + DAG 树结构 + GPU-Driven culling
3. **Page Streaming** — 异步 page 加载 + GPU 反馈

**本文档不覆盖**:
- Nanite 理论推导(见 Karis 2021 论文笔记)
- Material 内部细节(见 C05 shader 笔记)
- Ray Tracing 集成(见 [[../W28/UE5.8-MegaLights-随机光照|MegaLights 笔记]] 顺带的 Nanite RT 部分)

---

## 2. Nanite 文件总览(38 个 .h/.cpp)

`Engine/Source/Runtime/Renderer/Private/Nanite/` 38 文件,按功能分组:

```
┌─ 顶层入口 (Nanite.cpp / Nanite.h)
│  └─ EmitShadowMap / EmitCubemapShadow / PrintStats / ExtractShadingDebug
│
├─ 渲染子系统
│  ├─ NaniteCullRaster.cpp/.h       — Cluster DAG culling + rasterization
│  ├─ NaniteVisibility.cpp/.h       — Visibility Buffer 写入 + 读取
│  ├─ NaniteShading.cpp/.h           — 材质求值 + binning
│  ├─ NaniteComposition.cpp/.h      — 主场景 composition
│  ├─ NaniteDrawList.cpp/.h         — Draw list 管理
│  └─ NaniteVisualize.cpp/.h         — 调试可视化
│
├─ 材质 / 资源
│  ├─ NaniteMaterials.cpp/.h
│  ├─ NaniteMaterialsSceneExtension.cpp/.h
│  └─ NaniteShared.cpp/.h            — 共享工具
│
├─ 流式加载
│  ├─ NaniteStreamOut.cpp/.h        — Stream-out 数据导出
│  └─ NaniteFeedback.cpp/.h          — GPU 反馈
│
├─ Ray Tracing
│  ├─ NaniteRayTracing.cpp/.h
│  ├─ NaniteRayTracingASCache.cpp/.h
│  └─ NaniteTranslucency.cpp/.h
│
├─ Scene 扩展
│  ├─ NaniteOwnershipVisibilitySceneExtension.cpp/.h
│  └─ NaniteEditor.cpp/.h
│
└─ 工具
   ├─ TessellationTable.cpp          — 曲面细分表
   └─ Voxel.cpp/.h                   — 体素工具
```

**关键依赖**:Nanite 强依赖 `FVirtualShadowMapArray`(VSM 集成),`FInstanceCullingLoadBalancer`(GPU 裁剪),`FGPUScene`(场景 GPU 化),`RDG`(渲染图)。

---

## 3. 顶层入口 — `Nanite.h` 公共 API

`Nanite.h:14-49`:

```cpp
#pragma once

#include "NaniteShared.h"
#include "NaniteCullRaster.h"
#include "NaniteDrawList.h"
#include "NaniteMaterials.h"
#include "NaniteVisualize.h"
#if WITH_EDITOR
#include "NaniteEditor.h"
#endif

namespace Nanite
{

struct FShadeBinning;

void ExtractShadingDebug(FRDGBuilder& GraphBuilder, const FViewInfo& View,
    const FShadeBinning& ShadeBinning, uint32 NumShadingBins, uint32 NumShadingGroups);

void PrintStats(FRDGBuilder& GraphBuilder, const FViewInfo& View);

// 阴影发射入口(被 VSM 调用)
void EmitShadowMap(
    FRDGBuilder& GraphBuilder,
    const FSharedContext& SharedContext,
    const FRasterContext& RasterContext,
    const FRDGTextureRef DepthBuffer,
    const FIntRect& SourceRect,
    const FIntPoint DestOrigin,
    const FMatrix& ProjectionMatrix,
    float DepthBias,
    bool bOrtho);

// 立方阴影发射
void EmitCubemapShadow(
    FRDGBuilder& GraphBuilder,
    const FSharedContext& SharedContext,
    const FRasterContext& RasterContext,
    const FRDGTextureRef CubemapDepthBuffer,
    const FIntRect& ViewRect,
    uint32 CubemapFaceIndex,
    bool bUseGeometryShader);

} // namespace Nanite
```

**4 个公共 API**:
- `ExtractShadingDebug` — 提取 shading 调试数据(visualize 工具)
- `PrintStats` — GPU 端 Nanite 统计打印
- `EmitShadowMap` — 阴影发射(被 VSM / 主渲染调用)
- `EmitCubemapShadow` — 立方体阴影(点光源用)

**为什么 Emit* 在 Nanite.h 而不是某个 RenderPass.h**:这是 Nanite 子系统对外的"门面",所有 pass 集成 VSM / 立方阴影都通过这里。模块边界清晰。

---

## 4. Mesh Pass 集成

### 4.1 `FRasterContext` — 单个 raster pass 的状态

`NaniteCullRaster.h:48-69`:

```cpp
struct FSharedContext
{
    FGlobalShaderMap* ShaderMap;
    ERHIFeatureLevel::Type FeatureLevel;
    ERasterPipeline Pipeline;
};

struct FRasterContext
{
    FVector2f            RcpViewSize;
    FIntPoint            TextureSize;
    EOutputBufferMode    RasterMode;       // VisBuffer | DepthOnly
    ERasterScheduling    RasterScheduling; // HardwareOnly | HardwareThenSoftware | HardwareAndSoftwareOverlap

    FRasterParameters    Parameters;

    FRDGTextureRef       DepthBuffer;
    FRDGTextureRef       VisBuffer64;     // 64-bit visibility buffer
    FRDGTextureRef       DbgBuffer64;
    FRDGTextureRef       DbgBuffer32;

    bool VisualizeActive : 1;
    bool VisualizeModeOverdraw : 1;
    bool bCustomPass : 1;
    bool bEnableAssemblyMeta : 1;
    bool bAllowTessellation : 1;
};
```

**`ERasterScheduling` 关键**:
```cpp
enum class ERasterScheduling : uint8
{
    HardwareOnly = 0,                          // 仅硬件光栅
    HardwareThenSoftware = 1,                  // 硬件大三角 + 软件小三角
    HardwareAndSoftwareOverlap = 2,            // 两者并行
};
```

这是 Nanite 的核心优化:**大三角形用 GPU 硬件光栅(快),小三角形用 compute shader 软件光栅(避免 triangle setup overhead)**。三种模式让上层选 trade-off。

**`EOutputBufferMode`**:
```cpp
enum class EOutputBufferMode : uint8
{
    VisBuffer,   // 默认:输出 visibility buffer(64-bit ID + depth)
    DepthOnly,   // 仅输出 depth(用于 VSM / depth pre-pass)
};
```

**VisBuffer 是什么**:64-bit packed = 32-bit cluster ID + 32-bit triangle ID(或 leaf node ID)。这是 Nanite"GPU-Driven"的关键 — 不用传统 GBuffer,所有材质求值都在 shading pass 二次读取。

### 4.2 `FRasterParameters` — RDG shader 参数

`NaniteCullRaster.h:18-27`:

```cpp
BEGIN_SHADER_PARAMETER_STRUCT(FRasterParameters,)
    SHADER_PARAMETER_RDG_TEXTURE_UAV(RWTexture2D<uint>,            OutDepthBuffer)
    SHADER_PARAMETER_RDG_TEXTURE_UAV(RWTexture2DArray<uint>,       OutDepthBufferArray)  // 立方阴影用
    SHADER_PARAMETER_RDG_TEXTURE_UAV(RWTexture2D<UlongType>,       OutVisBuffer64)      // 64-bit VisBuffer
    SHADER_PARAMETER_RDG_TEXTURE_UAV(RWTexture2D<UlongType>,       OutDbgBuffer64)
    SHADER_PARAMETER_RDG_TEXTURE_UAV(RWTexture2D<uint>,            OutDbgBuffer32)
END_SHADER_PARAMETER_STRUCT()
```

**5 个 UAV 输出**:
- `OutDepthBuffer` — 单视图深度
- `OutDepthBufferArray` — 立方体阴影的 6 面深度
- `OutVisBuffer64` — **Nanite 核心**:64-bit visibility buffer(cluster + triangle ID)
- `OutDbgBuffer64` / `OutDbgBuffer32` — 调试用

**`UlongType` 是什么**:UE5 RHI 抽象的 64-bit 整数类型,跨平台(DX12 UINT64 / Vulkan uint64 / Metal ulong)。

### 4.3 `FRasterResults` — 反馈给上层

`NaniteCullRaster.h:71-`:

```cpp
struct FRasterResults
{
    FIntVector4 PageConstants;
    uint32 MaxVisibleClusters;
    // ... 还有 stats
};
```

**`PageConstants`** 是 VSM 集成的关键 — 把 raster 出来的 page 信息反馈给 VSM 的 page table,决定哪些 page 是 valid 的。

---

## 5. Cluster DAG 与 GPU-Driven Culling

### 5.1 概念链(W29 推理链)

```
Asset 导入时:
  原始 mesh → Mesh 简化算法 → 128-tri cluster 切分 → DAG 树
  (root node = 整 mesh, leaf node = 128-tri cluster)

运行时:
  Camera frustum → Cluster DAG 根节点
       ↓
  GPU cull 每个 cluster(用 SW BVH)
       ↓
  Visible cluster → Bin 到 screen tile
       ↓
  Rasterize(硬件大三角 + 软件小三角)
       ↓
  写入 VisBuffer(64-bit ID + depth)
       ↓
  Shading pass 二次读取 → 材质求值
```

**为什么是 128-tri cluster**:
- 128 是 SIMD 优化边界(SIMD 4 / 8 / 16 都能整除)
- 128-tri cluster 在 GPU 一次 threadgroup 可处理(32 线程 / cluster)
- 太小 → cluster 数量爆炸(渲染调度开销主导)
- 太大 → culling 粒度粗,overdraw 浪费

### 5.2 关键文件入口

`NaniteCullRaster.cpp` 是 Cluster DAG + culling + rasterization 三大子系统的实现。`NaniteCullRaster.h:7-11` 头文件声明:

```cpp
class FVirtualShadowMapArray;
class FViewFamilyInfo;
class FSceneInstanceCullingQuery;

BEGIN_SHADER_PARAMETER_STRUCT(FRasterParameters,)
    // ... (见 §4.2)
END_SHADER_PARAMETER_STRUCT()
```

**`FSceneInstanceCullingQuery` 集成**:Nanite 用 UE5.4+ 统一的 GPU 裁剪 query,避免维护独立的 culling 系统。

### 5.3 待追(W30 续)

- [ ] `NaniteCullRaster.cpp` 主入口函数名 + 调用链
- [ ] Cluster 切分算法的源码位置(可能在 `Engine/Source/Editor/NaniteTools/` 或 DCC 工具)
- [ ] GPU SW BVH 的实现细节(`NaniteShared.h` 应该有宏定义)
- [ ] `FRasterResults` 完整结构(目前只看到开头)
- [ ] Bin 到 screen tile 的算法(可能是 sort + reduce 模式)

---

## 6. Page Streaming — `NaniteStreamOut.h`

### 6.1 核心数据结构

`NaniteStreamOut.h:14-30`:

```cpp
namespace Nanite
{
    struct FStreamOutRequest
    {
        uint32 PrimitiveId;
        uint32 NumMaterials;
        uint32 NumSegments;
        uint32 SegmentMappingOffset;
        uint32 AuxiliaryDataOffset;
        uint32 MeshDataOffset;
    };

    struct FStreamOutMeshDataHeader
    {
        uint32 NumClusters;
        uint32 VertexBufferOffset;
        uint32 IndexBufferOffset;
        uint32 NumVertices;
        uint32 NumIndices;
    };

    struct FStreamOutMeshDataSegment
    {
        uint32 NumIndices;
        uint32 FirstIndex;
    };
}
```

**3 个 stream-out 结构**:
- `FStreamOutRequest` — 一个 stream-out 请求(per primitive)
- `FStreamOutMeshDataHeader` — 输出的 mesh 数据头(cluster / vertex / index counts)
- `FStreamOutMeshDataSegment` — mesh 段(用于 LOD chain 的 segment)

**为什么需要 Stream-out**:Nanite 资产是 GPU 端的 cluster DAG,CPU 端无法直接访问。Stream-out 把 GPU 端 mesh 数据导出到 CPU-readable buffer,供其他系统(碰撞、LOD 选择、AI 寻路)使用。

### 6.2 公共 API

`NaniteStreamOut.h:32-50`:

```cpp
/*
* Stream out nanite mesh data into buffers in a uncompressed format
*/
void StreamOutData(
    FRDGBuilder& GraphBuilder,
    FGlobalShaderMap* ShaderMap,
    FSceneUniformBuffer &SceneUniformBuffer,
    float CutError,                            // 切分误差阈值(越小 LOD 越细)
    uint32 NumRequests,
    FRDGBufferRef RequestBuffer,
    FRDGBufferRef SegmentMappingBuffer,
    FRDGBufferRef MeshDataBuffer,
    FRDGBufferRef AuxiliaryDataBuffer,
    FRDGBufferRef VertexBuffer,
    uint32 MaxNumVertices,
    FRDGBufferRef IndexBuffer,
    uint32 MaxNumIndices
);
```

**入参分解**:
- `CutError` — 切分误差(0.0 = 最高精度,1.0 = 最粗)
- 5 个输入 buffer:Request / SegmentMapping / MeshData / Auxiliary / Vertex+Index
- 3 个容量限制:MaxNumVertices / MaxNumIndices / 隐式的 segment 限制

**输出位置**:通过 RDG 外部别名(由调用方提供)写入 5 个输出 buffer。

### 6.3 关键概念:Page vs Cluster

| 概念 | 含义 | 谁拥有 |
|------|------|--------|
| **Page** | Nanite 资产在磁盘 / GPU 内存的物理页(2MB 边界) | Streaming 系统 |
| **Cluster** | 128-tri 渲染单元,DAG 节点 | Nanite runtime |
| **Cluster DAG** | 整个 mesh 的层次 cluster 树 | Nanite 资产 |
| **GPU Scene** | 当前可见的 cluster 集合 | FGPUScene |

**Page streaming 的本质**:**把磁盘上的 Nanite 资产页按需加载到 GPU 显存**,只加载当前视图需要的 page。`NaniteFeedback` 写 GPU 端 page 缺失信号,CPU 下一帧补 page。

### 6.4 待追(W30 续)

- [ ] `NaniteStreamOut.cpp` 实现细节(GPU 端如何切分 cluster → mesh)
- [ ] `NaniteFeedback.cpp` 的 GPU 反馈格式
- [ ] Page eviction 策略(LRU / distance-based?)
- [ ] Disk IO 路径(异步 IO 怎么协调 RDG)
- [ ] mGPU 路径(每个 GPU 独立的 page 状态?)

---

## 7. FPackedView — View Uniform 完整结构

`NaniteShared.h:67-108`(part of FPackedView):

```cpp
namespace Nanite
{
// Counterpart to FPackedNaniteView in NanitePackedNaniteView.ush
struct FPackedView
{
    FMatrix44f SVPositionToTranslatedWorld;
    FMatrix44f ViewToTranslatedWorld;
    FMatrix44f TranslatedWorldToView;
    FMatrix44f TranslatedWorldToClip;
    FMatrix44f ViewToClip;
    FMatrix44f ClipToRelativeWorld;

    FMatrix44f PrevTranslatedWorldToView;
    FMatrix44f PrevTranslatedWorldToClip;
    FMatrix44f PrevViewToClip;
    FMatrix44f PrevClipToRelativeWorld;

    FIntVector4 ViewRect;
    FVector4f   ViewSizeAndInvSize;
    FVector4f   ClipSpaceScaleOffset;
    FVector4f   MaterialCacheUnwrapMinAndInvSize;
    FVector4f   MaterialCachePageOffsetAndInvSize;
    FVector3f   PreViewTranslationHigh;
    float       ViewOriginHighX;
    // ... 还有 ~30 个 float 字段
};
}
```

**为什么 packed view 这么大**:Nanite shader 需要知道 camera 当前位置(High + Low split 避免精度丢失)+ view rect + 缓存 material 偏移 + 一切切分算法的输入。1076 行的 NaniteShared.h 里 FPackedView 占了约 1/3。

**PreViewTranslation High/Low 技巧**:`PreViewTranslationHigh` 存大场景整体偏移的高位,`PreViewTranslationLow` 存相对偏移,GPU 端用 `WorldPos = TranslatedWorld + (High - Low)` 重建 — 避免大世界坐标在 32-bit float 下精度丢失。

**PrevXXX 字段**:4 个 `Prev*` 矩阵是 TAA / motion vectors 的输入。Nanite 在 shading pass 用 prev view 重投影做时域累积。

---

## 8. 已知坑 + 待补(W30 续)

### W29 已落地(本笔记)
- ✅ Nanite 38 文件结构梳理
- ✅ `Nanite.h` 公共 API 4 个入口
- ✅ `FRasterContext` / `FRasterParameters` / `ERasterScheduling` 三大结构
- ✅ `NaniteStreamOut.h` Page Streaming 数据结构 + API 签名
- ✅ `FPackedView` 关键字段含义
- ✅ VSM 集成路径(`EmitShadowMap` 调用链)

### W30 待补
- [ ] **Cluster 切分算法源码** — Nanite 资产怎么从 mesh → 128-tri cluster DAG
- [ ] **GPU SW BVH 实现** — Cluster 内部空间索引的 GPU 实现
- [ ] **NaniteCullRaster.cpp 主函数链** — 入口函数名 + cull → bin → raster 调用顺序
- [ ] **FRasterResults 完整结构** + PageConstants 怎么反馈给 VSM
- [ ] **NaniteFeedback.cpp** — GPU 反馈 page 缺失的格式
- [ ] **Page eviction 策略** — LRU / distance / priority
- [ ] **Disk IO + RDG 集成** — 异步 IO 怎么不阻塞 GPU
- [ ] **mGPU page 同步** — 跨 GPU 的 page 状态一致性
- [ ] **Mesh Pass Processor** — UE Mesh Pass 框架怎么扩展到 Nanite
- [ ] **PSOPrecache 集成** — Material shader PSO 怎么预缓存(NaniteCullRaster.h 已经 include PSOPrecacheMaterial.h,需要追)

### 长期
- [ ] **5.0 → 5.4 → 5.6 演进** — 各版本 Nanite 大改动(已知:5.4 材质 Bin 调度减少 80% 空调度)
- [ ] **Mac Metal 实测** — Nanite Page Streaming 在 Apple Silicon 上的内存压力
- [ ] **Tessellation 路径** — `bAllowTessellation` 标志对应的实现

---

## 9. day-job 落地

day-job = **RAG + Mac Game Harness(LLM-driven UE on Mac)**,Nanite 源码追踪对应的 LLM 训练价值:

| 内容 | 适合喂 LLM 的形式 |
|------|---------------------|
| `Nanite::EmitShadowMap` 入口 | "Nanite 通过 EmitShadowMap 跟 VSM 集成,被 VSM 的 FShadowRenderer 调用" |
| `ERasterScheduling` 三种模式 | "大三角硬件光栅 + 小三角 compute 软件光栅,按 trade-off 选模式" |
| `OutVisBuffer64` 64-bit 输出 | "64-bit packed = cluster ID + triangle ID,shading pass 二次读取" |
| `FStreamOutRequest` 流式输出 | "GPU cluster → CPU-readable mesh 的导出,供碰撞/AI 使用" |
| `FPackedView` PreViewTranslation High/Low | "32-bit float 在大场景精度丢失,High/Low 拆分避免" |
| 128-tri cluster | "SIMD 优化边界,GPU 一次 threadgroup 32 线程可处理" |

---

## 10. 关联

- [[../../01-论文笔记库/Nanite/Karis-2021-Nanite-Virtualized-Geometry|论文笔记 Karis 2021]] — 理论 + SIGGRAPH 2021 course
- [[../../../03-Shader与特效案例集/C05/Nanite-材质管线|C05 shader 763 行]] — 材质管线视角
- [[../W26/UE5-Nanite-虚拟几何shader|W26 shader 源码]] — 已有源码积累
- [[../W27/Nanite-Card-Pack|Nanite Card Pack]] — W27 面试卡牌集
- [[UE5-VSM-源码追踪|姊妹篇:VSM 源码追踪]] — Nanite 的阴影目标
- [[../W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析|Lumen Surface Cache 源码]] — 渲染三大特性之三
- [[../../../04-性能优化备忘录/瓶颈案例/Nanite-WPO禁用距离-破面修复|Nanite WPO 破面案例]] — 实际生产问题
- [[../../../05-技术雷达/P0-立即学习/Nanite|Nanite 雷达条目]] — W28 升级到 P0
- [[../../W29/00-README|W29 README]] — 本周全部产出索引

---

*Create date: 2026-07-18(W29)*
*Last modified: 2026-07-18(W29)*
*W30 待续: Cluster 切分算法 + GPU SW BVH + cull/bin/raster 主函数链 + page eviction + 5.0→5.4→5.6 演进*
