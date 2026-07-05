"""
从本地已经下载好的 cpp 文件,精确数 RegisterCommand("xxx", ...) 真实调用。
"""
import os
import re

SRC_DIR = r"C:\Users\yuhang\AppData\Local\Temp\unrealmcp_src"
EXPECTED = {
    "Asset": 8,
    "Blueprint": 12,
    "BlueprintNode": 15,
    "Material": 11,
    "UMG": 7,
    "Project": 5,
    "Editor": 19,
    "Landscape": 8,
    "PIE": 5,
    "Data": 10,
}

def strip_comments(src):
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    src = re.sub(r"//[^\n]*", "", src)
    return src

def count_real_calls(src):
    src_nc = strip_comments(src)
    return re.findall(r'RegisterCommand\s*\(\s*"([^"]+)"', src_nc)

total = 0
all_cmds = {}
print(f"{'Handler':<32} {'Cat':<14} {'Calls':>6}  {'README':>7}  Match   Command names (first 5)")
print("-" * 120)
for fname in sorted(os.listdir(SRC_DIR)):
    if not fname.endswith(".cpp"):
        continue
    cat = fname.replace("N1MCP", "").replace("Handler.cpp", "")
    if cat == "BlueprintNode":
        cat_disp = "BlueprintNode"
    elif cat == "":
        cat_disp = "(?)"
    else:
        cat_disp = cat
    with open(os.path.join(SRC_DIR, fname), "r", encoding="utf-8") as f:
        src = f.read()
    cmds = count_real_calls(src)
    real_n = len(cmds)
    total += real_n
    all_cmds[cat] = cmds
    expected = EXPECTED.get(cat_disp, "?")
    match = "✓" if str(real_n) == str(expected) else f"✗ off by {real_n - (int(expected) if expected!='?' else 0):+d}"
    sample = ", ".join(cmds[:5])
    print(f"{fname:<32} {cat_disp:<14} {real_n:>6}  {str(expected):>7}  {match:<10}  {sample}{'...' if len(cmds)>5 else ''}")

print(f"\n{'='*70}")
print(f"Total from 10 handler cpp files: {total}")
print(f"README claim for 10 categories: {sum(EXPECTED.values())}")
print(f"Difference: {total - sum(EXPECTED.values()):+d}")
print(f"\nMeta category claim by README: 4 commands")
print(f"  Note: no N1MCPMetaHandler.cpp exists in Source/N1UnrealMCP/Private/Handlers/")
print(f"  Meta likely defined in CommandRegistry.cpp / HandlerBase.cpp / Module cpp")

# Also look at the asset handler's actual commands to see what 9 it really has
print(f"\n{'='*70}")
print(f"Asset handler — all 9 commands:")
for c in all_cmds.get("Asset", []):
    print(f"  - {c}")

print(f"\n{'='*70}")
print(f"Editor handler — all {len(all_cmds.get('Editor', []))} commands:")
for c in all_cmds.get("Editor", []):
    print(f"  - {c}")

print(f"\n{'='*70}")
print(f"Data handler — all {len(all_cmds.get('Data', []))} commands:")
for c in all_cmds.get("Data", []):
    print(f"  - {c}")