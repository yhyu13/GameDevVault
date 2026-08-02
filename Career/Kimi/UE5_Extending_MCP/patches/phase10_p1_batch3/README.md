# Phase 10: P1 Batch 3 — `set_property` (FProperty Reflection Setter)

## Summary

Adds the **16th MCP tool**: `set_property`. A generic FProperty reflection setter that lets an MCP client mutate *any* UPROPERTY on an actor by name, walking the class hierarchy for inherited properties and supporting nested object-property paths (e.g. `MyComponent.SomeFlag`).

The tool is gated behind `ENABLE_MCP_MUTATIONS=1` and enforces a denylist of forbidden path prefixes (`RootComponent.*`, `Tags`, `FolderPath`) to prevent accidentally destructive edits (transform/component swaps, layer reassignment, tag churn).

## Tool: `set_property`

**Input schema:**
```json
{
  "actor_name": "string",        // required — exact actor name in the editor world
  "property_path": "string",     // required — dot-separated UPROPERTY path, supports nested FObjectProperty hops
  "value": <any JSON value>      // required — string, number, boolean, or null (mapped to UE text import syntax)
}
```

**Output schema:**
```json
{
  "ok": true,
  "property": "PropertyName",
  "old_value": <json>,
  "new_value": <json>
}
```

**Notes:**
- Property lookup walks the class chain via `FindFProperty<FProperty>` over `UStruct::GetSuperStruct()` — inherited UPROPERTYs resolve transparently.
- Type coercion uses `FProperty::ImportText_Direct` (string-side) and `FProperty::ExportTextItem_Direct` (read-back), so any type with valid import/export text works: `float`, `double`, int family, `bool`, `FString`, `FName`, `FText`, `FVector`, `FRotator`, enums, structs.
- Calls `TargetActor->Modify()` before write so the change goes into the editor's undo buffer.
- Failure modes return `MakeErrorResult(...)` (MutationGate disabled / missing field / forbidden path / actor not found / property not found / unsupported JSON type).

## Files Changed

### New Files (2)
- `Engine/Plugins/Experimental/ModelContextProtocol/Source/ModelContextProtocolEditor/Public/ModelContextProtocolSetPropertyTool.h`
- `Engine/Plugins/Experimental/ModelContextProtocol/Source/ModelContextProtocolEditor/Private/ModelContextProtocolSetPropertyTool.cpp`

### Modified Files (2)
- `Engine/Plugins/Experimental/ModelContextProtocol/Source/ModelContextProtocolEditor/Public/ModelContextProtocolEditor.h`
  - Forward declaration for `FModelContextProtocolSetPropertyTool`
  - `TSharedPtr<FModelContextProtocolSetPropertyTool> SetPropertyTool;` member
- `Engine/Plugins/Experimental/ModelContextProtocol/Source/ModelContextProtocolEditor/Private/ModelContextProtocolEditor.cpp`
  - `#include "ModelContextProtocolSetPropertyTool.h"`
  - `MakeShared` + `Module->AddTool` registration block in `RegisterBuiltinEditorTools()`
  - `Module->RemoveTool` line in `DeregisterBuiltinEditorTools()`

## Build Target

- Module: `ModelContextProtocolEditor`
- Configuration: UE5 Editor Win64 Development
- No new dependencies — uses existing `Editor.h`, `Engine/World.h`, `EngineUtils.h`, `UObject/UnrealType.h`, `ModelContextProtocolMutationGate.h` (all already in the editor module's include graph).

## Patch Validation

The patch was validated end-to-end:

1. Created a pre-phase10 scratch state by reverting the three `SetPropertyTool` additions in `ModelContextProtocolEditor.h` and `ModelContextProtocolEditor.cpp`.
2. `patch -p5 --dry-run -i phase10_p1_batch3.patch` → all 4 files check cleanly (no offset warnings, no fuzz).
3. `patch -p5 -i phase10_p1_batch3.patch` (actual apply) → succeeded on all 4 files.
4. `diff` between patched result and `C:\Epic\UE_Engine\UE5_8\UnrealEngine\Engine\Plugins\Experimental\ModelContextProtocol\...` → **empty output for all 4 files** (byte-identical to the live engine state).

## Apply Instructions

```bash
cd "C:\Epic\UE_Engine\UE5_8\UnrealEngine\Engine\Plugins\Experimental\ModelContextProtocol"
patch -p5 -i "C:\Git-repo-my\GameDevVault\Career\Kimi\UE5_Extending_MCP\patches\phase10_p1_batch3\phase10_p1_batch3.patch"
```

Then rebuild the editor:

```powershell
& "C:\Epic\UE_Engine\UE5_8\UnrealEngine\Engine\Build\BatchFiles\Build.bat" `
    ModelContextProtocolEditorEditor Win64 Development `
    -Project="C:\Epic\UE_Project\58\IntroToUE\IntroToUE.uproject" `
    -WaitMutex
```

Launch with `ENABLE_MCP_MUTATIONS=1` to unlock the mutation tools (`set_visibility`, `set_mobility`, `set_collision`, **`set_property`**):

```powershell
$env:ENABLE_MCP_MUTATIONS=1
& "C:\Epic\UE_Engine\UE5_8\UnrealEngine\Engine\Binaries\Win64\UnrealEditor.exe" `
    "C:\Epic\UE_Project\58\IntroToUE\IntroToUE.uproject" `
    -ModelContextProtocolServer
```

## Smoke Test Sketch

```python
import json, urllib.request

def call(name, args):
    req = urllib.request.Request(
        "http://127.0.0.1:8000/mcp",
        data=json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call",
                         "params":{"name":name,"arguments":args}}).encode(),
        headers={"Content-Type":"application/json"})
    return json.loads(urllib.request.urlopen(req).read())["result"]["content"][0]["text"]

# Sanity: mutate a non-sensitive UPROPERTY on an existing actor
print(call("set_property", {
    "actor_name": "BP_TemplateCube_C_2",
    "property_path": "bCanBeDamaged",
    "value": True
}))
# → {"ok":true,"property":"bCanBeDamaged","old_value":false,"new_value":true}
```

## Tool Inventory After Phase 10

16 built-in editor tools registered at `ModelContextProtocolEditor` startup:

| # | Tool | Phase | Mutation? |
|---|------|-------|-----------|
| 1 | `get_editor_context` | 1 | – |
| 2 | `capture_viewport` | 3 | – |
| 3 | `save_current_level` | 6 | – |
| 4 | `list_levels` | 7 (P0) | – |
| 5 | `class_inventory` | 7 (P0) | – |
| 6 | `open_level` | 7 (P0) | – |
| 7 | `snapshot_world` | 7 (P0) | – |
| 8 | `restore_world` | 7 (P0) | – |
| 9 | `spawn_actor` | 7 (P0) | ✅ |
| 10 | `set_actor_transform` | 7 (P0) | ✅ |
| 11 | `verify_position` | 7 (P0) | – |
| 12 | `summarize_scene` | 7 (P0) | – |
| 13 | `search_actors` | 8 (P1 B1) | – |
| 14 | `list_blueprints` | 8 (P1 B1) | – |
| 15 | `set_visibility` / `set_mobility` / `set_collision` | 8 (P1 B2) | ✅ |
| **16** | **`set_property`** | **10 (P1 B3)** | ✅ |

## Next Steps (Backlog)

From the [roadmap memory](../gap_analysis_and_roadmap.md):

- P1 Batch 4: `attach_actor`, `add_component`
- P1 Batch 5: `duplicate_actor`, `bulk_spawn`, `bulk_delete`
- P1 Batch 6: `simulate_error` middleware
- P2 (8 tools): transaction / undo / redo / list_data_layers / measure_distance / list_assets / asset_metadata / save_snapshot / load_snapshot