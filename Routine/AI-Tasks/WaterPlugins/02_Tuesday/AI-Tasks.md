---
tags: [routine/AI-tasks, topic/WaterPlugins, day/Tuesday]
aliases: []
---

# 周二：AI 任务清单 — Water Plugins 专项技能突破

> **人类目标**：通过水体 Shader 编程和数学推导，内化 Water Plugin 的波浪模拟与渲染原理。  
> **AI 任务**：生成练习题、解释数学、review 代码、提供直觉，绝不替写核心算法。

---

## 任务 1：波浪数学练习题生成（AI 执行）

**输入**："给我生成 5 道关于波浪模拟的练习题，涵盖：Gerstner Waves 参数计算、波长-波速关系、法线推导、焦散投影、浮力计算（阿基米德原理）"

**AI 输出**：5 道练习题

**示例题目**：
> **Q1 (Easy)**：Gerstner Wave 的位移公式为 `P(x,z) = (x + Q·A·D.x·cos(D·(x,z)·ω + φ·t), y + A·sin(D·(x,z)·ω + φ·t), z + Q·A·D.z·cos(...))`。当 Q=1, A=0.5, ω=2, D=(1,0), t=0, x=0, z=0 时，位移后的位置 P 是什么？

**你必须做**：在纸上完成所有题目。

---

## 任务 2：Gerstner Wave Shader 脚手架（AI 生成，你填充）

**输入**："我想写一个简化版 Gerstner Wave 的 vertex shader，输入 worldPos，输出 displaced position + wave normal"

**AI 输出**：
```hlsl
// Gerstner Wave Shader（简化版）
struct WaveParams {
    float amplitude;
    float wavelength;
    float speed;
    float2 direction;
};

float3 DisplaceVertex(float3 worldPos, WaveParams wave) {
    // TODO(HUMAN): 实现 Gerstner Wave 位移
    // 1. 计算相位：dot(direction, worldPos.xz) * omega + phi * time
    // 2. 计算 x/z 偏移：Q * A * D * cos(phase)
    // 3. 计算 y 偏移：A * sin(phase)
    // 4. 返回新的 worldPos
}

float3 CalculateWaveNormal(float3 worldPos, WaveParams wave) {
    // TODO(HUMAN): 实现法线计算
    // 1. 对 Gerstner Wave 公式求偏导数（dx, dz）
    // 2. 叉乘得到法线
    // 3. 归一化
}
```

**你必须做**：填充 TODO，编译运行。

---

## 任务 3：你的 Water Shader 代码 Review（AI 执行）

**AI 检查清单**：
- [ ] 波浪相位计算是否正确？（角度单位：弧度 vs 度）
- [ ] 多波叠加时是否考虑了波长/波速的一致性？
- [ ] 法线计算是否考虑了所有叠加波的贡献？
- [ ] 反射/折射的采样 UV 是否考虑了扰动？
- [ ] 焦散（Caustics）是否考虑了水下光线的会聚？

**你必须做**：理解每个建议，手动修复。

---

## 任务 4：概念直觉（AI 解释，你内化）

| 概念 | AI 解释类比 |
|------|------------|
| Gerstner Waves | "就像看海上的波浪。每个水粒子不是上下直动，而是做圆周运动。Gerstner Wave 就是描述这个圆周运动的数学公式。" |
| 焦散（Caustics） | "就像把放大镜放在阳光下，地上会出现光斑。水面的波浪相当于无数个小放大镜，把阳光聚焦到海底，形成闪烁的光斑。" |
| Buoyancy | "就像船浮在水上。浮力等于排开水的重量。水波动时，船底接触的水量变化，浮力随之变化，所以船会随波起伏。" |

**你必须做**：用自己的话解释给假想同事。

---

## 今日 AI 禁区

- ❌ 让 AI 写完整 Water Shader
- ❌ 让 AI 直接给数学题答案
- ❌ 不做费曼输出
- ❌ 直接应用修复不理解根因

---

## 完成检查清单

- [ ] 5 道数学题已完成并核对
- [ ] Gerstner Wave Shader 核心逻辑已填充
- [ ] AI code review 的 bug 已理解并手动修复
- [ ] 3 个核心概念已用自己的话解释
- [ ] 代码和笔记已写入 Obsidian

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 2.5 小时*
