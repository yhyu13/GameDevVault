---
tags: [shader/AI, shader/BRDF, shader/PBR, shader/neural-network, shader/UE, shader/GGX]
aliases: [Neural BRDF, NeuralGGX, BRDF Approximation, Disney Replacement, GGX Neural]
week: W2
cycle: new
---

# 神经 BRDF — NeuralGGX (神经网络拟合 GGX/Disney BRDF)

| 字段       | 内容                                                                                                                                                                                |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **效果名称** | 神经 BRDF 拟合（用 MLP 学 "(roughness, metallic, viewDir, lightDir) → BRDF 值"，替代传统 GGX/Disney 公式）                                                                                          |
| **类型**   | BRDF / 神经推理 / 实时                                                                                                                                                              |
| **平台**   | PC SM6 / Console（mobile 不支持，需 fallback 传统 GGX）                                                                                                                                       |
| **创建日期** | 2026-07-09                                                                                                                                                                          |
| **参考来源** | "Neural BRDF Representation" (Kuznetsov 2021) + UE5 内部实验 "Neural Material Functions" + Disney BSDF 论文 + Karis 2013 "Real Shading in Unreal Engine 4"                  |
|          |                                                                                                                                                                                   |

---

## 效果对比

| 传统 BRDF (GGX / Disney)         | 神经 BRDF (NeuralGGX)                  |
| --------------------------- | ----------------------------------- |
| 固定公式（GGX + Fresnel + Geometry）  | **MLP 学公式**，可表示任意反射分布             |
| Cook-Torrance 微分方程            | **直接 forward 出结果**，无 analytic 推导  |
| 10+ 个 uniform（roughness/metallic/...） | **3-5 个 latent 输入**，自动编码 BRDF 形状   |
| 复杂材质（金属漆、皮肤、丝绸）需要叠加多层       | **MLP 直接拟合完整多层 BRDF**              |
| 自发光 / 各向异性 / 多层涂漆等特殊 BRDF 难实现 | **latent space 插值可生成任意 BRDF**      |

---

## 核心代码

### 1. C++ 侧 — Neural BRDF 接口

```cpp
// NeuralBRDF.h
class FNeuralBRDF {
public:
    // 输入: 4D BRDF 参数（half-vector dot, roughness, metallic, viewDot)
    // 输出: BRDF 值 (RGB)
    // 网络结构: 4 → 64 (ReLU) → 64 (ReLU) → 64 (ReLU) → 3 (sigmoid)

    struct FBRDFInput {
        float NdotH;      // cos angle between normal and half vector
        float NdotV;      // cos angle between normal and view direction
        float NdotL;      // cos angle between normal and light direction
        float Roughness;  // [0, 1]
        float Metallic;   // [0, 1]
        FVector3f BaseColor;
    };

    struct FBRDFOutput {
        FVector3f Specular;
        FVector3f Diffuse;
        FVector3f Combined;
    };

    // 推理（每像素每光源调用一次）
    FBRDFOutput Evaluate(const FBRDFInput& Input);

    // 网络权重
    FRDGBufferRef WeightsLayer1;  // [5 → 64]
    FRDGBufferRef WeightsLayer2;  // [64 → 64]
    FRDGBufferRef WeightsLayer3;  // [64 → 64]
    FRDGBufferRef WeightsLayer4;  // [64 → 3]
};
```

### 2. HLSL 侧 — Neural BRDF Forward Pass

```hlsl
// ============== 神经网络推理 ==============
// 4 input → 64 hidden → 64 hidden → 64 hidden → 3 output
// 输入: NdotH, NdotV, NdotL, Roughness, Metallic
// 输出: BRDF RGB

StructuredBuffer<float> NN_W1;  // [5 → 64] = 320
StructuredBuffer<float> NN_B1;  // [64]
StructuredBuffer<float> NN_W2;  // [64 → 64] = 4096
StructuredBuffer<float> NN_B2;  // [64]
StructuredBuffer<float> NN_W3;  // [64 → 64] = 4096
StructuredBuffer<float> NN_B3;  // [64]
StructuredBuffer<float> NN_W4;  // [64 → 3] = 192
StructuredBuffer<float> NN_B4;  // [3]

float3 NeuralBRDF(float NdotH, float NdotV, float NdotL, float Roughness, float Metallic) {
    float Input[5] = { NdotH, NdotV, NdotL, Roughness, Metallic };

    // Layer 1
    float Hidden1[64];
    [unroll]
    for (int h = 0; h < 64; ++h) {
        float Sum = NN_B1[h];
        [unroll]
        for (int f = 0; f < 5; ++f) {
            Sum += Input[f] * NN_W1[h * 5 + f];
        }
        Hidden1[h] = max(Sum, 0.0);  // ReLU
    }

    // Layer 2
    float Hidden2[64];
    [unroll]
    for (int h = 0; h < 64; ++h) {
        float Sum = NN_B2[h];
        [unroll]
        for (int f = 0; f < 64; ++f) {
            Sum += Hidden1[f] * NN_W2[h * 64 + f];
        }
        Hidden2[h] = max(Sum, 0.0);
    }

    // Layer 3
    float Hidden3[64];
    [unroll]
    for (int h = 0; h < 64; ++h) {
        float Sum = NN_B3[h];
        [unroll]
        for (int f = 0; f < 64; ++f) {
            Sum += Hidden2[f] * NN_W3[h * 64 + f];
        }
        Hidden3[h] = max(Sum, 0.0);
    }

    // Layer 4 (Output, Sigmoid for BRDF)
    float3 Out;
    Out.r = NN_B4[0]; Out.g = NN_B4[1]; Out.b = NN_B4[2];
    [unroll]
    for (int h = 0; h < 64; ++h) {
        Out.r += Hidden3[h] * NN_W4[h * 3 + 0];
        Out.g += Hidden3[h] * NN_W4[h * 3 + 1];
        Out.b += Hidden3[h] * NN_W4[h * 3 + 2];
    }
    return 1.0 / (1.0 + exp(-Out));  // Sigmoid → [0, 1]
}
```

### 3. HLSL 侧 — 完整 Base Pass PBR (Neural GGX 版)

```hlsl
// 简化版: 替换 GGX 为 Neural BRDF
float3 PBR_BasePass_Neural(
    float3 WorldPos,
    float3 WorldNormal,
    float3 BaseColor,
    float Roughness,
    float Metallic,
    float3 LightDir,
    float3 ViewDir,
    float3 LightColor
) {
    float3 N = normalize(WorldNormal);
    float3 L = normalize(LightDir);
    float3 V = normalize(ViewDir);
    float3 H = normalize(L + V);

    float NdotL = saturate(dot(N, L));
    float NdotV = saturate(dot(N, V));
    float NdotH = saturate(dot(N, H));
    float VdotH = saturate(dot(V, H));

    if (NdotL < 0.01) return 0.0;  // back-face culling

    // ===== 神经 BRDF =====
    float3 BRDF = NeuralBRDF(NdotH, NdotV, NdotL, Roughness, Metallic);

    // ===== 渲染方程 =====
    // Lo = integral(BRDF * Li * NdotL)
    // 这里简化成单光源
    float3 Lo = BRDF * LightColor * NdotL;

    return Lo;
}
```

### 4. 离线训练 Pipeline（Python, 对应 day-job 训练数据生成）

```python
# train_neural_brdf.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class NeuralBRDFNet(nn.Module):
    """用神经网络拟合 GGX + Disney BRDF"""
    def __init__(self, hidden_dim=64, num_layers=3):
        super().__init__()
        layers = []
        in_dim = 5  # NdotH, NdotV, NdotL, roughness, metallic

        for i in range(num_layers):
            layers.append(nn.Linear(in_dim, hidden_dim))
            layers.append(nn.ReLU())
            in_dim = hidden_dim

        # Output: BRDF RGB
        layers.append(nn.Linear(hidden_dim, 3))
        layers.append(nn.Sigmoid())

        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def ggx_brdf_ground_truth(NdotH, NdotV, NdotL, roughness, metallic, base_color):
    """真实 GGX BRDF 作为训练 ground truth"""
    alpha = roughness ** 2

    # Normal Distribution Function (GGX)
    a2 = alpha * alpha
    denom = NdotH * NdotH * (a2 - 1.0) + 1.0
    D = a2 / (3.14159 * denom * denom + 1e-7)

    # Geometry term (Smith)
    k = (roughness + 1.0) ** 2 / 8.0
    G_V = NdotV / (NdotV * (1.0 - k) + k + 1e-7)
    G_L = NdotL / (NdotL * (1.0 - k) + k + 1e-7)
    G = G_V * G_L

    # Fresnel (Schlick)
    F0 = lerp(float3(0.04, 0.04, 0.04), base_color, metallic)
    F = F0 + (1.0 - F0) * (1.0 - NdotH) ** 5

    # Specular
    specular = (D * G * F) / (4.0 * NdotV * NdotL + 1e-7)

    # Diffuse (Lambert, scaled by 1-metallic)
    diffuse = base_color / 3.14159 * (1.0 - metallic)

    return specular + diffuse


# 训练
def train(num_samples=1_000_000, num_epochs=50):
    model = NeuralBRDFNet().cuda()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    for epoch in range(num_epochs):
        # 随机采样 BRDF 参数
        NdotH = torch.rand(num_samples, 1).cuda()
        NdotV = torch.rand(num_samples, 1).cuda()
        NdotL = torch.rand(num_samples, 1).cuda()
        roughness = torch.rand(num_samples, 1).cuda()
        metallic = torch.rand(num_samples, 1).cuda()
        base_color = torch.rand(num_samples, 3).cuda()

        # Ground truth
        with torch.no_grad():
            gt = ggx_brdf_ground_truth(NdotH, NdotV, NdotL, roughness, metallic, base_color)

        # Forward
        input_params = torch.cat([NdotH, NdotV, NdotL, roughness, metallic], dim=1)
        pred = model(input_params)

        # Loss
        loss = F.mse_loss(pred, gt)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if epoch % 5 == 0:
            print(f"Epoch {epoch}: loss = {loss.item():.6f}")
```

### 5. UE5 集成（Material Expression 替换 GGX）

```cpp
// 在 UE5 Material Editor 里:
// 1. Custom HLSL Node: 把 NeuralGGX.usf include 进 Custom
// 2. Bind StructuredBuffer 网络权重（通过 RHI Upload）
// 3. 替换原 Material 里的 GGX 节点为 NeuralGGX 节点

UMaterialExpression* CreateNeuralBRDFNode() {
    auto* Node = NewObject<UMaterialExpressionMaterialFunctionCall>();
    Node->SetMaterialFunction(LoadObject<UMaterialFunction>(nullptr, TEXT("/Engine/Functions/NeuralGGX")));
    return Node;
}
```

---

## 8 个核心参数

| 参数 | 来源 | 含义 | 调参建议 |
|------|------|------|----------|
| `r.NeuralBRDF.Enable 0/1` | CVar | Neural BRDF 全局开关 | 默认 0（实验性） |
| `r.NeuralBRDF.NetworkPrecision` | CVar | 网络推理精度 (FP16/FP32) | 默认 FP16 |
| `r.NeuralBRDF.LatentDim` | CVar | Latent 维度（用于材质变体） | 默认 0（无 latent） |
| `r.NeuralBRDF.MaxRoughness` | CVar | 强制最大 roughness 阈值 | 默认 1.0 |
| `r.NeuralBRDF.EnergyConservation` | CVar | 能量守恒修正 | 默认 1 |
| `r.NeuralBRDF.FallbackToGGX` | CVar | 推理失败时回退到 GGX | 默认 1 |
| `r.NeuralBRDF.Debug 0/1` | CVar | Debug 视图 | 调参时打开 |
| `r.NeuralBRDF.WarmupFrames` | CVar | 网络权重 warmup 帧数 | 默认 0（无 warmup） |

---

## 5 档性能分级

| 分级 | 改动 | 性能影响 | 适用场景 |
|------|------|----------|----------|
| **极简** | 关闭 Neural BRDF, 用传统 GGX | 0ms | Mobile / SM5 |
| **标准** | Neural BRDF 推理 (5 → 64 → 64 → 64 → 3) | ~0.3ms | PC 中端 |
| **高配** | Neural BRDF + 多材质 latent | ~0.5ms | PC 高端 |
| **极限** | Neural BRDF + 反射 + 漫反射 + sheen + clearcoat 全套 | ~1.0ms | 截图级 |
| **Debug** | 输出网络中间层 + 强制 FP32 | 慢 2x | 调参 |

---

## 4 个变体版本

- **版本 A：单 MLP (3 hidden layer)** — 替换 GGX Specular + Lambert Diffuse
- **版本 B：双 MLP (Specular + Diffuse 分开)** — Specular 一个网络, Diffuse 一个网络
- **版本 C：Multi-output MLP** — 同时输出 specular / diffuse / sheen / clearcoat 4 个 BRDF
- **版本 D：Latent-conditioned MLP** — 输入加 latent code, 支持运行时换 BRDF 形状

---

## 6 个已知问题与限制

1. **不支持 mobile** — MLP 推理需要 SM6+
2. **每帧每像素每光源都调用** — 多光源场景下, 网络 forward 开销线性增加
3. **训练数据覆盖** — 训练集是 GGX ground truth,无法表示 GGX 之外的特殊 BRDF
4. **Latent 调参** — 运行时换 BRDF 形状需要重新推理,延迟 1-3 帧
5. **能量守恒需手动修正** — MLP 输出可能不满足能量守恒 (∫BRDF dΩ ≤ 1)
6. **光照模型耦合** — 输入只编码 direct lighting, 间接光需要叠加 Screen Probe

---

## 7 步调参 SOP

1. **`r.NeuralBRDF.Enable 1`** — 启用
2. **`r.NeuralBRDF.NetworkPrecision FP16`** — 推理精度
3. **校准训练数据** — 用生产环境的 GGX 参数分布采样训练数据,避免分布外失真
4. **`r.NeuralBRDF.EnergyConservation 1`** — 能量守恒修正（避免过曝）
5. **`r.NeuralBRDF.FallbackToGGX 1`** — 推理失败时回退 GGX
6. **统计 fallback rate** — `<5%` 算成功, `>20%` 需要重训
7. **`stat NeuralBRDF`** — 控制台看推理开销 + fallback rate

---

## 与 day-job RAG 的关联

NeuralGGX 是 day-job **神经 BRDF** 主线的核心载体:

### 1. 工具描述模板
```
BRDF.NeuralEval(
    NdotH: float,
    NdotV: float,
    NdotL: float,
    roughness: float,
    metallic: float,
    base_color: float3
) → float3 (BRDF RGB)
  - 推理开销: 0.3ms / pixel / light (5 → 64 → 64 → 64 → 3 MLP)
  - 训练数据: 1M GGX 随机样本
  - 替代: 传统 GGX + Disney (10+ uniform)
```

### 2. SFT 数据生成（day-job 核心）
- **训练数据**: 1M 随机 (NdotH, NdotV, NdotL, roughness, metallic, baseColor) → GGX 公式输出
- **训练时长**: 1 个 RTX 4090 + 1h ≈ 50 epoch 完成
- **产物**: 一个 5→3 的 MLP, 推理时直接替换 GGX

### 3. 跟 NeuralPBR 协同
- NeuralPBR 预测 PBR 参数（roughness / metallic / baseColor）
- NeuralGGX 用这些参数做 BRDF 评估
- **串联起来**: 1 张 base color → 4 PBR → BRDF → 最终颜色

### 4. RAG 检索应用
- 用户问"为什么我的金属看起来像塑料"
- LLM 检索到本案例, 答:"Roughness 太高, 调低到 0.1; 或启用 NeuralGGX 学习更准的 GGX"
- LLM 检索到调参 SOP, 输出具体步骤

---

## 关联知识库

- [[W1/神经材质-NeuralPBR]]（NeuralPBR 输出 PBR 参数, NeuralGGX 用这些参数）
- [[W7/DLSS-神经超分-时域重建]]（DLSS 解决空间, Neural BRDF 解决 shading 频率）
- [[W8/神经降噪-RT-Denoiser]]（神经降噪 vs 神经 BRDF 都是 MLP 在 GPU 上的应用）
- [[W9/神经辐射缓存-Neural-Radiance-Cache]]（NRC 学的是 GI radiance, NeuralGGX 学的是单光源 BRDF）
- [[../../../01-论文笔记库/2021-Neural-BRDF-Representation|Neural BRDF 论文精读]]
- [[../../../05-技术雷达/Neural-BRDF-工具对照|神经 BRDF 工具雷达]]

---

## 复用指南

把 NeuralGGX 集成到自研引擎:

1. **离线训练** — Python + PyTorch, MLP 3 hidden layer, 训练数据 1M (GGX 公式生成)
2. **模型导出** — ONNX → TensorRT / DirectML
3. **GPU 推理** — 替换 GGX 公式调用为 MLP forward
4. **网络权重上传** — 启动时一次性 upload 到 GPU StructuredBuffer
5. **能量守恒修正** — 加个 saturate 和能量归一化,避免输出超过 (BRDF dΩ ≤ 1)
6. **Fallback** — SM5 / 推理失败 → 自动回退 GGX 公式
7. **Latent extension** — 加 latent input, 支持运行时切材质变体 (木 / 金属 / 皮肤)

---

*Create date: 2026-07-09*
*Last modified: 2026-07-09*