---
tags: [routine/AI-tasks, topic/VSM, day/Thursday]
aliases: []
---

# 周四：AI 任务清单 — VSM 工程化与工具链

> **人类目标**：理解 VSM 的底层工程实现（Page Table 管理、稀疏纹理分配、GPU-Driven），为自研引擎做准备。  
> **AI 任务**：生成工具脚本、解释概念、review 架构，绝不替你做核心设计。

---

## 任务 1：VSM 分析工具生成（AI 执行，你 review）

**输入**："写一个 Python 脚本，分析 RenderDoc 捕获的 VSM 帧数据，统计：每帧分配的物理页数、未命中页数、级间过渡区域的像素比例"

**AI 输出**：完整的 Python 脚本（使用 RenderDoc API 或解析 CSV）

**你必须做**：
1. 逐行阅读代码
2. 检查引擎特定假设
3. 添加你自己的需求（如统计阴影质量指标）
4. 运行并验证输出

---

## 任务 2：Page Table 内存管理概念（AI 执行，你实践）

**输入**："VSM 的 Page Table 如何管理物理页的分配与回收？与 Lumen 的 Surface Cache 有何异同？"

**AI 输出**：
1. 概念解释：按需分配、LRU 回收、延迟分配
2. 与 Lumen Surface Cache 的对比（共享物理池 vs 独立池）
3. UE5 源码中的具体实现

**你必须做**：写一个简化版 Page Allocator，验证理解。

---

## 任务 3：VSM 架构 Review（AI 执行，你决策）

**AI 审查清单**：
- [ ] 是否支持 fallback 到传统 CSM？（旧 GPU 兼容性）
- [ ] 物理纹理池大小是否可动态调整？
- [ ] 多光源场景下，Page Pool 是否冲突？
- [ ] 透明物体阴影如何处理？（VSM 不支持）
- [ ] 与 Lumen GI 的协同：阴影精度是否影响 GI 质量？

**你必须做**：评估建议，记录决策。

---

## 任务 4：Page Table 内存布局分析（AI 计算，你验证）

**输入**：VSM 的 Page Table Entry 结构体

```cpp
struct VSMPageEntry {
    uint16 physicalPageX : 8;
    uint16 physicalPageY : 8;
    uint16 mipLevel : 4;
    uint16 allocated : 1;
    uint16 valid : 1;
};
```

**AI 输出**：总大小、Cache Line 分析、压缩建议

**你必须做**：用 `sizeof()` 验证。

---

## 今日 AI 禁区

- ❌ 让 AI 替你设计 VSM 架构
- ❌ 直接运行脚本不 review
- ❌ 解释概念后不写代码实践

---

## 完成检查清单

- [ ] 工具脚本已 review、修改、运行验证
- [ ] Page Allocator 已用迷你代码实践
- [ ] 架构审查报告已阅读，决策已记录
- [ ] 内存布局分析已验证
- [ ] 所有代码和文档已写入 Obsidian

---

*AI 执行时间：约 25 分钟*  
*人类执行时间：约 2 小时*
