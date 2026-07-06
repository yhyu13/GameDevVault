"""
V4 — 修正:命令字符串用 TEXT("...") 包裹。重新精确数。
"""
import os
import re

SRC_DIR = r"C:\Users\yuhang\AppData\Local\Temp\unrealmcp_src"
EXPECTED = {
    "Asset": 8, "Blueprint": 12, "BlueprintNode": 15, "Material": 11,
    "UMG": 7, "Project": 5, "Editor": 19, "Landscape": 8, "PIE": 5, "Data": 10,
}

def strip_comments(src):
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    src = re.sub(r"//[^\n]*", "", src)
    return src

def count_real_calls(src):
    """Match RegisterCommand(TEXT("...")) or RegisterCommand("...")."""
    src_nc = strip_comments(src)
    return re.findall(r'RegisterCommand\s*\(\s*(?:TEXT\s*\(\s*)?"([^"]+)"', src_nc)

total = 0
all_cmds = {}
print(f"{'Handler':<32} {'Cat':<14} {'Calls':>6}  {'README':>7}  Match   Sample commands")
print("-" * 130)
for fname in sorted(os.listdir(SRC_DIR)):
    if not fname.endswith(".cpp"):
        continue
    if "Module" in fname or "Bridge" in fname or "Registry" in fname or "HandlerBase" in fname:
        continue
    cat = fname.replace("N1MCP", "").replace("Handler.cpp", "")
    cat_disp = cat if cat != "" else "(?)"
    if cat_disp == "BlueprintNode":
        cat_disp = "BlueprintNode"
    with open(os.path.join(SRC_DIR, fname), "r", encoding="utf-8") as f:
        src = f.read()
    cmds = count_real_calls(src)
    real_n = len(cmds)
    total += real_n
    all_cmds[cat_disp] = cmds
    expected = EXPECTED.get(cat_disp, "?")
    if expected == "?":
        match = "?"
    elif real_n == expected:
        match = "✓"
    else:
        match = f"✗ {real_n - expected:+d}"
    sample = ", ".join(cmds[:6]) + ("..." if len(cmds) > 6 else "")
    print(f"{fname:<32} {cat_disp:<14} {real_n:>6}  {str(expected):>7}  {match:<10}  {sample}")

print(f"\n{'='*70}")
print(f"10-handler total from source: {total}")
print(f"README claim (10 categories): {sum(EXPECTED.values())}")
print(f"Diff: {total - sum(EXPECTED.values()):+d}")
print(f"Meta category (README claim): 4 → expected grand total: {sum(EXPECTED.values()) + 4} = {total + 4} if Meta=4")

# Dump each mismatch detail
print(f"\n{'='*70}")
print("Per-category breakdown:")
for cat in sorted(all_cmds.keys()):
    e = EXPECTED.get(cat, "?")
    real = len(all_cmds[cat])
    flag = "✓" if e == real else f"({real - (e if e != '?' else 0):+d})"
    print(f"  {cat:<14} source={real:>3}  README={e:>3}  {flag}")
    for c in all_cmds[cat]:
        print(f"      - {c}")