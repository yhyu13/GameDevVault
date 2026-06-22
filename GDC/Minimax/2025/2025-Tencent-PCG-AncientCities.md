---
title: Tencent — PCG Reconstruction of Ancient Cities
type: talk
tags: [talk, gdc-2025, topic/procedural-generation, topic/world-recreation, impact/medium, studio/tencent]
date: 2025-03
gdc_year: 2025
speakers: [Tencent PCG team]
venue: GDC 2025
status: covered (触乐, 腾讯互娱)
---

# Tencent — PCG Reconstruction of Ancient Cities

## TL;DR

A case study in using **PCG + AI to reconstruct historical Chinese cities** for open-world games. The team used the Qin-era Xi'an capital as the anchor example. Asset-creation efficiency improved **30×** over hand-authoring the same scope.

## What the talk covered

- The reconstruction target: a historically faithful ancient city with thousands of buildings, city walls, gates, canals, markets, and residential blocks.
- Data sources:
  - Historical texts (city layout, building counts, population estimates).
  - Archaeological surveys (location of walls, gate positions, river paths).
  - Satellite imagery of present-day ruins.
- The pipeline:
  1. **Data layer**: structured data from historians and archaeologists.
  2. **Rule layer**: PCG rules that encode Chinese urban-design grammar (axial symmetry, ward system, canal layout, feng-shui constraints).
  3. **AI layer**: generative models propose buildings and decorations that match the historical style.
  4. **Validation layer**: a domain expert (historian) reviews a sample of generated buildings for accuracy.
- Output: a complete ancient city with thousands of unique, historically plausible buildings. **30× faster than hand-authoring**.
- The talk argued this approach is the only way to ship historically accurate open worlds at modern scope.

## Why it matters for game creation

- The **PCG + AI + domain-expert validation** pattern is the most defensible approach to historical / cultural content. It respects the source material while scaling to game-scale scope.
- The 30× number is large but plausible: hand-authoring 5000 unique Chinese-imperial buildings is years of work; PCG + AI is weeks.
- The pattern generalises to any historically / culturally specific setting: medieval European cities, Edo-period Japan, pre-Columbian Americas.

## Limitations

- Domain expert is the bottleneck. Scaling requires more historians, not more compute.
- The generated cities are "plausible" not "accurate" — they are *inspired* by history, not historically verified.

## Related notes

- [[2025-Tencent-Photon-LIGHTCRAFT-LIGHTBOX|LIGHTCRAFT]] (the procedural-asset sibling)
- [[2025-Tencent-Photon-MLP-NeuralBuildings|Neural + procedural buildings]]
- [[2025-Keywords-Studios-AIPipelineCritique|Keywords — production critique]] (similar focus on shipping, not demos)

## Sources

- 触乐: GDC 上看到如何重建规模宏大的中国古代城市
- 腾讯互娱 official
- 腾讯研究院 reports
