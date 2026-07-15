#!/usr/bin/env python3
"""
UE5 Data Preparation

Format pruned conversations into train/val/test splits for SFT.
Converts conversation format to standard instruction-following format.

Usage:
    python data_prep.py \
        --input ../data/processed/conversations_pruned.jsonl \
        --output_dir ../data/splits \
        --train_ratio 0.8 \
        --val_ratio 0.1

Outputs:
    - data/splits/train.jsonl
    - data/splits/val.jsonl
    - data/splits/test.jsonl
    - data/splits/dataset_stats.json
"""

import argparse
import json
import random
import sys
from pathlib import Path

# Force UTF-8 stdout/stderr on Windows where the default is GBK.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def conversation_to_alpaca(record: dict) -> dict:
    """Convert conversation format to Alpaca instruction format."""
    conversation = record.get("conversation", [])
    if not conversation:
        return None

    # Use first user message as instruction, rest as context
    instruction_parts = []
    output_parts = []
    current_role = None

    for turn in conversation:
        role = turn.get("role", "")
        content = turn.get("content", "").strip()
        if not content:
            continue

        if role == "user":
            instruction_parts.append(content)
        elif role == "assistant":
            output_parts.append(content)

    if not instruction_parts or not output_parts:
        return None

    instruction = instruction_parts[0]
    # If there are multiple user turns, append as context
    if len(instruction_parts) > 1:
        input_text = "\n\n".join(instruction_parts[1:])
    else:
        input_text = ""

    output = output_parts[0]
    # If there are multiple assistant turns, combine
    if len(output_parts) > 1:
        output = "\n\n".join(output_parts)

    return {
        "instruction": instruction,
        "input": input_text,
        "output": output,
        "source": record.get("source", "unknown"),
        "topic": record.get("topic", "unknown"),
        "template": record.get("template", "unknown"),
        "category": "conversation_to_alpaca",
    }


def conversation_to_sharegpt(record: dict) -> dict:
    """Convert to ShareGPT format (for training with chat templates)."""
    conversation = record.get("conversation", [])
    if not conversation:
        return None

    messages = []
    for turn in conversation:
        role = turn.get("role", "")
        content = turn.get("content", "").strip()
        if not content:
            continue

        if role in ("user", "human"):
            messages.append({"from": "human", "value": content})
        elif role in ("assistant", "gpt"):
            messages.append({"from": "gpt", "value": content})

    if len(messages) < 2:
        return None

    return {
        "conversations": messages,
        "source": record.get("source", "unknown"),
        "topic": record.get("topic", "unknown"),
        "template": record.get("template", "unknown"),
        "category": "conversation_sharegpt",
    }


def split_dataset(records: list, train_ratio: float, val_ratio: float, seed: int = 42):
    """Split dataset into train/val/test."""
    random.seed(seed)
    shuffled = records.copy()
    random.shuffle(shuffled)

    n = len(shuffled)
    train_end = int(n * train_ratio)
    val_end = train_end + int(n * val_ratio)

    train = shuffled[:train_end]
    val = shuffled[train_end:val_end]
    test = shuffled[val_end:]

    return train, val, test


def main():
    parser = argparse.ArgumentParser(description="Prepare UE5 training data")
    parser.add_argument("--input", type=str, default="../data/processed/conversations_pruned.jsonl",
                        help="Input pruned JSONL")
    parser.add_argument("--output_dir", type=str, default="../data/splits",
                        help="Output directory for splits")
    parser.add_argument("--train_ratio", type=float, default=0.8,
                        help="Train split ratio")
    parser.add_argument("--val_ratio", type=float, default=0.1,
                        help="Validation split ratio")
    parser.add_argument("--format", type=str, default="alpaca",
                        choices=["alpaca", "sharegpt"],
                        help="Output format")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 UE5 Data Preparation")
    print(f"   Input: {args.input}")
    print(f"   Format: {args.format}")
    print(f"   Split: train={args.train_ratio}, val={args.val_ratio}, test={1.0 - args.train_ratio - args.val_ratio}")

    # Load
    records = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"   Loaded {len(records)} records")

    # Convert format
    if args.format == "alpaca":
        converted = []
        for r in records:
            c = conversation_to_alpaca(r)
            if c:
                converted.append(c)
    else:  # sharegpt
        converted = []
        for r in records:
            c = conversation_to_sharegpt(r)
            if c:
                converted.append(c)

    print(f"   Converted to {len(converted)} {args.format} records")

    # Split
    train, val, test = split_dataset(converted, args.train_ratio, args.val_ratio, args.seed)
    print(f"   Split: train={len(train)}, val={len(val)}, test={len(test)}")

    # Write splits
    train_path = output_dir / "train.jsonl"
    val_path = output_dir / "val.jsonl"
    test_path = output_dir / "test.jsonl"

    for path, split in [(train_path, train), (val_path, val), (test_path, test)]:
        with open(path, "w", encoding="utf-8") as f:
            for r in split:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Stats
    stats = {
        "input_count": len(records),
        "converted_count": len(converted),
        "train_count": len(train),
        "val_count": len(val),
        "test_count": len(test),
        "format": args.format,
        "seed": args.seed,
    }

    # Add topic distribution
    topic_counts = {}
    for r in converted:
        topic = r.get("topic", "unknown")
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    stats["topic_distribution"] = topic_counts

    stats_path = output_dir / "dataset_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Data preparation complete!")
    print(f"   Train: {train_path}")
    print(f"   Val:   {val_path}")
    print(f"   Test:  {test_path}")
    print(f"   Stats: {stats_path}")


if __name__ == "__main__":
    main()
