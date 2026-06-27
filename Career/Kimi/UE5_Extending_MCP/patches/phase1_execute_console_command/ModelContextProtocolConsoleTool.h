// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "IModelContextProtocolTool.h"

#define UE_API MODELCONTEXTPROTOCOLENGINE_API

/**
 * MCP tool that executes Unreal Engine console commands.
 * Wraps GEngine->Exec() to expose the ~ console to LLM clients.
 */
struct FModelContextProtocolConsoleTool : public IModelContextProtocolTool
{
public:
	//~ Begin IModelContextProtocolTool API
	virtual FString GetName() const override;
	virtual FString GetDescription() const override;
	virtual TSharedPtr<FJsonObject> GetInputJsonSchema() const override;
	virtual FModelContextProtocolToolResult Run(const TSharedPtr<FJsonObject>& Params) override;
	//~ End IModelContextProtocolTool API
};

#undef UE_API
