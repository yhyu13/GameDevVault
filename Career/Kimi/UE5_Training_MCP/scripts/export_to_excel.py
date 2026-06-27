#!/usr/bin/env python3
"""
UE5 Evaluation Results to Excel

Export evaluation results to Excel for comparison and analysis.

Usage:
    # Single model results
    python export_to_excel.py \
        --results ../outputs/results/eval_qwen3b.json \
        --output ../outputs/results/eval_qwen3b.xlsx

    # Multiple models comparison
    python export_to_excel.py \
        --results ../outputs/results/eval_*.json \
        --output ../outputs/results/comparison_report.xlsx
"""

import argparse
import glob
import json
from pathlib import Path
from typing import List

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description="Export eval results to Excel")
    parser.add_argument("--results", type=str, nargs="+", required=True,
                        help="Result JSON files (supports glob patterns)")
    parser.add_argument("--output", type=str, required=True,
                        help="Output Excel file")
    return parser.parse_args()


def load_result(path: str) -> dict:
    """Load a single evaluation result."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_model_name(path: str) -> str:
    """Extract model name from file path."""
    stem = Path(path).stem
    # Remove 'eval_' prefix if present
    if stem.startswith("eval_"):
        stem = stem[5:]
    return stem


def create_summary_sheet(results: List[tuple]) -> pd.DataFrame:
    """Create summary comparison sheet."""
    rows = []
    for model_name, data in results:
        rows.append({
            "Model": model_name,
            "Keyword Score": f"{data.get('average_keyword_score', 0):.2%}",
            "Structure Score": f"{data.get('average_structure_score', 0):.2%}",
            "Avg Length": f"{data.get('average_length', 0):.0f}",
            "Questions": data.get('total_questions', 0),
        })
    return pd.DataFrame(rows)


def create_detail_sheet(results: List[tuple]) -> pd.DataFrame:
    """Create detailed per-question comparison sheet."""
    all_rows = []
    
    for model_name, data in results:
        for detail in data.get("details", []):
            all_rows.append({
                "Model": model_name,
                "Topic": detail.get("topic", ""),
                "Template": detail.get("template", ""),
                "Question": detail.get("question", ""),
                "Prediction": detail.get("prediction", ""),
                "Reference": detail.get("reference", ""),
                "Keyword Score": detail.get("keyword_score", 0),
                "Structure Score": detail.get("structure_score", 0),
                "Gen Time (s)": detail.get("generation_time", 0),
            })
    
    return pd.DataFrame(all_rows)


def create_topic_breakdown(results: List[tuple]) -> pd.DataFrame:
    """Create per-topic performance breakdown."""
    rows = []
    
    for model_name, data in results:
        topic_scores = {}
        topic_counts = {}
        
        for detail in data.get("details", []):
            topic = detail.get("topic", "unknown")
            if topic not in topic_scores:
                topic_scores[topic] = 0
                topic_counts[topic] = 0
            topic_scores[topic] += detail.get("keyword_score", 0)
            topic_counts[topic] += 1
        
        for topic in topic_scores:
            avg_score = topic_scores[topic] / topic_counts[topic]
            rows.append({
                "Model": model_name,
                "Topic": topic,
                "Avg Keyword Score": avg_score,
                "Questions": topic_counts[topic],
            })
    
    return pd.DataFrame(rows)


def main():
    args = parse_args()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📊 Exporting to Excel: {args.output}")
    
    # Expand glob patterns
    all_paths = []
    for pattern in args.results:
        if "*" in pattern or "?" in pattern:
            all_paths.extend(glob.glob(pattern))
        else:
            all_paths.append(pattern)
    
    all_paths = sorted(set(all_paths))
    print(f"   Found {len(all_paths)} result files:")
    for p in all_paths:
        print(f"     - {p}")
    
    # Load all results
    results = []
    for path in all_paths:
        try:
            data = load_result(path)
            model_name = extract_model_name(path)
            results.append((model_name, data))
        except Exception as e:
            print(f"   ERROR loading {path}: {e}")
    
    if not results:
        print("❌ No valid result files found")
        return
    
    # Create sheets
    summary_df = create_summary_sheet(results)
    detail_df = create_detail_sheet(results)
    topic_df = create_topic_breakdown(results)
    
    # Write to Excel with multiple sheets
    with pd.ExcelWriter(args.output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        detail_df.to_excel(writer, sheet_name="Details", index=False)
        topic_df.to_excel(writer, sheet_name="Topic Breakdown", index=False)
        
        # Auto-adjust column widths
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 80)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"\n✅ Excel report saved to: {args.output}")
    print(f"   Sheets: Summary, Details, Topic Breakdown")
    print(f"   Models compared: {len(results)}")
    print(f"   Total questions: {sum(len(r[1].get('details', [])) for r in results)}")


if __name__ == "__main__":
    main()
