---
tags: [shader/AI, shader/denoise, shader/temporal, shader/upsample, shader/neural-network, shader/UE]
aliases: [DLSS, FSR, XeSS, TAA-Upsample, Neural Super Resolution, NSR]
week: W7
cycle: E
---

# DLSS 风格神经超分 + 时域重建 (Neural Super Resolution)

| 字段       | 内容                                                                                                                                                                                |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **效果名称** | DLSS 风格神经超采样（Low-Res Render → 高分辨率输出 + 时域历史融合 + AI 边缘重建）                                                                                                                          |
| **类型**   | 后处理 / 神经推理 / 时间重建                                                                                                                                                                 |
| **平台**   | PC SM6 / Console（mobile 不支持，需 fallback FSR1 风格的双边上采样）                                                                                                                                  |
| **创建日期** | 2026-07-09                                                                                                                                                                          |
| **参考来源** | NVIDIA DLSS 3 SDK + Intel XeSS 2 + AMD FSR 3 + UE5 `PostProcessTemporalAA.usf` + SIGGRAPH 2023 "Neural Supersampling for Real-time Rendering" + GDC 2023 "DLSS 3: Ray Reconstruction"      |
|          |                                                                                                                                                                                   |

---

## 效果对比

| 传统超分 (Bilinear + TAA)         | DLSS 风格神经超分                                |
| -------------------------- | ------------------------------------------ |
| 双线性 / 双立方固定 kernel         | **神经网络学习 kernel**（input → 64 channels hidden → output）|
| TAA 历史权重固定 (clamp + variance) | **时序重建网络**：学习 "该相信历史多少"                   |
| 高频细节靠 jitter 累加（要 8+ 帧）    | **直接超采样**：1 帧即可输出高清                    |
| 鬼影 / 闪烁靠 heuristic 修复     | **AI 学 ghost detection**                  |
| 4× 像素开销（2560×1440 → 640×360） | **保持 4× 开销**，但视觉接近 native               |

---

## 核心代码

### 1. DLSS 整体 Pipeline 简化

```cpp
// 简化版 DLSS 类接口（对应 NVIDIA NGX / Intel XeSS / UE5 FSR3 wrapper）
class FNeuralSuperResolution {
public:
    enum class EMode { Off, Performance, Balanced, Quality, UltraQuality };
    EMode Mode = EMode::Balanced;

    // 输入纹理
    FRHITexture* InputColor;          // 低分辨率渲染结果（带 jitter）
    FRHITexture* InputDepth;          // depth buffer (motion vector 计算依赖)
    FRHITexture* InputMotionVectors;  // 屏幕空间运动矢量
    FRHITexture* HistoryColor;        // 上一帧的输出
    FRHITexture* HistoryDepth;        // 上一帧的 depth

    // 输出纹理
    FRHITexture* OutputColor;         // 高分辨率结果（native res）

    // 神经网络权重（GPU 端 upload,10-30 MB）
    void* NetworkWeights;
    size_t NetworkWeightsSize;

    // 主调度（每帧一次）
    void Dispatch(
        FRDGBuilder& GraphBuilder,
        FNeuralSuperResolutionInputs Inputs,
        FNeuralSuperResolutionOutputs& Outputs
    );

private:
    // 4 阶段 pipeline
    // Stage 1: Pre-process (motion vector reproject + depth hierarchy)
    // Stage 2: Feature extraction (16-tap gather + conv)
    // Stage 3: Temporal blend + neural net inference
    // Stage 4: Output to native resolution
};
```

### 2. HLSL 侧 — 时域重建 Stage（DLSS 核心）

```hlsl
// ============== Stage 1: Reproject ==============
// 把当前低分辨率像素 reproject 到上一帧,得到 history color
float4 ReprojectHistoryColor(
    float2 CurrentUV,
    Texture2D<float4> HistoryColor,
    Texture2D<float2> MotionVectors,
    out float OutDepth,
    out bool OutIsValid
) {
    // 1. 读 motion vector (低分辨率)
    float2 MV = MotionVectors.SampleLevel(LinearClampSampler, CurrentUV, 0);

    // 2. Reproject UV: 上一帧 UV = 当前 UV - MV
    float2 HistoryUV = CurrentUV - MV;

    // 3. 边界检查
    OutIsValid = all(HistoryUV > 0.0) && all(HistoryUV < 1.0);

    // 4. 读 history
    float4 History = HistoryColor.SampleLevel(LinearClampSampler, HistoryUV, 0);

    OutDepth = History.w;  // alpha channel 存 depth
    return History;
}

// ============== Stage 2: 5x5 Feature Gather ==============
// 网络输入不是单个像素,是 5x5 邻域 (25 个 sample × 多 channel)
struct FFeature {
    float3 Color;
    float  Luma;
    float2 MV;       // motion vector
    float  Depth;
    float  NormalDotHistoryNormal;  // 法线一致性
    float  LumaDiff; // 当前 vs history luma diff
};

void Gather5x5Features(
    float2 UV,
    Texture2D<float4> InputColor,
    Texture2D<float2> MotionVectors,
    Texture2D<float> DepthTex,
    out FFeature Features[25]
) {
    float2 PixelOffset = 1.0 / float2(textureSize(InputColor));
    [unroll]
    for (int y = -2; y <= 2; ++y) {
        [unroll]
        for (int x = -2; x <= 2; ++x) {
            float2 SampleUV = UV + float2(x, y) * PixelOffset;
            int Idx = (y + 2) * 5 + (x + 2);

            float4 Color = InputColor.SampleLevel(LinearClampSampler, SampleUV, 0);
            float2 MV = MotionVectors.SampleLevel(LinearClampSampler, SampleUV, 0);

            Features[Idx].Color = Color.rgb;
            Features[Idx].Luma = dot(Color.rgb, float3(0.299, 0.587, 0.114));
            Features[Idx].MV = MV;
            Features[Idx].Depth = ConvertFromDeviceZ(DepthTex.SampleLevel(PointSampler, SampleUV, 0));
        }
    }
}

// ============== Stage 3: 神经网络推理 (简化版) ==============
// 真实 DLSS 是 16-32 channel conv,这里只展示 1 hidden layer 简化版

// 网络权重（预训练,Game-side upload）
StructuredBuffer<float> Conv1_W;   // [25 * 4 input → 32 hidden]
StructuredBuffer<float> Conv1_B;   // [32]
StructuredBuffer<float> Conv2_W;   // [32 hidden → 3 output]
StructuredBuffer<float> Conv2_B;   // [3]

float3 NeuralNetworkInference(FFeature Features[25]) {
    // Flatten 25 features to 100 floats (color × 3 + luma + mv × 2 + depth)
    float Input[100];
    [unroll]
    for (int i = 0; i < 25; ++i) {
        Input[i * 4 + 0] = Features[i].Color.r;
        Input[i * 4 + 1] = Features[i].Color.g;
        Input[i * 4 + 2] = Features[i].Color.b;
        Input[i * 4 + 3] = Features[i].Luma;
    }

    // Layer 1: 100 → 32, ReLU
    float Hidden[32];
    [unroll]
    for (int h = 0; h < 32; ++h) {
        float Sum = Conv1_B[h];
        [unroll]
        for (int f = 0; f < 100; ++f) {
            Sum += Input[f] * Conv1_W[h * 100 + f];
        }
        Hidden[h] = max(Sum, 0.0);
    }

    // Layer 2: 32 → 3, Sigmoid
    float3 Out;
    Out.r = Conv2_B[0]; Out.g = Conv2_B[1]; Out.b = Conv2_B[2];
    [unroll]
    for (int h = 0; h < 32; ++h) {
        float W = Conv2_W[h];
        Out.r += Hidden[h] * W;
    }
    return saturate(Out);
}

// ============== Stage 4: 写输出 ==============
[numthreads(8, 8, 1)]
void NSRMainCS(
    uint3 DTid : SV_DispatchThreadID,
    Texture2D<float4> InputColor,
    Texture2D<float2> MotionVectors,
    Texture2D<float> DepthTex,
    Texture2D<float4> HistoryColor,
    RWTexture2D<float4> OutputColor
) {
    // 输出分辨率 = 输入 × 2 (DLSS Quality 模式)
    uint2 OutputPixel = DTid.xy;
    uint2 InputPixel = OutputPixel / 2;
    float2 UV = (float2(InputPixel) + 0.5) / float2(textureSize(InputColor));

    // Stage 1+2
    float HistoryDepth;
    bool bHistoryValid;
    float4 History = ReprojectHistoryColor(UV, HistoryColor, MotionVectors,
                                           HistoryDepth, bHistoryValid);

    FFeature Features[25];
    Gather5x5Features(UV, InputColor, MotionVectors, DepthTex, Features);

    // Stage 3: 神经网络推理
    float3 NetworkOutput = NeuralNetworkInference(Features);

    // Stage 4: 与历史混合 (这里简化: 50/50)
    float3 FinalColor = bHistoryValid
        ? lerp(History.rgb, NetworkOutput, 0.5)
        : NetworkOutput;

    OutputColor[OutputPixel] = float4(FinalColor, 1.0);
}
```

### 3. Jitter 序列（DLSS 必备）

```cpp
// Halton 2-3 sequence,8 sample 周期
// 比 RNGSequence 更稳定,TAA 业界标准
float2 HaltonSequence(int SampleIndex, int BaseX = 2, int BaseY = 3) {
    float X = 0.0, Y = 0.0;
    float InvBaseX = 1.0 / BaseX;
    float InvBaseY = 1.0 / BaseY;
    float FractorX = InvBaseX;
    float FractorY = InvBaseY;
    int Idx = SampleIndex;
    while (Idx > 0) {
        X += FractorX * (Idx % BaseX);
        Idx /= BaseX;
        FractorX *= InvBaseX;
    }
    Idx = SampleIndex;
    while (Idx > 0) {
        Y += FractorY * (Idx % BaseY);
        Idx /= BaseY;
        FractorY *= InvBaseY;
    }
    return float2(X, Y);
}

// 在 view projection matrix 里加 jitter offset
FMatrix JitterMatrix(FMatrix ViewProj, float2 Jitter) {
    // 投影到 clip space 后,把 NDC ±0.5/pixel 加 jitter
    FTranslationMatrix Trans(Jitter.x / ScreenWidth, Jitter.y / ScreenHeight, 0);
    return Trans * ViewProj;
}
```

---

## 8 个核心参数

| 参数 | 来源 | 含义 | 调参建议 |
|------|------|------|----------|
| `r.NGX.DLSS.Enable 0/1` | CVar | DLSS 全局开关 | 0 = 关闭，1 = 启用 |
| `r.NGX.DLSS.Quality 0-4` | CVar | Quality 模式 (Performance/Balanced/Quality/UltraQuality/UltraPerf) | 默认 Balanced |
| `r.NGX.DLSS.Sharpness 0-1` | CVar | 锐化强度 | 0.5 默认，过高会出 ringing |
| `r.NGX.DLSS.Mode 0/1/2` | CVar | 0=DLAA, 1=DLSS, 2=RayReconstruction | 高端 GPU 用 2 |
| `r.PostProcessTemporalAA.Algorithm 0/1/2` | CVar | 0=Off, 1=FSR2 TAA, 2=DLSS/NSR | fallback 时用 1 |
| `r.PostProcessTemporalAA.Jitter Sequence` | CVar | Jitter 序列类型 | 默认 Halton |
| `r.PostProcessTemporalAA.HistoryWeight` | CVar | TAA 历史权重上限 | 0.95 default |
| `r.PostProcessTemporalAA.DiffusionMax` | CVar | 颜色扩散半径（去噪） | 0.04 默认 |

---

## 5 档性能分级

| 分级 | 改动 | 性能影响 | 适用场景 |
|------|------|----------|----------|
| **极简** | 关闭 NSR，原生分辨率 + TAA | 0ms（省下超分开销） | 原生分辨率即满足时 |
| **标准** | Quality 模式 (1.5x scale, 2560×1440 → 1707×960) | ~0.6ms | PC 中端 |
| **高配** | Balanced 模式 (2x scale) | ~0.5ms | PC 高端 / 主机 |
| **极限** | Performance 模式 (3x scale) + Ray Reconstruction | ~1.0ms | 帧率优先场景 |
| **Debug** | 神经网络 inference 关闭,纯双边上采样 | 0ms 但画质差 | 性能对比 |

---

## 4 个变体版本

- **版本 A：DLSS (NVIDIA only)** — Tensor Core 加速,质量最高,需 RTX 卡
- **版本 B：XeSS (Intel only)** — XMX 加速 + DP4a fallback,Intel Arc / 部分 iGPU
- **版本 C：FSR 3 (AMD 全平台)** — 无 AI 加速,纯传统算法 + TAA,通用
- **版本 D：自研 NSR** — 简化版 1-hidden-layer 网络,任何 SM6 都能跑

---

## 6 个已知问题与限制

1. **不支持 mobile** — NSR 至少要 SM6 + structured buffer + 10MB 权重上传
2. **VRAM 占用** — DLSS 模型权重 10-30 MB,需预算
3. **冷启动卡顿** — 首帧上传权重,延迟 50-200ms
4. **透明物体鬼影** — 半透 / 粒子在 history blend 时易出 ghost,需要 mask 排除
5. **运动矢量精度** — Motion vector 必须用 high-precision,否则 jitter frame 会糊
6. **植被 / 头发闪烁** — 高频细节 (树冠 / 发丝) 在网络推理不稳,需要 temporal stabilization

---

## 7 步调参 SOP

1. **启用 DLSS** — `r.NGX.DLSS.Enable 1` + 选 quality mode
2. **调 jitter** — `r.PostProcessTemporalAA.Jitter Sequence Halton`
3. **开 motion vector** — Mesh 上勾 `Render In Main Pass` + `Generate Motion Vectors`
4. **Sharpness 调** — `r.NGX.DLSS.Sharpness 0.5`,过高会 ringing
5. **透明 / 粒子排除** — 加 `r.PostProcessTemporalAA.ExcludeTranslucency 1`
6. **r.NGX.DLSS.Debug 1** — 显示低分辨率 / 内部网络输出,排查 artifact
7. **stat DLSS** — 实时看 NSR overhead (GPU 时间 + 显存)

---

## 与 day-job RAG 的关联

DLSS 神经超分是 day-job **RAG + LLM tool-call 训练数据** 的最佳载体:

### 1. 工具描述模板（喂给 LLM）
```
NSR.Upscale(
    input_low_res: Texture2D,
    motion_vectors: Texture2D,
    history: Texture2D,
    quality_mode: Enum [Performance, Balanced, Quality]
) → Texture2D (native_res)
  - 网络推理开销: 0.5-1.0ms / frame
  - 输入 scale: Performance=3x, Balanced=2x, Quality=1.5x
  - 网络权重: 10-30 MB (vendor-specific)
```

### 2. SFT 数据生成路径
- 收集 5000 帧 UE5 渲染（native 2560×1440）
- 把 native frame 降采样到 1280×720 作为 input
- 让 NSR 模型 upscale 回 2560×1440
- 与 native 对比算 loss → SFT
- **耗时**: 1 个 RTX 4090 + 24h ≈ 5000 帧完成

### 3. RAG 检索时的应用
- 用户问 "为什么我开了 DLSS 还是糊"
- LLM 检索到本案例的"已知问题"段,答:"检查 motion vector 是否开启"
- LLM 检索到"调参 SOP"段,答:"把 Sharpness 调到 0.5,排除透明物体"

---

## 关联知识库

- [[W6/VSM-Virtual-Shadow-Map]]（阴影也是 temporal 重建可优化点）
- [[W8/神经降噪-RT-Denoiser]]（NSR 跟 RT Denoiser 共享 temporal + neural 思路）
- [[W9/神经辐射缓存-Neural-Radiance-Cache]]（NSR 解决空间分辨率, NRC 解决 GI 频率）
- [[../../../01-论文笔记库/2024-DLSS-3-Ray-Reconstruction|DLSS 3 Ray Reconstruction 论文]]
- [[../../../05-技术雷达/FSR3-vs-DLSS3|FSR3 vs DLSS3 对比]]

---

## 复用指南

把 DLSS 风格神经超分移植到自研引擎:

1. **降采样渲染** — ViewProj 加 Halton jitter,RT 渲染到 1/2 或 1/3 分辨率
2. **Motion Vector 输出** — Mesh Pass 末尾输出屏幕空间 motion vector
3. **History 缓冲** — 分配 native_res R16G16B16A16 纹理,跨帧 persist
4. **网络权重加载** — Vulkan/SM6 StructuredBuffer,首次 init 时一次性 upload
5. **5×5 Feature Gather** — 25 个 sample × 4 channel = 100 floats,网络输入
6. **神经网络推理** — 100 → 32 (ReLU) → 3 (Sigmoid),或 vendor-specific 模型
7. **历史混合** — Network output 与 History lerp,权重由网络隐式决定

---

*Create date: 2026-07-09*
*Last modified: 2026-07-09*