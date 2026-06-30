# Phase 7: MCP API v2 P0 Tools (9 Tools)

## Summary

Implemented all 9 P0 (critical-path) tools from the MCP API v2 specification. These tools provide level/asset discovery, scene manipulation, actor spawning, and scene summarization capabilities.

## Tools Added

| Tool | Type | Description |
|------|------|-------------|
| `list_levels` | Read | Lists all .umap levels in the project via AssetRegistry |
| `class_inventory` | Read | Lists spawnable actor classes (blueprints + native) |
| `open_level` | Write | Opens a level by path with safety gate (MCP_ALLOWED_ROOTS) |
| `snapshot_world` | Write | Saves current level to `Saved/Snapshots/<label>.umap` |
| `restore_world` | Write | Loads a previously saved snapshot |
| `spawn_actor` | Write | Spawns actor by class name with location/rotation/scale |
| `set_actor_transform` | Write | Updates actor transform with sweep and delta cap |
| `verify_position` | Read | Verifies actor position against expected with tolerance |
| `summarize_scene` | Read | Returns actor count by class with optional filtering |

## Files Changed

### New Files (18)
- `ModelContextProtocolListLevelsTool.h/.cpp`
- `ModelContextProtocolClassInventoryTool.h/.cpp`
- `ModelContextProtocolOpenLevelTool.h/.cpp`
- `ModelContextProtocolSnapshotWorldTool.h/.cpp`
- `ModelContextProtocolRestoreWorldTool.h/.cpp`
- `ModelContextProtocolSpawnActorTool.h/.cpp`
- `ModelContextProtocolSetActorTransformTool.h/.cpp`
- `ModelContextProtocolVerifyPositionTool.h/.cpp`
- `ModelContextProtocolSummarizeSceneTool.h/.cpp`

### Modified Files (5)
- `ModelContextProtocolEditor.h` — Added forward declarations and member pointers for all 9 tools
- `ModelContextProtocolEditor.cpp` — Registered all 9 tools in `RegisterBuiltinEditorTools()`
- `ModelContextProtocolEditor.Build.cs` — Added `"AssetRegistry"` to private dependencies
- `CustomMcpEditorToolLibrary.h` — Removed `SpawnActor` and `SetActorTransform` UFUNCTIONs (replaced by C++ tools)
- `CustomMcpEditorToolLibrary.cpp` — Removed `SpawnActor` and `SetActorTransform` implementations

## Safety Features

- `open_level`: Validates paths against `MCP_ALLOWED_ROOTS` (default: `/Game/`)
- `snapshot_world`: Pins to `Saved/Snapshots/` directory, 50-snapshot quota
- `set_actor_transform`: Caps delta movement at `1e6 cm` to prevent runaway
- `spawn_actor`: Uses `UEditorActorSubsystem::SpawnActorFromClass` for undo support

## Build Status

✅ **Build: Succeeded** (UE5 Editor Win64 Development)
- No compilation errors
- No linking errors
- All 9 tools registered at module startup

## Spec Compliance

All tools follow the MCP API v2 specification (`MCP_API_Spec_v2.md`) with:
- Snake_case naming (`spawn_actor`, `set_actor_transform`)
- JSON Schema v2 input/output definitions
- Progress reporting via `IProgressReporter` where applicable

## Next Steps

- P1 Tools (8): Asset/Blueprint/Material operations
- P2 Tools (8): Advanced workflow (run_game, build, package, etc.)
