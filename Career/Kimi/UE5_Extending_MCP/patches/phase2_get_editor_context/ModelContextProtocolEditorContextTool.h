// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "IModelContextProtocolTool.h"

/**
 * MCP tool that queries the current Unreal Editor context.
 * Returns structured JSON with selected actors, current level, editor mode, and world statistics.
 */
struct FModelContextProtocolEditorContextTool : public IModelContextProtocolTool
{
public:
	//~ Begin IModelContextProtocolTool API
	virtual FString GetName() const override;
	virtual FString GetDescription() const override;
	virtual TSharedPtr<FJsonObject> GetInputJsonSchema() const override;
	virtual FModelContextProtocolToolResult Run(const TSharedPtr<FJsonObject>& Params) override;
	//~ End IModelContextProtocolTool API

private:
	static FString GetWorldTypeString(EWorldType::Type WorldType);
};
