# Phase 2: get_editor_context

## What It Does

Adds an MCP tool `get_editor_context` that lets LLM clients query the current Unreal Editor state and receive structured JSON back.

### Tool Schema

```json
{
  "name": "get_editor_context",
  "description": "Query the current Unreal Editor state including selected actors, current level, editor mode, and world statistics. Returns structured JSON.",
  "inputSchema": {
    "type": "object"
  }
}
```

### Example Output

```json
{
  "current_level": "PersistentLevel",
  "world_type": "Editor",
  "actor_count": 42,
  "is_pie": false,
  "is_simulating": false,
  "selected_actors": [
    {"name": "PointLight_0", "class": "APointLight"},
    {"name": "BP_Door_C_0", "class": "BP_Door_C"}
  ],
  "selected_actor_count": 2
}
```

## Files Changed

| File | Type | Description |
|------|------|-------------|
| `ModelContextProtocolEditor.h` | Modified | Forward-declares tool; adds `RegisterBuiltinEditorTools()` / `DeregisterBuiltinEditorTools()` and member pointer |
| `ModelContextProtocolEditor.cpp` | Modified | Calls register/deregister; implements `RegisterBuiltinEditorTools()` and `DeregisterBuiltinEditorTools()` |
| `ModelContextProtocolEditorContextTool.h` | New | Tool declaration |
| `ModelContextProtocolEditorContextTool.cpp` | New | Tool implementation — queries `GEditor`, `UWorld`, selected actors, serializes to JSON |

## Key Design Decisions

1. **Editor module, not Engine module** — `get_editor_context` needs `GEditor`, `USelection`, and other editor-only APIs. It lives in `ModelContextProtocolEditor` and registers via the editor module's startup path.

2. **No parameters** — Pure read-only query. Returns everything the LLM might need in one call to minimize round-trips.

3. **JSON text result** — Uses `MakeTextResult()` with a compact JSON string rather than `MakeStructuredContentResult()`. The LLM client parses the JSON text. This keeps the implementation simple and avoids dependency on `FJsonDomBuilder` nuances.

4. **Defensive null checks** — Guards `GEditor` and `EditorWorld` with graceful fallbacks (`"Unknown"`, `0`).

5. **No new dependencies** — Uses headers already available in the Editor module (`Editor.h`, `Engine/World.h`, `EngineUtils.h`, `Serialization/JsonSerializer.h`). Also pulls in `Selection.h` for `USelection` iteration.

## Build Fix Notes (v1.1)

- **Original bug**: `FSelectionIterator` requires the full class definition from `Selection.h`, but `Editor.h` only forward-declares it. Also, `USelection` is only forward-declared in `EditorEngine.h`.
- **Fix**: Added explicit `#include "Selection.h"`. Replaced `FSelectionIterator` loop with `USelection::Num()` / `GetSelectedObject()` index-based iteration, which works with the forward-declared `USelection` pointer returned by `GEditor->GetSelectedActors()`.

## Apply

```bash
cd Engine/Plugins/Experimental/ModelContextProtocol
patch -p5 < phase2_get_editor_context.patch
```

## Next (Remaining Phase 1 / v0.2)

| # | Feature | Size | Module |
|---|---------|------|--------|
| 3 | `capture_viewport` | M | Editor (screenshot + base64) |
| 4 | `progress reporting` | M | Core (tool execution framework) |
| 5 | `stdio transport` | XL | Core (new transport layer) |

## Limitations

- Does not include viewport camera transform (requires `FEditorViewportClient` iteration, adds complexity).
- Does not include asset browser selection (could be added later).
- Actor count iterates the entire world; for very large worlds this is O(N). Consider caching or sampling if needed.

## Source Evidence

- Tool registration pattern: `IModelContextProtocolModule::AddTool()` / `RemoveTool()` — `Engine/Plugins/Experimental/ModelContextProtocol/Source/ModelContextProtocol/Public/IModelContextProtocolModule.h`
- Editor module startup: `ModelContextProtocolEditor.cpp` lines 17–91
- `GEditor` world context: `UnrealEd/Public/Editor.h`
- `USelection` iteration: `UnrealEd/Public/Selection.h` (`Num()`, `GetSelectedObject()`) — `GEditor->GetSelectedActors()`
