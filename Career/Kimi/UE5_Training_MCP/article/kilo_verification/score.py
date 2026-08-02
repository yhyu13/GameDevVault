import json
import re

def keyword_terms(text: str) -> set[str]:
    text = text.lower()
    return set(re.findall(r"[\u4e00-\u9fff]{2,}|[a-zA-Z][a-zA-Z0-9_]*|\d+", text))

def keyword_overlap(pred: str, ref: str) -> float:
    ref_t = keyword_terms(ref)
    if not ref_t:
        return 0.0
    pred_t = keyword_terms(pred)
    return len(ref_t & pred_t) / len(ref_t)

def structure_score(pred: str) -> float:
    s = 0.0
    if "```" in pred:
        s += 0.25
    if re.search(r"engine[\\/]source[\\/]", pred.lower()):
        s += 0.25
    if re.search(r"^\s*(\d+\.|-|\*|\+)\s", pred, re.MULTILINE):
        s += 0.25
    if any(w in pred.lower() for w in ["trade-off", "tradeoff", "limitation", "limit",
                                       "代价", "局限", "bottleneck"]):
        s += 0.25
    return s

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

assert len(refs) == len(preds) == 15, (len(refs), len(preds))

total = 0.0
print(f"{'#':>2} {'kw':>6} {'struct':>6}  topic")
for i, (ref, pred) in enumerate(zip(refs, preds)):
    kw = keyword_overlap(pred["output"], ref["output"])
    sc = structure_score(pred["output"])
    total += kw
    print(f"{i:>2} {kw:6.3f} {sc:6.3f}  {ref['topic']}")
print(f"\navg kw = {total / 15:.3f}")
