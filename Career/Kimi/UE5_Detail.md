# UE5 技术详情（源码 + 打油诗）

> **用法：** 面试准备时深入阅读，每个话题配源码片段和打油诗。  
> **路径：** `C:\Git-repo-my\GameDevVault\Career\Kimi\`  
> **对应索引：** `UE5_Concept_Cards.md`

---

## §1 Nanite 详情

### §1.1 为什么叫 "Virtualized Geometry"？

```cpp
// Engine\Source\Runtime\Engine\Public\NaniteResources.h
// Nanite 资源的核心数据结构
namespace Nanite
{
    // FResources 包含 Cluster、Page、DAG 等数据
    // 类似虚拟内存的页管理：Page 是加载/卸载的最小单位
    struct FResources
    {
        TArray<uint8> RootData;        // DAG 根节点数据
        TArray<uint8> StreamablePages;  // 可流式加载的 Page 数据
        uint32 NumClusters;            // Cluster 总数
        uint32 NumNodes;               // DAG 节点总数
    };
}
```

**虚拟内存类比：**
- CPU 虚拟内存：虚拟地址 → 页表 → 物理页
- Nanite：虚拟 Cluster/Page → 运行时加载 → GPU Resident

```cpp
// Engine\Source\Runtime\Renderer\Private\Nanite\NaniteStreamingManager.cpp
// 流式加载管理：只加载可见 Page
void FStreamingManager::RequestPages(const FViewInfo& View)
{
    // 根据视锥和 HZB 计算可见 Cluster
    // 只加载对应的 Page，其他 Page 可以卸载
}
```

**打油诗：**
```
虚拟内存搬到 GPU，Page 级加载按需给，
Cluster 组 DAG 层级围，可见才加载不见飞。
LOD 决策 GPU 推，美术不用再累垂，
无级连续无 popping，微多边形精度追。
```

---

### §1.2 Cluster / Page / ClusterGroup 关系

```cpp
// Engine\Source\Runtime\Engine\Private\Nanite\NaniteBuild.cpp
// Cluster 是基本几何单元，一组三角形聚合
static void ClusterTriangles(
    const TArray<FStaticMeshBuildVertex>& Verts,
    const TArrayView<const uint32>& Indexes,
    const TArrayView<const int32>& MaterialIndexes,
    TArray<FCluster>& Clusters,    // 输出：Cluster 数组
    const FBounds& MeshBounds,
    uint32 NumTexCoords,
    bool bHasColors)
{
    // 1. 构建边哈希表，找到共享边
    // 2. 使用 FGraphPartitioner 将三角形图分割为 Cluster
    // 3. 每个 Cluster 包含约 128 个三角形（FCluster::ClusterSize）
}
```

```cpp
// Engine\Source\Runtime\Engine\Public\NaniteResources.h
// ClusterGroup 是 LOD 层级管理单元
struct FClusterGroup
{
    uint32 MipLevel;           // LOD 层级
    float MinLODError;         // 最小误差（子节点）
    float MaxParentLODError;   // 最大误差（父节点）
    TArray<uint32> Children;   // 子 Cluster 索引
    FSphere Bounds;            // 包围球
    FSphere LODBounds;         // LOD 包围球
};

// 关系：Cluster ∈ ClusterGroup ∈ Page
// DAG 描述 ClusterGroup 的父子依赖
```

**打油诗：**
```
Cluster 一百二十八，三角形聚合是一家，
ClusterGroup 层级搭，DAG 父子关系画，
Page 是页加载闸，流式按需不拖垮，
虚拟几何像书匣，需要哪页取哪页。
```

---

### §1.3 为什么需要硬件 + 软件光栅化？

```cpp
// Engine\Source\Runtime\Renderer\Private\Nanite\NaniteRender.h
// 光栅化技术枚举
enum class ERasterTechnique : uint8
{
    LockBufferFallback,     // 64 位原子不可用时的备用
    PlatformAtomics,        // 平台原生 64 位原子
    NVAtomics,              // NVIDIA 扩展
    AMDAtomicsD3D11,        // AMD D3D11 扩展
    AMDAtomicsD3D12,        // AMD D3D12 扩展
    DepthOnly,              // 仅深度光栅化
};

// 调度模式：硬件光栅化大三角 + 软件光栅化小三角
enum class ERasterScheduling : uint8
{
    HardwareOnly,               // 纯硬件光栅化
    HardwareThenSoftware,     // 硬件先，软件后
    HardwareAndSoftwareOverlap, // 硬件软件重叠
};
```

```cpp
// 软件光栅化（Compute Shader）处理小三角
// 硬件光栅化在三角形 < 1 像素时效率崩溃：
// 1. Quad Overdraw：一个 2×2 像素块覆盖 4 个像素，但小三角只覆盖 1 个，浪费 3 个
// 2. Early-Z 失效：硬件无法有效剔除被遮挡的小三角
// 3. 精度问题：亚像素级三角形的深度和覆盖率计算误差大

// CS 软件光栅化：直接计算每个像素是否被覆盖，精确无浪费
// 但大三角用 CS 光栅化效率低（线程发散），所以硬件处理大三角
```

**打油诗：**
```
硬件光栅大三角，Quad 并行效率高，
小三角来精度差，Early-Z 失效乱糟糟。
软件光栅 CS 跑，逐像素计算不瞎搞，
亚像素覆盖精确到，两者互补各显妙。
```

---

### §1.4 Nanite vs UE4 传统 LOD 本质区别

```cpp
// UE4：CPU 预计算 LOD，运行时切换
// FStaticMeshRenderData::LODResources[LODIndex]
// 每个 LOD 是独立 Mesh，切换时 popping 明显

// UE5 Nanite：GPU 运行时动态选择 Cluster 精度
// Engine\Source\Runtime\Renderer\Private\Nanite\NaniteRender.cpp
void RenderNanite(
    FRDGBuilder& GraphBuilder,
    const FViewInfo& View,
    const FCullingContext& CullingContext)
{
    // GPU-Driven Culling：根据像素覆盖度选择 Cluster
    // 无 popping：Cluster 精度连续变化，不是离散切换
    // 无 Draw Call：GPU 直接生成绘制指令
}
```

**本质区别表：**

| 维度 | UE4 | UE5 Nanite |
|------|-----|------------|
| LOD 决策 | CPU 预计算 | GPU 运行时动态 |
| Draw Call | 每个 Mesh 独立 | GPU-Driven 批量 |
| 数据加载 | 整个 Mesh | Page 级流式 |
| 三角形大小 | 受硬件限制 | 软件光栅化支持亚像素 |
| 美术工作 | 制作多档 LOD | 无需手动 LOD |

**打油诗：**
```
UE4 LOD 美术造，CPU 切换 popping 跳，
Nanite 计算 GPU 搞，无级连续自动调。
Page 流式按需到，Draw Call 瓶颈全消掉，
微多边形精度飙，一入 Nanite 美术笑。
```

---

### §1.5 Fallback 条件

```cpp
// Engine\Source\Runtime\Engine\Public\NaniteResources.h
// Nanite 支持检查
bool FMeshNaniteSettings::IsSupported() const
{
    // 检查：是否不透明材质
    // 检查：是否没有自定义 Vertex Factory
    // 检查：平台是否支持 Nanite
    return bSupported && !bIsTranslucent && !bCustomVertexFactory;
}
```

**当前限制（截至 UE5.5）：**
1. **Translucent**：不支持（Masked/Two-Sided 在 5.4+ 通过 Programmable Rasterizer 支持）
2. **Morph Targets**：Nanite Skeletal Mesh 不支持 Blendshape/Morph
3. **Cloth**：完全不兼容
4. **Custom Vertex Factory**：不支持
5. **移动端**：计算和带宽受限

**已解决（5.4/5.5+）：**
- ✅ Skeletal Mesh（骨骼动画）
- ✅ Foliage（Masked/Two-Sided + Assemblies + Voxels + Skinning）
- ✅ Landscape / Spline Mesh

**打油诗：**
```
半透明不兼容，Morph Cloth 走不通，
移动端受限制，Custom Factory 不能用。
骨骼植被已解封，地形样条也跟进，
未来 Translucent 和 Hair，Epic 还在研究中。
```

---

### §1.6 限制与未来

```cpp
// UE5.5+ Nanite Foliage 系统
// Engine\Source\Runtime\Engine\Public\NaniteFoliage.h
// Assemblies + Voxels + Skinning
struct FNaniteAssembly
{
    // 微实例化：相同部件共享几何数据
    // 41M 三角形树 → 29MB 磁盘（原 3.5GB）
    // 36MB 流式内存 → 2.7MB
    uint32 MaxInstances;  // 65k 实例上限
};
```

**未来方向：**
1. Skinned Nanite（动态骨骼 + 微多边形）
2. 更广泛材质（Translucent、Hair、Subsurface）
3. 移动端优化（Tile-Based、更小 Page）
4. AI 辅助内容生成（Neural LOD、Neural Texture）

**打油诗：**
```
静态不透明是边界，5.5 骨骼已解限，
植被系统巫师演，微实例化省空间。
未来 Translucent 和 Hair，移动端优化在追赶，
AI 生成 Neural 变，微多边形通用天。
```

---

## §2 Lumen 详情

### §2.1 Surface Cache 降维

```cpp
// Engine\Source\Runtime\Renderer\Private\Lumen\LumenSceneData.h
// Surface Cache 存储：Radiance / Normal / Depth
struct FLumenCard
{
    // 6 个方向对应立方体 6 个面
    // 每个方向存储 Radiance Atlas（颜色 + 光照）
    FIntPoint RadianceAtlasAllocation;  // Radiance Atlas 的分配位置
    FIntPoint NormalAtlasAllocation;   // Normal Atlas 的分配位置
    FIntPoint DepthAtlasAllocation;    // Depth Atlas 的分配位置
};
```

```cpp
// Engine\Source\Runtime\Renderer\Private\Lumen\LumenSceneRendering.cpp
// Surface Cache 更新：增量式，只更新 dirty Card
void BeginUpdateLumenSceneTasks(
    FRDGBuilder& GraphBuilder,
    const FSceneTextures& SceneTextures,
    const FViewInfo& View)
{
    // 1. 脏检测：哪些 Mesh/Card 发生变化
    // 2. 优先级排序：按距离和重要性
    // 3. 限制更新：每帧最多 CardCapturesPerFrame 张 Card
    // 4. 异步更新：ParallelFor 并行捕获
}
```

**降维原理：**
- 3D 场景：几十亿三角形 → 射线-三角形求交（expensive）
- Surface Cache：可见表面的 2D 纹理 → UV 随机访问（cheap）
- 计算复杂度：`O(数十亿 × 采样)` → `O(百万 × 采样)`

**打油诗：**
```
Surface Cache 降维妙，Radiance 法线深度照，
3D 场景几十亿跳，2D 纹理百万到。
射线求交变 UV 找，每帧只刷 dirty 卡，
O(数十亿) 变 O(百万)少，缓存替代实时跑。
```

---

### §2.2 三级 Trace 回退

```cpp
// Engine\Source\Runtime\Renderer\Private\Lumen\LumenScreenProbeGather.cpp
// RenderLumenScreenProbeGather：三级 Trace 的核心 Pass
FSSDSignalTextures RenderLumenScreenProbeGather(
    FRDGBuilder& GraphBuilder,
    const FSceneTextures& SceneTextures,
    const ScreenSpaceRayTracing::FPrevSceneColorMip& PrevSceneColorMip,
    FRDGTextureRef LightingChannelsTexture,
    const FViewInfo& View,
    FPreviousViewInfo* PreviousViewInfos,
    bool& bLumenUseDenoiserComposite,
    FLumenMeshSDFGridParameters& MeshSDFGridParameters)
{
    // 1. Screen Trace：利用上一帧的 Scene Color + Depth
    // 2. Mesh SDF Trace：查询 Mesh 的有向距离场
    // 3. Hardware Ray Trace：GPU 硬件光追（RTX）
    // 回退：Screen Trace 失败 → Mesh SDF → Hardware RT
}
```

```cpp
// Mesh SDF Trace：有向距离场查询
// Engine\Source\Runtime\Renderer\Private\Lumen\LumenMeshSDFTracing.cpp
// Sphere Tracing 步进：每次步进 = 当前 SDF 值（到最近表面的距离）
// 大步跳过空区域，只在接近表面时细化
float SphereTrace(
    const FMeshSDFVolumeTexture& SDFTexture,
    const FVector& RayOrigin,
    const FVector& RayDirection)
{
    float T = 0.0f;
    while (T < MaxDistance)
    {
        float SDF = SampleSDF(SDFTexture, RayOrigin + RayDirection * T);
        if (SDF < 0.0f) return T;  // 命中表面（穿过零等值面）
        T += SDF;  // 步进距离 = SDF 值（安全距离）
    }
    return -1.0f;  // 未命中
}
```

**打油诗：**
```
Screen Trace 近处妙，上一帧数据零开销，
屏幕之外找不到，Mesh SDF 来救号。
有向距离场体积罩，Sphere Tracing 大步跳，
空区域跳过不瞎搞，接近表面再细描。
远处复杂遮挡到，Hardware RT 精确照，
三级回退层层套，效率质量平衡好。
```

---

### §2.3 增量更新机制

```cpp
// Engine\Source\Runtime\Renderer\Private\Lumen\LumenSceneRendering.cpp
// Surface Cache 增量更新：不是每帧全部重建
void UpdateLumenScene(
    FRDGBuilder& GraphBuilder,
    const FSceneTextures& SceneTextures,
    const FViewInfo& View)
{
    // 1. 脏检测：移动、变形、材质变化的 Mesh
    // 2. 优先级：距离摄像机近 + 变化重要性高
    // 3. 限制数量：每帧最多 CardCapturesPerFrame
    // 4. 异步：ParallelFor 并行准备数据
    // 5. Atlas 管理：大小变化时重新分配
}
```

**为什么不需要预计算 Lightmap？**
- Lightmap：离线烘焙所有光路 → 运行时只采样（静态，不能响应动态光源）
- Lumen：运行时实时捕获和更新 → 每帧增量更新 dirty Card → 响应动态光源和物体

**打油诗：**
```
Lightmap 烘焙离线搞，静态光源不能跑，
Lumen 实时增量妙，dirty Card 每帧扫。
移动变形材质调，优先级排序距离靠，
异步并行捕获到，动态响应不用烤。
```

---

### §2.4 Screen Probe Gather

```cpp
// Engine\Source\Runtime\Renderer\Private\Lumen\LumenScreenProbeGather.cpp
// Screen Probe Gather：核心间接光照 Pass
// 1. Uniform Placement：屏幕空间均匀放置
// 2. Adaptive Placement：光照变化剧烈区域增加密度
// 3. Cone Tracing：发射 Cone 在 Surface Cache 上采样
// 4. MipMap：远距离用低分辨率，近距用高分辨率
FSSDSignalTextures RenderLumenScreenProbeGather(...)
{
    // Uniform Placement：每 16×16 像素一个探针
    // Adaptive Placement：边缘/阴影边界增加探针
    // Cone Tracing：八面体方向分布，Cone 开口角随距离增大
    // MipMap：远距离 1/8 分辨率，采样数从 100 降到 10
}
```

```cpp
// Cone Tracing + MipMap 的 O(log n) 近似
// 传统射线追踪：O(n) 逐点采样
// Cone Tracing：Cone 开口对应 Mip 层级，远距离低分辨率，O(log n)
// 采样数：100 → 10（远距离）
```

**打油诗：**
```
屏幕探针均匀放，16×16 网格框，
边缘阴影加密上，Adaptive 探针暗边找。
Cone Tracing 锥体照，八面体方向分布妙，
开口随距自然涨，MipMap 模糊远距描。
O(n) 变 O(log n)跳，采样百十效率飙，
Radiance 累积前后套，间接光照精确到。
```

---

### §2.5 Lumen Card

```cpp
// Engine\Source\Runtime\Renderer\Private\Lumen\LumenSceneData.h
// Lumen Card：每个 Mesh 表面的 6 方向光照捕获单元
struct FLumenCard
{
    // 通常 6 个方向对应立方体 6 个面
    // 每个方向存储 Radiance Atlas（颜色 + 光照）
    FVector4 Orientation;  // 方向四元数
    FVector3 Position;     // 世界位置
    float Distance;        // 与表面的偏移距离
    
    FIntPoint RadianceAtlasAllocation;  // Radiance Atlas 分配位置
};

// Card 是 Lumen 捕获和更新光照的最小单位
// 每帧限制更新数量：CardCapturesPerFrame
```

**打油诗：**
```
Lumen Card 六面照，立方体方向全包到，
Radiance Atlas 颜色套，光照信息里面藏。
Card 是更新最小量，每帧限制不超限，
 dirty 检测优先级算，距离重要先刷新。
```

---

### §2.6 算法/性能/局限性对比

**算法对比：**

| 维度 | UE4 RTGI | UE5 Lumen |
|------|----------|-----------|
| 算法 | 纯屏幕空间 Ray Marching | 多层级 Trace + 缓存传播 |
| 反弹 | 有限（1-2 次） | 无限（Radiosity 迭代） |
| 屏幕外 | 完全缺失 | Mesh SDF / HW RT 处理 |
| 计算 | 每帧全屏重新发射射线 | 缓存之间纹理采样 |

**性能对比：**

| 维度 | UE4 RTGI | UE5 Lumen |
|------|----------|-----------|
| 单次反弹 | 1-2ms | Screen Trace 0.1ms + Mesh SDF 0.5ms |
| 多次反弹 | 线性叠加（2次≈3-4ms） | 增量 Radiosity（额外 0.5-1ms） |
| 显存 | 小 | 大（Surface Cache Atlas + Radiance Atlas） |
| 总耗时 | 2-4ms（1-2 次反弹） | 2-3ms（无限反弹） |

**局限性：**
- UE4 RTGI："屏幕空间 = 近视眼"，完全无法处理屏幕外
- Lumen："缓存延迟 + 内存大户 + 移动端缺席"

**打油诗：**
```
RTGI 屏幕空间跑，Ray Marching 逐像素找，
屏幕之外全丢掉，反弹一次 Pass 一套。
Lumen 缓存传播妙，Radiosity 迭代摇，
Gather Scatter 来回跳，无限反弹成本小。
RTGI 近视眼不好，Lumen 内存大户饱，
移动端缺席还没到，各有优劣要记牢。
```

---

### §2.7 Radiosity 迭代详解

```cpp
// Radiosity 迭代：缓存之间传播能量
// 不是每帧发射新射线，而是 Surface Cache 之间的纹理采样

// 1. 初始状态：每个 Card 的 Radiance Atlas 存储直接光照
//    Direct Light + Emissive = BaseColor × LightColor + Emissive

// 2. Gather 阶段：查询周围 Card 的 Radiance
//    向周围发射 Cone 在 Surface Cache 上采样
//    收集其他表面的间接辐射度

// 3. Scatter 阶段：按 BRDF 散射
//    Indirect = GatheredRadiance × BRDF
//    写回当前 Card 的 Radiance Atlas

// 4. 迭代：重复 Gather→Scatter
//    每次迭代等效于一次光线反弹
//    计算成本：O(N × 纹理采样) vs O(N × 射线求交)

// 5. 增量更新：只更新 dirty Card
//    已稳定的 Card 复用上一帧结果
```

**为什么能"无限反弹"？**
- 迭代 N 次等效于 N 次光线反弹
- 但每次迭代不是发射新射线，而是纹理采样（cheap）
- 射线求交需要遍历 BVH/SDF（expensive）
- 纹理采样是 GPU 随机访问（cheap）

**打油诗：**
```
Radiosity 迭代妙，Gather Scatter 来回摇，
直接光照先存好，周围 Card 采样到。
BRDF 散射再写回，一次迭代一次跳，
不是射线重新发，纹理采样成本低。
迭代两三次收敛，无限反弹成本小，
增量更新 dirty 扫，稳定 Card 复用老。
```

---

### §2.8 Mesh SDF 生成与命中查询

```cpp
// Mesh SDF 生成：离线 Cook 阶段
// Engine\Source\Runtime\Engine\Private\DistanceField\MeshDistanceField.cpp
void GenerateMeshDistanceField(
    const FStaticMesh& StaticMesh,
    FMeshDistanceField& OutDistanceField)
{
    // 1. 在 Object Space 生成 3D 体积纹理（64³ 或自适应）
    // 2. 对每个体素，计算到最近三角形表面的有向距离
    // 3. 算法：点到平面距离 + Barycentric 坐标判断区域
    // 4. 结果：纯几何数据，只存距离（标量）
}
```

```cpp
// Mesh SDF 命中后：颜色/法线来自 Surface Cache（Lumen Card）
// 命中点世界坐标 → 查找 FLumenMeshCards → 选择最佳 Card → UV 投影 → 采样 Atlas

// 1. 命中点世界坐标 → 查找该 Mesh 对应的 FLumenMeshCards
// 2. 根据射线方向选择最佳 Card（6 个面，选面向最接近射线反方向的）
// 3. 命中点投影到 Card 平面，计算 UV 坐标
// 4. 从 Card 的 Surface Cache Atlas 采样：
//    - Radiance Atlas → 颜色
//    - Normal Atlas → 法线
//    - Depth Atlas → 深度验证
//    - Emissive Atlas → 自发光
// 5. 如果 Card 未更新或越界 → 回退到 GBuffer 或 Hardware RT
```

**打油诗：**
```
Mesh SDF 离线造，64 立方体素罩，
点到平面距离算，Barycentric 区域到。
纯几何数据只存标，颜色法线不打扰，
命中之后 Card 来找，UV 投影采样妙。
Radiance Normal 全拿到，Depth 验证不瞎搞，
SDF 求交 Card 填色，两级分工各自照。
```

---

## §3 VSM 详情

### §3.1 按需分配机制

```cpp
// Engine\Source\Runtime\Renderer\Private\VirtualShadowMaps\VirtualShadowMapArray.cpp
// BuildPageAllocations：核心页分配函数
void FVirtualShadowMapArray::BuildPageAllocations(
    FRDGBuilder& GraphBuilder,
    const FViewInfo& View)
{
    // 1. GeneratePageFlagsFromPixels：屏幕像素反推
    //    CS 遍历屏幕 tile，从 GBuffer/Depth 获取世界坐标
    //    投影到光源视图空间，计算落在哪个 page 的哪个 MipLevel
    //    标记该 page 为 REQUESTED
    
    // 2. MarkCoarsePages：方向光 Clipmap 粗粒度覆盖
    //    远距离标记 coarse level page，避免阴影缺失
    
    // 3. UpdatePhysicalPages：缓存复用
    //    查询上一帧 PhysicalPageMetaData
    //    CACHED（未 dirty）→ 复用
    //    UNCACHED（动态物体移动）→ 重新渲染
    //    UNREFERENCED → 放入 LRU 延迟释放
    
    // 4. AllocateNewPageMappings：新页分配
    //    从 Available Page List 弹出空闲物理页
    //    建立 PageTable 映射（虚拟页 ID → 物理页地址）
    //    物理页不足时回收 UNREFERENCED 的页
    
    // 5. PageTable 编码：uint 数组，解码为 FShadowPhysicalPage
}
```

```cpp
// PageTable 编码：Shader 中解码物理地址
// Engine\Source\Runtime\Renderer\Private\VirtualShadowMaps\VirtualShadowMapShader.cpp
uint ShadowDecodePageTable(uint EncodedPage)
{
    // 解码 uint 为 FShadowPhysicalPage
    // 获取物理页地址 + 是否有效位
    // 用于采样阴影深度
}
```

**为什么 Camera 驱动而非 Light 驱动？**
- Light 视角：所有被光照射的区域都分配 page → 很多区域 Camera 看不到
- Camera 视角：只有 Camera 需要采样的区域才分配 page → 精确按需

**打油诗：**
```
VSM 按需分配妙，Camera 像素反推号，
屏幕 tile 遍历到，世界坐标投影跑。
光源空间 page 标记，REQUESTED 才需要，
Light 视角全要到，Camera 驱动精确套。
缓存复用 LRU 保，新页分配 Available 找，
页表编码 Shader 解码，阴影深度精确照。
```

---

### §3.2 VSM vs CSM

| 维度 | UE4 CSM | UE5 VSM |
|------|---------|---------|
| 分配 | 预分配固定级联纹理 | 按需分配虚拟页 |
| 分辨率 | 每级联固定 | 动态调整（近距高，远距低） |
| 内存 | 大量预分配 | 按需分配，节省内存 |
| 与几何 | 无直接绑定 | 与 GPUScene + Nanite 紧密绑定 |
| 方向光 | 级联 | Clipmap 多层等大分辨率 |

**打油诗：**
```
CSM 级联预分配，固定分辨率内存沉，
VSM 虚拟页按需跟，动态调整省内存。
Clipmap 方向光分层，近距高分辨远距省，
GPUScene 数据共享，Nanite 几何紧密捆。
```

---

### §3.3 Nanite + VSM 数据共享

```cpp
// Engine\Source\Runtime\Renderer\Private\ShadowRendering.cpp
// RenderShadowDepthMaps：Shadow 渲染入口
void FSceneRenderer::RenderShadowDepthMaps(
    FRDGBuilder& GraphBuilder,
    FInstanceCullingManager& InstanceCullingManager)
{
    // 1. GPUScene 上传：Shadow 影响到的 Primitives 上传到 GPUScene
    //    与 Nanite 渲染共用同一套 FGPUScene 实例化数据
    for (FProjectedShadowInfo* ShadowInfo : VirtualShadowMapShadows)
    {
        Scene->GPUScene.UploadDynamicPrimitiveShaderDataForView(
            GraphBuilder, *Scene, *ShadowInfo->ShadowDepthView, ...);
    }
    
    // 2. Instance Culling：GPU 裁剪
    //    使用同一套 CullInstances 代码，但输入不同的 ViewMatrix
    InstanceCullingManager.BeginDeferredCulling(GraphBuilder, Scene->GPUScene);
    
    // 3. VSM Nanite 渲染：复用 Nanite 的 Cluster 数据
    //    从 Light Camera 视角做 GPU-Driven 裁剪和光栅化
    VirtualShadowMapArray.RenderVirtualShadowMapsNanite(GraphBuilder, ...);
    VirtualShadowMapArray.RenderVirtualShadowMapsNonNanite(GraphBuilder, ...);
}
```

**关键澄清：**
- 共享的是**图元级数据**（GPUScene 实例数据 + Nanite 几何数据）
- **视图级裁剪**是独立的（主相机 vs Light Camera 的 Frustum 和 HZB）
- VSM 的 Nanite 渲染是"同一套数据，换个视角看"

**打油诗：**
```
Nanite VSM 共享妙，图元级数据不用劳，
GPUScene 实例化缓冲，Primitive 变换全包到。
视图裁剪各自跑，Main Camera 和 Light 视角，
Frustum HZB 独立造，同一套数据换视角照。
Cluster Page 数据复用，Light Camera 裁剪光栅化，
CPU 无需重建 Primitive，Draw Call 开销全消掉。
```

---

## §4 面试扩展

### §4.1 火炬之光 UE4→UE5 升级挑战

```cpp
// 1. 自定义 HLSL 适配
// UE5 引入 Render Graph，Shader Pipeline 变化
// 需要验证所有自定义 Shader（如 GSR 超分）的兼容性

// 2. 移动端 Nanite/Lumen 可用性评估
// 火炬是移动游戏（Android/iOS）
// Lumen 和 Nanite 在移动端有严格限制
// 需要评估哪些平台可以开启，哪些 fallback

// 3. Cook 管线适配
// Nanite 资产需要 BuildNaniteData（特殊构建流程）
// 火炬有大量自定义 Cook 逻辑（如 Shader Patch）
// 需要与 Nanite 的构建流程整合

// 4. 性能基线重测
// UE5 渲染开销模型与 UE4 不同
// 需要重新评估 GPU 和 CPU 性能基线
// 特别是 Nanite 的 GPU-Driven Culling 对 GPU 占用率的影响

// 5. 工具链升级
// 材质编辑器、RenderDoc、Profiler 等需要适配 UE5
```

**打油诗：**
```
UE4 升级 UE5 挑战多，Shader 管线要适配，
移动端能力评估做，Cook 管线整合过。
性能基线重测播，工具链升级不错过，
Nanite Lumen 新特性，火炬是否能用要琢磨。
```

---

### §4.2 GPU-Driven Pipeline 细节

```cpp
// Engine\Source\Runtime\Renderer\Private\InstanceCulling\InstanceCullingManager.cpp
// Instance Culling：GPU 裁剪核心
void FInstanceCullingManager::CullInstances(
    FRDGBuilder& GraphBuilder, FGPUScene& GPUScene)
{
    // 1. 从 GPUScene 获取实例化数据
    // 2. 对每个视图，执行 CullInstances Compute Shader
    // 3. 生成 VisibleInstanceFlags（每个视图每个实例的可见性位图）
    // 4. 后续渲染直接读取该位图，无需 CPU 干预
}

// Engine\Source\Runtime\Renderer\Private\Nanite\NaniteRender.cpp
// Nanite GPU-Driven 渲染流程
void RenderNanite(FRDGBuilder& GraphBuilder, const FViewInfo& View, ...)
{
    // 1. GPUScene 更新：上传实例化数据
    // 2. Cluster Culling：CS 根据视锥和 HZB 裁剪不可见 Cluster
    // 3. Instance Culling：基于 GPUScene 的实例数据裁剪
    // 4. Draw Command Generation：GPU 直接生成绘制指令
    // 5. Rasterization：硬件 + 软件光栅化
}
```

**打油诗：**
```
GPU-Driven 流程妙，CPU 不再做主导，
Cluster Culling 先裁掉，Instance Culling 实例套。
绘制指令 GPU 造，无需 CPU 再操劳，
光栅化软硬互补，海量几何不卡壳。
```

---

### §4.3 Surface Cache 更新源码

```cpp
// Engine\Source\Runtime\Renderer\Private\Lumen\LumenSceneRendering.cpp
// Surface Cache 增量更新：每帧只更新 dirty Card
void UpdateLumenScene(FRDGBuilder& GraphBuilder, ...)
{
    // 1. 脏检测：哪些 Mesh/Card 发生变化
    //    - 移动、变形、材质变化
    //    - 新进入视口的 Card
    
    // 2. 优先级排序：
    //    - 距离摄像机近 → 高优先级
    //    - 变化重要性高 → 高优先级
    
    // 3. 限制更新数量：
    //    - 每帧最多 CardCapturesPerFrame 张 Card
    //    - 每帧最多 CardTexelsToCapturePerFrame 个纹素
    
    // 4. 异步更新：
    //    - ParallelFor 并行准备更新数据
    //    - RasterizeLumenCards 捕获光照
    
    // 5. Atlas 管理：
    //    - 如果 Atlas 大小变化，重新分配整个 Atlas
    //    - 增量更新：只更新 dirty 区域，非整个 Atlas
}
```

**打油诗：**
```
Surface Cache 更新妙，脏检测先找变化到，
优先级排序距离靠，近的重要的先刷新。
限制数量不超限，每帧 Card 有上限，
异步并行捕获到，Atlas 管理增量妙。
```

---

## 源码文件速查表

| 功能 | 文件路径 | 关键类/函数 |
|------|----------|-------------|
| Nanite 资源 | `Engine\Source\Runtime\Engine\Public\NaniteResources.h` | `Nanite::FResources` |
| Nanite 渲染 | `Engine\Source\Runtime\Renderer\Private\Nanite\NaniteRender.cpp` | `RenderNanite` |
| Nanite 裁剪 | `Engine\Source\Runtime\Renderer\Private\InstanceCulling\InstanceCullingManager.cpp` | `CullInstances` |
| Nanite 构建 | `Engine\Source\Runtime\Engine\Private\Nanite\NaniteBuild.cpp` | `ClusterTriangles`, `BuildDAG` |
| Lumen 场景数据 | `Engine\Source\Runtime\Renderer\Private\Lumen\LumenSceneData.h` | `FLumenSceneData`, `FLumenCard` |
| Lumen 渲染 | `Engine\Source\Runtime\Renderer\Private\Lumen\LumenSceneRendering.cpp` | `BeginUpdateLumenSceneTasks` |
| Screen Probe | `Engine\Source\Runtime\Renderer\Private\Lumen\LumenScreenProbeGather.cpp` | `RenderLumenScreenProbeGather` |
| Mesh SDF | `Engine\Source\Runtime\Renderer\Private\Lumen\LumenMeshSDFTracing.cpp` | `SphereTrace` |
| VSM 数组 | `Engine\Source\Runtime\Renderer\Private\VirtualShadowMaps\VirtualShadowMapArray.cpp` | `BuildPageAllocations` |
| VSM 管理 | `Engine\Source\Runtime\Renderer\Private\VirtualShadowMaps\VirtualShadowMaps.h` | `FVirtualShadowMap` |
| GPUScene | `Engine\Source\Runtime\Renderer\Private\GPUScene.cpp` | `FGPUScene` |
| 阴影渲染 | `Engine\Source\Runtime\Renderer\Private\ShadowRendering.cpp` | `RenderShadowDepthMaps` |

---

**整理完成时间：** 2026-06-20  
**对应索引：** `UE5_Concept_Cards.md`  
**整理者：** 俞航（用于 JD：游戏开发专家 AI 训练方向）
