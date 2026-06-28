#!/usr/bin/env python3
"""
Format adapter (v2 -> v1).

Reads a v2 MCP-grounded JSONL (with tool turns) and rewrites each example
into a v1-compatible JSONL (plain user/assistant turns) that the existing
scripts/data_prep.py can consume without modification, per DESIGN.md §8.1.

Two flattening strategies:

  1. "summary"   : collapse each tool_use cluster into a single assistant
                    turn that describes the tool call, its result, and the
                    reasoning. Loses some structural info but keeps
                    everything human-readable.
  2. "trace"     : keep user/assistant turns but render tool calls and
                    results as plain-text content within the assistant
                    turn. Preserves the full sequence.

Default is "summary". Pass --mode trace for the other behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Force UTF-8 stdout/stderr on Windows where the default is GBK.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def flatten_to_summary(conversation: list[dict]) -> list[dict]:
    """Walk the conversation, merging each tool-use cluster into one
    assistant turn whose content is a human-readable narrative."""
    out: list[dict] = []
    pending_tool: list[dict] = []  # tool calls awaiting observation
    pending_results: list[tuple[str, str]] = []  # (tool_name, content)

    for turn in conversation:
        role = turn.get("role", "")
        content = turn.get("content", "")

        if role == "user":
            # If we have pending tool stuff, flush as a synthesized assistant
            # turn before the next user turn.
            if pending_tool or pending_results:
                out.append(_synthesize_assistant(pending_tool, pending_results))
                pending_tool, pending_results = [], []
            out.append({"role": "user", "content": content})

        elif role == "assistant":
            tcs = turn.get("tool_calls") or []
            if tcs:
                # Queue the tool calls; the next tool turn(s) provide results.
                pending_tool.extend(tcs)
                # If the assistant also had prose, keep it as a "lead-in".
                if content:
                    pending_tool[-1]["_lead_in"] = content
            else:
                # Plain assistant turn.
                if pending_tool or pending_results:
                    out.append(_synthesize_assistant(pending_tool, pending_results))
                    pending_tool, pending_results = [], []
                out.append({"role": "assistant", "content": content})

        elif role == "tool":
            name = turn.get("name", "?")
            result = turn.get("content", "")
            pending_results.append((name, result))

    # Flush any trailing tool cluster.
    if pending_tool or pending_results:
        out.append(_synthesize_assistant(pending_tool, pending_results))

    return out


def _synthesize_assistant(
    tool_calls: list[dict], results: list[tuple[str, str]]
) -> dict:
    """Render a tool-use cluster as one assistant turn."""
    parts: list[str] = []
    lead_in = ""
    if tool_calls:
        last = tool_calls[-1]
        if isinstance(last, dict):
            lead_in = last.pop("_lead_in", "")
        # Defensive: lead_in should be a string; coerce lists / other types.
        if not isinstance(lead_in, str):
            lead_in = "" if not lead_in else str(lead_in)
        parts.append(lead_in.strip() if lead_in else "")
        parts.append("Tool calls:")
        for tc in tool_calls:
            name = tc.get("name", "?")
            args = tc.get("arguments", {}) or {}
            if isinstance(args, dict):
                arg_str = ", ".join(f"{k}={json.dumps(v)[:80]}" for k, v in args.items())
            else:
                arg_str = str(args)[:80]
            parts.append(f"  - {name}({arg_str})")
    if results:
        parts.append("Results:")
        for name, content in results:
            if not isinstance(content, str):
                content = str(content)
            snippet = content if len(content) <= 240 else content[:240] + "..."
            parts.append(f"  - {name} returned: {snippet}")
    return {
        "role": "assistant",
        "content": "\n".join(p for p in parts if p).strip(),
    }


def flatten_to_trace(conversation: list[dict]) -> list[dict]:
    """Same as summary but tool calls / results are embedded as plain-text
    inside an assistant turn rather than collapsed. Preserves the full
    tool-use sequence in one assistant message per cluster."""
    out: list[dict] = []
    pending_tool: list[dict] = []
    pending_results: list[tuple[str, str]] = []
    pending_lead: Optional[str] = None

    def flush():
        nonlocal pending_tool, pending_results, pending_lead
        if not (pending_tool or pending_results or pending_lead):
            return
        parts: list[str] = []
        if pending_lead:
            parts.append(pending_lead)
        for tc in pending_tool:
            name = tc.get("name", "?")
            args = tc.get("arguments", {}) or {}
            parts.append(f"[Tool call: {name} {json.dumps(args)}]")
        for name, content in pending_results:
            snippet = content if len(content) <= 400 else content[:400] + "..."
            parts.append(f"[Tool result: {name}] {snippet}")
        out.append({"role": "assistant", "content": "\n".join(parts).strip()})
        pending_tool, pending_results, pending_lead = [], [], None

    for turn in conversation:
        role = turn.get("role", "")
        content = turn.get("content", "")
        if role == "user":
            flush()
            out.append({"role": "user", "content": content})
        elif role == "assistant":
            tcs = turn.get("tool_calls") or []
            if tcs:
                pending_tool.extend(tcs)
                if content:
                    pending_lead = (pending_lead or "") + content
            else:
                flush()
                out.append({"role": "assistant", "content": content})
        elif role == "tool":
            name = turn.get("name", "?")
            pending_results.append((name, turn.get("content", "")))
    flush()
    return out


def adapt_record(record: dict, mode: str = "summary") -> dict:
    conv = record.get("conversation", [])
    if mode == "summary":
        new_conv = flatten_to_summary(conv)
    elif mode == "trace":
        new_conv = flatten_to_trace(conv)
    else:
        raise ValueError(f"Unknown mode: {mode!r}")
    out = dict(record)
    out["conversation"] = new_conv
    out["source"] = "mcp_grounded_v2_" + mode
    return out


def main():
    parser = argparse.ArgumentParser(description="Adapt v2 JSONL to v1-compatible format")
    parser.add_argument("--input", required=True, help="v2 JSONL input path")
    parser.add_argument("--output", required=True, help="adapted JSONL output path")
    parser.add_argument(
        "--mode", choices=("summary", "trace"), default="summary",
        help="Flattening strategy (default: summary)",
    )
    args = parser.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    n_in = 0
    n_out = 0
    with open(args.input, "r", encoding="utf-8") as fi, \
         open(args.output, "w", encoding="utf-8") as fo:
        for line in fi:
            line = line.strip()
            if not line:
                continue
            n_in += 1
            r = json.loads(line)
            r2 = adapt_record(r, mode=args.mode)
            fo.write(json.dumps(r2, ensure_ascii=False) + "\n")
            n_out += 1
    print(f"[OK] Adapted {n_out}/{n_in} records ({args.mode} mode) -> {args.output}")


if __name__ == "__main__":
    main()
