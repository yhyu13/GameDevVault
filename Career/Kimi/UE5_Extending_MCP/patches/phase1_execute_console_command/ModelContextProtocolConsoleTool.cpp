// Copyright Epic Games, Inc. All Rights Reserved.

#include "ModelContextProtocolConsoleTool.h"
#include "IModelContextProtocolModule.h"
#include "ModelContextProtocol.h"
#include "ModelContextProtocolToolResults.h"

#include "Dom/JsonObject.h"
#include "HAL/IConsoleManager.h"
#include "Misc/OutputDeviceRedirector.h"

FString FModelContextProtocolConsoleTool::GetName() const
{
	return TEXT("execute_console_command");
}

FString FModelContextProtocolConsoleTool::GetDescription() const
{
	return TEXT("Execute a console command (as if typed into the editor/PIE console). Commands prefixed with 'stat', 'show', 'r.' or similar are common.");
}

TSharedPtr<FJsonObject> FModelContextProtocolConsoleTool::GetInputJsonSchema() const
{
	TSharedPtr<FJsonObject> Schema = MakeShared<FJsonObject>();
	Schema->SetStringField(TEXT("type"), TEXT("object"));

	TSharedPtr<FJsonObject> Properties = MakeShared<FJsonObject>();

	TSharedPtr<FJsonObject> CommandProp = MakeShared<FJsonObject>();
	CommandProp->SetStringField(TEXT("type"), TEXT("string"));
	CommandProp->SetStringField(TEXT("description"), TEXT("Console command string to execute. e.g., 'stat fps', 'show collision', 'r.ScreenPercentage 50'"));
	Properties->SetObjectField(TEXT("command"), CommandProp);

	Schema->SetObjectField(TEXT("properties"), Properties);

	TArray<TSharedPtr<FJsonValue>> RequiredArray;
	RequiredArray.Add(MakeShared<FJsonValueString>(TEXT("command")));
	Schema->SetArrayField(TEXT("required"), RequiredArray);

	return Schema;
}

FModelContextProtocolToolResult FModelContextProtocolConsoleTool::Run(const TSharedPtr<FJsonObject>& Params)
{
	if (!Params.IsValid())
	{
		return UE::ModelContextProtocol::MakeErrorResult(TEXT("Missing parameters. Expected: {\"command\": \"...\"}"));
	}

	FString Command;
	if (!Params->TryGetStringField(TEXT("command"), Command) || Command.IsEmpty())
	{
		return UE::ModelContextProtocol::MakeErrorResult(TEXT("Missing or empty required parameter: command"));
	}

	// Capture log output while the command executes
	FOutputDeviceArchiveWrapper* LogCapturer = nullptr;
	FString CapturedLog;
	LogCapturer = new FOutputDeviceArchiveWrapper(FArchive::CreateWriterFromBuffer(CapturedLog));
	LogCapturer->AddToRoot();
	GLog->AddOutputDevice(LogCapturer);

	// Execute the command via the engine console
	bool bExecuted = false;
	if (GEngine)
	{
		UWorld* World = GEngine->GetCurrentPlayWorld();
		if (!World)
		{
			// Fall back to editor world if not in PIE
			World = GEngine->GetWorldContexts().Num() > 0 ? GEngine->GetWorldContexts()[0].World() : nullptr;
		}
		bExecuted = GEngine->Exec(World, *Command, *LogCapturer);
	}

	GLog->RemoveOutputDevice(LogCapturer);
	LogCapturer->RemoveFromRoot();
	delete LogCapturer;

	if (!bExecuted)
	{
		return UE::ModelContextProtocol::MakeErrorResult(FString::Printf(TEXT("Command '%s' was not recognized by the engine console."), *Command));
	}

	// Build result text
	FString ResultText = FString::Printf(TEXT("Executed: %s"), *Command);
	if (!CapturedLog.IsEmpty())
	{
		ResultText += TEXT("\n\nConsole Output:\n") + CapturedLog;
	}

	return UE::ModelContextProtocol::MakeTextResult(ResultText);
}
