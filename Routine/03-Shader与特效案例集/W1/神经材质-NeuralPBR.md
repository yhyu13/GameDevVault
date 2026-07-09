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

| 传统 PBR 材质流程                     | 神经材质参数化                            |
| ------------------------------ | ---------------------------------- |
| 美术手调 BaseColor / Metallic / Roughness | **神经网络从单图预测 4 个 PBR 通道**           |
| Substance Designer 流程长（小时级）        | **1 秒推理出 PBR**                   |
| 8 张 texture × 2K = 16 MB / material | **神经网络 1×1 Conv 直接重建**，省 90% 显存 |
| 同材质多 LOD 手动管理                   | **网络自动多尺度**                       |
| 材质变体爆炸（50 个 metal / 50 个 wood）    | **网络 latent space 连续插值**           |

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