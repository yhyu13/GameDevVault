---
title: Tencent (GiiNEX × 元梦之星) — AIUGC Platform
type: talk
tags: [talk, gdc-2025, topic/ugc, topic/llm, topic/generative-content, impact/high, studio/tencent-giinex]
date: 2025-03
gdc_year: 2025
speakers: [Tencent GiiNEX team, 元梦之星 team]
venue: GDC 2025
title_cn: GiiNEX × 元梦之星 AIUGC 平台
status: covered
---

# Tencent (GiiNEX × 元梦之星) — AIUGC Platform

## TL;DR

The most-cited Chinese-UGC-platform AI talk of GDC 2025. GiiNEX is Tencent's game-AI brand; the 《元梦之星》 team partnered to ship an **AIUGC platform** that lets players generate custom game levels from text prompts. The same system has been used internally to compress level-development time from days to minutes.

## What the talk covered

- The platform spans the full UGC loop:
  - **Prompt → concept** (LLM converts player text into a structured design brief).
  - **Design brief → 3D layout** (generative layout system).
  - **Layout → props** (Meshy-class 3D generation).
  - **Logic → playable** (rule-based + LLM agents glue the level).
  - **Test → iterate** (automated playtesting with AI agents).
- Internal benchmark: a designer + AIUGC produced a level equivalent to **5 days of manual work in 25 minutes**.
- Player-facing: simplified prompt interface. Players write "a snowy mountain fortress with 3 hideouts and a treasure room" and get a playable level.
- Safety: every AI-generated level is automatically checked against a list of banned content (no IP infringement, no platform-violating content).

## Why it matters for game creation

- This is the **first shipped, in-game, large-scale AIUGC platform** from a major Chinese publisher. Most "AI UGC" demos are pre-launch.
- The "5 days → 25 minutes" internal benchmark is the most-cited production-time number in 2025.
- The "designer + AI" framing matters. AI doesn't replace the designer; it executes the designer's intent.
- For platform business models: this is a *retention* and *content-velocity* lever. More player-generated levels → more time-in-game → more revenue per active user.

## Limitations

- The system is constrained to specific game genres. Open-world or narrative-driven games need different approaches.
- Quality variance is high. Most player-generated levels are low-quality; the top 5% are playable for other players.

## Related notes

- [[2025-InworldAI-Inworld|Inworld AI — UGC character generation]]
- [[2025-Roblox-Cube3D|Roblox — Cube 3D]] (parallel: AI asset generation for UGC)
- [[2026-Tencent-VISVISE-FullPipeline|VISVISE — full pipeline]] (the AIGC engine this builds on)

## Sources

- 搜狐: 腾讯 AI 技术 GDC 2025
- 腾讯游戏学堂 official
- 触乐 recap
