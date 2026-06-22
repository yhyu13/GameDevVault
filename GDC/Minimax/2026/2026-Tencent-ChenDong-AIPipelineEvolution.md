---
title: Tencent — Chen Dong: AI 时代下腾讯游戏的技术演进和创新之路
type: talk
tags: [talk, gdc-2026, topic/industry-strategy, topic/pipeline, impact/high, studio/tencent]
date: 2026-03-12
gdc_year: 2026
speakers: [陈冬 (Tencent Games CTO, Public Tech)]
venue: GDC 2026 "Summit Series" (杰出者系列) — high-level executive track
status: covered (腾讯研究院, 企鹅号, 站long之家)
---

# Tencent — Chen Dong: AI 时代下腾讯游戏的技术演进和创新之路

## TL;DR

The flagship Tencent talk of GDC 2026 and the only Chinese-vendor executive talk on the GDC Summit Stage. Chen Dong framed Tencent's strategy as **"use cases drive the model"** — pick the most-pressing, most-repetitive production pain point, build a focused model + pipeline for it, ship it, then expand outward. He also shared the headline number: **40+ Tencent games have already shipped with AI features**, and that footprint is growing.

## What the talk covered

- The "蒙皮 → 动画 → 角色定制 → 表情" evolutionary path: Tencent started with **auto-skinning** because that's what artists asked for first ("蒙皮环节重复性劳动太多"), then expanded to auto animation, then character customization, then facial animation. All four are now bundled inside the **VISVISE** product.
- The structural problem with off-the-shelf 3D generation: most models produce "a visual husk" — a closed mesh that doesn't satisfy game-pipeline requirements:
  - No part separation (shoulder armor, skirt flaps, accessories not editable as separate components)
  - No clean topology for animation
  - No automatic LOD / decimation
- 腾讯's response: the **Meshgen-O** architecture that emits **engine-ready quad-dominant meshes with up to 6 LODs**. This is what makes AI output drop-in for a real game pipeline.
- "We make AI act like a real artist responding to a real artist's needs" (让AI像真人一样根据艺术家的需求行动).
- Pipeline philosophy: **artist does concept + key frames; AI does the repetitive 60%**. Final asset must be cleanly layered so the artist can keep editing.
- Org model: Tencent's internal AI push is bottom-up — multiple teams get free tokens + budget to experiment. Some power users burn **200–300M tokens per day**. The output that proves out is then productised.
- Forward-looking: "AI doesn't replace the game industry; it reshapes it." (AI未必会颠覆游戏行业，但一定会重塑游戏行业).

## Why it matters for game creation

- This is the **most-cited 2026 talk by Chinese-language media** about AI in games. It sets the public reference point for "what does AI-native game production look like at scale."
- The "use cases drive the model" framing is the most-quoted strategy quote. It's a counterpoint to Google's "model drives the use case" Genie 3 narrative.
- VISVISE-as-product is significant: it's a packaged studio pipeline, not a research demo. It tells smaller studios that the gap to Tencent-grade tooling is shrinking.
- The 40+ games-shipped number is the strongest data point so far for "AI in shipped games" — most industry surveys (Steam's AI disclosure, GDC 2025's 52%) count *tool use*, not *shipped player features*.

## Specific projects mentioned

- **VISVISE**: AIGC animation, rigging, LOD, retopology, texture, voice — full chain.
- **Meshgen-O**: engine-ready 3D generation.
- **MIB (Motion In-Betweening)**: 3–5 keyframes → full animation in ~10s.
- **MotionGen**: 1B+ parameter multimodal animation model. 80% automation in rigging/skinning; <10% artefacts.
- Deployed in 90+ games including 《和平精英》《PUBG Mobile》.

## What it doesn't cover

- The talk is high-level strategy, not deep technical. The deep technical talks were given by the VISVISE / MagicDawn / 天美 teams separately (see linked notes).
- No revenue or cost data shared.

## Open questions

- Does VISVISE become externally licensed, or stay internal to Tencent / partner studios?
- What's the failure rate of AI-generated assets that pass auto-checks but get rejected by artists in practice?

## Related notes

- [[2026-Tencent-VISVISE-FullPipeline|VISVISE technical deep-dive]]
- [[2026-Tencent-MagicDawn-AIGlobalIllumination|MagicDawn — AI GI]]
- [[2026-Tencent-Tianming-AgenticAI|天美 — Agentic AI / 可微智能]]

## Sources

- 腾讯研究院 (2026-04): 2026 GDC 上的 AI 落地答案
- 站长之家: GDC 2026 报道集
- 网易科技: 腾讯在 GDC 2026 的官方 recap
- GDC 2026 official schedule (summit series)
