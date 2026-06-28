#!/usr/bin/env python3
"""
MCP Stdio Transport Test Suite for UE5 Plugin

Prerequisites:
    - UnrealEditor.exe with ModelContextProtocol plugin built
    - Project with at least one level open

Usage:
    python test_stdio_transport.py --editor-path "C:\\Epic\\UE_Engine\\UE5_8\\UnrealEngine\\Engine\\Binaries\\Win64\\UnrealEditor.exe" --project "C:\\MyProject\\MyProject.uproject"
"""

import subprocess
import json
import sys
import argparse
import time
import os


class MCPStdioClient:
    """Client for MCP stdio transport."""
    
    def __init__(self, editor_path: str, project_path: str):
        self.proc = subprocess.Popen(
            [editor_path, project_path, "-ModelContextProtocolStdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            # On Windows, this prevents the child from inheriting our console
            # which can cause issues with stdio
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        self._next_id = 1
        
    def _get_next_id(self) -> int:
        req_id = self._next_id
        self._next_id += 1
        return req_id
    
    def send_request(self, method: str, params: dict = None, req_id: int = None) -> dict:
        """Send a JSON-RPC request and return the response."""
        if req_id is None:
            req_id = self._get_next_id()
        
        req = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {}
        }
        
        req_str = json.dumps(req, separators=(',', ':'))
        print(f"  -> {req_str}")
        
        self.proc.stdin.write(req_str + "\n")
        self.proc.stdin.flush()
        
        # Read response line
        response_line = self.proc.stdout.readline()
        if not response_line:
            raise ConnectionError("No response from server (process may have exited)")
        
        print(f"  <- {response_line.strip()}")
        
        return json.loads(response_line)
    
    def send_notification(self, method: str, params: dict = None):
        """Send a JSON-RPC notification (no response expected)."""
        req = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        req_str = json.dumps(req, separators=(',', ':'))
        print(f"  -> {req_str}")
        
        self.proc.stdin.write(req_str + "\n")
        self.proc.stdin.flush()
    
    def close(self):
        """Terminate the editor process."""
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()


class MCPTestRunner:
    """Runs the full MCP test suite."""
    
    def __init__(self, client: MCPStdioClient):
        self.client = client
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def _assert(self, condition: bool, message: str):
        if not condition:
            self.failed += 1
            self.errors.append(f"  ✗ {message}")
            raise AssertionError(message)
    
    def _report(self, message: str):
        print(f"  ✓ {message}")
        self.passed += 1
    
    def run_all(self):
        tests = [
            ("initialize", self.test_initialize),
            ("tools/list", self.test_list_tools),
            ("execute_console_command", self.test_console_command),
            ("get_editor_context", self.test_editor_context),
            ("capture_viewport", self.test_capture_viewport),
            ("save_current_level", self.test_save_level),
            ("ListActors", self.test_list_actors),
            ("GetActorDetails", self.test_actor_details),
            ("SpawnActor", self.test_spawn_actor),
            ("DeleteActor", self.test_delete_actor),
            ("SetActorTransform", self.test_set_transform),
            ("error_handling", self.test_error_handling),
        ]
        
        for name, test_fn in tests:
            print(f"\n--- Test: {name} ---")
            try:
                test_fn()
            except Exception as e:
                self.failed += 1
                self.errors.append(f"  ✗ {name}: {str(e)}")
                print(f"  ✗ FAILED: {e}")
    
    def test_initialize(self):
        """Test initialize handshake."""
        resp = self.client.send_request("initialize", {
            "protocolVersion": "2025-11-25",
            "capabilities": {}
        })
        
        self._assert(resp.get("jsonrpc") == "2.0", "jsonrpc version must be 2.0")
        self._assert(resp.get("id") == 1, "response id must match request")
        self._assert("result" in resp, "response must have result")
        
        result = resp["result"]
        self._assert("protocolVersion" in result, "result must have protocolVersion")
        self._assert("capabilities" in result, "result must have capabilities")
        self._assert("sessionId" in resp, "response must have sessionId")
        
        self.session_id = resp["sessionId"]
        self._report(f"initialize passed, session: {self.session_id}")
    
    def test_list_tools(self):
        """Test tools/list returns all expected tools."""
        resp = self.client.send_request("tools/list", {})
        
        self._assert("result" in resp, "response must have result")
        result = resp["result"]
        self._assert("tools" in result, "result must have tools")
        
        tools = result["tools"]
        tool_names = [t["name"] for t in tools]
        
        expected = [
            "execute_console_command",
            "get_editor_context", 
            "capture_viewport",
            "save_current_level",
            "ListActors",
            "GetActorDetails",
            "SpawnActor",
            "DeleteActor",
            "SetActorTransform"
        ]
        
        for name in expected:
            self._assert(name in tool_names, f"tool '{name}' must be in tools/list")
        
        self._report(f"tools/list passed, found {len(tools)} tools")
    
    def test_console_command(self):
        """Test execute_console_command."""
        resp = self.client.send_request("tools/call", {
            "name": "execute_console_command",
            "arguments": {"command": "stat fps"}
        })
        
        self._assert("result" in resp, "response must have result")
        content = resp["result"]["content"]
        self._assert(len(content) > 0, "content must not be empty")
        self._assert(content[0]["type"] == "text", "content type must be text")
        self._assert(len(content[0]["text"]) > 0, "text content must not be empty")
        
        self._report(f"execute_console_command passed, output: {content[0]['text'][:80]}...")
    
    def test_editor_context(self):
        """Test get_editor_context."""
        resp = self.client.send_request("tools/call", {
            "name": "get_editor_context",
            "arguments": {}
        })
        
        self._assert("result" in resp, "response must have result")
        content = resp["result"]["content"]
        self._assert(len(content) > 0, "content must not be empty")
        
        text = content[0]["text"]
        self._assert("World" in text, "output must contain 'World'")
        
        self._report(f"get_editor_context passed: {text[:100]}")
    
    def test_capture_viewport(self):
        """Test capture_viewport."""
        resp = self.client.send_request("tools/call", {
            "name": "capture_viewport",
            "arguments": {}
        })
        
        self._assert("result" in resp, "response must have result")
        content = resp["result"]["content"]
        self._assert(len(content) > 0, "content must not be empty")
        self._assert(content[0]["type"] == "image", "content type must be image")
        self._assert("data" in content[0], "image must have data")
        self._assert(len(content[0]["data"]) > 100, "image data must not be empty")
        
        self._report(f"capture_viewport passed, image size: {len(content[0]['data'])} bytes")
    
    def test_save_level(self):
        """Test save_current_level."""
        resp = self.client.send_request("tools/call", {
            "name": "save_current_level",
            "arguments": {}
        })
        
        self._assert("result" in resp, "response must have result")
        content = resp["result"]["content"]
        self._assert(len(content) > 0, "content must not be empty")
        
        text = content[0]["text"]
        self._assert("saved" in text.lower() or "success" in text.lower(), 
                    "output must indicate success")
        
        self._report(f"save_current_level passed: {text}")
    
    def test_list_actors(self):
        """Test ListActors."""
        resp = self.client.send_request("tools/call", {
            "name": "ListActors",
            "arguments": {}
        })
        
        self._assert("result" in resp, "response must have result")
        content = resp["result"]["content"]
        self._assert(len(content) > 0, "content must not be empty")
        
        result = json.loads(content[0]["text"])
        self._assert("Actors" in result, "result must have 'Actors' key")
        
        self._report(f"ListActors passed, found {len(result['Actors'])} actors")
        # Store first actor name for subsequent tests
        if result["Actors"]:
            self.first_actor = result["Actors"][0]["Name"]
    
    def test_actor_details(self):
        """Test GetActorDetails."""
        if not hasattr(self, 'first_actor'):
            print("  SKIPPED: No actor from ListActors test")
            return
        
        resp = self.client.send_request("tools/call", {
            "name": "GetActorDetails",
            "arguments": {"ActorName": self.first_actor}
        })
        
        self._assert("result" in resp, "response must have result")
        content = resp["result"]["content"]
        result = json.loads(content[0]["text"])
        
        self._assert(result.get("Name") == self.first_actor, 
                    f"Name must match '{self.first_actor}'")
        self._assert("Class" in result, "result must have Class")
        self._assert("Location" in result, "result must have Location")
        
        self._report(f"GetActorDetails passed: {result['Name']} ({result['Class']})")
    
    def test_spawn_actor(self):
        """Test SpawnActor."""
        resp = self.client.send_request("tools/call", {
            "name": "SpawnActor",
            "arguments": {
                "ClassName": "PointLight",
                "Location": {"X": 0, "Y": 0, "Z": 500},
                "Rotation": {"Pitch": 0, "Yaw": 0, "Roll": 0},
                "Scale": {"X": 1, "Y": 1, "Z": 1}
            }
        })
        
        self._assert("result" in resp, "response must have result")
        content = resp["result"]["content"]
        result = json.loads(content[0]["text"])
        
        self._assert(result.get("bSuccess") == True, "SpawnActor must succeed")
        self._assert("ActorName" in result, "result must have ActorName")
        
        self.spawned_actor = result["ActorName"]
        self._report(f"SpawnActor passed: {self.spawned_actor}")
    
    def test_delete_actor(self):
        """Test DeleteActor on the spawned actor."""
        if not hasattr(self, 'spawned_actor'):
            print("  SKIPPED: No actor from SpawnActor test")
            return
        
        resp = self.client.send_request("tools/call", {
            "name": "DeleteActor",
            "arguments": {"ActorName": self.spawned_actor}
        })
        
        self._assert("result" in resp, "response must have result")
        content = resp["result"]["content"]
        result = json.loads(content[0]["text"])
        
        self._assert(result.get("bSuccess") == True, "DeleteActor must succeed")
        
        self._report(f"DeleteActor passed: {self.spawned_actor}")
    
    def test_set_transform(self):
        """Test SetActorTransform on the first actor."""
        if not hasattr(self, 'first_actor'):
            print("  SKIPPED: No actor from ListActors test")
            return
        
        resp = self.client.send_request("tools/call", {
            "name": "SetActorTransform",
            "arguments": {
                "ActorName": self.first_actor,
                "Location": {"X": 100, "Y": 200, "Z": 300},
                "Rotation": {"Pitch": 0, "Yaw": 45, "Roll": 0},
                "Scale": {"X": 2, "Y": 2, "Z": 2}
            }
        })
        
        self._assert("result" in resp, "response must have result")
        content = resp["result"]["content"]
        result = json.loads(content[0]["text"])
        
        self._assert(result.get("bSuccess") == True, "SetActorTransform must succeed")
        
        self._report(f"SetActorTransform passed: moved {self.first_actor} to (100,200,300)")
    
    def test_error_handling(self):
        """Test error handling for non-existent actor."""
        resp = self.client.send_request("tools/call", {
            "name": "DeleteActor",
            "arguments": {"ActorName": "NonExistentActor_12345"}
        })
        
        self._assert("result" in resp, "response must have result")
        content = resp["result"]["content"]
        result = json.loads(content[0]["text"])
        
        self._assert(result.get("bSuccess") == False, 
                    "DeleteActor for non-existent actor must fail")
        self._assert("ErrorMessage" in result, "result must have ErrorMessage")
        self._assert(len(result["ErrorMessage"]) > 0, "ErrorMessage must not be empty")
        
        self._report(f"error_handling passed: '{result['ErrorMessage']}'")
    
    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"  Test Results: {self.passed}/{total} passed")
        if self.errors:
            print(f"\n  Errors:")
            for err in self.errors:
                print(err)
        print(f"{'='*50}")
        return self.failed == 0


def main():
    parser = argparse.ArgumentParser(description="MCP Stdio Transport Test Suite")
    parser.add_argument("--editor-path", required=True, 
                       help="Path to UnrealEditor.exe")
    parser.add_argument("--project", required=True,
                       help="Path to .uproject file")
    parser.add_argument("--timeout", type=int, default=60,
                       help="Timeout for editor startup (seconds)")
    args = parser.parse_args()
    
    print(f"Starting UE5 MCP stdio transport tests...")
    print(f"Editor: {args.editor_path}")
    print(f"Project: {args.project}")
    print(f"Timeout: {args.timeout}s")
    
    client = None
    try:
        client = MCPStdioClient(args.editor_path, args.project)
        
        # Wait for editor to initialize and start MCP stdio
        print(f"\nWaiting for editor to initialize (up to {args.timeout}s)...")
        
        # Try initialize with retry
        start_time = time.time()
        last_error = None
        while time.time() - start_time < args.timeout:
            try:
                resp = client.send_request("initialize", {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {}
                }, req_id=0)
                if "result" in resp:
                    print(f"Editor initialized in {time.time() - start_time:.1f}s")
                    break
            except Exception as e:
                last_error = e
                time.sleep(0.5)
        else:
            print(f"ERROR: Editor did not initialize within {args.timeout}s")
            print(f"Last error: {last_error}")
            return 1
        
        # Run test suite
        runner = MCPTestRunner(client)
        runner.run_all()
        
        if runner.print_summary():
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130
    finally:
        if client:
            print("\nShutting down editor...")
            client.close()


if __name__ == "__main__":
    sys.exit(main())
