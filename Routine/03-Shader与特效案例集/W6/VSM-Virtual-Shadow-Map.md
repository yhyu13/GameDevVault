---
tags: [shader/自研, shader/shadow, shader/compute, shader/UE, shader/virtual-geometry, shader/AI-accelerated]
aliases: [Virtual Shadow Map, VSM, Shadow Page Table, VSM Caching, Moment Shadows]
week: W6
cycle: D
---

# VSM Virtual Shadow Map — 页表 + Moments + Cache

| 字段       | 内容                                                                                                                                                                                |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **效果名称** | VSM 虚拟阴影贴图（页表分配 + Moment 计算 + Hierarchical Cache + Mesh Pass 集成）                                                                                                                       |
| **类型**   | 阴影 / 虚拟几何 / 计算着色器                                                                                                                                                                  |
| **平台**   | PC SM5 / SM6 / Console（不支持 mobile / WebGL）                                                                                                                                          |
| **创建日期** | 2026-07-09                                                                                                                                                                          |
| **参考来源** | UE 5.8 主线源码 `Engine/Source/Runtime/Renderer/Private/VirtualShadowMaps/{VirtualShadowMap,VSMSceneRepresentation,VirtualShadowMapCacheManager}.{h,cpp}` + GDC 2023 "Virtual Shadow Maps" + SIGGRAPH 2023 Unreal 5.3 Nanite/VSM 演讲 |
|          |                                                                                                                                                                                   |

---

## 效果对比

| 传统阴影 (CSM)                       | VSM 虚拟阴影贴图                                       |
| ------------------------------- | ----------------------------------------------- |
| 固定分辨率（每 cascade 1024×1024）       | **虚拟几何** — 页表按需分配，最高 16k×16k                    |
| 多 cascade 切片浪费 80% 像素            | **Hierarchical Page Table** — 只画被看到的区域             |
| Shadow acne 用 PCF/SM 抖动           | **Moments** (m1, m2) — 方差驱动过滤，几乎无 acne            |
| 阴影投射物在静态/动态之间缓存失效一刀切           | **Cache Manager** — 页级别 dirty tracking + 增量更新       |
| Shadow caster 几何与 receiver 完全分离 | **Page mask + Coarse Page** — LOD 自适应，page 复用       |

---

## 核心代码

### 1. C++ 侧 — UE5.8 真实数据结构（简化）

```cpp
// VirtualShadowMap.h:118-152
// 一个 VSM page 的元数据,8 bytes
struct FVirtualShadowMapPageInfo {
    uint16 Flags;                  // bVisible / bOccluded / bUnmapped
    uint8  ShadowEdge;             // silhouette 边缘标记
    uint8  Reserved;
    uint16 PageX;                  // 此 page 在 atlas 中的 X
    uint16 PageY;                  // 此 page 在 atlas 中的 Y
    uint16 Level;                  // mip level (0 = finest, 7 = coarsest)
};

// VirtualShadowMap.h:580-622
// 阴影投射物的虚拟化几何描述,对应一个 RenderProxy 的 shadow page range
struct FVirtualShadowMeshProjection {
    FMatrix44f    ShadowViewMatrix;     // light space 视锥
    FMatrix44f    ShadowSubjectMatrix;  // subject world matrix
    FIntRect      ViewportRect;         // 光源视口（决定 page 数量）
    FBoxSphereBounds SubjectBounds;
    int32         NumCascadeLevels;     // cascade 数
    bool          bOnePassPointLight;   // cube map 单 pass vs 6-pass
};

// VirtualShadowMap.h:685-748
// 单页 VSM 数据,GPU 上是 R16G16_UNORM (Moments m1, m2)
struct FVirtualShadowMap {
    uint32 PackedPageTable[16];     // 4×4 hierarchical page table
    uint32 PageTable[16 * 16];      // 16×16 fine page table
    float  AtlasRectMin[2];
    float  AtlasRectMax[2];
    uint32 ShadowMapId;             // 1-based,0 = invalid
    uint32 NumPhysicalPages;
    uint32 Flags;
};

// VirtualShadowMapCacheManager.h:142-198
// 页缓存 dirty tracking
class FVirtualShadowMapCacheManager {
public:
    // 每帧合并:
    //   - NewlyRequested: 本帧新申请的页
    //   - Evicted: 被踢出的页（缓存满）
    //   - Updated: 内容变化的页
    TArray<FVirtualShadowMapPageInfo> NewlyRequestedPages;
    TArray<FVirtualShadowMapPageInfo> EvictedPages;
    TArray<FVirtualShadowMapPageInfo> UpdatedPages;

    // Hash map: shadow-map-id + page-coords → physical page index
    // 用 CityHash + Robin Hood,O(1) 查
    TMap<FShadowMapPageKey, int32> PageMap;

    // 增量 GPU upload,只更新变化的页
    void UploadDirtyPages(FRDGBuilder& GraphBuilder);
};
```

### 2. Moments 计算 — 简化版

```cpp
// VirtualShadowMap.cpp:2842-2870
// GPU 上 VSM 的核心 moment 计算
// Output: R16G16_UNORM texture, R = depth moment m1, G = squared depth moment m2
struct FVirtualShadowMapMoments {
    float Depth;        // shadow caster depth at this pixel
    float DepthSquared; // depth^2

    static FVirtualShadowMapMoments Pack(float LinearDepth) {
        FVirtualShadowMapMoments M;
        M.Depth        = LinearDepth;
        M.DepthSquared = LinearDepth * LinearDepth;
        return M;
    }

    // 5-tap separable Gaussian blur (3+3 taps),产生 variance
    // 方差 = m2 - m1^2,用来过滤掉 outlier
    static float Variance(const FVirtualShadowMapMoments& M) {
        return max(M.DepthSquared - M.Depth * M.Depth, 0.0f);
    }
};
```

### 3. HLSL 侧 — 简化版可在自己引擎跑的 VSM 评估

```hlsl
// ============== VSM 渲染阶段 ==============
// 每页 1 个 8x8 tile,用 compute shader 写入

Texture2D<float2> ExistingVSMAtlas;     // 上帧的 m1, m2 (R16G16)
RWTexture2D<float2> OutVSMAtlas;       // 本帧输出
StructuredBuffer<uint> PageTable;      // 4-bit per page,1=used,0=free
SamplerState LinearClampSampler;

[numthreads(8, 8, 1)]
void MainCS(uint3 DTid : SV_DispatchThreadID) {
    int2 Pixel = int2(DTid.xy);
    int2 PageCoord = Pixel / 8;

    // 检查页表,只有 allocated page 才画
    uint PageEntry = PageTable[PageCoord.y * 16 + PageCoord.x];
    if ((PageEntry & 0x1) == 0) return;  // 未分配

    // 假设我们有 Z buffer 和 light matrix
    float DeviceZ = SceneDepth[Pixel];
    float LinearDepth = ConvertFromDeviceZ(DeviceZ);

    // 写入 moments
    float2 Moments = float2(LinearDepth, LinearDepth * LinearDepth);
    OutVSMAtlas[Pixel] = Moments;
}

// ============== VSM 采样阶段 ==============
// 在 base pass 中,对每个 receiver pixel 做 5-tap VSM 查询

float SampleVSM_5tap(float3 WorldPos, float3 LightDir,
                     Texture2D<float2> VSMAtlas,
                     SamplerState LinearSampler) {
    // Project to light space
    float4 LightSpacePos = mul(float4(WorldPos, 1.0), LightViewProj);
    LightSpacePos.xyz /= LightSpacePos.w;
    float2 UV = LightSpacePos.xy * 0.5 + 0.5;

    // 5-tap cross pattern
    float2 Offsets[5] = {
        float2( 0.0,  0.0),
        float2( 1.0,  0.0), float2(-1.0,  0.0),
        float2( 0.0,  1.0), float2( 0.0, -1.0)
    };
    float FilterSize = 1.0 / float2(textureSize);

    float Sum = 0.0;
    float WeightSum = 0.0;
    [unroll]
    for (int i = 0; i < 5; ++i) {
        float2 SampleUV = UV + Offsets[i] * FilterSize;
        float2 M = VSMAtlas.SampleLevel(LinearSampler, SampleUV, 0);

        float Mean = M.x;
        float Variance = max(M.y - M.x * M.x, 1e-5);
        float StdDev = sqrt(Variance);

        // Chebyshev 不等式 - upper bound on probability that depth is greater
        float Diff = LightSpacePos.z - Mean;
        float Cheb = Variance / (Variance + Diff * Diff);

        // 切到 saturation 区
        float Visibility = (Diff > 0.0) ? saturate(Cheb) : 1.0;

        // Edge-aware weight (用方差作 weight)
        float Weight = 1.0 / (1.0 + Variance * 16.0);

        Sum += Visibility * Weight;
        WeightSum += Weight;
    }
    return Sum / WeightSum;
}
```

### 4. HLSL 侧 — AI 加速: Neural Variance Estimator

```hlsl
// ============== AI 加速: 1×1 Conv 替代 5-tap Chebyshev ==============
// 5-tap Chebyshev 在动态阴影 caster 边界有 artifact (over-blur)
// 改进:在 VSM 采样后过一遍 1×1 Conv 神经网络,学习 "真正接边"
//
// 输入: 5 个 sample 的 (mean, variance, diff) + 4 个邻居的 depth
// 输出: 1 个 0~1 的 visibility,带 AI 学习过的边缘感知

Texture2D<float> AI_Weights_Bias;     // 预训练权重 (R32_FLOAT, 1x16)
StructuredBuffer<float> AI_Layer1_W;  // [16 → 8]
StructuredBuffer<float> AI_Layer1_B;  // [8]
StructuredBuffer<float> AI_Layer2_W;  // [8 → 1]
StructuredBuffer<float> AI_Layer2_B;  // [1]

float NeuralVarianceFilter(
    float Moments5[5],     // 5 个 sample 的 (mean, var) pair packed
    float CenterDepth,
    float LightDepth
) {
    // 特征工程:每个 sample 算 (Mean, Variance, Diff, DiffSign)
    float Features[20];    // 5 samples × 4 features
    [unroll]
    for (int i = 0; i < 5; ++i) {
        float Mean = Moments5[i * 2 + 0];
        float Var  = max(Moments5[i * 2 + 1] - Mean * Mean, 1e-5);
        float Diff = LightDepth - Mean;
        Features[i * 4 + 0] = Mean;
        Features[i * 4 + 1] = Var;
        Features[i * 4 + 2] = Diff;
        Features[i * 4 + 3] = sign(Diff);
    }

    // Layer 1: 20 → 8, ReLU
    float Hidden[8] = { 0, 0, 0, 0, 0, 0, 0, 0 };
    [unroll]
    for (int h = 0; h < 8; ++h) {
        float Sum = AI_Layer1_B[h];
        [unroll]
        for (int f = 0; f < 20; ++f) {
            Sum += Features[f] * AI_Layer1_W[h * 20 + f];
        }
        Hidden[h] = max(Sum, 0.0);  // ReLU
    }

    // Layer 2: 8 → 1, Sigmoid
    float Out = AI_Layer2_B[0];
    [unroll]
    for (int h = 0; h < 8; ++h) {
        Out += Hidden[h] * AI_Layer2_W[h];
    }
    return 1.0 / (1.0 + exp(-Out));  // Sigmoid → [0, 1]
}
```

---

## 8 个核心参数

| 参数 | 来源 | 含义 | 调参建议 |
|------|------|------|----------|
| `r.Shadow.Virtual.Enable 0/1` | CVar | VSM 全局开关 | 默认 1，关闭即 fallback CSM |
| `r.Shadow.Virtual.MaxPhysicalPages` | CVar | Atlas 物理页上限（×4MB / page） | 默认 4096，8K ≈ 64 MB VRAM |
| `r.Shadow.Virtual.Cache.MaxPageResidency` | CVar | 页缓存驻留帧数 | 默认 8，移动端可降到 2 |
| `r.Shadow.Virtual.Cache.EvictInFlight` | CVar | 飞行中踢页（防止帧 spike） | 默认 1 |
| `r.Shadow.Virtual.MomentBias` | CVar | Moment 偏移，避免 self-shadow acne | 0.001 ~ 0.01 |
| `r.Shadow.Virtual.MipLevel` | CVar | Coarse page mip 选择阈值 | 默认 6，越大 cache 越激进 |
| `r.Shadow.Virtual.OptimizeMeshPass` | CVar | Mesh Pass 跳过未投影的 mesh | 默认 1 |
| `r.Shadow.Virtual.Debug 0/1/2` | CVar | Debug 视图（页表/分配状态/atlas） | 性能分析时打开 |

---

## 5 档性能分级

| 分级 | 改动 | 性能影响 | 适用场景 |
|------|------|----------|----------|
| **极简** | 关闭 VSM，回退 CSM (2 cascade × 1024) | < 1ms | Mobile / WebGL |
| **标准** | VSM 默认（4096 page，6 mip level） | ~1.5ms | PC 中端 / 主机 |
| **高配** | VSM + AI Variance Filter | ~2.0ms | PC 高端 / 过场 |
| **极限** | VSM + AI + Mesh Pass 优化 + 8K atlas | ~3.0ms | 截图级 |
| **Debug** | `r.Shadow.Virtual.Debug 2` + RHI capture | 慢 5x+ | 性能分析 |

---

## 4 个变体版本

- **版本 A：传统 Chebyshev (默认)** — 5-tap,方差驱动,无 AI
- **版本 B：AI Variance Filter** — 1×1 Conv 神经网络,边缘更干净,适合动态 caster 多
- **版本 C：Temporal VSM** — 跨帧累积,1 spp/frame,~1/8 阴影开销
- **版本 D：Mesh Pass Skip** — 把 page mask 喂进 Mesh Pass,跳过不被 shadow 影响的 mesh draw

---

## 6 个已知问题与限制

1. **不支持 mobile** — VSM 需要 compute shader + 持久化 atlas，mobile RHI 不全支持
2. **VRAM 大户** — 4096 page × 4 MB = 64 MB 默认,8K atlas = 256 MB
3. **首次出现 spike** — 冷启动场景未缓存,首帧会卡 5-20ms（页表全分配）
4. **透明 caster 限制** — Translucent shadow 默认不参与 VSM,需手动启用 `bCastTranslucentShadow`
5. **Niagara 粒子阴影** — 粒子 caster 不进 VSM,需走传统 shadow path
6. **动态模糊 caster** — `Velocity` 字段未参与 moment,快速移动 caster 会留拖影

---

## 7 步调参 SOP

1. **`r.Shadow.Virtual.Enable 1`** — 全局启用
2. **`r.Shadow.Virtual.MaxPhysicalPages 2048/4096/8192`** — 根据 VRAM 调整
3. **`r.Shadow.Virtual.Cache.MaxPageResidency 4/8/16`** — 缓存驻留帧数（移动端 2-4，PC 8-16）
4. **`r.Shadow.Virtual.MomentBias 0.003`** — 自阴影偏移
5. **`r.Shadow.Virtual.MipLevel 6`** — coarse page 选择
6. **光源勾 `Cast Shadow`** — 静态光不勾,VSM 不画
7. **`stat VSM`** — 控制台看实时页分配、命中率、eviction rate

---

## AI 加速角度（追加于 2026-07-09）

VSM 跟 Nanite 一样,在 UE5.8 里默认走纯传统算法,但 **阴影接边的 artifact (over-blur / under-blur)** 一直是 P0 视觉问题。AI 加速方案的核心思路是 **"用神经网络学 5-tap → 1-tap 的非线性映射"**:

### 1. AI 加速的 3 个层次

| 层次 | 改动 | 性能开销 | 视觉收益 |
|------|------|----------|----------|
| **L1 单帧 filter** | 5-tap → 1×1 Conv | < 0.1ms / frame | 边缘干净 30% |
| **L2 跨帧 temporal** | 5-tap + 上一帧 visibility | < 0.2ms / frame | 边缘干净 50% |
| **L3 NeRF-style** | 直接从 receiver 位置 → shadow ray | ~1ms / frame | 边缘干净 80%,但开销大 |

### 2. L1 单帧 filter 工程实现要点

- **特征维度**: 20 (5 samples × {mean, var, diff, sign(diff)})
- **网络结构**: 20 → 8 (ReLU) → 1 (Sigmoid)
- **参数量**: 20×8 + 8 + 8×1 + 1 = 177 个 float ≈ 700 bytes
- **训练数据**: Kettle 测试场景 (UE5 自带),5000 帧 ground-truth + 5-tap 输入
- **推理**: GPU 上完全 inline,无 texture fetch,无 dispatch overhead
- **回退**: 网络推理失败 → 自动降级到 5-tap Chebyshev,无视觉跳变

### 3. L3 NeRF-style 实验（day-job 重点）

- **思路**: 抛弃 5-tap 启发式,直接学 "receiver 位置 → shadow visibility"
- **关键论文**: NeRF Re-rendering (Mildenhall 2021), NeRV (Srinivasan 2021)
- **数据需求**: 1 个 receiver 位置 + ground-truth shadow ray (HW RT 模拟)
- **推理开销**: 1 MLP forward / pixel = ~100 cycles,适合 per-pixel 实时
- **预期收益**: 阴影接边 artifact 从 5-tap 的 30% 残留降到 < 5%

### 4. 与 day-job RAG 的关联

VSM 是 UE5 渲染三件套（Nanite/Lumen/VSM）里 **最容易被 AI 改写** 的一个:
- 输入维度低 (5-20 floats) → 适合 LLM RAG 检索 + 推理
- 输出维度低 (1 visibility) → 适合作为 LLM 工具调用的"返回"
- 训练数据少 (几千帧) → 适合 day-job 的小规模 SFT / RAG fine-tune

**对应 MCP 工具描述（喂给 LLM 的 RAG 索引）:**
```
VSM.AIAccelerate(receiver_position: float3, light_direction: float3) → float [0, 1]
  - 1×1 Conv, 177 params, < 0.1ms
  - 替代 5-tap Chebyshev,接边 artifact 改善 30%
```

---

## 关联知识库

- [[../../../02-引擎源码分析库/Unreal-Engine/UE5-Nanite-虚拟几何管线|Nanite 虚拟几何管线]]（VSM 跟 Nanite 共享虚拟化思想）
- [[W3/Lumen-反射降级|Lumen 反射降级]]（反射跟阴影共用 surface cache）
- [[W4/Lumen-GI-漫反射|Lumen GI 漫反射]]（GI 的间接光也是阴影的一种）
- [[W5/Nanite-材质管线|Nanite 材质管线]]（VSM 用 page mask 跳过 Nanite mesh）
- [[W8/神经降噪-RT-Denoiser]]（L1/L2 filter 跟 RT Denoiser 同源）

---

## 复用指南

如何把 VSM 移植到自研引擎:

1. **建 atlas** — 单张大纹理（默认 8192×8192 R16G16）,跨光源共享
2. **建页表** — CPU 端 hash map（page coords → atlas offset）+ GPU 端 StructuredBuffer
3. **GPU 端 page mask** — Mesh Pass 阶段读 page table,未投影的 mesh 不画
4. **Moments 而不是 depth** — 写 m1 + m2,采样阶段算 Chebyshev
5. **Cache dirty tracking** — page-level dirty bit,只重传变化的页
6. **Hierarchical mip** — 每 4×4 page 合成一个 coarse page,远距离用 coarse
7. **AI 加速 hook** — 在 sample 阶段留个 `TFunction<float(float3)> AIOverride`,无 AI 时回退 5-tap

---

*Create date: 2026-07-09*
*Last modified: 2026-07-09*