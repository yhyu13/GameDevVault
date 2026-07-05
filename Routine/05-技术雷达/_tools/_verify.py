import os
import re

src = r"C:\Git-repo-my\GameDevVault\Routine\05-技术雷达\P0-立即学习"
for name in sorted(os.listdir(src)):
    if not name.endswith(".html"):
        continue
    with open(os.path.join(src, name), "r", encoding="utf-8") as f:
        h = f.read()
    bad = [p for p in ["__TITLE__","__SUBTITLE__","__DRAG_JSON__","__SINGLE_JSON__","__MULTI_JSON__","__TF_JSON__"] if p in h]
    title = re.search(r"<title>(.+?)</title>", h)
    n_drag = h.count('"sentence":') + h.count("'sentence':")
    n_single_q = h.count('"options":') + h.count("'options':")
    n_tf = h.count('"answer":') + h.count("'answer':")
    print(f"{name[:42]:<42}")
    print(f"   title={title.group(1)[:60] if title else '?'}")
    print(f"   placeholders_remaining={len(bad)}  drag_q≈{n_drag}  options_q≈{n_single_q}  tf_q≈{n_tf}")