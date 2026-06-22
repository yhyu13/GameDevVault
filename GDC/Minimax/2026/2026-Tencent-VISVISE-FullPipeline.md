---
title: Tencent — VISVISE: Full AIGC Game-Art Pipeline
type: talk
tags: [talk, gdc-2026, topic/pipeline, topic/animation, topic/3d-generation, impact/high, studio/tencent]
date: 2026-03
gdc_year: 2026
speakers: [葛诚 (Tencent Games AIGC Product Director) and VISVISE team]
venue: GDC 2026 — Tencent booth theatre + dedicated session
status: covered (腾讯, 葛诚 talk write-up)
---

# Tencent — VISVISE: Full AIGC Game-Art Pipeline

## TL;DR

The most concrete end-to-end demonstration at GDC 2026 of generative AI in a shipping art pipeline. VISVISE is a packaged suite of AIGC tools covering animation, rigging, in-betweening, 3D mesh generation, and texture — all tuned for game-engine constraints. The most-quoted new feature: **text-to-animation** with 300+ game-action categories and 80%+ auto-rigging automation.

## What the talk covered

### Text-to-Animation (文生动画)

- Input: natural-language action description ("character climbs, waves forward, dances").
- Output: 3D animation clip, semantically correct, 300+ action categories, 3D-coherent.
- 10-billion-parameter multimodal animation model **MotionGen** under the hood.
- Designed for production: artist types prompt, gets back a clip, can edit keyframes.

### Video-to-Motion (视频动捕)

- Input: any reference video (e.g. a YouTube clip of a taekwondo kick).
- Output: retargeted, engine-ready 3D animation asset.
- Pipeline: human-pose estimation → trajectory tracking → skeleton mapping → standardised BVH/FBX.
- Solves the "we don't have a mocap studio" problem for indie teams.

### MIB (Motion In-Betweening) — AI补帧

- Input: 3–5 keyframes.
- Output: full animation sequence in ~10 seconds.
- Solves the "animator drew the extremes but doesn't want to tween" bottleneck.
- Quality claimed on par with optical mocap in internal benchmarks.

### Meshgen-O — Engine-Ready 3D Generation

- Input: image or text description.
- Output: **quad-dominant topology** mesh with **up to 6 LODs**.
- Solves the "AI mesh is a sealed visual husk" problem: this one drops straight into Unreal/Unity.
- Topology + auto-LOD are the two non-negotiables for game use, and most off-the-shelf tools fail on both.

### Auto Rigging & Skinning

- 80% automation in binding and weighting.
- Defect rate (sliding feet, jitter) under 10%.
- Works for the same 300+ action categories as text-to-animation.

## Why it matters for game creation

- This is the most-shipped AIGC toolchain mentioned at GDC 2026: **90+ games** use it (《和平精英》《PUBG Mobile》plus 88 more).
- The decision to gate on **engine-ready output** (clean topology, LODs, layered parts) is the most important design choice. Most academic / startup tools optimise for visual fidelity; VISVISE optimises for "does it drop into a real project without re-work."
- For an indie studio: the implication is that a 5–8 person team can now do what used to need 30–50 artists. The post-MagicDawn Tencent press claims **80% cost reduction** is achievable for 3D art in some pipelines.
- The 3D-coherence / part-separation feature is the one to watch — it's the gap between "AI demo" and "AI in shipping game."

## Limitations (not in the talk, but worth flagging)

- Action category coverage is biased toward combat and locomotion. Subtle facial animation, complex multi-character interaction, and long-tail action verbs remain weaker.
- The 80% automation claim is for *specific* asset classes (humanoid characters, common weapons, modular environments). Stylised art (cartoon, painterly, anime) is less covered.
- No public access. As of GDC 2026, VISVISE is a partner-only product; no public API.

## Related notes

- [[2026-Tencent-ChenDong-AIPipelineEvolution|Chen Dong — Tencent AI strategy]]
- [[2025-Tencent-Photon-LIGHTCRAFT-LIGHTBOX|光子 — LIGHTCRAFT + LIGHTBOX (programmatic assets + tools)]]
- [[2025-Meshy-3DAssetWorkflow|Meshy — AI 3D asset workflow]]

## Sources

- 葛诚 GDC 2026 talk (Tencent 官方)
- 腾讯官方 GDC 2026 recap
- VISVISE product page (tencent.com)
- 知乎/掘金 VISVISE 技术解析
