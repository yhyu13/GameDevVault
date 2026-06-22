---
title: NVIDIA + Microsoft — Neural Shading in DirectX
type: talk
tags: [talk, gdc-2025, topic/neural-rendering, topic/api, impact/high, studio/nvidia-microsoft]
date: 2025-03
gdc_year: 2025
speakers: [John Spitzer (NVIDIA), Shawn Hargreaves (Microsoft Direct3D), Andrew Burnes (NVIDIA)]
venue: GDC 2025 — joint session
status: covered (NVIDIA blog, IGN 中国, IT168)
---

# NVIDIA + Microsoft — Neural Shading in DirectX

## TL;DR

The single most industry-shaping announcement of GDC 2025. NVIDIA and Microsoft jointly announced **Cooperative Vectors** in the April 2025 DirectX preview, which lets developers run small neural networks *inside* the shader pipeline. This effectively makes neural shading a cross-vendor graphics API, not an NVIDIA-only feature.

## What was announced

- **Neural shading** = small neural networks called from within shader code.
- Built on a new DirectX feature called **Cooperative Vectors**: the GPU scheduler understands tensor ops alongside vector ops.
- Targets: per-pixel denoising, neural material evaluation, learned BRDFs, neural texture compression, neural lighting.
- **Cross-vendor**: any DirectX-12-supporting GPU can implement Cooperative Vectors. The API is hardware-agnostic.
- **Performance numbers** quoted by Microsoft:
  - 30%+ framerate uplift in scenes using neural denoising.
  - 2× detail precision in material evaluation.
  - 40% memory reduction in neural texture compression.
- April 2025 DirectX preview ships with the API; production SDK later in 2025.

## Why it matters for game creation

- Before this announcement, neural shading was an NVIDIA RTX-only path. Now it's an industry standard. Studios can target it without fear of vendor lock-in.
- For Unreal and Unity: expect Cooperative Vector support to land in mainline within 1–2 engine versions.
- For asset creators: the API enables **neural assets** — textures and materials that aren't pixel data but small networks. This is a new content type that existing tools don't yet author.
- For indies: the lowered hardware cost (any DirectX 12 GPU) makes the technique broadly deployable.

## What was *not* announced

- No AMD or Intel hardware with Cooperative Vector silicon confirmed (they have software support).
- No specific "neural assets" standard file format.

## Related notes

- [[2025-NVIDIA-AdvancesInRTX-NeuralRendering|NVIDIA — Advances in RTX]]
- [[2025-NVIDIA-RTXKit-UE5|RTX Kit in Unreal Engine 5]]

## Sources

- NVIDIA Technical Blog
- Microsoft DirectX developer blog
- IGN 中国 coverage
- IT168
