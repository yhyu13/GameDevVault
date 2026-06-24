---
tags: [routine/AI-tasks, topic/Nanite, day/Tuesday]
aliases: []
---

# 周二：AI 任务清单 — Nanite 专项技能突破

> **人类目标**：通过算法实现和数学推导，内化 Nanite 的 Cluster LOD 和 GPU-Driven 渲染原理。  
> **AI 任务**：生成练习题、解释数学、review 代码、提供直觉，绝不替写核心算法。

---

## 任务 1：Cluster LOD 数学练习题生成（AI 执行）

**输入**："给我生成 5 道关于 Nanite 所用数学的练习题，涵盖：Screen-space Error 计算、BVH 遍历、Cluster 合并、DAG 构建、GPU Instance Culling"

**AI 输出**：5 道练习题，每道包含：
- 题目描述（带具体数值）
- 建议解题时间
- 难度标签（Easy/Medium/Hard）
- 参考答案（你做完后再看）

**示例题目**：
> **Q1 (Easy)**：一个三角形在屏幕上的投影面积是 100 像素²，Nanite 的合并阈值为 200 像素²。该三角形是否会被合并到父 Cluster？为什么？

**你必须做**：在纸上或代码中完成所有题目，再核对答案。

---

## 任务 2：Visibility Buffer Shader 脚手架（AI 生成，你填充）

**输入**："我想写一个简化版 Visibility Buffer 的 fragment shader，只输出 primitive ID 和 barycentrics"

**AI 输出**：
```hlsl
// --- AI 生成的脚手架 ---
// TODO(HUMAN): 实现以下部分
// 1. 从 GPUScene 读取当前三角形的材质 ID
// 2. 计算 barycentric 坐标
// 3. 编码到 R32G32_UINT target（ID + barycentrics）
// 4. 处理 depth 写入

struct VisibilityOutput {
    uint2 Visibility : SV_Target0;  // PrimitiveID + Barycentrics
    float Depth : SV_Depth;
};

VisibilityOutput PS_Main(VS_OUTPUT input) {
    VisibilityOutput output;
    // ====== HUMAN: 在这里写你的代码 ======
    // hint: input.primitiveID, input.barycentrics
    // ======================================
    return output;
}
```

**你必须做**：填充所有 `// TODO(HUMAN)` 部分，运行并调试。

---

## 任务 3：你的 Cluster 构建代码 Review（AI 执行）

**输入**：你写完的简化版 Cluster 构建器代码（C++ 或 Python）

**AI 检查清单**：
- [ ] 是否处理了非流形边？（Nanite 要求 closed mesh）
- [ ] Cluster 大小是否均匀？（理想 128 triangles）
- [ ] 父子关系是否正确？（DAG 无环验证）
- [ ] 误差度量是否单调？（父节点误差 ≥ 子节点）
- [ ] 内存布局是否 cache-friendly？（连续存储）

**AI 输出**：发现的 bug 列表 + 修复建议（逐行）

**你必须做**：理解每个 bug 的根因，手动修复。

---

## 任务 4：概念直觉检查（AI 解释，你内化）

**AI 任务**：用类比解释核心概念

| 概念 | AI 解释类比 |
|------|------------|
| Cluster LOD | "就像 Google Maps 的卫星图。缩放时不是加载 10 张不同分辨率的图，而是加载一个巨大的虚拟图，根据视野只显示需要的块。Nanite 的 Cluster 就是地图的 '块'。" |
| GPU-Driven Rendering | "传统渲染是 CPU 告诉 GPU '画这个、画那个'。GPU-Driven 是 CPU 只告诉 GPU '这里有一大堆东西，你自己决定画哪些'。GPU 自己跑剔除、排序、绘制。" |
| Visibility Buffer | "传统 G-Buffer 存储颜色、法线、深度。Visibility Buffer 只存 '这是哪个三角形'。等需要 shading 时，再按需读取材质属性。像快递单号 vs 快递内容。" |

**你必须做**：用你自己的话向一个假想初级同事解释这些概念。

---

## 今日 AI 禁区

- ❌ 让 AI 写完整 Cluster 构建器代码
- ❌ 让 AI 直接给数学题的答案（先自己做）
- ❌ 让 AI 解释概念后你不做费曼输出
- ❌ 让 AI review 代码后直接应用修复（必须理解根因）

---

## 完成检查清单

- [ ] 5 道数学题已完成并核对
- [ ] Visibility Buffer Shader 核心逻辑已填充
- [ ] AI code review 的 bug 已理解并手动修复
- [ ] 3 个核心概念已用自己的话解释给假想同事
- [ ] 代码和数学笔记已写入 Obsidian

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 2.5 小时*  
*产出：5 道数学练习 + 1 个 Shader 练习 + 1 次 Code Review*
