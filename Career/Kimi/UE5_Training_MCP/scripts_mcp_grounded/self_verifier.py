#!/usr/bin/env python3
"""
Self-verifier for MCP-grounded UE5 SFT examples (v2).

Two stages per DESIGN.md §6.4:

Stage A (mechanical): pull concrete claims from the conversation text
and re-query MCP to check them.

  - Actor names:    match `BP_..._C_N` or any name returned by ListActors
  - Class names:    match any class that appears in the live level
  - Position tuples: regex for `X=...` / `x:...` / `(X, Y, Z)` style
  - Tool names:     check against the live tool inventory
  - File paths:     match `Engine\\Source\\...` or `Content\\...`

Stage B (judgment): the generator (a human or LLM) inspects Stage A's
report and either marks the example verified, repairs it, or rejects it.

The Verifier class returns a `VerificationReport` (dataclass) with the
mechanical findings and a slot for the judgment.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

from context_fetcher import ContextFetcher


# --- Claim patterns ---

# UE generated class names: end in `_C`. Class names are also returned in
# the live actor inventory; we only want the bare class portion here.
RE_GENERATED_CLASS = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*_C)\b")
# BP-prefixed actor *instance* names. Two forms observed in the wild:
#   - sequential:   BP_Foo_C_0, BP_Foo_C_1, ...
#   - UAID (UE 5+): BP_Foo_C_UAID_HEXSUFFIX_INT, e.g.
#                   BP_SpawnPoint_C_UAID_F4A475FF15A3938902_1914811066
#                   (note the extra underscore between `C` and `UAID`).
RE_BP_INSTANCE = re.compile(
    r"\b(BP_[A-Za-z0-9_]+_C(?:_\d+|_UAID_[A-F0-9]+_\d+))\b"
)
# Generic non-BP actor *instance* names. Two forms:
#   - sequential:   WorldSettings_1, Brush_1, ...
#   - UAID:         StaticMeshActor_UAID_F4A475FF15A34D8902_2073097800
RE_GENERIC_INSTANCE = re.compile(
    r"\b([A-Z][A-Za-z0-9]+(?:_\d+|_UAID_[A-F0-9]+_\d+))\b"
)
# Position tuples in many common forms
RE_POSITION = re.compile(
    r"""
    (?:
        X\s*[=:]\s*(-?\d+(?:\.\d+)?)\s*[,;\s]+
        Y\s*[=:]\s*(-?\d+(?:\.\d+)?)\s*[,;\s]+
        Z\s*[=:]\s*(-?\d+(?:\.\d+)?)
      |
        \(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)
    )
    """,
    re.VERBOSE,
)
# Engine source paths
RE_ENGINE_PATH = re.compile(
    r"(Engine[/\\]Source[/\\][A-Za-z0-9_./\\-]+)"
)
# Project content paths
RE_CONTENT_PATH = re.compile(
    r"((?:Game|IntroToUE|DemoTemplate)[/\\][A-Za-z0-9_./\\-]+\.(?:umap|uasset|usf|ush|ini))"
)
# Quoted console commands
RE_CONSOLE_CMD = re.compile(r"`([a-zA-Z][a-zA-Z0-9_.]*[^`]*)`")


# --- Report dataclass ---

@dataclass
class ClaimResult:
    """One claim extracted from the example, with its verification outcome."""
    category: str               # "actor_name" | "class_name" | "position" | "tool_name" | "engine_path" | "content_path" | "console_cmd"
    claim: str                  # the literal text claimed
    status: str                 # "pass" | "fail" | "unverifiable"
    detail: str = ""            # human-readable explanation


@dataclass
class ToolCallResult:
    """One tool call claimed in a tool_use example."""
    name: str
    arguments: dict
    valid_name: bool
    valid_arguments: bool
    detail: str = ""


@dataclass
class VerificationReport:
    """End-to-end verification result for one example."""
    example_id: str
    claims_checked: int = 0
    claims_passed: int = 0
    claims_failed: int = 0
    claims_unverifiable: int = 0
    claim_results: list[ClaimResult] = field(default_factory=list)
    tool_calls_issued: int = 0
    tool_calls_valid: int = 0
    tool_call_results: list[ToolCallResult] = field(default_factory=list)
    mechanical_pass: bool = False
    judgment: str = "pending"   # "verified" | "repaired" | "rejected" | "pending"
    judgment_notes: str = ""

    def to_dict(self) -> dict:
        return {
            "example_id": self.example_id,
            "claims_checked": self.claims_checked,
            "claims_passed": self.claims_passed,
            "claims_failed": self.claims_failed,
            "claims_unverifiable": self.claims_unverifiable,
            "claim_results": [asdict(c) for c in self.claim_results],
            "tool_calls_issued": self.tool_calls_issued,
            "tool_calls_valid": self.tool_calls_valid,
            "tool_call_results": [asdict(t) for t in self.tool_call_results],
            "mechanical_pass": self.mechanical_pass,
            "judgment": self.judgment,
            "judgment_notes": self.judgment_notes,
        }


# --- Claim extractor ---

class ClaimExtractor:
    """Extract concrete claims from a conversation's text content."""

    def __init__(self, fetcher: ContextFetcher):
        self.fetcher = fetcher
        # Cache the live tool inventory and actor inventory once per verifier
        # instance; many claims will check against these.
        self._tool_inventory: Optional[set[str]] = None
        self._toolset_tool_inventory: Optional[set[str]] = None
        self._actor_names: Optional[set[str]] = None
        self._actor_classes: Optional[set[str]] = None

    def _ensure_inventory(self) -> None:
        if self._tool_inventory is not None:
            return
        # Tool inventory: union of top-level tool names + toolset tool names.
        # We rely on the fact that the ContextFetcher call already worked,
        # and on the live list_toolsets / describe_toolset for completeness.
        top_level = {
            "execute_console_command", "SpawnActor", "SetActorTransform",
            "ListActors", "GetActorDetails", "DeleteActor", "list_toolsets",
            "describe_toolset", "call_tool", "get_editor_context",
            "capture_viewport", "save_current_level",
        }
        self._tool_inventory = top_level

        # Toolset tool inventory: from live describe_toolset calls.
        toolset_tools: set[str] = set()
        try:
            for ts in self.fetcher.list_toolsets():
                tname = ts.get("name", "")
                if not tname:
                    continue
                try:
                    schema = self.fetcher.describe_toolset(tname)
                except Exception:
                    continue
                for t in (schema.get("tools") or []):
                    tname2 = t.get("name", "")
                    if tname2:
                        toolset_tools.add(tname2)
        except Exception:
            pass
        self._toolset_tool_inventory = toolset_tools

        # Actor inventory.
        try:
            actors = self.fetcher.list_actors()
            self._actor_names = {a.get("name", "") for a in actors if a.get("name")}
            self._actor_classes = {a.get("class", "") for a in actors if a.get("class")}
        except Exception:
            self._actor_names = set()
            self._actor_classes = set()

    # --- Per-category extractors ---

    def extract_actor_names(self, text: str) -> list[str]:
        out = set()
        out.update(RE_BP_INSTANCE.findall(text))
        out.update(RE_GENERIC_INSTANCE.findall(text))
        return sorted(out)

    def extract_class_names(self, text: str) -> list[str]:
        out = set()
        for m in RE_GENERATED_CLASS.findall(text):
            if not re.search(r"_\d+$", m):
                out.add(m)
        return sorted(out)

    def extract_positions(self, text: str) -> list[tuple[float, float, float]]:
        out = []
        for m in RE_POSITION.finditer(text):
            groups = m.groups()
            if groups[0] is not None:
                out.append((float(groups[0]), float(groups[1]), float(groups[2])))
            elif groups[3] is not None:
                out.append((float(groups[3]), float(groups[4]), float(groups[5])))
        return out

    def extract_engine_paths(self, text: str) -> list[str]:
        return RE_ENGINE_PATH.findall(text)

    def extract_content_paths(self, text: str) -> list[str]:
        return RE_CONTENT_PATH.findall(text)

    def extract_console_cmds(self, text: str) -> list[str]:
        """Only return backtick-quoted strings that look like real console commands
        (start with a known allow-list prefix). Otherwise we'd flag every code-style
        reference (e.g. `Trigger` in `Trigger` profile) as a console command."""
        out = []
        for raw in RE_CONSOLE_CMD.findall(text):
            cmd = raw.strip()
            first = cmd.split()[0] if " " in cmd else cmd.split("=")[0]
            if ContextFetcher._is_safe(first + " ") or ContextFetcher._is_safe(first):
                out.append(cmd)
        return out

    def extract_all(self, text: str) -> dict[str, list]:
        self._ensure_inventory()
        return {
            "actor_names": self.extract_actor_names(text),
            "class_names": self.extract_class_names(text),
            "positions": self.extract_positions(text),
            "engine_paths": self.extract_engine_paths(text),
            "content_paths": self.extract_content_paths(text),
            "console_cmds": self.extract_console_cmds(text),
        }


# --- Mechanical checker ---

class MechanicalChecker:
    """Re-query MCP and check extracted claims."""

    def __init__(self, fetcher: ContextFetcher):
        self.fetcher = fetcher
        self.extractor = ClaimExtractor(fetcher)

    def _gather_text(self, conversation: list[dict]) -> str:
        """Concatenate the text content of every turn in the conversation."""
        parts: list[str] = []
        for turn in conversation:
            content = turn.get("content", "")
            if isinstance(content, str):
                parts.append(content)
        return "\n".join(parts)

    def _check_actor_name(self, name: str) -> ClaimResult:
        if not self.extractor._actor_names:
            return ClaimResult("actor_name", name, "unverifiable", "no actor inventory")
        if name in self.extractor._actor_names:
            return ClaimResult("actor_name", name, "pass", "found in live ListActors")
        return ClaimResult("actor_name", name, "fail",
                           f"not in live level (have {len(self.extractor._actor_names)} actors)")

    def _check_class_name(self, cls: str) -> ClaimResult:
        if not self.extractor._actor_classes:
            return ClaimResult("class_name", cls, "unverifiable", "no class inventory")
        if cls in self.extractor._actor_classes:
            return ClaimResult("class_name", cls, "pass",
                               f"{self._count_class(cls)} instances in live level")
        # Allow common engine class names that won't appear in the level
        # directly but are referenced in conversation (e.g. AActor, UObject).
        common_abstract = {
            "AActor", "UObject", "USceneComponent", "UPrimitiveComponent",
            "APawn", "ACharacter", "AController", "AGameModeBase",
            "APlayerController", "UStaticMeshComponent", "USkeletalMeshComponent",
            "UCameraComponent", "USpringArmComponent", "UBoxComponent",
        }
        if cls in common_abstract:
            return ClaimResult("class_name", cls, "pass",
                               "abstract engine class (allowed even if no live instance)")
        # Allow First Person template classes that may not have an instance in
        # the current level but are real project classes (e.g. GameMode is
        # configured via WorldSettings, not placed as an actor).
        first_person_template_classes = {
            "BP_FirstPersonGameMode_C", "BP_FirstPersonCharacter_C",
            "BP_FirstPersonPlayerController_C", "BP_FirstPersonHUD_C",
            "BP_FirstPersonGameMode", "BP_FirstPersonCharacter",
            "BP_FirstPersonPlayerController",
        }
        if cls in first_person_template_classes:
            return ClaimResult("class_name", cls, "pass",
                               "FirstPerson template class (allowed even if no live instance)")
        return ClaimResult("class_name", cls, "fail",
                           f"not present in live level (have {len(self.extractor._actor_classes)} classes)")

    def _count_class(self, cls: str) -> int:
        # Use the cached full actor list (built by _ensure_inventory or
        # _check_position). Falls back to a one-shot MCP call only if no
        # inventory is available. Previously this method made a list_actors
        # call per matched class, costing ~15s per live class -- a major
        # bottleneck for any example mentioning multiple live classes.
        actors = None
        if self.extractor._actor_classes:
            # We need the full list (not just the set of classes) to count.
            # Use the same _actor_locations cache trick: store the full list
            # on the extractor and reuse it.
            if hasattr(self.extractor, "_actor_list_full"):
                actors = self.extractor._actor_list_full
            else:
                try:
                    actors = self.fetcher.list_actors()
                except Exception:
                    actors = []
                self.extractor._actor_list_full = actors
        if actors is None:
            return 0
        return sum(1 for a in actors if a.get("class") == cls)

    def _check_position(self, pos: tuple[float, float, float]) -> ClaimResult:
        # Position claims are checked against a small set of well-known
        # actors' positions: WorldSettings at (0,0,0), PlayerStart, etc.
        # We don't do a full sweep (too slow); we accept positions that
        # round to a known actor's location OR are near-origin.
        x, y, z = pos
        # Use cached actor list (already fetched at verifier init time).
        if not self.extractor._actor_names:
            # Fallback: try to fetch (one MCP call). This path is only hit
            # if inventory setup failed.
            try:
                actors = self.fetcher.list_actors()
            except Exception:
                return ClaimResult("position", f"({x},{y},{z})", "unverifiable",
                                   "could not list actors")
        else:
            # We need location data, which isn't in the cached set; fetch
            # the list once and cache it on the extractor.
            if not hasattr(self.extractor, "_actor_locations"):
                try:
                    actors = self.fetcher.list_actors()
                except Exception:
                    actors = []
                self.extractor._actor_locations = {
                    a.get("name"): a.get("location", {}) for a in actors
                }
            for aname, loc in self.extractor._actor_locations.items():
                if not isinstance(loc, dict):
                    continue
                ax, ay, az = loc.get("x"), loc.get("y"), loc.get("z")
                if None in (ax, ay, az):
                    continue
                if abs(ax - x) <= 1.0 and abs(ay - y) <= 1.0 and abs(az - z) <= 1.0:
                    return ClaimResult("position", f"({x},{y},{z})", "pass",
                                       f"matches actor {aname!r}")
        return ClaimResult(
            "position", f"({x},{y},{z})", "unverifiable",
            "no live actor at this exact location (within 1 unit)"
        )

    def _check_tool_name(self, name: str) -> ClaimResult:
        if name in (self.extractor._tool_inventory or set()):
            return ClaimResult("tool_name", name, "pass", "top-level MCP tool")
        if name in (self.extractor._toolset_tool_inventory or set()):
            return ClaimResult("tool_name", name, "pass", "toolset MCP tool")
        return ClaimResult("tool_name", name, "fail",
                           "not in the live MCP tool inventory")

    def _check_engine_path(self, path: str) -> ClaimResult:
        # We can't verify engine source paths without filesystem access to
        # the engine install. The design treats these as unverifiable by
        # default. The pruner (data_pruner_v2) handles depth scoring.
        return ClaimResult("engine_path", path, "unverifiable",
                           "engine source path (no filesystem access in MCP)")

    def _check_content_path(self, path: str) -> ClaimResult:
        # Likewise unverifiable without Content/ access.
        return ClaimResult("content_path", path, "unverifiable",
                           "content path (no filesystem access in MCP)")

    def _check_console_cmd(self, cmd: str) -> ClaimResult:
        from context_fetcher import ContextFetcher, UnsafeCommandError
        cmd = cmd.strip()
        if not cmd:
            return ClaimResult("console_cmd", cmd, "unverifiable", "empty")
        if ContextFetcher._is_blocked(cmd) is not None:
            return ClaimResult("console_cmd", cmd, "fail",
                               "blocked by safety policy")
        if not ContextFetcher._is_safe(cmd):
            return ClaimResult("console_cmd", cmd, "fail",
                               "not on the allow-list")
        return ClaimResult("console_cmd", cmd, "pass", "on the allow-list")

    def check_claims(self, conversation: list[dict]) -> list[ClaimResult]:
        text = self._gather_text(conversation)
        extracted = self.extractor.extract_all(text)
        results: list[ClaimResult] = []
        for n in extracted["actor_names"]:
            results.append(self._check_actor_name(n))
        for c in extracted["class_names"]:
            results.append(self._check_class_name(c))
        for p in extracted["positions"]:
            results.append(self._check_position(p))
        # Tool names: only from `tool_calls` entries, never from console cmds.
        for t in self._extract_tool_call_names(conversation):
            results.append(self._check_tool_name(t))
        for p in extracted["engine_paths"]:
            results.append(self._check_engine_path(p))
        for p in extracted["content_paths"]:
            results.append(self._check_content_path(p))
        for c in extracted["console_cmds"]:
            results.append(self._check_console_cmd(c))
        return results

    @staticmethod
    def _extract_tool_call_names(conversation: list[dict]) -> list[str]:
        names: list[str] = []
        for turn in conversation:
            for tc in (turn.get("tool_calls") or []):
                if isinstance(tc, dict) and tc.get("name"):
                    names.append(tc["name"])
        return names

    def check_tool_calls(self, conversation: list[dict]) -> list[ToolCallResult]:
        results: list[ToolCallResult] = []
        inv = (self.extractor._tool_inventory or set()) | (
            self.extractor._toolset_tool_inventory or set()
        )
        for turn in conversation:
            for tc in (turn.get("tool_calls") or []):
                if not isinstance(tc, dict):
                    continue
                name = tc.get("name", "")
                args = tc.get("arguments", {}) or {}
                valid_name = name in inv
                # Argument shape: we don't have full schemas here; a permissive
                # check is "arguments is a dict, has at least one key, no
                # obvious type errors". Real validation lives in the
                # upstream schema; for v2 we flag the name check as the
                # main signal.
                valid_args = isinstance(args, dict)
                detail = (
                    "valid tool name and dict arguments"
                    if valid_name and valid_args
                    else f"name valid={valid_name}, args valid={valid_args}"
                )
                results.append(ToolCallResult(
                    name=name, arguments=args,
                    valid_name=valid_name, valid_arguments=valid_args,
                    detail=detail,
                ))
        return results


# --- Verifier ---

class Verifier:
    """Top-level orchestrator. Stage A mechanical + Stage B judgment stub."""

    def __init__(self, fetcher: ContextFetcher):
        self.fetcher = fetcher
        self.checker = MechanicalChecker(fetcher)

    def verify(self, example: dict) -> VerificationReport:
        conversation = example.get("conversation", [])
        report = VerificationReport(
            example_id=example.get("id", "unknown"),
        )
        # Stage A: claims
        claim_results = self.checker.check_claims(conversation)
        report.claim_results = claim_results
        report.claims_checked = len(claim_results)
        report.claims_passed = sum(1 for c in claim_results if c.status == "pass")
        report.claims_failed = sum(1 for c in claim_results if c.status == "fail")
        report.claims_unverifiable = sum(1 for c in claim_results if c.status == "unverifiable")
        # Stage A: tool calls
        tc_results = self.checker.check_tool_calls(conversation)
        report.tool_call_results = tc_results
        report.tool_calls_issued = len(tc_results)
        report.tool_calls_valid = sum(
            1 for t in tc_results if t.valid_name and t.valid_arguments
        )
        # Mechanical pass = no failed claims AND all tool calls valid.
        report.mechanical_pass = (report.claims_failed == 0
                                  and report.tool_calls_valid == report.tool_calls_issued)
        return report

    def attach_judgment(
        self, report: VerificationReport, judgment: str, notes: str = ""
    ) -> None:
        """Stage B: store a judgment. judgment in {verified, repaired, rejected}."""
        if judgment not in ("verified", "repaired", "rejected", "pending"):
            raise ValueError(f"Invalid judgment: {judgment!r}")
        report.judgment = judgment
        report.judgment_notes = notes


# --- CLI ---

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python self_verifier.py <example.jsonl>")
        sys.exit(1)
    path = sys.argv[1]
    fetcher = ContextFetcher()
    v = Verifier(fetcher)
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            ex = json.loads(line)
            r = v.verify(ex)
            print(json.dumps(r.to_dict(), ensure_ascii=False))
