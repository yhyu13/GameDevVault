# Stage 1 流水线统计（teacher_self_v1）

## physics_01_impulse（候选 25）
- L1 拦截 3，L3 拦截 7，通过 15（保留线 judge≥6.0）
- 通过解 judge 分：[8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 6.8, 6.8, 6.8, 6.8, 6.8]

## rendering_01_frustum_cull（候选 25）
- L1 拦截 3，L3 拦截 7，通过 15（保留线 judge≥6.0）
- 通过解 judge 分：[8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 6.8, 6.8, 6.8, 6.8, 6.8]

SFT 交接包样本数：30
DPO 偏好对数：20

> judge 为 self 模式 agent-judge（rubric 分级映射）；人工 golden 校准 + kappa 属后续步骤，此前分数不作最终决策依据。