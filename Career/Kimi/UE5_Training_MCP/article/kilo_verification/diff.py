import json
import re

def keyword_terms(text: str) -> set[str]:
    text = text.lower()
    return set(re.findall(r"[\u4e00-\u9fff]{2,}|[a-zA-Z][a-zA-Z0-9_]*|\d+", text))

refs = []
with open("/home/hangyu5/Documents/Gitrepo-My/GameDevVault/Career/Kimi/UE5_Training_MCP/data/splits/fresh_test.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            refs.append(json.loads(line))

preds = []
with open("/tmp/kilo_self_bench/answers_mine.jsonl", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            preds.append(json.loads(line))

for idx in [2, 3, 9, 13]:
    ref = refs[idx]["output"]
    pred = preds[idx]["output"]
    rt = keyword_terms(ref)
    pt = keyword_terms(pred)
    missing = sorted(rt - pt)
    print(f"=== [{idx}] {refs[idx]['topic']} — ref len {len(ref)} pred len {len(pred)}")
    print(f"MISSING ({len(missing)}): {missing}")
    print()
