---
tags: [routine/AI-tasks, topic/VGM, day/Thursday]
aliases: []
---

# 周四：AI 任务清单 — VGM 工程化与工具链

> **人类目标**：理解 Mesh Shader API 和 GPU-Driven 管线的工程实现，为自研引擎做准备。  
> **AI 任务**：生成工具脚本、解释 API、review 架构，绝不替你做核心设计。

---

## 任务 1：Mesh 分析工具生成（AI 执行，你 review）

**输入**："写一个 Python 脚本，将任意 Mesh 转换为 Meshlet 格式（按 NVidia 推荐的 64v/128p 标准），输出为二进制文件"

**AI 输出**：完整的 Python 脚本（使用 meshoptimizer 或自实现）

**你必须做**：
1. 逐行阅读代码
2. 检查边界条件（mesh 太小、非流形等）
3. 添加你自己的格式扩展（如材质 ID、LOD 层级）
4. 运行并验证输出

---

## 任务 2：Mesh Shader API 概念解释（AI 执行，你实践）

**输入**："Vulkan Mesh Shader Extension 的完整调用链是怎样的？从创建 pipeline 到 dispatch"

**AI 输出**：
1. 扩展名称：`VK_EXT_mesh_shader`
2. 关键 API：`vkCmdDrawMeshTasksEXT`
3. Pipeline 创建时需要 Mesh Shader 和 Task Shader 模块
4. 与传统 `vkCmdDrawIndexed` 的区别

**你必须做**：写一个最小 Vulkan 示例，验证 API 调用。

---

## 任务 3：GPU-Driven 架构 Review（AI 执行，你决策）

**AI 审查清单**：
- [ ] 是否支持 fallback 到传统管线？（旧 GPU 兼容性）
- [ ] Task Shader 的剔除粒度是否合适？
- [ ] Meshlet 数据是否紧凑？（内存带宽）
- [ ] 是否支持动态物体？（骨骼动画的 Mesh Shader 方案）
- [ ] 调试工具是否完善？（GPU printf、PIX / RenderDoc 支持）

**你必须做**：评估建议，记录决策。

---

## 任务 4：Meshlet 内存布局分析（AI 计算，你验证）

**输入**：Meshlet 结构体定义

```cpp
struct Meshlet {
    uint32 vertexIndices[64];
    uint8 primitiveIndices[128];  // 3 indices per triangle
    uint8 vertexCount;
    uint8 primitiveCount;
};
```

**AI 输出**：总大小、Cache Line 分析、压缩建议

**你必须做**：用 `sizeof()` 验证，测试内存带宽影响。

---

## 今日 AI 禁区

- ❌ 让 AI 替你设计 GPU-Driven 架构
- ❌ 直接运行脚本不 review
- ❌ 解释概念后不写代码实践

---

## 完成检查清单

- [ ] 工具脚本已 review、修改、运行验证
- [ ] Mesh Shader API 已用迷你代码实践
- [ ] 架构审查报告已阅读，决策已记录
- [ ] 内存布局分析已验证
- [ ] 所有代码和文档已写入 Obsidian

---

*AI 执行时间：约 25 分钟*  
*人类执行时间：约 2 小时*
