# Critique: `gap_analysis_and_roadmap.md`

> **Critic**: Mavis (mavis orchestrator session `mvs_b1df5a185906490aa7084c12a3bc0c82`)
> **Target**: `C:\Git-repo-my\GameDevVault\Career\Kimi\UE5_Extending_MCP\gap_analysis_and_roadmap.md`
> **Critique date**: 2026-06-28
> **Critique type**: Technical review + structural review + factual review

---

## TL;DR

The doc is a **competent first-pass analysis** with solid structure (Gaps → Features → Roadmap → Modules → Connection). The gap tables are clearly written and the code-evidence pattern is good. But it has **four serious problems** that prevent it from being actionable as a real extension plan:

1. **Effort estimates are meaningless** — "Small / Medium / Large" without person-hours, dependencies, or test scope cannot be used to plan, prioritize, or commit to the 8-week timeline. The phases are also not in strict priority order.
2. **The roadmap is detached from the gap analysis** — features in Part 2 don't trace back to gap numbers in Part 1, so it's impossible to verify "this feature closes this gap."
3. **Several technical claims are either wrong, over-strong, or unverifiable** — see §4 for specifics (`LastProgressValue`, "Claude Code's default mode is stdio", HTTP→WebSocket "drop-in" framing, etc.).
4. **The "Connection to Our Training Pipeline" section is a one-paragraph afterthought** — this is supposedly the whole *point* of the project, and it gets less space than the WebSocket feature.

If the goal is to use this as a plan-of-record for actually extending the UE5 MCP plugin, **don't ship it as-is**. Specific fixes in §6.

---

## 1. Overall Assessment by Section

| Section | Quality | Notes |
|---|---|---|
| Header / metadata | ✅ Good | Clear scope, target source path, date. |
| Part 1 (Gaps) | ⚠️ Mixed | Tables are well-structured and the code-evidence pattern is strong. But severity assignments are inconsistent (see §4.1), and several "gaps" are actually intentional Experimental-plugin behavior. |
| Part 2 (Features) | ⚠️ Mixed | Good use-case framing. But the *How* sections are vague ("use `FHttpServerModule` WebSocket support if available"), and the priority distribution is roughly P0:P1:P2:P3 = 5:7:9:1, which suggests P0 is being overused. |
| Part 3 (Roadmap) | ❌ Weak | Effort = Small/Medium/Large is useless. No dependencies. No risk. No acceptance criteria. No test strategy. The 8-week timeline for 20+ features is implausible. |
| Part 4 (New Modules) | ⚠️ OK | Helpful as a directory sketch, but the file tree doesn't show `.h` files, `.Build.cs` changes, or `IModuleInterface` wiring. |
| Part 5 (Training Pipeline) | ❌ Too thin | This is the **strategic justification** for the entire project. Currently 1 short paragraph + 6 bullet points. No metrics, no experiment design, no link to `mcp_data_generator.py` (which is referenced but never shown). |

---

## 2. What's Done Well

These are the parts to keep when fixing the doc:

1. **The code-evidence pattern.** Every gap section shows a real excerpt from the source. This is the right way to make an "I read the code" claim credible. Keep this pattern.
2. **The 6-category gap taxonomy** (Transport / Spec / Tool / Editor / Perf / DX) is a clean way to slice the surface. It maps naturally to module boundaries in Part 4.
3. **The MCP spec terminology is used correctly** — `prompts/list`, `notifications/resources/updated`, `resource/templates`, etc. The author clearly read the spec.
4. **The "Connection to Training Pipeline" framing is the right idea** — treating MCP as both *data source* and *testbed* is a non-obvious insight that distinguishes this from a generic "let's add X" feature request. Just needs to be expanded.
5. **The "🔴 / 🟡 / 🟢" severity + "P0/P1/P2/P3" priority** visual pattern is a good common vocabulary — but the two scales are conflated (see §4.2).

---

## 3. Structural / Process Issues

### 3.1 Gap → Feature traceability is missing

The Part 1 gaps are numbered 1–33 but Part 2 features have no back-references. A reader (or you, 6 months from now) cannot answer: *"Does feature 2.1.1 (stdio) close gap #1, #2, or both?"*

**Fix:** Either add a `Closes gaps: #1, #2` line to each feature in Part 2, or add a "Traceability Matrix" appendix table. The latter is more useful for a roadmap doc.

### 3.2 The roadmap is not derived from priority

Phase 1 mixes P0 and P1 features. P0 = "must do now" and P1 = "should do this quarter" — they should not be interleaved within a single 2-week phase.

| Phase | What's claimed as in it | Priority mix |
|---|---|---|
| Phase 1 (Wk 1-2) | stdio (P0), editor_context (P0), console (P0), viewport (P0), prompts (P1) | 4×P0 + 1×P1 |
| Phase 2 (Wk 3-4) | list_assets (P1), read_blueprint_graph (P1), stream_logs (P1), progress (P1) | 4×P1 |
| Phase 3 (Wk 5-6) | multi-modal (P1), subscriptions (P2), permissions (P2), rate limit (P2), schema (P1) | 2×P1 + 3×P2 |
| Phase 4 (Wk 7-8) | TMap (no priority), caching (none), history (P4), scaffold (P2), tests (none) | mixed |

Either commit to "phases = priority" or split into two columns. As-is, the phases and priorities are two different plans pretending to be one.

### 3.3 Effort labels are not estimates

"Small / Medium / Large" without a unit (hours? days? sprints?) is a vibe, not an estimate. Worse, the same label is applied inconsistently — `add_stdio_transport` and `add_execute_console_command` are both "Small" in Part 2's implicit ranking, but the former requires writing a new transport class + new file + new tests, while the latter is a one-liner over `GEngine->Exec()`. They are not the same size.

**Fix:** Use T-shirt sizes with explicit ranges (S = 1-2 days, M = 3-5 days, L = 1-2 weeks) AND a person-count (1 dev? 2 devs?). Without this, "8-week timeline" is fiction.

### 3.4 8 weeks for 20+ features is implausible

Sum of effort:
- Phase 1: 5 features × ~3-5 days each = 15-25 dev-days
- Phase 2: 4 features × ~5-7 days each = 20-28 dev-days (Blueprint graph reading alone is 1-2 weeks)
- Phase 3: 5 features × ~3-7 days each = 15-35 dev-days
- Phase 4: 5 features × ~3-5 days each = 15-25 dev-days

Total: **65-113 dev-days for one engineer = 13-23 weeks**, not 8. With testing, code review, and the inevitable 50% tax for the Experimental plugin's quirks, double it. Either:
- Cut the scope to the 5 P0 features and call it a v0.2
- Triple the timeline
- Get more engineers

### 3.5 The "New Modules" tree is incomplete

The tree shows only `.cpp` files in `Private/`. Where are:
- The corresponding `.h` headers?
- The `IModuleInterface` subclass for each new module?
- The `.Build.cs` updates to depend on `Json`, `JsonUtilities`, `HTTP`, `WebSockets`?
- The `PrivateDependencyModuleNames` for `Engine`, `UnrealEd`, `Slate`, `SlateCore`?

As written, this tree is more "wishful file list" than "module scaffold."

---

## 4. Technical / Factual Issues

### 4.1 Severity assignments are inconsistent

| Gap | Severity assigned | Reality |
|---|---|---|
| #1 "Only HTTP transport" | 🔴 High | Correct. |
| #3 "No WebSocket support" | 🟡 Medium | But this is **not in the MCP spec** — WebSocket is a transport choice, not a spec requirement. Calling it a "gap" is a category error. |
| #7 "No `roots` support" | 🟡 Medium | `roots` are **client-side**, not server-side. The client declares its roots. UE5 MCP being a server means it doesn't *implement* `roots` — it receives them via `initialize`. Calling this a "gap" in the server misreads the spec. |
| #10 "No pagination on `tools/list`" | 🟢 Low | Correct, but if you're registering 100+ tools in Eager mode, pagination is a *client-side problem*, not a server-side one. The spec recommends pagination when the response would be > 1MB or > 100 items — neither applies to a fresh plugin. |
| #12 "No progress reporting with actual percentage" | 🔴 High | Correct concern, but calling `LastProgressValue` a "heartbeat counter" is unsupported without quoting the source. I've seen implementations where `LastProgressValue` is a real percentage field. |
| #11 "Cancel only works for AsyncAction tools" | 🔴 High | This is partially wrong. The `{}` default implementation in `IModelContextProtocolTool.h:71` is the **C++ idiom for "optional override"** — sync tools *correctly* inherit the no-op. The "gap" is that the spec wants *all* tools to be cancellable in principle, not that sync tools are buggy. |

### 4.2 Severity ≠ Priority is fine, but the doc never explains the distinction

A "🔴 High severity gap" can have a "🟡 P2 priority feature" if the workaround is acceptable. The doc uses two scales interchangeably, which makes a reader wonder which one to act on. Either:
- Drop one scale
- Or add a 1-line legend: "Severity = user-impact; Priority = effort-adjusted ROI"

### 4.3 "Claude Code's default mode is stdio" — verify, don't assert

This is correct as of 2025-2026, but the doc cites it as evidence in gap #1/#2 without a source. If this analysis gets passed to a reviewer who doesn't know Claude Code, they need either:
- A link to Anthropic's MCP transport docs
- Or a sentence like: "Anthropic's MCP transport spec defines stdio as the default for local integrations; HTTP is for remote."

### 4.4 "Use existing `FHttpServerModule` WebSocket support (if available in UE 5.8+)" — hand-waving

UE's HTTP server stack (`FHttpServerModule`, `IHttpRouter`) does **not** ship WebSocket support out of the box. WebSocket in UE requires the `WebSockets` module and a custom server (e.g., `IWebSocketServer` from `libwebsockets` is not exposed; you have to roll your own or use a plugin like `VaRestWebSocket`). Phrase this as "add a third-party WebSocket dependency (e.g., WebSocket++ or a libwebsockets wrapper)" or remove the parenthetical hedge and commit to a plan.

### 4.5 `FSlateApplication::Get().TakeScreenshot()` is the wrong API

`FSlateApplication::TakeScreenshot()` captures the **entire application window** including chrome, not the level viewport. For viewport-only capture you need:
- `FSceneViewport::TakeHighResScreenShot()` for the active viewport
- Or `ULevelEditorViewportClient::TakeScreenshot()` for the editor viewport
- Or render-target capture for PIE

This is a P0 feature; getting the API wrong would burn 2-3 days of debugging.

### 4.6 `LastProgressValue` is not necessarily a "heartbeat counter"

I'd want to see the actual `IModelContextProtocolTool.h` definition before accepting this. The `FModelContextProtocolToolRequest` struct may well have a `ProgressPercent` field. The doc claims to cite evidence but doesn't actually quote the field.

### 4.7 The `chain([...])` example is ill-formed for the proposed design

Feature 2.5.1 proposes `FModelContextProtocolComposedTool` that wraps multiple tools. But:
- Each tool in MCP has its own JSON-RPC request/response cycle
- The `chain()` example bundles `get_editor_context` (server data) + `capture_viewport` (binary) + `analyze_image` (server? client?) — three tools with different ownerships
- The third "analyze_image" would have to be either (a) a server-side tool, which contradicts the "LLM analyzes" use case, or (b) a client-side step, which can't be in a server-side chain

This feature needs a clearer use case. **Real tool composition is rare in MCP**; most clients prefer multiple round-trips.

### 4.8 The "prompts" feature priority (P1) is questionable

In practice, `prompts/list` and `prompts/get` are **the least-used MCP capability**. Claude Code, Cursor, and most clients prefer their own prompt templates and ignore server-provided prompts. The cost of implementing `prompts/*` is real (new `IModelContextProtocolPromptProvider.h`, registration machinery, schema); the value is low. Either demote to P3 or commit to a specific client that will use it.

### 4.9 "Sampling" use case is weak

> "The engine could ask the LLM for help generating tool descriptions, asset documentation, or blueprint node suggestions."

Tool descriptions are written once at dev time, not at runtime. Asset documentation is a separate problem (RAG / embeddings). Blueprint node suggestions are a heavy LLM inference loop in a synchronous request path. None of these justify a P2 implementation cost.

### 4.10 `IModelContextProtocolModule::RequestSampling()` semantics are wrong

`RequestSampling` is **client→server** in the spec (the *client* calls `sampling/createMessage` on the *server* to ask the server to invoke an LLM). The server side doesn't "request sampling from the client" — the server, in the standard MCP architecture, doesn't have an LLM at all. This entire feature description is conceptually muddled; drop it or rewrite after re-reading the spec.

### 4.11 Missing concerns that should be gaps

These are *not* in the doc and should be:

| Missing gap | Why it matters |
|---|---|
| **No authentication on HTTP transport** | The HTTP server is presumably bound to `127.0.0.1`, but the doc never confirms this. If it's bound to `0.0.0.0`, anyone on the LAN can call tool endpoints. |
| **No CORS configuration** | If a browser-based LLM client tries to connect, CORS will block it. |
| **No structured error codes per MCP spec** | The spec defines `error.code` values (-32600 to -32603, plus implementation-defined). Without them, clients can't distinguish "tool not found" from "tool crashed" from "timeout." |
| **No streaming for large responses** | A `resources/read` returning 50MB of log buffer will time out on HTTP. Need `resources/read` chunking or a streaming variant. |
| **No `elicitation` support** | MCP 2025-06-18 added `elicitation/create` for server-initiated user prompts (e.g., "MCP wants to delete file X, confirm?"). This is the *correct* place for Feature 2.6.3 (confirmation), not a custom modal dialog. |
| **No MCP authorization spec** | MCP 2025-06-18 added OAuth 2.1-based auth. UE5 MCP implements none of it. |
| **No `roots/list_changed` notification handling** | If the client changes project roots (user opens a new project), the server should re-init. Not addressed. |

### 4.12 "Open asset" tool complexity is underestimated

Opening a Blueprint in the BP Editor while the editor is in an unknown state (compiling, in PIE, in another asset) requires:
- Checking editor state via `GEditor->PlayWorld == nullptr` etc.
- Calling `FAssetEditorManager::Get().OpenEditorForAsset()`
- Handling the case where the asset is already open in another editor
- Handling dirty state

This is a 🟡 P2 with a "Medium" effort estimate, which understates by ~2x.

---

## 5. Minor Issues

- **Last modified date**: 2026-07-07 is in the future relative to today (2026-06-28). Either it's a typo or the doc was written from a future timestamp. Check.
- **`mcp_data_generator.py` is referenced but never linked or shown.** If this is the strategic reason for the whole project, the doc should at minimum include the path or a 5-line description.
- **No diagram of the existing call chain.** A mermaid sequence diagram of `client → ModelContextProtocolServer → IModelContextProtocolTool → FModelContextProtocolLibraryTool → UFunction::ProcessEvent` would make the gap analysis 2x more readable. The reference doc `UE5-ModelContextProtocol-完整调用链路.md` probably has this — link to it instead of re-deriving.
- **"Risk Assessment" column missing** in the Phase tables. Examples:
  - Phase 2 `read_blueprint_graph` — high risk of UE internal API changes across versions
  - Phase 1 `capture_viewport` — high risk of PIE-state interactions
  - Phase 3 multi-modal — depends on client capability negotiation
- **The closing line "Source: `C:\Epic\UE_Engine\UE5_8\UnrealEngine\...`"** is hardcoded to a local path. The doc is in a git repo; either gitignore it or use a relative path. As-is, if the doc is shared, it leaks the author's local file structure.
- **No acceptance criteria** for any feature. What does "done" look like for `capture_viewport`? What is the test that proves stdio transport works?
- **No competitor/alternative scan.** Does Unreal Engine have a built-in scripting/automation interface (Python plugin, Slate UI scripting, Gauntlet) that already does some of this? If yes, MCP should complement, not duplicate.
- **Markdown formatting**: Tables are 4-column but the `🔴` emoji makes them visually wide. Consider `| # | Gap | Sev | Why |` with shorter "Why" cells. Some rows have very long "Why" cells that break wrapping.

---

## 6. Recommended Fixes (Concrete, Prioritized)

If you want this to be a usable plan-of-record, do these in order:

### Fix 1 (30 min) — Add traceability
Add a `Closes gap: #N` line to every feature in Part 2. Or add a "Traceability Matrix" appendix.

### Fix 2 (1 hour) — Rewrite the roadmap table
Replace "Small/Medium/Large" with `[S=1-2d | M=3-5d | L=1-2w]` plus a person-count. Add a "Depends on" column. Add a "Test/Acceptance" column.

### Fix 3 (1 hour) — Reconcile phases with priorities
Either:
- Phase 1 = all P0 (5 features, ~3-4 weeks)
- Phase 2 = all P1 (~6-8 weeks)
- Phase 3 = P2 (3-4 weeks)
- Phase 4 = P3 (1-2 weeks)
Or
- Drop the priority column and rely solely on the phase ordering. Don't have both.

### Fix 4 (2 hours) — Fact-check the technical claims
- Re-open `IModelContextProtocolTool.h` and quote the actual `LastProgressValue` definition
- Re-verify `FHttpServerModule` WebSocket support (or rewrite that feature to use the `WebSockets` module explicitly)
- Re-verify the `chain()` use case or drop feature 2.5.1
- Verify `FSlateApplication::TakeScreenshot` is the right API for viewport capture; if not, fix
- Re-read MCP 2025-06-18 spec for `sampling` directionality

### Fix 5 (2 hours) — Add the missing gap table
Add a §1.7 "Security & Spec-Compliance Gaps" covering: auth, CORS, structured error codes, `elicitation`, `roots/list_changed`, MCP authorization spec, large-response streaming.

### Fix 6 (1 hour) — Expand Part 5 by 5x
Currently 1 paragraph. Expand to:
- What `mcp_data_generator.py` does (link or 5-line summary)
- What training data shape is being collected
- How the extensions map to specific data collection steps
- A measurement plan: "after this extension, we expect to collect N more trajectories per editor session"
- Risks: "this only works if [condition]"

### Fix 7 (30 min) — Drop or rewrite two features
- Drop Feature 2.5.1 (Tool Composition) — use case is weak and design is muddled
- Rewrite Feature 2.1.4 (Sampling) — either correct the spec direction or drop

### Fix 8 (1 hour) — Re-scope the timeline
Either:
- Cut to 5 P0 features = "v0.2" release, ~3-4 weeks
- Or commit to 13-23 week timeline with 1 engineer, or 6-10 weeks with 2

**Total fix effort: ~9-10 hours of doc work.** Worth it if this doc is going to drive real work; not worth it if it's a one-time brainstorming artifact.

---

## 7. Summary Score

| Dimension | Score (1-5) | Comment |
|---|---|---|
| Structure & readability | 4 | Clean sections, consistent voice. |
| Factual accuracy | 2.5 | Several claims are unverified or wrong. (See §4.) |
| Actionability | 2 | Effort labels, missing traceability, weak acceptance criteria. |
| Strategic alignment | 1.5 | The training-pipeline justification is 1 paragraph; should be the spine. |
| Completeness | 2.5 | Missing security/auth, large-response handling, elicitation, spec directionality. |
| **Overall** | **2.5 / 5** | Good first draft, not yet a plan-of-record. |

---

## 8. One-Line Verdict

> Solid brainstorming output. Before it becomes a roadmap, it needs (1) real effort estimates, (2) gap→feature traceability, (3) a fact-check pass on the technical claims, and (4) a 5x expansion of why this matters to the training pipeline — which is currently the strongest argument in the doc and the most underdeveloped section.

---

*Critique generated 2026-06-28 by Mavis.*
*Cross-references: [[UE5-ModelContextProtocol-完整调用链路]] is in `Routine/02-引擎源码分析库/Unreal-Engine/`. The doc references this file but doesn't link it as `[[...]]`.*
