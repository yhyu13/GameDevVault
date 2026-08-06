# Stage 0 试点协议（分层验证实测）

目标：实测分层验证（L1 编译/API 门禁、L2 Schema 校验、L3 执行沙箱、L4 judge）在三域的**拦截率、成本、flakiness**，决定各层任务份额。
分层份额是实验结论，不是架构设定——先试点实测，再定任务分布。

## 每域交付（`pilot/<domain>/`）

1. `tasks/` — 2-3 个原子任务，每任务一个 md，用 `base/task_template.md` 格式
2. `verifiers/` — 可执行验证脚本（Python 优先；HLSL 若 DXC 可用则编译，否则软件求值并注明）
3. `reports/<domain>_pilot_report.md` — 实测报告

## 测量协议

每个任务跑 4 个解：1 个 golden + 3 个播种失败解（取自该域失败簇预测表，如单位错误/符号错误/API 误用）。

记录矩阵：

| 解 | L1 门禁 | L2 Schema | L3 执行 | L4 judge 分 | 预期判定 |
|---|---|---|---|---|---|
| golden | 通过 | 通过 | 全过 | 高分 | PASS |
| 失败解1（注明类型） | ？ | ？ | ？ | ？ | FAIL |
| 失败解2 | ？ | ？ | ？ | ？ | FAIL |
| 失败解3 | ？ | ？ | ？ | ？ | FAIL |

- **L1**：导入/语法检查 + API 表面检查（golden 应通过；API 误用解应被拦）
- **L2**：仅配置类任务；Schema 校验
- **L3**：hidden tests 通过率（含数值容差断言）
- **L4**：按 rubric 各维度打分，与"预期判定"比对 → judge 一致性
- **成本**：每个解验证的墙钟时间；**flakiness**：重复跑 3 次看抖动

## 报告结论

每个任务回答：**L3 执行沙箱是否必要**（即 L1+L2+L4 拦不住的错误占比）？若 L1+L4 已拦住全部播种失败，该任务可退到静态层。

## 边界

- 只写 `pilot/` 目录；**不改** `plan.md` / `jd.md` / `plan_ai_replacement.md` / `research/`
- 不跑 UE 构建/编辑器（太慢）；全部用轻量脚本
- judge 由 agent 扮演（在报告中注明：真实校准需人工 golden + kappa，属后续步骤）
- 任务 prompt 用中文，代码用 Python/HLSL；在 task md 中注明对应的 UE C++ 形态（Stage 1 迁移目标）
- Python 用 `python --version` 确认；无 DXC 时跳过 shader 编译，改软件求值
