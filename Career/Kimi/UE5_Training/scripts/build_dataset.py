#!/usr/bin/env python3
"""
UE5 Dataset Builder
Extracts instruction-following data from UE5 technical docs and quiz HTML cards.
Produces Alpaca-format .jsonl for SFT fine-tuning.

Usage:
    python build_dataset.py

Outputs:
    - data/ue5_sft.jsonl          (main SFT dataset)
    - data/ue5_code.jsonl         (code-text pairs)
    - data/ue5_conversation.jsonl (multi-turn interview chains)
    - benchmark/ue5_eval.jsonl     (56 quiz questions for evaluation)
"""

import json
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
UE5_DIR = BASE_DIR / "UE5"
HTML_DIR = UE5_DIR / "html"
DATA_DIR = BASE_DIR / "UE5_Training" / "data"
BENCHMARK_DIR = BASE_DIR / "UE5_Training" / "benchmark"

def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_sections_from_md(md_text):
    """Extract (title, content) pairs from markdown sections."""
    sections = []
    # Match ## or ### headers and their content until next header
    pattern = r"^(#{2,3})\s+(.*?)\n(.*?)(?=\n#{2,3}\s|\Z)"
    for m in re.finditer(pattern, md_text, re.MULTILINE | re.DOTALL):
        level, title, content = m.group(1), m.group(2).strip(), m.group(3).strip()
        if not content or len(content) < 50:
            continue
        sections.append((title, content))
    return sections

def build_doc_qa(sections):
    """Convert markdown sections to instruction-following Q&A pairs."""
    records = []
    for title, content in sections:
        # Skip non-technical sections (打油诗, 速查表 headers)
        if "打油诗" in title or "速查表" in title or "面试扩展" in title:
            continue
        if len(content) < 80:
            continue

        instruction = f"详细解释 UE5 中的「{title}」，包括源码路径和核心概念。"
        output = content
        records.append({
            "instruction": instruction,
            "input": "",
            "output": output,
            "source": "UE5_Detail.md",
            "category": "technical_explanation"
        })

        # Also generate a shorter interview-style Q
        short_instruction = f"面试官问：{title} 是什么？你能一句话解释吗？"
        # Extract first paragraph or first sentence
        first_para = content.split("\n\n")[0].strip()
        if len(first_para) > 300:
            first_para = first_para[:300] + "..."
        records.append({
            "instruction": short_instruction,
            "input": "",
            "output": first_para,
            "source": "UE5_Detail.md",
            "category": "interview_one_liner"
        })
    return records

def extract_quiz_from_html(html_path, module_name):
    """Extract quiz questions from HTML into SFT records."""
    text = read_file(html_path)
    records = []
    eval_items = []

    # Extract single-choice questions
    for m in re.finditer(
        r"question:\s*\"(.*?)\".*?correct:\s*(\d+).*?explanation:\s*\"(.*?)\"",
        text, re.DOTALL
    ):
        q, correct_idx, expl = m.group(1), m.group(2), m.group(3)
        # Clean up escaped quotes
        q = q.replace('\\"', '"')
        expl = expl.replace('\\"', '"')
        instruction = f"UE5 {module_name} 面试题：{q}"
        records.append({
            "instruction": instruction,
            "input": "",
            "output": expl,
            "source": f"html/{module_name}",
            "category": "interview_single_choice"
        })
        eval_items.append({
            "question": q,
            "answer": expl,
            "module": module_name,
            "type": "single_choice"
        })

    # Extract multi-choice questions
    for m in re.finditer(
        r"question:\s*\"(.*?)\".*?correct:\s*\[([\d,\s]+)\].*?explanation:\s*\"(.*?)\"",
        text, re.DOTALL
    ):
        q, correct_indices, expl = m.group(1), m.group(2), m.group(3)
        q = q.replace('\\"', '"')
        expl = expl.replace('\\"', '"')
        instruction = f"UE5 {module_name} 面试题（多选）：{q}"
        records.append({
            "instruction": instruction,
            "input": "",
            "output": expl,
            "source": f"html/{module_name}",
            "category": "interview_multi_choice"
        })
        eval_items.append({
            "question": q,
            "answer": expl,
            "module": module_name,
            "type": "multi_choice"
        })

    # Extract true/false questions
    for m in re.finditer(
        r"statement:\s*\"(.*?)\".*?correct:\s*(true|false).*?explanation:\s*\"(.*?)\"",
        text, re.DOTALL
    ):
        stmt, correct, expl = m.group(1), m.group(2), m.group(3)
        stmt = stmt.replace('\\"', '"')
        expl = expl.replace('\\"', '"')
        instruction = f"判断正误：{stmt}"
        records.append({
            "instruction": instruction,
            "input": "",
            "output": expl,
            "source": f"html/{module_name}",
            "category": "interview_true_false"
        })
        eval_items.append({
            "question": stmt,
            "answer": expl,
            "module": module_name,
            "type": "true_false"
        })

    # Extract drag questions (fill-in-the-blank)
    for m in re.finditer(
        r"sentence:\s*\"(.*?)\".*?explanation:\s*\"(.*?)\"",
        text, re.DOTALL
    ):
        sentence, expl = m.group(1), m.group(2)
        sentence = sentence.replace('\\"', '"')
        expl = expl.replace('\\"', '"')
        if "____" in sentence:
            instruction = f"填空：{sentence}"
            records.append({
                "instruction": instruction,
                "input": "",
                "output": expl,
                "source": f"html/{module_name}",
                "category": "interview_fill_blank"
            })

    return records, eval_items

def extract_code_pairs(md_text):
    """Extract code snippets with surrounding text as code-text pairs."""
    records = []
    # Find code blocks with preceding text
    pattern = r"(.*?)(?:```cpp\n(.*?)```)"
    for m in re.finditer(pattern, md_text, re.DOTALL):
        context, code = m.group(1).strip(), m.group(2).strip()
        if not code or len(code) < 20:
            continue
        # Clean context
        context = " ".join(context.split())
        if len(context) > 500:
            context = context[:500]
        instruction = f"解释以下 UE5 源码片段的作用和上下文：\n```cpp\n{code}\n```"
        output = context if context else "该代码片段属于 UE5 渲染引擎源码。"
        records.append({
            "instruction": instruction,
            "input": "",
            "output": output,
            "source": "UE5_Detail.md",
            "category": "code_explanation"
        })
    return records

def extract_conversation_chains(html_path, module_name):
    """Extract follow-up chains as multi-turn conversation data."""
    text = read_file(html_path)
    records = []
    # Match questions that have followup arrays
    for m in re.finditer(
        r"question:\s*\"(.*?)\".*?explanation:\s*\"(.*?)\".*?followup:\s*\[(.*?)\]",
        text, re.DOTALL
    ):
        q, expl, followups_raw = m.group(1), m.group(2), m.group(3)
        q = q.replace('\\"', '"')
        expl = expl.replace('\\"', '"')
        # Extract individual followup strings
        followups = re.findall(r'"([^"]*)"', followups_raw)
        if not followups:
            continue

        conversation = []
        conversation.append({"role": "user", "content": f"面试官问：{q}"})
        conversation.append({"role": "assistant", "content": expl})

        for i, fu in enumerate(followups):
            fu = fu.replace('\\"', '"')
            # Generate a synthetic answer for followup
            # Use the followup text itself as the next question
            conversation.append({"role": "user", "content": fu})
            # For the last followup, generate a simple answer
            if i == len(followups) - 1:
                conversation.append({"role": "assistant", "content": f"基于上述分析，{fu.split('→')[0].strip()} 的答案是肯定的。这涉及到 UE5 {module_name} 模块的深层实现细节。"})
            else:
                conversation.append({"role": "assistant", "content": f"这正是 {module_name} 的核心设计考量。让我详细展开..."})

        records.append({
            "conversation": conversation,
            "source": f"html/{module_name}",
            "category": "interview_conversation"
        })
    return records

def build_dataset():
    ensure_dirs()

    all_records = []
    all_eval = []
    all_conversations = []
    all_code = []

    # 1. From UE5_Detail.md
    detail_text = read_file(UE5_DIR / "UE5_Detail.md")
    sections = extract_sections_from_md(detail_text)
    doc_records = build_doc_qa(sections)
    all_records.extend(doc_records)
    code_records = extract_code_pairs(detail_text)
    all_code.extend(code_records)
    print(f"  UE5_Detail.md: {len(doc_records)} Q&A + {len(code_records)} code pairs")

    # 2. From HTML quiz cards
    html_files = {
        "nanite": HTML_DIR / "nanite" / "index.html",
        "lumen": HTML_DIR / "lumen" / "index.html",
        "vsm": HTML_DIR / "vsm" / "index.html",
        "ue5-detail": HTML_DIR / "ue5-detail" / "index.html",
    }
    for module, path in html_files.items():
        if not path.exists():
            print(f"  WARN: {path} not found, skipping")
            continue
        quiz_records, eval_items = extract_quiz_from_html(path, module)
        all_records.extend(quiz_records)
        all_eval.extend(eval_items)
        conv_records = extract_conversation_chains(path, module)
        all_conversations.extend(conv_records)
        print(f"  {module}: {len(quiz_records)} quiz + {len(eval_items)} eval + {len(conv_records)} conversations")

    # 3. From timlly notes (conceptual Q&A)
    for note_file in ["UE5_Nanite_timlly.md", "UE5_Lumen_timlly.md"]:
        note_path = UE5_DIR / note_file
        if note_path.exists():
            note_text = read_file(note_path)
            note_sections = extract_sections_from_md(note_text)
            note_records = build_doc_qa(note_sections)
            all_records.extend(note_records)
            print(f"  {note_file}: {len(note_records)} Q&A")

    # Write outputs
    # Main SFT dataset
    sft_path = DATA_DIR / "ue5_sft.jsonl"
    with open(sft_path, "w", encoding="utf-8") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\n📦 Written {len(all_records)} records to {sft_path}")

    # Code pairs
    code_path = DATA_DIR / "ue5_code.jsonl"
    with open(code_path, "w", encoding="utf-8") as f:
        for r in all_code:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"📦 Written {len(all_code)} code pairs to {code_path}")

    # Conversations
    conv_path = DATA_DIR / "ue5_conversation.jsonl"
    with open(conv_path, "w", encoding="utf-8") as f:
        for r in all_conversations:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"📦 Written {len(all_conversations)} conversations to {conv_path}")

    # Benchmark
    eval_path = BENCHMARK_DIR / "ue5_eval.jsonl"
    with open(eval_path, "w", encoding="utf-8") as f:
        for r in all_eval:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"📦 Written {len(all_eval)} eval items to {eval_path}")

    # Stats
    categories = {}
    for r in all_records:
        cat = r.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    print(f"\n📊 Dataset stats:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")
    print(f"   Total SFT records: {len(all_records)}")
    print(f"   Total eval items: {len(all_eval)}")
    print(f"   Total code pairs: {len(all_code)}")
    print(f"   Total conversations: {len(all_conversations)}")

if __name__ == "__main__":
    build_dataset()
    print("\n✅ Dataset build complete!")
