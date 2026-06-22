---
title: Tencent (天美) — AI Coaching in Honor of Kings
type: talk
tags: [talk, gdc-2025, topic/llm-in-game, topic/production-case-study, impact/medium, studio/tencent-tianmei]
date: 2025-03
gdc_year: 2025
speakers: [Tencent 天美工作室群 AI Coaching team]
venue: GDC 2025
title_cn: AI Coaching 王者荣耀人工智能辅导方案
status: borderline — included for production-deployment story
---

# Tencent (天美) — AI Coaching in Honor of Kings

## TL;DR

Borderline for this vault — the AI Coaching system in 《王者荣耀》 is an in-game LLM-powered personalised coach. Included because the talk covered the production lessons: how a 200M-MAU mobile MOBA shipped an LLM-driven feature without breaking latency, cost, or content moderation.

## What the talk covered

- Feature: after each match, the player gets a personalised voice + text coaching session. The AI reviews the replay, identifies the top 3 mistakes, and explains them in language appropriate to the player's rank.
- Architecture:
  - Match data → structured insight layer → LLM.
  - LLM output → text-to-speech with character voices.
  - Two model tiers: cheap distilled model for the bottom 80% of cases; full model only for high-engagement or paying users.
- Content moderation: every coaching line is pre-screened against a game-design policy library. The LLM can be told "no, this advice is bad for the meta" and re-write.
- Latency: most sessions are pre-generated, not real-time. The "AI coach" appears to respond in real time but the heavy compute is done in the background.
- Player results: 23% improvement in next-match win-rate among coached players; huge spike in new-player retention.

## Why it matters for game creation

- The pattern (distilled model + escalation + policy filter + pre-generation) is identical to F.A.C.U.L. — confirming it's the dominant 2025 production pattern.
- The pre-generation trick is the cost-saver: a 2-minute coaching session can be drafted offline and streamed to the player without burning inference during peak play.
- The "policy filter" approach to moderation is more sustainable than post-hoc content review. Other studios adopting LLM-driven features should copy this.

## Why it's borderline

- AI Coaching is an in-game system, not a creation tool.
- Included for the production-deployment lessons, same logic as F.A.C.U.L.

## Related notes

- [[2025-Tencent-Magic-FACUL-AITeammate|魔方 — F.A.C.U.L.]]
- [[2026-Tencent-Tianming-AgenticAI|天美 — Agentic AI]]

## Sources

- 腾讯游戏学堂 official recap
- GDC 2025 official schedule
- 搜狐: 腾讯 AI GDC 2025
