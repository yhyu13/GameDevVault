## Template: Single-Turn Q&A (单轮问答)

> 用于训练模型回答具体的 UE5 技术问题。  
> 复制此模板到 `human_data/你的文件名.md`，填写后运行转换脚本。

---

### Question 1

**Instruction**: 面试官问：Nanite 的 Cluster Culling 和 Instance Culling 的本质区别是什么？

**Category**: technical_explanation

**Output**:

两者的本质区别是**裁剪粒度**不同：

1. **InstanceCulling**（粗粒度）：
   - 裁剪对象：整个 Mesh 实例（Instance）
   - 输入：GPUScene 中的实例变换矩阵和包围盒
   - 输出：哪些实例需要进入后续渲染流程
   - 如果实例被裁掉，它的所有 Cluster 都不会参与后续步骤

2. **ClusterCulling**（细粒度）：
   - 裁剪对象：几何单元（Cluster，约128个三角形）
   - 输入：InstanceCulling 通过后的实例的 Cluster 列表
   - 使用 HZB（Hierarchical Z-Buffer）做遮挡剔除
   - 输出：哪些 Cluster 最终需要光栅化

3. **执行顺序**：InstanceCulling → ClusterCulling，两者都是 GPU 执行的 Compute Shader

**关键源码**：
- `Engine\Source\Runtime\Renderer\Private\Nanite\NaniteClusterCulling.cpp`
- `Engine\Source\Runtime\Renderer\Private\Nanite\NaniteInstanceCulling.cpp`

---

### Question 2

**Instruction**: 面试官问：Lumen 的 Surface Cache 为什么要做增量更新，而不是每帧全量更新？

**Category**: interview_answer

**Output**:

全量更新的成本是 O(场景 Card 数量)，对于大型场景无法接受：

1. **增量更新策略**：
   - 每帧只更新 `CardCapturesPerFrame` 张 Card（默认约几十张）
   - 优先更新 dirty Card（法线变化、距离变化、新可见）
   - 使用 LRU 管理更新队列

2. **权衡**：
   - 更新太少：动态物体光影延迟，出现滞后
   - 更新太多：GPU 负载突增，帧率波动
   - UE5 的默认值是在 60fps 目标下的经验值

3. **面试官追问**：如果光照变化剧烈（比如爆炸），增量更新不够怎么办？
   - 答：Lumen 有紧急更新机制，对于突然大量 dirty 的 Card，会临时增加每帧更新配额，但可能掉帧。

---

## 模板说明

- 每个 `### Question N` 区块会生成一条 `.jsonl` 记录
- `Instruction` 是用户输入的问题（要求像真实面试问题）
- `Output` 是模型应该学会生成的回答
- `Category` 可选：`technical_explanation`, `interview_answer`, `code_analysis`, `comparison`
- 可以写多个 Question 区块，转换脚本会一次性全部处理
