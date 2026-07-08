---
tags: [shader/AI, shader/denoise, shader/neural-network, shader/raytracing, shader/UE]
aliases: [RT Denoiser, NRD, OIDN, NRDS, Monte Carlo Denoising, Real-time Denoising]
week: W8
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

- [[W7/DLSS-神经超分-时域重建]]（DLSS 解决空间分辨率, NRD 解决 GI 频率）
- [[W6/VSM-Virtual-Shadow-Map]]（VSM 用 NRD Sigma 降噪阴影）
- [[W9/神经辐射缓存-Neural-Radiance-Cache]]（NRC 是 NRD 的 GI 版,降噪整个 GI）
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