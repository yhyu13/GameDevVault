# 本地基线评估 Runbook（Qwen3.5 小模型，direct HF load）

## 0. 前置

- 仓库：`git clone https://github.com/yhyu13/GameDevVault.git`（最新 master）
- Python ≥ 3.11
- GPU：≥16GB 显存（4B bf16 ≈ 8GB，余给 KV cache）
- **项目本地 venv**（`stage1/.venv`，已 `--system-site-packages` 复用 base 的 torch）：

  ```bash
  cd Career/Kimi/UE5_ExpertSteeer/pilot/stage1
  python3 -m venv --system-site-packages .venv
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install --pre "transformers>=5" "accelerate>=1" "huggingface_hub>=1" "tokenizers>=0.21"
  .venv/bin/pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cu121
  ```

  > `--pre` 必须：Qwen3.5 架构（`qwen3_5` + 混合 linear+full attention）在 transformers 5.x stable 之前发布。已验证 `transformers==5.14.1` + `torch==2.5.1+cu121` 可加载 `Qwen3.5-0.8B` 并产出代码。

- 本地模型路径：默认 `/media/home/hangyu5/Documents/Hugging-Face/Qwen/Qwen3.5-{0.8B,2B,4B}`（safetensors 全套含 `chat_template.jinja`）。可通过环境变量覆盖：

  ```bash
  export QWEN_HF_DIR=/your/qwen/dir
  ```

> 已知性能警告：未装 `flash-linear-attention` (fla) + `causal-conv1d` 时，Qwen3.5 的 linear attention 层走 torch fallback（慢 2-3x），正确性不受影响。后续若全量太慢再补：
> ```
> .venv/bin/pip install fla causal-conv1d
> ```

## 1. 环境自检（不加载模型）

```bash
cd Career/Kimi/UE5_ExpertSteeer/pilot/stage1
.venv/bin/python eval/run_local_eval.py --selftest        # 期望：selftest 9/9 tasks passed
```

只跑 verifier 在 POOL 候选代码上的 sanity check，不加载模型，约 10 秒。

## 2. Dry-run sanity（必须先跑，几分钟）

```bash
.venv/bin/python eval/run_local_eval.py --samples 1 --sizes 0.8B
# 期望：1 档 × 9 任务 × 1 样本 = 9 次生成
```

加载模型约 5-10 秒/档，单次生成（max 2048 tokens）约 10-30 秒。9 次约 3-5 分钟。

看输出对照 `eval/success_criteria.md` 的 A 门：
- 任一任务 9/9 NO_CODE → 该任务 prompt 需要重写或加 few-shot
- 任一档模型 9/9 L1_FAIL → 检查 SYSTEM 提示或模型 dtype

## 3. 全量

```bash
.venv/bin/python eval/run_local_eval.py --samples 10      # 3 档 × 9 任务 × 10 = 270 次生成
```

预计耗时（RTX 3090，bf16，无 fla 加速）：
- 0.8B：约 30-50 分钟
- 2B：约 50-90 分钟
- 4B：约 90-180 分钟

合计 ~3-5 小时。建议后台跑（`nohup ... &`）并把日志和结果都存进 `eval/results/`。

按档分段跑也行（避免单次跑太长中断）：
```bash
.venv/bin/python eval/run_local_eval.py --sizes 0.8B --samples 10   # 单独跑 0.8B
.venv/bin/python eval/run_local_eval.py --sizes 2B --samples 10     # 单独跑 2B
.venv/bin/python eval/run_local_eval.py --sizes 4B --samples 10     # 单独跑 4B
```

## 4. 结果与回传

产物（`eval/results/`）：
- `results_<ts>.json` — **逐样本**原始数据（`model/task/sample/parse_ok/l1/l3/verdict`）。这是 SFT/DPO 候选筛选的输入（哪些任务上有 0.8B→4B 可学习差距），**必须提交，不要只提交 summary**
- `summary_<ts>.md` — 模型×任务 pass@1 矩阵（只够看趋势）

回传步骤：
```bash
git add Career/Kimi/UE5_ExpertSteeer/pilot/stage1/eval/results/
git commit -m "docs(ue5-expert): local baseline eval results (Qwen3.5 direct HF, bf16, n=10)"
git push origin master
```

提交信息里注明：模型（`qwen3.5:0.8B/2B/4B`）、dtype、GPU 型号（RTX 3090）、summary 里有总耗时。

## 5. 字段 schema（results_*.json）

```json
{"base": "local", "models": ["qwen3.5:0.8B", "qwen3.5:2B", "qwen3.5:4B"],
 "tasks": [...], "samples": 10, "temperature": 0.6, "dtype": "bf16",
 "results": [
   {"model": "qwen3.5:0.8B", "task": "physics_01_impulse", "sample": 0,
    "parse_ok": true, "l1_ok": true, "l3_ok": false, "l3_failed": 1,
    "verdict": "PASS|L1_FAIL|L3_FAIL|NO_CODE|VERIFIER_ERROR", "error": null}
 ]}
```

判定口径：PASS = L3 全过；L3_FAIL = 过了 L1 但 hidden tests 未全过；L1_FAIL = 签名/禁用模式被拦；
NO_CODE = 输出无法提取代码；VERIFIER_ERROR = 验证器自身异常（重跑该样本）。

## 6. SFT/DPO 训练后再评估

`run_local_eval.py` 设计上同时支持基线和训练后评估。指向训练产物 checkpoint：

```bash
.venv/bin/python eval/run_local_eval.py \
  --model-path /path/to/sft-v1/checkpoint \
  --label qwen3.5:0.8B-sft-v1 \
  --samples 10
```

`--label` 决定 results/summary 里的 `model` 字段（区分基线和训练后）。可多次跑（不同 `--label`）后用 `jq` 或 pandas 在 `results_*.json` 上做对比。