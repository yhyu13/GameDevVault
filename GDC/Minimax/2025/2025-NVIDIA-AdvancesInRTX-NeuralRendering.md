---
title: NVIDIA — Advances in RTX: Neural Rendering
type: talk
tags: [talk, gdc-2025, topic/neural-rendering, topic/hardware, impact/high, studio/nvidia]
date: 2025-03-19
gdc_year: 2025
speakers: [John Spitzer (VP Dev & Perf Tech), Martin Stich (Director of Engineering), Aaron Lefohn (VP Graphics Research)]
venue: GDC 2025 — NVIDIA Information Booth C1819
status: covered (NVIDIA Developer blog, IGN 中国, IT168)
---

# NVIDIA — Advances in RTX: Neural Rendering

## TL;DR

The defining graphics talk of GDC 2025. NVIDIA laid out the **neural rendering** roadmap for RTX, anchoring it on the Blackwell GPU generation, DirectX partnership, and a slate of new tools (RTX Mega Geometry, RTX Hair, Zorah demo). The talk effectively renamed "ray tracing" to "neural rendering" for the next decade of real-time graphics.

## What the talk covered

- The thesis: **every pixel of a future game will be touched by AI**. Neural rendering = compute + AI prediction, replacing full real-time computation with learned approximations.
- The Zorah demo (new version at GDC 2025) showcases the full RTX Kit:
  - RTX Mega Geometry: 100× triangle count vs. current standards. Open worlds with billions of triangles.
  - RTX Hair: LSS (Linear-Swept Spheres) primitive for hair/fur, hardware-accelerated on RTX 50 series.
  - Path tracing with neural radiance caching.
  - RTX Skin / Subsurface.
- DirectX partnership: **Cooperative Vectors** in the April 2025 DirectX preview. Neural networks inside the shader pipeline, on any DirectX-supporting GPU. AMD and Intel users get the same benefits via the standardised API.
- DLSS 4 milestone: **100+ games** at launch, including God of War Ragnarok, Alan Wake 2, Rise of the Ronin, Diablo IV, THE FINALS, and the Chinese 3A slate (失落之魂, 影之刃零, 湮灭之潮).
- RTX Remix + Half-Life 2 RTX: free demo on Steam, March 18, 2025. Showcase for AI-augmented classic remastering.
- A clear long-term vision: 3D model creation may shift away from triangle-mesh authoring entirely, toward AI-generated geometry that understands the scene.

## Why it matters for game creation

- This talk reset the bar for what "real-time graphics" means. Studios that planned their roadmaps around traditional rasterisation now have to recalibrate.
- For indie studios, the **DirectX standardisation** is the biggest deal. Neural shading is no longer locked to NVIDIA hardware; it's a cross-vendor API.
- For asset creators, the implication is that *more* geometric detail becomes affordable, which means *higher* expectations per scene. The "good enough" bar rises.
- RTX Remix / Half-Life 2 RTX is a blueprint for AI-assisted remastering. The same pattern applies to old IPs the publisher wants to relaunch on modern hardware.

## Limitations (acknowledged in the talk)

- Best results still need high-end hardware. RTX 30 series users reported "can't run it" for Zorah.
- DLSS 4's multi-frame generation produces artefacts at very low base framerates.
- Neural radiance caches need per-scene training; they don't transfer cleanly across scenes.

## Related notes

- [[2025-NVIDIA-NeuralShading-DirectX|NVIDIA + Microsoft — Neural Shading]]
- [[2025-NVIDIA-RTXKit-UE5|RTX Kit in Unreal Engine 5]]
- [[2025-NVIDIA-RTXRemix-HalfLife2|RTX Remix & Half-Life 2 RTX]]
- [[2026-Tencent-MagicDawn-AIGlobalIllumination|Tencent MagicDawn]] (parallel direction: AI GI from a different vendor)

## Sources

- NVIDIA Technical Blog: NVIDIA RTX Advances with Neural Rendering and Digital Human Technologies at GDC 2025
- IGN 中国: GDC 2025 NVIDIA 神经网络渲染分享会报道
- IT168: NVIDIA GDC 2025 技术汇总
- Bilibili: GDC 2025 NVIDIA RTX session 上传录像
