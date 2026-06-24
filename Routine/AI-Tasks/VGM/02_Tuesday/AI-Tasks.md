---
tags: [routine/AI-tasks, topic/VGM, day/Tuesday]
aliases: []
---

# 周二：AI 任务清单 — VGM 专项技能突破

> **人类目标**：通过 Mesh Shader 编程和算法实现，内化 VGM 的 GPU-Driven 渲染原理。  
> **AI 任务**：生成练习题、解释数学、review 代码、提供直觉，绝不替写核心算法。

---

## 任务 1：Meshlet 划分算法练习题（AI 执行）

**输入**："给我生成 5 道关于 Meshlet 和 Mesh Shader 的练习题，涵盖：Meshlet 划分（METIS/贪心算法）、Task Shader 剔除、Work Group 大小选择、内存带宽计算、与 Compute Shader 的对比"

**AI 输出**：5 道练习题

**示例题目**：
> **Q1 (Easy)**：一个 Mesh 有 1024 个顶点，按 NVidia 推荐的 64 顶点/Meshlet 标准，最多需要多少个 Meshlet？如果每个 Meshlet 有 128 个 primitive，那么该 Mesh 的 primitive 上限是多少？

**你必须做**：在纸上完成所有题目。

---

## 任务 2：Mesh Shader 脚手架（AI 生成，你填充）

**输入**："我想写一个最小可运行的 Mesh Shader，只画一个三角形"

**AI 输出**：
```hlsl
// Task Shader (可选，只做 1 个 Task)
[NumThreads(1, 1, 1)]
void main() {
    DispatchMesh(1, 1, 1, payload);  // 1 meshlet
}

// Mesh Shader
struct MeshOutput {
    float4 position : SV_POSITION;
    float3 color : COLOR;
};

[NumThreads(3, 1, 1)]  // 1 triangle = 3 vertices
[OutputTopology("triangle")]
void main(out vertices MeshOutput verts[3], out indices uint3 prims[1]) {
    // ====== HUMAN: 在这里写你的代码 ======
    // 设置 3 个顶点的位置和颜色
    // 设置 1 个三角形的索引
    // ======================================
}
```

**你必须做**：填充 TODO，编译运行。

---

## 任务 3：你的 Mesh Shader 代码 Review（AI 执行）

**AI 检查清单**：
- [ ] `OutputTopology` 是否正确（triangle vs line）
- [ ] 顶点数是否超过 `MaxNumVertices`（如 256）
- [ ] Primitive 数是否超过 `MaxNumPrimitives`（如 256）
- [ ] Payload 结构是否正确传递
- [ ] 是否考虑了 subgroup 优化（Wave size）

**你必须做**：理解每个建议，手动修复。

---

## 任务 4：概念直觉（AI 解释，你内化）

| 概念 | AI 解释类比 |
|------|------------|
| Meshlet | "就像乐高积木。一个大模型被拆成很多小块（Meshlet），每块可以独立处理。GPU 一次处理一块，不需要 CPU 指挥。" |
| Task Shader | "就像建筑工地的调度员。Task Shader 先看一眼哪些 Meshlet 在视野内，只把那些‘需要建’的派给 Mesh Shader。" |
| Mesh Shader vs Vertex Shader | "传统 Vertex Shader 是‘流水线上的工人，每个只处理一个顶点’。Mesh Shader 是‘小组长，一次负责一整块（Meshlet）的所有顶点’。" |

**你必须做**：用自己的话解释给假想同事。

---

## 今日 AI 禁区

- ❌ 让 AI 写完整 Mesh Shader
- ❌ 让 AI 直接给数学题答案
- ❌ 不做费曼输出
- ❌ 直接应用修复不理解根因

---

## 完成检查清单

- [ ] 5 道数学题已完成并核对
- [ ] Mesh Shader 核心逻辑已填充
- [ ] AI code review 的 bug 已理解并手动修复
- [ ] 3 个核心概念已用自己的话解释
- [ ] 代码和笔记已写入 Obsidian

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 2.5 小时*
