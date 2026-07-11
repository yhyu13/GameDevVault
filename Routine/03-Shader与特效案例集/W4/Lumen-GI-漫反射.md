---
tags: [shader/自研, shader/post-process, shader/performance, shader/UE, shader/compute, shader/lumen, shader/AI-accelerated]
aliases: [Lumen GI, Diffuse GI, Voxel Cone Tracing, Surface Cache, Final Gather]
week: W4
cycle: B
---

# Lumen GI 漫反射 (Lumen Global Illumination — Diffuse)

| 字段 | 内容 |
|------|------|
| **效果名称** | Lumen GI 漫反射（Surface Cache + Voxel Cone Tracing + Final Gather） |
| **类型** | 后处理 / 全局光照 / 软件 RT |
| **平台** | PC / Console (Mobile 不支持) |
| **创建日期** | 2026-07-01 |
| **参考来源** | 参考自 UE5 Lumen Global Illumination `LumenSceneRendering.cpp` + GDC 2022 "Lumen: Global Illumination" + SIGGRAPH 2021 "Hardware-Accelerated Ray Tracing in Unreal Engine 5" + Crassin et al. "Aggregate G-Buffer Anti-Aliasing" 论文 |
| **前置阅读** | [[../W3/Lumen-反射降级]] [[../99-归档/体积云-Volumetric-Cloud]] |

---

## 效果截图

![室内 GI](assets/lumen_gi_indoor.png)  
*室内 GI：彩色 bounce light 把白墙染成漫反射颜色*

![户外天空](assets/lumen_gi_outdoor.png)  
*户外：sky light 主导 + 地面 bounce back*

![Final Gather 探针](assets/lumen_gi_probes.png)  
*屏幕空间探针分布，每个探针做 octahedral irradiance*

![漏光问题](assets/lumen_gi_leaking.png)  
*已知问题 #1：墙面"漏光"，需要 solid angle 修正*

---

## 核心概念

Lumen GI 漫反射 = **3 个 pass 串起来的管线**，每个解决不同子问题：

```
                   ┌──────────────────┐
   Scene → Pass 1: │ Surface Cache    │  ← 网格体素化 + 材质 (每帧/每 N 帧)
                   └────────┬─────────┘
                            ▼
                   ┌──────────────────┐
                   │ Lighting Cache   │  ← 每个 voxel 算一次直接光 (sky+sun)
                   └────────┬─────────┘
                            ▼
                   ┌──────────────────┐
                   │ Final Gather     │  ← 每像素：采样周围 probe 拿 octahedral
                   │ (Probe-based)    │     irradiance,做 diffuse 反弹
                   └────────┬─────────┘
                            ▼
                   ┌──────────────────┐
                   │ Voxel Cone Trace │  ← Probe 没覆盖到的区域:cone-march
                   │ (Fallback)       │     拿 distant bounce
                   └────────┬─────────┘
                            ▼
                       Final GI
```

| Pass | 目的 | 频率 | 性能 |
|------|------|------|------|
| **Surface Cache** | 网格 → 3D voxel atlas | 每帧 (增量) | 0.3-0.8ms |
| **Lighting Cache** | 每 voxel 算直接光 (sky+sun) | 每帧 | 0.2-0.4ms |
| **Final Gather** | 屏幕空间探针采样,octahedral irradiance | 每帧 | 1.2-2.0ms |
| **Voxel Cone Trace** | probe 覆盖不到的区域,cone-march 兜底 | 每帧 (可选) | 0.5-1.0ms |

> 室内 / 户外走不同侧重：
> - **户外** — Final Gather 占主导 (sky light 强,probe 直接拿到)
> - **室内** — Voxel Cone Trace 占主导 (probe 难铺开,要 voxel 漫射)

---

## 概念链（Concept Chain）— 从"为什么 GI 要 4 个 pass"到"NRC 能替换什么"

读代码前先把动机链条理清楚。这一节给初学者一个"4 步推理链"，把后面所有技术细节挂在因果链上，不容易迷失。

### Step 1: 业务痛点 — 漫反射 GI 是 3A 渲染的"灵魂"

GI（Global Illumination）让玩家感受到"光线在场景里反弹"——彩色 bounce light、白墙被天空染蓝、室内角落的彩色染色。这是 3A 渲染里"一眼就看出 3A 还是 indie"的关键。

但 GI 实现有 3 大难点：

| 难点 | 表现 |
|------|------|
| **多次弹射** | 漫反射是递归的，光从 A 弹到 B 弹到 C... |
| **屏幕外贡献** | 玩家视野外的物体也要贡献 GI（走廊尽头反射） |
| **动态几何** | 角色 / 移动物体要每帧参与 GI 计算 |

Lightmap（烘焙 GI）只能解决静态场景；动态 GI 必须 runtime 算。

### Step 2: 传统局限 — 为什么单一方案解不掉

| 方案 | 原理 | 优势 | 致命缺陷 |
|------|------|------|---------|
| **Lightmap 烘焙** | 离线 path trace → 烘焙贴图 | 静态完美 | 动态物体没 GI |
| **Light Propagation Volume (LPV)** | 网格化 3D 空间传播 | 实时 | 多次弹射模糊 |
| **Screen Space GI (SSGI)** | G-buffer cone trace | 0ms 开销 | 屏幕外失效、leaking |
| **Path Tracing** | 实时路径追踪 | 真 GI | 性能爆炸（需要 1024 spp） |

**为什么单一方案解不掉**：3 个难点互相对立，**生产环境必须混合管线**。

### Step 3: Lumen 4-Pass 管线 — 动态组合 4 个 Pass

Lumen 的 GI 漫反射用 **4 个 pass 串起来**：

```
Scene
   │
   ▼
Pass 1: Surface Cache (网格 → 3D voxel atlas)
   │   频率: 每帧 (增量)
   ▼
Pass 2: Lighting Cache (每 voxel 算直接光)
   │
   ▼
Pass 3: Final Gather (屏幕探针采样 + octahedral irradiance)
   │
   ▼
Pass 4: Voxel Cone Trace (probe 覆盖不到时兜底)
   │
   ▼
Final GI
```

**每个 Pass 的目的**：

| Pass | 解决什么 | 室内 / 户外侧重 |
|------|---------|----------------|
| **Surface Cache** | 场景几何 → 离屏 voxel 表达 | 都用 |
| **Lighting Cache** | voxel 直接光预计算 | 都用 |
| **Final Gather** | 屏幕空间探针采样（快路径） | **户外主导**（sky light 强） |
| **Voxel Cone Trace** | probe 覆盖不到（兜底） | **室内主导**（probe 难铺开） |

### Step 4: 落地路径 — NRC 能替换什么

AI 加速思路：**用 MLP 学 GI radiance，把离屏存储替换为在线推理**。

| 层次 | 替换对象 | VRAM 节省 |
|------|----------|---------|
| **L1 FG k-NN 加速** | 256 probe → 64 probe + MLP refine | probe atlas 4× 小 |
| **L2 Neural Cone Trace** | VCT 16 step → MLP 出 radiance | 不需要 voxel atlas |
| **L3 Neural Radiance Cache (NRC)** | 整个 GI lookup → NeRF query | **VRAM 50 MB → 150 KB** |

**对比 Lumen Surface Cache vs NRC**：

| 维度 | Lumen Surface Cache | NRC |
|------|---------------------|-----|
| VRAM | ~50 MB | ~150 KB |
| 收敛帧数 | 1 frame | 30+ frames |
| 多次弹射 | 显式 screen probe | 隐式 MLP |
| 动态光源响应 | 1 frame | 1-2 秒（fine-tune） |
| 室内表现 | 好 | 优 |
| 室外表现 | 好 | 一般 |

**对 day-job 的核心价值**：本笔记是 day-job **神经 GI / Lumen 替代方案** 主线的核心案例——4-Pass 管线 + AI 加速三层方案都是 day-job RAG 检索的关键素材。

---

## 核心代码

### C++ 端 — Surface Cache 增量更新

```cpp
// LumenScene.cpp — 增量更新 Surface Cache
// Lumen 用 Card UID 跟踪 mesh 变化,只重新体素化 changed parts
void UpdateSurfaceCache(FLumenSceneData& Scene, FRDGBuilder& GraphBuilder)
{
    // 1. 找出变动的 mesh (transform / material / 添加 / 删除)
    TArray<FCardId> ChangedCards = Scene.DetectChangedCards();
    TArray<FCardId> NewCards     = Scene.DetectNewCards();
    TArray<FCardId> RemovedCards = Scene.DetectRemovedCards();

    // 2. 释放 removed card 的 voxel 区域
    for (FCardId Removed : RemovedCards)
    {
        Scene.SurfaceCacheAllocator.Free(Removed.voxelRange);
    }

    // 3. 为新 card 分配 voxel 空间 (Card UUID 决定 hash 位置)
    for (FCardId NewCard : NewCards)
    {
        FCardPageTableEntry Entry;
        Entry.pageTableOffset = Scene.SurfaceCacheAllocator.Allocate(NewCard.bounds);
        Scene.CardPageTable[NewCard.uid] = Entry;
    }

    // 4. 把变动 mesh 体素化到 cache (compute shader)
    Scene.MeshVoxelizationCS->BuildVoxels(
        GraphBuilder,
        ChangedCards + NewCards,
        Scene.SurfaceCacheAtlas,
        Scene.SurfaceCacheAllocator);
}
```

### HLSL — Voxel Cone Tracing (Fallback Pass)

```hlsl
// LumenVoxelTracing.usf — Diffuse GI 的 voxel cone 步进
// 这是 Lumen GI 的"远场"路径 — 屏幕探针覆盖不到时走这个
Texture3D<float4> SurfaceCacheRadiance;   // voxel 化后的 radiance (RGB + alpha)
float3 VoxelGridOrigin;                    // voxel 网格原点 (世界空间)
float3 VoxelGridExtent;                    // voxel 网格范围
float  VoxelSize;                          // 单 voxel 尺寸 (cm)

float3 VoxelConeTrace(float3 origin, float3 dir, float coneAngle, int maxSteps)
{
    float3 accum = 0;
    float  occlusion = 1.0;
    float  dist = VoxelSize * 2.0;          // 起点偏一个 voxel 避免自相交
    float  diameter = 0;

    [loop]
    for (int i = 0; i < maxSteps; ++i)
    {
        float3 p = origin + dir * dist;

        // 1. 检查 p 是否在 voxel 网格内
        if (!IsInsideVoxelGrid(p)) break;

        // 2. 采样当前 voxel (带 trilinear)
        float3 uvw = (p - VoxelGridOrigin) / VoxelGridExtent;
        float4 voxel = SurfaceCacheRadiance.SampleLevel(LinearSampler, uvw, 0);

        // 3. 累积 radiance + 应用 occlusion
        //    alpha = 表面覆盖率,类似 Beer-Lambert 衰减
        float3 light = voxel.rgb;
        float  alpha = voxel.a;
        accum += light * alpha * occlusion;
        occlusion *= (1.0 - alpha);

        // 4. 早期退出
        if (occlusion < 0.01) break;

        // 5. 自适应步长 — 越远步长越大,锥角越宽
        //    diameter = 当前锥截面直径,不能小于 voxel 尺寸
        dist  += max(VoxelSize, diameter);
        diameter = 2.0 * tan(coneAngle * 0.5) * dist;
    }

    return accum;
}
```

### HLSL — Final Gather (屏幕探针采样)

```hlsl
// LumenFinalGather.usf — Probe-based Diffuse GI
// 关键:Lumen 维护一个"动态探针"集合,每帧在屏幕空间采 ~256 个
StructuredBuffer<FLumenProbe> LumenProbes;       // 当前帧的探针列表
StructuredBuffer<FIrradianceProbe> IrradianceProbes;  // 探针的 octahedral 数据

float3 PS_FinalGather(VS_OUTPUT input) : SV_Target
{
    float3 worldPos = ReconstructWorldPos(input.positionCS, input.deviceZ);
    float3 worldNormal = input.worldNormal;

    // 1. 找出最近的 N 个探针 (k-NN)
    const int k = 8;
    FLumenProbe neighbors[k];
    int numFound = FindNearestProbes(worldPos, /*radius=*/_ProbeSearchRadius, neighbors, k);

    // 2. 加权插值 — 距离越近、normal 越对齐,权重越高
    //    Lumen 用 "Bilinear by Inverse Distance" 权重,不是简单平均
    float3 result = 0;
    float  totalWeight = 0;

    [unroll]
    for (int i = 0; i < k; ++i)
    {
        if (i >= numFound) break;

        FLumenProbe probe = LumenProbes[neighbors[i].atlasIndex];
        FIrradianceProbe irrad = IrradianceProbes[neighbors[i].atlasIndex];

        // 3. 沿 normal 方向采样 octahedral irradiance
        //    Lumen 用 octahedral encoding 存 4x4 = 16 个方向的 irradiance
        float3 sampleNormal = worldNormal;
        float3 irradiance = SampleOctahedralIrradiance(irrad, sampleNormal);

        // 4. 距离 + 角度衰减权重
        float dist = length(probe.worldPos - worldPos);
        float ndotn = saturate(dot(probe.worldNormal, worldNormal));
        float weight = (ndotn * ndotn) / (1.0 + dist * dist * 0.001);

        result += irradiance * weight;
        totalWeight += weight;
    }

    // 5. Fallback — 没找到探针就 cone trace 兜底
    if (totalWeight < 0.001)
    {
        // 沿 normal 上半球 5 个方向各做一次 cone trace,平均
        result = 0;
        const float3 dirs[5] = {
            worldNormal,
            normalize(worldNormal + float3( 0.3, 0.0,  0.3)),
            normalize(worldNormal + float3(-0.3, 0.0,  0.3)),
            normalize(worldNormal + float3( 0.0, 0.0, -0.3)),
            normalize(worldNormal + float3( 0.0, 0.0,  0.3))
        };
        for (int j = 0; j < 5; ++j)
            result += VoxelConeTrace(worldPos + worldNormal * 1.0, dirs[j], 0.5, 16);
        result /= 5.0;
    }
    else
    {
        result /= totalWeight;
    }

    // 6. 与环境光 / 直接光合成
    float3 skyLight = SampleSkyLight(worldNormal);
    return skyLight * 0.3 + result * _LumenIndirectColor;
}
```

---

## 代码逐行讲解（Code Walkthrough）— 3 段代码各在做什么

> 这一节专门给"读完代码还是不知道在干嘛"的初学者。每个代码块对应一段讲解：**意图 / 关键参数 / 边界条件**。

### 代码块 1: `UpdateSurfaceCache` (C++ 增量更新)

**意图**：用 Card UID 跟踪 mesh 变化，**只重新体素化 changed parts**，避免每帧全量重建。

```cpp
void UpdateSurfaceCache(FLumenSceneData& Scene, FRDGBuilder& GraphBuilder)
{
    // 1. 找出变动的 mesh
    TArray<FCardId> ChangedCards = Scene.DetectChangedCards();
    TArray<FCardId> NewCards     = Scene.DetectNewCards();
    TArray<FCardId> RemovedCards = Scene.DetectRemovedCards();

    // 2. 释放 removed card 的 voxel 区域
    for (FCardId Removed : RemovedCards)
        Scene.SurfaceCacheAllocator.Free(Removed.voxelRange);

    // 3. 为新 card 分配 voxel 空间 (UUID 决定 hash 位置)
    for (FCardId NewCard : NewCards) {
        FCardPageTableEntry Entry;
        Entry.pageTableOffset = Scene.SurfaceCacheAllocator.Allocate(NewCard.bounds);
        Scene.CardPageTable[NewCard.uid] = Entry;
    }

    // 4. 把变动 mesh 体素化到 cache (compute shader)
    Scene.MeshVoxelizationCS->BuildVoxels(GraphBuilder,
        ChangedCards + NewCards, Scene.SurfaceCacheAtlas, Scene.SurfaceCacheAllocator);
}
```

**关键参数为什么**：
- **Card UID 跟踪**：每个 mesh 分配一个 UUID（基于 mesh 资源 ID + actor GUID），UUID 不变 = 不用重新体素化
- **Page Table**：Hash map，UUID → voxel range offset，避免连续内存分配
- **BuildVoxels 是 compute shader**：并行体素化，每个 voxel 一个 thread

**边界条件**：
- Removed card 必须先 Free 再 Allocate，否则 allocator 可能撞 hash 槽
- Changed + New 合并后传给 BuildVoxels，**避免重复处理**

### 代码块 2: `VoxelConeTrace` (HLSL 兜底 Pass)

**意图**：当 Final Gather probe 覆盖不到时，用 voxel cone-march 拿 distant bounce。

```hlsl
float3 VoxelConeTrace(float3 origin, float3 dir, float coneAngle, int maxSteps)
{
    float3 accum = 0;
    float  occlusion = 1.0;
    float  dist = VoxelSize * 2.0;          // 起点偏一个 voxel 避免自相交
    float  diameter = 0;

    for (int i = 0; i < maxSteps; ++i) {
        float3 p = origin + dir * dist;

        if (!IsInsideVoxelGrid(p)) break;   // 越界

        float3 uvw = (p - VoxelGridOrigin) / VoxelGridExtent;
        float4 voxel = SurfaceCacheRadiance.SampleLevel(LinearSampler, uvw, 0);

        // 累积 radiance + Beer-Lambert 衰减
        float3 light = voxel.rgb;
        float  alpha = voxel.a;
        accum += light * alpha * occlusion;
        occlusion *= (1.0 - alpha);

        if (occlusion < 0.01) break;        // 早期退出

        // 自适应步长：越远步长越大，锥角越宽
        dist  += max(VoxelSize, diameter);
        diameter = 2.0 * tan(coneAngle * 0.5) * dist;
    }

    return accum;
}
```

**关键参数为什么**：
- **`dist = VoxelSize * 2.0`**：起点偏一个 voxel 避免自相交（**否则会读到 surface cache 自身的高亮度**，整面墙都白）
- **`occlusion *= (1.0 - alpha)`**：Beer-Lambert 衰减，**alpha 累积遮挡**，模拟多次弹射吸收
- **`occlusion < 0.01` 早期退出**：穿透足够后停止，节省步骤
- **`dist += max(VoxelSize, diameter)`**：自适应步长，**保持锥截面直径 ≥ voxel 尺寸**，否则相邻 voxel 重复采样浪费

**边界条件**：
- `IsInsideVoxelGrid`：voxel grid 是有限大小，**origin 在 grid 外时直接 break**
- `diameter = 2.0 * tan(coneAngle * 0.5) * dist`：tan 0 角度 = 0，要确保 `coneAngle > 0`
- trilinear sampler 在 voxel 边界会插值，**避免硬切**

### 代码块 3: `PS_FinalGather` (HLSL 屏幕探针采样)

**意图**：每像素找最近的 k 个 probe，加权采样 octahedral irradiance。

```hlsl
float3 PS_FinalGather(VS_OUTPUT input) : SV_Target
{
    float3 worldPos = ReconstructWorldPos(input.positionCS, input.deviceZ);
    float3 worldNormal = input.worldNormal;

    const int k = 8;
    FLumenProbe neighbors[k];
    int numFound = FindNearestProbes(worldPos, _ProbeSearchRadius, neighbors, k);

    float3 result = 0;
    float  totalWeight = 0;
    for (int i = 0; i < k; ++i) {
        if (i >= numFound) break;

        FLumenProbe probe = LumenProbes[neighbors[i].atlasIndex];
        FIrradianceProbe irrad = IrradianceProbes[neighbors[i].atlasIndex];

        // 沿 normal 采样 octahedral irradiance
        float3 sampleNormal = worldNormal;
        float3 irradiance = SampleOctahedralIrradiance(irrad, sampleNormal);

        // 距离 + 角度衰减权重
        float dist = length(probe.worldPos - worldPos);
        float ndotn = saturate(dot(probe.worldNormal, worldNormal));
        float weight = (ndotn * ndotn) / (1.0 + dist * dist * 0.001);

        result += irradiance * weight;
        totalWeight += weight;
    }

    // Fallback：没找到 probe 就 cone trace 兜底
    if (totalWeight < 0.001) {
        result = 0;
        const float3 dirs[5] = {
            worldNormal,
            normalize(worldNormal + float3( 0.3, 0.0,  0.3)),
            normalize(worldNormal + float3(-0.3, 0.0,  0.3)),
            normalize(worldNormal + float3( 0.0, 0.0, -0.3)),
            normalize(worldNormal + float3( 0.0, 0.0,  0.3))
        };
        for (int j = 0; j < 5; ++j)
            result += VoxelConeTrace(worldPos + worldNormal * 1.0, dirs[j], 0.5, 16);
        result /= 5.0;
    } else {
        result /= totalWeight;
    }

    float3 skyLight = SampleSkyLight(worldNormal);
    return skyLight * 0.3 + result * _LumenIndirectColor;
}
```

**关键参数为什么**：
- **k=8 个 probe**：8 是 GPU warp 大小（NVIDIA 32, AMD 64），8 个 probe 一个 warp 处理满
- **`ndotn * ndotn`**：法线对齐权重平方，**让 normal 不对齐的 probe 投票权急剧下降**，避免跨表面 GI 错误
- **`(1.0 + dist * dist * 0.001)`**：inverse distance weight，**距离平方反比**，远 probe 投票权低
- **5 方向 fallback**：上下半球 5 个方向各做一次 cone trace，**模拟漫反射积分**
- **`skyLight * 0.3 + result * _LumenIndirectColor`**：sky light 直接贡献 30%，剩余 70% 来自 GI，**避免 GI 不足时全黑**

**边界条件**：
- `totalWeight < 0.001`：probe 都没找到（屏幕边缘 / 探针稀疏区域）→ cone trace 兜底
- `worldPos + worldNormal * 1.0`：起点偏 1cm 避免 self-intersection
- `_LumenIndirectColor` 用来调 GI 色调和强度，默认 (1, 1, 1)

---

## 参数解释

| 参数名 | 类型 | 范围 | 含义 | 调参建议 |
|--------|------|------|------|----------|
| `VoxelSize` | float | 5~50 (cm) | Surface Cache 体素尺寸 | 25 户外 / 10 室内,越小越精确但越贵 |
| `_ProbeSearchRadius` | float | 100~2000 (cm) | 找 probe 的搜索半径 | 500 平衡,室内可降到 200 |
| `_MaxFinalGatherSteps` | int | 4~32 | 每个 probe 漫反射采样步数 | 12 标准,20 高质量 |
| `_ConeAngle` | float | 0.1~1.0 (rad) | Cone trace 起始锥角 | 0.5 默认,0.3 锐利 |
| `_MaxConeSteps` | int | 8~64 | Cone trace 最大步数 | 16 标准,32 高质量 |
| `_BounceCount` | int | 1~4 | 漫反射反弹次数 | 2 标准,3+ 室内彩色 bounce |
| `_LumenIndirectColor` | float3 | HDR color | GI 强度 / 色调 | 默认 (1,1,1) |
| `r.Lumen.DiffuseIndirect` | CVar | 0/1/2 | 0=关 / 1=FinalGather / 2=全部 | 默认 2 (FG + VCT) |
| `r.Lumen.ProbeSpacing` | float | 0.5~2.0 | 探针空间间距 (屏幕像素) | 1.0 标准,2.0 性能优先 |

---

## 指标手册（Metric Guide）— 每个参数到底在测什么 / 为什么是这个值

> 9 个参数是 Lumen GI 调参的"入口"。初学者常见误区是"看到参数随便填一个"——这一节告诉你每个参数的"测什么 / 默认值为什么 / 阈值含义 / 怎么调"。

| 参数 | 测什么 | 默认值来源 | 阈值含义 | 怎么调 |
|------|-------|-----------|---------|--------|
| `VoxelSize` | Surface Cache 体素尺寸 | 25cm 户外 / 10cm 室内 | 5cm 内存 ×8，50cm 粗糙 | 1km² 户外 = 25cm，100m² 室内 = 5-10cm |
| `_ProbeSearchRadius` | probe 搜索半径 | 500 cm | < 200 cm probe 稀疏，> 1000 cm 远距噪声 | 室内 200-300 cm，户外 800 cm |
| `_MaxFinalGatherSteps` | 每个 probe 漫反射采样步数 | 12（标准） | < 8 噪点多，> 24 边际递减 | 性能不够降到 8，质量不够升到 20 |
| `_ConeAngle` | VCT 锥角 | 0.5 rad（≈30°） | < 0.3 锐利但慢，> 0.8 太钝 | 室内 0.4，户外 0.7 |
| `_MaxConeSteps` | VCT 最大步数 | 16（标准） | < 8 远处反弹丢失，> 32 边际 | 性能不够降到 8，质量不够升到 32 |
| `_BounceCount` | 漫反射反弹次数 | 2（标准） | 1 = 单反弹，3+ = 多次但色彩过饱和 | 户外 1-2，室内 2-3（限色衰减 LUT） |
| `_LumenIndirectColor` | GI 色调 / 强度 | (1, 1, 1) | HDR color，可调暖 / 冷 | 艺术风格化用，物理拟真保持 (1,1,1) |
| `r.Lumen.DiffuseIndirect` | GI 模式 | 2（FG + VCT） | 0 = 关，1 = FG only，2 = FG + VCT | 调试时切档验证，生产保持 2 |
| `r.Lumen.ProbeSpacing` | 探针屏幕间距 | 1.0（像素） | 0.5 密集但慢，2.0 稀疏但快 | 性能不够升到 2.0，质量不够降到 0.5 |

### 3 个常被误用的参数

#### `VoxelSize` 不是越小越精确

直觉："5cm 体素比 25cm 精度高 5 倍"。**对，但 1km³ 场景内存 256 GB 爆**。

| 场景尺度 | 推荐 VoxelSize | voxel 数 | VRAM |
|---------|---------------|---------|------|
| 100m² 室内 | 5 cm | 8 × 10⁶ | 256 MB ✅ |
| 100m² 室内 | 25 cm | 1.3 × 10⁵ | 4 MB ✅ |
| 1km² 户外 | 5 cm | 8 × 10⁹ | **256 GB** 💥 |
| 1km² 户外 | 25 cm | 6.4 × 10⁷ | 2 GB ✅ |
| 1km² 户外 | 50 cm | 8 × 10⁶ | 256 MB ✅ |

**经验法则**：体素数 = (场景半径 / 体素尺寸)³。**VRAM 应控制在 200 MB 以内**。

#### `_BounceCount` 不是越多越好

直觉："3 次反弹比 1 次反弹更准确"。**对，但色彩会过饱和**——多次 bounce 后墙面颜色叠加成"圣诞树"。

| Bounce | 室内彩色 bounce | 户外天空反弹 | 性能 |
|--------|----------------|-------------|------|
| 1（单反弹） | 弱（白墙） | 蓝灰 | +0.5 ms |
| 2（默认） | 自然 | 蓝灰偏蓝 | +1.0 ms |
| 3（多次） | 强（开始过饱和） | 偏深蓝 | +2.0 ms |
| 4+ | 严重过饱和 | 偏紫 | +3.0 ms |

**正解**：bounce count 限到 2-3，**加色彩衰减 LUT**（每 bounce 衰减 0.7-0.8）防止过饱和。

#### `r.Lumen.ProbeSpacing` 越密越慢但有极限

直觉："间距 0.5 像素比 2.0 像素 probe 多 4 倍，更准"。**对，但 GPU 端 k-NN 搜索开销线性增加**。

| Spacing | probe 数（1080p） | 搜索开销 | 视觉差异 |
|---------|------------------|---------|---------|
| 0.5 | ~8K | 4 ms | 完美（视觉饱和） |
| 1.0（默认） | ~2K | 1.5 ms | 好（不可见差异） |
| 2.0 | ~500 | 0.5 ms | 边缘略粗糙 |

**经验法则**：**1.0 是 sweet spot**，0.5 性能翻倍但视觉无差异，2.0 性能省但能看到 probe 边界。

---

## 性能分级

| 档位 | 改动 | 性能 | 适用 |
|------|------|------|------|
| **关 (Cheap)** | 关闭 Lumen GI,纯环境光 | ~0ms | Mobile / 低端 |
| **Final Gather only** | 256 probes,1 bounce,12 steps | 1.2-1.8ms | **户外默认** |
| **FG + VCT** | 256 probes + 16 cone steps,2 bounces | 2.5-3.5ms | **室内默认** |
| **FG + VCT + 多 bounce** | 256 probes + 32 cone steps,3 bounces | 4.0-6.0ms | 室内彩色 bounce |
| **混合 (生产用)** | FG 主路径 + 远处 VCT 兜底 + Half-res | 2.0-3.0ms | 商业项目默认 |

> Lumen GI 的真正常用配置是 **混合策略**：屏幕内用 Final Gather (快),屏幕外 / probe 稀疏区域用 VCT 兜底,室内 + 户外各一套参数。

---

## 变体版本

- **版本 A：Half-resolution Final Gather** — 在 0.5x 分辨率跑 FG,合成时双线性上采样,省 50% 时间
- **版本 B：Static-only Surface Cache** — 假设场景静态,Surface Cache 只在 Load 阶段烘焙一次,运行时只更新少量移动物体
- **版本 C：RT 混合** — 室内用 Lumen,室外大场景切到 Hardware RT (DXR),避开 VCT 内存
- **版本 D：自研 mini-GI** — 不上 Lumen,自己用 "4 个反射探针 + cubemap blur" 凑一个廉价 GI,适合老硬件

---

## 已知问题与限制

1. **漏光 (Light Leaking)** — **最经典 GI 伪影**。体素粒度粗,光从墙"缝隙"漏到墙另一侧。解决方案:Card 分层 + 厚度估计,或在 Final Gather 时加 solid angle 修正。
2. **Voxel Aliasing** — 物体轮廓处体素边界清晰可见。解决方案:体素尺寸 + trilinear + temporal jitter (TAA 风格)。
3. **Cache 失效风暴** — 大量小物体移动时,Surface Cache 增量更新阻塞主线程。解决方案:batched update + priority queue,优先更新视野内对象。
4. **Temporal 闪烁** — 摄像机快速平移时,probe 分布骤变,GI 出现闪烁。解决方案:temporal probe 累积 + history reprojection。
5. **场景大 → 内存爆** — 1km² 户外场景 voxel atlas 轻松 1GB+ 显存。解决方案:streaming + tile-based,远处用更粗的 voxel (LOD)。
6. **彩色 bounce 不真实** — 多次反弹后颜色饱和,墙面颜色叠加成"圣诞树"。解决方案:bounce count 限到 2 + 颜色衰减,或加色彩平衡 LUT。
7. **动态光源跟不上** — 5+ 移动光源 (爆炸、火焰) 时,Lighting Cache 更新成为瓶颈。解决方案:对 dynamic lights 做 importance-based 采样,不每帧都更新。

---

## 常见误读（Common Misreading）— 5 个初学者陷阱

> 这一节列的是"读文档时容易形成、但实际是错的"理解。每条都是 day-job 真实踩过的坑。

### 误区 1："4-Pass 都要开才是完整 GI"

**你以为**：Surface Cache + Lighting Cache + Final Gather + Voxel Cone Trace 全部启用 = 最强 GI。
**实际**：**全部启用是 4-6 ms 性能炸弹**，生产环境用混合策略只开其中 2-3 个。

**正解**：
- 户外：Final Gather（sky light 主导）+ 关 VCT
- 室内：Final Gather（近距）+ VCT（远距兜底），关 Lighting Cache 单独跑
- 移动端：只开 Final Gather，256 probe + 1 bounce

### 误区 2："漏光是 Lumen 的 bug"

**你以为**：墙面"漏光"是 Lumen 实现错误，应该修。
**实际**：**漏光是 Voxel Cone Tracing 的固有限制，不是 bug**——体素粒度粗，光从墙"缝隙"漏到墙另一侧。

**为什么**：
- 体素是 3D 网格，**两个相邻 voxel 之间的边界墙**没法编码厚度
- cone trace 直接穿过边界，**看到墙另一侧的光**

**正解**：
- Card 分层 + 厚度估计（UE5 Lumen 的解决方案）
- Final Gather 加 solid angle 修正
- 减小体素尺寸（5 cm vs 25 cm）— 但内存爆炸

### 误区 3："Probe 越多 GI 越准"

**你以为**：256 → 1024 probe GI 质量翻倍。
**实际**：**probe 数量 256 已是 GPU warp 满载，更多 probe 视觉无差异但 k-NN 搜索开销线性增加**。

**正解**：
- 256 probe 是 sweet spot，**生产环境保持默认**
- 视觉差异不明显，**性能翻倍不划算**
- 比加 probe 数更有效：**调 probe 分布**（用 importance sampling 让 probe 集中在视觉敏感区域）

### 误区 4："Bounce 越多 GI 越真实"

**你以为**：3-4 次反弹 = 物理正确的多次散射。
**实际**：**3+ bounce 色彩严重过饱和**，墙面叠加成"圣诞树"。

**为什么**：
- 每次 bounce 都把"上一帧颜色"乘以 albedo，**albedo 接近 1 时累积发散**
- 真实物理 bounce 用 diffusion approximation + 衰减，**不是简单累乘 albedo**

**正解**：
- bounce count 限到 2-3
- 加色彩衰减 LUT，每 bounce 乘 0.7-0.8
- 或用 NRC（Neural Radiance Cache）替代，**多次 bounce 隐式编码在 MLP 里**

### 误区 5："NRC 可以完全替代 Surface Cache"

**你以为**：NRC（神经网络辐射缓存）能完全替代 Lumen Surface Cache。
**实际**：**NRC 室内优、室外一般，且动态光源响应慢 1-2 秒**。

| 场景类型 | Lumen Surface Cache | NRC |
|---------|---------------------|-----|
| 静态室内 | ✅ | ✅（更优） |
| 动态室外 | ✅（1 frame 响应） | ⚠（1-2 秒 fine-tune） |
| 大场景（1km²） | ⚠（内存爆炸） | ✅（仅 150 KB MLP） |
| 冷启动 | ✅（1 frame） | ⚠（30+ frame 收敛） |

**正解**：
- 静态室内 → **NRC 优**
- 动态大场景 → **Lumen Surface Cache 优**
- Hybrid：静态用 NRC，动态光源用 Lumen

---

## 关联知识库

- [[../W3/Lumen-反射降级]] — 同架构的反射版本
- [[../99-归档/体积云-Volumetric-Cloud]] — 大气散射与 GI 的合成
- [[VSM-Virtual-Shadow-Map]] (待写) — GI 漫反射需要的 shadow 信息源
- [[Nanite-材质管线]] (待写) — Nanite mesh 如何参与 Surface Cache
- [[Hi-Z-Buffer-Construction]] — VCT 的 early-out 优化

---

## 复用指南

集成到自己项目 (无 UE5 Lumen)：

1. **构建 Surface Cache** — 离线 (Maya/Houdini) 或运行时 (compute shader),voxel size 看你场景尺度
2. **构建 Lighting Cache** — 每帧对每个 voxel 算直接光 (sky + sun),可以 batching
3. **屏幕探针采样** — 每帧在屏幕空间采 256 个探针,写入 probe atlas
4. **Final Gather** — pixel shader 里 k-NN + 加权插值
5. **Voxel Cone Trace** — 探针稀疏区域兜底
6. **合成** — GI + 直接光 (Deferred Lighting) + 反射 ([[../W3/Lumen-反射降级]]) + 雾

> 提示：自研 mini-GI 的 MVP 版本 = **2 个探针 + cubemap blur**,30 行 HLSL,性能 < 0.5ms。Lumen 是豪华版,先 MVP 验证需求再上 Lumen。

---

## 调参 SOP (踩坑顺序)

```
1. 先关掉 GI,看场景直接光对不对 — 排除 base 渲染问题
2. 开 Final Gather only,probe 256,1 bounce — 看 probe 分布够不够
3. 看 _ProbeSearchRadius:从 200 起步,加到 1000 看漏光是否好转
4. 室内场景开 VCT 兜底:voxel size 从 25 起步,降到 10 看质量
5. 出现漏光:加 Card 厚度估计,或者把 _BounceCount 降到 1
6. 出现闪烁:开 temporal probe 累积,history 0.92 起步
7. 性能不够:开 Half-res FG + voxel size 25,降 _MaxFinalGatherSteps 到 8
8. 多次 bounce 颜色过饱和:bounce count 限到 2,加色彩衰减 LUT
```

---

## AI 加速角度（追加于 2026-07-09）

Lumen GI 漫反射链路的瓶颈是 **Surface Cache 内存 + Final Gather k-NN 搜索 + Voxel Cone Trace 步数**。AI 加速的核心思路是 **"用神经网络学 GI radiance，把离屏存储替换为在线推理"**——这条路径直接对应 day-job 主线之一。

### 1. AI 加速的 3 个层次

| 层次 | 替换对象 | 网络规模 | VRAM 节省 | 视觉收益 |
|------|----------|----------|-----------|----------|
| **L1 FG k-NN 加速** | 256 probe → 64 probe + MLP refine | 8→64→64→3 (~10k params) | probe atlas 4× 小 | 视觉等价 |
| **L2 Neural Cone Trace** | VCT 16 step → MLP 出 radiance | 6→128→128→3 (~50k params) | 不需要 voxel atlas | 视觉略降（5%） |
| **L3 Neural Radiance Cache** | 整个 GI lookup → NeRF query | 8 layer × 64 dim (~33k params) | VRAM 50 MB → 150 KB | 多次弹射更好 |

### 2. L3 Neural Radiance Cache 详解（参见 [[../W9/神经辐射缓存-Neural-Radiance-Cache]]）

直接复用 W9 NRC 的方案——一个 8 hidden layer × 64 dim MLP，输入 (position, direction, scene_scale) → RGB radiance：

- **每像素 16 次 query**（半球积分），每次 ~100K GPU cycles
- **每帧 8K sample 训练**（用 path trace 拿 ground truth）
- **替代 Lumen Surface Cache 的 50 MB voxel atlas + Final Gather**

**对比表（day-job 决策依据）**:

| 维度 | Lumen Surface Cache | NRC |
|------|---------------------|-----|
| VRAM | ~50 MB | ~150 KB |
| 收敛帧数 | 1 frame | 30+ frames |
| 多次弹射 | 显式 screen probe | 隐式 MLP |
| 动态光源响应 | 1 frame | 1-2 sec（fine-tune） |
| 室内表现 | 好 | 优 |
| 室外表现 | 好 | 一般 |

### 3. L1 FG k-NN 加速工程实现

```hlsl
// 把 256 probe → 64 probe,用 MLP 学补全的 radiance
// 输入: 当前像素的 (position, normal, viewDir) + 64 个 probe 的 radiance
// 输出: refined GI radiance (跟 256 probe 的结果对齐)

StructuredBuffer<float3> SparseProbes64;  // 64 个
StructuredBuffer<float3> ProbeWeights;    // MLP weights, 8→64→64→3

float3 NeuralFGRefine(
    float3 WorldPos,
    float3 WorldNormal,
    float3 ViewDir,
    StructuredBuffer<float3> SparseProbes64
) {
    // 1. 找最近的 8 个 probe (k-NN)
    float Distances[8];
    int Indices[8];
    FindKNN(WorldPos, SparseProbes64, 8, Distances, Indices);

    // 2. 加权插值（inverse distance weight）
    float3 IDW = 0.0;
    float WeightSum = 0.0;
    [unroll]
    for (int i = 0; i < 8; ++i) {
        float W = 1.0 / (Distances[i] + 0.01);
        IDW += SparseProbes64[Indices[i]] * W;
        WeightSum += W;
    }
    IDW /= WeightSum;

    // 3. MLP refine: 输入 (8 probe radiance × 3 channel) + (normal × 3) + (viewDir × 3) = 33 features
    // 输出: residual
    float Features[33];
    [unroll]
    for (int p = 0; p < 8; ++p) {
        Features[p * 3 + 0] = SparseProbes64[Indices[p]].r;
        Features[p * 3 + 1] = SparseProbes64[Indices[p]].g;
        Features[p * 3 + 2] = SparseProbes64[Indices[p]].b;
    }
    Features[24] = WorldNormal.x; Features[25] = WorldNormal.y; Features[26] = WorldNormal.z;
    Features[27] = ViewDir.x; Features[28] = ViewDir.y; Features[29] = ViewDir.z;
    Features[30] = WorldPos.x * 0.01;  // scale down
    Features[31] = WorldPos.y * 0.01;
    Features[32] = WorldPos.z * 0.01;

    float3 Residual = MLPForward33to3(Features, ProbeWeights);

    return IDW + Residual * 0.1;  // 残差修正
}
```

### 4. 与 day-job RAG 的关联

Lumen GI 是 day-job **神经 BRDF / 神经 GI** 主线的核心研究对象:
- **L1 工具描述**: `Lumen.GI.NeuralFGRefine(probes_64, weights) → gi_radiance`
- **L3 工具描述**: `Lumen.GI.NeuralRadianceCache(position, direction) → gi_radiance`
- **RAG 检索应用**: 用户问"为什么室内 GI 闪烁" → 检索到 L2 神经 cone trace，输出解决方案

### 5. 已知问题与限制（AI 加速版）

1. **冷启动延迟** — NRC 需要 30+ 帧收敛，期间 GI 闪烁
2. **训练数据需求** — Path tracer 1 spp 收集需要 1024+ spp 离线 RT 拿 ground truth
3. **动态光源响应慢** — NRC 微调 MLP 需要 1-2 秒
4. **能量守恒** — 神经网络输出可能不满足物理约束，需要后处理 normalize
5. **Fallback 链路** — 网络推理失败必须回退到 Surface Cache

---

*Create date: 2026-07-01*
*Last modified: 2026-07-09*
