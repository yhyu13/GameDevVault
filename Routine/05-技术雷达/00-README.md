# 📡 技术雷达与工具栈

> **对应周计划：周五晚 — 更新技术雷达（整理）**

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

---

## 当前雷达（2026-06-26 更新 — 本批次聚焦 AI 游戏开发）

### P0-立即学习

| 技术 | 简介 | 关联工作 | 截止日期 |
|------|------|----------|----------|
| [[Rust-GameDev]] | Rust 在游戏引擎开发中的应用 | 自研引擎模块语言选型 | — |
| [[DLSS-FSR-AI超分辨率]] | DLSS 4.5 / FSR 4 / XeSS — 神经超分 + 帧生成（6 月 1 日 Computex 新增 Ray Reconstruction） | Lyra + Lumen 4K 路径追踪 | — |
| [[NVIDIA-ACE-AI-NPC]] | NVIDIA ACE 微服务 — 长期记忆 + 情绪 NPC（PUBG Ally / Total War: Pharaoh 已上生产） | 引擎集成 + AI 队友原型 | — |
| [[AI-Code-Assistant-Cursor-ClaudeCode]] | Cursor / Claude Code / Copilot / TRAE / MAI-Code — 直接吃产能 | 读项目代码 + 写工具 | — |
| [[3DGS-Gaussian-Splatting]] | 3DGS 神经渲染 — ZipSplat 33x 压缩 / World Labs Marble | 资产管线 + 扫描场景 | — |
| [[UnrealMCP-N1UnrealMCP]] | MCP 协议让 AI Agent 直接操控 UE Editor — 100+ 命令 11 类 | day-job "读 + 改 + 验证" 闭环 | — |
| [[UE-NNE-TensorRT-Plugin]] | UE NNE + NVIDIA TensorRT for RTX — 引擎里挂自定义神经网络的官方入口 | 自定义降噪 / 超分 / 神经压缩 / NPC 决策 | — |

### P1-持续关注

| 技术 | 简介 | 最新动态 | 下次回顾 |
|------|------|----------|----------|
| [[StableDiffusion-FLUX-AI美术]] | SD/FLUX 文本生图 — ComfyUI 工作流 | FLUX.2 32B 2025 末发布 | 1个月后 |
| [[Meshy-LumaGenie-Text-to-3D]] | Meshy / Luma / Tripo3D / Hunyuan3D | Meshy ARR 4000 万美元 | 1个月后 |
| [[LLM-NPC-Inworld-Convai]] | Inworld / Convai 产品化 NPC 平台 | Inworld 长期记忆生产可用 | 1个月后 |

### P2-了解即可

| 技术 | 简介 | 为什么放 P2 |
|------|------|-------------|
| [[ElevenLabs-AI-Voice]] | ElevenLabs AI 语音合成 | 偏音频/独立游戏向,不是引擎核心 |
| [[WorldModels-Genie3-Hunyuan]] | Genie 3 / Oasis 实时世界生成 | 5-10 年后的事,等它真正可用再学 |

---

## 标签体系

| 标签 | 含义 |
|------|------|
| `#radar/P0` | 立即学习 |
| `#radar/P1` | 持续关注 |
| `#radar/P2` | 了解即可 |
| `#radar/图形渲染` | 渲染相关 |
| `#radar/引擎架构` | 架构相关 |
| `#radar/工具链` | 编辑器/工具 |
| `#radar/语言` | 编程语言 |
| `#radar/AI-渲染` | AI 渲染方向(DLSS / 3DGS) |
| `#radar/AI-NPC` | AI NPC / 智能体方向 |
| `#radar/AI-资产生成` | AI 美术 / 3D / 音乐 / 语音 |
| `#radar/AI-生产力` | AI 编程 / 工具 |
| `#radar/AI-世界生成` | 世界模型 / 实时生成 |
| `#radar/已掌握` | 已学习完成，可移出雷达 |
| `#radar/已放弃` | 评估后不再关注 |

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
