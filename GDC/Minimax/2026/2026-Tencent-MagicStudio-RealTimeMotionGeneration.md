---
title: Tencent Magic Studio — Real-time AI Motion Generation (GDC 2026)
type: talk
tags: [talk, gdc-2026, topic/animation, topic/pipeline, impact/high, studio/tencent-magic]
date: 2026-03-10
gdc_year: 2026
speakers: [Liao Shiyang (廖诗飏), AI Lead, Tencent Magic Studio Group]
venue: GDC 2026 — Main Forum
title_cn: Real-time AI Generation for Action Game Animation
status: covered (deck + summary.md in this folder)
---

# Tencent Magic Studio — Real-time AI Motion Generation (GDC 2026)

## TL;DR

Liao Shiyang's third consecutive year on the GDC main forum. The talk presents a **production-deployed AI pipeline** that generates motion transitions in real time for a free-to-play 3D kung fu fighting game 《异人之下》. The headline numbers: **0.4 ms inference** per frame (INT8 quantized), **78% reduction** in time to produce one transition (90 min → 20 min), **52% reduction** in asset-to-action coverage ratio (1:1 → 0.48:1). Magic Studio's third year on the GDC main forum.

## What the talk covered

### Pipeline (3 stages)

1. **Data — Markerless multi-view mocap**
   - 7 consumer-grade cameras in a small room (no motion-capture stage)
   - Triangulation for joint positions + inertial sensors for spine rotation
   - No marker suits on actors
   - Augmentation: mirror flip, frame-rate rescale, mix-and-fuse initial frames

2. **Model — Lightweight LSTM + multi-encoder + MoE decoder**
   - 4 input encoders: current pose, target pose, offset (diff), future trajectory
   - Decoders split into upper body, lower body, face/hands, plus a Mixture-of-Experts transition decoder
   - **0.4 ms per frame** on game runtime (INT8)

3. **Game Integration — Async inference + post-process**
   - Inference runs off the render path; animation system never blocks
   - Weapon-clipping handled by splitting transitions into phases + Physics Motion Controller (PMC)
   - Multi-character scaling via bone-ratio remapping

### Hard numbers

| Metric | Traditional | AI System | Gain |
|---|---|---|---|
| Model size (FP32 / INT8) | n/a | 15 MB / 6 MB | shippable |
| Inference / frame | n/a | 0.75 ms (FP32) → **0.4 ms** (INT8) | real-time |
| Position error | n/a | < 1 unit | invisible to player |
| Time per transition | **90 min** (30 mocap + 60 cleanup) | **20 min** (5 mocap + 15 cleanup) | **−78%** |
| Asset-to-action ratio | 1.00 : 1 (930 clips / 930 actions) | 0.48 : 1 (445 clips / 930 actions) | **−52%** |

### Headline quote

> *"The path shifts from 'the game engine plays back pre-recorded motion' to 'the game engine generates motion in real time during play.'"* — Liao Shiyang

## Why it matters for game creation

- **First shipping case** of real-time generative AI motion in a free-to-play fighting game.
- For animators: no more hand-keying auxiliary transition frames; focus on hero poses.
- For studios: shipping a new character goes from "re-record and re-key everything" to "shoot a small reference set and let the model adapt."
- This talk is the **production-deployment follow-on** to the offline motion-from-video feature in 2024's `GiiNEX` launch. Two years apart, the model moved from offline asset generation to real-time in-game inference.

## Files in this folder

- `Tencent-Magic-Studio-Real-time-AI-Motion-Generation-GDC2026.pptx` — 13-slide breakdown (Pure Tech Blue palette, pptxgenjs)
- `slides/` — PptxGenJS source (one file per slide, plus `compile.js`)
- `summary.md` — long-form summary

## Related notes

- For the offline motion-from-video feature (predecessor), see `2024-Tencent-GiiNEX-Launch.md`.
- For Tencent's broader art-pipeline strategy, see `2026-Tencent-VISVISE-FullPipeline.md`.
- For Tencent's 2024 talk on reinforcement learning for fighting games (Liao Shiyang's *previous* GDC talk), note: that talk is about in-game AI for 火影忍者 and is OUT OF SCOPE for this vault per curation criteria.
