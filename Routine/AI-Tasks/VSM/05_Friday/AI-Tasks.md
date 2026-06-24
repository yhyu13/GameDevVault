---
tags: [routine/AI-tasks, topic/VSM, day/Friday]
aliases: []
---

# 周五：AI 任务清单 — VSM 轻量复盘与整理

> **人类目标**：整理本周 VSM 学习笔记，更新知识库，规划下周。  
> **AI 任务**：生成测验、建议链接、总结数据，绝不替你思考。

---

## 任务 1：VSM 知识测验生成（AI 执行）

**AI 输出**：结构化测验

```markdown
## Q1 (TF)
VSM 的虚拟纹理页是预先全部分配好的，每帧只更新内容。
Answer: False
Explanation: VSM 是按需分配物理页。只有实际被光源照射到的区域才会分配物理页，未被照射的区域不占用内存。

## Q2 (SC)
VSM 相比传统 CSM 的最大优势是什么？
Options:
- A. 支持透明物体阴影
- B. 消除级间裂缝和内存浪费
- C. 支持更多光源数量
- D. 构建时间更短
Answer: B

## Q3 (MC)
以下哪些是 VSM 的当前限制？
Options:
- A. 不支持透明物体阴影
- B. 需要硬件支持稀疏纹理
- C. 动态光源的更新开销较大
- D. 不支持软阴影
- E. 与 Lumen 冲突
Answer: A, B, C

## Q4 (FB)
VSM 的核心思想是将传统 Cascade Shadow Map 的固定分辨率分配改为 ______ 分配，通过 ______ 技术实现按需加载。
Answer: 按需, virtual texture / page table
```

**然后**：使用 `quiz-html-generator` 转 HTML。

**你必须做**：完成测验，复习错题。

---

## 任务 2：笔记链接建议（AI 执行，你确认）

**AI 建议**：
- [[VSM-论文笔记]] → [[Lumen-VT-显存调度]]：两者都使用虚拟纹理技术，共享 Page Pool 思想
- [[VSM-PageTable]] → [[C++-内存布局]]：Page Table Entry 的紧凑内存设计
- [[VSM-ShadowShader]] → [[Shader-后处理]]：阴影采样与软阴影算法
- [[VSM-工具脚本]] → [[Python-工具链]]：自动化阴影分析工具

**你必须做**：检查合理性，手动添加链接。

---

## 任务 3：下周规划（AI 执行，你补充）

**AI 建议**：
- 周一：VSM 与 Lumen 的协同渲染（阴影如何影响 GI）
- 周二：软阴影算法（PCSS、VSM 方差阴影、ESM）
- 周三：对比观察 VSM vs CSM 的游戏表现
- 周四：写一个简化版 VSM 分配器（Page Table + 物理池）
- 周末：mini-VSM 渲染器（方向光 + 虚拟阴影 + PCF 采样）

**你必须做**：根据实际工作负荷调整。

---

## 完成检查清单

- [ ] VSM 知识测验已完成（得分 ≥80）
- [ ] 错题已复习
- [ ] 笔记链接已手动添加
- [ ] 下周计划已写入 Obsidian 周模板

---

*AI 执行时间：约 20 分钟*  
*人类执行时间：约 1 小时*
