# UE5 MCP Extension Plan: Gaps Analysis & New Feature Roadmap

> **Analysis Target**: `Engine/Plugins/Experimental/ModelContextProtocol` (UE 5.8+)
> **Source**: `C:\Epic\UE_Engine\UE5_8\UnrealEngine\Engine\Plugins\Experimental\ModelContextProtocol\`
> **Reference**: `UE5-ModelContextProtocol-完整调用链路.md`
> **Date**: 2026-07-07

---

## Part 1: What UE5 MCP Is Not Perfect At

### 1.1 Transport Layer Gaps

| # | Gap | Severity | Why It Matters |
|---|-----|----------|---------------|
| 1 | **Only HTTP transport** | 🔴 High | Claude Code's default mode is **stdio** (spawn process + stdin/stdout). HTTP requires the user to manually start the server. This is a significant friction point for local AI coding assistants. |
| 2 | **No stdio transport** | 🔴 High | MCP spec 2025-06-18 defines both HTTP and stdio. stdio is simpler (no port conflicts, no firewall issues) and the de facto standard for CLI-based tools. |
| 3 | **No WebSocket support** | 🟡 Medium | HTTP polling is inefficient for bidirectional communication. WebSocket would enable real-time log streaming and push notifications. |
| 4 | **No transport auto-detection** | 🟡 Medium | The plugin can't detect whether the client expects HTTP or stdio. Must be configured manually. |

**Evidence from source**:
```cpp
// ModelContextProtocolServer.cpp
// Only HTTP routes are bound:
IHttpRouter::BindRoute(UrlPath, VERB_POST,  &ProcessPostRequest)
IHttpRouter::BindRoute(UrlPath, VERB_GET,   &ProcessGetRequest)
IHttpRouter::BindRoute(UrlPath, VERB_DELETE, &ProcessDeleteRequest)
// No stdio reader/writer exists anywhere in the codebase.
```

---

### 1.2 MCP Spec Compliance Gaps

| # | Gap | Severity | Why It Matters |
|---|-----|----------|---------------|
| 5 | **No `prompts` support** | 🔴 High | MCP spec defines `prompts/list` and `prompts/get` — pre-built prompts the LLM can use. UE5 MCP only implements `tools` and `resources`. Prompts would let the engine provide standardized prompts like "Analyze this blueprint for performance issues" or "Refactor this C++ class to use BlueprintNativeEvent". |
| 6 | **No `sampling` support** | 🟡 Medium | MCP spec allows the **server** to request LLM completions from the client. This would enable the MCP server to ask the LLM for help (e.g., "Generate a description for this new tool I'm creating"). |
| 7 | **No `roots` support** | 🟡 Medium | MCP spec allows clients to declare project roots. UE5 MCP doesn't expose the engine's content root or project directory as MCP resources. |
| 8 | **No `notifications/resources/updated` or `notifications/resources/list_changed`** | 🟡 Medium | Resources can change (e.g., asset list). Clients should be notified. Currently only `notifications/tools/list_changed` is implemented. |
| 9 | **Resource templates missing** | 🟡 Medium | MCP spec has `resource/templates` for parameterized resources (e.g., `asset://{path}`). Only static `resources/list` is implemented. |
| 10 | **No pagination on `tools/list`** | 🟢 Low | If tools exceed ~100, the response becomes unwieldy. MCP spec supports pagination cursors. |

**Evidence from source**:
```cpp
// ModelContextProtocolServer.cpp - ProcessJsonRpcCall()
// Only these methods are handled:
//   ping, initialize, notifications/initialized, notifications/cancelled
//   tools/list, tools/call
//   resources/list, resources/read
// Missing: prompts/list, prompts/get, sampling/*, resource templates, pagination
```

---

### 1.3 Tool Execution Gaps

| # | Gap | Severity | Why It Matters |
|---|-----|----------|---------------|
| 11 | **Cancel only works for AsyncAction tools** | 🔴 High | `FModelContextProtocolLibraryTool::CancelAsync()` and `FToolsetRegistryToolAdapter::CancelAsync()` are **empty implementations**. Long-running editor operations (e.g., lighting build, shader compilation) cannot be cancelled via MCP. |
| 12 | **No progress reporting with actual percentage** | 🔴 High | `LastProgressValue` is just a heartbeat counter. For operations like "Build Lighting" or "Cook Content", the LLM has no idea how long to wait. |
| 13 | **No input schema validation** | 🟡 Medium | The comment in `IModelContextProtocolTool.h` explicitly says: *"Schema adherence by MCP clients is assumed, not strictly checked internally."* Malformed inputs can crash the editor. |
| 14 | **No output schema validation** | 🟡 Medium | Tools claim to return structured output but don't validate it. LLM clients that expect JSON get broken responses. |
| 15 | **No tool chaining / composition** | 🟡 Medium | No built-in way for one tool to call another. Must be done manually by the LLM client. |
| 16 | **No retry mechanism** | 🟡 Medium | Failed tool calls have no retry. Transient failures (e.g., asset locked) require the LLM to manually retry. |
| 17 | **No tool call history/persistence** | 🟢 Low | Sessions are ephemeral. Previous tool calls and their results are lost on reconnect. |

**Evidence from source**:
```cpp
// IModelContextProtocolTool.h
virtual void CancelAsync(const FModelContextProtocolToolRequestId& RequestId) {}
// Default empty implementation — sync tools and ToolsetRegistry can't cancel.

// ModelContextProtocolToolLibrary.cpp - FModelContextProtocolLibraryTool::Run()
// UFunction::ProcessEvent() is called directly with no schema validation.
```

---

### 1.4 Editor Integration Gaps

| # | Gap | Severity | Why It Matters |
|---|-----|----------|---------------|
| 18 | **No real-time engine context** | 🔴 High | The MCP server has no way to expose: selected actors, viewport camera, current level, play mode state, editor mode. An LLM asking "what am I looking at?" gets no answer. |
| 19 | **No viewport screenshot/image capture** | 🔴 High | Vision-capable LLMs (GPT-4V, Claude 3, Gemini) can't see the viewport. Sending a screenshot would enable "why is this shadow flickering?" type questions. |
| 20 | **No console command execution** | 🔴 High | The `~` console is the primary debugging interface. No tool exposes `ExecuteConsoleCommand()`. |
| 21 | **No asset browser integration** | 🟡 Medium | Can't list content browser assets, filter by type, open for edit. Must rely on ToolsetRegistry which is editor-plugin-specific. |
| 22 | **No blueprint graph reading** | 🟡 Medium | LLM can't read the structure of a Blueprint graph (nodes, connections, variables) to suggest refactors. |
| 23 | **No log streaming** | 🟡 Medium | Engine logs are critical for debugging. No real-time log streaming to the LLM client. |
| 24 | **No profiling data access** | 🟡 Medium | Can't expose `stat` data, GPU profiling, or CPU timing to help LLM diagnose performance issues. |
| 25 | **No multi-user isolation** | 🟢 Low | Multiple developers on the same machine can't have isolated MCP sessions with different tool permissions. |

**Evidence from source**:
```cpp
// ModelContextProtocolEditorToolLibrary.h
// The only editor-specific tool library is a thin wrapper around UBlueprintFunctionLibrary.
// No viewport access, no selected actor queries, no console commands, no asset browser APIs.
```

---

### 1.5 Performance & Scalability Gaps

| # | Gap | Severity | Why It Matters |
|---|-----|----------|---------------|
| 26 | **Linear tool search O(N)** | 🟡 Medium | `IModelContextProtocolModule::FindTool()` does linear scan in `TArray`. With 100+ tools (Eager mode), this becomes noticeable. |
| 27 | **No tool caching/indexing** | 🟡 Medium | Tool schemas are regenerated on every `tools/list` call. Should be cached. |
| 28 | **No request rate limiting** | 🟡 Medium | Malicious or buggy LLM clients could spam tool calls, freezing the editor. |
| 29 | **No request queuing/prioritization** | 🟢 Low | All requests are FIFO. No way to prioritize "cancel" over "new tool call". |

**Evidence from source**:
```cpp
// ModelContextProtocolModule.cpp
TSharedPtr<IModelContextProtocolTool> FindTool(const FString& ToolName) const
{
    for (const TSharedRef<IModelContextProtocolTool>& Tool : Tools)
    {
        if (Tool->GetName().Equals(ToolName, ESearchCase::IgnoreCase))
        {
            return Tool;
        }
    }
    return nullptr;
}
// Linear search. No TMap index.
```

---

### 1.6 Developer Experience Gaps

| # | Gap | Severity | Why It Matters |
|---|-----|----------|---------------|
| 30 | **No built-in tool debugging** | 🟡 Medium | No way to trace a tool call through the system. No verbose logging mode. |
| 31 | **No tool development scaffold** | 🟡 Medium | Creating a new tool requires subclassing `UModelContextProtocolToolLibrary` (deprecated) or using ToolsetRegistry. No "New MCP Tool" template. |
| 32 | **No runtime testing without Editor** | 🟡 Medium | `ModelContextProtocolEditor` requires Editor module. Runtime-only tools can't be tested in Standalone mode. |
| 33 | **No CVar for runtime configuration** | 🟢 Low | Only `UModelContextProtocolSettings` (Editor-only). No runtime command-line overrides beyond `-ModelContextProtocolPort`. |

---

## Part 2: Brainstorm — New Features & Tools UE5 MCP Could Have

### 2.1 Transport & Protocol (Foundation Layer)

#### Feature 2.1.1: stdio Transport Support
**What**: Add `stdio` transport alongside HTTP. When launched with `--mcp-stdio`, read JSON-RPC from stdin and write to stdout.
**Why**: Claude Code, Zed, and other editors use stdio by default. Removes port configuration entirely.
**How**: Add `FModelContextProtocolStdioTransport` class that reads `std::cin` line-by-line (JSON-RPC messages), parses, and dispatches to the same `ProcessJsonRpcCall()` handler. Write responses to `std::cout`.
**Priority**: 🔴 P0

#### Feature 2.1.2: WebSocket Transport
**What**: Upgrade HTTP to WebSocket for bidirectional streaming.
**Why**: Real-time log streaming, asset change notifications, viewport updates.
**How**: Use existing `FHttpServerModule` WebSocket support (if available in UE 5.8+) or add a lightweight WebSocket server.
**Priority**: 🟡 P2

#### Feature 2.1.3: Prompts Provider
**What**: Implement `prompts/list` and `prompts/get` per MCP spec.
**Why**: Pre-built prompts standardize common LLM interactions:
  - `optimize-blueprint`: "Analyze this blueprint's event graph for performance issues..."
  - `refactor-cpp`: "Refactor this class to use modern UE5 patterns..."
  - `debug-render`: "The viewport shows artifacts. Check these common causes..."
**How**: Add `IModelContextProtocolPromptProvider` interface. Register prompts via `UModelContextProtocolPromptLibrary` (similar to ToolLibrary).
**Priority**: 🔴 P1

#### Feature 2.1.4: Sampling Support (Server → LLM)
**What**: Allow the MCP server to request completions from the LLM client via `sampling/createMessage`.
**Why**: The engine could ask the LLM for help generating tool descriptions, asset documentation, or blueprint node suggestions.
**How**: Add `IModelContextProtocolModule::RequestSampling()` that sends `sampling/createMessage` JSON-RPC to the client and awaits response.
**Priority**: 🟡 P2

---

### 2.2 Engine Context Provider (The "Eyes" of the LLM)

#### Feature 2.2.1: `get_editor_context` Tool
**What**: Returns real-time editor state: selected actors, viewport camera transform, current level, play mode, editor mode (Placement, Landscape, Foliage, etc.).
**Why**: Enables "what am I looking at?" questions. The LLM can't help if it doesn't know the context.
**Example response**:
```json
{
  "selected_actors": ["PointLight_5", "StaticMeshActor_12"],
  "viewport_camera": {"location": [100, 200, 300], "rotation": [0, -30, 45]},
  "current_level": "/Game/Maps/MainLevel",
  "editor_mode": "Placement",
  "play_mode": "Editor"
}
```
**Priority**: 🔴 P0

#### Feature 2.2.2: `capture_viewport` Tool
**What**: Captures the current viewport as a PNG/JPEG and returns it as a base64 data URI or saves to disk and returns the path.
**Why**: Vision-capable LLMs (GPT-4V, Claude 3, Gemini) can analyze screenshots. "Why is this shadow flickering?" → capture → analyze.
**How**: Use `FSlateApplication::Get().TakeScreenshot()` or `FHighResScreenshotConfig`.
**Priority**: 🔴 P0

#### Feature 2.2.3: `stream_logs` Resource
**What**: Provides a `resource` that streams the latest engine logs in real-time via SSE.
**Why**: LLM can monitor logs and proactively suggest fixes when errors appear.
**How**: Hook into `FOutputDevice` or intercept `UE_LOG` output. Buffer last N lines and push deltas.
**Priority**: 🟡 P1

#### Feature 2.2.4: `get_profiling_snapshot` Tool
**What**: Returns current `stat` data (fps, frame time, GPU time, memory usage) as structured JSON.
**Why**: Performance debugging via LLM. "Why is my FPS dropping?" → get snapshot → analyze.
**How**: Read from `FPerformanceSnapshot` or `FStatGroupData`.
**Priority**: 🟡 P1

---

### 2.3 Asset & Content Tools (The "Hands" of the LLM)

#### Feature 2.3.1: `list_assets` Tool
**What**: List content browser assets with filtering by path, type, tag.
**Why**: "Find all materials that use the Master_Material base" → list → filter.
**Example**:
```json
{
  "path": "/Game/Materials",
  "type": "Material",
  "recursive": true
}
```
**Priority**: 🔴 P1

#### Feature 2.3.2: `open_asset` Tool
**What**: Open an asset in the appropriate editor (Blueprint Editor, Material Editor, etc.).
**Why**: LLM can guide the user to specific assets for editing.
**Priority**: 🟡 P2

#### Feature 2.3.3: `read_blueprint_graph` Tool
**What**: Export a Blueprint's event graph / function graph as a structured representation (nodes, connections, variables, pins).
**Why**: LLM can analyze Blueprint logic, suggest optimizations, detect infinite loops.
**How**: Iterate `UEdGraphNode`s, export as JSON with node types, positions, pin connections.
**Priority**: 🟡 P1

#### Feature 2.3.4: `diff_asset` Tool
**What**: Compare two versions of an asset (e.g., current vs. last saved) and return a diff.
**Why**: "What changed in this Blueprint since yesterday?" → diff → summary.
**How**: Use `FAssetRevision` or source control diff.
**Priority**: 🟢 P3

---

### 2.4 Development & Build Tools

#### Feature 2.4.1: `execute_console_command` Tool
**What**: Execute any UE console command (`stat fps`, `show collision`, `r.ScreenPercentage 50`).
**Why**: The console is the primary debugging interface. LLM-guided debugging requires this.
**How**: `GEngine->Exec()` or `UWorld::Exec()`.
**Priority**: 🔴 P0

#### Feature 2.4.2: `cook_content` Tool
**What**: Trigger content cooking for specific platforms.
**Why**: "Cook for Windows to test the build" → execute → wait → report.
**How**: Wrap `UCookOnTheFlyServer` or `FUnrealCookCommand`.
**Priority**: 🟡 P2

#### Feature 2.4.3: `build_lighting` Tool
**What**: Trigger lighting build with quality settings.
**Why**: LLM can guide lighting optimization workflow.
**How**: Call `FLightingBuildOptions` and `FEditorBuildUtils::BuildLighting()`.
**Priority**: 🟡 P2

#### Feature 2.4.4: `package_project` Tool
**What**: Trigger project packaging.
**Why**: CI/CD integration via LLM. "Package for Shipping" → execute → report.
**How**: Wrap `FProjectPackagingSettings` and `FGameProjectAutomationTests`.
**Priority**: 🟢 P3

---

### 2.5 Advanced MCP Features

#### Feature 2.5.1: Tool Composition / Chaining
**What**: Allow tools to be composed declaratively. E.g., `chain([get_editor_context, capture_viewport, analyze_image])`.
**Why**: Reduces LLM round-trips. Complex workflows become single tool calls.
**How**: Add `FModelContextProtocolComposedTool` that wraps multiple tools and executes them sequentially, aggregating results.
**Priority**: 🟡 P2

#### Feature 2.5.2: Multi-Modal Resource (Images)
**What**: Return images as MCP resources with MIME type `image/png`.
**Why**: Vision LLMs can analyze screenshots, material previews, texture content.
**How**: Extend `FModelContextProtocolResource` to support binary content with base64 encoding.
**Priority**: 🔴 P1

#### Feature 2.5.3: Subscription-Based Resources
**What**: `resources/subscribe` — client subscribes to a resource URI, server pushes updates when the resource changes.
**Why**: Real-time viewport updates, live log streaming, asset change notifications.
**How**: Add `FModelContextProtocolSubscriptionManager` that tracks subscriptions and pushes `notifications/resources/updated` SSE messages.
**Priority**: 🟡 P2

#### Feature 2.5.4: Progress Reporting with Percentage
**What**: Add `IModelContextProtocolTool::ReportProgress(RequestId, Percentage, Message)`.
**Why**: Long operations (build, cook, lighting) need meaningful progress. Current heartbeat counter is useless.
**How**: Tool implementations call `ReportProgress()` which sends `notifications/progress` with actual percentage.
**Priority**: 🔴 P1

#### Feature 2.5.5: Schema Validation
**What**: Validate tool inputs against JSON Schema before calling `Run()`.
**Why**: Prevents crashes from malformed inputs. Catches client bugs early.
**How**: Use `FJsonSchemaValidator` (if available in UE) or a lightweight JSON Schema validator.
**Priority**: 🟡 P1

---

### 2.6 Security & Reliability

#### Feature 2.6.1: Request Rate Limiting
**What**: Rate limit tool calls per session (e.g., max 10/sec).
**Why**: Prevents accidental or malicious DoS from buggy LLM clients.
**How**: Add `FModelContextProtocolRateLimiter` with token bucket algorithm per session.
**Priority**: 🟡 P2

#### Feature 2.6.2: Tool Permission Levels
**What**: Assign permission levels to tools (ReadOnly, ReadWrite, Dangerous). Client must declare its permission level during initialization.
**Why**: Prevents LLM from accidentally deleting content or packaging projects without confirmation.
**How**: Add `permissions` field to `ClientCapabilities`. Filter available tools based on permission level.
**Priority**: 🟡 P2

#### Feature 2.6.3: Tool Call Confirmation
**What**: "Dangerous" tools (delete, cook, package) require explicit user confirmation before execution.
**Why**: Prevents destructive operations from LLM hallucinations.
**How**: Show a modal dialog in the editor: "LLM wants to execute 'delete_asset'. Confirm?"
**Priority**: 🟡 P1

---

## Part 3: Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Close the most critical gaps.

| Task | Files to Modify | Effort |
|------|----------------|--------|
| Add stdio transport | `ModelContextProtocolServer.h/cpp` + new `ModelContextProtocolStdioTransport.h/cpp` | Medium |
| Add `get_editor_context` tool | New `ModelContextProtocolEditorContextTool.cpp` | Small |
| Add `execute_console_command` tool | New `ModelContextProtocolConsoleTool.cpp` | Small |
| Add `capture_viewport` tool | New `ModelContextProtocolViewportTool.cpp` | Medium |
| Add `prompts` support | New `IModelContextProtocolPromptProvider.h`, `ModelContextProtocolPrompts.cpp` | Medium |

### Phase 2: Content Tools (Weeks 3-4)
**Goal**: Enable LLM to interact with project content.

| Task | Files to Modify | Effort |
|------|----------------|--------|
| Add `list_assets` tool | New `ModelContextProtocolAssetBrowserTool.cpp` | Medium |
| Add `read_blueprint_graph` tool | New `ModelContextProtocolBlueprintTool.cpp` | Large |
| Add `stream_logs` resource | New `ModelContextProtocolLogResourceProvider.cpp` | Medium |
| Add progress reporting with percentage | `IModelContextProtocolTool.h` + `ModelContextProtocolServer.cpp` | Medium |

### Phase 3: Advanced Features (Weeks 5-6)
**Goal**: Multi-modal, subscriptions, security.

| Task | Files to Modify | Effort |
|------|----------------|--------|
| Multi-modal image resources | `IModelContextProtocolResourceProvider.h` + `ModelContextProtocolResources.cpp` | Medium |
| Subscription-based resources | `ModelContextProtocolServer.cpp` + new `ModelContextProtocolSubscriptionManager.cpp` | Large |
| Tool permission levels | `ModelContextProtocolSession.h` + `IModelContextProtocolModule.h` | Medium |
| Request rate limiting | New `ModelContextProtocolRateLimiter.cpp` | Small |
| Schema validation | `IModelContextProtocolTool.h` + `FModelContextProtocolLibraryTool.cpp` | Medium |

### Phase 4: Performance & Polish (Weeks 7-8)
**Goal**: Scale and reliability.

| Task | Files to Modify | Effort |
|------|----------------|--------|
| Replace linear tool search with TMap | `ModelContextProtocolModule.h/cpp` | Small |
| Add tool caching | `ModelContextProtocolModule.cpp` | Small |
| Add tool call history/persistence | `ModelContextProtocolSession.cpp` | Medium |
| Tool development scaffold (New MCP Tool template) | Editor module + Content Browser | Medium |
| Full MCP spec compliance test suite | `ModelContextProtocolTests` | Large |

---

## Part 4: New Modules to Create

```
ModelContextProtocol/
  ├── Private/
  │   ├── Transports/
  │   │   ├── ModelContextProtocolStdioTransport.cpp    ← NEW (Phase 1)
  │   │   └── ModelContextProtocolWebSocketTransport.cpp ← NEW (Phase 3, optional)
  │   ├── ModelContextProtocolPrompts.cpp              ← NEW (Phase 1)
  │   ├── ModelContextProtocolSubscriptionManager.cpp  ← NEW (Phase 3)
  │   └── ModelContextProtocolRateLimiter.cpp          ← NEW (Phase 3)
  │
ModelContextProtocolEngine/
  ├── Private/
  │   ├── ModelContextProtocolConsoleTool.cpp          ← NEW (Phase 1)
  │   ├── ModelContextProtocolViewportTool.cpp         ← NEW (Phase 1)
  │   └── ModelContextProtocolLogResourceProvider.cpp  ← NEW (Phase 2)
  │
ModelContextProtocolEditor/
  ├── Private/
  │   ├── ModelContextProtocolEditorContextTool.cpp    ← NEW (Phase 1)
  │   ├── ModelContextProtocolAssetBrowserTool.cpp     ← NEW (Phase 2)
  │   ├── ModelContextProtocolBlueprintTool.cpp      ← NEW (Phase 2)
  │   └── ModelContextProtocolBuildTools.cpp           ← NEW (Phase 2)
  │
```

---

## Part 5: Connection to Our Training Pipeline

These extensions directly feed into our `UE5_Training_MCP` pipeline:

1. **stdio transport** → `mcp_data_generator.py` can spawn the engine directly, no HTTP config needed
2. **`get_editor_context`** + **`capture_viewport`** → Training data includes real engine state, not just text
3. **`stream_logs`** → Live feedback loop for iterative improvement (model sees errors, suggests fixes)
4. **`execute_console_command`** → Model can experiment with CVars and observe results
5. **Multi-modal** → Vision models can analyze screenshots for rendering issues
6. **Prompts** → Standardize the "interview question" format for our training data generation

The extended MCP becomes both a **data source** (for training) and a **testbed** (for evaluation) for our UE5-trained small models.

---

*Last modified: 2026-07-07*
*Source: `C:\Epic\UE_Engine\UE5_8\UnrealEngine\Engine\Plugins\Experimental\ModelContextProtocol\`*
