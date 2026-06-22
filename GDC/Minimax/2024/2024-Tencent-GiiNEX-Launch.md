---
title: Tencent — GiiNEX Launch at GDC 2024
type: talk
tags: [talk, gdc-2024, topic/generative-content, topic/ugc, topic/3d-generation, impact/high, studio/tencent]
date: 2024-03-20
gdc_year: 2024
speakers: [Tencent AI Lab Game AI team (GiiNEX team)]
venue: GDC 2024 — Tencent booth + GDC official coverage
title_cn: 腾讯自研游戏AI引擎GiiNEX全球首发
status: covered (腾讯互娱, IT之家, GameLook, 雷锋网, 澎湃新闻, 福州新闻网)
---

# Tencent — GiiNEX Launch at GDC 2024

## TL;DR

The first public launch of **GiiNEX** — Tencent AI Lab's full-lifecycle game AI engine. The headline numbers: a 25 km² game city in **25 minutes** (5 days → 25 min, 100× speedup), a single building from a reference image in **under 20 minutes** (50×), a full indoor scene from a few photos in **under 1 hour** (40×). The talk was a product launch, not a research paper — the focus was on the three AIGC tools (city layout, building facade, indoor mapping) plus UGC level design tools already live in 《元梦之星》.

## What the talk covered

### Architecture: three layers, one engine

- **Frontier algorithm models**: unified model layer with both generative-AI (LLM, diffusion, 3D) and decision-AI (reinforcement learning) capability. Supports MOBA, FPS, party games and 10+ genres.
- **High-performance training platform**: ten-thousand-card scale resource scheduling.
- **Online inference engine**: hybrid mobile + cloud deployment, cross-device parity.

### The three city-generation tools

| Tool | Input | Output | Traditional → GiiNEX | Speedup |
|------|-------|--------|------------------------|---------|
| City layout | Main features (water / main roads / mountains) + parameters | Full vector road network, special-district zoning, height map, building block function split | 5 days for 25 km² | **25 min** (~100×) |
| Building facade | Reference image | New 3D model with variation | Manual modeling | **< 20 min** (~50×) |
| Indoor mapping | Multi-angle room photos | 3D indoor scene with detail | Hand-built | **< 1 hour** (~40×) |

The city layout tool was the showpiece. Designers sketch the main features (water, main roads, mountains), set parameters, designate special-use districts, set building heights, and the system returns a complete detailed city plan. The published quotes are **~100× speedup** on city layout, **~50×** on building facade, **~40×** on indoor mapping.

### UGC tools deployed in 《元梦之星》

The most concrete shipped feature: a suite of in-game level-design tools for **players** (not professional devs):

- **Inspiration tool**: pick a preset template or type a text prompt to seed a level style.
- **Building PCG tool**: rule-based procedural generation for Chinese classical architecture (towers, pavilions, corridors, bridges), one-second assembly.
- **Color-palette inspiration tool**: pick a theme, or upload a reference image, to get a generated color palette and one-click re-color.
- **3D model simplification**: take a complex 3D model, decompose it into basic geometric primitives, and let the player edit / reassemble. This makes UGC-3D authoring possible for zero-skill users.
- **NPC motion generation**: upload a video of a real person, the system uses deep learning to extract the motion and retarget it to a game character, automatically adjusting for body-shape differences between performer and character.

The **NPC motion-from-video** feature is the one closest to the existing 2026 Magic Studio motion-generation talk. Magic Studio's 2026 version is real-time in-game inference; the 2024 GiiNEX version was offline asset generation. Same problem, different stage of the production stack.

### Decision-AI for MOBA coaching (the dual pitch)

The talk also covered GiiNEX's decision-AI side, in the form of a **MOBA coach** that:
- Does real-time match analysis.
- Simulates opponents at different skill brackets and playstyles.
- Provides targeted tactical suggestions via TTS, with multi-language support.
- Helps new players onboard and supports global market expansion.

This is the "decision AI" half of the dual-pitch. The same engine that AIGC-generates 3D cities can also train RL agents that play-test or coach games. The framing: one engine, two halves of the AI stack.

## Why it matters for game creation

- **The launch moment for "AI engine as platform" thinking.** GiiNEX is the first time a major publisher has publicly framed a single AI engine as covering the *full lifecycle* of game dev (research → training → inference → in-game deployment). Most Western competitors (Unity Muse, Unreal MetaHuman, etc.) were still in single-feature mode in March 2024.
- **The "5 days → 25 minutes" number became the most-cited production benchmark of 2024.** Every other AI-tool vendor benchmarked against it within 6 months.
- **The UGC-in-game approach pre-dates Roblox Cube 3D (GDC 2025) by 12 months.** Roblox's "AI gives every player creative superpowers" thesis was already running in 《元梦之星》in 2024.
- **The decision-AI + generative-AI pairing is the structurally important move.** It treats AI not as "a tool for art" or "a tool for code" but as a *platform* covering both. Studios that adopt this framing have an integration advantage over studios that buy point tools.

## Limitations

- Most numbers are time-on-task comparisons, not quality comparisons. The talk did not publish head-to-head visual quality benchmarks.
- "100× speedup" applies to *specific city/building types* with the right training data. Custom art styles still need hand-tuning.
- The decision-AI MOBA coach is real-time analysis + TTS delivery, not an LLM-based coach. The 2025 AI Coaching in Honor of Kings (LLM-based) is a different generation.

## Related notes

- The 2025 GDC follow-up is `2025-Tencent-GiiNEX-AIUGC` — that talk covered the deployed platform and 《元梦之星》integration at scale.
- For real-time in-game motion generation (the next step after GiiNEX's offline motion-from-video), see the 2026 Magic Studio talk.
- For the Tencent LLM-based coaching system, see `2025-Tencent-Tianmei-AICoachingHonorOfKings`.

## Sources

- 腾讯互娱 official GDC 2024 announcement
- IT之家 2024-03-21
- GameLook 2024-03-21
- 雷锋网 2024-03-21 (Nebula)
- 澎湃新闻 2024-03-22
- 福州新闻网 2024-03-26
- Tencent official EN article: tencent.com/en-us/articles/2201815.html
