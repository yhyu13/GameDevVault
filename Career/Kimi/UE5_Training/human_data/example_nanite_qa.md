## Nanite GPU-Driven Pipeline 深度问答

> 基于个人项目经验（火炬之光 UE5 升级）和源码阅读

---

### Question 1

**Instruction**: 面试官问：Nanite 的 GPU-Driven Pipeline 具体是怎么工作的？CPU 和 GPU 的分工是什么？

**Category**: technical_explanation

**Output**:

**CPU 的职责（离线 Cook 阶段）**：
1. 将静态 Mesh 分割为 Cluster（约 128 个三角形）
2. 计算 Cluster 的包围盒和 LOD 误差度量
3. 构建 DAG（有向无环图）描述连续 LOD 层级
4. 将 Cluster 打包为 Page（流式加载单元）
5. 生成 6 方向的 Lumen Card Representation（用于 Lumen）

**GPU 的职责（运行时）**：
1. **Instance Culling**：Compute Shader 遍历 GPUScene，基于视锥和 HZB 剔除不可见实例
2. **Cluster Culling**：对保留下来的实例，进一步剔除不可见 Cluster
3. **软件光栅化**：Compute Shader 处理亚像素三角形（小于 1 像素）
4. **硬件光栅化**：标准管线处理正常大小的三角形
5. **Visibility Buffer**：写入材质 ID 和三角形索引，而非传统 GBuffer

**关键源码路径**：
- `Engine\Source\Runtime\Renderer\Private\Nanite\NaniteRender.cpp` — 主入口
- `Engine\Source\Runtime\Renderer\Private\Nanite\NaniteClusterCulling.cpp` — Cluster 裁剪
- `Engine\Source\Runtime\Renderer\Private\Nanite\NaniteRasterizer.cpp` — 光栅化

**个人经验**：火炬之光升级时，植被实例从 CPU-Driven 的 2000 个实例瓶颈，迁移到 Nanite 后同屏支持 30000+ 实例。代价是 Cook 时间增加约 40%，但运行时 CPU 占用从 15ms 降到 2ms。

---

### Question 2

**Instruction**: 面试官问：软件光栅化（Compute Shader）和硬件光栅化的分界点是什么？怎么决定用哪个？

**Category**: technical_explanation

**Output**:

**分界标准**：三角形在屏幕上的投影面积是否小于 1 个像素。

- **硬件光栅化**：三角形 >= 1 像素 → 标准 GPU 管线
- **软件光栅化**：三角形 < 1 像素 → Compute Shader 逐像素计算覆盖

**为什么需要分界**：
1. 硬件光栅化以 2×2 Quad（4 个像素）为单位，小三角会产生 Quad Overdraw（1 个有效像素但占用 4 个像素的计算）
2. 亚像素三角形还会触发 Early-Z 失效，因为硬件无法精确判断深度
3. 软件光栅化在 Compute Shader 中精确计算每个像素的覆盖，没有 Quad Overdraw

**源码中的判断逻辑**：
```cpp
// NaniteRasterizer.cpp
// 根据三角形投影面积决定光栅化路径
if (TriangleProjectedArea < 1.0f)
{
    // 软件光栅化路径
    ComputeShaderRasterize(Triangle);
}
else
{
    // 硬件光栅化路径
    HardwareRasterize(Triangle);
}
```

**注意**：软件光栅化不写入 ROP（Render Output），而是通过 UAV（Unordered Access View）直接写入 Visibility Buffer，绕过了固定功能管线的限制。

---

### Question 3

**Instruction**: 面试官问：Nanite 的 Visibility Buffer 和传统 GBuffer 有什么区别？

**Category**: comparison

**Output**:

| 特性 | 传统 GBuffer | Nanite Visibility Buffer |
|------|-------------|--------------------------|
| 存储内容 | 直接存储颜色/法线/深度 | 存储实例 ID + 三角形索引 + 材质 ID |
| 内存占用 | 高（多通道 float 纹理） | 低（整数索引） |
| 材质处理 | Base Pass 直接写入 | 延迟材质评估（Decode Visibility） |
| 多材质支持 | 需要多 Pass | 支持单 Pass 多材质（通过索引查找） |
| Overdraw 代价 | 高（每像素重复写入） | 低（只写一次索引） |

**Visibility Buffer 的工作流程**：
1. 光栅化阶段写入：`(InstanceID, TriangleIndex, MaterialSlotID)`
2. 材质评估阶段（Material Pass）：根据索引读取三角形顶点属性，计算材质
3. 写入最终 GBuffer

**优势**：
- 避免传统 Deferred Rendering 的多材质多 Pass 问题
- 一个 Draw Call 可以处理成千上万个不同材质的三角形
- 内存带宽大幅降低（写整数索引 vs 写 float4 颜色）

**劣势**：
- 需要额外的 Decode 阶段（但现代 GPU 计算能力强，此开销很小）
- 对 MSAA 不友好（因为不是直接存储颜色）

---

## 模板使用示例

这个文件展示了 `template_qa.md` 的实际填写方式。你可以：
1. 复制 `template_qa.md` 到 `human_data/你的文件名.md`
2. 用你的专业知识替换示例内容
3. 运行 `python scripts/convert_human_data.py` 生成 .jsonl

每个 ### Question 区块会生成一条训练记录。
