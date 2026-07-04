---
tags: [radar/P0, radar/图形渲染, radar/AI-渲染]
aliases: [DLSS 4.5, FSR 4, FSR 4.1, DLSS Ray Reconstruction, XeSS, 实时超分辨率, 时序上采样]
quarterly_review: 2026-Q3
---

# DLSS / FSR / XeSS — AI 实时超分辨率三件套

| 字段 | 内容 |
|------|------|
| **技术名称** | AI 实时超分辨率与帧生成（NVIDIA DLSS 4.5 / AMD FSR 4 / Intel XeSS） |
| **类别** | 图形渲染 / AI 实时管线 |
| **当前优先级** | P0 |
| **发现日期** | 2026-06-25 |
| **最后评估日期** | 2026-06-26 |

---

## 一句话简介

> 用神经网络把"低分辨率 + 少帧"的渲染结果升到"高分辨率 + 多帧",让你在不砸硬件的前提下开路径追踪 / 高刷 — **2026 年的引擎已经不是"该不该接 DLSS"的问题,而是"接 DLSS 4.5 的 6x MFG 之后怎么压延迟"**。

---

## 成熟度评估

| 维度 | 评分 (1-5) | 说明 |
|------|------------|------|
| 生产可用性 | 5 | DLSS 4 已支持 250+ 游戏、4.5 覆盖 400+,FSR 4 突破 300 款,UE 自带插件 |
| 文档完善度 | 4 | NVIDIA 官方有完整 UE 集成文档,AMD/Intel 文档偏简略但够用 |
| 社区活跃度 | 5 | GDC 2026、Computex 2026、CES 2026 三连发,行业事实标准 |
| 学习资源 | 4 | 引擎插件已封装 90% 集成工作,核心是要理解时序数据流和 motion vector |
| 与现有栈兼容性 | 4 | DLSS 需 RTX 卡,FSR 全平台,XeSS 全平台,UE/Unity 均原生支持 |

**关键技术节点(2026 H1 现状):**
- **DLSS 4.5**(CES 2026):第二代 Transformer SR + 6x 多帧生成,RTX 50 系独占 6x MFG,RTX 30/20 也能享受画质提升
- **DLSS 4.5 Ray Reconstruction**(Computex 2026,6月1日):替代手工降噪器,8 月全系 RTX 推送,首批 27 款游戏;**Transformer 模型升级,降噪计算能力 +35%、参数处理 +20%、性能持平**;Blender Cycles 也将于 2026 秋季随 Blender 5.3 集成
- **RTX 游戏和应用数量突破 1000 款**(Computex 2026 数据);**2026 重磅新作首发支持 DLSS 4 MFG**:007 First Light / 影之刃零 / PRAGMATA / 生化危机:安魂曲
- **RTX Remix Logic**(Computex 2026 新发布):Modder 可在**不修改原始引擎代码**的前提下,根据实时游戏事件触发动态图形特效 — **Remix 平台能力大幅扩展**
- **FSR 4(Redstone)**:AMD 首款纯 AI 驱动,基于 RDNA4 首发 30 款,2026 Q4 暴增到 200 款,支持 300+ 游戏,INT8 版本下放 RDNA3(2026.7)和 RDNA2(2027)
- **XeSS 2**:Intel 跟进,帧生成 + 超分,生态规模小

---

## 学习成本估算

| 阶段 | 时间 | 产出 |
|------|------|------|
| 上手入门 | 3 天 | 能在 UE5 项目里开启 DLSS/FSR 插件,看得到画质提升 |
| 熟练应用 | 2 周 | 理解 motion vector / depth buffer 的提交契约,能排查鬼影与拖影 |
| 深度掌握 | 1-2 月 | 能在自研引擎/自研 RHI 路径里手动集成 Transformer 模型,知道 6x MFG 的延迟预算怎么算 |

**关键技能点:**
- 时序抗锯齿(TAA)与 TSR 的历史脉络 — 不懂这个就别碰超分
- Motion vector 的精度问题(尤其是粒子 / 透明物体的 motion vector 是 NaN)
- 帧生成的 base frame padding 与 input latency 关系(影响 VR 头显)
- 6x MFG 依赖 RTX 50 硬件 flip metering,不是纯软件

---

## 与当前工作的关联

- [x] 直接相关 — 当前项目可用
- [x] 间接相关 — 未来项目可能用
- [ ] 知识拓展 — 拓宽技术视野

**具体关联点:**
- **Lyra 模板 + Lumen 路径追踪**:不开 DLSS/FSR 在 4K 下根本跑不动,P0 路线图里必须解决
- **自己的 Lyra 性能分析(M5)**:在 Insights 里看到的 GPU 瓶颈,有 30-50% 可以被超分 + 帧生成吃掉
- **PCG(Procedural Content Generation)的 TSR 路径**:UE5.4+ 的 TSR 是无卡超分,低预算机型兜底
- **Multiplayer 同步**:帧生成引入额外 latency,竞技类项目要权衡

**Unreal 集成路径(知道就行,不用背):**
- `Project Settings → Engine → Rendering` 里勾 DLSS / FSR 插件
- NVIDIA 提供 `NvRTX UE Plugin`,直接拿到 TensorRT 编译好的模型
- UE5.7 的 NNE(Neural Network Engine)允许你用 UStruct 调用自己的网络 — 这是后续自定义超分的研究入口

---

## 评估记录

| 日期 | 评估人 | 结论 | 下次回顾 |
|------|--------|------|----------|
| 2026-06-25 | 我 | P0 立即学习 — 引擎标配,Lyra 项目阻塞 | 1个月后 |
| 2026-06-26 | 我 | 复核 — Blender 5.3 / RTX 1000+ / Remix Logic 等新细节已补 | 2周后 |
| 2026-07-03 | 我 | Q3 启动 — 纳入季度复盘 Routine | 2026-07-10 |

---

## 关键资源

- NVIDIA 官方 DLSS UE 集成:https://developer.nvidia.com/blog/build-ai-powered-games-with-nvidia-dlss-4-5-rtx-and-unreal-engine-5/
- AMD FSR 4 公告:https://www.amd.com/en/technologies/fidelityfx
- Intel XeSS 文档:https://www.intel.com/content/www/us/en/developer/articles/technical/xess-engine-integration.html
- 盲测对比报告(ComputerBase):DLSS 4.5 vs FSR 4 vs 原生,6 款游戏 6747 票,DLSS 4.5 拿 48.2% 选票
- 推荐阅读:UE5 内置 TSR 源码(`Engine/Source/Runtime/Renderer/Private/PostProcess/`)— 看懂这个比看 NVIDIA 文档更深入

---

## 状态迁移

- [x] P0 → 正在学习中 → 已掌握 → 移出雷达
- [ ] P1 → 评估后降为 P2 / 升为 P0
- [ ] P2 → 评估后放弃 / 升为 P1

---

## 我的判断(只对你说)

DLSS/FSR 已经不是"加分项",是 PC 端发行的事实门槛 — **不接就是放弃 4K 高刷 + 路径追踪的视觉卖点**。  
但更值得花时间的是看 UE5.7 的 **NNE(Neural Network Engine)** — 它把"调超分模型"和"调自己的网络"统一成同一套 UStruct 接口,这是**未来在引擎里挂自定义神经网络的入口**,不是只学 DLSS 怎么开。

---

*Create date: 2026-06-25*  
*Last modified: 2026-06-26*
