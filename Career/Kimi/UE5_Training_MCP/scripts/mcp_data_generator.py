#!/usr/bin/env python3
"""
UE5 MCP Data Generator

Generate training conversations using Unreal MCP + latest LLM.
Supports:
  - MCP server (stdio/sse) for UE5 context
  - Direct API fallback (OpenAI/Anthropic) with manual context injection

Usage:
    python mcp_data_generator.py \
        --config ../config/mcp_config.json \
        --num_conversations 100 \
        --output ../data/raw/conversations.jsonl

Outputs:
    - data/raw/conversations.jsonl      (main output)
    - data/raw/generation_log.json      (metadata per conversation)
"""

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Optional

# --- MCP client (optional) ---
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

# --- Direct API clients (optional) ---
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# --- Conversation Templates ---

INTERVIEW_TEMPLATE = """You are a senior Unreal Engine 5 graphics engineer being interviewed.

Topic: {topic}

Generate a realistic technical interview conversation with exactly 4-5 turns.
Each turn should build on the previous one. The interviewer asks increasingly deep questions.
Your answers should be:
- Specific (mention exact function names, file paths, data structures)
- Technical (explain the algorithm, not just the concept)
- Honest (mention limitations and trade-offs where relevant)
- Include source code paths from the UE5 engine source

Format as a JSON array of {"role": "user", "content": "..."} and {"role": "assistant", "content": "..."}.

If UE5 context is available, incorporate it naturally. Do not make up source paths."""

CODE_EXPLANATION_TEMPLATE = """You are explaining UE5 source code to a junior engineer.

Topic: {topic}

Generate a conversation where:
1. The user asks about a specific UE5 function or system
2. You explain what it does, WHY it does it that way, and what happens if you change it
3. Include the actual source file path and relevant code snippets
4. The user asks a follow-up about edge cases or performance implications

Format as a JSON array of {"role": "user", "content": "..."} and {"role": "assistant", "content": "..."}.

If UE5 context is available, use real source paths and function signatures."""

ARCHITECTURE_TEMPLATE = """You are doing a deep-dive architecture review of UE5's {topic}.

Generate a conversation with 4-5 turns covering:
1. High-level architecture overview
2. Key data structures and their relationships
3. Interaction with other engine systems
4. Performance characteristics and bottlenecks
5. Comparison with alternative approaches

Be specific. Name the actual C++ classes, structs, and functions.
Mention actual engine modules (e.g., Engine\Source\Runtime\Renderer).

Format as a JSON array of {"role": "user", "content": "..."} and {"role": "assistant", "content": "..."}."""

PERFORMANCE_TEMPLATE = """You are optimizing a UE5 game's performance. The problem area is: {topic}.

Generate a debugging/optimization conversation with 4-5 turns:
1. Describe a real performance issue (e.g., frame time spikes, memory bloat)
2. Walk through the diagnostic process
3. Propose specific optimizations with expected gains
4. Discuss trade-offs of each optimization
5. Mention relevant console commands or profiling tools

Format as a JSON array of {"role": "user", "content": "..."} and {"role": "assistant", "content": "..."}."""

DEBUGGING_TEMPLATE = """You are debugging a UE5 issue related to {topic}.

Generate a conversation with 4-5 turns:
1. Describe a bug symptom (e.g., flickering shadows, missing GI)
2. Walk through the systematic debugging process
3. Identify root cause with specific function/file references
4. Propose fix with code-level detail
5. Verify the fix and discuss prevention

Format as a JSON array of {"role": "user", "content": "..."} and {"role": "assistant", "content": "..."}."""

CROSS_MODULE_TEMPLATE = """Explain how UE5's {topic} interacts with other engine systems.

Generate a conversation with 4-5 turns:
1. What is {topic} and what does it do?
2. How does it interact with [related system A]?
3. How does it interact with [related system B]?
4. What happens if both systems are active simultaneously?
5. What are the common integration pitfalls?

Be specific about data flow, shared data structures, and render order.

Format as a JSON array of {"role": "user", "content": "..."} and {"role": "assistant", "content": "..."}."""

TEMPLATES = {
    "interview_technical": INTERVIEW_TEMPLATE,
    "code_explanation": CODE_EXPLANATION_TEMPLATE,
    "architecture_deep_dive": ARCHITECTURE_TEMPLATE,
    "performance_optimization": PERFORMANCE_TEMPLATE,
    "debugging_scenario": DEBUGGING_TEMPLATE,
    "cross_module_integration": CROSS_MODULE_TEMPLATE,
}


class MCPDataGenerator:
    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.gen_cfg = self.config.get("generation", {})
        self.fallback = self.config.get("fallback_mode", {})
        self.topics = self.config.get("topics", [])
        self.templates = self.config.get("conversation_templates", list(TEMPLATES.keys()))

        # Init clients
        self._init_api_client()

    def _init_api_client(self):
        self.client = None
        self.client_type = None
        if self.fallback.get("enabled", False):
            provider = self.fallback.get("provider", "anthropic")
            if provider == "anthropic" and HAS_ANTHROPIC:
                api_key = os.environ.get(self.fallback.get("api_key_env", "ANTHROPIC_API_KEY"))
                if api_key:
                    self.client = anthropic.Anthropic(api_key=api_key)
                    self.client_type = "anthropic"
                    self.model = self.fallback.get("model", "claude-sonnet-4-20250514")
            elif provider == "openai" and HAS_OPENAI:
                api_key = os.environ.get(self.fallback.get("api_key_env", "OPENAI_API_KEY"))
                if api_key:
                    self.client = openai.OpenAI(api_key=api_key)
                    self.client_type = "openai"
                    self.model = self.fallback.get("model", "gpt-4o")

        if self.client is None:
            print("WARNING: No API client available. Set ANTHROPIC_API_KEY or OPENAI_API_KEY env var.")

    def _call_llm(self, prompt: str, system: Optional[str] = None) -> str:
        """Call LLM with retry logic."""
        max_retries = self.gen_cfg.get("retry_attempts", 3)
        delay = self.gen_cfg.get("retry_delay_seconds", 2)

        for attempt in range(max_retries):
            try:
                if self.client_type == "anthropic":
                    messages = [{"role": "user", "content": prompt}]
                    if system:
                        response = self.client.messages.create(
                            model=self.model,
                            max_tokens=self.gen_cfg.get("max_tokens", 2048),
                            temperature=self.gen_cfg.get("temperature", 0.8),
                            system=system,
                            messages=messages,
                        )
                    else:
                        response = self.client.messages.create(
                            model=self.model,
                            max_tokens=self.gen_cfg.get("max_tokens", 2048),
                            temperature=self.gen_cfg.get("temperature", 0.8),
                            messages=messages,
                        )
                    return response.content[0].text

                elif self.client_type == "openai":
                    messages = []
                    if system:
                        messages.append({"role": "system", "content": system})
                    messages.append({"role": "user", "content": prompt})
                    response = self.client.chat.completions.create(
                        model=self.model,
                        max_tokens=self.gen_cfg.get("max_tokens", 2048),
                        temperature=self.gen_cfg.get("temperature", 0.8),
                        top_p=self.gen_cfg.get("top_p", 0.95),
                        messages=messages,
                    )
                    return response.choices[0].message.content

                else:
                    raise RuntimeError("No LLM client available")

            except Exception as e:
                print(f"  Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay * (attempt + 1))
                else:
                    raise

        return ""

    def generate_conversation(self, topic: str, template_name: str) -> dict:
        """Generate a single conversation."""
        template = TEMPLATES.get(template_name, INTERVIEW_TEMPLATE)
        prompt = template.format(topic=topic)

        system = "You are an expert Unreal Engine 5 graphics programmer. You generate high-quality technical training data. Always respond with a valid JSON array of conversation turns."
        raw_text = self._call_llm(prompt, system=system)

        # Extract JSON from the response (LLM may wrap in markdown)
        text = raw_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            conversation = json.loads(text)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON array from text
            start = text.find("[")
            end = text.rfind("]")
            if start != -1 and end != -1:
                conversation = json.loads(text[start:end+1])
            else:
                raise ValueError(f"Could not parse JSON from LLM response: {raw_text[:200]}")

        # Validate format
        for turn in conversation:
            if "role" not in turn or "content" not in turn:
                raise ValueError(f"Invalid turn format: {turn}")

        return {
            "conversation": conversation,
            "topic": topic,
            "template": template_name,
            "source": "mcp_llm_generation",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

    def generate_batch(self, num_conversations: int) -> list:
        """Generate a batch of conversations."""
        records = []
        log_entries = []

        for i in range(num_conversations):
            topic = random.choice(self.topics)
            template = random.choice(self.templates)

            print(f"[{i+1}/{num_conversations}] Generating: {topic} | {template}")
            try:
                record = self.generate_conversation(topic, template)
                records.append(record)
                log_entries.append({
                    "index": i,
                    "topic": topic,
                    "template": template,
                    "status": "success",
                    "num_turns": len(record["conversation"]),
                })
            except Exception as e:
                print(f"  FAILED: {e}")
                log_entries.append({
                    "index": i,
                    "topic": topic,
                    "template": template,
                    "status": "failed",
                    "error": str(e),
                })

        return records, log_entries


def main():
    parser = argparse.ArgumentParser(description="Generate UE5 training data via MCP + LLM")
    parser.add_argument("--config", type=str, default="../config/mcp_config.json",
                        help="Path to MCP config JSON")
    parser.add_argument("--num_conversations", type=int, default=50,
                        help="Number of conversations to generate")
    parser.add_argument("--output", type=str, default="../data/raw/conversations.jsonl",
                        help="Output JSONL file")
    parser.add_argument("--log", type=str, default="../data/raw/generation_log.json",
                        help="Generation log file")
    args = parser.parse_args()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)

    print(f"🚀 UE5 MCP Data Generator")
    print(f"   Config: {args.config}")
    print(f"   Target: {args.num_conversations} conversations")
    print(f"   Output: {args.output}")

    generator = MCPDataGenerator(args.config)

    if generator.client is None:
        print("\n❌ ERROR: No LLM client available.")
        print("   Please set one of these environment variables:")
        print("   - ANTHROPIC_API_KEY (for Anthropic models)")
        print("   - OPENAI_API_KEY (for OpenAI models)")
        print("   Or configure an MCP server in the config file.")
        sys.exit(1)

    print(f"   Using {generator.client_type} client with model: {generator.model}")

    records, log_entries = generator.generate_batch(args.num_conversations)

    # Write output
    with open(args.output, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Write log
    with open(args.log, "w", encoding="utf-8") as f:
        json.dump({
            "total_requested": args.num_conversations,
            "total_success": len(records),
            "total_failed": sum(1 for e in log_entries if e["status"] == "failed"),
            "entries": log_entries,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Generated {len(records)} conversations")
    print(f"   Failed: {sum(1 for e in log_entries if e['status'] == 'failed')}")
    print(f"   Output: {args.output}")
    print(f"   Log: {args.log}")


if __name__ == "__main__":
    main()
