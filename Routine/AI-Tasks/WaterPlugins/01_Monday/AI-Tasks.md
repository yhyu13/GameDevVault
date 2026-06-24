---
tags: [routine/AI-tasks, topic/WaterPlugins, day/Monday]
aliases: []
---

# 周一：AI 任务清单 — Water Plugins 前沿技术输入

> **人类目标**：精读 Water Plugins 相关论文/演讲，理解水体渲染与模拟的核心创新。  
> **AI 任务**：提供脚手架、解释障碍、生成问题，绝不替读论文。

---

## 任务 1：论文预读引导（AI 执行）

**输入**：Water Plugins 相关论文（如《Real-time Water Rendering》或《Simulating Ocean Water》或 UE5 Water Plugin 文档）

**AI 输出**：
1. 一段 **150 字摘要**
2. **3 个引导问题**：
   - Q1: Gerstner Waves 与 FFT-based 海洋模拟的优缺点对比？
   - Q2: Water Plugin 中的 Buoyancy 系统是如何与物理引擎协同的？
   - Q3: 水体渲染中如何处理反射、折射和焦散（Caustics）？
3. **重点章节标记**：先读 Gerstner Wave 基础，再读 Water Body 组件架构，最后读 Performance Optimization

**交付物**：`Water-Reading-Guide.md`

---

## 任务 2：波浪模拟算法对比（AI 执行，你验证）

**输入**：Gerstner Waves vs FFT vs Sine Wave 的对比

**AI 输出**：
1. Gerstner Waves：基于物理的圆形波形，适合开放海洋，参数可控
2. FFT：基于频谱的复杂波浪，更真实但计算量更大
3. Sine Wave：最简单，但视觉效果不够真实
4. 各种方法的适用场景（实时 vs 离线、开放海洋 vs 小池塘）

**你必须做**：写一个小型 Wave 生成器，对比三种方法的效果。

---

## 任务 3：面试谈资生成（AI 执行，你 rehearse）

**AI 输出**：
1. **30 秒版本**：Water Plugins 使用 Gerstner Waves 模拟开放海洋，通过参数控制波高、波长、方向，结合物理浮力系统实现真实的船体交互。
2. **2 分钟版本**：背景 → 波浪模拟方法对比 → Gerstner Waves 原理 → Water Body 组件 → Buoyancy 系统 → 与 Chaos 的协同 → 局限
3. **3 个追问**：
   - "Gerstner Waves 和 FFT 在性能上差多少？"
   - "Water Plugin 的 shoreline 处理怎么做？"
   - "如何在低端设备上优化水体渲染？"

**你必须做**：rehearse aloud。

---

## 任务 4：源码地图绘制（AI 执行，你验证）

**输入**："UE5 Water Plugin 的波浪计算入口在哪？从 Water Body 到 Buoyancy 的调用链？"

**AI 输出**：
1. `AWaterBody::UpdateWater()` 调用链
2. 关键文件：`WaterBody.cpp`, `GerstnerWave.cpp`, `BuoyancyComponent.cpp`
3. 与 Chaos Physics 的交互点

**你必须做**：在 UE5 源码中验证。

---

## 今日 AI 禁区

- ❌ 让 AI 替读论文
- ❌ 让 AI 替写笔记
- ❌ 让 AI 生成代码路径不验证
- ❌ 让 AI 替准备面试回答

---

## 完成检查清单

- [ ] AI 阅读指南已生成并打印
- [ ] 波浪算法对比已手写代码验证
- [ ] 面试谈资已 rehearse aloud
- [ ] 源码路径已验证
- [ ] 所有内容已写入 Obsidian 笔记

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2 小时*
