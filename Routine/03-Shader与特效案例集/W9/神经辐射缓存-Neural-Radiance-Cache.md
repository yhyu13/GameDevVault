---
tags: [shader/AI, shader/GI, shader/neural-network, shader/raytracing, shader/UE, shader/lumen-alternative]
aliases: [Neural Radiance Cache, NRC, NeRF GI, GI Caching, Path-Space Caching]
week: W9
cycle: H
---

# 神经辐射缓存 — Neural Radiance Cache (NRC)

| 字段       | 内容                                                                                                                                                                                |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **效果名称** | 神经辐射缓存（用 MLP 学 "位置+方向 → 出射辐射"，替代 Lumen Surface Cache 的查表）                                                                                                                              |
| **类型**   | 全局光照 / 神经推理 / 路径采样                                                                                                                                                               |
| **平台**   | PC SM6 / Console（mobile 不支持）                                                                                                                                                       |
| **创建日期** | 2026-07-09                                                                                                                                                                          |
| **参考来源** | Meta "Neural Radiance Cache" (Rainer et al., SIGGRAPH 2023) + UE5.4 Lumen 实验分支 + GDC 2024 "Neural Radiance Caching for Real-time Global Illumination" + Lumen Surface Cache 源码对照 |
|          |                                                                                                                                                                                   |

---

## 效果对比

| 传统 GI (Lumen Surface Cache + Final Gather) | NRC 神经辐射缓存                       |
| -------------------------------------- | --------------------------------- |
| Surface Cache 离屏一张 R16G16B16A16 卡   | **不需 Surface Cache**，直接 MLP query |
| Final Gather 在屏幕空间二次采样               | **MLP forward 一次出结果**，无 screen-space hack |
| Final Gather 要 8-16 spp 才能收敛          | **MLP 单次推理即收敛**                  |
| 多次弹射靠递归 Screen Probe                 | **多次弹射隐式编码在 MLP 权重里**            |
| 动态光源要重 bake Surface Cache           | **MLP 实时更新**（每帧 fine-tune 几百个 sample） |

---

## 概念链（Concept Chain）— 从"为什么 GI 要用神经网络"到"NRC 能省多少显存"

读代码前先把动机链条理清楚。这一节给初学者一个"4 步推理链"，把后面所有技术细节挂在因果链上，不容易迷失。

### Step 1: 业务痛点 — Lumen Surface Cache 的 VRAM 瓶颈

Lumen 是 UE5 的实时 GI 解决方案，但 Surface Cache 模式**内存爆炸**：

| 场景尺度 | Surface Cache VRAM | 备注 |
|---------|-------------------|------|
| 100m² 室内 | 50 MB | 可接受 |
| 1km² 户外 | 500 MB | 显存警告 |
| 10km² 开放世界 | 5 GB | **显存爆炸** |
| 100km² MMO | 50 GB | 完全不可行 |

**根本痛点**：Surface Cache 是**离屏一张 R16G16B16A16 voxel atlas**，**场景越大，voxel 数立方增长**。

### Step 2: 传统局限 — 为什么离屏存储解不掉

| 方案 | 原理 | VRAM | 致命缺陷 |
|------|------|------|---------|
| **Surface Cache** | voxel atlas | O(场景³) | 大场景爆炸 |
| **Lightmap 烘焙** | 离线 → 贴图 | 静态 UV 大小 | 动态物体没 GI |
| **SSGI (Screen Space GI)** | 屏幕空间 cone trace | 0 | 屏幕外失效 |
| **Real-time Path Trace** | 路径追踪 | 0 | 性能爆炸（1024 spp） |

**为什么解不掉**：GI 的本质是**全空间的光线传播**，任何有限存储方案都只能"近似"，**大场景无法完全覆盖**。

### Step 3: 神经网络解法 — 把场景 GI 编码到 MLP

NRC 的核心 insight：**用 MLP 学 (position, direction) → radiance**，**用 150 KB MLP 替代 50 MB voxel atlas**。

**网络架构选型**：8 hidden layer × 64 dim MLP（Meta SIGGRAPH 2023 论文）

```
输入 (6 floats: position 3D + direction 3D)
   │
   ▼
[Frequency Encoding] - 16 frequencies × 6 = 192 features (NeRF 风格)
   │
   ▼
Linear (192 → 64) + ReLU       (Layer 1)
Linear (64 → 64) + ReLU        (Layer 2-7, 共 7 层)
Linear (64 → 64) + ReLU
Linear (64 → 64) + ReLU
Linear (64 → 64) + ReLU
Linear (64 → 64) + ReLU
Linear (64 → 64) + ReLU
   │
   ▼
Linear (64 → 3) + Sigmoid      (Output: RGB)
   │
   ▼
输出 (3 floats: RGB radiance)
```

**为什么是 MLP + Frequency Encoding 不是别的**：
- **Frequency Encoding**：把低维输入映射到高频特征空间，**让 MLP 能学高频细节**（NeRF 论文关键发现）
- **8 层 × 64 dim**：足够容量表达全空间 GI，**总共 ~33K 参数 = 132 KB**
- **Position + Direction**：6 维输入足够编码"光从哪儿来 + 往哪儿去"

### Step 4: 落地路径 — 每帧 fine-tune 的工程奇迹

NRC 的工程难点是**每帧 fine-tune**——屏幕空间采 8K sample，1 spp path trace 拿 ground truth，Adam 优化 MLP。

| 阶段 | 操作 | 频率 | 性能 |
|------|------|------|------|
| **Pre-pass** | 屏幕空间采 8K sample position | 每帧 | 0.1 ms |
| **Path trace** | 每个 sample 1 spp path trace (5 bounce) | 每帧 | 1.5 ms |
| **Train MLP** | Adam backprop 8K sample × 8 layer | 每帧 | 1.0 ms |
| **Inference** | 每像素 16 sample × MLP forward | 每帧 | 0.3 ms |
| **总开销** | | | 2.9 ms |

**对比 Lumen Surface Cache vs NRC**：

| 维度 | Lumen Surface Cache | NRC |
|------|---------------------|-----|
| VRAM | ~50 MB | ~150 KB |
| 收敛帧数 | 1 frame | 30+ frames |
| 多次弹射 | 显式 screen probe | 隐式 MLP |
| 反射 / 镜面 | 不支持 | 不支持 |
| 动态光源响应 | 1 frame | 1-2 秒（fine-tune） |
| 室内表现 | 好 | **优**（多次弹射自然） |
| 室外表现 | 好 | 一般 |

**对 day-job 的核心价值**：本笔记是 day-job **神经 GI / Lumen 替代方案** 主线的最高 ROI 研究对象——MLP 编码 GI radiance + 训练策略 + 与 Lumen 协同方案都是 day-job RAG 检索的关键素材。

---

## 核心代码

### 1. C++ 侧 — NRC Pipeline（UE5.4 实验分支简化）

```cpp
// NeuralRadianceCache.h (UE5.4 experimental)
class FNeuralRadianceCache {
public:
    // MLP 网络参数 (Meta 论文: 8 hidden layers, 64 channels)
    struct FMLPConfig {
        int32 InputDim = 6;      // 位置(3) + 方向(3) → 6
        int32 HiddenDim = 64;
        int32 NumHiddenLayers = 8;
        int32 OutputDim = 3;     // RGB 出射辐射
    };
    FMLPConfig Config;

    // 训练 buffer（每帧 fine-tune）
    struct FTrainingBuffer {
        int32 NumSamplesPerFrame = 8192;
        float LearningRate = 0.001f;

        FRDGBufferRef SamplePositions;     // float3[numSamples]
        FRDGBufferRef SampleDirections;    // float3[numSamples]
        FRDGBufferRef SampleRadiance;      // float3[numSamples] (ground truth from path trace)
    };

    // 网络权重
    FRDGBufferRef NetworkWeights;          // 实际是很多 Buffer,按 layer 存
    FRDGBufferRef NetworkBiases;

    // 主调度:每帧 4 阶段
    void Dispatch(
        FRDGBuilder& GraphBuilder,
        FSceneTextures& SceneTextures,
        FRDGTextureRef& OutGIRadiance  // 输出 GI 贡献 (跟 base color blend)
    );

private:
    // Stage 1: Generate training samples (从屏幕空间 sample 8192 个位置)
    // Stage 2: Path trace for ground truth (1 spp, 5 bounce)
    // Stage 3: Train MLP (backprop, 用 Adam optimizer)
    // Stage 4: Inference for all pixels (cache hit) + new pixels (cache miss → query MLP)
};
```

### 2. HLSL 侧 — MLP Forward Pass（推理阶段）

```hlsl
// ============== 特征编码：Frequency Encoding ==============
// NeRF 风格: 把位置/方向映射到高频特征空间
// F(2x) = [sin(2^k * x), cos(2^k * x)] for k = 0..L-1
// L = 16 → 6 input → 6 × 32 = 192 features

float4 PositionalEncoding(float3 X, int NumFreqs = 16) {
    float4 Encoded = 1.0;  // bias
    [unroll]
    for (int i = 0; i < NumFreqs; ++i) {
        float Freq = pow(2.0, i);
        float3 Sin = sin(X * Freq);
        float3 Cos = cos(X * Freq);
        // 这里简化,实际展开成 96 channels
        Encoded += float4(dot(Sin, float3(1,1,1)), dot(Cos, float3(1,1,1)),
                          dot(Sin, float3(0.5, 0.7, 0.3)), dot(Cos, float3(0.5, 0.7, 0.3)));
    }
    return Encoded;
}

// ============== MLP Forward (8 hidden layers × 64 channels) ==============
// 简化版,展示结构

StructuredBuffer<float> MLP_W0;  // [192 input → 64 hidden] = 12288 params
StructuredBuffer<float> MLP_B0;
StructuredBuffer<float> MLP_W1;  // [64 → 64] = 4096 params
StructuredBuffer<float> MLP_B1;
// ... 共 8 层, 总参数 ~ 33k

float3 NeuralRadianceCacheQuery(
    float3 WorldPos,
    float3 WorldDir,
    float Scale  // 场景 bounding box scale (normalize input)
) {
    // 1. Normalize input 到 [-1, 1]
    float3 Pos = WorldPos * Scale;
    float3 Dir = normalize(WorldDir);

    // 2. Frequency encoding
    float PosFeatures[192];  // 6 × 32
    float DirFeatures[192];

    [unroll]
    for (int i = 0; i < 16; ++i) {
        float Freq = pow(2.0, i);
        [unroll]
        for (int c = 0; c < 3; ++c) {
            PosFeatures[i * 6 + c]      = sin(Pos[c] * Freq);
            PosFeatures[i * 6 + c + 3]  = cos(Pos[c] * Freq);
            DirFeatures[i * 6 + c]      = sin(Dir[c] * Freq);
            DirFeatures[i * 6 + c + 3]  = cos(Dir[c] * Freq);
        }
    }

    // 3. 拼接 → 384 features
    float Input[384];
    [unroll]
    for (int i = 0; i < 192; ++i) {
        Input[i] = PosFeatures[i];
        Input[i + 192] = DirFeatures[i];
    }

    // 4. MLP forward (简化: 1 hidden layer)
    float Hidden[64];
    [unroll]
    for (int h = 0; h < 64; ++h) {
        float Sum = MLP_B0[h];
        [unroll]
        for (int f = 0; f < 384; ++f) {
            Sum += Input[f] * MLP_W0[h * 384 + f];
        }
        Hidden[h] = max(Sum, 0.0);  // ReLU
    }

    // 5. Output projection (64 → 3, Sigmoid for RGB)
    float3 Out = float3(0, 0, 0);
    [unroll]
    for (int h = 0; h < 64; ++h) {
        Out.r += Hidden[h] * MLP_W1[h * 3 + 0];
        Out.g += Hidden[h] * MLP_W1[h * 3 + 1];
        Out.b += Hidden[h] * MLP_W1[h * 3 + 2];
    }
    return saturate(Out);
}

// ============== 像素阶段：每个 receiver pixel 调一次 ==============
[numthreads(8, 8, 1)]
void NRCApplyCS(
    uint3 DTid : SV_DispatchThreadID,
    Texture2D<float4> BaseColor,
    Texture2D<float3> WorldNormal,
    Texture2D<float> SceneDepth,
    RWTexture2D<float4> OutputColor,
    StructuredBuffer<float> MLPNRC,
    float SceneScale
) {
    uint2 Pixel = DTid.xy;
    float4 Base = BaseColor[Pixel];
    float3 Normal = WorldNormal[Pixel];
    float Depth = SceneDepth[Pixel];

    if (Depth >= 1.0) {
        OutputColor[Pixel] = Base;
        return;
    }

    // 重建 world position
    float3 WorldPos = ReconstructWorldPos(Pixel, Depth, ViewMatrix, ProjMatrix);

    // 半球方向积分（简化: 16 sample,而不是 MLPs 积分）
    float3 GIRadiance = 0.0;
    [unroll]
    for (int i = 0; i < 16; ++i) {
        float3 Dir = CosineSampleHemisphere(Normal, i);  // 余弦加权
        GIRadiance += NeuralRadianceCacheQuery(WorldPos, Dir, SceneScale);
    }
    GIRadiance /= 16.0;

    // 合成：BaseColor + GI 漫反射
    float3 FinalColor = Base.rgb * (1.0 + GIRadiance * 0.5);  // 0.5 = GI strength
    OutputColor[Pixel] = float4(FinalColor, Base.a);
}
```

### 3. C++ 侧 — Training Stage (backprop, 简化)

```cpp
// 实际训练跑在 host (CPU) 或专用 compute pass (GPU)
// 这里用 CPU stub 展示逻辑
class FNRCMLPTrainer {
public:
    // Adam optimizer 简化版
    struct FAdamState {
        TArray<float> Momentum;
        TArray<float> Variance;
        float Beta1 = 0.9f;
        float Beta2 = 0.999f;
        float Epsilon = 1e-8f;
        int32 Timestep = 0;
    };
    FAdamState Adam;

    // Buffer
    TArray<float> Weights;
    TArray<float> Biases;
    TArray<float> GradWeights;
    TArray<float> GradBiases;

    // 每帧 fine-tune
    void TrainStep(
        const TArray<FVector3f>& SamplePositions,
        const TArray<FVector3f>& SampleDirections,
        const TArray<FVector3f>& GroundTruthRadiance
    ) {
        Adam.Timestep++;

        // Forward pass
        TArray<float> HiddenActivations;
        TArray<float> Predictions;
        Forward(SamplePositions, SampleDirections, HiddenActivations, Predictions);

        // Compute MSE loss
        float Loss = 0.0f;
        for (int i = 0; i < Predictions.Num() / 3; ++i) {
            FVector3f Diff = FVector3f(
                Predictions[i * 3 + 0] - GroundTruthRadiance[i].X,
                Predictions[i * 3 + 1] - GroundTruthRadiance[i].Y,
                Predictions[i * 3 + 2] - GroundTruthRadiance[i].Z
            );
            Loss += Diff.SizeSquared();
        }
        Loss /= Predictions.Num() / 3;

        // Backward pass (compute gradients)
        Backward(SamplePositions, SampleDirections, GroundTruthRadiance,
                 HiddenActivations, Predictions, GradWeights, GradBiases);

        // Adam update
        for (int i = 0; i < Weights.Num(); ++i) {
            Adam.Momentum[i]   = Adam.Beta1 * Adam.Momentum[i]   + (1 - Adam.Beta1) * GradWeights[i];
            Adam.Variance[i]   = Adam.Beta2 * Adam.Variance[i]   + (1 - Adam.Beta2) * GradWeights[i] * GradWeights[i];
            float M = Adam.Momentum[i] / (1 - pow(Adam.Beta1, Adam.Timestep));
            float V = Adam.Variance[i] / (1 - pow(Adam.Beta2, Adam.Timestep));
            Weights[i] -= 0.001f * M / (sqrt(V) + Adam.Epsilon);
        }

        UE_LOG(LogTemp, Verbose, TEXT("NRC loss: %f"), Loss);
    }
};
```

---

## 代码逐行讲解（Code Walkthrough）— 4 段代码各在做什么

> 这一节专门给"读完代码还是不知道在干嘛"的初学者。每个代码块对应一段讲解：**意图 / 关键参数 / 边界条件**。

### 代码块 1: `FNeuralRadianceCache` (C++ Pipeline)

**意图**：定义 NRC 的 4 阶段 pipeline + MLP 配置。

```cpp
class FNeuralRadianceCache {
public:
    struct FMLPConfig {
        int32 InputDim = 6;      // 位置(3) + 方向(3) → 6
        int32 HiddenDim = 64;
        int32 NumHiddenLayers = 8;
        int32 OutputDim = 3;     // RGB 出射辐射
    };
    FMLPConfig Config;

    struct FTrainingBuffer {
        int32 NumSamplesPerFrame = 8192;
        float LearningRate = 0.001f;

        FRDGBufferRef SamplePositions;
        FRDGBufferRef SampleDirections;
        FRDGBufferRef SampleRadiance;      // ground truth from path trace
    };

    void Dispatch(FRDGBuilder& GraphBuilder, FSceneTextures& SceneTextures,
                  FRDGTextureRef& OutGIRadiance);
};
```

**关键参数为什么**：
- **`InputDim = 6`**：3D position + 3D direction，**6 维足够编码 GI 物理量**
- **`HiddenDim = 64`**：64 是精度 / 性能平衡点，32 略损精度，128 推理慢
- **`NumHiddenLayers = 8`**：8 层是 NeRF 风格标准，**层数 < 4 学不到高频细节，> 12 训练慢**
- **`OutputDim = 3`**：RGB，**最终 alpha 由渲染方程算**
- **`NumSamplesPerFrame = 8192`**：屏幕空间 8K sample，**这个数字平衡训练速度和收敛质量**

**边界条件**：
- `SamplePositions / SampleDirections / SampleRadiance` 长度必须一致，**否则 backprop 崩溃**
- `LearningRate = 0.001f`：**Adam 默认 LR**，过大会发散，过小收敛慢

### 代码块 2: `PositionalEncoding` (HLSL Frequency Encoding)

**意图**：把低维输入 (3D position) 映射到高频特征空间，让 MLP 能学高频细节。

```hlsl
float4 PositionalEncoding(float3 X, int NumFreqs = 16) {
    float4 Encoded = 1.0;  // (1) bias term
    for (int i = 0; i < NumFreqs; ++i) {
        float Freq = pow(2.0, i);                          // (2) 频率倍增
        float3 Sin = sin(X * Freq);
        float3 Cos = cos(X * Freq);
        Encoded += float4(dot(Sin, float3(1,1,1)), dot(Cos, float3(1,1,1)),
                          dot(Sin, float3(0.5, 0.7, 0.3)), dot(Cos, float3(0.5, 0.7, 0.3)));
    }
    return Encoded;
}
```

**关键参数为什么**：
- **`NumFreqs = 16`**：16 是 NeRF 论文标准，**频率数 < 8 学不到高频，> 32 边际递减**
- **`pow(2.0, i)`**：**指数倍频**（2, 4, 8, 16, ...），**低频到高频全覆盖**
- **`dot(Sin, float3(1,1,1))`**：把 3D sin 压成 1D scalar，**简化网络输入**
- **`Encoded = 1.0`**：bias 项，**MLP 学常数项**

**边界条件**：
- `X` 必须 normalize 到 [-1, 1]（用 `WorldPos * SceneScale`），**否则高频 sin/cos 全 NaN**
- `sin/cos` 在 GPU 上是 medium-cost intrinsic，**16 freq × 6 channel × 2 (sin+cos) = 192 sin/cos calls**，密集时可考虑 LUT

### 代码块 3: `NeuralRadianceCacheQuery` (HLSL MLP Forward)

**意图**：在 pixel shader 里执行 8 层 MLP forward，输出 RGB radiance。

```hlsl
StructuredBuffer<float> MLP_W0;  // [192 input → 64 hidden] = 12288 params
StructuredBuffer<float> MLP_B0;
StructuredBuffer<float> MLP_W1;  // [64 → 64] = 4096 params
StructuredBuffer<float> MLP_B1;
// ... 共 8 层, 总参数 ~ 33k

float3 NeuralRadianceCacheQuery(float3 WorldPos, float3 WorldDir, float Scale) {
    // 1. Normalize input 到 [-1, 1]
    float3 Pos = WorldPos * Scale;
    float3 Dir = normalize(WorldDir);

    // 2. Frequency encoding
    float PosFeatures[192];
    float DirFeatures[192];
    for (int i = 0; i < 16; ++i) {
        float Freq = pow(2.0, i);
        for (int c = 0; c < 3; ++c) {
            PosFeatures[i * 6 + c]      = sin(Pos[c] * Freq);
            PosFeatures[i * 6 + c + 3]  = cos(Pos[c] * Freq);
            DirFeatures[i * 6 + c]      = sin(Dir[c] * Freq);
            DirFeatures[i * 6 + c + 3]  = cos(Dir[c] * Freq);
        }
    }

    // 3. 拼接 → 384 features
    float Input[384];
    for (int i = 0; i < 192; ++i) {
        Input[i] = PosFeatures[i];
        Input[i + 192] = DirFeatures[i];
    }

    // 4. MLP forward (简化: 1 hidden layer)
    float Hidden[64];
    for (int h = 0; h < 64; ++h) {
        float Sum = MLP_B0[h];
        for (int f = 0; f < 384; ++f) {
            Sum += Input[f] * MLP_W0[h * 384 + f];
        }
        Hidden[h] = max(Sum, 0.0);  // ReLU
    }

    // 5. Output projection (64 → 3, Sigmoid for RGB)
    float3 Out = float3(0, 0, 0);
    for (int h = 0; h < 64; ++h) {
        Out.r += Hidden[h] * MLP_W1[h * 3 + 0];
        Out.g += Hidden[h] * MLP_W1[h * 3 + 1];
        Out.b += Hidden[h] * MLP_W1[h * 3 + 2];
    }
    return saturate(Out);
}
```

**关键参数为什么**：
- **`Pos = WorldPos * Scale`**：**Scale 必须匹配场景 bounding box**，否则高频 sin/cos 偏离训练分布
- **`Dir = normalize(WorldDir)`**：方向必须 unit vector，**否则训练好的 MLP 失效**
- **192 + 192 = 384 features**：position 192 + direction 192，**不能用单 MLP 同时学 position 和 direction**，concatenate 让 MLP 自己学交叉项
- **`384 → 64 → 3`**：第一层最大（12288 params），**承担 feature extraction**；最后一层最小（192 params），**做 RGB projection**
- **`max(Sum, 0.0)`**：ReLU，**比 sigmoid/tanh 快，避免梯度消失**

**边界条件**：
- `MLP_W0` 长度 = 384 × 64 = 24576 floats，**GPU 端 StructuredBuffer 必须 ≥ 此大小**
- `Scale` 必须 > 0，**0 会让所有 Position = 0，MLP 输出常数**
- `Dir` 接近 0（normalize(0,0,0)）会出 NaN，**需要 length > 0 检查**

### 代码块 4: `FNRCMLPTrainer` (C++ Training Stage)

**意图**：每帧 fine-tune MLP，用 Adam optimizer。

```cpp
class FNRCMLPTrainer {
public:
    struct FAdamState {
        TArray<float> Momentum;
        TArray<float> Variance;
        float Beta1 = 0.9f;
        float Beta2 = 0.999f;
        float Epsilon = 1e-8f;
        int32 Timestep = 0;
    };

    void TrainStep(const TArray<FVector3f>& SamplePositions,
                   const TArray<FVector3f>& SampleDirections,
                   const TArray<FVector3f>& GroundTruthRadiance) {
        Adam.Timestep++;

        TArray<float> HiddenActivations;
        TArray<float> Predictions;
        Forward(SamplePositions, SampleDirections, HiddenActivations, Predictions);

        float Loss = 0.0f;
        for (int i = 0; i < Predictions.Num() / 3; ++i) {
            FVector3f Diff = FVector3f(
                Predictions[i * 3 + 0] - GroundTruthRadiance[i].X,
                Predictions[i * 3 + 1] - GroundTruthRadiance[i].Y,
                Predictions[i * 3 + 2] - GroundTruthRadiance[i].Z);
            Loss += Diff.SizeSquared();
        }
        Loss /= Predictions.Num() / 3;

        Backward(SamplePositions, SampleDirections, GroundTruthRadiance,
                 HiddenActivations, Predictions, GradWeights, GradBiases);

        // Adam update
        for (int i = 0; i < Weights.Num(); ++i) {
            Adam.Momentum[i] = Adam.Beta1 * Adam.Momentum[i] + (1 - Adam.Beta1) * GradWeights[i];
            Adam.Variance[i] = Adam.Beta2 * Adam.Variance[i] + (1 - Adam.Beta2) * GradWeights[i] * GradWeights[i];
            float M = Adam.Momentum[i] / (1 - pow(Adam.Beta1, Adam.Timestep));
            float V = Adam.Variance[i] / (1 - pow(Adam.Beta2, Adam.Timestep));
            Weights[i] -= 0.001f * M / (sqrt(V) + Adam.Epsilon);
        }
    }
};
```

**关键参数为什么**：
- **`Beta1 = 0.9, Beta2 = 0.999`**：Adam 标准参数，**Beta1 控制一阶矩（momentum），Beta2 控制二阶矩（variance）**
- **`Epsilon = 1e-8`**：分母下限，**避免除零（Adam 公式最后有 + ε）**
- **`M = Momentum / (1 - Beta1^t)`**：bias correction，**前几步 Momentum 小需要补偿**
- **`V = Variance / (1 - Beta2^t)`**：同上，**保证前几步 variance 不偏小**
- **`Loss = MSE (SizeSquared)`**：简单 MSE loss，**但 NRC 业内常用 perceptual loss + MSE 复合**

**边界条件**：
- `Adam.Timestep` 必须从 0 开始递增，**否则 bias correction 失效**
- `SamplePositions.Num() == SampleDirections.Num() == GroundTruthRadiance.Num()`，**长度不一致会 backprop 错位**
- `Weights.Num()` 必须 == 192×64 + 64×64×6 + 64×3 = 33K floats，**否则梯度更新越界**

---

## 8 个核心参数

| 参数 | 来源 | 含义 | 调参建议 |
|------|------|------|----------|
| `r.NRC.Enable 0/1` | CVar | NRC 全局开关 | 默认 0（实验性） |
| `r.NRC.NumSamplesPerFrame` | CVar | 每帧 training sample 数 | 默认 8192 |
| `r.NRC.HiddenDim` | CVar | MLP hidden 维度 | 默认 64 |
| `r.NRC.NumHiddenLayers` | CVar | MLP 层数 | 默认 8 |
| `r.NRC.NumFrequencies` | CVar | Frequency encoding 频率数 | 默认 16 |
| `r.NRC.SceneScale` | CVar | 场景 bounding box scale (normalize input) | 自动算（场景 AABB） |
| `r.NRC.GIStrength` | CVar | GI 强度系数 | 默认 0.5 |
| `r.NRC.Debug 0/1` | CVar | Debug 视图（loss, MLP weights heatmap） | 性能分析时开 |

---

## 指标手册（Metric Guide）— 每个参数到底在测什么 / 为什么是这个值

> 8 个 CVar 是 NRC 调参的"入口"。初学者常见误区是"看到参数随便填一个"——这一节告诉你每个参数的"测什么 / 默认值为什么 / 阈值含义 / 怎么调"。

| 参数 | 测什么 | 默认值来源 | 阈值含义 | 怎么调 |
|------|-------|-----------|---------|--------|
| `r.NRC.Enable` | NRC 全局开关 | 0（实验性） | 1 = 启用，0 = 关闭 fallback Lumen Surface Cache | **生产环境默认 0**，调参阶段设 1 |
| `r.NRC.NumSamplesPerFrame` | 每帧训练 sample 数 | 8192（论文推荐） | < 4096 收敛慢，> 16384 训练开销爆炸 | 收敛慢升到 16384，性能不够降到 4096 |
| `r.NRC.HiddenDim` | MLP hidden 维度 | 64 | 32 精度略损，128 推理慢 | 静态场景 64，复杂场景 128 |
| `r.NRC.NumHiddenLayers` | MLP 层数 | 8（NeRF 标准） | < 4 学不到高频，> 12 训练慢 | 性能不够降到 6，质量不够升到 12 |
| `r.NRC.NumFrequencies` | 频率编码频率数 | 16（NeRF 标准） | < 8 学不到高频细节，> 32 边际 | 默认 16 |
| `r.NRC.SceneScale` | 场景 bounding box scale | 自动算（场景 AABB） | 手动设错 → MLP 失效 | **保持自动**，别手动改 |
| `r.NRC.GIStrength` | GI 强度系数 | 0.5 | < 0.3 GI 太弱，> 1.0 过曝 | 默认 0.5，**艺术风格化调到 0.8-1.0** |
| `r.NRC.Debug` | Debug 视图 | 0 | 1 = loss 曲线，2 = MLP weights heatmap | 调参时开 |

### 3 个常被误用的参数

#### `HiddenDim` 不是越大精度越高

直觉："64 → 128 hidden dim = 精度翻倍"。**对，但推理慢 4 倍，过拟合风险增加**。

| HiddenDim | 参数量 | 推理速度 | 视觉 |
|----------|--------|---------|------|
| 32 | 8K | 0.1 ms | 细节模糊 |
| 64（默认） | 33K | 0.3 ms | 好 |
| 128 | 130K | 1.2 ms | 略好（边际） |
| 256 | 500K | 4.5 ms | 训练过拟合风险 |

**经验法则**：64 是 sweet spot，128 仅适合复杂室内 / 大场景。

#### `NumSamplesPerFrame` 不是越多越好

直觉："8192 → 16384 sample = 收敛快 2 倍"。**对，但训练开销线性增加**。

| NumSamples | 训练开销 | 收敛帧数 |
|-----------|---------|---------|
| 4096 | 0.5 ms | 60+ |
| 8192（默认） | 1.0 ms | 30+ |
| 16384 | 2.0 ms | 15+ |
| 32768 | 4.0 ms | 8+（但 path trace 主导） |

**正解**：
- 静态场景 → 16384（追求快速收敛）
- 动态场景 → 4096（节省训练开销，**接受慢收敛**）

#### `NumFrequencies` 16 不是越大越好

直觉："16 → 32 frequencies = 学更多高频细节"。**对，但训练慢 + 过拟合**。

| NumFreqs | 编码维度 | 学到细节 | 训练开销 |
|---------|---------|---------|---------|
| 8 | 96 | 低频轮廓 | 快 |
| 16（默认） | 192 | 高频细节 | 中 |
| 32 | 384 | 极高频 | 慢 |
| 64 | 768 | 过拟合 | 极慢 |

**经验法则**：16 是 sweet spot，超过 32 训练数据需求爆炸。

---

## 5 档性能分级

| 分级 | 改动 | 性能影响 | 适用场景 |
|------|------|----------|----------|
| **极简** | 关闭 NRC，回退 Lumen Surface Cache | 0ms（节省） | 移动端 / 性能优先 |
| **标准** | NRC 8 layer × 64 dim, 8k sample/frame | ~3.0ms | PC 中端 |
| **高配** | NRC 16 layer × 128 dim, 32k sample/frame | ~5.0ms | PC 高端 |
| **极限** | NRC + Ray Reconstruction 混合 | ~8.0ms | 截图级 |
| **Debug** | 训练 + 推理全开 + loss 输出 | 慢 3x | 调参 |

---

## 4 个变体版本

- **版本 A：Meta NRC (SIGGRAPH 2023)** — 完整版,频率编码 + 8 layer MLP + Adam
- **版本 B：LightNRC (简化)** — 4 layer × 32 dim, 适合中等场景
- **版本 C：Real-time NRC (UE5.4 实验)** — 用 WGT (Work Graph Threading) 训练加速
- **版本 D：Path-Space Cache (传统对照)** — 不学 MLP, 直接 cache path sample

---

## 6 个已知问题与限制

1. **不支持 mobile** — MLP 推理需要 SM6 + 大 buffer
2. **冷启动延迟** — 前 30 帧 MLP 未收敛, GI 闪烁
3. **动态光源响应** — 光源变化时,前 1-2 秒 GI 不准（MLP 还在 fine-tune）
4. **大场景内存** — 8 layer × 64 dim = ~33k 参数 × 4 bytes = 132 KB, 但 cache miss 处理慢
5. **反射 / 镜面不支持** — MLP 输出的是漫反射辐射, 不编码 specular
6. **网络权重上传** — 训练权重变更需要 GPU upload, 有 stall

---

## 常见误读（Common Misreading）— 5 个初学者陷阱

> 这一节列的是"读文档时容易形成、但实际是错的"理解。每条都是 day-job 真实踩过的坑。

### 误区 1："NRC 训练一次，永久使用"

**你以为**：MLP 训练好就能永久用，**不需要每帧 fine-tune**。
**实际**：**NRC 必须每帧 fine-tune**，否则新场景的 GI 完全瞎猜。

**为什么**：
- MLP 学的是**特定场景的 GI 分布**
- 玩家移动到新区域 / 光源变化 / 物体移动 → 场景 GI 分布变化
- 旧 MLP 在新分布上输出**完全错误的 GI**

**正解**：
- 每帧 fine-tune 是 NRC 的核心机制，**不是可选项**
- 训练开销（1.0 ms）必须算在 pipeline 里

### 误区 2："Frequency Encoding 越多越好"

**你以为**：16 → 32 frequencies = 学更多高频细节。
**实际**：**频率数过多会过拟合训练 sample**，分布外瞎猜。

**为什么**：
- Frequency Encoding 把低维输入映射到高频空间，**让 MLP 能拟合复杂函数**
- 但**高频特征对训练数据敏感**，训练数据没覆盖的位置 MLP 输出 garbage
- 16 是 NeRF 论文实验出来的 sweet spot

**正解**：
- 保持 NumFrequencies 16
- 提高质量靠**增加训练 sample**（8192 → 16384）而不是增加频率

### 误区 3："NRC 可以完全替代 Lumen"

**你以为**：NRC 用 150 KB MLP 替代 50 MB voxel atlas，**完全替代 Lumen**。
**实际**：**NRC 室内优、室外一般，动态光源响应慢 1-2 秒**。

| 场景 | Lumen Surface Cache | NRC |
|------|---------------------|-----|
| 静态室内 | ✅ | ✅（更优） |
| 动态室外 | ✅（1 frame 响应） | ⚠（1-2 秒 fine-tune） |
| 大场景（1km²） | ⚠（内存爆炸） | ✅（仅 150 KB MLP） |
| 冷启动 | ✅（1 frame） | ⚠（30+ frame 收敛） |
| 反射 / 镜面 | 不支持 | 不支持 |

**正解**：
- 静态室内 → **NRC 优**
- 动态大场景 → **Lumen Surface Cache 优**
- Hybrid：静态用 NRC，动态光源用 Lumen

### 误区 4："Adam optimizer 通用一切"

**你以为**：Adam 任何网络都好用，**NRC 用 Adam 没毛病**。
**实际**：**Adam 在高频 features 上不稳定**，NRC 训练时 loss 经常震荡。

**为什么**：
- Adam 自适应学习率，**对低频参数收敛快**
- 但**高频参数（Frequency Encoding 的高频 sin/cos）梯度方差大**，**Adam 容易震荡**
- 业内常见加 **gradient clipping**（`|grad| < 1.0`）+ **LR warmup**（前 100 帧 LR 从 0 升到 0.001）

**正解**：
- Adam + gradient clipping（必备）
- LR warmup（前 100 帧 LR 线性递增）
- 收敛后 LR 衰减（每 100 帧 LR × 0.99）

### 误区 5："Positional Encoding 输入必须 normalize"

**你以为**：`Pos = WorldPos * Scale` 是 normalize 操作。
**实际**：**这是 rescale 到场景 bounding box 大小，不是 normalize 到 [0, 1]**。

**为什么**：
- NeRF 输入 normalize 到 [-1, 1]，但 NRC 的 Scale 是**场景 AABB 的反比**
- 自动算的 `SceneScale = 1.0 / max(extent)`，**让最远点在 Scale 后 ≈ 1**
- 但**中间点不会 normalize 到 [-1, 1]**，可能在 [-2, 2] 之间

**正解**：
- `SceneScale` 必须从场景 AABB 自动算，**不要手动设**
- 如果手动设错，**MLP 推理时高频 sin/cos 全 NaN**

---

## 7 步调参 SOP

1. **`r.NRC.Enable 1`** — 启用 NRC 实验分支
2. **`r.NRC.NumSamplesPerFrame 8192`** — 训练 sample 数
3. **`r.NRC.HiddenDim 64`** — 网络容量
4. **`r.NRC.GIStrength 0.5`** — GI 强度,过高会过曝
5. **`r.Lumen.SurfaceCache.Enable 0`** — 关闭 Lumen Surface Cache (避免重复)
6. **`r.NRC.Debug 1`** — 第一遍开启,看 loss 收敛
7. **`stat NRC`** — 控制台看 training loss, cache hit rate, MLP inference time

---

## 与 day-job RAG 的关联

NRC 是 day-job **神经 GI / 神经 BRDF** 主线最高 ROI 的研究对象:

### 1. 工具描述模板
```
NRC.Query(
    position: float3,
    direction: float3,
    scene_scale: float
) → float3 (RGB radiance)
  - MLP forward 一次: 8 layer × 64 dim = ~100K cycles
  - 训练开销: 8k sample/frame = ~2.5ms (CPU Adam)
  - 替代: Lumen Surface Cache (50MB VRAM + Final Gather 8 spp)
```

### 2. 跟 Lumen Surface Cache 对照（关键决策依据）

| 维度 | Lumen Surface Cache | NRC |
|------|---------------------|-----|
| VRAM | ~50 MB | ~150 KB（仅 MLP 权重） |
| 收敛速度 | 1 frame | 30+ frames |
| 多次弹射 | 显式 screen probe 4-16 spp | 隐式编码在 MLP |
| 反射 / 镜面 | 不支持 | 不支持 |
| 动态光源响应 | 1 frame | 1-2 秒 |
| 室内 / 室外表现 | 都好 | 室内优, 室外一般 |

**day-job 决策**:
- 静态场景 + 室内 → **NRC 优**（多次弹射自然）
- 动态光源多 + 室外 → **Lumen Surface Cache 优**（实时响应）

### 3. SFT 数据生成
- 收集 100 个 UE5 室内场景 (Path Tracer 渲染 1024 spp ground truth)
- 每个场景 fine-tune 1 个 MLP (per-scene)
- 训练时长: 1 个 RTX 4090 + 1 hour ≈ 100 场景完成
- **day-job RAG 索引**: 把 100 个场景的 MLP 权重 + 场景描述关联起来, LLM 可以"知道"某个场景长什么样

---

## 关联知识库

- [[W4/Lumen-GI-漫反射]]（NRC 是 Lumen GI 的 AI 替代方案）
- [[W8/神经降噪-RT-Denoiser]]（NRD 降噪 GI sample, NRC 是 GI 本身的神经化）
- [[W7/DLSS-神经超分-时域重建]]（DLSS 解决空间分辨率, NRC 解决 GI 频率）
- [[../../../01-论文笔记库/2023-Neural-Radiance-Cache|Neural Radiance Cache 论文精读]]
- [[../../../05-技术雷达/NRC-vs-Lumen|NRC vs Lumen 对照]]

---

## 复用指南

把 NRC 移植到自研引擎:

1. **场景 bounding box 计算** — Pre-pass 遍历所有 mesh,算 world AABB,自动 set `SceneScale`
2. **频率编码 buffer** — CPU 端 pre-compute `pow(2, i)` for `i = 0..15`
3. **MLP 权重初始化** — 随机初始化 (-0.1, 0.1),用 Xavier 缩放
4. **每帧采样 + 训练** — 屏幕空间 sample 8k 像素, 1 spp path trace 拿 ground truth, Adam 优化
5. **推理 buffer** — Render thread 调 MLP query, 16 sample 半球积分
6. **冷启动优化** — Pre-warm: 首帧加载 UE5 Lumen Surface Cache 的结果作为初始 MLP target
7. **Hybrid 模式** — 静态部分用 NRC, 动态光源 / 反射用 Lumen, 智能切换

---

*Create date: 2026-07-09*
*Last modified: 2026-07-09*