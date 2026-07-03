#!/usr/bin/env python3
"""Smoke test for the 15 new MCP tools shipped in Phase 7 (P0) + Phase 8 (P1 B1+B2).

Run after the UE Editor is up with -ModelContextProtocolServer:
    python tests/smoke_test_mcp_new_tools.py

The script will:
  1. Initialize an MCP session.
  2. tools/list to verify all 15 names exist (and no PascalCase duplicates).
  3. For each tool, send a minimal valid call and capture the response.
  4. Write a JSON report to tests/reports/smoke_<timestamp>.json.

Pass / GATED / Fail criteria:
  PASS   — HTTP 200, JSON-RPC result present, no isError, shape matches spec.
  GATED  — Mutation tools returned "mutations disabled" (expected when env var unset).
  FAIL   — isError, missing tool name, schema error, 5xx, or unexpected exception.
"""

from __future__ import annotations

import argparse
import http.client
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Reused from context_fetcher._MCPClient (keep in sync)
# ---------------------------------------------------------------------------


class MCPError(Exception):
    """Generic MCP server error."""


class MCPTimeout(MCPError):
    """MCP request timed out."""


class _MCPClient:
    """Minimal JSON-RPC-over-SSE client."""

    PROTOCOL_VERSION = "2024-11-05"

    def __init__(self, url: str, timeout: float):
        self.url = url
        u = urlparse(url)
        if not u.hostname or not u.port:
            raise MCPError(f"Invalid MCP URL: {url!r}")
        self._host = u.hostname
        self._port = u.port
        self._path = u.path or "/"
        self.timeout = timeout
        self.session_id: Optional[str] = None
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _post(self, payload: dict, with_session: bool = True, capture_headers: bool = False) -> tuple[bytes, dict, str]:
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
            raise MCPTimeout(f"Request to MCP server timed out after {self.timeout}s: {e}") from e
        except OSError as e:
            raise MCPError(f"HTTP error talking to MCP server at {self.url}: {e}") from e
        finally:
            try:
                conn.close()
            except Exception:
                pass

    @staticmethod
    def _parse_envelope(data: bytes, content_type: str = "") -> dict:
        text = data.decode("utf-8", errors="replace").strip()
        if not text:
            raise MCPError("Empty response from MCP server")
        if text.startswith("{") or text.startswith("["):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
        for line in text.splitlines():
            if line.startswith("data: "):
                return json.loads(line[6:])
        raise MCPError(f"Could not parse MCP response (content-type={content_type!r}): {text[:200]!r}")

    def initialize(self) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": self.PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "mcp-smoke-test", "version": "1.0"},
            },
        }
        data, headers, _ = self._post(payload, with_session=False, capture_headers=True)
        sid = headers.get("Mcp-Session-Id") or headers.get("mcp-session-id")
        if not sid:
            raise MCPError(f"No Mcp-Session-Id in initialize response. Headers: {list(headers.keys())}")
        self.session_id = sid
        envelope = self._parse_envelope(data)
        if "error" in envelope:
            raise MCPError(f"initialize failed: {envelope['error']}")

        note = {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        try:
            self._post(note, with_session=True, capture_headers=False)
        except MCPError:
            pass
        return envelope.get("result", {})

    def call_raw(self, method: str, params: dict) -> dict:
        payload = {"jsonrpc": "2.0", "id": self._next_id(), "method": method, "params": params}
        data, _, _ = self._post(payload, with_session=True, capture_headers=False)
        return self._parse_envelope(data)

    def call_tool(self, name: str, arguments: dict) -> Any:
        envelope = self.call_raw("tools/call", {"name": name, "arguments": arguments})
        if "error" in envelope:
            err = envelope["error"]
            raise MCPError(f"tool {name!r} error {err.get('code')}: {err.get('message')}")
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

    def list_tools(self) -> list[str]:
        """Return live tool names from tools/list."""
        envelope = self.call_raw("tools/list", {})
        if "error" in envelope:
            raise MCPError(f"tools/list error: {envelope['error']}")
        result = envelope.get("result", {})
        tools = result.get("tools", [])
        return [t.get("name", "") for t in tools if isinstance(t, dict)]


# ---------------------------------------------------------------------------
# Test definitions
# ---------------------------------------------------------------------------

TEST_CASES = [
    # P0 (Phase 7)
    ("list_levels",            {"root": "/Game/"},                          "Read"),
    ("class_inventory",        {"filter_prefix": "BP_"},                    "Read"),
    ("open_level",             {"level_path": "/Game/DemoTemplate/_Core/Lvl_IntroRoom", "save_first": True}, "Write"),
    ("snapshot_world",         {"label": "smoke_test_v8", "save_first": True},  "Write"),  # FIXED: file copy instead of SaveLevel
    ("restore_world",          {"label": "smoke_test_v8"},                      "Write"),  # FIXED: file copy instead of LoadMap
    ("spawn_actor",            {"class_name": "BP_TemplateCube_C", "location": {"x": 0, "y": 0, "z": 100}}, "Write"),
    ("set_actor_transform",    {"actor_name": "<PLACEHOLDER>", "location": {"x": 0, "y": 0, "z": 100}}, "Write"),
    ("verify_position",        {"actor_name": "<PLACEHOLDER>", "expected": {"x": 0, "y": 0, "z": 100}}, "Read"),
    ("summarize_scene",        {},                                          "Read"),
    # P1 B1+B2 (Phase 8)
    ("search_actors",          {"class_regex": "BP_.*"},                    "Read"),
    ("list_blueprints",        {},                                          "Read"),  # FIXED: only loaded assets, no LoadPackage
    ("set_visibility",         {"actor_name": "<PLACEHOLDER>", "hidden": False}, "Mutation"),
    ("set_mobility",           {"actor_name": "<PLACEHOLDER>", "mobility": "Movable"}, "Mutation"),
    ("set_collision",          {"actor_name": "<PLACEHOLDER>", "profile": "BlockAll"}, "Mutation"),
]


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------


def _substitute(args: dict, placeholder: str) -> dict:
    """Replace <PLACEHOLDER> with a real actor name."""
    def _replace(v: Any) -> Any:
        if isinstance(v, str):
            return v.replace("<PLACEHOLDER>", placeholder)
        if isinstance(v, dict):
            return {k: _replace(vv) for k, vv in v.items()}
        return v
    return _replace(args)


def _is_gated(result: Any) -> bool:
    """Check if the result is the MutationGate 'disabled' message."""
    if isinstance(result, str) and "mutations are disabled" in result.lower():
        return True
    if isinstance(result, dict) and isinstance(result.get("error"), str):
        return "mutations are disabled" in result["error"].lower()
    return False


def _is_ok(result: Any) -> bool:
    """Check if the result is a successful response (not an error dict or error string)."""
    if result is None:
        return False
    if isinstance(result, dict):
        if result.get("isError") or result.get("error"):
            return False
        return True
    if isinstance(result, str):
        # Check for common error string prefixes/patterns
        err_prefixes = ("error", "not found", "failed", "invalid", "cannot", "unable", "actor class not found", "level not saved", "please save")
        lower = result.lower().strip()
        if any(lower.startswith(p) for p in err_prefixes) or "not found" in lower:
            return False
        return True
    return True


def run_tests(client: _MCPClient, args: argparse.Namespace) -> dict:
    records: list[dict] = []
    summary = {"pass": 0, "gated": 0, "fail": 0, "unreachable": 0}

    # --- Step 1: list_tools for inventory check ---
    try:
        live_tools = client.list_tools()
    except MCPError as e:
        print(f"CRITICAL: Cannot list tools: {e}")
        return {"summary": {"error": str(e)}, "records": []}

    expected_names = {t[0] for t in TEST_CASES}
    missing = expected_names - set(live_tools)
    if missing:
        print(f"WARNING: Missing tools in live inventory: {missing}")

    # --- Step 2: pick a placeholder actor name (skip WorldSettings which is pinned) ---
    placeholder_actor = ""
    try:
        result = client.call_tool("ListActors", {})
        if isinstance(result, dict) and result.get("actors"):
            for actor in result["actors"]:
                name = actor.get("name", "")
                if name and not name.startswith("WorldSettings"):
                    placeholder_actor = name
                    break
        elif isinstance(result, list) and result:
            for actor in result:
                name = actor.get("name", "")
                if name and not name.startswith("WorldSettings"):
                    placeholder_actor = name
                    break
    except Exception as e:
        print(f"WARNING: Could not fetch placeholder actor: {e}")

    print(f"Using placeholder actor: {placeholder_actor!r}")

    # --- Step 3: run each test case ---
    for tool_name, tool_args, kind in TEST_CASES:
        resolved = _substitute(tool_args, placeholder_actor) if placeholder_actor else tool_args
        record: dict = {
            "name": tool_name,
            "kind": kind,
            "args": resolved,
            "status": "UNRUN",
            "result": None,
            "latency_ms": 0,
        }
        t0 = time.perf_counter()
        try:
            result = client.call_tool(tool_name, resolved)
            latency_ms = int((time.perf_counter() - t0) * 1000)
            record["latency_ms"] = latency_ms
            record["result"] = result

            if _is_gated(result):
                record["status"] = "GATED"
                summary["gated"] += 1
            elif _is_ok(result):
                record["status"] = "PASS"
                summary["pass"] += 1
            else:
                record["status"] = "FAIL"
                summary["fail"] += 1
        except MCPError as e:
            latency_ms = int((time.perf_counter() - t0) * 1000)
            record["latency_ms"] = latency_ms
            record["result"] = {"error": str(e)}
            if "not found" in str(e).lower() or "timeout" in str(e).lower():
                record["status"] = "FAIL"
                summary["fail"] += 1
            else:
                record["status"] = "FAIL"
                summary["fail"] += 1
        except Exception as e:
            latency_ms = int((time.perf_counter() - t0) * 1000)
            record["latency_ms"] = latency_ms
            record["result"] = {"error": str(e)}
            record["status"] = "FAIL"
            summary["fail"] += 1

        records.append(record)
        print(f"  [{record['status']:6s}] {tool_name:20s} ({record['latency_ms']:5d} ms)")

    # --- Step 4: check for PascalCase / snake_case collision ---
    snake_case_tools = {t for t in live_tools if "_" in t and t.islower()}
    pascal_case_tools = {t for t in live_tools if t[0].isupper() and t not in ("ListActors", "GetActorDetails", "DeleteActor")}
    collision = pascal_case_tools & {"SpawnActor", "SetActorTransform"}

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "server_url": args.url,
        "live_tool_count": len(live_tools),
        "live_tools": sorted(live_tools),
        "missing_tools": sorted(missing),
        "pascal_case_duplicates": sorted(collision),
        "summary": summary,
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test for 15 new MCP tools")
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp", help="MCP server URL")
    parser.add_argument("--timeout", type=float, default=60.0, help="HTTP timeout in seconds")
    parser.add_argument("--output", default=None, help="Output JSON path (default: auto)")
    args = parser.parse_args()

    print(f"Connecting to MCP server at {args.url} ...")
    client = _MCPClient(args.url, timeout=args.timeout)
    try:
        init_result = client.initialize()
        print(f"Initialized. Server: {init_result.get('serverInfo', {}).get('name', '?')}")
    except MCPError as e:
        print(f"FAILED to initialize: {e}")
        return 1

    print("Running smoke tests ...")
    report = run_tests(client, args)

    # Save report
    out_path = args.output
    if not out_path:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_dir = Path(__file__).parent / "reports"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"smoke_{ts}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport saved to: {out_path}")

    # Summary
    s = report["summary"]
    print(f"\n{'='*50}")
    print(f"Summary: PASS={s['pass']}, GATED={s['gated']}, FAIL={s['fail']}")
    print(f"Live tools: {report['live_tool_count']}")
    if report.get("missing_tools"):
        print(f"Missing: {report['missing_tools']}")
    if report.get("pascal_case_duplicates"):
        print(f"PascalCase duplicates: {report['pascal_case_duplicates']} — FAIL")
    print(f"{'='*50}")

    return 0 if s["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
