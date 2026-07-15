---
tags: [shader/AI, shader/denoise, shader/temporal, shader/upsample, shader/neural-network, shader/UE]
aliases: [DLSS, FSR, XeSS, TAA-Upsample, Neural Super Resolution, NSR]
case: C07
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

## 概念链（Concept Chain）— 从"为什么需要神经超分"到"DLSS 能省多少"

读代码前先把动机链条理清楚。这一节给初学者一个"4 步推理链"，把后面所有技术细节挂在因果链上，不容易迷失。

### Step 1: 业务痛点 — 4K 渲染太贵，1080p 又糊

3A 项目渲染 4K (3840×2160) 帧率 60fps 需要单 GPU 跑满 16K draw call + 复杂 shading。玩家想要"4K + 60fps + 光追"，但**单卡预算有限**：

| 方案 | 像素开销 | 视觉质量 | 适用 |
|------|---------|---------|------|
| **原生 4K 渲染** | 8.3M pixels | 完美 | 4090 单卡跑不动 |
| **1080p 上采样到 4K (双线性)** | 2.1M pixels | 糊（细节全失） | 完全不可接受 |
| **TAA 抖动累加** | 2.1M pixels | 接近 4K（8 帧累加） | 玩家感受滞后 |
| **DLSS / FSR3** | 2.1M pixels | 接近 4K（1 帧） | 完美方案 |

**根本痛点**：降采样渲染省像素，**但上采样回来视觉必须接近原生**——传统双线性 / 双立方做不到。

### Step 2: 传统局限 — 为什么传统上采样解不掉

| 方法 | 原理 | 视觉 |
|------|------|------|
| **双线性** | 4 邻域线性插值 | 糊、边缘锯齿 |
| **双立方 (bicubic)** | 16 邻域三次插值 | 比双线性好，仍糊 |
| **TAA 抖动累加** | 8 帧 jitter 累加到 4K | 接近原生，但延迟 8 帧 |
| **TAA + Lanczos** | 加权 Lanczos 核 | 仍糊，细节丢失 |

**为什么传统解不掉**：上采样本质是个**病态问题**——4K 像素有 4 倍信息量，1080p 输入没那么多信息。任何固定 kernel 插值都会丢失细节。

### Step 3: 神经网络解法 — 学"超分 kernel"

核心 insight：**把超分问题当成 regression 问题**——用神经网络学 (低分辨率像素 + 邻域 + history) → 高分辨率像素。

**网络架构选型**：CNN（Convolutional Neural Network）

```
输入（5×5 邻域 × 4 channel = 100 features）
   │
   ▼
Conv 1×1 (100 → 32) + ReLU         (feature extraction)
   │
   ▼
Conv 1×1 (32 → 16) + ReLU          (compression)
   │
   ▼
Conv 1×1 (16 → 3) + Sigmoid        (output RGB)
```

**为什么是 CNN 不是别的**：
- CNN 用 **卷积核共享权重**，5×5 邻域每个像素用同一个 kernel
- 卷积层数可以很深，**学多尺度特征**
- NVIDIA Tensor Core 加速（DLSS 用），**RTX 卡上推理 < 1 ms**
- 1×1 Conv 极致轻量，**网络权重 < 1 MB**

### Step 4: 落地路径 — DLSS / FSR3 / XeSS 生态

| 方案 | 厂商 | 加速硬件 | 视觉质量 | 平台 |
|------|------|---------|---------|------|
| **DLSS** | NVIDIA | Tensor Core | 最好（厂商调优） | RTX only |
| **DLSS Ray Reconstruction** | NVIDIA | Tensor Core | 最好（+RR 处理 ray noise） | RTX only |
| **XeSS** | Intel | XMX / DP4a | 好 | Arc / 部分 iGPU |
| **FSR3** | AMD | 无（纯算法） | 中（无 AI） | 全平台 |

**对比传统 TAA 的总账**：

| 维度 | TAA 8 帧累加 | DLSS 1 帧 |
|------|-------------|-----------|
| 输入分辨率 | 1080p | 1080p |
| 输出分辨率 | 4K | 4K |
| 视觉 | 接近原生（有拖影） | 接近原生（无拖影） |
| 延迟 | 8 帧 | 1 帧 |
| GPU 开销 | 1.5 ms | 0.5 ms（DLSS 更快） |
| 网络权重 | 0 | 10-30 MB（vendor specific） |

**对 day-job 的核心价值**：本笔记是 day-job **RAG + LLM tool-call 训练数据** 的核心载体——DLSS 工具描述 + 调参 SOP 直接喂给 LLM（详见下方"与 day-job RAG 的关联"一节）。

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

## 代码逐行讲解（Code Walkthrough）— 4 段代码各在做什么

> 这一节专门给"读完代码还是不知道在干嘛"的初学者。每个代码块对应一段讲解：**意图 / 关键参数 / 边界条件**。

### 代码块 1: `FNeuralSuperResolution` (C++ 类接口)

**意图**：定义 DLSS 风格神经超分的"输入契约 + 4 阶段 pipeline"。

```cpp
class FNeuralSuperResolution {
public:
    enum class EMode { Off, Performance, Balanced, Quality, UltraQuality };
    EMode Mode = EMode::Balanced;

    FRHITexture* InputColor;
    FRHITexture* InputDepth;
    FRHITexture* InputMotionVectors;
    FRHITexture* HistoryColor;
    FRHITexture* HistoryDepth;

    FRHITexture* OutputColor;

    void* NetworkWeights;
    size_t NetworkWeightsSize;

    void Dispatch(FRDGBuilder& GraphBuilder, FNeuralSuperResolutionInputs Inputs, FNeuralSuperResolutionOutputs& Outputs);

private:
    // 4 阶段 pipeline
    // Stage 1: Pre-process (motion vector reproject + depth hierarchy)
    // Stage 2: Feature extraction (16-tap gather + conv)
    // Stage 3: Temporal blend + neural net inference
    // Stage 4: Output to native resolution
};
```

**关键参数为什么**：
- **`EMode`**：5 个 mode 对应 4 个 scale factor（Performance=3x, Balanced=2x, Quality=1.5x, UltraQuality=1.3x）+ Off
- **5 个输入纹理**：color / depth / motion / history color / history depth，**每个都有具体作用**
  - `InputColor`：低分辨率渲染结果（带 jitter）
  - `InputDepth`：motion vector 计算依赖 depth
  - `InputMotionVectors`：屏幕空间运动矢量
  - `HistoryColor` / `HistoryDepth`：上一帧输出，**时域融合用**
- **`NetworkWeightsSize = 10-30 MB`**：vendor-specific，**首次加载一次性 upload**

**边界条件**：
- `Mode = Off` → 跳过所有 stage，**直接用 InputColor 上采样**
- `NetworkWeightsSize == 0` → 网络未加载，**降级到 FSR1 风格**

### 代码块 2: `ReprojectHistoryColor` + `Gather5x5Features` (HLSL Stage 1+2)

**意图**：Stage 1 reproject history + Stage 2 gather 5×5 邻域 feature。

```hlsl
float4 ReprojectHistoryColor(float2 CurrentUV, Texture2D<float4> HistoryColor,
                              Texture2D<float2> MotionVectors,
                              out float OutDepth, out bool OutIsValid)
{
    float2 MV = MotionVectors.SampleLevel(LinearClampSampler, CurrentUV, 0);
    float2 HistoryUV = CurrentUV - MV;          // (1) 上一帧 UV

    OutIsValid = all(HistoryUV > 0.0) && all(HistoryUV < 1.0);  // (2) 边界检查
    OutDepth = History.w;  // alpha channel 存 depth
    return History;
}

void Gather5x5Features(float2 UV, Texture2D<float4> InputColor,
                       Texture2D<float2> MotionVectors, Texture2D<float> DepthTex,
                       out FFeature Features[25])
{
    float2 PixelOffset = 1.0 / float2(textureSize(InputColor));
    for (int y = -2; y <= 2; ++y) {
        for (int x = -2; x <= 2; ++x) {
            float2 SampleUV = UV + float2(x, y) * PixelOffset;
            int Idx = (y + 2) * 5 + (x + 2);

            float4 Color = InputColor.SampleLevel(LinearClampSampler, SampleUV, 0);
            Features[Idx].Color = Color.rgb;
            Features[Idx].Luma = dot(Color.rgb, float3(0.299, 0.587, 0.114));
            Features[Idx].MV = MotionVectors.SampleLevel(LinearClampSampler, SampleUV, 0);
            Features[Idx].Depth = ConvertFromDeviceZ(DepthTex.SampleLevel(PointSampler, SampleUV, 0));
        }
    }
}
```

**关键参数为什么**：
- **`HistoryUV = CurrentUV - MV`**：reproject 公式，**motion vector 从当前指向上帧**
- **`OutIsValid`**：边界检查，**越界 history 不可信**
- **5×5 = 25 个 sample**：网络输入是 5×5 邻域，**不是单像素**——提供局部上下文
- **`PointSampler`** for depth + **`LinearClampSampler`** for color：**depth 用 point 避免插值失真，color 用 linear 抗锯齿**
- **`OutDepth = History.w`**：alpha channel 复用存 depth，**节省一张纹理**

**边界条件**：
- `MV == 0`：物体不动，**history 完全可用**
- `MV > 1.0`：物体高速移动，**history 不可信，权重降为 0**
- `ConvertFromDeviceZ(DeviceZ)`：device Z ∈ [0, 1]，转换公式依赖 projection matrix

### 代码块 3: `NeuralNetworkInference` (HLSL Stage 3 推理)

**意图**：执行 1 hidden layer MLP 推理，输出 RGB。

```hlsl
StructuredBuffer<float> Conv1_W;   // [25 * 4 input → 32 hidden]
StructuredBuffer<float> Conv1_B;   // [32]
StructuredBuffer<float> Conv2_W;   // [32 hidden → 3 output]
StructuredBuffer<float> Conv2_B;   // [3]

float3 NeuralNetworkInference(FFeature Features[25]) {
    // Flatten 25 features → 100 floats
    float Input[100];
    for (int i = 0; i < 25; ++i) {
        Input[i * 4 + 0] = Features[i].Color.r;
        Input[i * 4 + 1] = Features[i].Color.g;
        Input[i * 4 + 2] = Features[i].Color.b;
        Input[i * 4 + 3] = Features[i].Luma;
    }

    // Layer 1: 100 → 32, ReLU
    float Hidden[32];
    for (int h = 0; h < 32; ++h) {
        float Sum = Conv1_B[h];
        for (int f = 0; f < 100; ++f) {
            Sum += Input[f] * Conv1_W[h * 100 + f];
        }
        Hidden[h] = max(Sum, 0.0);
    }

    // Layer 2: 32 → 3, Sigmoid
    float3 Out;
    Out.r = Conv2_B[0]; Out.g = Conv2_B[1]; Out.b = Conv2_B[2];
    for (int h = 0; h < 32; ++h) {
        float W = Conv2_W[h];
        Out.r += Hidden[h] * W;
    }
    return saturate(Out);
}
```

**关键参数为什么**：
- **2 层（100 → 32 → 3）**：简化版，真实 DLSS 用 16-32 channel conv 数十层
- **`max(Sum, 0.0)`**：ReLU，**比 sigmoid 快 2x**
- **`saturate(Out)`**：最后一层强制 [0, 1]，**HDR 场景需要后处理 rescale**
- **`Hidden[32]`**：本地数组，**GPU 编译器会 spill 到 local memory**，32 维还行

**边界条件**：
- `Conv1_W` 长度 = 100 × 32 = 3200 floats，**GPU 端 StructuredBuffer 必须 ≥ 此大小**
- 网络权重损坏 → 输出 NaN，**应该有 NaN guard fallback 到双线性**

### 代码块 4: `HaltonSequence` (C++ Jitter 序列)

**意图**：生成低差异序列 jitter，**让 TAA / DLSS 多帧覆盖更均匀**。

```cpp
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
    // Y 同理（base = 3）
    return float2(X, Y);
}
```

**关键参数为什么**：
- **`BaseX = 2, BaseY = 3`**：Halton 低差异序列，**2-3 是质数对，避免周期性**
- **8 sample 周期**：8 帧覆盖完整 [0, 1]² 区间
- **比 Random RNG 优势**：random 有 cluster，**Halton 均匀分布**

**边界条件**：
- `SampleIndex > 1024` 后 Halton 退化为 random，**生产用 8 sample 循环**
- `BaseX == BaseY`：序列退化为 1D，**必须用质数对**

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

## 指标手册（Metric Guide）— 每个参数到底在测什么 / 为什么是这个值

> 8 个 CVar 是 DLSS 调参的"入口"。初学者常见误区是"看到参数随便填一个"——这一节告诉你每个参数的"测什么 / 默认值为什么 / 阈值含义 / 怎么调"。

| 参数 | 测什么 | 默认值来源 | 阈值含义 | 怎么调 |
|------|-------|-----------|---------|--------|
| `r.NGX.DLSS.Enable` | DLSS 全局开关 | 0（默认关闭） | 1 = 启用，0 = 关闭 | RTX 卡上启用，否则保持 0 |
| `r.NGX.DLSS.Quality` | Quality 模式 | Balanced | 0=Performance, 1=Balanced, 2=Quality, 3=UltraQuality, 4=UltraPerf | 帧率优先 Performance，质量优先 Quality |
| `r.NGX.DLSS.Sharpness` | 锐化强度 | 0.5 | < 0.3 模糊，> 0.8 ringing | 默认 0.5，**过高会出 ringing artifact** |
| `r.NGX.DLSS.Mode` | DLSS 子模式 | 1（DLSS） | 0=DLAA, 1=DLSS, 2=RayReconstruction | 高端 GPU 用 RayReconstruction（处理 ray noise） |
| `r.PostProcessTemporalAA.Algorithm` | 整体算法 | 2（DLSS/NSR） | 0=Off, 1=FSR2, 2=DLSS/NSR | fallback 时切 FSR2 |
| `r.PostProcessTemporalAA.Jitter Sequence` | Jitter 序列 | Halton | Halton 比 Random 均匀 | 默认 Halton |
| `r.PostProcessTemporalAA.HistoryWeight` | 历史权重 | 0.95 | > 0.98 拖影，< 0.9 闪烁 | 静态场景 0.98，动态 0.92 |
| `r.PostProcessTemporalAA.DiffusionMax` | 颜色扩散半径 | 0.04 | > 0.1 模糊，< 0.01 噪点 | 高速运动场景降到 0.02 |

### 3 个常被误用的参数

#### `Sharpness` 越高越清晰（其实是 ringing）

直觉："`Sharpness 0.8` 比 0.5 锐化更强 = 更清晰"。**错——过高会出 ringing（边缘振铃）**。

| Sharpness | 视觉 |
|-----------|------|
| 0.3 | 模糊（DLSS 原生） |
| 0.5（默认） | 平衡 |
| 0.7 | 锐利但有轻微 ringing |
| 0.8+ | 严重 ringing（边缘白边） |
| 1.0 | 完全崩坏 |

**正解**：保持 0.5，需要锐化用锐化后处理（CAS / FidelityFX CAS）。

#### `Quality` 不是越高画质越好

直觉："UltraQuality 比 Performance 画质好 4 倍"。**对，但输入分辨率差异大**：

| Quality | 输入 scale | 输入分辨率（4K 输出） | 帧率 |
|---------|----------|--------------------|------|
| Performance | 3.0x | 1280×720 | 60 fps |
| Balanced（默认） | 2.0x | 1920×1080 | 45 fps |
| Quality | 1.5x | 2560×1440 | 30 fps |
| UltraQuality | 1.3x | 2954×1666 | 25 fps |
| DLAA | 1.0x | 3840×2160 | 15-20 fps（仅 RTX 4090） |

**正解**：玩家主机配置不同 → 用不同的 Quality mode，**没有"always best"**。

#### `Jitter Sequence` 不是越随机越好

直觉："Random jitter 比 Halton 更好（更多变化）"。**错——Random 有 cluster**。

**为什么 Halton 更好**：
- Halton 是**低差异序列**，N 帧内均匀覆盖 [0, 1]² 区间
- Random 有 cluster（连续多个 sample 在同一区域），**覆盖不均匀**
- DLSS 训练数据基于 Halton，**Random jitter 会让推理结果偏离训练分布**

| Jitter 类型 | 8 帧覆盖 | DLSS 推理稳定性 |
|----------|---------|-----------------|
| Halton | 完美均匀 | 训练匹配 |
| Random | 有 cluster | 略差 |
| Blue noise | 均匀但 slow | 略差 |

**正解**：永远保持 Halton。

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

## 常见误读（Common Misreading）— 5 个初学者陷阱

> 这一节列的是"读文档时容易形成、但实际是错的"理解。每条都是 day-job 真实踩过的坑。

### 误区 1："DLSS = AI 上采样就够了"

**你以为**：启用 DLSS，DLSS 自动处理一切。
**实际**：**DLSS 需要正确的输入才能工作**——motion vector、depth、history buffer 都要正确。

**为什么**：
- DLSS 输入是 `InputColor + InputDepth + InputMotionVectors + HistoryColor + HistoryDepth`
- 任一输入错（motion vector 没勾选 / depth 反推错）→ DLSS 推理结果崩坏
- 历史 8 帧 history 损坏 → 闪烁 / 拖影

**正解**：
- Mesh 上**必须**勾 `Generate Motion Vectors`
- `r.RayTracing 1`（如果用 RT）
- 检查 `r.NGX.DLSS.Debug 1` 显示内部 buffer 是否正常

### 误区 2："DLSS 一定比 FSR 好"

**你以为**：DLSS 是 AI 算法，FSR 不是 → DLSS 永远更好。
**实际**：**FSR3 在某些场景（粒子 / 头发）比 DLSS 更稳定**——因为 FSR 没用 AI 推理，没有神经网络的不确定性。

| 场景 | DLSS | FSR3 |
|------|------|------|
| 静态 / 慢速场景 | ✅ 最好 | 好 |
| 粒子 / 头发 | ⚠ 偶有 artifact | ✅ 稳定 |
| Ray Reconstruction | ✅ 唯一方案 | 不支持 |
| 非 RTX 平台 | 不支持 | ✅ 通用 |

**正解**：
- RTX 高端 + 复杂场景 → DLSS Ray Reconstruction
- 跨平台 / 兼容性优先 → FSR3
- 粒子 / 头发多 → FSR3 更稳

### 误区 3："DLSS Performance 模式永远比 Quality 快"

**你以为**：3x scale 比 1.5x scale 快 4 倍。
**实际**：**DLSS 推理开销恒定（约 0.5-1 ms），Performance vs Quality 差异在输入渲染开销**。

| Mode | 渲染开销（4K 输出） | DLSS 推理 | 总开销 |
|------|-------------------|----------|--------|
| Performance | 0.5 ms（720p 输入） | 0.5 ms | 1.0 ms |
| Quality | 2.0 ms（1440p 输入） | 0.5 ms | 2.5 ms |
| UltraQuality | 4.0 ms（1666p 输入） | 0.5 ms | 4.5 ms |

**正解**：Performance 模式 = 渲染开销低 + DLSS 推理开销恒定 = 总开销 1.0 ms。Quality = 渲染开销高，但视觉更好。

### 误区 4："DLSS 训练一次通用"

**你以为**：NVIDIA 训练的 DLSS 模型适用于所有游戏。
**实际**：**DLSS 训练数据来自 NVIDIA 自家 demo 集，生产游戏风格 / 光照 / 材质差异**。

**为什么不是绝对通用**：
- DLSS 3+ 引入了**游戏特定 fine-tune**，每款 AAA 游戏发布前 NVIDIA 都做过 fine-tune
- 训练数据来自 100+ demo，**但 indie / 二次元 / 像素风训练数据少**
- 风格化游戏（borderlands 描边 / cel-shading）DLSS 可能失真

**正解**：
- 大作发布前联系 NVIDIA 做 DLSS fine-tune
- 风格化游戏先 A/B 测试 DLSS vs FSR 视觉

### 误区 5："DLSS 网络权重上传是一次性的"

**你以为**：启动时上传一次权重，**之后不再上传**。
**实际**：**DLSS Quality 切换会触发不同权重重新上传**。

**为什么**：
- DLSS 5 个 Quality mode 各有不同权重（Performance / Balanced / Quality / UltraQuality / DLAA）
- 运行时切换 Quality mode → 上传对应权重 → **5-20 ms stall**
- 玩家设置菜单切 Quality = **短暂卡顿**

**正解**：
- 启动时预上传所有 Quality mode 权重（**多占用 50-100 MB VRAM**）
- 或者限制玩家只能在加载界面切换 Quality

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

- [[C06/VSM-Virtual-Shadow-Map]]（阴影也是 temporal 重建可优化点）
- [[C08/神经降噪-RT-Denoiser]]（NSR 跟 RT Denoiser 共享 temporal + neural 思路）
- [[C09/神经辐射缓存-Neural-Radiance-Cache]]（NSR 解决空间分辨率, NRC 解决 GI 频率）
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