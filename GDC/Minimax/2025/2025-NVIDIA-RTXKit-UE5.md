---
title: NVIDIA — RTX Kit in Unreal Engine 5 (Mega Geometry + Hair)
type: talk
tags: [talk, gdc-2025, topic/unreal-engine, topic/neural-rendering, impact/high, studio/nvidia-epic]
date: 2025-03
gdc_year: 2025
speakers: [NVIDIA NvRTX team, Epic Games]
venue: GDC 2025 — joint session
status: covered (Bilibili, NVIDIA blog, IGN 中国)
---

# NVIDIA — RTX Kit in Unreal Engine 5 (Mega Geometry + Hair)

## TL;DR

The most concrete "drop into your engine tomorrow" neural rendering talk of GDC 2025. Two new Unreal-5-compatible technologies: **RTX Mega Geometry** for 100× more triangles at the same performance, and **RTX Hair** with the new LSS primitive for sub-strand hair rendering. Both ship in the NvRTX branch.

## What was covered

### RTX Mega Geometry

- Solves the "open-world geometry has exploded past engine budgets" problem.
- AI-driven geometry processing pipeline. Same scene, 100× the triangle count.
- Enables open worlds with **billions of triangles** rather than millions.
- Critical for: open-world AAA, large-scale VR, photoreal cinematics.

### RTX Hair (Linear-Swept Spheres / LSS)

- New GPU primitive designed for curves, not triangles.
- One LSS represents a strand, evaluated with proper light response.
- Much more accurate than triangle-strip approximations of hair.
- Hardware-accelerated on RTX 50 series.
- Impact: better hair/fur/grass in every scene that uses them.

### Zorah Demo (UE5 / NvRTX)

- Showcases the full RTX Kit in a playable scene.
- Path tracing + neural radiance caching + Mega Geometry + Hair.
- Reaches near-cinematic fidelity in real time on high-end RTX.

## Why it matters for game creation

- **For UE5 studios**, both technologies are immediately adoptable through the NvRTX branch. No engine fork required.
- For non-UE5 studios: NVIDIA's API is the de-facto reference. Expect Unity, Godot, and custom engines to follow with similar integrations.
- The Mega Geometry technique is **indirectly generative**: AI pipelines can now generate *much* more detailed geometry, because the engine can hold it. The bottleneck shifts from "can the engine hold this" to "can the artist author / generate it."
- Hair / fur is a sleeper category. Most games have cheap hair because the cost was prohibitive. RTX Hair is the first time sub-strand hair is real-time on consumer hardware.

## Limitations

- RTX 30 series can't run the full Zorah demo.
- Mega Geometry is mostly helpful for static geometry; dynamic geometry still pays traditional cost.
- Adoption in shipping engines other than UE5 is slow.

## Related notes

- [[2025-NVIDIA-AdvancesInRTX-NeuralRendering|NVIDIA — Advances in RTX]]
- [[2025-NVIDIA-NeuralShading-DirectX|NVIDIA + Microsoft — Neural Shading]]
- [[2025-NVIDIA-RTXRemix-HalfLife2|RTX Remix & Half-Life 2 RTX]]

## Sources

- Bilibili: GDC 2025 NVIDIA RTX session
- NVIDIA Technical Blog
- NvRTX GitHub README
