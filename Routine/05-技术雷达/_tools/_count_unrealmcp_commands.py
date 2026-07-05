"""
下载 DandyDay/UnrealMCP 的所有 handler cpp 文件,数 RegisterCommand( 调用,验证 README 说 '104 total' 是否属实。
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

OUT_DIR = r"C:\Users\yuhang\AppData\Local\Temp\unrealmcp_src"
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_raw(name):
    url = f"https://raw.githubusercontent.com/DandyDay/UnrealMCP/main/Source/N1UnrealMCP/Private/Handlers/{name}.cpp"
    out = os.path.join(OUT_DIR, name + ".cpp")
    try:
        urllib.request.urlretrieve(url, out)
        with open(out, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return None

# 1. count RegisterCommand( in each handler cpp
total = 0
print(f"{'Handler':<28} {'Cat':<14} {'RegCmds':>8}  Notes")
print("-" * 75)
for name, cat in HANDLERS:
    src = fetch_raw(name)
    if src is None:
        print(f"{name:<28} {cat:<14} (fetch failed)")
        continue
    # RegisterCommand can appear with various whitespace — match RegisterCommand\s*(
    n = len(re.findall(r"RegisterCommand\s*\(", src))
    # Also find RegisterCommand occurrences that are NOT followed by ( (declarations etc)
    n_decl = len(re.findall(r"RegisterCommand\s+(?![\(])", src))
    total += n
    note = ""
    if n_decl > 0:
        note = f"(+{n_decl} non-call mentions)"
    print(f"{name:<28} {cat:<14} {n:>8}  {note}")

# 2. Also fetch CommandRegistry + Bridge for Meta commands
extra = [
    ("N1MCPCommandRegistry", r"C:\Git-repo-my\GameDevVault\Routine\05-技术雷达\_tools\unrealmcp_src\N1MCPCommandRegistry.cpp"),
    ("N1MCPBridge",          r"C:\Git-repo-my\GameDevVault\Routine\05-技术雷达\_tools\unrealmcp_src\N1MCPBridge.cpp"),
    ("N1MCPHandlerBase",     r"C:\Git-repo-my\GameDevVault\Routine\05-技术雷达\_tools\unrealmcp_src\N1MCPHandlerBase.cpp"),
]
for name, _ in extra:
    src = fetch_raw(name)
    if src is None:
        print(f"{name:<28} (fetch failed)")
        continue
    n = len(re.findall(r"RegisterCommand\s*\(", src))
    n_decl = len(re.findall(r"RegisterCommand\s+(?![\(])", src))
    print(f"{name:<28} (in root)  {n:>8}  (+{n_decl} non-call mentions)")

print(f"\nTotal RegisterCommand( calls across 10 handlers + registry: see above")
print("README claims: 104 total commands, 11 categories")
print(f"10 handlers counted: {total}")
print("Missing category in cpp: Meta (4 commands claimed by README) — likely in HandlerBase or CommandRegistry")