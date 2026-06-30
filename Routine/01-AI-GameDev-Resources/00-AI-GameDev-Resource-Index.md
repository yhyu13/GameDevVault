---
tags: [routine/master-index, ai-game-dev, system/reference]
aliases: [AI-GameDev-Resources, AI-Resource-Index]
created: 2026-06-29
---

# AI Game Development — 资源总索引

> **范围**：本目录只收录 **AI 相关** 的游戏开发技术与技能。
> **覆盖维度**：(1) 引擎内置 AI 能力；(2) AI 工具链；(3) AI 资产生成；(4) AI 渲染；(5) AI 辅助编程。
> **阅读约定**：每个主题用「方向论断 + 5 条证据 + 1 个本周动作」格式呈现。看完要能直接动手。

---

## 0. 一句话优先级（先看这个）

**如果只做一件事**：去你 `Routine\AI-Tasks\UnrealMCP\` 的 `01_Monday\AI-Tasks.md`，把 Anthropic MCP 规范原文 + Unreal MCP 插件源码读完。  
**为什么**：MCP 是 2024-11 之后 AI 工具的 "USB-C 标准"，Unreal 已经在引擎里原生实现；理解 MCP = 理解你未来 5 年用 AI 工具的所有姿势。其他 7 个主题都可以缓。

**如果还能挤 1 小时**：装 Claude Code（Anthropic 官方 CLI），在你当前 Lyra/Lumen 项目里跑一圈，体会 "本地 Agent + 上下文工程" 的真实体感。SWE-bench 80.8% 不是吹的，是真实差距。

---

## 1. 优先级矩阵（按"对 M5 Lyra+Lumen 突破贡献度"排序）

| # | 主题 | 对你的相关度 | 新颖度 | 已有 AI-Tasks | 本周动作 |
|---|------|------------|--------|--------------|---------|
| **1** | **MCP / Unreal MCP** | ★★★★★ | ★★★★★ | [[../AI-Tasks/UnrealMCP]] | 读 MCP 规范 + 实现一个最小 MCP Server |
| **2** | **AI 辅助编程工具** | ★★★★★ | ★★★★ | ✗ | 装 Claude Code，在 Lyra 源码上跑 5 个真实任务 |
| **3** | **DLSS / 神经渲染** | ★★★★ | ★★★★★ | ✗ | 读 Karpathy 2025 总结 + 试 DLSS 4.5 6x MFG |
| **4** | **Neural Rendering (NNE + ML Deformer)** | ★★★★ | ★★★★ | [[../AI-Tasks/NeuralRendering]] | 把 UE5.8 NNE 模块 grep 一遍 |
| **5** | **LLM 驱动 NPC** | ★★★ | ★★★★★ | ✗ | 读 Inworld / Convai 架构综述 1 篇 |
| **6** | **Learning Agents / 强化学习** | ★★★ | ★★★★ | [[../AI-Tasks/MassAILearningAgents]] | 看 AReaL v1.0 仓库 README |
| **7** | **PCG（程序化生成）** | ★★★ | ★★★ | [[../AI-Tasks/PCG]] | 看完 PCG 官方文档 "Quick Start" |
| **8** | **生成式 AI 资产（SD/ComfyUI/LTX-2）** | ★★ | ★★★★ | ✗ | 本周不学，记下 ComfyUI 节点图思路就行 |

---

## 2. 主题详细索引（每节 5 分钟可读完）

### 2.1 MCP / Unreal MCP — 方向论断 + 证据

**方向论断**：MCP 已经不是"新协议"了，是 2025 年 AI 工具的 **事实标准**。Anthropic 在 2024-12 已把 MCP 捐给 Linux Foundation 旗下 Agentic AI Foundation；OpenAI、ChatGPT、VS Code Goose、Salesforce、Slack、Box、Asana、Figma 全都宣布兼容。任何还在做"自研工具集成协议"的团队都在浪费时间。Unreal Engine 5.8 在 `Experimental/ModelContextProtocol` 已经实现 6 个模块的 Server，是 Epic 押注方向。

**5 条证据**：
1. 2024-11 Anthropic 发布 MCP 协议，规范基于 JSON-RPC 2.0，本地 stdio + 远程 SSE/HTTP。
2. 2025-04 Anthropic 发布 **MCP Apps** 框架：MCP Server 直接在聊天界面渲染交互式 UI（仪表板、文档预览、消息草稿）。Goose/VS Code 已支持，本周 ChatGPT 跟进。
3. OpenAI Apps SDK 以 MCP 为核心做了兼容层，Nick Cooper（OpenAI）公开背书。
4. Unreal MCP 插件（Experimental）含 6 模块：`ModelContextProtocol` / `Engine` / `Editor` / 三套 Tests。
5. 你能立刻用：Claude Desktop / Cursor / Continue / Cline 全部支持 MCP Server 加载。

**本周动作**：克隆 `modelcontextprotocol/python-sdk`，跑通 `examples/filesystem` server，用 `mcp-cli` 接到 Claude Desktop，确认你能让 AI 读你的 Lyra 项目源码。

**资源链接**：
- 规范原文：https://modelcontextprotocol.io
- Python SDK：https://github.com/modelcontextprotocol/python-sdk
- Servers 集合：https://github.com/modelcontextprotocol/servers
- UE5.8 源码：`Unreal/Engine/Plugins/Experimental/ModelContextProtocol/`
- Vault 内：[[../AI-Tasks/UnrealMCP/00-Master-Index]]、[[../UE58-Topic-Exploration-Report]]

---

### 2.2 AI 辅助编程工具 — 方向论断 + 证据

**方向论断**：2026 年 **Claude Code 是推理之王**，**Cursor 是 IDE 体验之王**，**GitHub Copilot 是企业基座**。对个人 Unreal 引擎程序员，**Claude Code + Cursor 二选一**。不要用 Copilot 做主力（中文差、Agent 弱、$10/月不值）。**对游戏引擎程序员特别有用的是 Claude Code**：能读你十万行 C++、理解整个 Unreal 源码目录结构。

**5 条证据**（来自 2026 多家横评）：
1. SWE-bench：Claude Code **80.8%**（业界第一），Cursor Composer 2.5 次之（缩差 35 分），Copilot 显著落后。
2. 大上下文能力：Claude Code 能一次处理 10w+ 行代码库，Cursor 次之，Copilot 仅看当前文件。
3. 多文件编辑：Cursor Composer 模式体验最好；Claude Code 也能做但方式不同；Copilot 偏弱。
4. 本地化（中文 + 国内网络）：Cursor 差、Copilot 差；Trae（字节）免费且中文优化好，但推理能力不及前两者。
5. Karpathy 在 2025 年度总结明确把 Claude Code 列为"AI 范式转移的代表"——"栖息在用户电脑中的智能实体"。

**本周动作**：
- 装 Claude Code：`curl -fsSL https://claude.ai/install.sh | claude`，登录授权。
- 在你的 Lyra 仓库跑 3 个真实任务：(1) "Lyra 的 CharacterMovementComponent 有哪些 TickDependency"；(2) "LumenSurfaceCache 的 invalidate 触发条件"；(3) "找出 Lyra 项目里所有 hardcoded 字符串并列出"。
- 对比 Cursor Composer 在同一任务上的输出，记到 [[../06-职业复盘日志/]]。

**资源链接**：
- Claude Code 官网：https://claude.com/product/claude-code
- 横评（2026）：https://blog.csdn.net/xinpengfei521/article/details/159015508
- Karpathy 2025 总结：腾讯科技转载（核心 6 大范式转移）
- Vault 内：✗（待创建 `AI-Tasks/CodingTools/` 主题）

---

### 2.3 DLSS / 神经渲染 — 方向论断 + 证据

**方向论断**：**DLSS 已经从"性能工具"升级为"画面生成器"**。DLSS 4（2025-01）引入 Multi Frame Generation + Transformer 模型；DLSS 4.5（2026-01）支持 **6x 多帧生成** 和动态多帧；DLSS 5（2026 GTC 发布，秋季上线）首次引入 **实时神经网络渲染模型**——直接把光照和材质生成交给神经网络，黄仁勋称之为图形学的 "GPT 时刻"。**对你的意义**：在 Lyra/Lumen 项目里调 perf 时，必须把 DLSS 4.5 / FSR 4 当作 baseline，而不是"再压一压"。

**5 条证据**：
1. DLSS 4 Multi Frame Gen：每渲染 1 帧生成 3 帧，速度 +40%、显存 -30%（RTX 50 系独占）。
2. DLSS 4.5 用第二代 Transformer 模型，超分画质显著提升，新增 6x MFG。
3. DLSS 5 是 **GTC 2026 重大发布**：以颜色 + 运动矢量为输入，端到端神经网络生成光照/材质，4K 实时运行，可调强度以保留美术风格。首发游戏包括《星空》《生化危机》《永劫无间》《逆水寒》等 16+ 款，中国厂商占近一半。
4. 架构变化：DLSS 4 起 CNN → Transformer；DLSS 5 起 AI 模型直接生成像素。
5. 行业格局：FSR 4（AMD）继续开源追赶；XeSS 2（Intel）跟进帧生成。**NVIDIA 主导"AI 渲染"叙事**。

**本周动作**：
- 在 Lyra 项目里启用 DLSS 4.5（4K + 路径追踪），用 NVIDIA FrameView 抓 1% Low、平均延迟、显存峰值。
- 写一条 [[../04-性能优化备忘录/]] 笔记：Lyra 在 DLSS Quality / Balanced / Performance 三档下的 perf 对比。
- 读 GTC 2026 DLSS 5 keynote 摘要（中文媒体已大量转载），重点关注"AI 渲染对美术工作流的冲击"。

**资源链接**：
- DLSS 4.5 实测：https://www.163.com/dy/article/SO8VLM5C0511B6FU.html
- DLSS 5 GTC 2026：https://news.qq.com/rain/a/20260316A07BZM00
- NVIDIA Streamline 框架：开源 SDK，UE 集成通过插件
- Vault 内：✗（待创建 `AI-Tasks/DLSS-NerualRender/`）

---

### 2.4 Neural Rendering（NNE + ML Deformer）— 方向论断 + 证据

**方向论断**：UE5.8 把 **ONNX Runtime 直接嵌入引擎**（`Plugins/NNE`），用 `NNERuntimeORT` 跑训练好的模型做实时推理。这是 Epic 给所有想做"用 AI 替代昂贵 CPU/GPU 模拟"的人的官方通道。**ML Deformer** 是这条通道最成熟的样板：训练数据来自 Chaos Physics 高保真模拟，推理阶段用 MLP 替代，开销远低于原始模拟。

**5 条证据**：
1. UE5.8 NNE 模块结构：`NNE`（Runtime）+ `NNERuntimeBasicCpu` + `NNERuntimeORT`（ONNX Runtime 封装）+ `NNERuntimeRDG`（Render Graph 集成）。
2. ONNX Runtime 跨平台优化最佳实践：显式指定 ExecutionProvider（TensorRT > CUDA > CPU）、IO Binding 避拷贝、固定 Shape 或分桶、INT8 量化。
3. ML Deformer 在 Lyra 项目里有现成资产：`Engine/Plugins/Experimental/MLDeformer/`。
4. 公开示例：`MehrdadAbsolute/OnnxRuntime-UnrealEngine`（Style Transfer 实时风格迁移）。
5. 训练数据流：Chaos → 高保真模拟 → 导出 ONNX → UE 推理。**这是"ML 替代物理"的最小可行管线**。

**本周动作**：
- 在 UE5.8 里跑 `OnnxRuntime-UnrealEngine` 示例，对比 CPU vs CUDA ExecutionProvider 的帧时间差。
- 把 `NeuralNetworkEngine` 模块的 `IModel` 接口读完，写一行 [[../02-引擎源码分析库/]] 笔记。

**资源链接**：
- ONNX Runtime 微软仓库：https://github.com/microsoft/onnxruntime
- UE Style Transfer 示例：https://github.com/MehrdadAbsolute/OnnxRuntime-UnrealEngine
- 性能优化 8 条：https://www.163.com/dy/article/JA0PUOSM0514C3QE.html
- Vault 内：[[../AI-Tasks/NeuralRendering/00-Master-Index]]

---

### 2.5 LLM 驱动 NPC — 方向论断 + 证据

**方向论断**：**LLM NPC 已走出 demo 阶段，开始进生产**。代表产品是 Inworld AI（Character Brain 引擎：记忆 + 情绪 + 目标 + 多模态）、Convai、阿里达摩院的 DVM 框架。学术前沿是 CPDC 2025 Challenge（Persona-Grounded Dialogue）和 Park 等人的 25-NPC 虚拟村庄。**对你的意义**：UE5.8 的 Mass AI + Learning Agents 是底层 NPC 框架；上层接入 LLM 是产品层的玩法，不需要再"自研对话系统"。

**5 条证据**：
1. Inworld AI Character Brain：长期记忆 + 情绪 + 目标 + 多模态（语音/表情/动作）+ 安全护栏。已商用。
2. Convai：专注 Unreal/Unity 集成，提供 NPC 实时对话 + 行动决策。
3. 学术：CPDC 2025 Challenge（MSRA_SC 方案公开），DVM 框架用于社交推理游戏。
4. 关键技术挑战：Context Engineering（动态工具剪枝 + Persona 裁剪）+ Prompt Refinement + Function Merging。
5. 行业拐点：Karpathy 在 2025 总结明确 LLM GUI 范式已经到来，"幽灵 vs 动物"智能理论适用 NPC 设计。

**本周动作**：
- 读 Inworld AI 官方技术博客 1 篇（https://docs.inworld.ai），重点看 Character Brain 架构图。
- 把 Convai 的 UE 插件仓库 `git clone` 下来，看它怎么和 Unreal CharacterComponent 集成。
- 不用这周写代码——目标是建立"LLM NPC 工程链路"的脑图。

**资源链接**：
- Inworld AI 文档：https://docs.inworld.ai
- Convai UE 插件：https://github.com/Convai
- DVM 论文：https://arxiv.org/html/2501.06695v1
- CPDC 2025：https://arxiv.org/abs/2511.20200
- Vault 内：✗（可创建 `AI-Tasks/LLM-NPC/`）

---

### 2.6 Learning Agents / 强化学习 — 方向论断 + 证据

**方向论断**：UE5.8 的 Learning Agents 还在 0.2 Experimental，但行业整体已经把 **RL 作为 Agent 训练的事实后端**。2026 开年最值得关注的是 AReaL v1.0（蚂蚁 + 清华）："Agent 一键接入 RL 训练"——改一行配置就能让任意 Agent 跑 RL，2026 年 Agent + RL 闭环将爆发。**对你的意义**：Lyra 的 AI Bot 用 Behavior Tree + EQS 是过渡方案；长期看 RL 训练 + Inference 才是出路。

**5 条证据**：
1. UE5.8 Learning Agents：含 4 模块（LearningAgents + Training + TrainingEditor + Replay），依赖 PyTorch + ONNX。
2. AReaL v1.0（2026-03）：首个全异步训推解耦 RL 训练系统，5D 并行（数据/流水线/张量/上下文/专家），支持千亿参数 MoE。
3. DeepSeek R1 / Kimi k1.5 验证 RLVR（可验证奖励强化学习）成为 2025 后训练新范式。
4. Karpathy 2025 总结："RLVR 占用原预训练算力份额"是 LLM 行业最大范式转移。
5. 学术论文：`Reinforcement Learning for Machine Learning Engineering Agents`（arXiv:2509.01684）证明弱模型 + RL 训练可超越大模型 + Prompting。

**本周动作**：
- 看 AReaL GitHub README + 架构图（不要求跑通）：https://github.com/inclusionAI/AReaL
- 读 UE5.8 Learning Agents 文档首章（理解 Observation/Action/Reward 三元组）。
- 写下"如果我要训练 Lyra 的近战 Bot RL 策略，需要准备什么"——10 行清单即可。

**资源链接**：
- AReaL 论文：https://arxiv.org/abs/2505.24298
- arXiv 2509.01684：https://arxiv.org/abs/2509.01684
- UE 官方文档（Plugins/LearningAgents）
- Vault 内：[[../AI-Tasks/MassAILearningAgents/00-Master-Index]]

---

### 2.7 PCG（程序化内容生成）— 方向论断 + 证据

**方向论断**：PCG 是 UE 引擎默认启用的"节点式程序化生成框架"，已经 **稳定** 而非前沿。它的价值不在"AI"，而在 **图式管线**——你未来用 AI 资产生成（SD/ComfyUI 输出）的"批处理管线"思路和 PCG 完全一致。**对你的意义**：Lyra 关卡里所有可重复元素都应用 PCG 思维重写；不要硬塞手工 Actor。

**5 条证据**：
1. UE PCG 插件已稳定（默认启用），含 PCGGraph + PCGComponent + Runtime 生成器。
2. 与 MassSpawner / SmartObjects / StateTree 深度集成，是 MassAI 的生成端。
3. 视觉脚本风格（非 C++），学习曲线平缓。
4. 行业类比：Houdini PCG / SideFX 思路；Unity 也有类似资产。
5. 局限：PCG 本身不"生成 AI 资产"，需要接 Stable Diffusion API 才能做 AI 生成。

**本周动作**：
- 打开 UE5.8 Lyra 工程，找到 PCG 相关的关卡资产，跑一遍"强制重新生成"。
- 看 PCG 官方文档 Quick Start 的前 3 章。
- 写下"Lyra 哪些系统能用 PCG 重构"——5 行即可。

**资源链接**：
- UE PCG 官方文档：https://dev.epicgames.com/documentation/en-us/unreal-engine/procedural-content-generation-framework
- Vault 内：[[../AI-Tasks/PCG/00-Master-Index]]

---

### 2.8 生成式 AI 资产（SD/ComfyUI/LTX-2）— 方向论断 + 证据

**方向论断**：**生成式 AI 资产对引擎程序员是"二级相关"**——你不需要自己跑 Stable Diffusion，但你需要理解 ComfyUI 节点图、SDXL / Flux / LTX-2 模型差异，以及"如何在 UE 引擎外批量生成 → 导入 UE"的管线。2026 年 PC 级 SLM（小语言模型）准确率 +100%，AI 视频生成（LTX-2）在 RTX GPU 上 3 倍加速，本地创作工作流爆发。

**5 条证据**：
1. Stable Diffusion 3.5（2024-10）：Large 80 亿参数、Large Turbo、Medium 三档；Medium 可消费级显卡跑。
2. ComfyUI 是节点式工作流（类似 Substance Designer），能完整复现生成管线；相比 WebUI 提速 10-25%。
3. NVIDIA RTX 50 系 CES 2026 升级：PyTorch-CUDA 优化 + ComfyUI 原生 NVFP4/FP8 + RTX VSR（视频超分）；视频生成 3 倍加速、显存 -60%。
4. Lightricks LTX-2：音视频生成模型开源权重，NVIDIA 优化版 NVFP8 量化。
5. ControlNet（blur/canny/depth）让"可控生成"成为可能，工业级管线必备。

**本周动作**：
- 不要求跑通，但要 **看懂 ComfyUI 节点图的结构**（Load Checkpoint → CLIP Text Encode → KSampler → VAE Decode → Save Image）。
- 关注 1 个生成式 AI 资产管线教程（B 站 / YouTube），标星但不看。
- 长期目标：把"AI 生成 → ComfyUI 批处理 → UE 导入"作为外包给美术同学的工作流。

**资源链接**：
- ComfyUI 仓库：https://github.com/comfyanonymous/ComfyUI
- Stable Diffusion 3.5 模型：https://huggingface.co/stabilityai
- NVIDIA RTX AI 工具链：https://developer.nvidia.com/rtx-ai
- Vault 内：✗

---

## 3. 跨主题连接图

```
                         ┌──────────────────────────────┐
                         │  1. MCP / Unreal MCP         │ ← 横切
                         │  (AI 工具集成的 USB-C)        │
                         └──────────────────────────────┘
                                    │
        ┌─────────────────┬─────────┼─────────┬─────────────────────┐
        ▼                 ▼         ▼         ▼                     ▼
   ┌─────────┐      ┌─────────┐ ┌──────────┐ ┌──────────┐    ┌─────────────┐
   │ 2. AI   │      │ 5. LLM  │ │ 6. RL /  │ │ 7. PCG   │    │ 8. GenAI    │
   │ Coding  │      │ NPC     │ │ Learning │ │ 节点图   │    │ Assets      │
   │ Tools   │      │         │ │ Agents   │ │          │    │ SD/ComfyUI  │
   └─────────┘      └─────────┘ └──────────┘ └──────────┘    └─────────────┘
                          │              │
                          └──────┬───────┘
                                 ▼
                    ┌─────────────────────────────┐
                    │ 4. Neural Rendering / NNE   │ ← 运行时 AI 推理
                    │ (ONNX Runtime + ML Deformer)│
                    └─────────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────┐
                    │ 3. DLSS / 神经渲染          │ ← 画面生成
                    │ (DLSS 4.5 / DLSS 5)         │
                    └─────────────────────────────┘
```

**横切关系**：
- **MCP** 增强所有主题：你能用 MCP 调 Lyra 关卡、调 NNE 模型状态、调 PCG 生成器、调 SD 资产生成队列。
- **AI 编码工具** 加速所有主题：你的 Lyra 代码、Unreal 源码、Shader、Python 训练脚本全部能本地 Agent 化。
- **NNE** 是运行时 AI 推理的统一通道：Deformer / 风格迁移 / SD 实时生成都跑在这上面。

---

## 4. 主题 vs Vault 已有 AI-Tasks 对照

| 主题 | 已有 AI-Tasks | 状态 | 建议 |
|------|--------------|------|------|
| MCP / Unreal MCP | [[../AI-Tasks/UnrealMCP]] | W1 进行中 | 继续，本周读完 MCP 规范 |
| AI 辅助编程 | ✗ | 新主题 | **本周新建** `AI-Tasks/CodingTools/` |
| DLSS / 神经渲染 | ✗ | 新主题 | 列入 [[../05-技术雷达/]]，3 周内启动 |
| Neural Rendering | [[../AI-Tasks/NeuralRendering]] | W1 进行中 | 继续，扩展 NNE 章节 |
| LLM NPC | ✗ | 新主题 | 列入 [[../05-技术雷达/]]，1 月内启动 |
| Learning Agents | [[../AI-Tasks/MassAILearningAgents]] | W1 进行中 | 继续，关注 AReaL 进展 |
| PCG | [[../AI-Tasks/PCG]] | 待开始 | **本周启动 W1** |
| GenAI 资产 | ✗ | 二级主题 | 仅维护本索引，不深入 |

---

## 5. 一周 7 天行动表（最小可行版本）

| 日 | 主题 | 动作 | 产出 |
|----|------|------|------|
| **周一** | MCP | 读 Anthropic MCP 规范首章；克隆 python-sdk；跑通 filesystem 示例 | MCP-Reading-Guide.md + 1 篇源码笔记 |
| **周二** | AI 编码 | 装 Claude Code；在 Lyra 仓库跑 3 个真实任务 | 1 篇工具对比笔记 |
| **周三** | DLSS 4.5 | 在 Lyra 项目里启 DLSS 4.5；FrameView 抓数据 | 1 条 [[../04-性能优化备忘录/]] |
| **周四** | NNE | grep `Engine/Plugins/Plugins/NNE/` 模块结构；读 `IModel` | 1 篇 [[../02-引擎源码分析库/]] 笔记 |
| **周五** | 复盘 | 整理本周 5 篇笔记；建 [[../05-技术雷达/AI-GameDev]] 条目 | 1 篇 [[../07-日记/]] 周记 |
| **周六** | LLM NPC | 读 Inworld AI 文档 + Convai UE 插件 README | 1 篇 [[../05-技术雷达/]] 评估 |
| **周日** | 学习曲线 | 读 Karpathy 2025 总结 + 1 篇 AReaL 摘要 | 1 篇 [[../07-日记/]] 反思 |

---

## 6. 元数据

- **创建日期**：2026-06-29
- **创建者**：Mavis (AI assistant)
- **数据来源**：2026-06 实时网络搜索 + vault 已有 AI-Tasks 目录
- **下次更新**：每月 1 号刷新 DLSS / MCP / Claude Code 版本信息

---

*This is a living index. Refresh when Epic 5.8 → 5.9 ships or when MCP gets major updates.*