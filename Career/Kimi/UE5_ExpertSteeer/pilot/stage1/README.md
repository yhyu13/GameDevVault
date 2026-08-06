# Stage 1：数据侧流水线 + 训练交接包 v1

## 这是什么

把 pilot 的 9 个任务里首批 2 个（`physics_01_impulse`、`rendering_01_frustum_cull`）跑通完整数据侧闭环：
**teacher 生成候选 → L1/L3 分层验证 → agent-judge 分级 → SFT/DPO 交接包**。

本机无训练环境（无模型、无 GPU、无 API key），此包即交付给训练侧的产物。

## 产物清单

| 文件 | 内容 |
|---|---|
| `output/ue5_math_verified_v1.jsonl` | **SFT 交接包**，Alpaca 格式 `{instruction, input, output, metadata}`，30 条（通过验证 + judge≥6.0） |
| `output/ue5_math_dpo_v1.jsonl` | **DPO 偏好对**，`{instruction, chosen, rejected, metadata}`，20 对 |
| `output/results.json` | 50 个候选的逐层验证结果 + judge 分（全量原始数据） |
| `output/stats.md` | 统计摘要 |
| `teacher_pool.py` | teacher 候选池（v1 = self 模式，本会话 LLM 生成；可插拔） |
| `run_stage1.py` | 流水线主控（`python run_stage1.py` 一键重跑） |

## 本轮实测数字（50 候选）

- 每任务 25 候选：L1 拦 3（API 违规：参数名错/禁 import/结构违规）、L3 拦 7（行为 bug：分离守卫、约化质量、float32、符号、漏半径、FOV 语义）、通过 15
- SFT 30 条（10 high + 5 mid × 2 域）、DPO 20 对
- 典型验证实例：
  - `phys_18` float32 截断：低速全过、1e5 cm/s 高速误差 0.004 → **只有 L3 能拦**（judge 读码易放行）
  - `phys_21` 用 `m_a+m_b` 代替约化质量：等质量时恰好正确 → 质量悬殊测试才暴露
  - `rend_17` 漏包围球半径：球心外但相交的物体被误剔除（闪烁 bug 原型）

## 格式说明（对齐现有管线）

- SFT：Alpaca `{instruction, input, output}`，与 `UE5_Training`（train_lora.py）兼容；`metadata` 为附加字段
- DPO：`{instruction, chosen, rejected}`，与 `hitl_self_improvement.md` 的 Phase 3 流程对应
- judge 分含义：`correct_high=8.5 / correct_mid=6.8 / buggy=2.0~3.5 / api_bad=1.0`，保留线 6.0（对标现有 `dataset_stats` 的 judge_threshold 思路）

## 已知局限（诚实声明）

1. **judge 未校准**：self 模式 agent-judge 是 rubric 分级映射，不是独立 LLM judge，更不是人工 golden。接入独立 judge（API 强模型）后用人工 golden 算 kappa、插 honeypot 之前，分数不作最终决策依据
2. **teacher = 本会话 LLM**：候选分布由我控制（含刻意播种的 bug），不等于真实小模型输出分布。真实分布下的拦截率需用目标模型（Qwen 0.8B/2B）生成候选后重测
3. **Python ≠ UE C++**：任务的 UE C++ 形态（Chaos 求解核、FConvexVolume）尚未落地；真实引擎验证（Automation Test / DXC）是 Stage 2
4. **任务覆盖窄**：仅 2/9 任务、单域数学核；Niagara 配置类、HLSL 类、真实项目任务未进流水线

## 下一步

1. 扩量：其余 7 个任务（spring、wheel、LOD、sRGB、Niagara 配置、curl noise、flipbook）进流水线，接 API teacher 批量生成
2. judge 校准：人工 golden 20 条 + kappa + honeypot
3. Stage 2：DXC/HLSL 编译门禁 + IntroToUE Automation Test 真实引擎验证
4. 目标模型候选：有模型环境后，用目标模型生成候选重测分层拦截率（真实分布基线）
