---
tags: [shader/自研, shader/nanite, shader/material, shader/performance]
aliases: []
---

# Nanite 材质管线 — 虚拟几何 + 持久化 Material ID + Shading Bin

| 字段 | 内容 |
|------|------|
| **效果名称** | Nanite 虚拟几何的材质管线（5-bin 分类 + 持久化 Material Buffer + Shading Pipeline 缓存） |
| **类型** | 渲染管线 / 材质 / 几何 |
| **平台** | PC SM5 / SM6 / Console（不支持 mobile / WebGL） |
| **创建日期** | 2026-07-02 |
| **参考来源** | UE 5.8 主线源码 `Engine/Source/Runtime/Renderer/Private/Nanite/{NaniteMaterials,NaniteShading,NaniteShared,NaniteMaterialsSceneExtension}.{h,cpp}` + GDC 2022 Nanite 演讲 |

---

## 效果对比

| 传统材质管线 | Nanite 材质管线 |
|------------|---------------|
| 每个 Draw Call 绑一个材质 | **5 个 Bin** 分类（Triangle / Voxel / Curve / Raster / Fallback）|
| DrawIndexedInstanced 逐 mesh | **Persistent Material Buffer** 字节寻址 |
| 按 Mesh 排序（不跨 mesh） | **FNaniteShadingPipeline** 去重 + 按 Shader 分组 |
| Pixel Shader 像素级评估 | **Compute Shader** + Hidden Surface Removal（无 Z pre-pass）|
| Material ID 是 1 个 uint16 | **Material Index 在 MaterialDataBuffer 中** 每 triangle 1 个 entry |

---

## 核心代码

### 1. C++ 侧 — UE5.8 真实数据结构（简化）

```cpp
// NaniteMaterials.h:15-46
// 每个 material slot 占 16 bytes,内含 5 个 16-bit bin ID
struct FNaniteMaterialSlot {
    uint16 TriangleShadingBin;   // 主三角 shading
    uint16 VoxelShadingBin;      // 体素 shading (Lumen GI 捕获)
    uint16 CurveShadingBin;      // 曲线 shading (Hair/Fur)
    uint16 RasterBin;            // Raster fallback
    uint16 FallbackRasterBin;    // Software raster fallback

    struct FPacked { uint32 Data[4]; };
    inline FPacked Pack() const {
        FPacked Ret;
        Ret.Data[0] = (TriangleShadingBin | (VoxelShadingBin << 16u));
        Ret.Data[1] = (RasterBin | (FallbackRasterBin << 16u));
        Ret.Data[2] = CurveShadingBin;
        Ret.Data[3] = 0;
        return Ret;
    }
};

// NaniteShared.h:865-884
// 8 bytes,光栅化阶段 bin 三角形用
struct FNaniteShadingBin {
    int32  BinId = INDEX_NONE;
    uint16 BinIndex = 0xFFFFu;
    inline bool IsValid() const { return *this != FNaniteShadingBin(); }
};

// NaniteShared.h:891-959
// 核心:一个 material + shader + UB 组合的完整 pipeline state
struct FNaniteShadingPipeline {
    TPimplPtr<FNaniteBasePassData, EPimplPtrMode::DeepCopy>    BasePassData;
    TPimplPtr<FNaniteLumenCardData, EPimplPtrMode::DeepCopy>  LumenCardData;
    TPimplPtr<FNaniteMaterialCacheData, EPimplPtrMode::DeepCopy> MaterialCacheData;
    TPimplPtr<FMeshDrawShaderBindings, EPimplPtrMode::DeepCopy> ShaderBindings;

    const FMaterialRenderProxy* MaterialProxy = nullptr;
    const FMaterial* Material = nullptr;
    FRHIComputeShader*   ComputeShader   = nullptr;
    FRHIWorkGraphShader* WorkGraphShader = nullptr;     // 5.8 新增 Work Graph 路径
    FRHIUniformBuffer*   MaterialUB      = nullptr;
    int32 MaterialUBSerialNumber = 0;

    uint32 BoundTargetMask    = 0u;
    uint32 ShaderBindingsHash = 0u;
    uint32 MaterialBitFlags   = 0x0u;
    uint32 MaterialCBIndex    = INDEX_NONE;

    union {
        struct {
            uint16 bIsTwoSided      : 1;
            uint16 bIsMasked        : 1;   // alpha cutout
            uint16 bNoDerivativeOps : 1;   // 不能用 ddx/ddy
            uint16 bVoxel           : 1;
            uint16 bCurve           : 1;
            uint16 bPadding         : 11;
        };
        uint16 ShadingFlagsHash = 0;
    };

    // CityHash 128 位去重
    inline uint32 GetPipelineHash() const {
        uint64 H = uint64(reinterpret_cast<UPTRINT>(MaterialProxy) >> 4);
        H = CityHash128to64({ H, reinterpret_cast<UPTRINT>(ComputeShader) });
        H = CityHash128to64({ H, reinterpret_cast<UPTRINT>(WorkGraphShader) });
        H = CityHash128to64({ H, reinterpret_cast<UPTRINT>(MaterialUB) });
        H = CityHash128to64({ H, ShadingFlagsHash });
        H = CityHash128to64({ H, BoundTargetMask });
        H = CityHash128to64({ H, ShaderBindingsHash });
        return HashCombineFast(uint32(H & 0xFFFFFFFF), uint32((H >> 32) & 0xFFFFFFFF));
    }
};
```

### 2. 持久化 Material Buffer (NaniteMaterialsSceneExtension.h:149-156)

```cpp
// 跨帧持久,字节寻址,GPU 直接 ByteAddressBuffer 访问
class FMaterialBuffers {
public:
    FMaterialBuffers();

    // 每个 primitive (mesh) 一条元数据:MaterialBufferOffset + NumMaterials + MeshPassMask
    TPersistentByteAddressBuffer<FPackedPrimitiveData> PrimitiveDataBuffer;

    // 每个 triangle 一个 material entry(在 MaterialScatterStride = 4 uint32 = 16 bytes)
    TPersistentByteAddressBuffer<uint32> MaterialDataBuffer;
};

// FPackedPrimitiveData 字段(NaniteMaterialsSceneExtension.h:108-118)
struct FPackedPrimitiveData {
    uint32 MaterialBufferOffset;        // 此 primitive 在 MaterialDataBuffer 的起点
    uint32 MaterialMaxIndex : 8;        // 材质数 - 1 (0 = 单一材质)
    uint32 MeshPassMask     : 8;        // 此 primitive 参与的 mesh pass
    uint32 bHasUVDensities  : 1;
    // editor 字段省略
};
```

### 3. HLSL 侧 — 简化版可在自己的引擎跑的 Material 评估

```hlsl
// 模拟 Nanite 的 Material ID 字节寻址读取
// 实际 UE5 用 ByteAddressBuffer + Load4
StructuredBuffer<uint4> MaterialDataBuffer;  // 每 triangle 16 bytes

struct TriangleMaterialData {
    uint MaterialIndex0;       // triangle 的第一个材质 ID (0~7,8 个材质用 8 bits)
    uint MaterialIndex1;       // 第二个材质 ID
    uint MaterialIndex2;       // 第三个材质 ID
    uint Reserved;
};

// 字节寻址读取(对应 ByteAddressBuffer.Load(offset*4))
TriangleMaterialData LoadTriangleMaterial(uint TriangleId) {
    uint4 Packed = MaterialDataBuffer[TriangleId];
    TriangleMaterialData D;
    D.MaterialIndex0 = Packed.x & 0xFF;
    D.MaterialIndex1 = (Packed.x >> 8)  & 0xFF;
    D.MaterialIndex2 = (Packed.x >> 16) & 0xFF;
    D.Reserved = Packed.y;
    return D;
}

// 简化版 Shading Bin dispatch 逻辑(对应 NaniteShadeBinning.usf)
// 把三角形按 MaterialIndex 写入对应 bin,GPU 上并行完成
RWStructuredBuffer<uint> BinningCounter;       // 记录每个 bin 当前写了多少 triangle
StructuredBuffer<TriangleMaterialData> TriMat;
RWStructuredBuffer<uint> BinningOutput;        // [BinID][SlotInBin]

[numthreads(64, 1, 1)]
void MainCS(uint3 DTid : SV_DispatchThreadID) {
    uint TriId = DTid.x;
    if (TriId >= NumTriangles) return;

    TriangleMaterialData Mat = LoadTriangleMaterial(TriId);

    // 简单版本:按 MaterialIndex0 分 bin
    uint BinId = Mat.MaterialIndex0;
    uint Slot;

    // 原子计数器分配 bin slot
    InterlockedAdd(BinningCounter[BinId], 1, Slot);
    BinningOutput[BinId * MaxTrianglesPerBin + Slot] = TriId;
}

// Bin dispatch(每 material 一次 dispatch,模拟 FNaniteShadingPipeline 去重)
[numthreads(8, 8, 1)]
void MaterialEvaluateCS(
    uint3 DTid : SV_DispatchThreadID,
    uint3 GTid : SV_GroupID,
    uniform uint MaterialIndex,        // 对应 FNaniteShadingPipeline.MaterialProxy
    uniform StructuredBuffer<float4> MaterialConstants
) {
    // 从 bin 中拿三角形 ID
    uint BinSlot = GTid.x;
    uint TriId = BinningOutput[MaterialIndex * MaxTrianglesPerBin + BinSlot];
    if (TriId == INVALID_TRIANGLE) return;

    // 取三角形顶点
    FVertex V0 = VertexBuffer[IndexBuffer[TriId * 3 + 0]];
    FVertex V1 = VertexBuffer[IndexBuffer[TriId * 3 + 1]];
    FVertex V2 = VertexBuffer[IndexBuffer[TriId * 3 + 2]];

    // Pixel coordinate
    uint2 Pixel = DTid.xy;

    // Barycentric
    float3 Bary = ComputeBarycentric(Pixel, V0, V1, V2);

    // 简化版 material 评估
    float4 BaseColor = MaterialConstants[MaterialIndex * 4 + 0];
    float Roughness   = MaterialConstants[MaterialIndex * 4 + 1].x;

    // PBR shading (省略完整 BRDF)
    float3 Shaded = BaseColor.rgb * (1.0 - Roughness * 0.5);

    RWTexture2D<float4> Output;
    Output[Pixel] = float4(Shaded, BaseColor.a);
}
```

---

## 8 个核心参数

| 参数 | 来源 | 含义 | 调参建议 |
|------|------|------|----------|
| `TriangleShadingBin` | FNaniteMaterialSlot | 主三角形 shading 分桶 ID | 16 bits,最多 65k unique material |
| `VoxelShadingBin` | FNaniteMaterialSlot | 体素 shading bin (Lumen 捕获)| 同上,跟主 bin 不同 |
| `CurveShadingBin` | FNaniteMaterialSlot | 曲线 shading bin | Hair / Fur 用 |
| `RasterBin` | FNaniteMaterialSlot | Raster fallback bin | Compute 不可用时 |
| `bIsMasked` | FNaniteShadingPipeline | Alpha cutout 标志 | 开 → 多一次 ddx/ddy → 慢 |
| `bIsTwoSided` | FNaniteShadingPipeline | 双面标志 | 影响背面 normal 翻转 |
| `bNoDerivativeOps` | FNaniteShadingPipeline | 不能用 ddx/ddy | voxel / curve 强制 true |
| `MaterialCBIndex` | FNaniteShadingPipeline | Constant Buffer 索引 | 决定 GPU 端 buffer 访问 |

---

## 5 档性能分级

| 分级 | 改动 | 性能影响 | 适用场景 |
|------|------|----------|----------|
| **极简** | 单一材质 + WorkGraph (UE5.8+) | < 1ms | mobile 类项目（不支持 Nanite, 仅参考） |
| **标准** | 5-bin 分类 + Persistent Buffer | ~1.5ms | PC 中端 / 主机 |
| **高配** | 加上 VSM 阴影 + Lumen Capture 双 bin | ~2.5ms | PC 高端 / 过场动画 |
| **极限** | Work Graph + Material Cache + 全部 permutation | ~3.5ms | 截图级（不常用） |
| **Debug** | 开 `r.Nanite.MaterialDebug` + Instruction Count 输出 | 慢 5x+ | 性能分析 |

---

## 4 个变体版本

- **版本 A：WorkGraph 路径 (UE5.8 新)** — `FRHIWorkGraphShader` + 自动 load balancing,小场景性能更好
- **版本 B：Compute 路径 (经典)** — `FRHIComputeShader` + 显式 bin dispatch,稳定可预测
- **版本 C：Translucency 路径** — `NaniteTranslucency.usf`,普通 Nanite 不透,Translucency 走单独管线
- **版本 D：Lumen Card 路径** — `DispatchLumenMeshCapturePass`,把 Nanite 几何捕获到 Lumen Card

---

## 6 个已知问题与限制

1. **不支持 translucent** — Nanite 主路径只支持 opaque,半透要 fallback 到传统 mesh pass。
2. **不支持 mobile** — `r.Nanite 1` 在 mobile 上 disable,必须用传统 LOD。
3. **不支持 vertex animation** — Vertex shader 不能动顶点位置,只能 color/normal 级别。
4. **不支持 custom vertex factory** — 第三方 vertex format 需要先 wrap 成 FLocalVertexFactory。
5. **不支持 tessellation** — 曲面细分需在 export 前 baking。
6. **不支持 particle / decal** — 粒子和贴花有专门系统,不走 Nanite。

---

## 7 步调参 SOP

1. **`r.Nanite 1`** — 全局启用
2. **`r.Nanite.MaterialMaxIndex 0~255`** — 单 mesh 最多材质数,默认 256,大部分场景够用
3. **`r.Nanite.AssemblyScript 0/1`** — 是否用 Assembly Script (WorkGraph) 路径
4. **`r.Nanite.MaterialDebug 0/1`** — debug 模式下显示每个 bin 的指令数
5. **材质启用 `Used With Nanite`** — 必须勾,否则 fallback 严重
6. **`r.Nanite.ShadowContext 0/1/2`** — 0=无, 1=VSM, 2=全阴影
7. **`r.Nanite.LumenCapture 0/1`** — 是否参与 Lumen Card 捕获

---

## 关联知识库

- [[../../../02-引擎源码分析库/Unreal-Engine/UE5-Nanite-虚拟几何管线|Nanite 虚拟几何管线]]（UE5.3 老版,但 page-table 部分一致）
- [[../../../02-引擎源码分析库/Unreal-Engine/UE5.8-VolumetricCloud-体积云|VolumetricCloud 体积云]]（Voxel bin 跟 Lumen 共享）
- [[../后处理效果/Lumen-反射降级|Lumen 反射降级]]（5-bin 的 Triangle / Voxel 复用）
- [[../后处理效果/Lumen-GI-漫反射|Lumen GI 漫反射]]（Voxel ShadingBin 用法）

---

## 复用指南

如何把 Nanite 风格管线移植到自研引擎:

1. **建立 Persistent Material Buffer** — 用 `ByteAddressBuffer` 存每 triangle 材质索引,GPU 端 `Load4` 一次性读 4 个 uint
2. **5-bin 分类** — 不只是主 shading,预留 Voxel/Curve/Raster/Fallback 4 个旁路
3. **`FNaniteShadingPipeline` 去重** — 用 hash map 去重 `(material proxy, shader, UB, flags)` 组合,缓存 pipeline state
4. **Robin Hood Hash** — `TDefaultMapHashableKeyFuncs` 配 Robin Hood 哈希,O(1) 查找 + 稳定迭代
5. **Compute dispatch per bin** — 而不是 DrawIndexed,跟 virtual geometry 的 hidden surface removal 天然契合
6. **Material CBIndex 化** — 把所有材质参数塞进一个 mega-constant-buffer,GPU 用 `MaterialCBIndex` 索引

---

*Create date: 2026-07-02*  
*Last modified: 2026-07-02*
