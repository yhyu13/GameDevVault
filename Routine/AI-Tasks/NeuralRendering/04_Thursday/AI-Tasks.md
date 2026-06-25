---
tags: [routine/AI-tasks, topic/NeuralRendering, day/Thursday]
aliases: []
---

# 周四：AI 任务清单 — Neural Rendering 工程化与工具链

> **人类目标**：理解 UE5.8 Neural Rendering 的 C++ 数据结构和 ONNX 集成模式，开发实用工具脚本。  
> **AI 任务**：生成工具脚本、解释架构、review 内存布局，绝不替你做核心设计。

---

## 任务 1：C++ Neural 模块概念研究（AI 执行，你实践）

**输入**："UE5.8 NeuralNetworkEngine 和 MLDeformer 的核心 C++ 数据结构和类关系？"

**AI 输出**：
1. **NeuralNetworkEngine 核心类**：
   - `FNeuralNetworkEngine` — 模块单例，管理 ONNX Runtime 环境
   - `FONNXRuntimeSession` — 封装 ONNX Runtime Session，负责 `Run()` 推理
   - `FNeuralTensor` — 张量封装，管理输入/输出 buffer（`float*` + dims）
   - `ENeuralExecutionProvider` — 枚举：CPU / DirectML / CUDA / CoreML
2. **MLDeformer 核心类**：
   - `UMLDeformerModel` — 继承 `UObject`，存储 ONNX 模型资产和元数据（input/output dims）
   - `UMLDeformerComponent` — 继承 `UActorComponent`，附加到 `SkeletalMeshActor`，每帧收集 bone transforms
   - `FMLDeformerInputInfo` — 描述输入格式（bone names, rotation format, normalization params）
   - `FMLDeformerOutputInfo` — 描述输出格式（vertex indices, offset scale, apply mode: additive vs replace）
3. **集成点**：
   - `FSkeletalMeshObject::UpdateSkinning()` 中插入 `MLDeformer` vertex offset 应用
   - `NeuralNetworkEngine` 的 `FNeuralTensor` 与 `FSkeletalMeshVertexBuffer` 的数据对齐

**你必须做**：
1. 在 UE58 源码中打开 `NeuralNetworkEngine/Public/` 和 `MLDeformer/Public/` 目录
2. 阅读 `NeuralNetworkEngine.h` 和 `MLDeformerModel.h` 的完整接口
3. 画出类关系图（UML 或手写）

---

## 任务 2：ONNX 模型检查工具脚本（AI 执行，你 review）

**输入**："写一个 Python 脚本，检查一个 ONNX 模型是否兼容 UE5.8 NeuralNetworkEngine，验证：opset version、输入输出维度、支持的算子列表"

**AI 输出**：完整的 Python 脚本

```python
#!/usr/bin/env python3
"""ONNX Model Compatibility Checker for UE5.8 NeuralNetworkEngine."""

import onnx
import sys
from pathlib import Path

UE58_SUPPORTED_OPS = {
    "Conv", "Relu", "MaxPool", "AveragePool",
    "Gemm", "MatMul", "Add", "Sub", "Mul", "Div",
    "Reshape", "Transpose", "Flatten", "Concat",
    "BatchNormalization", "Dropout", "Softmax",
    "Tanh", "Sigmoid", "LeakyRelu", "Swish",
    # TODO(HUMAN): 根据 UE5.8 ONNX Runtime 版本补充完整列表
}

def check_onnx_ue58_compatibility(model_path: str) -> dict:
    """Check if an ONNX model is compatible with UE5.8 NeuralNetworkEngine."""
    model = onnx.load(model_path)
    
    # TODO(HUMAN): 实现检查逻辑
    # 1. 检查 opset version (UE5.8 通常支持 >= 11)
    # 2. 检查所有算子是否在 UE58_SUPPORTED_OPS 中
    # 3. 检查输入输出维度（batch size 是否 dynamic？vertex count 是否匹配？）
    # 4. 检查模型大小（是否超过内存预算？）
    # 5. 返回兼容性报告 dict
    pass

def generate_ml_deformer_report(model_path: str) -> str:
    """Generate a human-readable report for ML Deformer model."""
    # TODO(HUMAN): 生成 Markdown 格式报告
    # 包含：模型名称、opset、输入维度、输出维度、参数量、算子列表、兼容性结论
    pass

if __name__ == "__main__":
    # TODO(HUMAN): 命令行参数解析，调用 check 和 report 函数
    pass
```

**你必须做**：
1. 逐行阅读代码
2. 根据 UE5.8 实际 ONNX Runtime 版本（1.15+）补充 `UE58_SUPPORTED_OPS`
3. 添加对 dynamic axes 的检查（UE5.8 是否支持 dynamic batch size？）
4. 运行并验证输出（用你周二生成的 `ml_deformer.onnx` 测试）

---

## 任务 3：ML Deformer Pipeline 架构 Review（AI 执行，你决策）

**AI 审查清单**：
- [ ] Training data 的 temporal coherence 是否足够？（相邻帧的 vertex offsets 应该平滑，否则网络会学到噪声）
- [ ] Network capacity 是否与 deformation complexity 匹配？（10000 顶点全精度 vs 100 顶点局部变形）
- [ ] ONNX Runtime 的 Execution Provider 选择是否合理？（PC 用 DirectML，Console 用专用 NPU，Mobile 用 CPU / CoreML）
- [ ] Memory layout 是否 cache-friendly？（vertex offsets 的存储顺序是否与 GPU vertex buffer 一致？）
- [ ] 与现有 Animation Blueprint 的兼容性？（ML Deformer 是否影响 Animation Blueprint 的 blend weight？）
- [ ] LOD / Distance culling 策略？（远距离角色是否关闭 ML Deformer 以节省性能？）

**你必须做**：评估每个建议，记录决策。

---

## 任务 4：Neural Inference 内存布局（AI 计算，你验证）

**输入**：ML Deformer runtime 内存结构（简化版）

```cpp
struct FMLDeformerFrame {
    TArray<FTransform> BoneTransforms;     // 64 bones × 4×4 float matrix
    TArray<FVector3f> VertexOffsets;     // 10000 verts × 3 float
    float NormalizationScale;              // 1 float
    float NormalizationOffset;           // 1 float
};

struct FONNXRuntimeSession {
    Ort::Session* Session;                 // ONNX Runtime Session
    Ort::MemoryInfo* MemoryInfo;         // CPU / GPU memory info
    TArray<FNeuralTensor> InputTensors;    // 输入张量绑定
    TArray<FNeuralTensor> OutputTensors;   // 输出张量绑定
    TArray<int64> InputShape;              // [1, 768] (batch=1, bone features)
    TArray<int64> OutputShape;             // [1, 30000] (batch=1, vertex offsets)
};
```

**AI 输出**：内存大小估算、CPU→GPU 拷贝开销分析、cache locality 建议

| 组件 | 估算大小 | 优化建议 |
|------|----------|---------|
| BoneTransforms (64 × 16 × 4 bytes) | 4,096 bytes | 转换为 12-float 表示（去掉最后一行），压缩到 3,072 bytes |
| VertexOffsets (10000 × 3 × 4 bytes) | 120,000 bytes | 使用 FP16（Half）压缩到 60,000 bytes，如果精度允许 |
| ONNX Input Tensor | 768 × 4 = 3,072 bytes | 预分配 persistent buffer，避免每帧 alloc |
| ONNX Output Tensor | 30000 × 4 = 120,000 bytes | 直接 map 到 vertex buffer 的 staging memory |
| Session + MemoryInfo | ~几百 bytes | 全局单例，不要每帧创建 |

**你必须做**：用 `sizeof()` 或 `UE_LOG` 测量实际内存大小，对比 AI 估算。在 UE5 中验证 `FNeuralTensor` 的内存布局。

---

## 今日 AI 禁区

- ❌ 让 AI 替你设计 ONNX 兼容性检查逻辑（必须自己理解 UE5.8 的 ONNX Runtime 限制）
- ❌ 直接运行脚本不 review（ONNX 模型检查工具需要理解每个算子的含义）
- ❌ 解释概念后不写代码实践
- ❌ 让 AI 决定内存优化策略（必须自己测量实际瓶颈）

---

## 完成检查清单

- [ ] C++ 核心类头文件已阅读，类关系图已绘制
- [ ] ONNX 兼容性检查脚本已 review、修改、运行验证
- [ ] ML Deformer pipeline 架构审查报告已阅读，决策已记录
- [ ] 内存布局分析已验证（实际测量 vs AI 估算）
- [ ] 所有代码和文档已写入 Obsidian

---

*AI 执行时间：约 25 分钟*  
*人类执行时间：约 2 小时*
