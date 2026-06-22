---
title: Tencent (魔方) — F.A.C.U.L.: First Human-Language FPS AI Teammate
type: talk
tags: [talk, gdc-2025, topic/llm-in-game, topic/production-case-study, impact/medium, studio/tencent-mofang]
date: 2025-03
gdc_year: 2025
speakers: [Tencent 魔方工作室 F.A.C.U.L. team]
venue: GDC 2025
title_cn: F.A.C.U.L.：首个懂人类语言的FPS AI队友
status: borderline — included for production-deployment lessons
---

# Tencent (魔方) — F.A.C.U.L.: First Human-Language FPS AI Teammate

## TL;DR

Borderline for this vault — the F.A.C.U.L. system is an in-game AI teammate in 《暗区突围》 that responds to natural-language voice commands. Included because the **production-deployment story** is the most-cited example in 2025 of "how do you actually ship an LLM-driven feature in a live FPS at scale." The talk is more about the production pipeline than the gameplay.

## What the talk covered

- The system architecture:
  - Voice → ASR → LLM (intent parsing + planning) → game actions.
  - Recognises thousands of in-game objects ("二楼", "箱子", "门后") using game-specific fine-tuning.
  - Responds to compound commands: "throw flashbang then push the door."
- The production lessons — the more interesting part:
  - **Latency budget**: each command must respond in <2 seconds. The team designed a hybrid cloud + edge architecture.
  - **Cost**: scaling an LLM per-player-per-game-session is expensive. F.A.C.U.L. uses distilled smaller models for most interactions and the full model only for ambiguous commands.
  - **Safety**: agents can refuse commands that would grief the player or break the game economy.
  - **QA**: how do you test an LLM-driven feature? The team built a synthetic player pool that generates thousands of voice commands per day for regression testing.
- Player reception: 75% of players who tried the feature kept it on; the most engaged players were *social-avoidant* single-player-FPS players who wanted cooperative play but didn't want the social cost of playing with humans.

## Why it matters for game creation

- This is the **first large-scale production deployment** of an LLM as a player-facing feature in an FPS. Everything before was prototype.
- The cost-latency-safety pattern (distilled model + LLM escalation + safety filter) is the template every other studio is now copying.
- The "social-avoidant" player finding is the unexpected product insight: the feature worked because it solved a real player need, not because AI was trendy.

## Why it's borderline for this vault

- The F.A.C.U.L. system itself is an in-game AI teammate. Strictly, that's out-of-scope.
- The talk's actual value is the *production lessons* — how to build, deploy, and pay for an LLM in a live game. Those lessons are useful to anyone shipping AI tooling, not just NPCs.

## Related notes

- [[2025-Tencent-Tianmei-AICoachingHonorOfKings|天美 — AI Coaching (parallel LLM-in-production story)]]
- [[2025-Tencent-GiiNEX-AIUGC|GiiNEX — AIUGC platform]]
- [[2026-Tencent-Tianming-AgenticAI|天美 — Agentic AI]] (next iteration of the same team's thinking)

## Sources

- 搜狐: 腾讯 AI 技术革新 GDC 2025 深度解析
- 触乐: F.A.C.U.L. talk recap
- 腾讯互娱 official
