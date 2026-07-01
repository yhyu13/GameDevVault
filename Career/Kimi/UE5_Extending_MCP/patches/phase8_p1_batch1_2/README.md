# Phase 8: P1 Batch 1+2 — Mutation Infrastructure + Read-only Discovery + Typed Setters

## Summary

Implemented P1 Batch 1 and Batch 2 tools from the MCP API v2 specification. These 6 tools (plus infrastructure) provide actor search, blueprint discovery, and typed actor state mutation (visibility, mobility, collision).

## Tools Added

| Tool | Type | Description |
|------|------|-------------|
| `search_actors` | Read | Search actors by name regex, class regex, or proximity |
| `list_blueprints` | Read | List all Blueprint assets with parent class and status |
| `set_visibility` | Mutation | Set actor `HiddenInGame` (gated by `ENABLE_MCP_MUTATIONS`) |
| `set_mobility` | Mutation | Set root component mobility (Static/Stationary/Movable) |
| `set_collision` | Mutation | Set collision profile (e.g. BlockAll, Pawn) |

## Infrastructure Added

- `MutationGate.h/.cpp` — Environment variable gate (`ENABLE_MCP_MUTATIONS=1`)
- `AreMcpMutationsEnabled()` / `IsErrorInjectionEnabled()` / `GetMutationsDisabledError()`

## Files Changed

### New Files (10)
- `ModelContextProtocolMutationGate.h/.cpp`
- `ModelContextProtocolSearchActorsTool.h/.cpp`
- `ModelContextProtocolListBlueprintsTool.h/.cpp`
- `ModelContextProtocolSetActorStateTools.h/.cpp` (3 tools in 1 file)

### Modified Files (2)
- `ModelContextProtocolEditor.h` — Added 6 forward declarations + TSharedPtr members
- `ModelContextProtocolEditor.cpp` — Registered all 6 tools, added includes

## Build Notes

Compilation fixes applied during build:
- `Regex.h` → `Internationalization/Regex.h` (UE5 path)
- `FRegexPattern::IsValid()` → removed (method doesn't exist in UE5)
- `EditorActorSubsystem.h` → `Subsystems/EditorActorSubsystem.h`
- `Blueprint->IsCompiled()` → `Blueprint->GeneratedClass != nullptr`
- `FAssetData::PackageGuid` → removed (field doesn't exist in UE5.8)
- `MakeTextResultFromJson()` → `FModelContextProtocolToolResult()` constructor
- `MakeErrorResult()` → `UE::ModelContextProtocol::MakeErrorResult()` (template in header)

## Build Status

✅ **Build: Succeeded** (UE5 Editor Win64 Development, 6 actions, 4.55s link time)
- DLL size: 399KB → 572KB (+43%)
- All 6 P1 tools registered at module startup

## Safety

- All mutation tools gated by `ENABLE_MCP_MUTATIONS=1` env var
- Default: mutations OFF (safe for read-only deployments)
- `set_mobility` validates enum values (Static, Stationary, Movable)
- `set_collision` uses `UPrimitiveComponent::SetCollisionProfileName`

## Next Steps

- P1 Batch 3: `set_property` (generic FProperty reflection setter)
- P1 Batch 4: `attach_actor` / `add_component`
- P1 Batch 5: `duplicate_actor` / `bulk_spawn` / `bulk_delete`
- P1 Batch 6: `simulate_error` middleware
