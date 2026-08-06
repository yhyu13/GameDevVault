# rendering 域 Stage 0 试点实测报告

- 运行环境：Windows / Python 3.13.12（`python --version` 实测）
- 测量协议：每任务 4 解（1 golden + 3 播种失败解）× **3 次重复**（flakiness）
- 验证器：`verifiers/run_all.py 3`，产物 `reports/verification_results.json`
- 说明：本域 3 个任务均为纯数学核（非配置类），**无 L2 层**（结果中 l2=None）；**L4 judge 由 agent 扮演**（真实校准需人工 golden + kappa，属后续步骤，见 pilot/README 边界）

## 1. 任务清单

| id | 内容 | UE C++/shader 形态 |
|---|---|---|
| rendering_01_frustum_cull | 视锥剔除点/包围球测试（6 平面） | `FConvexVolume::IntersectSphere` / `UWorld::IsPointInFrustum`；shader `View.SFrustum*Plane`（Common.ush） |
| rendering_02_lod_distance | LOD 距离选择（带 hysteresis） | `UStaticMeshComponent::ComputeDesiredLODLevel` / `GetLODForScreenSize`（ScreenSize + bUseHysteresis） |
| rendering_03_linear_srgb | linear → sRGB（IEC 61966-2-1） | shader `LinearToSrgb`（Common.ush）；C++ `FLinearColor→FColor` 量化 |

## 2. 分层验证矩阵（judge 由 agent 扮演；L4 分 = 0.35×正确性+0.35×API+0.15×工程化+0.15×性能，PASS 门槛 加权≥7 且 正确性≥6）

| 任务 | 解（失败类型） | L1 门禁 | L2 Schema | L3 执行 | L4 judge 分 | 预期判定 | 实测判定 |
|---|---|---|---|---|---|---|---|
| 01 | golden | 通过 | — | 23/23 | 9.85 | PASS | PASS |
| 01 | fail1 平面法线符号反 | 通过（拦不住） | — | 10/23 | 3.60 | FAIL | FAIL |
| 01 | fail2 近平面距离错（near=0） | 通过（拦不住） | — | 20/23 | 3.95 | FAIL | FAIL |
| 01 | fail3 忽略包围球半径 | 通过（拦不住） | — | 20/23 | 4.65 | FAIL | FAIL |
| 02 | golden | 通过 | — | 13/13 | 9.85 | PASS | PASS |
| 02 | fail1 无 hysteresis | 通过（拦不住） | — | 10/13 | 5.70 | FAIL | FAIL |
| 02 | fail2 降级阈值 off-by-one | 通过（拦不住） | — | 10/13 | 5.35 | FAIL | FAIL |
| 02 | fail3 迟滞方向反 | 通过（拦不住） | — | 10/13 | 5.00 | FAIL | FAIL |
| 03 | golden | 通过 | — | 4/4 | 9.85 | PASS | PASS |
| 03 | fail1 双伽马 | 通过（拦不住） | — | 2/4 | 4.30 | FAIL | FAIL |
| 03 | fail2 指数 2.2/2.4 颠倒 | 通过（拦不住） | — | 3/4 | 4.65 | FAIL | FAIL |
| 03 | fail3 丢线性段 | 通过（拦不住） | — | 2/4 | 4.30 | FAIL | FAIL |

- **L1 拦截**：播种失败解 0/9（语义错误均可运行、签名正确）；L1 门禁本身经自检有效（注入语法错误/缺函数文件 3 任务 × 2 变体全部被 L1 拦，`l1_self_check` 全 True）
- **L3 拦截**：9/9（100%），判定与 judge 分一致：golden 加权 9.85 全 PASS，失败解加权 ≤5.70 且正确性 ≤3 全 FAIL → **L1+L3 与 L4 判定 12/12 一致**
- **L2**：3/3 任务非配置类，不适用

## 3. 墙钟时间（每解中位数，含进程启动 + import + L1 + L3）

| 任务 | 单解 min/med/max（s） | 12 解全量 |
|---|---|---|
| 01 frustum | 0.0003 / 0.0004 / 0.0391 | — |
| 02 lod | 0.0002 / 0.0002 / 0.0113 | — |
| 03 srgb | 0.0002 / 0.0002 / 0.0049 | — |
| **合计** | — | **总墙钟 7.72 s**（3 次重复 × 12 解 + L1 自检 6 次） |

- 纯执行成本 **< 1 ms/解**（数值核级），7.72 s 几乎全部为子进程启动（~0.2 s/次）；批内执行（进程内 importlib）可将成本压到 ~10 ms 级
- 对比：UE 构建/编辑器跑一次 > 10 min → 执行沙箱成本可忽略，**GPU 不进 CI 的策略成立**

## 4. Flakiness（3 次重复）

- 判定抖动：**0/12**（所有解 3 次 verdict 全一致，`verdict_stable=yes`）
- 时间抖动：max 有偶发 0.04 s 尖峰（OS 调度/进程启动噪声），不影响判定
- 结论：纯数学核 + 硬编码期望值 → **确定性零 flakiness**，可安全进 CI 每提交

## 5. 每任务"L3 是否必要"结论

| 任务 | L1 拦住的播种失败 | L3 拦住 | L4（judge）能否单独拦 | L3 是否必要 |
|---|---|---|---|---|
| 01 frustum_cull | 0/3 | 3/3 | 能（但 judge 不可靠、贵、需逐解调用） | **必要**：3 个符号/距离/半径错误全是"能跑但错"，仅执行层可确定性暴露；数值核执行成本 <1ms |
| 02 lod_distance | 0/3 | 3/3 | 能 | **必要**：迟滞方向/索引/缺失错误仅在带内状态序列上暴露（hysteresis 本质是运行时行为），静态层无信号 |
| 03 linear_srgb | 0/3 | 3/3 | 能 | **必要**：双伽马/指数错在端点处与正确解重合（0 和 1），肉眼/judge 易漏，执行断言（含端点、阈值点、暗部）确定性区分 |

**域结论**：渲染域数学核任务 L1 只拦语法/签名（播种语义错误全漏），L3 以 <1ms/解、零 flakiness 的成本 100% 拦截 → **L3 执行沙箱对本域全部 3 个任务必要，分层份额建议 100% 数学核任务上 L3**；L4 judge 与 L3 判定 12/12 一致，judge 保留用于"工程化/性能意识"软分（DPO 偏好对），不承担正确性裁决。

## 6. 附注

- 边界经验：frustum 平面布尔测试需避开精确边界点（float 精度使边界点判定不稳，如 2.6666666667 恰好落在右平面上被判外），用例已改用边界外 0.1 距离的点
- sRGB 阈值点 0.0031308 处线性段与 gamma 段按设计连续（差 ~1.7e-5 < 1e-4），不能用于区分"丢线性段"错误——必须用 0.001 这类纯线性段点；此为 hidden test 设计陷阱，已规避
- L1 自检注入文件在临时目录，不落盘 pilot/rendering
