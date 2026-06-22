---
title: Tencent (魔方) — MagicDawn: AI-Powered Global Illumination
type: talk
tags: [talk, gdc-2026, topic/rendering, topic/neural-rendering, impact/high, studio/tencent-mofang]
date: 2026-03-12
gdc_year: 2026
speakers: [冯升 (魔方 首席技术美术), 陳家銘 (魔方 首席引擎程序员), 张震元 (MagicDawn 高级研发工程师)]
venue: GDC 2026 — Tencent session
title_cn: 点亮洛克世界：高性能全局光照方案的最佳实践
status: covered (Tencent, 博客园, 游戏葡萄)
---

# Tencent (魔方) — MagicDawn: AI-Powered Global Illumination

## TL;DR

The first AI-driven cross-engine global illumination solution to ship at scale in a mobile + PC open-world game. MagicDawn bakes dynamic TOD (time-of-day) GI in the cloud and runs spatial audio with neural+ray-tracing hybrid at runtime. Deployed in 5+ shipped games including 《暗区突围》《暗区突围：无限》《鸣潮》《洛克王国：世界》《王者荣耀：世界》. Cuts GI bake time from days to hours.

## What the talk covered

- The three pain points of mobile open-world GI:
  1. **Baking time**: traditional GI baking takes days, blocks iteration.
  2. **Storage cost**: 24-hour TOD needs 24 hours of lightmaps.
  3. **Multi-platform parity**: mobile gets the "downgraded" version, PC gets the real one — the experience gap is visible.
- MagicDawn's answer:
  - **Cloud-distributed baking**: lift the bake to cloud GPUs. Time reduction: tens-of-x (day → hours).
  - **CLV (Compact Light Volume)** proprietary compression: keeps memory stable even on phones, with high-fidelity visual output.
  - **AI + ray-tracing spatial audio**: use AI to migrate optical methods (denoising, sampling) into acoustic simulation. Players can "hear" the shape of a virtual room.
  - **Cross-engine**: works on Unity, Unreal, custom engines. This is the explicit differentiator vs. engine-bundled solutions.
  - **Cross-platform**: same GI output on PC and mobile — the parity story is the production story.
- Case study: 《洛克王国：世界》. 24-hour TOD GI, mobile+PC parity, custom dynamic time-of-day with art-directable parameters.
- Honest claim: "All technical breakthroughs ultimately serve artistic creation" (所有技术突破最终都服务于艺术创作). The tool is a multiplier on art, not a replacement.

## Why it matters for game creation

- This is the **first major AAA mobile title to ship a fully AI-driven GI pipeline** in production. Most "neural rendering" demos at GDC are pre-rendered; MagicDawn is in the shipped product.
- The cross-engine design choice is important: it means studios don't have to migrate to a new engine to get the benefit. For Unity-heavy and bespoke-engine studios, this lowers the adoption bar.
- The spatial audio piece is a sleeper: visual AI gets all the press, but audio is the harder unsolved problem. Using AI to port optical methods is a clever cross-domain move.

## Limitations / open questions

- Cloud-bake cost is real; no public per-frame or per-km² numbers.
- Spatial audio quality is "objectively measurable" but no listener-study data shared.
- Tooling maturity vs. baked-in solutions (Unreal Lumen) is unproven across studios outside of Tencent's portfolio.

## Related notes

- [[2025-NVIDIA-AdvancesInRTX-NeuralRendering|NVIDIA — neural rendering]]
- [[2025-NVIDIA-RTXKit-UE5|RTX Kit / Mega Geometry]]
- [[2026-Tencent-ChenDong-AIPipelineEvolution|Tencent AI strategy]]

## Sources

- 博客园企业博客: MagicDawn 亮相 GDC 2026
- 腾讯魔方工作室 official GDC 2026 release
- 冯升/陈家铭/张震元 talk write-ups
- MagicDawn product page (tencent.com)
