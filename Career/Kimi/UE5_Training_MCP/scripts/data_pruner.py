#!/usr/bin/env python3
"""
UE5 Data Pruner

Prune low-quality LLM-generated conversations using multiple filters:
  - Length filter (too short / too long)
  - Factuality filter (check against known UE5 facts)
  - Duplicate filter (semantic deduplication)
  - Quality scoring (LLM-as-judge or heuristic)

Usage:
    python data_pruner.py \
        --input ../data/raw/conversations.jsonl \
        --output ../data/processed/conversations_pruned.jsonl \
        --min_quality 3.0 \
        --dedup_threshold 0.85

Outputs:
    - data/processed/conversations_pruned.jsonl (filtered data)
    - data/processed/pruning_report.json (stats per filter)
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path


# Known UE5 facts for factuality checking
UE5_FACTS = {
    "source_paths": [
        "Engine\\Source\\Runtime",
        "Engine\\Source\\Runtime\\Renderer",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Nanite",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Lumen",
        "Engine\\Source\\Runtime\\Renderer\\Private\\VirtualShadowMaps",
        "Engine\\Source\\Runtime\\Engine\\Public",
        "Engine\\Source\\Runtime\\Engine\\Public\\NaniteResources.h",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Nanite\\NaniteClusterCulling.cpp",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Nanite\\NaniteRasterizer.cpp",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Lumen\\LumenSceneLighting.cpp",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Lumen\\LumenSurfaceCache.cpp",
    ],
    "keywords": [
        "Cluster", "ClusterGroup", "Page", "DAG", "HZB", "GPUScene",
        "SurfaceCache", "LumenCard", "ScreenProbe", "Radiosity",
        "VirtualShadowMap", "PageTable", "PhysicalPage", "Clipmap",
        "MeshSDF", "SphereTracing", "ConeTracing", "VisibilityBuffer",
        "RenderGraph", "RDG", "BasePass", "NaniteRender",
        "CardCapturesPerFrame", "MaxNumAdaptiveProbes",
    ],
    "numbers": [
        "128",  # Cluster size
        "16",   # Screen probe spacing
        "6",    # Lumen card directions
    ],
}


def count_tokens(text: str) -> int:
    """Rough token count (Chinese chars + English words)."""
    # Chinese characters count as tokens
    chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
    # English words
    english = len(re.findall(r'[a-zA-Z]+', text))
    return chinese + english


def length_filter(record: dict, min_tokens: int = 100, max_tokens: int = 2048) -> tuple:
    """Filter by conversation length."""
    conversation = record.get("conversation", [])
    total_text = " ".join([turn.get("content", "") for turn in conversation])
    token_count = count_tokens(total_text)

    if token_count < min_tokens:
        return False, f"too_short ({token_count} tokens < {min_tokens})"
    if token_count > max_tokens:
        return False, f"too_long ({token_count} tokens > {max_tokens})"
    return True, f"ok ({token_count} tokens)"


def factuality_filter(record: dict) -> tuple:
    """Check if conversation contains known UE5 facts."""
    conversation = record.get("conversation", [])
    total_text = " ".join([turn.get("content", "") for turn in conversation]).lower()

    score = 0
    reasons = []

    # Check source paths
    for path in UE5_FACTS["source_paths"]:
        if path.lower().replace("\\", "/") in total_text.replace("\\", "/"):
            score += 2
            reasons.append("has_source_path")
            break

    # Check keywords
    keyword_hits = sum(1 for kw in UE5_FACTS["keywords"] if kw.lower() in total_text)
    if keyword_hits >= 3:
        score += 2
        reasons.append(f"keywords({keyword_hits})")
    elif keyword_hits >= 1:
        score += 1
        reasons.append(f"keywords({keyword_hits})")

    # Check specific numbers
    for num in UE5_FACTS["numbers"]:
        if num in total_text:
            score += 1
            reasons.append(f"number({num})")
            break

    # Check for code blocks
    if "```cpp" in total_text or "```c++" in total_text:
        score += 2
        reasons.append("has_code_block")
    elif "```" in total_text:
        score += 1
        reasons.append("has_code_block")

    # Check for "trade-off" or "limitation" mentions (indicates depth)
    if any(word in total_text for word in ["trade-off", "tradeoff", "limitation", "limit", "代价", "局限"]):
        score += 1
        reasons.append("has_tradeoff")

    if score >= 3:
        return True, f"score={score} ({', '.join(reasons)})"
    else:
        return False, f"score={score} ({', '.join(reasons)}) - too few facts"


def jaccard_similarity(text1: str, text2: str) -> float:
    """Compute Jaccard similarity between two texts."""
    # Extract keywords (Chinese + English terms)
    def extract_terms(text):
        text = text.lower()
        # Chinese terms (2+ chars)
        chinese = re.findall(r'[\u4e00-\u9fff]{2,}', text)
        # English technical terms (camelCase, snake_case, or single words)
        english = re.findall(r'[a-zA-Z][a-zA-Z0-9_]*', text)
        return set(chinese + english)

    terms1 = extract_terms(text1)
    terms2 = extract_terms(text2)

    if not terms1 or not terms2:
        return 0.0

    intersection = len(terms1 & terms2)
    union = len(terms1 | terms2)
    return intersection / union if union > 0 else 0.0


def deduplicate(records: list, threshold: float = 0.85) -> tuple:
    """Remove semantically similar conversations."""
    kept = []
    removed = []

    for i, record in enumerate(records):
        text_i = " ".join([turn.get("content", "") for turn in record.get("conversation", [])])

        is_duplicate = False
        for kept_record in kept:
            text_j = " ".join([turn.get("content", "") for turn in kept_record.get("conversation", [])])
            sim = jaccard_similarity(text_i, text_j)
            if sim >= threshold:
                is_duplicate = True
                removed.append({
                    "index": i,
                    "reason": f"duplicate(similarity={sim:.2f})",
                })
                break

        if not is_duplicate:
            kept.append(record)

    return kept, removed


def heuristic_quality_score(record: dict) -> float:
    """Score a conversation on quality (0-5)."""
    conversation = record.get("conversation", [])
    total_text = " ".join([turn.get("content", "") for turn in conversation]).lower()
    score = 0.0

    # Length
    token_count = count_tokens(total_text)
    if token_count > 500:
        score += 1.0
    elif token_count > 200:
        score += 0.5

    # Technical depth indicators
    depth_markers = [
        "source", "engine", "cpp", "function", "struct", "class",
        "algorithm", "optimize", "performance", "memory", "gpu", "cpu",
        "trade-off", "tradeoff", "limitation", "bottleneck",
        "源码", "函数", "结构体", "优化", "性能", "内存", "瓶颈",
    ]
    depth_hits = sum(1 for m in depth_markers if m in total_text)
    score += min(depth_hits / 5, 1.0)  # cap at 1.0

    # Source code paths
    if re.search(r'engine[\\/]source[\\/]', total_text):
        score += 1.0

    # Code blocks
    if "```" in total_text:
        score += 1.0

    # Multi-turn depth (more turns = more depth)
    num_turns = len(conversation)
    if num_turns >= 8:
        score += 1.0
    elif num_turns >= 4:
        score += 0.5

    # Specificity (numbers and function names)
    if re.search(r'\b\d{2,}\b', total_text) and re.search(r'[a-zA-Z][a-zA-Z0-9]*\(', total_text):
        score += 1.0

    return min(score, 5.0)


def main():
    parser = argparse.ArgumentParser(description="Prune LLM-generated UE5 training data")
    parser.add_argument("--input", type=str, default="../data/raw/conversations.jsonl",
                        help="Input JSONL file")
    parser.add_argument("--output", type=str, default="../data/processed/conversations_pruned.jsonl",
                        help="Output pruned JSONL file")
    parser.add_argument("--min_quality", type=float, default=3.0,
                        help="Minimum quality score (0-5)")
    parser.add_argument("--dedup_threshold", type=float, default=0.85,
                        help="Jaccard similarity threshold for deduplication")
    parser.add_argument("--min_tokens", type=int, default=100,
                        help="Minimum conversation length in tokens")
    parser.add_argument("--max_tokens", type=int, default=2048,
                        help="Maximum conversation length in tokens")
    parser.add_argument("--report", type=str, default="../data/processed/pruning_report.json",
                        help="Pruning report JSON")
    args = parser.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)

    print(f"🧹 UE5 Data Pruner")
    print(f"   Input: {args.input}")
    print(f"   Filters: length[{args.min_tokens}-{args.max_tokens}], quality>={args.min_quality}, dedup<{args.dedup_threshold}")

    # Load data
    records = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"   Loaded {len(records)} raw records")

    # Apply filters sequentially
    stats = {
        "input_count": len(records),
        "length_filter": {"passed": 0, "removed": 0, "details": []},
        "factuality_filter": {"passed": 0, "removed": 0, "details": []},
        "quality_filter": {"passed": 0, "removed": 0, "details": []},
        "dedup_filter": {"passed": 0, "removed": 0, "details": []},
    }

    # Step 1: Length filter
    after_length = []
    for i, record in enumerate(records):
        ok, reason = length_filter(record, args.min_tokens, args.max_tokens)
        if ok:
            after_length.append(record)
            stats["length_filter"]["passed"] += 1
        else:
            stats["length_filter"]["removed"] += 1
            stats["length_filter"]["details"].append({"index": i, "reason": reason})
    print(f"   Length filter: {stats['length_filter']['passed']} passed, {stats['length_filter']['removed']} removed")

    # Step 2: Factuality filter
    after_factuality = []
    for i, record in enumerate(after_length):
        ok, reason = factuality_filter(record)
        if ok:
            after_factuality.append(record)
            stats["factuality_filter"]["passed"] += 1
        else:
            stats["factuality_filter"]["removed"] += 1
            stats["factuality_filter"]["details"].append({"index": i, "reason": reason})
    print(f"   Factuality filter: {stats['factuality_filter']['passed']} passed, {stats['factuality_filter']['removed']} removed")

    # Step 3: Quality score filter
    after_quality = []
    for i, record in enumerate(after_factuality):
        score = heuristic_quality_score(record)
        record["_quality_score"] = score
        if score >= args.min_quality:
            after_quality.append(record)
            stats["quality_filter"]["passed"] += 1
        else:
            stats["quality_filter"]["removed"] += 1
            stats["quality_filter"]["details"].append({"index": i, "reason": f"score={score:.2f} < {args.min_quality}"})
    print(f"   Quality filter (>{=args.min_quality}): {stats['quality_filter']['passed']} passed, {stats['quality_filter']['removed']} removed")

    # Step 4: Deduplication
    after_dedup, removed = deduplicate(after_quality, args.dedup_threshold)
    stats["dedup_filter"]["passed"] = len(after_dedup)
    stats["dedup_filter"]["removed"] = len(removed)
    stats["dedup_filter"]["details"] = removed
    print(f"   Deduplication (<{args.dedup_threshold}): {stats['dedup_filter']['passed']} passed, {stats['dedup_filter']['removed']} removed")

    # Final stats
    final_records = after_dedup
    stats["output_count"] = len(final_records)
    stats["retention_rate"] = len(final_records) / len(records) if records else 0.0
    stats["quality_distribution"] = Counter([r["_quality_score"] for r in final_records])

    # Remove internal score before writing
    for r in final_records:
        r.pop("_quality_score", None)

    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        for r in final_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Write report
    with open(args.report, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Pruning complete!")
    print(f"   Input:  {len(records)} records")
    print(f"   Output: {len(final_records)} records ({stats['retention_rate']:.1%} retention)")
    print(f"   Output: {args.output}")
    print(f"   Report: {args.report}")


if __name__ == "__main__":
    main()
