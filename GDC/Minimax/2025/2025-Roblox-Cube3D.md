---
title: Roblox — Cube 3D
type: talk
tags: [talk, gdc-2025, topic/3d-generation, topic/ugc, impact/high, studio/roblox]
date: 2025-03
gdc_year: 2025
speakers: [Roblox AI team]
venue: GDC 2025
status: covered
---

# Roblox — Cube 3D

## TL;DR

Roblox's open-source **text-to-3D model** foundation model. The first time a major UGC platform has shipped an in-house generative 3D model to all its creators. The most-cited "AI for UGC" milestone of GDC 2025.

## What the talk covered

- Cube 3D is Roblox's foundation model for **text-to-3D mesh generation**.
- Trained on a mix of licensed 3D assets, Roblox's own user-generated content (with opt-out respected), and synthetic data.
- Output: a textured 3D mesh, ready to drop into a Roblox experience.
- Open-sourced the model weights and training methodology.
- Deployed to all Roblox creators as a built-in tool in the Roblox Studio.
- Quality tier: not photoreal. Aimed at Roblox's signature blocky / low-poly aesthetic.

## Why it matters for game creation

- Roblox is the **largest UGC game platform in the world** by user-generated-content volume. Shipping an in-house 3D-gen model to all of them is the biggest single deployment of "AI gives players creative superpowers" in 2025.
- Open-sourcing the weights is the strategically important move. It signals to the industry that Roblox is positioning itself as the platform, not the model vendor.
- For other UGC platforms (Rec Room, Manticore, etc.), this raises the bar. Players will expect "I can type a prompt and get an asset."

## Limitations

- The model is Roblox-stylized; not general-purpose.
- Quality is "good enough for Roblox" not "AAA quality." Fine for props and background; not for hero assets.
- Doesn't solve animation, rigging, or gameplay logic.

## Related notes

- [[2025-Meshy-3DAssetWorkflow|Meshy]] (competing 3D-gen product)
- [[2025-Tencent-GiiNEX-AIUGC|Tencent AIUGC]] (parallel in-game UGC platform)
- [[2025-InworldAI-Inworld|Inworld AI]] (UGC character generation)

## Sources

- Roblox official press release
- GDC 2025 schedule
- 腾讯研究院 recap
