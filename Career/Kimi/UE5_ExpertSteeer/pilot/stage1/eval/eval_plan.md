# 本地基线评估计划（Qwen 小模型 × 9 任务）

## 目标

用**本地推理**（ollama / llama.cpp / vLLM，OpenAI 兼容端点）跑 Qwen 小模型（0.6B/1.7B/4B 档）解 pilot 的 9 个任务，回答三个问题：

1. **任务有没有区分度**：9 个任务对小模型的 pass@1 是否拉开梯度（有的 <30%、有的 >60%）？全过=任务太简单，全挂=任务不可学或 prompt 有问题
2. **模型尺寸梯度**：pass@1 是否随模型增大单调上升（≥6/9 任务）？无梯度=任务测的不是"能力"
3. **训练空间**：基线 pass@1 落在哪个区间，决定 SFT 数据形态是否需要调整

> 注：计划中的 "Qwen 0.8B/2B" 无对应型号，映射到 **Qwen3 0.6B / 1.7B / 4B**（或 Qwen2.5 0.5B / 1.5B），以本地实际加载的模型为准。

## 协议

- **Zero-shot 单轮**：system 提示（"你是 UE5 工程师，只输出完整 Python 代码，不解释"）+ 任务 prompt（与训练数据完全一致）
- **每 (模型, 任务) 采样 10 次**（temperature 0.6, top_p 0.9, max_tokens 2048），独立样本
- **提取**：解析代码块；无代码块则从首个 `def` 截取；无 `def` → `NO_CODE`（计为失败，单独统计——小模型答非所问本身就是信号）
- **验证**：复用 pilot 分层验证器（L1 门禁 + L3 hidden tests，与训练流水线同一套），避免"换评测器"
- **指标**：`pass@1`（主指标）、`parse_fail_rate`、`l1_only_pass`
- **成本**：本地推理，无 API 费用；GPU 机器 270 次调用约 15-40 分钟

## 执行顺序（gate 式，防浪费）

1. **环境自检**：`--selftest`（9/9 PASS）+ `--list-models`（有 qwen）
2. **Dry-run**：`--samples 1`（27 次，几分钟）→ 对照 success_criteria.md A 门，过不了先修
3. **全量**：`--samples 10`（270 次）→ 对照 success_criteria.md B 表判定

## 运行方法（另一台机器）

详见 `eval/README.md`（runbook：推理后端安装、模型拉取、回传步骤、结果 schema）。

## 产物

- `eval/results/results_<时间戳>.json` — **逐样本**原始数据（SFT/DPO 候选筛选的输入，必须提交）
- `eval/results/summary_<时间戳>.md` — 模型×任务 pass@1 矩阵（趋势）
- 判定对照 `eval/success_criteria.md`（区分度/梯度/全过全挂/NO_CODE 决策表）
