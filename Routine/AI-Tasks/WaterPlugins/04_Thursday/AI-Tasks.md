---
tags: [routine/AI-tasks, topic/WaterPlugins, day/Thursday]
aliases: []
---

# 周四：AI 任务清单 — Water Plugins 工程化与工具链

> **人类目标**：理解 Water Plugin 的底层工程实现（波浪计算、浮力系统、工具链），为自研引擎做准备。  
> **AI 任务**：生成工具脚本、解释概念、review 架构，绝不替你做核心设计。

---

## 任务 1：波浪分析工具生成（AI 执行，你 review）

**输入**："写一个 Python 脚本，可视化 Gerstner Wave 的参数空间（A, λ, D, Q），生成交互式 3D 图"

**AI 输出**：完整的 Python 脚本（使用 matplotlib 或 plotly）

**你必须做**：
1. 逐行阅读代码
2. 检查参数范围是否合理
3. 添加你自己的需求（如多波叠加可视化）
4. 运行并验证输出

---

## 任务 2：Buoyancy 系统概念（AI 执行，你实践）

**输入**："Water Plugin 的 Buoyancy 系统如何与 Chaos Physics 协同？浮力计算的数学原理？"

**AI 输出**：
1. 阿基米德原理：浮力 = 排开水的重量
2. 实现方式：计算物体浸入水中的体积，乘以水的密度
3. 与 Chaos 的交互：每帧更新浮力力和力矩

**你必须做**：写一个简化版 Buoyancy 计算示例（Python 或 C++）。

---

## 任务 3：Water Plugin 架构 Review（AI 执行，你决策）

**AI 审查清单**：
- [ ] 是否支持多种水体类型（Ocean / Lake / River / Pond）？
- [ ] 波浪计算是否在 Compute Shader 中？
- [ ] 浮力计算的性能优化（BVH / Spatial Hash）？
- [ ]  shoreline 的波浪衰减如何处理？
- [ ] 与 Lumen/Nanite 的协同（水下 GI、反射）？

**你必须做**：评估建议，记录决策。

---

## 任务 4：Water 渲染内存布局分析（AI 计算，你验证）

**输入**：Water 顶点的结构体

```cpp
struct WaterVertex {
    float3 position;      // 12 bytes
    float3 normal;        // 12 bytes
    float2 uv;            // 8 bytes
    float4 tangent;       // 16 bytes
    float waveHeight;     // 4 bytes
};
```

**AI 输出**：总大小、padding、Cache Line 分析、重排序建议

**你必须做**：用 `sizeof()` 验证。

---

## 今日 AI 禁区

- ❌ 让 AI 替你设计水体架构
- ❌ 直接运行脚本不 review
- ❌ 解释概念后不写代码实践

---

## 完成检查清单

- [ ] 工具脚本已 review、修改、运行验证
- [ ] Buoyancy 计算已用迷你代码实践
- [ ] 架构审查报告已阅读，决策已记录
- [ ] 内存布局分析已验证
- [ ] 所有代码和文档已写入 Obsidian

---

*AI 执行时间：约 25 分钟*  
*人类执行时间：约 2 小时*
