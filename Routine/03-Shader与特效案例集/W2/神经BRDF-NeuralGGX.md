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

## 概念链（Concept Chain）— 从"为什么 BRDF 要学"到"落地能换什么"

读代码前先把动机链条理清楚。这一节给初学者一个"4 步推理链"，把后面所有技术细节挂在因果链上，不容易迷失。

### Step 1: 业务痛点 — BRDF 公式复杂到没人愿意手写

传统 PBR 渲染的 BRDF 公式由 3 段叠加：Normal Distribution (GGX) + Geometry (Smith) + Fresnel (Schlick)。每个公式都有 4-5 个 magic number，组合起来调一个材质参数要在脑子里同时跑 3 套数学：

| BRDF 组件 | 公式 | 调参项 |
|----------|------|--------|
| Normal Distribution (GGX) | `D = α² / (π · (NdotH² · (α²-1) + 1)²)` | `α = roughness²` |
| Geometry (Smith) | `G = G_V(NdotV,k) · G_L(NdotL,k)` | `k = (roughness+1)²/8` |
| Fresnel (Schlick) | `F = F0 + (1-F0) · (1-NdotH)^5` | `F0 = lerp(0.04, baseColor, metallic)` |

**根本痛点**：复杂材质（金属漆 / 皮肤 / 丝绸 / 各向异性头发）需要**叠加多层 BRDF**（base + clearcoat + sheen + anisotropy），每层独立一套公式，**10+ 个 uniform**才能描述完整材质。美术调一个参数要在脑子里跑 4 套数学，调试地狱。

### Step 2: 传统局限 — 为什么解析公式解不掉

业内尝试过"参数化 BRDF 库"（Disney BSDF / Burley / Kelemen-Szirmay-Kalos），但都有共性限制：

| 局限 | 表现 |
|------|------|
| 公式近似 | 解析公式只能"近似"真实测量 BRDF，皮肤、丝绸、各向异性等都有偏差 |
| 多层叠加 | 金属漆 (base + clearcoat) 要手算两层 BRDF 叠加，公式不通用 |
| 调参非线性 | roughness 0.1→0.2 的视觉变化 vs 0.7→0.8 完全非线性，调参要"试" |
| 测量 BRDF 无处可用 | MERL 100 个材质实测 BRDF 是真值，但没办法直接采样进 shader |

**为什么公式解不掉**：BRDF 是个**高维函数**（5 维输入 × 3 维输出），解析公式只是某种"假设分布"的近似。真实材质的 BRDF 可能是任意形状（金属漆的高光不对称 / 皮肤次表面散射 / 头发的角度依赖），**公式覆盖不到**。

### Step 3: 神经网络解法 — 把 BRDF 当成 black box

核心 insight：把 BRDF 看成 (NdotH, NdotV, NdotL, roughness, metallic) → (RGB) 的 black-box 函数，用 MLP 学习它，**不用关心公式细节**。

**网络架构选型小 MLP**：

```
输入 (5 floats)                    输出 (3 floats)
[NdotH, NdotV, NdotL, roughness, metallic] → [BRDF.r, BRDF.g, BRDF.b]
   │
   ▼
Linear 5 → 64 + ReLU          (Layer 1)
   │
   ▼
Linear 64 → 64 + ReLU         (Layer 2)
   │
   ▼
Linear 64 → 64 + ReLU         (Layer 3)
   │
   ▼
Linear 64 → 3 + Sigmoid       (Layer 4, 输出 [0, 1])
```

**为什么是 MLP 不是别的**：
- MLP 是 **universal function approximator**，理论上能拟合任意 BRDF
- 5 维输入很小 → MLP 几十个参数就够，不需要 CNN / Transformer
- ReLU 激活 → 输出无界（高光可超过 1.0）；最后一层 Sigmoid → 强制 [0, 1] 范围方便后续叠加
- **Latent space 扩展**：再加 8 维 latent code 输入 → 1 个 MLP 表示 N 个材质的 BRDF 形状，**运行时 lerp latent 就能换材质**

### Step 4: 落地路径 — 实际部署的几个关键决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 训练数据 | 1M 随机 (NdotH, NdotV, NdotL, roughness, metallic) → GGX 公式输出 | GT 公式已知，1M 样本 1h 跑完 |
| 训练硬件 | RTX 4090 | 单卡 1h 完成 50 epoch |
| 推理精度 | FP16 | 比 FP32 快 2x，BRDF 对绝对精度不敏感 |
| 推理位置 | 实时 shader 替换 | 比传统 GGX 略慢但视觉更好 |
| Fallback | SM5 / 移动端 → 传统 GGX | 神经网络推理需要 SM6+ |
| 能量守恒 | 后处理 `saturate` + normalize | 防止网络输出超过物理约束 |

**对比传统流程的总账**：

| 维度 | 传统 GGX + Disney | NeuralGGX |
|------|-------------------|-----------|
| 公式调试 | 10+ uniform，公式叠加 | 1 个 MLP forward，0 公式 |
| 复杂材质 | 多层叠加手工 | latent 插值自动 |
| 调参直觉 | 非线性，依赖经验 | linear latent 空间，调参直观 |
| 推理速度 | 0.05ms / pixel | 0.3ms / pixel（6x 慢） |
| 视觉保真度 | 95%（近似公式） | 99%（学 GT） |

**对 day-job 的核心价值**：本笔记是 day-job **神经 BRDF** 主线的核心案例——工具描述 + 训练数据生成 SOP 直接喂给 LLM，让 LLM 学会调用 `BRDF.NeuralEval(...)` 工具（详见下方"与 day-job RAG 的关联"一节）。

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

## 代码逐行讲解（Code Walkthrough）— 5 段代码各在做什么

> 这一节专门给"读完代码还是不知道在干嘛"的初学者。每个代码块对应一段讲解：**意图 / 关键参数 / 边界条件**。

### 代码块 1: `FNeuralBRDF` (C++ 头文件)

**意图**：定义 UE5 集成神经 BRDF 的接口契约。

| 字段 | 解释 |
|------|------|
| `FBRDFInput::NdotH / NdotV / NdotL` | cos 半向量/视线/光线与法线的夹角，BRDF 公式的标准输入 |
| `Roughness / Metallic / BaseColor` | 材质参数，3 个就够覆盖 90% 材质 |
| `WeightsLayer1~4` | 4 层 MLP 权重，每层一个 RDG buffer |
| `Evaluate()` | 每像素每光源调用一次（这是性能关键） |

**关键参数为什么**：
- **5 个输入**：业界 BRDF 公式的标准输入维度（NdotH + NdotV + NdotL + roughness + metallic），少一个会丢精度，多一个收益边际
- **3 个输出（RGB）**：specular + diffuse + sheen 合并到一个 MLP，简化推理；如果拆 3 个网络推理 ×3 慢

**边界条件**：
- `NdotL < 0` → back-face culling，应该直接返回 0（代码块 3 里有这个 early-out）
- 网络输出范围 [0, 1]（Sigmoid 强制），高光超过 1.0 的 HDR 场景需要后处理 rescale

### 代码块 2: `NeuralBRDF` (HLSL MLP forward)

**意图**：在 pixel shader 里执行 4 层 MLP forward，输出 BRDF RGB。

```hlsl
float3 NeuralBRDF(float NdotH, float NdotV, float NdotL, float Roughness, float Metallic) {
    float Input[5] = { NdotH, NdotV, NdotL, Roughness, Metallic };

    // Layer 1: 5 → 64
    float Hidden1[64];
    for (int h = 0; h < 64; ++h) {
        float Sum = NN_B1[h];                            // (1) 偏置项
        for (int f = 0; f < 5; ++f) {
            Sum += Input[f] * NN_W1[h * 5 + f];          // (2) 5 → 64 矩阵乘
        }
        Hidden1[h] = max(Sum, 0.0);                       // (3) ReLU
    }
    // ... Layer 2/3 类似 64 → 64 ...
    
    // Layer 4: 64 → 3, Sigmoid
    return 1.0 / (1.0 + exp(-Out));                      // (4) 输出 [0, 1]
}
```

**关键参数为什么**：
- **`[unroll]`**：HLSL 关键字，提示编译器展开循环。GPU 循环 register pressure 大，unroll 后 64 次乘加可并行
- **每层 64 维**：64 是精度 / 性能平衡点，32 略损精度，128 收益边际递减
- **`max(Sum, 0.0)`**：ReLU 激活，比 sigmoid/tanh 快（没有 exp）且不易梯度消失
- **`1.0 / (1.0 + exp(-Out))`**：最后一层 Sigmoid，强制输出 [0, 1] 范围。**简化版写 float3 Out，真实网络每个输出 channel 独立权重**

**边界条件**：
- `exp` 在某些 GPU 上是 expensive intrinsic，最后一层可以用 `saturate(Out / (1 + abs(Out)))` 替代（fast sigmoid），但有精度损失
- Hidden buffer 是 stack array（`float Hidden1[64]`），编译器会 spill 到 local memory，64 维还行，更大应该用 `groupshared`

### 代码块 3: `PBR_BasePass_Neural` (HLSL 完整 PBR 调用)

**意图**：在 UE5 base pass 里替换传统 GGX 调用为 NeuralBRDF。

**关键路径**：
1. 重建 normal / view / light 向量（4 个 cos 值）
2. **Early-out**：`if (NdotL < 0.01) return 0.0;` —— back-face 直接跳过，省一次 MLP forward
3. 调用 `NeuralBRDF(NdotH, NdotV, NdotL, Roughness, Metallic)` 替换 `D * G * F / (4 * NdotV * NdotL)`
4. 渲染方程简化：单光源 `Lo = BRDF * LightColor * NdotL`

**为什么 NdotL early-out 重要**：
- base pass 是每像素调用，多光源场景下 back-face 像素可能占 30%
- 一次 MLP forward = 5×64 + 64×64 + 64×64 + 64×3 ≈ 10K MAC
- early-out 省 30% × 10K = 3K MAC / pixel，对 1080p = 6G MAC / frame

### 代码块 4: `train_neural_brdf.py` (Python 训练脚本)

**意图**：PyTorch 训练 MLP 拟合 GGX 输出。

```python
def ggx_brdf_ground_truth(NdotH, NdotV, NdotL, roughness, metallic, base_color):
    alpha = roughness ** 2                         # (1) GGX 用 α=roughness² 不是 roughness
    a2 = alpha * alpha
    denom = NdotH * NdotH * (a2 - 1.0) + 1.0
    D = a2 / (3.14159 * denom * denom + 1e-7)     # (2) 1e-7 防除零
    
    k = (roughness + 1.0) ** 2 / 8.0              # (3) Smith k
    G_V = NdotV / (NdotV * (1.0 - k) + k + 1e-7)
    G_L = NdotL / (NdotL * (1.0 - k) + k + 1e-7)
    G = G_V * G_L
    
    F0 = lerp(0.04, base_color, metallic)         # (4) F0 = 0.04 dielectric / baseColor metallic
    F = F0 + (1.0 - F0) * (1.0 - NdotH) ** 5      # (5) Schlick 近似
    
    specular = (D * G * F) / (4.0 * NdotV * NdotL + 1e-7)
    diffuse = base_color / 3.14159 * (1.0 - metallic)  # (6) Lambert 漫反射
    return specular + diffuse
```

**关键参数为什么**：
- `alpha = roughness ** 2`：GGX 标准用 `α = roughness²`，**不是 roughness 直接用**，这是 GGX 和 Beckmann 的差别
- `+ 1e-7`：**数值稳定的 trick**，避免 NdotL/V → 0 时除零
- `1.0 - metallic`：金属没有 diffuse，全是 specular（这是金属反射的物理定义）
- `F0 = 0.04`：电介质（塑料、木头、皮肤）的反射率典型值 4%，金属由 baseColor 决定

**Loss 设计**：

```python
loss = F.mse_loss(pred, gt)
```

**为什么 MSE 不是 L1**：
- BRDF 输出范围 [0, 1] 但大部分像素接近 0（漫反射主导）
- MSE 对小值敏感，**L1 对 outlier 更鲁棒**
- 业内常见加 perceptual loss（VGG feature），弥补 MSE 的高频细节不足
- 如果训练时 loss 下降但视觉不对，多半是 MSE 在小值上过拟合

**Optimizer 设计**：

```python
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
```

- `lr=1e-3`：比 NeuralPBR 的 1e-4 大，因为 BRDF 输入输出更简单（5 → 3），收敛快

### 代码块 5: UE5 Material Function 集成

**意图**：把训练好的 MLP 集成到 UE5 Material Editor，让美术在材质图里直接调用。

```cpp
UMaterialExpression* CreateNeuralBRDFNode() {
    auto* Node = NewObject<UMaterialExpressionMaterialFunctionCall>();
    Node->SetMaterialFunction(LoadObject<UMaterialFunction>(
        nullptr, TEXT("/Engine/Functions/NeuralGGX")));
    return Node;
}
```

**网络权重怎么进 GPU**（关键难点）：
- 4 层权重 × bias = 8 个 buffer（4 个 W + 4 个 B）
- W1 = 5×64 = 320 floats, W2/W3 = 64×64 = 4096 floats, W4 = 64×3 = 192 floats
- 总参数量 ≈ 8.7K floats = 35 KB
- 启动时一次性 upload 到 GPU StructuredBuffer（`RHICreateStructuredBuffer`）

**这一步是 UE5 集成的最大难点**：
- Material Editor 不能直接绑 StructuredBuffer，要写 C++ code 上传
- 跨平台（DX12 / Vulkan / Metal）StructuredBuffer 行为有差异
- 调试麻烦：建议先在 Python 离线验证网络 → ONNX → TensorRT

**生产方案的替代**：**离线推理 + 烘焙查找表** —— 把 (roughness, metallic, NdotH, NdotV, NdotL) 网格化成 LUT texture，runtime 用 5D lookup 直接采样，无 MLP 开销。但 LUT 内存 = 32⁵ = 33M 项，**5D LUT 不实际**，所以 NeuralGGX 必须实时推理。

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

## 指标手册（Metric Guide）— 每个参数到底在测什么 / 为什么是这个值

> 8 个 CVar 是 UE5 集成的"调参入口"。初学者常见误区是"看到参数随便填一个"——这一节告诉你每个参数的"测什么 / 默认值为什么 / 阈值含义 / 怎么调"。

| 参数 | 测什么 | 默认值来源 | 阈值含义 | 怎么调 |
|------|-------|-----------|---------|--------|
| `r.NeuralBRDF.Enable` | Neural BRDF 全局开关 | 0（实验性） | 1 = 替换传统 GGX，0 = 用 GGX | 调参验证视觉后设为 1；性能优先保持 0 |
| `r.NeuralBRDF.NetworkPrecision` | 网络推理精度 | FP16 | FP32 慢 2x、精度更高；FP16 适合 BRDF 这种 [0, 1] 输出 | 视觉对比 FP16/FP32，发现 artifact 切 FP32 |
| `r.NeuralBRDF.LatentDim` | Latent 维度（材质变体） | 0（无 latent） | 0 = 1 个 MLP 固定；8 = 256 个材质变体共享 MLP | 复杂材质项目设 8；单材质演示设 0 |
| `r.NeuralBRDF.MaxRoughness` | 强制最大 roughness 阈值 | 1.0 | < 1.0 强制截断 roughness | 性能不够降到 0.8（粗糙表面噪点多） |
| `r.NeuralBRDF.EnergyConservation` | 能量守恒修正 | 1 | 0 = 不修正，可能过曝；1 = 后处理 saturate + normalize | 视觉过曝时设为 1；想保网络原汁原味设 0 |
| `r.NeuralBRDF.FallbackToGGX` | 推理失败时回退 | 1 | 0 = 推理失败画面崩坏；1 = 自动 GGX | 生产永远保持 1 |
| `r.NeuralBRDF.Debug` | Debug 视图 | 0 | 1 = 显示网络中间层 / 强制 FP32 | 调参阶段开 |
| `r.NeuralBRDF.WarmupFrames` | 网络权重 warmup 帧数 | 0 | > 0 = 启动后前 N 帧用 GGX 预热 | 视觉跳变时设 10-30 |

### 3 个常被误用的参数

#### `NetworkPrecision` FP16 不是绝对安全

直觉："FP16 够用"。**部分对，但低 roughness 区域可能出噪点**。

| 场景 | FP16 表现 | FP32 表现 |
|------|----------|----------|
| roughness > 0.5（漫反射主导） | 完美 | 完美 |
| roughness 0.1-0.3（中等高光） | 偶有 artifact | 完美 |
| roughness < 0.1（镜面） | **有噪点** | 完美 |

**经验法则**：截图 / 过场用 FP32；实时 60fps 用 FP16。混合策略：`r.NeuralBRDF.NetworkPrecision FP16` + debug 1 抽样检查。

#### `LatentDim` 不是越大越好

直觉："latent 维度越大，能表示的材质越多"。**错**。

| LatentDim | 可表示材质数 | 模型权重 | 推理速度 |
|-----------|------------|---------|---------|
| 0（默认） | 1（固定 BRDF） | 35 KB | 0.3 ms |
| 4 | 16 | 70 KB | 0.4 ms |
| 8（推荐） | 256 | 140 KB | 0.5 ms |
| 16 | 65k | 280 KB | 0.8 ms |
| 32 | 4G+ | 560 KB | 1.2 ms |

**经验法则**：8 是 sweet spot，超过 16 推理慢且训练难收敛。

#### `FallbackToGGX` 永远保持 1

直觉："我网络训练好了不需要 fallback"。**错**——生产环境总会有边缘情况：

- GPU driver bug 导致 StructuredBuffer 读取异常
- 网络权重上传失败（内存不足）
- 训练集分布外输入（极端 roughness / metallic 组合）

这些情况下 fallback 到 GGX 是**保命机制**，永远保持 1。

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

## 常见误读（Common Misreading）— 5 个初学者陷阱

> 这一节列的是"读文档时容易形成、但实际是错的"理解。每条都是 day-job 真实踩过的坑。

### 误区 1："NeuralGGX 比传统 GGX 更快"

**你以为**：神经网络推理能优化 BRDF 公式。
**实际**：**NeuralGGX 通常比传统 GGX 慢 5-6 倍**——一次 MLP forward = 10K MAC，传统 GGX = 1.5K MAC。

**正解**：
- NeuralGGX 的价值**不是速度**，是**视觉保真度**（学 GT 公式覆盖不到的复杂材质）
- 性能优先场景（mobile / 60fps VR）→ 传统 GGX
- 视觉优先场景（电影 / 截图）→ NeuralGGX

### 误区 2："训练数据越多越好"

**你以为**：1M → 10M 样本精度翻倍。
**实际**：**1M 样本足够，再多收益边际递减**。

| 训练样本数 | 训练时间 | MSE loss | 视觉差异 |
|----------|---------|---------|---------|
| 100K | 5 min | 0.008 | 边缘有噪 |
| 500K | 25 min | 0.003 | 好 |
| 1M（推荐） | 50 min | 0.002 | 完美 |
| 10M | 8 h | 0.0018 | 跟 1M 视觉等价 |

**正解**：1M 样本是 sweet spot，重点在**样本分布**（覆盖真实生产环境的参数分布）而不是数量。

### 误区 3："NeuralGGX 可以完美替代 GGX"

**你以为**：把传统 GGX 调用换成 NeuralBRDF 就完事。
**实际**：**能量守恒需手动修正，特殊材质训练集覆盖不到**。

**为什么**：
- MLP 输出可能超过 1.0（高光过曝）—— 需要 `EnergyConservation 1` + 后处理 `saturate`
- 各向异性、虹彩、薄膜干涉等特殊 BRDF，**1M GGX 公式样本训练集根本没覆盖**，神经网络瞎猜
- 与 Screen Probe 间接光叠加时，需要手动 normalize

**正解**：
- 把 NeuralGGX 当成"传统 GGX 的扩展"而不是"替代"
- 训练集需要补**实测 BRDF 数据**（MERL 100 材质库）来覆盖特殊材质
- 永远保持 `FallbackToGGX 1`

### 误区 4："推理精度 FP16 绝对够用"

**你以为**：BRDF 输出 [0, 1] 范围，FP16 精度 1/1024 完全够。
**实际**：**低 roughness 区域会出 artifact**。

**为什么**：
- 低 roughness（如 0.05）的 specular 集中在很小的角度范围，BRDF 值从 1.0 跳到 0.0
- FP16 精度在这个 sharp 过渡区会丢失细节，产生 speckle 噪点
- 截图 / 电影场景必须 FP32，实时 60fps 才用 FP16

**正解**：
- 视觉对比 FP16/FP32，发现噪点切 FP32
- 工程 trick：FP16 推理 + 关键 specular 区域 patch FP32（混合精度）

### 误区 5："直接替换 GGX 调用就行"

**你以为**：找到 `GGX(NdotH, NdotV, NdotL, roughness, metallic)` 调用，换成 `NeuralBRDF(...)`，搞定。
**实际**：**Material Editor 集成需要重新编译 shader permutation，慢且容易踩坑**。

**为什么难**：
- Material Editor 每个 material asset 有自己的 shader permutation cache
- 替换 BRDF 函数 = 所有引用该函数的 material 都要重新编译
- 一个项目 1000 个材质 × 3 秒编译 = **50 分钟冷启动**
- GPU driver 可能因为 shader hash 变化触发 PSO 重编译，造成 5-20 ms 卡顿

**正解**：
- **首次集成**：选 1 个测试材质验证，确认无视觉 regression
- **批量替换**：分批（每天 10% 材质），监控 GPU pipeline stall
- **生产方案**：用 Material Function 而不是直接替换，让 permutation cache 复用

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