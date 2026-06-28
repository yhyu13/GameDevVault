# Phase 4: Progress Reporting

## What It Does

Extends the MCP tool execution pipeline to support **progress notifications** for long-running async tools. When a client sends a `progressToken` in `params._meta.progressToken`, tools can now report intermediate progress via `notifications/progress` SSE messages.

This is **framework infrastructure** — no new end-user tools are added. Instead, the `IModelContextProtocolTool` interface gains a 4-argument `RunAsync` overload that accepts a `FProgressCallback`. Future long-running tools (build, cook, lighting bake) can call this callback to stream progress to the LLM client.

### MCP Progress Notification Flow

```
Client request: tools/call
  params._meta.progressToken: "abc123"

Server -> Tool->RunAsync(..., OnProgress)

During execution:
  OnProgress(25, 100)  -- SSE: notifications/progress {token: "abc123", progress: 25}
  OnProgress(50, 100)  -- SSE: notifications/progress {token: "abc123", progress: 50}
  OnProgress(75, 100)  -- SSE: notifications/progress {token: "abc123", progress: 75}

On completion:
  SSE: result {content: [...]}
```

### How a Tool Uses Progress Reporting

```cpp
void FMyLongRunningTool::RunAsync(
    const FModelContextProtocolToolRequestId& RequestId,
    const TSharedPtr<FJsonObject>& Params,
    const FResultCallback& OnComplete,
    const FProgressCallback& OnProgress)
{
    // Total work = 10 steps
    for (int32 i = 0; i < 10; ++i)
    {
        DoWorkStep(i);
        OnProgress(i + 1, 10);  // Report progress after each step
    }
    OnComplete(MakeTextResult(TEXT("Done!")));
}
```

## Files Changed

| File | Module | Change |
|------|--------|--------|
| `IModelContextProtocolTool.h` | Core | Added `FProgressCallback` typedef; added 4-arg `RunAsync` overload with default delegation to 3-arg |
| `ModelContextProtocolServer.cpp` | Core | Passes progress lambda to `Tool->RunAsync`; lambda calls `SendProgressUpdate` with captured `ProgressToken` |
| `ModelContextProtocolToolAsyncAction.h` | Engine | Updated `RunAsync` declaration to 4-arg |
| `ModelContextProtocolToolAsyncAction.cpp` | Engine | Updated `RunAsync` definition to 4-arg |
| `ModelContextProtocolToolSearch.h` | Editor | Updated `FCallToolDelegate` signature; updated `FCallTool::RunAsync` declaration |
| `ModelContextProtocolToolSearch.cpp` | Editor | Updated `FCallTool::RunAsync` to forward progress callback |
| `ModelContextProtocolToolsetRegistryAdapter.h` | Editor | Updated `FToolsetRegistryToolAdapter::RunAsync` and `DispatchToolCall` declarations |
| `ModelContextProtocolToolsetRegistryAdapter.cpp` | Editor | Updated `RunAsync`, `DispatchToolCall`, and `FCallToolDelegate` lambda to forward progress |

## Key Design Decisions

1. **Backward-compatible overload** — The base `IModelContextProtocolTool` adds a 4-arg `RunAsync(RequestId, Params, OnComplete, OnProgress)` that by default delegates to the existing 3-arg `RunAsync`. Existing tools (including all currently registered tools) continue to work without modification. Only tools that explicitly override the 4-arg version gain progress reporting.

2. **ProgressToken already wired** — The server was already extracting `params._meta.progressToken` and storing it in `FModelContextProtocolToolContext`. The `SendProgressUpdate` helper was already implemented. This patch simply connects the tool interface to the existing infrastructure.

3. **No-op for tools that don't use it** — `FCallTool`, `FToolsetRegistryToolAdapter`, and `FModelContextProtocolAsyncActionTool` all accept the progress callback but don't use it themselves (they just forward it). This is correct: they're dispatchers, not long-running operations.

4. **No built-in demo tool** — This is pure framework infrastructure. A future tool like `build_lighting` or `cook_content` would override the 4-arg `RunAsync` and call `OnProgress` during its work loop.

## Apply

```bash
# Prerequisites: Phases 1-3 must be applied first
cd Engine/Plugins/Experimental/ModelContextProtocol
patch -p5 < phase4_progress_reporting.patch
```

## Build Notes

- `SendProgressUpdate` lives in `UE::ModelContextProtocol::Private` namespace; the lambda in `ModelContextProtocolServer.cpp` must fully qualify it.

## Source Evidence

- `ProgressToken` extraction: `ModelContextProtocolServer.cpp` lines 821–828
- `SendProgressUpdate`: `ModelContextProtocolServer.cpp` lines 305–308
- `CreateJsonRpcProgressResponse`: `ModelContextProtocolServer.cpp` lines 283–303
- `FModelContextProtocolToolContext`: `ModelContextProtocolSession.h` — stores `ProgressToken` and `EventStreamWrite`

## Next (Remaining v0.2)

| # | Feature | Size | Module |
|---|---------|------|--------|
| 5 | `stdio transport` | XL | Core (new transport layer) |

## Limitations

- No built-in tool currently demonstrates progress reporting. The capability is available but unused until a long-running tool is implemented.
- The `Total` parameter of `FProgressCallback` is optional but the server-side `SendProgressUpdate` currently ignores it (the MCP `notifications/progress` spec only requires `progress` and `progressToken`).
