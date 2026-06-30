---
tags: [shader/自研, shader/post-process, shader/performance, shader/UE, shader/compute]
aliases: [Lumen GI, Diffuse GI, Voxel Cone Tracing, Surface Cache, Final Gather]
---

# Lumen GI 漫反射 (Lumen Global Illumination — Diffuse)

| 字段 | 内容 |
|------|------|
| **效果名称** | Lumen GI 漫反射（Surface Cache + Voxel Cone Tracing + Final Gather） |
| **类型** | 后处理 / 全局光照 / 软件 RT |
| **平台** | PC / Console (Mobile 不支持) |
| **创建日期** | 2026-07-01 |
| **参考来源** | 参考自 UE5 Lumen Global Illumination `LumenSceneRendering.cpp` + GDC 2022 "Lumen: Global Illumination" + SIGGRAPH 2021 "Hardware-Accelerated Ray Tracing in Unreal Engine 5" + Crassin et al. "Aggregate G-Buffer Anti-Aliasing" 论文 |
| **前置阅读** | [[Lumen-反射降级]] [[体积云-Volumetric-Cloud]] |

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

## 关联知识库

- [[Lumen-反射降级]] — 同架构的反射版本
- [[体积云-Volumetric-Cloud]] — 大气散射与 GI 的合成
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
6. **合成** — GI + 直接光 (Deferred Lighting) + 反射 ([[Lumen-反射降级]]) + 雾

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

*Create date: 2026-07-01*  
*Last modified: 2026-07-01*
