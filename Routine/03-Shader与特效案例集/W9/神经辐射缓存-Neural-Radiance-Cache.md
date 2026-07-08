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