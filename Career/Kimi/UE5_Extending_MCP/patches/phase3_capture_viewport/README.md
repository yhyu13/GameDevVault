# Phase 3: capture_viewport

## What It Does

Adds an MCP tool `capture_viewport` that lets LLM clients capture the current Unreal Editor viewport as a PNG image and receive it as a base64-encoded image result. This enables **multi-modal analysis** — vision-capable LLMs can now "see" the editor state.

### Tool Schema

```json
{
  "name": "capture_viewport",
  "description": "Capture the current editor viewport as a PNG image and return it as a base64-encoded image. Useful for visual debugging and scene analysis.",
  "inputSchema": {
    "type": "object"
  }
}
```

### Example MCP Result

```json
{
  "content": [
    {
      "type": "image",
      "mimeType": "image/png",
      "data": "iVBORw0KGgoAAAANSUhEUg..."
    }
  ]
}
```

## Files Changed

| File | Type | Description |
|------|------|-------------|
| `ModelContextProtocolEditor.h` | Modified | Forward-declares `FModelContextProtocolViewportTool`; adds `ViewportTool` member pointer |
| `ModelContextProtocolEditor.cpp` | Modified | Includes header; registers/deregisters viewport tool alongside `get_editor_context` |
| `ModelContextProtocolViewportTool.h` | New | Tool declaration |
| `ModelContextProtocolViewportTool.cpp` | New | Tool implementation — reads viewport pixels, encodes PNG, base64, returns `MakeImageResult` |

## Key Design Decisions

1. **Editor module** — viewport capture requires `GEditor` and `FViewport`, both editor-only. Lives in `ModelContextProtocolEditor`.

2. **No parameters** — captures the active viewport by default. Future extension could accept `viewport_index` or `resolution` parameters.

3. **PNG encoding** — `FImageUtils::ThumbnailCompressImageArray()` encodes `TArray<FColor>` to `TArray<uint8>` PNG. This is the standard UE path for screenshot-to-PNG.

4. **Base64 return** — `FBase64::Encode()` converts the PNG bytes to a string. `MakeImageResult("image/png", MoveTemp(Base64Image))` produces an MCP-compliant image content block.

5. **Defensive validation** — checks `GEditor`, `Viewport`, `Size`, `ReadPixels` success, `PixelData` count, and `PngData` size before returning.

## Apply

```bash
# Prerequisites: Phase 2 (get_editor_context) must already be applied
cd Engine/Plugins/Experimental/ModelContextProtocol
patch -p5 < phase3_capture_viewport.patch
```

## Build Notes

- `FImageUtils::ThumbnailCompressImageArray()` returns `void` (not `bool`). Don't wrap it in an `if` condition.
- `FBase64::Encode(const TArray<uint8>&)` returns `FString`. Must be non-const for `MoveTemp()` to work with `MakeImageResult(..., FString&&)`.
- `UnrealClient.h` is included directly (not `Engine/UnrealClient.h`) — the file lives in `Runtime/Engine/Public/UnrealClient.h`.

## Source Evidence

- `FViewport::ReadPixels()`: `UnrealClient.h` line 113 — `ENGINE_API virtual bool ReadPixels(TArray<FColor>& OutImageData, ...)`
- `FImageUtils::ThumbnailCompressImageArray()`: `ImageUtils.h` line 316 — `ENGINE_API static void ThumbnailCompressImageArray(int32, int32, const TArray<FColor>&, TArray<uint8>&)`
- `FBase64::Encode()`: `Base64.h` line 42 — `static CORE_API FString Encode(const TArray<uint8>& Source, ...)`
- `MakeImageResult`: `ModelContextProtocolToolResults.h` line 82 — `UE_API FModelContextProtocolToolResult MakeImageResult(const FString&, FString&&, ...)`

## Next (Remaining v0.2)

| # | Feature | Size | Module |
|---|---------|------|--------|
| 4 | `progress reporting` | M | Core (tool execution framework) |
| 5 | `stdio transport` | XL | Core (new transport layer) |

## Limitations

- Captures only the **active** viewport (the one with focus). Multi-viewport setups may need a parameter to select which viewport.
- Resolution is whatever the viewport currently is — no downscaling. Large 4K viewports produce large base64 strings.
- `ReadPixels` stalls the render thread briefly. For high-frequency capture, consider async readback.
