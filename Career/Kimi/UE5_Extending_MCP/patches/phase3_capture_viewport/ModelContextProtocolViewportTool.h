// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "IModelContextProtocolTool.h"

/**
 * MCP tool that captures the current editor viewport as a PNG image.
 * Returns a base64-encoded image result for multi-modal LLM analysis.
 */
struct FModelContextProtocolViewportTool : public IModelContextProtocolTool
{
public:
	//~ Begin IModelContextProtocolTool API
	virtual FString GetName() const override;
	virtual FString GetDescription() const override;
	virtual TSharedPtr<FJsonObject> GetInputJsonSchema() const override;
	virtual FModelContextProtocolToolResult Run(const TSharedPtr<FJsonObject>& Params) override;
	//~ End IModelContextProtocolTool API
};
