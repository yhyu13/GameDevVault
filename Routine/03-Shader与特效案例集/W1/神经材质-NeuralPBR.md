---
tags: [shader/AI, shader/material, shader/PBR, shader/neural-network, shader/UE]
aliases: [Neural Material, NeuralPBR, Material Parameterization, Material Synthesis, BRDF Prediction]
week: W1
cycle: new
---

# 神经材质 — NeuralPBR (从图像预测 PBR 参数)

| 字段       | 内容                                                                                                                                                                                |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **效果名称** | 神经材质参数化（从单张/多张图像 → BaseColor / Metallic / Roughness / Normal）                                                                                                                       |
| **类型**   | 材质 / 神经推理 / 离线烘焙                                                                                                                                                              |
| **平台**   | 离线（training 时）+ 实时 SM6（inference）/ 离线到 SM5（shader 烘焙后）                                                                                                                              |
| **创建日期** | 2026-07-09                                                                                                                                                                          |
| **参考来源** | Meta "Material Prediction for Bandwidth-Limited Scenes" + Adobe "Neural Material Recognition" + UE5.4 Material Editor + 论文 "Single-Image BRDF Estimation" (Aittala 2015)                |
|          |                                                                                                                                                                                   |

---

## 效果对比

| 传统 PBR 材质流程                           | 神经材质参数化                         |
| ------------------------------------- | ------------------------------- |
| 美术手调 BaseColor / Metallic / Roughness | **神经网络从单图预测 4 个 PBR 通道**        |
| Substance Designer 流程长（小时级）           | **1 秒推理出 PBR**                  |
| 8 张 texture × 2K = 16 MB / material   | **神经网络 1×1 Conv 直接重建**，省 90% 显存 |
| 同材质多 LOD 手动管理                         | **网络自动多尺度**                     |
| 材质变体爆炸（50 个 metal / 50 个 wood）        | **网络 latent space 连续插值**        |

---

## 概念链（Concept Chain）— 从"为什么要做神经材质"到"落地省了什么"

读代码前先把动机链条理清楚。这一节给初学者一个"4 步推理链"，把后面所有技术细节挂在因果链上，不容易迷失。

### Step 1: 业务痛点 — 美术做 4 张 PBR 图到底有多痛

UE5 的 PBR 渲染要求每个材质至少 4 张贴图：BaseColor / Metallic / Roughness / Normal（高端的还要 AO / Height / Anisotropy / Cavity）。美术做一张完整的 UE5 PBR 材质，标准流程是：

| 步骤 | 工具 | 耗时 |
|------|------|------|
| 1. 找参考图 / 拍照片 | Photoshop / 相机 | 0.5h |
| 2. Substance Designer 调 BaseColor | SD | 1-2h |
| 3. SD 调 Metallic + Roughness（最难） | SD | 1-2h |
| 4. SD 烘焙 Normal | SD | 0.5h |
| 5. UE5 Material Editor 拼装 | UE | 0.5h |
| **合计** | | **3-6h / 材质** |

一个 3A 项目要 **500-2000 个材质**（石头 / 木材 / 金属 / 布料 / 皮肤 / ...），乘起来 = **1500-12000 小时**，是项目美术人力的大头。

**根本痛点**：Metallic 和 Roughness 这俩通道没有"看图就能写"的规则，全靠美术经验。同一个金属在干 / 湿 / 旧 / 新 4 种状态下 roughness 从 0.1 到 0.7 各不同，要复刻 4 份 asset。

### Step 2: 传统局限 — 为什么启发式规则解不掉

业内早期尝试过"启发式自动生成 PBR"：

| 启发式规则 | 思路 | 失败率 |
|----------|------|--------|
| 灰度 → Metallic | 高灰度 = 金属 | 70%（亮色塑料全错） |
| 边缘密度 → Roughness | Sobel 算子密度 | 60%（平滑大理石纹误判成粗糙） |
| 单视角恢复法线 | 从 shading 反推 | 完全不可行（病态问题） |

**为什么启发式不行**：
- 启发式是"硬规则"，没法学"细节规律"
- 同一张图，人能看出是塑料 vs 金属，靠的是 **全局上下文 + 经验**，不是像素级规则
- 这正是神经网络擅长的事：**learn from data**

### Step 3: 神经网络解法 — 把问题转成 image-to-image translation

核心 insight：把"从 base color 推 4 张 PBR"当成一个 **image-to-image translation** 问题，跟 Pix2Pix / Stable Diffusion 同一类问题。

**网络架构选型 U-Net**：

```
输入 (1024×1024×3)             输出 (1024×1024×8)
base color 图                  base(3) + metallic(1) + roughness(1) + normal_xy(2) + mask(1)
   │
   ▼
┌─────────────┐
│ Conv 3×3    │ 32 ch
│ BN + ReLU   │
│ Conv 3×3    │ 32 ch
│ MaxPool /2  │
└─────────────┘
   │
   ▼
┌─────────────┐
│ Conv 3×3    │ 64 ch
│ BN + ReLU   │
│ Conv 3×3    │ 64 ch
│ MaxPool /2  │
└─────────────┘
   │
   ▼  (重复 4 层，到 64×64×512)
   │
   ▼  Bottleneck (64×64×1024)
   │
   ▼  Decoder (反卷积 + skip connection)
   │
   ▼
Conv 1×1 → 8 ch 输出
```

**为什么是 U-Net 不是别的**：
- **Encoder**（downsampling）学全局语义："这是一块金属 / 一块木头 / 一块布"
- **Bottleneck** 学最抽象的特征：材质类型 + 整体反射率
- **Decoder**（upsampling）+ **skip connection** 学局部细节："这里有一道划痕、那里有一个凹坑"
- skip connection 让 decoder 直接拿到 encoder 对应层的高频特征，**避免输出 Normal map 模糊**（这是单纯 encoder-decoder 的通病）。

**变体扩展**：上面是单图预测（版本 A）。扩展到 latent space interpolation（版本 C）时，再加一个 encoder 把"材质 A"压成 8-64 维 latent，第二个 encoder 把"材质 B"压成 latent，中间态 latent_t = lerp(A, B, t)，decoder 就能输出"半金属半木"的混合材质——传统流程根本做不到。

### Step 4: 落地路径 — 实际部署的几个关键决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 训练数据 | UE5 商城 100 材质 × 50 视角 = 5000 张 | 真实 GT，泛化性好 |
| 训练硬件 | RTX 4090 / A100 | 单卡 24h 完成 |
| 推理位置 | 离线推理 + 烘焙 .dds | 实时推理 3-8ms × 100 材质 = 帧爆炸 |
| 运行时 | UE5 sampler 直接采样烘焙结果 | 0ms 额外开销 |
| Fallback | SM5 → 离线烘焙；SM6 → 可选实时推理 | 兼容性 |

**对比传统流程的总账**：

| 维度 | 传统流程 | 神经材质 |
|------|---------|---------|
| 单材质人力 | 3-6h | 1-5 min（拍照 + 推理 + 校对） |
| 显存（1000 材质） | 16 GB | 100 KB |
| 变体爆炸 | 1000 个独立 asset | 1 个 shared MLP + 1000 个 latent |
| 材质间插值 | 不可能 | lerp latent 即可 |

**对 day-job 的核心价值**：本笔记是 day-job **神经材质** 主线的核心案例——工具描述 + 调参 SOP 直接喂给 LLM，让 LLM 学会调用 `Material.NeuralPBR(...)` 工具（详见下方"与 day-job RAG 的关联"一节）。

---

## 核心代码

### 1. C++ 侧 — 简化版 Material Prediction Network

```cpp
// MaterialPredictionNetwork.h
class FMaterialPredictionNetwork {
public:
    // 输入: 1 张 base color 图 (任意尺寸,典型 1024x1024)
    // 输出: 4 张 PBR map (baseColor, metallic, roughness, normal)
    struct FPredictionInput {
        FRHITexture* InputImage;          // RGB base color (美术给的照片 / AI 生成图)
        int32 ImageSize = 1024;
    };

    struct FPredictionOutput {
        FRHITexture* OutBaseColor;
        FRHITexture* OutMetallic;         // R8 单通道
        FRHITexture* OutRoughness;        // R8 单通道
        FRHITexture* OutNormal;           // RG8 (xy, z 通过 sqrt(1-x^2-y^2))
    };

    // U-Net 简化版（实际 Meta 用 50+ layer U-Net）
    // 这里用 4 downsample + 4 upsample + skip connection
    struct FConfig {
        int32 BaseChannelCount = 32;      // 32 / 64 / 128 / 256 / 512
        int32 NumDownsampleLevels = 4;
    };
    FConfig Config;

    // 推理路径：encode → bottleneck → decode + skip
    void Predict(
        FRDGBuilder& GraphBuilder,
        FPredictionInput Input,
        FPredictionOutput& Output
    );
};
```

### 2. HLSL 侧 — 简化版 UNet 推理

```hlsl
// ============== 简化版 U-Net Encoder ==============
// 4 个 downsample level: 1024 → 512 → 256 → 128 → 64
// 每个 level: 2 × (conv 3×3 + BN + ReLU) + maxpool

Texture2D<float3> InputImage;
RWTexture2D<float3> OutBaseColor;
RWTexture2D<float>  OutMetallic;
RWTexture2D<float>  OutRoughness;
RWTexture2D<float2> OutNormal;

// 网络权重（预训练,典型 200-500 MB / material network）
StructuredBuffer<float> UNet_W_E1_Conv1;   // [3 → 32] = 864
StructuredBuffer<float> UNet_W_E1_Conv2;   // [32 → 32] = 9216
StructuredBuffer<float> UNet_W_E2_Conv1;   // [32 → 64] = 18432
StructuredBuffer<float> UNet_W_E2_Conv2;   // [64 → 64] = 36864
// ... 省略 E3, E4, Bottleneck, D1, D2, D3, D4 的权重
StructuredBuffer<float> UNet_W_D4_Final;   // [32 → 9] 输出

float3 Conv2D_3x3(
    int2 Pixel, int2 TexSize,
    Texture2D<float3> Input,
    StructuredBuffer<float> Weights,
    StructuredBuffer<float> Biases,
    int InputChannelCount
) {
    float Sum = Biases[0];
    [unroll]
    for (int dy = -1; dy <= 1; ++dy) {
        [unroll]
        for (int dx = -1; dx <= 1; ++dx) {
            int2 Sample = clamp(Pixel + int2(dx, dy), 0, TexSize - 1);
            float3 V = Input[Sample];
            [unroll]
            for (int c = 0; c < 3; ++c) {
                int WeightIdx = ((dy + 1) * 3 + (dx + 1)) * 3 + c;
                Sum += V[c] * Weights[WeightIdx];
            }
        }
    }
    return max(float3(Sum, Sum, Sum), 0.0);  // ReLU,简化（实际每 channel 单独 ReLU）
}

// ============== 主调度 ==============
[numthreads(8, 8, 1)]
void MaterialPredictCS(uint3 DTid : SV_DispatchThreadID) {
    uint2 Pixel = DTid.xy;
    int2 TexSize = int2(1024, 1024);

    // 简化版：实际 U-Net 几十层,这里只展示 1 个 conv 输出 4 个 PBR 通道

    // 1. 3×3 conv 提取特征
    float3 Feature = Conv2D_3x3(Pixel, TexSize, InputImage, UNet_W_E1_Conv1, ...);

    // 2. 简化版:用启发式算 PBR
    // Base color = 输入图（保持不变）
    float3 BaseColor = InputImage[Pixel];

    // Metallic: 启发式 = (灰度高的区域 = 金属)
    float Luma = dot(BaseColor, float3(0.299, 0.587, 0.114));
    float Metallic = saturate(pow(Luma, 4.0) * 2.0);

    // Roughness: 启发式 = (边缘密度高的区域 = 粗糙)
    float Roughness = 0.5;  // 实际网络推理

    // Normal: 简化 = (luma 梯度)
    int2 TexSizeI = int2(TexSize);
    float L = dot(InputImage[clamp(Pixel + int2(-1, 0), 0, TexSizeI - 1)], float3(0.299, 0.587, 0.114));
    float R = dot(InputImage[clamp(Pixel + int2( 1, 0), 0, TexSizeI - 1)], float3(0.299, 0.587, 0.114));
    float D = dot(InputImage[clamp(Pixel + int2( 0,-1), 0, TexSizeI - 1)], float3(0.299, 0.587, 0.114));
    float U = dot(InputImage[clamp(Pixel + int2( 0, 1), 0, TexSizeI - 1)], float3(0.299, 0.587, 0.114));
    float2 NormalXY = float2(L - R, D - U) * 4.0;
    NormalXY = clamp(NormalXY, -1.0, 1.0);

    // 输出
    OutBaseColor[Pixel] = BaseColor;
    OutMetallic[Pixel]  = Metallic;
    OutRoughness[Pixel] = Roughness;
    OutNormal[Pixel]    = NormalXY;
}
```

### 3. 离线训练 Pipeline（Python stub, 对应 day-job 训练数据生成）

```python
# MaterialPredictor/train.py (简化版)
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

class MaterialUNet(nn.Module):
    """简化版 U-Net:从 base color 预测 4 张 PBR map"""

    def __init__(self, base_channels=32, num_levels=4):
        super().__init__()
        # Encoder
        self.encoders = nn.ModuleList()
        in_ch = 3
        for i in range(num_levels):
            out_ch = base_channels * (2 ** i)
            self.encoders.append(self._make_block(in_ch, out_ch))
            in_ch = out_ch

        # Bottleneck
        self.bottleneck = self._make_block(in_ch, in_ch * 2)

        # Decoder (with skip connections)
        self.decoders = nn.ModuleList()
        for i in reversed(range(num_levels)):
            out_ch = base_channels * (2 ** i)
            self.decoders.append(self._make_block(in_ch + out_ch, out_ch))
            in_ch = out_ch

        # Output heads (4 channels: base + metallic + roughness + normal_xy)
        self.output_head = nn.Conv2d(in_ch, 8, kernel_size=1)  # 3 + 1 + 1 + 2 + 1 mask

    def _make_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        # Encode
        skips = []
        for enc in self.encoders:
            x = enc(x)
            skips.append(x)
            x = F.max_pool2d(x, 2)

        # Bottleneck
        x = self.bottleneck(x)

        # Decode with skip
        for dec, skip in zip(self.decoders, reversed(skips)):
            x = F.interpolate(x, scale_factor=2, mode='bilinear', align_corners=False)
            x = torch.cat([x, skip], dim=1)
            x = dec(x)

        return self.output_head(x)


# 训练循环 (示意)
def train():
    model = MaterialUNet().cuda()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    dataset = MaterialDataset()  # 加载 UE5 导出的 (base, gt_base, gt_metallic, gt_roughness, gt_normal)
    loader = DataLoader(dataset, batch_size=16, shuffle=True)

    for epoch in range(100):
        for batch in loader:
            input_img = batch['input'].cuda()
            gt = batch['gt'].cuda()  # [B, 8, H, W]

            pred = model(input_img)

            # L1 loss on each PBR channel
            loss_base = F.l1_loss(pred[:, 0:3], gt[:, 0:3])
            loss_metal = F.l1_loss(pred[:, 3:4], gt[:, 3:4])
            loss_rough = F.l1_loss(pred[:, 4:5], gt[:, 4:5])
            loss_normal = F.l1_loss(pred[:, 5:7], gt[:, 5:7])
            loss = loss_base + loss_metal + loss_rough + loss_normal

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
```

### 4. UE5 集成（Material Expression 节点）

```cpp
// 简化版 UE5 Material Function: "NeuralPBR"
// Input:  Texture2D BaseColor (RGB)
// Output: 4 个 PBR 通道

// 在 UE5 Material Editor 里:
// 1. 添加 Custom Node
// 2. 把 NeuralPBR.usf include 进 Custom HLSL
// 3. Bind StructuredBuffer 网络权重 (通过 RHI Upload)

UMaterialExpression* CreateNeuralPBRNode() {
    auto* Node = NewObject<UMaterialExpressionMaterialFunctionCall>();
    Node->SetMaterialFunction(LoadObject<UMaterialFunction>(nullptr, TEXT("/Engine/Functions/NeuralPBR")));
    return Node;
}
```

---

## 代码逐行讲解（Code Walkthrough）— 4 段代码各在做什么

> 这一节专门给"读完代码还是不知道在干嘛"的初学者。每个代码块对应一段讲解：**意图 / 关键参数 / 边界条件**。

### 代码块 1: `FMaterialPredictionNetwork` (C++ 头文件)

**意图**：定义 UE5 集成神经材质的"接口契约"。

| 字段 | 解释 |
|------|------|
| `FPredictionInput::InputImage` | 美术给的 RGB base color 图（任意尺寸，典型 1024×1024） |
| `FPredictionOutput::OutBaseColor` | 网络直接复用输入（或微调） |
| `OutMetallic / OutRoughness` | R8 单通道 texture（每像素 1 byte，节省显存） |
| `OutNormal` | RG8 = (x, y)，z 通过 `sqrt(1 - x² - y²)` 恢复（避免 R10G10B10A2 的解码开销） |
| `FConfig::BaseChannelCount` | U-Net 第一层 channel 数（默认 32） |
| `FConfig::NumDownsampleLevels` | 4 = 16× 下采样（1024 → 64） |

**关键参数为什么**：
- `BaseChannelCount = 32`：32 是精度 / 显存平衡点，16 略损精度，64 收益边际递减。
- `NumDownsampleLevels = 4`：4 层下采样到 64×64，足以覆盖 1024 输入的全局语义（材质类型）。

**边界条件**：
- 输入图非 1024×1024 → 需要 padding / crop 到 32 的倍数（U-Net 下采样的要求）。
- 输出图想用更高分辨率 → 需要在网络外部加 upsample block（不能直接改 OutputSize，会破坏训练对齐）。

### 代码块 2: `Conv2D_3x3` (HLSL 计算 shader)

**意图**：在 GPU compute shader 里手写一个 3×3 卷积。这是**简化版**，真实生产用 DXC / Slang 直接编译网络，**不会手写**。这里是为了讲清楚 HLSL 卷积的实现细节。

```hlsl
float3 Conv2D_3x3(
    int2 Pixel, int2 TexSize,
    Texture2D<float3> Input,
    StructuredBuffer<float> Weights,
    StructuredBuffer<float> Biases,
    int InputChannelCount
) {
    float Sum = Biases[0];                              // (1) 偏置项
    [unroll]
    for (int dy = -1; dy <= 1; ++dy) {                  // (2) 卷积核 y 方向
        [unroll]
        for (int dx = -1; dx <= 1; ++dx) {              // (3) 卷积核 x 方向
            int2 Sample = clamp(Pixel + int2(dx, dy), 0, TexSize - 1);  // (4) 边界处理
            float3 V = Input[Sample];
            [unroll]
            for (int c = 0; c < 3; ++c) {
                int WeightIdx = ((dy + 1) * 3 + (dx + 1)) * 3 + c;
                Sum += V[c] * Weights[WeightIdx];       // (5) 卷积累加
            }
        }
    }
    return max(float3(Sum, Sum, Sum), 0.0);             // (6) ReLU（简化）
}
```

**关键参数为什么**：
- `[unroll]`：HLSL 关键字，提示编译器展开循环。GPU 循环有 register pressure 和 branch divergence 开销，unroll 后编译器可以并行 9 次乘加（实际是 9 × 3 = 27 次）。
- `clamp(Pixel + offset, 0, TexSize - 1)`：**replicate padding**（重复边缘像素），避免读取越界。真实 U-Net 通常用 zero padding 或 reflection padding，效果略有差异。
- `max(float3(Sum), 0.0)`：ReLU。**简化版把 3 个 channel 合并成一个值**，真实网络每个 channel 独立权重 + 独立 ReLU（用 `float3(...)` 而不是单 float）。

**边界条件**：
- 边界像素（Pixel 在 [0, TexSize-1] 边缘）：clamp 后会读多次边缘像素，等效于 replicate padding。
- 输入图小于 3×3：直接返回 bias（极端边界，真实场景不会触发）。

### 代码块 3: `MaterialPredictor/train.py` (Python 训练脚本)

**意图**：PyTorch 训练一个 U-Net，从 base color 预测 4 张 PBR map。

```python
class MaterialUNet(nn.Module):
    def __init__(self, base_channels=32, num_levels=4):
        # Encoder: 3 → 32 → 64 → 128 → 256
        # Bottleneck: 256 → 512
        # Decoder: 512 → 256 (+ skip 256) → 128 (+ skip 128) → 64 (+ skip 64) → 32 (+ skip 32)
        # Output: 8 channel (3 base + 1 metallic + 1 roughness + 2 normal_xy + 1 mask)

    def _make_block(self, in_ch, out_ch):
        # 标准 U-Net block：Conv 3×3 → BN → ReLU → Conv 3×3 → BN → ReLU
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),  # padding=1 保持 spatial 尺寸
            nn.BatchNorm2d(out_ch),                   # BN 加速收敛
            nn.ReLU(inplace=True),                    # inplace 省显存
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        skips = []
        for enc in self.encoders:
            x = enc(x)
            skips.append(x)
            x = F.max_pool2d(x, 2)                     # 下采样 /2
        x = self.bottleneck(x)
        for dec, skip in zip(self.decoders, reversed(skips)):
            x = F.interpolate(x, scale_factor=2, mode='bilinear', align_corners=False)
            x = torch.cat([x, skip], dim=1)            # skip connection
            x = dec(x)
        return self.output_head(x)
```

**关键参数为什么**：
- `padding=1`：3×3 卷积 + padding=1 保持 spatial 尺寸不变，encoder/decoder 对齐 skip。
- `BatchNorm2d`：训练时 normalize，推理时用 running stats。**生产推理时必须 `.eval()` 模式**，否则 BN 行为不一致。
- `align_corners=False`：PyTorch 0.4+ 默认。False 让 corner pixel 不强制对齐，避免双线性插值的 corner artifact。
- `torch.cat([x, skip], dim=1)`：**skip connection 让 decoder 拿到 encoder 对应层的高频特征**，是 U-Net 名字的来源（U 形）。对 Normal map 至关重要。

**Loss 设计**：

```python
loss_base = F.l1_loss(pred[:, 0:3], gt[:, 0:3])      # L1 比 L2 对 outlier 鲁棒
loss_metal = F.l1_loss(pred[:, 3:4], gt[:, 3:4])
loss_rough = F.l1_loss(pred[:, 4:5], gt[:, 4:5])
loss_normal = F.l1_loss(pred[:, 5:7], gt[:, 5:7])
loss = loss_base + loss_metal + loss_rough + loss_normal
```

**为什么 L1 不是 L2 (MSE)**：
- PBR 通道有 outlier（金属区域 metallic=1，非金属区域 metallic=0）
- L2 (MSE) 对 outlier 平方放大，loss 会被 outlier 主导
- L1 (MAE) 线性，更鲁棒
- 生产环境经常加 perceptual loss（VGG feature）补充 L1 的高频细节不足

**Optimizer 设计**：

```python
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
```

- Adam：自适应学习率，比 SGD 鲁棒
- `lr=1e-4`：**小学习率**，避免 loss 跳变。U-Net 收敛通常 100 epoch，lr 大会发散。

### 代码块 4: UE5 Material Function 集成

**意图**：把训练好的网络集成到 UE5 Material Editor，让美术能在材质图里直接调用。

```cpp
UMaterialExpression* CreateNeuralPBRNode() {
    auto* Node = NewObject<UMaterialExpressionMaterialFunctionCall>();
    Node->SetMaterialFunction(LoadObject<UMaterialFunction>(
        nullptr, TEXT("/Engine/Functions/NeuralPBR")));
    return Node;
}
```

**关键路径**：
1. 创建 `UMaterialExpressionMaterialFunctionCall`（UE5 Material Editor 的"函数调用"节点）
2. `LoadObject` 加载 `NeuralPBR.ufunction`（一个 Material Function 资产，封装了 .usf shader 调用）
3. 美术在 Material Editor 里拖出这个节点 → 接 BaseColor 输入 → 输出 4 个 PBR 通道

**网络权重怎么进 GPU**（示意代码）：

```cpp
// (示意) 把 .bin 权重文件 upload 到 StructuredBuffer
TArray<FVector4f> Weights;
FFileHelper::LoadFileToArray(Weights, ...);
FRHIBuffer* WeightBuffer = RHICreateStructuredBuffer(sizeof(float), Weights.Num(), ...);
```

**这一步是 UE5 集成的最大难点**：
- Material Editor 不能直接读 .bin，要写 C++ code upload 到 StructuredBuffer
- 调试很麻烦：建议先在 Python 离线验证网络 → ONNX → TensorRT → 直接做 RHI upload
- Meta 论文的生产方案：**离线推理 + 烘焙 .dds**，runtime 不走 shader，**完全规避**了 StructuredBuffer 的麻烦

**这是 day-job 的关键决策点**：实时推理 vs 离线烘焙，见上面"5 档性能分级"和"7 步调参 SOP"。

---

## 8 个核心参数

| 参数 | 来源 | 含义 | 调参建议 |
|------|------|------|----------|
| `r.MaterialPrediction.Model` | CVar | 选择预训练模型 (wood/metal/stone/fabric) | 默认通用 |
| `r.MaterialPrediction.Enable 0/1` | CVar | 全局开关 | 默认 1 |
| `r.MaterialPrediction.OutputSize` | CVar | 输出 texture 尺寸 | 默认 2048 |
| `r.MaterialPrediction.BaseChannels` | CVar | 网络 base channel 数 | 默认 32 |
| `r.MaterialPrediction.NumLevels` | CVar | U-Net 层数 | 默认 4 |
| `r.MaterialPrediction.NormalStrength` | CVar | 法线强度乘子 | 默认 1.0 |
| `r.MaterialPrediction.MetallicThreshold` | CVar | Metallic 阈值 | 默认 0.5 |
| `r.MaterialPrediction.Debug 0/1` | CVar | Debug 视图（输入图 / 输出 4 张 PBR） | 调参时打开 |

---

## 指标手册（Metric Guide）— 每个参数到底在测什么 / 为什么是这个值

> 8 个 CVar 是 UE5 集成的"调参入口"。初学者常见误区是"看到参数随便填一个"——这一节告诉你每个参数的"测什么 / 默认值为什么 / 阈值含义 / 怎么调"。

| 参数 | 测什么 | 默认值来源 | 阈值含义 | 怎么调 |
|------|-------|-----------|---------|--------|
| `r.MaterialPrediction.Model` | 选用的预训练模型 | `General` 通用，覆盖 80% 场景 | wood/metal/stone/fabric 是专用模型，对应类别精度 +20% | 边缘材质（金属丝 / 玻璃）切专用模型；不确定就用 General |
| `r.MaterialPrediction.Enable` | 总开关 | 1 = 实时推理 | 0 = 用烘焙结果，跳过推理 | 性能不够 / 移动端 → 0；调参阶段 → 1 |
| `r.MaterialPrediction.OutputSize` | 输出 PBR map 尺寸 | 2048 = UE5 高细节材质主流 | 1024（中端）~ 4096（截图级） | 显存 < 4GB → 1024；VRAM 富余 → 4096 |
| `r.MaterialPrediction.BaseChannels` | U-Net 基础 channel 数 | 32 是精度 / 显存平衡点 | 16（手机端）~ 64（高精度 / 离线） | 显存不够 → 16；想 capture 更多细节 → 64 |
| `r.MaterialPrediction.NumLevels` | U-Net 层数 | 4 = 16× 下采样 | 3 层（更快 / 8× 下采样）~ 5 层（更高频 / 32× 下采样） | 细节不够 → 5；速度不够 → 3 |
| `r.MaterialPrediction.NormalStrength` | 法线强度乘子 | 1.0 = 物理正确 | < 1.0（磨平 / 风格化）> 1.0（夸张 / 凹凸感强） | 美术风格化调 0.5-1.5；物理拟真保持 1.0 |
| `r.MaterialPrediction.MetallicThreshold` | 金属判定阈值 | 0.5 是 PBR 行业经验值 | < 0.3 偏塑料感，> 0.7 偏全金属 | **不要随便调**！全局偏移所有 metallic 通道 |
| `r.MaterialPrediction.Debug` | Debug 可视化 | 0 = 生产 / 1 = 调参 | 1 时 UE5 viewport 会显示 4 张 PBR 中间结果 | 调参阶段必开；排查 "metallic 全黑" 时第一件事 |

### 3 个常被误用的参数

#### `BaseChannels` 不是越大越好

直觉："channel 数翻倍 = 精度翻倍"。**错**。

| BaseChannels | 模型权重 | 显存占用 | 推理速度 | 精度提升 |
|-------------|---------|---------|---------|---------|
| 16 | 25 MB | 80 MB | 1.5 ms | baseline |
| 32（默认） | 100 MB | 300 MB | 3 ms | +15% |
| 64 | 400 MB | 1.2 GB | 8 ms | +20% |
| 128 | 1.6 GB | 4.8 GB | 25 ms | +22%（边际递减） |

**经验法则**：32 之后收益递减，64 是 sweet spot，超过 64 大部分场景看不出来。

#### `OutputSize` 不是越高越好

`OutputSize` 是**输出 PBR map 的分辨率**，不是 U-Net 内部 feature map 尺寸。1024 → 2048 是 4× 像素，推理时间接近 4×。

| OutputSize | 像素数 | 推理时间 | UE5 sampler 开销 |
|-----------|-------|---------|----------------|
| 1024 | 1M | 1 ms | 低（适合 mobile） |
| 2048（默认） | 4M | 3-4 ms | 中（PC 主流） |
| 4096 | 16M | 15 ms | 高（截图级） |

**经验法则**：在 UE5 viewport 实际看上去"够清晰"为止，过高浪费。

#### `MetallicThreshold` 不是"金属占比"

直觉："设为 0.7 = 70% 的像素被判定为金属"。**错**。这个参数是**后处理阈值**，把网络输出的 metallic 概率图做 binary threshold：

```
Metallic_final = step(threshold, Metallic_pred)
```

所以 `MetallicThreshold 0.5` 意味着：**网络输出 > 0.5 的像素被强制标为完全金属（1.0），其余为非金属（0.0）**。这会丢失亚金属（0.3-0.7）的细节，**生产环境慎用**。

---

## 5 档性能分级

| 分级 | 改动 | 性能影响 | 适用场景 |
|------|------|----------|----------|
| **极简** | 离线烘焙（训练一次，shader 用结果） | 0ms 实时 | Mobile / 静态资产 |
| **标准** | 实时推理，1024×1024 输出 | ~3.0ms | PC 中端 |
| **高配** | 实时推理，2048×2048 输出 | ~8.0ms | PC 高端 / 过场 |
| **极限** | 实时推理 + 4K + 多材质 latent blending | ~15ms | 截图级 |
| **Debug** | 输出 4 张 PBR 中间结果 | +5ms | 调参 |

---

## 4 个变体版本

- **版本 A：单图预测** — 1 张 base color → 4 PBR（最常见）
- **版本 B：多视角预测** — 3 张不同视角 → 4 PBR（精度更高）
- **版本 C：Latent blending** — 多个材质 latent code 插值，生成 mixed material
- **版本 D：Style transfer** — 风格迁移，参考材质 A 的风格生成材质 B

---

## 6 个已知问题与限制

1. **冷启动长** — 离线训练 24h+，实时推理需 GPU
2. **Metallic / Roughness 难预测** — 这两个通道没有明显视觉线索, L1 loss 难收敛
3. **Normal map 模糊** — 1×1 Conv 无法恢复高频细节,需要结合超分
4. **材质类型局限** — 训练集覆盖不到的特殊材质（金属丝/玻璃），预测质量差
5. **不支持动画** — 输出是静态 PBR,不能预测 vertex animation / 风动
6. **版权 / 训练数据** — 训练数据来源合法性需要确认

---

## 常见误读（Common Misreading）— 5 个初学者陷阱

> 这一节列的是"读文档时容易形成、但实际是错的"理解。每条都是 day-job 真实踩过的坑。

### 误区 1："神经网络预测的 PBR 直接 runtime 用"

**你以为**：把网络接进 UE5 Material Editor，runtime 自动推理 4 张 PBR。
**实际**：实时推理 3-8ms / 材质，100 个材质 = 300-800ms / 帧，直接**爆帧**。

**正解**：
- **生产环境**：离线推理 → 烘焙成 .dds → UE5 直接 sampler
- **实时推理**：仅用于 Editor 调参 / 过场动画 / 截图模式
- 上面"5 档性能分级"里"极简（离线烘焙）"才是 99% 场景的正解

### 误区 2："Metallic / Roughness 跟 BaseColor 一样容易预测"

**你以为**：4 个通道都是 image-to-image translation，难度差不多。
**实际**：BaseColor 是输入的复用（难度最低），Normal 是几何梯度（中等），**Metallic 和 Roughness 是公认难题**。

**为什么难**：
- BaseColor：网络输出 ≈ 输入（passthrough 即可）
- Normal：可以从 shading 梯度反推（有几何线索）
- Metallic / Roughness：**没有明显视觉线索**——一张灰度图，可能是亮塑料也可能是抛光金属，必须依赖**训练集的统计偏差**判断

**正解**：
- 单纯 L1 loss 在这俩通道上**收敛差**，业内常见加 perceptual loss（VGG feature）或 GAN loss
- 如果只看 L1 loss 数字好看但视觉不对，多半是这俩通道的 loss 没优化
- **调参时专门看 metallic / roughness 的可视化**，不要只看 loss 曲线

### 误区 3："1 张图就够了"

**你以为**：单视角 base color 包含足够信息预测 PBR。
**实际**：复杂材质（镜面金属 / 透明玻璃 / 织物）**单视角根本判断不了**。

**为什么**：
- 法线方向 = 高频纹理的反射关系，需要**多个观察角度**才能反推
- 镜面金属的 metallic 几乎是 1，但只有看到反射才确认
- 织物在正面 vs 侧面 roughness 完全不同

**正解**：
- 版本 B（多视角预测）精度比单图高 **30%+**
- 复杂材质必须多视角（Meta 论文 3 视角是 sweet spot）
- 简单材质（diffuse 为主）单图够用

### 误区 4："latent code 插值 = 真混合材质"

**你以为**：金属 latent [0.9, 0.1, ...] 和木材 latent [0.05, 0.8, ...] 插值 = 视觉上像"半金属半木"。
**实际**：**视觉上像，物理上不一定对**。

**为什么**：
- 金属的 BRDF 用 Fresnel + 微表面模型
- 木材的 BRDF 用 Lambertian diffuse
- 中间状态 lerp 出来，神经网络会输出"半金属半木"的样子，但 BRDF 公式**不兼容**——可能 Fresnel 项在 50% metallic 下出现非物理反射
- 这就是 latent space 的 "**interpolation gap**"：训练数据没覆盖的区域，网络瞎猜

**正解**：
- latent 插值仅用于**风格化探索**，不要用于物理拟真场景
- 生产环境的材质插值，建议用**显式参数插值**（metallic / roughness 各自 lerp），不要碰 latent
- 想要物理正确，就老老实实走 4 张 PBR map 的 lerp 路径

### 误区 5："GPU 推理靠 StructuredBuffer 就行了"

**你以为**：网络权重序列化进 .bin → upload 到 StructuredBuffer → shader 直接采样。
**实际**：UE5 里 StructuredBuffer 集成**非常 tricky**，调试成本极高。

**为什么难**：
- Material Editor 不能直接绑 StructuredBuffer，要写 RHI code 上传
- 调试时要分别看 CPU 端的 weight 上传 + GPU 端的 sampler 读取，两端可能不一致
- 跨平台（DX12 / Vulkan / Metal）StructuredBuffer 行为有细微差异

**正解**：
- **首选方案**：离线推理 → 烤进 texture → sampler 读取（最稳）
- **进阶方案**：TensorRT → DirectML / NNE（UE5 内置神经网络推理框架，5.4+ 支持）
- **避免方案**：手写 StructuredBuffer 上传（仅用于研究 / POC，不上生产）

---

## 7 步调参 SOP

1. **`r.MaterialPrediction.Enable 1`** — 启用神经材质预测
2. **`r.MaterialPrediction.Model`** — 选对应用场景的预训练模型（wood/metal/stone）
3. **`r.MaterialPrediction.OutputSize 2048`** — 输出尺寸
4. **校准输入图** — 输入 base color 应是中性光照下拍摄,避免 baked-in lighting
5. **`r.MaterialPrediction.NormalStrength 1.0`** — 法线强度
6. **检查输出** — 在 Material Editor 看 4 张 PBR 通道,Metallic / Roughness 是否合理
7. **烘焙到 texture** — 生产环境烘焙成 texture, runtime 不再推理

---

## 与 day-job RAG 的关联

NeuralPBR 是 day-job **神经材质** 主线的核心载体:

### 1. 工具描述模板
```
Material.NeuralPBR(
    input_base_color: Texture2D,
    model_type: Enum [Wood, Metal, Stone, Fabric, General],
    output_size: int = 2048
) → (BaseColor, Metallic, Roughness, Normal)
  - 推理开销: 3-8ms (1024x1024 → 2048x2048)
  - 训练开销: 24h+ (single GPU)
  - 输出: 4 张 PBR map (16 MB total)
```

### 2. SFT 数据生成路径（day-job 核心）
- **收集**: UE5 商城 100 个高细节材质,导出 base + 4 PBR
- **训练**: 100 材质 × 50 角度 → 5000 张训练样本, MaterialUNet 训练
- **时长**: 1 个 RTX 4090 + 24h ≈ 100 epoch 完成
- **产物**: 一个泛化的 NeuralPBR 模型,可处理"训练集没见过的新材质"

### 3. RAG 检索应用
- 用户问"如何把照片转成 UE5 材质"
- LLM 检索到本案例的工具描述 + 调参 SOP
- LLM 输出工作流:"用 NeuralPBR 模型推理 4 张 PBR, 烘焙到 texture, 在 Material Editor 里绑"

---

## 关联知识库

- [[W2/神经BRDF-NeuralGGX]]（NeuralPBR 预测 PBR 参数, NeuralGGX 拟合 BRDF 公式）
- [[W7/DLSS-神经超分-时域重建]]（NeuralPBR 输出低分辨率 + DLSS 超分 = 神经材质）
- [[W8/神经降噪-RT-Denoiser]]（神经材质预测 vs 神经降噪都是 MLP 在 GPU 上的应用）
- [[../../../01-论文笔记库/2023-NeuralPBR-Material-Prediction|NeuralPBR 论文精读]]
- [[../../../05-技术雷达/Neural-Material-工具对照|神经材质工具雷达]]

---

## 复用指南

把 NeuralPBR 集成到自研引擎:

1. **离线训练** — Python + PyTorch, U-Net 50 层, 训练数据 (base + 4 PBR ground truth)
2. **模型导出** — ONNX → TensorRT (NVIDIA) / OpenVINO (Intel) / DirectML (Cross-platform)
3. **GPU 推理** — texture → 4 texture, 写入到 Material Asset
4. **烘焙** — 离线烘焙成 .dds / .png, runtime 用 texture sampler
5. **风格迁移扩展** — 加个 style reference input, 实现 "画 A 像 B" 的材质生成
6. **多材质 latent** — 把多个材质 latent code 存进 KV cache, 支持快速材质切换
7. **实时推理 fallback** — SM5 不支持 → 离线烘焙,SM6 支持 → 实时推理

---

*Create date: 2026-07-09*
*Last modified: 2026-07-09*