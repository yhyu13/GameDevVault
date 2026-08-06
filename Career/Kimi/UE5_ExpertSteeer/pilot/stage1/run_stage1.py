"""run_stage1 —— 数据侧流水线主控：teacher 候选池 → 分层验证 → agent-judge → 训练交接包。

用法：python run_stage1.py
输出（stage1/output/）：
- results.json            每个候选的 L1/L3 逐层结果 + judge 分
- ue5_math_verified_v1.jsonl  SFT 交接包（Alpaca 格式：instruction/input/output + metadata）
- ue5_math_dpo_v1.jsonl    DPO 偏好对（chosen=最高分通过解，rejected=每个失败解）
- stats.md                 统计摘要

teacher 插拔：teacher_pool.POOL 当前为 self 模式（本会话 LLM 生成）；
接 API teacher 时由 generate_candidates.py 按相同契约（task_id -> {name: source}）填充。
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from teacher_pool import POOL, TIER, JUDGE_SCORE, PROMPTS, MODEL_SIZE, DOMAIN  # noqa: E402

STAGE1 = Path(__file__).resolve().parent
PILOT = STAGE1.parent
CAND_DIR = STAGE1 / "candidates"
OUT_DIR = STAGE1 / "output"
PY = sys.executable or "python"

VERIFIERS = {
    "physics_01_impulse": (PILOT / "physics" / "verifiers", "run_one.py"),
    "rendering_01_frustum_cull": (PILOT / "rendering" / "verifiers", "verify_rendering_01_frustum_cull.py"),
}

KEEP_THRESHOLD = 6.0  # judge 加权分保留线（对标现有 dataset_stats 的 judge_threshold 思路）


def run_verifier(task_id, cand_path):
    """子进程跑分层验证器，返回解析后的结果 dict（含 l1/l3/verdict）。"""
    ver_dir, script = VERIFIERS[task_id]
    cmd = [PY, str(ver_dir / script)]
    if task_id == "physics_01_impulse":
        cmd += [task_id, str(cand_path)]
    else:
        cmd += ["--solution", str(cand_path)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace",
                              timeout=60, cwd=str(ver_dir))
        out = proc.stdout.strip().splitlines()
        if not out:
            return {"error": f"无输出: {proc.stderr[-300:]}"}
        if task_id == "physics_01_impulse":
            data = json.loads(out[-1])
            return {"l1_ok": data["l1"]["ok"], "l1_reasons": data["l1"]["reasons"],
                    "l3_ok": data["l3"]["ok"], "l3_passed": data["l3"]["passed"],
                    "l3_failed": data["l3"]["failed"], "l3_failures": data["l3"]["failures"]}
        line = next((ln for ln in out if ln.startswith("RESULT ")), None)
        data = json.loads(line[len("RESULT "):])
        return {"l1_ok": data.get("l1") is True, "l1_reasons": [data.get("l1_error", "")] if not data.get("l1") else [],
                "l3_ok": data.get("verdict") == "PASS", "l3_passed": data.get("l3_passed"),
                "l3_failed": data.get("l3_total", 0) - data.get("l3_passed", 0),
                "l3_failures": data.get("l3_error") or []}
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_results = {}
    sft_rows, dpo_rows = [], []

    for task_id, candidates in POOL.items():
        tiers = TIER[task_id]
        prompt = PROMPTS[task_id]
        task_rows = []
        task_dir = CAND_DIR / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        for name, source in candidates.items():
            cand_path = task_dir / f"{name}.py"
            cand_path.write_text(source.lstrip("\n"), encoding="utf-8")
            result = run_verifier(task_id, cand_path)
            result["name"] = name
            result["tier"] = tiers.get(name, "unknown")
            result["judge_score"] = JUDGE_SCORE.get(result["tier"], 0.0)
            result["source"] = source
            all_results[f"{task_id}/{name}"] = result

            passed = result.get("l3_ok") is True
            if passed:
                task_rows.append(result)
                sft_rows.append({
                    "instruction": prompt,
                    "input": "",
                    "output": source.lstrip("\n"),
                    "metadata": {
                        "task_id": task_id,
                        "domain": DOMAIN[task_id],
                        "model_size": MODEL_SIZE[task_id],
                        "source": "teacher_self_v1",
                        "tier": result["tier"],
                        "judge_score": result["judge_score"],
                        "l3_passed": result["l3_passed"],
                        "l3_failed": result["l3_failed"],
                    },
                })

        # DPO：chosen = 本任务最高分通过解；rejected = 每个失败解
        best = max(task_rows, key=lambda r: r["judge_score"]) if task_rows else None
        for name in candidates:
            r = all_results[f"{task_id}/{name}"]
            if r.get("l3_ok") is not True and best is not None:
                dpo_rows.append({
                    "instruction": prompt,
                    "input": "",
                    "chosen": best["source"].lstrip("\n"),
                    "rejected": r["source"].lstrip("\n"),
                    "metadata": {
                        "task_id": task_id,
                        "domain": DOMAIN[task_id],
                        "source": "teacher_self_v1",
                        "chosen_judge_score": best["judge_score"],
                        "rejected_tier": r["tier"],
                        "rejected_fail_layer": "L1" if not r.get("l1_ok") else "L3",
                    },
                })

    (OUT_DIR / "results.json").write_text(
        json.dumps(all_results, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT_DIR / "ue5_math_verified_v1.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in sft_rows) + "\n", encoding="utf-8")
    (OUT_DIR / "ue5_math_dpo_v1.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in dpo_rows) + "\n", encoding="utf-8")

    # ---- stats ----
    lines = ["# Stage 1 流水线统计（teacher_self_v1）", ""]
    for task_id in POOL:
        rs = [r for k, r in all_results.items() if k.startswith(task_id + "/")]
        l1_fail = sum(1 for r in rs if not r.get("l1_ok"))
        l3_fail = sum(1 for r in rs if r.get("l1_ok") and not r.get("l3_ok"))
        passed = sum(1 for r in rs if r.get("l3_ok"))
        lines.append(f"## {task_id}（候选 {len(rs)}）")
        lines.append(f"- L1 拦截 {l1_fail}，L3 拦截 {l3_fail}，通过 {passed}（保留线 judge≥{KEEP_THRESHOLD}）")
        lines.append(f"- 通过解 judge 分：{[r['judge_score'] for r in rs if r.get('l3_ok')]}")
        lines.append("")
    lines.append(f"SFT 交接包样本数：{len(sft_rows)}")
    lines.append(f"DPO 偏好对数：{len(dpo_rows)}")
    lines.append("")
    lines.append("> judge 为 self 模式 agent-judge（rubric 分级映射）；人工 golden 校准 + kappa 属后续步骤，此前分数不作最终决策依据。")
    (OUT_DIR / "stats.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
