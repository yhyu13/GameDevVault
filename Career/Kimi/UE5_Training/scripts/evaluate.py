#!/usr/bin/env python3
"""
UE5 Code LLM Evaluation Script
Evaluate fine-tuned model against benchmark quiz questions.

Usage:
    python evaluate.py \
        --model_path ../outputs/ue5-coder-7b-lora \
        --base_model Qwen/Qwen2.5-Coder-7B-Instruct \
        --benchmark ../benchmark/ue5_eval.jsonl \
        --output ../outputs/eval_results.json
"""

import argparse
import json
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate UE5 Code LLM")
    parser.add_argument("--model_path", type=str, required=True,
                        help="Path to LoRA adapter")
    parser.add_argument("--base_model", type=str, default="Qwen/Qwen2.5-Coder-7B-Instruct",
                        help="Base model name")
    parser.add_argument("--benchmark", type=str, default="../benchmark/ue5_eval.jsonl",
                        help="Path to benchmark .jsonl")
    parser.add_argument("--output", type=str, default="../outputs/eval_results.json",
                        help="Path to save evaluation results")
    parser.add_argument("--max_new_tokens", type=int, default=512,
                        help="Max tokens to generate")
    parser.add_argument("--sample_limit", type=int, default=None,
                        help="Only evaluate first N questions (for quick test)")
    return parser.parse_args()


def load_benchmark(path: str) -> list:
    """Load benchmark questions."""
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def load_model(model_path: str, base_model: str):
    """Load base model + LoRA adapter."""
    print(f"🚀 Loading model: {base_model} + {model_path}")
    
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
    
    model = PeftModel.from_pretrained(model, model_path)
    model.eval()
    
    return model, tokenizer


def build_prompt(question: str, model_name: str) -> str:
    """Build evaluation prompt."""
    model_name_lower = model_name.lower()
    if "qwen" in model_name_lower or "deepseek" in model_name_lower:
        return f"<|im_start|>user\n{question}\n<|im_start|>assistant\n"
    else:
        return f"### Instruction:\n{question}\n\n### Response:\n"


def generate(model, tokenizer, prompt: str, max_new_tokens: int) -> str:
    """Generate response."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
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


def simple_similarity(pred: str, ref: str) -> float:
    """Simple keyword-based similarity score (0-1)."""
    pred_lower = pred.lower()
    ref_lower = ref.lower()
    
    # Extract key terms (Chinese and English words, numbers)
    ref_terms = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z_][a-zA-Z0-9_]*|\d+', ref_lower))
    pred_terms = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z_][a-zA-Z0-9_]*|\d+', pred_lower))
    
    if not ref_terms:
        return 0.0
    
    overlap = len(ref_terms & pred_terms)
    return overlap / len(ref_terms)


def evaluate(model, tokenizer, benchmark: list, args) -> dict:
    """Run evaluation and return results."""
    results = []
    total_score = 0.0
    
    items = benchmark[:args.sample_limit] if args.sample_limit else benchmark
    
    for i, item in enumerate(items):
        question = item["question"]
        reference = item["answer"]
        module = item.get("module", "unknown")
        q_type = item.get("type", "unknown")
        
        print(f"\n[{i+1}/{len(items)}] {module} | {q_type}")
        print(f"   Q: {question[:80]}...")
        
        prompt = build_prompt(question, args.base_model)
        prediction = generate(model, tokenizer, prompt, args.max_new_tokens)
        
        score = simple_similarity(prediction, reference)
        total_score += score
        
        results.append({
            "question": question,
            "reference": reference,
            "prediction": prediction,
            "score": score,
            "module": module,
            "type": q_type,
        })
        
        print(f"   Score: {score:.2f}")
        print(f"   Pred: {prediction[:120]}...")
    
    avg_score = total_score / len(items) if items else 0.0
    
    # Per-module breakdown
    module_scores = {}
    module_counts = {}
    for r in results:
        mod = r["module"]
        module_scores[mod] = module_scores.get(mod, 0.0) + r["score"]
        module_counts[mod] = module_counts.get(mod, 0) + 1
    
    module_breakdown = {
        mod: module_scores[mod] / module_counts[mod]
        for mod in module_scores
    }
    
    # Per-type breakdown
    type_scores = {}
    type_counts = {}
    for r in results:
        t = r["type"]
        type_scores[t] = type_scores.get(t, 0.0) + r["score"]
        type_counts[t] = type_counts.get(t, 0) + 1
    
    type_breakdown = {
        t: type_scores[t] / type_counts[t]
        for t in type_scores
    }
    
    return {
        "average_score": avg_score,
        "total_questions": len(items),
        "module_breakdown": module_breakdown,
        "type_breakdown": type_breakdown,
        "details": results,
    }


def main():
    args = parse_args()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    print("📂 Loading benchmark...")
    benchmark = load_benchmark(args.benchmark)
    print(f"   Benchmark size: {len(benchmark)} questions")
    
    if args.sample_limit:
        print(f"   Evaluating first {args.sample_limit} questions")
    
    model, tokenizer = load_model(args.model_path, args.base_model)
    
    print("\n🎯 Running evaluation...")
    results = evaluate(model, tokenizer, benchmark, args)
    
    # Save results
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Evaluation Summary")
    print("=" * 60)
    print(f"   Average Score: {results['average_score']:.2%}")
    print(f"   Total Questions: {results['total_questions']}")
    print("\n   Per Module:")
    for mod, score in sorted(results['module_breakdown'].items(), key=lambda x: -x[1]):
        print(f"      {mod:12s}: {score:.2%}")
    print("\n   Per Question Type:")
    for t, score in sorted(results['type_breakdown'].items(), key=lambda x: -x[1]):
        print(f"      {t:12s}: {score:.2%}")
    print(f"\n💾 Results saved to: {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
