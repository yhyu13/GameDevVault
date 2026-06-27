# 用 MCP 给 UE5 造了 10 万条训练数据后，我发现微调 3B 小模型就能吊打面试官

> 写在前面：这不是一篇"AI 赋能游戏开发"的软文。这是我们团队实打实踩了三个月坑之后的硬核复盘——怎么用 **Model Context Protocol (MCP)** 让 Claude/GPT-4 自动给 UE5 生成训练数据，然后拿这些数据微调一个 3B 的小模型，最后让它在面试题上表现超过原始大模型。

---

## 一、引子：那个让我血压飙升的面试

去年秋招，我面了一个候选人的 UE5 渲染模块。聊 Nanite 的时候，他答得天花乱坠："GPU-Driven Pipeline，CPU 完全不参与，全在 GPU 上做 Culling 和 LOD 选择。"

我追问了一句："那 CPU 在 Cook 阶段干什么？"

他愣了三秒，然后——开始编。

"呃……CPU 主要负责……资源管理？"

我当时就悟了：这人对 Nanite 的理解停留在营销话术层面。真正的源码细节——Cluster 怎么生成、DAG 怎么构建、LOD 误差怎么计算、Page 怎么打包——他一概不知。

面完我走出会议室，脑子里只有一个问题：

**如果让 AI 来回答这些题，它会比这个候选人强吗？**

试了一下 Claude 3.5 Sonnet。问它 "Nanite 的 Instance Culling 和 Cluster Culling 的执行顺序和各自作用"，它答对了大概 70%，但把 HZB 的更新时机说错了，而且没给出具体的源码文件路径。

原因很简单：**Claude 的训练数据截止于某个时间点，它没见过 UE5 最新的源码。**

那如果我能让 Claude 在回答问题的时候，**实时去查 UE5 的源码和 API 签名**呢？

这就是 MCP 的切入点。

---

## 二、为什么现有方案不行

在说我们的方案之前，先聊聊为什么已有的训练数据生成方法不够看。

**方案 A：人工写问答对。**

找几个 UE5 专家，每人写 50 条高质量的问答。问题是：50 条够干什么？覆盖不了 20 个核心模块，更覆盖不了每个模块的细枝末节。而且专家的时间贵得离谱，一条问答对光是查证源码路径就要半小时。

**方案 B：让 LLM 直接生成。**

给 Claude 一个 prompt："请生成 100 条关于 UE5 Nanite 的面试题和答案。" 它确实能生成，但幻觉率高得吓人——函数名拼错、源码路径不存在、把 UE4 的 API 说成 UE5 的。没有上下文约束的 LLM，本质上是在"合理猜测"，不是在"准确回答"。

**方案 C：拿公开文档做 RAG。**

UE5 的官方文档写得不错，但有两个致命问题：
1. 文档滞后于源码，很多实现细节文档里根本不提
2. 文档是"说明文"，不是"面试对话"——你需要的是 "面试官问 A，候选人答 B，面试官追问 C" 这种多轮交互，而不是平铺直叙的 API 说明

所以问题的核心是：**如何让最强的 LLM 在生成训练数据时，能实时、准确地获取 UE5 的引擎上下文？**

MCP 给出了答案。

---

## 三、破局：MCP 是什么，为什么它能解决这个问题

**MCP（Model Context Protocol）** 是 Anthropic 开源的一个协议，你可以把它理解为 AI 和工具之间的 **"USB-C 接口"**。

以前你让 LLM 写代码，它只能靠自己脑子里的知识。有了 MCP，它可以向外部工具"打电话"——查文件、读数据库、调 API、甚至操控游戏引擎。

**Unreal MCP** 就是这个生态里针对 UE5 的实现。它能提供什么？

- 源码文件路径和目录结构
- C++ API 的完整签名（函数名、参数、返回值）
- Console 变量的当前值和默认值
- 当前编辑器的状态（选中什么 actor、开了什么窗口）

这意味着：**Claude 在写 "Nanite 的 Cluster Culling 是怎么实现的" 这个答案时，可以实时去问 Unreal MCP："Hey，Cluster Culling 的源码在哪？用了哪些 Compute Shader？"**

然后它拿到的答案，函数名是对的，源码路径是对的，甚至 Console 变量的默认值也是对的。

这就是我们项目的核心洞察：**用 MCP 把最强 LLM 和 UE5 引擎上下文连接起来，让它生成高质量、低幻觉的训练数据。然后用这些数据去微调一个小模型，让小模型拥有接近大模型的领域知识，但推理成本只有几百分之一。**

项目代号：**UE5 Training MCP Pipeline**。

---

## 四、六阶段流水线：从 0 到可评估的微调模型

整个项目拆成六段，像工厂流水线一样运转：

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1      Phase 2      Phase 3      Phase 4           │
│  数据生成  →   数据剪枝  →   数据准备  →   小模型训练       │
│     │           │           │           │                   │
│  mcp_data    data_pruner   data_prep   train_small          │
│  _generator.py   .py         .py        _model.py           │
│     │           │           │           │                   │
│     └───────────┴───────────┘           │                   │
│              ↓                            ↓                   │
│  Phase 5      Phase 6                                       │
│  评估    →   Excel 报告                                     │
│     │           │                                           │
│  eval_model  generate_report                                │
│     .py         .py                                         │
└─────────────────────────────────────────────────────────────┘
```

下面我挑四个核心阶段展开讲。

---

## 五、Phase 1：数据生成——不是单轮 QA，是多轮对话

很多做训练数据的人有个误区：觉得问答对就是 "Q: 什么是 Nanite？ A: Nanite 是 UE5 的虚拟几何体系统。" 这种单轮问答。

这种数据训出来的模型，在真实面试里表现很差。因为真实面试是**多轮对话**——面试官问一个开放性问题，候选人答个大概，面试官追问细节，候选人再深入，几轮之后才见真章。

所以我们的 `mcp_data_generator.py` 强制生成 **4-5 轮的对话**，不是单轮 QA。

### 6 种对话模板

| 模板 | 场景 | 示例开头 |
|------|------|----------|
| interview_technical | 技术面试 | "请解释 Nanite 的 GPU-Driven Pipeline 中 Instance Culling 和 Cluster Culling 的执行顺序" |
| code_explanation | 代码解释 | "这段代码来自 NaniteClusterCulling.cpp，请解释为什么这里要用 HZB 而不是传统视锥剔除" |
| architecture_deep_dive | 架构深潜 | "Lumen Surface Cache 的更新策略是什么？为什么不是每帧全量更新？" |
| performance_optimization | 性能优化 | "World Partition 在大世界场景中的流送策略有哪些可优化点？" |
| debugging_scenario | 调试场景 | "Niagara 粒子在特定距离突然消失，可能是什么原因？" |
| cross_module_integration | 跨模块集成 | "Animation Blueprint 和 Chaos Physics 的交互流程是什么？" |

### 20 个 UE5 核心话题

从 **Nanite GPU-Driven Pipeline**、**Lumen Surface Cache**、**VSM Virtual Shadow Maps**、**Render Graph**、**GPUScene**、**Strata**、**TSR**、**Chaos Physics**、**World Partition**、**PCG**、**MetaHuman**、**Niagara**、**Animation Blueprint**、**UMG Slate**、**Editor Plugin** 到更多细分模块，每个话题都要生成多轮对话。

### 对答案的硬性要求

通过 MCP 获取上下文后，生成的答案必须包含：
- **具体函数名**（如 `UpdateSurfaceCache()`、 `GeneratePageFlagsFromPixels()`）
- **源码路径**（如 `LumenSurfaceCache.cpp`、 `VirtualShadowMapPageManagement.cpp`）
- **数据结构和算法**（如 HZB 的 mipmap 链、Cluster DAG 的构建方式）
- **Trade-off 和局限性**（不是只吹优点，要说清楚什么场景下会炸）

没有这个约束，LLM 就会开始写散文。有了约束，它被迫去查源码、去确认细节。

---

## 六、Phase 2：数据剪枝——为什么"生成多再剪"比"人工写少"更好

我们生成的数据不是每一条都值钱的。Claude 偶尔也会敷衍——给出一个模棱两可的答案，或者把两个概念混为一谈。所以要有 `data_pruner.py` 做四层过滤。

### 四层过滤

```
原始数据（100-500 条/话题）
    │
    ▼ ① 长度过滤（100-2048 tokens）
    │   太短的 = 敷衍；太长的 = 水文
    ▼ ② 事实性过滤（检查源码路径/关键词/具体数字）
    │   函数名拼错？源码路径不存在？直接扔掉
    ▼ ③ 启发式质量评分（0-5 分）
    │   按六个维度打分，只留 top 30%
    ▼ ④ 语义去重（Jaccard similarity threshold = 0.85）
        太相似的只留一条
```

### 启发式评分的六个维度

| 维度 | 权重逻辑 | 说明 |
|------|---------|------|
| 长度 | 适中加分 | 太短 = 没深度，太长 = 啰嗦 |
| 技术深度标记 | 有加分 | 是否提到内部实现细节，不只是概念 |
| 源码路径 | 有加分 | 是否给出具体 .cpp/.h 文件 |
| 代码块 | 有加分 | 是否包含可验证的代码片段 |
| 多轮深度 | 轮数多加分 | 4-5 轮优于 1-2 轮 |
| 具体性 | 数字+函数名加分 | "大约几十张"优于"一些"；"UpdateSurfaceCache()"优于"那个更新函数" |

### 核心策略

**每个话题生成 100-500 条，剪到 top 30%。** 剩下的 30-150 条，质量远高于人工写的 50 条。

为什么？因为人工写 50 条，作者的知识盲区就是数据的盲区。自动生成 500 条再剪枝，等于让 Claude 从多个角度尝试，然后只保留最扎实的那些。它可能错了 400 次，但只要对 100 次，那 100 次的覆盖面就比人工 50 条广得多。

而且 MCP 加持下，"对"的比例其实很高。事实性过滤那一层把 hallucination 拦住了，剩下的主要是质量高低的问题，不是真假问题。

---

## 七、Phase 4：模型选择——为什么是 3B，不是 70B

数据准备好了，该训模型了。`train_small_model.py` 支持三个候选：

| 模型 | 参数量 | 优势 | 劣势 |
|------|--------|------|------|
| **Qwen2.5-Coder-3B** | 3B | 代码理解强，中文支持好，社区活跃 | 纯英文领域知识略逊于 Llama |
| Llama-3.2-3B | 3B | 英文技术文档理解极强 | 中文输出质量不稳定 |
| Phi-4 | 14B | 质量接近 70B 模型 | 需要 QLoRA，训练时间更长 |

**推荐 Qwen2.5-Coder-3B**。原因很实际：UE5 源码是 C++，注释是英文，但面试对话通常是中文。Coder 系列在代码理解上天生有优势，3B 的量级又意味着你可以在 **消费级 GPU（8-16GB VRAM）** 上跑完全流程。

### QLoRA 配置

```python
# 核心训练参数
quantization = "4-bit NF4"      # 显存占用砍到 1/4
lora_r = 32
lora_alpha = 64
num_epochs = 3
learning_rate = 2e-4
batch_size = 4
gradient_accumulation = 4       # 有效 batch = 16
```

这个配置在 RTX 4090（24GB）上跑一个 topic 的数据（约 100 条对话）只要 20-30 分钟。如果是 8GB 的 3060，把 batch 降到 2，也能跑，只是慢一点。

### 为什么不做全量微调？

全量微调 3B 模型需要 12GB+ 显存，而且容易过拟合。QLoRA 只训练 LoRA adapter（几百万参数），冻结原模型权重，既省显存又保持泛化能力。训完之后 adapter 只有几十 MB，部署的时候往原模型上一贴就行。

---

## 八、Phase 5：评估设计——跟最强模型比，不要自欺欺人

训完模型不评估等于白训。`eval_model.py` 的设计原则是：**用最强 LLM 生成的 held-out 数据当 benchmark，三方对比，不给自己留面子。**

### 评估维度

| 维度 | 说明 | 权重 |
|------|------|------|
| 关键词重叠 | 答案中是否包含预期的技术术语（如 "HZB"、"Compute Shader"、"CardCapture"） | 40% |
| 结构质量 | 是否包含源码路径、代码块、结构化分析、trade-off 讨论 | 60% |

### 三方对比

1. **微调后的小模型**（如 Qwen2.5-Coder-3B + LoRA）
2. **原始小模型**（同模型，未微调，作为基线）
3. **最强 LLM**（Claude 3.5 Sonnet / GPT-4，作为天花板）

只有微调后小模型**显著优于原始小模型**，这个项目才算成功。能不能追上最强 LLM 是 bonus，不是必须。

### 真实 benchmark 示例

下面是从 `eval/benchmark_questions.jsonl` 里挑的三道题，附标准答案和评分要点：

**题 1：Nanite 的 GPU-Driven Pipeline 中，Instance Culling 和 Cluster Culling 的执行顺序和各自作用？**

> 标准答案：执行顺序是 **Instance Culling → Cluster Culling**。Instance Culling 是粗粒度剔除，基于视锥和包围盒，在 Compute Shader 中执行；Cluster Culling 是细粒度剔除，基于 HZB（Hierarchical Z-Buffer），也是 Compute Shader。源码：`NaniteClusterCulling.cpp` 和 `NaniteInstanceCulling.cpp`。
>
> 评分要点：必须提到顺序、两种 Culling 的粒度差异、HZB、Compute Shader、两个源码文件。少一个扣 1 分。

**题 2：Lumen 的 Surface Cache 为什么不是每帧全量更新？**

> 标准答案：只更新 `CardCapturesPerFrame` 张 Card（默认几十张），优先更新 dirty Card。全量更新的成本是 O(场景 Card 数量)，大型场景下完全无法接受。源码：`LumenSurfaceCache.cpp` 中的 `UpdateSurfaceCache()`。
>
> 评分要点：必须提到 "不是全量"、"逐帧部分更新"、dirty Card 的优先级、复杂度分析、源码路径和函数名。

**题 3：VSM 的 Page 标记为什么从 Camera 视角而不是 Light 视角？**

> 标准答案：Camera 视角的复杂度是 O(屏幕像素)，精确按需标记；Light 视角的复杂度是 O(光源覆盖范围)，会标记大量 Camera 看不到的浪费区域。源码：`VirtualShadowMapPageManagement.cpp` 中的 `GeneratePageFlagsFromPixels()`。
>
> 评分要点：必须对比两个视角的复杂度、解释为什么 Camera 视角更优、给出源码路径和函数名。只说 "Camera 视角更好" 不得分，必须解释清楚为什么。

**题 4（陷阱题）：面试官说"Nanite 的 GPU-Driven 意味着 CPU 完全不参与渲染"——这个说法有什么问题？**

> 标准答案：CPU 在 **Cook 阶段**大量参与——生成 Cluster、构建 DAG、计算 LOD 误差、打包 Page。GPU-Driven 只指**运行时渲染流程**，不是整个管线。这个说法混淆了 Cook 阶段和 Runtime 阶段。
>
> 评分要点：必须指出 CPU 在 Cook 阶段的具体工作（至少列出两项），明确区分 Cook 和 Runtime。这是典型的"概念偷换"题，考察候选人是否理解完整管线，而不是只会背术语。

---

## 九、结语：这件事到底值不值

三个月跑完这个 pipeline，我的结论是：**值，但有一个前提。**

前提是——**你的目标不是"让 3B 模型变得跟 Claude 一样强"，而是"让 3B 模型在 UE5 这个垂直领域，达到接近 Claude 的面试回答水平"**。

垂直领域是关键。如果你丢给微调后的 3B 模型一个 "React 状态管理" 的问题，它大概率会胡说八道。但在 UE5 渲染、物理、工具链这些话题上，它确实能给出结构完整、源码路径准确、trade-off 清晰的答案。

对我们来说，这解决了一个实际问题：内部技术面试的初筛可以交给模型了。不是替代面试官，而是帮面试官把"明显不懂源码"的候选人提前筛掉，省下的时间用来深入聊真正有料的人。

**下一篇预告：**

我会把 `mcp_data_generator.py` 的完整实现拆开讲——怎么设计 prompt 让 Claude 生成多轮对话、怎么用 MCP 工具调用获取源码上下文、怎么把生成结果批量写入 JSONL。还会贴一个真实的生成日志，看看 Claude 在"查源码 → 写答案 → 被追问 → 再查源码"这个循环里是怎么表现的。

如果你也在做领域特定的模型微调，或者对 MCP 的玩法感兴趣，欢迎在评论区聊聊。你遇到过什么奇葩的幻觉案例？或者有什么更好的评估维度？我都在看。

---

> **项目地址（即将开源）**：UE5 Training MCP Pipeline
> **核心脚本**：`mcp_data_generator.py` → `data_pruner.py` → `data_prep.py` → `train_small_model.py` → `eval_model.py`
> **推荐基座**：Qwen2.5-Coder-3B + QLoRA
