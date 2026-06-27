// Copyright Epic Games, Inc. All Rights Reserved.

#include "ModelContextProtocolEditorContextTool.h"
#include "ModelContextProtocolToolResults.h"

#include "Dom/JsonObject.h"
#include "Editor.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Selection.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

FString FModelContextProtocolEditorContextTool::GetName() const
{
	return TEXT("get_editor_context");
}

FString FModelContextProtocolEditorContextTool::GetDescription() const
{
	return TEXT("Query the current Unreal Editor state including selected actors, current level, editor mode, and world statistics. Returns structured JSON.");
}

TSharedPtr<FJsonObject> FModelContextProtocolEditorContextTool::GetInputJsonSchema() const
{
	TSharedPtr<FJsonObject> Schema = MakeShared<FJsonObject>();
	Schema->SetStringField(TEXT("type"), TEXT("object"));
	// No required properties — this is a read-only query tool.
	return Schema;
}

FString FModelContextProtocolEditorContextTool::GetWorldTypeString(EWorldType::Type WorldType)
{
	switch (WorldType)
	{
		case EWorldType::None:           return TEXT("None");
		case EWorldType::Game:           return TEXT("Game");
		case EWorldType::Editor:         return TEXT("Editor");
		case EWorldType::PIE:            return TEXT("PIE");
		case EWorldType::EditorPreview:  return TEXT("EditorPreview");
		case EWorldType::GamePreview:    return TEXT("GamePreview");
		case EWorldType::GameRPC:        return TEXT("GameRPC");
		case EWorldType::Inactive:       return TEXT("Inactive");
		default:                         return TEXT("Unknown");
	}
}

FModelContextProtocolToolResult FModelContextProtocolEditorContextTool::Run(const TSharedPtr<FJsonObject>& Params)
{
	if (!GEditor)
	{
		return UE::ModelContextProtocol::MakeErrorResult(TEXT("Editor not available. This tool only works within the Unreal Editor."));
	}

	TSharedPtr<FJsonObject> Result = MakeShared<FJsonObject>();

	// --- Current world / level info ---
	UWorld* EditorWorld = GEditor->GetEditorWorldContext().World();
	if (EditorWorld)
	{
		Result->SetStringField(TEXT("current_level"), EditorWorld->GetMapName());
		Result->SetStringField(TEXT("world_type"), GetWorldTypeString(EditorWorld->WorldType));

		int32 ActorCount = 0;
		for (TActorIterator<AActor> It(EditorWorld); It; ++It)
		{
			++ActorCount;
		}
		Result->SetNumberField(TEXT("actor_count"), ActorCount);
	}
	else
	{
		Result->SetStringField(TEXT("current_level"), TEXT("Unknown"));
		Result->SetStringField(TEXT("world_type"), TEXT("Unknown"));
		Result->SetNumberField(TEXT("actor_count"), 0);
	}

	// --- Editor mode ---
	const bool bIsPIE = (GEditor->PlayWorld != nullptr);
	Result->SetBoolField(TEXT("is_pie"), bIsPIE);
	Result->SetBoolField(TEXT("is_simulating"), GEditor->bIsSimulatingInEditor);

	// --- Selected actors ---
	TArray<TSharedPtr<FJsonValue>> SelectedActors;
	int32 SelectedCount = 0;
	if (USelection* SelectedSet = GEditor->GetSelectedActors())
	{
		for (int32 i = 0; i < SelectedSet->Num(); ++i)
		{
			AActor* Actor = Cast<AActor>(SelectedSet->GetSelectedObject(i));
			if (Actor)
			{
				TSharedPtr<FJsonObject> ActorObj = MakeShared<FJsonObject>();
				ActorObj->SetStringField(TEXT("name"), Actor->GetName());
				ActorObj->SetStringField(TEXT("class"), Actor->GetClass()->GetName());
				SelectedActors.Add(MakeShared<FJsonValueObject>(ActorObj));
				++SelectedCount;
			}
		}
	}
	Result->SetArrayField(TEXT("selected_actors"), SelectedActors);
	Result->SetNumberField(TEXT("selected_actor_count"), SelectedCount);

	// Serialize to compact JSON string for the text result
	FString OutputString;
	TSharedRef<TJsonWriter<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>> Writer =
		TJsonWriterFactory<TCHAR, TCondensedJsonPrintPolicy<TCHAR>>::Create(&OutputString);
	FJsonSerializer::Serialize(Result.ToSharedRef(), Writer);

	return UE::ModelContextProtocol::MakeTextResult(OutputString);
}
