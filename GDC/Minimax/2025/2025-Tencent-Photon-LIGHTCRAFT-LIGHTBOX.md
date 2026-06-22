---
title: Tencent (光子) — LIGHTCRAFT Procedural Assets + LIGHTBOX Tooling
type: talk
tags: [talk, gdc-2025, topic/procedural-generation, topic/dev-tools, impact/medium, studio/tencent-photon]
date: 2025-03
gdc_year: 2025
speakers: [光子工作室群 艺术部]
venue: GDC 2025
title_cn: LIGHTCRAFT 程序化资产生成 + LIGHTBOX 工具平台
status: covered
---

# Tencent (光子) — LIGHTCRAFT Procedural Assets + LIGHTBOX Tooling

## TL;DR

Two production-deployed tools from 光子 (Lightspeed Studios):
- **LIGHTCRAFT**: a flexible procedural-asset-generation pipeline. Generates buildings, props, and environments from rule-based + data-driven templates.
- **LIGHTBOX**: a deployment platform for internal tools. Surfaces tools, tasks, and assets in a unified UI for the art team.

## What the talk covered

### LIGHTCRAFT

- The asset-generation problem: open-world games need thousands of unique buildings. Hand-authoring each one is impossible; copy-paste looks bad.
- LIGHTCRAFT is a **rule-based + data-driven** procedural system. Designers define grammar rules ("facade must have at least one window per 3m"), and the system generates thousands of unique buildings that satisfy the rules.
- **Neural + procedural hybrid**: for specific asset classes (e.g. building facades), LIGHTCRAFT uses a neural network to suggest variations; the procedural system enforces the rules.
- Output: LOD-ready, engine-ready meshes. Direct drop-in to the production pipeline.
- Deployed in 《和平精英》 and other open-world titles.

### LIGHTBOX

- The tool-fatigue problem: art teams use 20+ tools daily. Each tool has its own UI, its own asset-format, its own version control story.
- LIGHTBOX is a **unified deployment surface**. Tools are packaged as LIGHTBOX plug-ins; the artist sees a single UI with task queues, asset previews, and tool actions.
- Solves the "where is the version of this asset" problem by integrating with the studio's DAM.
- Deployed across all of 光子.

## Why it matters for game creation

- LIGHTCRAFT is the **most-shipped procedural asset system from a Chinese studio** in 2025. Most "PCG" talks are research; this is production.
- The "neural + procedural hybrid" is the most important design pattern: pure procedural looks mechanical; pure neural looks unstable. Hybrid is the way.
- LIGHTBOX is the less-glamorous but more important story. The "AI tool sprawl" problem is real: studios that adopt 10 AI tools need a way to manage them, or artists won't use them. LIGHTBOX is a model for the industry.

## Limitations

- LIGHTCRAFT is rule-heavy to set up. The first month of a new asset class is mostly grammar writing.
- LIGHTBOX is a custom in-house tool, not a product. Other studios have to build their own version.

## Related notes

- [[2025-Tencent-Photon-MLP-NeuralBuildings|光子 — MLP GI + Neural Buildings]]
- [[2025-Tencent-PCG-AncientCities|Tencent — PCG Ancient Cities]]
- [[2026-Tencent-VISVISE-FullPipeline|VISVISE]] (AIGC side of the same studio's toolset)

## Sources

- 网易: 看见 GDC 2025 — 全球化的光子
- 腾讯互娱 official GDC 2025 recap
- 游戏茶馆
