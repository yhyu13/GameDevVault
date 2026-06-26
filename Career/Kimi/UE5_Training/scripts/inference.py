#!/usr/bin/env python3
"""
UE5 Code LLM Inference Script
Load base model + LoRA adapter and generate responses.

Usage:
    python inference.py \
        --model_path ../outputs/ue5-coder-7b-lora \
        --base_model Qwen/Qwen2.5-Coder-7B-Instruct \
        --question "Nanite 的 Cluster Culling 和 Instance Culling 有什么区别？"

Or interactive mode:
    python inference.py \
        --model_path ../outputs/ue5-coder-7b-lora \
        --base_model Qwen/Qwen2.5-Coder-7B-Instruct \
        --interactive
"""

import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel


def parse_args():
    parser = argparse.ArgumentParser(description="UE5 Code LLM Inference")
    parser.add_argument("--model_path", type=str, required=True,
                        help="Path to LoRA adapter directory")
    parser.add_argument("--base_model", type=str, default="Qwen/Qwen2.5-Coder-7B-Instruct",
                        help="Base model name or path")
    parser.add_argument("--question", type=str, default=None,
                        help="Single question to answer")
    parser.add_argument("--interactive", action="store_true",
                        help="Run in interactive mode")
    parser.add_argument("--max_new_tokens", type=int, default=512,
                        help="Maximum new tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Sampling temperature")
    parser.add_argument("--top_p", type=float, default=0.9,
                        help="Top-p sampling")
    parser.add_argument("--top_k", type=int, default=50,
                        help="Top-k sampling")
    return parser.parse_args()


def build_prompt(question: str, model_name: str) -> str:
    """Build prompt based on model family."""
    model_name_lower = model_name.lower()
    if "qwen" in model_name_lower or "deepseek" in model_name_lower:
        return f"<|im_start|>user\n{question}\\n<|im_start|>assistant\\n"
    else:
        return f"### Instruction:\\n{question}\\n\\n### Response:\\n"


def load_model(model_path: str, base_model: str):
    """Load base model + LoRA adapter."""
    print(f"🚀 Loading base model: {base_model}")
    
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


def generate(model, tokenizer, prompt: str, args) -> str:
    """Generate response for a single prompt."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            top_k=args.top_k,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Remove the prompt from the output
    if prompt in generated_text:
        response = generated_text[len(prompt):].strip()
    else:
        response = generated_text.strip()
    
    return response


def interactive_mode(model, tokenizer, args):
    """Run interactive Q&A session."""
    print("\\n🎮 UE5 Code LLM Interactive Mode")
    print("   Type 'exit' or 'quit' to stop.\\n")
    
    while True:
        question = input("You: ").strip()
        if question.lower() in ("exit", "quit", "q"):
            print("\\n👋 Goodbye!")
            break
        if not question:
            continue
        
        prompt = build_prompt(question, args.base_model)
        response = generate(model, tokenizer, prompt, args)
        print(f"\\n🤖 Assistant: {response}\\n")
        print("-" * 60)


def main():
    args = parse_args()
    
    model, tokenizer = load_model(args.model_path, args.base_model)
    
    if args.interactive:
        interactive_mode(model, tokenizer, args)
    elif args.question:
        prompt = build_prompt(args.question, args.base_model)
        print(f"\\n❓ Question: {args.question}\\n")
        response = generate(model, tokenizer, prompt, args)
        print(f"🤖 Answer: {response}\\n")
    else:
        print("❌ Please provide --question or use --interactive mode")


if __name__ == "__main__":
    main()
