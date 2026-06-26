#!/usr/bin/env python3
"""
Convert human-written markdown templates into standard .jsonl training data.

Usage:
    python convert_human_data.py --input ../human_data --output ../data/human_sft.jsonl

Supports 4 template types from ../templates/:
    - template_qa.md          -> single-turn Q&A records
    - template_code.md        -> code explanation records
    - template_conversation.md -> multi-turn conversation records
    - template_negative.md    -> misconception correction records

How it works:
    1. Scans human_data/ for .md files
    2. Detects template type from headings (### Question / ### Code / ### Conversation / ### Misconception)
    3. Extracts Instruction, Output, Category
    4. Writes Alpaca-format .jsonl + conversation-format .jsonl
"""

import argparse
import json
import re
from pathlib import Path


def parse_qa(text: str) -> list:
    """Parse template_qa.md format."""
    records = []
    # Split by ### Question N
    blocks = re.split(r'###\s+Question\s+\d+', text)
    for block in blocks[1:]:  # skip preamble
        block = block.strip()
        if not block:
            continue
        
        inst_match = re.search(r'\*\*Instruction\*\*:\s*(.*?)(?=\*\*Category\*\*|$)', block, re.DOTALL)
        cat_match = re.search(r'\*\*Category\*\*:\s*(\S+)', block)
        out_match = re.search(r'\*\*Output\*\*:\s*(.*?)(?=###\s+Question|$)', block, re.DOTALL)
        
        if inst_match and out_match:
            instruction = inst_match.group(1).strip()
            output = out_match.group(1).strip()
            category = cat_match.group(1).strip() if cat_match else "interview_answer"
            records.append({
                "instruction": instruction,
                "input": "",
                "output": output,
                "source": "human_data",
                "category": category
            })
    return records


def parse_code(text: str) -> list:
    """Parse template_code.md format."""
    records = []
    blocks = re.split(r'###\s+Code\s+\d+', text)
    for block in blocks[1:]:
        block = block.strip()
        if not block:
            continue
        
        inst_match = re.search(r'\*\*Instruction\*\*:\s*(.*?)(?=\*\*Category\*\*|$)', block, re.DOTALL)
        cat_match = re.search(r'\*\*Category\*\*:\s*(\S+)', block)
        out_match = re.search(r'\*\*Output\*\*:\s*(.*?)(?=###\s+Code|$)', block, re.DOTALL)
        
        if inst_match and out_match:
            instruction = inst_match.group(1).strip()
            output = out_match.group(1).strip()
            category = cat_match.group(1).strip() if cat_match else "code_explanation"
            records.append({
                "instruction": instruction,
                "input": "",
                "output": output,
                "source": "human_data",
                "category": category
            })
    return records


def parse_conversation(text: str) -> list:
    """Parse template_conversation.md format."""
    records = []
    blocks = re.split(r'###\s+Conversation\s+\d+', text)
    for block in blocks[1:]:
        block = block.strip()
        if not block:
            continue
        
        topic_match = re.search(r'\*\*Topic\*\*:\s*(.*?)(?=\*\*Turn|$)', block, re.DOTALL)
        topic = topic_match.group(1).strip() if topic_match else "UE5 Interview"
        
        # Extract all turns
        turns = []
        turn_blocks = re.findall(
            r'\*\*Turn\s+\d+\*\*:\s*\n-\s+\*\*User\*\*:\s*(.*?)(?=\n-\s+\*\*Assistant\*\*:|$)\s*\n-\s+\*\*Assistant\*\*:\s*(.*?)(?=\*\*Turn|$)',
            block, re.DOTALL
        )
        
        for user_msg, assistant_msg in turn_blocks:
            user_msg = user_msg.strip()
            assistant_msg = assistant_msg.strip()
            if user_msg and assistant_msg:
                turns.append({"role": "user", "content": user_msg})
                turns.append({"role": "assistant", "content": assistant_msg})
        
        if turns:
            records.append({
                "conversation": turns,
                "source": "human_data",
                "category": "interview_conversation",
                "topic": topic
            })
    return records


def parse_negative(text: str) -> list:
    """Parse template_negative.md format."""
    records = []
    blocks = re.split(r'###\s+Misconception\s+\d+', text)
    for block in blocks[1:]:
        block = block.strip()
        if not block:
            continue
        
        inst_match = re.search(r'\*\*Instruction\*\*:\s*(.*?)(?=\*\*Category\*\*|$)', block, re.DOTALL)
        cat_match = re.search(r'\*\*Category\*\*:\s*(\S+)', block)
        out_match = re.search(r'\*\*Output\*\*:\s*(.*?)(?=###\s+Misconception|$)', block, re.DOTALL)
        
        if inst_match and out_match:
            instruction = inst_match.group(1).strip()
            output = out_match.group(1).strip()
            category = cat_match.group(1).strip() if cat_match else "misconception_correction"
            records.append({
                "instruction": instruction,
                "input": "",
                "output": output,
                "source": "human_data",
                "category": category
            })
    return records


def detect_template_type(text: str) -> str:
    """Detect template type from content."""
    if "### Question" in text:
        return "qa"
    elif "### Code" in text:
        return "code"
    elif "### Conversation" in text:
        return "conversation"
    elif "### Misconception" in text:
        return "negative"
    else:
        return "unknown"


def convert_file(filepath: Path) -> list:
    """Convert a single human data file to records."""
    text = filepath.read_text(encoding="utf-8")
    ttype = detect_template_type(text)
    
    if ttype == "qa":
        return parse_qa(text)
    elif ttype == "code":
        return parse_code(text)
    elif ttype == "conversation":
        return parse_conversation(text)
    elif ttype == "negative":
        return parse_negative(text)
    else:
        print(f"  WARN: Unknown template type in {filepath.name}, skipping")
        return []


def main():
    parser = argparse.ArgumentParser(description="Convert human data to .jsonl")
    parser.add_argument("--input", type=str, default="../human_data",
                        help="Directory containing human-written .md files")
    parser.add_argument("--output", type=str, default="../data/human_sft.jsonl",
                        help="Output .jsonl file path")
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        print(f"   Create it and copy templates from ../templates/ to start writing.")
        return
    
    all_records = []
    md_files = sorted(input_dir.glob("*.md"))
    
    if not md_files:
        print(f"⚠️ No .md files found in {input_dir}")
        print(f"   Copy templates from ../templates/ and start writing!")
        return
    
    print(f"📂 Found {len(md_files)} .md files in {input_dir}")
    
    for md_file in md_files:
        print(f"  Processing: {md_file.name}")
        records = convert_file(md_file)
        all_records.extend(records)
        print(f"    -> {len(records)} records")
    
    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    # Stats
    categories = {}
    for r in all_records:
        cat = r.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\n✅ Written {len(all_records)} records to {output_path}")
    print(f"\n📊 Breakdown:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Merge with auto-extracted data: cat {output_path} ../data/ue5_sft.jsonl > ../data/combined_sft.jsonl")
    print(f"   2. Train: python train_lora.py --dataset_path ../data/combined_sft.jsonl")


if __name__ == "__main__":
    main()
