---
title: Proxima Studio — Suck Up! (LLM-driven NPC Interactions)
type: talk
tags: [talk, gdc-2025, topic/llm-in-game, topic/indie, impact/medium, studio/proxima]
date: 2025-03
gdc_year: 2025
speakers: [Proxima Studio team]
venue: GDC 2025
status: covered
---

# Proxima Studio — Suck Up! (LLM-driven NPC Interactions)

## TL;DR

A small indie adventure game where **every NPC is LLM-driven** with no pre-authored dialogue. Released on Steam. The talk focused on the practical lessons of shipping an LLM-driven indie game.

## What the talk covered

- The game: 《Suck Up!》 — a vampire-themed comedy adventure. The player is a vampire trying to befriend humans; every conversation is LLM-driven.
- The architecture:
  - Per-NPC system prompt with personality, goals, secret info.
  - LLM generates dialogue in real time.
  - Voice synthesis with character timbre.
  - **Cost model**: indie-tier; the studio disclosed per-session token costs.
- The lessons:
  - **Hallucinations are a feature**: weird NPC responses are funny in a comedy game.
  - **Memory is the hardest part**: keeping NPC consistency across a 10+ hour playthrough requires careful prompt engineering.
  - **Safety**: explicit content policy on the system prompt prevents most violations.
- The team noted they iterated from GPT-2 (too incoherent) → GPT-3.5 (playable) → GPT-4 (production).

## Why it matters for game creation

- The most-cited **indie case study** of shipping an LLM-driven game in 2025. Not a demo, a Steam release.
- The "hallucinations are a feature" lesson is the under-appreciated one. For comedy / horror / surreal games, AI weirdness is a creative asset.
- The cost model disclosure is rare. Most studios don't share per-session token costs.
- The GPT-2 → GPT-3.5 → GPT-4 progression timeline is the most-cited "how soon can you ship an LLM game" benchmark.

## Why it's borderline

- The NPCs are in-game AI, not a creation tool.
- Included because: (a) the production / cost lessons are about shipping AI-driven content, not playing against it; (b) the indie case study is a useful counterweight to AAA case studies.

## Related notes

- [[2025-Tencent-Magic-FACUL-AITeammate|F.A.C.U.L. (Tencent)]] (AAA LLM-in-game)
- [[2025-InworldAI-Inworld|Inworld AI]] (infrastructure for this kind of game)
- [[2025-GoogleDeepMind-Gemini-GameDev|Gemini for game dev]] (tooling for LLM-driven games)

## Sources

- Proxima Studio official
- Steam: Suck Up! listing
- 腾讯研究院 GDC 2025 recap
