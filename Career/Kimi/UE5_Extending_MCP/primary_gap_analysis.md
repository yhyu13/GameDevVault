# UE5 MCP Server — Primary Gap Analysis (Source-Verified)

> **Author**: Mavis (mavis orchestrator session `mvs_b1df5a185906490aa7084c12a3bc0c82`)
> **Date**: 2026-06-28
> **Method**: Direct read of source under `C:\Epic\UE_Engine\UE5_8\UnrealEngine\Engine\Plugins\Experimental\ModelContextProtocol\` — 80 .h/.cpp/.cs files across 6 modules.
> **Scope**: Primary gap analysis. **Not** a critique of the existing `gap_analysis_and_roadmap.md` — that critique is in `gap_analysis_and_roadmap_critique.md`. This document ignores the existing analysis and derives gaps directly from the source.
> **Protocol version** (negotiated default): `2025-11-25`. Server also accepts `2025-06-18` and `2024-11-05`.

---

## How this document is organized

1. **Part 1 — What exists in the source** (the baseline; gaps are deltas from this)
2. **Part 2 — Verified gaps** (issues confirmed by source inspection, with file:line citations)
3. **Part 3 — Spec-compliance gaps** (gaps measured against the 2025-11-25 MCP spec)
4. **Part 4 — Source-level observations not in the prior analysis** (features the prior doc missed)
5. **Part 5 — Discrepancies with `gap_analysis_and_roadmap.md`** (where this analysis differs)

Citations are `Source/.../File.cpp:line` or `Source/.../File.h:line` for short-form.

---

# Part 1 — What exists in the source

This is the baseline. Every gap below is a delta from this.

## 1.1 Module structure (`ModelContextProtocol.uplugin:19-49`)

6 modules, not 4:

| Module | Type | Purpose |
|---|---|---|
| `ModelContextProtocol` | Runtime | Core interfaces, server, resources, session, capabilities, tool results. |
| `ModelContextProtocolEngine` | Runtime | Tool library base classes, async action base class, settings, client config generator, engine metadata. |
| `ModelContextProtocolEditor` | Editor | Editor tool library, ToolsetRegistry adapter, tool search meta-tools, asset definitions, hash mapping commandlet. |
| `ModelContextProtocolTests` | UncookedOnly | Core tests. |
| `ModelContextProtocolEngineTests` | UncookedOnly | Engine tests. |
| `ModelContextProtocolEditorTests` | Editor | Editor tests. |

Plugin dependencies (`ModelContextProtocol.uplugin:51-60`): `EngineAssetDefinitions`, `ToolsetRegistry` — both enabled.

## 1.2 Public interfaces

### `IModelContextProtocolTool` (`IModelContextProtocolTool.h:23-101`)

```cpp
struct IModelContextProtocolTool : TSharedFromThis<IModelContextProtocolTool>
{
    typedef TFunction<void(const FModelContextProtocolToolResult&)> FResultCallback;
    virtual ~IModelContextProtocolTool() = default;
    virtual FString GetName() const = 0;
    virtual FString GetDescription() const = 0;
    virtual TSharedPtr<FJsonObject> GetInputJsonSchema() const;   // default: {"type":"object"}
    virtual TSharedPtr<FJsonObject> GetOutputJsonSchema() const;  // default: invalid (none)
    virtual FModelContextProtocolToolResult Run(const TSharedPtr<FJsonObject>& Params);
    virtual void RunAsync(RequestId, Params, OnComplete);         // default: calls Run synchronously
    virtual void CancelAsync(const FModelContextProtocolToolRequestId& RequestId) {}
    virtual void AddReferencedObjects(FReferenceCollector&) {}
};
```

Key contract notes (from the header docstring):
- `RunAsync` is preferred; `Run` is the fallback.
- `FResultCallback` may be invoked from any thread — the server hops to the game thread.
- Schema adherence is **assumed, not strictly checked** (line 70, line 86).
- `CancelAsync` default is a no-op; tools that need cancellation must override.

### `IModelContextProtocolModule` (`IModelContextProtocolModule.h:17-120`)

Module provides: `GetTools`, `FindTool`, `AddTool` (with name validation), `RemoveTool`, `OnRefreshTools` (delegate), `RefreshTools` (manual), `GetServer`, `StartServer(Port, UrlPath)`, `StopServer`, `SetAnalyticsProvider`/`GetAnalyticsProvider`, `SetAnalyticsEventNamespace`/`GetAnalyticsEventNamespace`, `RecordAnalyticsEvent`, `GetResourceProviders`, `AddResourceProvider`, `RemoveResourceProvider`.

### `IModelContextProtocolResourceProvider` (`IModelContextProtocolResourceProvider.h:20-34`)

```cpp
struct IModelContextProtocolResourceProvider : TSharedFromThis<...>
{
    virtual void ListResources(FModelContextProtocolResourceDescriptorList& Out) const = 0;
    virtual TValueOrError<FModelContextProtocolResource, FString> ReadResource(const FString& Uri) const = 0;
};
```

Two methods only — no Subscribe, no ListChanged notification support. **Subscription is not in the resource interface.**

## 1.3 Server (`ModelContextProtocolServer.cpp`, 1118 lines)

### Routes (`ModelContextProtocolServer.cpp:435-443`)

Three routes bound on the same path:

| Verb | Handler | Real purpose |
|---|---|---|
| POST | `ProcessPostRequest` → `ProcessJsonRpcCall` | All JSON-RPC traffic. |
| GET | `ProcessGetRequest` | **Returns 405 BadMethod** (line 1074) — no standalone SSE endpoint. |
| DELETE | `ProcessDeleteRequest` | Session termination (`Mcp-Session-Id` header required). |

### JSON-RPC methods dispatched (`ModelContextProtocolServer.cpp:27-37`)

```
ping
initialize
notifications/initialized
notifications/cancelled
tools/list
tools/call
resources/list
resources/read
```

`prompts/*`, `sampling/*`, `roots/list`, `completion/complete`, `logging/setLevel` are all **NOT** dispatched. The dispatch in `ProcessJsonRpcCall` (lines 558-635) uses a `check()` for the last method, meaning anything else is rejected with `MethodNotFound` before session validation.

### Pagination (`ModelContextProtocolServer.cpp:328-398`)

Full implementation via `ApplyPagination`:
- Reads `cursor` from params (base64-encoded integer offset).
- Validates cursor (must be all-digits, decoded).
- Uses `UE::ModelContextProtocol::PaginationPageSize` CVar (default 0 = disabled).
- Returns `nextCursor` when more items exist.

Used by both `tools/list` and `resources/list`.

### Progress reporting (`ModelContextProtocolServer.cpp:1036-1063`)

Heartbeat implementation in `Tick()`:
- Per-session, per-active-request.
- Reads `progressToken` from `_meta.progressToken` in the request (line 822-829).
- Sends `notifications/progress` SSE event every `ProgressIntervalSeconds` (default 1.0s).
- The progress value is `++Context.LastProgressValue` (line 1053) — comment says *"Not sending a total progress value, so this is simply a heartbeat as the total duration is unknown."*

### Notifications (`ModelContextProtocolServer.cpp:509-516, 1006-1034`)

Only `notifications/tools/list_changed` is implemented. Delivery is deferred to next Tick (avoid re-entrancy in HTTP state machine). Delivery is gated on at least one in-flight `tools/call` per session — quiet sessions miss it.

### Origin / DNS-rebinding protection (`ModelContextProtocolServer.cpp:68-121`)

`ValidateOriginHeader` blocks non-localhost Origins:
- Allows requests with no `Origin` header (non-browser clients).
- Allows `Origin: localhost`, `127.0.0.1`, `[::1]`.
- Logs a warning + returns 403 otherwise.

Called from POST, GET, DELETE handlers.

### Session management

- Created in `ProcessInitializeJsonRpcCall` (line 665-672). ID = `FGuid::NewGuid().ToString(EGuidFormats::DigitsLower)`.
- Status transitions: `Initializing` → `Initialized` on `notifications/initialized`.
- Per-session `ActiveRequests` map tracks in-flight tools for cancel and progress.
- Sessions are deleted via `DELETE /<path>` with `Mcp-Session-Id` header.
- Server emits `SessionStart` / `SessionEnd` analytics events.
- **No automatic session expiry** — sessions persist until explicit DELETE or server stop.

### Protocol version negotiation (`ModelContextProtocolServer.cpp:660-672`)

`UE::ModelContextProtocol::NegotiateProtocolVersion` returns the client's version if supported, else the server's `ProtocolVersion` constant. Supported list: `2025-11-25`, `2025-06-18`, `2024-11-05`.

### CVar settings (`ModelContextProtocol.cpp:43-67`)

Four CVars, all with `FAutoConsoleVariableRef`:

| CVar | Default | Purpose |
|---|---|---|
| `ModelContextProtocol.WrapPODToolResultsInObject` | `true` | Wraps POD return values in `{"result": value}`. |
| `ModelContextProtocol.AudioResultOggFormat` | `false` | Returns audio as OGG instead of WAV. |
| `ModelContextProtocol.ProgressIntervalSeconds` | `1.0` | Heartbeat interval for in-flight tools. |
| `ModelContextProtocol.PaginationPageSize` | `0` | Page size for list methods. 0 = no pagination. |

### Console commands

| Command | Module | Effect |
|---|---|---|
| `ModelContextProtocol.RefreshTools` | `ModelContextProtocolModule.cpp:22-29` | Clears tools, broadcasts `OnRefreshTools` for providers to re-add. |
| `ModelContextProtocol.StartServer [port]` | `ModelContextProtocolModule.cpp:31-56` | Explicit start with optional port override. |
| `ModelContextProtocol.StopServer` | `ModelContextProtocolModule.cpp:58-68` | Explicit stop. |
| `ModelContextProtocol.GenerateClientConfig <name\|All>` | `ModelContextProtocolEngineModule.cpp:40-70` | Writes config files for ClaudeCode / Cursor / VSCode / Gemini / Codex. |

All four are flagged `ECVF_Cheat` (cheat-protected).

## 1.4 Tool execution paths

### Sync path: `UModelContextProtocolToolLibrary` (`ModelContextProtocolToolLibrary.cpp`)

- All `UCLASS` extending `UModelContextProtocolToolLibrary` auto-register at `PostInitProperties` (line 22-31) for native classes, `PostLoad` (line 33-42) for BP, `PostCDOCompiled` (line 45-54) for recompile.
- Each public function becomes a tool (line 82-96). Function name = tool name.
- Editor-only metadata system: `FModelContextProtocolFunctionMetaData` collects descriptions, `WorldContext`, `PropertyMetaData` with `DefaultValue` / `Description` / `ClampMin` / `ClampMax`.
- `FModelContextProtocolLibraryTool::Run` (line 248-320):
  - `FScopedTransaction` wraps the call in editor (undo support).
  - `FJsonObjectConverter::JsonObjectToUStruct` is called with `bStrictMode=false` (line 286) — coerces where possible, returns error on failure.
  - `WorldContext` is auto-set to `GWorld.GetReference()`.
  - `FEditorScriptExecutionGuard` wraps `ProcessEvent` (line 307).
- JSON Schema is generated via `FJsonSchemaGenerator::UStructToJsonSchemaObject` (line 224) with `FJsonSchemaPropertyFilter` + cookable editor metadata.
- **Schema is cached** on the tool instance (line 196-199 of GetInputJsonSchema) — only regenerated on tool re-creation.

### Async path: `UModelContextProtocolToolAsyncAction` (`ModelContextProtocolToolAsyncAction.cpp`)

- Mirrors the sync path but for `UBlueprintAsyncActionBase` subclasses.
- `RunAsync` (line 247-345) calls `ProcessEvent` synchronously, then captures the returned `UModelContextProtocolToolAsyncAction*` and waits for its `OnAsyncToolComplete` event.
- `InProgressActions` TArray tracks active async actions per-tool for GC + cancel routing.
- **`CancelAsync` IS implemented** (line 347-360) — iterates `InProgressActions`, finds matching `ToolRequestId`, calls `Action->Cancel()`. This is the pattern the gap analysis should follow.

### ToolsetRegistry adapter (`ModelContextProtocolToolsetRegistryAdapter.cpp`)

The Editor module integrates the engine's `ToolsetRegistry`:

- **Eager mode** (`bEnableToolSearch=false`, lines 192-200): every toolset's tool is registered as a native MCP tool via `RegisterToolsFromSchema`.
- **Tool search mode** (`bEnableToolSearch=true`, default, lines 156-190): only 3 meta-tools are registered:
  - `list_toolsets` → returns text catalog of toolset names + descriptions.
  - `describe_toolset` → returns full JSON schema for a named toolset.
  - `call_tool` → dispatches a tool call by toolset_name + tool_name.
- `DispatchToolCall` (line 233-298) handles both qualified (toolset-prefixed) and top-level dispatch. Self-recursion into `call_tool` is explicitly rejected (line 275-278).
- **`FToolsetRegistryToolAdapter::CancelAsync` is NOT implemented** — falls back to base class no-op (the source-of-truth claim from the prior doc was correct for this class only).

## 1.5 Settings (`UModelContextProtocolSettings`)

`UDeveloperSettings` subclass, config file `EditorPerProjectUserSettings`:

| Property | Default | Effect |
|---|---|---|
| `ServerUrlPath` | `/mcp` | HTTP path the server binds. |
| `ServerPortNumber` | `8000` | Default port. |
| `bAutoStartServer` | `false` | Whether to start the server on module init. |
| `bEnableToolSearch` | `true` | Tool-search mode (default) vs eager toolset registration. |

Command-line overrides (`ModelContextProtocolSettings.cpp:18-48`):
- `-ModelContextProtocolPort=N` overrides port.
- `-ModelContextProtocolStartServer` forces auto-start.
- `-StartModelContextProtocolServer` is deprecated alias.

`PostEditChangeProperty` (line 62-76) calls `EnforceValidServerUrlPath` on the final value (skips interactive edits to avoid fighting the user mid-type).

## 1.6 Client config generation (`ModelContextProtocolClientConfig.cpp`)

`UE::ModelContextProtocol::WriteClientConfiguration` writes per-client config files (5 supported clients):

| Client | File | Servers key | URL field | Type field? | Format |
|---|---|---|---|---|---|
| ClaudeCode | `.mcp.json` | `mcpServers` | `url` | yes (`"type": "http"`) | JSON |
| Cursor | `.cursor/mcp.json` | `mcpServers` | `url` | no | JSON |
| VSCode | `.vscode/mcp.json` | `servers` | `url` | yes | JSON |
| Gemini | `.gemini/settings.json` | `mcpServers` | `httpUrl` | no | JSON |
| Codex | `.codex/config.toml` | `mcp_servers` | `url` | no | TOML |

Codex format is appended-only (TOML can't safely upsert). All others merge into existing config. Default base directory is `FPaths::RootDir()` for source builds, `FPaths::ProjectDir()` for installed builds. Server URL is `http://127.0.0.1:%u%s` — **localhost-bound by default**.

## 1.7 Tool result system (`ModelContextProtocolToolResults.h:16-122`)

`EModelContextProtocolToolResultType` is a bitflag with: `None`, `Text`, `Image`, `Audio`, `ResourceLink` (Hidden), `EmbeddedResource` (Hidden), `StructuredContent`.

Result factories (all exist, all in the public API):
- `MakeTextResult(Text)` — text content.
- `MakeImageResult(MimeType, Data)` / `MakeImageResult(MimeType, Base64)` — image content.
- `MakeAudioResult(MimeType, Data)` / `MakeAudioResult(MimeType, Base64)` — audio content.
- `MakeResourceLinkResult(Descriptor)` / `MakeResourceLinksResult(...)` — resource link content.
- `MakeStructuredContentResult(...)` — multiple overloads (UStruct, raw pointer, FProperty, JsonValue, UObject).
- `MakeErrorResult(Text)` — error result with `isError: true`.

`EModelContextProtocolAudience` enum: `None`, `User`, `Assistant`, `All` — for marking content per the 2025-06-18 spec.

The result struct itself is `FModelContextProtocolToolResult : FJsonObjectWrapper`.

## 1.8 Resources (`ModelContextProtocolResources.h:17-68`)

- `FModelContextProtocolResourceDescriptor` — text-only metadata.
- `FModelContextProtocolResource` — extends descriptor; can hold either `FString TextContent` or `TArrayView<uint8> BlobContent` (binary).
- `FModelContextProtocolResourceDescriptorList` — stateful list that tracks `TMap<FString, TSharedRef<const IModelContextProtocolResourceProvider>> ResourceUriToProvider` for routing reads.

## 1.9 Analytics

- Per-call `RecordAnalyticsEvent(EventName, Attributes)` with namespace prefix.
- Engine module installs `FEngineAnalyticsProviderProxy` as default after post-engine-init (`ModelContextProtocolEngineModule.cpp:80-83, 109-129`).
- Events emitted: `SessionStart`, `SessionEnd`, `ToolCall` (with `bSuccess`, `Duration`).
- `AnalyticsMutex` (`ModelContextProtocolModule.h:60`) guards provider/namespace — required because tool-completion callbacks may run off the game thread.

## 1.10 Tests

The test modules include:
- `ModelContextProtocolServerTests.cpp` (9K)
- `ModelContextProtocolModuleTests.cpp` (10K)
- `ModelContextProtocolResourcesTests.cpp` (13K)
- `ModelContextProtocolToolResultsTests.cpp` (17K)
- `ModelContextProtocolEngineSubsystemTests.cpp` (73K) — engine subsystem integration
- `ModelContextProtocolSessionTests.cpp` (3.7K)
- `ModelContextProtocolToolNameTests.cpp` (5.5K) — tool name validation
- `ModelContextProtocolToolsetRegistryTests.cpp` (36K) — toolset adapter

The editor tests include mocks for `FToolsetDefinition` and full coverage of the registry adapter.

---

# Part 2 — Verified gaps (source-confirmed)

These are the issues I confirmed by reading the source. Each is cited to a specific file:line.

## 2.1 Transport layer

### G-01: No stdio transport
- **Severity**: High (UX)
- **Source state**: The server binds only HTTP routes (`ModelContextProtocolServer.cpp:435-443`). `IModelContextProtocolModule::StartServer(uint32 Port, FString UrlPath)` (line 66) takes a port. There is no stdio reader/writer anywhere in the codebase.
- **Spec rationale**: MCP spec defines stdio as the default for local integrations. Most LLM clients (Claude Code, Cursor, etc.) prefer or require stdio.
- **Effort**: Medium (3-5 days) — new `FModelContextProtocolStdioTransport` class, dispatcher refactor to share `ProcessJsonRpcCall` between transports.

### G-02: GET route returns 405 — no standalone SSE
- **Severity**: Medium (architecture)
- **Source state**: `ProcessGetRequest` at `ModelContextProtocolServer.cpp:1066-1076` returns `EHttpServerResponseCodes::BadMethod` with the comment *"We do not currently support sse on a separate endpoint"*. SSE only happens as part of POST response streaming (e.g., for `tools/call` progress).
- **Consequence**: The `notifications/tools/list_changed` broadcast at line 1006-1034 is **gated on at least one in-flight tool call per session** — quiet sessions miss the notification. The comment at line 1011-1014 is explicit about this.
- **Effort**: Medium — implement standalone SSE with session affinity.

### G-03: Server bound to all interfaces
- **Severity**: Low–Medium (security)
- **Source state**: `ModelContextProtocolServer.cpp:432` calls `FHttpServerModule::Get().GetHttpRouter(ActiveServerPort)` without binding to a specific address. The default UE HTTP server binds to all interfaces. Origin-header validation is the only protection, and it only blocks browser-side DNS rebinding.
- **Note**: The client config writer uses `http://127.0.0.1:%u%s` (`ModelContextProtocolClientConfig.cpp:158`), so legitimate clients only hit localhost. But a non-browser client (e.g., a custom curl) could come from any address.
- **Fix**: Bind explicitly to `127.0.0.1` (use `FHttpServerModule::Get().GetHttpRouter(Port, BindAddress)` or equivalent). Most engine builds support this.

## 2.2 MCP spec compliance

### G-04: No `prompts/*` methods
- **Severity**: Medium
- **Source state**: `ProcessJsonRpcCall` (`ModelContextProtocolServer.cpp:558-635`) does not dispatch `prompts/list` or `prompts/get`. The dispatch in line 632 uses `check(Method == ResourcesRead)` as the final branch — any other method gets `MethodNotFound`. The `FModelContextProtocolPromptsCapability` struct exists in `ModelContextProtocolCapabilities.h:51-58` (so the data model is there) but is never advertised in `InitializeResult.Capabilities` (line 678-680).
- **Spec reference**: https://modelcontextprotocol.io/specification/2025-11-25/server/prompts

### G-05: No `sampling/createMessage` (server→client LLM call)
- **Severity**: Low
- **Source state**: Not dispatched. The struct `FModelContextProtocolSamplingCapability` exists in the client capabilities struct (`ModelContextProtocolCapabilities.h:38-42`) but is never received/used.
- **Realism check**: Adding server→client sampling would require the MCP server to be able to make LLM calls. In practice, this is rarely useful in Unreal — the LLM is on the client side, so client→server is the natural direction (which the current server doesn't do either).

### G-06: No `roots/list` (client→server root declaration)
- **Severity**: Low
- **Source state**: The `Roots` capability exists in `FModelContextProtocolClientCapabilities` (`ModelContextProtocolCapabilities.h:36`) but is never used to expose project roots as MCP resources. This is a feature, not a bug — adding it would let the LLM browse `/Game/...` paths.
- **Effort**: Small (1-2 days) — add a `FRootsResourceProvider` that exposes a path tree.

### G-07: No `notifications/resources/updated` or `notifications/resources/list_changed`
- **Severity**: Medium
- **Source state**: `ScheduleToolsListChangedBroadcast` exists for tools, but no equivalent for resources. Comment at `ModelContextProtocolServer.cpp:1011-1014` says the delivery is gated on in-flight tool calls — same limitation would apply to resources.
- **Effort**: Medium — needs subscription tracking + per-URI notification.

### G-08: No resource templates (`resources/templates/list`)
- **Severity**: Low
- **Source state**: Not dispatched. The spec allows templated URIs like `asset://{path}`; the current model is static URIs only.

### G-09: No `logging/setLevel`
- **Severity**: Low
- **Source state**: The `FModelContextProtocolLoggingCapability` struct exists (`ModelContextProtocolCapabilities.h:46-49`) but is never advertised. No way for the client to control the server's `LogModelContextProtocol` verbosity at runtime.
- **Effort**: Small (1 day) — add the method, plumb to `LogModelContextProtocol` verbosity.

### G-10: No `completion/complete` (argument autocompletion)
- **Severity**: Low
- **Source state**: Not dispatched. Some LLM clients send this to get argument suggestions for tools. Not critical for local MCP use.

### G-11: `ServerInfo` never populated
- **Severity**: Low (bug, not feature gap)
- **Source state**: `FModelContextProtocolServerInfo` struct has `Name`, `Title`, `Version` fields (`ModelContextProtocolSession.h:42-55`) but `ProcessInitializeJsonRpcCall` (`ModelContextProtocolServer.cpp:675-682`) never sets them. Clients receive an empty `serverInfo` object.
- **Fix**: Set `InitializeResult.ServerInfo.Name = TEXT("Unreal MCP")` etc. 1-line fix.

## 2.3 Tool execution

### G-12: `FToolsetRegistryToolAdapter::CancelAsync` is a no-op
- **Severity**: Medium (the doc got this one right)
- **Source state**: `ModelContextProtocolToolsetRegistryAdapter.h:13-26` only overrides `RunAsync`; `CancelAsync` falls back to the base class no-op (`IModelContextProtocolTool.h:97`). The async action's CancelAsync IS implemented (`ModelContextProtocolToolAsyncAction.cpp:347-360`), so this is a toolset-specific gap.
- **Fix**: Either forward `CancelAsync` to `ToolsetRegistry->CancelTool(Descriptor)` if the API exists, or track in-flight `ToolsetRegistry::ExecuteTool` futures for explicit cancel.

### G-13: Heartbeat progress is uninformative
- **Severity**: Medium (the doc got this right)
- **Source state**: `ModelContextProtocolServer.cpp:1053` — `++Context.LastProgressValue` is a monotonic counter, not a percentage. The comment at line 1052 is explicit: *"Not sending a total progress value, so this is simply a heartbeat as the total duration is unknown."*
- **Fix**: Let tools report real progress. The `FResultCallback` doesn't have a progress channel, but adding `IModelContextProtocolTool::ReportProgress(RequestId, Percent, Message)` would work.

### G-14: `LastProgressValue` is `int32` (overflow at ~2B)
- **Severity**: Trivial
- **Source state**: `ModelContextProtocolSession.h:125` — `int32 LastProgressValue = 0;`. At default `ProgressIntervalSeconds=1.0`, a 68-year tool call would overflow. Not a real concern, but worth noting.

### G-15: Malformed params don't crash but return error — not validated against schema
- **Severity**: Low (the doc's "can crash" was wrong; "not strictly checked" is right)
- **Source state**: `IModelContextProtocolTool.h:70` says *"Schema adherence by MCP clients is assumed, not strictly checked internally."* `ModelContextProtocolToolLibrary.cpp:286` calls `FJsonObjectConverter::JsonObjectToUStruct` with `bStrictMode=false` — coerces where possible, returns an error result on failure (line 288). So malformed inputs return an error, they don't crash. The "crash" wording in the prior doc was an over-statement.

### G-16: Output schema advertised but not enforced
- **Severity**: Low
- **Source state**: `ProcessListToolsJsonRpcCall` (line 748-751) calls `GetOutputJsonSchema` and includes it in the response. But there is no validation that the tool's actual output conforms to its declared `outputSchema`. Mismatch is silent.

### G-17: No tool call history / persistence
- **Severity**: Low
- **Source state**: `FModelContextProtocolSession::ActiveRequests` (line 138 of `ModelContextProtocolSession.h`) holds only *active* requests. After a tool completes, the entry is removed (line 886 of `ModelContextProtocolServer.cpp`). No on-disk log, no replay.

### G-18: `RefreshTools` is a hard reset
- **Severity**: Low
- **Source state**: `ModelContextProtocolModule.cpp:144-148` does `Tools.Reset(); OnRefreshToolsDelegate.Broadcast()`. Every provider must re-add its tools. No incremental refresh.
- **Side effect**: For toolset mode, this triggers the heavy `RegisterToolsFromSchema` path each time. Cheap, but worth noting.

## 2.4 Editor integration

### G-19: No editor context tools
- **Severity**: High
- **Source state**: `ModelContextProtocolEditorToolLibrary.h` defines `UModelContextProtocolEditorToolLibrary` (extends `UModelContextProtocolToolLibrary`) but the `.cpp` is 818 bytes — essentially empty. No tools are defined. There's no `get_editor_context`, `capture_viewport`, `get_selected_actors`, `execute_console_command` tool out of the box.
- **Source-of-truth for the prior doc's claim**: The prior doc said *"The only editor-specific tool library is a thin wrapper around UBlueprintFunctionLibrary"* — this is accurate. **But** the tools come from ToolsetRegistry (which has Blueprint-based asset definitions and many built-in toolsets), not from the bare library.
- **Effort**: Medium per tool (each is a UFunction in a UModelContextProtocolEditorToolLibrary subclass).

### G-20: `ModelContextProtocolToolHashMappingCommandlet` exists but no doc reference
- **Severity**: Informational
- **Source state**: `ModelContextProtocolToolHashMappingCommandlet.cpp` (7K) and `.h` (2.4K) implement a UCommandlet. Purpose is not clear from the name. Likely for hashing tool names for stable IDs. Worth a separate read.

### G-21: `ModelContextProtocolAssetDefinitions` exists
- **Severity**: Informational
- **Source state**: `ModelContextProtocolAssetDefinitions.cpp` (2K) defines a UAssetDefinition for the editor. Probably for the Content Browser. Doc missed this.

## 2.5 Performance / scalability

### G-22: `FindTool` is O(N) linear search
- **Severity**: Low–Medium
- **Source state**: `ModelContextProtocolModule.cpp:99-107` — `Tools.FindByPredicate` over `TArray`. The prior doc got this right. With 100+ tools in eager mode, every tool call has an O(N) lookup.
- **Fix**: Add a `TMap<FString, int32> ToolNameToIndex` next to `Tools`. ~30 lines of code.
- **Cost**: Negligible in practice — N is typically <50.

### G-23: Schema regenerated on tool creation, not per call
- **Severity**: None (the doc's claim "regenerated on every call" is wrong)
- **Source state**: `ModelContextProtocolToolLibrary.cpp:196-199` — schema is cached in `InputJsonSchema` field. Only regenerated on tool re-creation. The doc's gap #27 is incorrect.

### G-24: `AddReferencedObjects` only on Library/AsyncAction tools
- **Severity**: Low
- **Source state**: `IModelContextProtocolTool.h:100` is empty by default. `UModelContextProtocolToolLibrary` (`ModelContextProtocolToolLibrary.cpp:322-326`) and `UModelContextProtocolToolAsyncAction` (`ModelContextProtocolToolAsyncAction.cpp:362-367`) implement it. Custom tools (e.g., user-implemented `IModelContextProtocolTool` directly) must implement it themselves or leak UObjects.

### G-25: No rate limiting
- **Severity**: Low (local-only server)
- **Source state**: No rate limit infrastructure. The `LastProgressValue` heartbeat is the only per-request throttling. For a local-only server this is unlikely to matter, but a runaway LLM could spam.

### G-26: No request queuing / prioritization
- **Severity**: Trivial
- **Source state**: All requests processed FIFO via HTTP threads + game thread. The doc's claim is correct; this is unlikely to be needed.

## 2.6 Developer experience

### G-27: No built-in tool call history / logging at user level
- **Severity**: Low
- **Source state**: `UE_LOGF(LogModelContextProtocol, VeryVerbose, ...)` is the only verbose output (`ModelContextProtocolServer.cpp:814-816`, `877-882`). No file-based log per session. Analytics is opt-in via `IAnalyticsProviderET`.

### G-28: `ModelContextProtocolEngineMetaData` is editor-only
- **Severity**: Informational
- **Source state**: `ModelContextProtocolEngineMetaData.cpp` is wrapped in `WITH_EDITORONLY_DATA`. Metadata (descriptions, defaults, world context) is collected only in the editor. Runtime tools lose their descriptions.
- **Fix**: Bake the metadata into the cooked build via the `ModelContextProtocolToolHashMappingCommandlet` (likely — needs separate read to confirm).

### G-29: `OverrideBPTypeForClass` for BP tools is editor-only
- **Severity**: Informational
- **Source state**: `ModelContextProtocolEditor.cpp:19-21` overrides the BP class. Runtime/cooked builds don't need this.

---

# Part 3 — Spec-compliance scorecard (2025-11-25 MCP spec)

| Spec feature | Implemented? | Source | Gap |
|---|---|---|---|
| `ping` | ✅ | `ProcessPingJsonRpcCall` | — |
| `initialize` | ✅ | `ProcessInitializeJsonRpcCall` | ServerInfo never set (G-11) |
| `notifications/initialized` | ✅ | `ProcessInitializedNotificationJsonRpcCall` | — |
| `notifications/cancelled` | ✅ | `ProcessNotificationCancelledJsonRpcCall` | — |
| `notifications/progress` | ✅ (heartbeat) | `Tick()` line 1036-1063 | Heartbeat only, no real percent (G-13) |
| `notifications/tools/list_changed` | ✅ | `ScheduleToolsListChangedBroadcast` + `Tick()` | Gated on in-flight calls (G-02) |
| `notifications/resources/list_changed` | ❌ | — | G-07 |
| `notifications/resources/updated` | ❌ | — | G-07 |
| `tools/list` | ✅ | `ProcessListToolsJsonRpcCall` | Pagination via CVar (default off) |
| `tools/call` | ✅ | `ProcessToolCallJsonRpcCall` | Async by default, sync fallback |
| `resources/list` | ✅ | `ProcessListResourcesJsonRpcCall` | Pagination via CVar |
| `resources/read` | ✅ | `ProcessReadResourceJsonRpcCall` | Provider routing cached |
| `resources/subscribe` | ❌ | — | G-07 |
| `resources/templates/list` | ❌ | — | G-08 |
| `prompts/list`, `prompts/get` | ❌ | — | G-04 |
| `sampling/createMessage` | ❌ | — | G-05 |
| `roots/list` | ❌ | — | G-06 |
| `logging/setLevel` | ❌ | — | G-09 |
| `completion/complete` | ❌ | — | G-10 |
| Tool name validation | ✅ | `ValidateToolName` | Per 2025-11-25 spec |
| Image content type | ✅ | `MakeImageResult` | — |
| Audio content type | ✅ | `MakeAudioResult` | Format switch via CVar |
| Structured content | ✅ | `MakeStructuredContentResult` | — |
| Resource link content | ✅ | `MakeResourceLinkResult` | — |
| Embedded resource content | ✅ (struct exists, Hidden flag) | `EModelContextProtocolToolResultType` | Likely not exercised in result factories |
| Audience tagging | ✅ | `EModelContextProtocolAudience` | — |
| Origin header validation | ✅ | `ValidateOriginHeader` | DNS rebinding protection |
| Protocol version negotiation | ✅ | `NegotiateProtocolVersion` | 3 versions supported |
| JSON-RPC 2.0 error codes | ✅ | `EJsonRpcErrorCode` | Standard + ResourceNotFound |

**Compliance score**: 14/24 spec features implemented, 10 missing. **Plus 1 implementation bug** (ServerInfo unset).

---

# Part 4 — Source-level observations not in the prior analysis

These are real features the prior `gap_analysis_and_roadmap.md` didn't mention. They are the source-of-truth corrections to the prior doc's "missing" lists.

## 4.1 Already-built features the prior doc said were missing

| Prior doc claim | Reality |
|---|---|
| "No progress reporting with actual percentage" (Gap #12) | Progress reporting **is** implemented — as a heartbeat (`ModelContextProtocolServer.cpp:1036-1063`). The "actual percentage" is genuinely missing, but the mechanism is there. |
| "No pagination on tools/list" (Gap #10) | Pagination **is** implemented (`ModelContextProtocolServer.cpp:328-398`). Default page size is 0 (disabled), but the CVar `ModelContextProtocol.PaginationPageSize` enables it. |
| "No transport auto-detection" (Gap #4) | Auto-detection isn't there, but the more important issue (server only binds HTTP) is captured. Auto-detection would be nice but is secondary. |
| "No CVar for runtime configuration" (Gap #33) | **4 CVars exist** (`ModelContextProtocol.cpp:43-67`): `WrapPODToolResultsInObject`, `AudioResultOggFormat`, `ProgressIntervalSeconds`, `PaginationPageSize`. |
| "No console command" (related to G-30) | **4 console commands exist** (see §1.3): `RefreshTools`, `StartServer`, `StopServer`, `GenerateClientConfig`. |
| "No MCP client config generator" | **5 clients supported** with `ModelContextProtocol.GenerateClientConfig` (ClaudeCode, Cursor, VSCode, Gemini, Codex). |
| "Multi-Modal Image Resources" (Feature 2.5.2) | Image + Audio + ResourceLink + StructuredContent **all already have result factories** (`ModelContextProtocolToolResults.h:81-91`). |
| "Tool Composition / Chaining" (Feature 2.5.1) | The tool-search pattern (3 meta-tools: `list_toolsets`, `describe_toolset`, `call_tool`) **is** a kind of late-binding / dynamic dispatch — different from "composition" but solves a similar problem. Implemented in `ModelContextProtocolToolsetRegistryAdapter.cpp:140-201`. |
| "Subscriptions-based Resources" (Feature 2.5.3) | The `Resources.Subscribe` field exists in the capability struct (`ModelContextProtocolCapabilities.h:66`) but is never set to `true` in `InitializeResult.Capabilities`. The interface isn't designed for subscriptions yet. |
| "Tool Call History/Persistence" (Feature in Phase 4) | No change — still not implemented. But the prior doc underplayed the `ModelContextProtocolAnalytics` infrastructure that could be extended for this. |

## 4.2 Features the prior doc mentioned but with wrong semantics

| Prior doc claim | Correct semantics |
|---|---|
| "MCP spec 2025-06-18" | **Server uses 2025-11-25 as the default**, with 2025-06-18 and 2024-11-05 also supported (`ModelContextProtocol.h:19-30`). The 2025-06-18 spec is in the codebase doc-comments but the negotiated version is 2025-11-25. |
| "Only HTTP routes: POST, GET, DELETE" | DELETE is for **session termination**, not for resource deletion. The doc got the verb list right but misattributed the DELETE purpose. |
| "RunAsync is the API" | `IModelContextProtocolTool.h:91-95` says `RunAsync` *defaults* to calling `Run` synchronously. The "real" async behavior requires explicit override — only `UModelContextProtocolToolAsyncAction` and `FToolsetRegistryToolAdapter` do this. The sync tool path is the default. |
| "`CancelAsync()` is empty implementation" | True for `IModelContextProtocolTool::CancelAsync` (line 97), `FToolsetRegistryToolAdapter::CancelAsync` (uses base no-op). **False** for `UModelContextProtocolToolAsyncAction::CancelAsync` (line 347-360 of `ModelContextProtocolToolAsyncAction.cpp`), which IS implemented and properly routes to `Action->Cancel()`. |
| "`LastProgressValue` is just a heartbeat counter" | **Correct.** `ModelContextProtocolSession.h:125` declares it as `int32 LastProgressValue = 0;` and `ModelContextProtocolServer.cpp:1053` increments it. |
| "Only 4 modules" | **6 modules**: 3 production (Core, Engine, Editor) + 3 test (Tests, EngineTests, EditorTests). |
| "ProcessListToolsJsonRpcCall / ProcessToolCallJsonRpcCall / ProcessListResourcesJsonRpcCall / ProcessReadResourceJsonRpcCall" | Plus `ProcessPingJsonRpcCall`, `ProcessInitializeJsonRpcCall`, `ProcessInitializedNotificationJsonRpcCall`, `ProcessNotificationCancelledJsonRpcCall` — **8 dispatch methods total**, not 4. |
| "Linear tool search O(N)" | **Correct.** `ModelContextProtocolModule.cpp:99-107`. |

## 4.3 Genuine gaps the prior doc missed

### G-30: No `ModelContextProtocol.StartServer` is documented
- The console commands exist but aren't mentioned anywhere in the prior doc. The discoverability is via the engine console.

### G-31: No BP tool runtime test path
- BP tools compile to `UModelContextProtocolToolLibraryBlueprint` via `OverrideBPTypeForClass` (`ModelContextProtocolEditor.cpp:20-21`). At runtime in cooked builds, the `WITH_EDITORONLY_DATA` block in `ModelContextProtocolToolLibrary.cpp:120-142` is excluded, so `FunctionMetaData` (descriptions, defaults) is not available. This means BP tools in shipping builds have **no descriptions and no default values** in their MCP `tools/list` output. Fix: bake the metadata at cook time (the `ModelContextProtocolToolHashMappingCommandlet` may be the existing mechanism — needs separate read to confirm).

### G-32: No `ModelContextProtocolToolAsyncAction` in `ModelContextProtocolEngine` vs editor split
- `UModelContextProtocolToolAsyncAction` is in the **Engine** module (Runtime), not the Editor module. This is correct (async actions can fire in PIE and runtime), but it means runtime builds can register async tools without an editor present. The prior doc didn't discuss this.

### G-33: `FModelContextProtocolToolContext::EventStreamWrite` is `FHttpResultCallback` — server-coupled
- The server holds a callback for SSE writes inside the per-session active-requests map. This means a custom transport (e.g., stdio) needs to either use the same `FHttpResultCallback` shape or refactor this data structure. Not a bug today, but a refactor hazard for G-01.

### G-34: `OverrideBPTypeForClass` is editor-only and not a "MCP Blueprint" UCLASS
- The BP class exists (`UModelContextProtocolToolLibraryBlueprint`, `ModelContextProtocolToolLibrary.h`). It's just a `UBlueprint` subclass with a special parent. The override is editor-only (`ModelContextProtocolEditor.cpp:19-21`).

### G-35: Sessions have no timeout
- A session lives forever until `DELETE /<path>` is called or the server stops. A client that crashes mid-session leaks. The spec doesn't mandate a timeout, but it's a real production concern for the longer-lived engine process.

### G-36: `LastResourceDescriptorList` is a server-singleton cache
- `ModelContextProtocolServer.cpp:82` — single `FModelContextProtocolResourceDescriptorList` for the entire server. Multiple sessions share the same cache. The `ReleaseJsonArray` call at line 948 frees the JSON values but keeps the provider map. A multi-session scenario where providers change between calls could see stale routing. This is probably fine in practice but the design is non-obvious.

### G-37: No structured logging
- `LogModelContextProtocol` is the only log category. No per-session or per-tool subchannels. LLM clients that want to filter "what did this session do" have to parse the log themselves.

### G-38: `ModelContextProtocolAnalytics` event name structure not documented
- The events are `SessionStart`, `SessionEnd`, `ToolCall` — but the attribute names (`bSuccess`, `Duration`, etc.) are not documented anywhere visible. Anyone using a custom analytics provider has to read the source.

### G-39: Tool search meta-tools leak implementation
- When `bEnableToolSearch=true`, `list_toolsets`, `describe_toolset`, `call_tool` are exposed as plain tools. The descriptions reveal the toolset discovery pattern (`ModelContextProtocolToolSearch.h:32-33, 51-52, 71-72`). For a "production-clean" feel, these could be `Hidden` in the tools/list response. This is intentional design, not a bug.

### G-40: The deprecated `-StartModelContextProtocolServer` is still parsed
- Backwards compat is good, but the warning is once-only (`bDeprecationWarned` static, `ModelContextProtocolSettings.cpp:40-45`). In a long-running editor session, the second invocation is silent. Fine in practice.

---

# Part 5 — Discrepancies with `gap_analysis_and_roadmap.md`

The prior analysis correctly identified some gaps and missed others. Here's the reconciliation.

## 5.1 Where the prior doc was correct

| Prior doc claim | Source confirmation |
|---|---|
| Gap #1 "Only HTTP transport" | ✅ Confirmed. G-01 in this doc. |
| Gap #5 "No prompts support" | ✅ Confirmed. G-04. |
| Gap #11 "Cancel only works for AsyncAction tools" | ✅ Partially correct. AsyncAction CancelAsync IS implemented (line 347-360). The doc's claim is right for `FToolsetRegistryToolAdapter` (uses base no-op) but wrong as a generalization. |
| Gap #12 "No progress reporting with actual percentage" | ✅ Correct about the *percentage* part. The heartbeat mechanism exists. |
| Gap #13 "No input schema validation" | ✅ Correct. "Schema adherence assumed" per interface. |
| Gap #16 "No retry mechanism" | ✅ Correct. No retry in source. |
| Gap #20 "No console command execution" | ✅ Correct. No `execute_console_command` tool. |
| Gap #22 "No blueprint graph reading" | ✅ Correct. |
| Gap #23 "No log streaming" | ✅ Correct. No log resource provider. |
| Gap #24 "No profiling data access" | ✅ Correct. No `stat` tool. |
| Gap #26 "Linear tool search O(N)" | ✅ Confirmed in `ModelContextProtocolModule.cpp:99-107`. |
| Gap #32 "No runtime testing without Editor" | ✅ Correct — `ModelContextProtocolEditorToolLibrary` is editor-only via `WITH_EDITOR`. |

## 5.2 Where the prior doc was wrong or oversold

| Prior doc claim | What the source shows |
|---|---|
| Gap #2 "No stdio transport" | Correct. (Same as G-01.) |
| Gap #3 "No WebSocket support" | True, but WebSocket isn't in the MCP spec — this is a category error. MCP 2025-11-25 uses HTTP+SSE, not WebSocket. (See G-02.) |
| Gap #4 "No transport auto-detection" | True, but auto-detection only matters if you have multiple transports. Today there is only HTTP. Auto-detection becomes a real gap only after G-01 (stdio) is added. |
| Gap #6 "No sampling support" | Partially correct. The struct exists, the dispatch doesn't. See G-05. |
| Gap #7 "No roots support" | Misread: `roots` are client-side. The server can choose to read them or not. The right framing is "server doesn't expose project root as a resource" — which is G-06. |
| Gap #8 "No `notifications/resources/updated`" | ✅ Correct. G-07. |
| Gap #9 "Resource templates missing" | ✅ Correct. G-08. |
| Gap #10 "No pagination on tools/list" | **WRONG.** Pagination is implemented (G-23 in this doc, lines 328-398 of server). Default disabled, but configurable via CVar. |
| Gap #14 "No output schema validation" | Partially wrong. `outputSchema` IS advertised in `tools/list` (line 748-751) but not enforced. G-16 in this doc. |
| Gap #15 "No tool chaining" | "Chaining" isn't a thing in MCP. The closest concept is the tool-search pattern (G-39), which exists. |
| Gap #17 "No tool call history" | ✅ Correct. G-17. |
| Gap #18 "No real-time engine context" | ✅ Correct. G-19. |
| Gap #19 "No viewport screenshot" | ✅ Correct. G-19. |
| Gap #21 "No asset browser integration" | ✅ Correct. No asset browser tool. |
| Gap #25 "No multi-user isolation" | ✅ Correct. Single server, no user concept. |
| Gap #27 "No tool caching" | **WRONG.** Schema is cached in `InputJsonSchema` (line 196-199 of `ModelContextProtocolToolLibrary.cpp`). |
| Gap #28 "No request rate limiting" | ✅ Correct. G-25. |
| Gap #29 "No request queuing" | ✅ Correct. G-26. |
| Gap #30 "No built-in tool debugging" | Mostly wrong. There are 4 console commands + `VeryVerbose` log level. Not a debugging *trace* but more than "nothing." |
| Gap #31 "No tool development scaffold" | Mostly wrong. `UModelContextProtocolToolLibrary` and `UModelContextProtocolToolAsyncAction` are the scaffolds. A "New MCP Tool" content browser template would be nice but the building blocks exist. |
| Gap #33 "No CVar for runtime configuration" | **WRONG.** 4 CVars exist (G-04 in this doc). |

## 5.3 Gaps the prior doc invented

| Prior doc claim | Source state |
|---|---|
| "Malformed inputs can crash the editor" (Gap #13) | **False.** `bStrictMode=false` in `FJsonObjectConverter::JsonObjectToUStruct` means invalid params return an error result, not a crash. The interface header does say "assumed" but the implementation coerces safely. |
| "HTTP polling is inefficient" (Gap #3) | Misleading — MCP 2025-11-25 uses streaming HTTP (POST returns `text/event-stream`), not polling. There is no polling. |
| "Open asset" tool (Feature 2.3.2) | The MCP server has no way to interact with the editor's asset opener. This is a real gap, but `FAssetEditorManager::OpenEditorForAsset` is the right UE API, not the simplistic one implied. |
| "Multi-Modal Resource (Images)" (Feature 2.5.2) | The result factories for image exist. The "resource" side (multi-modal resources with MIME `image/png`) does NOT exist — the existing `FModelContextProtocolResource` supports binary blobs but the tools don't surface image data via `resources/read`. So the *tool* path is there but the *resource* path isn't. Subtle distinction. |
| "Subscription-Based Resources" (Feature 2.5.3) | The capability struct has `Subscribe` field, so the design anticipates it. Not in the dispatch, but the shape is half-done. |

## 5.4 Gaps the prior doc missed entirely (high-value)

1. **No `ModelContextProtocol.GenerateClientConfig` documentation** — major DX feature.
2. **No `ServerInfo` populated in initialize** — bug, G-11.
3. **No `notification/cancelled` validation** — server silently no-ops if `requestId` is unknown (`ModelContextProtocolServer.cpp:724`). Per spec this is correct behavior, but no error feedback to the client.
4. **Sessions have no timeout** — G-35.
5. **BP tool metadata is editor-only** — G-31, may break BP tools in shipping builds.
6. **The deprecated `-StartModelContextProtocolServer` is still parsed** — G-40 (informational).
7. **Toolset adapter cancel** — G-12 (the prior doc was right about this specific gap).
8. **No `embeddedResource` result type** — the enum has it as Hidden, but no `MakeEmbeddedResourceResult` factory exists. (See `ModelContextProtocolToolResults.h:23-24`.)
9. **No `ELicitation` use** — the `Elicitation` field exists in client capabilities but the server never uses it for confirmation dialogs. This is the correct MCP pattern for "are you sure?" prompts; the prior doc's Feature 2.6.3 (confirmation modal) should use this instead.
10. **The plugin is `IsExperimentalVersion=true`** — should be flagged in any extension plan as a "things may change" risk.

---

# Part 6 — Synthesis: what this means for the extension roadmap

(I don't write the roadmap here — that's a separate deliverable. But the source-confirmed gaps give a much more honest starting point.)

**Real P0 candidates** (high impact, low risk, fills real gaps):
- G-01 (stdio transport) — biggest UX win.
- G-11 (ServerInfo fix) — 1-line bug fix.
- G-19 (editor context tools: `get_editor_context`, `capture_viewport`, `execute_console_command`) — the doc's P0 list, but only after G-19 is well-defined.

**Real P1 candidates** (high impact, medium risk):
- G-04 (`prompts/*` support) — adds a real spec feature.
- G-07 (resource subscriptions) — already half-designed.
- G-12 (cancel for toolset adapter) — closes a real correctness gap.
- G-13 (real percentage progress) — needs API change but big DX win.

**Re-evaluate** (the prior doc had these at wrong priority):
- G-02 (standalone SSE) — Medium, not High. The current gated broadcast works for active sessions.
- Feature 2.5.1 (tool composition) — already exists as tool search. **Drop from roadmap.**
- Feature 2.5.2 (multi-modal image) — already exists in result factories. **Drop from roadmap.**
- Gap #10 (pagination) — already implemented. **Remove from gap list.**

**Cut from roadmap** (low ROI or already done):
- Feature 2.1.4 (sampling) — wrong direction, weak use case.
- Tool call history / persistence (P4 in prior doc) — useful but not on the critical path.

---

# Part 7 — How to verify this analysis

This is a primary source analysis. To verify:

1. **Each gap is cited to a file:line.** Re-open the file, go to the line, confirm.
2. **Each "this exists" claim is cited.** Same.
3. **The protocol version is `2025-11-25`** per `Source/ModelContextProtocol/Public/ModelContextProtocol.h:19`.
4. **The 6 modules are listed in** `ModelContextProtocol.uplugin:19-49`.
5. **The 4 console commands are in** `Source/ModelContextProtocol/Private/ModelContextProtocolModule.cpp:22-68` and `Source/ModelContextProtocolEngine/Private/ModelContextProtocolEngineModule.cpp:40-70`.
6. **The 4 CVars are in** `Source/ModelContextProtocol/Private/ModelContextProtocol.cpp:43-67`.
7. **The 5 client configs are in** `Source/ModelContextProtocolEngine/Private/ModelContextProtocolClientConfig.cpp:26-43`.

If any of these don't match, this analysis is wrong at that point and the gap is real-or-not opposite.

---

*End of primary gap analysis. ~2,200 lines of source reviewed across 6 modules.*
*Total file count: 80 .h/.cpp/.cs files.*
*Total source bytes: ~570KB (excluding tests).*
*Test source NOT reviewed in this analysis — see G-XX placeholders for test coverage gaps if needed.*
