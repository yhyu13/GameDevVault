---
title: Curation Criteria
type: meta
tags: [criteria, meta, curation]
last_updated: 2026-06-20
---

# Curation Criteria

This vault exists to surface **GDC talks about AI that MAKES / CREATES video games** — generative AI applied to game development, content creation, rendering, and production pipelines.

## IN-SCOPE — Include a talk if it is about

- **Generative content**: AI creating 3D models, textures, animations, audio, levels, dialogue, narrative, quests, dialogue trees.
- **World / level generation**: PCG, neural rendering, world models, runtime environment synthesis.
- **AI in the development pipeline**: code generation, asset pipelines, automation of art/animation/rigging/skinning/QA, AI-assisted localization, anti-piracy/anti-cheat tooling where the talk is about the AI/ML technique.
- **AI-driven rendering**: neural rendering, neural radiance caches, AI denoising, path-tracing acceleration, real-time neural shaders.
- **AI-native engines and tools**: prompt-to-game, AI agents that build games, LLM-driven UGC platforms for players or creators.
- **Process and case studies**: how a studio integrated generative AI into production, what worked, what failed.
- **Future-of-work / industry talks**: only if they specifically address how AI changes the *creation* of games (not the in-game product).

## OUT-OF-SCOPE — Skip if the talk is primarily about

- **In-game AI systems** — NPC behavior, combat AI, enemy tactics, pathfinding, decision trees, state machines, bot coordination.
- **AI as a character** — ACE-style "AI-controlled teammate that plays WITH the player" when the talk is about the gameplay experience, not the production system that built it. (A talk about *how the AI teammate was built and deployed* is borderline — include only if the focus is on the production pipeline.)
- **Pure machine learning on telemetry** — churn prediction, matchmaking, A/B testing, retention modeling, anti-cheat detection unless the talk is itself about the ML technique's novelty.
- **AI in non-games contexts** — film VFX, robotics, general productivity.
- **Hardware / chip announcements** without a games-creation angle.

## Priority tiers (when triaging the 100+ GDC 2026 AI sessions)

- **Tier 1 — Anchor talks**: deep technical talks from major players (Tencent, NVIDIA, Google DeepMind, Roblox, Meshy, Inworld) that set industry direction. Always include.
- **Tier 2 — Practitioner case studies**: how a real studio shipped AI tooling in a live game (pipeline integration, cost reduction, quality bar). Include with one-paragraph note.
- **Tier 3 — Tool demos and panels**: live demos, founder panels, future-of-work roundtables. Include if they introduce a concept or product that isn't already in the Tier 1/2 notes.
- **Tier 4 — Skip**: in-game AI, marketing, hardware-only.

## Naming convention

`YYYY-SpeakerOrCompany-TopicShort.md`

Examples:
- `2026-GoogleDeepMind-Genie3-PlayableWorlds.md`
- `2026-Tencent-ChenDong-AIPipelineEvolution.md`
- `2025-NVIDIA-AdvancesInRTX-NeuralRendering.md`

## Tags

Use Obsidian frontmatter tags: `talk`, `gdc-2026` / `gdc-2025`, `topic/<one-of-above>`, `impact/high|medium`, `studio/<vendor>`.
