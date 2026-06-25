# 🔧 引擎源码与架构分析库

> **对应周计划：周一晚 — 源码分析（输入）**

---

## 分析策略

**带着问题看源码**，不要通读。推荐的问题模板：

- "UE5 的虚拟纹理系统具体是如何调度显存的？"
- "RenderThread 和 GameThread 的交互机制是什么？"
- "Unity 的 ECS 架构如何做到 Cache Friendly？"
- "Godot 的渲染器抽象层设计有什么特点？"

---

## 文件夹结构

- **[[Unreal-Engine]]** — UE4/UE5 源码分析
- **[[Unity]]** — Unity DOTS/ECS/Render Pipeline
- **[[Godot]]** — Godot 开源引擎学习
- **通用架构** — 跨引擎设计模式（如 Job System、内存池、资源热更）

---

## 记录格式标准

每篇源码分析必须包含：

1. **问题定义** — 为什么看这段代码？
2. **模块图** — 涉及哪些线程/模块的交互
3. **关键类继承关系** — 用文字或 Mermaid 图表示
4. **内存布局分析** — 关键结构体的字段对齐
5. **代码路径** — 从入口到核心逻辑的调用链
6. **个人评价** — 设计优劣、可改进点

---

## 标签体系

| 标签 | 含义 |
|------|------|
| `#source/UE` | Unreal Engine 相关 |
| `#source/Unity` | Unity 相关 |
| `#source/Godot` | Godot 相关 |
| `#source/RenderThread` | 渲染线程相关 |
| `#source/GameThread` | 游戏线程相关 |
| `#source/Memory` | 内存管理 |
| `#source/JobSystem` | 多线程/任务系统 |
| `#source/Resource` | 资源加载/热更 |
| `#source/深度完成` | 已完整分析并输出笔记 |
| `#source/浅度浏览` | 仅了解大概，待深入 |

---

## 关联知识库

- [[01-论文笔记库]] — 论文中的理论如何在引擎中落地
- [[04-性能优化备忘录]] — 源码中发现的性能陷阱
- [[99-Templates/源码分析]] — 新建分析笔记模板

---

## 当前分析目标

| 目标 | 引擎 | 状态 | 截止日期 | 笔记 |
|------|------|------|----------|------|
| 虚拟纹理系统 | UE5 | ✅ 完成 | — | [[Unreal-Engine/UE5-VT-显存调度]] |
| Lumen 调用链 | UE5 | ✅ 完成 | — | [[Unreal-Engine/UE5-Lumen-源码调用链]] |
| ECS Job System | Unity | 待开始 | — | — |
| 渲染器抽象层 | Godot | 待开始 | — | — |
