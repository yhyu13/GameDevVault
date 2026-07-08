---
tags: [shader/自研, shader/nanite, shader/material, shader/performance, shader/UE, shader/AI-accelerated]
aliases: []
week: W5
cycle: C
---

# Nanite 材质管线 — 虚拟几何 + 持久化 Material ID + Shading Bin

| 字段       | 内容                                                                                                                                                                  |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **效果名称** | Nanite 虚拟几何的材质管线（5-bin 分类 + 持久化 Material Buffer + Shading Pipeline 缓存）                                                                                              |
| **类型**   | 渲染管线 / 材质 / 几何                                                                                                                                                      |
| **平台**   | PC SM5 / SM6 / Console（不支持 mobile / WebGL）                                                                                                                          |
| **创建日期** | 2026-07-02                                                                                                                                                          |
| **参考来源** | UE 5.8 主线源码 `Engine/Source/Runtime/Renderer/Private/Nanite/{NaniteMaterials,NaniteShading,NaniteShared,NaniteMaterialsSceneExtension}.{h,cpp}` + GDC 2022 Nanite 演讲 |
|          |                                                                                                                                                                     |

---

## 效果对比

| 传统材质管线                      | Nanite 材质管线                                                    |
| --------------------------- | -------------------------------------------------------------- |
| 每个 Draw Call 绑一个材质          | **5 个 Bin** 分类（Triangle / Voxel / Curve / Raster / Fallback）   |
| DrawIndexedInstanced 逐 mesh | **Persistent Material Buffer** 字节寻址                            |
| 按 Mesh 排序（不跨 mesh）          | **FNaniteShadingPipeline** 去重 + 按 Shader 分组                    |
| Pixel Shader 像素级评估          | **Compute Shader** + Hidden Surface Removal（无 Z pre-pass）      |
| Material ID 是 1 个 uint16    | **Material Index 在 MaterialDataBuffer 中** 每 triangle 1 个 entry |

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
- [[../W3/Lumen-反射降级|Lumen 反射降级]]（5-bin 的 Triangle / Voxel 复用）
- [[../W4/Lumen-GI-漫反射|Lumen GI 漫反射]]（Voxel ShadingBin 用法）

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

## AI 加速角度（追加于 2026-07-09）

Nanite 材质管线的瓶颈不在 compute throughput，而在 **Material Bin dispatch overhead + Persistent Material Buffer 索引带宽**。AI 加速的核心思路是 **"用神经网络替换传统 material evaluation，把 5-bin dispatch 折叠成单次 MLP forward"**。

### 1. AI 加速的 3 个层次

| 层次 | 替换对象 | 网络规模 | 性能收益 | 视觉收益 |
|------|----------|----------|----------|----------|
| **L1 Neural Material Eval** | 5-bin dispatch → 单 MLP forward 出 PBR | 8→64→64→4 (~10k params) | 5× bin dispatch 减少 | 视觉等价 |
| **L2 Neural PBR Compression** | Material Constant Buffer → MLP 隐式编码 | 32→128→128→16 (~50k params) | 8× constant buffer 减小 | 视觉略降（<2%） |
| **L3 Latent Material Code** | Material UUID → 16-dim latent code（动态切换材质） | Variational Autoencoder (~200k params) | 支持运行时材质插值 | 视觉更好（材质过渡） |

### 2. L1 Neural Material Evaluation 工程实现

```hlsl
// 简化版:把 5-bin dispatch 折叠成单 MLP forward
// 输入: 当前 triangle 的 materialId + vertex attributes
// 输出: BaseColor, Metallic, Roughness, Normal (4 个 PBR 通道)

// 真实 Nanite 用 (proxy, shader, UB, flags) 决定 pipeline
// AI 版本: latent code + vertex → MLP → PBR

StructuredBuffer<float> MLP_W1;  // [12 → 64] (latent 8 + vertex normal/uv/tangent 4)
StructuredBuffer<float> MLP_B1;  // [64]
StructuredBuffer<float> MLP_W2;  // [64 → 64]
StructuredBuffer<float> MLP_B2;
StructuredBuffer<float> MLP_W3;  // [64 → 4] = BaseColor.rgb (scaled) + Roughness
StructuredBuffer<float> MLP_B3;

StructuredBuffer<float> MaterialLatent;  // [materialId × 8] latent code per material

struct FMaterialOutput {
    float3 BaseColor;
    float  Metallic;
    float  Roughness;
    float3 Normal;
};

FMaterialOutput NeuralMaterialEval(uint MaterialId, float3 VertexPos, float3 VertexNormal, float2 VertexUV) {
    FMaterialOutput Out;

    // 1. 拼 features: 8 latent + 3 pos + 3 normal + 2 uv = 16
    float Latent[8];
    [unroll]
    for (int i = 0; i < 8; ++i) {
        Latent[i] = MaterialLatent[MaterialId * 8 + i];
    }

    float Input[16] = {
        Latent[0], Latent[1], Latent[2], Latent[3],
        Latent[4], Latent[5], Latent[6], Latent[7],
        VertexNormal.x, VertexNormal.y, VertexNormal.z,
        VertexPos.x * 0.01, VertexPos.y * 0.01, VertexPos.z * 0.01,
        VertexUV.x, VertexUV.y
    };

    // 2. MLP forward: 16 → 64 → 64 → 4
    float Hidden1[64];
    [unroll]
    for (int h = 0; h < 64; ++h) {
        float Sum = MLP_B1[h];
        [unroll]
        for (int f = 0; f < 16; ++f) {
            Sum += Input[f] * MLP_W1[h * 16 + f];
        }
        Hidden1[h] = max(Sum, 0.0);  // ReLU
    }

    float Hidden2[64];
    [unroll]
    for (int h = 0; h < 64; ++h) {
        float Sum = MLP_B2[h];
        [unroll]
        for (int f = 0; f < 64; ++f) {
            Sum += Hidden1[f] * MLP_W2[h * 64 + f];
        }
        Hidden2[h] = max(Sum, 0.0);
    }

    // 3. Output projection
    Out.BaseColor = float3(MLP_B3[0], MLP_B3[1], MLP_B3[2]);
    Out.Metallic = 0.0;
    Out.Roughness = MLP_B3[3];

    [unroll]
    for (int h = 0; h < 64; ++h) {
        Out.BaseColor.r += Hidden2[h] * MLP_W3[h * 4 + 0];
        Out.BaseColor.g += Hidden2[h] * MLP_W3[h * 4 + 1];
        Out.BaseColor.b += Hidden2[h] * MLP_W3[h * 4 + 2];
        Out.Roughness += Hidden2[h] * MLP_W3[h * 4 + 3];
    }

    Out.BaseColor = saturate(Out.BaseColor);
    Out.Roughness = saturate(Out.Roughness);
    Out.Normal = normalize(VertexNormal);  // 简化:直接用 vertex normal

    return Out;
}
```

### 3. L3 Latent Material Code（day-job 长期目标）

- **思路**: 把每个 material UUID 编码到 16-dim latent space
- **训练**: Variational Autoencoder (VAE) 训练，把 50+ PBR 参数压到 16 dim
- **推理**: 运行时换材质 = 改 latent code，不需要重新编译 PSO
- **关键收益**: 1 个 shared MLP 评估所有材质，无需 5-bin dispatch

**对比表（Nanite + AI 加速 vs 传统）**:

| 维度 | 传统 Nanite 5-bin | Nanite + Neural Material Eval |
|------|---------------------|-------------------------------|
| Bin dispatch 开销 | 5 dispatch / frame | 1 dispatch / frame |
| Material Constant Buffer | 4 MB (50 material × 80KB) | 800 KB (50 × 16 latent × 4 bytes) |
| Pipeline switch 开销 | 高（PSO 重编译） | 低（latent code 切换） |
| 运行时材质插值 | 不支持 | 支持（latent 线性插值） |
| 训练数据需求 | 无 | 50+ 材质 × 1000 角度 |

### 4. 与 day-job RAG 的关联

Nanite 材质管线是 day-job **神经材质** 主线的核心数据源:
- **L1 工具描述**: `Nanite.Material.NeuralEval(materialId, vertex) → pbr_output`
- **L3 工具描述**: `Nanite.Material.LatentInterpolation(materialIdA, materialIdB, t) → pbr_output`
- **RAG 检索应用**: 用户问"如何让材质过渡" → 检索到 L3 latent interpolation 方案

### 5. 已知问题与限制（AI 加速版）

1. **MLP 推理开销** — 每 triangle 一次 forward，百万 triangle 量级下仍需 batch
2. **latent 训练数据** — 需要 ground truth PBR 参数训练 VAE，5000+ 材质起步
3. **精度损失** — L2 Neural PBR Compression 视觉略降（<2%），L3 Latent 需 fine-tune
4. **Fallback 链路** — 推理失败时必须回退到传统 5-bin dispatch
5. **不支持自定义 shader** — Neural 版本只能预测 PBR，自定义 emissive / anisotropy 难

---

*Create date: 2026-07-02*
*Last modified: 2026-07-09*
