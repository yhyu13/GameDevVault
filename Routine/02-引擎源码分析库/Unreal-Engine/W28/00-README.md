---
tags: [source/周归档, source/W28, source/UE5.8]
aliases: [W28 Mini-Index, UE5.8 重头戏]
---

# W28 (2026-07-06 ~ 2026-07-12) — UE5.8 重头戏

> 本周 4 个新主题:**MegaLights / Substrate / InstanceCulling / HeterogeneousVolumes** — 都是 day-job "给 LLM 喂 UE 特性" 的高质量语料。

---

## 产出清单

| 主题 | MD | 卡牌 | 大小 | 核心要点 |
|------|:--:|:--:|-----|----------|
| **MegaLights 随机光照** | ✅ | ✅ | 35 KB / 41 KB | 7 步 pipeline + 13 TileType + HWRT/VSM 双模式 + History guide |
| **Substrate 材质系统** | ✅ | ✅ | 31 KB / 43 KB | 4 TileType + Stencil 分类 + DBuffer/RoughRefraction + Tile-based Closure |
| **InstanceCulling GPU 裁剪** | ✅ | ✅ | 35 KB / 53 KB | LoadBalancer 位打包(`ThreadGroupSize=64`, `PrefixBits=6`) + Bin 多 HZB + DeferredContext |
| **HeterogeneousVolumes 体素体积** | ✅ | ✅ | 39 KB / 50 KB | 7 Pipeline(SparseVoxel / VoxelGrid / LiveShading / HWRT / Preshading / MaterialBaking / AO) |

**总计**:8 个文件,~138 KB 源码笔记 + 互动卡牌

## 文件

- [[UE5.8-MegaLights-随机光照]] · [卡牌](./UE5.8-MegaLights-随机光照.html)
- [[UE5.8-Substrate-材质系统]] · [卡牌](./UE5.8-Substrate-材质系统.html)
- [[UE5.8-InstanceCulling-GPU裁剪]] · [卡牌](./UE5.8-InstanceCulling-GPU裁剪.html)
- [[UE5.8-HeterogeneousVolumes-体素体积]] · [卡牌](./UE5.8-HeterogeneousVolumes-体素体积.html)

---

## 与 day-job 的对接

day-job = **RAG + Mac Game Harness,目标"提到 LLM 对 UE 特性的使用"**。这 4 个主题对应的 LLM 训练价值:

| 主题 | 适合喂给 LLM 的内容 | day-job 落地形式 |
|------|---------------------|------------------|
| MegaLights | "大量光源场景的判定式渲染决策树" | RAG 检索语料:遇到 "几百盏灯" 场景时 LLM 应该调用 MegaLights 而不是传统 deferred |
| Substrate | "现代材质 vs legacy GBuffer slot" 的范式对比 | 工具描述:LLM 写材质脚本时识别 Substrate-only 节点 |
| InstanceCulling | "GPU-Driven 渲染管线的决策模式" | 训练数据:让 LLM 理解 LoadBalancer 位打包的并行化思想 |
| HeterogeneousVolumes | "VDB → voxel → ray-march" 完整链路 | 性能档案:LLM 评估体积方案时知道 7 个 pipeline 各自的代价 |

## 本周彩蛋

- **MegaLights 源码 typo**:`DonwnsampledSampleBufferSize` 少一个 'w'(在 `MegaLightsResolve.cpp:979`),可作面试谈资 — "看 UE 源码也能挑 typo 😏"

---

## 待办 / 后续

- [ ] **MegaLightsViewState 完整状态机** — MD 提了 `bSamplesGenerated / bVolumeSamplesGenerated / bVolumeRaysTraced / bVolumeLightingResolved` 4 个 bool,但完整 state 转移图没展开
- [ ] **Substrate BSDF 闭包图** — `FSubstrateBSDF` / `FSubstrateIntegrationFunction` 还没单独拆,这是 Substrate 真正"取代旧管线"的算法核心
- [ ] **同步进 day-job RAG 索引** — 待确认 chunked-MD 还是 JSONL 格式(chunked-MD 跟 Obsidian vault 复用成本低,JSONL 适合直接喂 embedding)
- [ ] W26/W27 mini-README 补齐(模板已成型,复制改日期即可)

---

## 关联

- [[../../00-README|02-引擎源码分析库 根 README]] — 全库索引
- [[../../../07-日记/周模板|周模板]] — day-job 周节奏对齐(07-日记 系统未来按 2026-W##/ 归档时复用)
- [[../../../05-技术雷达/00-README|技术雷达]] — P0 待补 Lumen/Nanite/VSM(W28 没动这轴,但下个周期要把 P0 雷达补齐)

---

*W28 mini-README 模板:W29 起复制本文件改日期 + 主题清单即可。*