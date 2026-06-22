---
title: Perforce — P4 MCP & P4 One (UE Plugin)
type: talk
tags: [talk, gdc-2026, topic/dev-tools, topic/ai-pipeline, impact/medium, studio/perforce]
date: 2026-03
gdc_year: 2026
speakers: [Jase Lindgren (Perforce Senior Dev Advocate), Tom Guillermin (Sandfall Interactive co-founder, podcast guest)]
venue: GDC 2026 — Perforce booth + podcast
status: covered (SegmentFault / 龙智 official recap)
---

# Perforce — P4 MCP & P4 One (UE Plugin)

## TL;DR

Perforce's GDC 2026 message: **"creators stay in the driver's seat, AI rides shotgun."** Two product launches: (1) **P4 MCP** — a natural-language server that lets AI tools (Claude Code, Cursor, JetBrains Rider) query P4 asset history and dependencies; (2) **P4 One** — an Unreal Engine plugin for engine-internal asset experiments. The frame is anti-displacement, pro-tooling: humans steer, AI accelerates.

## What was launched

### P4 MCP (Model Context Protocol server)

- Natural-language interface over Perforce P4 repositories.
- Works with Claude Code, Cursor, JetBrains Rider.
- Queries supported: find asset, query change history, reveal dependencies.
- Read & write operations respect the user's existing P4 permissions.
- Released as community-supported.
- Sandfall Interactive (Clair Obscur: Expedition 33) recorded a podcast on how a <50-person team delivered a record-breaking debut title — exemplifies the human-crew-with-AI-tools story.

### P4 One (Unreal Engine plugin)

- Friendly version control for artists and designers.
- **P4 One Experiments** — engine-internal variant generator. Artists can spawn multiple variants of a level or asset inside an active Unreal project without duplicating the whole project.
- Targets the "let me try something without breaking main" workflow.

## Why it matters for game creation

- P4 MCP is the first major version-control vendor shipping a **production-grade AI tool bridge**. Most studios today are bolting AI tooling onto Git with custom MCPs; Perforce is doing the same for the AAA segment.
- The "AI respects existing permissions" line is significant. It addresses the most common enterprise objection to AI-in-the-pipeline: data exfiltration and uncontrolled writes.
- The Experiments plugin addresses the **iterative cost** of Unreal prototyping. Copy-project-to-try-something is the biggest friction in UE workflows; this kills it.
- The human-in-the-loop framing is strategic. GDC audiences are sensitive to "AI replaces artists" rhetoric. Perforce is positioning AI as the layer that handles mechanical work (find this asset, what changed since last week) so humans can stay on creative work.

## What's still missing

- No public benchmarks on how much time P4 MCP actually saves in real pipelines.
- No adoption numbers — only "available now."

## Related notes

- [[2026-Tencent-Tianming-AgenticAI|天美 — Agentic AI]] (same theme: AI in the production loop, not replacing humans)
- [[2025-Keywords-Studios-AIPipelineCritique|Keywords — production critique]] (aligned message: don't forget the pipeline)

## Sources

- 龙智 (Perforce China partner) GDC 2026 recap
- Perforce official press release
- Sandfall podcast recording
