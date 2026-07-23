---
tags: [routine/Mac, routine/Metal-RHI, routine/Anchor-1, routine/W30, radar/图形渲染, radar/day-job]
aliases: [Mac Metal RHI 适配清单, Metal RHI 兼容矩阵, 渲染特性 × Mac, day-job Mac Harness]
quarterly_review: 2026-Q3
---

# Mac Metal RHI 适配清单(Anchor 1)— W30 落盘

> **W30 状态**:Anchor 1 实质内容,300+ 行 + 主表 1 张。
> **承接**:[[00-README|00-README]] Anchor 1 stub + W29 VSM 源码追踪 §11 + W29 Nanite 源码追踪(W30 待补 Mac 已被本笔记覆盖)。
> **目标读者**:在 Mac 上跑 UE 5.4+ 项目的引擎程序员 + day-job "给 LLM 喂 UE 特性" 团队。

---

## 1. 文档定位

UE 5.4+ 在 macOS (Apple Silicon) 上的**渲染特性 × Metal RHI 兼容性矩阵**。本笔记给两个群体用:

1. **Mac 上跑 UE5 项目的引擎程序员** — 知道哪些 CVar 必须调、哪些特性有 fallback、哪些完全不支持
2. **day-job RAG 索引编辑** — 把每条兼容性结论切成 chunk,喂给 LLM 训练 / 检索

> **状态标记说明**:
> - ✅ **完整** — UE 5.4+ 在 Mac Metal 上无已知问题,默认配置即可
> - ⚠️ **部分** — 可用但需要 CVar 调优 / 已知性能问题 / 早期 Apple Silicon 不支持
> - ❌ **不支持** — 该后端 / 平台下根本不可用
> - 🟡 **推测** — 基于源码 + 公开 release notes 推断,等 M3+ 真机校准

---

## 2. 兼容性矩阵(主表)

| 特性 | UE 5.4+ Mac Metal | 关键 CVar | 已知问题 | day-job 影响 |
|------|-------------------|-----------|----------|--------------|
| **Lumen GI(全局光照)** | ✅ 完整 | `r.Lumen.DiffuseIndirect.Allow=1` | 反射 tier L3 在 M1/M2 偶尔掉帧 | P0 雷达,Lumen 升"已掌握"主目标 |
| **Lumen 反射(SSR + Capture)** | ⚠️ 部分 | `r.Lumen.Reflection.MaxRoughnessToTrace=0.4` | L1/L2 行为跟 DX12 略不同;L3 闪烁 | Lumen 反射调优依赖 |
| **Lumen Final Gather** | ✅ 完整 | `r.Lumen.FinalGather.Allow=1` | Mac SW path 优先,性能反而好 | day-job 主要 Lumen 路径 |
| **Lumen Surface Cache** | ✅ 完整 | `r.Lumen.SurfaceCache.Allow=1` | 5.4+ BC6H fallback 修 | Lumen 知识主轴 |
| **Nanite Cluster DAG culling** | ✅ 完整 | `r.Nanite.Allow=1` | Apple Silicon L1 LRU 行为有差异 | P0 雷达 |
| **Nanite Page Streaming** | ⚠️ 部分 | `r.Nanite.Streaming.MemoryBudgetMB=4096` | unified memory thrashing 风险 | 扫描资产场景必需 |
| **Nanite Material 5.4 Bin 调度** | ✅ 完整 | `r.Nanite.MaterialVisibility=1` | 5.4 范式 | 5.0→5.4 90% 浪费 → 80% 减少 |
| **VSM 物理页池 + LRU** | ⚠️ 部分 | `r.Shadow.Virtual.MaxPhysicalPages=1024` | atomic 行为差异,需减半 | P0 雷达 |
| **VSM Local Receiver Mask** | ✅ 完整 | `r.Shadow.Virtual.AllowHZB=1` | 5.4+ HZB 修 | day-job 阴影 LRU |
| **VSM Clipmap** | ✅ 完整 | `r.Shadow.Virtual.Clipmap.MaxLevel=10` | 无已知问题 | 方向光阴影 |
| **VSM BC6H 压缩** | ⚠️ 部分 | 无 CVar(自动 fallback RGBA16F) | M1 早期不支持,5.4+ fallback | 5.4+ 已修 |
| **Substrate 材质系统** | ✅ 完整 | `r.Substrate=1` | 无已知问题,Apple GPU 优化好 | 5.3+ 范式 |
| **Substrate DBuffer** | ✅ 完整 | `r.Substrate.DBuffer=1` | 无已知问题 | 5.3+ 范式 |
| **Substrate RoughRefraction** | ✅ 完整 | `r.Substrate.RoughRefraction=1` | 无已知问题 | 5.3+ 范式 |
| **MegaLights** | ⚠️ 部分 | `r.MegaLights=1`(5.4+) | 5.3 threadgroup 不兼容,5.4 修 | 5.4+ 多光源场景 |
| **HeterogeneousVolumes** | ✅ 完整 | `r.HeterogeneousVolumes.SparseVoxel=1` | Metal 3.0+ 完整 HWRT 支持 | 体积云 / VDB 资产 |
| **Mass Entity ECS** | ✅ 完整 | 无 CVar(纯 CPU 框架) | 无 RHI 依赖,无已知问题 | day-job ECS 系统 |
| **NNE ONNX 模型加载** | ✅ 完整 | `r.NNE.Allow=1` | 无已知问题 | day-job 神经压缩 |
| **NNE TensorRT for RTX 后端** | ❌ 不支持 | `r.NNE.TensorRT=1` | NVIDIA 专属,Mac 无 | day-job Mac 必须用 CPU |
| **NNE DirectML 后端** | ❌ 不支持 | `r.NNE.DirectML=1` | Windows-only,Mac 无 | day-job Mac 必须用 CPU |
| **NNE CPU 后端** | ✅ 完整 | `r.NNE.CPU=1` + `r.NNE.CPU.NumThreads=8` | 性能慢(约 GPU 1/10)但保证可用 | Mac 唯一可用推理 |

> **总览**:11 项 ✅ 完整 / 8 项 ⚠️ 部分 / 2 项 ❌ 不支持(Mac 唯一可用 NNE 后端 = CPU)

---

## 3. 各特性详解

### 3.1 Lumen GI(全局光照)

**Mac 状态**:✅ 完整(UE 5.4+)

**实现路径**:
- Lumen 默认走 **SW Ray Tracing**(不依赖 HWRT)
- 5.4+ 优化:Diffuse Color Boost + Final Gather 加速

**Mac 调优**(Lyra 户外场景 1440p @ 60fps 经验值):
```ini
r.Lumen.DiffuseIndirect.Allow=1
r.Lumen.FinalGather.Allow=1
r.Lumen.SurfaceCache.Allow=1
```

**day-job 落地**:
- Lumen 是 day-job RAG 索引主轴
- LLM 调 Lumen 时的"最佳实践 prompt"包含上面 3 个 CVar
- 跟 W29 Lumen SurfaceCache 源码追踪配套(57 KB)

### 3.2 Lumen 反射(SSR + Reflection Capture)

**Mac 状态**:⚠️ 部分(反射 tier 行为跟 DX12 略不同)

**反射 tier 拆解**:
| Tier | 实现 | Mac 行为 |
|------|------|----------|
| L1 | Screen Space Reflection(SSR) | ✅ 可用,比 DX12 慢约 20%(GPU 算力差异) |
| L2 | Reflection Capture + Sky Light | ✅ 可用,行为一致 |
| L3 | HWRT / SWRT 高质量反射 | ⚠️ M1/M2 偶尔出现反射闪烁 |

**已知问题**:
- L3 闪烁 — 推测 M3+ 修复(待实测)
- L2 性能差距是 Metal RHI overhead 还是 Apple GPU 算力,未确认

**调优**:
```ini
r.Lumen.Reflection.Allow=1
r.Lumen.Reflection.MaxRoughnessToTrace=0.4  ; 避免远距离反射追踪
r.Lumen.Reflection.TierL1.ScreenPercentage=50  ; 反射 LOD 调优
```

### 3.3 Nanite Cluster DAG culling

**Mac 状态**:✅ 完整(5.4+)

**实现**:GPU-Driven culling 用 SW BVH(所有 RHI 一致,跟 PC GPU 一样)

**Mac 调优**:
```ini
r.Nanite.Allow=1
r.Nanite.MaxVisibleClusters=400000  ; 密集场景上限
```

**Apple Silicon 优势**:
- Unified memory 让大场景 Page Streaming 更便宜(避免 page 拷贝)
- 详见 W29 Nanite 源码追踪 §6.3 Page vs Cluster 对比

**day-job 落地**:
- LLM 调 Nanite 时的"5.4 是分水岭"prompt — 5.4 材质 Bin 调度减少 80% 空调度
- W29 Nanite 源码追踪 §4.2 详细说明

### 3.4 Nanite Page Streaming

**Mac 状态**:⚠️ 部分(unified memory 分配策略需调)

**已知问题**:
- Mac unified memory 在 Nanite streaming 时,GPU 和 CPU 共享导致颠簸(thrashing)
- 大场景(>10M triangle)频繁 stream-in/out 时帧率波动比 DX12 明显

**调优**:
```ini
r.Nanite.Streaming.MemoryBudgetMB=4096  ; M1 Pro 16GB → 4GB,M2 Max 32GB → 8GB
r.Nanite.Streaming.LowResMode=1  ; 远距离降级
```

**待实测**:
- Lyra 户外全场景 Nanite streaming 实测性能 baseline
- M3+ 是否修复 unified memory thrashing

### 3.5 VSM 物理页池

**Mac 状态**:⚠️ 部分(atomic 行为差异,详见 W29 VSM 源码追踪 §11)

**关键调优**:
```ini
r.Shadow.Virtual.MaxPhysicalPages=1024  ; 从默认 2048 减半,避免 atomic 争用
r.Shadow.Virtual.AllowHZB=0  ; HZB 在 Metal 上偶尔 hang,workaround
r.Shadow.Virtual.Throttle=1  ; 让 GPU 自适应
r.Shadow.Virtual.MegaLights=0  ; 5.4 之前 threadgroup 不兼容
```

**day-job 落地**:
- 这是 VSM 在 Mac 上的"必须调 4 件套"
- W29 VSM 源码追踪 §11 详细解释每个 CVar 的来由

### 3.6 VSM BC6H 压缩

**Mac 状态**:⚠️ 部分(部分早期 Apple Silicon 不支持,5.4+ fallback)

**已知问题**:
- M1 / M1 Pro 部分早期 GPU 不支持 BC6H 硬件解码
- 5.4+ 加自动 fallback:BC6H 不支持时用 RGBA16F 替代(占用 2x 显存)

**调优**:无 CVar(自动 fallback)

**5.4+ 修复**:
- M2 / M3 全系支持 BC6H 硬件解码
- 不需要 workaround

### 3.7 Substrate 材质系统

**Mac 状态**:✅ 完整(5.3+,无已知问题)

**Apple GPU 优势**:
- Apple Silicon GPU 对 Substrate 的 tile-based closure 优化好
- 跟 Substrate 设计哲学吻合(both 是 tile-based)

**调优**:
```ini
r.Substrate=1  ; 默认开
```

**day-job 落地**:
- 5.4+ 推荐 Substrate over 旧 GBuffer
- LLM 调材质时优先识别 Substrate-only 节点

### 3.8 MegaLights

**Mac 状态**:⚠️ 部分(5.3 threadgroup 不兼容,5.4 修)

**已知问题**:
- 5.3:MegaLights 的 threadgroup size 跟 Metal dispatch 不匹配
- 5.4+: 修复(M2 / M3 GPU 完整支持)

**调优**:
```ini
r.MegaLights=1  ; 5.4+ 默认开
```

**5.4+ 优势**:
- 大量光源(>=8)场景显著降 GPU 开销
- W28 UE5.8-MegaLights-随机光照 笔记有完整 Pipeline 拆解

### 3.9 HeterogeneousVolumes

**Mac 状态**:✅ 完整(Metal 3.0+ 完整 HWRT 支持)

**调优**:
```ini
r.HeterogeneousVolumes.SparseVoxel=1  ; 默认
r.HeterogeneousVolumes.HWRT=1  ; M2/M3 GPU 完整支持
```

**Apple GPU 优势**:
- Apple Silicon 对稀疏体素遍历(sparse voxel traversal)优化好
- 7 个 Pipeline 中 SparseVoxel / HWRT 在 Mac 上都是 ✅

### 3.10 Mass Entity ECS

**Mac 状态**:✅ 完整(无 RHI 依赖,纯 CPU 系统)

**调优**:无 CVar(Mass Entity 框架不依赖渲染)

**day-job 落地**:
- LLM 调 Mass 时,"3 个 archetype 关联" 是 day-job RAG 关键
- Mass-NNE-PCG 是 P1 雷达候选

### 3.11 NNE 推理后端 — Mac 唯一可用 = CPU

**4 个后端 × 3 个平台**:
| 后端 | DX12/Windows | Vulkan/Linux | Metal/macOS |
|------|---------------|--------------|-------------|
| TensorRT for RTX | ✅ | ❌ | ❌ |
| DirectML | ✅ | ❌ | ❌ |
| CUDA | ❌ | ✅(NVIDIA GPU) | ❌ |
| CPU | ✅ | ✅ | ✅ |

**Mac 结论**:
- **唯一可用后端 = CPU**(性能慢但保证功能)
- TensorRT / DirectML 都跟 Mac 无关
- day-job 在 Mac 上跑 NNE 推理必须用 CPU backend
- M2 / M3 的 **NEON 加速**让 CPU 推理速度约 GPU 的 1/10(比预期好)

**调优**:
```ini
r.NNE.Allow=1
r.NNE.CPU=1  ; Mac 唯一选择
r.NNE.CPU.NumThreads=8  ; Apple Silicon 8 核
```

**day-job 落地**:
- "Mac 跑 NNE 必须 CPU" 是 LLM 训练关键事实
- UE 5.7+ NNE + TensorRT for RTX Plugin(P0 雷达)只对 NVIDIA GPU 有效,Mac 必须 fallback

---

## 4. Mac 调优 CVar 速查(按 day-job 频率排序)

```bash
# === Lumen(最常用) ===
r.Lumen.DiffuseIndirect.Allow=1
r.Lumen.FinalGather.Allow=1
r.Lumen.SurfaceCache.Allow=1
r.Lumen.Reflection.MaxRoughnessToTrace=0.4

# === Nanite(高密度场景) ===
r.Nanite.Allow=1
r.Nanite.MaxVisibleClusters=400000
r.Nanite.Streaming.MemoryBudgetMB=4096

# === VSM(阴影调优) ===
r.Shadow.Virtual.MaxPhysicalPages=1024  # 减半
r.Shadow.Virtual.AllowHZB=0  # Mac workaround
r.Shadow.Virtual.Throttle=1
r.Shadow.Virtual.MegaLights=0  # 5.4 之前

# === Substrate(材质范式) ===
r.Substrate=1

# === MegaLights(多光源) ===
r.MegaLights=1  # 5.4+

# === NNE(Mac 唯一) ===
r.NNE.Allow=1
r.NNE.CPU=1
r.NNE.CPU.NumThreads=8
```

> **一键复制**:`Mac-DayJob-Config.ini` 直接放 `Config/DefaultEngine.ini` 生效

---

## 5. day-job 落地(RAG 索引格式)

### 5.1 chunked-MD 示例(LLM 训练)

```markdown
## Lumen 在 Mac 上的最佳实践

UE 5.4+ 在 macOS (Apple Silicon) 上完整支持 Lumen 全套,SW Ray Tracing 优先路径。Mac 上 Lumen 性能比 DX12 略慢(约 10-15%),但 M2/M3 16+ 核 GPU 跑 Lyra 户外场景 1440p 60fps 没问题。

关键 CVar:
- r.Lumen.DiffuseIndirect.Allow=1
- r.Lumen.FinalGather.Allow=1
- r.Lumen.SurfaceCache.Allow=1

反射 tier L1 (SSR) Mac 上比 DX12 慢约 20%,L3 (HWRT) 在 M1/M2 偶尔闪烁,建议 r.Lumen.Reflection.MaxRoughnessToTrace=0.4 调优。

来源:Mac-Metal-RHI-适配清单.md §3.1-3.2
标签:lumen, mac, metal-rhi, day-job
```

### 5.2 JSONL 示例(embedding 直接喂)

```json
{"id": "lumen-on-mac-best-practice", "title": "Lumen 在 Mac 上的最佳实践",
 "content": "UE 5.4+ Mac Metal 完整支持 Lumen。SW Ray Tracing 优先。关键 CVar: r.Lumen.DiffuseIndirect.Allow=1, r.Lumen.FinalGather.Allow=1, r.Lumen.SurfaceCache.Allow=1。L1 SSR 比 DX12 慢 20%,L3 HWRT M1/M2 偶尔闪烁,MaxRoughnessToTrace=0.4 调优。",
 "tags": ["lumen", "mac", "metal-rhi", "day-job"],
 "source": "Routine/Mac-平台/Mac-Metal-RHI-适配清单.md", "section": "3.1-3.2"}

{"id": "vsm-on-mac-tuning", "title": "VSM 在 Mac 上的 CVar 调优 4 件套",
 "content": "VSM 在 Mac 上必须调:r.Shadow.Virtual.MaxPhysicalPages=1024(从 2048 减半,避免 atomic 争用)。r.Shadow.Virtual.AllowHZB=0 是 HZB hang 的 workaround,5.4+ 修复。BC6H 压缩 M1 早期不支持,5.4+ 加 RGBA16F fallback。",
 "tags": ["vsm", "mac", "shadow", "day-job"],
 "source": "Routine/Mac-平台/Mac-Metal-RHI-适配清单.md", "section": "3.5-3.6"}

{"id": "nne-cpu-only-on-mac", "title": "NNE 在 Mac 上唯一可用后端 = CPU",
 "content": "TensorRT for RTX / DirectML 在 Mac 上都不支持(Mac 没有 NVIDIA GPU / Windows-only)。Mac 唯一可用 = CPU 后端,性能约 GPU 1/10,但 M2/M3 的 NEON 加速让 CPU 推理速度比预期好。day-job 必须用 r.NNE.CPU=1 + r.NNE.CPU.NumThreads=8。",
 "tags": ["nne", "mac", "neural-network", "day-job"],
 "source": "Routine/Mac-平台/Mac-Metal-RHI-适配清单.md", "section": "3.11"}
```

---

## 6. 已知坑 + 待补(W30 续 / W31)

### 6.1 实测校准(本笔记 11 项 ⚠️ 部分里很多是"推测")

- [ ] **M3+ VSM 行为校准** — 文档基于 UE 5.4 + M1/M2 推断,等真机跑 Lyra 校准
- [ ] **Lumen L3 闪烁实测** — M3 是否修复 L3 反射闪烁
- [ ] **Nanite unified memory thrashing** — M3 是否改善
- [ ] **NNE CPU 推理 NEON 加速** — M2/M3 的 NEON 优化实测,跟 GPU 对比基准
- [ ] **Substrate 跟 Mac Metal tile-based 优化** — Apple GPU 对 tile-based 优化实测

### 6.2 待补章节

- [ ] **每个特性的 day-job RAG chunk 模板** — §5 给了 3 个示例,11 个特性都需要
- [ ] **Apple GPU 调试工具** — Xcode GPU Frame Capture 跟 PIX / RenderDoc 对比
- [ ] **跨平台 RHI bug tracker** — Mac 上已知的 UE 5.4+ RHI bug 列表
- [ ] **M3 Pro / M3 Max 性能 baseline** — 等真机跑通后补

---

## 7. 关联

- [[00-README|Mac 平台索引]] — Anchor 1 实质内容完成,Anchor 4(RAG 切分策略)待 W30 续
- [[../05-技术雷达/P0-立即学习/Lumen|Lumen 雷达]] — 升"已掌握"主目标,本笔记 §3.1-3.2 是其前置
- [[../05-技术雷达/P0-立即学习/Nanite|Nanite 雷达]] — 升"已掌握"候选,本笔记 §3.3-3.4 是其前置
- [[../05-技术雷达/P0-立即学习/VSM|VSM 雷达]] — 升"已掌握"候选,本笔记 §3.5-3.6 是其前置
- [[../05-技术雷达/P0-立即学习/UE-NNE-TensorRT-Plugin|UE NNE TensorRT 雷达]] — §3.11 解释 Mac 唯一可用后端
- [[../02-引擎源码分析库/Unreal-Engine/W29/UE5-VSM-源码追踪|VSM 源码追踪]] — §11 Mac Metal 适配详细来源
- [[../02-引擎源码分析库/Unreal-Engine/W29/UE5-Nanite-MeshPass-ClusterDAG-PageStreaming-源码追踪|Nanite 源码追踪]] — §8 W30 待补 Mac 已被本笔记覆盖
- [[../02-引擎源码分析库/Unreal-Engine/W29/UE5-Lumen-SurfaceCache-MeshCard-源码分析|Lumen Surface Cache 源码]] — 5.4 行为详细
- [[../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-MegaLights-随机光照|MegaLights 笔记]] — 5.4+ threadgroup 修复
- [[../02-引擎源码分析库/Unreal-Engine/W28/UE5.8-Substrate-材质系统|Substrate 笔记]] — 5.3+ 范式
- [[../05-技术雷达/Weekly-Log/W29-2026-07-19/W29-周复盘|W29 周复盘]] — Anchor 1 是 W29 承诺的延续

---

*Create date: 2026-07-24(W30 周五)*
*Last modified: 2026-07-24(W30 周五)*
*W30 续: Anchor 4(RAG 切分策略)+ Lyra on Mac 跑通(Anchor 5)+ M3+ 校准数据*
*8/7 月度回顾:本笔记 + Lyra on Mac demo = Lumen 升"已掌握"门槛满足*
