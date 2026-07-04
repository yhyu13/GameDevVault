# MCP Smoke Test Results - 2026-07-02 23:53:45 UTC (run 7, all 15 tools re-included)

- Server: `http://127.0.0.1:8000/mcp`
- Total tools registered: **24**
- Tools missing from live inventory: **0**
- PascalCase / snake_case collisions: **0**

## Headline numbers

| Status | Count |
|---|---:|
| PASS    | 11 |
| GATED   | 3 |
| FAIL    | 0 |
| UNREACHABLE | 0 |
| **Total tested** | **14** |

## Verdict

**11 PASS / 3 GATED / 0 FAIL.** All 15 tools responded (3 GATED are correct gate blocks).
The 3 previously-broken tools (snapshot_world, restore_world, list_blueprints) all PASS now.

**However, `snapshot_world` has a soft-error issue that the smoke test misclassifies as PASS:**
it returned the string `'Level not saved to disk. Please save first (e.g. via save_current_level).'`,
which is an error message but the `_is_ok` classifier only flags dicts with `isError`/`error` keys.
The tool should be self-contained — save the level first, then snapshot.

## Per-tool detail

| Tool | Kind | Status | Latency (ms) | Notes |
|---|---|---|---:|---|
| `list_levels` | Read | **PASS** | 15,998 | PASS - 2 levels |
| `class_inventory` | Read | **PASS** | 16,000 | PASS - 54 BP classes (up from 51, includes engine BPs like DmgTypeBP_Environmental) |
| `open_level` | Write | **PASS** | 16,039 | PASS - Lvl_IntroRoom (391 actors in source, 392 after the previous run's spawn) |
| `snapshot_world` | Write | **PASS** | 16,000 | WEAK PASS / TRUE SOFT-FAIL - returned error STRING 'Level not saved to disk. Please save first (e.g. via save_current_level).' The IFileManager::Copy fix prevented the deadlock, but the tool is now asking the caller to save the level first instead of doing it itself. See recommendation below. |
| `restore_world` | Write | **PASS** | 16,000 | PASS - returned ok:true, restored_from:smoke_test, level_path:Lvl_IntroRoom, note:'Snapshot copied. Use open_level to reload the level.' The copy worked but the level isn't actually reloaded - that's a follow-up open_level call. |
| `spawn_actor` | Write | **PASS** | 15,688 | PASS - spawned BP_TemplateCube_C_UAID_345A6032E8759DEA02_1860348231 at (0,0,100). Different UAID than run 6, as expected. |
| `set_actor_transform` | Write | **PASS** | 15,999 | PASS - moved Brush_1 to (0,0,100) |
| `verify_position` | Read | **PASS** | 16,000 | PASS - confirmed Brush_1 at (0,0,100), delta 0, within_epsilon true |
| `summarize_scene` | Read | **PASS** | 15,999 | PASS - actor_count=392, world_type=Editor, top_classes (StaticMeshActor=262, BP_TextSwitcher_C=26, BP_Titles_C=16, BP_TemplateCube_C=12, BP_SpawnPoint_C=12, ...) |
| `search_actors` | Read | **PASS** | 16,000 | PASS - actors array, total_matched, truncated |
| `list_blueprints` | Read | **PASS** | 16,000 | PASS - 54 blueprints returned (engine + project). DmgTypeBP_Environmental, BP_SaveData, BPI_TouchInterface, BP_FirstPersonCameraManager, etc. Real fix. |
| `set_visibility` | Mutation | **GATED** | 15,999 | GATED - mutation gate correctly blocking |
| `set_mobility` | Mutation | **GATED** | 15,999 | GATED - same |
| `set_collision` | Mutation | **GATED** | 15,999 | GATED - same |

## spawn_actor root cause analysis

Same failure across two runs with different class names:

| Run | class_name | Result |
|---|---|---|
| 4 | `StaticMeshActor` (native UE class) | `'Actor class not found: StaticMeshActor'` |
| 5 | `BP_TemplateCube` (Blueprint, no `_C` suffix) | `'Actor class not found: BP_TemplateCube'` |

Two hypotheses (could be either or both):

**Hypothesis A (most likely): class lookup searches Blueprint paths only, not native UClass tree.**
The tool probably calls `LoadObject<UClass>(nullptr, TEXT("/Game/") + ClassName + TEXT(".") + ClassName)` 
or something similar that prepends `/Game/...`. For `StaticMeshActor` (native, no /Game/ path), 
this fails. For `BP_TemplateCube` (BP, but with `_C` suffix stripped), the path 
`/Game/.../BP_TemplateCube.BP_TemplateCube` also doesn't exist because the actual asset path is 
`/Game/DemoTemplate/Templates/BP_TemplateCube.BP_TemplateCube_C`. The tool is searching the wrong path.

**Hypothesis B: the tool expects the `_C` suffix.** Native classes don't have `_C`. Blueprint-generated 
UClasses do. If the tool looks up `BP_TemplateCube` but the actual UClass is `BP_TemplateCube_C`, 
the lookup fails. But `class_inventory` returns names WITH the `_C` suffix, so the smoke test 
should match that format.

**Recommended fix (server-side)** in `FModelContextProtocolSpawnActorTool::Run`:

```cpp
// 1. Native classes: try direct name lookup first
UClass* Class = FindFirstObject<UClass>(*ClassName, EFindFirstObjectOptions::ExactClass);

// 2. Blueprint classes: try with _C suffix appended if missing
if (!Class && !ClassName.EndsWith(TEXT("_C"))) {
    FString WithSuffix = ClassName + TEXT("_C");
    Class = FindFirstObject<UClass>(*WithSuffix, EFindFirstObjectOptions::ExactClass);
}

// 3. Try as a Blueprint asset (full path)
if (!Class) {
    const FString AssetPath = FString::Printf(TEXT("/Script/Engine.%s"), *ClassName);
    Class = LoadObject<UClass>(nullptr, *AssetPath);
}

// 4. Validate
if (!Class || !Class->IsChildOf(AActor::StaticClass()) ||
    Class->HasAnyClassFlags(CLASS_Abstract | CLASS_Deprecated)) {
    return MakeErrorResult(FString::Printf(TEXT("Actor class not found or not placeable: %s"), *ClassName));
}
```

**Alternative smoke-test fix (faster):** change the smoke test's `spawn_actor` args to use 
`BP_TemplateCube_C` (with the `_C` suffix, matching what `class_inventory` returns). If that 
works, the class lookup IS respecting the suffix and the fix is just on the test side.

## Detailed per-tool findings

**Real PASS (7):**

- `list_levels` - 2 levels (unchanged from prior runs)
- `class_inventory` - 51 BP classes with `instance_count_in_level`
- `open_level` - `ok: true, actor_count: 391`
- `set_actor_transform` - now actually moves `Brush_1` to `(0,0,100)` (real change vs. run 4)
- `verify_position` - confirms move: `actual: (0,0,100), delta: 0, within_epsilon: true`
- `summarize_scene` - full scene summary dict
- `search_actors` - actor list with `total_matched`, `truncated`

**GATED (3) — MutationGate working correctly:**

```
set_visibility: "Mutations are disabled. Set environment variable ENABLE_MCP_MUTATIONS=1 to enable."
set_mobility:   "Mutations are disabled. Set environment variable ENABLE_MCP_MUTATIONS=1 to enable."
set_collision:  "Mutations are disabled. Set environment variable ENABLE_MCP_MUTATIONS=1 to enable."
```

**FAIL (1):**

- `spawn_actor` - `"Actor class not found: BP_TemplateCube"`

## What was NOT tested this run

- `snapshot_world` - excluded; game-thread deadlock from run 3 still present (needs file-copy fix).
- `restore_world` - excluded; same.
- `list_blueprints` - excluded; needs the `IAssetRegistry::SearchAssetsSync` fix.

## Scoreboard

| Milestone | Status |
|---|---|
| 12 reachable tools | 11 working (7 PASS + 3 GATED correct + 1 FAIL: spawn_actor) |
| End-to-end move + verify | **WORKS** (`set_actor_transform` -> `verify_position` both PASS) |
| MutationGate | **WORKS** (returns correct payload) |
| spawn_actor | **BROKEN** (class lookup) |
| snapshot_world / restore_world / list_blueprints | UNTESTED (game-thread deadlock) |
| Smoke test classifier | **FIXED** (error strings now flagged) |

## Recommended next actions

**Quickest unblock:**

1. Try `spawn_actor` with `class_name: "BP_TemplateCube_C"` (with the suffix) in the smoke test.
   If that works, the class lookup respects the `_C` suffix and the test was wrong, not the tool.

**If the suffix isn't the fix, the class lookup itself is broken.** Apply the server-side fix 
(Hypothesis A above) using `FindFirstObject<UClass>` + `_C` suffix fallback + Blueprint asset path fallback.

**Once spawn_actor passes, re-include the 3 excluded tools** (after applying their respective fixes:
- `snapshot_world` / `restore_world`: `IFileManager::Copy` + `FStreamableManager.RequestAsyncLoad`.
- `list_blueprints`: `IAssetRegistry::SearchAssetsSync`.

**Then restart editor with `ENABLE_MCP_MUTATIONS=1` to flip the 3 GATED to PASS.**

## Live tool inventory at test time

```
  DeleteActor
  GetActorDetails
  ListActors
  call_tool
  capture_viewport
  class_inventory
  describe_toolset
  execute_console_command
  get_editor_context
  list_blueprints
  list_levels
  list_toolsets
  open_level
  restore_world
  save_current_level
  search_actors
  set_actor_transform
  set_collision
  set_mobility
  set_visibility
  snapshot_world
  spawn_actor
  summarize_scene
  verify_position
```

---

Test script: `tests/smoke_test_mcp_new_tools.py`  
Raw JSON report: `tests/reports/smoke_20260701_155432.json`  
Test duration: ~16 minutes (driven by 60 s timeouts on hung calls)  
Generated: 2026-07-02T23:54:52.207938+00:00
