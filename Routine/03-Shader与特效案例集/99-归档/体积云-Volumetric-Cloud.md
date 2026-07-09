---
tags: [shader/自研, shader/volumetric, shader/performance]
aliases: []
---

# 体积云 Volumetric Cloud

| 字段 | 内容 |
|------|------|
| **效果名称** | 程序化体积云 |
| **类型** | 后处理 / 体积渲染 |
| **平台** | PC / Console |
| **创建日期** | 2025-01-07 |
| **参考来源** | 参考自 Horizon Zero Dawn 技术分享 + 《Real-Time Rendering 4th》 |

---

## 效果截图

![效果正面](assets/cloud_final.png)  
*正面效果：动态变化的积雨云*

![效果参数面板](assets/cloud_params.png)  
*可调参数：覆盖率、密度、风速、光照方向*

---

## 核心代码

### HLSL / Ray Marching

```hlsl
// 核心 Shader 代码 — 简化版
float4 PS_VolumetricCloud(VS_OUTPUT input) : SV_Target {
    float3 rayOrigin = _CameraPos;
    float3 rayDir = normalize(input.worldPos - _CameraPos);
    
    // 云层高范围
    float cloudMin = _CloudBaseHeight;
    float cloudMax = _CloudBaseHeight + _CloudThickness;
    
    // 与云层包围盒求交
    float2 intersect = RayBoxIntersect(rayOrigin, rayDir, cloudMin, cloudMax);
    if (intersect.y < 0) return float4(0, 0, 0, 0); // 无云
    
    float stepSize = (intersect.y - intersect.x) / _StepCount;
    float density = 0;
    float transmittance = 1;
    float3 lightEnergy = 0;
    
    for (int i = 0; i < _StepCount; i++) {
        float3 pos = rayOrigin + rayDir * (intersect.x + i * stepSize);
        
        // 3D 噪声采样 — 低频形状 + 高频细节
        float shapeNoise = SampleNoise3D(pos * _ShapeScale);
        float detailNoise = SampleNoise3D(pos * _DetailScale);
        float combinedNoise = shapeNoise + detailNoise * _DetailStrength;
        
        // 密度场
        float d = saturate(combinedNoise - _Coverage) * _DensityScale;
        if (d < 0.01) continue; // 早期跳过
        
        // 光照积分 — 向太阳方向采样
        float3 lightDir = _SunDirection;
        float lightDensity = SampleLightDensity(pos, lightDir); // 简化的光照 march
        float beerPowder = BeerPowder(lightDensity, _LightAbsorption);
        
        float3 scattering = _CloudColor * _LightColor * beerPowder * _PhaseFunction;
        lightEnergy += transmittance * scattering * d * stepSize;
        transmittance *= exp(-d * stepSize * _LightAbsorption);
        
        if (transmittance < 0.01) break; // 早期退出
    }
    
    return float4(lightEnergy, 1 - transmittance);
}
```

---

## 参数解释

| 参数名 | 类型 | 范围 | 含义 | 调参建议 |
|--------|------|------|------|----------|
| `_CloudBaseHeight` | float | 1000~3000 | 云层底部高度 (m) | 1500 适合大多数场景 |
| `_CloudThickness` | float | 500~2000 | 云层厚度 | 1000 对应标准积雨云 |
| `_Coverage` | float | 0~1 | 覆盖率阈值 | 0.3 少云，0.6 多云，0.8 阴 |
| `_ShapeScale` | float | 0.0001~0.001 | 形状噪声频率 | 越低云块越大 |
| `_DetailScale` | float | 0.001~0.01 | 细节噪声频率 | 建议 ShapeScale × 10 |
| `_DetailStrength` | float | 0~1 | 细节强度 | 0.3 适合远景，0.6 适合近景 |
| `_StepCount` | int | 16~128 | 步进次数 | 64 平衡质量性能 |
| `_LightAbsorption` | float | 0.1~1.0 | 光吸收系数 | 0.5 标准，越高云越暗 |

---

## 性能分级

| 分级 | 改动 | 性能影响 | 适用场景 |
|------|------|----------|----------|
| **高配** | 128 steps + 3D Worley noise + 光照 march 8 steps | 高 (~2.5ms) | PC 高端 / 过场动画 |
| **中配** | 64 steps + 2D 噪声烘焙 3D | 中 (~1.2ms) | PC 主流 / 主机 |
| **低配** | 32 steps + 纯 2D 噪声 + 无光照 march | 低 (~0.4ms) | Mobile / 低配 PC |

---

## 变体版本

- **版本 A：实时天气系统** — 通过 `_Coverage` 参数动画实现晴天→多云→暴雨的过渡，配合 `_CloudColor` 做色温变化
- **版本 B：风格化云** — 降低 `_DetailStrength` 到 0，用 `_StepCount=16`，配合卡通色带实现二次元风格

---

## 已知问题与限制

1. **边缘锯齿** — 低 step count 时云层边缘有明显分层。解决方案：蓝噪声抖动 + TAA 复用历史帧。
2. **背面光照缺失** — 当前只做了单向光（太阳），多光源场景下背光面死黑。解决方案：简化的环境光近似。
3. **性能波动** — 摄像机朝向地平线时 march 距离剧增。解决方案：动态 step size，远距大步进、近距小步进。

---

## 关联知识库

- [[Horizon-Zero-Dawn-Cloud]] — 参考论文/演讲笔记
- [[Ray-Marching-Optimization]] — 性能优化记录
- [[Beer-Powder-Approximation]] — 光照近似公式推导

---

## 复用指南

如何在其他项目中快速复用：

1. 复制 `Shader/VolumetricCloud.hlsl`
2. 复制 `Material/VolumetricCloud.mat` — 注意设置 Render Queue 为 Transparent + 300
3. 设置参数：先调 `_Coverage` 和 `_CloudBaseHeight` 确定云层存在，再调 `_StepCount` 平衡质量
4. 注意平台差异：Mobile 上必须开 `LOD` 开关，自动降到 32 steps + 2D 噪声

---

*Create date: 2025-01-07*  
*Last modified: 2025-01-07*
