---
tags: [routine/AI-tasks, topic/VSM, day/Monday]
aliases: []
---

# 周一：AI 任务清单 — VSM 前沿技术输入

> **人类目标**：精读 VSM（Virtual Shadow Maps）相关论文/演讲，理解虚拟化阴影映射的核心创新。  
> **AI 任务**：提供脚手架、解释障碍、生成问题，绝不替读论文。

---

## 任务 1：论文预读引导（AI 执行）

**输入**：VSM 相关论文（《Virtual Shadow Maps in Unreal Engine 5》或 GDC 2022 演讲）

**AI 输出**：
1. 一段 **150 字摘要**（核心问题 + 方法 + 结果）
2. **3 个引导问题**：
   - Q1: VSM 如何将 Virtual Texture 的思想应用到 Shadow Maps 上？
   - Q2: VSM 的 Page Table 与 Lumen 的 VT 系统有何异同？
   - Q3: VSM 如何解决传统 Cascade Shadow Maps 的过渡裂缝和内存爆炸问题？
3. **重点章节标记**：先读 Section 3 (Virtual Shadow Map 原理)，再读 Section 4 (Page Table & Allocation)，最后读 Section 5 (Performance Analysis)

**交付物**：`VSM-Reading-Guide.md`

---

## 任务 2：VSM 算法对比解释（AI 执行，你验证）

**输入**：VSM vs CSM vs SDSM 的对比表格

**AI 输出**：
1. 传统 CSM 的瓶颈：级数固定、内存浪费、级间裂缝
2. VSM 的解决方案：按需分配、虚拟化、稀疏纹理
3. SDSM（Sample Distribution Shadow Maps）与 VSM 的区别

**你必须做**：画一张自己的对比图，确认理解。

---

## 任务 3：面试谈资生成（AI 执行，你 rehearse）

**AI 输出**：
1. **30 秒版本**：VSM 是 UE5 的虚拟化阴影系统，通过按需分配虚拟纹理页来替代传统 Cascade，解决内存浪费和级间裂缝。
2. **2 分钟版本**：背景 → CSM 瓶颈 → VT 思想迁移 → Page Table 机制 → 与 Nanite/Lumen 的协同 → 局限
3. **3 个追问**：
   - "VSM 和 Lumen 的 VT 共享物理纹理池吗？"
   - "VSM 如何处理透明物体？"
   - "VSM 的 fallback 是什么？"

**你必须做**：rehearse aloud。

---

## 任务 4：源码地图绘制（AI 执行，你验证）

**输入**："VSM 在 UE5 中的渲染管线入口在哪？从光源视角到最终屏幕的完整调用链？"

**AI 输出**：
1. `FVirtualShadowMap::RenderVirtualShadowMaps` 调用链
2. 关键文件：`VirtualShadowMaps.cpp`, `ShadowMapAllocation.cpp`, `PageTableManager.cpp`
3. 每步的一句话职责说明

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
- [ ] VSM 算法对比已手绘验证
- [ ] 面试谈资已 rehearse aloud
- [ ] 源码路径已验证
- [ ] 所有内容已写入 Obsidian 笔记

---

*AI 执行时间：约 15 分钟*  
*人类执行时间：约 2 小时*
