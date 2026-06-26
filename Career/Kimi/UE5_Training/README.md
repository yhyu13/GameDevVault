# UE5 Code LLM Fine-Tuning with QLoRA

使用 **Qwen2.5-Coder-7B-Instruct** + **QLoRA** 在本地 UE5 技术数据集上微调。

## 环境要求

```bash
# 需要 CUDA 12.1+，推荐显存 16GB+
pip install torch transformers peft accelerate bitsandbytes trl datasets

# 如果 bitsandbytes 在 Windows 上编译失败，尝试预编译 wheel:
pip install https://github.com/jllllll/bitsandbytes-windows-webui/releases/download/wheels/bitsandbytes-0.41.1-py3-none-win_amd64.whl
```

## 硬件要求

| 配置 | 模型 | 量化 | 显存 |
|------|------|------|------|
| 最低 | Qwen2.5-Coder-7B | 4-bit | ~10GB |
| 推荐 | Qwen2.5-Coder-7B | 4-bit | 16GB+ |
| 高配 | Qwen2.5-Coder-14B | 4-bit | 24GB+ |

## 快速开始

```bash
cd UE5_Training/scripts
python train_lora.py \
  --model_name Qwen/Qwen2.5-Coder-7B-Instruct \
  --dataset_path ../data/ue5_sft.jsonl \
  --output_dir ../outputs/ue5-coder-7b-lora \
  --num_epochs 3 \
  --batch_size 4 \
  --learning_rate 2e-4 \
  --lora_r 16 \
  --lora_alpha 32
```

## 训练后推理

```bash
python inference.py \
  --model_path ../outputs/ue5-coder-7b-lora \
  --base_model Qwen/Qwen2.5-Coder-7B-Instruct \
  --question "Nanite 的 Cluster Culling 和 Instance Culling 有什么区别？"
```

## 评估

```bash
python evaluate.py \
  --model_path ../outputs/ue5-coder-7b-lora \
  --base_model Qwen/Qwen2.5-Coder-7B-Instruct \
  --benchmark ../benchmark/ue5_eval.jsonl
```

---

## 关键参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `lora_r` | 16 | LoRA 低秩维度，越大表达能力越强 |
| `lora_alpha` | 32 | 缩放因子，通常 = 2*r |
| `learning_rate` | 2e-4 | 学习率，QLoRA 建议 1e-4 ~ 2e-4 |
| `num_epochs` | 3 | 训练轮数，小数据集 3-5 轮即可 |
| `max_seq_length` | 2048 | 最大序列长度 |
| `target_modules` | q_proj,k_proj,v_proj,o_proj | 训练的目标线性层 |

## 数据集格式

训练脚本期望 Alpaca 格式 `.jsonl`：
```json
{"instruction": "...", "input": "", "output": "..."}
```

已在 `../data/ue5_sft.jsonl` 中生成（118 条记录）。

## 输出结构

```
outputs/ue5-coder-7b-lora/
├── adapter_config.json      # LoRA 配置
├── adapter_model.safetensors # LoRA 权重
├── checkpoint-*/           # 训练中间 checkpoint
└── training_log.json        # 训练日志
```

## 合并为单模型（可选）

推理时可以直接加载 adapter + base model，也可以合并为单一模型：

```python
from peft import AutoPeftModelForCausalLM

model = AutoPeftModelForCausalLM.from_pretrained(
    "../outputs/ue5-coder-7b-lora",
    device_map="auto"
)
model = model.merge_and_unload()  # 合并 LoRA 到基座
model.save_pretrained("../outputs/ue5-coder-7b-merged")
```