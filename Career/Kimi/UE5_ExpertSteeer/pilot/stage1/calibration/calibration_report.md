# Judge 校准报告（盲测 v1）

- 样本数：36（9 任务 × 4）　评审人：人工专家（盲测，未看 agent 分）
- 双 PASS：18　双 FAIL：18　agent PASS/人 FAIL：0　agent FAIL/人 PASS：0
- **一致率 po = 1.000**（36/36）
- **Cohen's kappa = 1.000**（目标 ≥ 0.70）
- 分数相关性 Pearson r = 0.955（人工 0-10 vs agent 分级分）

## 混淆矩阵（行=agent，列=人工）

| | 人 PASS | 人 FAIL |
|---|---|---|
| agent PASS | 18 | 0 |
| agent FAIL | 0 | 18 |

## 逐 tier 分解

| tier | n | 判定一致 | 人工均分 | agent 均分 |
|---|---|---|---|---|
| correct_high | 9 | 9/9 | 9.0 | 8.5 |
| correct_mid | 9 | 9/9 | 8.0 | 6.8 |
| buggy_subtle | 9 | 9/9 | 3.6 | 3.5 |
| api_bad | 9 | 9/9 | 2.9 | 1.0 |

## 结论与动作

- kappa 1.00 ≥ 0.7：**agent-judge 判定与人类专家校准通过**，分数可作数据筛选依据（保留线 6.0 维持）
- 数值分数仍有系统性偏差（agent 分级分 8.5/6.8/3.5/2.0/1.0 vs 人工连续分），判定一致不代表分数一致；DPO 构造与排序应基于判定而非裸分数
- 下一步：API 基线（Qwen 0.8B/2B 跑 9 任务 eval）
