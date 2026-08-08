# 本地基线评估 Runbook（另一台机器）

## 0. 前置

- 仓库：`git clone https://github.com/yhyu13/GameDevVault.git`（最新 master）
- Python ≥ 3.8（纯 stdlib，无 pip 依赖）
- 本地推理服务（三选一）：
  - **ollama（最简单）**：`ollama pull qwen3:0.6b && ollama pull qwen3:1.7b && ollama pull qwen3:4b`，默认端点 `http://localhost:11434/v1`
  - **llama.cpp**：`llama-server -m Qwen3-1.7B-Q4_K_M.gguf --port 8080`，端点 `http://localhost:8080/v1`
  - **vLLM**：`python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen3-0.6B`，端点 `http://localhost:8000/v1`

> 模型名以本地实际为准（ollama 为 `qwen3:0.6b` 这类标签）。runner 缺省自动选名称含 "qwen" 的模型；`--base-url` 可指向任意 OpenAI 兼容端点。

## 1. 环境自检（不调模型）

```bash
cd Career/Kimi/UE5_ExpertSteeer/pilot/stage1
python eval/run_local_eval.py --selftest        # 期望：selftest 9/9 tasks passed
python eval/run_local_eval.py --list-models     # 期望：列出 ≥1 个 qwen 模型
```

## 2. Dry-run sanity（必须先跑，~27 次调用，几分钟）

```bash
python eval/run_local_eval.py --samples 1
```

看输出对照 `eval/success_criteria.md` 的 A 门：
- 任一模型 ≥6/9 任务 NO_CODE → 该模型格式能力不足，先加 few-shot 重测或换模型
- 任一任务三档全过或全挂 → 先记录，不必中断（全量会给更稳的数字），但要在回传时标注

## 3. 全量

```bash
python eval/run_local_eval.py --samples 10      # 3 模型 × 9 任务 × 10 = 270 次，GPU 机器约 15-40 分钟
```

## 4. 结果与回传

产物（`eval/results/`）：
- `results_<ts>.json` — **逐样本**原始数据（model/task/sample/parse_ok/l1/l3/verdict）。这是 SFT/DPO 候选筛选的输入（哪些任务上有 0.6B→4B 可学习差距），**必须提交，不要只提交 summary**
- `summary_<ts>.md` — 模型×任务 pass@1 矩阵（只够看趋势）

回传步骤：
```bash
git add Career/Kimi/UE5_ExpertSteeer/pilot/stage1/eval/results/
git commit -m "docs(ue5-expert): local baseline eval results (provider=<ollama|llama.cpp|vllm>, n=10)"
git push origin master
```

提交信息里注明：推理后端、模型名、GPU 型号（如 RTX 4090）、每样本耗时（summary 里有总耗时）。

## 5. 字段 schema（results_*.json）

```json
{"base": "...", "models": [...], "tasks": [...], "samples": 10, "temperature": 0.6,
 "results": [
   {"model": "qwen3:0.6b", "task": "physics_01_impulse", "sample": 0,
    "parse_ok": true, "l1_ok": true, "l3_ok": false, "l3_failed": 1,
    "verdict": "PASS|L1_FAIL|L3_FAIL|NO_CODE|VERIFIER_ERROR", "error": null}
 ]}
```

判定口径：PASS = L3 全过；L3_FAIL = 过了 L1 但 hidden tests 未全过；L1_FAIL = 签名/禁用模式被拦；
NO_CODE = 输出无法提取代码；VERIFIER_ERROR = 验证器自身异常（重跑该样本）。
