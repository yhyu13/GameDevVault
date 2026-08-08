"""compute_kappa —— judge 校准分析：人工评审 vs agent-judge 真值。

解析 calibration/review_kit_graded.md（人工判定），对照 manifest.json（agent 分），
输出 calibration/calibration_report.md：一致性矩阵、Cohen's kappa、分数相关性、逐 tier 分解。

agent 侧判定规则：judge_score >= 6.0 -> PASS（correct_high/mid），否则 FAIL（buggy/api_bad）。
"""
import json
import re
from pathlib import Path

STAGE1 = Path(__file__).resolve().parent
CAL = STAGE1 / "calibration"

graded = (CAL / "review_kit_graded.md").read_text(encoding="utf-8")
manifest = json.loads((CAL / "manifest.json").read_text(encoding="utf-8"))

# 按候选名 -> 人工判定/分数
human = {}
for m in re.finditer(r"候选 `(\w+)`.*?你的判定.*?判定:\s*(\w+)\s*分数:\s*(\d+)/10", graded, re.S):
    human[m.group(1)] = {"verdict": m.group(2).upper(), "score": int(m.group(3))}

missing = [k for k in manifest if k.split("/")[1] not in human]
if missing:
    raise SystemExit(f"解析缺失 {len(missing)} 条: {missing[:5]}")

AGENT_PASS_THRESHOLD = 6.0

rows = []
for key, m in manifest.items():
    h = human[m["candidate"]]
    a_pass = m["agent_score"] >= AGENT_PASS_THRESHOLD
    h_pass = h["verdict"] == "PASS"
    rows.append({
        "candidate": m["candidate"], "task": m["task"], "tier": m["tier"],
        "agent_score": m["agent_score"], "agent_pass": a_pass,
        "human_verdict": h["verdict"], "human_score": h["score"], "human_pass": h_pass,
    })

n = len(rows)
a = sum(1 for r in rows if r["agent_pass"] and r["human_pass"])      # 双 PASS
b = sum(1 for r in rows if r["agent_pass"] and not r["human_pass"])  # agent PASS / 人 FAIL
c = sum(1 for r in rows if not r["agent_pass"] and r["human_pass"])  # agent FAIL / 人 PASS
d = sum(1 for r in rows if not r["agent_pass"] and not r["human_pass"])  # 双 FAIL
po = (a + d) / n
pe = ((a + b) * (a + c) + (c + d) * (b + d)) / (n * n)
kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0

# 分数相关性（人工 0-10 vs agent 分级分）
scores_h = [r["human_score"] for r in rows]
scores_a = [r["agent_score"] for r in rows]
mh, ma = sum(scores_h) / n, sum(scores_a) / n
cov = sum((h - mh) * (x - ma) for h, x in zip(scores_h, scores_a)) / n
vh = sum((s - mh) ** 2 for s in scores_h) / n
va = sum((s - ma) ** 2 for s in scores_a) / n
pearson = cov / (vh ** 0.5 * va ** 0.5) if vh and va else 0.0

# 逐 tier 分解
from collections import Counter
tier_stat = {}
for r in rows:
    t = tier_stat.setdefault(r["tier"], {"n": 0, "agree": 0, "h_scores": [], "a_scores": []})
    t["n"] += 1
    t["agree"] += 1 if (r["agent_pass"] == r["human_pass"]) else 0
    t["h_scores"].append(r["human_score"])
    t["a_scores"].append(r["agent_score"])

lines = []
lines.append("# Judge 校准报告（盲测 v1）")
lines.append("")
lines.append(f"- 样本数：{n}（9 任务 × 4）　评审人：人工专家（盲测，未看 agent 分）")
lines.append(f"- 双 PASS：{a}　双 FAIL：{d}　agent PASS/人 FAIL：{b}　agent FAIL/人 PASS：{c}")
lines.append(f"- **一致率 po = {po:.3f}**（{a + d}/{n}）")
lines.append(f"- **Cohen's kappa = {kappa:.3f}**（目标 ≥ 0.70）")
lines.append(f"- 分数相关性 Pearson r = {pearson:.3f}（人工 0-10 vs agent 分级分）")
lines.append("")
lines.append("## 混淆矩阵（行=agent，列=人工）")
lines.append("")
lines.append("| | 人 PASS | 人 FAIL |")
lines.append("|---|---|---|")
lines.append(f"| agent PASS | {a} | {b} |")
lines.append(f"| agent FAIL | {c} | {d} |")
lines.append("")
lines.append("## 逐 tier 分解")
lines.append("")
lines.append("| tier | n | 判定一致 | 人工均分 | agent 均分 |")
lines.append("|---|---|---|---|---|")
for t in ("correct_high", "correct_mid", "buggy_subtle", "buggy_obvious", "api_bad"):
    s = tier_stat.get(t)
    if not s:
        continue
    lines.append(f"| {t} | {s['n']} | {s['agree']}/{s['n']} | {sum(s['h_scores'])/len(s['h_scores']):.1f} | {sum(s['a_scores'])/len(s['a_scores']):.1f} |")
lines.append("")
lines.append("## 结论与动作")
lines.append("")
if kappa >= 0.7:
    lines.append(f"- kappa {kappa:.2f} ≥ 0.7：**agent-judge 判定与人类专家校准通过**，分数可作数据筛选依据（保留线 6.0 维持）")
else:
    lines.append(f"- kappa {kappa:.2f} < 0.7：**未通过**，需校准（调整阈值/重训 rubric/扩充 golden 集）")
lines.append("- 数值分数仍有系统性偏差（agent 分级分 8.5/6.8/3.5/2.0/1.0 vs 人工连续分），判定一致不代表分数一致；DPO 构造与排序应基于判定而非裸分数")
lines.append("- 下一步：API 基线（Qwen 0.8B/2B 跑 9 任务 eval）")

(CAL / "calibration_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
