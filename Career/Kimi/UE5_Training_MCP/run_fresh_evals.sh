#!/bin/bash
# Run the fresh 15-question test set against all 6 Qwen variants.
# Sequential (one GPU) — total wall ~18 min. Outputs go to outputs/results/eval_fresh_*.
set -u
cd /home/hangyu5/Documents/Gitrepo-My/GameDevVault/Career/Kimi/UE5_Training_MCP
source outputs/venv/bin/activate
export CUDA_VISIBLE_DEVICES=1
export TRANSFORMERS_VERBOSITY=error
export TOKENIZERS_PARALLELISM=false

LOG_DIR=outputs/logs
mkdir -p "$LOG_DIR"
RES_DIR=outputs/results
INPUT=data/splits/fresh_test.jsonl

declare -a CMDS=(
  "0.8B|BASE|/media/home/hangyu5/Documents/Hugging-Face/Qwen/Qwen3.5-0.8B|"
  "0.8B|FT|/media/home/hangyu5/Documents/Hugging-Face/Qwen/Qwen3.5-0.8B|outputs/models/qwen3.5-0.8b-ue5-lora"
  "2B|BASE|/media/home/hangyu5/Documents/Hugging-Face/Qwen/Qwen3.5-2B|"
  "2B|FT|/media/home/hangyu5/Documents/Hugging-Face/Qwen/Qwen3.5-2B|outputs/models/qwen3.5-2b-ue5-lora"
  "4B|BASE|/media/home/hangyu5/Documents/Hugging-Face/Qwen/Qwen3.5-4B|"
  "4B|FT|/media/home/hangyu5/Documents/Hugging-Face/Qwen/Qwen3.5-4B|outputs/models/qwen3.5-4b-ue5-lora"
)

for entry in "${CMDS[@]}"; do
  IFS='|' read -r SIZE ADAPTER MODEL ADAPTER_DIR <<< "$entry"
  OUT="$RES_DIR/eval_fresh_${SIZE}_${ADAPTER}.json"
  LOG="$LOG_DIR/eval_fresh_${SIZE}_${ADAPTER}.log"
  echo "================================================================"
  echo "[$(date +%H:%M:%S)] starting $SIZE $ADAPTER → $OUT"
  echo "================================================================"
  if [ -n "$ADAPTER_DIR" ]; then
    python scripts/eval_qwen35.py \
      --model_path "$MODEL" \
      --adapter_dir "$ADAPTER_DIR" \
      --input_file "$INPUT" \
      --output "$OUT" \
      2>&1 | tee "$LOG"
  else
    python scripts/eval_qwen35.py \
      --model_path "$MODEL" \
      --input_file "$INPUT" \
      --output "$OUT" \
      2>&1 | tee "$LOG"
  fi
done
echo "[$(date +%H:%M:%S)] all 6 evals complete"
