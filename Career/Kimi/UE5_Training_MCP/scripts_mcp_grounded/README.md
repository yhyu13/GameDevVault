# UE5 MCP-Grounded Training Data Pipeline (v2)

> Generates SFT data for a small (1.5B–3B) model that can drive an Unreal
> Editor session via MCP. Every example is grounded in live editor state
> and self-verified. See [DESIGN.md](DESIGN.md) for the design rationale.

## What this replaces

The v1 `scripts/mcp_data_generator.py` in the parent directory calls an
external LLM API and never actually invokes the MCP server. v2 fixes both:
the teacher is the in-session model, the MCP server is driven for real, and
the data is grounded in observable editor state.

The v1 scripts (`mcp_data_generator.py`, `data_prep.py`, `data_pruner.py`,
`train_small_model.py`, `eval_model.py`) are not modified.

## File layout

| File | Purpose |
|---|---|
| `DESIGN.md` | Design document, all 5 decisions locked in §11 |
| `context_fetcher.py` | JSON-RPC client + 12 high-level tool wrappers + safety allow-list |
| `topic_catalog.json` | 4 data types × topic seeds |
| `self_verifier.py` | Mechanical claim check (re-query MCP) + judgment hook |
| `format_adapter.py` | Flattens v2 tool turns → user/assistant for `data_prep.py` |
| `data_pruner_v2.py` | Two-tier pruner (v1 rendering facts + v2 MCP facts) |
| `run_pilot.py` | Orchestrator: `ingest` / `fetch` / `report` subcommands |
| `README.md` | This file |

## Latency caveat (read first)

The live MCP server at `http://127.0.0.1:8000/mcp` takes **~15 seconds per
tool call** in our observed runs (Lvl_IntroRoom, 391 actors). This is
server-side, not a client bug. Implications:

- A pilot of 10 examples with 2-3 MCP calls each = **5-7 minutes of pure
  waiting** + generation overhead.
- A realistic in-session pilot target is **10-15 examples**, not 20-25.
- For larger corpora, run multiple sessions and append.

The fetcher uses `http.client` (not `urllib.request`) with a 60-second
timeout and reads the SSE body in chunks because the server sets
`Content-Length: 0` and then streams the actual body. `urllib` honors
Content-Length: 0 and bails out — we work around it.

## Quick start

### 1. Generate one example (interactive in-session)

The pilot is driven by a human or LLM (this session) using the modules
directly. The `run_pilot.py fetch` subcommand helps gather grounding:

```bash
python run_pilot.py fetch --data_type tool_use --topic "Inventorying actors by class"
```

The output is a JSON document with the live MCP state for that data type.
Use it as the grounding context for the example you then write.

### 2. Ingest a batch of examples

When you have a JSONL of v2 examples (one per line, format per
DESIGN.md §4), verify and persist them:

```bash
python run_pilot.py ingest --in raw_examples.jsonl --out data/raw/pilot_verified.jsonl
```

Verified examples have `verified: true` plus a `verification` block with
per-claim pass/fail counts. Rejected examples go to
`pilot_verified.failures.json` for inspection.

### 3. Adapt to v1 format and prune

```bash
python format_adapter.py --in data/raw/pilot_verified.jsonl --out data/raw/pilot_v1.jsonl
python run_pilot.py report --in data/raw/pilot_v1.jsonl --out data/processed/pilot_pruned.jsonl
```

The adapted JSONL is consumable by `scripts/data_prep.py` without
modification. The pruner is v2-aware (two-tier factuality catalog).

### 4. Train

```bash
python ../scripts/train_small_model.py \
  --model_name Qwen/Qwen2.5-Coder-3B-Instruct \
  --dataset ../data/splits/train.jsonl \
  --eval_dataset ../data/splits/val.jsonl \
  --output_dir ../outputs/models/qwen-3b-ue5-mcp
```

(Use the standard upstream pipeline; nothing v2-specific here.)

## Safety policy

`execute_console_command` is allow-listed. See
[DESIGN.md §11 decision 2](DESIGN.md#11-decisions-confirmed) for the full
table of allowed and blocked prefixes. Cvars that are runtime overrides
(`r.MaterialQualityLevel`, `r.ViewDistanceScale`) are auto-restored after
the call. The safety policy is enforced in `context_fetcher.py` and
re-checked by the verifier.

## Output format (v2)

Each line of the output JSONL is a record (see DESIGN.md §4):

```json
{
  "id": "pilot_2026-06-28_001",
  "data_type": "tool_use",
  "topic": "Inventorying actors by class",
  "conversation": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "...", "tool_calls": [{"name": "ListActors", "arguments": {}}]},
    {"role": "tool", "name": "ListActors", "content": "[{...}]"},
    {"role": "assistant", "content": "..."}
  ],
  "source": "mcp_grounded_v2",
  "mcp_grounded": true,
  "verified": true,
  "verification": {"claims_checked": 7, "claims_passed": 7, "claims_failed": 0, ...},
  "grounding_provenance": {"mcp_calls": [...], "scene_snapshot": {...}},
  "license": {"engine_refs": [], "project_refs": ["BP_FirstPersonCharacter_C_0"]},
  "timestamp": "2026-06-28T..."
}
```

The `format_adapter.py` collapses `tool` turns to plain text for
consumption by v1 `data_prep.py`.

## Cross-run dedup

Set `--dedup_threshold 0.7` (default) to drop near-duplicates via Jaccard
similarity on word sets. The threshold is lower than v1's 0.85 because v2
conversations share substantial MCP-derived vocabulary from the same scene
and would false-positive at 0.85.

## Per-example license

Each example carries a `license: {engine_refs, project_refs}` block for
future data audit. The pilot doesn't auto-populate this yet; it's a
placeholder for downstream tooling.

## Re-running

To grow the corpus:

1. Re-run `run_pilot.py ingest` against an accumulating `data/raw/pilot_*.jsonl`
2. The pruner dedups against the union of all prior examples
3. Repeat until you hit your target size (5,000+ for a useful SFT set)

To swap topics: edit `topic_catalog.json`. To add a new data type: extend
`DEFAULT_GROUNDING` in `run_pilot.py` and add a new branch in
`self_verifier.py`'s claim extraction.

## Known limitations

- **Latency**: 15s/tool call. Plan accordingly.
- **Tool set**: 12 top-level + 6 toolset tools. No Blueprint editing, no
  PIE control, no Python in Editor. If you need more, add a toolset plugin
  to `IntroToUE.uproject`.
- **Claim extraction**: regex-based. Misses claims phrased in unusual
  ways (e.g., the model says "the character actor" without naming it).
  Acceptable for v2; a v3 could use an LLM-based extractor.
- **No ground-truth for engine source paths**: claims like
  `Engine/Source/Runtime/...` are flagged as `unverifiable` rather than
  `pass` / `fail`, because the MCP server doesn't expose the filesystem.

## License of generated data

Each record carries a `license` field. Fill it in per your data policy.
For UE engine internals, respect the Unreal Engine EULA. For project
content (Blueprints, levels, configs), respect your project's IP. The
pilot does not auto-detect or enforce this.
