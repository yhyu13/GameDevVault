#!/usr/bin/env python3
"""
UE5 Small Model Trainer

Fine-tune small models (1.5B-7B) with QLoRA on UE5 data.
Targets consumer GPUs with 8-16GB VRAM.

Usage:
    # Qwen2.5-Coder-3B (recommended starting point)
    python train_small_model.py \
        --model_name Qwen/Qwen2.5-Coder-3B-Instruct \
        --dataset ../data/splits/train.jsonl \
        --eval_dataset ../data/splits/val.jsonl \
        --output_dir ../outputs/models/qwen-3b-ue5-lora

    # Llama-3.2-3B
    python train_small_model.py \
        --model_name meta-llama/Llama-3.2-3B-Instruct \
        --dataset ../data/splits/train.jsonl \
        --eval_dataset ../data/splits/val.jsonl \
        --output_dir ../outputs/models/llama-3b-ue5-lora

    # Phi-4 (14B, use QLoRA with lower batch)
    python train_small_model.py \
        --model_name microsoft/phi-4 \
        --dataset ../data/splits/train.jsonl \
        --eval_dataset ../data/splits/val.jsonl \
        --output_dir ../outputs/models/phi-4-ue5-lora \
        --batch_size 1 \
        --gradient_accumulation_steps 8
"""

import argparse
import json
import yaml
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    DataCollatorForSeq2Seq,
)
from trl import SFTTrainer


def parse_args():
    parser = argparse.ArgumentParser(description="Train small UE5 Code LLM")
    parser.add_argument("--model_name", type=str, required=True,
                        help="Base model (e.g., Qwen/Qwen2.5-Coder-3B-Instruct)")
    parser.add_argument("--dataset", type=str, required=True,
                        help="Training dataset JSONL")
    parser.add_argument("--eval_dataset", type=str, default=None,
                        help="Validation dataset JSONL")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Output directory")
    parser.add_argument("--config", type=str, default="../config/training_config.yaml",
                        help="Training config YAML")
    parser.add_argument("--batch_size", type=int, default=None,
                        help="Override batch size")
    parser.add_argument("--num_epochs", type=int, default=None,
                        help="Override num epochs")
    parser.add_argument("--learning_rate", type=float, default=None,
                        help="Override learning rate")
    parser.add_argument("--lora_r", type=int, default=None,
                        help="Override LoRA rank")
    return parser.parse_args()


def load_dataset(path: str) -> Dataset:
    """Load JSONL dataset."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return Dataset.from_list(records)


def format_prompt(record: dict, model_name: str) -> str:
    """Format record based on model family."""
    model_lower = model_name.lower()

    instruction = record.get("instruction", "")
    input_text = record.get("input", "")
    output = record.get("output", "")

    if input_text:
        user_msg = f"{instruction}\n\n{input_text}"
    else:
        user_msg = instruction

    # Qwen / DeepSeek chat template
    if "qwen" in model_lower or "deepseek" in model_lower:
        return f"<|im_start|>user\n{user_msg}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"

    # Llama chat template
    elif "llama" in model_lower:
        return f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_msg}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n{output}<|eot_id|>"

    # Phi-4
    elif "phi" in model_lower:
        return f"<|im_start|>user\n{user_msg}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"

    # Fallback: Alpaca
    else:
        return f"### Instruction:\n{user_msg}\n\n### Response:\n{output}"


def main():
    args = parse_args()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Load config
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Override config with CLI args
    if args.batch_size is not None:
        config["training"]["per_device_train_batch_size"] = args.batch_size
    if args.num_epochs is not None:
        config["training"]["num_train_epochs"] = args.num_epochs
    if args.learning_rate is not None:
        config["training"]["learning_rate"] = args.learning_rate
    if args.lora_r is not None:
        config["lora"]["r"] = args.lora_r

    print(f"🚀 Training: {args.model_name}")
    print(f"   Output: {args.output_dir}")
    print(f"   Epochs: {config['training']['num_train_epochs']}")
    print(f"   Batch: {config['training']['per_device_train_batch_size']}")
    print(f"   LR: {config['training']['learning_rate']}")
    print(f"   LoRA r: {config['lora']['r']}")

    # Tokenizer
    print("\n📦 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        padding_side="right",
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Quantization
    print("🔧 Loading model with 4-bit quantization...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=config["quantization"]["load_in_4bit"],
        bnb_4bit_use_double_quant=config["quantization"]["bnb_4bit_use_double_quant"],
        bnb_4bit_quant_type=config["quantization"]["bnb_4bit_quant_type"],
        bnb_4bit_compute_dtype=getattr(torch, config["quantization"]["bnb_4bit_compute_dtype"]),
    )

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=getattr(torch, config["quantization"]["bnb_4bit_compute_dtype"]),
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model)

    # LoRA
    print("🎯 Applying LoRA...")
    lora_config = LoraConfig(
        r=config["lora"]["r"],
        lora_alpha=config["lora"]["lora_alpha"],
        target_modules=config["lora"]["target_modules"],
        lora_dropout=config["lora"]["lora_dropout"],
        bias=config["lora"]["bias"],
        task_type=config["lora"]["task_type"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Datasets
    print("\n📂 Loading datasets...")
    train_dataset = load_dataset(args.dataset)
    print(f"   Train: {len(train_dataset)} examples")

    eval_dataset = None
    if args.eval_dataset:
        eval_dataset = load_dataset(args.eval_dataset)
        print(f"   Val:   {len(eval_dataset)} examples")

    # Formatting function
    def formatting_func(examples):
        if isinstance(examples, list):
            return [format_prompt(ex, args.model_name) for ex in examples]
        return format_prompt(examples, args.model_name)

    # Training args
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        **config["training"],
        bf16=config.get("bf16", False),
        fp16=config.get("fp16", False),
    )

    # Trainer
    print("\n🔥 Starting training...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        formatting_func=formatting_func,
        max_seq_length=config["max_seq_length"],
        args=training_args,
        data_collator=DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8),
    )

    trainer.train()

    # Save
    print(f"\n💾 Saving adapter to {args.output_dir}")
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    # Save config
    with open(Path(args.output_dir) / "training_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Training complete!")
    print(f"   Adapter: {args.output_dir}")
    print(f"   To evaluate: python eval_model.py --model_path {args.output_dir} --base_model {args.model_name}")


if __name__ == "__main__":
    main()
