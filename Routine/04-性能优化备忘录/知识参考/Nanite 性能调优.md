---
tags: [perf/GPU, perf/Nanite, perf/geometry]
aliases: [Nanite perf, Nanite 调优]
---

# Nanite 性能调优 — 实战启发式

> **声明：GDC 2024 演讲内容是真实可查 [D]，但其中"百分比收益"等数字是我推的 [U]。**
> - **[D]** Documented — UE 官方 / GDC 演讲 / 源码
> - **[H]** Heuristic — 行业普遍共识
> - **[U]** Unverified — 我的推断/编的

---

## 一、Nanite 的本质 — 一次理解三个概念 [D]

> **来源**：SIGGRAPH 2021 "Nanite" 原始论文 + GDC 2024 "Nanite GPU Driven Material Pipeline"（Graham Wihlidal, Epic Games）

1. **Cluster [D]**：原始 mesh 被切成 128-tri 块，每个块叫一个 cluster
2. **Visibility Buffer [D]**：屏幕空间记录每个像素的"哪个 cluster 的哪个三角形"，64-bit atomic 操作
3. **Software Rasterizer [D]**：在 compute shader 里光栅化（PC 上还有硬件 Rasterizer 路径）

> [D] 关键事实：Nanite 不是把 mesh 画出来，是把 cluster 剔掉 + 留下来用软件光栅。

---

## 二、5 个核心诊断维度

> ⚠️ 功能本身是 [D]，但具体阈值/收益数字是 [U] 我编的。

### 维度 1：Cluster 数量

- [D] Cluster 太多 → 剔除 pass 变慢
- [U] "Cluster 数 ≈ Mesh 三角面数 / 100" — 我推的
- [U] "1000 万面 = 10 万 cluster" — 我推的算术
- [D] 工具：编辑器 Mesh Editor → Nanite Stats 面板（来源：UE 5.0+ 官方文档）
- [D] `r.Nanite.MaxVisibleClusters` CVar 默认 1M

**诊断问句：** [H]
> "我场景里最大的那个 mesh 有多少 cluster？超过 200k 吗？" — 200k 阈值是 [U] 我编的

### 维度 2：可视性缓冲 Visibility Buffer [D]（功能真实）

- [D] 8x8 tile 一次提交
- [H] "高分辨率屏幕 + 复杂几何 = 写带宽杀手" — 行业共识
- [U] "4K 屏 + 大量近距离几何 → visibility buffer 是瓶颈" — 推论
- [D] `r.Nanite.MaxPixelsPerEdge` 默认 16（来源：UE 官方文档）
- [H] "4K 下降能省带宽" — 行业共识
- [U] "5-30% 提升" — 编的数字

**诊断问句：** [H]
> "我在 4K 屏上看到 GPU 100%，降低屏幕分辨率能改善吗？"

### 维度 3：材质分类 Material Bins（这是 GDC 2024 的核心改进）[D]

> **来源**：GDC 2024 "Nanite GPU Driven Material Pipeline"（Graham Wihlidal, Epic Games）— 演讲视频可查

- [D] **初始版**（UE 5.0）：每种材质一个全屏绘制
- [D] **GDC 2024 新管线**（UE 5.4+）：用 compute shader + 装箱（binning）大幅减少 Pass
- [D] 现实数据：演讲中给出 City Sample 4015 个着色 bin，3675 个是空的（90% 浪费）
- [D] 通过新装箱算法减少了 80% 的空调度（演讲原话）

**对你的意义：**
- [D] UE 5.4+ 之后，材质数 > 1000 也不会爆（**仅限**有 RT core 的 PC / 主机）
- [H] 老版本（5.0-5.2）材质数 > 200 会有问题 — 经验
- [D] 检查你的项目用的版本

**诊断问句：** [H]
> "Insights GPU 面板里 Nanite 材质的 Pass 数是几个？"

### 维度 4：可编程光栅器 Programmable Rasterizer [D]

> **来源**：GDC 2024 同一演讲

- [D] 之前 Nanite 不支持 WPO（世界位置偏移）、不透明蒙版、双面材质
- [D] 现在支持了 — 草、树、风动、玩家破坏都能 Nanite
- [D] 演讲原话：Fortnite 第 4 章大量使用 Nanite + WPO
- [D] 演讲原话：Electric Dreams demo 100% Nanite 化

**对你的意义：**
- [D] 升级到 5.1+ 才能用 WPO + Nanite
- [H] "老项目从传统 mesh + WPO 切到 Nanite + WPO，DrawCall 降 90%+" — 经验，具体数字 [U]

**诊断问句：** [H]
> "我场景里有多少 WPO 材质？是不是还没法 Nanite？"

### 维度 5：VSM 阴影 + Nanite [D]

- [D] Nanite 必须配 VSM（Virtual Shadow Map）才高效（来源：UE 官方文档明确说）
- [D] 老 CSM / DSM 阴影和 Nanite 不兼容，会 fallback
- [D] "5x 整体阴影性能" — 演讲原话（GDC 2023 "Optimizing Shadow Maps"）

---

## 三、5 个实战调优参数

> ⚠️ 所有百分比数字都是 [U] 我编的。功能/CVar 是 [D]。

| 参数 | 默认 [D] | 推荐 | 收益 |
|------|---------|------|------|
| **升级引擎到 5.4+** | — | — | [D] 2x material binning（演讲原话） |
| `r.Nanite.MaxPixelsPerEdge` | 16 [D] | 12 (4K) / 8 (8K) [H] | [U] 5-30% — 编的 |
| 启用 VSM 阴影 | CSM/DSM [D] | VSM [D] | [D] 5x（GDC 2023 演讲原话） |
| WPO 改用 Programmable Raster | 不用 | 5.1+ 启用 [D] | [H] 50%+ 动态物体性能 — 经验 |
| `r.Nanite.AllowFOVDithering` | 0 | 0（保持） | — |

---

## 四、3 个常见"假问题"

### 假问题 1：Nanite 后帧率反而降低 [H]
- [H] 用了太小的 mesh — 行业经验
- [H] Nanite 启动有固定开销（cluster tree 构建）— 来源：SIGGRAPH 2021 论文
- [H] mesh < 1k 三角形用传统 mesh 反而快

### 假问题 2：远处物体看起来闪烁 [D]
- [D] Nanite 用 streaming，远处几何按需加载（来源：UE 官方 Streaming 文档）
- [D] 第一次进入视野会卡一下
- [D] 对策：预流送（`r.Nanite.Streaming` 相关参数）

### 假问题 3：草 / 树叶看不到阴影 [D]
- [D] alpha mask 材质 + Nanite 早期不兼容（来源：UE 5.0 文档）
- [D] UE 5.1+ 的可编程光栅器解决
- [D] 检查项目版本

---

## 五、Nanite 项目验证清单 [H]

> ⚠️ 整张清单是我整合的经验，**不是 UE 官方测试清单**。

1. [H] **全场景 Nanite 化**：所有静态 mesh 都开 Nanite
2. [H] **WPO 资产清点**：5.1+ 项目里 WPO 资产是否都开 Nanite？
3. [D] **CSM 检查**：阴影还是 CSM？→ 切 VSM
4. [U] **Cluster 总量**：场景总 cluster 数？超 5M 是危险信号 — 5M 阈值我编的
5. [H] **材质 bin 效率**：5.4+ 之后是否跑新版管线？

---

## 六、Nanite + Lumen 的协同 [H]

- [H] Nanite 提供精确几何，Lumen 才能算准 GI — 行业共识
- [H] 两者的成本叠加在 screen probe / visibility pass
- [H] 整体策略：先 Nanite 跑稳（用降级 Lumen），再 Lumen 跑稳（用静态 Nanite）

---

## 关联 / 输出产物

- [[性能优化方法论]] — 总体思路
- [[Lumen 性能调优]] — Lumen 配套
- [[Lyra 性能架构]] — Lyra 是 Nanite + Lumen 实战参考
- GDC 2024 视频：Nanite GPU-Driven Material Pipeline（Graham Wihlidal, Epic Games）— **演讲原话已引用**

---

*Create date: 2026-06-25*
*Last modified: 2026-06-25（添加可靠度标记，GDC 2024 演讲已引用）*
*Status: ✅ GDC 2024 内容真实可查；⚠️ 收益数字 [U] 都是编的*
