#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool-calling adapter: convert v2 format (with tool_calls and tool turns)
to OpenAI Chat Completions function-calling training format.

This is the format the small model actually needs to learn:
  - emit structured `tool_calls` JSON, not text that mentions tools
  - the trainer (TRL SFTTrainer, axolotl, llamafactory, OpenAI's fine-tuning
    API, vLLM, etc.) reads this format and trains the model to output
    `tool_calls` rather than text

Output: a JSONL where each line has the OpenAI messages format + a top-level
`tools` field listing the function definitions.

Usage:
    python tool_calling_adapter.py \
        --in  ../data/processed/corpus_200_pruned.jsonl \
        --out ../data/splits/train_tool_calls.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# MCP tool schemas. These are the actual inputSchema values from the live
# server, so the model learns the real tool surface.
MCP_TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "ListActors",
        "description": "List all actors in the current editor level. Returns an array of {name, class, location}.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "GetActorDetails",
        "description": "Get detailed information (transform, selection state) about a specific actor by name.",
        "parameters": {
            "type": "object",
            "properties": {
                "actorName": {"type": "string", "description": "The exact actor name, e.g. 'StaticMeshActor_UAID_F4A475FF15A34D8902_2073097800'"}
            },
            "required": ["actorName"],
        },
    }},
    {"type": "function", "function": {
        "name": "SetActorTransform",
        "description": "Set the transform of an actor by name.",
        "parameters": {
            "type": "object",
            "properties": {
                "actorName": {"type": "string", "description": "The actor name"}
            },
            "required": ["actorName"],
        },
    }},
    {"type": "function", "function": {
        "name": "SpawnActor",
        "description": "Spawn a new actor of the given UClass.",
        "parameters": {
            "type": "object",
            "properties": {
                "className": {"type": "string", "description": "The UClass name, e.g. 'StaticMeshActor'"}
            },
            "required": ["className"],
        },
    }},
    {"type": "function", "function": {
        "name": "DeleteActor",
        "description": "Delete an actor by name from the current level.",
        "parameters": {
            "type": "object",
            "properties": {
                "actorName": {"type": "string", "description": "The actor name"}
            },
            "required": ["actorName"],
        },
    }},
    {"type": "function", "function": {
        "name": "execute_console_command",
        "description": "Execute a console command in the editor (allow-listed prefixes only: stat, show, r.ScreenPercentage, r.Lumen, r.Shadow, r.AmbientOcclusion, ke, obj list, Dump, MemReport, etc.).",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The console command, e.g. 'stat fps', 'show collision', 'obj list class=Light'"}
            },
            "required": ["command"],
        },
    }},
    {"type": "function", "function": {
        "name": "capture_viewport",
        "description": "Capture the current editor viewport as a base64 PNG.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "save_current_level",
        "description": "Save the current level to disk.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "get_editor_context",
        "description": "Query current editor state (level name, world type, actor count, PIE state, selected actors).",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "list_toolsets",
        "description": "List all MCP toolsets registered with the server.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "describe_toolset",
        "description": "Get the full schema of a toolset (version, description, tool list with input schemas).",
        "parameters": {
            "type": "object",
            "properties": {
                "toolset_name": {"type": "string", "description": "The toolset name, e.g. 'AIAssistant.AIAssistantToolset'"}
            },
            "required": ["toolset_name"],
        },
    }},
    {"type": "function", "function": {
        "name": "call_tool",
        "description": "Call a tool that lives inside a named toolset. Use list_toolsets / describe_toolset first.",
        "parameters": {
            "type": "object",
            "properties": {
                "toolset_name": {"type": "string", "description": "The toolset name (optional)"},
                "tool_name": {"type": "string", "description": "The tool name within the toolset (optional)"},
                "arguments": {"type": "object", "description": "Arguments to pass to the tool (optional)"},
            },
        },
    }},
]


def gen_tool_call_id() -> str:
    return f"call_{uuid.uuid4().hex[:24]}"


def adapt_record(record: dict) -> dict | None:
    """Convert one v2 record to OpenAI Chat Completions format.

    The v2 record's `conversation` is a list of turns with roles
    {user, assistant, tool} and optional `tool_calls` (on assistant) and
    `name` + `content` (on tool). We:
      - drop any assistant turn that has neither content nor tool_calls
      - convert assistant+tool_calls to the OpenAI `tool_calls` format
      - convert tool turns to OpenAI `tool` role with `tool_call_id`
      - drop the `name` field (OpenAI uses `tool_call_id` instead)
    """
    messages = []
    pending_call_id = None  # the most recent assistant tool_call.id

    for turn in record.get("conversation", []):
        role = turn.get("role")
        content = turn.get("content", "")
        tool_calls = turn.get("tool_calls") or []

        if role == "user":
            messages.append({"role": "user", "content": content})
        elif role == "assistant":
            msg = {"role": "assistant"}
            if content:
                msg["content"] = content
            else:
                msg["content"] = None
            if tool_calls:
                openai_calls = []
                for tc in tool_calls:
                    name = tc.get("name", "")
                    args = tc.get("arguments", {}) or {}
                    call_id = gen_tool_call_id()
                    openai_calls.append({
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "name": name,
                            "arguments": json.dumps(args, ensure_ascii=False),
                        },
                    })
                    # If there's a single tool call, remember its id so the
                    # next tool turn can be linked.
                    if len(tool_calls) == 1:
                        pending_call_id = call_id
                msg["tool_calls"] = openai_calls
            messages.append(msg)
        elif role == "tool":
            # Link this tool result to the most recent assistant tool_call.
            # If multiple tool calls were issued in the prior turn, link
            # to the first one (a simplification; OpenAI supports 1:1).
            messages.append({
                "role": "tool",
                "tool_call_id": pending_call_id or gen_tool_call_id(),
                "content": content or "",
            })
            pending_call_id = None
        # ignore other roles

    if not messages:
        return None
    # Ensure the conversation starts with a user turn
    if messages[0].get("role") != "user":
        return None
    # Ensure there's at least one assistant turn
    if not any(m.get("role") == "assistant" for m in messages):
        return None

    return {
        "messages": messages,
        "tools": MCP_TOOL_SCHEMAS,
    }


def main():
    parser = argparse.ArgumentParser(description="v2 -> OpenAI tool-calling format")
    parser.add_argument("--in", dest="input", required=True)
    parser.add_argument("--out", dest="output", required=True)
    args = parser.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    n_in, n_out = 0, 0
    n_with_tool_calls = 0
    with open(args.input, encoding="utf-8") as fi, \
         open(args.output, "w", encoding="utf-8") as fo:
        for line in fi:
            line = line.strip()
            if not line:
                continue
            n_in += 1
            r = json.loads(line)
            adapted = adapt_record(r)
            if adapted is None:
                continue
            fo.write(json.dumps(adapted, ensure_ascii=False) + "\n")
            n_out += 1
            if any("tool_calls" in m for m in adapted["messages"]):
                n_with_tool_calls += 1
    print(f"[OK] Adapted {n_out}/{n_in} records -> {args.output}")
    print(f"     with tool_calls: {n_with_tool_calls}/{n_out} ({n_with_tool_calls*100//max(n_out,1)}%)")
    print(f"     tools per example: {len(MCP_TOOL_SCHEMAS)} (always present)")


if __name__ == "__main__":
    main()
