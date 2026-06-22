---
title: Tencent (光子) — Hao Yang: AI-Driven 3D Game Prototyping in Engine
type: talk
tags: [talk, gdc-2026, topic/rapid-prototyping, topic/pipeline, impact/medium, studio/tencent-photon]
date: 2026-03
gdc_year: 2026
speakers: [郝阳 (光子工作室群 首席工程师)]
venue: GDC 2026
title_cn: 在游戏引擎中AI驱动制作3D游戏原型
status: covered (腾讯研究院, GDC floor reporting)
---

# Tencent (光子) — Hao Yang: AI-Driven 3D Game Prototyping in Engine

## TL;DR

A hands-on, "how do I actually do this" talk about using generative AI inside a game engine to spin up playable 3D prototypes fast. The intended audience is indie devs and small-team leads. The line that landed: when asked "what skills do I need to start?" — Hao Yang answered "just try to make something, and the skills come along the way."

## What the talk covered

- The prototyping workflow:
  1. **Asset generation** in engine (Tencent uses internal tools, but the pattern is the same as Meshy / Tripo / ComfyUI pipelines).
  2. **Layout / scene composition** with prompt-driven scripting.
  3. **Logic scaffolding** with LLM agents writing the glue code.
  4. **Play-test loop** with 30-minute iteration cycles.
- The point is not "AI makes a game" but "AI makes the loop between idea and playable prototype short enough that a single developer can do it."
- Demos showed side-by-side: 1-person team vs. 1-person team + AI agents, hitting feature parity that would normally require 5–8 person-months.
- Honest framing: the prototype is throw-away. The talk is about *learning what to build*, not *shipping what AI built*.

## Why it matters for game creation

- The "playable prototype in an afternoon" workflow is a real shift. Pre-AI, even a 2D prototype took a day. 3D prototype in-engine was a week of asset + code work. Now: hours.
- For studios this is a **discovery velocity** multiplier — more prototypes tested per quarter means better games shipped per year.
- For indies this is a **capital efficiency** multiplier — fewer pre-production failures, faster pivot.

## What's missing

- No metrics on quality, retention, or what % of prototypes graduate to production.
- No clear comparison vs. Unreal's built-in generative tooling or Unity Muse.

## Related notes

- [[2026-Panel-TripoBitmagicGlassBead|Tripo/Bitmagic/Glass Bead panel — AI-native engine founders]]
- [[2026-Tencent-Tianming-AgenticAI|天美 — Agentic AI]] (overlap on "AI writes game code")
- [[2025-Meshy-3DAssetWorkflow|Meshy]] (similar 3D-generation pattern)

## Sources

- GDC 2026 official schedule
- 腾讯研究院 recap
- 企鹅号 / 触乐 GDC 2026 floor reports
