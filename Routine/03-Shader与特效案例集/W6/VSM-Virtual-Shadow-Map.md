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

## 概念链（Concept Chain）— 从"为什么阴影要虚拟化"到"AI Variance Filter 能省什么"

读代码前先把动机链条理清楚。这一节给初学者一个"4 步推理链"，把后面所有技术细节挂在因果链上，不容易迷失。

### Step 1: 业务痛点 — 阴影是 3A 渲染的"细节天花板"

阴影和反射一样是"看着不起眼，掉了立刻露馅"的效果。CSM (Cascaded Shadow Map) 是 UE4 时代的标准方案，但有 3 大局限：

| 局限 | 表现 |
|------|------|
| **固定分辨率浪费** | 1024×1024 × 4 cascade = 16 MB，但远处 cascade 80% 像素没用到 |
| **Shadow acne** | PCF/SM 抖动去锯齿，但 self-shadow 边界模糊 |
| **静态 / 动态一刀切** | 静态光烘焙好，动态光完全重画，**没有"中间档"** |
| **Caster / Receiver 割裂** | 阴影 caster 几何不知道 receiver 视角，detail 浪费 |

Nanite 时代，几亿三角形虚拟几何，传统 CSM 完全失效——**阴影必须虚拟化**。

### Step 2: 传统局限 — 为什么 CSM 在 Nanite 时代崩溃

| 维度 | CSM (传统) | VSM (虚拟化) |
|------|-----------|--------------|
| 最高分辨率 | 2048×2048 | 16K×16K（按需分配） |
| 多 cascade 浪费 | 80% 像素浪费 | 0%（按需 page） |
| 阴影 acne | PCF 抖动 | Moments (方差) 几乎无 acne |
| Nanite 兼容 | ❌ 几亿三角形爆炸 | ✅ Page 表按需分配 |
| 移动端兼容 | ✅ SM5 | ❌ 需要 compute + 持久化 atlas |

### Step 3: VSM 虚拟化 — 4 个核心机制

VSM 的核心创新是 **"虚拟几何 + 页表 + Moments + Cache"**：

```
阴影 caster 几何
   │
   ▼
[1] 页表分配 (Page Table)
   │   4-bit per page, 1=used, 0=free
   │   按需分配,Hierarchical Page Table (4×4)
   ▼
[2] Moments 计算 (m1, m2)
   │   R = depth moment m1
   │   G = squared depth moment m2 (方差驱动过滤)
   ▼
[3] Cache Manager
   │   NewlyRequested / Evicted / Updated 三类
   │   Page-level dirty tracking + 增量更新
   ▼
[4] Mesh Pass Page Mask
   │   page mask 喂进 Mesh Pass, 跳过不投影的 mesh
   ▼
最终阴影
```

**关键机制**：
- **页表按需分配**：只在视野内分配 8×8 像素的 page，**远处自动粗化（coarse page）**
- **Moments (m1, m2)**：存深度 + 平方深度，**采样阶段算方差 → Chebyshev 不等式过滤**
- **Cache Manager**：页级别 dirty tracking，**只上传 changed pages**
- **Mesh Pass Page Mask**：**page mask 喂进 Mesh Pass 跳过不投影的 mesh draw**

### Step 4: 落地路径 — AI 加速能省什么

AI 加速思路：**用神经网络学 5-tap → 1-tap 的非线性映射**。

| 层次 | 改动 | 性能开销 | 视觉收益 |
|------|------|----------|---------|
| **L1 单帧 filter** | 5-tap → 1×1 Conv | < 0.1 ms / frame | 边缘干净 30% |
| **L2 跨帧 temporal** | 5-tap + 上一帧 visibility | < 0.2 ms / frame | 边缘干净 50% |
| **L3 NeRF-style** | 直接从 receiver 位置 → shadow ray | ~1 ms / frame | 边缘干净 80% |

**对比传统 5-tap vs L1 AI Filter**：

| 维度 | 传统 5-tap Chebyshev | L1 NeuralVarianceFilter |
|------|---------------------|------------------------|
| 单像素开销 | 5 texture fetch + 算方差 | 1 texture fetch + 1×1 Conv |
| 动态 caster 边界 | over-blur artifact | 边缘干净 |
| 训练数据 | 0 | Kettle 5000 帧 GT |
| 网络权重 | 0 | 700 bytes |

**对 day-job 的核心价值**：本笔记是 day-job **神经阴影 / Lumen 三件套** 主线的核心案例——页表 + Moments + AI filter 方案都是 day-job RAG 检索的关键素材。

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

## 代码逐行讲解（Code Walkthrough）— 4 段代码各在做什么

> 这一节专门给"读完代码还是不知道在干嘛"的初学者。每个代码块对应一段讲解：**意图 / 关键参数 / 边界条件**。

### 代码块 1: `FVirtualShadowMapPageInfo` + `FVirtualShadowMap` (C++ 数据结构)

**意图**：8 bytes 编码每个 page 的元数据，单张 atlas 存所有 shadow map。

```cpp
struct FVirtualShadowMapPageInfo {
    uint16 Flags;                  // bVisible / bOccluded / bUnmapped
    uint8  ShadowEdge;             // silhouette 边缘标记
    uint8  Reserved;
    uint16 PageX;                  // 此 page 在 atlas 中的 X
    uint16 PageY;                  // 此 page 在 atlas 中的 Y
    uint16 Level;                  // mip level (0 = finest, 7 = coarsest)
};

struct FVirtualShadowMap {
    uint32 PackedPageTable[16];     // 4×4 hierarchical page table
    uint32 PageTable[16 * 16];      // 16×16 fine page table
    float  AtlasRectMin[2];
    float  AtlasRectMax[2];
    uint32 ShadowMapId;
    uint32 NumPhysicalPages;
    uint32 Flags;
};
```

**关键参数为什么**：
- **`PackedPageTable[16]`**：4×4 hierarchical page table，**16 uint32 = 64 bytes**，GPU 端一次 Load4 读完整 4×4 区域
- **`PageTable[16 * 16]`**：16×16 fine page table，**256 entries = 1KB**，每 entry 指向物理 page
- **Hierarchical 2 级**：4×4 mip 0 找不到时降级到 16×16 mip 1，**远处自动粗化**
- **`ShadowEdge`**：silhouette 边缘标记，**AI Variance Filter 用这个识别 caster 边界**
- **`PageX / PageY`**：page 在 atlas 中的坐标，**不是世界坐标**，避免 float 精度问题

**边界条件**：
- `Flags & bUnmapped`：page 未分配，**GPU 端必须 early-out**
- `ShadowMapId == 0`：invalid shadow map，**所有 sample 必须先检查**
- `Level > 7`：超出 mip 范围，**coarsest 不能再粗化**

### 代码块 2: `FVirtualShadowMapCacheManager` (C++ 缓存管理)

**意图**：页级别 dirty tracking，**只上传变化的页**到 GPU。

```cpp
class FVirtualShadowMapCacheManager {
public:
    TArray<FVirtualShadowMapPageInfo> NewlyRequestedPages;
    TArray<FVirtualShadowMapPageInfo> EvictedPages;
    TArray<FVirtualShadowMapPageInfo> UpdatedPages;

    // Hash map: shadow-map-id + page-coords → physical page index
    TMap<FShadowMapPageKey, int32> PageMap;

    void UploadDirtyPages(FRDGBuilder& GraphBuilder);
};
```

**关键参数为什么**：
- **3 类 dirty pages**：Newly（新增）、Evicted（踢出）、Updated（修改），**分类后用不同 RDG pass 处理**
- **TMap<FShadowMapPageKey, int32>**：hash map 用 CityHash + Robin Hood，**O(1) 查找 + 稳定迭代**
- **`UploadDirtyPages`**：RDG pass 一次性 upload 所有 dirty pages，**避免多次 GPU sync**

**边界条件**：
- `NewlyRequested + Evicted + Updated` 必须按帧合并，**否则 page table 不一致**
- `PageMap` 大小超过物理 page 上限 → 触发 evict，**优先 evict 最旧 page**

### 代码块 3: `MainCS` (HLSL 渲染阶段)

**意图**：每页 8×8 tile，compute shader 写入 moments。

```hlsl
[numthreads(8, 8, 1)]
void MainCS(uint3 DTid : SV_DispatchThreadID) {
    int2 Pixel = int2(DTid.xy);
    int2 PageCoord = Pixel / 8;

    uint PageEntry = PageTable[PageCoord.y * 16 + PageCoord.x];
    if ((PageEntry & 0x1) == 0) return;  // 未分配

    float DeviceZ = SceneDepth[Pixel];
    float LinearDepth = ConvertFromDeviceZ(DeviceZ);

    float2 Moments = float2(LinearDepth, LinearDepth * LinearDepth);
    OutVSMAtlas[Pixel] = Moments;
}
```

**关键参数为什么**：
- **`PageCoord = Pixel / 8`**：每个 page 是 8×8 tile，**dispatch 用 8×8 thread 对应 1 个 page**
- **`PageEntry & 0x1`**：最低位是 allocation flag，**未分配 page 直接 early-out**（省 compute）
- **`Moments = (depth, depth²)`**：存深度 + 平方深度，**采样阶段算方差 m2 - m1²**
- **`LinearDepth`**：**线性深度不是 device Z**，Chebyshev 不等式需要线性距离

**边界条件**：
- `ConvertFromDeviceZ(DeviceZ)`：device Z ∈ [0, 1]，转换公式依赖 projection matrix
- `Moments` 是 float2 packing 到 R16G16，**远距离精度会丢**（超过 65535 距离截断）

### 代码块 4: `SampleVSM_5tap` + `NeuralVarianceFilter` (HLSL 采样阶段)

**意图**：5-tap cross pattern 采样 moments + Chebyshev 不等式过滤。

```hlsl
float SampleVSM_5tap(float3 WorldPos, float3 LightDir,
                     Texture2D<float2> VSMAtlas, SamplerState LinearSampler) {
    float4 LightSpacePos = mul(float4(WorldPos, 1.0), LightViewProj);
    LightSpacePos.xyz /= LightSpacePos.w;
    float2 UV = LightSpacePos.xy * 0.5 + 0.5;

    float2 Offsets[5] = {
        float2( 0.0,  0.0),
        float2( 1.0,  0.0), float2(-1.0,  0.0),
        float2( 0.0,  1.0), float2( 0.0, -1.0)
    };
    float FilterSize = 1.0 / float2(textureSize);

    float Sum = 0.0, WeightSum = 0.0;
    for (int i = 0; i < 5; ++i) {
        float2 SampleUV = UV + Offsets[i] * FilterSize;
        float2 M = VSMAtlas.SampleLevel(LinearSampler, SampleUV, 0);

        float Mean = M.x;
        float Variance = max(M.y - M.x * M.x, 1e-5);
        float StdDev = sqrt(Variance);

        float Diff = LightSpacePos.z - Mean;
        float Cheb = Variance / (Variance + Diff * Diff);

        float Visibility = (Diff > 0.0) ? saturate(Cheb) : 1.0;
        float Weight = 1.0 / (1.0 + Variance * 16.0);

        Sum += Visibility * Weight;
        WeightSum += Weight;
    }
    return Sum / WeightSum;
}
```

**关键参数为什么**：
- **5-tap cross pattern**：中心 + 4 邻居，**比 9-tap square 省 44% texture fetch**
- **`Variance = m2 - m1²`**：方差公式，**但需要 max 0 否则浮点误差出负数**
- **`Chebyshev 不等式`**：`P(X ≥ μ + t) ≤ σ² / (σ² + t²)`，**用方差估计 receiver 被遮挡概率**
- **`(Diff > 0.0) ? saturate(Cheb) : 1.0`**：**Diff ≤ 0 说明 receiver 在 caster 前面，必然可见**
- **`Weight = 1.0 / (1.0 + Variance * 16.0)`**：edge-aware weight，**方差大的区域权重低**（边缘）

**边界条件**：
- `LightSpacePos.w` 不能为 0（**避免除零**），裁剪空间在视锥外时丢弃
- `Variance < 1e-5` 强制下限，防止 sqrt 出 NaN
- `SampleUV` 越界：texture wrap mode 决定，**production 用 ClampToEdge**

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

## 指标手册（Metric Guide）— 每个参数到底在测什么 / 为什么是这个值

> 8 个 CVar 是 VSM 调参的"入口"。初学者常见误区是"看到参数随便填一个"——这一节告诉你每个参数的"测什么 / 默认值为什么 / 阈值含义 / 怎么调"。

| 参数 | 测什么 | 默认值来源 | 阈值含义 | 怎么调 |
|------|-------|-----------|---------|--------|
| `r.Shadow.Virtual.Enable` | VSM 全局开关 | 1（默认启用） | 0 = fallback CSM，1 = VSM | 移动端 / 老 GPU 设 0 |
| `r.Shadow.Virtual.MaxPhysicalPages` | Atlas 物理页上限 | 4096，**× 4 MB / page = 64 MB VRAM** | 2048 = 32 MB，8192 = 128 MB | VRAM 紧降 2048，宽裕升 8192 |
| `r.Shadow.Virtual.Cache.MaxPageResidency` | 页缓存驻留帧数 | 8 | < 4 闪烁（cache 太快踢），> 16 浪费 | 移动端 2-4，PC 8-16 |
| `r.Shadow.Virtual.Cache.EvictInFlight` | 飞行中踢页 | 1 | 1 = 防止帧 spike，0 = 等当前帧完成 | 永远保持 1 |
| `r.Shadow.Virtual.MomentBias` | Moment 偏移 | 0.003（UE5 经验值） | < 0.001 自阴影，> 0.01 阴影偏移（"彼得潘"） | 视觉调，0.001~0.01 区间 |
| `r.Shadow.Virtual.MipLevel` | Coarse page mip 选择 | 6 | 越大 cache 越激进（更多 coarse page） | 性能紧降 4，质量紧升 7 |
| `r.Shadow.Virtual.OptimizeMeshPass` | Mesh Pass 跳过未投影 mesh | 1（默认开启） | 0 = 全部 mesh 都画，1 = page mask 过滤 | 永远保持 1 |
| `r.Shadow.Virtual.Debug` | Debug 视图 | 0 | 1 = 页表，2 = atlas | 调参 / 性能分析时开 |

### 3 个常被误用的参数

#### `MaxPhysicalPages` 不是越大越好

直觉："4096 → 8192 物理页 = 阴影分辨率翻倍"。**对，但 VRAM 128 MB 是真**。

| MaxPhysicalPages | VRAM | 性能 | 适用 |
|----------------|------|------|------|
| 2048 | 32 MB | 快 | 移动端 / 显存紧 |
| 4096（默认） | 64 MB | 平衡 | PC 中端 |
| 8192 | 128 MB | 慢 30% | PC 高端 / 过场 |
| 16384 | 256 MB | 慢 80% | 截图级 |

**经验法则**：**VRAM 应控制在总显存的 10% 以内**，8GB VRAM → Max ≤ 8192。

#### `MaxPageResidency` 太低会闪烁

直觉："`MaxPageResidency 2` 节省 cache 内存"。**对，但阴影边界闪烁**。

**为什么**：
- page 在 cache 驻留 N 帧后被踢出
- 摄像机不动时，**被踢出的 page 下一帧又重新分配**，**重新分配时是新计算的 page**
- 计算结果与上次略有差异 → 视觉闪烁

| MaxPageResidency | 视觉 | 内存 |
|----------------|------|------|
| 2 | 闪烁明显 | 省 |
| 4 | 偶有闪烁 | 平衡 |
| 8（默认） | 稳定 | 平衡 |
| 16 | 非常稳定 | 费 |

**正解**：保持 ≥ 8，**移动端可以降到 4 但不能更低**。

#### `MomentBias` 太小会有自阴影，太大会"彼得潘"

直觉："MomentBias 越小越好（精确）"。**错**——会出 self-shadow acne。

**为什么**：
- `m1 = depth + bias` 加一个小偏移防止 caster 自阴影
- bias 太小 → caster 表面对自己的光产生阴影
- bias 太大 → 阴影**整体偏移**，出现"彼得潘"（角色和地面阴影脱节）

| MomentBias | 视觉 |
|-----------|------|
| 0.0001 | 自阴影 acne |
| 0.003（默认） | 平衡 |
| 0.01 | 阴影偏移（彼得潘） |
| 0.05+ | 阴影远离 caster |

**正解**：保持默认 0.003，**特殊情况（薄物体）调到 0.005-0.008**。

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

## 常见误读（Common Misreading）— 5 个初学者陷阱

> 这一节列的是"读文档时容易形成、但实际是错的"理解。每条都是 day-job 真实踩过的坑。

### 误区 1："VSM 一定比 CSM 快"

**你以为**：VSM 虚拟化按需分配，比 CSM 固定 cascade 快。
**实际**：**VSM 在动态场景可能比 CSM 慢**（page table churn 开销）。

| 场景 | CSM | VSM |
|------|-----|-----|
| 静态 / 慢速相机 | 0.5 ms | 1.0 ms（page table 频繁更新） |
| 中速相机 | 0.5 ms | 1.5 ms |
| 高速相机 / 大场景 | 1.5 ms | 2.5 ms |
| 静态场景 + Nanite | 💥 不支持 | 1.5 ms |

**正解**：
- **静态 / 慢速场景**：CSM 更简单稳定
- **Nanite 几亿三角形**：必须 VSM
- **高速相机**：CSM + cascaded shadow 也够用

### 误区 2："Moments (m1, m2) 等于 ESM"

**你以为**：Moments 阴影 = Exponential Shadow Map（ESM）。
**实际**：**Moments 用方差驱动过滤（Chebyshev），ESM 用指数衰减**，两者数学完全不同。

| 维度 | ESM | VSM Moments |
|------|-----|-------------|
| 存储 | R32F (e^(c × depth)) | R16G16 (depth, depth²) |
| 过滤 | exp 函数 | Chebyshev 不等式 |
| Light bleeding | 严重（指数衰减带权重扩散） | 几乎无 |
| 数值稳定性 | exp 容易溢出 | 平方深度稳定 |

**正解**：Moments 比 ESM 更稳定，**现代 UE5 / CryEngine 都用 Moments**。

### 误区 3："AI Variance Filter 训练一次通用"

**你以为**：用 Kettle 5000 帧训练的网络可以应用到所有场景。
**实际**：**训练集覆盖不到的场景会有 5-10% 视觉 regression**。

**为什么**：
- 训练数据来自 Kettle 标准场景
- 生产环境的 caster 拓扑 / 光照 / 阴影长度不同
- 神经网络在分布外瞎猜

**正解**：
- **跨场景通用网络**：用 5-10 个不同场景混合训练，**收集成本高但泛化好**
- **per-scene 网络**：每个项目自己训练，**质量好但收集成本爆炸**
- **生产推荐**：跨场景通用网络 + 严重 regression 时切回 5-tap Chebyshev

### 误区 4："Chebyshev 不等式 = 完美阴影"

**你以为**：Chebyshev 不等式 = 数学上正确，**所有阴影都该用它**。
**实际**：**Chebyshev 在 light bleeding（光从缝隙漏出）时表现差**。

**为什么**：
- Chebyshev 给的是 **receiver 被遮挡概率的上界**
- light bleeding = 阴影里有"光斑"，数学上是 receiver 实际没遮挡但 Chebyshev 估计为有遮挡
- VSM 用 **MomentBias 偏移 + 5-tap 邻域平滑**缓解，但根因是数学模型近似

**正解**：
- 简单阴影场景，Chebyshev 完全够
- 复杂阴影（薄墙 / 栅栏 / 头发）需要更复杂的 variance reduction

### 误区 5："Page mask 让所有 mesh draw 都跳过"

**你以为**：`OptimizeMeshPass 1` 让不投影的 mesh 完全不画。
**实际**：**Mesh Pass 跳过的是 shadow draw（depth-only pass），G-buffer pass 还是要画**。

**为什么**：
- Mesh Pass Page Mask 只影响**阴影 caster 的 depth-only pass**
- 主 G-buffer pass（color + normal + depth）必须画所有 mesh，**否则 receiver 看不到 caster**

**正解**：
- Page mask 节省的是 **shadow pass 的 vertex shader**（几亿虚拟几何的 HSR / binning）
- G-buffer pass 仍然全画

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