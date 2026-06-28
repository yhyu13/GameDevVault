# Phase 5: stdio Transport

## What It Does

Adds **stdio transport** to the UE5 MCP plugin, enabling CLI-based LLM clients (e.g., Claude Code, `mcp` CLI) to spawn the Unreal Editor directly and communicate via line-delimited JSON-RPC over `stdin`/`stdout`. This complements the existing HTTP+SSE transport.

### Why stdio Matters

- **No port configuration** — The LLM client spawns the editor as a subprocess; no TCP port binding or firewall rules needed.
- **No CORS / Origin headers** — stdio is a single pipe; no HTTP request validation overhead.
- **Standard MCP transport** — The MCP spec defines stdio as the primary transport for local tool servers. Most CLI clients default to it.

### Stdio JSON-RPC Flow

```
Client (stdin)  ->  {jsonrpc: "2.0", id: 1, method: "initialize", params: {...}}
Server (stdout) ->  {jsonrpc: "2.0", id: 1, result: {protocolVersion: "2025-11-25", ...}, sessionId: "..."}

Client (stdin)  ->  {jsonrpc: "2.0", id: 2, method: "tools/list"}
Server (stdout) ->  {jsonrpc: "2.0", id: 2, result: {tools: [...]}}

Client (stdin)  ->  {jsonrpc: "2.0", id: 3, method: "tools/call", params: {name: "execute_console_command", arguments: {...}}}
Server (stdout) ->  {jsonrpc: "2.0", id: 3, result: {content: [...]}}

During long-running tools:
Server (stdout) ->  {jsonrpc: "2.0", method: "notifications/progress", params: {progressToken: "...", progress: 25}}
```

### Auto-Start

Pass `-ModelContextProtocolStdio` on the command line to automatically start the stdio transport during engine initialization:

```bash
UnrealEditor.exe MyProject.uproject -ModelContextProtocolStdio
```

Console commands are also available:

```
ModelContextProtocol.StartStdioTransport
ModelContextProtocol.StopStdioTransport
```

## Files Changed

| File | Module | Change |
|------|--------|--------|
| `IModelContextProtocolModule.h` | Core | Added `StartStdioTransport()` / `StopStdioTransport()` pure virtual methods |
| `ModelContextProtocolServer.h` | Core | Added `StartStdioTransport()` / `StopStdioTransport()` public API; `ProcessStdioJsonRpcCall` / `ProcessStdioToolCallJsonRpcCall` private dispatch; `StdioThread`, `StdioRunnable`, `StdioSession` members; `friend class FModelContextProtocolStdioRunnable` |
| `ModelContextProtocolServer.cpp` | Core | Added `FModelContextProtocolStdioRunnable` (FRunnable that reads UTF-8 lines from stdin); `WriteStdioJsonLine` / `WriteStdioErrorResponse` / `WriteStdioResultResponse` helpers; `CreateStdioResultCallback` (strips SSE wrapper, writes plain JSON to stdout); full stdio dispatch logic reusing existing HTTP handlers with dummy `FHttpServerRequest` |
| `ModelContextProtocolModule.h` | Core | Added `StartStdioTransport()` / `StopStdioTransport()` declarations |
| `ModelContextProtocolModule.cpp` | Core | Implemented `StartStdioTransport()` / `StopStdioTransport()`; `ShutdownModule` now stops stdio before HTTP server |
| `ModelContextProtocolEngineModule.cpp` | Engine | Auto-starts stdio transport on `-ModelContextProtocolStdio` flag in `PostEngineInit` |

## Key Design Decisions

1. **Reuse existing HTTP handlers via callback wrapper** — Instead of duplicating tool call logic, `ProcessStdioToolCallJsonRpcCall` delegates to `ProcessToolCallJsonRpcCall` with a custom `FHttpResultCallback` (`CreateStdioResultCallback`). This callback receives the same SSE-wrapped responses the HTTP path uses, strips the `event: message\r\ndata: ` envelope, and writes the plain JSON to stdout. This means:
   - Tool execution logic is **not duplicated**.
   - Progress reporting (Phase 4) works over stdio **for free** — the SSE progress notifications are stripped and written as plain JSON-RPC notifications.
   - Heartbeat progress (controlled by `ProgressIntervalSeconds` CVar) also works over stdio.

2. **Single session model** — stdio transport maintains one session (`StdioSession`). `initialize` creates/replaces it; subsequent calls validate `StdioSession->Status == Initialized`. No `Mcp-Session-Id` header is needed because there's only one client per pipe.

3. **Dummy `FHttpServerRequest`** — `ProcessPingJsonRpcCall`, `ProcessListToolsJsonRpcCall`, etc. don't actually use the `Request` parameter (except `ProcessInitializeJsonRpcCall` which reads `Request.PeerAddress`, which we set to `nullptr`). So passing a default-constructed `FHttpServerRequest` is safe.

4. **UTF-8 over stdio** — Reading uses `fgets` + `FUTF8ToTCHAR`; writing uses `FTCHARToUTF8` + `fwrite` to stdout. No reliance on Windows console code page. This ensures Cyrillic, CJK, and emoji in tool output round-trip correctly.

5. **Thread model** — `FModelContextProtocolStdioRunnable` runs on a dedicated `FRunnableThread` reading stdin in a blocking loop. Each line is parsed and marshalled to the game thread via `AsyncTask(ENamedThreads::GameThread, ...)`. This prevents JSON-RPC dispatch from blocking the game thread while waiting for input.

6. **Destructor safety** — `~FModelContextProtocolServer()` calls `StopStdioTransport()` before `StopServer()`, ensuring the stdio thread is killed before the server state is torn down. `AliveGuard` is still reset after stdio cleanup.

## Apply

```bash
# Prerequisites: Phases 1-4 must be applied first
cd Engine/Plugins/Experimental/ModelContextProtocol
patch -p5 < phase5_stdio_transport.patch
```

## Build Notes

- `FUtf8String::Get()` does not exist in UE5; use `FString` + `FTCHARToUTF8` for writing to stdout.
- `FModelContextProtocolStdioRunnable` must be declared as `friend` in `ModelContextProtocolServer.h` to access `AliveGuard` and `ProcessStdioJsonRpcCall`.
- `FModelContextProtocolModule` must declare the new interface methods in its `.h` to satisfy `IModelContextProtocolModule`.

## Source Evidence

- `FModelContextProtocolStdioRunnable::Run`: `ModelContextProtocolServer.cpp` lines ~1186–1260
- `CreateStdioResultCallback`: `ModelContextProtocolServer.cpp` lines ~1169–1185
- `ProcessStdioJsonRpcCall`: `ModelContextProtocolServer.cpp` lines ~1343–1416
- `StartStdioTransport` / `StopStdioTransport`: `ModelContextProtocolServer.cpp` lines ~1316–1341
- Auto-start flag: `ModelContextProtocolEngineModule.cpp` lines ~88–95

## Limitations

- `fgets` is blocking; `StopStdioTransport()` uses `FRunnableThread::Kill(true)` which may briefly block if stdin is idle. In practice, the parent process closes the pipe on shutdown, causing `fgets` to return EOF immediately.
- No `Mcp-Protocol-Version` header validation for stdio (there is no HTTP header). The negotiated version from `initialize` is still stored in `StdioSession`.
- `notifications/tools/list_changed` broadcasts (triggered by `ModelContextProtocol.RefreshTools`) are sent to stdio sessions via the same SSE-stripping callback, but stdio clients may not expect unsolicited notifications. This is harmless — the client can ignore unknown notifications.
- Stdio transport does not support multiple concurrent sessions. Only one stdio client can be connected at a time.

## Compatibility

- **Backward-compatible** — HTTP transport is unchanged. Existing HTTP clients work exactly as before.
- **Additive-only** — No existing tool or API is modified. All stdio transport code is new.
- **Cross-transport** — A server can run both HTTP and stdio simultaneously (e.g., HTTP for IDE integration, stdio for CLI usage), though `StdioSession` is independent of HTTP `Sessions`.
