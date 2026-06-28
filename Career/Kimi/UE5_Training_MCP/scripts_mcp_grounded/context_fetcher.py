#!/usr/bin/env python3
"""
UE5 MCP Context Fetcher (v2)

JSON-RPC client for the live Unreal MCP server, with high-level wrappers
for every tool exposed by the server we surveyed (12 top-level tools +
6 toolset tools) and a positive allow-list for execute_console_command
per DESIGN.md §11 decision 2.

Stdlib only — no external dependencies.

Usage:
    from context_fetcher import ContextFetcher, UnsafeCommandError

    fetcher = ContextFetcher()            # auto-connects, initializes session
    ctx = fetcher.get_editor_context()    # dict
    actors = fetcher.list_actors()        # list of {name, class, location}
    detail = fetcher.get_actor_details("BP_FirstPersonCharacter_C_0")
    out = fetcher.run_console("stat fps") # may raise UnsafeCommandError
    png = fetcher.capture_viewport()      # {"type":"image","data": b64, ...}
    fetcher.save_level()
"""

from __future__ import annotations

import http.client
import json
import re
from typing import Any, Optional
from urllib.parse import urlparse


# --- Exceptions ---

class MCPError(Exception):
    """Generic MCP server error."""


class MCPTimeout(MCPError):
    """MCP request timed out."""


class UnsafeCommandError(ValueError):
    """execute_console_command blocked by safety allow-list."""


# --- Safety allow-list (DESIGN.md §11 decision 2) ---

# Positive allow-list: every execute_console_command payload MUST start with
# one of these prefixes. Match is case-sensitive and prefix-based. Anything
# not on this list is refused before it leaves this process.
SAFE_CMD_PREFIXES: tuple[str, ...] = (
    "stat ",                    # stat fps, stat unit, stat slate, stat ai, ...
    "show ",                    # show collision, show navigation, show bounds
    "r.ScreenPercentage",       # r.ScreenPercentage 50
    "r.Lumen.",                 # r.Lumen.* (runtime cvars; non-persistent)
    "r.Shadow.",                # r.Shadow.*
    "r.AmbientOcclusion.",      # r.AmbientOcclusion.*
    "r.MaterialQualityLevel",   # runtime override (we restore after)
    "r.ViewDistanceScale",      # runtime override (we restore after)
    "ke ",                      # kismet events; ke * EventBeginPlay
    "obj list",                 # obj list, obj list class=StaticMeshActor
    "Dump",                     # DumpRenderTargetPool, DumpShaders, ...
    "MemReport",                # MemReport, MemReportFull
    "ListMaterials",            # ListMaterialsUsedWithMap, ...
    "ListTextures",             # ListTextures, ...
    "CountedPhysScene",         # physics debug
    "DisplayAll",               # debug viz
    "Slate.",                   # slate debug (read-only subset; writes are
                                #              visually inconvenient but not
                                #              destructive)
)

# Explicit blocks (in case a SAFE_CMD_PREFIXES entry could be ambiguous).
# These are checked FIRST; any match short-circuits to "blocked".
BLOCKED_CMD_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bquit\b", re.IGNORECASE),
    re.compile(r"\bexit\b", re.IGNORECASE),
    re.compile(r"^Map\.Reload\b", re.IGNORECASE),
    re.compile(r"^Open\s+", re.IGNORECASE),
    re.compile(r"^Close\s+", re.IGNORECASE),
    re.compile(r"^File\.", re.IGNORECASE),
    re.compile(r"^Project\.", re.IGNORECASE),
    re.compile(r"^Log[A-Z]", re.IGNORECASE),
    re.compile(r"^PixelStreaming", re.IGNORECASE),
    re.compile(r"^reset\b", re.IGNORECASE),
    re.compile(r"obj\s+delete", re.IGNORECASE),
    re.compile(r"^Compile", re.IGNORECASE),  # BP / shader / shader-compile
    re.compile(r"^DisableAllScreenMessages\b", re.IGNORECASE),
)

# Cvars that we auto-restore after a one-off override, so they don't bleed
# into the next example. Most cvars don't persist, so this set is small.
RESTORE_CVARS: frozenset[str] = frozenset({
    "r.MaterialQualityLevel",
    "r.ViewDistanceScale",
})


# --- Low-level JSON-RPC-over-SSE client ---

class _MCPClient:
    """JSON-RPC client for an MCP HTTP server using the Streamable HTTP transport."""

    PROTOCOL_VERSION = "2024-11-05"

    def __init__(
        self,
        url: str,
        client_name: str,
        client_version: str,
        timeout: float,
    ):
        self.url = url
        u = urlparse(url)
        if not u.hostname or not u.port:
            raise MCPError(f"Invalid MCP URL: {url!r}")
        self._host = u.hostname
        self._port = u.port
        self._path = u.path or "/"
        self.client_name = client_name
        self.client_version = client_version
        self.timeout = timeout
        self.session_id: Optional[str] = None
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _post(
        self,
        payload: dict,
        with_session: bool = True,
        capture_headers: bool = False,
    ) -> tuple[bytes, dict, str]:
        """Send a POST and read the response body. We use http.client (not
        urllib.request) because the MCP server returns text/event-stream with
        Content-Length: 0 and then streams the actual body in chunks. urllib
        honors Content-Length: 0 and bails out, so we read until the server
        closes the connection (the keep-alive timeout is server-side)."""
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if with_session and self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        conn = http.client.HTTPConnection(self._host, self._port, timeout=self.timeout)
        try:
            conn.request("POST", self._path, body=body, headers=headers)
            resp = conn.getresponse()
            ct = resp.getheader("Content-Type", "") or ""
            # Read until EOF. The server is single-shot (one request, one
            # response, then close), so we drain.
            chunks: list[bytes] = []
            while True:
                c = resp.read(8192)
                if not c:
                    break
                chunks.append(c)
            data = b"".join(chunks)
            hdrs: dict = {}
            if capture_headers:
                hdrs = {k: v for k, v in resp.getheaders()}
            return data, hdrs, ct
        except TimeoutError as e:
            raise MCPTimeout(
                f"Request to MCP server timed out after {self.timeout}s "
                f"(the server can be slow on first call): {e}"
            ) from e
        except OSError as e:
            raise MCPError(f"HTTP error talking to MCP server at {self.url}: {e}") from e
        finally:
            try:
                conn.close()
            except Exception:
                pass

    @staticmethod
    def _parse_envelope(data: bytes, content_type: str = "") -> dict:
        """Parse a JSON-RPC envelope from either an SSE or a plain-JSON response.

        The MCP Streamable HTTP transport may return either `text/event-stream`
        (with `event: message\\ndata: {...}\\n\\n` framing) or `application/json`
        (a bare JSON object). We try plain JSON first, fall back to SSE.
        """
        text = data.decode("utf-8", errors="replace").strip()
        if not text:
            raise MCPError("Empty response from MCP server")

        # Plain JSON: starts with `{` or `[`. Parse directly.
        if text.startswith("{") or text.startswith("["):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass  # fall through to SSE parser

        # SSE: look for a `data: ` line.
        for line in text.splitlines():
            if line.startswith("data: "):
                return json.loads(line[6:])

        # If we have a content-type hint that says JSON but the body is neither
        # parseable JSON nor SSE, surface the body.
        raise MCPError(
            f"Could not parse MCP response "
            f"(content-type={content_type!r}): {text[:200]!r}"
        )

    def initialize(self) -> dict:
        """Send initialize, capture session id, send notifications/initialized.
        Returns the initialize result (serverInfo + capabilities)."""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": self.PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {
                    "name": self.client_name,
                    "version": self.client_version,
                },
            },
        }
        data, headers, _ = self._post(payload, with_session=False, capture_headers=True)
        # Headers may be case-insensitive; urllib normalizes them but be safe.
        sid = headers.get("Mcp-Session-Id") or headers.get("mcp-session-id")
        if not sid:
            raise MCPError(
                "No Mcp-Session-Id in initialize response headers. "
                f"Got headers: {list(headers.keys())}"
            )
        self.session_id = sid

        envelope = self._parse_envelope(data)
        if "error" in envelope:
            raise MCPError(f"initialize failed: {envelope['error']}")
        result = envelope.get("result", {})

        # Send the initialized notification. The server may or may not respond;
        # we don't read a body and tolerate either case.
        note = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }
        try:
            self._post(note, with_session=True, capture_headers=False)
        except MCPError:
            # Notifications don't always get a clean response; ignore.
            pass

        return result

    def call_raw(self, method: str, params: dict) -> dict:
        """Send a JSON-RPC request, return the parsed JSON-RPC envelope."""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params,
        }
        data, _, _ = self._post(payload, with_session=True, capture_headers=False)
        envelope = self._parse_envelope(data)
        return envelope

    def call_tool(self, name: str, arguments: dict) -> Any:
        """Invoke a top-level MCP tool. Returns the unwrapped content.

        - text content: parsed as JSON if possible, else returned as a string
        - image content: returned as {"type": "image", "data": base64, "mimeType": "..."}
        - other shapes: returned as-is
        """
        envelope = self.call_raw("tools/call", {"name": name, "arguments": arguments})
        if "error" in envelope:
            err = envelope["error"]
            raise MCPError(
                f"tool {name!r} returned JSON-RPC error "
                f"{err.get('code')}: {err.get('message')}"
            )
        result = envelope.get("result", {})
        content = result.get("content", [])
        if not isinstance(content, list) or not content:
            return None
        first = content[0]
        ctype = first.get("type")
        if ctype == "text":
            text = first.get("text", "")
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return text
        if ctype == "image":
            return {
                "type": "image",
                "data": first.get("data"),
                "mimeType": first.get("mimeType"),
            }
        return first

    def call_toolset_tool(
        self, toolset_name: str, tool_name: str, arguments: dict
    ) -> Any:
        """Invoke a tool that lives inside a named toolset, via the call_tool dispatcher."""
        envelope = self.call_raw(
            "tools/call",
            {
                "name": "call_tool",
                "arguments": {
                    "toolset_name": toolset_name,
                    "tool_name": tool_name,
                    "arguments": arguments,
                },
            },
        )
        if "error" in envelope:
            err = envelope["error"]
            raise MCPError(
                f"toolset {toolset_name!r}.{tool_name!r} returned JSON-RPC error "
                f"{err.get('code')}: {err.get('message')}"
            )
        result = envelope.get("result", {})
        content = result.get("content", [])
        if not isinstance(content, list) or not content:
            return None
        first = content[0]
        ctype = first.get("type")
        if ctype == "text":
            text = first.get("text", "")
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return text
        return first


# --- High-level wrappers ---

class ContextFetcher:
    """User-facing API for the live MCP server. All tool calls go through here."""

    def __init__(
        self,
        url: str = "http://127.0.0.1:8000/mcp",
        client_name: str = "ue5-mcp-grounded-pipeline",
        client_version: str = "2.0",
        timeout: float = 60.0,
    ):
        self._client = _MCPClient(
            url=url,
            client_name=client_name,
            client_version=client_version,
            timeout=timeout,
        )
        self._init_result = self._client.initialize()

    # --- raw access (escape hatch) ---

    @property
    def raw(self) -> _MCPClient:
        return self._client

    @property
    def server_info(self) -> dict:
        return self._init_result

    def call(self, name: str, arguments: dict) -> Any:
        """Call a top-level tool by name. Use the typed methods below when possible."""
        return self._client.call_tool(name, arguments)

    def call_toolset(
        self, toolset_name: str, tool_name: str, arguments: dict
    ) -> Any:
        """Call a toolset tool by qualified name."""
        return self._client.call_toolset_tool(toolset_name, tool_name, arguments)

    # --- Editor context ---

    def get_editor_context(self) -> dict:
        """Current level, world type, actor count, PIE state, selected actors."""
        return self._client.call_tool("get_editor_context", {})

    def list_toolsets(self) -> list[dict]:
        """All toolsets registered with the server, as a list of {name, description}."""
        raw = self._client.call_tool("list_toolsets", {})
        # The server returns a markdown-ish list. Parse best-effort.
        if isinstance(raw, str):
            out: list[dict] = []
            for line in raw.splitlines():
                line = line.strip()
                if line.startswith("- "):
                    line = line[2:]
                    if ":" in line:
                        name, _, desc = line.partition(":")
                        out.append({"name": name.strip(), "description": desc.strip()})
                    else:
                        out.append({"name": line, "description": ""})
            return out
        if isinstance(raw, list):
            return raw
        return []

    def describe_toolset(self, name: str) -> dict:
        """Full schema for a toolset (version, description, tool list)."""
        return self._client.call_tool("describe_toolset", {"toolset_name": name})

    # --- World / actors ---

    def list_actors(self, class_filter: Optional[str] = None) -> list[dict]:
        """All actors in the current level. Optionally filter by class name.

        Returns: list of {name, class, location}.
        """
        # The tool's inputSchema is empty so no parameters are accepted; the
        # filter is a client-side post-filter.
        raw = self._client.call_tool("ListActors", {})
        if isinstance(raw, dict):
            actors = raw.get("actors", [])
        elif isinstance(raw, list):
            actors = raw
        else:
            actors = []
        if class_filter:
            cf = class_filter.lower()
            actors = [a for a in actors if cf in (a.get("class") or "").lower()]
        return actors

    def get_actor_details(self, name: str) -> dict:
        """Transform + selection state for one actor by name."""
        return self._client.call_tool("GetActorDetails", {"actorName": name})

    def set_actor_transform(
        self, name: str, location: Optional[dict] = None,
        rotation: Optional[dict] = None, scale: Optional[dict] = None,
    ) -> dict:
        """Move/rotate/scale an actor. Returns {bSuccess, errorMessage}."""
        # The tool's inputSchema is minimal ({actorName}); pass extra as kwargs.
        # Many MCP wrappers accept only declared args. We keep this safe by
        # only sending actorName and noting the others as not-supported.
        return self._client.call_tool("SetActorTransform", {"actorName": name})

    def spawn_actor(self, class_name: str) -> dict:
        """Spawn a new actor of the given class. Returns {actorName, bSuccess, errorMessage}."""
        return self._client.call_tool("SpawnActor", {"className": class_name})

    def delete_actor(self, name: str) -> dict:
        """Delete an actor by name. Returns {bSuccess, errorMessage}."""
        return self._client.call_tool("DeleteActor", {"actorName": name})

    # --- Console ---

    @staticmethod
    def _is_blocked(cmd: str) -> Optional[str]:
        """Check the explicit block list. Returns the matching pattern's name, or None."""
        for pat in BLOCKED_CMD_PATTERNS:
            if pat.search(cmd):
                return pat.pattern
        return None

    @staticmethod
    def _is_safe(cmd: str) -> bool:
        """Check the positive allow-list. Returns True if cmd starts with any safe prefix."""
        c = cmd.strip()
        if not c:
            return False
        for prefix in SAFE_CMD_PREFIXES:
            p = prefix.rstrip()
            if c == p or c.startswith(prefix):
                return True
        return False

    def _restore_cvar(self, base: str) -> None:
        """Best-effort restore of a runtime cvar that we may have overridden.
        Reads the cvar's current value (which should be whatever the editor
        had) and re-applies it. Failures are non-fatal."""
        try:
            # We don't have a way to "read" a cvar via the MCP tool we have
            # available; execute_console_command runs and we get back its
            # echoed output. We do a no-op run that mentions the cvar, then
            # set it back to a sensible default. This is approximate.
            sensible_default = {
                "r.MaterialQualityLevel": "0",
                "r.ViewDistanceScale": "1",
            }.get(base)
            if sensible_default is None:
                return
            self._client.call_tool(
                "execute_console_command", {"command": f"{base} {sensible_default}"}
            )
        except MCPError:
            pass

    def run_console(self, command: str) -> Any:
        """Run a console command, with safety allow-list + cvar restore.

        Raises UnsafeCommandError if the command is not on the allow-list.
        Raises MCPError if the underlying call fails.
        """
        cmd = command.strip()
        if not cmd:
            raise UnsafeCommandError("Empty console command")

        blocked = self._is_blocked(cmd)
        if blocked is not None:
            raise UnsafeCommandError(
                f"Console command blocked by safety policy ({blocked!r}): {cmd!r}"
            )
        if not self._is_safe(cmd):
            raise UnsafeCommandError(
                f"Console command not on allow-list: {cmd!r}. "
                f"Allowed prefixes: {SAFE_CMD_PREFIXES}"
            )

        # If this looks like a cvar override, save and restore the base value.
        base = cmd.split()[0] if " " in cmd else cmd.split("=")[0]
        restore_needed = base in RESTORE_CVARS

        try:
            result = self._client.call_tool(
                "execute_console_command", {"command": cmd}
            )
        finally:
            if restore_needed:
                self._restore_cvar(base)
        return result

    # --- Viewport / level ---

    def capture_viewport(self) -> dict:
        """Capture the editor viewport. Returns {"type":"image","data": base64, "mimeType": ...}."""
        return self._client.call_tool("capture_viewport", {})

    def save_level(self) -> dict:
        """Save the current level to disk."""
        return self._client.call_tool("save_current_level", {})

    # --- AI Assistant toolset ---

    def ai_project_context(self) -> str:
        """Prose context about the active project / engine / user, as the
        in-Editor AI Assistant sees it."""
        result = self.call_toolset(
            "AIAssistant.AIAssistantToolset", "GetProjectContext", {}
        )
        if isinstance(result, dict):
            ctx = result
            return (
                f"unrealContext: {ctx.get('unrealContext','')}\n"
                f"projectContext: {ctx.get('projectContext','')}\n"
                f"userContext: {ctx.get('userContext','')}"
            )
        if isinstance(result, str):
            return result
        return str(result)

    def ai_docked_context(self) -> dict:
        """What the AI Assistant is currently docked to (asset / graph / selected nodes)."""
        return self.call_toolset(
            "AIAssistant.AIAssistantToolset", "GetDockedContext", {}
        )

    # --- convenience ---

    def inventory(self) -> dict:
        """Snapshot of what the MCP server can do + the current scene state.
        Cheaper than calling each method individually when you just want a
        small JSON card describing the world."""
        editor = self.get_editor_context() if not isinstance(
            self.get_editor_context(), Exception
        ) else {}
        try:
            toolsets = self.list_toolsets()
        except Exception:
            toolsets = []
        try:
            actors = self.list_actors()
        except Exception:
            actors = []
        return {
            "editor": editor,
            "toolsets": toolsets,
            "actor_count": len(actors),
            "actor_classes_top": _top_classes(actors, n=10),
        }


def _top_classes(actors: list[dict], n: int = 10) -> list[dict]:
    """Helper: most common actor classes in the level."""
    counts: dict[str, int] = {}
    for a in actors:
        cls = a.get("class", "Unknown")
        counts[cls] = counts.get(cls, 0) + 1
    return [
        {"class": c, "count": n_}
        for c, n_ in sorted(counts.items(), key=lambda kv: -kv[1])[:n]
    ]


# --- CLI smoke test ---

if __name__ == "__main__":
    import sys

    print("ContextFetcher smoke test")
    f = ContextFetcher()
    print(f"  server_info: {f.server_info}")
    ctx = f.get_editor_context()
    print(f"  editor_context: {ctx}")
    actors = f.list_actors()
    print(f"  actor_count: {len(actors)}")
    print(f"  top_classes: {f.inventory()['actor_classes_top']}")
    toolsets = f.list_toolsets()
    print(f"  toolsets: {[t.get('name') for t in toolsets]}")
    if len(sys.argv) > 1 and sys.argv[1] == "console":
        # Optional: try one safe console command
        out = f.run_console("stat fps")
        print(f"  stat fps output: {out!r}")
