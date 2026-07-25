#!/usr/bin/env python3
"""
Evaluate LoRA-fine-tuned Qwen3.5 model on a JSONL alpaca-style dataset.

Loads base model in bf16, attaches the LoRA adapter, generates with the
tokenizer's chat template, scores with simple keyword overlap + length.

Usage:
    python eval_qwen35.py \
        --model_path /media/home/hangyu5/Documents/Hugging-Face/Qwen/Qwen3.5-0.8B \
        --adapter_dir outputs/models/qwen3.5-0.8b-ue5-lora \
        --input_file data/splits/test.jsonl \
        --output outputs/results/eval_test.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--model_path", required=True, help="Base model dir")
    p.add_argument("--adapter_dir", default=None,
                   help="LoRA adapter dir; if None, evaluate base model")
    p.add_argument("--input_file", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--max_new_tokens", type=int, default=256)
    p.add_argument("--temperature", type=float, default=0.0,
                   help="0=greedy; set >0 for sampling")
    p.add_argument("--max_input_tokens", type=int, default=480,
                   help="Truncate prompt to this to control prefill time")
    p.add_argument("--sample_limit", type=int, default=None)
    return p.parse_args()


def build_prompt(record: dict, tok) -> str:
    instr = record.get("instruction", "").strip()
    inp = record.get("input", "").strip()
    user = f"{instr}\n\n{inp}" if inp else instr
    msgs = [{"role": "user", "content": user}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


def keyword_terms(text: str) -> set[str]:
    text = text.lower()
    # English / UE5-style identifiers + Chinese 2+ chars + numbers
    return set(re.findall(r"[\u4e00-\u9fff]{2,}|[a-zA-Z][a-zA-Z0-9_]*|\d+", text))


def keyword_overlap(pred: str, ref: str) -> float:
    ref_t = keyword_terms(ref)
    if not ref_t:
        return 0.0
    pred_t = keyword_terms(pred)
    return len(ref_t & pred_t) / len(ref_t)


def structure_score(pred: str) -> float:
    s = 0.0
    # code fence
    if "```" in pred:
        s += 0.25
    # engine source path
    if re.search(r"engine[\\/]source[\\/]", pred.lower()):
        s += 0.25
    # structured list
    if re.search(r"^\s*(\d+\.|-|\*|\+)\s", pred, re.MULTILINE):
        s += 0.25
    # trade-off or limit discussion
    if any(w in pred.lower() for w in ["trade-off", "tradeoff", "limitation", "limit",
                                       "代价", "局限", "bottleneck"]):
        s += 0.25
    return s


def main() -> int:
    args = parse_args()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    print(f"[eval] base={args.model_path} adapter={args.adapter_dir} input={args.input_file}",
          flush=True)

    tok = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    print("[eval] loading base model bf16...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path,
        dtype=torch.bfloat16,
        device_map={"": 0},
        trust_remote_code=True,
        attn_implementation="sdpa",
    )
    if args.adapter_dir:
        print(f"[eval] attaching LoRA adapter from {args.adapter_dir}", flush=True)
        model = PeftModel.from_pretrained(model, args.adapter_dir)
    model.eval()

    records = []
    with open(args.input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    if args.sample_limit:
        records = records[: args.sample_limit]
    print(f"[eval] {len(records)} records", flush=True)

    results = []
    total_kw = 0.0
    total_struct = 0.0
    total_gen_len = 0
    total_time = 0.0
    detail_dump = []

    for i, rec in enumerate(records):
        prompt = build_prompt(rec, tok)
        enc = tok(prompt, return_tensors="pt", truncation=True,
                  max_length=args.max_input_tokens, add_special_tokens=False).to(model.device)

        gen_kwargs = dict(
            input_ids=enc["input_ids"],
            attention_mask=enc["attention_mask"],
            max_new_tokens=args.max_new_tokens,
            pad_token_id=tok.pad_token_id,
            eos_token_id=tok.eos_token_id,
        )
        if args.temperature > 0:
            gen_kwargs.update(do_sample=True, temperature=args.temperature, top_p=0.9)
        else:
            gen_kwargs.update(do_sample=False)

        t0 = time.time()
        with torch.no_grad():
            out = model.generate(**gen_kwargs)
        dt = time.time() - t0

        text = tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=False)
        # strip trailing <|im_end|> / <|endoftext|>
        for tok_stop in ("<|im_end|>", "<|endoftext|>"):
            if text.endswith(tok_stop):
                text = text[: -len(tok_stop)]
        text = text.strip()

        ref = rec.get("output", "").strip()
        kw = keyword_overlap(text, ref)
        sc = structure_score(text)
        total_kw += kw
        total_struct += sc
        total_gen_len += len(text)
        total_time += dt

        results.append({
            "index": i,
            "topic": rec.get("topic", ""),
            "question": rec.get("instruction", ""),
            "input": rec.get("input", ""),
            "reference": ref,
            "prediction": text,
            "keyword_overlap": kw,
            "structure_score": sc,
            "gen_time_seconds": dt,
            "char_len": len(text),
        })
        detail_dump.append({
            "topic": rec.get("topic", ""),
            "q": rec.get("instruction", "")[:80],
            "ref_head": ref[:120].replace("\n", " "),
            "pred_head": text[:120].replace("\n", " "),
            "kw": round(kw, 3),
            "struct": round(sc, 3),
        })
        print(f"  [{i+1}/{len(records)}] kw={kw:.2f} struct={sc:.2f} t={dt:.1f}s  "
              f"q={rec.get('instruction','')[:60]!r}", flush=True)

    n = len(records)
    summary = {
        "base_model": args.model_path,
        "adapter_dir": args.adapter_dir,
        "input_file": args.input_file,
        "n": n,
        "avg_keyword_overlap": total_kw / n if n else 0,
        "avg_structure_score": total_struct / n if n else 0,
        "avg_gen_chars": total_gen_len / n if n else 0,
        "avg_gen_time_seconds": total_time / n if n else 0,
        "total_seconds": total_time,
    }
    out = {"summary": summary, "details": results}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # Per-record short MD for browsing
    md_path = Path(args.output).with_suffix(".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Eval: {Path(args.input_file).name}  adapter={args.adapter_dir or 'BASE'}\n\n")
        f.write(f"n={n}  avg_kw={summary['avg_keyword_overlap']:.3f}  "
                f"avg_struct={summary['avg_structure_score']:.3f}  "
                f"avg_chars={summary['avg_gen_chars']:.0f}  "
                f"avg_t={summary['avg_gen_time_seconds']:.1f}s\n\n")
        f.write("| # | topic | kw | struct | question | ref head | pred head |\n")
        f.write("|---|-------|----|--------|---------|---------|-----------|\n")
        for j, d in enumerate(detail_dump):
            f.write(f"| {j+1} | {d['topic'][:24]} | {d['kw']:.2f} | {d['struct']:.2f} | "
                    f"{d['q']!r} | {d['ref_head']!r} | {d['pred_head']!r} |\n")
    print(f"[eval] saved {args.output} and {md_path}", flush=True)
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
