## Template: Common Misconceptions (常见错误纠正)

> 用于训练模型识别和纠正 UE5 领域的常见错误说法。  
> 这些数据让模型学会 "批判性思考"，不只是复述正确知识。

---

### Misconception 1

**Instruction**: 面试官说："Nanite 的 GPU-Driven 意味着 CPU 完全不参与渲染，所以 Nanite 的 Cook 时间也可以省了。" 这个说法有什么问题？

**Category**: misconception_correction

**Output**:

这个说法有两个错误：

1. **"CPU 完全不参与"是错的**：CPU 在 Cook 阶段大量参与——生成 Cluster、构建 DAG、计算 LOD 误差、打包 Page。没有这些预处理，GPU 运行时根本无数据可加载。GPU-Driven 指的是**运行时**的渲染流程，不是整个流程。

2. **"Cook 时间可以省了"是错的**：Nanite 的 Cook 时间实际上比传统 LOD **更长**，因为：
   - 需要生成多层级 ClusterGroup
   - 需要计算每个层级的误差度量
   - 需要构建 DAG 父子关系
   - 需要打包 Page 用于流式加载

传统 LOD 只需要美术做 3-4 个模型，Cook 时不做额外计算；Nanite 的自动化是以**更长的 Cook 时间**和**更大的磁盘占用**为代价的。

---

### Misconception 2

**Instruction**: 有人说："Lumen 的 Surface Cache 就是预计算的光照贴图，和 Lightmap 一样。" 这个观点对吗？

**Category**: misconception_correction

**Output**:

不对，虽然两者都存储光照信息，但本质区别很大：

| 特性 | Lightmap | Lumen Surface Cache |
|------|---------|---------------------|
| 更新频率 | 完全静态，烘焙后不变 | 每帧增量更新，动态响应 |
| 精度 | 高分辨率（像素级） | 中等分辨率（Card 级别） |
| 范围 | 只存储直接光照 | 存储 Radiance（可用于间接光照） |
| 用途 | 直接显示 | 被 Screen Probe 采样用于间接光照 |

Surface Cache 更像**动态光照的缓存**，而不是静态 Lightmap。它的光照信息是每帧更新的，只是更新频率受 `CardCapturesPerFrame` 限制。

---

### Misconception 3

**Instruction**: 有候选人回答："VSM 的 Page 标记是从 Light Camera 视角做的，因为阴影是 Light 生成的。" 这个说法正确吗？

**Category**: misconception_correction

**Output**:

不正确。VSM 的 `GeneratePageFlagsFromPixels` 是**从 Camera（主相机）视角**标记的：

- 遍历屏幕像素，根据深度和法线反推光源空间坐标
- 标记哪些虚拟页会被 Camera 采样
- 如果反过来从 Light Camera 标记，会标记所有被光照到的区域，造成大量浪费

**关键区别**：
- Camera 视角标记：O(屏幕像素数量) → 精确、按需
- Light 视角标记：O(光源覆盖范围) → 可能包含大量 Camera 看不到的区域

源码位置：`Engine\Source\Runtime\Renderer\Private\VirtualShadowMaps\VirtualShadowMapPageManagement.cpp`

---

## 模板说明

- 每个 `### Misconception N` 生成一条记录
- `Instruction` 先给出错误说法，然后问 "有什么问题？"
- `Output` 必须：**指出错误 → 解释正确事实 → 对比说明为什么错**
- Category 固定为 `misconception_correction`
- 这类数据对模型学习 "批判性回答" 非常重要
