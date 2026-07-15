---
tags: [shader/AI, shader/denoise, shader/neural-network, shader/raytracing, shader/UE]
aliases: [RT Denoiser, NRD, OIDN, NRDS, Monte Carlo Denoising, Real-time Denoising]
case: C08
cycle: G
---

# 神经降噪器 — RT Denoiser (Real-time Monte Carlo Denoising)

| 字段       | 内容                                                                                                                                                                                |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **效果名称** | 神经 RT 降噪（Monte Carlo 噪声 → 收敛结果，用神经网络学 spatial+temporal 联合去噪）                                                                                                                            |
| **类型**   | 后处理 / 神经推理 / 多通道                                                                                                                                                                 |
| **平台**   | PC SM5/SM6 / Console（mobile 不支持，需 fallback SVGF 风格的简化版）                                                                                                                                |
| **创建日期** | 2026-07-09                                                                                                                                                                          |
| **参考来源** | NVIDIA NRD 4.0 + Intel Open Image Denoise (OIDN) 2 + UE5 `PostProcessDenoiser.usf` + SIGGRAPH 2017 "Interactive Reconstruction of Monte Carlo Image Sequences" + GDC 2022 "NRD: Real-time Ray Tracing Denoising" |
|          |                                                                                                                                                                                   |

---

## 效果对比

| 传统降噪 (Bilateral + TAA)     | 神经 RT Denoiser                            |
| ------------------------ | ----------------------------------------- |
| Bilateral filter (fixed kernel) | **神经网络学 kernel**（5×5 → conv → output）         |
| 颜色 / 深度分开处理              | **多通道联合**：color + depth + normal + motion    |
| 时域权重靠 luminance clamp      | **时域权重靠网络输出**（学 "该相信 history 多少"）           |
| 1-2 spp/frame 噪点明显        | **0.5-1 spp/frame** 即可达到 64+ spp 视觉          |
| 高光 / 反射区 artifact 难修      | **AI 学 specular highlight / glossy reflection** |

---

## 概念链（Concept Chain）— 从"为什么 RT 需要降噪"到"NRD 能省多少 spp"

读代码前先把动机链条理清楚。这一节给初学者一个"4 步推理链"，把后面所有技术细节挂在因果链上，不容易迷失。

### Step 1: 业务痛点 — RT 噪声是光追落地的最大障碍

光线追踪（Ray Tracing）的物理本质是 Monte Carlo 积分——每像素发射 N 条光线做平均。**N 越大噪声越小**，但**性能爆炸**：

| 采样率 (spp) | 噪声水平 | 性能（4K 输出） | 视觉 |
|------------|---------|----------------|------|
| 1 spp | 严重噪点 | 0.5 ms | 不可用 |
| 16 spp | 轻微噪点 | 8 ms | 勉强可接受 |
| 64 spp | 几乎无噪 | 32 ms | 好（不可实时） |
| 1024 spp | 收敛 | 500 ms | 离线（电影） |

3A 游戏想 60 fps 跑光追反射 / GI = **单帧预算 16 ms**，**留 1-2 spp 预算给 RT，剩余全部降噪**。

### Step 2: 传统局限 — 为什么启发式降噪解不掉

业内早期用启发式降噪（双边滤波 / TAA）：

| 方法 | 原理 | 视觉 |
|------|------|------|
| **双边滤波 (Bilateral)** | 像素值加权，权重 = exp(-距离²) × exp(-色差²) | 边缘模糊 |
| **TAA 抖动累加** | 8 帧 jitter 累加到 1 spp | 8 帧延迟 |
| **SVGF (方差引导)** | 5×5 spatial + variance + temporal | 高光 / 反射区难收敛 |
| **BMFR (Median Filter)** | 中值滤波 | 抹细节 |

**为什么启发式解不掉**：
- 启发式是**固定 kernel**，**学不到 RT 的统计偏差**
- 高光 / 镜面反射的 firefly 噪点需要**像素级非线性判断**
- 单 spp 输入信息有限，**TAA 累加要 8 帧延迟**

### Step 3: 神经网络解法 — NRD 4 阶段管线

NRD（Nvidia Real-time Denoiser）的核心创新是 **"4 阶段 spatial+temporal 联合降噪"**：

```
RT 1 spp 输入
   │
   ▼
Stage 1: Pre-pass (切线空间 + visibility 计算)
   │
   ▼
Stage 2: Spatial Filter (5×5 双边 + variance 引导)
   │
   ▼
Stage 3: Temporal Blend (reproject + clamp + 网络权重)
   │
   ▼
Stage 4: Neural Refinement (1×1 Conv 学 history 权重)
   │
   ▼
最终 64+ spp 视觉
```

**关键创新**：
- **多通道联合**：color + depth + normal + motion 同时进网络，**比单 color 通道信息丰富**
- **时域权重靠网络输出**：传统 TAA 用固定 luminance clamp，**NRD 用 1×1 Conv 学"该信 history 多少"**
- **firefly 检测**：网络专门学处理高光 / 镜面反射区的 outlier

### Step 4: 落地路径 — NRD / OIDN / SVGF 对照

| 方案 | 厂商 | 平台 | 速度 | 视觉 |
|------|------|------|------|------|
| **NRD Reblur** | NVIDIA | GPU (RTX 优先) | 快 | 优 |
| **NRD Sigma** | NVIDIA | GPU | 快（阴影专用） | 优 |
| **OIDN** | Intel | CPU | 慢 (50ms+) | 最好 |
| **SVGF** | 自研 | GPU | 中 | 好（无 AI） |

**对比 NRD Reblur vs 传统 SVGF**：

| 维度 | SVGF (纯算法) | NRD Reblur |
|------|---------------|------------|
| 单 spp 输入 | 16 帧收敛 | 1 帧接近 64 spp 视觉 |
| 高光 / 反射 | 难收敛 | AI 学过 |
| 神经推理开销 | 0 ms | +0.3 ms |
| 训练数据 | 0 | Path tracer 1024 spp GT |

**对 day-job 的核心价值**：本笔记是 day-job **神经降噪（DLSS 风格）** 主线最直接的产品——NRD 工具描述 + 调参 SOP 直接喂给 LLM（详见下方"与 day-job RAG 的关联"一节）。

---

## 核心代码

### 1. C++ 侧 — NRD 风格 Denoiser 接口

```cpp
// 简化版 NRD 接口（对应 NVIDIA NRD / Intel OIDN / UE5 RDG denoiser）
class FRayTracingDenoiser {
public:
    enum class EMethod {
        NRD_Reblur,        // 漫反射 / 镜面 / 透明 通用
        NRD_Sigma,         // 阴影专用
        OIDN_CPU,          // CPU fallback
        NeuralVariance,    // 自研轻量
        BilateralFallback  // 移动端 fallback
    };
    EMethod Method = EMethod::NRD_Reblur;

    // NRD 输入 (5 个 buffer)
    struct FDenoiserInputs {
        FRHITexture* Radiance;             // 当前帧 RT 结果（带噪）
        FRHITexture* NormalRoughness;      // G-buffer normal + roughness packed
        FRHITexture* Depth;                // G-buffer depth
        FRHITexture* MotionVectors;        // 屏幕空间 MV
        FRHITexture* HistoryLength;        // 每像素历史累计帧数
        FRHITexture* ViewZ;                // 视图空间 Z
    };

    // NRD 内部状态
    struct FDenoiserState {
        FRHITexture* PreviousRadiance;     // 上一帧输出
        FRHITexture* PreviousNormalRoughness;
        FRHITexture* PreviousViewZ;
        FRHITexture* Accumulation;         // 时域累加器
        uint32       FrameIndex;
    };

    FDenoiserState State;

    // 主调度（每帧 1 次,分 4 个 pass）
    void Dispatch(
        FRDGBuilder& GraphBuilder,
        FDenoiserInputs Inputs,
        FRHITexture*& OutCleanRadiance
    );
};
```

### 2. HLSL 侧 — 4 阶段 Denoise Pipeline

```hlsl
// ============== Stage 1: Pre-pass ==============
// 计算每个像素的"切线空间"和"可见性",给后面 kernel 用
[numthreads(8, 8, 1)]
void PrepassCS(
    uint3 DTid : SV_DispatchThreadID,
    Texture2D<float4> InputRadiance,
    Texture2D<float4> NormalRoughness,
    RWTexture2D<float4> OutTangentSpace,
    RWTexture2D<float>  OutVisibility
) {
    uint2 Pixel = DTid.xy;
    float4 NR = NormalRoughness[Pixel];
    float3 Normal = normalize(NR.xyz * 2.0 - 1.0);
    float Roughness = NR.w;

    // 切线空间 (normal + 2 perpendicular vectors)
    float3 Tangent = normalize(cross(Normal, float3(0.0, 1.0, 0.0)));
    float3 Bitangent = cross(Normal, Tangent);

    OutTangentSpace[Pixel] = float4(Tangent, Bitangent.x);
    OutVisibility[Pixel] = 1.0;  // 简化:全可见
}

// ============== Stage 2: Spatial Filter (单帧去噪) ==============
// 5x5 邻域内,bilateral filter 用 depth/normal 做边缘感知
float4 SpatialFilter5x5(
    float2 UV,
    Texture2D<float4> Radiance,
    Texture2D<float> Depth,
    Texture2D<float4> NormalRoughness,
    float CenterDepth,
    float3 CenterNormal
) {
    float2 PixelOffset = 1.0 / float2(textureSize(Radiance));
    float4 SumColor = 0.0;
    float SumWeight = 0.0;

    [unroll]
    for (int y = -2; y <= 2; ++y) {
        [unroll]
        for (int x = -2; x <= 2; ++x) {
            float2 SampleUV = UV + float2(x, y) * PixelOffset;
            float4 SampleColor = Radiance.SampleLevel(LinearClampSampler, SampleUV, 0);
            float SampleDepth = Depth.SampleLevel(LinearClampSampler, SampleUV, 0);
            float3 SampleNormal = NormalRoughness.SampleLevel(LinearClampSampler, SampleUV, 0).xyz * 2.0 - 1.0;

            // Depth weight (边缘检测)
            float DepthDiff = abs(SampleDepth - CenterDepth);
            float DepthWeight = exp(-DepthDiff * 100.0);

            // Normal weight
            float NormalDot = dot(SampleNormal, CenterNormal);
            float NormalWeight = pow(saturate(NormalDot), 32.0);

            // Luminance weight (防 firefly)
            float Luma = dot(SampleColor.rgb, float3(0.299, 0.587, 0.114));
            float LumaWeight = 1.0 / (1.0 + Luma * Luma * 0.01);

            float Weight = DepthWeight * NormalWeight * LumaWeight;

            SumColor += SampleColor * Weight;
            SumWeight += Weight;
        }
    }
    return SumColor / max(SumWeight, 1e-5);
}

// ============== Stage 3: Temporal Blend (时域稳定) ==============
// 把当前 spatial filter 结果与 history 混合,带 MV reproject
float4 TemporalBlend(
    float2 UV,
    Texture2D<float4> SpatialFiltered,
    Texture2D<float4> HistoryRadiance,
    Texture2D<float2> MotionVectors,
    float BlendWeight  // 网络输出的 0~1
) {
    // Reproject
    float2 MV = MotionVectors.SampleLevel(LinearClampSampler, UV, 0);
    float2 HistoryUV = UV - MV;
    float4 History = HistoryRadiance.SampleLevel(LinearClampSampler, HistoryUV, 0);

    // Clamp history 到当前帧 min/max,防鬼影
    float4 Current = SpatialFiltered[uint2(UV * textureSize(SpatialFiltered))];
    float4 Lo = min(Current, History);
    float4 Hi = max(Current, History);
    History = clamp(History, Lo, Hi);

    return lerp(Current, History, BlendWeight);
}

// ============== Stage 4: Neural Network Refinement ==============
// 关键创新:用一个小型 CNN 学 "history 权重 + 残差修复"
// 真实 NRD 用更复杂的网络,这里简化成 1 hidden layer

StructuredBuffer<float> Denoise_W1;  // [20 → 32]
StructuredBuffer<float> Denoise_B1;  // [32]
StructuredBuffer<float> Denoise_W2;  // [32 → 1]
StructuredBuffer<float> Denoise_B2;  // [1]

struct FNoiseFeatures {
    float4 CurrentColor;
    float4 HistoryColor;
    float  LumaDiff;
    float  NormalDiff;
    float  DepthDiff;
    float  MVLength;
    float  HistoryAge;
};

float NeuralBlendWeight(FNoiseFeatures F) {
    // Flatten 到 20 floats
    float Input[20] = {
        F.CurrentColor.r, F.CurrentColor.g, F.CurrentColor.b, F.CurrentColor.a,
        F.HistoryColor.r, F.HistoryColor.g, F.HistoryColor.b, F.HistoryColor.a,
        F.LumaDiff, F.NormalDiff, F.DepthDiff, F.MVLength, F.HistoryAge,
        F.CurrentColor.r - F.HistoryColor.r,
        F.CurrentColor.g - F.HistoryColor.g,
        F.CurrentColor.b - F.HistoryColor.b,
        F.CurrentColor.r + F.HistoryColor.r,
        F.CurrentColor.g + F.HistoryColor.g,
        F.CurrentColor.b + F.HistoryColor.b,
        F.HistoryColor.r * F.CurrentColor.r
    };

    // Hidden
    float Hidden[32];
    [unroll]
    for (int h = 0; h < 32; ++h) {
        float Sum = Denoise_B1[h];
        [unroll]
        for (int f = 0; f < 20; ++f) {
            Sum += Input[f] * Denoise_W1[h * 20 + f];
        }
        Hidden[h] = max(Sum, 0.0);
    }

    // Output: blend weight (sigmoid)
    float Out = Denoise_B2[0];
    [unroll]
    for (int h = 0; h < 32; ++h) {
        Out += Hidden[h] * Denoise_W2[h];
    }
    return 1.0 / (1.0 + exp(-Out));
}

// ============== Final Dispatch ==============
[numthreads(8, 8, 1)]
void MainCS(
    uint3 DTid : SV_DispatchThreadID,
    Texture2D<float4> InputRadiance,
    Texture2D<float4> NormalRoughness,
    Texture2D<float> Depth,
    Texture2D<float2> MotionVectors,
    Texture2D<float4> HistoryRadiance,
    RWTexture2D<float4> OutputClean
) {
    uint2 Pixel = DTid.xy;
    float2 UV = (float2(Pixel) + 0.5) / float2(textureSize(InputRadiance));

    float CenterDepth = Depth[Pixel];
    float3 CenterNormal = NormalRoughness[Pixel].xyz * 2.0 - 1.0;

    // Stage 2: Spatial
    float4 SpatialFiltered = SpatialFilter5x5(UV, InputRadiance, Depth, NormalRoughness,
                                              CenterDepth, CenterNormal);

    // Stage 3: Reproject + clamp
    float2 MV = MotionVectors[Pixel];
    float2 HistoryUV = UV - MV;
    float4 History = HistoryRadiance.SampleLevel(LinearClampSampler, HistoryUV, 0);
    float4 Lo = min(SpatialFiltered, History);
    float4 Hi = max(SpatialFiltered, History);
    History = clamp(History, Lo, Hi);

    // Stage 4: Neural blend weight
    FNoiseFeatures F;
    F.CurrentColor = SpatialFiltered;
    F.HistoryColor = History;
    F.LumaDiff = abs(dot(SpatialFiltered.rgb, float3(0.299, 0.587, 0.114))
                    - dot(History.rgb, float3(0.299, 0.587, 0.114)));
    F.NormalDiff = 1.0 - dot(CenterNormal, CenterNormal);  // 简化
    F.DepthDiff = abs(CenterDepth - CenterDepth);
    F.MVLength = length(MV);
    F.HistoryAge = 0.0;

    float BlendWeight = NeuralBlendWeight(F);

    // Final blend
    OutputClean[Pixel] = lerp(SpatialFiltered, History, BlendWeight);
}
```

### 3. 简化版（不依赖神经网络，纯算法版）

```hlsl
// 对应 SVGF (Spatiotemporal Variance Guided Filtering)
// 用 variance 而不是神经网络,在 mobile 上 fallback
float4 SVGFFallback(
    float2 UV,
    Texture2D<float4> Radiance,
    Texture2D<float> Depth,
    Texture2D<float4> NormalRoughness,
    Texture2D<float4> HistoryRadiance,
    Texture2D<float2> MotionVectors
) {
    float CenterDepth = Depth.SampleLevel(PointSampler, UV, 0);
    float3 CenterNormal = NormalRoughness.SampleLevel(PointSampler, UV, 0).xyz * 2.0 - 1.0;

    // 5x5 bilateral
    float4 SumColor = 0.0;
    float SumWeight = 0.0;
    float SumColorSq = 0.0;  // for variance

    [unroll]
    for (int y = -2; y <= 2; ++y) {
        [unroll]
        for (int x = -2; x <= 2; ++x) {
            float2 SampleUV = UV + float2(x, y) * 1.0/textureSize(Radiance);
            float4 Sample = Radiance.SampleLevel(LinearClampSampler, SampleUV, 0);
            float SampleDepth = Depth.SampleLevel(LinearClampSampler, SampleUV, 0);
            float3 SampleNormal = NormalRoughness.SampleLevel(LinearClampSampler, SampleUV, 0).xyz * 2.0 - 1.0;

            float DepthWeight = exp(-abs(SampleDepth - CenterDepth) * 64.0);
            float NormalWeight = pow(saturate(dot(SampleNormal, CenterNormal)), 16.0);
            float Weight = DepthWeight * NormalWeight;

            SumColor += Sample * Weight;
            SumColorSq += Sample * Sample * Weight;
            SumWeight += Weight;
        }
    }
    float4 Spatial = SumColor / max(SumWeight, 1e-5);

    // Variance → 决定 temporal weight
    float4 Variance = max(SumColorSq / max(SumWeight, 1e-5) - Spatial * Spatial, 1e-5);
    float VarianceMag = dot(Variance, float4(1,1,1,0.25));

    // 高方差 → 少信 history;低方差 → 多信 history
    float TemporalWeight = exp(-VarianceMag * 100.0);

    // Temporal blend
    float2 MV = MotionVectors.SampleLevel(PointSampler, UV, 0);
    float4 History = HistoryRadiance.SampleLevel(LinearClampSampler, UV - MV, 0);
    History = clamp(History, min(Spatial, History), max(Spatial, History));

    return lerp(Spatial, History, TemporalWeight);
}
```

---

## 代码逐行讲解（Code Walkthrough）— 4 段代码各在做什么

> 这一节专门给"读完代码还是不知道在干嘛"的初学者。每个代码块对应一段讲解：**意图 / 关键参数 / 边界条件**。

### 代码块 1: `FRayTracingDenoiser` (C++ 类接口)

**意图**：定义 NRD 风格降噪器的接口契约 + 5 个输入 buffer。

```cpp
class FRayTracingDenoiser {
public:
    enum class EMethod { NRD_Reblur, NRD_Sigma, OIDN_CPU, NeuralVariance, BilateralFallback };
    EMethod Method = EMethod::NRD_Reblur;

    struct FDenoiserInputs {
        FRHITexture* Radiance;             // 当前帧 RT 结果（带噪）
        FRHITexture* NormalRoughness;      // G-buffer normal + roughness packed
        FRHITexture* Depth;                // G-buffer depth
        FRHITexture* MotionVectors;        // 屏幕空间 MV
        FRHITexture* HistoryLength;        // 每像素历史累计帧数
        FRHITexture* ViewZ;                // 视图空间 Z
    };

    struct FDenoiserState {
        FRHITexture* PreviousRadiance;     // 上一帧输出
        FRHITexture* PreviousNormalRoughness;
        FRHITexture* PreviousViewZ;
        FRHITexture* Accumulation;         // 时域累加器
        uint32       FrameIndex;
    };

    FDenoiserState State;
};
```

**关键参数为什么**：
- **5 种 EMethod**：覆盖 NVIDIA NRD Reblur / Sigma + Intel OIDN CPU + 自研 + 移动端 fallback
- **5 个输入 buffer**：radiance / normal-roughness / depth / MV / history-length，**每个都有具体作用**
  - `Radiance`：1 spp 输入（带噪）
  - `NormalRoughness`：packed = `xyz = normal, w = roughness`，**节省一张纹理**
  - `Depth`：G-buffer depth，**边缘检测 + reproject 用**
  - `MotionVectors`：reproject history
  - `HistoryLength`：每像素已收敛帧数，**决定何时停止 temporal 累积**
- **`FDenoiserState`**：跨帧 persist 的 state，**`Accumulation` 是关键时域累加器**

**边界条件**：
- `Method = BilateralFallback` → 移动端 fallback，**完全无 AI**
- `HistoryLength > MaxFramesAccumulated` → 强制 reset history，**防止 ghosting 永远不收敛**

### 代码块 2: `SpatialFilter5x5` (HLSL Stage 2)

**意图**：5×5 邻域内的双边滤波，用 depth + normal + luminance 多通道加权。

```hlsl
float4 SpatialFilter5x5(float2 UV, Texture2D<float4> Radiance,
                        Texture2D<float> Depth, Texture2D<float4> NormalRoughness,
                        float CenterDepth, float3 CenterNormal)
{
    float2 PixelOffset = 1.0 / float2(textureSize(Radiance));
    float4 SumColor = 0.0;
    float SumWeight = 0.0;

    for (int y = -2; y <= 2; ++y) {
        for (int x = -2; x <= 2; ++x) {
            float2 SampleUV = UV + float2(x, y) * PixelOffset;
            float4 SampleColor = Radiance.SampleLevel(LinearClampSampler, SampleUV, 0);
            float SampleDepth = Depth.SampleLevel(LinearClampSampler, SampleUV, 0);
            float3 SampleNormal = NormalRoughness.SampleLevel(LinearClampSampler, SampleUV, 0).xyz * 2.0 - 1.0;

            // 3 个独立权重
            float DepthWeight = exp(-DepthDiff * 100.0);   // (1) 深度边缘
            float NormalWeight = pow(saturate(NormalDot), 32.0);  // (2) 法线边缘
            float LumaWeight = 1.0 / (1.0 + Luma * Luma * 0.01);  // (3) 防 firefly

            float Weight = DepthWeight * NormalWeight * LumaWeight;
            SumColor += SampleColor * Weight;
            SumWeight += Weight;
        }
    }
    return SumColor / max(SumWeight, 1e-5);
}
```

**关键参数为什么**：
- **`exp(-DepthDiff * 100.0)`**：深度边缘权重，**100 是 magic number，**调大 = 更锐利边缘，调小 = 更模糊
- **`pow(saturate(NormalDot), 32.0)`**：法线边缘权重，**32 是"法线差异灵敏度"，32 适合大多数场景**
- **`1.0 / (1.0 + Luma * Luma * 0.01)`**：luminance 倒数，**防止 firefly（高亮噪点主导权重）**
- **`max(SumWeight, 1e-5)`**：分母下限，**避免 SumWeight = 0 时除零**

**边界条件**：
- `DepthDiff` 不能是 NaN（**边缘像素 depth 是 0**）
- `SampleNormal * 2.0 - 1.0`：normal packed 是 [0, 1]，**解码回 [-1, 1]**
- `SampleUV` 越界：texture clamp mode 决定，**production 用 ClampToEdge**

### 代码块 3: `TemporalBlend` + `NeuralBlendWeight` (HLSL Stage 3+4)

**意图**：Stage 3 reproject + clamp history；Stage 4 用网络学 "history 权重"。

```hlsl
float4 TemporalBlend(float2 UV, Texture2D<float4> SpatialFiltered,
                     Texture2D<float4> HistoryRadiance, Texture2D<float2> MotionVectors,
                     float BlendWeight)
{
    float2 MV = MotionVectors.SampleLevel(LinearClampSampler, UV, 0);
    float2 HistoryUV = UV - MV;
    float4 History = HistoryRadiance.SampleLevel(LinearClampSampler, HistoryUV, 0);

    // Clamp 到当前帧 min/max 防鬼影
    float4 Current = SpatialFiltered[uint2(UV * textureSize(SpatialFiltered))];
    float4 Lo = min(Current, History);
    float4 Hi = max(Current, History);
    History = clamp(History, Lo, Hi);

    return lerp(Current, History, BlendWeight);  // (1) 网络输出的权重
}

float NeuralBlendWeight(FNoiseFeatures F) {
    float Input[20] = {
        F.CurrentColor.r, F.CurrentColor.g, F.CurrentColor.b, F.CurrentColor.a,
        F.HistoryColor.r, F.HistoryColor.g, F.HistoryColor.b, F.HistoryColor.a,
        F.LumaDiff, F.NormalDiff, F.DepthDiff, F.MVLength, F.HistoryAge,
        F.CurrentColor.r - F.HistoryColor.r,  // (2) diff features
        F.CurrentColor.g - F.HistoryColor.g,
        F.CurrentColor.b - F.HistoryColor.b,
        F.CurrentColor.r + F.HistoryColor.r,
        F.CurrentColor.g + F.HistoryColor.g,
        F.CurrentColor.b + F.HistoryColor.b,
        F.HistoryColor.r * F.CurrentColor.r
    };

    float Hidden[32];
    for (int h = 0; h < 32; ++h) {
        float Sum = Denoise_B1[h];
        for (int f = 0; f < 20; ++f) {
            Sum += Input[f] * Denoise_W1[h * 20 + f];
        }
        Hidden[h] = max(Sum, 0.0);
    }

    float Out = Denoise_B2[0];
    for (int h = 0; h < 32; ++h) {
        Out += Hidden[h] * Denoise_W2[h];
    }
    return 1.0 / (1.0 + exp(-Out));  // (3) Sigmoid → [0, 1]
}
```

**关键参数为什么**：
- **`clamp(History, Lo, Hi)`**：防鬼影关键，**history 颜色不能偏离当前帧太多**
- **20 个 input features**：8 当前帧 + 8 history + 5 diff/age/几何，**足够区分"该信 history 多少"**
- **2 层（20 → 32 → 1）**：网络极小，**推理开销 < 0.1 ms**
- **`1.0 / (1.0 + exp(-Out))`**：Sigmoid 强制输出 [0, 1]，**作为 blend weight**

**边界条件**：
- `MV = (0, 0)`：物体静止，**完全信 history（weight 接近 1）**
- `MV 非常大`：物体高速移动，**完全信当前帧（weight 接近 0）**
- `HistoryUV` 越界：production 用 ClampToEdge，**避免采样非法地址**

### 代码块 4: `SVGFFallback` (HLSL 移动端 fallback)

**意图**：无 AI 纯算法的降噪，对应 SVGF 思路。

```hlsl
float4 SVGFFallback(float2 UV, Texture2D<float4> Radiance, ...) {
    // 5x5 bilateral（与 SpatialFilter5x5 类似）
    float4 SumColor = 0.0;
    float SumWeight = 0.0;
    float SumColorSq = 0.0;  // (1) for variance

    for (int y = -2; y <= 2; ++y) {
        for (int x = -2; x <= 2; ++x) {
            // ... 双边滤波 ...
            SumColor += Sample * Weight;
            SumColorSq += Sample * Sample * Weight;  // (2) 平方和用于方差
            SumWeight += Weight;
        }
    }
    float4 Spatial = SumColor / max(SumWeight, 1e-5);

    // Variance → 决定 temporal weight
    float4 Variance = max(SumColorSq / max(SumWeight, 1e-5) - Spatial * Spatial, 1e-5);
    float VarianceMag = dot(Variance, float4(1,1,1,0.25));
    float TemporalWeight = exp(-VarianceMag * 100.0);

    // Temporal blend
    float4 History = clamp(History, min(Spatial, History), max(Spatial, History));
    return lerp(Spatial, History, TemporalWeight);
}
```

**关键参数为什么**：
- **`SumColorSq`**：平方和，**算方差用（Variance = E[X²] - E[X]²）**
- **`TemporalWeight = exp(-VarianceMag * 100)`**：方差大 → 权重小（少信 history），**方差小 → 权重大（多信 history）**
- **`VarianceMag`**：4 个 channel 的方差加权和，**w = (1,1,1,0.25) alpha 权重低（避免 alpha 影响方差）**

**边界条件**：
- `VarianceMag` 上限 / 下限要 saturate，**防止极端情况权重 = 0 / 1**
- 历史 buffer 必须 clamp 到当前帧 min/max，**否则 ghosting**

---

## 8 个核心参数

| 参数 | 来源 | 含义 | 调参建议 |
|------|------|------|----------|
| `r.Denoiser.Method 0/1/2/3` | CVar | 0=Off, 1=NRD_Reblur, 2=NRD_Sigma, 3=OIDN_CPU | 默认 1 |
| `r.Denoiser.MaxFramesAccumulated` | CVar | 时域累加上限 | 默认 30 |
| `r.Denoiser.SpatialIterations` | CVar | Spatial filter 迭代次数 | 默认 2 |
| `r.Denoiser.TemporalWeightScale` | CVar | 时域权重系数 | 默认 1.0 |
| `r.Denoiser.HistoryFix` | CVar | 防鬼影权重 | 默认 1.0 |
| `r.Denoiser.GlossyMaterial` | CVar | 镜面材质专用降噪 | 默认 1 |
| `r.Denoiser.DiffuseMaterial` | CVar | 漫反射材质专用降噪 | 默认 1 |
| `r.Denoiser.Debug 0/1/2` | CVar | Debug 视图 | 性能分析时打开 |

---

## 指标手册（Metric Guide）— 每个参数到底在测什么 / 为什么是这个值

> 8 个 CVar 是 RT Denoiser 调参的"入口"。初学者常见误区是"看到参数随便填一个"——这一节告诉你每个参数的"测什么 / 默认值为什么 / 阈值含义 / 怎么调"。

| 参数 | 测什么 | 默认值来源 | 阈值含义 | 怎么调 |
|------|-------|-----------|---------|--------|
| `r.Denoiser.Method` | 降噪方法 | 1（NRD_Reblur） | 0=Off, 1=NRD_Reblur, 2=NRD_Sigma, 3=OIDN_CPU | NVIDIA 优先 NRD，跨平台 NRD + OIDN fallback |
| `r.Denoiser.MaxFramesAccumulated` | 时域累加上限 | 30 帧 | < 10 闪烁，> 60 拖影 | 静态场景 60，动态场景 10 |
| `r.Denoiser.SpatialIterations` | Spatial filter 迭代次数 | 2 | < 1 噪点，> 4 模糊 | 性能不够降到 1，质量不够升到 3 |
| `r.Denoiser.TemporalWeightScale` | 时域权重系数 | 1.0 | < 0.5 闪烁，> 1.5 拖影 | 静态场景 1.2，动态 0.8 |
| `r.Denoiser.HistoryFix` | 防鬼影权重 | 1.0 | < 0.5 ghosting，> 1.5 闪烁 | 高速运动降到 0.7 |
| `r.Denoiser.GlossyMaterial` | 镜面材质降噪 | 1（开启） | 0 = 关，镜面噪点多 | 玻璃 / 金属场景必开 |
| `r.Denoiser.DiffuseMaterial` | 漫反射材质降噪 | 1（开启） | 0 = 关，漫反射也需降噪 | 漫反射场景必开 |
| `r.Denoiser.Debug` | Debug 视图 | 0 | 1 = variance heatmap，2 = temporal weight | 调参 / 性能分析时开 |

### 3 个常被误用的参数

#### `MaxFramesAccumulated` 不是越大越好

直觉："30 → 60 帧累加 = 降噪更彻底"。**对，但拖影会加剧**。

| MaxFramesAccumulated | 视觉 | 拖影 |
|---------------------|------|------|
| 5 | 闪烁 | 几乎无 |
| 15 | 平衡 | 轻微 |
| 30（默认） | 好 | 平衡 |
| 60 | 非常好 | 严重拖影（物体停止后阴影残留） |
| 120 | 极好 | 极端拖影 |

**正解**：保持 30，**静态场景（剧情过场）可以升到 60**。

#### `SpatialIterations` 多次迭代会过度模糊

直觉："1 → 3 次迭代 = 噪声更少"。**对，但边缘会模糊**。

| Iterations | 视觉 | 边缘 |
|-----------|------|------|
| 1 | 噪点 | 锐利 |
| 2（默认） | 平衡 | 略糊 |
| 3 | 好 | 模糊 |
| 4+ | 几乎无噪 | 严重模糊 |

**正解**：保持 2 次，**追求高质量用 temporal 多帧代替 spatial 多迭代**。

#### `HistoryFix` 不是越大越防鬼影

直觉："`HistoryFix 1.5` 比 1.0 防鬼影更强"。**对，但会闪烁**。

| HistoryFix | 视觉 |
|-----------|------|
| 0.5 | 鬼影严重（高速物体） |
| 1.0（默认） | 平衡 |
| 1.5 | 防鬼影但闪烁（物体边缘） |
| 2.0 | 严重闪烁 |

**正解**：保持 1.0，**高速物体场景降到 0.7-0.8**。

---

## 5 档性能分级

| 分级 | 改动 | 性能影响 | 适用场景 |
|------|------|----------|----------|
| **极简** | SVGF fallback (纯 bilateral) | < 0.5ms | Mobile / WebGL |
| **标准** | NRD Reblur 1 spp | ~1.0ms | PC 中端 |
| **高配** | NRD Reblur 1 spp + Sigma shadow | ~1.5ms | PC 高端 / 主机 |
| **极限** | NRD + 自研神经 refinement | ~2.5ms | 截图级 |
| **Debug** | OIDN CPU fallback | 50ms+（CPU） | 调试 |

---

## 4 个变体版本

- **版本 A：NRD Reblur (NVIDIA)** — 4 stage: pre + spatial + temporal + post
- **版本 B：NRD Sigma** — 阴影专用，1 stage temporal-only
- **版本 C：OIDN** — CPU 实现，质量最高但慢
- **版本 D：SVGF** — 纯算法 fallback，无 AI，mobile 可用

---

## 6 个已知问题与限制

1. **不支持 mobile（神经版）** — 神经网络推理需要 SM6+，mobile fallback 到 SVGF
2. **运动矢量依赖** — 必须开 `r.RayTracing 1` + Mesh 输出 motion vector
3. **首帧延迟** — 冷启动时 history 不可用，~10 帧才能收敛
4. **透明 / 粒子模糊** — Translucent / particle 不进 G-buffer，denoise 失效
5. **动态 emissive** — 高频闪烁的灯光（火焰、闪电）denoise 难收敛
6. **神经模型大小** — NRD 模型 ~30 MB，首次加载卡顿

---

## 常见误读（Common Misreading）— 5 个初学者陷阱

> 这一节列的是"读文档时容易形成、但实际是错的"理解。每条都是 day-job 真实踩过的坑。

### 误区 1："NRD = 万能降噪，任何 RT 输出都能降"

**你以为**：RT 1 spp 输出直接送 NRD，NRD 自动收敛到 64 spp 视觉。
**实际**：**NRD 需要正确的输入才能工作**——normal + depth + motion vector 缺一不可。

**为什么**：
- NRD 用 normal 做边缘检测（normal 错 = 边缘模糊）
- NRD 用 depth 做 reproject（depth 错 = ghosting）
- NRD 用 motion vector 做时域累积（MV 错 = 拖影 / 闪烁）

**正解**：
- Mesh 上**必须**勾 `Generate Motion Vectors`
- `r.RayTracing 1`（如果用 RT）
- 检查 G-buffer 输出（`r.RayTracing.Debug 1`）

### 误区 2："NRD 比 SVGF 快"

**你以为**：NRD 是 NVIDIA Tensor Core 加速，比 SVGF 快。
**实际**：**NRD 比 SVGF 慢 0.5 ms**（神经网络推理开销），但**视觉更好**。

| 方案 | 单帧开销 | 视觉 |
|------|---------|------|
| 无降噪 | 0 ms | 噪点爆炸 |
| SVGF (纯算法) | 0.5 ms | 好 |
| NRD Reblur (神经) | 1.0 ms | 优 |
| OIDN CPU | 50 ms+ | 最好 |

**正解**：
- 性能优先（mobile / 60fps VR）→ SVGF
- 视觉优先（PC 高端）→ NRD Reblur
- 离线 / 截图 → OIDN CPU

### 误区 3："TAA 也能降噪 RT 输出"

**你以为**：TAA 抖动累加 8 帧 = 8 spp 等效 = 不需要专用降噪。
**实际**：**TAA 的 8 帧累加 vs RT 8 spp 是两回事**。

**为什么不一样**：
- TAA：8 个 jitter sample × 1 spp = **相同场景多次采样**，但**采样方向相同**
- RT 8 spp：8 个 jitter sample × 1 spp = **相同场景不同方向采样**
- TAA jitter 是 sub-pixel 抖动，**不能减少 RT 的高光 / 反射区 firefly**

**正解**：
- TAA 处理 G-buffer / color 的 sub-pixel aliasing
- NRD / SVGF 处理 RT 1 spp 的高方差噪点
- 两者**叠加使用**，TAA 处理 primary，NRD 处理 RT secondary

### 误区 4："History clamping 是可选的"

**你以为**：`clamp(History, min(Spatial, History), max(Spatial, History))` 是可选优化。
**实际**：**History clamping 是防鬼影的"保命"机制，去掉必然出 ghosting**。

**为什么必须 clamp**：
- 高光闪烁的 emissive（火焰 / 闪电）会突然出现 / 消失
- history buffer 缓存了上一帧的高亮值
- 当前帧该位置无高亮 → history 残留 → ghosting

**正解**：
- 永远保持 clamp
- 调整 clamp 范围（`r.Denoiser.HistoryFix 1.0` 默认）

### 误区 5："OIDN CPU 总是比 NRD 好"

**你以为**：OIDN CPU 是 Intel 工业级，**总是比 NRD 好**。
**实际**：**OIDN 慢 50 倍**，仅适合离线 / 截图，不适合实时。

| 场景 | NRD (GPU) | OIDN (CPU) |
|------|-----------|------------|
| 实时 60 fps | ✅ | ❌（50ms 单帧） |
| 离线 / 截图 | ⚠ 稍差 | ✅ 最好 |
| 移动端 | ✅ SM6+ | ❌ CPU 不实用 |
| 服务器 farm | ❌ | ✅ 离线 rendering |

**正解**：
- 实时 → NRD
- 离线 → OIDN
- 用 NRD 跑实时，截图用 OIDN 后处理

---

## 7 步调参 SOP

1. **`r.Denoiser.Method 1`** — 启用 NRD_Reblur
2. **`r.Denoiser.MaxFramesAccumulated 30`** — 时域累加上限
3. **开 motion vector** — Mesh `Generate Motion Vectors` + `r.RayTracing 1`
4. **`r.Denoiser.GlossyMaterial 1`** — 镜面材质降噪（玻璃、金属）
5. **`r.Denoiser.DiffuseMaterial 1`** — 漫反射降噪
6. **HDR clamp** — `r.Denoiser.HistoryFix 0.95` 防 firefly
7. **`stat Denoiser`** — 控制台看 denoise overhead

---

## 与 day-job RAG 的关联

NRD 是 day-job **神经降噪（DLSS 风格）** 主线最直接的产品：

### 1. 工具描述模板
```
Denoiser.Filter(
    noisy_radiance: Texture2D,
    gbuffer_normal: Texture2D,
    gbuffer_depth: Texture2D,
    motion_vectors: Texture2D,
    method: Enum [NRD_Reblur, NRD_Sigma, OIDN, SVGF]
) → Texture2D (clean_radiance)
  - 单帧降噪开销: 1.0-1.5ms / 1080p
  - 输入 spp: 1-2 (RT 端预算)
  - 输出: 视觉等价 64+ spp
```

### 2. SFT 数据生成路径（与 W7 DLSS 类似）
- 收集 5000 帧 UE5 Path Tracer (1024 spp ground truth)
- 把 ground truth 降采样到 1 spp 作为 input
- NRD 模型 denoise 后算 loss
- **耗时**: 1 个 RTX 4090 + 24h ≈ 5000 帧完成

### 3. 跟 DLSS 协同
- DLSS 解决空间分辨率（4x → 1x）
- NRD 解决 GI/反射 频率（1 spp → 64 spp 视觉）
- 两者可叠加，帧率提升 4-8x

---

## 关联知识库

- [[C07/DLSS-神经超分-时域重建]]（DLSS 解决空间分辨率, NRD 解决 GI 频率）
- [[C06/VSM-Virtual-Shadow-Map]]（VSM 用 NRD Sigma 降噪阴影）
- [[C09/神经辐射缓存-Neural-Radiance-Cache]]（NRC 是 NRD 的 GI 版,降噪整个 GI）
- [[../../../01-论文笔记库/2023-NRD4-Multi-Layer-Performance|NRD 4 多层降噪论文]]
- [[../../../05-技术雷达/RT-Denoising-算法对照|Denoising 算法雷达]]

---

## 复用指南

把神经 RT 降噪移植到自研引擎:

1. **G-buffer 准备** — normal + depth + roughness + motion vector 都得画出来
2. **4 阶段调度** — pre-pass → spatial (5x5 bilateral) → temporal blend → neural refine
3. **History 缓冲** — 跨帧 persist R16G16B16A16 texture
4. **网络权重上传** — 30 MB StructuredBuffer,首次 init 一次性 upload
5. **Variance clamping** — History 颜色必须 clamp 到当前帧 min/max,防鬼影
6. **fallback 链路** — SM5 fallback 到 SVGF, 完全无 AI, 仍可工作
7. **RT 端 spp 预算** — 1 spp/frame 即可, 把节省的开销转给 RT 反射

---

*Create date: 2026-07-09*
*Last modified: 2026-07-09*