---
tags: [review/三能力对账, review/AI训练, review/UE5, review/工程化, diary/周日]
aliases: []
---

# 三能力对账 —— 是否满足「懂 AI 训练 pipeline + 懂 UE5 垂直领域 + 懂工程化」

> **姊妹篇**：`2026-07-05-过去一周repo修改研究复盘-AI时代对齐.md`（过去一周改了啥）
> **本文档**：改了这些，**在不在 day-job「RAG + Mac Game Harness」的人岗匹配上**
> **基准日**：2026-07-05 ｜ 作者：与 Mavis 对账后整理

---

## TL;DR

| 能力 | 自评满足分 | day-job 尺子下的真实分 | 卡点 |
|------|:--------:|:--------------------:|------|
| 懂 AI 训练 pipeline | 7/10 | 7/10 | 建了工厂没产出产品 |
| 懂 UE5 垂直领域 | 7/10 | **5/10** | VSM 单点 + Mac 零覆盖 |
| 懂工程化 | 8/10 | 8/10 | 缺 CI/CD |
| **加权综合** | **7.3/10** | **6.5/10** | day-job 准备严重不足 |

**满足了吗？「懂」满足，「精通」还远。**

---

## 0. Day-job 真实背景（先校准尺子）

> **重要前提**：day-job = **RAG + Mac Game Harness**，目的 = **让 LLM 能调用 UE 特性**。
> 之前我用 Boris Cherny 的「6 极 sextuple」做能力评估 —— **对你 day-job 不适用**。
> 本文档用 day-job 真实需要的 6 能力极重排：
>
> 1. **UE 渲染特性深度掌握**（Lumen/Nanite/VSM/RDG/TSR/Strata）← **P0**
> 2. **MCP / Agent-engine 接口** ← P0 ← 主线 A 已达标
> 3. **Mac 平台工程能力**（Metal RHI / ARM64 / 性能调优）← **P0** ← 当前 vault 零覆盖
> 4. **RAG 数据工程**（chunk / embedding / retrieval）← P1 ← Training Pipeline 间接覆盖
> 5. **小模型微调**（QLoRA / SFT / 评测）← P1 ← 主线 B 已搭骨架
> 6. **AI 资产生成 / 神经渲染 / 决策 AI** ← P2

下面三项对账的能力是**前三项 P0 能力的拆解**，不是 day-job 全部画像。

---

## 1. 懂 AI 训练 pipeline —— **7/10**

### 做了什么（硬证据）

- ✅ `Career/Kimi/UE5_Training_MCP/` 完整 6 阶段流水线（mcp_data_generator → data_pruner → data_prep → train_small_model → eval_model → export_to_excel）—— README + 8 个 Python 脚本
- ✅ `data/raw/grounding.json` **4113 行真实 MCP 调用 ground truth** —— 不是玩具数据
- ✅ 3 套训练语料生成器：pilot(12) / 50 / 200，对应 verified.jsonl
- ✅ `scripts_mcp_grounded/` 完整 8 个脚本（context_fetcher、data_pruner_v2、self_verifier、format_adapter 等）
- ✅ `UE5_Expert_AI_Training_Complete_Guide.md` 552 行 + 3 篇研究 1332 行（dim01 SFT/RLHF/DPO/RLAIF / dim02 UE5 数据缺口 / dim03 行业实践）
- ✅ `UE5_Training_MCP_Background.md` 283 行对外文章 —— 形成了「叙事」

### 关键差距（为什么只给 7 分）

| 差距 | 影响 |
|------|------|
| ❌ **没有训出可用模型** | pipeline 跑通 ≠ 训出来。`outputs/models/` 没有 checkpoint 证据 |
| ❌ **没有跑过 held-out eval** | `eval/benchmark_questions.jsonl` 写了吗？得分多少？没数字 |
| ❌ **数据量在 pilot 级别** | 200 条 vs 行业 1 万 / 10 万量级，差 50-500 倍 |
| ❌ **没有 RAG 索引格式输出** | day-job 是 RAG，但 pipeline 输出是 JSONL for SFT，没看到 chunked MD for embedding |

> **一句话**：**建了工厂（pipeline）但还没生产出产品（训出的模型）**。这是「满足 ≠ 精通」的最大鸿沟。

---

## 2. 懂 UE5 垂直领域 —— **7/10（自评）/ 5/10（day-job 尺子）**

### 做了什么（硬证据）

- ✅ `Routine/02-引擎源码分析库/` 一周 9+ 篇源码分析：Cook / Jolt / Sky / Cloud / SkyPass / Lumen / Nanite
- ✅ `Routine/03-Shader与特效案例集/` 5 篇大案例：SSR / Lumen GI diffuse / Lumen Reflection / Nanite material / UE5.8 Sky
- ✅ `Routine/01-论文笔记库/Lumen/` 3 篇 Lumen 深度笔记（含 SIGGRAPH 2021）
- ✅ `Career/Kimi/UE5_Extending_MCP/patches/phase3_capture_viewport/` **真写过 UE5 编辑器代码**（ModelContextProtocolViewportTool.cpp/.h 自己实现）
- ✅ `grounding.json` 4113 行 = 真实调过 UE5 API（不是文档拼凑）

### 关键差距（为什么 day-job 尺子只有 5 分）

| 差距 | 影响 |
|------|------|
| ⚠️ **VSM 单点故障** | 只有 1 篇「页溢出」性能瓶颈，**没有页表 / Cache / Nanite-VSM 集成完整笔记** ← day-job 必考 |
| ⚠️ **Nanite 缺源码分析** | 只有 shader + 性能，源码层空白 |
| ⚠️ **Mac 平台零笔记** | day-job 在 Mac，**vault 里 Mac 相关 = 0** ← 最大缺位 |
| ⚠️ **大量笔记停在「读」层** | MCP patch 改的是 plugin（用户侧），不是改 Lumen/Nanite/VSM 引擎代码本身 |
| ⚠️ **UE5 版本演进没系统梳理** | 5.6/5.7/5.8 的差异没横向对比 |
| ⚠️ **没在 Mac 上跑过 UE5 项目** | 不会知道 Metal RHI vs DX12 的真实差异 |

> **一句话**：**有广度没深度，有读没改**。「懂」需要至少改过一个引擎 CVAR 或修过一个引擎 bug，光读源码 + 写 plugin 不够。

### Day-job 尺子下的额外扣分

- Lumen: ✅ 厚（3 论文 + 2 shader + 2 性能，覆盖度高）
- Nanite: ⚠️ 中（1 shader + 2 性能，缺源码分析）
- **VSM: ⚠️ 薄**（只有 1 篇「页溢出」性能瓶颈，**没有完整技术笔记**）← 当前最大缺位
- **Mac: ❌ 零**（Mac Game Harness 没有任何 vault 笔记）← 另一个缺位

---

## 3. 懂工程化 —— **8/10**

### 做了什么（硬证据）

- ✅ smoke test **7 轮迭代** + inspect_run×4 + dump_smoke_summary.py = 完整测试基础设施
- ✅ HTTP + stdio 两种 transport 都覆盖测试
- ✅ **MutationGate 设计**（`ENABLE_MCP_MUTATIONS=1` 环境变量开关）= 2026 年 LLM-tool 防御性编程的前沿
- ✅ JSON result 标准化（`MakeTextResult` 包装）= 协议一致性
- ✅ Class lookup 三级 fallback（FindFirstObject → `_C` 后缀 → TObjectIterator）= 鲁棒性
- ✅ Game thread deadlock 修复（`IFileManager::Copy` 替代 `LoadPackage`）= 死锁预防
- ✅ **`gen_p0_cards.py` 1524 行** —— 把「内容生产」工具化，每张卡 9-10 题覆盖核心+边界+误区
- ✅ 9 个 phase patch 都配 README.md = 文档与代码同步

### 关键差距（为什么只给 8 分）

| 差距 | 影响 |
|------|------|
| ⚠️ **没有 CI/CD** | 没有 GitHub Actions、没有 pre-commit hook、没有 nightly build |
| ⚠️ **单元测试覆盖率没数字** | smoke test 是集成测试，不是单元测试；如果覆盖率 0%，那是 demo 不是工程 |
| ⚠️ **smoke test JSON 进了 git** | 应该 .gitignore + 只留 .md 总结 |
| ⚠️ **代码组织有点散** | patches/phase1...phase9 + scripts_mcp_grounded + data/raw，跨目录心智负担 |
| ⚠️ **错误处理主要是「重启编辑器」** | 没有 graceful degradation / retry / fallback |

> **一句话**：**有工具化意识，没达到工业级**。差的就是 CI + 单测覆盖率 + 错误处理策略。

---

## 4. 综合判断

| 维度 | 自评满足分 | day-job 尺子 | 主要差距 |
|------|:----------:|:-----------:|---------|
| AI 训练 pipeline | 7/10 | 7/10 | 没训出模型 |
| UE5 垂直领域 | 7/10 | **5/10** | VSM/Mac 零覆盖 |
| 工程化 | 8/10 | 8/10 | 缺 CI/CD |
| **加权综合** | **7.3/10** | **6.5/10** | 反思 + day-job 准备断档 |

### 满足 vs 精通

| 层级 | 当前 | 距离 |
|------|------|------|
| **「懂」（拿得出手）** | ✅ 满足 | 三项都能讲清道道、拿出硬证据、形成对外叙事 |
| **「精通」（能上生产）** | ❌ 远 | 三个能力卡在不同瓶颈 |

每个能力的瓶颈不一样：

- **AI 训练 pipeline** 卡在「训出来」—— 没有产物证明 pipeline 真的 work
- **UE5 垂直领域** 卡在「改引擎」—— 没碰过 Lumen/Nanite/VSM 的引擎源码
- **工程化** 卡在「自动化」—— 没 CI/CD

---

## 5. 从满足到精通，3 件事要做

### 5.1 本周（W28 内）—— 让 pipeline 跑出真模型

- [ ] 用 pilot 12 条数据训 Qwen-3B（哪怕效果差）
- [ ] 截 loss 曲线 + eval 分数留证
- [ ] 写一篇「第一次端到端训练纪实」（失败也写，比不训强 100 倍）

### 5.2 下周（W29）—— 改一次 UE5 引擎源码

- [ ] 找一个 Lumen CVAR 或 VSM 参数
- [ ] **改引擎源码 + 验证 + 写笔记**
- [ ] 哪怕只是改个默认值 + 跑测试
- [ ] 这是「读 vs 改」的鸿沟，跳过去

### 5.3 本周末（W28 末）—— 给 UE5_Extending_MCP 加 CI

- [ ] 一个 GitHub Actions 跑 smoke test shell 脚本
- [ ] PR 触发，main 分支保护
- [ ] 这是工业级的入场券

### 5.4 Q3 重点补位（与 day-job 真实对齐）

- [ ] **VSM 完整技术笔记** —— 页表 / Cache / Nanite 集成 / 移动端降级，目标 ≥ 600 行
- [ ] **Nanite 源码分析** —— Mesh Pass / Cluster DAG / Page Streaming
- [ ] **Mac 平台 vault 子目录** + 索引页（Metal RHI / UE5.4+ Mac 支持差异 / 已知 bug / 性能基线）
- [ ] **Routine 笔记新硬约束**：每篇末尾加 `LLM 检索锚点` 段落（关键术语 / API 名 / 源码路径 / 5-10 个高频问题 / 跨笔记链接）
- [ ] **雷达 README 紧急补丁**：P0 增加 `Lumen（GI / 反射 / 反射降级）/ Nanite（材质管线 / 虚拟几何 shader）/ VSM（页表 / Cache）`，并标注「day-job 必考」

---

## 6. 关联 / 输出产物

### 姊妹篇

- [[2026-07-05-过去一周repo修改研究复盘-AI时代对齐]] —— 过去一周改了啥

### 引用主线

- [[Routine/02-引擎源码分析库/00-目录]] —— 源码分析索引
- [[Routine/03-Shader与特效案例集/00-目录]] —— Shader 案例索引
- [[Routine/05-技术雷达/00-README]] —— 技术雷达（**待补 Lumen/Nanite/VSM P0 项**）
- [[Routine/04-性能优化备忘录/00-目录]] —— 性能优化索引
- [[Career/Kimi/UE5_Training_MCP/00-README]] —— Training Pipeline 索引
- [[Career/Kimi/UE5_Extending_MCP/00-README]] —— UE5 MCP 真实工程索引

### 待补缺位

- **VSM 完整技术笔记**（最大缺位）
- **Mac 平台 vault 索引页**（零覆盖）
- **雷达 README P0 补丁**（待执行）

### Day-job 真相复盘链

- `User Profile / Day-job truth — Routine vault serves LLM-driven UE on Mac (2026-07-05)`