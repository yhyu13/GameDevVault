#!/usr/bin/env python3
"""
UE5 Code LLM Fine-Tuning with QLoRA (SFT)
Compatible with: Qwen2.5-Coder, DeepSeek-Coder, CodeLlama

Usage:
    python train_lora.py --model_name Qwen/Qwen2.5-Coder-7B-Instruct \
                         --dataset_path ../data/ue5_sft.jsonl \
                         --output_dir ../outputs/ue5-coder-7b-lora
"""

import argparse
import json
import os
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
    parser = argparse.ArgumentParser(description="Fine-tune UE5 Code LLM with QLoRA")
    parser.add_argument("--model_name", type=str, default="Qwen/Qwen2.5-Coder-7B-Instruct",
                        help="Base model name or path")
    parser.add_argument("--dataset_path", type=str, default="../data/ue5_sft.jsonl",
                        help="Path to Alpaca-format .jsonl dataset")
    parser.add_argument("--output_dir", type=str, default="../outputs/ue5-coder-7b-lora",
                        help="Directory to save LoRA adapter")
    parser.add_argument("--num_epochs", type=int, default=3,
                        help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=4,
                        help="Per-device batch size")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=2,
                        help="Gradient accumulation steps")
    parser.add_argument("--learning_rate", type=float, default=2e-4,
                        help="Learning rate")
    parser.add_argument("--max_seq_length", type=int, default=2048,
                        help="Maximum sequence length")
    parser.add_argument("--lora_r", type=int, default=16,
                        help="LoRA rank")
    parser.add_argument("--lora_alpha", type=int, default=32,
                        help="LoRA alpha scaling")
    parser.add_argument("--lora_dropout", type=float, default=0.05,
                        help="LoRA dropout")
    parser.add_argument("--warmup_ratio", type=float, default=0.03,
                        help="Warmup ratio")
    parser.add_argument("--weight_decay", type=float, default=0.01,
                        help="Weight decay")
    parser.add_argument("--save_steps", type=int, default=50,
                        help="Save checkpoint every N steps")
    parser.add_argument("--logging_steps", type=int, default=10,
                        help="Log every N steps")
    parser.add_argument("--bf16", action="store_true", default=True,
                        help="Use bf16 mixed precision")
    parser.add_argument("--fp16", action="store_true", default=False,
                        help="Use fp16 mixed precision (fallback if no bf16)")
    return parser.parse_args()


def load_alpaca_dataset(path: str) -> Dataset:
    """Load Alpaca-format .jsonl into HuggingFace Dataset."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return Dataset.from_list(records)


def format_alpaca_prompt(example: dict) -> str:
    """Format Alpaca example into chat prompt."""
    instruction = example.get("instruction", "")
    input_text = example.get("input", "")
    output = example.get("output", "")

    if input_text:
        prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n"
    else:
        prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"

    return prompt + output


def format_chat_prompt(example: dict) -> str:
    """Format as Qwen/DeepSeek chat template for better instruction following."""
    instruction = example.get("instruction", "")
    input_text = example.get("input", "")
    output = example.get("output", "")

    if input_text:
        user_msg = f"{instruction}\n\n{input_text}"
    else:
        user_msg = instruction

    return f"<|im_start|>user\n{user_msg}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"


def main():
    args = parse_args()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    print(f"🚀 Loading base model: {args.model_name}")

    # 4-bit quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16 if args.bf16 else torch.float16,
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        padding_side="right",
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Load model with quantization
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16 if args.bf16 else torch.float16,
    )
    model.config.use_cache = False  # Disable KV cache for training

    # Prepare model for k-bit training
    model = prepare_model_for_kbit_training(model)

    # LoRA config
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    print(f"📊 LoRA trainable parameters: {model.print_trainable_parameters()}")

    # Load dataset
    print(f"📂 Loading dataset from {args.dataset_path}")
    dataset = load_alpaca_dataset(args.dataset_path)
    print(f"   Dataset size: {len(dataset)}")

    # Detect model family for prompt formatting
    model_name_lower = args.model_name.lower()
    if "qwen" in model_name_lower or "deepseek" in model_name_lower:
        format_prompt = format_chat_prompt
        print("   Using chat template format")
    else:
        format_prompt = format_alpaca_prompt
        print("   Using Alpaca format")

    def tokenize_function(examples):
        texts = [format_prompt(ex) for ex in examples]
        return tokenizer(
            texts,
            truncation=True,
            max_length=args.max_seq_length,
            padding="max_length",
        )

    # Actually, for SFTTrainer we should use the text format approach
    # Let's use the simpler text-based approach compatible with SFTTrainer
    def formatting_func(example):
        return format_prompt(example)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.num_epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        warmup_ratio=args.warmup_ratio,
        weight_decay=args.weight_decay,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        save_total_limit=3,
        bf16=args.bf16,
        fp16=args.fp16 and not args.bf16,
        optim="paged_adamw_8bit",  # 8-bit AdamW for QLoRA
        report_to="none",
        remove_unused_columns=False,
    )

    # SFT Trainer
    print("🎯 Starting training...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        formatting_func=formatting_func,
        max_seq_length=args.max_seq_length,
        args=training_args,
        data_collator=DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8),
    )

    trainer.train()

    # Save final adapter
    print(f"💾 Saving LoRA adapter to {args.output_dir}")
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    # Save training config
    config_path = Path(args.output_dir) / "training_config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(vars(args), f, indent=2, ensure_ascii=False)

    print(f"\n✅ Training complete! Adapter saved to: {args.output_dir}")
    print(f"   To inference: python inference.py --model_path {args.output_dir} --base_model {args.model_name}")


if __name__ == "__main__":
    main()
