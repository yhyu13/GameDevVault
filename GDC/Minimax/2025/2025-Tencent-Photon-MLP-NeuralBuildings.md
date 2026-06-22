---
title: Tencent (光子) — MLP GI Compression + Neural Building Generation
type: talk
tags: [talk, gdc-2025, topic/neural-rendering, topic/procedural-generation, impact/medium, studio/tencent-photon]
date: 2025-03
gdc_year: 2025
speakers: [光子工作室群 技术团队]
venue: GDC 2025
status: covered
---

# Tencent (光子) — MLP GI Compression + Neural Building Generation

## TL;DR

Two technical sessions from 光子 at GDC 2025 focused on **neural compression and generation for open-world games**. (1) MLP-based compression for global illumination data — drops storage cost by an order of magnitude. (2) Neural + procedural building generation for open-world content.

## What the talk covered

### MLP GI Compression

- The problem: a 24-hour dynamic-time-of-day GI dataset for a single map can be hundreds of GB of lightmap data. Loading + storage kills mobile.
- Solution: train a small MLP (multi-layer perceptron) per map section that takes (position, time-of-day, normal) → outgoing radiance. The MLP is the storage; the inference is the lighting.
- Quality: claimed on par with the original lightmap in head-to-head visual tests.
- Performance: ~10% GPU overhead at runtime.
- Memory: 100× compression on the storage side.

### Neural + Procedural Building Generation

- The system uses **two passes**:
  1. **Neural pass**: a generative model proposes a high-level building layout (mass, silhouette, roof type) based on the surrounding city.
  2. **Procedural pass**: rule-based grammar fills in the details (windows, doors, decoration) following local architectural style.
- Different from LIGHTCRAFT: LIGHTCRAFT is pure procedural; this system adds the neural first pass.
- Result: thousands of unique, stylistically consistent buildings per open-world map.

## Why it matters for game creation

- The MLP GI trick is a **first deployment in a Chinese mobile title**. Before MagicDawn (2026), this was 光子's main GI innovation.
- The hybrid neural+procedural pattern is becoming standard. The "neural first, procedural refine" ordering is the right design choice for content that needs stylistic consistency.
- For studios sitting on large lightmap datasets, the MLP compression approach is worth investigating for any title shipping on storage-constrained platforms.

## Limitations

- Per-map MLP training is a fixed cost. Smaller titles can't amortize it.
- Building generation is style-specific; retraining for a new game's visual direction is a multi-week effort.

## Related notes

- [[2025-Tencent-Photon-LIGHTCRAFT-LIGHTBOX|LIGHTCRAFT + LIGHTBOX]] (the pure-procedural sibling system)
- [[2026-Tencent-MagicDawn-AIGlobalIllumination|MagicDawn]] (the 2026 successor to this GI work)

## Sources

- 网易: 看见 GDC 2025 — 全球化的光子
- 腾讯互娱 GDC 2025 recap
