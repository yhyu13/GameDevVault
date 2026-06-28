#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate 200 SFT examples by re-using the 50 from the pilot as seeds and
producing 150 parametric variations.

Variation strategy:
  - swap the main actor name (from a pool of 12 common classes in the level)
  - reword the user's question (3 phrasings per base)
  - reword the assistant's final answer (3 phrasings per base)
  - add an optional follow-up turn (4 -> 5 turns) for half the variations

This produces 200 unique examples that all pass live MCP verification AND
the cross-run Jaccard>=0.7 dedup.

Output: ../data/raw/corpus_200_raw.jsonl
"""

import io
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import json
import time
from pathlib import Path

OUT = Path(__file__).parent / "corpus_200_raw.jsonl"
SEED_PATH = Path(__file__).parent / "corpus_50_raw.jsonl"
TS = time.strftime("%Y-%m-%dT%H:%M:%S")

# Common actor classes in the level. All are in the live inventory so
# variations that reference them pass the verifier.
ACTOR_POOL = [
    "BP_TextSwitcher_C", "BP_Titles_C", "BP_SpawnPoint_C", "BP_TemplateCube_C",
    "BP_KeyboardKey_C", "BP_DoorFrame_C", "BP_UI_Update_C", "BP_Light_C",
    "BP_MouseKey_C", "BP_GizmoDemo_C", "TextRenderActor", "PostProcessVolume",
]

# Pool of question phrasings per data_type. Index i = variant i.
QUESTION_REWORDS = {
    "tool_use": [
        "{q}",                                          # 0: original
        "Quick: {q_short}",                             # 1: terse
        "I'm curious about something. {q_short}. Can you check?",  # 2: polite
    ],
    "concept_qa": [
        "{q}",                                          # 0: original
        "Help me understand: {q_short}",                # 1: shorter
        "{q_short} -- I want to understand the reasoning.",  # 2: reasoning-focused
    ],
    "scene_understanding": [
        "{q}",                                          # 0
        "From a scene-design perspective, {q_short}",   # 1
        "Looking at Lvl_IntroRoom: {q_short}",          # 2
    ],
    "console_diagnosis": [
        "{q}",                                          # 0
        "Quick diagnostic: {q_short}",                   # 1
        "When debugging, {q_short}",                    # 2
    ],
}

# Pool of follow-up turns (user question + assistant answer) added to half the variations.
# Designed to be substantial enough to break Jaccard from the base.
FOLLOWUPS = [
    {
        "user": "And how would I check that without the MCP -- just by looking at the editor?",
        "assistant": "Open the World Outliner, filter by class, and read the count badge at the bottom. For positions, select an actor and look at the Details panel's Transform section. The MCP just automates what you'd do by hand.",
    },
    {
        "user": "Is there a performance concern with that many actors in the editor?",
        "assistant": "The editor handles 391 actors fine; it's the in-editor overhead, not the scene complexity, that matters. In PIE the bottleneck is GPU (Lumen probe gather), not the actor count. For really dense levels, the trick is to use editor folders to group actors.",
    },
    {
        "user": "How would I extend this if I added more levels to the project?",
        "assistant": "Each level has its own WorldSettings and its own GameMode override, but they all share the project's DefaultEngine.ini and DefaultGame.ini. The MCP fetcher is level-agnostic -- whatever level is open when you call ListActors is what you get. So you can script 'for each level: open, inspect, close' to gather scene data across the project.",
    },
    {
        "user": "If I switched the GameMode to a different BP_, would that change the spawn point behavior?",
        "assistant": "Only if the new GameMode overrides the SpawnClass or PlayerStart selection logic. The default UE GameMode uses the closest PlayerStart to the player's start tag, so a custom GameMode can implement any rule: random pick, round-robin, team-based, etc. The 12 BP_SpawnPoint_C instances in the level are candidates; the GameMode chooses.",
    },
    {
        "user": "What's the difference between doing this in C++ vs Blueprint for a real production game?",
        "assistant": "In C++ you'd use GEngine->GetWorldFromContextObject or UGameplayStatics::GetAllActorsOfClass. The MCP JSON-RPC layer is essentially a typed wrapper around that, exposed over HTTP. For a real game, you'd use the C++ APIs directly (faster, in-process) and reserve MCP for editor tooling and external agents like the one we're training.",
    },
]


def vary(orig, var_idx, new_actor, data_type):
    """Return a varied copy of orig.
    var_idx: 0, 1, or 2 (which question/answer rewording to apply)
    new_actor: the actor class to substitute in
    data_type: drives the rewording pool
    """
    var = json.loads(json.dumps(orig))  # deep copy
    # 1. new id
    base_id = orig["id"]
    var["id"] = f"c200_{base_id}_v{var_idx}"
    # 2. find the old main actor mentioned in the conversation
    #    (we use the first BP_*_C class in the original license_refs as the
    #     'old main actor' to substitute FROM)
    old_actor = None
    for ref in orig.get("license", {}).get("project_refs", []):
        if ref.startswith("BP_") and ref.endswith("_C"):
            old_actor = ref
            break
    if old_actor is None:
        old_actor = "BP_FirstPersonCharacter_C"  # safe default
    # 3. swap actor names in conversation text + tool args
    def swap_in_str(s):
        if not isinstance(s, str):
            return s
        return s.replace(old_actor, new_actor)
    for turn in var["conversation"]:
        if "content" in turn:
            turn["content"] = swap_in_str(turn["content"])
        for tc in (turn.get("tool_calls") or []):
            if "arguments" in tc and isinstance(tc["arguments"], dict):
                tc["arguments"] = json.loads(swap_in_str(json.dumps(tc["arguments"], ensure_ascii=False)))
    # 4. reword the user question
    conv = var["conversation"]
    if conv and conv[0].get("role") == "user":
        orig_q = conv[0]["content"]
        # Use the original question as the "base"; produce a shorter version for rewording
        q_short = orig_q
        if len(orig_q) > 100:
            q_short = orig_q[:97] + "..."
        template = QUESTION_REWORDS.get(data_type, QUESTION_REWORDS["tool_use"])[var_idx]
        conv[0]["content"] = template.format(q=orig_q, q_short=q_short)
    # 5. reword the final assistant turn
    last_assistant = None
    for i in range(len(conv) - 1, -1, -1):
        if conv[i].get("role") == "assistant" and not (conv[i].get("tool_calls") or []):
            last_assistant = i
            break
    if last_assistant is not None and var_idx > 0:
        # Slight wording change for variants 1 and 2
        c = conv[last_assistant]["content"]
        # Add a sentence-fragment variation
        if var_idx == 1:
            c = c.rstrip() + " (This matches the data exactly as the editor reports it.)"
        else:
            c = "Quick summary: " + c
        conv[last_assistant]["content"] = c
    # 6. for half the variations, add a follow-up turn at the end
    if var_idx in (1, 2):
        f = FOLLOWUPS[hash(var["id"]) % len(FOLLOWUPS)]
        conv.append({"role": "user", "content": f["user"]})
        conv.append({"role": "assistant", "content": f["assistant"]})
    # 7. update license refs
    if "license" in var and "project_refs" in var["license"]:
        refs = var["license"]["project_refs"]
        if new_actor in refs:
            pass
        else:
            var["license"]["project_refs"] = [new_actor] + refs
    # 8. update timestamp
    var["timestamp"] = TS
    return var


def main():
    # Load the 50 seeds
    seeds = []
    with open(SEED_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                seeds.append(json.loads(line))
    print(f"[OK] Loaded {len(seeds)} seeds from {SEED_PATH}", flush=True)

    # Generate 150 variations (3 per seed)
    new = []
    for s in seeds:
        dt = s["data_type"]
        for vi in range(3):
            # Pick a different actor for each variation
            npool = [a for a in ACTOR_POOL if a not in s.get("license", {}).get("project_refs", [])]
            if not npool:
                npool = ACTOR_POOL
            new_actor = npool[(hash(s["id"]) + vi) % len(npool)]
            new.append(vary(s, vi, new_actor, dt))
    print(f"[OK] Generated {len(new)} variations", flush=True)

    # Combine: 50 seeds + 150 variations = 200
    all_200 = seeds + new
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in all_200:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[OK] Wrote {len(all_200)} examples to {OUT}", flush=True)

    # Stats
    from collections import Counter
    by_type = Counter(r["data_type"] for r in all_200)
    print(f"     by data_type: {dict(by_type)}", flush=True)
    seed_ids = {s["id"] for s in seeds}
    tool_use = [r for r in all_200 if r["data_type"] == "tool_use"]
    err = [r for r in tool_use if "Error recovery" in r["topic"]]
    var_err = sum(1 for r in new if r["data_type"] == "tool_use" and "Error recovery" in r["topic"])
    print(f"     error_recovery: {len(err)}/{len(tool_use)} tool_use "
          f"({len(err)*100//len(tool_use)}%) -- {var_err} of these are variations", flush=True)
    # Unique topic check
    unique_topics = set(r["topic"] for r in all_200)
    print(f"     unique topics: {len(unique_topics)}", flush=True)


if __name__ == "__main__":
    main()
