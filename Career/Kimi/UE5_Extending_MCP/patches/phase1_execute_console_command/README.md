# Phase 1 Patch: execute_console_command

> **Feature**: `execute_console_command` MCP tool  
> **Effort**: S (1-2 days)  
> **Scope**: Easiest Phase 1 feature — adds a built-in tool that executes UE console commands via `GEngine->Exec()`

---

## What This Patch Does

Adds a new MCP tool `execute_console_command` that lets LLM clients (Claude Code, Cursor, etc.) run any Unreal Engine console command as if typed into the `~` console.

### Example Usage (from LLM client)

```json
{
  "name": "execute_console_command",
  "arguments": {
    "command": "stat fps"
  }
}
```

**Returns**:
```
Executed: stat fps

Console Output:
Frame: 120.5 FPS
...
```

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "description": "Console command string to execute. e.g., 'stat fps', 'show collision', 'r.ScreenPercentage 50'"
    }
  },
  "required": ["command"]
}
```

---

## Files Changed

| File | Change |
|------|--------|
| `ModelContextProtocolEngineModule.cpp` | Modified — adds `RegisterBuiltinTools()` / `DeregisterBuiltinTools()` |
| `ModelContextProtocolConsoleTool.h` | **New** — tool declaration |
| `ModelContextProtocolConsoleTool.cpp` | **New** — tool implementation |

---

## How to Apply

```bash
# From your UE5 engine root
cd Engine/Plugins/Experimental/ModelContextProtocol

# Apply the patch
patch -p5 < phase1_execute_console_command.patch

# Rebuild the plugin
# (Via Visual Studio or Unreal Build Tool)
```

---

## Technical Details

- **No new module dependencies** — uses existing `Engine` module (already in `PrivateDependencyModuleNames`)
- **No deprecated API usage** — implements `IModelContextProtocolTool` directly, not the deprecated `UModelContextProtocolToolLibrary`
- **Log capture** — captures console output during execution via `FOutputDeviceArchiveWrapper` so the LLM sees results
- **World context** — tries `GEngine->GetCurrentPlayWorld()` first, falls back to editor world if not in PIE
- **Error handling** — returns MCP-compliant error if command is not recognized or parameters are missing

---

## Limitations (Known)

- **No progress reporting** — synchronous execution, completes immediately
- **No cancel support** — console commands run to completion; `CancelAsync()` is inherited no-op
- **No schema validation** — input is parsed but not validated against JSON Schema (follows existing plugin pattern)
- **Log capture may be incomplete** — some commands write to `UE_LOG` directly, bypassing the output device

---

## Next Steps (Remaining Phase 1 Features)

After applying this patch, proceed to the next easiest features:

| # | Feature | Size | Why Next? |
|---|---------|------|-----------|
| 2 | `get_editor_context` | M | Exposes selected actors, viewport, level — foundational for contextual questions |
| 3 | `capture_viewport` | M | Enables vision-model debugging (screenshot → analyze) |
| 4 | `progress reporting` | M | Required for long operations (build, cook) |
| 5 | `stdio transport` | XL | Unlocks CLI-based LLM clients (Claude Code, Zed) |

---

*Patch generated: 2026-06-28*  
*Based on UE 5.8 `ModelContextProtocol` plugin source*
