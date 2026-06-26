## Template: Code Explanation (代码解释)

> 用于训练模型解释 UE5 源码片段。  
> 必须包含：代码作用 + 为什么这样写 + 如果改会怎样。

---

### Code 1

**Instruction**: 分析这段 UE5 源码的作用，并解释如果去掉 HZB 检查会怎样？

```cpp
void FStreamingManager::RequestPages(const FViewInfo& View)
{
    // 根据视锥和 HZB 计算可见 Cluster
    // 只加载对应的 Page，其他 Page 可以卸载
}
```

**Category**: code_explanation

**Output**:

**作用**：这是 Nanite 流式加载管理器的核心入口。根据当前相机的视锥（Frustum Culling）和 HZB（Hierarchical Z-Buffer，层级深度缓冲）双重检查，决定哪些 Cluster 对应的 Page 需要加载到 GPU 显存中。

**为什么这样写**：
1. **视锥剔除**：先看 Cluster 的包围盒是否在相机视锥内，不在的直接排除
2. **HZB 遮挡剔除**：视锥内的 Cluster 还要检查是否被前面物体遮挡。HZB 是上一帧渲染结果构建的层级深度图，coarse 层级快速剔除，fine 层级精确验证
3. **按需加载**：只有通过双重检查的 Cluster 才会触发 Page 加载，避免一次性加载整个场景的 Nanite 数据

**如果去掉 HZB 检查**：
- 所有视锥内的 Cluster 都会被加载，即使它们被完全遮挡
- 显存占用可能增加 3-5 倍（取决于场景遮挡复杂度）
- 在封闭室内场景（大量遮挡）中尤其严重

**关键源码路径**：`Engine\Source\Runtime\Renderer\Private\Nanite\NaniteStreamingManager.cpp`

---

### Code 2

**Instruction**: 这段代码中的 `MipLevel` 和 `MinLODError` 是什么意思？它们如何决定 LOD 切换？

```cpp
struct FClusterGroup
{
    uint32 MipLevel;           // LOD 层级
    float MinLODError;         // 最小误差（子节点）
    float MaxParentLODError;   // 最大误差（父节点）
    TArray<uint32> Children;   // 子 Cluster 索引
    FSphere Bounds;            // 包围球
    FSphere LODBounds;         // LOD 包围球
};
```

**Category**: code_explanation

**Output**:

**MipLevel**：表示该 ClusterGroup 所在的 LOD 层级。0 是最高精度（原始几何），数值越大越粗糙。

**MinLODError**：子节点（更精细的下一层）的最小屏幕空间误差。当相机距离某个 Cluster 很近时，如果当前 MipLevel 的误差已经小于 MinLODError，说明需要切换到更精细的子节点。

**MaxParentLODError**：父节点（更粗糙的上一层）的最大误差。当相机远离某个 Cluster 时，如果当前 MipLevel 的误差已经大于 MaxParentLODError，说明可以切换到更粗糙的父节点。

**LOD 切换决策**：
GPU 在运行时根据像素覆盖度计算当前 ClusterGroup 的屏幕空间误差，如果：
- 误差 < MinLODError → 选择子节点（更精细）
- 误差 > MaxParentLODError → 选择父节点（更粗糙）
- 否则 → 保持当前层级

这就是 Nanite "无级连续 LOD" 的核心：没有离散 LOD 切换，误差在父子之间连续变化。

---

## 模板说明

- 每个 `### Code N` 区块生成一条记录
- `Instruction` 必须包含代码片段 + 具体问题（不要只给代码）
- `Output` 必须包含三部分：作用 / 为什么这样写 / 如果改会怎样
- Category 固定为 `code_explanation`
