#!/usr/bin/env python3
"""
UE5 Data Pruner (v2)

Same four-filter structure as scripts/data_pruner.py, but with a two-tier
factuality catalog so that v2 MCP-grounded examples pass alongside v1
rendering-system examples. v1 is left untouched.

Filters:
  1. length         - too short / too long
  2. factuality     - score against EITHER v1 rendering facts OR v2 MCP facts
  3. quality        - heuristic depth / specificity score
  4. deduplication  - jaccard similarity against prior examples

Usage:
    python data_pruner_v2.py \
      --input  ../data/raw/pilot_mcp_grounded.jsonl \
      --output ../data/processed/pilot_pruned.jsonl \
      --min_quality 3.0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

# Force UTF-8 stdout/stderr on Windows where the default is GBK.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# --- v1 rendering-system facts (kept identical to scripts/data_pruner.py) ---

V1_FACTS = {
    "source_paths": [
        "Engine\\Source\\Runtime",
        "Engine\\Source\\Runtime\\Renderer",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Nanite",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Lumen",
        "Engine\\Source\\Runtime\\Renderer\\Private\\VirtualShadowMaps",
        "Engine\\Source\\Runtime\\Engine\\Public",
        "Engine\\Source\\Runtime\\Engine\\Public\\NaniteResources.h",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Nanite\\NaniteClusterCulling.cpp",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Nanite\\NaniteRasterizer.cpp",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Lumen\\LumenSceneLighting.cpp",
        "Engine\\Source\\Runtime\\Renderer\\Private\\Lumen\\LumenSurfaceCache.cpp",
    ],
    "keywords": [
        "Cluster", "ClusterGroup", "Page", "DAG", "HZB", "GPUScene",
        "SurfaceCache", "LumenCard", "ScreenProbe", "Radiosity",
        "VirtualShadowMap", "PageTable", "PhysicalPage", "Clipmap",
        "MeshSDF", "SphereTracing", "ConeTracing", "VisibilityBuffer",
        "RenderGraph", "RDG", "BasePass", "NaniteRender",
        "CardCapturesPerFrame", "MaxNumAdaptiveProbes",
    ],
    "numbers": ["128", "16", "6"],
}


# --- v2 MCP-observable facts (this design's domain) ---

V2_FACTS = {
    # Top-level MCP tool names
    "tool_names": [
        "ListActors", "GetActorDetails", "SetActorTransform", "SpawnActor",
        "DeleteActor", "execute_console_command", "capture_viewport",
        "save_current_level", "get_editor_context", "list_toolsets",
        "describe_toolset", "call_tool",
    ],
    # Toolset-qualified tool names
    "toolset_tools": [
        "GetProjectContext", "GetDockedContext",
        "ListSkills", "GetSkills", "CreateSkill", "UpdateSkill",
    ],
    # UE actor class names that commonly appear in IntroToUE and similar
    # projects. (The set is open-ended; we cover the most common ones
    # observed in the live level + the first-person template.)
    "class_names": [
        "StaticMeshActor", "TextRenderActor", "PostProcessVolume",
        "BP_FirstPersonCharacter_C", "BP_FirstPersonGameMode_C",
        "BP_FirstPersonPlayerController_C", "BP_TextSwitcher_C",
        "BP_Titles_C", "BP_SpawnPoint_C", "BP_TemplateCube_C",
        "BP_KeyboardKey_C", "BP_DoorFrame_C", "BP_UI_Update_C",
        "DirectionalLight", "PointLight", "SpotLight", "RectLight",
        "SkyLight", "PlayerStart", "WorldSettings", "AtmosphericFog",
        "ExponentialHeightFog", "TriggerBox", "TriggerSphere",
        "TriggerVolume", "CameraActor", "LevelScriptActor",
    ],
    # Config keys observed in the live DefaultEngine.ini / DefaultGame.ini
    "config_keys": [
        "ECC_GameTraceChannel", "Projectile",
        "GlobalDefaultGameMode", "GameMapsSettings",
        "EditorStartupMap", "GameDefaultMap",
        "r.AllowStaticLighting", "r.Lumen", "r.Shadow",
        "r.Substrate", "r.AmbientOcclusion", "r.MaterialQualityLevel",
        "r.ViewDistanceScale", "r.ScreenPercentage",
        "Lumen", "Substrate", "VirtualShadowMap", "VirtualShadowMaps",
        "IMC_Default", "IMC_MouseLook",
        "ActiveGameNameRedirects",
    ],
    # Asset-class prefixes from CLAUDE.md conventions
    "asset_prefixes": [
        "BP_", "M_", "MI_", "NS_", "MS_", "SM_", "T_", "DL_", "StrT_",
    ],
    # Console command families
    "console_cmd_families": [
        "stat", "show", "r.ScreenPercentage", "r.Lumen", "r.Shadow",
        "r.AmbientOcclusion", "r.MaterialQualityLevel", "r.ViewDistanceScale",
        "ke", "obj list", "Dump", "MemReport", "ListMaterials", "ListTextures",
        "CountedPhysScene", "DisplayAll", "Slate",
    ],
    # Level naming convention
    "level_naming": [r"Lvl_\w+", r"/Game/.*Lvl_\w+", r"/Game/.*\.umap"],
    # First-person template asset paths
    "asset_paths": [
        "FirstPerson/Blueprints/BP_FirstPersonCharacter",
        "FirstPerson/Blueprints/BP_FirstPersonGameMode",
        "FirstPerson/Blueprints/BP_FirstPersonPlayerController",
        "DemoTemplate/_Core/Lvl_IntroRoom",
        "DemoTemplate/_Core/BP_GM_Template",
        "DemoTemplate/_Core/BP_SaveData",
    ],
}


# --- Token counter (kept identical to v1) ---

def count_tokens(text: str) -> int:
    chinese = len(re.findall(r"[一-鿿]", text))
    english = len(re.findall(r"[a-zA-Z]+", text))
    return chinese + english


# --- Filter 1: length ---

def length_filter(record: dict, min_tokens: int = 100, max_tokens: int = 4096) -> tuple:
    conversation = record.get("conversation", [])
    total_text = " ".join(turn.get("content", "") for turn in conversation)
    token_count = count_tokens(total_text)
    if token_count < min_tokens:
        return False, f"too_short ({token_count} tokens < {min_tokens})"
    if token_count > max_tokens:
        return False, f"too_long ({token_count} tokens > {max_tokens})"
    return True, f"ok ({token_count} tokens)"


# --- Filter 2: factuality (two-tier: v1 OR v2) ---

def v1_factuality_score(text: str) -> tuple:
    text_lower = text.lower()
    score = 0
    reasons: list[str] = []
    for path in V1_FACTS["source_paths"]:
        if path.lower().replace("\\", "/") in text_lower.replace("\\", "/"):
            score += 2
            reasons.append("v1:has_source_path")
            break
    keyword_hits = sum(1 for kw in V1_FACTS["keywords"] if kw.lower() in text_lower)
    if keyword_hits >= 3:
        score += 2; reasons.append(f"v1:keywords({keyword_hits})")
    elif keyword_hits >= 1:
        score += 1; reasons.append(f"v1:keywords({keyword_hits})")
    for num in V1_FACTS["numbers"]:
        if num in text_lower:
            score += 1; reasons.append(f"v1:number({num})")
            break
    if "```cpp" in text_lower or "```c++" in text_lower:
        score += 2; reasons.append("v1:has_cpp_block")
    elif "```" in text_lower:
        score += 1; reasons.append("v1:has_code_block")
    if any(w in text_lower for w in ["trade-off", "tradeoff", "limitation", "limit", "代价", "局限"]):
        score += 1; reasons.append("v1:has_tradeoff")
    return score, reasons


def v2_factuality_score(text: str) -> tuple:
    score = 0
    reasons: list[str] = []
    text_l = text  # we keep case for class names; lower only when needed

    # Tool names
    tool_hits = sum(1 for t in V2_FACTS["tool_names"] if t in text)
    if tool_hits:
        score += 1; reasons.append(f"v2:tools({tool_hits})")

    # Toolset tool names (qualified)
    toolset_hits = sum(1 for t in V2_FACTS["toolset_tools"] if t in text)
    if toolset_hits:
        score += 1; reasons.append(f"v2:toolset_tools({toolset_hits})")

    # Actor class names
    class_hits = sum(1 for c in V2_FACTS["class_names"] if c in text)
    if class_hits >= 3:
        score += 2; reasons.append(f"v2:classes({class_hits})")
    elif class_hits >= 1:
        score += 1; reasons.append(f"v2:classes({class_hits})")

    # Config keys
    config_hits = sum(1 for k in V2_FACTS["config_keys"] if k in text)
    if config_hits:
        score += 1; reasons.append(f"v2:config({config_hits})")

    # Asset prefixes
    prefix_hits = sum(1 for p in V2_FACTS["asset_prefixes"] if p in text)
    if prefix_hits:
        score += 1; reasons.append(f"v2:prefixes({prefix_hits})")

    # Console command families
    cmd_hits = sum(1 for c in V2_FACTS["console_cmd_families"] if c in text)
    if cmd_hits:
        score += 1; reasons.append(f"v2:cmds({cmd_hits})")

    # Level naming
    level_hits = sum(1 for p in V2_FACTS["level_naming"] if re.search(p, text))
    if level_hits:
        score += 1; reasons.append(f"v2:level({level_hits})")

    # Asset paths
    path_hits = sum(1 for p in V2_FACTS["asset_paths"] if p in text)
    if path_hits:
        score += 1; reasons.append(f"v2:asset_paths({path_hits})")

    return score, reasons


def factuality_filter(record: dict) -> tuple:
    conversation = record.get("conversation", [])
    text = " ".join(turn.get("content", "") for turn in conversation)
    v1_score, v1_reasons = v1_factuality_score(text)
    v2_score, v2_reasons = v2_factuality_score(text)
    best_score = max(v1_score, v2_score)
    reasons = v1_reasons + v2_reasons
    if best_score >= 3:
        return True, f"score={best_score} (v1={v1_score}, v2={v2_score}, {', '.join(reasons) or 'no_detail'})"
    return False, (
        f"score={best_score} (v1={v1_score}, v2={v2_score}, {', '.join(reasons) or 'no_detail'})"
        f" - too few facts"
    )


# --- Filter 3: quality (heuristic, expanded) ---

def heuristic_quality_score(record: dict) -> float:
    """v2-aware quality score.

    Calibration note (2026-06-28): the v1 calibration expected long render-internals
    prose and gave near-zero scores to v2's compact tool-use traces. This v2
    calibration rewards:
      - the number of MCP tool calls issued  (rich tool-use traces)
      - the number of verified claims       (MCP-grounded examples)
      - text-based depth markers (v1 and v2)
    """
    conversation = record.get("conversation", [])
    text = " ".join(turn.get("content", "") for turn in conversation).lower()
    score = 0.0

    # --- Length bonus ---
    token_count = count_tokens(text)
    if token_count > 500:
        score += 1.0
    elif token_count > 200:
        score += 0.5

    # --- v1 depth markers (rendering internals) ---
    depth_markers = [
        "source", "engine", "cpp", "function", "struct", "class",
        "algorithm", "optimize", "performance", "memory", "gpu", "cpu",
        "trade-off", "tradeoff", "limitation", "bottleneck",
        "源码", "函数", "结构体", "优化", "性能", "内存", "瓶颈",
    ]
    depth_hits = sum(1 for m in depth_markers if m in text)
    score += min(depth_hits / 5, 1.0)

    # --- v2 depth markers (MCP + project) ---
    v2_depth = [
        "listactors", "getactordetails", "save_current_level", "capture_viewport",
        "r.lumen", "virtual shadow", "substrate", "imc_", "playerstart",
        "execute_console", "aiassistant", "toolset",
        "实例", "控制台", "关卡", "项目", "插件", "渲染", "碰撞",
    ]
    v2_hits = sum(1 for m in v2_depth if m in text)
    score += min(v2_hits / 5, 1.0)

    # --- Code blocks ---
    if "```" in text:
        score += 1.0

    # --- Multi-turn depth ---
    num_turns = len(conversation)
    if num_turns >= 8:
        score += 1.0
    elif num_turns >= 4:
        score += 0.5

    # --- Specificity: numbers + function-like patterns ---
    if re.search(r"\b\d{2,}\b", text) and re.search(r"[a-zA-Z][a-zA-Z0-9]*\(", text):
        score += 1.0

    # === V2-AWARE ADDITIONS ===

    # --- Tool call depth: count actual tool_calls in the conversation ---
    total_tool_calls = sum(len(turn.get("tool_calls") or []) for turn in conversation)
    if total_tool_calls > 0:
        # +0.3 per tool call, capped at 1.0 (3+ tool calls saturates the bonus)
        score += min(0.3 * total_tool_calls, 1.0)

    # --- v1-format fallback: detect "Tool calls:" header in adapted text ---
    if total_tool_calls == 0 and "tool calls:" in text:
        m = re.findall(r"-\s+(\w+)\(", text)
        if m:
            score += min(0.3 * len(m), 1.0)

    # --- Verification block: reward verified claims (only present in v2 verified data) ---
    verification = record.get("verification", {})
    claims_passed = verification.get("claims_passed", 0)
    if claims_passed and claims_passed > 0:
        # +0.1 per verified claim, capped at 0.5 (5+ claims saturates)
        score += min(0.1 * claims_passed, 0.5)

    return min(score, 5.0)


# --- Filter 4: deduplication (Jaccard on terms) ---

def jaccard_similarity(text1: str, text2: str) -> float:
    def extract_terms(text: str) -> set:
        text = text.lower()
        chinese = re.findall(r"[一-鿿]{2,}", text)
        english = re.findall(r"[a-zA-Z][a-zA-Z0-9_]*", text)
        return set(chinese + english)

    a = extract_terms(text1)
    b = extract_terms(text2)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def deduplicate(records: list, threshold: float = 0.7) -> tuple:
    kept, removed = [], []
    for i, record in enumerate(records):
        text_i = " ".join(
            turn.get("content", "") for turn in record.get("conversation", [])
        )
        is_dup = False
        for kept_record in kept:
            text_j = " ".join(
                turn.get("content", "") for turn in kept_record.get("conversation", [])
            )
            sim = jaccard_similarity(text_i, text_j)
            if sim >= threshold:
                is_dup = True
                removed.append({"index": i, "reason": f"duplicate(similarity={sim:.2f})"})
                break
        if not is_dup:
            kept.append(record)
    return kept, removed


def rebalance_by_type(
    kept: list, all_records: list, min_per_type: int
) -> list:
    """Post-prune rebalancer: ensure each data_type has at least min_per_type
    records in the output. Pulls the next-highest-quality records of each
    under-represented type from the original input set.

    Tracks which records came from rebalancing (added with a marker that the
    caller can inspect via the `_rebalanced` key).
    """
    if min_per_type <= 0:
        return kept
    by_type = Counter(r.get("data_type", "unknown") for r in kept)
    kept_ids = {r.get("id") for r in kept}
    # Score every input record (in case quality scores weren't computed)
    for r in all_records:
        if "_quality_score" not in r:
            r["_quality_score"] = heuristic_quality_score(r)
    for dt, count in list(by_type.items()):
        if count >= min_per_type:
            continue
        needed = min_per_type - count
        # Find candidates of this type, not already in kept, sorted by quality desc
        candidates = sorted(
            [r for r in all_records
             if r.get("data_type") == dt and r.get("id") not in kept_ids],
            key=lambda r: -(r.get("_quality_score", 0.0)),
        )
        for c in candidates[:needed]:
            c["_rebalanced"] = True
            kept.append(c)
            kept_ids.add(c.get("id"))
    return kept


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Prune UE5 training data (v2)")
    parser.add_argument("--input", required=True, help="Input JSONL")
    parser.add_argument("--output", required=True, help="Output pruned JSONL")
    parser.add_argument("--min_quality", type=float, default=3.0)
    parser.add_argument("--dedup_threshold", type=float, default=0.7)
    parser.add_argument("--min_tokens", type=int, default=100)
    parser.add_argument("--max_tokens", type=int, default=4096)
    parser.add_argument("--per_type_min", type=int, default=0,
                        help="If >0, ensure each data_type has at least N records in output")
    parser.add_argument("--report", default=None, help="Pruning report path")
    args = parser.parse_args()

    report_path = args.report or args.output.replace(".jsonl", "_report.json")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    records = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    print(f"[PRUNE] Loaded {len(records)} records from {args.input}")

    stats = {
        "input_count": len(records),
        "length_filter": {"passed": 0, "removed": 0, "details": []},
        "factuality_filter": {"passed": 0, "removed": 0, "details": []},
        "quality_filter": {"passed": 0, "removed": 0, "details": []},
        "dedup_filter": {"passed": 0, "removed": 0, "details": []},
        "rebalance": {"added": 0, "by_type": {}},
    }

    # Filter 1: length
    after_length = []
    for i, r in enumerate(records):
        ok, reason = length_filter(r, args.min_tokens, args.max_tokens)
        if ok:
            after_length.append(r); stats["length_filter"]["passed"] += 1
        else:
            stats["length_filter"]["removed"] += 1
            stats["length_filter"]["details"].append({"index": i, "reason": reason})
    print(f"   length   : {stats['length_filter']['passed']} passed, {stats['length_filter']['removed']} removed")

    # Filter 2: factuality (two-tier)
    after_factuality = []
    for i, r in enumerate(after_length):
        ok, reason = factuality_filter(r)
        if ok:
            after_factuality.append(r); stats["factuality_filter"]["passed"] += 1
        else:
            stats["factuality_filter"]["removed"] += 1
            stats["factuality_filter"]["details"].append({"index": i, "reason": reason})
    print(f"   factuality: {stats['factuality_filter']['passed']} passed, {stats['factuality_filter']['removed']} removed")

    # Filter 3: quality (v2-aware)
    after_quality = []
    for i, r in enumerate(after_factuality):
        s = heuristic_quality_score(r)
        r["_quality_score"] = s
        if s >= args.min_quality:
            after_quality.append(r); stats["quality_filter"]["passed"] += 1
        else:
            stats["quality_filter"]["removed"] += 1
            stats["quality_filter"]["details"].append({"index": i, "reason": f"score={s:.2f} < {args.min_quality}"})
    print(f"   quality  : {stats['quality_filter']['passed']} passed, {stats['quality_filter']['removed']} removed")

    # Filter 4: dedup
    after_dedup, removed = deduplicate(after_quality, args.dedup_threshold)
    stats["dedup_filter"]["passed"] = len(after_dedup)
    stats["dedup_filter"]["removed"] = len(removed)
    stats["dedup_filter"]["details"] = removed
    print(f"   dedup    : {stats['dedup_filter']['passed']} passed, {stats['dedup_filter']['removed']} removed")

    # Optional: rebalance by type (Fix 2)
    final = list(after_dedup)
    if args.per_type_min > 0:
        before = len(final)
        final = rebalance_by_type(final, records, args.per_type_min)
        added = len(final) - before
        stats["rebalance"]["added"] = added
        final_by_type = Counter(r.get("data_type", "unknown") for r in final)
        for dt, n in final_by_type.items():
            stats["rebalance"]["by_type"][dt] = n
        if added > 0:
            print(f"   rebalance: added {added} (per_type_min={args.per_type_min})")

    stats["output_count"] = len(final)
    stats["retention_rate"] = len(final) / len(records) if records else 0.0
    stats["quality_distribution"] = dict(Counter(r.get("_quality_score", 0) for r in final))
    # Strip internal keys
    for r in final:
        r.pop("_quality_score", None)
        r.pop("_rebalanced", None)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        for r in final:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Pruning complete!")
    print(f"   Input:  {len(records)} records")
    print(f"   Output: {len(final)} records ({stats['retention_rate']:.1%} retention)")
    print(f"   Output: {args.output}")
    print(f"   Report: {report_path}")


if __name__ == "__main__":
    main()
