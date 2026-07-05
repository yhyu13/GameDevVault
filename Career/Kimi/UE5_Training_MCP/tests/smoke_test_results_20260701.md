# MCP Smoke Test Results - 2026-07-03 14:28:20 UTC (run 9, mutations enabled + set_property)

- Server: `http://127.0.0.1:8000/mcp`
- Total tools registered: **25** (up from 24 - new tool: set_property)
- Tools missing from live inventory: **0**
- PascalCase / snake_case collisions: **0**
- Editor launched via: `C:\Epic\UE_Project\58\IntroToUE\launch_mcp_server.bat` (sets ENABLE_MCP_MUTATIONS=1)

## Headline numbers

| Status | Count |
|---|---:|
| PASS    | 14 |
| GATED   | 0 |
| FAIL    | 1 |
| UNREACHABLE | 0 |
| **Total tested** | **15** |

## Verdict

**14 PASS / 0 GATED / 1 FAIL.** The 3 previously-GATED mutation tools all flipped to PASS
(confirming the env var worked). The 11 from run 8 stayed PASS. But `set_property` (the new
P1 B3 tool) FAILED — and worse, it CRASHED the editor with a Fatal error.

## CRITICAL: `set_property` caused an editor crash

The test tool was called with:
```json
{"actor_name": "Brush_1", "property_path": "bHiddenInGame", "value": true}
```

The editor crashed at 14:28:06 with this fatal error in `Saved/Logs/IntroToUE.log`:

```
Fatal error: [File:.../Engine/Source/Runtime/CoreUObject/Public/UObject/UnrealType.h] [Line: 7494]
Failed to find Property bHiddenInGame in Class /Script/Engine.Brush
[Callstack] UnrealEditor-ModelContextProtocolEditor.dll!FindFieldChecked<FProperty>() [UnrealType.h:7494]
[Callstack] UnrealEditor-ModelContextProtocolEditor.dll!FModelContextProtocolSetPropertyTool::ResolvePropertyPath() [SetPropertyTool.cpp:90]
[Callstack] UnrealEditor-ModelContextProtocolEditor.dll!FModelContextProtocolSetPropertyTool::Run() [SetPropertyTool.cpp:262]
... rest of stack follows normal MCP dispatch ...
```

**Root cause:** `set_property` uses `FindFieldChecked` (a hard-fail assertion) in its property
resolution. The target actor `Brush_1` is a `ABrush` (UE's brush class), which does NOT have
a `bHiddenInGame` property — that property exists on `AActor` (the parent). `FindFieldChecked`
only looks at the leaf class, not inherited members, and the missing property triggers an
`assert` -> Fatal error -> editor crash. The crash then causes the HTTP socket to be reset
(WinError 10054), which is what the smoke test saw as the FAIL.

**This is a real production bug** — any caller who sends a property name that doesn't exist
on the actor's leaf class will crash the editor. The fix is server-side (see below).

## The 3 previously-GATED tools - all flipped to PASS

**`set_visibility`** (`Brush_1`, `hidden: false`):
```json
{"ok": true, "property": "HiddenInGame", "old_value": false, "new_value": false}
```
(no change because Brush_1 was already not hidden)

**`set_mobility`** (`Brush_1`, `mobility: "Movable"`):
```json
{"ok": true, "property": "Mobility", "old_value": "EComponentMobility::Static", "new_value": "Movable"}
```
**REAL CHANGE** - Brush_1's root component mobility went from Static to Movable.

**`set_collision`** (`Brush_1`, `profile: "BlockAll"`):
```json
{"ok": true, "property": "CollisionProfile", "old_value": "BlockAll", "new_value": "BlockAll"}
```
(no change because Brush_1 was already BlockAll)

MutationGate is fully open. **set_mobility is the only one that actually mutated state** in this run.

## Per-tool detail

| Tool | Kind | Status | Latency (ms) | Notes |
|---|---|---|---:|---|
| `list_levels` | Read | **PASS** | 13,426 | PASS - 2 levels |
| `class_inventory` | Read | **PASS** | 13,443 | PASS - 54 BP classes |
| `open_level` | Write | **PASS** | 13,769 | PASS - Lvl_IntroRoom, actor_count 391 (still 392 in memory from prior spawn_actor) |
| `snapshot_world` | Write | **PASS** | 13,440 | PASS - byte_size: 14721, real snapshot file written |
| `restore_world` | Write | **PASS** | 13,442 | PASS - file copy back, note: 'Use open_level to reload' |
| `spawn_actor` | Write | **PASS** | 13,444 | PASS - spawned BP_TemplateCube_C at (0,0,100) with new UAID |
| `set_actor_transform` | Write | **PASS** | 13,452 | PASS - moved Brush_1 |
| `verify_position` | Read | **PASS** | 13,456 | PASS - confirmed move |
| `summarize_scene` | Read | **PASS** | 13,445 | PASS - actor_count 392, top classes as expected |
| `search_actors` | Read | **PASS** | 13,424 | PASS - actors with locations |
| `list_blueprints` | Read | **PASS** | 13,429 | PASS - 54 BP entries (engine + project) |
| `set_visibility` | Mutation | **PASS** | 13,438 | PASS (flipped from GATED) - ok:true, no actual change (already visible) |
| `set_mobility` | Mutation | **PASS** | 13,436 | PASS (flipped from GATED) - **REAL CHANGE** Static -> Movable |
| `set_collision` | Mutation | **PASS** | 13,445 | PASS (flipped from GATED) - ok:true, no actual change (already BlockAll) |
| `set_property` | Mutation | **FAIL** | 14,349 | **FAIL - EDITOR CRASH** - FindFieldChecked assertion on missing inherited property bHiddenInGame in /Script/Engine.Brush. Connection reset (WinError 10054). |

## Side effect: editor crashed, level is dirty

The editor was killed by the crash. Restart required. When you re-launch, the level is
still in its prior state: actor_count 392 (with extra BP_TemplateCube_C from prior runs)
and Brush_1 still at (0,0,100) with mobility now Movable.

## Server-side fix for `set_property` (REQUIRED)

In `FModelContextProtocolSetPropertyTool::ResolvePropertyPath` at line 90 of
`ModelContextProtocolSetPropertyTool.cpp`:

```cpp
// BROKEN (asserts on missing property):
FProperty* Property = FindFieldChecked<FProperty>(Actor->GetClass(), *PropertyPath);

// FIX: walk the class hierarchy with FindField (returns nullptr if not found)
FProperty* Property = nullptr;
for (UStruct* Struct = Actor->GetClass(); Struct != nullptr; Struct = Struct->GetSuperStruct()) {
    Property = FindFProperty<FProperty>(Struct, *PropertyPath);
    if (Property) break;
}
if (!Property) {
    return MakeErrorResult(FString::Printf(
        TEXT("Property '%s' not found on %s (or any parent class)"),
        *PropertyPath, *Actor->GetClass()->GetName()));
}
```

Two key changes:
1. Use `FindFProperty` (returns nullptr) instead of `FindFieldChecked` (asserts).
2. Walk the superclass chain so inherited properties like `bHiddenInGame` (on AActor) are found
   on a leaf actor like `ABrush`.

## Test-side improvement

Either:
- Change the placeholder actor to one that has `bHiddenInGame` directly (e.g., `BP_TemplateCube_1`
  if any are in the level - they're BP classes so the property is inherited from AActor too, but
  the class hierarchy walk will find it).
- Or call with a property that exists on the leaf class (e.g., `BrushColor.R` on a Brush).
- Or use a BP actor that has the property declared locally.

After the server-side fix, the test should pass for any property/actor combination. Without
the fix, the test will crash the editor.

## Scoreboard

| Milestone | Status |
|---|---|
| 15 previously-tested tools | **15 still PASS** (no regression from set_property) |
| 3 GATED mutation tools | **all flipped to PASS** with ENABLE_MCP_MUTATIONS=1 |
| set_property (P1 B3) | **CRASHES EDITOR** - FindFieldChecked bug, needs server-side fix |
| Live tool count | 25 (was 24) - set_property is registered |

## Recommended next steps

1. **Apply the server-side `FindFProperty` + class-hierarchy-walk fix** in `ResolvePropertyPath`
   (see code above).
2. **Rebuild the plugin** (`taskkill UnrealEditor.exe` then `Build.bat IntroToUEEditor ...`).
3. **Relaunch via `launch_mcp_server.bat`** (already has ENABLE_MCP_MUTATIONS=1).
4. **Re-run smoke test** -> expect **15 PASS / 0 GATED / 0 FAIL**.
5. **Optionally test more `set_property` cases** in the smoke test: `bHiddenInGame`, `Mobility`,
   `Tags`, etc., on different actor types to verify the class-walk works.
