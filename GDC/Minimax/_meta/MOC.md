---
title: GameDevVault / GDC / Minimax
type: moc
tags: [moc, index]
last_updated: 2026-06-20
---

# GameDevVault / GDC / Minimax

Curated GDC talks on **AI that MAKES / CREATES video games** — generative content, AI pipelines, neural rendering, world models, AI-native engines.

Skip in-game AI (NPC behavior, combat AI, bots, enemy tactics).

## 2026 — GDC 2026 (San Francisco, March 9–13)

The "Change the Game" year. GDC officially rebranded to "GDC Festival of Gaming." 100+ AI sessions, >110% YoY growth. First year with Chinese vendors (Tencent, etc.) bringing more AI sessions than any other region.

### Anchor talks

- [[2026-GoogleDeepMind-Genie3-PlayableWorlds|Google DeepMind — Genie 3 / Playable Worlds]] — World model that generates playable 3D environments in real time. DeepMind's first GDC stage talk.
- [[2026-Tencent-ChenDong-AIPipelineEvolution|Tencent — Chen Dong: AI 时代下腾讯游戏的技术演进]] — Headline Tencent talk at the GDC Summit. 21 sessions; this is the strategy one.
- [[2026-Tencent-VISVISE-FullPipeline|Tencent — VISVISE: AIGC Game Art Pipeline]] — Text-to-animation, video-to-motion, auto-rigging, MIB in-betweening, Meshgen-3D, deployed in 90+ Tencent games.
- [[2026-Tencent-Tianming-AgenticAI|Tencent (天美) — Yu Yu & Mou Qian: Agentic AI / 可微智能]] — 98% AI-coded large project. The "AI-native game studio" thesis.
- [[2026-Tencent-MagicDawn-AIGlobalIllumination|Tencent (魔方) — MagicDawn: AI-Powered Global Illumination]] — AI GI baked at cloud scale, runtime spatial audio. Case study on 《洛克王国：世界》.
- [[2026-Tencent-HaoYang-AIDrivenPrototype|Tencent (光子) — Hao Yang: AI-Driven 3D Game Prototyping in Engine]] — Practical prompt-to-game-prototype talk. See also: full PPTX deck + slide source under `AI-Driven 3D Game Prototyping - GDC 2026/`.
- [[2026-Tencent-MagicStudio-RealTimeMotionGeneration|Tencent Magic Studio — Real-time AI Motion Generation (Liao Shiyang)]] — First shipping case of real-time generative AI motion in a free-to-play fighting game 《异人之下》. 0.4 ms/frame INT8 inference, 78% time-per-transition reduction. Full PPTX deck under `Tencent Magic Studio - Real-time AI Motion Generation - GDC 2026/`.

### Panels & industry

- [[2026-Panel-TripoBitmagicGlassBead|Tripo AI / Bitmagic / Glass Bead / GenAI Assembling — AI Game Creation Panel]] — "AI-native engine" founders: 3D generation, prompt-play-iterate, 4-person team running on agents.
- [[2026-Perforce-P4MCP-UEPlugin|Perforce — P4 MCP & P4 One (UE Plugin)]] — Natural-language queries over Perforce repos for AI tools. Creator-in-the-loop framing.

## 2024 — GDC 2024 (San Francisco, March 18–22)

The "AI is everywhere" year. AI was officially the dominant theme. 64 of 773 sessions (~8%) were AI-tagged. GDC industry report: 49% of devs using gen-AI tools. 16 AI Summit sessions, 14 Machine Learning Summit sessions. Strong showing from Tencent (15 sessions), NetEase, ByteDance, and Western vendors (NVIDIA, Microsoft, Ubisoft, Roblox).

### Anchor talks

- [[2024-Tencent-GiiNEX-Launch|Tencent — GiiNEX Launch]] — The first public launch of Tencent AI Lab's full-lifecycle game AI engine. 5 days → 25 min for 25 km² city, 50× speedup for building facade, 40× for indoor mapping. Decision-AI + generative-AI in one platform. UGC tools live in 《元梦之星》. **Foundation talk** for everything in the 2025/2026 Tencent series.

## 2025 — GDC 2025 (San Francisco, March 17–21)

The "from concepts to deployments" year. 50+ AI sessions. 52% of devs using gen-AI tools (GDC industry survey). 41 sessions from Chinese studios (Tencent alone: 20).

### Anchor talks

- [[2025-NVIDIA-AdvancesInRTX-NeuralRendering|NVIDIA — Advances in RTX: Neural Rendering]] — John Spitzer / Martin Stich / Aaron Lefohn. The defining graphics talk of the year.
- [[2025-NVIDIA-NeuralShading-DirectX|NVIDIA + Microsoft — Neural Shading in DirectX]] — Cooperative announcement, ships April 2025. Neural networks inside the shader pipeline.
- [[2025-NVIDIA-RTXKit-UE5|NVIDIA — RTX Kit in Unreal Engine 5 (Mega Geometry + Hair)]] — 100× triangle density, LSS hair primitives.
- [[2025-NVIDIA-RTXRemix-HalfLife2|NVIDIA — RTX Remix & Half-Life 2 RTX]] — Generative mod remastering.
- [[2025-Tencent-Magic-FACUL-AITeammate|Tencent (魔方) — F.A.C.U.L.: First Human-Language FPS AI Teammate]] — Production-scale LLM-controlled teammate in 《暗区突围》. Borderline in-game AI; included for the production lessons.
- [[2025-Tencent-Tianmei-AICoachingHonorOfKings|Tencent (天美) — AI Coaching in Honor of Kings]] — LLM-powered personalised coaching. Included for the production-deployment story.
- [[2025-Tencent-GiiNEX-AIUGC|Tencent (GiiNEX + 元梦之星) — AIUGC Platform]] — Prompt-to-3D-scene platform used in shipping game.
- [[2025-Tencent-Photon-LIGHTCRAFT-LIGHTBOX|Tencent (光子) — LIGHTCRAFT Procedural Assets + LIGHTBOX Tooling]] — Programmatic building/asset generation + deployment platform.
- [[2025-Tencent-Photon-MLP-NeuralBuildings|Tencent (光子) — MLP GI Compression + Neural Building Generation]] — Neural radiance compression + neural+procedural building pipeline.
- [[2025-Tencent-PCG-AncientCities|Tencent — PCG Reconstruction of Ancient Cities]] — How AI + rules + historical data recreate Chinese imperial cityscapes.
- [[2025-GoogleDeepMind-SIMA|Tencent-GoogleDeepMind — SIMA Agent (GDC 2025)]] — Generalist agent across many 3D games.
- [[2025-GoogleDeepMind-Gemini-GameDev|Google DeepMind — Gemini + Gemma for Game Development]] — GenAI assistants for studio workflows.
- [[2025-Roblox-Cube3D|Roblox — Cube 3D]] — Open-source text-to-3D model; shipped to all Roblox creators.
- [[2025-Meshy-3DAssetWorkflow|Meshy — AI 3D Asset Workflow]] — 3D generation integrated with ZBrush / Blender pipelines.
- [[2025-InworldAI-Inworld|Inworld AI — Inworld for UGC & Production]]
- [[2025-BrendanGreene-PrologueGoWayback|Brendan Greene — Prologue: Go Wayback! (AI Generated Maps)]]
- [[2025-Proxima-SuckUp|Proxima Studio — Suck Up! (LLM-driven NPC interactions)]]
- [[2025-Keywords-Studios-AIPipelineCritique|Keywords Studios — AI in the Production Pipeline]] — Critical practitioners' view: "too many people thinking about better AI, too few about better products."
- [[2025-DMM-AILocalization|DMM — Human-AI Co-pilot for Game Localization]] — 50 games localized in 6 months.

## Out of scope (skipped)

- Most anti-cheat ML talks (in-game system).
- Most NPC behavior / combat AI / enemy tactics talks.
- Pure matchmaking / retention / personalization.
- Streaming/cloud gaming (Amazon GameLift Streams) — distribution, not creation.

## Sources

- GDC official schedule / GDC Vault
- Tencent Game Tech public recaps
- NVIDIA GDC 2025 technical blog series
- Google DeepMind blog + 第三方 reports (DVG, 触乐, 腾讯研究院)

## Curator

- This vault is maintained by the `gdc-writing` cron curator (hourly). Each run adds new talks and refreshes the MOC.
