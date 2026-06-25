# 剖析虚幻渲染体系（06）- UE5特辑Part 1（特性和Nanite）

> 来源：timlly 博客园 / 知乎  
> 原文：https://www.cnblogs.com/timlly/p/14927797.html  
> 适用：UE5 源码级 Nanite 理解（面试速查 + 概念地图）

---

## 6.1 本篇概述

早在2020年5月，虚幻官方放出了展示 UE5 渲染特性的视频 **Lumen in the Land of Nanite**，展示了基于虚拟微多边形几何体的 Nanite 和实时全局光照的 Lumen 技术。

UE5 于 2021 年 5 月下旬发布预览版 Early Access（EA）。

---

## 6.2 UE5 新特性

### 6.2.2 新渲染特性

#### 6.2.2.1 Nanite 虚拟微多边形

Nanite 是 UE5 的虚拟微多边形技术。

#### 6.2.2.2 Lumen 全局动态光照

**Lumen** 是 UE5 的全动态全局光照和反射系统，是 UE5 的默认全局光照和反射方式。Lumen 可以在从毫米级到公里级的大范围、带细节的环境中呈现无限反弹和间接镜面反射的漫反射。

**开启方式：** 工程设置中默认开启。

**Lumen 开启后的替代关系：**
- Lumen GI 代替 SSGI 和 DFAO
- Lumen 反射 代替 SSR
- 静态光照被禁用，所有光照图都被隐藏

**Lumen 支持的渲染特性：**
- **全局光照**：解决非直接光照部分（Color Bleeding），正确处理非直接光的阴影遮挡。
- **天空光照**：Final Gather 阶段解决，户内户外有明显区别。
- **发光材质**：通过 Final Gather 完成光照传播，无额外消耗，但对辐射区域大小和亮度有限制。
- **反射**：为所有范围粗糙度的材质解决间接镜面反射，支持清漆材质。

**Lumen 的渲染策略：** 全分辨率的法线细节，同时用较低分辨率计算间接照明以达到实时渲染。

#### 6.2.2.3 虚拟阴影图（VSM）

UE5 为了提升阴影的质量和优化阴影的消耗，使用了 **VSM** 和 **Clipmap** 技术，获得效果和消耗相平衡的实时阴影渲染。

#### 6.2.2.4 时间超分辨率（Temporal Super Resolution）

#### 6.2.2.5 移动端渲染

---

## 6.3 UE5 渲染体系变化

### 6.3.5 Shaders

- **新增 Nanite：** ClusterCulling、Culling、HZBCull、InstanceCulling、MaterialCulling、Shadow、GBuffer、Impsoter、DataDecode、DataPacked、Rasterizer、WritePixel 等。
- **新增 Lumen：** DiffuseIndirect、Scene、HardwareRayTracing、Mesh、Probe、Radiance、Radiosity、TranslucencyVolume、Voxel、FinalGather 等。
- **新增 Strata：** DeferredLighting、EnvironmentLighting、Evaluation、ForwardLighting、Material 等。
- **新增 VirtualShadowMap：** 构建每页绘制命令、缓存管理、Page、Projection、SMRT 等模块。
- **新增 InstanceCulling：** BuildInstanceDrawCommands（GPUScene 在 Compute Shader 中动态裁剪和生成绘制指令）、CullInstances（Compute Shader 中裁剪视野外或被遮挡的图元）、InstanceCullingCommon 等。
- **增强 HairStrands、PathTracing、RayTracing、SSD、SSRT、TAA 等模块。**
- **删除 LPV 模块。**
- **完善基础、材质、着色、光照、阴影、专用 Pass 等模块。**

---

## 6.4 Nanite

### 6.4.1 Nanite 基础

#### 6.4.1.1 FMeshNaniteSettings

控制 Nanite 的开关和参数。

#### 6.4.1.2 StaticMesh

- `FStaticMeshRenderData` 增加 `Nanite::FResources` 数据及相关处理逻辑。
- `UStaticMeshComponent` 增加 `bDisplayNaniteProxyMesh` 及 `FMeshNaniteSettings` 数据。
- `UHierarchicalInstancedStaticMeshComponent`、`UInstancedStaticMeshComponent` 等组件增加 Nanite 数据和 `SceneProxy` 支持。
- 增加 `InstanceUniformShaderParameters` 模块。

#### 6.4.1.3 NaniteResource

Nanite 资源模块，包含 `Nanite::FSceneProxy`、`Nanite::FResources`、`Nanite::FVertexFactory` 等类型。

#### 6.4.1.4 Cluster, ClusterGroup, Page

- **Cluster（簇）**：Nanite 几何体的基本单位，一组三角形被聚合为一个 Cluster。
- **ClusterGroup（簇组）**：多个 Cluster 组成 ClusterGroup，用于 LOD 层级管理。
- **Page（页）**：Nanite 数据的存储单位，类似于虚拟内存的页，用于流式加载和 GPU 驻留。

### 6.4.2 Nanite 数据构建

#### 6.4.2.1 BuildNaniteFromHiResSourceModel

从高精度源模型构建 Nanite 数据。

#### 6.4.2.2 BuildNaniteData

构建 Nanite 的核心数据：
- 输入：高模（High-Res Mesh）
- 输出：Cluster、ClusterGroup、Page、Imposter 等数据

#### 6.4.2.3 ClusterTriangles

将三角形聚合成 Cluster。

#### 6.4.2.4 FGraphPartitioner

图分割器，将网格分割为 Cluster 层次结构。

#### 6.4.2.5 BuildDAG

构建有向无环图（DAG）表示 Cluster 的 LOD 依赖关系。

#### 6.4.2.6 BuildCoarseRepresentation

构建粗粒度表示（低 LOD 代理）。

#### 6.4.2.7 NaniteEncode

编码 Nanite 数据，压缩存储。

#### 6.4.2.8 FImposterAtlas::Rasterize

生成 Imposter（广告牌）图集，用于远距离渲染。

#### 6.4.2.9 Nanite 数据构建总结

1. 输入高精度模型
2. 分割为 Cluster（图分割器）
3. 构建 ClusterGroup 和 DAG（LOD 层级）
4. 构建 Page（数据分页）
5. 生成 Imposter（远距离代理）
6. 编码压缩输出

### 6.4.3 Nanite 渲染

#### 6.4.3.1 Nanite 渲染概述

UE5 在渲染模块做了较大的改动以支持 Nanite 特性：

- **新增 NaniteRender 模块**：包含 `FNaniteCommandInfo`、`ENaniteMeshPass`、`FNaniteDrawListContext`、`FCullingContext`、`FRasterContext`、`FRasterResults`、`FNaniteShader` 等类型。
- `FPrimitiveSceneInfo` 增加 `NaniteCommandInfos`、`NaniteMaterialIds`、`LumenPrimitiveIndex` 等数据。
- `FPrimitiveSceneProxy` 增加 `SupportsNaniteRendering`、`IsNaniteMesh`、`bSupportsMeshCardRepresentation` 等接口。
- SceneInterface 和 SceneManagement 增加 `FInstanceCullingManagerResources`，使用 `FGPUScenePrimitiveCollector` 代替 `FPrimitiveUniformShaderParameters`。
- SceneView 增加大量 Shader 绑定（Lumen、Instance、Page 等）。
- Shader 模块新增：ClusterCulling、Culling、HZBCull、InstanceCulling、MaterialCulling、Shadow、GBuffer、Impsoter、DataDecode、DataPacked、Rasterizer、WritePixel 等。

#### 6.4.3.2 Nanite 渲染基础

**核心 Shader 参数：**

```cpp
// Nanite统一缓冲区参数
BEGIN_GLOBAL_SHADER_PARAMETER_STRUCT(FNaniteUniformParameters, )
    SHADER_PARAMETER(FIntVector4, SOAStrides)
    SHADER_PARAMETER(FIntVector4, MaterialConfig)
    SHADER_PARAMETER(uint32, MaxNodes)
    SHADER_PARAMETER(uint32, MaxVisibleClusters)
    SHADER_PARAMETER(uint32, RenderFlags)
    SHADER_PARAMETER(FVector4, RectScaleOffset)
    SHADER_PARAMETER_SRV(ByteAddressBuffer, ClusterPageData)
    SHADER_PARAMETER_SRV(ByteAddressBuffer, ClusterPageHeaders)
    SHADER_PARAMETER_SRV(ByteAddressBuffer, VisibleClustersSWHW)
    SHADER_PARAMETER_SRV(StructuredBuffer<uint>, VisibleMaterials)
    SHADER_PARAMETER_TEXTURE(Texture2D<uint2>, MaterialRange)
    SHADER_PARAMETER_TEXTURE(Texture2D<UlongType>, VisBuffer64)
    SHADER_PARAMETER_TEXTURE(Texture2D<UlongType>, DbgBuffer64)
    SHADER_PARAMETER_TEXTURE(Texture2D<uint>, DbgBuffer32)
END_GLOBAL_SHADER_PARAMETER_STRUCT()

// 光栅化参数
BEGIN_SHADER_PARAMETER_STRUCT(FRasterParameters, )
    SHADER_PARAMETER_RDG_TEXTURE_UAV(RWTexture2D<uint>, OutDepthBuffer)
    SHADER_PARAMETER_RDG_TEXTURE_UAV(RWTexture2D<UlongType>, OutVisBuffer64)
    SHADER_PARAMETER_RDG_TEXTURE_UAV(RWTexture2D<UlongType>, OutDbgBuffer64)
    SHADER_PARAMETER_RDG_TEXTURE_UAV(RWTexture2D<uint>, OutDbgBuffer32)
    SHADER_PARAMETER_RDG_TEXTURE_UAV(RWTexture2D<uint>, LockBuffer)
END_SHADER_PARAMETER_STRUCT()
```

**FNaniteCommandInfo：** 存储 Nanite 绘制命令的索引，映射到 `FScene::NaniteDrawCommands`。

**FNaniteDrawListContext：** 继承 `FMeshPassDrawListContext`，Nanite 专用的绘制命令列表上下文。

**FNaniteMeshProcessor：** 继承 `FMeshPassProcessor`，Nanite 网格处理器。

#### 6.4.3.3 Nanite 渲染流程

1. **Culling（裁剪）**：GPU-Driven 的 Cluster 和 Instance 裁剪
2. **Rasterization（光栅化）**：硬件光栅化大三角形 + 软件光栅化（Compute Shader）小三角形
3. **BasePass**：材质着色
4. **光影处理**：阴影、光照

#### 6.4.3.4 Nanite 裁剪

- **Cluster Culling**：基于视锥和 HZB 的 Cluster 级裁剪
- **Instance Culling**：基于 GPUScene 的实例裁剪
- **Material Culling**：材质级别的裁剪

#### 6.4.3.5 Nanite 光栅化

- **RasterTechnique**：光栅化技术选择
  - `LockBufferFallback`：64 位原子不可用时的备用方案
  - `PlatformAtomics`：平台原生 64 位原子
  - `NVAtomics` / `AMDAtomicsD3D11` / `AMDAtomicsD3D12`：GPU 厂商扩展
  - `DepthOnly`：仅深度光栅化
- **RasterScheduling**：光栅化调度模式
  - `HardwareOnly`：纯硬件光栅化
  - `HardwareThenSoftware`：硬件光栅化大三角形 + 软件光栅化小三角形
  - `HardwareAndSoftwareOverlap`：硬件和软件光栅化重叠执行

#### 6.4.3.6 Nanite BasePass

使用 `FNaniteMaterialVS` 和对应的像素着色器进行材质着色。

#### 6.4.3.7 Nanite 光影

Nanite 与 Lumen 和 VSM 的交互：Nanite 场景代理为 Lumen 提供 `MeshCardRepresentation` 数据，为 VSM 提供 `GPUScene` 数据。

### 6.4.4 Nanite 总结

**Nanite 核心思想：**
1. 将高精度模型离线分割为 Cluster 层次结构（DAG）
2. 运行时 GPU-Driven 地进行 Cluster 裁剪和 LOD 选择
3. 混合硬件/软件光栅化处理不同大小的三角形
4. 数据以 Page 为单位流式加载，类似虚拟内存

**与 UE4 的区别：**
- UE4：CPU 决策 LOD + 传统 Draw Call
- UE5：GPU-Driven Culling + Cluster Page 管理

---

## 参考文献

- timlly, 《剖析虚幻渲染体系》系列, 2021
- Epic Games, Nanite: A Deep Dive, GDC 2021
- Epic Games, Unreal Engine 5.4 Documentation
