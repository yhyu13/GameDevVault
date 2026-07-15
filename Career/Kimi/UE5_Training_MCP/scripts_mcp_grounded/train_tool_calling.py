#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke-test SFT for tool-calling on a small model.

Target: Qwen/Qwen2.5-0.5B-Instruct (smallest Qwen with tool-call template).
Data: data/splits/corpus_200_tool_calls.jsonl (OpenAI Chat Completions format).
Goal: prove the data works end-to-end. NOT a real production model.

Run:
    python train_tool_calling.py --model Qwen/Qwen2.5-0.5B-Instruct \
        --max_examples 50 --epochs 1
"""

from __future__ import annotations

import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="../data/splits/corpus_200_tool_calls.jsonl")
    p.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    p.add_argument("--output_dir", default="../outputs/qwen-0.5b-ue5-mcp-smoke")
    p.add_argument("--max_examples", type=int, default=50,
                   help="Cap the training set (CPU smoke-test friendly)")
    p.add_argument("--epochs", type=float, default=1.0)
    p.add_argument("--batch_size", type=int, default=1)
    p.add_argument("--grad_accum", type=int, default=4)
    p.add_argument("--lr", type=float, default=2e-5)
    p.add_argument("--max_seq_length", type=int, default=2048)
    args = p.parse_args()

    # 1. Load data, filter to examples with actual tool_calls
    print(f"[1/5] Loading {args.data}", flush=True)
    ds = load_dataset("json", data_files=args.data, split="train")
    print(f"     raw: {len(ds)}", flush=True)
    ds = ds.filter(lambda ex: any("tool_calls" in m for m in ex["messages"]))
    print(f"     with tool_calls: {len(ds)}", flush=True)
    if len(ds) > args.max_examples:
        ds = ds.shuffle(seed=42).select(range(args.max_examples))
        print(f"     capped to: {len(ds)} (smoke-test mode)", flush=True)

    # 2. Tokenizer
    print(f"[2/5] Loading tokenizer: {args.model}", flush=True)
    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    # 3. Model
    print(f"[3/5] Loading model: {args.model}", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.float32,  # CPU only
        device_map="cpu",
        low_cpu_mem_usage=True,
    )
    model.config.use_cache = False
    n_params = sum(p.numel() for p in model.parameters())
    print(f"     params: {n_params / 1e6:.1f}M", flush=True)

    # 4. SFT config
    print(f"[4/5] SFTConfig: epochs={args.epochs}, bs={args.batch_size}, "
          f"grad_accum={args.grad_accum}, lr={args.lr}", flush=True)
    cfg = SFTConfig(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        max_length=args.max_seq_length,
        bf16=False,           # CPU
        fp16=False,           # CPU
        logging_steps=2,
        save_strategy="epoch",
        save_total_limit=1,
        report_to=[],         # no W&B
        warmup_ratio=0.05,
        lr_scheduler_type="cosine",
        seed=42,
        # SFT-specific: tell TRL the messages+tools format
        # (TRL 1.8+ auto-detects chat-format datasets)
        dataset_kwargs={"skip_prepare_dataset": False},
        chat_template_path=None,
    )

    trainer = SFTTrainer(
        model=model,
        args=cfg,
        train_dataset=ds,
        processing_class=tok,
    )

    # 5. Train
    print(f"[5/5] Training on {len(ds)} examples ({args.epochs} epoch)", flush=True)
    print(f"     effective batch: {args.batch_size * args.grad_accum}", flush=True)
    print(f"     steps: {len(ds) // (args.batch_size * args.grad_accum)}", flush=True)
    print(flush=True)
    trainer.train()
    trainer.save_model(args.output_dir)
    tok.save_pretrained(args.output_dir)
    print(f"\n[OK] Model saved to {args.output_dir}", flush=True)


if __name__ == "__main__":
    main()
