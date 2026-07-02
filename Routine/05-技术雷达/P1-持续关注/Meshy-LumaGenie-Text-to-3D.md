---
tags: [radar/P1, radar/AI-资产生成, radar/工具链]
aliases: [Meshy, Luma AI, Luma Genie, Tripo3D, 文本生 3D, Image-to-3D, 3D Agent]
quarterly_review: 2026-Q3
---

# Meshy / Luma Genie / Tripo3D — Text/Image-to-3D 资产生成

| 字段 | 内容 |
|------|------|
| **技术名称** | 文本/图像 → 3D 资产生成(Meshy / Luma Genie / Tripo3D / Hunyuan3D) |
| **类别** | AI 资产生成 / 3D 资产管线 |
| **当前优先级** | P1 |
| **发现日期** | 2026-06-25 |
| **最后评估日期** | 2026-06-25 |

---

## 一句话简介

> 输入一句话或一张图,几分钟内出一个能进引擎的 3D 模型 — **Meshy 2025 年 ARR 4000 万美元、月活 800 万、欧美市占率 60%;Luma Genie 10 秒出模型;腾讯 Hunyuan3D 已经有"专业布线结构",直接进 UE 资产管线**。3D 资产生成已经从"玩具"变成"生产工具"。

---

## 成熟度评估

| 维度 | 评分 (1-5) | 说明 |
|------|------------|------|
| 生产可用性 | 4 | Meshy / Luma / Tripo3D / Hunyuan3D 都已商用,大厂在用 |
| 文档完善度 | 4 | 各家都有详细 API 文档,Meshy + Luma 还提供 UE 插件 |
| 社区活跃度 | 5 | Meshy / Luma 是 A16Z、Unity、Epic 生态合作伙伴,Discord / Twitter 活跃 |
| 学习资源 | 4 | 教程多,但"如何把 AI 资产管线化"是隐性知识 |
| 与现有栈兼容性 | 4 | 输出 FBX / OBJ / GLB / USDZ,主流引擎直接接;Hunyuan3D 直接出拓扑结构 |

**2026 年 6 月主流方案对比:**

| 平台 | 模型 | 时长 | 价格 | 拓扑质量 | UE 集成 |
|------|------|------|------|----------|---------|
| **Meshy 3D Agent** | Text/Image/Agent | 2 分钟/模型 | ~$1/模型 | 中(可后处理) | 有插件 |
| **Luma Genie** | Text | 10 秒 | 按量 | 中 | 有 UE5 插件 |
| **Tripo3D** | Text/Image | 1-3 分钟 | 订阅制 | 良 | 通用 FBX |
| **Hunyuan3D**(腾讯) | Image-to-3D | 30 秒-2 分钟 | 开源/云 | 优(带拓扑) | 通用 | → 已独立为 [[Hunyuan3D-Tencent-Topology]] (P0) |
| **CSM** | Video/Image | 1-5 分钟 | 订阅 | 中 | 通用 |

**核心技术栈(2026):**
- **3DGS + Mesh 混合**:神经渲染 + 拓扑 mesh,质量+可控性兼顾
- **专业拓扑布线**:[[Hunyuan3D-Tencent-Topology]] 的关键突破 — 直接出"能挂骨骼动画"的 mesh(已独立成 P0 条目)
- **3D Agent 模式**:Meshy 首创,多轮对话 + 持续迭代,像和设计师协作

---

## 学习成本估算

| 阶段 | 时间 | 产出 |
|------|------|------|
| 上手入门 | 3 天 | 注册 Meshy / Luma,试 10 个生成结果,了解各家差异 |
| 熟练应用 | 2 周 | 选定 1-2 家主力,接 API 进自己工程,能批量出"风格统一"的资产集 |
| 深度掌握 | 1-2 月 | 能做后处理(重拓扑 / 减面 / UV 重展 / 骨骼绑定),能设计 prompt-template 保持一致性 |

**关键技能点:**
- **Prompt Template**:把"日系卡通风 + 三头身 + Q 版"这种风格描述写成模板,所有生成走同一 prompt,保证一致
- **后处理流水线**:AI 出的 mesh 一般要 retopo(Instant Meshes / Quad Remesher)+ UV 优化 + LOD 生成
- **风格锁定**:LoRA / IPAdapter 思路同样适用 3D — 训练 10-20 个参考 mesh 就能锁定风格
- **法律合规**:商业项目必须用训练数据可商用的方案(FLUX / Hunyuan3D / 商用授权平台)

---

## 与当前工作的关联

- [x] 直接相关 — 当前项目可用(资产生成)
- [x] 间接相关 — 未来项目可能用(程序化内容生成 PCG)
- [x] 知识拓展 — 拓宽技术视野

**具体关联点:**
- **快速 prototype**:策划说"我要一堆史莱姆",AI 一下午出 50 个变体,挑 10 个进项目
- **UGC 工具**:UE 项目里加个"AI 生成你的角色"功能,Meshy/Luma API + WebSocket 推流
- **程序化关卡**:把 AI 生成 + PCG 框架结合 — 美术给 prompt,引擎批量出场景元素
- **NPC 角色变体**:[[Hunyuan3D-Tencent-Topology]] 的"专业布线"让 AI 角色能直接挂 UE 的 Skeletal Mesh + Animation Blueprint

**对你 day-job 的真实杠杆:**
- 读项目代码时看到"资源加载流程"能马上想到"这个流程可以接 AI 资产生成"
- 给 demo 快速出资产,不再卡在"美术没资源"
- 面试时讲"我把 Meshy API 接到项目里做了 X",这是新兴能力,加分明显

---

## 评估记录

| 日期 | 评估人 | 结论 | 下次回顾 |
|------|--------|------|----------|
| 2026-06-25 | 我 | P1 持续关注 — 资产管线拐点,选定 1-2 家试用 | 1个月后 |
| 2026-07-03 | 我 | Q3 启动 — [[Hunyuan3D-Tencent-Topology]] 从本条目拆出独立 P0 | 2026-07-25 |

---

## 关键资源

- Meshy:https://www.meshy.ai/
- Luma AI:https://lumalabs.ai/
- Tripo3D:https://www.tripo3d.ai/
- 腾讯 Hunyuan3D:https://3d.hunyuan.tencent.com/(开源版本可用) — 已独立为 [[Hunyuan3D-Tencent-Topology]] P0 条目,作为 day-job 主力 AI 资产生成选择
- A16Z 2024 年度报告把 Meshy 评为"最受欢迎 3D AI 工具"
- Perforce 2025 State of Game Technology:https://www.perforce.com/resources/state-of-game-technology-report

---

## 状态迁移

- [x] P0 → 正在学习中 → 已掌握 → 移出雷达
- [x] P1 → 评估后降为 P2 / 升为 P0
- [ ] P2 → 评估后放弃 / 升为 P1

---

## 我的判断(只对你说)

**3D 资产生成已经跨过"玩具"线**,但**还没到"全自动"线** — AI 出的 mesh 还要 retopo / UV / LOD,后处理占整个流程 60% 时间。  
短期策略:**Hunyuan3D 优先**(腾讯开源 + 拓扑结构好 + 商业可商用),Luma / Meshy 留作快速验证。  
警惕:别迷信"全自动 AI 资产",**真正稳的管线是 "AI 出 + 人工 retopo + 程序化 LOD"** — 这才是 UE 项目能落地的形态。  
对你 day-job:**Meshy/Luma API 接 UE 资产管线**是 2026 年最值钱的复合技能之一,值得花一个周末跑通 demo。

---

*Create date: 2026-06-25*  
*Last modified: 2026-06-25*
