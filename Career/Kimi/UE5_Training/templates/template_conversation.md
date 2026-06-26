## Template: Multi-Turn Conversation (多轮面试追问)

> 用于训练模型处理层层深入的面试追问。  
> 模拟真实面试：面试官问基础 → 追问细节 → 追问边界条件 → 追问项目经验。

---

### Conversation 1

**Topic**: Nanite GPU-Driven Pipeline

**Turn 1**:
- **User**: 面试官问：什么是 GPU-Driven Pipeline？和 UE4 的 CPU-Driven 有什么区别？
- **Assistant**: GPU-Driven 指渲染的裁剪和绘制指令生成都在 GPU 上完成，CPU 只负责提交高层命令。UE4 的 CPU-Driven 每帧需要 CPU 逐个遍历实例、计算 LOD、提交 Draw Call，Draw Call 数量受 CPU 限制；GPU-Driven 把这些工作交给 Compute Shader，CPU 只需提交一次 Indirect Draw 命令，GPU 自己决定画什么。

**Turn 2**:
- **User**: 追问：那 CPU 完全不管了吗？Cook 阶段它做什么？
- **Assistant**: 不是完全不管。CPU 在 Cook 阶段（离线构建）负责：1. 将 Mesh 分割为 Cluster（约128个三角形）；2. 构建 DAG（连续 LOD 层级）；3. 生成 Page（流式加载单元）。这些是一次性预处理，运行时只需要 GPU 加载已生成的数据。

**Turn 3**:
- **User**: 追问：如果运行时想动态修改 Mesh（比如 vertex animation），Nanite 还能工作吗？
- **Assistant**: 看修改方式。Vertex Shader 变形（如波浪、缩放）Nanite 支持，因为 GPU 在光栅化前可以应用 VS。但 CPU 级别的顶点修改（如 Morph Targets、Cloth 模拟）Nanite 不支持，因为这些需要重新生成 Cluster/DAG。Skinned Mesh 在 UE5.5+ 已支持，但仍有限制。

**Turn 4**:
- **User**: 追问：你在火炬之光项目中遇到过 GPU-Driven 的问题吗？怎么解决的？
- **Assistant**: 火炬之光升级 UE5 时，我们遇到大量植被实例的渲染瓶颈。UE4 的 CPU-Driven 在植被密集区域（几千个实例）Draw Call 爆炸，CPU 成为瓶颈。迁移到 Nanite 后， vegetation 用 GPU-Driven 渲染，同屏实例数提升到数万级别。但问题是不支持 Wind Animation（顶点动画），我们最终改用 Vertex Shader 做风动效果，绕过了 Nanite 的限制。

---

### Conversation 2

**Topic**: Lumen Surface Cache vs Screen Space GI

**Turn 1**:
- **User**: 面试官问：Lumen 的 Surface Cache 和 Screen Space GI（SSGI）有什么区别？
- **Assistant**: SSGI 只收集屏幕上的像素信息，看不到屏幕外的物体，所以会有漏光（Light Leak）和反射截断。Lumen 的 Surface Cache 是世界空间的表示：每个 Mesh 都有预计算的 Lumen Card，存储世界空间的光照信息，即使物体不在屏幕上，也能参与间接光照计算。

**Turn 2**:
- **User**: 追问：Surface Cache 是预计算的吗？动态物体怎么办？
- **Assistant**: 不是完全预计算。Surface Cache 的 Card 是静态布局的，但 Card 上的光照信息是每帧动态更新的。增量更新机制只更新 dirty Card。动态物体的间接光照主要靠 Screen Probe（屏幕空间探针）实时捕获，不是 Surface Cache。

**Turn 3**:
- **User**: 追问：那动态物体在 Lumen 中会有间接光照吗？质量怎么样？
- **Assistant**: 有，但质量有限。动态物体的间接光照通过 Screen Probe Gather 捕获：屏幕上的每个像素区域发射 Cone 收集周围光照。问题是：1. 只能收集屏幕上可见的信息，看不到背面的反弹光；2. 远距离采样用低分辨率 Mip，细节丢失。所以在动态角色密集的场景，Lumen 的间接光照不如静态场景稳定。

---

## 模板说明

- 每个 `### Conversation N` 生成一条多轮对话记录
- 最少 3 轮，建议 4-5 轮，模拟真实面试节奏
- 最后一轮建议加入**项目经验**（如果你有个人经历）
- 追问要有逻辑递进：What → Why → How → Edge Case → Project Experience
- 转换脚本会把这些 Turn 转成 `conversation` 格式的 `.jsonl`
