#!/usr/bin/env python3
"""
Qwen3.5-0.8B LoRA SFT on UE5 MCP data.

Tailored for Qwen3.5 hybrid-attention model loaded as text-only
(`Qwen3_5ForCausalLM`). Uses bf16 LoRA (no 4-bit), single GPU,
and the tokenizer's `apply_chat_template` so train/eval prompts
are guaranteed to match token-for-token.

Usage:
    python train_qwen35.py \
        --model_path /media/home/hangyu5/Documents/Hugging-Face/Qwen/Qwen3.5-0.8B \
        --train_file data/splits/train.jsonl \
        --val_file data/splits/val.jsonl \
        --output_dir outputs/models/qwen3.5-0.8b-ue5-lora
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ---------- prompt formatting using the model's own chat template ----------


def build_train_text(record: dict, tok) -> str:
    """Convert an alpaca record into a single chat-template string with both
    user and assistant turns. The model is trained to generate the assistant
    turn and the trailing <|im_end|>."""
    instr = record.get("instruction", "").strip()
    inp = record.get("input", "").strip()
    out = record.get("output", "").strip()
    user_msg = f"{instr}\n\n{inp}" if inp else instr
    msgs = [
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": out},
    ]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)


def build_eval_prompt(record: dict, tok) -> str:
    """The exact eval-time prompt: user message + assistant header."""
    instr = record.get("instruction", "").strip()
    inp = record.get("input", "").strip()
    user_msg = f"{instr}\n\n{inp}" if inp else instr
    msgs = [{"role": "user", "content": user_msg}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--model_path", required=True, help="Local model dir")
    p.add_argument("--train_file", required=True)
    p.add_argument("--val_file", default=None)
    p.add_argument("--output_dir", required=True)
    p.add_argument("--max_seq_length", type=int, default=512)
    p.add_argument("--per_device_train_batch_size", type=int, default=4)
    p.add_argument("--gradient_accumulation_steps", type=int, default=2)
    p.add_argument("--num_train_epochs", type=float, default=3.0)
    p.add_argument("--learning_rate", type=float, default=3e-4)
    p.add_argument("--warmup_ratio", type=float, default=0.05)
    p.add_argument("--weight_decay", type=float, default=0.0)
    p.add_argument("--lr_scheduler_type", default="cosine")
    p.add_argument("--lora_r", type=int, default=16)
    p.add_argument("--lora_alpha", type=int, default=32)
    p.add_argument("--lora_dropout", type=float, default=0.05)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--eval_steps", type=int, default=20)
    p.add_argument("--save_strategy", default="no", choices=["no", "epoch", "steps"])
    p.add_argument("--logging_steps", type=int, default=5)
    p.add_argument("--gradient_checkpointing", action="store_true")
    p.add_argument("--max_train_samples", type=int, default=None,
                   help="If set, cap training data size (debugging)")
    return p.parse_args()


def load_jsonl(path: str) -> list[dict]:
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def tokenize_dataset(records: list[dict], tok, max_len: int) -> Dataset:
    """Tokenize once for speed. We mask the prompt portion of the labels so
    loss only applies to the assistant turn (standard SFT practice)."""
    def gen():
        for r in records:
            yield {"text": build_train_text(r, tok)}

    ds = Dataset.from_generator(gen)

    def proc(batch):
        out = tok(
            batch["text"],
            truncation=True,
            max_length=max_len,
            padding=False,
        )
        labels_batch = []
        assistant_open = "<|im_start|>assistant\n"
        for i, text in enumerate(batch["text"]):
            ids = out["input_ids"][i]
            prompt_text = text[: text.rfind(assistant_open) + len(assistant_open)]
            prompt_ids = tok(prompt_text, truncation=True, max_length=max_len,
                             padding=False, add_special_tokens=False)["input_ids"]
            pl = min(len(prompt_ids), len(ids))
            lbl = [-100] * pl + ids[pl:]
            labels_batch.append(lbl)
        out["labels"] = labels_batch
        return out

    ds = ds.map(proc, batched=True, batch_size=16, remove_columns=["text"])
    return ds


class PadCollator:
    """Pad input_ids / labels to the longest sequence in the batch."""
    def __init__(self, pad_id: int):
        self.pad_id = pad_id

    def __call__(self, batch: list[dict]) -> dict:
        max_len = max(len(b["input_ids"]) for b in batch)
        ids = torch.full((len(batch), max_len), self.pad_id, dtype=torch.long)
        attn = torch.zeros((len(batch), max_len), dtype=torch.long)
        labs = torch.full((len(batch), max_len), -100, dtype=torch.long)
        for i, b in enumerate(batch):
            n = len(b["input_ids"])
            ids[i, :n] = torch.tensor(b["input_ids"], dtype=torch.long)
            attn[i, :n] = 1
            labs[i, :n] = torch.tensor(b["labels"], dtype=torch.long)
        return {"input_ids": ids, "attention_mask": attn, "labels": labs}


def main() -> int:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    print("[train_qwen35] starting", flush=True)
    print(json.dumps(vars(args), indent=2), flush=True)

    # Tokenizer
    tok = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    # Data
    train_records = load_jsonl(args.train_file)
    if args.max_train_samples:
        train_records = train_records[: args.max_train_samples]
    val_records = load_jsonl(args.val_file) if args.val_file else None
    print(f"[data] train={len(train_records)}  val={len(val_records) if val_records else 0}", flush=True)

    train_ds = tokenize_dataset(train_records, tok, args.max_seq_length)
    val_ds = tokenize_dataset(val_records, tok, args.max_seq_length) if val_records else None

    # Sequence-length stats
    lens = [len(x) for x in train_ds["input_ids"]]
    print(f"[data] tokenized train lens min={min(lens)} p50={sorted(lens)[len(lens)//2]} "
          f"p95={sorted(lens)[int(len(lens)*0.95)]} max={max(lens)}", flush=True)

    # Model
    print("[model] loading bf16 base...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        dtype=torch.bfloat16,
        device_map={"": 0},
        trust_remote_code=True,
        attn_implementation="sdpa",
    )
    model.config.use_cache = False
    if args.gradient_checkpointing:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()

    # LoRA — all attention + MLP projections that exist on this Qwen3.5
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj"]
    lc = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        target_modules=target_modules,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )
    model = get_peft_model(model, lc)
    model.print_trainable_parameters()

    # Training arguments
    targs = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        num_train_epochs=args.num_train_epochs,
        learning_rate=args.learning_rate,
        warmup_ratio=args.warmup_ratio,
        weight_decay=args.weight_decay,
        lr_scheduler_type=args.lr_scheduler_type,
        logging_steps=args.logging_steps,
        save_strategy=args.save_strategy,
        save_total_limit=2,
        eval_strategy=("steps" if val_ds is not None else "no"),
        eval_steps=args.eval_steps if val_ds is not None else None,
        bf16=True,
        fp16=False,
        report_to=[],
        dataloader_num_workers=0,
        seed=args.seed,
        max_grad_norm=1.0,
        optim="adamw_torch",
        remove_unused_columns=False,
        gradient_checkpointing=False,  # handled above to control use_reentrant
    )

    trainer = Trainer(
        model=model,
        args=targs,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=PadCollator(pad_id=tok.pad_token_id),
        processing_class=tok,
    )

    t0 = time.time()
    trainer.train()
    elapsed = time.time() - t0
    print(f"[train] wall={elapsed:.1f}s", flush=True)

    # Save adapter
    print(f"[save] LoRA adapter -> {args.output_dir}", flush=True)
    model.save_pretrained(args.output_dir)
    tok.save_pretrained(args.output_dir)

    # Dump metadata
    with open(Path(args.output_dir) / "train_meta.json", "w", encoding="utf-8") as f:
        json.dump({
            "model_path": args.model_path,
            "train_file": args.train_file,
            "val_file": args.val_file,
            "lora_r": args.lora_r,
            "lora_alpha": args.lora_alpha,
            "lora_dropout": args.lora_dropout,
            "target_modules": target_modules,
            "max_seq_length": args.max_seq_length,
            "num_train_epochs": args.num_train_epochs,
            "per_device_train_batch_size": args.per_device_train_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "effective_batch_size": args.per_device_train_batch_size * args.gradient_accumulation_steps,
            "learning_rate": args.learning_rate,
            "wall_seconds": elapsed,
        }, f, indent=2, ensure_ascii=False)

    # Final eval loss
    if val_ds is not None:
        m = trainer.evaluate()
        with open(Path(args.output_dir) / "final_eval.json", "w", encoding="utf-8") as f:
            json.dump(m, f, indent=2)
        print(f"[eval] final {m}", flush=True)

    print("[done] ok", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
