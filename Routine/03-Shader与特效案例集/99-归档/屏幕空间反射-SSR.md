---
tags: [shader/自研, shader/post-process, shader/performance]
aliases: [SSR, Screen Space Reflection]
---

# 屏幕空间反射 SSR (Screen Space Reflection)

| 字段 | 内容 |
|------|------|
| **效果名称** | Hi-Z 加速的屏幕空间反射 |
| **类型** | 后处理 / 屏幕空间光线步进 |
| **平台** | PC / Console（移动端谨慎） |
| **创建日期** | 2026-07-01 |
| **参考来源** | 参考自 Unreal Engine 5 SSR 实现 + 《Real-Time Rendering 4th》第 21 章 + SIGGRAPH 2015 "Stochastic Screen-Space Reflections" |

---

## 效果截图

![SSR 平面反射](assets/ssr_plane.png)  
*平面反射：地面 / 水面的镜面反射近似*

![SSR 边缘降级](assets/ssr_falloff.png)  
*边缘降级到环境立方体贴图（roughness 越高、环境贡献越重）*

![SSR 屏幕外失效](assets/ssr_out_of_screen.png)  
*屏幕外反射消失 → fallback 到 cubemap，避免硬截断*

---

## 核心代码

### HLSL — Hi-Z Ray March 主体

```hlsl
// 屏幕空间反射：Hi-Z 加速 + roughness 截断 + cubemap fallback
// 输入：SceneColor, SceneDepth, HiZBuffer, ReflectionEnvCube
float4 PS_SSR(VS_OUTPUT input) : SV_Target
{
    // 1. 重建世界空间反射射线
    float deviceZ = SceneDepth[input.positionCS];
    float3 worldPos = ReconstructWorldPos(input.positionCS, deviceZ);
    float3 viewDir = normalize(worldPos - _CameraPos);
    float3 normalVS = mul(float4(input.normalWS, 0), _ViewMatrix).xyz;

    // 2. 计算反射方向（屏幕空间版本）
    float3 reflectVS = reflect(viewDir, normalVS);

    // 3. Hi-Z 加速步进（参考 UE5 ScreenSpaceReflections.usf）
    float roughness = input.roughness;
    int   mipLevel = (int)(roughness * _MaxMipLevel);   // 越粗糙用越粗的深度图
    float stepSize = _InitialStepSize;
    float3 currentVS = input.positionVS;
    float4 currentCS = float4(input.positionCS, deviceZ);

    float3 hitPos = 0;
    bool   hit = false;

    [loop]
    for (int i = 0; i < _MaxSteps; ++i)
    {
        // 沿反射方向前进
        currentVS += reflectVS * stepSize;
        currentCS  = mul(float4(currentVS, 1), _ProjMatrix);

        // NDC → UV
        float2 uv = (currentCS.xy / currentCS.w) * float2(0.5, -0.5) + 0.5;
        if (any(uv < 0) || any(uv > 1)) break;     // 越界 → cubemap

        // Hi-Z 深度比较
        float sceneZ = HiZBuffer.SampleLevel(uv, mipLevel).r;
        float rayZ   = currentCS.z / currentCS.w;

        if (rayZ < sceneZ + _DepthBias)
        {
            // 命中：二分精修
            float3 prevVS = currentVS - reflectVS * stepSize;
            [unroll(8)]
            for (int j = 0; j < 8; ++j)
            {
                float3 midVS = (currentVS + prevVS) * 0.5;
                float4 midCS = mul(float4(midVS, 1), _ProjMatrix);
                float midRayZ = midCS.z / midCS.w;
                float midSceneZ = HiZBuffer.SampleLevel(
                    (midCS.xy / midCS.w) * float2(0.5, -0.5) + 0.5, mipLevel).r;
                if (midRayZ < midSceneZ + _DepthBias) currentVS = midVS;
                else                                 prevVS   = midVS;
            }
            hit = true;
            hitPos = currentVS;
            break;
        }

        // 自适应步长：与场景深度差成反比
        stepSize = max(_MinStepSize, abs(rayZ - sceneZ) * _StepScale);
    }

    // 4. 命中：采样 SceneColor；未命中：采样环境立方体
    float3 result;
    if (hit)
    {
        float2 hitUV = (mul(float4(hitPos, 1), _ProjMatrix).xy
                      / mul(float4(hitPos, 1), _ProjMatrix).w)
                      * float2(0.5, -0.5) + 0.5;
        result = SceneColor.SampleLevel(hitUV, 0).rgb;
    }
    else
    {
        float3 reflectWS = mul(float4(reflectVS, 0), _InvViewMatrix).xyz;
        float lod = roughness * 8.0;
        result = ReflectionEnvCube.SampleLevel(reflectWS, lod).rgb;
    }

    // 5. 距离 / 边缘衰减
    float distFade = saturate(1.0 - (length(currentVS - input.positionVS) / _MaxDistance));
    float edgeFade = saturate(min(min(input.positionCS.x / 32.0,
                                       _ScreenSize.x - input.positionCS.x),
                                  min(input.positionCS.y / 32.0,
                                       _ScreenSize.y - input.positionCS.y)));
    float visibility = distFade * edgeFade * (1.0 - roughness * _RoughnessCutoff);

    return float4(result * visibility, 1.0);
}
```

### C++ 端调度（伪代码）

```cpp
// 一帧 SSR 的执行顺序
void RenderSSR(CommandBuffer& cmd)
{
    // Pass 1: 降采样深度，生成 Hi-Z mip chain
    cmd.Dispatch(BuildHiZ, /*mipCount=*/8);

    // Pass 2: 屏幕空间光线步进
    cmd.SetRenderTarget(SSRTarget);
    cmd.DrawShader(SSRShader, sceneGBuffer);

    // Pass 3: 与 SceneColor 合成
    cmd.DrawShader(CompositeShader, SceneColor, SSRTarget);
}
```

---

## 参数解释

| 参数名 | 类型 | 范围 | 含义 | 调参建议 |
|--------|------|------|------|----------|
| `_InitialStepSize` | float | 0.05~0.5 | 第一步步长 | 0.1 适合大多数场景，0.3 性能优先 |
| `_MinStepSize` | float | 0.001~0.02 | 最小步长 | 0.005 平衡精度 / 步数 |
| `_MaxSteps` | int | 32~256 | 最大步进次数 | 96 PC 高端 / 64 主流 / 32 移动 |
| `_StepScale` | float | 0.5~2.0 | 自适应步长系数 | 1.0 标准，越大越激进 |
| `_DepthBias` | float | 0.0005~0.01 | 深度容差 | 0.001 标准，越大越不容易漏命中但越容易穿模 |
| `_MaxMipLevel` | int | 4~9 | Hi-Z 最粗 mip | 7 适配 1080p / 8 适配 4K |
| `_MaxDistance` | float | 1000~10000 | 最大追踪距离（cm） | 5000 一般场景，2000 室内 |
| `_RoughnessCutoff` | float | 0.6~1.0 | 超过此粗糙度直接走 cubemap | 0.85 节省算力，0.95 保留边缘高光 |
| `_BinarySearchSteps` | int | 4~16 | 命中后二分精修步数 | 8 标准，再多收益递减 |

---

## 性能分级

| 分级 | 改动 | 性能影响 | 适用场景 |
|------|------|----------|----------|
| **高配** | 256 steps + 16 二分 + Hi-Z mip 9 | 高 (~2.8ms @ 1080p) | PC 高端 / 主机过场 |
| **中配** | 96 steps + 8 二分 + Hi-Z mip 7 | 中 (~1.4ms) | PC 主流 / 主机标准 |
| **低配** | 32 steps + 4 二分 + 半分辨率 | 低 (~0.5ms) | Mobile / Switch |
| **极低** | 关闭 SSR，纯 cubemap | 极低 | VR / 旧硬件 |

> 备注：Hi-Z 加速是性能的关键 — 不开 Hi-Z 直接线性步进 256 次要 6ms+。

---

## 变体版本

- **版本 A：基于 BRDF mask 的重要性采样 SSR** — 沿用 Unreal `r.SSR.Quality` 的 0/1/2/3 档，按像素 BRDF 贡献动态降级，纯漫反射区域直接跳过
- **版本 B：时间累积 + 抖动去噪** — 加入蓝噪声抖动偏移 + 上一帧累积（参考 Frostbite 的 stochastic SSR），可减少 30% 步数仍保持画质
- **版本 C：接触硬化** — 接近地面的反射区域减少模糊（ray 长度越短 → mip 越细），模拟掠射角的菲涅尔效应

---

## 已知问题与限制

1. **屏幕外反射缺失** — 反射射线跑出屏幕就完全没贡献。解决方案：边缘 fade + 强制 fallback 到环境立方体，绝不输出黑色。
2. **自反射错误（self-reflection）** — 反射射线击中自己所在的几何体（薄墙、单平面）。解决方案：法线扰动 + 深度差检测 + 提前 N 步拒绝。
3. **薄壁穿透（thin geometry）** — 玻璃、树叶等薄物体反射会出现"假双面"伪影。解决方案：分层 SSR 或转用真正的硬件 RT。
4. **时间不稳定** — 摄像机快速平移时反射目标帧间跳变。解决方案：Temporal SSR（TAA-style 复用历史帧 + motion vector 重投影）。
5. **Hi-Z 误命中** — 远处小物体在粗 mip 上被平均成一个大表面，造成"鬼影反射"。解决方案：Mip 切换时强制二分精修。

---

## 关联知识库

- [[Ray-Marching-Optimization]] — 通用光线步进性能优化
- [[Hi-Z-Buffer-Construction]] — Hi-Z mip chain 构造
- [[Lumen-GI]] — Lumen 的 SSR fallback 策略对比
- [[TAA-History-Reprojection]] — 时间累积去噪

---

## 复用指南

如何快速集成到自己的项目：

1. **生成 Hi-Z** — 复制 `HiZ/BuildHiZ.cs`，mip 数 = log2(max(width, height))
2. **挂 SSR Pass** — 在 `Deferred Lighting` 之后、`Tonemap` 之前
3. **材质参数面板** — 暴露 `_RoughnessCutoff` 和 `_MaxDistance` 给美术
4. **平台分级** — Mobile 直接走 cubemap（`r.SSR.Quality=0`），不要硬跑 SSR
5. **法线要求** — GBuffer 必须存真实世界空间法线，不能用 view-space 替代

---

## 调参 SOP（踩坑顺序）

```
1. 先把 _MaxDistance 调到场景对角线长度的一半（保证室内外都能覆盖）
2. 调 _DepthBias：先给 0.005 看是否有"穿模"伪影，再降到 0.001
3. 调 _MaxSteps：观察 Nvidia NSight，先给 64 看耗时，再加到 96
4. 调 _RoughnessCutoff：默认 0.85，金属表面可降到 0.6 保留更多反射
5. 打开 BRDF mask（版本 A）做最后优化
```

---

*Create date: 2026-07-01*  
*Last modified: 2026-07-01*
