---
tags: [paper/signed, paper/video, paper/Lumen, paper/UE5, paper/rendering, paper/待复现]
aliases: [Lumen-HowItActuallyWorks, Stop-Guessing-Lumen-UE5]
---

# Stop Guessing: How Lumen Actually Works in UE5

> 别猜了：Lumen 在 UE5 中到底是怎么运作的

| 字段 | 内容 |
|------|------|
| **Talk 标题** | Stop Guessing: How Lumen Actually Works in UE5 |
| **讲者** | (YouTube 上传者 / creator 视频，未署名） |
| **年份** | 2022–2023 (基于 UI / 5.1 提及推断) |
| **原始链接** | YouTube: <https://www.youtube.com/watch?v=WuzJ8hYDVYA> · B 站: <https://www.bilibili.com/video/BV1GnEe6aELp/> |
| **本地视频** | `Routine/01-论文笔记库/Lumen/Lumen-HowItActuallyWorks-UE5.mp4` (1920×1080@60fps · 51:50 · 218 MB) |
| **本地 PPT** | `Routine/01-论文笔记库/Lumen/Lumen-HowItActuallyWorks-UE5.pptx` (20 slides · 2.2 MB) |
| **本地字幕** | `Routine/01-论文笔记库/Lumen/Lumen-HowItActuallyWorks-UE5.transcript.txt` (~49 KB · 5 段切片合并) |
| **Slide 帧图** | `Routine/01-论文笔记库/Lumen/slide-images/` (10 张关键帧, PPT 直接引用) |
| **阅读日期** | 2026-06-28 |
| **精读时长** | ~1.5h (transcript + 20 张 PPT + 视频重点段落对照) |

---

## 一句话总结

> 这是一条 **52 分钟的 Lumen 实战向科普** —— 把 [[Lumen-SIGGRAPH-2021]] 那套 *Software Ray Tracing + Radiance Cache + Surface Cache* 的学术抽象，落到 **UE5 编辑器实际菜单** 上：哪些 Project Settings 要勾选、Ray Lighting Mode 怎么选、Surface Cache vs Hit Lighting 在视图里长什么样、为什么薄墙会漏光、为什么 flat 材质会闪烁、SSAO 怎么跟 Lumen 共存。

---

## 这条视频在 vault 里能补什么

已有的 [[Lumen-SIGGRAPH-2021]] 是 SIGGRAPH 2021 论文向的拆解 —— SDF、Radiance Cache、Probe 放置策略这些**底层机制**讲得深，但**没讲编辑器操作**。
这条视频正好反过来：它默认你已经知道 Lumen 是干啥的，全部精力放在 **"打开 UE5 项目后到底要勾哪些开关、哪些设置会跟哪些 artifact 对应"**。

把它放进 vault 的目的不是替代 SIGGRAPH 笔记，而是 **两者对照读**：
- SIGGRAPH 笔记 → 想知道 Lumen 为什么这么做（理论层）
- 这条视频 → 想知道 Lumen 在我场景里为什么不这么做（操作层）

---

## 核心结构（视频原顺序 → PPT 对应 slide）

| 视频段落 | 时间戳 | PPT slide | 一句话 |
|---------|--------|-----------|--------|
| 开场 + Lumen 是什么 | 0:00 – 3:00 | slide 1, 2 | Lumen = 实时 GI + Reflections 的UE5 内建系统 |
| Global Illumination / Final Gather | 3:00 – 6:30 | slide 3 | 间接光照 + 噪声平滑 |
| 双路径：HW RT vs SW RT | 6:30 – 11:30 | slide 4, 8 | 硬件贵但准 / 软件便宜但粗 |
| Screen Space Traces | 7:00 – 10:30 | slide 5 | 摄像机画面内做 GI fallback |
| Distance Fields + Surface Cache | 11:30 – 16:30 | slide 6, 7 | SW RT 的两根柱子 |
| Pros / Cons | 16:30 – 19:30 | slide 9 | 性能成本表 |
| Project Settings 实战 | 19:30 – 24:00 | slide 10, 11, 12 | SM6 / GI=Lumen / Ray Lighting Mode / SW RT Mode |
| 场景演示（Rect Lights） | 24:00 – 30:00 | slide 13 | 删掉直接光后 Lumen 还能 fill |
| Post Process Volume 覆盖 | 30:00 – 35:00 | slide 14 | 局部 override 优于全局 |
| View Modes & 调试 | 35:00 – 38:00 | slide 15 | Lumen Scene / Mesh DF 可视化 |
| 实战 tips（厚度、材质、光） | 38:00 – 45:00 | slide 16, 17 | directional ≪ spot < point < rect |
| Emissive material 注意事项 | 45:00 – 47:00 | (slide 9 第二部分) | 单独讨论，发光面要够大 |
| SSAO + Lumen 共存 (cvar trick) | 47:00 – 51:00 | slide 18 | `r.SSAO 1` + `ScreenProbeGather.ShortRangeAO 0` |
| 收尾 + 下期预告 | 51:00 – 51:50 | slide 20 | 预告 baked lighting 对比 |

---

## 编辑器层落地清单（直接可用的 cheat-sheet）

### Project Settings → Rendering

- **Platforms → Windows → Shader Format** = `SM6`（DX12 必要条件；Vulkan 路径另算）
- **Rendering → Global Illumination** = `Lumen`（不要选 Screen Space / Plugin / None）
- **Rendering → Reflections** = `Lumen`
- **Rendering → Lumen** 区块：
  - ✅ `Use Hardware Ray Tracing when available`
  - `Ray Lighting Mode` = `Surface Cache` / `Hit Lighting` / `Hit Lighting and Reflections`
  - `High Quality Translucency Reflections` ✅
  - `Software Ray Tracing Mode` = `Global Tracing`（便宜） / `Detail Tracing`（每 mesh 独立 DF，贵但准）
  - `Screen Tracing Source` = `Anti-aliased Scene Color, with Translucency`
  - `Allow Static Lighting` ❌

### Post Process Volume（局部 override）

- `Global Illumination → Method` = `Lumen`（同 Project Settings）
- `Lumen Global Illumination`：
  - `Ray Lighting Mode`（同上三种）
  - `Lumen Scene Lighting Quality`（2 / 4 → 软化黑斑，更贵）
  - `Lumen Scene Detail`（提高 → 减少小几何 flicker）
  - `Final Gather Quality`（2 / 4 → 更平滑但更慢）
  - ✅ `Screen Traces`（注入 in-frame GI）

### Viewport View Modes（调试必备）

- `Lit → Lumen` → `Lumen Scene`：看 Lumen 当前 GI 数据；**会闪烁**（实时累积）
- `Lit → Lumen → Surface Cache`：看 surface cache 视图
- `Show → Visualize → Mesh Distance Fields`：看每个 mesh 的 DF proxy（**漏光高发区定位**）

---

## 实战 tips（视频原话精简）

| 类别 | 关键约束 | 原因 |
|------|---------|------|
| **几何厚度** | 墙体/楼板/天花 ≥ 20–25 cm | DF proxy 在薄几何上失真 → 漏光 |
| **材质表面** | 别用全 flat planar 颜色 | flat 面会暴露 surface cache 更新延迟 → sparkle |
| **材质表面** | 镜面/高光反射降到 0.25–0.30 roughness | 高 roughness 隐藏 Lumen 噪声 |
| **光源类型** | directional ≪ spot < point < rect | rect ≈ 3–4 个 spot，**重叠动态光爆炸贵** |
| **发光材质** | 用作面积光，**别做小斑点** | 小 emissive 是 Lumen 噪声/闪烁的头号来源 |
| **Viewport** | Scalability ≥ HIGH 才看得见 Lumen | medium/low 实际是关闭 |
| **SSAO** | `r.SSAO 1` + `Lumen.ScreenProbeGather.ShortRangeAO 0` | 加一层经典 AO 修 Lumen GI 自带 AO 太软的角落 |

---

## 与我当前工作的关联度

- [ ] P0 — 直接相关，立即能应用
- [x] P1 — 有关联，可中长期借鉴
- [ ] P2 — 纯知识拓展，开阔视野

**具体关联点：**
1. **如果接 Lumen 商业项目**：编辑器层 checklist + 实操 tips（厚度、材质粗糙度、光源选型）直接拿来当 art-bible。
2. **如果做自研实时光照**（[[Lumen-SIGGRAPH-2021]] 里提到的简化版）：这条视频里 *"哪个旋钮控制哪类 artifact"* 的因果链，是验证简化版是否对齐预期的最快方法。
3. **面试向**：[[Lumen-SIGGRAPH-2021]] 已有 30 秒 / 2 分钟版本；这条视频可以作为 **"UE5 编辑器操作层"** 的延伸谈资，被问 *"Lumen 实际用起来要注意什么"* 时甩出来。

---

## 实现难点分析

| 难点 | 我的理解 | 是否需要深入 |
|------|----------|---------------|
| Surface Cache 闪烁在什么时候被放大？ | 跟材质 brightness + camera 移动速度强相关；视频没定量 | 否 — 定性足够，量化要 profile |
| HW RT 和 SW RT 切换的运行时成本 | 没有具体切换开销数据，视频只说"HW 更贵" | 否 — 决策时主要看目标硬件 |
| `ScreenProbeGather.ShortRangeAO` cvar 副作用 | 只在 cvar console 生效；关闭场景失效；需要写进 `DefaultEngine.ini` | 是 — 工程化部署时要落 ini |
| Mesh Distance Field 生成开销 | 视频只说"自动生成"，没量化 mesh 数 / 三角形数对 build 时间影响 | 否 — UE 文档有量化数据 |

---

## 是否值得复现？

- [ ] 是 — 已列入待办
- [ ] 否 — 仅了解思路即可
- [x] 部分 — 只在 **Lumen 编辑器清单** 这层做记录

**复现计划：**
1. 把上面的 cheat-sheet 落到 `Career/Kimi/SOP-Unreal-Lighting.md` 作为 SOP 草稿
2. 跟 [[Lumen-SIGGRAPH-2021]] 的简化版实现记录关联：每个简化版假设都要回答 *"这个简化能不能跑通视频里说的这几个 tips"*
3. 下次接 UE5 灯光相关需求前，先打开 `slide-images/` 里的 6 张 PPT 截图快速对齐语言

---

## 关键公式/伪代码

```cpp
// 视频里没有新公式，但有一个隐性"分层近似"公式可以记一下
// （这是 Lumen 的设计哲学，不是某段代码）

lighting_result(p) = screen_space_traces(p)
                  + software_rt(p, df_proxy, surface_cache)
                  + hardware_rt(p, hit_reflections)
                  // 三层各自 cost 递增、按 priority 合并
                  // 最终合并方式 = priority-based blend, not max/min
```

---

## 相关笔记 / 前置知识

- [[Lumen-SIGGRAPH-2021]] — 理论层（DF + Radiance Cache + Surface Cache 学术向）
- [[Lumen-实战手册：渲染-Profile-调优-场景搭建指南]] — 操作层（UE5 编辑器实战汇总）
- 后续待写（如果有 UE5 项目实战）：[[Lumen-Project-Settings-SOP]] — 把本笔记的 cheat-sheet 拆成可直接抄的 DefaultEngine.ini 片段

---

## 个人评价

**优点：**
- **编辑器层 cheat-sheet 价值极高** —— 51 分钟里塞了 7-8 个我之前在 SIGGRAPH 论文里找不到答案的操作问题（漏光、闪烁、SSAO 冲突）。
- **没有 marketing buzzword** —— 视频标题就明确说"Stop Guessing"，通篇把 HW RT / SW RT / Screen Space 拆得很干净，对术语恐惧症友好。
- **演示节奏对** —— 每一个概念都跟一个编辑器操作对应（Settings 截图、View Mode 切换、Post Process Volume 调参），**不需要先相信再验证**。

**局限性：**
- **没有量化数据** —— "更贵"、"更快"全凭经验感觉，没有 frame-time / VRAM 数字。
- **5.1 提及的中等质量模式已经过时** —— 现在 5.4+ 又有新变化，这条视频大概落后 2 个大版本，需要对照 5.x release notes 验证。
- **不涉及 Lumen Scene Lighting Update Speed / Diffuse Color Boost / Volumetric Lighting 那一批 cvar** —— 高级调参这块没覆盖。

**启发：**
- **"分层近似"是一个可移植的设计模式** —— Lumen 把屏幕空间 / DF 代理 / HW RT 三层按 cost 优先级叠加，这个思路可以直接搬到自研引擎的 GI 实现里：先 cheapest 跑，再叠 mid，最后叠 expensive。
- **视频形式的知识比论文更适合做"操作 SOP"** —— 论文讲"为什么"，视频讲"哪里点哪个按钮"。两者不可互相替代。

---

## 面试谈资准备

**30 秒版本：**
> "Lumen 在 UE5 里是三层叠加：Screen Space Traces 做最便宜的 in-frame 注入，Software Ray Tracing 用 Mesh Distance Field + Surface Cache 做中等成本近似，Hardware Ray Tracing 用 hit reflections 做准确但昂贵的光追。实际项目里 80% 的 artifact 都来自第二层（DF proxy 失真 + Surface Cache 更新延迟），对应到 art bible 就是厚度 ≥ 20cm、材质别用全 flat、光源少用 rect、别用小 emissive 斑点。"

**2 分钟版本：**
> "如果让我现在接一个 Lumen 项目，第一步不是调参，是把 Project Settings 锁死：SM6、GI=Lumen、Reflections=Lumen、Allow Static Lighting=OFF。第二步打开 Post Process Volume 的 Ray Lighting Mode，决定走 Surface Cache（低成本）还是 Hit Lighting（高成本）。第三步看 Viewport ≥ HIGH，否则啥都看不到。Lumen 漏光的根因几乎都是 Mesh Distance Field 的 proxy 在薄几何上失真 —— 所以墙体 ≥ 20cm 是硬性 art 约束。闪烁的根因是 Surface Cache 更新延迟跟不上 camera 移动，加材质 roughness / 提高 Lumen Scene Detail 都能压住。如果还嫌 GI 自带的 AO 太软，可以 `r.SSAO 1` 加上 `Lumen.ScreenProbeGather.ShortRangeAO 0` 把经典 SSAO 叠回来。"

---

## 输出产物

- [x] 已写笔记（本文）
- [x] 已生成 PPT (`Lumen-HowItActuallyWorks-UE5.pptx`，20 slides)
- [x] 已下载视频 (`Lumen-HowItActuallyWorks-UE5.mp4`，218 MB)
- [x] 已转录 transcript（49 KB 文本，可搜索）
- [ ] 已拆出 SOP 草稿 → 链接到 [[Lumen-Project-Settings-SOP]]（待写）
- [ ] 已分享 / 交流

---

*Create date: 2026-06-28*
*Last modified: 2026-06-28*