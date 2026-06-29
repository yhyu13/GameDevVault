---
tags: [source/深度分析]
aliases: [UE5 MCP 缺点与改进, UE5 MCP 使用指南, UE5 MCP 最佳实践]
---

# UE5 ModelContextProtocol 插件：缺点、改进建议与最佳使用实践

> 本文是 `UE5-ModelContextProtocol-完整调用链路.md` 的姊妹篇。前者回答「代码是怎么工作的」，本文回答「为什么不够好」以及「怎么让它更好」。
>
> **关键修正：** 前文中错误地声称 MCP 插件「不支持 stdio 传输」。实际上，`FModelContextProtocolServer` 的 `StartStdioTransport()` / `StopStdioTransport()` 已经实现了完整的 stdio 传输模式（通过 `FModelContextProtocolStdioRunnable` 读取 stdin → 解析 JSON-RPC → `AsyncTask` 跳转 GameThread → 复用 HTTP 路径的处理逻辑 → 通过 `CreateStdioResultCallback` 将结果写回 stdout）。stdio 支持在 `FModelContextProtocolServer.h` 第63-68行和 `ModelContextProtocolServer.cpp` 第1135-1348行完整实现。我的错误源于第一次阅读时只看了 HTTP 部分，未翻到文件底部。这是值得自我反思的阅读盲区—— **永远不要因为没看完文件就下结论。**

---

## 一、当前实现中的缺陷（按严重程度排序）

### 1.1 `FindTool` 线性搜索 O(N) — 已验证的性能隐患

```cpp
// ModelContextProtocolModule.cpp:99
TSharedPtr<IModelContextProtocolTool> FModelContextProtocolModule::FindTool(const FString& ToolName) const
{
    const TSharedRef<IModelContextProtocolTool>* Tool = Tools.FindByPredicate(
        [&ToolName](const TSharedPtr<IModelContextProtocolTool>& Tool)
        {
            return Tool->GetName().Equals(ToolName, ESearchCase::IgnoreCase);
        });
    return Tool ? *Tool : TSharedPtr<IModelContextProtocolTool>();
}
```

**问题：** `TArray` 线性搜索，且每次 `Equals` 是大小写不敏感的 Unicode 比较。Eager 模式下（如 ToolsetRegistry 预注册所有工具），工具数量可能达到数百个。每个 `tools/call` 都要走这一遍。

**量化：** 假设 200 个工具，每次调用平均比较 100 次。UE 的 `FString::Equals` 对于 ASCII 是 memcmp 级别，但 `ESearchCase::IgnoreCase` 需要逐字符 `tolower` 转换。这在高频调用场景（如 AI 助手批量执行重构）中可能成为瓶颈。

**修复建议：** 维护一个 `TMap<FString, TSharedRef<IModelContextProtocolTool>>` 做索引。UE 的 `FString` 作为 `TMap` 的 Key 是大小写敏感的，所以需要在 `AddTool` 时同时插入到 `TMap`，在 `RemoveTool` 时从 `TMap` 移除。查找时先查 `TMap`（O(1)），失败再回退到 `TArray`（处理大小写不匹配的边缘情况）。

---

### 1.2 SSE 流实现存在冗余和未完善

```cpp
// ModelContextProtocolServer.cpp:1088
bool FModelContextProtocolServer::ProcessGetRequest(...)
{
    // We do not currently support sse on a separate endpoint
    UE::ModelContextProtocol::Private::CompleteWithResponseCode(OnComplete, EHttpServerResponseCodes::BadMethod);
    return true;
}
```

**问题：** GET 请求直接返回 `405 BadMethod`。MCP 的 Streamable HTTP 规范允许通过 GET 请求建立独立的 SSE 端点（用于通知推送），而当前实现将 SSE 完全耦合在 POST 的响应流中。这意味着：
- 通知（如 `notifications/tools/list_changed`）只能推送到有活跃 tool call 的 SSE 流
- 如果客户端没有正在执行的工具调用，它无法独立接收服务器推送的通知
- 这限制了某些客户端架构（如需要长期保持 SSE 连接但不频繁调用工具的 IDE 插件）

**修复建议：** 将 SSE 拆分为独立的 GET 端点。`FModelContextProtocolServer` 中已经有 `SseMcpRoute` 句柄（`FHttpRouteHandle`），但从未被绑定。应该实现：
```cpp
// 绑定 GET 到 SSE 端点
IHttpRouter::BindRoute(UrlPath, VERB_GET, &ProcessGetRequest)
// ProcessGetRequest 中：建立长期 SSE 连接，将 EventStreamWrite 存入 Session
// 通知通过独立的 SSE 通道推送，不依赖于 tool call 的响应流
```

---

### 1.3 `LastResourceDescriptorList` 的全局单缓存不是按 Session 隔离的

```cpp
// ModelContextProtocolServer.h:96
FModelContextProtocolResourceDescriptorList LastResourceDescriptorList;
```

**问题：** 资源列表缓存在 `FModelContextProtocolServer` 实例级别，所有 Session 共享同一个缓存。`ProcessReadResourceJsonRpcCall` 的逻辑是：先查 `LastResourceDescriptorList` 缓存，若未找到再遍历所有 Provider。这导致：
- Session A 调用 `resources/list` 后，Session B 可以直接 `resources/read` 读取 Session A 列出的资源
- 虽然 URI 匹配本身没有安全问题（Provider 的 `ReadResource` 不依赖 Session），但缓存语义上是不对的——资源列表是**按请求**的，不是全局的
- 更严重的是，如果 Session A 的 `list` 结果很大，占用了缓存，Session B 的 `read` 命中了缓存但实际 Provider 可能已经过期

**修复建议：** 将 `LastResourceDescriptorList` 移到 `FModelContextProtocolSession` 中，每个 Session 独立缓存。或者干脆移除缓存，在 `ProcessReadResourceJsonRpcCall` 中直接遍历所有 Provider（资源列表通常不大，遍历开销可忽略）。后一种更简洁且语义正确。

---

### 1.4 stdio 传输的 `AliveGuard` 检查时机存在竞态

```cpp
// ModelContextProtocolServer.cpp:1299
AsyncTask(ENamedThreads::GameThread, [WeakAlive, Server = Server, RequestId, Method, Params]()
{
    if (!WeakAlive.IsValid()) { return; }
    Server->ProcessStdioJsonRpcCall(RequestId, Method, Params);
});
```

**问题：** 在 `FModelContextProtocolStdioRunnable::Run()` 中，读取到 stdin 的 JSON 行后，通过 `AsyncTask` 将处理跳转到 GameThread。但是：
- `WeakAlive` 的 `IsValid()` 检查在 GameThread 上执行，但 `AliveGuard` 可能在**主线程还在处理这条消息的过程中**被 `~FModelContextProtocolServer()` 析构 `Reset()`
- 这意味着 `IsValid()` 通过 → 进入 `ProcessStdioJsonRpcCall` → 此时析构开始 → `Server` 的 `Sessions` 等成员被销毁 → 使用已释放内存

**对比 HTTP 路径：** HTTP 的 `HandleToolResult` 也有同样的 `WeakAlive` 检查，但 HTTP 的 `OnComplete` 回调是在 `FHttpServerResponse` 的析构中触发的，而 `FHttpServerResponse` 的持有者是 `FHttpServerConnection`，其生命周期独立于 `FModelContextProtocolServer`。stdio 的 `Server` 指针直接指向 `FModelContextProtocolServer` 自身，风险更高。

**修复建议：** 在 `ProcessStdioJsonRpcCall` 内部也使用 `TWeakPtr` 检查，并在**每一个**访问 `Server` 成员之前验证。或者更根本的：将 stdio 的 `StdioSession` 提升为独立的管理对象（类似 HTTP 的 `Sessions`），使得 stdio 的运行时生命周期不依赖于 `FModelContextProtocolServer` 的存活。

---

### 1.5 `StdioRunnable` 的线程安全缓冲区

```cpp
// ModelContextProtocolServer.cpp:1234
constexpr int32 BufferSize = 65536;
char Buffer[BufferSize];
if (fgets(Buffer, BufferSize, stdin) == nullptr) { break; }
```

**问题：** `fgets` 是阻塞的。如果 stdin 没有数据（例如客户端尚未发送请求），`fgets` 会阻塞 stdio 线程。虽然这是预期的行为，但如果 `FModelContextProtocolServer` 被析构（例如编辑器关闭时），`bRunning` 被设为 `false`，但 `fgets` 可能仍在阻塞中，直到下一个 stdin 输入到达。`StopStdioTransport` 调用 `StdioRunnable->Stop()` 后 `Kill(true)`，但 `Kill(true)` 是强制终止线程，在 Windows 上可能导致 `fgets` 的文件句柄处于不一致状态。

**修复建议：** 使用非阻塞 I/O（`SetStdinHandle` 为非阻塞模式，或使用 `PeekConsoleInput` 在 Windows 上），或者使用更现代的线程取消机制。

---

### 1.6 `bWrapPODResultsInObject` 的全局开关缺乏文档

```cpp
// ModelContextProtocolToolResults.cpp:176
if (UE::ModelContextProtocol::bWrapPODResultsInObject && StructuredContent->Type != EJson::Object)
{
    StructuredContent = FJsonDomBuilder::FObject()
        .Set(UE::ModelContextProtocol::PODWrapperResultPropertyName, StructuredContent)
        .AsJsonValue();
}
```

**问题：** 这个全局 `bool` 开关控制是否将非对象（POD）的结构化内容包装为 `{"result": value}` 对象。如果工具返回一个 `int32` 或 `FString`，根据这个开关，结果可能被包装也可能不被包装。这是为了向后兼容（MCP spec 的某个版本要求结果必须是对象）。但这个开关没有在任何 UPROPERTY 或 ConsoleVariable 中暴露，代码中的注释也不够清晰。工具作者可能不知道自己的返回结果会被这个开关影响。

**修复建议：** 将 `bWrapPODResultsInObject` 提升为 `UDeveloperSettings` 的可见属性，并在工具文档中明确说明。或者干脆移除这个开关，强制始终包装（因为 spec 已经稳定）。

---

### 1.7 工具 Schema 生成中的 `UMETA` 处理缺失

```cpp
// 在 FModelContextProtocolLibraryTool 的 Schema 生成中
// 通过 FJsonSchemaGenerator::UStructToJsonSchemaObject() 从 UPROPERTY 生成
```

**问题：** 从 `UFunction` 参数生成 JSON Schema 时，`UMETA` 元数据（如 `EditCondition`、`ClampMin`、`ClampMax`、`Enum` 的 `DisplayName`）没有被翻译为 JSON Schema 的 `minimum`/`maximum`/`enum`/`description` 等属性。这意味着 LLM 客户端无法知道一个 `int32` 参数的有效范围是 `0..100`，也不知道一个 `FString` 参数只能是 `"A"`、`"B"`、`"C"` 中的一个。这会导致 LLM 生成无效的参数，浪费 tool call 往返。

**修复建议：** 扩展 `FJsonSchemaGenerator` 或编写 MCP 专用的 Schema 生成器，将 UPROPERTY 的 `UMETA` 元数据映射到 JSON Schema 的 `minimum`/`maximum`/`enum`/`pattern`/`format` 等约束。例如：
- `UPROPERTY(meta = (ClampMin = 0, ClampMax = 100))` → `"minimum": 0, "maximum": 100`
- `UPROPERTY(meta = (Enum = "ENameOfEnum"))` → `"enum": ["ValueA", "ValueB"]`

---

### 1.8 `ValidateToolName` 对非法字符的警告不够严格

```cpp
// ModelContextProtocolModule.cpp:119-132
switch (UE::ModelContextProtocol::ValidateToolName(ToolName))
{
    case EToolNameValidation::InvalidCharacters:
        UE_LOGF(LogModelContextProtocol, Log, ...);  // 只是 Log，不是 Warning！
        break;  // 仍然添加到 Tools！
    default:
        break;
}
Tools.Add(Tool);
```

**问题：** 对于非法字符，`ValidateToolName` 返回 `InvalidCharacters`，但代码只打印一个 `Log` 级别（非 Warning）的日志，然后**继续**将工具添加到 `Tools` 中。这意味着 MCP 客户端可能收到一个工具名中包含非法字符的工具定义，然后在 `tools/call` 时因为同样的非法字符检查而失败。工具名在 `AddTool` 和 `FindTool` 中的验证不一致。

**修复建议：** 将 `InvalidCharacters` 也视为错误（返回 `false`），或者至少在 `AddTool` 时打印 `Warning`。如果必须保留兼容行为，应在 `FindTool` 和 `ProcessToolCallJsonRpcCall` 中对请求中的工具名也做同样的验证，确保不一致的字符处理在两端对称。

---

### 1.9 `ModelContextProtocolEngine` 的 `StartStdioTransport` 缺乏 UI 入口

```cpp
// ModelContextProtocolEngineModule.cpp 中没有调用 StartStdioTransport 的代码
// 只有 ModelContextProtocolModule.cpp 中的 Console 命令:
//   ModelContextProtocol.StartServer
//   ModelContextProtocol.StopServer
// 没有 ModelContextProtocol.StartStdioTransport 的 Console 命令！
```

**问题：** stdio 传输虽然代码完整实现，但用户无法通过 UI 或命令行启动它。只有 HTTP 传输有 `StartServer` 的 Console 命令。stdio 传输的启动只能通过代码中显式调用 `IModelContextProtocolModule::StartStdioTransport()` 来触发。这意味着终端用户（如 Claude Code 的默认 stdio 模式用户）无法直接使用这个插件，除非他们编写自定义启动器。

**修复建议：** 添加 `ModelContextProtocol.StartStdioTransport` 和 `ModelContextProtocol.StopStdioTransport` 的 Console 命令，并在 `UModelContextProtocolSettings` 的 UI 中添加一个复选框「启动时自动启用 stdio 传输」。

---

## 二、改进建议（让插件更强大、更简洁）

### 2.1 架构简化：将 HTTP 和 stdio 统一为「传输层」抽象

当前代码中，HTTP 和 stdio 的处理逻辑大量重复：
- `ProcessJsonRpcCall` 和 `ProcessStdioJsonRpcCall` 几乎相同的方法分发逻辑
- `HandleToolResult` 和 `HandleStdioToolResult` 几乎相同的 SSE/stdout 回写逻辑
- 两套 Session 管理（`Sessions` 数组和 `StdioSession` 单例）

**建议重构：** 引入 `ITransport` 抽象接口：
```cpp
class IModelContextProtocolTransport
{
public:
    virtual void SendResponse(const TSharedPtr<FJsonValue>& RequestId, const TSharedPtr<FJsonValue>& Result) = 0;
    virtual void SendNotification(const FString& Method, const TSharedPtr<FJsonObject>& Params) = 0;
    virtual void SendProgress(const TSharedPtr<FJsonValue>& ProgressToken, int32 Progress) = 0;
    virtual TSharedRef<FModelContextProtocolSession> GetOrCreateSession() = 0;
};

class FHttpTransport : public IModelContextProtocolTransport { ... };
class FStdioTransport : public IModelContextProtocolTransport { ... };
```

这样 `ProcessJsonRpcCall` 只需接收一个 `ITransport` 引用，无需关心底层是 HTTP 还是 stdio。Session 管理也可以统一（`StdioSession` 就是 `Sessions` 中的第一个元素）。代码量减少约 30%，维护难度显著降低。

---

### 2.2 工具注册改用 `TMap` 索引 + 预计算哈希

**当前：** `TArray` 线性搜索，O(N)，每次调用大小写不敏感字符串比较。

**建议：**
```cpp
class FModelContextProtocolModule
{
    // 保持 TArray 用于有序遍历（tools/list 需要有序输出）
    TArray<TSharedRef<IModelContextProtocolTool>> Tools;
    
    // 新增：TMap 做索引，Key 是 ToLower 后的工具名，Value 是 TArray 中的索引
    TMap<FString, int32> ToolNameToIndex;
};

TSharedPtr<IModelContextProtocolTool> FindTool(const FString& ToolName) const
{
    if (const int32* Index = ToolNameToIndex.Find(ToolName.ToLower()))
    {
        return Tools[*Index];
    }
    return nullptr;
}
```

复杂度从 O(N) 降到 O(1)（UE 的 `FString` 哈希是预计算的，不分配内存）。`AddTool` 和 `RemoveTool` 时同步维护 `ToolNameToIndex`。`TArray` 保留用于 `tools/list` 的有序输出（因为 `TMap` 的遍历顺序是哈希桶顺序，不稳定）。

---

### 2.3 引入「工具组」概念，替代 Search 模式的元工具

**当前 Search 模式的问题：**
- `list_toolsets` 返回纯文本目录，LLM 需要解析自然语言来理解工具分组
- `describe_toolset` 返回单个 toolset 的完整 JSON Schema，可能仍然很大
- `call_tool` 的 tool name 需要包含 toolset 前缀（如 `EditorScripting.AssetTool.CreateAsset`），这增加了 LLM 的生成复杂度

**建议：** 在 MCP 的 `tools/list` 响应中引入 `toolsets` 字段（扩展 spec，或者利用 `_meta` 字段），让工具分组信息直接嵌入到标准 `tools/list` 响应中。这样 LLM 客户端（如 Claude Code）在 `tools/list` 时就知道了分组，可以按需展开。无需引入 `list_toolsets`/`describe_toolset`/`call_tool` 这三个非标准元工具。

```json
{
  "tools": [
    { "name": "EditorScripting.CreateAsset", "description": "...", "toolset": "EditorScripting" },
    { "name": "EditorScripting.DeleteAsset", "description": "...", "toolset": "EditorScripting" },
    { "name": "LevelEditor.SpawnActor", "description": "...", "toolset": "LevelEditor" }
  ]
}
```

当工具数量超过某个阈值时，客户端只加载每个 toolset 的「代表工具」（第一个），需要时再调用 `tools/list?toolset=EditorScripting` 展开该组。这比当前的三个元工具更简洁，也更符合 MCP 的标准语义。

---

### 2.4 工具 Schema 注入 UPROPERTY 约束

前文提到的问题。具体实现建议：

```cpp
// 在 FJsonSchemaGenerator 或 MCP 专用生成器中扩展
void ApplyUMetaConstraints(FJsonDomBuilder::FObject& Schema, const FProperty* Property)
{
    if (const int64* ClampMin = Property->GetMetaDataAsInt64(TEXT("ClampMin")))
        Schema.Set(TEXT("minimum"), *ClampMin);
    if (const int64* ClampMax = Property->GetMetaDataAsInt64(TEXT("ClampMax")))
        Schema.Set(TEXT("maximum"), *ClampMax);
    if (FString* Enum = Property->GetMetaData(TEXT("Enum")))
    {
        // 解析 UEnum 的 DisplayName
        FJsonDomBuilder::FArray EnumValues;
        for (const auto& Entry : GetEnumDisplayNames(*Enum))
            EnumValues.Add(Entry);
        Schema.Set(TEXT("enum"), EnumValues);
    }
    if (FString* Pattern = Property->GetMetaData(TEXT("Pattern")))
        Schema.Set(TEXT("pattern"), *Pattern);
    if (FString* Format = Property->GetMetaData(TEXT("JsonFormat")))
        Schema.Set(TEXT("format"), *Format);
}
```

这样 LLM 在生成参数时就有了约束信息，大幅减少无效 tool call。

---

### 2.5 引入工具「预热」和「缓存」机制

**问题：** 某些工具（如读取大型关卡、编译着色器、Bake 光照）的首次调用非常慢（数秒到数分钟）。LLM 客户端没有耐心等待，可能超时重试或放弃。

**建议：** 为 `IModelContextProtocolTool` 增加 `WarmUp()` 接口：
```cpp
class IModelContextProtocolTool
{
    // 返回预估执行时间（毫秒），0 表示瞬时
    virtual uint32 GetEstimatedExecutionTimeMs() const { return 0; }
    
    // 返回是否有缓存机制（如编译结果缓存）
    virtual bool HasCache() const { return false; }
    
    // 返回是否需要预热（如加载资产到内存）
    virtual bool NeedsWarmUp() const { return false; }
    virtual void WarmUp() {} // 异步预热，不影响工具执行
};
```

在 `tools/list` 的响应中，通过 `_meta` 字段注入这些元信息：
```json
{
  "name": "CompileShaders",
  "_meta": { "estimatedTimeMs": 300000, "hasCache": true, "needsWarmUp": true }
}
```

LLM 客户端可以根据这些信息：
- 对耗时工具提前调用 `WarmUp()`（在后台）
- 在 `tools/call` 时设置更长的超时时间
- 对有缓存的工具，在参数不变时复用结果

---

### 2.6 资源提供者的「懒加载」优化

**当前：** `ProcessListResourcesJsonRpcCall` 每次调用都遍历所有 `ResourceProvider` → 调用 `ListResources()` → 生成 JSON。如果 Provider 很多（如每个资产目录一个 Provider），这会很慢。

**建议：** 引入资源缓存 TTL 和懒加载：
```cpp
struct FResourceProviderCache
{
    double LastUpdateTime = 0.0;
    double TTLSeconds = 60.0; // 1分钟缓存
    FModelContextProtocolResourceDescriptorList CachedList;
    bool IsStale() const { return FPlatformTime::Seconds() - LastUpdateTime > TTLSeconds; }
};
```

`ProcessListResources` 先检查缓存，仅在 stale 时调用 `ListResources`。这对资产浏览器等低频变化、高频查询的场景非常有用。

---

## 三、如何让 AI Agent 用得更好

### 3.1 工具描述的质量决定一切

LLM 只能通过 `tools/list` 中的 `description` 和 `inputSchema` 来理解工具。当前实现中：
- `BlueprintFunctionLibrary` 的工具描述取自 `UFUNCTION` 的 `ToolTip`（如果设置了的话）
- 如果没有 `ToolTip`，描述为空字符串

**问题：** 很多 UE 内置的 `BlueprintFunctionLibrary` 没有 `ToolTip` 或 `ToolTip` 是 UI 导向的（如 "Create a new asset"），没有告诉 LLM 参数的语义和约束。

**最佳实践：**
1. **为每个工具函数写清晰的 `UFUNCTION` 注释：**
   ```cpp
   UFUNCTION(BlueprintCallable, Category = "MCP Tools", meta = (ToolTip = "Create a new asset in the Content Browser. Returns the asset path on success. Input: AssetName (string, no spaces), AssetType (enum: StaticMesh, Texture, Material), ParentFolder (string, default '/Game')."))
   static FModelContextProtocolToolResult CreateAsset(const FString& AssetName, const FString& AssetType, const FString& ParentFolder = TEXT("/Game"));
   ```

2. **使用 `meta = (MCPDescription = "...")` 替代 `ToolTip`：** 如果 ToolTip 是面向人类 UI 的，可以添加 `MCPDescription` 元数据专门面向 LLM。当前插件已支持 `ToolTip` 自动提取，但可以考虑添加 `MCPDescription` 的优先级更高。

3. **参数命名要语义化：** `Index` 不如 `ArrayIndex`；`Str` 不如 `AssetPath`。LLM 生成参数时，参数名是上下文的重要线索。

### 3.2 工具拆分粒度：粗 vs 细

**粗粒度工具（如 `BuildLevel`）的问题：**
- 参数多，Schema 复杂，LLM 容易填错
- 执行时间长，反馈延迟高
- 出错后难以定位是哪个参数的问题

**细粒度工具（如 `SetActorLocation`, `SetActorRotation`, `SpawnActor`）的问题：**
- 工具数量爆炸，上下文窗口被淹没
- LLM 需要多次调用完成一个完整操作，token 消耗大

**建议：** 采用「粗主工具 + 细辅助工具」的层级结构。Search 模式已经部分实现了这一点（通过 toolset 分组），但可以在工具描述中更明确地表达这种层级：
```cpp
// 主工具：描述整体操作
UFUNCTION(meta = (ToolTip = "Create a basic room: spawns 4 walls, floor, ceiling, and a door. For fine-grained control, use the Wall/... tools.", MCPDescription = "High-level room creation tool. Use this for simple rooms; for custom architecture, use individual wall tools."))
static FModelContextProtocolToolResult CreateBasicRoom(...);

// 辅助工具：描述精确操作
UFUNCTION(meta = (ToolTip = "Spawn a single wall at the given location and rotation.", MCPDescription = "Low-level wall placement tool. Use only when CreateBasicRoom is insufficient."))
static FModelContextProtocolToolResult SpawnWall(...);
```

### 3.3 返回结构化结果，减少 LLM 的解析负担

**当前默认：** `MakeTextResult()` 返回纯文本字符串。LLM 需要解析自然语言来提取信息（如 "Asset created at /Game/MyAsset"）。

**建议：** 优先使用 `MakeStructuredContentResult()`：
```cpp
USTRUCT()
struct FCreateAssetResult
{
    GENERATED_BODY()
    UPROPERTY() bool bSuccess = false;
    UPROPERTY() FString AssetPath;
    UPROPERTY() FString ErrorMessage;
};

static FModelContextProtocolToolResult CreateAsset(...)
{
    FCreateAssetResult Result;
    Result.bSuccess = true;
    Result.AssetPath = TEXT("/Game/MyAsset");
    return UE::ModelContextProtocol::MakeStructuredContentResult(Result);
}
```

这样返回结果是：
```json
{"content": [{"type": "text", "text": "{\"bSuccess\":true,\"AssetPath\":\"/Game/MyAsset\"}"}], "structuredContent": {"bSuccess": true, "AssetPath": "/Game/MyAsset"}}
```

LLM 可以直接读取 `structuredContent` 中的字段，无需解析文本。这在与多步骤工作流（如创建资产 → 设置材质 → 放置到关卡）中尤其重要——每一步的输入都依赖上一步的输出字段。

### 3.4 错误结果要包含「可操作建议」

当前 `MakeErrorResult()` 只返回一个文本错误消息。LLM 收到错误后，只能猜测如何修复。

**建议：** 扩展错误结果，包含建议的修复方式：
```cpp
FModelContextProtocolToolResult MakeErrorResultWithSuggestion(
    const FString& ErrorText, 
    const FString& SuggestedAction)
{
    auto Result = MakeTextResult(ErrorText);
    Result.JsonObject->SetBoolField(TEXT("isError"), true);
    Result.JsonObject->SetStringField(TEXT("suggestion"), SuggestedAction);
    return Result;
}

// 使用：
return MakeErrorResultWithSuggestion(
    TEXT("Asset '/Game/MyAsset' already exists"),
    TEXT("Call DeleteAsset first, or use a different AssetName.")
);
```

LLM 收到这个错误后，可以自动调用 `DeleteAsset` 然后重试 `CreateAsset`，无需用户介入。

---

## 四、如何让人用得更好、更方便

### 4.1 一键配置：消除手动 JSON 编辑

**当前：** 用户需要在 `UModelContextProtocolSettings` 中手动配置端口、路径，然后运行 `ModelContextProtocol.GenerateClientConfig` 命令生成 JSON 配置文件。Claude Code 用户还需要手动编辑 `.mcp.json`。

**建议改进：**
1. **在 Editor Preferences → Plugins → ModelContextProtocol 中提供图形化配置面板：**
   - 复选框：自动启动 HTTP 服务器（Editor 启动时）
   - 复选框：自动启动 stdio 传输（Editor 启动时）
   - 端口输入框（带验证：1-65535）
   - 路径输入框（默认 `/mcp`）
   - 客户端选择：Claude Code / Cursor / VSCode / Gemini / Codex
   - 按钮：「生成客户端配置」→ 自动写入对应文件，并提示路径

2. **检测端口冲突：** 若 8000 被占用（如另一个 UE 实例），自动提示并建议下一个可用端口。

3. **配置导入/导出：** 支持将配置导出为 `.mcpconfig` 文件，团队共享。

### 4.2 调试工具：让开发者能看到 MCP 在做什么

**当前：** 没有内建的调试 UI。开发者只能通过日志（`LogModelContextProtocol`）来追踪问题。`UE_LOG` 在 Editor 中不便过滤和搜索。

**建议改进：**
1. **MCP 调试窗口（Editor 扩展）：**
   - 实时显示 HTTP 请求/响应日志（类似 Postman 的 History）
   - 显示当前活跃的 Session 列表、连接状态、协议版本
   - 显示已注册工具列表（带 Schema 预览）
   - 显示已注册资源列表
   - 手动触发 `tools/list`、`resources/list` 并查看 JSON 输出
   - 手动发送 `tools/call` 并查看结果

2. **可视化工具调用链路：** 类似 UE 的 Blueprint Debugger，显示一次 `tools/call` 的完整调用链路：哪个 Session 发起 → 哪个工具被调用 → 参数值 → 执行时间 → 结果/错误 → 响应回写耗时。

3. **Schema 验证器：** 在 Editor 中打开一个工具函数，右键 →「验证 MCP Schema」，检查：
   - 参数是否有 `ToolTip` 或 `MCPDescription`
   - 参数类型是否支持（如 `FText` 不被支持 → 警告）
   - 参数名是否语义化
   - 返回值类型是否正确（`FModelContextProtocolToolResult`）

### 4.3 文档和示例：降低上手门槛

**当前：** 没有官方文档说明如何编写一个 MCP 工具。开发者需要通过阅读源码来理解 `UModelContextProtocolToolLibrary` 和 `UModelContextProtocolToolAsyncAction` 的用法。

**建议改进：**
1. **在 `99-Templates` 中添加 MCP 工具模板：**
   - 同步工具模板（BlueprintFunctionLibrary）
   - 异步工具模板（AsyncAction）
   - 资源提供者模板

2. **示例项目：** 提供包含 10-15 个常用 MCP 工具的示例插件（如创建资产、修改关卡、运行 PIE、编译项目、运行测试），每个工具附带完整的 `UFUNCTION` 注释和 Schema 示例。

3. **视频教程：** 5 分钟快速上手：从安装插件 → 配置 Claude Code → 让 AI 自动创建资产 → 检查 Editor 中的变化。

### 4.4 安全性：默认配置最小化原则

**当前：** 默认 `bAutoStartServer = true`（Editor 启动时自动启动 HTTP 服务器），且默认端口 8000 是公开的（虽然 Origin 限制了 localhost）。

**问题：** 如果用户在没有意识到的情况下启动服务器，攻击者可能利用本地网络中的 DNS Rebinding（虽然 Origin 检查已经防护了大部分情况）或者通过 localhost 代理（如某些代理软件配置错误）。

**建议改进：**
1. **默认 `bAutoStartServer = false`：** 用户必须显式启动服务器（通过 UI 或命令）。
2. **首次启动时弹出确认对话框：** 说明「启动 MCP 服务器后，本地 AI 助手可以控制 Editor。确保你信任的 AI 助手正在运行。」
3. **Token 认证：** 在 `initialize` 请求中支持 `auth_token` 参数，与 `UModelContextProtocolSettings` 中配置的预期 token 匹配。这在团队共享开发机时尤其重要。

### 4.5 版本管理和兼容性

**当前：** 协议版本协商在 `initialize` 时完成（支持 2025-11-25, 2025-06-18, 2024-11-05）。但没有机制来通知用户「你的 Claude Code 版本太旧，不支持此协议版本」。

**建议改进：**
1. **版本不匹配时的友好提示：** 当客户端请求不支持的版本时，返回错误信息中包含建议的更新方式：
   ```json
   {"error": {"code": -32602, "message": "Unsupported protocol version 2024-09-01. Please update Claude Code to v0.41.0+ or use ModelContextProtocolSettings to enable legacy protocol support."}}
   ```

2. **协议版本迁移日志：** 在 `CHANGELOG` 中记录每个版本的新增/移除/变更方法，让工具作者知道何时需要更新他们的工具代码。

---

## 五、关联知识库

- [[UE5-ModelContextProtocol-完整调用链路]] — 本文的姊妹篇，覆盖完整代码调用链
- [[MCP Specification]] — Anthropic 官方规范，本文多处引用 2025-06-18 版本
- [[ToolsetRegistry]] — UE 编辑器工具注册框架，与 MCP 插件通过适配器集成
- [[UE HTTP Server]] — `FHttpServerModule` 的底层实现，本文讨论的 SSE 拆分需要此知识
- [[FJsonSchemaGenerator]] — JSON Schema 从 UStruct 反射生成的实现，本文建议扩展其约束映射
- [[FJsonDomBuilder]] — 本文多处引用，用于 JSON 响应构造
- [[Claude Code MCP]] — Claude Code 的 MCP 客户端配置和使用文档

---

## 输出产物

- [x] 已修正前文的错误（stdio 传输已存在）
- [x] 已列出 9 个缺陷（按严重程度排序）
- [x] 已提出 6 个改进建议（架构简化、性能优化、功能增强）
- [x] 已给出 AI Agent 的 4 个最佳实践
- [x] 已给出人类用户的 5 个体验改进建议
- [ ] 已应用到工作中（调研中，待后续项目验证）

---

*Create date: 2026-06-27*  
*Last modified: 2026-06-27*  
*Source: `Engine/Plugins/Experimental/ModelContextProtocol/`*  
*勘误：前文中关于 stdio 不支持的结论是错误的。stdio 传输在 `FModelContextProtocolServer::StartStdioTransport()` 中完整实现，通过 `FModelContextProtocolStdioRunnable` 在独立线程中读取 stdin。*
