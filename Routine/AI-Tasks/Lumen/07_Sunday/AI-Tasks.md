---
tags: [routine/AI-tasks, topic/Lumen, day/Sunday]
aliases: []
---

# 周日：AI 任务清单 — Lumen 项目实战与复盘

> **人类目标**：完成 mini-Lumen Demo 的最终集成，输出文档，做周复盘。  
> **AI 任务**：协助 debug、润色文档、生成复盘模板，绝不写核心代码。

---

## 上午：项目收尾（2h）

### 任务 1：集成测试辅助（AI 执行）

**输入**："我的 mini-Lumen 有三个模块：SDFGenerator、RayMarcher、SurfaceCache。帮我设计一个集成测试计划，确保它们能协同工作"

**AI 输出**：测试矩阵

| 测试场景 | 输入 | 预期输出 | 验证方法 |
|----------|------|----------|---------|
| SDF 生成 | 简单 Cube Mesh | 正确的距离场，中心为负，外部为正 | 可视化切片 |
| Ray Marching | 从外部射向 Cube | 命中点 + 法线正确 | 与解析解对比 |
| Surface Cache | 单方向光照射 Cube | 正面亮、背面暗（间接光） | 截图对比 |
| 端到端 | 移动光源 | 间接光随光源移动实时更新 | 录屏观察 |

**AI 还会生成**：简单的测试代码框架（用 assert 验证）

**你必须做**：运行每个测试，记录实际结果，与预期对比。发现差异时自己 debug。

---

### 任务 2：性能 Baseline（AI 执行，你测量）

**输入**："帮我设计测量 mini-Lumen 性能的 benchmark 方案"

**AI 输出**：
1. **测量指标**：FPS、GPU Time、CPU Time、内存占用、纹理带宽
2. **测量工具**：RenderDoc、Tracy、std::chrono
3. **Benchmark 场景**：
   - 场景 A：简单 Cube（1 draw call）
   - 场景 B：复杂场景（100 个 Mesh）
   - 场景 C：动态光源（每帧移动）
4. **对比基准**：
   - 关闭 GI（仅直接光）
   - 开启 GI（你的 mini-Lumen）
   - 目标：开销 < 20% of 直接光

**你必须做**：实际运行 benchmark，记录数据。AI 不能替你运行代码。

---

## 下午：文档与复盘（1-2h）

### 任务 3：项目文档生成（AI 执行，你填充）

**输入**：你的项目结构和核心代码片段

**AI 输出**：README 模板

```markdown
# mini-Lumen
> 一个简化版 Lumen 实现，用于学习 Software Ray Tracing 和 Surface Cache 原理

## 特性
- [x] SDF 生成（从 Mesh）
- [x] Software Ray Marching
- [x] Surface Cache 模拟
- [ ] Radiance Cache（TODO）
- [ ] Hardware RT fallback（TODO）

## 构建
```bash
mkdir build && cd build
cmake .. -DENABLE_DX12=ON
make -j
```

## 性能
| 场景 | 直接光 | +mini-Lumen | 开销 |
|------|--------|-------------|------|
| 1 Cube | 2.1ms | 2.4ms | +14% |
| 100 Mesh | 3.5ms | 4.2ms | +20% |

## 学习笔记
见 [Obsidian Vault](link)

## 致谢
基于 UE5 Lumen (SIGGRAPH 2021) 的简化实现
```

**你必须做**：填写所有 `[TODO]` 和测量数据，确保准确性。

---

### 任务 4：周复盘辅助（AI 执行，你补充）

**输入**：你本周的所有日记条目和项目数据

**AI 输出**：结构化复盘

#### 数据总结
| 维度 | 目标 | 实际 | 评分 |
|------|------|------|------|
| 论文输入 | 1 篇 | 1 篇 (Lumen) | 10/10 |
| 源码分析 | 1 篇 | 1 篇 (UE5 VT) | 9/10 |
| Shader 练习 | 1 个 | 1 个 (Surface Cache) | 8/10 |
| 工程化 | 1 个工具 | 1 个 (纹理检查) | 9/10 |
| 项目输出 | 1 个 Demo | 1 个 (mini-Lumen) | 8/10 |
| 社交 | 1 次 | 1 次 (GitHub Issue) | 7/10 |

#### AI 发现的模式
- 你在 SDF 数学上花了额外时间 → 这是值得深挖的方向
- 你的 Shader 调试效率较低 → 建议学习 RenderDoc 高级用法
- 你的博客输出为 0 → 建议下周安排 1 小时写博客

#### 下周建议
1. 重点：SDF 生成算法（弥补本周薄弱点）
2. 新增：RenderDoc 帧分析教程（提升调试效率）
3. 保持：论文精读 + 源码分析节奏

**你必须做**：补充 AI 无法感知的主观体验（如 "周二写 Shader 时突然理解了间接光的概念，这种顿悟感很重要"）。

---

## 今日 AI 禁区

- ❌ 让 AI 替你运行测试和 benchmark
- ❌ 让 AI 替你写项目文档的核心技术描述
- ❌ 让 AI 替你写周复盘日记（日记必须是你的反思）
- ❌ 让 AI 替你决定下周计划（AI 建议，你决策）

---

## 完成检查清单

- [ ] mini-Lumen 集成测试全部通过
- [ ] 性能 benchmark 已运行，数据已记录
- [ ] README 文档已填写并发布到 GitHub
- [ ] 周复盘已完成，主观体验已补充
- [ ] 下周计划已调整并写入 Obsidian
- [ ] 所有链接（GitHub、博客、Obsidian）已更新到知识库

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 3-4 小时*  
*产出：1 个完整 Demo + 1 份文档 + 1 次周复盘 + 下周计划*
