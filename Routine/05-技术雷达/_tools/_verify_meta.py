"""
Try to fetch CommandRegistry/HandlerBase/Bridge, look for Meta commands.
Also dump Asset handler RegisterCommand lines for inspection.
"""
import os
import re
import urllib.request

def fetch(name, subdir="Private"):
    url = f"https://raw.githubusercontent.com/DandyDay/UnrealMCP/main/Source/N1UnrealMCP/{subdir}/{name}.cpp"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        return None

# 1. CommandRegistry — likely has Meta
print("="*70)
print("N1MCPCommandRegistry.cpp")
print("="*70)
src = fetch("N1MCPCommandRegistry")
if src:
    print(f"  total bytes: {len(src)}")
    # find all RegisterCommand( ... ) calls
    matches = re.findall(r"RegisterCommand\s*\([^)]+\)", src, re.DOTALL)
    print(f"  RegisterCommand( calls: {len(matches)}")
    for i, m in enumerate(matches[:6]):
        print(f"    [{i+1}] {m[:100].strip()}")
    if len(matches) > 6:
        print(f"    ... ({len(matches)-6} more)")
else:
    print("  fetch failed")

# 2. HandlerBase
print()
print("="*70)
print("N1MCPHandlerBase.cpp")
print("="*70)
src = fetch("N1MCPHandlerBase")
if src:
    print(f"  total bytes: {len(src)}")
    matches = re.findall(r"RegisterCommand\s*\([^)]+\)", src, re.DOTALL)
    print(f"  RegisterCommand( calls: {len(matches)}")
    for i, m in enumerate(matches[:6]):
        print(f"    [{i+1}] {m[:100].strip()}")
else:
    print("  fetch failed")

# 3. Bridge
print()
print("="*70)
print("N1MCPBridge.cpp")
print("="*70)
src = fetch("N1MCPBridge")
if src:
    print(f"  total bytes: {len(src)}")
    matches = re.findall(r"RegisterCommand\s*\([^)]+\)", src, re.DOTALL)
    print(f"  RegisterCommand( calls: {len(matches)}")
    for i, m in enumerate(matches[:6]):
        print(f"    [{i+1}] {m[:100].strip()}")
else:
    print("  fetch failed")

# 4. Public headers
print()
print("="*70)
print("Public/Handlers/ — list header files")
print("="*70)
import json
url = "https://api.github.com/repos/DandyDay/UnrealMCP/contents/Source/N1UnrealMCP/Public/Handlers"
req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15) as r:
    items = json.loads(r.read())
for it in items:
    print(f"  {it['name']}  ({it['size']} bytes)")

# 5. Asset handler — dump all RegisterCommand lines to understand category mismatch
print()
print("="*70)
print("N1MCPAssetHandler.cpp — full RegisterCommand lines")
print("="*70)
url = "https://raw.githubusercontent.com/DandyDay/UnrealMCP/main/Source/N1UnrealMCP/Private/Handlers/N1MCPAssetHandler.cpp"
req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15) as r:
    src = r.read().decode("utf-8")
# Find the RegisterCommands method block
m = re.search(r"(void\s+RegisterCommands[^{]*\{[\s\S]*?^\})", src, re.MULTILINE)
if m:
    block = m.group(1)
    lines = [l.strip() for l in block.split("\n") if "RegisterCommand" in l]
    print(f"  {len(lines)} RegisterCommand lines:")
    for l in lines:
        print(f"    {l[:100]}")