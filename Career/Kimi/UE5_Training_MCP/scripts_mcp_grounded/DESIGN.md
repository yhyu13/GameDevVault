# UE5 MCP-Grounded Training Data Pipeline — Design (v2)

> **Status:** Design only, awaiting approval. No code written yet.
> **Author:** Claude (MiniMax-M3), via live MCP session on `IntroToUE.uproject`.
> **Replaces (does not modify):** `scripts/mcp_data_generator.py` (the existing v1 script).

---

## 1. Why a v2 (executive summary)

The existing v1 pipeline at `scripts/mcp_data_generator.py` has three structural problems for our setup:

1. **It calls an external LLM API** (Anthropic / OpenAI). We have a teacher LLM in-session (MiniMax-M3). External API = cost, latency, key management, no advantage.
2. **The MCP server block is decorative.** The `import mcp` exists, but `generate_conversation()` never invokes any MCP tool. The "MCP" name is aspirational; the data is LLM-from-prior-knowledge only.
3. **The topic catalog is wrong-shaped.** 20 topics are all rendering internals (Nanite, Lumen, VSM, TSR, GPUScene, etc.) that no MCP tool can observe. A 1.5B / 3B model trained on this learns to *hallucinate* UE5 source paths.

Additionally, the existing `scripts/data_pruner.py` would **filter out** the data we want to generate: its hardcoded `UE5_FACTS` catalog scores only on Nanite / Lumen / VSM / Render Graph source paths and keywords. Editor-/actor-/MCP-grounded examples would fail the factuality filter (score < 3) and be dropped.

**v2 fixes all three:** the teacher is the in-session model, the MCP server is actually driven, and the data is grounded in observable editor state. A v2 pruner replaces the fact catalog.

---

## 2. Goals & non-goals

### Goals
- Generate SFT data that teaches a small (1.5B–3B) model to be useful inside an Unreal Editor session driven by MCP.
- Every concrete claim (actor name, class, position, tool name, console output) is **verifiable** against the live MCP server at generation time.
- Output is a single JSONL file compatible with the existing `scripts/data_prep.py` (with a one-line wrapper), and with a v2 pruner for the new fact catalog.
- Re-runnable: the same code, run against a different `Lvl_*.umap` or different MCP state, produces a different but consistently-shaped dataset.

### Non-goals (this design)
- Training the model. (Owned by `scripts/train_small_model.py`, out of scope.)
- Evaluating the model. (Owned by `scripts/eval_model.py`, out of scope.)
- Generating 5,000+ examples in a single session. (Pilot target: 30–50 verified examples per session.)
- Replacing the v1 script. (v1 stays for reference; v2 lives alongside in `scripts_mcp_grounded/`.)

---

## 3. Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Live MCP server (port 8000)                  │
│  - get_editor_context, list_toolsets, describe_toolset           │
│  - ListActors, GetActorDetails, SetActorTransform,               │
│    SpawnActor, DeleteActor, execute_console_command,             │
│    capture_viewport, save_current_level                          │
│  - AIAssistant.AIAssistantToolset.{GetProjectContext,            │
│                                   GetDockedContext}              │
└──────────────────────────────────────────────────────────────────┘
                              ▲  JSON-RPC
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌────────────────┐    ┌────────────────┐
│ ContextFetcher│    │ SelfVerifier   │    │ ConsoleProbe   │
│  (queries MCP │    │  (re-queries   │    │  (runs safe    │
│   for ground  │    │   MCP, checks  │    │   stat/        │
│   truth)      │    │   claims)      │    │   show cmds)   │
└───────┬───────┘    └────────┬───────┘    └────────┬───────┘
        │                     │                     │
        ▼                     ▲                     │
┌───────────────┐             │                     │
│ Conversation  │             │                     │
│   Planner     │             │                     │
│ (picks type,  │             │                     │
│  angle, seed) │             │                     │
└───────┬───────┘             │                     │
        │                     │                     │
        ▼                     │                     │
┌───────────────┐             │                     │
│  Generator    │             │                     │
│  (MiniMax-M3) │─────────────┘                     │
│               │◄────────────────────────────────────┘
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  JSONL sink   │  →  data/raw/pilot_mcp_grounded.jsonl
│  (verified)   │  →  data/raw/pilot_generation_log.json
└───────────────┘
```

### Data flow per example

1. **Seed** — pick `data_type` ∈ {`concept_qa`, `tool_use`, `scene_understanding`, `console_diagnosis`} and a `topic`.
2. **Fetch context** — ContextFetcher pulls the relevant MCP state (actor list, tool inventory, project context, console probe results).
3. **Plan** — ConversationPlanner drafts the multi-turn structure (4–6 turns for `concept_qa`, 2–4 turns for `tool_use` with interspersed tool calls, etc.).
4. **Generate** — I produce the conversation, with the MCP state injected as concrete grounding.
5. **Verify** — SelfVerifier re-queries MCP, extracts concrete claims from my output (actor names, classes, positions, tool names, console outputs), and flags mismatches. Failed examples are repaired or dropped.
6. **Persist** — verified example appended to JSONL, with provenance (which MCP calls grounded it).

---

## 4. Output schema

Each line of `data/raw/pilot_mcp_grounded.jsonl` is a JSON object:

```json
{
  "id": "pilot_2026-06-28_001",
  "data_type": "tool_use",
  "topic": "actor inspection workflow",
  "conversation": [
    {"role": "user",      "content": "..."},
    {"role": "assistant", "content": "...",
     "tool_calls": [
       {"name": "ListActors", "arguments": {}}
     ]},
    {"role": "tool",      "name": "ListActors",
     "content": "[{\"name\":\"BP_FirstPersonCharacter_C_0\",\"class\":\"BP_FirstPersonCharacter_C\",...}]"},
    {"role": "assistant", "content": "..."}
  ],
  "source": "mcp_grounded_v2",
  "template": "tool_use_traces",
  "mcp_grounded": true,
  "verified": true,
  "verification": {
    "claims_checked": 7,
    "claims_passed": 7,
    "claims_failed": [],
    "tool_calls_issued": 3,
    "tool_calls_observed": 3
  },
  "grounding_provenance": {
    "mcp_calls": [
      {"tool": "ListActors",       "ts": "...", "ok": true},
      {"tool": "GetActorDetails",  "ts": "...", "ok": true},
      {"tool": "execute_console_command", "args": {"command": "show collision"}, "ok": true}
    ],
    "scene_snapshot": {
      "level": "Lvl_IntroRoom",
      "actor_count": 391,
      "is_pie": false
    }
  },
  "timestamp": "2026-06-28T..."
}
```

**Compatibility with existing `data_prep.py`:** the existing loader reads `record["conversation"]` and per-turn `role` / `content`. Tool calls and tool results use extra keys (`tool_calls`, `name`) that `data_prep.py` doesn't know about. **Two options:**

- **Option A (recommended, low-friction):** add a `format_adapter.py` that flattens tool turns to user/assistant-only before `data_prep.py` runs. Keeps the pruner/trainer untouched.
- **Option B:** extend `data_prep.py` with a `--format messages_with_tools` mode that emits a 3-message pattern (assistant tool_call → tool result → assistant follow-up) as two turns. Slightly more work, more faithful to the tool-use data.

---

## 5. Four data types

### 5.1 `concept_qa` — UE5 concepts grounded in your project

Multi-turn (4–6 turns) Q&A about a UE5 concept, with concrete examples drawn from `Lvl_IntroRoom` and your `Config/DefaultEngine.ini`.

Example angle: *"How does UE5's collision query system pick a channel?"* — answer cites `ECC_GameTraceChannel1 = Projectile` from your `DefaultEngine.ini` and a real trigger actor in `Lvl_IntroRoom` that uses the `Trigger` profile.

Grounding source: `AIAssistant.GetProjectContext` + `ListActors` (filtered) + targeted `execute_console_command` to confirm runtime behavior.

### 5.2 `tool_use` — Real MCP tool-call chains

A user asks for an editor task. The assistant chains real MCP tool calls. The trace records: what the user asked, what the model decided to call, what the tool returned, what the model reasoned, what it called next, and the final answer. Includes **error recovery** turns (e.g., tool returns `errorMessage` → model adjusts → succeeds).

Example trace:
1. user: "Find every static mesh actor in the level and tell me their bounds."
2. assistant → `ListActors`
3. tool returns 391 actors
4. assistant → `GetActorDetails` for each StaticMeshActor (or filters first)
5. tool returns transforms
6. assistant summarizes

Grounding source: live MCP `ListActors` / `GetActorDetails` / `execute_console_command` / `SetActorTransform`.

### 5.3 `scene_understanding` — Read-and-explain the level

A user asks "what's in this level?" or "is anything broken?". The assistant inspects the actor list, identifies game-mode actors, player starts, lighting, trigger volumes, and flags suspicious configurations (e.g., a `BP_DoorTrigger` with no paired `BP_DoorFrame_Unlockable`, a missing `Player Start`, lighting that doesn't match the project setting). 

This is where the project-specific value is highest — the model learns to interpret *your* level structure, not a generic UE5 scene.

Grounding source: `ListActors` + `get_editor_context` + `AIAssistant.GetProjectContext`.

### 5.4 `console_diagnosis` — Console commands and their meaning

User: "what does `r.ScreenPercentage 50` do here?" or "is `stat unit` useful for this scene?". Assistant: explains the command, predicts its output for *this* scene (e.g., "this level has 391 actors, expect `stat unit` to show …"), and may run the command to confirm.

Grounding source: targeted `execute_console_command` calls. **Safety:** only `stat *`, `show *`, `r.*` (read-mostly), `ke *` (read-only dumps). No mutation commands, no `quit`, no file deletion.

---

## 6. The four components

### 6.1 `ContextFetcher` (Python, in-session)

Talks JSON-RPC to `http://127.0.0.1:8000/mcp` using the existing `Mcp-Session-Id` flow (initialize → initialized → tools/call). One Python class with methods per MCP tool. ~150 lines.

Methods (one per top-level tool + toolset tools):
```python
class ContextFetcher:
    def get_editor_context(self) -> dict
    def list_actors(self, class_filter: str = None) -> list
    def get_actor_details(self, name: str) -> dict
    def run_console(self, command: str) -> str
    def capture_viewport_b64(self) -> str
    def list_toolsets(self) -> list
    def describe_toolset(self, name: str) -> dict
    def ai_project_context(self) -> str
    def ai_docked_context(self) -> str
    def save_level(self) -> bool
```

Safety wrapper around `run_console`: command allow-list, refuse anything matching `(quit|obj delete|file delete|reset|rebuild|...)`.

### 6.2 `ConversationPlanner` (in-session logic, no separate file)

Picks a `data_type` and a concrete `topic` (from a curated topic catalog, see §7), drafts a turn structure (e.g., "tool_use with 3 tool calls, 2 of which fail then recover"), and asks the Generator to fill in the content.

### 6.3 `Generator` (MiniMax-M3, in-session, not a separate file)

I am the generator. For each example, the planner hands me a prompt like:

> You are generating one SFT example for a small model that will drive an Unreal Editor via MCP. Produce a JSON object matching the schema in §4.
>
> **Data type:** `tool_use`
> **Topic:** actor inspection workflow
> **Grounding facts (live MCP, use ONLY these):**
> - level: Lvl_IntroRoom
> - actor count: 391
> - selected actors: []
> - tool inventory: [ListActors, GetActorDetails, SetActorTransform, execute_console_command, ...]
> - first 5 actors: [BP_FirstPersonCharacter_C_0, BP_FirstPersonGameMode_C_0, ...]
> **Plan:** 4 turns — user asks, assistant calls ListActors, tool returns 391 actors, assistant picks 3 and calls GetActorDetails on each, then summarizes.
> **Rules:** cite real tool names from the inventory; never invent source paths; never claim an actor exists that wasn't in the grounding facts; tool-call arguments must match the input schema.

I produce the JSON object.

### 6.4 `SelfVerifier` (Python + MiniMax-M3 hybrid, in-session)

Two-stage:

**Stage A — mechanical check** (Python, regex/parsing):
- Extract every concrete claim from my output (actor names, class names, position tuples, tool names, console output strings).
- For each claim, re-query MCP and compare. Flag mismatches.
- Verify `tool_calls` arrays have valid `name` and `arguments` per the tool's input schema.

**Stage B — judgment** (me, MiniMax-M3):
- Show me the example + the mechanical check report.
- I either: (a) mark verified, (b) repair the example and re-verify, (c) reject and explain why.

Failed/repaired counts go into the per-example `verification` block.

---

## 7. Topic catalog (v2)

The v1 20 topics are all rendering-internals. The v2 catalog mixes the four data types with topics **the live MCP can actually observe.** Seed values:

### `concept_qa` topics (mix of project-specific and general)
- Collision channels and profiles (uses your `DefaultEngine.ini` + actors)
- GameMode vs PlayerController vs Pawn (uses your `BP_FirstPersonGameMode`, `BP_FirstPersonCharacter`, `BP_FirstPersonPlayerController`)
- Level streaming vs single-level (`Lvl_IntroRoom` is the default map per `DefaultEngine.ini`)
- Input mapping contexts (`IMC_Default` vs `IMC_MouseLook`)
- SaveGame subsystem (`BP_SaveData` exists in your project)
- Custom trace channels — `Projectile` channel
- Plugin loading order (your enabled plugins in `.uproject`)
- Lumen vs Substrate (your config: Lumen on, Substrate off)
- Virtual Shadow Maps (your config: enabled)
- Static lighting policy (`r.AllowStaticLighting=False` in your config)
- Gameplay tags and asset references (project convention)
- Asset naming conventions (`BP_`, `M_`, `MI_`, `NS_`, `MS_`, `SM_`, `T_`, `DL_`, `StrT_`)

### `tool_use` topics
- Inventorying actors of a class
- Finding the largest/smallest actor by bounds
- Detecting duplicate actor names
- Locating a specific gameplay actor (game mode, player start, etc.)
- Triggering a console diagnostic
- Capturing a viewport snapshot for visual review
- Saving the level programmatically
- Discovering available toolsets and their tools
- Reading the project context via AI Assistant

### `scene_understanding` topics
- Identify the level's purpose from its actor mix
- Find unlit / unshadowed actors in a Lumen-enabled level
- Detect missing prerequisites (player start, game mode, light source)
- Spot orphan triggers (trigger without target)
- Compare actor count to project default expectations
- Identify the player pawn and its components

### `console_diagnosis` topics
- `stat fps` and `stat unit` interpretation
- `show collision` for finding invisible geometry
- `r.ScreenPercentage` trade-off
- `r.Lumen.*` toggles
- `ke * dumpobject` patterns
- `obj list class=...` for asset count
- `DumpRenderTargetPool` for memory

(Topics are not fixed — the planner can compose new ones from the live scene's structure.)

---

## 8. Compatibility shims

### 8.1 `format_adapter.py` (new, ~40 lines)

Reads `data/raw/pilot_mcp_grounded.jsonl`, rewrites each `tool` turn into a user/assistant pair, writes to `data/raw/pilot_for_existing_pipeline.jsonl`. This makes the new data consumable by the existing `data_prep.py` and `data_pruner.py` *without modifying either*.

**Caveat:** the existing `data_pruner.py` will still score v2 examples as low-factuality (because its `UE5_FACTS` is hardcoded to rendering internals). So in practice v2 needs its own pruner.

### 8.2 `data_pruner_v2.py` (new, ~200 lines, replaces the filter catalog)

Same four-filter structure as v1 (length, factuality, quality, dedup) but:
- `length_filter`: unchanged
- `factuality_filter`: catalog is **two-tier** — (a) the v1 rendering facts (still relevant for any concept_qa that touches rendering), (b) a v2 catalog of MCP-observable facts (real actor-class names, real tool names, real Config keys). Score = max(v1_score, v2_score), so either kind of grounded example passes.
- `quality_filter`: unchanged heuristic
- `dedup_filter`: unchanged Jaccard

This file coexists with v1 (does not modify it).

### 8.3 `train_small_model.py` and `eval_model.py`

Not modified. They consume the alpaca/sharegpt output of `data_prep.py`, which is fed by the adapter. Verified by reading `data_prep.py` (the only intermediate they care about).

---

## 9. Pilot scope and success criteria

### Pilot target (one session, ~30–60 minutes)
- **30–50 verified examples**, distributed roughly:
  - 10 `concept_qa`
  - 10 `tool_use`
  - 5 `scene_understanding`
  - 5 `console_diagnosis`
  - (the remaining are split as the generator sees fit)
- Output: `data/raw/pilot_mcp_grounded.jsonl` + `data/raw/pilot_generation_log.json`
- Compatibility mirror: `data/raw/pilot_for_existing_pipeline.jsonl`

### Success criteria
- ✅ 100% of examples have `verified: true`
- ✅ 0 hallucinated actor names (mechanical check passes on every claim)
- ✅ All `tool_calls` in `tool_use` examples are valid per the tool's input schema
- ✅ At least 70% of examples reference at least one concrete fact grounded in the live `Lvl_IntroRoom` state (not generic UE5 knowledge)
- ✅ The pilot JSONL is consumable by `data_prep.py` (via the adapter) without errors

### What "finish" means
After the pilot, the user has:
1. A reusable pipeline they can re-run against any UE5 project / level
2. A pilot JSONL ready for `data_prep.py` → `train_small_model.py`
3. A clean, MCP-grounded dataset whose quality they can spot-check
4. Decision inputs for "should we scale this to 5,000 examples?"

---

## 10. File layout (proposed)

```
UE5_Training_MCP/
├── scripts/                          # v1 (untouched)
│   ├── mcp_data_generator.py
│   ├── data_prep.py
│   ├── data_pruner.py
│   ├── train_small_model.py
│   └── eval_model.py
└── scripts_mcp_grounded/             # v2 (this design)
    ├── DESIGN.md                     # this file
    ├── context_fetcher.py            # 6.1
    ├── conversation_planner.py       # 6.2
    ├── self_verifier.py              # 6.4 (Stage A)
    ├── format_adapter.py             # 8.1
    ├── data_pruner_v2.py             # 8.2
    ├── topic_catalog.json            # §7
    ├── run_pilot.py                  # orchestrator (drives the whole thing)
    └── README.md                     # how to run the pilot
```

**No code yet.** After approval, files are added in the order above. The v1 scripts are not modified.

---

## 11. Decisions (confirmed)

| # | Question | Decision |
|---|---|---|
| 1 | Topic catalog scope | **Keep** v1's 20 rendering topics alongside v2's editor topics. v1 stays as-is; v2 is additive. |
| 2 | MCP safety policy | Positive allow-list for `execute_console_command`. Allowed: `stat *`, `show *`, `r.ScreenPercentage*`, `r.Lumen.*`, `r.Shadow.*`, `r.AmbientOcclusion.*`, `r.MaterialQualityLevel*`, `r.ViewDistanceScale*`, `ke *`, `obj list*`, `Dump*`, `MemReport*`, `ListMaterials*`, `ListTextures*`, `CountedPhysScene*`, `DisplayAll*`, `Slate.*` (read-only subset). Blocked: `Compile*` (BP / shaders / anything), `quit`/`exit`, `Map.Reload`, `Open *`/`Close *`, `File.*`, `Project.*`, `Editor.*` mutations, `Log*`, `PixelStreaming*`, `reset`, `obj delete`, `DisableAllScreenMessages`. Runtime cvar overrides (e.g. `r.MaterialQualityLevel`) are auto-restored after the call. |
| 3 | Error-recovery examples | **≥20% of `tool_use` traces, no upper cap** (revised from "20–30% target"). Driven by natural availability of error states from the live MCP (e.g. `GetActorDetails` on missing actor, `execute_console_command` typo) rather than a quota. The pruner's `length_filter` (≤2048 tokens) implicitly caps any single example. |
| 4 | Cross-run dedup | **Jaccard ≥ 0.7** on word sets (Chinese-character bigrams + English terms), matching the v1 pruner's algorithm but with a lower threshold (v1 uses 0.85) because v2 conversations share substantial MCP-derived vocabulary from the same scene. |
| 5 | Per-example `license` field | **Yes.** Each example carries a `license: {engine_refs: [...], project_refs: [...]}` block listing which engine internals and project-specific facts it references, for future data audit / redaction. |

---

## 12. Implementation order

The 8 files in §10 are built in this order. The v1 scripts are not modified.

| # | File | Purpose |
|---|---|---|
| 1 | `context_fetcher.py` | MCP JSON-RPC client + high-level tool wrappers + safety allow-list |
| 2 | `topic_catalog.json` | The 4 data types × topic lists from §7 |
| 3 | `self_verifier.py` | Mechanical claim extraction + re-query + verification report |
| 4 | `format_adapter.py` | Flattens v2 tool turns to user/assistant for `data_prep.py` |
| 5 | `data_pruner_v2.py` | Same 4 filters as v1, two-tier factuality catalog (v1 rendering facts + v2 MCP facts) |
| 6 | `run_pilot.py` | Orchestrator: drives ContextFetcher → Generator callback → SelfVerifier → JSONL |
| 7 | `README.md` | How to run the pilot + format compatibility notes |
| 8 | (this file, after pilot) | Append the pilot report, then mark this design as superseded by `pilot_report.md` |

After all 8 files exist, the pilot runs against the live MCP server in a single session. Pilot target: **15–25 verified examples** (revised from 30–50 in §9 after more realistic per-example budget analysis for an in-session interactive run).
