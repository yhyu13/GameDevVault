---
title: Meshy — AI 3D Asset Workflow
type: talk
tags: [talk, gdc-2025, topic/3d-generation, topic/pipeline, impact/medium, studio/meshy]
date: 2025-03
gdc_year: 2025
speakers: [Meshy team, Shutterstock Studios partner]
venue: GDC 2025
status: covered
---

# Meshy — AI 3D Asset Workflow

## TL;DR

Meshy is one of the most-used **AI 3D generation** services for game studios. Their GDC 2025 talk focused on the practical workflow of integrating Meshy output with traditional tools (ZBrush, Blender) and on the **copyright / IP** issues that come with generated assets.

## What the talk covered

- The Meshy product:
  - Text-to-3D, image-to-3D, text-to-texture.
  - Multiple art styles (realistic, cartoon, voxel, anime).
  - Per-asset fine-tuning with reference images.
- The integration workflow with traditional tools:
  - Meshy output as a **starting base** (not final asset).
  - ZBrush for silhouette + detail refinement.
  - Blender for rigging + animation.
  - Substance for texturing passes.
- The **copyright and IP** discussion:
  - The team acknowledged training data is mostly proprietary / licensed; outputs are owned by the user.
  - **Shutterstock Studios** partnership: Shutterstock-licensed image → Meshy 3D output → guaranteed commercial use.
  - Recommended studios establish a clear AI-asset policy: which tools, which outputs, what data was used.
- Practical case studies: small studios shipping 50-asset game in 3 months using Meshy for 80% of props.

## Why it matters for game creation

- Meshy is the **most-used third-party AI 3D tool** by small-to-mid studios. The "starting base, then ZBrush refine" workflow is the dominant pattern.
- The **copyright / IP partnership** (Shutterstock) is a model other AI vendors are copying. Studios that care about commercial-safe outputs need this kind of guarantee.
- For indie studios, the "50-asset game in 3 months" case study is the most-relatable AI productivity claim.

## Limitations

- Quality of generated assets is style-dependent. Realistic = good. Stylised cartoon = hit-or-miss.
- Meshy output often needs significant hand-refinement for hero assets.
- No animation generation in the base product.

## Related notes

- [[2025-Roblox-Cube3D|Roblox Cube 3D]] (competing / complementary)
- [[2025-Tencent-GiiNEX-AIUGC|Tencent AIUGC]] (in-game UGC platform)
- [[2025-Keywords-Studios-AIPipelineCritique|Keywords — production critique]] (same "ship, don't demo" theme)
- [[2026-Tencent-VISVISE-FullPipeline|VISVISE]] (Tencent's in-house equivalent)

## Sources

- Meshy official
- Shutterstock GDC 2025 booth
- 腾讯研究院 GDC 2025 recap
