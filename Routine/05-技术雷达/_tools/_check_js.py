"""Extract <script> from each HTML, write to tmp, run node --check."""
import os
import re
import subprocess
import sys
import tempfile

src_dir = r"C:\Git-repo-my\GameDevVault\Routine\05-技术雷达\P0-立即学习"
files = sorted(f for f in os.listdir(src_dir) if f.endswith(".html"))

ok = 0
fail = 0
for name in files:
    path = os.path.join(src_dir, name)
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"<script>([\s\S]*?)</script>", html)
    if not m:
        print(f"✗ {name}: no <script> block")
        fail += 1
        continue
    js = m.group(1)
    # Write to temp file
    fd, tmp = tempfile.mkstemp(suffix=".js")
    os.close(fd)
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(js)
        r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
        if r.returncode == 0:
            print(f"✓ {name}: JS syntax OK ({len(js)} chars)")
            ok += 1
        else:
            print(f"✗ {name}: JS syntax ERROR")
            print(r.stderr[:500])
            fail += 1
    finally:
        os.unlink(tmp)

print(f"\nSummary: {ok} ok / {fail} fail / {len(files)} total")
sys.exit(0 if fail == 0 else 1)