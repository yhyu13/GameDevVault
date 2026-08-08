# Stage 1：数据侧流水线 + 训练交接包 v1

## 这是什么

把 pilot 的全部 **9 个任务**（物理 3、渲染 3、特效 3）跑通完整数据侧闭环：
**teacher 生成候选 → L1/L3 分层验证 → agent-judge 分级 → SFT/DPO 交接包**。

本机无训练环境（无模型、无 GPU、无 API key），此包即交付给训练侧的产物。

## 产物清单

| 文件 | 内容 |
|---|---|
| `output/ue5_math_verified_v1.jsonl` | **SFT 交接包**，Alpaca 格式 `{instruction, input, output, metadata}`，**122 条**（通过验证 + judge≥6.0） |
| `output/ue5_math_dpo_v1.jsonl` | **DPO 偏好对**，`{instruction, chosen, rejected, metadata}`，**54 对** |
| `output/results.json` | **176 个候选**的逐层验证结果 + judge 分（全量原始数据） |
| `output/stats.md` | 统计摘要 |
| `teacher_pool.py` + `teacher_pool_extra.py` + `teacher_pool_fx.py` | teacher 候选池（v1 = self 模式，本会话 LLM 生成；可插拔） |
| `run_stage1.py` | 流水线主控（`python run_stage1.py` 一键重跑） |

## 本轮实测数字（176 候选，9 任务）

| 任务 | 候选 | L1 拦 | L3 拦 | 通过 | judge 分布 |
|---|---|---|---|---|---|
| physics_01_impulse | 25 | 3 | 7 | 15 | 10×8.5 + 5×6.8 |
| rendering_01_frustum_cull | 25 | 3 | 7 | 15 | 10×8.5 + 5×6.8 |
| physics_02_spring_euler | 18 | 1 | 4 | 13 | 9×8.5 + 4×6.8 |
| physics_03_wheel_friction | 18 | 1 | 4 | 13 | 9×8.5 + 4×6.8 |
| rendering_02_lod_distance | 18 | 2 | 4 | 12 | 8×8.5 + 4×6.8 |
| rendering_03_linear_srgb | 18 | 2 | 3 | 13 | 9×8.5 + 4×6.8 |
| fx_01_niagara_config | 18 | 1 | 3 | 14 | 9×8.5 + 5×6.8 |
| fx_02_curl_noise3d | 18 | 1 | 4 | 13 | 9×8.5 + 4×6.8 |
| fx_03_flipbook_uv | 18 | 1 | 3 | 14 | 9×8.5 + 5×6.8 |

- SFT **122 条**（达标：验证样本 ≥100）、DPO **54 对**
- 播种失败解全部按预期拦截：物理 3 任务（显式欧拉次序/阻尼符号/参数名/摩擦圆漏算/不安全 sqrt/random 导入等）、渲染 3 任务（无迟滞/迟滞反向/clamp 越界/缺线性段/双伽马/指数错/返回值类型错）、特效 3 任务（缺字段检查/int 截断/Schema 漏检/curl 符号/冻结时间/缺衰减/行列互换/取模对象错/缺函数）

## 格式说明（对齐现有管线）

- SFT：Alpaca `{instruction, input, output}`，与 `UE5_Training`（train_lora.py）兼容；`metadata` 为附加字段
- DPO：`{instruction, chosen, rejected}`，与 `hitl_self_improvement.md` 的 Phase 3 流程对应
- judge 分含义：`correct_high=8.5 / correct_mid=6.8 / buggy=2.0~3.5 / api_bad=1.0`，保留线 6.0（对标现有 `dataset_stats` 的 judge_threshold 思路）

## 已知局限（诚实声明）

1. **judge 未校准**：self 模式 agent-judge 是 rubric 分级映射，不是独立 LLM judge，更不是人工 golden。接入独立 judge（API 强模型）后用人工 golden 算 kappa、插 honeypot 之前，分数不作最终决策依据
2. **teacher = 本会话 LLM**：候选分布由我控制（含刻意播种的 bug），不等于真实小模型输出分布。真实分布下的拦截率需用目标模型（Qwen 0.8B/2B）生成候选后重测
3. **Python ≠ UE C++**：任务的 UE C++ 形态（Chaos 求解核、FConvexVolume、Niagara 配置校验）尚未落地；真实引擎验证（Automation Test / DXC）是 Stage 2
4. **任务覆盖窄**：仅数学核/数值/配置校验类；HLSL 编译、真实项目任务、动画/网络/GamePlay 域未进流水线

## 下一步

1. ✅ **judge 校准**：已通过（kappa=1.0，36/36 一致，`calibration/calibration_report.md`）
2. **API 基线**：`eval/eval_plan.md` + `eval/run_api_baseline.py`（纯 stdlib，克隆即跑），Qwen3 0.6B/1.7B/4B 跑 9 任务 eval，测任务区分度与尺寸梯度
3. 接 API teacher 批量扩量（当前 122 条 → 数百条）
4. Stage 2：DXC/HLSL 编译门禁 + IntroToUE Automation Test 真实引擎验证
