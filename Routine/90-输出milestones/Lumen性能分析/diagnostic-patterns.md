---
tags: [routine/milestone, reference/diagnostic, method/heuristic, engine/unreal, domain/rendering]
aliases: [Lumen诊断模式, Diagnostic-Patterns-Lumen, Performance-Diagnostic-Heuristics, 12条诊断启发式]
---

# Diagnostic Patterns — Lyra + Lumen 性能分析参考

> 12 条 mid/senior 级别的诊断启发式。每条**带方向、可能错**——拿去对 Lyra 数据验证，对的留、错的扔。
> 本文件是**方法论参考**，不是 phase 输出。Phase 1-4 的输出文件命名走 `01-baseline.md` / `02-lumen-tuning.md` / `03-memory.md` / `99-final-analysis.md` 这条线，本文件不占数字。

---

## 怎么用这份文件

1. **跑 Phase 1 baseline 之前**，把这份文件打印出来贴显示器。
2. **每看一条 trace 数据**，问自己"这条数据对应 12 条里的哪几条？"——不是全用，挑 2-3 条最相关的用。
3. **错了就扔**。这是启发式不是定理。你的 Lyra 数据很可能证伪其中 3-4 条——**那是好事**，说明你看到了真东西。
4. **Phase → Pattern 映射**：Phase 1（baseline）→ 重点用 1 / 3 / 8；Phase 2（调参）→ 重点用 2 / 4 / 7；Phase 3（内存）→ 重点用 2 / 7；Phase 4（综合）→ 全部。

---

## 1. 先列假设，再看数据

**错的姿势**：跑 Insights → 看数字 → "嗯帧时间是 16ms" → 然后不知所措。
**对的姿势**：跑之前先在纸上写 3-5 个候选瓶颈，按预期成本排序。然后看数据是 confirm 还是 reject 哪个假设。

> **核心问题**：在打开 Insights 之前，你认为最贵的 3 个东西是什么？为什么？

---

## 2. Cost = Unit × Count

几乎所有 GPU 瓶颈都是 `单次成本 × 次数`。看到 "贵" 不要停——拆：是单次贵，还是次数太多？这两类修法完全相反。

> **核心问题**：这个 Pass 是**每次都很重**，还是**很轻但调用了几千次**？

---

## 3. 三桶分类

把耗时分成三桶：
- (a) **必要的工作**
- (b) **冗余但暂时躲不开**
- (c) **纯浪费**

Senior 几乎所有优化都在 (c)。Junior 一直在跟 (a) 较劲。

> **核心问题**：这部分耗时，是**真的必要**，还是**没人写过删除它的代码**？

---

## 4. 对称测试

改一个参数、测、改回去。如果 "优化" 在反向 toggle 后就消失，那是巧合不是因果。

> **核心问题**：如果我把"修复"撤掉，性能会回到原来吗？还是更差？

---

## 5. CPU/GPU 失配

- CPU 闲但 GPU 忙 → RHI 提交或 fence stall
- CPU 忙但 GPU 闲 → 命令编码器被吃光了（draw call 太多），不是 GPU 弱

> **核心问题**：RenderThread 和 RHIThread 谁在等谁？等待的箭头指向哪边？

---

## 6. 带宽 vs 算力

GPU 瓶颈分两种：
- **bandwidth-bound**（内存读写占大头）
- **compute-bound**（ALU 占大头）

RenderDoc 看 memory traffic；Insights timing 看的是混合信号——别混。

> **核心问题**：如果我把 Lumen 跑在 4K 而不是 1080p，瓶颈会变吗？变 = 带宽相关；不变 = 算力相关。

---

## 7. Hotspot Relocation 陷阱

"修好" 一个 Pass 后，总时间通常不变——它挪到下一个 Pass 去了。别庆祝到端到端改善。

> **核心问题**：我把 Pass X 砍掉 50% 后，总帧时间是不是真的少 25%？还是挪去了 Pass Y？

---

## 8. 首帧 vs 稳态

Lumen 有大量首帧成本：surface capture、cache build、probe layout。第 1 帧的 trace 和第 1000 帧的 trace 是两个不同的故事。

> **核心问题**：我现在 profile 的是**第几帧**？如果是首帧，我在测的是初始化成本而不是运行成本。

---

## 9. 像素成本不对称

Lumen 很多 Pass 是 per-pixel 的。1080p 时开销压满；4K 时摊薄。换分辨率测两次——比例变 = per-pixel；不变 = per-object 或 per-frame。

> **核心问题**：分辨率 ×2，总帧时间 ×几？

---

## 10. Frame Phase 分解

Lumen 一帧分阶段：
1. scene update
2. probe build
3. gather
4. composite
5. resolve

每阶段成本动因不同。Senior 不把它们糊在一起。

> **核心问题**：我的慢是在哪个**阶段**？前 1/3 是 scene 更新慢？中段是 gather 慢？还是后段 composite 慢？

---

## 11. 硬件 RT vs 软件 Lumen

两者**成本结构完全不同**：
- HW RT 成本 ≈ ray 数 × BVH 遍历
- 软件 fallback 成本 ≈ screen probe 数 × 距离场采样

直接比较耗时是错的——要先确认测的是什么。

> **核心问题**：我跑的是 `Lumen.HardwareRayTracing=1` 还是 `0`？如果两者都跑过，比较的是**实现差异**还是**算法差异**？

---

## 12. 反向推理

不要问 "为什么 GPU 慢"。问 "**GPU 要快，需要什么条件成立**"。然后去测这些条件。

> **核心问题**：让这个 Pass 跑得快 5 倍，需要哪些**条件同时为真**？哪些条件现在是 false？

---

## 反模式清单（避免这些）

- ❌ "我的 GPU 利用率只有 60%，所以我没满载" → 这是 average utilization，spike 可能藏在里头。要看 stall 占比。
- ❌ "我把所有 `r.Lumen.*` 都调低了，性能没变，所以 Lumen 不是瓶颈" → 你同时改了一堆变量，无法定位任何一个。
- ❌ "这个 Pass 看起来很贵，所以是瓶颈" → 看起来贵 ≠ 真的是瓶颈。要看它在总帧时间里的占比和不可替代性。
- ❌ "Pass A 之后 Pass B 就变贵了，所以 A 在拖累 B" → 可能 B 一直这么贵，只是之前被 A 遮住了。relocation ≠ causation。
- ❌ "硬件 RT 比软件慢，所以软件更好" → 你可能没开硬件 RT 的有效负载（小场景、low trace distance 反而软件更快）。

---

## 与 Lyra + Lumen milestone 的连接

- 主 milestone brief：[[00-README]]
- AI 辅助度判定：[[../../../References/AI-Augmentation-Reference]]
- Lumen 输入侧 AI 任务：[[../../../AI-Tasks/Lumen/00-Master-Index]]
- 综合分析输出落点：`../../../04-性能优化备忘录/瓶颈分析/Lyra-Lumen-Final-Analysis-<日期>.md`（Phase 4）

---

*Created by AI (Mavis) on 2026-06-24 — saved from chat discussion.*  
*Methodology reference, not a phase deliverable.*