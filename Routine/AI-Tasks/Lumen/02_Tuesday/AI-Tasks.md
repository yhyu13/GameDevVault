---
tags: [routine/AI-tasks, topic/Lumen, day/Tuesday]
aliases: []
---

# 周二：AI 任务清单 — Lumen 专项技能突破

> **人类目标**：通过 Shader 练习和数学推导，内化 Lumen 的核心技术原理。  
> **AI 任务**：生成练习题、解释数学、review 代码、提供直觉，绝不替写 Shader。

---

## 任务 1：Lumen 相关数学练习题生成（AI 执行）

**输入**："给我生成 5 道关于 Lumen 所用数学的练习题，涵盖：Sphere Tracing、球谐函数、蒙特卡洛积分、向量反射、距离场查询"

**AI 输出**：5 道练习题，每道包含：
- 题目描述
- 建议解题时间
- 难度标签（Easy/Medium/Hard）
- 参考答案（你做完后再看）

**示例题目**：
> **Q1 (Easy)**：给定一个单位球体的 SDF 函数 `f(p) = |p| - 1`，光线从 `ro = (2, 0, 0)` 沿方向 `rd = (-1, 0, 0)` 出发。用 Sphere Tracing 求前 3 步的步进位置和步长。

**你必须做**：在纸上或代码中完成所有题目，再核对答案。

---

## 任务 2：Shader 脚手架生成（AI 执行，你填充）

**输入**："我想写一个简化版 Lumen Surface Cache 的 fragment shader，只缓存直接光照"

**AI 输出**：
```hlsl
// --- AI 生成的脚手架 ---
// TODO(HUMAN): 实现以下部分
// 1. 计算当前像素的表面法线和世界坐标
// 2. 查询 Shadow Map 得到遮挡信息
// 3. 计算直接光照 (Diffuse + Specular)
// 4. 编码到 RGBA8 缓存
// 5. 处理多光源叠加

struct SurfaceCacheOutput {
    float4 DirectLighting : SV_Target0;
    float4 NormalDepth : SV_Target1;
};

SurfaceCacheOutput PS_Main(VS_OUTPUT input) {
    SurfaceCacheOutput output;
    // ====== HUMAN: 在这里写你的代码 ======
    // hint: 使用 input.worldPos, input.normal, _LightDir
    // ======================================
    return output;
}
```

**你必须做**：填充所有 `// TODO(HUMAN)` 部分，运行并调试。

---

## 任务 3：你的 Shader 代码 Review（AI 执行）

**输入**：你写完的 HLSL/GLSL 代码（粘贴完整文件）

**AI 检查清单**：
- [ ] 除零保护（除法前检查分母）
- [ ] 未初始化变量
- [ ] 分支发散（在 GPU 上避免动态分支）
- [ ] 精度问题（float vs half 使用场景）
- [ ] 越界访问（数组索引、纹理采样）
- [ ] Lumen 特定：是否考虑了 Surface Cache 的 atlas 坐标映射？

**AI 输出**：发现的 bug 列表 + 修复建议（逐行）

**你必须做**：理解每个 bug 的根因，手动修复，不直接 copy AI 的修复代码。

---

## 任务 4：概念直觉解释（AI 执行，你内化）

**输入**：你感到困惑的 Lumen 概念

**AI 输出**：用类比解释

| 概念 | AI 解释类比 |
|------|------------|
| SDF Sphere Tracing | "你在黑暗中走路，每次喊一声问'前面多远有墙？'，然后走那么远的距离。如果撞上墙，说明距离信息准确；如果还没撞上，继续问。" |
| Radiance Cache | "就像地图的缩略图。你不需要看全分辨率地图来知道城市在哪，缩略图就够了。Radiance Cache 就是光照的'缩略图'。" |
| Surface Cache | "每个表面有一个便签条，上面写着'如果光照打到我这里会是什么颜色'。光线追踪时直接读便签条，不用重新计算。" |

**你必须做**：用你自己的话向一个假想的初级同事解释这些概念（费曼检验）。

---

## 今日 AI 禁区

- ❌ 让 AI 写完整 Shader 代码
- ❌ 让 AI 直接给数学题的答案（先自己做）
- ❌ 让 AI 解释概念后你不做费曼输出
- ❌ 让 AI review 代码后直接应用修复（必须理解根因）

---

## 完成检查清单

- [ ] 5 道数学题已完成并核对
- [ ] Shader 脚手架已填充核心逻辑
- [ ] AI code review 的 bug 已理解并手动修复
- [ ] 3 个核心概念已用自己的话解释给假想同事
- [ ] 代码和数学笔记已写入 Obsidian

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 2.5 小时*  
*产出：5 道数学练习 + 1 个 Shader 练习 + 1 次 Code Review*
