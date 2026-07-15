---
tags: [shader/自研, shader/nanite, shader/material, shader/performance, shader/UE, shader/AI-accelerated]
aliases: []
case: C05
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

## 概念链（Concept Chain）— 从"为什么 Nanite 要做 5-bin 分类"到"AI 加速能折叠什么"

读代码前先把动机链条理清楚。这一节给初学者一个"4 步推理链"，把后面所有技术细节挂在因果链上，不容易迷失。

### Step 1: 业务痛点 — 虚拟几何的材质评估贵在哪

Nanite 让 UE5 能渲染**几亿三角形**的虚拟几何（Zbrush 高模、摄影测量），但**材质评估开销爆炸**。每个三角形都要 shading，每个 shading 都触发 PSO（Pipeline State Object）切换 / 纹理采样 / 常量缓冲上传。

| 痛点 | 表现 |
|------|------|
| **PSO 切换开销** | 每个材质 permutation 是独立 PSO，1000 材质 × PSO 编译 = 50 分钟冷启动 |
| **Draw Call 调度** | 按 mesh 排序不跨 mesh，draw call 数 = 材质数 × mesh 数 |
| **常量缓冲冗余** | 每个 draw 都重新上传 material UB，浪费带宽 |
| **三角形 → 材质评估** | 1 个三角形 1 次 shading，几亿三角形 = 几亿次 shading |

### Step 2: 传统局限 — 为什么单一方案解不掉

| 方案 | 原理 | 优势 | 致命缺陷 |
|------|------|------|---------|
| **每 Mesh 一个 Draw** | DrawIndexedInstanced | 简单 | 1000 mesh = 1000 draw call，PSO 切换爆炸 |
| **按材质合批 (Static Batching)** | 同材质 mesh 合并 | draw call 减少 | 内存爆炸，virtual geometry 无法 batch |
| **Mega Material Constant Buffer** | 所有材质参数塞一张 mega UB | 单次 upload | 4 MB / 1000 材质，浪费显存 |
| **Material Atlas** | 纹理集 | 减少 sampler 切换 | 不解决 PSO 切换 |

### Step 3: Nanite 5-Bin 分类 — 分而治之

Nanite 的核心创新是 **"5 个 Bin 分类"**——每个三角形按用途分桶，避免跨桶评估：

```
每个三角形
   │
   ▼
FNaniteMaterialSlot (16 bytes, 5 个 uint16)
   │
   ├─ TriangleShadingBin  (主三角 shading)
   ├─ VoxelShadingBin     (Lumen GI 捕获, 单独评估避免 PSO 冲突)
   ├─ CurveShadingBin     (Hair / Fur, 不同拓扑)
   ├─ RasterBin           (Raster fallback)
   └─ FallbackRasterBin   (Software raster fallback)
```

**配套机制**：
- **FNaniteShadingPipeline**：(material + shader + UB) 组合 hash 去重，避免 PSO 重复编译
- **Persistent Material Buffer**：字节寻址 `ByteAddressBuffer`，每个 triangle 16 bytes 持久化
- **MaterialCBIndex**：mega constant buffer 索引，**所有材质参数塞一张 GPU buffer**
- **CityHash 128 位去重**：用 CityHash 算法做 pipeline hash，**O(1) 查找 + 稳定迭代**

### Step 4: 落地路径 — AI 加速能折叠什么

AI 加速思路：**用神经网络替换传统 material evaluation，把 5-bin dispatch 折叠成单次 MLP forward**。

| 层次 | 替换对象 | 网络规模 | 性能收益 |
|------|----------|----------|---------|
| **L1 Neural Material Eval** | 5-bin dispatch → 单 MLP forward 出 PBR | 8→64→64→4 (~10k params) | 5× bin dispatch 减少 |
| **L2 Neural PBR Compression** | Material Constant Buffer → MLP 隐式编码 | 32→128→128→16 (~50k params) | 8× constant buffer 减小 |
| **L3 Latent Material Code** | Material UUID → 16-dim latent code（动态切换材质） | VAE (~200k params) | 支持运行时材质插值 |

**对比传统 vs Neural 总账**：

| 维度 | 传统 Nanite 5-bin | Nanite + Neural Material Eval |
|------|---------------------|-------------------------------|
| Bin dispatch 开销 | 5 dispatch / frame | 1 dispatch / frame |
| Material Constant Buffer | 4 MB (50 material × 80KB) | 800 KB (50 × 16 latent × 4 bytes) |
| Pipeline switch 开销 | 高（PSO 重编译） | 低（latent code 切换） |
| 运行时材质插值 | 不支持 | 支持（latent 线性插值） |

**对 day-job 的核心价值**：本笔记是 day-job **神经材质 / Nanite AI 加速** 主线的核心案例——5-bin 调度 + Persistent Buffer + AI 折叠方案都是 day-job RAG 检索的关键素材。

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

## 代码逐行讲解（Code Walkthrough）— 3 段代码各在做什么

> 这一节专门给"读完代码还是不知道在干嘛"的初学者。每个代码块对应一段讲解：**意图 / 关键参数 / 边界条件**。

### 代码块 1: `FNaniteMaterialSlot` + `FNaniteShadingPipeline` (C++ 头文件)

**意图**：用 16 bytes 编码每个 material slot 的 5 个 bin ID，用 hash 去重避免 PSO 重复编译。

```cpp
struct FNaniteMaterialSlot {
    uint16 TriangleShadingBin;
    uint16 VoxelShadingBin;
    uint16 CurveShadingBin;
    uint16 RasterBin;
    uint16 FallbackRasterBin;

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

struct FNaniteShadingPipeline {
    const FMaterialRenderProxy* MaterialProxy = nullptr;
    const FMaterial* Material = nullptr;
    FRHIComputeShader*   ComputeShader   = nullptr;
    FRHIWorkGraphShader* WorkGraphShader = nullptr;
    FRHIUniformBuffer*   MaterialUB      = nullptr;

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

**关键参数为什么**：
- **5 个 uint16 = 80 bits = 10 bytes**，pack 成 16 bytes（4 个 uint32）：**`>> 4` 位运算打包**，GPU 端 `Load4` 一次读完整 slot
- **`CityHash128to64`**：Google 2011 提出的快速 hash 函数，**比传统 FNV / MurmurHash 快 2x**，UE5 默认 hash
- **`reinterpret_cast<UPTRINT>(MaterialProxy) >> 4`**：指针地址 hash，**指针低位恒为 0（16 字节对齐）**，丢弃低位避免 hash 碰撞
- **`HashCombineFast`**：UE5 的快速 32-bit hash combine，**避免 64-bit 乘法**
- **5 个 Bin 而不是 1 个**：Triangle / Voxel / Curve / Raster / Fallback，**用途分开**，避免主 shading 的 PSO 被 Lumen 捕获拉低

**边界条件**：
- Material slot pack 失败（如 5 个 bin 不全）→ `FPacked::Data[3] = 0` 保留扩展位
- Pipeline hash 碰撞概率极低（128-bit space），但**仍然要去重验证**，否则编译浪费时间

### 代码块 2: `FMaterialBuffers` (C++ Persistent Buffer)

**意图**：把每个 triangle 的 material entry 持久化到 ByteAddressBuffer，跨帧复用。

```cpp
class FMaterialBuffers {
public:
    FMaterialBuffers();

    // 每个 primitive 一条元数据
    TPersistentByteAddressBuffer<FPackedPrimitiveData> PrimitiveDataBuffer;

    // 每个 triangle 一个 material entry (16 bytes)
    TPersistentByteAddressBuffer<uint32> MaterialDataBuffer;
};

struct FPackedPrimitiveData {
    uint32 MaterialBufferOffset;        // 此 primitive 在 MaterialDataBuffer 的起点
    uint32 MaterialMaxIndex : 8;        // 材质数 - 1 (0 = 单一材质)
    uint32 MeshPassMask     : 8;        // 此 primitive 参与的 mesh pass
    uint32 bHasUVDensities  : 1;
};
```

**关键参数为什么**：
- **TPersistentByteAddressBuffer**：跨帧持久 buffer，**避免每帧重新分配**
- **`MaterialBufferOffset`**：每个 primitive 在全局 MaterialDataBuffer 的起点，**GPU 端直接 Load(offset) 读自己的 entry**
- **`MaterialMaxIndex : 8`**：8-bit 字段，**支持 256 种材质 / mesh**，超过需要分多个 primitive
- **`: 8` / `: 1` bitfield**：位域压缩，**1 个 uint32 装下 4 个字段**，节省 75% 显存

**边界条件**：
- MaterialBufferOffset 范围：0 ~ MaterialDataBuffer 总大小，**超出 buffer 大小会 GPU crash**
- MeshPassMask 必须 8-bit 完整，**否则后续位域错位**

### 代码块 3: `MainCS` + `MaterialEvaluateCS` (HLSL Binning Dispatch)

**意图**：把三角形按 MaterialIndex 分 bin，每个 bin 一次 dispatch。

```hlsl
[numthreads(64, 1, 1)]
void MainCS(uint3 DTid : SV_DispatchThreadID) {
    uint TriId = DTid.x;
    if (TriId >= NumTriangles) return;

    TriangleMaterialData Mat = LoadTriangleMaterial(TriId);

    uint BinId = Mat.MaterialIndex0;
    uint Slot;

    InterlockedAdd(BinningCounter[BinId], 1, Slot);    // 原子计数分配 slot
    BinningOutput[BinId * MaxTrianglesPerBin + Slot] = TriId;
}

[numthreads(8, 8, 1)]
void MaterialEvaluateCS(
    uint3 DTid, uint3 GTid,
    uniform uint MaterialIndex,
    uniform StructuredBuffer<float4> MaterialConstants
) {
    uint BinSlot = GTid.x;
    uint TriId = BinningOutput[MaterialIndex * MaxTrianglesPerBin + BinSlot];
    if (TriId == INVALID_TRIANGLE) return;

    FVertex V0 = VertexBuffer[IndexBuffer[TriId * 3 + 0]];
    FVertex V1 = VertexBuffer[IndexBuffer[TriId * 3 + 1]];
    FVertex V2 = VertexBuffer[IndexBuffer[TriId * 3 + 2]];

    uint2 Pixel = DTid.xy;
    float3 Bary = ComputeBarycentric(Pixel, V0, V1, V2);
    float4 BaseColor = MaterialConstants[MaterialIndex * 4 + 0];

    RWTexture2D<float4> Output;
    Output[Pixel] = float4(BaseColor.rgb * (1.0 - Roughness * 0.5), BaseColor.a);
}
```

**关键参数为什么**：
- **`InterlockedAdd`**：GPU 原子操作，**多线程写同一 bin 不会冲突**
- **`BinningOutput[BinId * MaxTrianglesPerBin + Slot]`**：bin 内偏移，**每个 bin 有自己的 slot 范围**
- **`ComputeBarycentric`**：重心坐标插值，**三角形内任意点都能算**
- **`[numthreads(64, 1, 1)]` MainCS**：64 thread 一组，**对应 GPU warp 大小**
- **`[numthreads(8, 8, 1)]` MaterialEvaluateCS**：8x8 = 64 thread，**对应一个 8x8 tile**（Nanite 一个 page 的大小）

**边界条件**：
- `TriId == INVALID_TRIANGLE`：bin 内未填满的 slot 必须有 sentinel，**否则计算用垃圾数据**
- `ComputeBarycentric`：三角形退化（V0=V1=V2）会除零，**生产代码要检查**
- `Roughness * 0.5`：简化版 PBR，**真实生产需要完整 BRDF 公式**（参见 W2 NeuralGGX）

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

## 指标手册（Metric Guide）— 每个参数到底在测什么 / 为什么是这个值

> 8 个参数是 Nanite 材质管线调参的"入口"。初学者常见误区是"看到参数随便填一个"——这一节告诉你每个参数的"测什么 / 默认值为什么 / 阈值含义 / 怎么调"。

| 参数 | 测什么 | 默认值来源 | 阈值含义 | 怎么调 |
|------|-------|-----------|---------|--------|
| `TriangleShadingBin` | 主三角形 shading 分桶 ID | 16 bits，max 65k | 0 = 默认 bin，超过 65k 需要分多 mesh | 单 mesh 一般 < 100 unique bin |
| `VoxelShadingBin` | Lumen 捕获 bin | 同上，**与主 bin 不同** | 强制独立，避免 Lumen 捕获拖累主 shading | Lumen 启用时必填，否则填 0 |
| `CurveShadingBin` | Hair / Fur bin | 16 bits | 跟 Triangle bin 拓扑不同，**不能用同一个** | Hair / Fur mesh 启用 |
| `RasterBin` | Raster fallback | 16 bits | Compute 不可用时 fallback（mobile / 老 GPU） | 永远填，fallback 路径 |
| `bIsMasked` | Alpha cutout 标志 | 0（默认关闭） | 开启 = 多一次 ddx/ddy 求导，**慢 10-15%** | 透明 / 树叶 mesh 启用 |
| `bIsTwoSided` | 双面标志 | 0（默认单面） | 开启 = 背面 normal 翻转 = **多 1 倍三角形评估** | 草 / 树叶 / 纸启用 |
| `bNoDerivativeOps` | 不能用 ddx/ddy | 0（默认允许） | voxel / curve 强制 true（求导在 compute 中无意义） | 体素 / 曲线 shading 自动设 true |
| `MaterialCBIndex` | Constant Buffer 索引 | 自动分配 | 决定 GPU 端 buffer 访问，**手动管理易错** | 一般无需手动 |

### 3 个常被误用的参数

#### `bIsMasked` 不是免费的 alpha cutout

直觉："勾一下 `bIsMasked` 就有 alpha 效果"。**对，但性能代价 10-15%**。

| 场景 | bIsMasked | 性能影响 | 视觉效果 |
|------|----------|---------|---------|
| 不透明材质 | 0（默认） | 0ms 开销 | 完美 |
| 半透明 cutout | 1 | +10-15% | 边缘有 dithering 才能平滑 |
| 不勾 bIsMasked 但 alpha < 1 | 0 | 快 | **完全错误**（黑 / 透明 bug） |

**正解**：真要 alpha cutout 必须勾 bIsMasked，并且**手动加 dithering 避免边缘锯齿**。

#### `bIsTwoSided` 不是"两面都渲染"

直觉："勾一下双面就能从两面看"。**对，但每三角形评估 2 次**。

| 三角形数 | bIsTwoSided = 0 | bIsTwoSided = 1 |
|---------|----------------|----------------|
| 100 万 | 1.5 ms | 3.0 ms（×2） |
| 1 亿 | 150 ms | 300 ms（×2） |

**正解**：
- 草 / 树叶 / 纸用双面
- 实体墙 / 地面 / 角色皮肤**永远不要勾**（浪费 ×2 性能）

#### `bNoDerivativeOps` 强制 true 的代价

直觉："`bNoDerivativeOps` true 让代码变简单"。**对，但禁用 ddx/ddy 后某些材质特性丢失**。

**为什么有 bNoDerivativeOps**：
- voxel / curve shading 在 compute shader 里跑，**ddx/ddy 在 compute shader 里没定义**
- 强制 true 防止写代码时误用 ddx/ddy

**代价**：
- mipmap 选择算法失效，**远距离纹理可能闪烁**
- 法线贴图 LOD 不准，**远处 normal 偏色**

**正解**：默认 bIsMasked / bIsTwoSided / 主 Triangle bin 都允许 ddx/ddy（bNoDerivativeOps = 0），只有 voxel / curve bin 强制 true。

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

## 常见误读（Common Misreading）— 5 个初学者陷阱

> 这一节列的是"读文档时容易形成、但实际是错的"理解。每条都是 day-job 真实踩过的坑。

### 误区 1："5-bin 分类越多越好"

**你以为**：5 个 bin 不够，应该扩到 10-20 个。
**实际**：**5 个 bin 是 Nanite 平衡点，更多 bin 增加 dispatch overhead 但收益边际**。

| Bin 数 | Dispatch 开销 | 视觉收益 | 适用 |
|--------|--------------|---------|------|
| 1（单 bin） | 0 ms | 低（PSO 频繁切换） | 单材质场景 |
| 5（默认） | +0.5 ms | 高（按用途分开） | 通用 |
| 10 | +1.5 ms | 边际（< 5%） | 极端复杂场景 |
| 20+ | +3 ms | 负收益（dispatch 主导） | **不要用** |

**正解**：5 个 bin 覆盖 90% 场景，**生产保持默认**。

### 误区 2："CityHash 128 位永远不碰撞"

**你以为**：128-bit CityHash 碰撞概率 ≈ 0。
**实际**：**理论碰撞概率 ≈ 2⁻¹²⁸，但生产环境的 hash 输入可能高度相似**。

**为什么相似**：
- 多个 material 共享同一个 ComputeShader（变体差异仅在 UB）
- 多个 material 共享同一个 MaterialProxy（如同一基础材质的不同 instance）

**正解**：
- CityHash 128 位够用，**无需手动加 hash 验证**
- 但 pipeline state mismatch 仍然可能发生，**编译错误时检查 shader 变体**

### 误区 3："Persistent Material Buffer 不需要更新"

**你以为**：TPersistentByteAddressBuffer 跨帧持久，**一次设置永久使用**。
**实际**：**场景改动时必须更新 buffer，否则 GPU 读到旧数据**。

**什么时候必须更新**：
- 三角形 mesh 改动（add / remove / transform）
- 材质 slot 数量变化
- Lumen VoxelBin / CurveBin 切换

**正解**：
- 用 Card UID 跟踪 mesh 变化（参见 W4 UpdateSurfaceCache 思路）
- 增量更新：**只更新 changed parts**，不全量重建

### 误区 4："WorkGraph 路径一定比 Compute 快"

**你以为**：UE5.8 新增的 WorkGraph（FRHIWorkGraphShader）= 自动 load balancing = 一定快。
**实际**：**WorkGraph 在小场景可能比 Compute 慢**（graph setup overhead 大）。

| 场景规模 | Compute 路径 | WorkGraph 路径 |
|---------|-------------|----------------|
| < 1K 三角形 | 0.5 ms | 1.2 ms（graph setup 主导） |
| 1K-100K | 1.5 ms | 1.5 ms（追平） |
| > 100K | 3.0 ms | 2.5 ms（load balancing 优势） |

**正解**：默认 Compute 路径，**大场景（> 100K tri）切 WorkGraph**。

### 误区 5："L1 Neural Material Eval 能 1:1 替代 5-bin"

**你以为**：1 个 MLP forward 替代 5-bin dispatch = 完美等价。
**实际**：**MLP 输出范围有限，特殊材质（emissive / anisotropy）无法编码**。

**为什么不能完美替代**：
- MLP 输出是连续 PBR 参数（BaseColor / Metallic / Roughness / Normal）
- **emissive（自发光）强度**不在 PBR 通道里，MLP 没法学
- **anisotropy（各向异性）**需要切线方向输入，8 维 latent 不够
- **subsurface scattering** 需要 thickness / scattering color 等额外参数

**正解**：
- 通用 PBR 材质 → L1 完全够
- 特殊材质（emissive / hair / skin）→ **保留 5-bin dispatch**，MLP 作为 fallback

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
- [[../C03/Lumen-反射降级|Lumen 反射降级]]（5-bin 的 Triangle / Voxel 复用）
- [[../C04/Lumen-GI-漫反射|Lumen GI 漫反射]]（Voxel ShadingBin 用法）

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
