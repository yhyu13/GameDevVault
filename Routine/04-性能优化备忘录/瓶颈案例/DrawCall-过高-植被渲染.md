---
tags: [perf/GPU, perf/DrawCall, perf/culling, perf/已验证]
aliases: []
---

# DrawCall 过高导致帧率骤降

| 字段 | 内容 |
|------|------|
| **现象** | 同屏 500+ 物体时，DrawCall 超过 2000，帧率从 60fps 跌到 30fps |
| **发现日期** | 2025-01-09 |
| **项目/场景** | 开放世界植被渲染 |
| **平台** | PC (RTX 3060) |
| **严重程度** | 严重 |

---

## 现象描述

> 场景中有大量植被（草、灌木、树），每个都是单独 MeshRenderer。当摄像机旋转到某个角度，同屏物体超过 500 时，帧率骤降。

**触发条件：** 摄像机俯角 30° 左右，看向远处山坡。  
**复现步骤：** 固定摄像机位置 → 观察 Stat 面板 → DrawCall 从 200 飙升到 2000+。  
**影响范围：** 所有植被密集区域。

---

## Profile 工具与数据

### 工具选择

- [x] RenderDoc
- [ ] Pix
- [ ] UE Insights
- [x] Unity Profiler
- [ ] Tracy
- [ ] Intel VTune
- [ ] 其他：___

### 关键数据截图

![RenderDoc截图](assets/drawcall_spike.png)  
*事件浏览器显示 2000+ DrawIndexed 调用*

| 指标 | 数值 | 正常范围 | 偏差 |
|------|------|----------|------|
| DrawCall | 2100 | < 500 | 4x |
| GPU Time | 28ms | < 8ms | 3.5x |
| CPU Time | 12ms | < 5ms | 2.4x |
| SetPassCall | 1800 | < 100 | 18x |
| ShadowCaster | 900 | < 200 | 4.5x |

---

## 根因分析

> 每个草/灌木都是独立 Mesh + Material，没有合批。即使材质相同，因为 Mesh 不同，无法 Dynamic Batching。

**初步假设：** 材质过多导致 SetPassCall 高。  
**验证过程：** RenderDoc 中确认，大量 `DrawIndexed` 之间只有 `VSSetConstantBuffers1` 变化（每个物体自己的矩阵），说明材质确实相同，只是没合批。  
**最终根因：** 植被没有使用 GPU Instancing 或 SRP Batcher 不兼容（Shader 中用了 Material Property Block 导致打断）。

---

## 解决方案

| 方案 | 实现难度 | 性能收益 | 副作用 | 是否采纳 |
|------|----------|----------|--------|----------|
| A: GPU Instancing | 低 | 极大 (2000→50) | 需要统一 Mesh | **是** |
| B: SRP Batcher 兼容 | 中 | 大 (2000→200) | 需改 Shader 去掉 MPB | 否 — 需要 MPB 做风动 |
| C: LOD + 距离剔除 | 低 | 中 | 远处质量下降 | 是 — 作为补充 |
| D: 合并 Mesh 为 Atlas | 高 | 大 | 编辑灵活性丧失 | 否 — 破坏动态加载 |

**最终方案详细描述：**
1. **草：** 使用 `Graphics.DrawMeshInstancedIndirect` + Compute Shader 生成实例数据（位置、旋转、缩放），一次 DrawCall 绘制 1000+ 草实例。
2. **灌木/树：** 保留 MPB 做风动动画，改用 `DrawMeshInstanced`（非 Indirect），每树种一批。
3. **LOD：** 距离 > 50m 的草直接不渲染，> 100m 的树降到 LOD2。

---

## 验证结果

> 优化后重新 Profile：

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| DrawCall | 2100 | 85 | 96% ↓ |
| GPU Time | 28ms | 6.2ms | 78% ↓ |
| CPU Time | 12ms | 3.1ms | 74% ↓ |
| 帧率 | 30fps | 120fps | 4x ↑ |

**是否达到预期？** 是，超出预期。  
**是否有回退风险？** 有 — Compute Shader 在旧版 Metal 上不支持，需保留 CPU 回退路径。

---

## 经验沉淀

**肌肉记忆：** 下次看到 DrawCall > 500，先查 `SetPassCall` vs `DrawCall` 比例。如果 `SetPassCall ≈ DrawCall`，说明是材质打断；如果 `SetPassCall << DrawCall`，说明是 Mesh 没合批。  
**可复用方案：** 这个 Instancing + Compute Shader 方案可以推广到所有大批量重复物体（草、石子、粒子、人群）。

---

## 关联知识库

- [[UE5-VT-显存调度]] — 大规模场景的纹理管理
- [[Instancing-Best-Practice]] — Instancing 的更多细节
- [[Compute-Shader-Grass]] — 程序化生成草地的 Compute Shader 方案

---

*Create date: 2025-01-09*  
*Last modified: 2025-01-09*  
*Verified: 是*
