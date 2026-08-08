# API 基线评估计划（Qwen 小模型 × 9 任务）

## 目标

在无本地模型/GPU 的情况下，用 API 跑目标小模型（Qwen 家族 0.6B/1.7B/4B 档）解 pilot 的 9 个任务，
回答三个问题：

1. **任务有没有区分度**：9 个任务对小模型的 pass@1 是否拉开梯度（有的 <30%、有的 >60%）？全过=任务太简单，全挂=任务不可学或 prompt 有问题
2. **模型尺寸梯度**：pass@1 是否随模型增大单调上升（≥6/9 任务）？无梯度=任务测的不是"能力"
3. **训练空间**：基线 pass@1 落在哪个区间，决定 SFT 数据形态是否需要调整

> 注：JD/计划中的 "Qwen 0.8B/2B" 无对应型号，映射到 **Qwen3 0.6B / 1.7B / 4B**（或 Qwen2.5 0.5B / 1.5B，`--models` 可覆盖）。

## 协议

- **Zero-shot 单轮**：system 提示（"你是 UE5 工程师，只输出完整 Python 代码，不解释"）+ 任务 prompt（与训练数据完全一致）
- **每 (模型, 任务) 采样 10 次**（temperature 0.6, top_p 0.9, max_tokens 2048），独立样本
- **提取**：解析代码块（```python）；无代码块则从首个 `def` 截取；无 `def` → `NO_CODE`（计为失败，单独统计——小模型答非所问本身就是信号）
- **验证**：复用 pilot 分层验证器（L1 门禁 + L3 hidden tests，与训练流水线同一套），避免"换评测器"
- **指标**：
  - `pass@1` = L3 全过样本 / 总样本（主指标）
  - `parse_fail_rate` = 提取失败占比（模型"不会写代码"的量化）
  - `l1_only_pass` = 过了 L1 但 L3 失败（写对了形、没写对行为）
- **费用预算**：每样本 ≈ 1.4K token；9 任务 × 3 模型 × 10 次 ≈ 270 样本 ≈ 40 万 token；SiliconFlow/DashScope 小模型 API 单价极低，**预计 < ¥10**。`--samples` 可降（最低 3）

## 成功标准（决定后续动作）

| 观察 | 判定 | 动作 |
|---|---|---|
| ≥4/9 任务 pass@1 落在 5%-60% 之间 | 任务有区分度 | 数据形态可用，进扩量 |
| ≥6/9 任务 pass@1 随尺寸单调上升 | 测的是能力梯度 | 按 0.6B 基线设计 SFT |
| 某任务三档模型全过（≥80%） | 太简单 | 该任务升级/降级难度，换更硬变体 |
| 某任务三档全挂（≤5%） | 不可学或 prompt 问题 | 检查 prompt 与任务，或弃用 |
| parse_fail_rate > 50% | 小模型不会代码输出格式 | 加 few-shot 格式示范后再测 |

## 运行方法（另一台机器）

```bash
git clone https://github.com/yhyu13/GameDevVault.git
cd GameDevVault/Career/Kimi/UE5_ExpertSteeer/pilot/stage1

# 自检：本机环境 + 验证器链路正常（golden 应全 PASS）
python eval/run_api_baseline.py --selftest

# SiliconFlow（模型 Qwen/Qwen3-0.6B 等）
set SILICONFLOW_API_KEY=sk-xxx
python eval/run_api_baseline.py --provider siliconflow --samples 10

# DashScope（模型 qwen3-0.6b 等）
set DASHSCOPE_API_KEY=sk-xxx
python eval/run_api_baseline.py --provider dashscope --samples 10
```

无第三方依赖（纯 stdlib urllib），Python ≥ 3.8。

## 产物

- `eval/results/results_<时间戳>.json` — 全量原始数据（每样本逐层结果）
- `eval/results/summary_<时间戳>.md` — 模型×任务 pass@1 矩阵 + 区分度/梯度判定 + 建议

把结果目录拷回本仓库（或提交回远程），下一步据此做数据形态决策。
