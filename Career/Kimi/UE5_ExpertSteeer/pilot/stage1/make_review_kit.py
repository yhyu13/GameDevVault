"""make_review_kit —— 生成 judge 校准包（盲测）。

- 从 9 任务 × 176 候选中抽取 30 条：每任务 1 high + 1 mid + 1 buggy + 3 个 api_bad（每域 1 个）
- review_kit.md：评审人用（隐藏 agent 分/tier，避免锚定）
- manifest.json：真值表（tier + agent judge 分 + L1/L3），用于事后算 kappa

评审协议：每条给出 PASS/FAIL + 0-10 分 + 一句理由；评分依据 rubric：
正确性（逻辑/边界）高权重、API/UE 语义、工程化、性能。分 >= 7 视为 PASS。
"""
import json
from pathlib import Path

STAGE1 = Path(__file__).resolve().parent  # pilot/stage1
OUT = STAGE1 / "calibration"
OUT.mkdir(parents=True, exist_ok=True)

results = json.loads((STAGE1 / "output" / "results.json").read_text(encoding="utf-8"))

# 每任务固定抽样（确定性，可复现）
PICKS = {
    "physics_01_impulse": ("phys_01", "phys_11", "phys_16", "phys_24"),
    "rendering_01_frustum_cull": ("rend_01", "rend_11", "rend_17", "rend_23"),
    "physics_02_spring_euler": ("spr_01", "spr_10", "spr_14", "spr_18"),
    "physics_03_wheel_friction": ("whl_01", "whl_10", "whl_14", "whl_18"),
    "rendering_02_lod_distance": ("lod_01", "lod_10", "lod_14", "lod_17"),
    "rendering_03_linear_srgb": ("srgb_01", "srgb_10", "srgb_14", "srgb_17"),
    "fx_01_niagara_config": ("fx1_01", "fx1_10", "fx1_15", "fx1_17"),
    "fx_02_curl_noise3d": ("fx2_01", "fx2_10", "fx2_14", "fx2_18"),
    "fx_03_flipbook_uv": ("fx3_01", "fx3_10", "fx3_14", "fx3_17"),
}

DOMAIN_CN = {"physics": "物理", "rendering": "渲染", "fx": "特效"}
TASK_CN = {
    "physics_01_impulse": "两球碰撞冲量解算", "physics_02_spring_euler": "阻尼弹簧半隐式欧拉步进",
    "physics_03_wheel_friction": "载具轮纵向力/摩擦圆", "rendering_01_frustum_cull": "视锥剔除 6 平面",
    "rendering_02_lod_distance": "LOD 距离选择（迟滞）", "rendering_03_linear_srgb": "linear→sRGB（IEC 61966-2-1）",
    "fx_01_niagara_config": "Niagara 配置校验+预算", "fx_02_curl_noise3d": "3D curl noise",
    "fx_03_flipbook_uv": "flipbook 帧号→行列+UV",
}

manifest = {}
blocks = []
blocks.append("# Judge 校准评审包（盲测 v1）\n")
blocks.append("## 评审协议\n")
blocks.append("""- 共 **30 条**候选（9 任务 × 3~4 条），每条都是模型对给定任务的实现
- 对每条给出三个字段：**判定**（PASS/FAIL）、**分数**（0-10，≥7 为 PASS）、**理由**（一句话，指出问题或亮点）
- 评分维度（按权重）：正确性（逻辑与边界处理，最重要）→ UE/API 语义 → 工程化（结构/可读/防御性）→ 性能
- 参考：L1 = 导入/签名/禁用模式门禁结果，L3 = 隐藏测试执行结果（L3 失败 ≠ 直接 FAIL，你判断是否可救/是否训练毒药；L3 通过 ≠ 直接 PASS，你判断是否存在测试外错误）
- 填完保存为 `review_kit_graded.md`（在每条的判定行后填），或按序号另存为 JSON 返回
- 注意：**评审人看不到 agent 的自动评分**（防锚定）；填完由流水线算一致性（kappa）""")
blocks.append("")
blocks.append("---\n")

idx = 0
for task_id, names in PICKS.items():
    for name in names:
        key = f"{task_id}/{name}"
        r = results[key]
        idx += 1
        manifest[key] = {
            "candidate": name, "task": task_id, "tier": r["tier"],
            "agent_score": r["judge_score"], "l1_ok": r.get("l1_ok"),
            "l3_ok": r.get("l3_ok"), "l3_failed": r.get("l3_failed"),
        }
        l1_s = "PASS" if r.get("l1_ok") else "FAIL"
        l3_s = "PASS" if r.get("l3_ok") else f"FAIL({r.get('l3_failed')} 用例)"
        blocks.append(f"## #{idx} [ {DOMAIN_CN.get(r['tier'][:0] or '?', '?')} ] {TASK_CN[task_id]} —— 候选 `{name}`")
        blocks.append("")
        blocks.append(f"- L1（导入/签名门禁）：`{l1_s}`　L3（隐藏测试执行）：`{l3_s}`")
        blocks.append("")
        blocks.append("```python")
        blocks.append(r["source"].rstrip("\n"))
        blocks.append("```")
        blocks.append("")
        blocks.append("**你的判定**：判定: ____　分数: ____/10　理由: ________________________________")
        blocks.append("")
        blocks.append("---")
        blocks.append("")

(OUT / "review_kit.md").write_text("\n".join(blocks), encoding="utf-8")
(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"written {idx} items -> calibration/review_kit.md + manifest.json")
