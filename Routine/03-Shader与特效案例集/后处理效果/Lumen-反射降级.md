---
tags: [shader/自研, shader/post-process, shader/performance, shader/UE]
aliases: [Lumen Reflection, Lumen-Reflection-Fallback, Screen Probe, Surface Cache]
---

# Lumen 反射降级 (Lumen Reflection Fallback)

| 字段 | 内容 |
|------|------|
| **效果名称** | Lumen 反射四档降级 |
| **类型** | 后处理 / 反射 / 软件 RT |
| **平台** | PC / Console (Mobile 不支持) |
| **创建日期** | 2026-07-01 |
| **参考来源** | 参考自 UE5 Lumen Reflection `ScreenSpaceReflections.cpp` + GDC 2022 "Lumen: Real-time Global Illumination" + SIGGRAPH 2021 "Hardware-Accelerated Ray Tracing in Unreal Engine 5" |
| **前置阅读** | [[屏幕空间反射-SSR]] |

---

## 效果截图

![四档对比](assets/lumen_reflection_4tier.png)  
*四档降级：SSR (最快) → Screen Probe (默认) → Surface Cache (备选) → HW RT (高端)*

![屏幕外反射对比](assets/lumen_reflection_off_screen.png)  
*屏幕外反射：SSR 失效（左）vs Screen Probe 保留（右）*

![Surface Cache 室内](assets/lumen_reflection_surface_cache.png)  
*Surface Cache 室内场景：自反射 / 多次弹射都正常*

---

## 核心概念

Lumen 反射是 **4 档降级架构**，按硬件 / 屏幕覆盖 / 粗糙度 / 距离动态选择：

```
                  ┌──────────────┐
  反射请求 ───→   │ Tier 选择器  │
                  └──────┬───────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌────────┐      ┌──────────┐     ┌─────────┐
   │ Tier 1 │      │  Tier 2  │     │ Tier 3  │   ...
   │  SSR   │      │ Screen   │     │ Surface │
   │ 0.5ms  │      │  Probe   │     │  Cache  │
   └────────┘      │ 1.2-2.5ms│     │ 1.5-3.5 │
                   └──────────┘     └─────────┘
   
   ┌────────┐
   │ Tier 4 │
   │  HW RT │
   │ 0.5-2ms│ (独立分支,DXR 设备才走)
   └────────┘
```

| 档位 | 原理 | 屏幕外 | 多次反射 | 性能 | 适用 |
|------|------|--------|----------|------|------|
| **T1 SSR** | 屏幕空间光线步进 | ❌ | ❌ | 0.5-2.8ms | 屏幕内 / 平面 |
| **T2 Screen Probe** | Probe 网格 + Cone Trace | ✅ | ⚠ 1-2 次 | 1.2-2.5ms | 默认档 / 开放世界 |
| **T3 Surface Cache** | 网格体素化 + DDA | ✅ | ✅ 多次 | 1.5-3.5ms | 复杂几何 / 室内 |
| **T4 HW RT** | DXR / RTX | ✅ | ✅ 多次 | 0.5-2ms (硬件) | 高端 PC / 展示 |

> 关键设计：**T1 SSR 是独立的"快路径"**——只对屏幕内、平面、距离近的反射才走（命中条件最严格），剩下全交给 T2/T3。

---

## 核心代码

### C++ 端 — Tier 选择器（核心调度逻辑）

```cpp
// LumenReflection.cpp — Tier 选择器 (简化版 UE5 r.Subsurface 决策树)
ELumenReflectionTier SelectReflectionTier(
    const FMaterialProperties& MatProps,
    const FViewInfo& View,
    const FLumenSceneData& LumenScene,
    float3 WorldPos,
    float3 ReflectDir)
{
    // 1. 硬件 RT 优先（如果开了）
    if (CVarLumenHWRT.GetValueOnRenderThread() > 0 &&
        LumenScene.IsHardwareRTSupported())
    {
        return ELumenReflectionTier::HardwareRT;
    }

    // 2. 屏幕内 + 高光强 + 平面 → 走 SSR (T1)
    bool bInScreen = IsReflectRayInScreen(WorldPos, ReflectDir, View);
    bool bSharpReflection = MatProps.Roughness < 0.2f && MatProps.Metallic > 0.5f;
    if (bInScreen && bSharpReflection && CVarLumenSSRStyle.GetValueOnRenderThread())
    {
        return ELumenReflectionTier::ScreenSpace;
    }

    // 3. 屏幕内 + 屏幕外都覆盖 → Screen Probe (T2,默认)
    //    Lumen 默认走这条，除非强制 T3
    if (CVarLumenReflectionMethod.GetValueOnRenderThread() == 0) // 0 = ScreenProbe
    {
        return ELumenReflectionTier::ScreenProbe;
    }

    // 4. 室内 / 复杂几何 / 多次反射 → Surface Cache (T3)
    if (LumenScene.IsSurfaceCacheValid())
    {
        return ELumenReflectionTier::SurfaceCache;
    }

    return ELumenReflectionTier::ScreenProbe; // fallback
}
```

### HLSL — Tier 2 Screen Probe (Lumen 默认档)

```hlsl
// LumenScreenProbe.usf — Screen Probe 反射采样
// 关键数据结构: 屏幕空间 Probe 网格 (16x16 = 256 probes/frame)
StructuredBuffer<FProbe> ScreenProbeAtlas;       // 每帧采样的 probe 列表
StructuredBuffer<FProbeOffset> ProbeOffsets;      // probe 在 atlas 里的位置

float3 PS_LumenScreenProbe(VS_OUTPUT input) : SV_Target
{
    // 1. 反射起点 + 方向
    float3 worldPos = ReconstructWorldPos(input.positionCS, input.deviceZ);
    float3 viewDir = normalize(worldPos - _CameraPos);
    float3 reflectDir = reflect(-viewDir, input.worldNormal);

    // 2. 在 atlas 中找最近的几个 probe
    //    Lumen 用 spatial hash 分桶,每像素最多采样 8 个 probe
    FProbeProximity probes[8];
    int numProbes = FindNearestProbes(worldPos, /*radius=*/_ProbeSearchRadius, probes);

    // 3. 多 probe 投票 — 用 BRDF mask 加权
    float3 result = 0;
    float totalWeight = 0;
    [unroll]
    for (int i = 0; i < 8; ++i)
    {
        if (i >= numProbes) break;
        FProbe p = ScreenProbeAtlas[probes[i].atlasIndex];

        // 4. 在 probe 位置 cone-trace (锥形步进,采样多个方向)
        float3 probeHit = ConeTraceScreenProbe(
            p.worldPos,
            reflectDir,
            /*coneAngle=*/_ProbeConeAngle,
            /*maxDist=*/_MaxReflectionDistance,
            /*stepCount=*/_ProbeStepCount);

        // 5. 加权 — 距离越近、BRDF 越对齐,权重越高
        float distWeight = saturate(1.0 - probes[i].distance / _ProbeSearchRadius);
        float ndotr = saturate(dot(p.worldNormal, reflectDir));
        float weight = distWeight * ndotr;
        result += probeHit * weight;
        totalWeight += weight;
    }

    return (totalWeight > 0.001) ? (result / totalWeight) : SampleEnvironment(input.worldNormal, input.roughness);
}
```

### HLSL — Tier 3 Surface Cache (室内 / 复杂几何)

```hlsl
// LumenSurfaceCache.usf — 体素化网格 DDA 步进
Texture3D<float4> SurfaceCacheLuminance;   // 体素亮度 (Lumen 烘焙)
Texture3D<float2> SurfaceCacheDepth;       // 体素深度
float3 SurfaceCacheVoxelSize;              // 单 voxel 尺寸 (cm)

float3 PS_LumenSurfaceCache(VS_OUTPUT input) : SV_Target
{
    float3 worldPos = ReconstructWorldPos(input.positionCS, input.deviceZ);
    float3 viewDir = normalize(worldPos - _CameraPos);
    float3 reflectDir = reflect(-viewDir, input.worldNormal);

    // 1. 转换到体素空间
    float3 rayOriginVoxel = worldPos / SurfaceCacheVoxelSize;
    float3 rayDirVoxel = normalize(reflectDir / SurfaceCacheVoxelSize);

    // 2. DDA (Digital Differential Analyzer) — Amanatides & Woo 经典算法
    int3 voxel = int3(floor(rayOriginVoxel));
    int3 step = int3(sign(rayDirVoxel));
    float3 tMax = abs((float3(voxel) + max(step, 0) - rayOriginVoxel) / rayDirVoxel);
    float3 tDelta = abs(1.0 / rayDirVoxel);

    float t = 0;
    float3 hitPos = 0;
    bool found = false;

    [loop]
    for (int i = 0; i < _MaxDDAIterations; ++i)
    {
        // 3. 采样当前 voxel
        float2 depthRange = SurfaceCacheDepth.Load(int4(voxel, 0)).rg;
        float rayDepth = length(rayOriginVoxel - float3(voxel)) * length(SurfaceCacheVoxelSize);

        if (rayDepth >= depthRange.x && rayDepth <= depthRange.y)
        {
            // 命中! 二分精修
            hitPos = float3(voxel) * SurfaceCacheVoxelSize;
            found = true;
            break;
        }

        // 4. 推进到下一个 voxel
        if (tMax.x < tMax.y) {
            if (tMax.x < tMax.z) { voxel.x += step.x; t = tMax.x; tMax.x += tDelta.x; }
            else                 { voxel.z += step.z; t = tMax.z; tMax.z += tDelta.z; }
        } else {
            if (tMax.y < tMax.z) { voxel.y += step.y; t = tMax.y; tMax.y += tDelta.y; }
            else                 { voxel.z += step.z; t = tMax.z; tMax.z += tDelta.z; }
        }

        if (t > _MaxReflectionDistance / length(SurfaceCacheVoxelSize)) break;
    }

    if (!found) return SampleEnvironment(input.worldNormal, input.roughness);

    // 5. 命中后采样亮度 + 算光照 (二次 ray)
    float3 hitWorldPos = hitPos;
    float luminance = SurfaceCacheLuminance.Load(int4(voxel, 0)).r;
    return luminance * _LumenIndirectColor;
}
```

---

## 参数解释

| 参数名 | 类型 | 范围 | 含义 | 调参建议 |
|--------|------|------|------|----------|
| `_ProbeSearchRadius` | float | 100~2000 (cm) | 找 probe 的搜索半径 | 500 平衡质量性能 |
| `_ProbeConeAngle` | float | 0.1~1.0 (rad) | Cone trace 锥角 | 0.5 默认,越小越精确但越贵 |
| `_ProbeStepCount` | int | 4~32 | Cone trace 步数 | 8 标准,16 高质量 |
| `_MaxReflectionDistance` | float | 1000~10000 (cm) | 最大追踪距离 | 5000 标准,室内 2000 |
| `_MaxDDAIterations` | int | 32~256 | Surface Cache DDA 最大步数 | 128 标准,256 高质量 |
| `_SurfaceCacheVoxelSize` | float | 5~50 (cm) | 体素分辨率 | 10 标准,5 高质量但内存 ×8 |
| `r.Lumen.HWRT` | CVar | 0/1/2 | 强制 HW RT / 自动 / 关闭 | 默认自动,展示场景 = 1 |
| `r.Lumen.ReflectionMethod` | CVar | 0/1/2 | 0=ScreenProbe / 1=SurfaceCache / 2=自动 | 默认 2 自动 |

---

## 性能分级

| 档位 | 改动 | 性能 | 适用 |
|------|------|------|------|
| **T1 SSR only** | 强制只走 SSR | 0.5-2.8ms | Mobile / 移动端备选 |
| **T2 Screen Probe** | 16x16 probe + 8 cone steps | 1.2-2.5ms | **默认 / 开放世界** |
| **T3 Surface Cache** | voxel size 10cm + 128 DDA | 1.5-3.5ms | 室内 / 复杂几何 |
| **T4 HW RT** | DXR primary rays | 0.5-2ms (硬件) | 高端 PC / 展示 |
| **混合策略 (生产用)** | T1 快路径 + T2 主路径 + T4 高端 | 1.5-2.5ms | 商业项目默认 |

> Lumen 生产项目实际跑的是 **混合策略**——T1 SSR 命中条件严苛 (只对屏幕内 + 高光强平面),T2 Screen Probe 兜底,T4 硬件支持时升级。

---

## 变体版本

- **版本 A：Probe 网格降采样** — 256 → 64 probes,每帧省 0.4ms,代价是远处反射模糊
- **版本 B：Surface Cache Streaming** — 把 voxel atlas 拆成 tile,只更新可见区域,内存省 60%
- **版本 C：Temporal 复用** — 反射结果跨帧累积 (类似 TAA),probe 步数可以减半
- **版本 D：自研混合 (无 Lumen)** — 不用 Lumen,自己组合 SSR + 光线步进 + cubemap fallback,适合需要控制每一档的定制引擎

---

## 已知问题与限制

1. **Screen Probe "黑洞" 现象** — Probe 落在物体内部 / 阴影区,导致反射出现黑斑。解决方案:probe 重要性采样 + 抖动 (dithering),让 probe 分布更均匀。
2. **Surface Cache 内存爆炸** — 大场景 voxel atlas 轻易吃 200MB+ 显存。解决方案:streaming + LOD,远处用更粗的 voxel。
3. **多次反射 (Mirror) 不稳定** — 镜面球 / 玻璃幕墙之间的多次反射会闪烁。解决方案:temporal 累积 + 历史帧混合 (TAA 风格)。
4. **HW RT 与软件 RT 切换闪** — 进 / 出 RTX 区域时画面跳变。解决方案:在边界处做 200ms 线性混合。
5. **屏幕空间与 Surface Cache 边界硬切** — 屏幕内用 SSR、屏幕外用 Probe,边界反射会"嘎嘣"一下。解决方案:屏幕边缘 32 像素的 blend zone。
6. **粗糙表面噪点** — rough > 0.6 时 probe cone trace 步数不够,出现椒盐噪点。解决方案:降低粗糙度截断 + TAA。

---

## 关联知识库

- [[屏幕空间反射-SSR]] — T1 前置阅读
- [[Hi-Z-Buffer-Construction]] — T1 的 Hi-Z 加速,Screen Probe 也复用
- [[TAA-History-Reprojection]] — temporal 累积去噪
- [[Lumen-GI-漫反射]] (待写) — T2/T3 的 GI 漫反射版本
- [[VSM-Virtual-Shadow-Map]] (待写) — Lumen 配套的虚拟阴影

---

## 复用指南

集成到自己项目 (无 UE5 Lumen)：

1. **实现 Tier 选择器** — 复制 `SelectReflectionTier.cpp`,先支持 T1 SSR (已有) + T2 cubemap fallback
2. **加 Screen Probe** — 每帧采 256 个 probe,写入 `ScreenProbeAtlas` 缓冲
3. **加 Surface Cache** — 用 [OpenVDB](https://www.openvdb.org/) 或自研体素化,离线烘焙 + 运行时 DDA
4. **可选 HW RT** — 用 DXR / Vulkan RT,只在支持的设备启用
5. **混合策略** — 命中 T1 → 用 SSR;否则 → 视情况 T2/T3;再否则 → cubemap

> 提示：如果项目预算紧,**只用 T1 SSR + cubemap fallback** 也能解决 80% 反射需求,T2/T3 留给有 Lumen 的项目。

---

## 调参 SOP (踩坑顺序)

```
1. 先开 T1 SSR (W2 那篇) 验证屏幕内反射对不对
2. 关闭 T2/T3/T4,只看 SSR 表现 — 找出 SSR 失效的边界
3. 开 T2 Screen Probe — 默认 256 probes,8 steps
4. 调整 _ProbeSearchRadius:从 200 起步,加到 1000 看质量
5. 室内场景开 T3 Surface Cache:voxel size 先 20,再降到 10
6. 高端设备开 T4 HW RT:不要默认开,做"展示模式"开关
7. 最后做 T1↔T2 边界 blend (解决 #5 已知问题)
```

---

*Create date: 2026-07-01*  
*Last modified: 2026-07-01*
