// Copyright Epic Games, Inc. All Rights Reserved.

#include "ModelContextProtocolViewportTool.h"
#include "ModelContextProtocolToolResults.h"

#include "Dom/JsonObject.h"
#include "Editor.h"
#include "UnrealClient.h"
#include "ImageUtils.h"
#include "Misc/Base64.h"

FString FModelContextProtocolViewportTool::GetName() const
{
	return TEXT("capture_viewport");
}

FString FModelContextProtocolViewportTool::GetDescription() const
{
	return TEXT("Capture the current editor viewport as a PNG image and return it as a base64-encoded image. Useful for visual debugging and scene analysis.");
}

TSharedPtr<FJsonObject> FModelContextProtocolViewportTool::GetInputJsonSchema() const
{
	TSharedPtr<FJsonObject> Schema = MakeShared<FJsonObject>();
	Schema->SetStringField(TEXT("type"), TEXT("object"));
	// No required properties -- captures the active viewport by default.
	return Schema;
}

FModelContextProtocolToolResult FModelContextProtocolViewportTool::Run(const TSharedPtr<FJsonObject>& Params)
{
	if (!GEditor)
	{
		return UE::ModelContextProtocol::MakeErrorResult(TEXT("Editor not available. This tool only works within the Unreal Editor."));
	}

	FViewport* Viewport = GEditor->GetActiveViewport();
	if (!Viewport)
	{
		return UE::ModelContextProtocol::MakeErrorResult(TEXT("No active viewport found. Make sure a level viewport is open."));
	}

	const FIntPoint Size = Viewport->GetSizeXY();
	if (Size.X == 0 || Size.Y == 0)
	{
		return UE::ModelContextProtocol::MakeErrorResult(TEXT("Viewport has zero size."));
	}

	// Read pixels from the viewport (RGBA8)
	TArray<FColor> PixelData;
	if (!Viewport->ReadPixels(PixelData))
	{
		return UE::ModelContextProtocol::MakeErrorResult(TEXT("Failed to read viewport pixels."));
	}

	if (PixelData.Num() != Size.X * Size.Y)
	{
		return UE::ModelContextProtocol::MakeErrorResult(TEXT("Viewport pixel read returned unexpected size."));
	}

	// Encode to PNG (ThumbnailCompressImageArray returns void)
	TArray<uint8> PngData;
	FImageUtils::ThumbnailCompressImageArray(Size.X, Size.Y, PixelData, PngData);

	if (PngData.Num() == 0)
	{
		return UE::ModelContextProtocol::MakeErrorResult(TEXT("PNG encoding produced empty data."));
	}

	// Base64 encode the PNG data
	FString Base64Image = FBase64::Encode(PngData);

	// Return as MCP image content
	return UE::ModelContextProtocol::MakeImageResult(TEXT("image/png"), MoveTemp(Base64Image));
}
