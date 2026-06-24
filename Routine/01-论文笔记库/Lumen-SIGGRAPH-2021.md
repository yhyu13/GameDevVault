---
tags: [paper/signed, paper/lumen, paper/待复现]
aliases: []
---

# Lumen: Global Illumination in Unreal Engine 5

| 字段 | 内容 |
|------|------|
| **论文标题** | Lumen: Global Illumination in Unreal Engine 5 |
| **作者** | Karis, B. et al. (Epic Games) |
| **发表年份/会议** | SIGGRAPH 2021 |
| **原始链接** | [GDC Talk](https://www.youtube.com/watch?v=O-0SJENq4K4) / [PDF 见 UE 文档](https://docs.unrealengine.com/5.0/en-US/lumen-global-illumination-and-reflections-in-unreal-engine/) |
| **阅读日期** | 2025-01-06 |
| **精读时长** | 2h |

---

## 一句话总结

> 这篇论文解决了动态开放世界中实时全局光照的问题，通过结合**光线追踪（Software Ray Tracing）**和**辐射度缓存（Radiance Cache）**的分层方案，在消费级硬件上实现了无预烘焙的全局光照。

---

## 核心创新点

1. **Software Ray Tracing** — 不依赖硬件 RT Core，通过 SDF + Mesh Card 实现高质量的软件光追，兼容更广泛硬件。
2. **Radiance Cache 分层** — 远距离用低频辐射度缓存，近距离用高分辨率 Surface Cache，平衡质量与性能。
3. **Screen Space Probe** — 在屏幕空间放置探针，动态更新，避免传统 Lightmap 的预烘焙限制。

---

## 与我当前工作的关联度

- [x] P0 — 直接相关，当前项目正在评估实时光照方案
- [ ] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点：** 我们正在做的一个开放世界项目需要动态昼夜系统，烘焙光照完全不可行。Lumen 的辐射度缓存思想可以借鉴到我们的自研引擎中，即使不实现完整 Lumen，也能做简化版。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|-------------|
| SDF 生成与更新 | 每个 Mesh 需要生成 SDF，动态物体更新开销大 | 是 — 这是核心 |
| Surface Cache 管理 | 需要管理大量小纹理的分配与回收，像虚拟纹理 | 是 — 与 VT 系统联动 |
| Probe 放置策略 | 屏幕空间放置需要处理边缘 case（新暴露区域） | 是 — 质量关键 |
| 多帧复用 | 时间稳定性与响应性的平衡，TAA 类似问题 | 是 — 性能关键 |

---

## 是否值得复现？

- [x] 是 — 已列入待办
- [ ] 否 — 仅了解思路即可
- [ ] 部分 — 只复现核心算法

**复现计划：** 不实现完整 Lumen，而是实现一个简化版：
- 只实现静态场景的 SDF 光追
- 辐射度缓存降采样到 1/4 分辨率
- 先支持漫反射 GI，暂不支持镜面反射
- 预计周末 3h × 4 周完成

---

## 关键公式/伪代码

```cpp
// Lumen 的核心追踪循环 — 简化版
float3 TraceRay(Ray ray, SceneSDF scene) {
    float t = 0;
    for (int i = 0; i < MAX_STEPS; i++) {
        float dist = scene.SampleSDF(ray.pos);
        if (dist < EPSILON) {
            return scene.SampleRadiance(ray.pos, ray.dir);
        }
        t += dist;
        ray.pos += ray.dir * dist;
        if (t > MAX_DISTANCE) break;
    }
    return SkyRadiance(ray.dir);
}
```

---

## 相关论文/前置知识

- [[SDF-Based Rendering]] — SDF 渲染基础，Lumen 的追踪基础
- [[Voxel-Based GI]] — 对比方案，理解为什么 Lumen 选择 SDF 而非体素
- [[Screen Space Probes]] — 屏幕空间探针的通用理论

---

## 个人评价

**优点：** 工程化程度极高，解决了开放世界动态 GI 的业界难题；Software RT 的思路非常务实，不盲目追新硬件。  
**局限性：** 纯软件方案在复杂场景下开销仍大；镜面反射质量不如硬件 RT；对植被等高频细节处理一般。  
**启发：** 做技术选型时，不要只追最新硬件特性，软件方案 + 聪明的分层近似往往更务实。

---

## 面试谈资准备

**30秒版本：**  
> "Lumen 是 UE5 的实时光照系统，核心思路是用 SDF 做软件光追，配合分层辐射度缓存，在消费级 GPU 上实现无预烘焙的全局光照。"

**2分钟版本：**  
> "Lumen 的核心创新是三层结构：最底层用 SDF 做软件光线追踪，避免依赖 RTX 硬件；中间层用 Surface Cache 缓存直接光照，减少重复计算；最高层用 Radiance Cache 做远距离的低频近似。对于动态物体，它用屏幕空间 Probe 动态更新。我自己正在复现一个简化版，重点关注 SDF 生成和辐射度缓存的联动。"

---

## 输出产物

- [x] 已写笔记（本文）
- [ ] 已复现代码 → 周末启动 [[Lumen-Mini-Demo]]
- [ ] 已写博客 → 复现完成后写
- [ ] 已分享/交流 → 下次组会分享

---

*Create date: 2025-01-06*  
*Last modified: 2025-01-06*
