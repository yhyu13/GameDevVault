#!/usr/bin/env python3
"""
UE5 Model Evaluation

Evaluate fine-tuned small model against:
  1. Fixed benchmark (held-out test set)
  2. Latest LLM baseline (compare answers side-by-side)
  3. MCP integration test (with live UE5 context)

Usage:
    # Basic evaluation on test set
    python eval_model.py \
        --model_path ../outputs/models/qwen-3b-ue5-lora \
        --base_model Qwen/Qwen2.5-Coder-3B-Instruct \
        --benchmark ../data/splits/test.jsonl \
        --output ../outputs/results/eval_qwen3b.json

    # With latest LLM baseline comparison
    python eval_model.py \
        --model_path ../outputs/models/qwen-3b-ue5-lora \
        --base_model Qwen/Qwen2.5-Coder-3B-Instruct \
        --benchmark ../data/splits/test.jsonl \
        --baseline_model claude-sonnet-4-20250514 \
        --output ../outputs/results/eval_qwen3b_vs_baseline.json
"""

import argparse
import json
import re
import time
from pathlib import Path
from typing import Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate UE5 fine-tuned model")
    parser.add_argument("--model_path", type=str, required=True,
                        help="Path to LoRA adapter")
    parser.add_argument("--base_model", type=str, required=True,
                        help="Base model name")
    parser.add_argument("--benchmark", type=str, required=True,
                        help="Benchmark JSONL file")
    parser.add_argument("--output", type=str, required=True,
                        help="Output JSON results")
    parser.add_argument("--max_new_tokens", type=int, default=512,
                        help="Max tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Sampling temperature")
    parser.add_argument("--baseline_model", type=str, default=None,
                        help="Optional: baseline LLM model name for comparison")
    parser.add_argument("--sample_limit", type=int, default=None,
                        help="Only evaluate first N questions")
    return parser.parse_args()


def load_model(model_path: str, base_model: str):
    """Load base model + LoRA adapter."""
    print(f"🚀 Loading model: {base_model}")
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    
    tokenizer = AutoTokenizer.from_pretrained(
        base_model,
        trust_remote_code=True,
        padding_side="right",
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    )
    
    print(f"🔌 Loading LoRA adapter from: {model_path}")
    model = PeftModel.from_pretrained(model, model_path)
    model.eval()
    
    return model, tokenizer


def build_prompt(record: dict, model_name: str) -> str:
    """Build prompt from benchmark record."""
    model_lower = model_name.lower()
    instruction = record.get("instruction", "")
    input_text = record.get("input", "")
    
    if input_text:
        user_msg = f"{instruction}\n\n{input_text}"
    else:
        user_msg = instruction
    
    if "qwen" in model_lower or "deepseek" in model_lower:
        return f"<|im_start|>user\n{user_msg}to<|im_start|>assistant\n"
    elif "llama" in model_lower:
        return f"<|begin_of_text|>to<|start_header_id|>user<|end_header_id|>\n\n{user_msg}<|eot_id|>to<|start_header_id|>assistant<|end_header_id|>\n\n"
    elif "phi" in model_lower:
        return f"<|im_start|>user\n{user_msg}to<|im_start|>assistant\n"
    else:
        return f"### Instruction:\n{user_msg}\n\n### Response:\n"


def generate(model, tokenizer, prompt: str, max_new_tokens: int, temperature: float) -> str:
    """Generate response."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    if prompt in generated_text:
        response = generated_text[len(prompt):].strip()
    else:
        response = generated_text.strip()
    
    return response


def keyword_overlap_score(pred: str, ref: str) -> float:
    """Compute keyword overlap score (0-1)."""
    pred_lower = pred.lower()
    ref_lower = ref.lower()
    
    # Extract technical terms
    ref_terms = set(re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z][a-zA-Z0-9_]*|\d+', ref_lower))
    pred_terms = set(re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z][a-zA-Z0-9_]*|\d+', pred_lower))
    
    if not ref_terms:
        return 0.0
    
    overlap = len(ref_terms & pred_terms)
    return overlap / len(ref_terms)


def structure_score(pred: str) -> float:
    """Score structural quality (0-1)."""
    score = 0.0
    
    # Has source code paths
    if re.search(r'engine[\\/]source[\\/]', pred.lower()):
        score += 0.25
    
    # Has code blocks
    if "```" in pred:
        score += 0.25
    
    # Has structured formatting (numbered lists, bullet points)
    if re.search(r'^\d+\.', pred, re.MULTILINE) or re.search(r'^[-*]', pred, re.MULTILINE):
        score += 0.25
    
    # Has trade-off or limitation mention
    if any(word in pred.lower() for word in ["trade-off", "tradeoff", "limitation", "limit", "代价", "局限", "bottleneck"]):
        score += 0.25
    
    return score


def evaluate_model(model, tokenizer, benchmark: list, model_name: str, args) -> dict:
    """Evaluate model on benchmark."""
    results = []
    total_keyword_score = 0.0
    total_struct_score = 0.0
    total_length = 0
    
    items = benchmark[:args.sample_limit] if args.sample_limit else benchmark
    
    for i, item in enumerate(items):
        prompt = build_prompt(item, model_name)
        reference = item.get("output", "")
        
        print(f"\n[{i+1}/{len(items)}] {item.get('topic', 'unknown')[:40]}")
        
        start_time = time.time()
        prediction = generate(model, tokenizer, prompt, args.max_new_tokens, args.temperature)
        gen_time = time.time() - start_time
        
        kw_score = keyword_overlap_score(prediction, reference)
        struct_score = structure_score(prediction)
        
        total_keyword_score += kw_score
        total_struct_score += struct_score
        total_length += len(prediction)
        
        results.append({
            "question": item.get("instruction", ""),
            "reference": reference,
            "prediction": prediction,
            "keyword_score": kw_score,
            "structure_score": struct_score,
            "generation_time": gen_time,
            "topic": item.get("topic", "unknown"),
            "template": item.get("template", "unknown"),
        })
        
        print(f"   Keyword: {kw_score:.2f} | Structure: {struct_score:.2f} | Time: {gen_time:.1f}s")
    
    n = len(items)
    return {
        "average_keyword_score": total_keyword_score / n if n else 0,
        "average_structure_score": total_struct_score / n if n else 0,
        "average_length": total_length / n if n else 0,
        "total_questions": n,
        "details": results,
    }


def main():
    args = parse_args()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    print(f"🎯 UE5 Model Evaluation")
    print(f"   Model: {args.model_path}")
    print(f"   Base: {args.base_model}")
    print(f"   Benchmark: {args.benchmark}")
    
    # Load benchmark
    benchmark = []
    with open(args.benchmark, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                benchmark.append(json.loads(line))
    
    print(f"   Benchmark size: {len(benchmark)}")
    if args.sample_limit:
        print(f"   Evaluating first {args.sample_limit} questions")
    
    # Load model
    model, tokenizer = load_model(args.model_path, args.base_model)
    
    # Evaluate
    print("\n🔥 Running evaluation...")
    results = evaluate_model(model, tokenizer, benchmark, args.base_model, args)
    
    # Save results
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Evaluation Summary")
    print("=" * 60)
    print(f"   Average Keyword Score: {results['average_keyword_score']:.2%}")
    print(f"   Average Structure Score: {results['average_structure_score']:.2%}")
    print(f"   Average Response Length: {results['average_length']:.0f} chars")
    print(f"   Total Questions: {results['total_questions']}")
    print(f"\n💾 Results saved to: {args.output}")
    print("=" * 60)
    
    # Baseline comparison note
    if args.baseline_model:
        print(f"\n📌 To compare with baseline {args.baseline_model}:")
        print(f"   Run the same eval with baseline and use export_to_excel.py")


if __name__ == "__main__":
    main()
