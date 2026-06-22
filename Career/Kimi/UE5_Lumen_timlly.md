# 剖析虚幻渲染体系（06）- UE5特辑Part 2（Lumen和其它）

> 来源：timlly 博客园 / 知乎  
> 原文：https://www.cnblogs.com/timlly/p/15007236.html  
> 适用：UE5 源码级 Lumen 理解（面试速查 + 概念地图）

---

## 6.5 Lumen

### 6.5.1 Lumen 技术特性

#### 6.5.1.1 表面缓存（Surface Cache）

**Surface Cache** 是 Lumen 的核心数据结构之一，用于存储场景中可见表面的光照信息。

- 存储内容：Radiance（辐射率）、Normal（法线）、Depth（深度）
- 作用：将复杂的几何场景简化为一系列可见表面的集合，大幅降低全局光照的计算复杂度
- 更新策略：每帧增量更新，只更新发生变化的区域

#### 6.5.1.2 屏幕追踪（Screen Tracing）

**Screen Tracing** 是 Lumen 的第一级光线追踪策略：
- 利用上一帧的屏幕空间数据（Scene Color、Depth）进行光线追踪
- 优势：零额外几何开销，对近处物体效果极好
- 局限：无法处理屏幕外物体、遮挡物后面的物体
- 回退策略：当 Screen Trace 失败时，回退到 Hardware Ray Trace 或 Mesh SDF

#### 6.5.1.3 Lumen 光线追踪

Lumen 的光线追踪是多层次的：
1. **Screen Trace**（屏幕空间追踪）
2. **Mesh SDF Trace**（网格有向距离场追踪）
3. **Hardware Ray Trace**（硬件光线追踪，如 RTX）

#### 6.5.1.4 Lumen 其它说明

- Lumen 实现了全分辨率的法线细节，同时用较低分辨率计算间接照明
- 支持从毫米级到公里级的场景范围
- 支持无限反弹的全局光照

### 6.5.2 Lumen 渲染基础

#### 6.5.2.1 FLumenCard

**Lumen Card** 是 Lumen 场景中的基本光照单元：
- 每个 Mesh 会在表面生成若干张 Card（卡片）
- Card 的方向由 Mesh 的 Card Representation 数据决定（通常 6 个方向对应立方体 6 个面）
- 每张 Card 存储该方向上的光照信息（Radiance Atlas）

#### 6.5.2.2 FLumenMeshCards

**MeshCards** 是图元级别的 Lumen 数据：
- 每个 `FPrimitiveSceneInfo` 对应一组 `FLumenMeshCards`
- 包含该图元的所有 Card 的索引和参数
- 通过 `LumenPrimitiveIndex` 关联到 Lumen 场景数据

#### 6.5.2.3 FLumenSceneData

**LumenSceneData** 是整个场景的 Lumen 数据管理器：
- `LumenPrimitives`：所有参与 Lumen 的图元列表
- `MeshCards`：所有 MeshCards 的数组
- `Cards`：所有 Card 的数组
- `AtlasAllocator`：Card 纹理的 Atlas 分配器
- `RadiosityAtlas` / `RadianceAtlas`：光照结果的纹理图集

### 6.5.3 Lumen 数据构建

#### 6.5.3.1 CardRepresentation

Card Representation 数据描述一个 Mesh 的 Card 生成参数：
- Card 的数量和方向
- Card 的分辨率
- 与 Mesh 表面的距离（偏移量）

#### 6.5.3.2 GCardRepresentationAsyncQueue

异步构建 Card Representation 数据的队列。

#### 6.5.3.3 GenerateCardRepresentationData

生成 Card Representation 数据的核心函数：
- 分析 Mesh 的几何特征
- 确定 Card 的位置、方向、分辨率
- 输出 Card 的捕获参数

### 6.5.4 Lumen 渲染流程

Lumen 的渲染流程分为几个阶段：
1. **场景更新**：更新 Surface Cache、Card 捕获
2. **场景光照**：计算 Lumen 场景的光照（Voxel Cone Tracing、Radiosity）
3. **非直接光照**：Screen Probe Gather、Reflections、DiffuseIndirect
4. **合成**：将 Lumen 结果与直接光照合成

### 6.5.5 Lumen 场景更新

#### 6.5.5.1 UpdateLumenScene

每帧更新 Lumen 场景：
- 检测脏 Card（发生变化的 Card）
- 更新 Lumen 图元信息
- 更新远处场景（Distant Scene）
- 重新分配 Atlas（如果 Atlas 大小变化）

#### 6.5.5.2 CardsToRender

选择每帧需要渲染的 Card 列表：
- 按距离和优先级排序
- 限制每帧最大更新数量（`CardCapturesPerFrame`）
- 使用 ParallelFor 并行准备更新数据

#### 6.5.5.3 MeshCardCapture

捕获 Mesh Card 的光照信息：
- 从 Card 的方向渲染场景
- 捕获辐射率（Radiance）到 Atlas
- 支持异步捕获和增量更新

#### 6.5.5.4 RasterizeLumenCards

光栅化 Lumen Card 的捕获过程：
- 使用简化渲染管线（不需要完整材质）
- 捕获直接光照和基础颜色
- 输出到 Surface Cache Atlas

### 6.5.6 Lumen 场景光照

#### 6.5.6.1 Voxel Cone Tracing

**Voxel Cone Tracing** 是 Lumen 中用于计算间接光照的一种技术：
- 将场景体素化（Voxelize）
- 从每个点向不同方向发射 Cone 进行追踪
- 利用 MipMap 层级加速远距离查询

#### 6.5.6.2 RenderLumenSceneLighting

渲染 Lumen 场景的整体光照：
- 计算每个 Card 的光照贡献
- 处理直接光和间接光
- 更新 Radiosity Atlas 和 Radiance Atlas

#### 6.5.6.3 RenderRadiosityForLumenScene

计算 Lumen 场景的 Radiosity（辐射度）：
- 基于 Surface Cache 的 Radiance 数据
- 计算表面之间的能量传递
- 迭代求解光照传播

#### 6.5.6.4 CombineLumenSceneLighting

合并 Lumen 场景的光照结果：
- 将 Radiosity 和直接光合并
- 输出最终的 Lumen 场景光照

#### 6.5.6.5 RenderDirectLightingForLumenScene

为 Lumen 场景渲染直接光照：
- 在 Card 捕获阶段计算直接光照
- 存储到 Surface Cache 的 Radiance 中

#### 6.5.6.6 PrefilterLumenSceneLighting

对 Lumen 场景光照进行预过滤：
- 生成 MipMap 层级
- 为不同距离的 Cone Tracing 提供合适的采样级别

#### 6.5.6.7 ComputeLumenSceneVoxelLighting

计算 Lumen 场景的体素光照：
- 将 Surface Cache 的光照信息注入体素网格
- 为 Voxel Cone Tracing 提供查询数据

### 6.5.7 Lumen 非直接光照

#### 6.5.7.1 RenderDiffuseIndirectAndAmbientOcclusion

渲染非直接光照和环境光遮蔽：
- 使用 Lumen 的间接光照替代传统 SSAO/SSGI
- 输出 DiffuseIndirect 和 AmbientOcclusion

#### 6.5.7.2 RenderLumenScreenProbeGather

**Screen Probe Gather** 是 Lumen 的核心间接光照计算 Pass：

**流程：**
1. **Uniform Placement**：在屏幕空间均匀放置探针（Probe）
2. **Adaptive Placement**：在光照变化剧烈的区域自适应增加探针
3. **Trace Rays**：从每个探针向不同方向发射光线
4. **CompositeTraces**：合并光线追踪结果，生成 ScreenProbeRadiance
5. **FilterRadianceWithGather**：对探针辐射率进行多次过滤，减少噪点
6. **ComputeIndirect**：利用探针数据计算最终的场景非直接光颜色

**关键参数：**
- `ScreenProbeDownsampleFactor`：探针下采样因子（相对于屏幕分辨率）
- `ScreenProbeTracingOctahedronResolution`：追踪方向的八面体分辨率
- `NumUniformScreenProbes`：均匀探针数量
- `MaxNumAdaptiveProbes`：最大自适应探针数量

**代码核心（简化）：**
```cpp
FSSDSignalTextures FDeferredShadingSceneRenderer::RenderLumenScreenProbeGather(
    FRDGBuilder& GraphBuilder,
    const FSceneTextures& SceneTextures,
    const ScreenSpaceRayTracing::FPrevSceneColorMip& PrevSceneColorMip,
    FRDGTextureRef LightingChannelsTexture,
    const FViewInfo& View,
    FPreviousViewInfo* PreviousViewInfos,
    bool& bLumenUseDenoiserComposite,
    FLumenMeshSDFGridParameters& MeshSDFGridParameters)
{
    // 1. 设置屏幕空间探针参数
    FScreenProbeParameters ScreenProbeParameters;
    ScreenProbeParameters.ScreenProbeDownsampleFactor = ...;
    ScreenProbeParameters.ScreenProbeTracingOctahedronResolution = ...;
    
    // 2. 下采样深度和速度
    // FScreenProbeDownsampleDepthUniformCS
    
    // 3. 自适应探针放置
    // FScreenProbeAdaptivePlacementCS
    
    // 4. 光线追踪（Screen Trace + Mesh SDF + Hardware RT）
    // CompositeTraces
    
    // 5. 过滤辐射率
    // FilterRadianceWithGather
    
    // 6. 计算最终间接光
    // ComputeIndirect
}
```

#### 6.5.7.3 RenderLumenReflections

渲染 Lumen 反射：
- 使用 Screen Space Reflection 和 Lumen 的 Trace 结果
- 支持粗糙度范围的模糊反射
- 清漆材质（Clear Coat）的特殊处理

#### 6.5.7.4 DiffuseIndirectComposite

将 Lumen 的 DiffuseIndirect 结果与场景合成：
- 将 Screen Probe Gather 的结果应用到 BasePass
- 与直接光照、AmbientOcclusion 合并
- 输出最终颜色

### 6.5.8 Lumen 总结

**Lumen 核心思想：**
1. **Surface Cache**：将复杂 3D 场景简化为可见表面的 2D 表示
2. **Card 系统**：在每个 Mesh 表面生成方向性的光照捕获点
3. **Screen Probe Gather**：在屏幕空间密集采样间接光照
4. **多层次 Trace**：Screen Trace → Mesh SDF → Hardware RT，效率和质量的平衡
5. **Radiosity 迭代**：通过多次迭代计算光照传播

**与 UE4 的区别：**
- UE4：Lightmap（预计算）/ RTGI（有限实时）/ DFAO（仅 AO）
- UE5：Lumen（全实时、无限反弹、支持反射和 GI）

**面试必答要点：**
- Surface Cache 存什么？→ Radiance、Normal、Depth
- Screen Trace 和 Hardware RT 分别在什么场景使用？→ Screen Trace 用于近处（零额外开销），Hardware RT 用于远处和屏幕外（精确但昂贵）
- 为什么 Lumen 不需要预计算 Lightmap？→ 因为 Surface Cache 和 Screen Probe 实时捕获和更新光照

---

## 6.6 其它渲染技术

### 6.6.1 Temporal Super Resolution（TSR）

UE5 的时间超分辨率技术，类似 DLSS/FSR，但基于 UE 的时间抗锯齿框架。

### 6.6.2 Strata

UE5 的新材质系统，提供更统一和可扩展的材质评估框架。

---

## 6.7 本篇总结

UE5 的渲染体系变化核心：
1. **Nanite**：GPU-Driven 虚拟微多边形，替代传统 LOD
2. **Lumen**：全实时全局光照，替代 Lightmap 和 RTGI
3. **VSM**：Virtual Shadow Maps，替代 CSM
4. **Render Graph**：显式依赖管理的渲染架构
5. **GPU Scene**：实例化数据 GPU 驻留

---

## 参考文献

- timlly, 《剖析虚幻渲染体系》系列, 2021
- Epic Games, Lumen: Dynamic Global Illumination and Reflections in Unreal Engine 5, GDC 2022
- Epic Games, Unreal Engine 5.4 Documentation
