---
title: Curator Changelog
type: meta
tags: [changelog, meta]
last_updated: 2026-06-20
---

# Curator Changelog

## 2026-06-20 (run 2, 08:00) — Preservation + first 2024 entry + Magic Studio 2026 frontmatter

- **Preserved the 27 talks** that the previous cron run (~07:00) had built in its transient session workspace, by copying them into the canonical vault at `C:\Git-repo-my\GameDevVault\GDC\Minimax\`. The 07:00 vault was in a session-workspace path that does not persist between cron invocations, so without this propagation the work would have been lost.
- **Added GDC 2024 section to MOC** with the first GDC 2024 entry (Tencent GiiNEX launch). This fills the biggest gap in the prior coverage (vault had 0 talks for 2024).
- **Added 2026 frontmatter entry for the Tencent Magic Studio motion generation talk**, which previously existed only as a PPTX-deck folder. The 2025 GiiNEX talk and the 2026 Magic Studio talk are now properly cross-referenced in the MOC and the frontmatter files.

### Talks added this run

- `2024-Tencent-GiiNEX-Launch.md` — GiiNEX launch talk, March 20, 2024. The "5 days → 25 minutes for 25 km² city" benchmark that became the most-cited production number of 2024.
- `2026-Tencent-MagicStudio-RealTimeMotionGeneration.md` — frontmatter wrapper for the existing PPTX deck folder (Liao Shiyang, 《异人之下》).

### Other changes

- MOC: added 2024 section, added Magic Studio 2026 link, added cross-references between Hao Yang frontmatter and the corresponding PPTX deck folder.
- Vault structure is now consistent: every talk has either a frontmatter `.md` file under `YYYY/`, or a PPTX-deck folder, or both.

## 2026-06-20 (run 1, ~07:00) — Initial bootstrap

- Created vault structure: `GameDevVault/GDC/Minimax/{2025,2026,_meta}`.
- Wrote Curation Criteria (`_meta/Curation-Criteria.md`).
- Wrote MOC (`_meta/MOC.md`).

### GDC 2026 talks added (6)

- 2026-GoogleDeepMind-Genie3-PlayableWorlds
- 2026-Tencent-ChenDong-AIPipelineEvolution
- 2026-Tencent-VISVISE-FullPipeline
- 2026-Tencent-Tianming-AgenticAI
- 2026-Tencent-MagicDawn-AIGlobalIllumination
- 2026-Tencent-HaoYang-AIDrivenPrototype
- 2026-Panel-TripoBitmagicGlassBead
- 2026-Perforce-P4MCP-UEPlugin

### GDC 2025 talks added (15)

- 2025-NVIDIA-AdvancesInRTX-NeuralRendering
- 2025-NVIDIA-NeuralShading-DirectX
- 2025-NVIDIA-RTXKit-UE5
- 2025-NVIDIA-RTXRemix-HalfLife2
- 2025-Tencent-Magic-FACUL-AITeammate (borderline — included for production lessons)
- 2025-Tencent-Tianmei-AICoachingHonorOfKings (borderline — included for production lessons)
- 2025-Tencent-GiiNEX-AIUGC
- 2025-Tencent-Photon-LIGHTCRAFT-LIGHTBOX
- 2025-Tencent-Photon-MLP-NeuralBuildings
- 2025-Tencent-PCG-AncientCities
- 2025-GoogleDeepMind-SIMA
- 2025-GoogleDeepMind-Gemini-GameDev
- 2025-Roblox-Cube3D
- 2025-Meshy-3DAssetWorkflow
- 2025-InworldAI-Inworld
- 2025-BrendanGreene-PrologueGoWayback
- 2025-Proxima-SuckUp (borderline — included for indie case study)
- 2025-Keywords-Studios-AIPipelineCritique
- 2025-DMM-AILocalization

### Skipped (with reason)

- In-game NPC / combat AI talks.
- Anti-cheat ML (in-game system).
- Matchmaking / retention / personalisation.
- Amazon GameLift Streams (distribution, not creation).
- Hardware-only chip announcements.

## Next run

- Cross-check against GDC Vault official catalogue for missed talks.
- Add GDC 2024 talks if there's bandwidth.
- Update MOC with new entries.
