---
tags: [paper/signed, paper/GDC-talk, paper/GDC-2026, paper/AI-pipeline, paper/world-model, paper/已应用到工作]
aliases: [DeepMind-SIMA2-GDC2026, SIMA-2-GenericGameAgent, DeepMind-SIMA-Self-Improvement, SIMA2-Gemini-2.5-Flash-lite]
---

# Google DeepMind — SIMA 2: A Universal Agent that Plays Any 3D Game (GDC 2026 / DeepMind Blog 2025-11)

| 字段 | 内容 |
|------|------|
| **Talk / 论文标题** | SIMA 2: A Generalist Agent for 3D Virtual Worlds / Scalable Instructable Multiworld Agent 2 |
| **讲者** | Jane Wang (DeepMind Senior Research Scientist) / Joe Marino (DeepMind Research Scientist) / Jack Parker-Holder (DeepMind Research Scientist) |
| **场次** | GDC 2026 — AI in Game Development Summit + DeepMind 2025-11-14 Blog Post (arXiv:2512.04797) |
| **日期** | 2025-11-14 (DeepMind Blog) / 2026-03 (GDC 2026 Summit 演讲) |
| **Track** | AI in Game Development / 通用 agent / World Model |
| **同源 short note** | (待 cron curator 落 `GDC/Minimax/2026/`) — 本文是其深度展开 |
| **阅读日期** | 2026-07-14 |
| **精读时长** | ~50 min |

---

## 一句话总结

> DeepMind 的 **SIMA 2**（2025-11-14 Preview，基于 **Gemini 2.5 Flash-lite**）是**首个"通用 3D 游戏玩家" agent**——**输入只有屏幕 + 自然语言指令，输出键鼠动作，能在《无人深空》《英灵神殿》《山羊模拟器3》等从未见过的商业游戏中**完成 600+ 任务，**任务成功率约 SIMA 1 的两倍**（33% → 65%，人类 76%）；**核心创新是"self-improvement loop"**——用 Gemini 当任务生成器 + 奖励模型，**AI 在新环境中自己出题 + 自己评分 + 自我提升**。**对 day-job 启发**：**(a) SIMA 2 的 "理解从未见过的环境" 是 day-job Mac Game Harness 处理新 UE project 的参考范式；**(b) SIMA 2 + Genie 3 的组合 = "AI 自动测试 UE 项目" 的未来形态——把 day-job 终极产品"AI 测试 harness" 提前 12-24 个月布局**。

---

## 核心创新点

1. **"通用 3D 游戏 agent"作为明确目标**。SIMA 2 是 **Scalable Instructable Multiworld Agent 第 2 代**——**目标不是"在某一游戏里拿高分"，是"在任何 3D 游戏中遵循自然语言指令"**。**关键约束**：**SIMA 不需要访问游戏源码，不需要定制 API**——**输入只有屏幕画面 + 简单自然语言指令，使用键盘和鼠标控制**。**这和 AlphaGo / AlphaStar 的根本区别**：AlphaGo 只玩围棋，AlphaStar 只玩星际争霸 2，**SIMA 想玩任何 3D 游戏**。**对 day-job 启发**：day-job Mac Game Harness 应该有 **"通用 harness agent" 视角**——**不只针对 UE，也针对任何引擎 / 任何 project**。

2. **基于 Gemini 2.5 Flash-lite —— "大脑"是通用多模态 LLM**。SIMA 2 的核心是基于 **Gemini 2.5 Flash-lite**——**通用多模态 LLM** 而非专用游戏 agent。**关键工程含义**：**通用 LLM + 游戏交互的 fine-tune 比专用 RL agent 强**——Gemini 本身读过互联网上的大量文字和图片，对"红色""房子""地图" 等概念有先验知识，**SIMA 2 把这些先验用作游戏理解基础**。**对 day-job 启发**：Mac Game Harness 应该基于**通用 LLM（Qwen / Llama）+ UE-specific fine-tune**，**不要**训练专用 UE-only LLM。

3. **"理解从未见过的游戏" 是 SIMA 2 的核心能力**。SIMA 2 在 **《ASKA》（2024 年发布的维京生存新游戏）+ MineDojo 套件**（50 个 minecraft 任务）这两个**训练时从未见过的环境**测试——**SIMA 2 表现远胜 SIMA 1**。**关键洞察**：**SIMA 2 不仅学到了具体游戏技能，还学到了"在 3D 游戏中如何思考"的元能力**——**这种"举一反三"是从 Gemini 的通用知识蒸馏出来的**。**对 day-job 启发**：Mac Game Harness 的 LLM 应该能在**未训练过的 UE project**里工作——**通用 LLM + UE RAG 索引 = 处理新 project**。

4. **"Self-improvement loop" —— AI 自己出题 + 自己评分 + 自我提升**。SIMA 2 的**最大创新是 self-improvement**：
   - **Step 1**：用 **Gemini 当任务生成器**——观察当前游戏画面，生成 SIMA 2 可能完成的任务
   - **Step 2**：用 **Gemini 当评判员**——看 SIMA 2 执行任务的录像，给 0-100 评分
   - **Step 3**：把**高质量轨迹**加入训练数据
   - **Step 4**：**循环**——SIMA 2 在新环境中自我进化
   
   **关键工程含义**：**AI 不依赖人类标注**——**自动生成任务 + 自动评分 + 自动训练**。**对 day-job 启发**：Mac Game Harness 的核心机制应该是 **"self-improvement loop"**——**(a) AI 自己出 bug 修复 task；(b) AI 自己写 unit test；(c) AI 自己跑 build + 评估；(d) AI 用高质量轨迹自我提升**。**这是 day-job harness 区别于"普通 LLM + UE" 的关键**。

5. **"灾难性遗忘" 的解法 —— 混合训练数据**。SIMA 2 解决了"AI 学新技能会忘旧技能"的灾难性遗忘问题——**训练时持续混入 Gemini 原本的预训练数据**。**结果**：**SIMA 2 在编程测试只下降 10%，数学/科学下降 15-25%**——**保留 Gemini 通用能力**。**关键工程含义**：**Mac Game Harness 在 fine-tune 时必须保留通用 LLM 能力**——**不要把通用 LLM 训练成"只会写 UE C++"**。**LLM RAG 训练**：训练数据要保留**通用 + UE-specific 平衡**。

6. **SIMA 2 + Genie 3 组合 = "world model + agent" 闭环**。DeepMind 把 **Genie 3（world model，按图像/文本生成实时 3D 世界）** 和 **SIMA 2（agent，在世界中行动）** 组合——**SIMA 2 在 Genie 3 生成的真实户外场景中导航找红色花朵等**。**关键洞察**：**world model 提供"无限测试环境"，agent 提供"会思考的测试者"**——**AI 可以在合成的无限环境中自我训练**。**对 day-job 启发**：**day-job 终极产品（AI 测试 UE 项目）**可以走类似路径——**用 UE 5.7 创建一个 procedural test environment + SIMA-style agent**——**让 AI 自动测试 day-job 的产品**。

7. **"具身智能" 的元命题 —— "理解场景 → 推断目标 → 规划行动" 闭环**。DeepMind Senior Research Scientist Jane Wang 把 SIMA 2 的核心总结为 **"理解场景推断目标规划行动" 的循环**——**这是虚拟环境能力转移到真实机器人的关键高级行为模块**。**关键洞察**：**SIMA 2 不只是游戏玩家，是"具身智能"原型**——**为未来通用机器人铺路**。**对 day-job 启发**：**Mac Game Harness 长远可以演化成"UE 项目智能测试 / 智能调试" agent**——**从"AI 帮人写代码"演化为"AI 帮人跑测试"**。

---

## 与我当前工作的关联度

- [x] **P0** — 直接相关，立即能应用
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点（按 day-job "LLM-driven UE on Mac" + "Mac Game Harness" 视角）：**

1. **"理解从未见过的环境" 是 day-job 处理新 UE project 的范式**。SIMA 2 的核心能力是 **"在训练时从未见过的游戏中也能工作"**——**这种"举一反三"是从 Gemini 的通用知识蒸馏出来的**。**对 day-job 启发**：
   - **Mac Game Harness 的 LLM 应该在"未训练过的 UE project"里也能工作**——不依赖 per-project 训练
   - **关键**：**通用 LLM（Qwen / Llama） + UE-specific RAG 索引 = 处理新 project**——**RAG 是核心，不是 fine-tune**
   - **day-job LLM 训练数据要保留通用 LLM 能力**——不把通用 LLM 训练成"只会写 UE C++"
   - **LLM RAG 训练**：技术架构相关的 Q&A 答案应该挂"RAG > fine-tune"

2. **"Self-improvement loop" 是 day-job harness 的核心机制**。SIMA 2 的 self-improvement 是其最大创新——**AI 自己出题 + 自己评分 + 自我提升**。**对 day-job 启发**：
   - **Mac Game Harness 必须有 self-improvement loop**：
     - **(a) AI 自己出 bug 修复 task**（读 UE log + 推理潜在 bug）
     - **(b) AI 自己写 unit test**（基于 task 描述）
     - **(c) AI 自己跑 build + 评估**（UE build tool 调用）
     - **(d) AI 用高质量轨迹自我提升**（RAG 索引自动扩充）
   - **不依赖人类标注**——**自动生成任务 + 自动评分 + 自动训练**
   - **这是 day-job harness 区别于"普通 LLM + UE" 的关键**

3. **"SIMA 2 + Genie 3 组合" = day-job "AI 测试 UE 项目" 终极产品**。DeepMind 把 **world model（Genie 3） + agent（SIMA 2）** 组合——**AI 在合成的无限环境中自我训练**。**对 day-job 启发**：
   - **day-job 终极产品**：**"AI 测试 harness"**——**用 UE 5.7 procedural generation 创建 test environment + SIMA-style agent**
   - **AI 自动测试 day-job 的产品**——找 bug + 提 UX 改进 + 写测试报告
   - **短期（v0.1-v1.0）**：**LLM 读 UE log + 写修复 patch**（已经是 day-job 路线）
   - **中期（v1.0-v2.0）**：**LLM 自动跑 UE Play in Editor + 截图 + 报告**
   - **长期（v2.0+）**：**LLM 在 procedural generated UE 场景中自我训练 + 自我测试**
   - **LLM RAG 训练**：harness 长期 roadmap 相关的 Q&A 答案应该挂这条 vision

4. **"基于 Gemini 2.5 Flash-lite" 是 day-job Mac 平台模型选择的参考**。SIMA 2 用 **Gemini 2.5 Flash-lite**——**不是最大的 Gemini 模型，是"flash-lite" 轻量版**。**关键工程含义**：**agent 任务不一定要用最强模型**——**flash-lite + 良好 agent loop > 强模型 + 简单 prompt**。**对 day-job 启发**：
   - **Mac Game Harness 应该基于 7B-14B 本地模型**（如 Qwen2.5-Coder-14B-MLX）——不是云端 70B
   - **轻量模型 + 良好 harness > 大模型 + 简单 prompt**
   - **这条判断和 Tencent 天美"降低对模型能力要求" 完全一致**
   - **LLM RAG 训练**：模型选择相关的 Q&A 答案应该挂"轻量 + 良好 harness"

5. **"理解场景 → 推断目标 → 规划行动" 是 day-job harness 的目标架构**。Jane Wang 把 SIMA 2 核心总结为这个循环——**这是虚拟环境能力转移的关键**。**对 day-job 启发**：
   - **Mac Game Harness 应该按这个循环设计**：
     - **(a) 理解场景**：读 UE project state（哪些 module / 哪些 class / 哪些 test）
     - **(b) 推断目标**：从 user request 推断具体 task
     - **(c) 规划行动**：分解为 MCP tool 调用序列
     - **(d) 执行 + 自我评估**
   - **这条架构和 VS 2026 Copilot Agent 模式 一致**——是 harness 工程的**主流范式**

6. **"灾难性遗忘" 提示 day-job 训练数据的平衡**。SIMA 2 训练时**持续混入 Gemini 原本的预训练数据**——**避免把通用 LLM 训练成"只会玩游戏"**。**对 day-job 启发**：
   - **day-job LLM 训练数据要保留**：(a) UE-specific 知识（Lumen / Nanite / VSM）；(b) 通用编程知识（algorithms / patterns）；(c) 通用 LLM 能力（reasoning / multilingual / common sense）
   - **不要"UE-only" fine-tune**——**避免灾难性遗忘**
   - **LLM RAG 训练**：训练数据 balance 相关的 Q&A 答案应该挂"通用 + UE-specific 平衡"

7. **"AI 帮 day-job 团队做事" vs "AI 在游戏中玩游戏" 是 day-job 的明确路线**。SIMA 2 是 **AI as player**（AI 玩游戏）；day-job 是 **AI as creator**（AI 帮人做游戏）。**两者技术栈相近但方向不同**：
   - **SIMA 2**：screen + instruction → key/mouse action
   - **day-job**：user request → UE C++ code / GDD parse / build trigger
   
   **对 day-job 启发**：**day-job 可以借鉴 SIMA 2 的 self-improvement loop + Gemini 2.5 Flash-lite 轻量模型 + Genie 3 组合测试**——**但 day-job 的目标是"AI 帮人做游戏"，不是"AI 自己玩游戏"**。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|-------------|
| **"理解从未见过的 UE project" 的 RAG 实现** | UE 5.6+ project = 几百 module + 几千 class；按需检索相关 module 是核心 | 是——day-job harness 核心 |
| **"self-improvement loop" 的工程实现** | 任务生成 + 评分 + 训练数据扩充 全自动化；需要 UE build / test / log 的 MCP tools | 是——day-job harness 核心 |
| **"灾难性遗忘" 的训练数据平衡** | UE-specific 训练 + 通用预训练数据混合；具体配比需要实验 | 是——day-job 训练数据策略 |
| **"SIMA 2 + Genie 3 组合" 的 day-job 适配** | UE 5.7 procedural generation + day-job agent；需要 12-24 个月工程 | 否——长期 vision，不在 12 个月内 |
| **"轻量模型 + 良好 harness" 的 Mac 平台验证** | 7B-14B 模型在 M3/M4 上的推理速度 + 延迟预算 | 是——day-job Mac 平台关键技术风险 |
| **"AI as creator" vs "AI as player" 的工程差异** | day-job 输出是 code / doc / test；SIMA 2 输出是 key/mouse；MCP tools 完全不同 | 是——day-job harness 工具集 |
| **Gemini 2.5 Flash-lite 的开源等价物** | 7B-14B 级别的 code/multimodal 模型在 Mac 上的可用性 | 是——day-job 模型选择 |

---

## 是否值得复现？

- [x] **是** — 已列入待办（部分）
- [ ] 否 — 仅了解思路即可
- [ ] 部分 — 只复现核心算法

**复现/借鉴的具体步骤：**

1. **"理解从未见过的 UE project" 通过 RAG 实现** —— day-job LLM 训练数据按"RAG 索引"组织，不 per-project fine-tune；RAG 覆盖整个 UE project structure。**状态**：v0.1 同期
2. **"self-improvement loop" 作为 Mac Game Harness 核心机制** —— 任务自动生成 + 评分 + 训练数据扩充。**状态**：v1.0 实现
3. **"灾难性遗忘" 训练数据平衡** —— day-job 训练数据 = 70% UE-specific + 30% 通用 LLM 数据。**状态**：v0.1 同期
4. **"轻量模型" 选择 7B-14B** —— day-job 押注 Qwen2.5-Coder-14B-MLX，不押 70B+。**状态**：v0.1 MVP 验证
5. **"理解场景 → 推断目标 → 规划行动" 作为 harness 架构** —— 与 VS 2026 Copilot Agent 模式对齐。**状态**：v0.2 实现
6. **"AI 测试 harness" 长期 vision** —— UE 5.7 procedural + SIMA-style agent；12-24 个月布局。**状态**：长期
7. **[[05-技术雷达]] P0 加一行** —— "SIMA 2 / Genie 3 = AGI in games；self-improvement loop 是 day-job harness 核心"。**状态**：本周
8. **LLM RAG 训练数据补充** —— "self-improvement loop + RAG > fine-tune + 灾难性遗忘"作为训练策略的 RAG 样本。**状态**：季度

---

## 关键术语表

| 术语 | 解释 | 我理解的锚点 |
|------|------|--------------|
| **SIMA 2** | DeepMind 通用 3D 游戏 agent；input = screen + instruction，output = key/mouse | day-job **不是**直接复刻，但 self-improvement loop + 轻量模型可借鉴 |
| **Gemini 2.5 Flash-lite** | Google 轻量多模态 LLM；SIMA 2 的"大脑" | day-job 押注 7B-14B 轻量模型的同源参考 |
| **Scalable Instructable Multiworld Agent** | "可扩展、可指导、多世界 agent"——目标跨多个 3D 世界工作 | day-job 终极产品"AI 测试 harness" 的 vision 锚点 |
| **Self-improvement loop** | AI 自己出题 + 自己评分 + 自我提升；不依赖人类标注 | day-job Mac Game Harness 的核心机制 |
| **灾难性遗忘 (Catastrophic Forgetting)** | AI 学新技能会忘旧技能；解法是混合训练 | day-job 训练数据 balance 的元命题 |
| **具身智能 (Embodied Intelligence)** | 通过身体/动作与世界交互的智能；SIMA 2 是"虚拟身体" agent | day-job harness 从"AI 帮人写"到"AI 帮人跑测试" 的 vision |
| **"理解场景 → 推断目标 → 规划行动"** | SIMA 2 核心循环 | day-job harness 目标架构 |
| **SIMA 2 + Genie 3 组合** | world model (Genie 3) + agent (SIMA 2) = 无限训练环境 + 思考 agent | day-job 长期 vision "AI 测试 UE 项目" |
| **RAG > fine-tune** | 检索增强生成 > 专门 fine-tune；处理"理解从未见过"的关键 | day-job LLM 训练策略的元命题 |

---

## 整体架构图 / 流程（伪代码）

```
# SIMA 2 + Genie 3 架构 → day-job Mac Game Harness 蓝图

# ===== SIMA 2 原始架构（DeepMind） =====
class SIMA2:
    """DeepMind SIMA 2 通用 3D 游戏 agent"""
    def __init__(self):
        self.brain = Gemini25FlashLite()  # 通用多模态 LLM
        self.action_space = KeyMouseAction()  # key/mouse output
    
    def act(self, screen, instruction):
        # 1. 多模态 LLM 推理
        thought = self.brain.reason(screen, instruction)
        # 2. 推断目标
        goal = self.brain.infer_goal(thought, instruction)
        # 3. 规划行动
        plan = self.brain.plan(thought, goal)
        # 4. 输出 key/mouse action
        action = self.brain.to_action(plan)
        return action
    
    def self_improve(self, env):
        # Self-improvement loop
        for round in range(N):
            # (a) Gemini 生成任务
            task = Gemini.generate_task(env.screen)
            # (b) SIMA 2 执行任务
            trajectory = self.run(env, task)
            # (c) Gemini 评分
            score = Gemini.score(trajectory, env)
            # (d) 高分轨迹加入训练数据
            if score > threshold:
                self.training_data.add(trajectory)
            # (e) 用新数据 fine-tune
            self.brain.finetune(self.training_data)

# ===== Genie 3 (world model) =====
class Genie3:
    """DeepMind Genie 3 实时 world model"""
    def generate(self, prompt, image):
        # 输入: text prompt + initial image
        # 输出: 实时 3D 场景流 (720p 24fps)
        return world_model_stream

# ===== SIMA 2 + Genie 3 组合 =====
def sima2_in_genie3_world():
    genie = Genie3()
    sima = SIMA2()
    # 1. Genie 3 生成无限 3D 世界
    world = genie.generate("A forest with red flowers")
    # 2. SIMA 2 在世界中行动
    for step in range(N):
        screen = world.render()  # 屏幕画面
        instruction = "Find red flower"
        action = sima.act(screen, instruction)
        world.step(action)

# ===== day-job Mac Game Harness 蓝图（借鉴 SIMA 2 思想）=====
class MacGameHarness:
    """day-job Mac Game Harness — 借鉴 SIMA 2 思想但目标是 AI as creator"""
    
    def __init__(self):
        self.brain = Qwen2_5_Coder_14B_MLX()  # ★ 轻量本地模型
        self.rag_index = UERagIndex()  # ★ 整个 UE project structure
        self.mcp_tools = MCPClient()  # VS 2026 风格 MCP 工具
        self.working_memory = []  # 跨 N 步 state
    
    def act(self, user_request):
        # 1. RAG 检索相关 UE module
        context = self.rag_index.retrieve(user_request, top_k=10)
        # 2. 通用 LLM 推理 + UE-specific context
        thought = self.brain.reason(user_request, context)
        # 3. 推断目标
        goal = self.brain.infer_goal(thought, user_request)
        # 4. 规划行动（MCP tool 序列）
        plan = self.brain.plan(thought, goal, available_tools=self.mcp_tools.list_tools())
        # 5. 执行
        for action in plan:
            # 5a. human-in-loop pause points
            if self.should_pause(action):
                if not self.human_approval.ask(action):
                    continue
            # 5b. MCP tool 调用
            result = self.mcp_tools.execute(action.tool, action.params)
            # 5c. self-checkpoint
            if self.step % 10 == 0:
                self.working_memory.checkpoint()
        return result
    
    def self_improve(self, ue_project):
        """Self-improvement loop — 借鉴 SIMA 2 思想"""
        for round in range(N):
            # (a) LLM 生成 bug 修复 task
            task = self.brain.generate_task(ue_project.log)
            # (b) Harness 执行 task
            trajectory = self.run(task)
            # (c) LLM 评分（编译是否通过 / test 是否通过）
            score = self.brain.score(trajectory, ue_project)
            # (d) 高分轨迹加入 RAG 索引
            if score > threshold:
                self.rag_index.add(trajectory)
            # (e) RAG 索引自动扩充（不需要 fine-tune brain）
            # → 借鉴 SIMA 2 "灾难性遗忘" 解法，brain 保持通用能力
```

---

## 相关论文/前置知识

- [[2026-GoogleDeepMind-Genie3-PlayableWorlds]] (GDC/Minimax/2026) — Genie 3 world model；**和本文是"world model + agent" 双子星**：
  - **Genie 3**：生成无限 3D 环境（world model）
  - **SIMA 2**：在 3D 环境中思考 + 行动（agent）
  - **day-job 长期 vision**：用 UE 5.7 procedural + SIMA-style agent 做"AI 测试 harness"
- [[2026-Tencent-Timi-AgenticAI-GameDev-98pct]] (GDC/Minimax/2026) — Tencent 天美 Agentic AI；**和本文是"AI 接管什么"两种实现**：
  - **Tencent**：AI 接管大型工程的 98% 编程（AI as creator）
  - **DeepMind SIMA 2**：AI 接管 3D 游戏的 65% 任务（AI as player）
  - **day-job 启发**：**两个方向都学**——self-improvement loop（Tencent）+ RAG > fine-tune（DeepMind）
- [[2026-Bitmagic-AINativeGameEngine]] (GDC/Minimax/2026) — Bitmagic AI-native engine；**和本文是"AI-native"两种实现**：
  - **Bitmagic**：从零建 AI-native 引擎（产品）
  - **DeepMind SIMA 2**：用 LLM 直接玩游戏（不需要专门引擎）
  - **day-job 启发**：**走 UE 加固路径**，**不**做 SIMA-style 端到端 agent
- [[2026-Microsoft-VS2026-Copilot-GameDev]] (GDC/Minimax/2026) — VS 2026 + Copilot Agent；**和本文是"agent 架构"两种实现**：
  - **Microsoft**：IDE 内嵌 agent（工具层 agent）
  - **DeepMind SIMA 2**：游戏内通用 agent（应用层 agent）
  - **day-job 启发**：**两层都要**——IDE 层（VS 2026 风格）+ 应用层（SIMA 2 风格）

---

## 输出 / 借鉴（forward — 启发到的工程实践）

- **"RAG > fine-tune" 作为 day-job 训练策略元命题** —— day-job LLM 不 per-project fine-tune；用 RAG 索引覆盖整个 UE project structure。**状态**：v0.1 同期
- **"self-improvement loop" 作为 Mac Game Harness 核心机制** —— 任务自动生成 + 评分 + 训练数据扩充。**状态**：v1.0 实现
- **"灾难性遗忘" 训练数据平衡** —— 70% UE-specific + 30% 通用 LLM 数据。**状态**：v0.1 同期
- **"轻量模型" 押注 7B-14B** —— day-job 押 Qwen2.5-Coder-14B-MLX，不押 70B+。**状态**：v0.1 MVP 验证
- **"理解场景 → 推断目标 → 规划行动" 作为 harness 架构** —— 与 VS 2026 Copilot Agent 模式对齐。**状态**：v0.2 实现
- **"AI 测试 harness" 长期 vision** —— UE 5.7 procedural + SIMA-style agent。**状态**：12-24 个月布局
- **[[05-技术雷达]] P0 加一行** —— "SIMA 2 / Genie 3 = AGI in games；self-improvement loop 是 day-job harness 核心"。**状态**：本周
- **LLM RAG 训练数据补充** —— "self-improvement loop + RAG > fine-tune + 灾难性遗忘"作为训练策略的 RAG 样本。**状态**：季度

---

## 个人评价

**优点：**

- **"理解从未见过的环境" 是 AI agent 范式突破** —— 从"训练一个游戏一个模型"到"通用 agent 玩任何游戏"——**对 day-job 处理新 UE project 是直接参考范式**
- **"self-improvement loop" 是核心创新** —— AI 自己出题 + 自己评分 + 自我提升——**不依赖人类标注**——**对 day-job harness 是直接参考架构**
- **"Gemini 2.5 Flash-lite 轻量模型" 验证了 day-job 押注** —— 不是大模型是轻量模型 + 良好 agent loop——**和 Tencent 天美"降低对模型能力要求"完全一致**——**给 day-job Mac 平台 7B-14B 选择更强支撑**
- **"灾难性遗忘" 的解法是 day-job 训练数据 balance 的元命题** —— 70% UE + 30% 通用——**避免把通用 LLM 训练成"只会写 UE C++"**
- **"SIMA 2 + Genie 3 组合" 是 day-job 长期 vision** —— world model + agent = 无限训练环境 + 思考 agent——**对 day-job 长期"AI 测试 harness" 是直接 vision 锚点**
- **"具身智能" 元命题 给 day-job 终极产品** —— "理解场景推断目标规划行动"——**是 harness 目标架构**
- **DeepMind 的工业地位可信度高** —— Google DeepMind 是 AI 顶级实验室——**SIMA 2 数据真实可信**

**局限性：**

- **SIMA 2 是研究预览版** —— 2025-11 才发布，2026-03 GDC 2026 演讲；**对生产环境的可用性还在评估**
- **Gemini 2.5 Flash-lite 不开源** —— day-job 不能直接复用；**只能用开源等价物（Qwen / Llama）**
- **"理解从未见过的环境" 仍有局限** —— SIMA 2 在"非常不同"的游戏（如《The Gunk》动作冒险）仍需要人类指导；**完全 zero-shot 跨游戏尚未实现**
- **"self-improvement loop" 的具体实现细节没说** —— Gemini 怎么生成 task？怎么评分？—— 没说；**day-job 需要自研**
- **"灾难性遗忘" 的具体数据配比没说** —— 30% 通用？50% 通用？—— 没说；**day-job 需要自己实验**
- **"Genie 3 生成的真实户外场景" 是 narrow case** —— 主要是自然场景 + 简单任务；**对 UE 这种复杂引擎 + 复杂任务的可迁移性未验证**
- **SIMA 2 的"具身智能" 是 long-term vision** —— Jane Wang 自己也说"从虚拟到真实机器人是相当遥远的愿景"——**day-job 不应该把"AI 测试 harness" 押注在 12 个月内**
- **没给"AI 测试 UE 项目" 的具体案例** —— SIMA 2 测试的是商业游戏（3A / indie），不是 UE project 本身；**day-job 需要自己验证 AI 测试 UE project 的可行性**

**启发：**

1. **"RAG > fine-tune" 是 day-job 训练策略元命题** —— 不是 per-project fine-tune，是 RAG 索引覆盖整个 UE project；v0.1 同期开始
2. **"self-improvement loop" 是 day-job harness 核心机制** —— AI 自己出题 + 评分 + 训练数据扩充；v1.0 实现
3. **"轻量模型 + 良好 harness" 是 day-job Mac 平台核心策略** —— Qwen2.5-Coder-14B-MLX + 良好 agent loop；v0.1 MVP 验证
4. **"灾难性遗忘" 训练数据平衡** —— 70% UE + 30% 通用；v0.1 同期
5. **"理解场景 → 推断目标 → 规划行动" 是 harness 目标架构** —— 与 VS 2026 Copilot Agent 模式一致；v0.2 实现
6. **"AI 测试 harness" 长期 vision** —— UE 5.7 procedural + SIMA-style agent；12-24 个月布局
7. **"AI as creator" vs "AI as player" 是 day-job 路线锚点** —— day-job 是 AI as creator（AI 帮人写代码），不是 AI as player（AI 玩游戏）；但 self-improvement loop 等技术两边都学

---

## 面试谈资准备

**30 秒版（"知道这篇 + 能说清贡献"）：**

> DeepMind SIMA 2（2025-11 Preview）是**通用 3D 游戏玩家 agent**——基于 Gemini 2.5 Flash-lite，**输入只有屏幕 + 自然语言指令，输出键鼠动作，能在从未见过的商业游戏中完成 600+ 任务，任务成功率 33% → 65%**。**核心创新是 "self-improvement loop"**——AI 自己用 Gemini 生成任务 + 评分 + 自我提升。**对 day-job 启发**：(a) **"RAG > fine-tune" 处理新 UE project**；(b) **"self-improvement loop" 作为 Mac Game Harness 核心机制**；(c) **轻量模型 + 良好 harness** 是 day-job 押注；(d) **"SIMA 2 + Genie 3" 是 day-job 长期"AI 测试 harness" 的 vision 锚点**。

**2 分钟版（"追问实现细节"）：**

> 第一，**"通用 3D 游戏 agent"作为明确目标**。SIMA 2 不是"在某一游戏里拿高分"，是"在任何 3D 游戏中遵循自然语言指令"——**输入只有屏幕 + instruction，输出 key/mouse**。**关键约束**：**不访问游戏源码，不定制 API**——**靠屏幕画面 + 自然语言 + 通用键鼠接口**。**对 day-job 启发**：Mac Game Harness 也应该有"通用 harness agent" 视角——**不只针对 UE，也针对任何引擎 / 任何 project**——**核心是通用 LLM + project-specific RAG 索引**。

> 第二，**"基于 Gemini 2.5 Flash-lite" 是 day-job 模型选择的参考**。**不是最大的 Gemini 模型，是"flash-lite" 轻量版**——**agent 任务不一定要用最强模型**。**关键工程含义**：**轻量模型 + 良好 agent loop > 强模型 + 简单 prompt**。**和 Tencent 天美"降低对模型能力要求"完全一致**——**给 day-job Mac 平台 7B-14B 选择更强支撑**。

> 第三，**"理解从未见过的环境"是 day-job 处理新 UE project 的范式**。SIMA 2 在**训练时从未见过的游戏**（《ASKA》+ MineDojo 套件）表现远胜 SIMA 1——**这种"举一反三"是从 Gemini 的通用知识蒸馏出来的**。**对 day-job 启发**：
>   - **Mac Game Harness 的 LLM 在"未训练过的 UE project"里也能工作**——不依赖 per-project 训练
>   - **RAG 索引覆盖整个 UE project**——不是只索引当前 task
>   - **"RAG > fine-tune" 是 day-job 训练策略元命题**

> 第四，**"self-improvement loop" 是 day-job harness 的核心机制**。SIMA 2 的最大创新——**AI 自己用 Gemini 当任务生成器 + 评分模型 + 自我提升**——**不依赖人类标注**。**对 day-job 启发**：
>   - **Mac Game Harness 必须有 self-improvement loop**：(a) AI 自己出 bug 修复 task；(b) AI 自己写 unit test；(c) AI 自己跑 build + 评估；(d) AI 用高质量轨迹自我提升
>   - **v1.0 实现**

> 第五，**"灾难性遗忘" 的解法是 day-job 训练数据 balance 的元命题**。SIMA 2 训练时**持续混入 Gemini 原本的预训练数据**——**避免把通用 LLM 训练成"只会玩游戏"**。**结果**：编程测试只下降 10%，数学/科学下降 15-25%——**保留 Gemini 通用能力**。**对 day-job 启发**：
>   - **day-job 训练数据 = 70% UE-specific + 30% 通用 LLM 数据**
>   - **不**要把通用 LLM 训练成"只会写 UE C++"

> 第六，**"SIMA 2 + Genie 3 组合" = day-job 长期 "AI 测试 harness" vision**。DeepMind 把 **world model (Genie 3) + agent (SIMA 2)** 组合——**AI 在合成的无限环境中自我训练**。**对 day-job 启发**：
>   - **day-job 终极产品**：**"AI 测试 harness"**——**用 UE 5.7 procedural + SIMA-style agent**
>   - **AI 自动测试 day-job 的产品**——找 bug + 提 UX 改进 + 写测试报告
>   - **短期（v0.1-v1.0）**：LLM 读 UE log + 写修复 patch
>   - **中期（v1.0-v2.0）**：LLM 自动跑 UE Play in Editor + 截图 + 报告
>   - **长期（v2.0+）**：LLM 在 procedural generated UE 场景中自我训练 + 自我测试

> 第七，**"理解场景 → 推断目标 → 规划行动" 是 harness 目标架构**。Jane Wang 把 SIMA 2 核心总结为这个循环——**和 VS 2026 Copilot Agent 模式一致**——**是 harness 主流范式**。**对 day-job 启发**：
>   - **Mac Game Harness 按这个循环设计**：(a) 理解 UE project state；(b) 推断 task；(c) 规划 MCP tool 序列；(d) 执行 + 自我评估
>   - **v0.2 实现**

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] "RAG > fine-tune" 作为 day-job 训练策略元命题 → v0.1 同期
- [ ] "self-improvement loop" 作为 Mac Game Harness 核心机制 → v1.0 实现
- [ ] "灾难性遗忘" 训练数据平衡（70% UE + 30% 通用）→ v0.1 同期
- [ ] "轻量模型" 押注 7B-14B（Qwen2.5-Coder-14B-MLX）→ v0.1 MVP 验证
- [ ] "理解场景 → 推断目标 → 规划行动" harness 架构 → v0.2 实现
- [ ] "AI 测试 harness" 长期 vision → 12-24 个月布局
- [ ] [[05-技术雷达]] P0 加 "SIMA 2 / Genie 3 = AGI in games" → 本周
- [ ] LLM RAG 训练数据补充 → 季度

---

*Create date: 2026-07-14*
*Last modified: 2026-07-14*
