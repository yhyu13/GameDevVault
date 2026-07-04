---
tags: [radar/P1, radar/AI-资产生成, radar/工具链]
aliases: [Stable Diffusion, FLUX, FLUX.2, SDXL, ComfyUI, AI 美术, 文本生图, LoRA, ControlNet]
quarterly_review: 2026-Q3
---

# Stable Diffusion / FLUX — AI 美术管线(贴图/概念图/Icon)

| 字段 | 内容 |
|------|------|
| **技术名称** | Stable Diffusion / FLUX 文本生图生态(SD 1.5/SDXL/SD3/FLUX.1/FLUX.2) |
| **类别** | AI 资产生成 / 工具链 |
| **当前优先级** | P1 |
| **发现日期** | 2026-06-25 |
| **最后评估日期** | 2026-06-25 |

---

## 一句话简介

> 文本 → 图像的扩散模型生态 — **2026 年 FLUX.2 (32B 参数) + ComfyUI 工作流 已经是 AI 美术的事实生产工具,Steam 上 1 万+ 游戏标注"使用生成式 AI",渗透率 86%**。从概念图、UI icon、贴图素材到角色立绘,正在重做整个美术前置流程。

---

## 成熟度评估

| 维度 | 评分 (1-5) | 说明 |
|------|------------|------|
| 生产可用性 | 5 | 国内三七互娱/网易/腾讯/米哈游全在用,海外暴雪/EA/育碧早用 |
| 文档完善度 | 5 | ComfyUI / A1111 / FLUX 官方文档齐全,中文社区极活跃 |
| 社区活跃度 | 5 | Civitai / HuggingFace / r/StableDiffusion 日活极高,LoRA 日增千级 |
| 学习资源 | 5 | 提示词工程、LoRA 训练、ControlNet 教程遍地都是 |
| 与现有栈兼容性 | 5 | 输出 PNG 直接进 UE / Unity / Godot,贴图自动接 Substance / Quixel |

**2026 年 6 月生态现状:**
- **FLUX.2**(2025 末,黑森林实验室):最大 32B 参数,文字渲染、上下文编辑一流,本地可跑 8-13GB 显存版
- **SDXL / SD3**:老牌稳定,生态最大,LoRA 多
- **ComfyUI** + **A1111**:两套主力 UI,ComfyUI 工作流模式更适合生产
- **LoRA / ControlNet / IPAdapter**:三大控制工具,缺一不可
- **RTX 加速**:NVIDIA 已在 ComfyUI 中集成 PyTorch-CUDA 优化 + NVFP4/FP8,**出图速度 3 倍提升,显存省 60%**

---

## 学习成本估算

| 阶段 | 时间 | 产出 |
|------|------|------|
| 上手入门 | 3 天 | 装 ComfyUI,跑通文生图 + 图生图基础工作流 |
| 熟练应用 | 2 周 | 掌握 ControlNet(IP-Adapter / Depth / Pose) + LoRA 微调,能稳定出"想要"的图 |
| 深度掌握 | 2-3 月 | 能训练自定义 LoRA(角色一致性 / 画风统一)、能搭复杂 ComfyUI 工作流(SD + ControlNet + Upscale + Inpaint) |

**关键技能点(实操导向):**
- **提示词工程**:CLIP 词 + 权重 + 反向提示词 — 这是"会出图"和"出好图"的分水岭
- **LoRA 训练**:用自己的素材(角色图、画风参考)微调,20-50 张图训 1-2 小时
- **ControlNet 控制**:用 pose / depth / canny 控制构图,**避免 AI 乱画**
- **ComfyUI 工作流**:把生成拆成"草图 → 精修 → 放大 → 局部修复"流水线
- **法务边界**:版权、Steam 标注、欧盟 AI 法案对训练数据的要求 — **不能忽略**

---

## 与当前工作的关联

- [ ] 直接相关 — 当前项目可用
- [x] 间接相关 — 未来项目可能用
- [x] 知识拓展 — 拓宽技术视野(理解美术管线,方便和美术/技术美术沟通)

**具体关联点:**
- **贴图生成**:SD/FLUX + ControlNet(tile) 可以出"无缝可平铺的 PBR 贴图 base color**,然后 Substance 加工
- **UI icon 量产**:1 天 200+ 个 icon,不再依赖美术排期
- **概念图验证**:方案设计阶段 1 小时出 50 张概念稿,而不是 3 天画 3 张
- **NPC 立绘**:角色 LoRA + IPAdapter,稳定出"同一个角色不同姿势/服装"
- **对 UE 的工程入口**:FLUX 已经能直接通过 ComfyUI 输出 4K 图,挂上 PBR 通道就当基础材质用

**对你 day-job 的真实杠杆:**
- 理解技术美术在做啥,沟通成本减半
- 自己做 quick prototype 时,icon 和概念图不求人
- 面试能讲"AI 美术管线" 是个加分项

---

## 评估记录

| 日期 | 评估人 | 结论 | 下次回顾 |
|------|--------|------|----------|
| 2026-06-25 | 我 | P1 持续关注 — 美术主管导,自己不一定要上手画,但要懂 | 1个月后 |
| 2026-07-03 | 我 | Q3 启动 — 纳入季度复盘 Routine | 2026-07-25 |

---

## 关键资源

- ComfyUI 官方:https://github.com/comfyanonymous/ComfyUI
- FLUX 官方:https://blackforestlabs.ai/
- Civitai 模型市场:https://civitai.com/
- HuggingFace 模型:https://huggingface.co/models?pipeline_tag=text-to-image
- 秋叶整合包(国内开箱即用):https://www.bilibili.com/video/BV1iM4y1y7oA/
- NVIDIA RTX 加速 ComfyUI:https://blogs.nvidia.com/

---

## 状态迁移

- [x] P0 → 正在学习中 → 已掌握 → 移出雷达
- [x] P1 → 评估后降为 P2 / 升为 P0
- [ ] P2 → 评估后放弃 / 升为 P1

---

## 我的判断(只对你说)

**对程序员来说,这个 P1 不是"学 SD 画图",而是"懂 SD 在干啥,能和技术美术对话"**。  
最值钱的不是出图能力(那是你和美术比),而是**"理解 AI 美术的边界"** — 知道 SD 出 8K 贴图很难(分辨率限制)、知道 LoRA 训练 50 张图就够、知道 ComfyUI 工作流可以"批量出"。  
如果你要升 senior,这个必须懂;不升的话,知道就好。  
**避坑:版权** — Steam 2024 起强制标注"使用生成式 AI",训练数据来源不清的素材有法律风险,商业项目必须用 FLUX / Adobe Firefly / Shutterstock 这种训练数据合规的方案。

---

*Create date: 2026-06-25*  
*Last modified: 2026-06-25*
