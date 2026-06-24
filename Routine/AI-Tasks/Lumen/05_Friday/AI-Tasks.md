---
tags: [routine/AI-tasks, topic/Lumen, day/Friday]
aliases: []
---

# 周五：AI 任务清单 — Lumen 轻量复盘与整理

> **人类目标**：整理本周 Lumen 学习笔记，更新知识库，规划下周。  
> **AI 任务**：生成测验、建议链接、总结数据，绝不替你思考。

---

## 任务 1：Lumen 知识测验生成（AI 执行）

**输入**：你本周的 Lumen 笔记（论文笔记 + 源码分析 + Shader 练习）

**AI 输出**：结构化测验内容，格式如下：

```markdown
## Q1 (TF)
Lumen 的 Surface Cache 存储的是最终光照结果，可以直接作为屏幕输出。
Answer: False
Explanation: Surface Cache 存储的是直接光照（含阴影），最终光照需要结合 Radiance Cache 的间接光和镜面反射。

## Q2 (SC)
Lumen 中哪种结构用于软件光线追踪？
Options:
- A. Lightmap
- B. Signed Distance Field (SDF)
- C. Voxel Grid
- D. BVH
Answer: B

## Q3 (MC)
哪些操作发生在 Lumen 的 RenderThread 上？
Options:
- A. Mesh SDF 生成
- B. Surface Cache 更新
- C. 屏幕空间探针放置
- D. 游戏逻辑更新
Answer: B, C

## Q4 (FB)
在 Lumen 的分层结构中，______ 用于近场高分辨率表面，______ 用于远场低频光照近似。
Answer: Surface Cache, Radiance Cache
```

**然后**：使用 `quiz-html-generator` skill 将以上内容转换为交互式 HTML 测验文件。

**你必须做**：亲自完成测验，记录得分，复习错题。

---

## 任务 2：笔记链接建议（AI 执行，你确认）

**输入**：你本周写的所有 Lumen 相关笔记（粘贴 Obsidian 笔记内容或链接）

**AI 输出**：建议建立的双向链接列表：

| 笔记 A | 笔记 B | 建议链接原因 |
|--------|--------|-------------|
| [[Lumen-SIGGRAPH-2021]] | [[UE5-VT-显存调度]] | VT 是 Lumen Surface Cache 的底层支撑 |
| [[Lumen-SIGGRAPH-2021]] | [[体积云-Volumetric-Cloud]] | 体积云也可使用 Radiance Cache 做光照 |
| [[体积云-Volumetric-Cloud]] | [[Ray-Marching-Optimization]] | 体积云的 Ray Marching 与 Lumen 的 SDF tracing 有共同优化技巧 |
| [[UE5-VT-显存调度]] | [[性能优化-DrawCall]] | 大规模场景下纹理流送与 DrawCall 优化需协同 |

**你必须做**：检查每个建议的合理性，手动添加 `[[链接]]`，不盲目采纳。

---

## 任务 3：周数据总结（AI 执行，你补充）

**输入**：你的本周日记条目（粘贴或描述）

**AI 输出**：数据化总结

| 指标 | 本周 | 目标 | 状态 |
|------|------|------|------|
| 论文精读 | 1 篇 (Lumen) | 1 篇 | ✅ |
| 源码分析 | 1 篇 (VT) | 1 篇 | ✅ |
| Shader 练习 | 1 个 (Surface Cache) | 1 个 | ✅ |
| 数学练习 | 5 题 | 5 题 | ✅ |
| 工具脚本 | 1 个 (纹理检查) | 1 个 | ✅ |
| 测验得分 | 80/100 | ≥80 | ✅ |
| 断更天数 | 0 | 0 | ✅ |

**AI 还发现**：
- 你在 "Radiance Cache 更新频率" 上花了额外 30 分钟，说明这是薄弱点
- 建议下周重点：SDF 生成算法

**你必须做**：补充 AI 无法感知的主观信息（"周三打游戏时突然理解了间接光"），这些是 AI 分析不了的。

---

## 任务 4：下周 Lumen 学习规划（AI 执行，你调整）

**输入**："基于本周学习，帮我规划下周 Lumen 深入方向"

**AI 输出**：建议规划

| 日期 | 主题 | 具体目标 | 关联本周薄弱点 |
|------|------|----------|---------------|
| 周一 | SDF 生成算法 | 精读《Fast Construction of Accurate SDF》 | 本周对 SDF 原理理解不够深 |
| 周二 | SDF 实现 | 写一个简化版 Mesh-to-SDF 转换器 | 实践内化 |
| 周三 | 游戏观察 | 对比观察 UE5 游戏 vs 非 UE5 游戏的 GI 差异 | 建立直觉 |
| 周四 | 多线程优化 | 实现并行 SDF 更新 | 工程化落地 |
| 周五 | 复盘 | 生成 SDF 专题测验 | 巩固 |
| 周末 | 项目 | 将 SDF 集成到你的 mini-Lumen Demo | 端到端输出 |

**你必须做**：根据实际工作负荷和个人兴趣调整。如果下周有 release 压力，削减任务量。

---

## 今日 AI 禁区

- ❌ 让 AI 替你写周复盘日记（日记必须是你自己的反思）
- ❌ 让 AI 替你决定下周学什么（AI 建议，你决策）
- ❌ 只做测验不复习错题（错题才是学习机会）
- ❌ 盲目采纳 AI 的链接建议（必须理解为什么链接）

---

## 完成检查清单

- [ ] Lumen 知识测验已生成并完成（得分 ≥80）
- [ ] 错题已复习，薄弱点已标记
- [ ] 笔记双向链接已手动添加（至少 3 条）
- [ ] 周数据总结已补充主观信息
- [ ] 下周规划已调整并写入 Obsidian 周模板

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 1 小时*  
*产出：1 个 HTML 测验 + 笔记链接更新 + 周总结 + 下周规划*
