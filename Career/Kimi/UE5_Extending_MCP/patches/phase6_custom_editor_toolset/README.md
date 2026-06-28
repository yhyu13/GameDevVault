# Phase 6: Custom Editor Toolset (Hybrid)

## What It Does

Implements a **hybrid toolset** for the UE5 MCP plugin: 5 lightweight actor inspection/mutation tools via `UModelContextProtocolEditorToolLibrary` auto-registration, plus 1 heavy tool (`save_current_level`) as a direct C++ `IModelContextProtocolTool`.

This follows **Path B** from the plan review: BP-library-style for lightweight operations, C++ for heavy/long-running operations.

### Tools Added

**Library Tools** (auto-registered via `UCustomMcpEditorToolLibrary` CDO):

| Tool | Description | Return |
|------|-------------|--------|
| `ListActors` | List all actors in current level | `FActorListResult` (array of name/class/location) |
| `GetActorDetails` | Get detailed info for actor by name | `FActorDetailsResult` (name, class, location, rotation, scale, selection) |
| `SpawnActor` | Spawn actor by class name at transform | `FSpawnActorResult` (spawned actor name or error) |
| `DeleteActor` | Delete actor by name | `FDeleteActorResult` (success/error, guards against duplicate names) |
| `SetActorTransform` | Set location/rotation/scale of actor by name | `FSetTransformResult` (success/error) |

**C++ Tool** (manually registered in `FModelContextProtocolEditorModule`):

| Tool | Description |
|------|-------------|
| `save_current_level` | Save the current level to disk via `FEditorFileUtils::SaveLevel` |

### Architecture

```
UCustomMcpEditorToolLibrary (extends UModelContextProtocolEditorToolLibrary)
  ├── CDO created on module load
  ├── PostInitProperties → RegisterTools()
  ├── FModelContextProtocolLibraryTool auto-created per UFUNCTION
  └── JSON schema auto-generated from UPROPERTY metadata

FModelContextProtocolSaveLevelTool (extends IModelContextProtocolTool)
  ├── Manually registered in RegisterBuiltinEditorTools()
  └── Run() calls FEditorFileUtils::SaveLevel(Level)
```

## Files Changed

| File | Module | Change |
|------|--------|--------|
| `CustomMcpEditorToolLibrary.h` | Editor (new) | `UCustomMcpEditorToolLibrary` class + 6 `BlueprintType` USTRUCTs (result types) + 5 `UFUNCTION` declarations |
| `CustomMcpEditorToolLibrary.cpp` | Editor (new) | Implementation of all 5 UFUNCTIONs (ListActors, GetActorDetails, SpawnActor, DeleteActor, SetActorTransform) |
| `ModelContextProtocolSaveLevelTool.h` | Editor (new) | `FModelContextProtocolSaveLevelTool` declaration |
| `ModelContextProtocolSaveLevelTool.cpp` | Editor (new) | `Run()` implementation using `FEditorFileUtils::SaveLevel` |
| `ModelContextProtocolEditor.h` | Editor | Added `FModelContextProtocolSaveLevelTool` forward declaration + `SaveLevelTool` member |
| `ModelContextProtocolEditor.cpp` | Editor | Added `CustomMcpEditorToolLibrary.h` and `ModelContextProtocolSaveLevelTool.h` includes; force CDO creation via `GetDefault<UCustomMcpEditorToolLibrary>()`; register/deregister `SaveLevelTool` |

## Key Design Decisions

1. **Library approach for lightweight tools** — `UCustomMcpEditorToolLibrary` extends `UModelContextProtocolEditorToolLibrary`. The CDO auto-registers all public `UFUNCTION`s as MCP tools via `PostInitProperties` → `RegisterTools()`. JSON schemas are auto-generated from `UPROPERTY` metadata. Zero manual registration boilerplate.

2. **C++ direct tool for heavy operation** — `save_current_level` is a direct `IModelContextProtocolTool` subclass because `FEditorFileUtils::SaveLevel` is a blocking editor operation that doesn't fit the UFUNCTION reflection model well.

3. **BlueprintType structs** — All result structs are marked `USTRUCT(BlueprintType)` so UHT allows them as UFUNCTION return types. Without this, UHT rejects the function declarations.

4. **No default parameters in UFUNCTIONs** — UHT cannot parse `FVector::OneVector` as a default parameter. Default values are omitted from declarations; the LLM client must provide all parameters. The `FunctionMetaData` system in `UModelContextProtocolToolLibrary` can still capture defaults if needed via UPROPERTY metadata.

5. **Duplicate name guard in DeleteActor** — `DeleteActor` collects all matching actors first. If multiple actors share the same name, it returns an error rather than deleting the wrong one. This is a safety measure because `AActor::GetName()` is not guaranteed to be unique.

6. **Force CDO creation** — `GetDefault<UCustomMcpEditorToolLibrary>()` in `SetupEditorIntegration()` forces the CDO to exist before tool registration, ensuring the UFUNCTIONs are discovered and registered as MCP tools.

## Apply

```bash
# Prerequisites: Phases 1-5 must be applied first
cd Engine/Plugins/Experimental/ModelContextProtocol
patch -p5 < phase6_custom_editor_toolset.patch
```

## Build Notes

- `USTRUCT(BlueprintType)` is **required** for custom structs used as UFUNCTION return types. UHT will reject `USTRUCT()` without it.
- UHT cannot parse `FVector::OneVector` / `FRotator::ZeroRotator` as default parameters. Remove defaults from UFUNCTION declarations.
- `USelection` header (`Selection.h`) is needed for `GEditor->GetSelectedActors()->IsSelected()`.
- `FindObject` with boolean `ExactClass` is deprecated; use `EFindObjectFlags::ExactClass` instead.
- `FEditorFileUtils::SaveLevel` is in `FileHelpers.h` (included via `Editor.h` in the editor module).

## Source Evidence

- `UCustomMcpEditorToolLibrary` declaration: `CustomMcpEditorToolLibrary.h` lines 100–135
- `ListActors` implementation: `CustomMcpEditorToolLibrary.cpp` lines 18–32
- `SpawnActor` implementation: `CustomMcpEditorToolLibrary.cpp` lines 49–77
- `DeleteActor` duplicate-name guard: `CustomMcpEditorToolLibrary.cpp` lines 79–106
- `SaveLevelTool::Run`: `ModelContextProtocolSaveLevelTool.cpp` lines 38–55
- CDO creation: `ModelContextProtocolEditor.cpp` line 54
- Tool registration: `ModelContextProtocolEditor.cpp` lines 96–132

## Limitations

- **Sync-only** — All library tools run synchronously on the calling thread (game thread). No `RunAsync` override, no progress reporting, no cancellation. This is acceptable for lightweight operations (milliseconds) but would be problematic for heavy operations (which is why `save_current_level` is a separate C++ tool).
- **No default parameters** — UFUNCTIONs lack default parameter values. LLM clients must provide all parameters.
- **No `isError` flag** — Library tools return structured results; error states are encoded in the result struct (`bSuccess` + `ErrorMessage`) rather than the MCP `isError` JSON field. The C++ `save_current_level` tool uses `MakeErrorResult` correctly.
- **Class name resolution** — `SpawnActor` uses `FindObject<UClass>` which requires the class to be already loaded. Dynamic class loading (e.g., Blueprint classes) may not work without `StaticLoadClass` or `FSoftClassPath`.
- **Actor name uniqueness** — `GetActorDetails` and `SetActorTransform` return the first matching actor. `DeleteActor` guards against duplicates but returns an error.

## Compatibility

- **Editor-only** — `UCustomMcpEditorToolLibrary` extends `UModelContextProtocolEditorToolLibrary` which is only available in editor builds. All tools are `#if WITH_EDITOR`.
- **Additive-only** — Does not modify existing tools. The 3 existing C++ tools (`get_editor_context`, `capture_viewport`, `execute_console_command`) remain untouched.
- **Cross-transport** — All new tools work over both HTTP+SSE and stdio (Phase 5) transports because they use the standard `IModelContextProtocolTool` / `FModelContextProtocolLibraryTool` execution path.
