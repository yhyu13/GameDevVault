---
tags: [routine/AI-tasks, topic/WaterPlugins, day/Friday]
aliases: []
---

# 周五：AI 任务清单 — Water Plugins 轻量复盘与整理

> **人类目标**：整理本周 Water 学习笔记，更新知识库，规划下周。  
> **AI 任务**：生成测验、建议链接、总结数据，绝不替你思考。

---

## 任务 1：Water Plugins 知识测验生成（AI 执行）

**AI 输出**：结构化测验

```markdown
## Q1 (TF)
Gerstner Waves 的位移只包含 y 方向（垂直方向）。
Answer: False
Explanation: Gerstner Waves 不仅改变 y 方向，还改变了 x 和 z 方向（水平方向），模拟水粒子的圆周运动。

## Q2 (SC)
Water Plugin 中，哪种水体类型最适合用 Gerstner Waves？
Options:
- A. 小池塘（Pond）
- B. 河流（River）
- C. 开放海洋（Ocean）
- D. 游泳池
Answer: C

## Q3 (MC)
以下哪些是 Water Plugin 的渲染特性？
Options:
- A. 反射（Reflection）
- B. 折射（Refraction）
- C. 焦散（Caustics）
- D. 体积光（Volumetric Light）
- E. 泡沫（Foam）
Answer: A, B, C, E

## Q4 (FB)
Water Plugin 的 Buoyancy 系统基于 ______ 原理，浮力等于物体 ______ 的水的重量。
Answer: 阿基米德, 排开
```

**然后**：使用 `quiz-html-generator` 转 HTML。

**你必须做**：完成测验，复习错题。

---

## 任务 2：笔记链接建议（AI 执行，你确认）

**AI 建议**：
- [[Water-GerstnerWave]] → [[Lumen-反射系统]]：水面的反射与 Lumen 的全局反射协同
- [[Water-Buoyancy]] → [[ChaosPhysics-刚体动力学]]：浮力与物理引擎的交互
- [[Water-Shader]] → [[03-Shader与特效案例集]]：水体 Shader 的折射/焦散效果
- [[Water-工具脚本]] → [[Python-可视化]]：波浪参数空间的可视化分析

**你必须做**：检查合理性，手动添加链接。

---

## 任务 3：下周规划（AI 执行，你补充）

**AI 建议**：
- 周一：FFT-based Ocean 模拟（从频谱到波浪）
- 周二：写一个 FFT Ocean 的 Compute Shader
- 周三：观察游戏中 shore 交互和泡沫效果
- 周四：水下渲染（Underwater Post-Process、焦散体积光）
- 周末：mini-Ocean 渲染器（Gerstner + FFT 混合 + 简单浮力）

**你必须做**：根据实际工作负荷调整。

---

## 完成检查清单

- [ ] Water 知识测验已完成（得分 ≥80）
- [ ] 错题已复习
- [ ] 笔记链接已手动添加
- [ ] 下周计划已写入 Obsidian 周模板

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 1 小时*
