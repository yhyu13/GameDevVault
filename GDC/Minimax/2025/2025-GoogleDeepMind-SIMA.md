---
title: Google DeepMind — SIMA Agent
type: talk
tags: [talk, gdc-2025, topic/agent, topic/research, impact/medium, studio/google-deepmind]
date: 2025-03
gdc_year: 2025
speakers: [Google DeepMind SIMA team]
venue: GDC 2025
status: covered (DeepMind blog, third-party recaps)
---

# Google DeepMind — SIMA Agent

## TL;DR

SIMA (Scalable Instructable Multiworld Agent) is a DeepMind research project on a generalist agent that follows natural-language instructions in any 3D game. Not a shipped product, but the most-cited research demo of "AI plays games you didn't train it on." Included here for the *training-environment* angle — SIMA requires procedurally generated game worlds to learn in, which feeds back into the world-generation research.

## What the talk covered

- The goal: an agent that can take a plain-English command like "go to the red building and pick up the blue object" in any 3D game and execute it using only keyboard + mouse (no API access).
- The training methodology:
  - SIMA was trained on a **portfolio of commercial and research games** (No Man's Sky, Valheim, Goat Simulator 3, and several custom research games).
  - Each game is paired with a human-annotated instruction dataset ("go to X" → behavior trace).
  - The agent is trained to predict the next action from pixels + instruction.
- The result: SIMA executes 600+ instruction types across 10+ games without per-game fine-tuning.
- The 2025 update integrates **Gemini** as the language-understanding layer.

## Why it matters for game creation

- The most important signal: **the games that train SIMA are the games that ship in 2025–2026**. Studios whose games appear in SIMA's training set get early visibility into where the agent-tech industry is heading.
- The training approach requires **diverse, procedurally generated worlds**. This is direct validation of the world-generation research at Google (Genie 2 → Genie 3).
- For game designers: the question "would a natural-language instruction-following agent enjoy this game?" becomes a new design test.

## Why it's borderline

- SIMA is an AI that *plays* games, not one that *makes* games.
- Included because: (a) it drives demand for generated worlds, (b) it changes how games are designed, and (c) it's the most-discussed DeepMind game-AI work in 2025.

## Related notes

- [[2026-GoogleDeepMind-Genie3-PlayableWorlds|Genie 3]] (the world-generation companion to SIMA)
- [[2025-GoogleDeepMind-Gemini-GameDev|Gemini for game dev]] (overlapping team)

## Sources

- DeepMind blog: SIMA 2 announcement
- arxiv papers: SIMA-1, GVGAI-LLM benchmark
- 腾讯研究院 GDC 2025 recap
