# AI-Driven 3D Game Prototyping — GDC 2026

## Short Summary

**Talk:** *AI-Driven 3D Game Prototyping*
**Speaker:** Hao Yang, Senior Engineer, Tencent Photon Studio Group
**Venue:** GDC 2026 (40th edition), Moscone Center, San Francisco
**Date:** March 2026
**Track:** AI Summit
**Impact:** One of the most oversubscribed AI talks at GDC 2026 — the queue started forming an hour before the session started and the room filled to capacity before doors opened.

---

## The Core Idea

Existing AI tools can ship small **Web 2D** games end-to-end. They cannot cross the boundary into a **3D game engine** — which is where the real money is. The talk introduces **C.A.T**, a three-principle framework that lets a language model build playable 3D prototypes inside Unreal.

## The C.A.T Framework

| Letter | Principle | What it does |
|---|---|---|
| **C** | **Code Reuse** | Share the same TypeScript source between Web and engine runtimes. Logic ships once, runs everywhere. |
| **A** | **Adapter Design** | Split the codebase into a platform-agnostic **core** (game rules, state) and platform-specific **adapters** (Web DOM, Unreal ECS). AI only touches the core. |
| **T** | **Token-Friendly** *(most critical)* | Tokenize the 3D world before the AI touches it: feed domain rules, expose asset bounding boxes / colliders as text, let designers place named markers. AI manipulates a textual representation of the 3D scene. |

## The Stack

`Prompt (TypeScript)` → **Puerts** (Tencent's open-source TypeScript-to-engine bridge, no C++) → **ECS** (data-driven core) → **Unreal Web Browser widget** (renders Web UI pixel-perfectly in-engine) → playable prototype.

## Three Demo Prototypes (all built by AI)

1. **8-Ball Pool** — physics-heavy, simple rules, deterministic. 100% functional.
2. **Top-down RPG** — built from a single prompt in ~40 minutes, ~70% of the final game.
3. **Action Combat** — multi-character, multi-boss, varied mechanics. Most ambitious test case.

## Why It Matters

- **Internal R&D:** Designers validate mechanics in hours instead of weeks, without pulling in a full engineering team.
- **External:** Amateur creators can build playable 3D prototypes from a sentence.
- **Strategic:** Game tooling must shift from GUI-first (built for humans) to token-first (built for AI). The two will converge.

## Headline Quote

> *"Game tools were built for humans. Stop expecting AI to see pixels."* — Hao Yang

## Why This Talk Was Picked

Among the 105+ AI sessions at GDC 2026, this one had the highest real-world impact per slot: it offered a working technical framework (not a vision slide), open-source tooling (Puerts), and concrete proof points (three playable prototypes), while framing the broader industry shift from GUI to token interfaces. It's the most actionable single talk on AI in 3D game development from the past 10 years.

---

## Files

- `AI-Driven-3D-Game-Prototyping-GDC2026.pptx` — 13-slide breakdown of the talk
- `slides/` — PptxGenJS source (one file per slide, plus `compile.js`)
- `summary.md` — this file