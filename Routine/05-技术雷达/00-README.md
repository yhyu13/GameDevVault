# 📡 技术雷达与工具栈

> **对应周计划：周五晚 — 更新技术雷达（整理）**
> **当前形态：2026-Q3 季度复盘 Routine** — 每次周五整理同时维护"周行动"与"季度复盘"两条线

---

## 评估标准

每个技术/工具进入雷达前，评估：

1. **成熟度** — 生产可用？还是玩具阶段？
2. **学习成本** — 需要多少时间能上手？
3. **与当前工作的关联度** — 现在用得上吗？
4. **社区活跃度** — 最近提交时间？Issue 响应速度？

---

## 优先级定义

| 优先级 | 含义 | 行动 |
|--------|------|------|
| **P0-立即学习** | 与当前工作直接相关，或即将成为行业标准 | 本周内安排时间学习 |
| **P1-持续关注** | 有潜力，但尚未成熟或暂时用不上 | 每月回顾一次，收集资料 |
| **P2-了解即可** | 有意思但偏离当前方向 | 听说过就行，不投入时间 |
| **已掌握** | 已完成学习并能用于生产 | 移出活跃雷达，季度复盘抽样回看 |
| **已放弃** | 评估后判断不再投入 | 保留记录以备重评，移出活跃雷达 |

---

## 当前雷达（2026-07-12 更新 — P0 渲染特性补丁）

> **本批次（2026-07-12）**：在 7-03 深度重构基础上，**新增 P0-渲染特性 3 项**（[[Lumen]] / [[Nanite]] / [[VSM]]）作为独立子节。原因：day-job = RAG + Mac Game Harness（LLM-driven UE on Mac），渲染三大特性是 LLM 能否正确调用 UE 渲染管线的核心知识；7-05 三能力对账反复点名缺位。
> **上批次（2026-07-03）**：从 12 项调整为 13 项：把 [[Hunyuan3D-Tencent-Topology]] 从 [[Meshy-LumaGenie-Text-to-3D]] 拆出独立条目；把 [[Rust-GameDev]] 从 P0 降为 P2；新建 `已掌握/` 和 `已放弃/` 两个 bucket。

### P0-立即学习（7 项 — 工具链轴）

| 技术 | 简介 | 关联工作 | 截止日期 | 下次回顾 |
|------|------|----------|----------|----------|
| [[DLSS-FSR-AI超分辨率]] | DLSS 4.5 / FSR 4 / XeSS — 神经超分 + 帧生成 | Lyra + Lumen 4K 路径追踪 | — | 2026-07-10 |
| [[NVIDIA-ACE-AI-NPC]] | NVIDIA ACE 微服务 — 长期记忆 + 情绪 NPC | 引擎集成 + AI 队友原型 | — | 2026-07-10 |
| [[AI-Code-Assistant-Cursor-ClaudeCode]] | Cursor / Claude Code / Copilot / TRAE / MAI-Code | 读项目代码 + 写工具 | — | 2026-07-10 |
| [[3DGS-Gaussian-Splatting]] | 3DGS 神经渲染 — ZipSplat 33x 压缩 | 资产管线 + 扫描场景 | — | 2026-07-10 |
| [[UnrealMCP-N1UnrealMCP]] | MCP 协议让 AI Agent 直接操控 UE Editor | day-job "读 + 改 + 验证" 闭环 | — | 2026-07-26 |
| [[UE-NNE-TensorRT-Plugin]] | UE NNE + NVIDIA TensorRT for RTX — 自定义神经网络官方入口 | 自定义降噪 / 超分 / 神经压缩 / NPC 决策 | — | 2026-07-26 |
| [[Hunyuan3D-Tencent-Topology]] ⭐ NEW | 腾讯 Hunyuan3D — 拓扑 mesh + 开源可商用 | day-job 主力 AI 资产生成选择 | — | 2026-08-03 |

### P0-渲染特性（3 项 — day-job 必考）⭐ NEW 2026-07-12

> **为什么独立成子节**：day-job = RAG + Mac Game Harness（LLM-driven UE on Mac），**渲染三大特性是 LLM 能否正确调用 UE 渲染管线的核心知识**。与上方"工具链轴"7 项**正交**——工具=怎么用引擎，特性=引擎内部机制。本批次（P0 渲染特性）弥补 [[2026-07-05-三能力对账]] 反复点名的 day-job 必考缺位。
> **补位来源**：`5469a3f` 5 篇性能瓶颈 + `fbf5131` shader 重组 + W28 W5/W6 shader 已落盘（VSM 763 行）。**Lumen 是"已可掌握"候选，Nanite/VSM 仍在补完中**。

| 技术 | 简介 | 当前 vault 状态 | 关联工作 | 下次回顾 |
|------|------|----------------|----------|----------|
| [[Lumen]] ⭐ | UE5 全局光照 + 反射（SSGI 替代） | ✅ **厚**：3 论文 + 2 shader（W3 反射降级 / W4 GI 漫反射）+ 2 性能（反射开销/调优）| day-job RAG 索引主轴 / Mac Metal RHI 适配 | 2026-08-07 |
| [[Nanite]] ⭐ | UE5 虚拟几何 + 材质管线 | ⚠️ **中**：1 shader（W5 材质管线 763 行）+ 2 性能（WPO 禁用距离 / 性能调优）+ W27 mini-README；**缺源码分析** | day-job RAG 索引 + 虚拟几何 shader 适配 | 2026-08-14 |
| [[VSM]] ⭐ | UE5 虚拟阴影映射（页表 + Moments） | ⚠️ **中**：1 shader（W6, 763 行）+ 1 性能（页溢出）+ 1 QA 卡；**缺源码分析** | day-job RAG 索引 + 阴影 LRU 调优 | 2026-08-14 |

### P1-持续关注（3 项）

| 技术 | 简介 | 最新动态 | 下次回顾 |
|------|------|----------|----------|
| [[StableDiffusion-FLUX-AI美术]] | SD/FLUX 文本生图 — ComfyUI 工作流 | FLUX.2 32B 2025 末发布 | 2026-07-25 |
| [[Meshy-LumaGenie-Text-to-3D]] | Meshy / Luma / Tripo3D | Meshy ARR 4000 万美元 | 2026-07-25 |
| [[LLM-NPC-Inworld-Convai]] | Inworld / Convai 产品化 NPC 平台 | Inworld 长期记忆生产可用 | 2026-07-25 |

### P2-了解即可（3 项 — 含 1 项降级）

| 技术 | 简介 | 为什么放 P2 |
|------|------|-------------|
| [[ElevenLabs-AI-Voice]] | ElevenLabs AI 语音合成 | 偏音频/独立游戏向,不是引擎核心 |
| [[WorldModels-Genie3-Hunyuan]] | Genie 3 / Oasis 实时世界生成 | 5-10 年后的事,等它真正可用再学 |
| [[Rust-GameDev]] ⚠️ DEGRADED | Rust 在游戏引擎开发中的应用 | 18 个月未复评 + day-job 已转向 Lyra/Lumen,Q3 末决定是否"已放弃" |

### 已掌握（暂无）

> 占位 — 等第一批 P0 项完成时填入。预期顺序：**[[Lumen]]（最厚候选）** > DLSS-FSR > AI-Code-Assistant > UnrealMCP > 3DGS > UE-NNE > NVIDIA-ACE > Hunyuan3D

### 已放弃（暂无）

> 占位 — Q3 末评估 [[Rust-GameDev]] 时决定是否首次填入

---

## 季度复盘（2026-Q3: 7月-9月）

### 本季度核心目标

- **完成 P0 全部 10 项的"上手"阶段**（7 工具 + 3 渲染特性；每个至少跑通一次 demo / 在工程里见过一次效果）
- **Hunyuan3D demo 闭环**：跑通 Image-to-3D → 拓扑 mesh → UE 导入 → 挂骨骼动画
- **AI-Code-Assistant + UnrealMCP 联动**：用 MCP 让 AI Agent 自动跑 PIE 验证
- **[[Lumen]] 升"已掌握"**：3 论文 + 2 shader + 2 性能已厚，Q3 末升入"已掌握"作为 day-job 渲染知识主轴
- **[[Nanite]] + [[VSM]] 补完**：W29 把 VSM 升到 source-analysis 级（≥ 600 行）；W30 把 Nanite 补源码分析
- **Rust 终审**：9 月底评估，决定"继续 P2"还是"移入已放弃"

### 季度回顾日历

| 日期 | 事件 | 触发条件 |
|------|------|----------|
| 2026-07-03 | 深度重构 + Q3 启动 | 本次整理 |
| 2026-08-07 | 月度回顾 1 | P0 进度盘点 |
| 2026-09-04 | 月度回顾 2 | P0 进度盘点 + 季度收尾 |
| 2026-09-25 | Q3 收尾 + Q4 计划 | 季度总结 |

### 季度成功标准（OKR 风格）

- **O1**:P0 十项全部完成"上手"阶段（每项都有 1 个可展示的 demo 或工程证据）
- **O2**:Routine 雷达具备"季度复盘"形态（README / 状态迁移 / 季度日历 三件套跑通）
- **O3**:至少 1 项 P0 升入"已掌握"（**[[Lumen]] 是首选目标**；如果季度内 AI-Code-Assistant / DLSS-FSR 已能日常用，就算达成）

### 季度风险

- **P0 项过多（10 项 — 7 工具 + 3 渲染特性）**:每周 1 项都满负荷,任何一项卡壳都会拖累整体进度 → 缓解：渲染特性 3 项已有 vault 积累（无需从零研究），重点是 W29/W30 补完源码分析；工具链优先保 AI-Code-Assistant + UnrealMCP（day-job 直接杠杆）
- **Hunyuan3D API 限制**:腾讯云 API 可能有 QPS / 月配额 → 缓解：提前查清限制,准备 fallback 到 Luma
- **Lumen 升"已掌握"门槛**:虽然 vault 笔记最厚，但 Lumen 内部机制（Surface Cache / Probe Densification / 反射 tier / Fallback Stack）要在 Mac Metal RHI 上跑通才算"已掌握" → 缓解：Mac 平台 vault 子目录 W29 必建（哪怕 5 行也行）

---

## 下一步行动（按周拆解 — 2026-W28 / W29 / W30）

> **这是 Routine 雷达"季度复盘形态"的核心改进**:每个周五整理都要更新"未来三周的下一步"。

### 本周（W28: 7/6 - 7/12）— 7/10 是 4 个 P0 的"2 周后回顾"到期日

- [x] **雷达 P0 渲染特性补丁**：Lumen / Nanite / VSM 加入 P0（**2026-07-12 完成**）
- [ ] 复评 [[AI-Code-Assistant-Cursor-ClaudeCode]]:是否已在 day-job 日常用？
- [ ] 复评 [[NVIDIA-ACE-AI-NPC]]:是否跑通一个 demo？
- [ ] 复评 [[DLSS-FSR-AI超分辨率]]:Lyra 项目是否已开 DLSS 4.5？
- [ ] 复评 [[3DGS-Gaussian-Splatting]]:是否用过 Luma UE 插件拍场景？
- [ ] Hunyuan3D:注册账号 + 跑 5 张图看拓扑质量

### 下周（W29: 7/13 - 7/19）— 渲染特性补位 + Mac 起头

- [ ] **[[VSM]] 升级到 source-analysis 级**：`Routine/02-引擎源码分析库/Unreal-Engine/W29/UE5-VSM-源码追踪.md`（页表 + Cache + Nanite 集成 ≥ 600 行）
- [ ] **[[Nanite]] 起头 source-analysis**：从 W27 mini-README 起，写 W29/W30 两周的 Mesh Pass / Cluster DAG / Page Streaming 源码笔记
- [ ] **Mac 平台 vault 子目录**：`Routine/Mac-平台/00-README.md` + 3-5 个待办锚点（哪怕只填 5 行）
- [ ] Hunyuan3D:接 API 进工程 + 出一个挂骨骼 demo 角色
- [ ] AI-Code-Assistant + UnrealMCP 联动：试 ping → spawn_actor → create_blueprint
- [ ] 评估是否把 [[NVIDIA-ACE-AI-NPC]] 升到"已掌握"

### 再下周（W30: 7/20 - 7/26）— 2 个 P0 的"1 个月后回顾"到期

- [ ] 复评 [[UnrealMCP-N1UnrealMCP]]:是否已用于真实 day-job 工作流？
- [ ] 复评 [[UE-NNE-TensorRT-Plugin]]:是否跑通 ONNX 加载 demo？
- [ ] **[[Lumen]] 升"已掌握"预审**：Mac Metal RHI 上跑通 Lumen 反射降级 / GI 漫反射 → 8/7 月度回顾时决定
- [ ] 月度盘点：把完成度同步到 [[季度复盘（2026-Q3）]]

---

## 状态迁移流程

```
进入雷达
  ↓
P2 / P1 / P0 (按评估决定)
  ↓ 周期回顾
评估后保留 / 升级 / 降级 / 移入已掌握 / 移入已放弃
  ↓
已掌握 ←─ 完成学习 + 用于生产
已放弃 ←─ 评估后不再投入
```

### 状态迁移触发条件

- **升 P0 → P1**:学了但目前用不上
- **升 P0 → 已掌握**:能在生产中独立使用,不再需要查资料
- **降 P0 → P2**:18 个月未复评 或 day-job 转向
- **P0/P1/P2 → 已放弃**:确认不会再投入时间

### 迁移记录位置

- 每个条目末尾的"状态迁移"区块记录单条目的迁移历史
- `已掌握/` 和 `已放弃/` 目录放归档后的文件
- 本 README 的"当前雷达"区块只保留活跃项

---

## 标签体系

| 标签 | 含义 |
|------|------|
| `#radar/P0` | 立即学习 |
| `#radar/P1` | 持续关注 |
| `#radar/P2` | 了解即可 |
| `#radar/已掌握` | 已学习完成，可移出雷达 |
| `#radar/已放弃` | 评估后不再关注 |
| `#radar/图形渲染` | 渲染相关 |
| `#radar/引擎架构` | 架构相关 |
| `#radar/工具链` | 编辑器/工具 |
| `#radar/语言` | 编程语言 |
| `#radar/AI-渲染` | AI 渲染方向(DLSS / 3DGS) |
| `#radar/AI-NPC` | AI NPC / 智能体方向 |
| `#radar/AI-资产生成` | AI 美术 / 3D / 音乐 / 语音 |
| `#radar/AI-生产力` | AI 编程 / 工具 |
| `#radar/AI-世界生成` | 世界模型 / 实时生成 |
| `#quarterly_review/2026-Q3` | 季度复盘锚点 |

---

## 信息源列表

| 来源 | 频率 | 链接 |
|------|------|------|
| GitHub Trending | 每周 | https://github.com/trending?l=c%2B%2B |
| Graphics Programming Weekly | 每周 | https://www.jendryschik.de/books/graphics/ |
| Twitter/X 技术大佬 | 每日 | — |
| 技术 Discord/微信群 | 实时 | — |
| **AI 游戏开发专属源** | | |
| NVIDIA Developer Blog | 每周 | https://developer.nvidia.com/blog/ |
| GDC Vault(GDC 2026 起公开演讲) | 每年 | https://www.gdcvault.com/ |
| GTC 录像(CES / Computex 同步) | 每季度 | https://www.nvidia.com/en-us/gtc/ |
| a16Z Games Newsletter | 每月 | https://a16z.com/the-generative-ai-craze-in-gaming/ |
| Perforce State of Game Technology | 每年 | https://www.perforce.com/resources/state-of-game-technology-report |
| Civitai(SD/FLUX 模型 + 趋势) | 每周 | https://civitai.com/ |
| arXiv cs.GR / cs.AI 关键词 | 每日 | https://arxiv.org/list/cs.GR/recent |

---

## 关联知识库

- [[01-论文笔记库]] — 新论文转化为雷达条目
- [[99-Templates/技术雷达条目]] — 新建条目模板

---

## 当前聚焦主题：AI 游戏开发(2026-06 起)

本批次只收录 **AI 相关** 的游戏开发技术与技能。后续批次会逐步覆盖：
- 渲染管线扩展(自研 RHI / NNE 深度集成)
- 物理与动画(ML Deformer / Motion Synthesis)
- 工具链与引擎架构(GameFeature / Lyra 衍生)
- 多玩家与网络(Prediction / Replication 与 AI)

## 2026 H1 关键事件(给 1 个月后回顾参考)

- **CES 2026**(1 月):DLSS 4.5 发布、RTX Remix Logic、ACE 在 Total War Pharaoh / PUBG Ally 上生产
- **Microsoft Build 2026**(6 月 2 日):从"消费前沿模型"转向"智能体时代",MAI-Thinking-1 / MAI-Code-1-Flash / Majorana 2 量子芯片
- **NVIDIA Computex 2026**(6 月 1 日):DLSS 4.5 Ray Reconstruction 8 月推送、RTX 游戏破 1000 款、NVIDIA + Microsoft 推 Personal AI Agents + MCP 协议
- **ZipSplat 论文**(6 月 3 日,ETH + Microsoft):3DGS 33x 压缩,24 视角 0.8s 推理,3.3MB 存储 685 FPS
- **UnrealMCP / N1UnrealMCP**:UE 5.7 官方 MCP 插件,AI Agent 100+ 命令控制 Editor
- **NVIDIA TensorRT for RTX Plugin for UE NNE**:引擎里挂自定义神经网络的官方入口
- **腾讯 Hunyuan3D**:Image-to-3D 自带专业拓扑结构,开源可商用

---

## Routine 维护节奏

| 周期 | 任务 |
|------|------|
| **每周五晚** | 更新"下一步行动"、处理到期回顾、加新条目 |
| **每月第一周五** | 月度盘点:P0 进度 + P1 资料收集 + 下个月计划 |
| **季度末(9/25)** | 季度复盘:状态迁移决策 + Q4 计划 + 整库健康度盘点 |

---

*Create date: 2026-06-25*
*Last modified: 2026-07-12（P0 渲染特性补丁：Lumen / Nanite / VSM 加入 P0 作为独立子节）*