---
tags: [routine/AI-tasks, topic/VSM, day/Tuesday]
aliases: []
---

# 周二：AI 任务清单 — VSM 专项技能突破

> **人类目标**：通过 Shadow Map 编程和数学推导，内化 VSM 的虚拟化阴影原理。  
> **AI 任务**：生成练习题、解释数学、review 代码、提供直觉，绝不替写核心算法。

---

## 任务 1：Shadow Map 数学练习题生成（AI 执行）

**输入**："给我生成 5 道关于 VSM 和 Shadow Mapping 的练习题，涵盖：视锥体投影、深度偏差（bias）、PCF 采样、Page Table 索引计算、级间过渡（cascade blending）"

**AI 输出**：5 道练习题

**示例题目**：
> **Q1 (Easy)**：一个方向光源的 VSM 使用 4096×4096 的虚拟分辨率，实际每页为 128×128。总共需要多少个物理页？如果场景中只有 10% 的区域被实际照射，物理页占用率是多少？

**你必须做**：在纸上完成所有题目。

---

## 任务 2：VSM Page Table Shader 脚手架（AI 生成，你填充）

**输入**："我想写一个简化版 VSM 的 Page Table 查找 shader，输入虚拟 UV，输出物理 UV"

**AI 输出**：
```hlsl
// VSM Page Table 查找（简化版）
float2 GetPhysicalUV(float2 virtualUV, uint shadowMapID) {
    // TODO(HUMAN): 实现以下逻辑
    // 1. 将 virtualUV 转换为 Page Table 的 texel 坐标
    // 2. 从 PageTableTexture 中读取物理页索引
    // 3. 将物理页索引转换为 PhysicalAtlas 的 UV
    // 4. 处理未分配页（fallback 到默认阴影）
}
```

**你必须做**：填充 TODO，编译运行。

---

## 任务 3：你的 Shadow Map Shader 代码 Review（AI 执行）

**AI 检查清单**：
- [ ] 深度偏差（bias）是否正确处理？（acne vs peter-panning）
- [ ] PCF 采样范围是否足够？（软阴影质量）
- [ ] VSM 的 Page Table 查找是否考虑了 mipmap 层级？
- [ ] 级间过渡（cascade blending）是否平滑？
- [ ] 透明物体是否被正确处理？（VSM 不支持透明阴影）

**你必须做**：理解每个建议，手动修复。

---

## 任务 4：概念直觉（AI 解释，你内化）

| 概念 | AI 解释类比 |
|------|------------|
| Virtual Shadow Map | "就像地图 App 的卫星图。你看哪里，它加载哪里的高清图；不看的地方，不浪费内存。VSM 的 '卫星图' 就是阴影。" |
| Page Table | "就像图书馆的索引卡。Page Table 告诉你 '这本书在第 3 书架第 5 层'。物理纹理池就是书架。" |
| Cascade Blending | "就像两个灯泡的照明区域交界。如果直接切换，交界会很硬。Cascade Blending 是在交界处让两个阴影 '渐变色'。" |

**你必须做**：用自己的话解释给假想同事。

---

## 今日 AI 禁区

- ❌ 让 AI 写完整 Shadow Map Shader
- ❌ 让 AI 直接给数学题答案
- ❌ 不做费曼输出
- ❌ 直接应用修复不理解根因

---

## 完成检查清单

- [ ] 5 道数学题已完成并核对
- [ ] VSM Page Table 查找逻辑已填充
- [ ] AI code review 的 bug 已理解并手动修复
- [ ] 3 个核心概念已用自己的话解释
- [ ] 代码和笔记已写入 Obsidian

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 2.5 小时*
