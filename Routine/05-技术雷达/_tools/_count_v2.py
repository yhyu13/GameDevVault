"""
精确数 — 只数 "RegisterCommand(" 后跟双引号命令名的真实调用。
排除:函数签名、多行注释。
"""
import os
import re
import urllib.request

HANDLERS = [
    ("N1MCPAssetHandler",         "Asset"),
    ("N1MCPBlueprintHandler",     "Blueprint"),
    ("N1MCPBlueprintNodeHandler", "BlueprintNode"),
    ("N1MCPDataHandler",          "Data"),
    ("N1MCPEditorHandler",        "Editor"),
    ("N1MCPLandscapeHandler",     "Landscape"),
    ("N1MCPMaterialHandler",      "Material"),
    ("N1MCPPIEHandler",           "PIE"),
    ("N1MCPProjectHandler",       "Project"),
    ("N1MCPUMGHandler",           "UMG"),
]

EXTRA_FILES = [
    ("N1MCPCommandRegistry", "Private"),
    ("N1MCPHandlerBase",     "Private"),
    ("N1MCPBridge",          "Private"),
    ("N1MCPModule",          "Private"),  # might be N1UnrealMCPModule
    ("N1UnrealMCPModule",    "Private"),
    ("N1MCPHandlerBase",     "Public"),
]

def fetch(name, subdir="Private"):
    url = f"https://raw.githubusercontent.com/DandyDay/UnrealMCP/main/Source/N1UnrealMCP/{subdir}/{name}.cpp"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        return None

def fetch_header(name, subdir="Public"):
    url = f"https://raw.githubusercontent.com/DandyDay/UnrealMCP/main/Source/N1UnrealMCP/{subdir}/{name}.h"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        return None

def strip_comments(src):
    # strip /* ... */ and // ... \n
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    src = re.sub(r"//[^\n]*", "", src)
    return src

def count_real_calls(src):
    """Count RegisterCommand("...") — actual call with string literal."""
    src_nc = strip_comments(src)
    # Match RegisterCommand( followed by optional whitespace then "
    matches = re.findall(r'RegisterCommand\s*\(\s*"([^"]+)"', src_nc)
    return matches

# 1. count real RegisterCommand("xxx", ...) calls in each handler cpp
total = 0
all_cmds = {}
print(f"{'Handler':<28} {'Cat':<14} {'Real Calls':>11}  {'README claim':>14}  Match")
print("-" * 80)
for name, cat in HANDLERS:
    src = fetch(name)
    if src is None:
        print(f"{name:<28} {cat:<14} (fetch failed)")
        continue
    cmds = count_real_calls(src)
    real_n = len(cmds)
    total += real_n
    all_cmds[cat] = cmds
    readme_n = {"Editor":19,"Blueprint":12,"BlueprintNode":15,"Material":11,
                "UMG":7,"Project":5,"Asset":8,"Landscape":8,"PIE":5,"Data":10}.get(cat, "?")
    match = "✓" if str(real_n) == str(readme_n) else f"✗ (off by {real_n - int(readme_n)})"
    print(f"{name:<28} {cat:<14} {real_n:>11}  {readme_n:>14}  {match}")

# 2. Search other cpp/h files for any additional RegisterCommand("...") calls
print()
print("="*70)
print("Search extra files for additional RegisterCommand calls")
print("="*70)
extra_total = 0
for name, subdir in EXTRA_FILES:
    src = fetch(name, subdir)
    if src is None:
        continue
    cmds = count_real_calls(src)
    if cmds:
        print(f"\n  [{name}.cpp / {subdir}] {len(cmds)} calls:")
        for c in cmds:
            print(f"    {c}")
        extra_total += len(cmds)

print(f"\nTotal from 10 handlers: {total}")
print(f"Total from extras:      {extra_total}")
print(f"GRAND TOTAL:            {total + extra_total}")
print(f"\nREADME claim: 104 total (10 categories with explicit counts + Meta=4)")
print(f"Verified from source: {total + extra_total} {'✓' if total+extra_total==104 else '(mismatch)'}")