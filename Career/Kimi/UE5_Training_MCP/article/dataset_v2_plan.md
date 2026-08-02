# Dataset v2 Plan — Phase 3 SFT Data

> **Author**: M3 (the assistant), 2026-08-02.
> **Status**: Action plan, derived from findings in [`self_benchmark_learnings.md`](self_benchmark_learnings.md) and [`article/kilo_verification/`](kilo_verification/) (kilo's independent re-scoring).
> **Supersedes**: [`plan.md`](plan.md), [`UE5_Training_MCP_Background.md`](UE5_Training_MCP_Background.md). See "Deprecated" header on both.

---

## 1. The honest baseline (read this before the plan)

Two independent measurements of "what a broad UE5-knowledge LLM scores on the fresh 15-question set, against my rubric":

| Who answered | kw overlap | n | Note |
|---|---:|---:|---|
| **M3 (me, same session as the rubric)** | **0.948** | 15 | Self-biased. I wrote both questions and rubric in the same session. My own doc §8 caveats this. |
| **Kilo (independent model, different session)** | **0.379** | 15 | Same rubric, same questions, no leakage. See [`kilo_verification/score.py`](kilo_verification/score.py). |
| **Qwen3.5-0.8B FT** | 0.159 | 15 | Source: `outputs/results/eval_fresh_0.8B_FT.json` |
| **Qwen3.5-2B FT** | 0.188 | 15 | `outputs/results/eval_fresh_2B_FT.json` |
| **Qwen3.5-4B FT** | 0.224 | 15 | `outputs/results/eval_fresh_4B_FT.json` |

**The realistic "LLM with broad UE5 vocabulary, no UE5-MCP fine-tune, answering general UE5 questions" ceiling is ~0.38, not ~0.95.** The 0.948 was my own self-bias artifact.

**What this means for the small-model goal**: 0.224 (best Qwen) → 0.379 (independent LLM ceiling) is a ~0.15 kw gap to close. That is **achievable with the right data**, unlike the 0.724 gap my self-biased 0.948 implied.

---

## 2. Where we are (Phase 2 status)

- 6 Qwen variants trained on 108 records, all evaluated on the 15-question MCP-flavored test (`data/splits/test.jsonl`) and the 15-question general-UE5 test (`data/splits/fresh_test.jsonl`).
- Best MCP-flavored result: 2B-FT = 0.425 (style transfer, not knowledge).
- Best general-UE5 result: 4B-FT = 0.224.
- FT *hurts* 0.8B (−0.047) and 2B (−0.024) on the general-UE5 set because the 108-record corpus is all MCP style and no UE5 architecture.
- The current eval is kw-overlap only — fast but rewards vocabulary mimicry, not correctness.

The data, training, and eval pipeline all work. The numbers are dominated by **what's in the 108 SFT records**, which is the only thing we can change to move them.

---

## 3. Goal (realistic reframe)

The user-stated goal: *"make small model inference good enough so we don't have to use commercial models."* All-or-nothing framing.

The realistic reframe: **handle the narrow UE5-MCP scene-query workload reliably locally (≥0.55 kw + ≥4/5 LLM-judge correctness on a held-out 100-question scene-query set), and fall back to a commercial LLM for general UE5 questions it isn't trained on.** That is a 60–70% cost reduction at full coverage, not 100% — but it is the right cost/benefit for the engineering effort.

### 3.1 Acceptance criteria for Phase 3

| Metric | Current best (4B-FT) | Phase 3 target (2B-FT) |
|---|---:|---:|
| Fresh-set kw overlap | 0.224 | **≥ 0.40** (close kilo's gap) |
| Original-test kw overlap | 0.318 | **≥ 0.45** (recover + improve) |
| LLM-judge correctness (1–5, scene queries) | not measured | **≥ 3.5** |
| Wall-clock per inference (2B, 24 GB GPU) | 9.4 s | unchanged (≤ 10 s) |
| Adapter size | ~61 MB | unchanged (≤ 80 MB) |

If 2B-FT hits ≥0.40 fresh + ≥0.45 original + ≥3.5 LLM-judge, **ship it for the scene-query workload**. Anything below that, keep iterating.

---

## 4. Data plan (the only thing that matters)

### 4.1 The mix

| Bucket | Records | Style | Source |
|---|---:|---|---|
| **A. MCP scene queries** (existing) | ~150 | "Tool calls: → Results: → Quick summary:" with mock live-editor data | Re-run `mcp_data_generator.py` on 2–3 different UE5 projects (not just First Person template), expand from 108 to ~150 records |
| **B. General UE5 architecture Q&A** (new) | ~5,000 | Direct conceptual explanation, no tool calls | Distill from Claude/GPT-4 with LLM-judge filter (see §5) |
| **C. Code patterns** (new) | ~1,500 | C++ snippets + UE5 API names + "when to use" | Distill from Claude/GPT-4 with LLM-judge filter |
| **D. Console variables / diagnostics** (new) | ~500 | Single-line variable name + meaning + reasonable default | Distill from UE5 docs + LLM expansion |
| **E. Replication / networking** (new) | ~500 | "When does this fire" / "what goes wrong" style | Distill from UE5 docs + LLM expansion |
| **F. Comparison questions** (new) | ~500 | "X vs Y", "X or Y for use case Z" | Distill from UE5 community FAQ + LLM expansion |

**Total: ~8,150 records.** Bucket A preserves the Phase 2 MCP-style fluency; B–F fix the missing UE5-architecture coverage that the kilo baseline shows is the actual gap.

### 4.2 Topic distribution (proportions of buckets B–F)

```
Bucket B: 60% — UE5 architecture (subsystems, asset types, GameplayTags, asset manager, modules, plugins)
Bucket C: 18% — C++ code patterns (delegate binding, RPC, overlap, tick, async loading, asset loading)
Bucket D:  6% — Console variables (r.Lumen.*, r.Shadow.*, niagara.*, foliage.*, stat unit, stat gpu)
Bucket E:  6% — Replication (Multicast vs Server, OnRep, relevancy, dormancy)
Bucket F: 10% — Comparisons (UStaticMesh vs USkeletalMesh, Material vs MIC, Cascade vs Niagara, World Partition vs Level Streaming)
```

The distribution was chosen to match what I scored highest on (architecture, code patterns, console variables) and what the small models scored lowest on (everything else, because the 108 records don't teach it).

### 4.3 Per-record shape

Alpaca format, same as existing `data/splits/test.jsonl`:

```json
{
  "instruction": "What's the difference between a Multicast RPC and a Server RPC in UE5 replication?",
  "input": "",
  "output": "Both are RPCs (Remote Procedure Calls) — UFUNCTIONs marked with a specifier that the engine replicates as a network message. ...",
  "topic": "Multicast vs Server RPC",
  "category": "replication",
  "difficulty": "intermediate",
  "source": "claude_distill_v1"
}
```

`category` ∈ {architecture, code_pattern, console_variable, replication, comparison, scene_query}.
`difficulty` ∈ {basic, intermediate, advanced}.

---

## 5. Generation pipeline

### 5.1 Distill from Claude with LLM-judge filter

```
Claude API ($50–200 budget)
        │
        ▼
┌───────────────────────────────────────┐
│  Per-topic prompt template:           │
│  "Generate 50 UE5 (topic) Q&A pairs.  │
│   Each pair: (instruction, output).   │
│   Style: direct conceptual, no tool   │
│   calls, no live-editor mock.         │
│   Length: 200–600 words per answer.   │
│   Include specific UE5 class names,   │
│   console variables, code patterns."  │
└───────────────────────────────────────┘
        │
        ▼
  8,000–10,000 candidate records
        │
        ▼
┌───────────────────────────────────────┐
│  LLM-judge filter (Claude or GPT-4):  │
│  Score 1–5 on:                        │
│   - factual correctness               │
│   - specificity (real class names,    │
│     real console vars)                │
│   - clarity                           │
│   - absence of hallucinated APIs      │
│  Keep ≥ 4/5.                          │
└───────────────────────────────────────┘
        │
        ▼
  ~5,000–7,000 records after filter
        │
        ▼
  Human spot-check on 5% sample
        │
        ▼
  data/splits/train_v2.jsonl (90%),
  data/splits/val_v2.jsonl (5%),
  data/splits/test_v2.jsonl (5%)
```

### 5.2 What the LLM-judge rubric must reject

- API names that don't exist (e.g. `UParticleSystemComponent2` — there's no such class)
- Console variables with wrong defaults (e.g. claiming `r.Lumen.ScreenProbeGather.ScreenSize` defaults to 2.0 when it defaults to 1.0)
- Vague generalities that don't name a specific UE5 class / function / variable
- Pure hand-waving ("use the engine to do this")
- Style bleed from MCP templates ("Tool calls: → Results:") — these belong in bucket A, not B–F

### 5.3 Cost estimate

- Claude Sonnet 4 input $3 / MTok, output $15 / MTok.
- ~10K records × ~300 words input + ~400 words output ≈ 5 MTok input + 6.5 MTok output.
- Generation: 5 × 3 + 6.5 × 15 = **$112.50** raw.
- LLM-judge filter (each record scored once): 11K × 300 words input + 11K × 50 words output ≈ 5.5 MTok + 1 MTok.
- Filter: 5.5 × 3 + 1 × 15 = **$31.50**.
- **Total distillation budget: ~$150**, plus retry overhead and human spot-check time.

---

## 6. Training plan

Use the **2B model** as the production target. It is the best balance of capability vs VRAM (8 GB vs 16 GB for 4B) and the project's own [run_report_phase2.md](../outputs/run_report_phase2.md) showed 2B-FT outperforming 4B-FT on the in-domain test. 4B-FT underperforms because it is under-trained on small data; with ~8K records it should overtake 2B, but ship 2B first.

| Hyperparameter | Value | Why |
|---|---|---|
| `lora_r` | 32 (was 16) | More capacity to absorb 8K-record mix |
| `lora_alpha` | 64 | Standard 2× ratio |
| `epochs` | 2 (was 3) | More data → fewer passes needed |
| `effective_batch_size` | 8 | Same as Phase 2 |
| `learning_rate` | 2e-4 | Same as Phase 2 2B |
| `max_seq_length` | 768 (was 512) | Longer answers in buckets B–F |

Reuse `scripts/train_qwen35.py` with the new hyperparameter block.

---

## 7. Eval plan (correctness matters now)

### 7.1 Three-tier evaluation

1. **Kw overlap** (existing, fast) — keep as-is for fast iteration during data generation.
2. **LLM-as-judge correctness** (new) — Claude or GPT-4 scores each (prediction, reference) on a 1–5 correctness scale. Add `scripts/eval_judge.py`. Cost: ~$5 per 100-record eval.
3. **Live-tool execution** (out of scope for Phase 3) — only for bucket A (scene queries) where the rubric is executable.

### 7.2 Two held-out sets

| Set | Source | Style | Use |
|---|---|---|---|
| `data/splits/test.jsonl` | Phase 2 | MCP-flavored | Backwards-compat: any FT must not regress below 0.45 |
| `data/splits/fresh_test.jsonl` | Phase 2.5 | General UE5 | New: any FT must improve above 0.379 (kilo's independent baseline) |
| `data/splits/test_v2.jsonl` | Phase 3 (new) | Mixed | Held-out from the v2 data, never seen during distillation |

The v2 held-out is the final acceptance gate.

---

## 8. Timeline

| Week | Work |
|---|---|
| 1 | Build `scripts/distill_claude.py` + `scripts/eval_judge.py`. Pilot on 200 records, measure judge quality. |
| 2 | Distill all of buckets B–F. Filter. Spot-check. ~$150 spend. |
| 3 | Train 2B-FT v2 (4B-FT v2 in parallel). Sweep `lora_r` ∈ {16, 32, 64} on a 1K subset. |
| 4 | Final 2B-FT v2 on full 8K. Evaluate on all three test sets. Decide ship. |

End state: a v2 2B LoRA adapter at `outputs/models/qwen3.5-2b-ue5-lora-v2/`, published to Hugging Face as `Yhyu13/Qwen3.5-2B-UE5-LoRA-v2`.

---

## 9. What this plan does NOT solve

- **100% replacement of commercial models** — even with 8K records, 2B will not match Claude on the long tail of general UE5 questions. The realistic ceiling is "useful for ~70% of in-scope queries." Plan accordingly.
- **Live MCP tool execution** — out of scope. The current eval is text-only; running the model against actual UE5 MCP tools would need a separate harness.
- **Multi-turn reasoning** — buckets B–F are all single-turn. Real dev questions are multi-turn ("now bind that to OnRep_Foo on the same actor"). Add a multi-turn bucket in Phase 4 if the single-turn ceiling proves insufficient.

---

## 10. Decision criteria (write this down before starting)

- If after Week 2 the LLM-judge filter rejects >40% of generated records → **stop**, the prompt template is wrong, fix the template before regenerating. Do not throw bad data at training.
- If after Week 3 the 2B-FT v2 still regresses on `fresh_test` vs kilo's 0.379 → **stop**, the data mix is wrong (too much bucket A), rebalance.
- If after Week 4 the 2B-FT v2 hits ≥0.40 fresh + ≥0.45 original + ≥3.5 judge → **ship**. Publish to HF.
- If it hits <0.30 fresh → the bucket weights are still wrong, do another iteration of buckets B–F.

---

## 11. One-page summary for the user

**Today**: 4B-FT best general-UE5 = 0.224 kw. Independent LLM (kilo) baseline = 0.379 kw. Gap = 0.15 kw, achievable.

**Plan**: Distill ~8K records (150 MCP + 5K general UE5 + 1.5K code + 500 console + 500 replication + 500 comparisons) from Claude with an LLM-judge filter. Train 2B-FT v2 with `lora_r=32`, 2 epochs. Evaluate with kw + LLM-judge on 3 test sets. Ship if 2B-FT v2 ≥ 0.40 fresh + ≥0.45 original + ≥3.5 judge.

**Cost**: ~$150 distillation + ~$50 eval + 1 GPU-week. ~4 weeks calendar time.

**Outcome**: A 2B model that handles the UE5-MCP scene-query workload reliably locally and falls back to Claude for the long tail. ~60–70% cost reduction at full coverage.