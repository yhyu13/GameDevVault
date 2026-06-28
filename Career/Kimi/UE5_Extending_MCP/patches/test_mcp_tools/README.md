# MCP Test Suite for UE5 Plugin

This directory contains test prompts, expected results, and code samples for validating the UE5 MCP plugin across all 6 phases.

## Quick Start

### 1. Start the MCP Server (HTTP)

```bash
# Launch the Unreal Editor with HTTP server auto-start
UnrealEditor.exe MyProject.uproject -ModelContextProtocolServer
```

Or manually in the console:
```
ModelContextProtocol.StartServer
```

### 2. Start the MCP Server (stdio)

```bash
# Launch the Unreal Editor with stdio transport
UnrealEditor.exe MyProject.uproject -ModelContextProtocolStdio
```

## Test Matrix

| Tool | Transport | Test File | Phase |
|------|-----------|-----------|-------|
| `initialize` | HTTP / stdio | `test_initialize.py` | Core |
| `tools/list` | HTTP / stdio | `test_tools_list.py` | Core |
| `execute_console_command` | HTTP / stdio | `test_console_command.py` | Phase 1 |
| `get_editor_context` | HTTP / stdio | `test_editor_context.py` | Phase 2 |
| `capture_viewport` | HTTP / stdio | `test_capture_viewport.py` | Phase 3 |
| `save_current_level` | HTTP / stdio | `test_save_level.py` | Phase 6 |
| `ListActors` | HTTP / stdio | `test_list_actors.py` | Phase 6 |
| `GetActorDetails` | HTTP / stdio | `test_actor_details.py` | Phase 6 |
| `SpawnActor` | HTTP / stdio | `test_spawn_actor.py` | Phase 6 |
| `DeleteActor` | HTTP / stdio | `test_delete_actor.py` | Phase 6 |
| `SetActorTransform` | HTTP / stdio | `test_set_transform.py` | Phase 6 |
| Progress notifications | HTTP / stdio | `test_progress.py` | Phase 4 |
| `notifications/cancelled` | stdio | `test_cancel.py` | Phase 4 |

---

## HTTP Transport Tests (curl)

### Test 1: Initialize Session

```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-11-25",
      "capabilities": {}
    }
  }'
```

**Expected Response (SSE):**
```
event: message

data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-11-25","capabilities":{"tools":{"listChanged":true},"resources":{}}},"sessionId":"a1b2c3d4e5f6..."}
```

---

### Test 2: List Tools

**Prompt:** "What tools are available?"

**Request:**
```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID_FROM_INIT>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "execute_console_command",
        "description": "Execute a console command..."
      },
      {
        "name": "get_editor_context",
        "description": "Get the current editor context..."
      },
      {
        "name": "capture_viewport",
        "description": "Capture the current viewport..."
      },
      {
        "name": "save_current_level",
        "description": "Save the current level to disk"
      },
      {
        "name": "ListActors",
        "description": "List all actors in the current editor level..."
      },
      {
        "name": "GetActorDetails",
        "description": "Get detailed information about a specific actor..."
      },
      {
        "name": "SpawnActor",
        "description": "Spawn an actor of the specified class..."
      },
      {
        "name": "DeleteActor",
        "description": "Delete an actor by name from the current level..."
      },
      {
        "name": "SetActorTransform",
        "description": "Set the transform of an actor by name..."
      }
    ]
  }
}
```

---

### Test 3: Execute Console Command (Phase 1)

**Prompt:** "Show me the current engine version"

**Request:**
```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "execute_console_command",
      "arguments": {
        "command": "version"
      }
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "LogConsoleResponse: Display: \nLogConsoleResponse: Display: UE5 Main...\nLogConsoleResponse: Display: CL-0\nLogConsoleResponse: Display: Built from main branch..."
      }
    ]
  }
}
```

---

### Test 4: Get Editor Context (Phase 2)

**Prompt:** "What is the current editor state?"

**Request:**
```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "get_editor_context",
      "arguments": {}
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "World: MyProject_C_1\nLevel: PersistentLevel\nSelected Actors: 2\n  - Cube (StaticMeshActor)\n  - LightSource (DirectionalLight)"
      }
    ]
  }
}
```

---

### Test 5: Capture Viewport (Phase 3)

**Prompt:** "Show me the current viewport"

**Request:**
```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "tools/call",
    "params": {
      "name": "capture_viewport",
      "arguments": {}
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "content": [
      {
        "type": "image",
        "data": "/9j/4AAQSkZJRgABAQEASABIAAD...",
        "mimeType": "image/jpeg"
      }
    ]
  }
}
```

---

### Test 6: Save Current Level (Phase 6)

**Prompt:** "Save the current level"

**Request:**
```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "save_current_level",
      "arguments": {}
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Level saved successfully"
      }
    ]
  }
}
```

---

### Test 7: List Actors (Phase 6)

**Prompt:** "List all actors in the level"

**Request:**
```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 7,
    "method": "tools/call",
    "params": {
      "name": "ListActors",
      "arguments": {}
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"Actors\":[{\"Name\":\"Cube\",\"Class\":\"StaticMeshActor\",\"Location\":{\"X\":0.0,\"Y\":0.0,\"Z\":0.0}},{\"Name\":\"LightSource\",\"Class\":\"DirectionalLight\",\"Location\":{\"X\":100.0,\"Y\":200.0,\"Z\":300.0}}]}"
      }
    ]
  }
}
```

---

### Test 8: Get Actor Details (Phase 6)

**Prompt:** "What are the details of the Cube actor?"

**Request:**
```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 8,
    "method": "tools/call",
    "params": {
      "name": "GetActorDetails",
      "arguments": {
        "ActorName": "Cube"
      }
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"Name\":\"Cube\",\"Class\":\"StaticMeshActor\",\"Location\":{\"X\":0.0,\"Y\":0.0,\"Z\":0.0},\"Rotation\":{\"Pitch\":0.0,\"Yaw\":0.0,\"Roll\":0.0},\"Scale\":{\"X\":1.0,\"Y\":1.0,\"Z\":1.0},\"bIsSelected\":true}"
      }
    ]
  }
}
```

---

### Test 9: Spawn Actor (Phase 6)

**Prompt:** "Spawn a PointLight at (0, 0, 500)"

**Request:**
```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 9,
    "method": "tools/call",
    "params": {
      "name": "SpawnActor",
      "arguments": {
        "ClassName": "PointLight",
        "Location": {"X": 0.0, "Y": 0.0, "Z": 500.0},
        "Rotation": {"Pitch": 0.0, "Yaw": 0.0, "Roll": 0.0},
        "Scale": {"X": 1.0, "Y": 1.0, "Z": 1.0}
      }
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"ActorName\":\"PointLight_1\",\"bSuccess\":true,\"ErrorMessage\":\"\"}"
      }
    ]
  }
}
```

---

### Test 10: Delete Actor (Phase 6)

**Prompt:** "Delete the PointLight actor"

**Request:**
```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 10,
    "method": "tools/call",
    "params": {
      "name": "DeleteActor",
      "arguments": {
        "ActorName": "PointLight_1"
      }
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"bSuccess\":true,\"ErrorMessage\":\"\"}"
      }
    ]
  }
}
```

---

### Test 11: Set Actor Transform (Phase 6)

**Prompt:** "Move the Cube to (100, 200, 300) and scale it by 2"

**Request:**
```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 11,
    "method": "tools/call",
    "params": {
      "name": "SetActorTransform",
      "arguments": {
        "ActorName": "Cube",
        "Location": {"X": 100.0, "Y": 200.0, "Z": 300.0},
        "Rotation": {"Pitch": 0.0, "Yaw": 0.0, "Roll": 0.0},
        "Scale": {"X": 2.0, "Y": 2.0, "Z": 2.0}
      }
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 11,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"bSuccess\":true,\"ErrorMessage\":\"\"}"
      }
    ]
  }
}
```

---

### Test 12: Error Case - Delete Non-Existent Actor

**Prompt:** "Delete a non-existent actor"

**Request:**
```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 12,
    "method": "tools/call",
    "params": {
      "name": "DeleteActor",
      "arguments": {
        "ActorName": "NonExistentActor"
      }
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 12,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"bSuccess\":false,\"ErrorMessage\":\"Actor not found: NonExistentActor\"}"
      }
    ]
  }
}
```

---

## Stdio Transport Tests (Python)

### Setup

```bash
# Launch UE5 with stdio transport
UnrealEditor.exe MyProject.uproject -ModelContextProtocolStdio
```

### Python Test Script

See `test_stdio_transport.py` for a complete Python test harness.

```python
import subprocess
import json
import sys

# Launch UE5 with stdio transport
proc = subprocess.Popen(
    ["UnrealEditor.exe", "MyProject.uproject", "-ModelContextProtocolStdio"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

def send_request(req):
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()
    response = proc.stdout.readline()
    return json.loads(response)

# Test 1: Initialize
def test_initialize():
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-11-25",
            "capabilities": {}
        }
    }
    resp = send_request(req)
    assert resp["jsonrpc"] == "2.0"
    assert resp["id"] == 1
    assert "result" in resp
    assert "sessionId" in resp
    print("✓ initialize passed")
    return resp["result"]["sessionId"]

# Test 2: List Tools
def test_list_tools():
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    resp = send_request(req)
    assert resp["id"] == 2
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "execute_console_command" in tool_names
    assert "get_editor_context" in tool_names
    assert "capture_viewport" in tool_names
    assert "save_current_level" in tool_names
    assert "ListActors" in tool_names
    assert "GetActorDetails" in tool_names
    assert "SpawnActor" in tool_names
    assert "DeleteActor" in tool_names
    assert "SetActorTransform" in tool_names
    print("✓ tools/list passed")
    print(f"  Found {len(tools)} tools")

# Test 3: Execute Console Command
def test_console_command():
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "execute_console_command",
            "arguments": {"command": "stat fps"}
        }
    }
    resp = send_request(req)
    assert resp["id"] == 3
    content = resp["result"]["content"]
    assert len(content) > 0
    assert content[0]["type"] == "text"
    print("✓ execute_console_command passed")
    print(f"  Output: {content[0]['text'][:100]}...")

# Test 4: Get Editor Context
def test_editor_context():
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_editor_context",
            "arguments": {}
        }
    }
    resp = send_request(req)
    assert resp["id"] == 4
    content = resp["result"]["content"]
    assert "World" in content[0]["text"]
    print("✓ get_editor_context passed")

# Test 5: List Actors
def test_list_actors():
    req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "ListActors",
            "arguments": {}
        }
    }
    resp = send_request(req)
    assert resp["id"] == 5
    content = resp["result"]["content"]
    result = json.loads(content[0]["text"])
    assert "Actors" in result
    print("✓ ListActors passed")
    print(f"  Found {len(result['Actors'])} actors")

# Test 6: Spawn + Delete Actor
def test_spawn_and_delete():
    # Spawn
    req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "SpawnActor",
            "arguments": {
                "ClassName": "PointLight",
                "Location": {"X": 0, "Y": 0, "Z": 500},
                "Rotation": {"Pitch": 0, "Yaw": 0, "Roll": 0},
                "Scale": {"X": 1, "Y": 1, "Z": 1}
            }
        }
    }
    resp = send_request(req)
    result = json.loads(resp["result"]["content"][0]["text"])
    assert result["bSuccess"] == True
    actor_name = result["ActorName"]
    print(f"✓ SpawnActor passed: {actor_name}")
    
    # Delete
    req = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "DeleteActor",
            "arguments": {"ActorName": actor_name}
        }
    }
    resp = send_request(req)
    result = json.loads(resp["result"]["content"][0]["text"])
    assert result["bSuccess"] == True
    print(f"✓ DeleteActor passed: {actor_name}")

# Run all tests
if __name__ == "__main__":
    try:
        test_initialize()
        test_list_tools()
        test_console_command()
        test_editor_context()
        test_list_actors()
        test_spawn_and_delete()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    finally:
        proc.terminate()
```

---

## Progress Reporting Test (Phase 4)

Progress notifications are sent via SSE during long-running operations. The built-in tools are fast, so progress is only visible if:

1. The tool manually reports progress via `OnProgress` callback
2. The heartbeat interval fires (default 5s)

To test progress notifications manually, you can use a slow command:

```bash
curl -N -X POST http://localhost:9877/jsonrpc \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Mcp-Session-Id: <SESSION_ID>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 13,
    "method": "tools/call",
    "params": {
      "name": "execute_console_command",
      "arguments": {
        "command": "obj list class=StaticMesh"
      }
    }
  }'
```

**Expected Progress Notification (SSE):**
```
event: message

data: {"jsonrpc":"2.0","method":"notifications/progress","params":{"progressToken":"13","progress":50,"total":100}}
```

The progress notification is sent as an intermediate SSE message before the final result.

---

## Cancellation Test (Phase 4)

To test cancellation, you need a tool that takes long enough to execute. For stdio:

```python
import subprocess
import json
import threading
import time

proc = subprocess.Popen(
    ["UnrealEditor.exe", "MyProject.uproject", "-ModelContextProtocolStdio"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
    bufsize=1
)

def send_request(req):
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()

# Send a long-running command (e.g., a slow console command)
send_request({
    "jsonrpc": "2.0",
    "id": 14,
    "method": "tools/call",
    "params": {
        "name": "execute_console_command",
        "arguments": {"command": "stat unit"},
        "meta": {"progressToken": "14"}
    }
})

# Wait a bit, then send cancellation
time.sleep(1)
send_request({
    "jsonrpc": "2.0",
    "id": 15,
    "method": "notifications/cancelled",
    "params": {
        "requestId": 14,
        "reason": "User cancelled"
    }
})
```

**Expected:** The original request (id=14) may return an error or be cancelled depending on whether the tool supports cancellation. The built-in tools do not support cancellation yet, so the request will likely complete normally.

---

## Validation Checklist

- [ ] HTTP server starts on port 9877
- [ ] Stdio transport starts with `-ModelContextProtocolStdio`
- [ ] `initialize` returns session ID
- [ ] `tools/list` returns all 9 tools
- [ ] `execute_console_command` returns console output
- [ ] `get_editor_context` returns world/level/selection info
- [ ] `capture_viewport` returns base64 image
- [ ] `save_current_level` saves level and returns success
- [ ] `ListActors` returns actor list
- [ ] `GetActorDetails` returns actor details by name
- [ ] `SpawnActor` creates actor and returns name
- [ ] `DeleteActor` removes actor and returns success
- [ ] `SetActorTransform` moves/scales actor and returns success
- [ ] Error cases return structured error messages
- [ ] Progress notifications sent during long operations (if applicable)
- [ ] Stdio transport produces plain JSON (no SSE wrapper)
