---
tags: [perf/CPU, perf/memory, perf/loading, perf/待验证]
aliases: [RT Pool Thrash, 大纹理上传卡顿, Render Thread卡顿]
---

# Render 线程大纹理 / RT 申请抖动

| 字段 | 内容 |
|------|------|
| **现象** | Render 线程出现 ~10ms 级别的卡顿尖刺，常见于关卡切换、流送触发、镜头瞬移 |
| **发现日期** | 2026-07-02 |
| **项目/场景** | UE5 任意有大纹理 / 大量流送的项目 |
| **平台** | 全平台 |
| **严重程度** | 中等（10ms 单次卡顿；频繁触发时变严重） |
| **来源类型** | 知乎 UE5 性能优化-Render线程（一线经验） |

---

## 来源与可信度

| 来源 | 类型 | 关键事实 |
|------|------|----------|
| 知乎《UE5性能优化-Render线程》 | [U] 一线工程师 | 完整列出 RT 申请抖动原因、阈值（64MB）、缓解方案 |
| 知乎《UE5性能优化-GPU》（同作者） | [U] 同源 | 纹理池 extend 抖动 |

> **本文性质：** 知乎一线经验，**未经本人 Profile 验证**。具体阈值（64MB、10ms）与平台/驱动相关。

---

## 现象描述

**触发条件：**

- 关卡加载 / 流送触发瞬间有大量纹理上传
- 剧情瞬移 / 镜头切换导致一帧内大量新纹理需要
- 镜头切换导致 CSM 缓存失效 → 重新申请大深度图

**Profile 表现：**

```bash
stat unit
stat gpu
stat rhi
stat scenerendering
```

观察到：
- **render thread** 出现 5–20ms 级别 spike
- 时间分布：**主要在帧末**（流送申请 + memcpy 上传）
- GPU 端相对平稳，瓶颈在 CPU

**知乎原文：**
> "对于大贴图，GPU 专用显存和 upload buffer 都不走池，这里申请会达到 10MS 以上的卡顿"

---

## 根因分析

### 纹理上传的三段式开销

知乎原文：
> "一个贴图的上传有三部分，申请 GPU 专用显存，申请 upload buffer 上传 GPU，从流送的贴图内存 copy 到 upload buffer"

| 阶段 | 正常（走池） | 大纹理（不走池） |
|------|-------------|------------------|
| 申请 GPU 显存 | 池内复用 | 独立调用驱动 → ~ms 级 |
| 申请 upload buffer | 池内复用 | 独立调用驱动 |
| memcpy 上传 | 池内 buffer 预热 | **跨多页 + 冷页 → 缺页中断爆炸** |

**冷页缺页中断：**
> "由于系统存在惰性初始化机制，一开始的内存而全是冷页，memcpy 会产生大量的缺页中断，耗时非常高"

——这是申请大块连续内存时必然发生的"初始化税"。

### 阈值

> "对于大贴图（如超过 64M），GPU 专用显存和 upload buffer 都不走池"

——64MB 是分水岭。超过此大小的纹理都走"独立申请 → 卡顿"路径。

### CSM 缓存失效触发的深度图申请

知乎原文（GPU 篇）：
> "正常来说，平行光的深度图都是固定的，但是会有一种情况产生深度图的申请，CSM 缓存（r.Shadow.CSMCaching），当两帧之间的 CSM 重叠低于一个阈值的时候，会 InvalidateCachedShadow，这时会产生大深度图的申请，这个申请抖动我们是不能接受的，禁用 CSM 缓存。"

---

## 解决方案（按收益从大到小）

### 方案 A：预加载大纹理（最有效）

知乎原文：
> "对于大贴图，我的建议是预加载，在进游戏 loading 的时候加载好，一般都是些 UI 底图。"

**实现：**

```cpp
// 在加载屏幕（或关卡加载函数）里：
TArray<FSoftObjectPath> BigTexturesToPreload = {
    FSoftObjectPath("/Game/UI/LoadingScreen_BG"),
    FSoftObjectPath("/Game/Cutscenes/Opening_MainBG"),
    // ...
};
FStreamableManager& Streamable = UAssetManager::GetStreamableManager();
Streamable.RequestAsyncLoad(BigTexturesToPreload, FStreamableDelegate());
```

**好处：** 把冷页缺页中断分散到加载屏幕的几十毫秒里，不挤进 gameplay 帧。

### 方案 B：内存预热（次优）

知乎原文：
> "对于大贴图，我的建议是预加载……一般像这种情况，也可以通过内存预热做处理，每一个页读取一个字节，但是麻烦。"

```cpp
// 强制每页 touch 一次
volatile uint8* TouchPtr = (volatile uint8*)Buffer;
for (size_t i = 0; i < BufferSize; i += PageSize) {
    (void)TouchPtr[i];
}
```

——强行触发缺页中断。**麻烦但有效**。

### 方案 C：禁用 CSM 缓存（如果深度图申请是主因）

```ini
r.Shadow.CSMCaching=0
```

**触发条件：** 镜头瞬移 / 大范围移动 → CSM 缓存失效 → 重新申请大深度图。

**权衡：** 失去缓存 → basepass 重绘成本上升。需要权衡帧时间和缓存收益。

### 方案 D：VT 化 / 纹理合并（减小单纹理体积）

知乎原文：
> "对这种情况，我的建议是，能走 VT 的材质都走 VT，贴图能合并的都走合并。"

- **VT 化：** 4K+ 纹理走 Virtual Texture，按需流送
- **RGB 通道合并：** ORM（AO/Rough/Metal）合并到一张图的 RGB → 单文件 1/3 大小

### 方案 E：纹理流送池调优

```ini
r.Streaming.PoolSize=2048   ; 默认 1000；调大避免流送抖动
```

——避免"流送池不足 → 切 mip → 重新流送"的循环抖动。

---

## 验证流程（自己 Profile 时跑一遍）

| 步骤 | 工具 / 命令 | 看什么 |
|------|------------|--------|
| 1. 抓卡顿帧 | `stat dumphitches`（输出 log 含每次 spike 的耗时） | 哪些函数耗时 |
| 2. 看 RT 时序 | Unreal Insights → RenderThread track | RT spike 集中在帧末 → 大概率本案例 |
| 3. 测预加载 | 在 loading screen 加载目标纹理 | 对比 spike 高度 |
| 4. 测 CSM 缓存 | 关 `r.Shadow.CSMCaching=0` | 镜头瞬移 spike 是否消失 |
| 5. 测纹理池 | 调 `r.Streaming.PoolSize` | 频繁切 mip 警告是否消失 |

**判断标准：** render thread 不再有 > 5ms 的 isolated spike。

---

## 经验沉淀

**肌肉记忆：**

| 看到 | 先查 |
|------|------|
| RT spike + 关卡/流送 | 大纹理申请，预先在 loading screen 加载 |
| RT spike + 镜头瞬移 | CSM 缓存失效，考虑 `r.Shadow.CSMCaching=0` |
| RT 持续 spike + 大量实例移动 | GPU Scene 频繁 upload，合并 Niagara / 减少动态 |
| RT spike + RT 申请 | 大深度图或 RT 池抖动，禁用 CSM 缓存或预加载 |

**可复用方案：** "loading screen 预加载所有大纹理"是几乎所有 3A 项目的标配；预热一次换整个项目的稳定性。

---

## 关联知识库

- [[知识参考/渲染线程瓶颈诊断]] — Render 线程卡顿的整体方法论
- [[知识参考/Lyra 性能架构]] — Lyra 的加载流程（5 阶段）是 loading screen 设计的参考
- [[VSM-页溢出-阴影棋盘瑕疵]] — CSM/VSM 缓存抖动在本案例的延伸

---

*Create date: 2026-07-02*
*Last modified: 2026-07-02*
*Verified: 否（公开资料汇编，本人未 Profile）*
*Source URLs（公开资料，作者/标题已注明）:*

- **知乎《UE5性能优化-Render线程》**（作者：草木不全；本文核心来源）：
  - 知乎站内搜索：https://www.zhihu.com/search?type=content&q=UE5%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96-Render%E7%BA%BF%E7%A8%8B
  - 注：本文 90% 内容直接引用自该文，包括 64MB 阈值、~10ms 单次卡顿、CSM 缓存失效、distance field 3d 贴图上传等具体细节
- **知乎《UE5性能优化-GPU》**（作者：草木不全，同系列）：
  - 知乎站内搜索：https://www.zhihu.com/search?type=content&q=UE5%E6%80%A7%E8%83%BD%E4%BC%98%E5%8C%96-GPU
  - 注：本文"纹理池 extend 抖动"小节引用自此

> 我**未能直接获取原文精确 URL**。如需定位原文，请在知乎站内搜索结果中找标题/作者名匹配的文章。
>
> **重要修正提示：** 这篇笔记早期版本 Source URLs 段曾引用"知乎《UE5性能优化-Render线程》: https://zhuanlan.zhihu.com/p/..."——**这是占位符 URL，不存在**。真实的知乎原文需通过上方站内搜索 URL 定位，作者 ID 为"草木不全"。