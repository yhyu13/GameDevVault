# Tencent Magic Studio — Real-time AI Motion Generation (GDC 2026)

## Short Summary

**Talk:** *Real-time AI Generation for Action Game Animation — The First落地 in Free-to-Play Fighting Games*
**Speaker:** Liao Shiyang (廖诗飏), AI Lead, Tencent Magic Studio Group
**Game referenced:** *异人之下* (a free-to-play 3D kung fu fighting game)
**Venue:** GDC 2026 — Main Forum (invited back for the 3rd consecutive year)
**Date:** March 10, 2026 (Pacific Time)
**Track:** AI in Game / Animation
**Impact:** First time generative AI motion generation has been deployed in a shipped free-to-play fighting game. Magic Studio's third year on the GDC main forum.

---

## The Core Idea

Fighting games need *thousands* of motion transitions between combat states (attack, dodge, idle, sprint, hit-react, get-up, weapon-draw). Traditional methods — mocap for every transition, or hand-keyed inverse kinematics — break down: mocap can't cover every angle, IK slides, weapons clip through bodies. The talk presents a **production-deployed AI pipeline** that generates transition frames in real time, replacing ~half of the mocap asset pool.

## The Pipeline (3 stages)

### 1. Data — Markerless multi-view mocap
- 7 consumer-grade cameras in a small room (no motion-capture stage)
- Triangulation for joint positions + inertial sensors for spine rotation
- No marker suits on actors
- Data augmentation: mirror flip, frame-rate rescale, mix-and-fuse initial frames

### 2. Model — Lightweight LSTM + multi-encoder + MoE decoder
- 4 input encoders: current pose, target pose, offset (diff), future trajectory
- Decoders split into upper body, lower body, face/hands, plus a Mixture-of-Experts transition decoder
- Designed for **real-time inference at 0.4 ms per frame** on game runtime

### 3. Game Integration — Async inference + post-process
- Inference runs off the render path so the animation system never blocks
- Weapon-clipping handled by splitting transitions into phases and adjusting with a Physics Motion Controller (PMC)
- Multi-character scaling via bone-ratio remapping (works for tall, short, weapon-wielding characters)

## Hard Numbers

| Metric | Traditional | AI System | Gain |
|---|---|---|---|
| Model size (FP32 / INT8) | n/a | 15 MB / 6 MB | small enough for shipping |
| Inference time per frame | n/a | 0.75 ms (FP32) → **0.4 ms** (INT8) | real-time |
| Position error | n/a | < 1 unit | invisible to player |
| Time to produce one transition | 30 min mocap + 60 min cleanup = **90 min** | 5 min mocap + 15 min cleanup = **20 min** | **−78%** |
| Asset-to-action coverage ratio | 930 mocap clips for 930 actions (**1 : 1**) | 445 clips for 930 actions (**0.48 : 1**) | **−52%** |
| Combat states covered | finite; many missing transitions | combinatorially generated on demand | effectively infinite |

## Why It Matters

- **For players:** smoother combat, no sliding feet, no weapon-through-body glitches, faster response to inputs.
- **For animators:** no more hand-keying auxiliary transition frames; focus on hero poses instead.
- **For studios:** shipping a new character goes from "re-record and re-key everything" to "shoot a small reference set and let the model adapt."

## Where It Fits The "AI Makes Video Games" Theme

This talk is a textbook case of AI as a *content generator* inside production: the AI does not run inside the gameplay loop (it's not a bot or NPC). It runs at build time and at runtime to *produce animation content* that the human team could not feasibly hand-craft. It belongs in the same vault as Photon's C.A.T prototyping talk — both push the question from "how do we use AI to make games faster" to "how do we redesign the pipeline so AI can be a co-author of the game itself."

## Headline Quote

> *"The path shifts from 'the game engine plays back pre-recorded motion' to 'the game engine generates motion in real time during play.'"* — Liao Shiyang

## Files

- `Tencent-Magic-Studio-Real-time-AI-Motion-Generation-GDC2026.pptx` — 13-slide breakdown
- `slides/` — PptxGenJS source (one file per slide, plus `compile.js`)
- `summary.md` — this file