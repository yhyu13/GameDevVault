---
title: Tencent (天美) — Agentic AI / 可微智能
type: talk
tags: [talk, gdc-2026, topic/agentic-ai, topic/code-generation, impact/high, studio/tencent-tianmei]
date: 2026-03
gdc_year: 2026
speakers: [余煜 (天美 技术组长), 牟骞 (天美 技术专家)]
venue: GDC 2026
status: covered (腾讯研究院, 企鹅号)
---

# Tencent (天美) — Agentic AI / 可微智能

## TL;DR

The most provocative talk of GDC 2026: the 天美 (TiMi) studio shared their work on **Agentic AI / 可微智能** — AI agents that autonomously plan, code, debug, and even ingest design docs to generate programs in a live, large-scale game project. Their internal benchmark hit **98% AI-authored code** in a focused module. This is the strongest public case study so far of an "AI-native game studio."

## What the talk covered

- The **可微智能 (roughly: differentiable / agentic intelligence)** concept: a task is broken into subtasks, the AI plans and executes with minimal human-in-the-loop, and the model is chosen to be just-good-enough rather than state-of-the-art.
- Use cases shown:
  - **Crash analysis**: problems that previously required senior engineers days to investigate are now resolved by an agent in hours.
  - **Bug fixing**: agent reads the bug, proposes a fix, opens a PR.
  - **Design-doc-to-code**: agent reads a design document and generates a runnable feature implementation.
  - **Self-debugging**: agent's own output is checked against runtime and test signals; it iterates.
- The 98% claim refers to a *specific* module of a live game, not the whole codebase. The other 2% was human review of edge cases and integration glue.
- The future-state goal: an AI that can "work in a large project for long periods of time without error" (长时间在大型工程中稳定工作不出错).
- Org implication: 天美 is experimenting with a **dedicated AI-native team** — smaller than a conventional team, structured around prompt-and-review loops instead of feature-team hand-offs.

## Why it matters for game creation

- This is the *first* large-studio public case where the metric is "AI-authored code in a live game project" rather than "AI-assisted assets."
- If Agentic AI works at scale, it changes the cost structure of game development more dramatically than any art-side tool. A team that needs 30 engineers for a 2-year project might need 5 engineers and a fleet of agents for the same project.
- The honest framing matters: 余煜 and 牟骞 explicitly said this is "pure technical experimentation" (纯粹的技术尝试), not yet a productised workflow. The intent is to "walk the road to the end before scaling the pipeline."

## What's novel

- **Self-iteration**: the agent re-reads its own PRs and improves them.
- **Asset + code as one fabric**: the long-term vision is to bundle all project production materials — code, assets, documents — as a single corpus the agent can operate on.
- **Long-horizon task completion**: not "answer this question" but "build this feature, ship it, verify it."

## What we don't know

- Cost numbers (tokens, dollars, runtime) for the 98% benchmark.
- Failure modes the team has observed but didn't share.
- Whether the AI-native team is replacing engineers or augmenting them.

## Related notes

- [[2026-Tencent-ChenDong-AIPipelineEvolution|Chen Dong — strategy talk]]
- [[2025-Tencent-Tianmei-AICoachingHonorOfKings|天美 — AI Coaching (the older LLM-in-game work)]]
- [[2026-GoogleDeepMind-Genie3-PlayableWorlds|Google DeepMind — Genie 3]] (parallel: AI generates the world; 天美 is on AI generates the code)

## Sources

- 腾讯研究院 2026-04
- 企鹅号: 2026 GDC AI 落地答案
- 掘金/知乎 Agentic AI 解析
- GDC 2026 official schedule
