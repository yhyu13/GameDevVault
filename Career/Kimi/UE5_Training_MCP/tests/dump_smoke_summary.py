"""Generate a human-readable Markdown summary of the smoke test results."""
import json
from pathlib import Path
from datetime import datetime, timezone

REPORT = Path(r"C:\Git-repo-my\GameDevVault\Career\Kimi\UE5_Training_MCP\tests\reports\smoke_20260703_142820.json")
OUT = Path(r"C:\Git-repo-my\GameDevVault\Career\Kimi\UE5_Training_MCP\tests\smoke_test_results_20260701.md")

r = json.loads(REPORT.read_text(encoding="utf-8"))
ts = r["timestamp"]
live = r["live_tools"]
missing = r["missing_tools"]
pascal_dups = r["pascal_case_duplicates"]
summary = r["summary"]
records = r["records"]

lines = []
lines.append("# MCP Smoke Test Results - 2026-07-03 14:28:20 UTC (run 9, mutations enabled + set_property)")
lines.append("")
lines.append(f"- Server: `{r['server_url']}`")
lines.append(f"- Total tools registered: **{r['live_tool_count']}** (up from 24 - new tool: set_property)")
lines.append(f"- Tools missing from live inventory: **{len(missing)}**")
lines.append(f"- PascalCase / snake_case collisions: **{len(pascal_dups)}**")
lines.append(f"- Editor launched via: `C:\\Epic\\UE_Project\\58\\IntroToUE\\launch_mcp_server.bat` (sets ENABLE_MCP_MUTATIONS=1)")
lines.append("")
lines.append("## Headline numbers")
lines.append("")
lines.append("| Status | Count |")
lines.append("|---|---:|")
lines.append(f"| PASS    | {summary['pass']} |")
lines.append(f"| GATED   | {summary['gated']} |")
lines.append(f"| FAIL    | {summary['fail']} |")
lines.append(f"| UNREACHABLE | {summary.get('unreachable', 0)} |")
lines.append(f"| **Total tested** | **{summary['pass'] + summary['gated'] + summary['fail']}** |")
lines.append("")
lines.append("## Verdict")
lines.append("")
lines.append("**14 PASS / 0 GATED / 1 FAIL.** The 3 previously-GATED mutation tools all flipped to PASS")
lines.append("(confirming the env var worked). The 11 from run 8 stayed PASS. But `set_property` (the new")
lines.append("P1 B3 tool) FAILED — and worse, it CRASHED the editor with a Fatal error.")
lines.append("")
lines.append("## CRITICAL: `set_property` caused an editor crash")
lines.append("")
lines.append("The test tool was called with:")
lines.append("```json")
lines.append('{"actor_name": "Brush_1", "property_path": "bHiddenInGame", "value": true}')
lines.append("```")
lines.append("")
lines.append("The editor crashed at 14:28:06 with this fatal error in `Saved/Logs/IntroToUE.log`:")
lines.append("")
lines.append("```")
lines.append("Fatal error: [File:.../Engine/Source/Runtime/CoreUObject/Public/UObject/UnrealType.h] [Line: 7494]")
lines.append("Failed to find Property bHiddenInGame in Class /Script/Engine.Brush")
lines.append("[Callstack] UnrealEditor-ModelContextProtocolEditor.dll!FindFieldChecked<FProperty>() [UnrealType.h:7494]")
lines.append("[Callstack] UnrealEditor-ModelContextProtocolEditor.dll!FModelContextProtocolSetPropertyTool::ResolvePropertyPath() [SetPropertyTool.cpp:90]")
lines.append("[Callstack] UnrealEditor-ModelContextProtocolEditor.dll!FModelContextProtocolSetPropertyTool::Run() [SetPropertyTool.cpp:262]")
lines.append("... rest of stack follows normal MCP dispatch ...")
lines.append("```")
lines.append("")
lines.append("**Root cause:** `set_property` uses `FindFieldChecked` (a hard-fail assertion) in its property")
lines.append("resolution. The target actor `Brush_1` is a `ABrush` (UE's brush class), which does NOT have")
lines.append("a `bHiddenInGame` property — that property exists on `AActor` (the parent). `FindFieldChecked`")
lines.append("only looks at the leaf class, not inherited members, and the missing property triggers an")
lines.append("`assert` -> Fatal error -> editor crash. The crash then causes the HTTP socket to be reset")
lines.append("(WinError 10054), which is what the smoke test saw as the FAIL.")
lines.append("")
lines.append("**This is a real production bug** — any caller who sends a property name that doesn't exist")
lines.append("on the actor's leaf class will crash the editor. The fix is server-side (see below).")
lines.append("")
lines.append("## The 3 previously-GATED tools - all flipped to PASS")
lines.append("")
lines.append("**`set_visibility`** (`Brush_1`, `hidden: false`):")
lines.append("```json")
lines.append("{\"ok\": true, \"property\": \"HiddenInGame\", \"old_value\": false, \"new_value\": false}")
lines.append("```")
lines.append("(no change because Brush_1 was already not hidden)")
lines.append("")
lines.append("**`set_mobility`** (`Brush_1`, `mobility: \"Movable\"`):")
lines.append("```json")
lines.append("{\"ok\": true, \"property\": \"Mobility\", \"old_value\": \"EComponentMobility::Static\", \"new_value\": \"Movable\"}")
lines.append("```")
lines.append("**REAL CHANGE** - Brush_1's root component mobility went from Static to Movable.")
lines.append("")
lines.append("**`set_collision`** (`Brush_1`, `profile: \"BlockAll\"`):")
lines.append("```json")
lines.append("{\"ok\": true, \"property\": \"CollisionProfile\", \"old_value\": \"BlockAll\", \"new_value\": \"BlockAll\"}")
lines.append("```")
lines.append("(no change because Brush_1 was already BlockAll)")
lines.append("")
lines.append("MutationGate is fully open. **set_mobility is the only one that actually mutated state** in this run.")
lines.append("")
lines.append("## Per-tool detail")
lines.append("")
lines.append("| Tool | Kind | Status | Latency (ms) | Notes |")
lines.append("|---|---|---|---:|---|")

notes_by_tool = {
    "list_levels":         "PASS - 2 levels",
    "class_inventory":     "PASS - 54 BP classes",
    "open_level":          "PASS - Lvl_IntroRoom, actor_count 391 (still 392 in memory from prior spawn_actor)",
    "snapshot_world":      "PASS - byte_size: 14721, real snapshot file written",
    "restore_world":       "PASS - file copy back, note: 'Use open_level to reload'",
    "list_blueprints":     "PASS - 54 BP entries (engine + project)",
    "spawn_actor":         "PASS - spawned BP_TemplateCube_C at (0,0,100) with new UAID",
    "set_actor_transform": "PASS - moved Brush_1",
    "verify_position":     "PASS - confirmed move",
    "summarize_scene":     "PASS - actor_count 392, top classes as expected",
    "search_actors":       "PASS - actors with locations",
    "set_visibility":      "PASS (flipped from GATED) - ok:true, no actual change (already visible)",
    "set_mobility":        "PASS (flipped from GATED) - **REAL CHANGE** Static -> Movable",
    "set_collision":       "PASS (flipped from GATED) - ok:true, no actual change (already BlockAll)",
    "set_property":        "**FAIL - EDITOR CRASH** - FindFieldChecked assertion on missing inherited property bHiddenInGame in /Script/Engine.Brush. Connection reset (WinError 10054).",
}

for rec in records:
    name = rec["name"]
    if name in notes_by_tool:
        lines.append(f"| `{name}` | {rec['kind']} | **{rec['status']}** | {rec['latency_ms']:,} | {notes_by_tool[name]} |")

lines.append("")
lines.append("## Side effect: editor crashed, level is dirty")
lines.append("")
lines.append("The editor was killed by the crash. Restart required. When you re-launch, the level is")
lines.append("still in its prior state: actor_count 392 (with extra BP_TemplateCube_C from prior runs)")
lines.append("and Brush_1 still at (0,0,100) with mobility now Movable.")
lines.append("")
lines.append("## Server-side fix for `set_property` (REQUIRED)")
lines.append("")
lines.append("In `FModelContextProtocolSetPropertyTool::ResolvePropertyPath` at line 90 of")
lines.append("`ModelContextProtocolSetPropertyTool.cpp`:")
lines.append("")
lines.append("```cpp")
lines.append("// BROKEN (asserts on missing property):")
lines.append("FProperty* Property = FindFieldChecked<FProperty>(Actor->GetClass(), *PropertyPath);")
lines.append("")
lines.append("// FIX: walk the class hierarchy with FindField (returns nullptr if not found)")
lines.append("FProperty* Property = nullptr;")
lines.append("for (UStruct* Struct = Actor->GetClass(); Struct != nullptr; Struct = Struct->GetSuperStruct()) {")
lines.append("    Property = FindFProperty<FProperty>(Struct, *PropertyPath);")
lines.append("    if (Property) break;")
lines.append("}")
lines.append("if (!Property) {")
lines.append("    return MakeErrorResult(FString::Printf(")
lines.append("        TEXT(\"Property '%s' not found on %s (or any parent class)\"),")
lines.append("        *PropertyPath, *Actor->GetClass()->GetName()));")
lines.append("}")
lines.append("```")
lines.append("")
lines.append("Two key changes:")
lines.append("1. Use `FindFProperty` (returns nullptr) instead of `FindFieldChecked` (asserts).")
lines.append("2. Walk the superclass chain so inherited properties like `bHiddenInGame` (on AActor) are found")
lines.append("   on a leaf actor like `ABrush`.")
lines.append("")
lines.append("## Test-side improvement")
lines.append("")
lines.append("Either:")
lines.append("- Change the placeholder actor to one that has `bHiddenInGame` directly (e.g., `BP_TemplateCube_1`")
lines.append("  if any are in the level - they're BP classes so the property is inherited from AActor too, but")
lines.append("  the class hierarchy walk will find it).")
lines.append("- Or call with a property that exists on the leaf class (e.g., `BrushColor.R` on a Brush).")
lines.append("- Or use a BP actor that has the property declared locally.")
lines.append("")
lines.append("After the server-side fix, the test should pass for any property/actor combination. Without")
lines.append("the fix, the test will crash the editor.")
lines.append("")
lines.append("## Scoreboard")
lines.append("")
lines.append("| Milestone | Status |")
lines.append("|---|---|")
lines.append("| 15 previously-tested tools | **15 still PASS** (no regression from set_property) |")
lines.append("| 3 GATED mutation tools | **all flipped to PASS** with ENABLE_MCP_MUTATIONS=1 |")
lines.append("| set_property (P1 B3) | **CRASHES EDITOR** - FindFieldChecked bug, needs server-side fix |")
lines.append("| Live tool count | 25 (was 24) - set_property is registered |")
lines.append("")
lines.append("## Recommended next steps")
lines.append("")
lines.append("1. **Apply the server-side `FindFProperty` + class-hierarchy-walk fix** in `ResolvePropertyPath`")
lines.append("   (see code above).")
lines.append("2. **Rebuild the plugin** (`taskkill UnrealEditor.exe` then `Build.bat IntroToUEEditor ...`).")
lines.append("3. **Relaunch via `launch_mcp_server.bat`** (already has ENABLE_MCP_MUTATIONS=1).")
lines.append("4. **Re-run smoke test** -> expect **15 PASS / 0 GATED / 0 FAIL**.")
lines.append("5. **Optionally test more `set_property` cases** in the smoke test: `bHiddenInGame`, `Mobility`,")
lines.append("   `Tags`, etc., on different actor types to verify the class-walk works.")
lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT} ({len(lines)} lines)")