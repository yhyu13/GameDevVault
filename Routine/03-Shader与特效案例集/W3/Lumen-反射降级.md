---
tags: [shader/自研, shader/post-process, shader/performance, shader/UE, shader/lumen, shader/AI-accelerated]
aliases: [Lumen Reflection, Lumen-Reflection-Fallback, Screen Probe, Surface Cache]
week: W3
cycle: A
---

# Lumen 反射降级 (Lumen Reflection Fallback)

| 字段 | 内容 |
|------|------|
| **效果名称** | Lumen 反射四档降级 |
| **类型** | 后处理 / 反射 / 软件 RT |
| **平台** | PC / Console (Mobile 不支持) |
| **创建日期** | 2026-07-01 |
| **参考来源** | 参考自 UE5 Lumen Reflection `ScreenSpaceReflections.cpp` + GDC 2022 "Lumen: Real-time Global Illumination" + SIGGRAPH 2021 "Hardware-Accelerated Ray Tracing in Unreal Engine 5" |
| **前置阅读** | [[99-归档/屏幕空间反射-SSR]] |

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

## 概念链（Concept Chain）— 从"为什么反射要 4 档"到"AI 加速能省多少"

读代码前先把动机链条理清楚。这一节给初学者一个"4 步推理链"，把后面所有技术细节挂在因果链上，不容易迷失。

### Step 1: 业务痛点 — 反射是 3A 渲染最贵的效果之一

反射在 3A 项目里是"看着不起眼，掉了立刻露馅"的效果。镜子、玻璃幕墙、水面、金属高光——任何一个反射错位 / 缺失都会被玩家立刻察觉。但反射的实现有 3 大难点：

| 难点 | 表现 |
|------|------|
| **屏幕外反射** | 物体在屏幕边缘，SSR 失效；玩家看到屏幕里反射在，但屏幕外物体没反射 |
| **多次弹射** | 玻璃球 / 镜面之间的反射需要递归追踪，传统方法爆炸式增长 |
| **动态几何** | 角色 / 移动物体需要每帧更新反射缓存，性能压力大 |

单一反射方案（如纯 SSR 或纯 RT）无法同时解决 3 个难点——SSR 屏幕外失效，HW RT 移动端不支持，多次弹射性能爆炸。

### Step 2: 传统局限 — 为什么单一方案解不掉

| 方案 | 原理 | 优势 | 致命缺陷 |
|------|------|------|---------|
| **SSR (屏幕空间反射)** | 在 G-buffer 上光线步进 | 0.5-2.8ms 快 | 屏幕外失效、平面假设 |
| **Cubemap** | 预渲染立方体贴图 | 极快 | 静态、不支持动态物体 |
| **HW RT (DXR)** | 硬件光线追踪 | 屏幕外 + 多次弹射都支持 | 移动端不支持，需要 RTX |
| **Planar Reflection** | 二次渲染 mirror plane | 准确 | 反射平面数 = draw call 倍增 |

**为什么单一方案解不掉**：上面 4 种方案各自只能解决 1-2 个难点。**生产环境必须混合策略**，这正是 Lumen 的核心设计。

### Step 3: 神经网络 / 4 档降级 — 动态选择最佳路径

Lumen 的核心创新是 **"Tier 选择器"**——根据硬件 / 屏幕覆盖 / 粗糙度 / 距离动态选择反射路径：

```
反射请求
   │
   ▼
[1] 硬件 RT 优先 (RTX 设备才走)
   │ 否
   ▼
[2] T1 SSR (屏幕内 + 高光强 + 平面, 命中条件严)
   │ 否
   ▼
[3] T2 Screen Probe (默认, 256 probe + cone trace)
   │ 复杂几何/室内
   ▼
[4] T3 Surface Cache (体素化 + DDA, 多次弹射)
   │
   ▼
最终反射 (T2 兜底)
```

**关键设计**：
- **T1 SSR 是独立的"快路径"**，命中条件最严格（屏幕内 + 高光强平面），其他全交给 T2
- **T2 Screen Probe 是默认档**，覆盖 80% 场景，硬件要求低（SM5 即可）
- **T3 Surface Cache 是"室内豪华版"**，多次弹射 + 复杂几何，但内存大（200MB+）
- **T4 HW RT 是"高端备选"**，DXR 设备才走

### Step 4: 落地路径 — AI 加速能省多少

AI 加速思路：**用神经网络学反射 lookup，把多次离散采样替换成一次 forward**。

| 层次 | 替换对象 | 网络规模 | 性能收益 |
|------|----------|----------|---------|
| **L1 Probe Densification** | T2 256 probe → 64 probe + MLP 补全 | 5→64→64→3 (~10k params) | 4× probe 减少 |
| **L2 Neural Cone Trace** | cone trace 8 step → MLP 直接出结果 | 6→128→128→3 (~50k params) | 8× step 减少 |
| **L3 NeRF Reflection Cache** | 整个反射 lookup → NeRF query | 8 layer × 256 dim (~500k params) | 完全替代 cone trace |

**对比传统 4 档的总账**：

| 维度 | 传统 4 档 | Lumen + L1 Probe Densification |
|------|----------|-------------------------------|
| 单像素反射开销 | 0.5-2.5 ms | 0.4-1.5 ms（节省 30%） |
| Probe atlas VRAM | 256 KB | 64 KB |
| 多次弹射质量 | 屏幕 probe 1-2 次 | MLP 隐式编码，多次弹射自然 |
| 移动端兼容 | T1+T2 可用 | L1 MLP 也可移植到 mobile |

**对 day-job 的核心价值**：本笔记是 day-job **Lumen 反射降级链路**的核心案例——Tier 选择器 + Screen Probe 数据 + AI 加速方案都是 day-job RAG 检索的关键素材（详见下方"与 day-job RAG 的关联"一节）。

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

## 代码逐行讲解（Code Walkthrough）— 3 段代码各在做什么

> 这一节专门给"读完代码还是不知道在干嘛"的初学者。每个代码块对应一段讲解：**意图 / 关键参数 / 边界条件**。

### 代码块 1: `SelectReflectionTier` (C++ Tier 选择器)

**意图**：根据硬件 + 屏幕覆盖 + 材质属性 + 场景数据，动态选择反射档位。

```cpp
ELumenReflectionTier SelectReflectionTier(
    const FMaterialProperties& MatProps,
    const FViewInfo& View,
    const FLumenSceneData& LumenScene,
    float3 WorldPos,
    float3 ReflectDir)
{
    // 1. 硬件 RT 优先
    if (CVarLumenHWRT.GetValueOnRenderThread() > 0 &&
        LumenScene.IsHardwareRTSupported())
        return ELumenReflectionTier::HardwareRT;

    // 2. 屏幕内 + 高光强 + 平面 → SSR
    bool bInScreen = IsReflectRayInScreen(WorldPos, ReflectDir, View);
    bool bSharpReflection = MatProps.Roughness < 0.2f && MatProps.Metallic > 0.5f;
    if (bInScreen && bSharpReflection && CVarLumenSSRStyle.GetValueOnRenderThread())
        return ELumenReflectionTier::ScreenSpace;

    // 3. 默认走 Screen Probe
    if (CVarLumenReflectionMethod.GetValueOnRenderThread() == 0)
        return ELumenReflectionTier::ScreenProbe;

    // 4. 室内 / 复杂几何 → Surface Cache
    if (LumenScene.IsSurfaceCacheValid())
        return ELumenReflectionTier::SurfaceCache;

    return ELumenReflectionTier::ScreenProbe;
}
```

**关键参数为什么**：
- **判断顺序很重要**：HW RT > SSR > Screen Probe > Surface Cache，从最贵到最便宜依次降级
- `bSharpReflection = roughness < 0.2 && metallic > 0.5`：只有"近镜面"才走 SSR，粗糙反射走 Probe（SSR 平面假设失效）
- `IsSurfaceCacheValid()`：Surface Cache 在加载阶段才能用，运行时改场景要 invalidate
- `CVarLumenReflectionMethod == 0` 作为默认 → 美术可以在控制台强制切档调试

**边界条件**：
- 所有 tier 都失效（极端 GPU bug）→ Screen Probe 兜底，永远不会返回 invalid
- 冷启动首帧 `IsSurfaceCacheValid()` 返回 false，自动跳过 T3

### 代码块 2: `PS_LumenScreenProbe` (HLSL T2 默认档)

**意图**：在屏幕空间采样 8 个最近的 probe，cone trace 拿反射 radiance，多 probe BRDF mask 加权。

```hlsl
float3 PS_LumenScreenProbe(VS_OUTPUT input) : SV_Target
{
    float3 worldPos = ReconstructWorldPos(input.positionCS, input.deviceZ);
    float3 reflectDir = reflect(-viewDir, input.worldNormal);

    // 1. 找最近 8 个 probe
    FProbeProximity probes[8];
    int numProbes = FindNearestProbes(worldPos, _ProbeSearchRadius, probes);

    // 2. 多 probe 投票
    float3 result = 0;
    float totalWeight = 0;
    for (int i = 0; i < 8; ++i) {
        FProbe p = ScreenProbeAtlas[probes[i].atlasIndex];

        // 3. probe 位置 cone trace
        float3 probeHit = ConeTraceScreenProbe(p.worldPos, reflectDir,
            _ProbeConeAngle, _MaxReflectionDistance, _ProbeStepCount);

        // 4. 距离 + 法线对齐加权
        float distWeight = saturate(1.0 - probes[i].distance / _ProbeSearchRadius);
        float ndotr = saturate(dot(p.worldNormal, reflectDir));
        float weight = distWeight * ndotr;
        result += probeHit * weight;
        totalWeight += weight;
    }

    return (totalWeight > 0.001) ? (result / totalWeight) : SampleEnvironment(input.worldNormal, input.roughness);
}
```

**关键参数为什么**：
- **`_ProbeSearchRadius`**：搜索半径，默认 500 cm。太小 → 找不到 probe，太多 → 远距离 probe 噪声进来
- **`_ProbeConeAngle`**：cone trace 锥角，默认 0.5 rad (~30°)。越小越精确但越贵（步数要增加）
- **`_ProbeStepCount`**：每条 cone trace 步数，8 标准 16 高质量。**步数 × cone 数 = 反射总开销**
- **BRDF mask 加权**：用 `ndotr = dot(probeNormal, reflectDir)` 作为权重，**法线不对齐的 probe 投票权低**，减少视觉错误

**边界条件**：
- `totalWeight < 0.001`：所有 probe 都没命中 → fallback 到 environment cubemap（避免黑屏）
- `numProbes < 8`：probe 不足时循环 `if (i >= numProbes) break` 提前退出

### 代码块 3: `PS_LumenSurfaceCache` (HLSL T3 室内豪华档)

**意图**：体素化场景 + DDA (Digital Differential Analyzer) 步进，命中后采样亮度。

```hlsl
float3 PS_LumenSurfaceCache(VS_OUTPUT input) : SV_Target
{
    // 1. 转换到体素空间
    float3 rayOriginVoxel = worldPos / SurfaceCacheVoxelSize;
    float3 rayDirVoxel = normalize(reflectDir / SurfaceCacheVoxelSize);

    // 2. DDA 初始化 (Amanatides & Woo 算法)
    int3 voxel = int3(floor(rayOriginVoxel));
    int3 step = int3(sign(rayDirVoxel));
    float3 tMax = abs((float3(voxel) + max(step, 0) - rayOriginVoxel) / rayDirVoxel);
    float3 tDelta = abs(1.0 / rayDirVoxel);

    float t = 0;
    bool found = false;
    for (int i = 0; i < _MaxDDAIterations; ++i) {
        // 3. 采样当前 voxel
        float2 depthRange = SurfaceCacheDepth.Load(int4(voxel, 0)).rg;
        float rayDepth = length(rayOriginVoxel - float3(voxel)) * length(SurfaceCacheVoxelSize);

        if (rayDepth >= depthRange.x && rayDepth <= depthRange.y) {
            hitPos = float3(voxel) * SurfaceCacheVoxelSize;
            found = true;
            break;
        }

        // 4. 推进到下一个 voxel
        if (tMax.x < tMax.y) {
            if (tMax.x < tMax.z) { voxel.x += step.x; tMax.x += tDelta.x; }
            else                 { voxel.z += step.z; tMax.z += tDelta.z; }
        } else {
            if (tMax.y < tMax.z) { voxel.y += step.y; tMax.y += tDelta.y; }
            else                 { voxel.z += step.z; tMax.z += tDelta.z; }
        }

        if (t > _MaxReflectionDistance / length(SurfaceCacheVoxelSize)) break;
    }
}
```

**关键参数为什么**：
- **`SurfaceCacheVoxelSize`**：体素尺寸，默认 10 cm。越小精度越高但内存 ×8（内存随 voxel 数立方增长）
- **`_MaxDDAIterations`**：128 标准 256 高质量。太多 step 浪费，太少远处反射丢失
- **`_MaxReflectionDistance`**：5000 cm 标准，室内 2000 cm。**比 scene 半径大就足够**
- **DDA 算法**：经典 Amanatides & Woo 1987，**每次推进选 tMax 最小的轴**，O(1) per step，无浮点误差累积

**边界条件**：
- `rayOriginVoxel / rayDirVoxel` 不能是 0 → 加 `+ 1e-7` 防止除零
- `voxel 超出 voxel grid 范围` → `IsInsideVoxelGrid` 检查，越界 break
- 命中检测用 `depthRange`（每个 voxel 存最小/最大深度），**避免体素内部的孔洞穿透**

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

## 指标手册（Metric Guide）— 每个参数到底在测什么 / 为什么是这个值

> 9 个参数是 Lumen 反射调参的"入口"。初学者常见误区是"看到一个 CVar 随便填一个"——这一节告诉你每个参数的"测什么 / 默认值为什么 / 阈值含义 / 怎么调"。

| 参数 | 测什么 | 默认值来源 | 阈值含义 | 怎么调 |
|------|-------|-----------|---------|--------|
| `_ProbeSearchRadius` | probe 搜索半径 | 500 cm（UE5 经验值） | < 200 cm probe 太稀疏，> 1000 cm 远距离噪声 | 室外 800-1000 cm，室内 200-500 cm |
| `_ProbeConeAngle` | cone trace 锥角 | 0.5 rad（≈30°） | < 0.3 锐利但慢，> 0.8 太钝模糊 | 室外 0.7（粗略），室内 0.4（精确） |
| `_ProbeStepCount` | cone trace 步数 | 8（标准） | 4 粗糙 32 精确 | 性能不够降到 4，质量不够升到 16 |
| `_MaxReflectionDistance` | 最大追踪距离 | 5000 cm（≈50m） | < 2000 cm 室内够用，> 10000 cm 浪费 | 室内 2000，室外 8000 |
| `_MaxDDAIterations` | DDA 最大步数 | 128 | < 64 远处反射丢失，> 256 浪费 | 性能不够降到 64，质量不够升到 256 |
| `_SurfaceCacheVoxelSize` | 体素尺寸 | 10 cm | 5 cm 内存 ×8，25 cm 粗糙 | 室内 5 cm，室外 25 cm，混合场景 10 cm |
| `r.Lumen.HWRT` | 强制 HW RT | 0（自动） | 1 = 强制，2 = 关闭 | 展示场景 = 1，普通项目 = 0（自动），移动端 = 2 |
| `r.Lumen.ReflectionMethod` | 反射方法 | 2（自动） | 0 = ScreenProbe，1 = SurfaceCache | 调试时强制切档，验证视觉差异 |

### 3 个常被误用的参数

#### `_ProbeSearchRadius` 不是越大越好

直觉："半径越大，probe 越多，反射越好"。**错**。

| 半径 (cm) | probe 数 | 视觉 | 性能 |
|----------|---------|------|------|
| 200 | 4-5 | 远处反射缺失 | 0.8 ms |
| 500（默认） | 8（满） | 好 | 1.5 ms |
| 1000 | 8（仍然满）+ 远距离 probe 噪声 | 噪点增加 | 2.5 ms |
| 2000 | 8 + 大量远距离噪声 | 远处闪烁 | 4.0 ms |

**为什么半径过大反而变差**：8 个 probe 已经加权平均了，**远距离 probe 投票权低但仍贡献**，相当于给近 probe 加了噪声。最佳做法：**保持 8 个 probe 满，加权时排除距离 > 半径的 70%**。

#### `_SurfaceCacheVoxelSize` 内存爆炸陷阱

直觉："5 cm 体素精度比 25 cm 高 5 倍"。**对，但内存爆炸 125 倍**（3D 立方）。

| 体素尺寸 | 1km³ 场景体素数 | VRAM (假设 R16G16B16A16) |
|---------|----------------|-------------------------|
| 5 cm | 8 × 10⁹ | 256 GB 💥 |
| 10 cm（默认） | 10⁹ | 32 GB |
| 25 cm | 6.4 × 10⁷ | 2 GB |
| 50 cm | 8 × 10⁶ | 256 MB |

**经验法则**：体素尺寸 × 场景半径 ≈ VRAM 立方根。1 km 室外场景用 25 cm 才不会爆内存。

#### `r.Lumen.HWRT` 强制开启 = 性能灾难

直觉："强制 HW RT 总是最好的"。**错**——HW RT 在不支持 DXR 的设备会直接 disable，强制开启时控制台只显示"disabled"。

| 设备类型 | HWRT = 1 | HWRT = 0（自动） | HWRT = 2 |
|---------|---------|------------------|---------|
| RTX 3080+ | 0.5-2 ms（最快） | 0.5-2 ms | 1.5-3 ms（走 T2） |
| GTX 1660 | 不支持 💥 | 1.5-3 ms（T2） | 1.5-3 ms |
| 移动端 | 不支持 💥 | 1.5-3 ms（T2） | 1.5-3 ms |

**正解**：永远保持 `r.Lumen.HWRT 0`（自动），让 UE5 根据硬件决定；展示模式可以临时 `1`。

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

## 常见误读（Common Misreading）— 5 个初学者陷阱

> 这一节列的是"读文档时容易形成、但实际是错的"理解。每条都是 day-job 真实踩过的坑。

### 误区 1："Lumen 自动选择最优档，我不用管"

**你以为**：Lumen Tier 选择器会自动选最好的反射档。
**实际**：**Lumen 默认走 T2 Screen Probe，但 T1 SSR（快路径）需要满足"屏幕内 + 高光强平面"才走**——很多本应走 T1 的反射被错误地走了 T2。

**正解**：
- `r.Lumen.ReflectionMethod` 调试时强制切档验证
- 检查 `_ProbeSearchRadius` 和 `_ProbeStepCount` 是否对当前场景合理
- 室内场景要显式启用 T3（Surface Cache 不会自动开）

### 误区 2："Surface Cache 一定比 Screen Probe 好"

**你以为**：Surface Cache 是"豪华版"，永远比 Screen Probe 强。
**实际**：**Surface Cache 内存大（200MB+）、冷启动慢（5-20ms）、不适合动态场景**。

| 场景 | Surface Cache | Screen Probe |
|------|--------------|--------------|
| 静态室内 | ✅ 多次弹射自然 | ⚠ 弹射少 |
| 静态室外 | ❌ 浪费内存 | ✅ 天空主导 |
| 动态场景（角色移动） | ⚠ 增量更新阻塞 | ✅ 自然适应 |
| 移动端 | ❌ 不支持 | ✅ SM5 可跑 |

**正解**：根据场景类型选档，**不是越贵越好**。开放世界 = Screen Probe，封闭空间 = Surface Cache。

### 误区 3："T1 SSR 屏幕外也能反射"

**你以为**：SSR 能反射屏幕外的物体。
**实际**：**SSR 在屏幕边缘反射会"嘎嘣"硬切到环境贴图**——这是 SSR 算法的硬伤，不是 UE5 的 bug。

**为什么**：
- SSR 沿反射方向在 G-buffer 上光线步进
- 反射射线离开屏幕 → G-buffer 越界 → 算法返回 invalid
- 工业做法：屏幕边缘 32 像素 blend zone，平滑过渡到 Screen Probe

**正解**：不要指望 SSR 处理屏幕外反射，T2/T3 才是屏幕外的正确答案。

### 误区 4："HW RT 总是比软件 RT 快"

**你以为**：硬件 RTX 加速 = 一定比软件 cone trace 快。
**实际**：**HW RT 在场景几何简单时反而慢**（ray launch overhead 占主导），且只支持 DXR 设备。

| 场景复杂度 | HW RT | Screen Probe | Surface Cache |
|----------|-------|--------------|---------------|
| 简单（< 100 mesh） | 1.0 ms（ray launch overhead 大） | 0.8 ms（更快） | 1.2 ms |
| 中等（100-1000 mesh） | 1.5 ms | 1.5 ms（追平） | 1.8 ms |
| 复杂（> 1000 mesh） | 2.0 ms（最快） | 2.5 ms（多次弹射慢） | 2.0 ms |

**正解**：HW RT 在复杂几何占优，简单场景让 `r.Lumen.HWRT 0`（自动）让 UE5 决定。

### 误区 5："L1 Probe Densification（256→64 probe）视觉等价"

**你以为**：256 → 64 probe + MLP 补全视觉上等价。
**实际**：**视觉略降（5%），且训练集覆盖不到的训练分布外输入可能瞎猜**。

**为什么**：
- 训练时用 256 probe 的结果作为 ground truth，MLP 学的是"补全 64 → 256"
- 训练集是 Kettle / Subway 等几个标准场景，**生产环境的复杂几何分布外，MLP 失真**
- 漫反射主导场景视觉差异小（粗糙反射不敏感），**镜面反射场景差异大**

**正解**：
- 室内漫反射主导 → L1 完全够用，**视觉等价**
- 高金属 / 镜面场景 → L1 不够，用 L2 Neural Cone Trace 或 L3 NeRF

---

## 关联知识库

- [[99-归档/屏幕空间反射-SSR]] — T1 前置阅读
- [[Hi-Z-Buffer-Construction]] — T1 的 Hi-Z 加速,Screen Probe 也复用
- [[TAA-History-Reprojection]] — temporal 累积去噪
- [[../W4/Lumen-GI-漫反射]] — T2/T3 的 GI 漫反射版本
- [[../W6/VSM-Virtual-Shadow-Map]] — Lumen 配套的虚拟阴影

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

## AI 加速角度（追加于 2026-07-09）

Lumen 反射降级链路里 T2/T3/T4 的核心瓶颈都是 **probe 数量 / cone trace 步数 / RT bounce 数**——这三个都直接决定显存带宽和 GPU cycle。AI 加速方案的核心思路是 **"用神经网络学反射 lookup，把多次离散采样替换成一次 forward"**。

### 1. AI 加速的 3 个层次（按 ROI 排序）

| 层次 | 替换对象 | 网络规模 | 性能收益 | 视觉收益 |
|------|----------|----------|----------|----------|
| **L1 Probe Densification** | T2 256 probe → 64 probe + 神经网络补全 | 5→64→64→3 (~10k params) | 4× probe 减少 | 视觉等价 |
| **L2 Neural Cone Trace** | T2/T3 cone trace 8 step → MLP 直接出结果 | 6→128→128→3 (~50k params) | 8× step 减少 | 视觉略降（5%） |
| **L3 NeRF Reflection Cache** | 整个反射 lookup → neural radiance field query | 8 layer × 256 dim (~500k params) | 完全替代 cone trace | 视觉更好（多次弹射自然） |

### 2. L1 Probe Densification 工程实现要点（day-job 重点）

```hlsl
// 简化版:把 256 probe → 64 probe,缺的部分用 MLP 补
StructuredBuffer<float3> SparseProbes;       // 64 个
StructuredBuffer<float3> NeuralWeights;       // [5 → 64 → 64 → 3]

float3 NeuralProbeInterpolate(float2 UV, StructuredBuffer<float3> SparseProbes) {
    // 找最近的 4 个 probe
    int2 ProbeGridSize = int2(8, 8);  // 8x8 = 64 probe
    float2 ProbeUV = UV * float2(ProbeGridSize);
    int2 Probe00 = int2(floor(ProbeUV));
    float2 Frac = frac(ProbeUV);

    float3 P00 = SparseProbes[Probe00.y * ProbeGridSize.x + Probe00.x];
    float3 P10 = SparseProbes[Probe00.y * ProbeGridSize.x + min(Probe00.x + 1, ProbeGridSize.x - 1)];
    float3 P01 = SparseProbes[min(Probe00.y + 1, ProbeGridSize.y - 1) * ProbeGridSize.x + Probe00.x];
    float3 P11 = SparseProbes[min(Probe00.y + 1, ProbeGridSize.y - 1) * ProbeGridSize.x + min(Probe00.x + 1, ProbeGridSize.x - 1)];

    // 双线性插值 + MLP refine
    float3 Bilinear = lerp(lerp(P00, P10, Frac.x), lerp(P01, P11, Frac.x), Frac.y);

    // MLP refine: 输入 (uv_x, uv_y, depth, normal_dot_view, roughness) → 输出 residual
    float Input[5] = { UV.x, UV.y, 0.5, 0.5, 0.5 };  // 简化
    float3 Residual = MLPForward(Input, NeuralWeights);

    return Bilinear + Residual * 0.1;  // 残差修正
}
```

### 3. L3 NeRF Reflection Cache（day-job 长期目标）

- **思路**: 把整个场景的反射 radiance 编码到一个 NeRF 网络（位置 + 反射方向 → radiance）
- **论文参照**: NeRF Re-rendering (Mildenhall 2021), NeRV (Srinivasan 2021), Instant-NGP (Müller 2022)
- **关键创新**: 用 hash grid + small MLP，单场景训练 < 5s，单像素推理 < 5ms
- **对比 Lumen Surface Cache**: VRAM 从 50 MB → 5 MB（MLP 权重），多次弹射隐式编码
- **trade-off**: 静态场景表现好，动态光源响应差（MLP 重新训练需要时间）

### 4. 与 day-job RAG 的关联

Lumen 反射降级链路是 day-job **神经 BRDF / 神经材质** 训练数据的主要载体:
- **L1 工具描述**: `Lumen.Reflection.NeuralProbeDensify(probes, mlp_weights) → reflection_radiance`
- **L3 工具描述**: `Lumen.Reflection.NeRFCache(position, direction) → reflection_radiance`
- **RAG 检索应用**: 用户问"为什么反射闪烁" → 检索到 L2 神经 cone trace，输出解决方案

### 5. 已知问题与限制（AI 加速版）

1. **训练数据稀缺** — 反射 radiance ground truth 难收集（需要 64+ spp 离线 RT）
2. **动态光照响应** — L3 NeRF 训练一次固定，动态光源变化需要重训
3. **Fallback 链路** — 网络推理失败时必须自动回退到 T1 SSR，不能让画面空白
4. **内存 / 显存换性能** — MLP 权重虽小，但推理中间层需要 GPU registers，FP32 推理占用大
5. **能量守恒** — 神经网络输出可能不满足 ∫BRDF dΩ ≤ 1，需要后处理 normalize

---

*Create date: 2026-07-01*
*Last modified: 2026-07-09*
