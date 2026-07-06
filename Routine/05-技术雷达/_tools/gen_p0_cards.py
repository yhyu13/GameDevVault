# -*- coding: utf-8 -*-
"""
生成 05-技术雷达/P0-立即学习/ 下每条目的 Q&A 互动卡 HTML。
模板紧贴 interview-card-system 规范:拖拽填空 / 单选 / 多选 / 判断题 / 总览 / 打分。

用法:
    python gen_p0_cards.py

输出:
    Routine/05-技术雷达/P0-立即学习/<basename>.html
"""
import os
import json

OUT_DIR = r"C:\Git-repo-my\GameDevVault\Routine\05-技术雷达\P0-立即学习"

# 7 个 P0 条目的题目数据
# 每个 entry 含: title / subtitle / topic / dragQ / singleQ / multiQ / tfQ / source_md
ENTRIES = [
    {
        "basename": "DLSS-FSR-AI超分辨率",
        "title": "DLSS / FSR / XeSS — AI 实时超分辨率三件套",
        "subtitle": "P0-立即学习 | 引擎标配,Lyra 4K 路径追踪离不开它",
        "source_md": "DLSS-FSR-AI超分辨率.md",
        "drag": [
            {
                "sentence": "DLSS 由 {0} 出品,FSR 4 由 {1} 出品,二者都靠时序抗锯齿(TAA/TSR)做基础。",
                "answers": ["NVIDIA", "AMD"],
                "pool": ["NVIDIA", "AMD", "Intel", "Qualcomm", "ARM"],
                "per_slot_analysis": [
                    "NVIDIA 出 DLSS 系列,要求 RTX 显卡;非 NVIDIA 卡走 FSR / XeSS。",
                    "AMD 出 FSR 系列,基于 RDNA4 首发,纯 AI 驱动,INT8 下放 RDNA3。"
                ]
            },
            {
                "sentence": "DLSS 4.5 的 6x 多帧生成(MFG)在 {0} 系独占,XR 后端用 {1} 模拟跨厂商加速。",
                "answers": ["RTX 50", "DirectML"],
                "pool": ["RTX 50", "RTX 30", "RTX 20", "DirectML", "Vulkan"],
                "per_slot_analysis": [
                    "6x MFG 依赖 RTX 50 硬件 flip metering,不是纯软件方案;RTX 30/20 也能享受画质提升但 MFG 倍数低。",
                    "DirectML 是 NNE 后端之一,跨厂商 GPU(Xbox / AMD / Intel)上跑 NNE 模型用。"
                ]
            }
        ],
        "single": [
            {
                "question": "DLSS 4.5 的 Ray Reconstruction 在 Computex 2026 上公布的核心指标是?",
                "options": [
                    "A. 替代 DLSS 4 SR 模型,只跑 1080p 上采样",
                    "B. 用 Transformer 模型替代手工降噪器,降噪能力 +35% / 参数处理 +20%",
                    "C. 完全开源,任何引擎都能直接编译",
                    "D. 只支持 PCVR 头显,主机端跳过"
                ],
                "correct": 1,
                "analysis": [
                    "❌ DLSS Ray Reconstruction 是降噪器(Denoiser)替代,不是上采样(SR)替代。",
                    "✅ 用 Transformer 模型替代手工降噪器,降噪能力 +35%、参数处理 +20%、性能持平;8 月全系 RTX 推送,首批 27 款游戏。",
                    "❌ DLSS 整体不开源,但 UE 插件 + TensorRT 编译好的模型可以白嫖用。",
                    "❌ DLSS 全平台覆盖,主机端通过硬件厂商适配同样支持。"
                ]
            },
            {
                "question": "FSR 4 (Redstone) 的关键技术节点是?",
                "options": [
                    "A. 仍用空间上采样,纯传统算法",
                    "B. AMD 首款纯 AI 驱动,基于 RDNA4 首发 30 款,2026 Q4 暴增到 200 款",
                    "C. 只能 RDNA4 跑,RDNA3 完全不支持",
                    "D. 需要专门硬件模块,与 DLSS 不兼容"
                ],
                "correct": 1,
                "analysis": [
                    "❌ FSR 4 是 AMD 首款纯 AI 驱动,FSR 3 才是传统空间上采样。",
                    "✅ FSR 4 (Redstone) 基于 RDNA4 首发 30 款,2026 Q4 暴增到 200 款,支持 300+ 游戏;INT8 版本下放 RDNA3 (2026.7) 和 RDNA2 (2027)。",
                    "❌ FSR 4 INT8 版本下放 RDNA3 (2026.7) 和 RDNA2 (2027),不是 RDNA4 独占。",
                    "❌ 不需要专门硬件模块,纯算法 + 通用 GPU 算力。"
                ]
            },
            {
                "question": "UE 5.7 中把'调超分模型'和'调自己的网络'统一成同一套 UStruct 接口的是?",
                "options": [
                    "A. UE 旧版 RHI 直接调用",
                    "B. NNE (Neural Network Engine)",
                    "C. Subsystem 反射",
                    "D. 仅 C++ 模板元编程"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 旧版 RHI 是渲染硬件接口,跟神经网络推理无关。",
                    "✅ UE 5.7 的 NNE (Neural Network Engine) 允许你用 UStruct 调用自己的网络——这是后续自定义超分 / 自研降噪的研究入口,不是只学 DLSS 怎么开。",
                    "❌ Subsystem 反射是 UE 的模块化机制,不专门管神经网络。",
                    "❌ UE 神经网络入口不止 C++,Blueprint 也支持 NNE 调用。"
                ]
            }
        ],
        "multi": [
            {
                "question": "DLSS / FSR / XeSS 的平台覆盖差异是?(多选)",
                "options": [
                    "A. DLSS 需 RTX 卡(NVIDIA 独占)",
                    "B. FSR 4 全平台 (RDNA2/3/4 + 竞品 GPU)",
                    "C. XeSS 全平台 + Intel Arc 加速",
                    "D. 三者都必须 D3D12 / Vulkan",
                    "E. DLSS 在 RTX 20/30 系享受不到 MFG",
                    "F. 三者都能在 UE / Unity 原生集成"
                ],
                "correct": [0, 1, 2, 4, 5],
                "analysis": [
                    "✅ DLSS 必须 NVIDIA RTX 卡(20 系起),其它卡走 FSR / XeSS。",
                    "✅ FSR 4 INT8 下放 RDNA2/3/4,理论可跑任何 GPU;但 INT8 优化针对 AMD。",
                    "✅ XeSS 是 Intel 跨平台方案,Intel Arc 加速;非 Arc 卡走 DP4a 通用路径。",
                    "❌ 不是必须 D3D12/Vulkan,DX11 也能跑部分功能(FSR 1/2 明确支持 DX11)。",
                    "✅ RTX 50 才有 6x MFG,RTX 30/20 享受不到 6x,但能享受画质提升(SR / RR)。",
                    "✅ UE 5.4+ 原生支持 DLSS/FSR 插件,Unity 同样;独立 RHI 需自接。"
                ]
            },
            {
                "question": "DLSS Ray Reconstruction 替代手工降噪器后,在游戏 / 引擎里的实际效果是?(多选)",
                "options": [
                    "A. 路径追踪下的反射 / GI 噪点显著下降",
                    "B. 替代所有 RHI Pass 中的手工降噪",
                    "C. 8 月全系 RTX 推送,首批 27 款游戏支持",
                    "D. Blender Cycles 5.3 (2026 秋) 集成",
                    "E. 仅支持 NVIDIA 显卡,AMD / Intel 完全跳过",
                    "F. 性能持平,但需要额外显存"
                ],
                "correct": [0, 2, 3, 5],
                "analysis": [
                    "✅ Transformer 模型替代手工降噪器,主要解决路径追踪下的反射 / GI 噪点问题。",
                    "❌ 不是替代所有,UE / 自研引擎仍有部分特殊路径用专用降噪。",
                    "✅ Computex 2026 公布,8 月全系 RTX 推送,首批 27 款游戏。",
                    "✅ Blender Cycles 5.3 (2026 秋季) 集成,Offline Renderer 也能享受。",
                    "❌ NVIDIA RTX 显卡专属(20 系起),这是 DLSS 系列的固有约束。",
                    "✅ 性能持平,但 Transformer 模型需要额外显存(几十 MB 级别)。"
                ]
            }
        ],
        "tf": [
            {
                "question": "DLSS 必须 NVIDIA RTX 显卡才能用,FSR 才能在所有平台跑。",
                "answer": True,
                "analysis": "✅ 正确理解:DLSS 系列(NVIDIA 出品)必须 RTX 显卡;FSR(AMD 出品)跨平台、跨厂商(Xbox / PS5 / 竞品 GPU)。\n\n❌ 常见误解:以为 XeSS 也是 NVIDIA 的——XeSS 是 Intel 的,Intel Arc 上加速,其它卡走 DP4a 通用路径。"
            },
            {
                "question": "DLSS 4.5 的降噪能力相对上一代提升 35%、参数处理 +20%、性能持平。",
                "answer": True,
                "analysis": "✅ 正确理解:Computex 2026 官方数据,Transformer 模型替代手工降噪器的核心指标就是这三条。\n\n❌ 常见误解:以为性能提升是免费的——Transformer 模型需额外显存(几十 MB),性能持平是因为其它管线做了同步优化。"
            },
            {
                "question": "FSR 4 是开源算法,任何引擎都能直接编译集成。",
                "answer": False,
                "analysis": "✅ 正确理解:FSR 4(Redstone)闭源算法,AMD 提供 SDK 和 UE 插件;引擎集成需要通过 AMD 官方 SDK 接入,不能直接编译源码。\n\n❌ 常见误解:FSR 1/2 是开源(基于开源的 CAS 锐化算法),FSR 3+ 转向闭源 AI 驱动,混为一谈就错了。\n\n**追问**:'那 FSR 的开源版本还能用吗?'\n→ FSR 2.x 的源码仍可下载集成,但效果远不如 FSR 4;生产项目建议直接上 FSR 4 SDK。"
            }
        ]
    },
    {
        "basename": "NVIDIA-ACE-AI-NPC",
        "title": "NVIDIA ACE — AI NPC 微服务(与 Unreal 直接集成)",
        "subtitle": "P0-立即学习 | 行业拐点,PUBG Ally + Total War Pharaoh 已上生产",
        "source_md": "NVIDIA-ACE-AI-NPC.md",
        "drag": [
            {
                "sentence": "ACE 把 NPC 拆成 {0} → LLM → {1} → {2} 四件套,长期记忆由 2026 新增的 {3} 层管理。",
                "answers": ["Riva ASR", "Riva TTS", "Audio2Face", "记忆"],
                "pool": ["Riva ASR", "Riva TTS", "Audio2Face", "记忆", "DLSS", "Nanite"],
                "per_slot_analysis": [
                    "Riva ASR = 自动语音识别,把玩家语音转文本。",
                    "Riva TTS(或 ElevenLabs) = 文本转语音输出给玩家。",
                    "Audio2Face = 语音驱动的面部 blendshape 预测,接 UE Skeletal Mesh。",
                    "记忆层是 2026 新增模块,PUBG Ally 用它记住玩家过往战术表现。"
                ]
            }
        ],
        "single": [
            {
                "question": "NVIDIA ACE 在 2026 H1 真正'已上生产'的两个标杆案例是?",
                "options": [
                    "A. 《赛博朋克 2077》和《艾尔登法环》",
                    "B. PUBG Ally (长期记忆) 和 Total War: Pharaoh (动态 AI 顾问)",
                    "C. 《原神》和《王者荣耀》",
                    "D. Roblox 和 Minecraft"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 这两个 demo 性质多,不是 GDC/CES 2026 主推的'已上生产'。",
                    "✅ PUBG Ally (《绝地求生》AI 队友,长期记忆) 和 Total War: Pharaoh (动态 AI 顾问) 是 NVIDIA 在 CES / Computex / GDC 2026 反复主推的'ACE 已上生产'案例。",
                    "❌ 《原神》《王者荣耀》是 miHoYo / 腾讯自研 AI,不是 ACE 主推案例。",
                    "❌ Roblox / Minecraft 不是 NVIDIA ACE 主推生产案例。"
                ]
            },
            {
                "question": "ACE 一轮对话的典型延迟预算是?",
                "options": [
                    "A. 总计 < 100ms",
                    "B. Riva ASR 200ms + LLM 800ms + TTS 300ms + A2F 50ms ≈ 1.3s",
                    "C. 总计 5-10s",
                    "D. 完全实时,无延迟"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 1.3s 是典型值,< 100ms 不可能覆盖 LLM 推理。",
                    "✅ 典型值:Riva ASR 200ms + LLM 800ms + TTS 300ms + A2F 50ms ≈ 1.3s;要在产品设计阶段算清。",
                    "❌ 5-10s 太长,玩家失去耐心。",
                    "❌ '完全实时'是 marketing 话术,LLM 推理固有延迟不可消除。"
                ]
            },
            {
                "question": "Audio2Face 输出的 blendshape 在 UE 里的集成点是?",
                "options": [
                    "A. 直接替换 USkeletalMeshComponent 的几何体",
                    "B. 通过 USkeletalMeshComponent 驱动骨骼,和 MetaHuman 兼容",
                    "C. 只能用于 Niagara 粒子",
                    "D. 仅在 Sequencer 中有效"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 不替换几何体,而是驱动骨骼动画(blendshape = bone 权重)。",
                    "✅ A2F 输出 blendshape 序列,直接接 UE 的 USkeletalMeshComponent 驱动骨骼,和 MetaHuman 兼容(同套 blendshape 协议)。",
                    "❌ 和 Niagara 无关,Niagara 是粒子系统。",
                    "❌ 不只在 Sequencer,运行时 PIE 也能用。"
                ]
            }
        ],
        "multi": [
            {
                "question": "NVIDIA ACE 的核心微服务组成是?(多选)",
                "options": [
                    "A. Riva ASR(自动语音识别)",
                    "B. LLM(Nemotron / DeepSeek / 第三方)",
                    "C. Riva TTS / ElevenLabs(文本到语音)",
                    "D. Audio2Face(语音到面部表情)",
                    "E. 记忆层(2026 新增,长期记忆图谱)",
                    "F. RTX Remix Logic 运行时替换器"
                ],
                "correct": [0, 1, 2, 3, 4],
                "analysis": [
                    "✅ Riva ASR = 自动语音识别(玩家语音→文本)。",
                    "✅ LLM 任意,Nemotron / DeepSeek / 第三方都接。",
                    "✅ Riva TTS / ElevenLabs = 文本→语音。",
                    "✅ Audio2Face = 语音→面部表情 + 口型(blendshape 输出)。",
                    "✅ 记忆层 2026 新增,PUBG Ally 用它记住玩家过往战术表现。",
                    "❌ RTX Remix Logic 是 modder 工具(动态图形特效),不是 ACE 微服务。"
                ]
            },
            {
                "question": "ACE 的关键合作伙伴(2026)有哪些?(多选)",
                "options": [
                    "A. Convai(Remen chef demo)",
                    "B. Inworld AI(长期记忆 NPC 平台)",
                    "C. Charisma.AI(故事驱动 NPC)",
                    "D. 米哈游 / 网易游戏 / 掌趣 / 腾讯",
                    "E. 育碧 / UneeQ",
                    "F. Only Epic Games"
                ],
                "correct": [0, 1, 2, 3, 4],
                "analysis": [
                    "✅ Convai 是 NVIDIA 合作伙伴,做了 ramen chef demo。",
                    "✅ Inworld AI 做长期记忆 NPC 平台。",
                    "✅ Charisma.AI 做故事驱动 NPC。",
                    "✅ 中国厂商:米哈游 / 网易游戏 / 掌趣 / 腾讯都在合作伙伴名单。",
                    "✅ 育碧 / UneeQ 也接 ACE。",
                    "❌ 不是 Only Epic,合作伙伴横跨全球主要厂商。"
                ]
            }
        ],
        "tf": [
            {
                "question": "ACE 只能在云端跑,本地 PC 完全不支持。",
                "answer": False,
                "analysis": "✅ 正确理解:ACE 支持本地 PC(RTX 50 系 + TensorRT-LLM)和云端两种模式。本地模式是'离线游戏'和'低延迟场景'(VR/竞技)的护城河。\n\n❌ 常见误解:以为云端是唯一部署形态——一旦本地推理延迟到 300ms 以内,整个 NPC 范式又会变(NVIDIA 已有 Chat with RTX 雏形)。"
            },
            {
                "question": "Audio2Face 输出的 blendshape 可以直接接 UE 的 Skeletal Mesh,和 MetaHuman 兼容。",
                "answer": True,
                "analysis": "✅ 正确理解:Audio2Face 输出 blendshape 序列,直接接 UE 的 USkeletalMeshComponent 驱动骨骼;MetaHuman 用同一套 blendshape 协议(ARKit 52 个 blendshape)。\n\n❌ 常见误解:以为 A2F 输出的是几何体顶点数据——不是,是 bone 权重。"
            },
            {
                "question": "ACE 不能接第三方 LLM,只能用 NVIDIA Nemotron。",
                "answer": False,
                "analysis": "✅ 正确理解:ACE 的 LLM 环节是开放的,Nemotron / DeepSeek / 第三方 LLM 都可以接。\n\n❌ 常见误解:以为整套都是 NVIDIA 闭源——其实 ASR/TTS/A2F 是 NVIDIA Riva 系列,LLM 是开放可替换的。\n\n**追问**:'那 LLM 推理用谁的 GPU?'\n→ 本地模式:RTX 50 系 + TensorRT-LLM 跑 NVIDIA 优化版;云端模式:任意云厂商 GPU 都能跑。第三方 LLM 通过 OpenAI 兼容 API 接入。"
            }
        ]
    },
    {
        "basename": "AI-Code-Assistant-Cursor-ClaudeCode",
        "title": "AI 编程助手 — Cursor / Claude Code / Copilot",
        "subtitle": "P0-立即学习 | 直接吃产能,GDC 2026 行业基线",
        "source_md": "AI-Code-Assistant-Cursor-ClaudeCode.md",
        "drag": [
            {
                "sentence": "在 UE C++ 工程里,跨文件编辑用 {0},批量改文件 + 跑命令用 {1},纯行内补全用 {2}。",
                "answers": ["Cursor", "Claude Code", "GitHub Copilot"],
                "pool": ["Cursor", "Claude Code", "GitHub Copilot", "TRAE", "Windsurf"],
                "per_slot_analysis": [
                    "Cursor 是 VSCode fork,Composer 模式适合跨文件编辑、多文件重构。",
                    "Claude Code 是终端 Agent,适合读大工程、批量改文件、跑命令。",
                    "GitHub Copilot 是 IDE 插件,行内补全速度最快。"
                ]
            },
            {
                "sentence": "UE C++ 的 {0} / {1} / {2} 宏,加头文件互相引用,Cursor 表现最好;跨模块批量改签名,Claude Code 表现最好。",
                "answers": ["UCLASS", "UPROPERTY", "UFUNCTION"],
                "pool": ["UCLASS", "UPROPERTY", "UFUNCTION", "GENERATED_BODY", "IMPLEMENT_PRIMARY_GAME_MODULE"],
                "per_slot_analysis": [
                    "UCLASS 是 UE 类反射宏,定义 UObject 类时用。",
                    "UPROPERTY 是属性反射宏,让变量在 Blueprint / Editor 中可见。",
                    "UFUNCTION 是函数反射宏,让 C++ 函数在 Blueprint 中调用。"
                ]
            }
        ],
        "single": [
            {
                "question": "Microsoft Build 2026 (6 月 2 日) 推出的关键编程模型是?",
                "options": [
                    "A. GPT-5 编程专用版",
                    "B. MAI-Code-1-Flash(基于 GitHub Copilot 生产环境训练)",
                    "C. 只推 GitHub Copilot Workspace",
                    "D. 完全放弃编程模型,转投 Claude"
                ],
                "correct": 1,
                "analysis": [
                    "❌ GPT-5 不是 Microsoft 出品(OpenAI 出品)。",
                    "✅ MAI-Code-1-Flash 编程模型已在 GitHub Copilot 全计划用户推,基于 GitHub Copilot 生产环境训练——未来 6 个月 Copilot 会显著变强。",
                    "❌ Copilot Workspace 2024 推过,2026 H1 不是 Microsoft 重点。",
                    "❌ Microsoft 从'消费前沿模型'转向'全方位参与到前沿生态',没有放弃编程模型。"
                ]
            },
            {
                "question": "给 AI 写工程规约的标准做法是?",
                "options": [
                    "A. 在每次对话开始时口头告诉 AI",
                    "B. 在工程根目录放 .cursorrules / CLAUDE.md 等文件",
                    "C. 让 AI 自己猜 UE 规范",
                    "D. 不需要规约,AI 都知道"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 口头告诉效率低,跨会话失效。",
                    "✅ 推荐在工程根目录放 .cursorrules(Cursor) / CLAUDE.md(Claude Code) / copilot-instructions.md(Copilot),AI 改代码时会自动遵守。",
                    "❌ AI 不知道你的项目特殊规范,会写出和工程风格不一致的代码。",
                    "❌ 必须写规约,UE 的 TObjectPtr<> / TArray<> / 头文件顺序等都不是 AI 默认知道的。"
                ]
            },
            {
                "question": "AI 给的 UE C++ 代码真实质量评价是?",
                "options": [
                    "A. 100% 编译能过,直接用",
                    "B. 大约 80% 编译能过,真正的功夫是 5 秒内扫出错的 20%",
                    "C. 50% 编译能过,要大量修改",
                    "D. 10% 编译能过,基本不可用"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 不可能 100%,AI 会编造不存在的 UE API、错用宏参数。",
                    "✅ AI 给的代码 80% 编译能过,真正的功夫是 5 秒内扫出错的 20%——这是 senior 和 junior 拉开差距的地方。",
                    "❌ 50% 太悲观,好的 AI 工具 + 好的 prompt 远超 50%。",
                    "❌ 10% 是糟糕 prompt + 不会用的结果,不是 AI 的实际能力。"
                ]
            }
        ],
        "multi": [
            {
                "question": "AI 写 UE C++ 代码的真实风险是?(多选)",
                "options": [
                    "A. 编造不存在的 UE API / 类名",
                    "B. 误用宏参数(如 UFUNCTION 拼写错误)",
                    "C. 内存管理用裸指针而非 TObjectPtr<>",
                    "D. 头文件顺序打乱,导致循环引用",
                    "E. 永远无法运行 LLM 推理",
                    "F. AI 总是输出 100% 正确代码"
                ],
                "correct": [0, 1, 2, 3],
                "analysis": [
                    "✅ LLM 会编造不存在的 UE API,必须对照引擎源码验证。",
                    "✅ UFUNCTION(UFunctionGenerator) 等宏参数容易拼写错误,AI 经常写错。",
                    "✅ AI 经常用裸指针而不是 TObjectPtr<>(UE 5.0+ 推荐),导致 GC 不回收。",
                    "✅ AI 改头文件顺序容易打乱,导致循环引用 / 编译失败。",
                    "❌ AI 完全能运行 LLM 推理,这是 NNE Plugin 的核心场景。",
                    "❌ AI 不会 100% 输出正确,需要人工 review。"
                ]
            },
            {
                "question": "'AI 友好'的 UE C++ 工程结构特点是?(多选)",
                "options": [
                    "A. 文件小、每个类一个头文件 + 一个 .cpp",
                    "B. 依赖清晰、接口明确、避免循环依赖",
                    "C. .cursorrules / CLAUDE.md 写明规范",
                    "D. 一个文件塞 5000 行,所有类一起",
                    "E. 模块拆分清晰(Module A 依赖 Module B,C 不依赖 A)",
                    "F. 注释完整,AI 能理解类用途"
                ],
                "correct": [0, 1, 2, 4, 5],
                "analysis": [
                    "✅ 文件小 = AI 一次能看全,改起来准确。",
                    "✅ 依赖清晰 = AI 改签名时不会漏改 override。",
                    "✅ .cursorrules / CLAUDE.md 是必备,AI 会自动遵守。",
                    "❌ 一个文件塞 5000 行 = AI 上下文溢出,改不动。",
                    "✅ 模块拆分清晰 = AI 能用 @module 限定 scope,准确改局部。",
                    "✅ 注释完整 = AI 理解类用途,生成的代码更贴需求。"
                ]
            }
        ],
        "tf": [
            {
                "question": "Cursor 是 VSCode 的 fork,UI 和扩展生态完全兼容。",
                "answer": True,
                "analysis": "✅ 正确理解:Cursor 基于 VSCode fork,UI 一致,VSCode 扩展可以直接装。\n\n❌ 常见误解:以为 Cursor 是独立 IDE——它就是 VSCode 的 AI 增强版,VSCode 用户的迁移成本极低。"
            },
            {
                "question": "Claude Code 是 IDE 形态,需要切换窗口使用。",
                "answer": False,
                "analysis": "✅ 正确理解:Claude Code 是终端 Agent,通过 `claude` 命令启动,不需要 IDE 切换,直接在 terminal 里对话。\n\n❌ 常见误解:把它和 Cursor / Copilot 混为一谈——Claude Code 是 Agent,Cursor / Copilot 是 IDE 插件。\n\n**追问**:'那 Claude Code 能写代码吗?'\n→ 当然能,只是它在 terminal 里用 Read/Grep/Edit/Bash 工具操作文件系统;UE 工程可以用它读源码 + 批量改文件 + 跑命令。"
            },
            {
                "question": "AI 给的 UE C++ 代码大约 80% 编译能过,真正的功夫是 5 秒内扫出错的 20%。",
                "answer": True,
                "analysis": "✅ 正确理解:这是 senior 和 junior 拉开差距的关键——AI 给的代码不会完美,但会很快;真正的杠杆是 review 速度,不是打字速度。\n\n❌ 常见误解:以为用 AI 写代码就是'少打字'——其实核心价值是'快速看到正确方向的 80%',自己补完关键的 20%。"
            }
        ]
    },
    {
        "basename": "3DGS-Gaussian-Splatting",
        "title": "3D Gaussian Splatting (3DGS) — 神经渲染新范式",
        "subtitle": "P0-立即学习 | Luma UE 插件可跑实时,神经渲染已进生产",
        "source_md": "3DGS-Gaussian-Splatting.md",
        "drag": [
            {
                "sentence": "3DGS 用带颜色和透明度的 {0} 表示场景,光栅化在 {1} 上跑,核心论文发表在 {2} 上。",
                "answers": ["3D 高斯椭球", "GPU", "SIGGRAPH 2023"],
                "pool": ["3D 高斯椭球", "三角形", "体素", "GPU", "CPU", "SIGGRAPH 2023", "CVPR 2024"],
                "per_slot_analysis": [
                    "3DGS 用 3D 高斯椭球(不是三角形、不是体素)做场景表示。",
                    "光栅化在 GPU 上跑,这是实时性(1080p 30fps)的来源。",
                    "原始论文 SIGGRAPH 2023(Kerbl, INRIA),引用 10000+。"
                ]
            }
        ],
        "single": [
            {
                "question": "ZipSplat (ETH Zürich + Microsoft, arxiv 2026.6.3) 的核心创新是?",
                "options": [
                    "A. 把 3DGS 全部转 mesh",
                    "B. K-means 场景令牌聚类打破像素-Gaussian 绑定,神经场景重建压缩 33x",
                    "C. 完全用 CPU 跑 3DGS",
                    "D. 只支持静态场景"
                ],
                "correct": 1,
                "analysis": [
                    "❌ ZipSplat 仍是 3DGS,不是 mesh。",
                    "✅ ZipSplat 用 K-means 场景令牌聚类打破像素-Gaussian 绑定,神经场景重建压缩 33x——同样 PSNR 下 Gaussian 数量从 1.2M 降到 36K,24 视角下完整前向推理 0.8s,峰值显存 < 8.1GB,生成 36K 高斯的场景只占 3.3MB、685 FPS 渲染。",
                    "❌ GPU 加速,不是 CPU。",
                    "❌ 静态 + 动态场景都支持。"
                ]
            },
            {
                "question": "World Labs Marble (2025.11 发布) 的核心表示是?",
                "options": [
                    "A. 传统 mesh + 贴图",
                    "B. 3D Gaussian Splatting(原生导出 + 转 mesh 都支持)",
                    "C. 仅 NeRF 体渲染",
                    "D. 仅 point cloud"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 不是传统 mesh + 贴图。",
                    "✅ World Labs Marble 是首个真正意义上的多模态生成式世界模型,核心表示就是 3DGS;文字/单图/视频/粗 3D 布局都能'抬升'成高保真、可编辑、可无限扩展的交互式 3D 环境;原生的 Gaussian Splat 可导出到 Spark 查看器 / WebXR,也能转三角网格到 Unity / Blender。",
                    "❌ 不只 NeRF,核心是 3DGS。",
                    "❌ 不只 point cloud,3DGS 是带方向的高斯椭球,不是简单点。"
                ]
            },
            {
                "question": "3DGS 和 Nanite 在游戏里的正确关系是?",
                "options": [
                    "A. 3DGS 完全替代 Nanite",
                    "B. Nanite 完全替代 3DGS",
                    "C. 互补:主角 + 关键道具用 Nanite,远景 + 扫描资产用 3DGS",
                    "D. 完全没关系"
                ],
                "correct": 2,
                "analysis": [
                    "❌ 3DGS 不能完全替代 Nanite——动画、互动、物理都不成熟。",
                    "❌ Nanite 不能完全替代 3DGS——Nanite 是从 mesh 出发,3DGS 是神经表示。",
                    "✅ 互补:主角 + 关键道具用 Nanite(精度可控、动画兼容好);远景 + 程序化场景 + 扫描资产用 3DGS(开发快、视觉真)。",
                    "❌ 两者都是渲染管线的不同维度,完全无关是误解。"
                ]
            }
        ],
        "multi": [
            {
                "question": "3DGS 当前在游戏里的局限性是?(多选)",
                "options": [
                    "A. 动态场景 / 物理仿真不成熟",
                    "B. 流式加载 + LOD 不成熟",
                    "C. 一个场景动辄几 GB,体积爆炸",
                    "D. 网格结构无法 retopo",
                    "E. 动画兼容差,需要专门管线",
                    "F. 完全无法编辑"
                ],
                "correct": [0, 1, 2, 4],
                "analysis": [
                    "✅ 动态场景 / 物理仿真不成熟(ArtisanGS 等刚起步,布料/碰撞还在论文阶段)。",
                    "✅ 流式加载 + LOD 不成熟,游戏需要这些,3DGS 还在研究。",
                    "✅ 一个场景动辄几 GB,ZipSplat 33x 压缩后才 3.3MB,体积爆炸是最大障碍。",
                    "❌ 不是没有网格——3DGS 转 mesh 路径存在,只是质量不如原生 mesh。",
                    "✅ 动画兼容差,3DGS 的高斯是静态参数,动画需要专门管线。",
                    "❌ 完全可以编辑(World Labs Marble 主推'可编辑'卖点)。"
                ]
            },
            {
                "question": "3DGS 在 Unreal Engine 5.7+ 的集成路径包括?(多选)",
                "options": [
                    "A. Luma UE5 Windows 插件",
                    "B. UE NNE 加载 .plan / .onnx 格式 3DGS 推理模型",
                    "C. [[Hunyuan3D-Tencent-Topology]] Image-to-3D 带拓扑结构",
                    "D. World Labs Marble 导出 Gaussian Splat 到 Spark 查看器",
                    "E. 仅 Linux 平台",
                    "F. 必须替换整个 UE Renderer"
                ],
                "correct": [0, 1, 2, 3],
                "analysis": [
                    "✅ Luma UE5 Windows 插件已可跑实时。",
                    "✅ UE NNE 在 5.7+ 能加载 .plan / .onnx 格式的模型,可以挂自定义 3DGS 推理。",
                    "✅ Hunyuan3D-Tencent 的 Image-to-3D 自带'专业布线结构',直接进 UE 资产管线(已独立 P0 条目)。",
                    "✅ World Labs Marble 原生 Gaussian Splat 可导出到 Spark 查看器 / WebXR。",
                    "❌ 不只 Linux,Luma 插件是 Windows。",
                    "❌ 不替换 Renderer,而是作为新的资产 / 渲染格式接入。"
                ]
            }
        ],
        "tf": [
            {
                "question": "3DGS 可以完全替代游戏里的所有 mesh。",
                "answer": False,
                "analysis": "✅ 正确理解:3DGS 的动态场景 / 物理 / 流式加载都不成熟,别想用 3DGS 替代所有 mesh——Nanite 和 3DGS 是分工关系,不是替代。\n\n❌ 常见误解:以为神经表示一定胜过 mesh——mesh 在动画、互动、物理上仍是主力,3DGS 适合远景 + 扫描资产。"
            },
            {
                "question": "3DGS 一个场景动辄几 GB,体积爆炸是游戏落地的最大障碍。",
                "answer": True,
                "analysis": "✅ 正确理解:未优化的 3DGS 场景确实是几 GB,ZipSplat (arxiv 2026.6.3) 用 K-means 场景令牌聚类打破像素-Gaussian 绑定,把 1.2M Gaussian 压到 36K,场景只占 3.3MB、685 FPS。\n\n❌ 常见误解:以为 3DGS 已经为游戏优化好了——ZipSplat 等压缩方案刚出现,2026 H1 是落地爆发期,不是已经成熟。"
            },
            {
                "question": "3DGS 已经在生产可用,Luma UE5 插件能跑实时。",
                "answer": True,
                "analysis": "✅ 正确理解:Luma AI 已有 UE5 Windows 插件能跑实时,1 分钟建模、$1 成本(对比传统 2 周 $1000);World Labs Marble 也是 3DGS 为核心表示。\n\n❌ 常见误解:以为 3DGS 还停在论文阶段——2026 H1 已经在生产可用,学术界 + 工业界同步推进。"
            }
        ]
    },
    {
        "basename": "UnrealMCP-N1UnrealMCP",
        "title": "UnrealMCP (N1) — 让 AI Agent 直接操控 UE Editor",
        "subtitle": "P0-立即学习 | day-job 直接闭环加速,MCP 协议 2026 H1 爆发",
        "source_md": "UnrealMCP-N1UnrealMCP.md",
        "drag": [
            {
                "sentence": "UnrealMCP 架构:MCP({0}) → Python Bridge(TCP:55558) → UE Plugin → EditorSubsystem({1})。",
                "answers": ["stdio", "MCP Server"],
                "pool": ["stdio", "TCP", "HTTP", "MCP Server", "EditorSubsystem", "WorldSubsystem"],
                "per_slot_analysis": [
                    "MCP(stdio) = AI Agent 端的 MCP 协议,Claude Code / Cursor 都通过 stdio 通信。",
                    "EditorSubsystem 是 MCP Server,扩展 Editor 能力的标准入口。"
                ]
            }
        ],
        "single": [
            {
                "question": "UnrealMCP 提供 100+ 命令,分多少类?",
                "options": [
                    "A. 5 类",
                    "B. 11 类",
                    "C. 20 类",
                    "D. 50 类"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 5 类太少。",
                    "✅ UnrealMCP 提供 100+ 命令,分 11 类:Editor(19)、Blueprint(12)、Blueprint Node(15)、Material(11)、UMG(7)、Project(5)、Asset(8)、Landscape(8)、PIE(5)、Data(10)、Meta(4)。",
                    "❌ 20 类偏多。",
                    "❌ 50 类明显过多。"
                ]
            },
            {
                "question": "UnrealMCP 在哪个 UE 版本上已稳定?",
                "options": [
                    "A. UE 4.27",
                    "B. UE 5.0",
                    "C. UE 5.4",
                    "D. UE 5.7"
                ],
                "correct": 3,
                "analysis": [
                    "❌ UE 4.27 太老,MCP 协议 2024 才发布。",
                    "❌ UE 5.0 不支持,缺少必要的 EditorSubsystem 扩展。",
                    "❌ UE 5.4 部分支持,但不完整。",
                    "✅ UE 5.7 已稳定,GitHub 12 commits + 持续活跃,Demo 项目齐全。"
                ]
            },
            {
                "question": "UnrealMCP 的所有 mutation 命令包在什么事务里,实现自动 Undo/Redo?",
                "options": [
                    "A. FTransaction 安全网",
                    "B. FScopedTransaction",
                    "C. 手动 git checkout",
                    "D. 无事务,直接改"
                ],
                "correct": 1,
                "analysis": [
                    "❌ FTransaction 不是 UE 的标准事务类。",
                    "✅ UnrealMCP 把所有 mutation 命令包在 FScopedTransaction 里——自动 Undo/Redo。这是 UE Editor 编程的标准模式。",
                    "❌ git checkout 跟 Undo/Redo 无关,git 是版本控制。",
                    "❌ 没有事务就直接改是 dangerous,容易出错。"
                ]
            }
        ],
        "multi": [
            {
                "question": "UnrealMCP 的 11 类命令包括?(多选)",
                "options": [
                    "A. Editor(19 个:spawn/delete/transform actor 等)",
                    "B. Blueprint(12 个:创建 BP、加 component、编译)",
                    "C. Material(11 个:创建材质、加 expression)",
                    "D. Niagara(8 个:粒子系统控制)",
                    "E. PIE(5 个:Play/Stop、控制台命令)",
                    "F. Meta(4 个:ping、list_commands 等)"
                ],
                "correct": [0, 1, 2, 4, 5],
                "analysis": [
                    "✅ Editor(19 个):spawn/delete/transform actor、开 level、截图、视口操作。",
                    "✅ Blueprint(12 个):创建 BP、加 component/variable、编译。",
                    "✅ Material(11 个):创建材质、加 expression、连节点。",
                    "❌ 不包含 Niagara(粒子系统控制)。",
                    "✅ PIE(5 个):Play/Stop、控制台命令(带黑名单)。",
                    "✅ Meta(4 个):ping、list_commands、describe_command、list_categories。"
                ]
            },
            {
                "question": "UnrealMCP + Claude Code 配合实现的 AI 工作流包括?(多选)",
                "options": [
                    "A. AI 读 Lyra GameMode,然后自动加自定义 GameState",
                    "B. AI 创建 GameFeature 子类 + 加 1 个 Ability + 跑 PIE 截图",
                    "C. AI 改 C++ 后自动调 UnrealMCP 编译 + 检查 BP 编译错误",
                    "D. 完全手动,AI 不能触发任何 UE 操作",
                    "E. MetaHuman / Audio2Face 集成测试自动化",
                    "F. 跨模块批量重构 + 自动验证"
                ],
                "correct": [0, 1, 2, 4, 5],
                "analysis": [
                    "✅ '在 LyraGameMode 里加一个自定义 GameState 初始化步骤'——AI 直接 spawn actor / 改蓝图 / 编译 / 跑 PIE。",
                    "✅ UnrealMCP 让 AI 自己读 Lyra 的 GameFeature → 创建自定义 GameFeature 子类 → 加 1 个 Ability → 跑 PIE 截图,全程 5 分钟。",
                    "✅ 跨模块批量重构(引擎模块间同步签名):AI 改完 C++,自动调 UnrealMCP 编译 + 检查 BP 编译错误 + 截图验证。",
                    "❌ 不是完全手动,UnrealMCP 核心价值就是让 AI 触发 UE 操作。",
                    "✅ MetaHuman / Audio2Face / 3DGS 这些 P0 条目的'实测验证'都能靠 UnrealMCP 自动化。",
                    "✅ 跨模块批量重构是 UnrealMCP + Claude Code 的招牌场景。"
                ]
            }
        ],
        "tf": [
            {
                "question": "UnrealMCP 直接修改 UE 引擎源码。",
                "answer": False,
                "analysis": "✅ 正确理解:UnrealMCP 是项目级插件(Plugins/N1UnrealMCP),通过 EditorSubsystem 扩展 UE 能力,不需要修改引擎源码。\n\n❌ 常见误解:以为 MCP 工具要改引擎——其实通过 Subsystem 反射即可,Epic 官方也推荐这种方式扩展 Editor。"
            },
            {
                "question": "UnrealMCP 通过 stdio 和 AI Agent 通信,Claude Code / Cursor 都直接对接。",
                "answer": True,
                "analysis": "✅ 正确理解:MCP(stdio)是 LLM tool call 的标准通信模型,Claude Code / Cursor 都直接走 stdio,不用自定义协议。\n\n❌ 常见误解:以为要写 HTTP/RPC——MCP 协议本身就是为了统一 LLM tool call 设计的,stdio + JSON-RPC 是默认。"
            },
            {
                "question": "UnrealMCP 的所有 mutation 命令支持自动 Undo/Redo。",
                "answer": True,
                "analysis": "✅ 正确理解:所有 mutation 命令包在 FScopedTransaction 里,这是 UE Editor 编程的标准模式,自动 Undo/Redo。\n\n❌ 常见误解:以为需要手动实现 Undo——FScopedTransaction 是 UE 内置事务类,AI 改错的成本几乎为零。\n\n**追问**:'那 Perforce 自动 checkout 呢?'\n→ UnrealMCP 同时做了 Perforce 自动 checkout + MarkPackageDirty + 可选 save,资产版本管理自动化。"
            }
        ]
    },
    {
        "basename": "UE-NNE-TensorRT-Plugin",
        "title": "UE NNE + TensorRT for RTX Plugin — 引擎里挂自定义神经网络的官方入口",
        "subtitle": "P0-立即学习 | 自定义 AI 在引擎里的官方入口,不是只学 DLSS 怎么开",
        "source_md": "UE-NNE-TensorRT-Plugin.md",
        "drag": [
            {
                "sentence": "NNE 把'加载模型 → 准备输入 → 推理 → 处理输出'封装成统一 API,后端支持 {0} / {1} / {2}。",
                "answers": ["CUDA / TensorRT", "DirectML", "CPU"],
                "pool": ["CUDA / TensorRT", "DirectML", "CPU", "Vulkan", "OpenGL"],
                "per_slot_analysis": [
                    "CUDA / TensorRT(NVIDIA RTX) = 性能最优,NVIDIA 显卡走这条路。",
                    "DirectML(Windows DX12 GPU) = 跨厂商,Xbox / AMD / Intel 都能跑。",
                    "CPU = 无 GPU 时的兜底,性能差但保证功能可用。"
                ]
            },
            {
                "sentence": "TensorRT for RTX Plugin 是 NVIDIA 在 2026 H1 推出的官方 runtime,比通用 CUDA 后端快 {0} x,显存省 {1} %。",
                "answers": ["2", "30"],
                "pool": ["2", "5", "10", "30", "50"],
                "per_slot_analysis": [
                    "TensorRT for RTX 比通用 CUDA 后端快 2x。",
                    "显存省 30%。"
                ]
            }
        ],
        "single": [
            {
                "question": "UE NNE 支持的主要模型格式是?",
                "options": [
                    "A. 仅 TensorRT .plan",
                    "B. ONNX(主)、TensorRT .plan / .engine",
                    "C. 仅 PyTorch .pth",
                    "D. 仅 TensorFlow .pb"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 不只 TensorRT。",
                    "✅ ONNX 是主要模型格式(PyTorch / TensorFlow / JAX 都支持),TensorRT 是 ONNX 转 .plan / .engine 后的优化格式。",
                    "❌ 不直接支持 PyTorch .pth,需要先转 ONNX。",
                    "❌ 不直接支持 TensorFlow .pb,需要先转 ONNX。"
                ]
            },
            {
                "question": "UE NNE 在哪个 UE 版本上稳定可用?",
                "options": [
                    "A. UE 5.0",
                    "B. UE 5.2",
                    "C. UE 5.4+",
                    "D. UE 5.7 独占"
                ],
                "correct": 2,
                "analysis": [
                    "❌ UE 5.0 NNE 还在实验阶段。",
                    "❌ UE 5.2 部分 API,但不稳定。",
                    "✅ UE 5.4+ 稳定,UE 5.7 完整支持。",
                    "❌ 不是 5.7 独占,5.4+ 都稳定。"
                ]
            },
            {
                "question": "NNE 推理结果集成到 RHI 后处理管线的关键是?",
                "options": [
                    "A. 完全替换 RHI",
                    "B. 神经推理结果作为 render pass 输入,理解 UE 5 的渲染线程模型",
                    "C. 必须用 Compute Shader 重写所有 RHI",
                    "D. RHI 后处理不支持 NNE"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 不替换 RHI,NNE 是叠加层。",
                    "✅ 神经推理结果作为 render pass 输入,需要懂 UE 5 的渲染线程模型(RenderGraph / RDG)。",
                    "❌ 不重写 RHI,NNE 通过 FRDGBuilder 接入。",
                    "❌ RHI 后处理完全支持 NNE,这是 NNE 设计目标之一。"
                ]
            }
        ],
        "multi": [
            {
                "question": "NNE 在 UE 项目中的典型应用是?(多选)",
                "options": [
                    "A. 自定义超分(配合 Lumen 路径追踪的特殊降噪)",
                    "B. 自定义角色行为网络(小型 in-game decision network)",
                    "C. 神经压缩资产(纹理、动画、音频的神经压缩)",
                    "D. Audio classification / 玩家行为预测",
                    "E. 渲染器线程管理",
                    "F. 替代 UE RHI 全部功能"
                ],
                "correct": [0, 1, 2, 3],
                "analysis": [
                    "✅ 自定义超分(配合 Lumen 路径追踪的特殊降噪),DLSS Ray Reconstruction 是通用降噪,你的项目可以训专用。",
                    "✅ 自定义角色行为网络(不是 LLM,是小型 MLP / Transformer,做 NPC micro-decision),NNE 推理延迟 < 1ms。",
                    "✅ 神经压缩资产(纹理、动画、音频的神经压缩),运行时 NNE 解码。",
                    "✅ Audio classification / 玩家行为预测(in-game AI)。",
                    "❌ 渲染器线程管理是 RHI 的事,NNE 不管。",
                    "❌ 不替代 RHI,NNE 是叠加在 RHI 之上的推理层。"
                ]
            },
            {
                "question": "NNE 集成所需的关键技能是?(多选)",
                "options": [
                    "A. ONNX 格式(跨框架模型交换标准)",
                    "B. TensorRT 优化(FP16 / INT8 / NVFP4 量化、kernel fusion、动态 shape)",
                    "C. UE UStruct ↔ Tensor buffer 的内存布局对齐",
                    "D. RHI / RenderGraph 集成(神经推理结果作为 render pass 输入)",
                    "E. 多后端 fallback 策略(RTX → DirectML → CPU)",
                    "F. 必须手写 CUDA kernel 才能用 NNE"
                ],
                "correct": [0, 1, 2, 3, 4],
                "analysis": [
                    "✅ ONNX 格式 = 跨框架模型交换标准,PyTorch / TensorFlow / JAX 都支持。",
                    "✅ TensorRT 优化 = FP16 / INT8 / NVFP4 量化、kernel fusion、动态 shape。",
                    "✅ UE UStruct ↔ Tensor buffer 的内存布局对齐,这是最大的坑。",
                    "✅ RHI / RenderGraph 集成,神经推理结果作为 render pass 输入,需要懂 UE 5 渲染线程模型。",
                    "✅ 多后端 fallback,RTX 用户用 TensorRT,其他用户用 DirectML,代码里要写。",
                    "❌ 不必须手写 CUDA kernel,NNE 已经封装了。"
                ]
            }
        ],
        "tf": [
            {
                "question": "NNE 只能用 NVIDIA GPU,AMD / Intel 完全跳过。",
                "answer": False,
                "analysis": "✅ 正确理解:NNE 跨厂商,后端包括 CUDA / TensorRT(NVIDIA RTX)、DirectML(Windows DX12 GPU,跨厂商)、CPU 兜底。\n\n❌ 常见误解:以为 NNE 是 NVIDIA 专属——其实 NNE 是抽象层,NVIDIA 只是性能最优的后端之一。"
            },
            {
                "question": "ONNX 是 UE NNE 的主要模型格式。",
                "answer": True,
                "analysis": "✅ 正确理解:ONNX 是 NNE 的主要模型格式(PyTorch / TensorFlow / JAX 都支持),TensorRT 是 ONNX 转 .plan / .engine 后的优化格式。\n\n❌ 常见误解:以为必须 TensorRT——NNE 直接吃 ONNX,转 TensorRT 是优化选项,不是必须。"
            },
            {
                "question": "NNE 推理结果可以直接接入 RHI 后处理管线。",
                "answer": True,
                "analysis": "✅ 正确理解:NNE 设计目标之一就是接入 RHI 后处理,神经推理结果作为 render pass 输入,通过 FRDGBuilder 接入。\n\n❌ 常见误解:以为推理和渲染是分离的两套——其实 UE 5.4+ 的 RenderGraph 已经为 NNE 预留了接入点,这是未来 1-2 年'在 PostProcess 里挂一个神经 Pass'会变成 UE 项目标配操作的原因。"
            }
        ]
    },
    {
        "basename": "Hunyuan3D-Tencent-Topology",
        "title": "Hunyuan3D (腾讯混元 3D) — 带拓扑结构的 Image-to-3D",
        "subtitle": "P0-立即学习 | day-job AI 资产生成主力,开源可商用",
        "source_md": "Hunyuan3D-Tencent-Topology.md",
        "drag": [
            {
                "sentence": "Hunyuan3D 核心突破是 {0},开源协议 {1} 可商用,出来的 mesh 直接挂 UE 的 {2}。",
                "answers": ["专业拓扑布线结构", "MIT/Apache", "Skeletal Mesh"],
                "pool": ["专业拓扑布线结构", "Meshy 闭源", "Luma 闭源", "MIT/Apache", "CC-BY-NC", "Skeletal Mesh", "Static Mesh", "Niagara"],
                "per_slot_analysis": [
                    "专业拓扑布线结构 = Hunyuan3D 的核心突破,出来的 mesh 直接能挂动画,不用再 retopo。",
                    "MIT / Apache 等宽松开源协议,商业项目免授权费(具体协议细节首次商用前查清)。",
                    "Skeletal Mesh = UE 的骨骼网格,挂 Animation Blueprint 跑动画。"
                ]
            }
        ],
        "single": [
            {
                "question": "Hunyuan3D 的归属公司是?",
                "options": [
                    "A. 字节跳动",
                    "B. 阿里通义",
                    "C. 腾讯混元",
                    "D. 百度文心"
                ],
                "correct": 2,
                "analysis": [
                    "❌ 字节跳动没出 Hunyuan3D。",
                    "❌ 阿里通义没出 Hunyuan3D。",
                    "✅ Hunyuan3D 归属腾讯混元系列(Tencent Hunyuan3D),2026 H1 频繁更新。",
                    "❌ 百度文心没出 Hunyuan3D。"
                ]
            },
            {
                "question": "Hunyuan3D 的典型出图时间是?",
                "options": [
                    "A. 1 毫秒",
                    "B. 30 秒 - 2 分钟",
                    "C. 30 分钟",
                    "D. 2 小时"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 1ms 不可能,Image-to-3D 至少几秒。",
                    "✅ 30 秒 - 2 分钟出一张图的拓扑 mesh(取决于复杂度和队列)。",
                    "❌ 30 分钟太慢,不是主流时间。",
                    "❌ 2 小时不是 Image-to-3D 范畴,那是离线渲染。"
                ]
            },
            {
                "question": "Hunyuan3D 输出的格式是?",
                "options": [
                    "A. 仅 .obj",
                    "B. FBX / OBJ / GLB / USDZ,主流引擎直接接",
                    "C. 仅 .fbx",
                    "D. 仅 .usd"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 不只 .obj。",
                    "✅ 多格式输出:FBX / OBJ / GLB / USDZ,主流引擎(UE / Unity / Blender / Maya)直接接。",
                    "❌ 不只 .fbx。",
                    "❌ 不只 .usd。"
                ]
            }
        ],
        "multi": [
            {
                "question": "Hunyuan3D 从 [[Meshy-LumaGenie-Text-to-3D]] 拆出来独立的三个核心价值是?(多选)",
                "options": [
                    "A. 拓扑质量:优(带拓扑)",
                    "B. Meshy/Luma:中(可后处理)",
                    "C. 开源可商用",
                    "D. Meshy/Luma 闭源按量计费",
                    "E. 直接挂骨骼动画",
                    "F. 其他家要 retopo 后再绑骨"
                ],
                "correct": [0, 2, 4],
                "analysis": [
                    "✅ Hunyuan3D 拓扑质量优,带拓扑;Meshy/Luma 拓扑质量中,需要后处理。",
                    "❌ 这不是 Hunyuan3D 的优势,这是 Meshy/Luma 的劣势——题目问的是 Hunyuan3D 的核心价值。",
                    "✅ 开源可商用是 Hunyuan3D 的核心价值之一,商业项目免授权费。",
                    "❌ 这是 Meshy/Luma 的劣势,不是 Hunyuan3D 的优势。",
                    "✅ 直接挂骨骼动画是 Hunyuan3D 的核心价值——出来的 mesh 直接能挂 UE Skeletal Mesh + Animation Blueprint。",
                    "❌ 这是其他家的劣势,不是 Hunyuan3D 的优势。"
                ]
            },
            {
                "question": "Hunyuan3D 配合 [[UnrealMCP-N1UnrealMCP]] 的闭环工作流是?(多选)",
                "options": [
                    "A. Hunyuan3D API 生成带拓扑 mesh",
                    "B. UnrealMCP 自动导入 UE 资产管线",
                    "C. UE 自动验证拓扑质量 + 挂骨骼动画",
                    "D. 完全手动,AI 不能介入",
                    "E. PCG 框架批量生成场景元素",
                    "F. 一周内完成从 API 注册到 demo 角色挂骨骼"
                ],
                "correct": [0, 1, 2, 4, 5],
                "analysis": [
                    "✅ Hunyuan3D API 出带拓扑 mesh 是起点。",
                    "✅ UnrealMCP 自动导入 UE 资产管线。",
                    "✅ UE 验证拓扑质量 + 挂骨骼动画 + 跑 PIE。",
                    "❌ 不是完全手动,UnrealMCP 核心价值就是让 AI 触发 UE 操作。",
                    "✅ 程序化关卡 + PCG 框架批量生成场景元素(美术给 prompt,引擎批量出场景元素)。",
                    "✅ 推荐路线:注册 → 5 张图 → UE 看拓扑 → 接 API → 挂骨骼 demo。一周内做完。"
                ]
            }
        ],
        "tf": [
            {
                "question": "Hunyuan3D 是闭源算法,商业项目需要付费授权。",
                "answer": False,
                "analysis": "✅ 正确理解:Hunyuan3D 是腾讯开源协议,商业项目免授权费(具体协议范围首次商用前查清,如是否需要 attribution)。\n\n❌ 常见误解:以为大厂出品一定闭源——腾讯混元系列开源 + 商业可商用是 2026 H1 的明确信号,这是中国 AI 资产生成的主推路线。"
            },
            {
                "question": "Hunyuan3D 出来的 mesh 需要 retopo 后才能挂骨骼动画。",
                "answer": False,
                "analysis": "✅ 正确理解:Hunyuan3D 的'专业拓扑布线结构'让出来的 mesh 直接挂 UE 的 Skeletal Mesh + Animation Blueprint,跳过 retopo + 绑骨步骤——这是它从对比表里拆出来独立的核心价值。\n\n❌ 常见误解:以为所有 AI 生成的 mesh 都要 retopo——Hunyuan3D 是带拓扑的,Meshy/Luma 出来才需要 retopo。"
            },
            {
                "question": "Hunyuan3D 支持通过 LoRA / 参考图锁定画风。",
                "answer": True,
                "analysis": "✅ 正确理解:Hunyuan3D 通过 LoRA / 参考图锁定画风(类似 2D 那套),可以保持风格一致性。\n\n❌ 常见误解:以为每次出图风格都随机——LoRA 锁定 + 参考图 conditioning 是 AI 资产生成的基本能力。"
            }
        ]
    }
]


def make_html(entry):
    """根据 entry 数据生成单个 HTML 卡牌。"""
    base = entry["basename"]
    title = entry["title"]
    subtitle = entry["subtitle"]
    source_md = entry["source_md"]
    drag_json = json.dumps(entry["drag"], ensure_ascii=False, indent=2)
    single_json = json.dumps(entry["single"], ensure_ascii=False, indent=2)
    multi_json = json.dumps(entry["multi"], ensure_ascii=False, indent=2)
    tf_json = json.dumps(entry["tf"], ensure_ascii=False, indent=2)
    template = HTML_TEMPLATE
    out = (template
        .replace("__TITLE__", title)
        .replace("__SUBTITLE__", subtitle)
        .replace("__SOURCE_MD__", source_md)
        .replace("__DRAG_JSON__", drag_json)
        .replace("__SINGLE_JSON__", single_json)
        .replace("__MULTI_JSON__", multi_json)
        .replace("__TF_JSON__", tf_json))
    return out


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__ — 互动式面试卡牌</title>
<style>
  :root {
    --bg:#f5f5f0; --card-bg:#fff; --primary:#3a5a7c; --accent:#6b9e75; --accent-wrong:#c45c5c;
    --text:#2c3e50; --text-light:#5d6d7e; --border:#d0d5dd; --shadow:rgba(0,0,0,0.08);
    --drop-zone:#eef2f7; --draggable:#f0f4f8;
    --status-correct:#e8f5e9; --status-wrong:#fce8e8; --status-unanswered:#f8f9fa;
  }
  *{box-sizing:border-box}
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);margin:0;padding:0;min-height:100vh}
  header{background:var(--primary);color:#fff;padding:1.2rem 1.5rem;box-shadow:0 2px 8px var(--shadow)}
  header h1{margin:0;font-size:1.2rem;font-weight:500}
  header p{margin:0.2rem 0 0;opacity:0.85;font-size:0.85rem}
  .container{max-width:820px;margin:0 auto;padding:1.5rem}
  .nav-tabs{display:flex;gap:0.4rem;margin-bottom:1.0rem;flex-wrap:wrap}
  .nav-tab{flex:1;min-width:90px;padding:0.6rem 0.6rem;border:1px solid var(--border);border-radius:8px;background:var(--card-bg);cursor:pointer;text-align:center;font-size:0.85rem;transition:all 0.2s;color:var(--text-light)}
  .nav-tab.active{background:var(--primary);color:#fff;border-color:var(--primary);box-shadow:0 2px 6px rgba(58,90,124,0.25)}
  .nav-tab:hover:not(.active){background:var(--drop-zone)}
  .score-bar{display:flex;align-items:center;gap:1rem;margin-bottom:0.6rem;flex-wrap:wrap}
  .score-mini{font-size:0.85rem;color:var(--text-light);white-space:nowrap}
  .score-mini .score-num{color:var(--primary);font-weight:700;font-size:1.05rem}
  .progress-text{text-align:right;font-size:0.8rem;color:var(--text-light);margin-bottom:0.3rem}
  .progress-bar{height:6px;background:#e8e8e0;border-radius:3px;overflow:hidden;margin-bottom:1.2rem}
  .progress-fill{height:100%;background:var(--accent);border-radius:3px;transition:width 0.3s ease}
  .card{background:var(--card-bg);border-radius:12px;padding:1.6rem 1.8rem;box-shadow:0 4px 16px var(--shadow);margin-bottom:1.2rem}
  .card-number{display:inline-block;width:26px;height:26px;background:var(--primary);color:#fff;border-radius:50%;text-align:center;line-height:26px;font-size:0.8rem;font-weight:600;margin-right:0.5rem}
  .card h3{margin:0 0 1.0rem;font-size:1.05rem;font-weight:500;line-height:1.5}
  .q-type{font-size:0.75rem;color:var(--text-light);background:#eef2f7;padding:2px 8px;border-radius:4px;margin-left:0.4rem}
  .drag-sentence{font-size:1.0rem;line-height:2.4;margin-bottom:1.2rem}
  .drop-zone{display:inline-block;min-width:90px;height:32px;line-height:30px;border:2px dashed var(--border);border-radius:6px;background:var(--drop-zone);text-align:center;vertical-align:middle;margin:0 3px;transition:all 0.2s;padding:0 6px;font-size:0.95rem}
  .drop-zone.drag-over{background:#dbe4ee;border-color:var(--primary)}
  .drop-zone.filled{border-style:solid;border-color:var(--primary);background:#e8f0f8;cursor:pointer}
  .drop-zone.correct{border-color:var(--accent);background:#e8f5e9}
  .drop-zone.wrong{border-color:var(--accent-wrong);background:#fce8e8}
  .drop-zone .dropped-text{font-weight:500;color:var(--primary)}
  .drop-zone.correct .dropped-text{color:var(--accent)}
  .drop-zone.wrong .dropped-text{color:var(--accent-wrong)}
  .drag-pool{margin:1.2rem 0;display:flex;flex-wrap:wrap;gap:0.5rem;padding:0.8rem;background:var(--drop-zone);border-radius:8px}
  .draggable{padding:0.4rem 0.9rem;background:var(--draggable);border:1px solid var(--border);border-radius:6px;cursor:grab;user-select:none;transition:all 0.15s;font-size:0.92rem}
  .draggable:hover{background:#dbe4ee;border-color:var(--primary);transform:translateY(-1px)}
  .draggable.used{opacity:0.35;cursor:default;pointer-events:none}
  .options-list{display:flex;flex-direction:column;gap:0.5rem;margin-bottom:1.0rem}
  .option{padding:0.7rem 1.0rem;background:var(--card-bg);border:1.5px solid var(--border);border-radius:8px;cursor:pointer;transition:all 0.15s;display:flex;align-items:center;gap:0.6rem;font-size:0.95rem;line-height:1.45}
  .option:hover{border-color:var(--primary);background:var(--drop-zone)}
  .option.selected{border-color:var(--primary);background:#e8f0f8}
  .option.correct-mark{border-color:var(--accent);background:#e8f5e9}
  .option.wrong-mark{border-color:var(--accent-wrong);background:#fce8e8}
  .option .opt-marker{width:22px;height:22px;border:1.5px solid var(--border);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:0.78rem;font-weight:600;flex-shrink:0;background:#fff}
  .option.selected .opt-marker{background:var(--primary);color:#fff;border-color:var(--primary)}
  .option.correct-mark .opt-marker{background:var(--accent);color:#fff;border-color:var(--accent)}
  .option.wrong-mark .opt-marker{background:var(--accent-wrong);color:#fff;border-color:var(--accent-wrong)}
  .tf-options{display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;margin-bottom:1.0rem}
  .tf-btn{padding:0.9rem;border:1.5px solid var(--border);border-radius:8px;background:var(--card-bg);cursor:pointer;transition:all 0.15s;font-size:0.95rem;text-align:center}
  .tf-btn:hover{border-color:var(--primary);background:var(--drop-zone)}
  .tf-btn.selected{border-color:var(--primary);background:#e8f0f8}
  .tf-btn.correct-mark{border-color:var(--accent);background:#e8f5e9}
  .tf-btn.wrong-mark{border-color:var(--accent-wrong);background:#fce8e8}
  .feedback{margin-top:1.0rem;padding:0.9rem 1.1rem;border-radius:8px;background:#f0f4f8;border-left:3px solid var(--primary);font-size:0.92rem;line-height:1.6;display:none}
  .feedback.show{display:block}
  .feedback.feedback-correct{border-left-color:var(--accent);background:#e8f5e9}
  .feedback.feedback-wrong{border-left-color:var(--accent-wrong);background:#fce8e8}
  .feedback-title{font-weight:600;margin-bottom:0.3rem;display:block}
  .feedback ul{margin:0.4rem 0 0 0;padding-left:1.2rem}
  .feedback li{margin-bottom:0.3rem}
  .action-row{display:flex;gap:0.6rem;flex-wrap:wrap;margin-top:1.0rem}
  .btn{padding:0.55rem 1.2rem;border-radius:8px;border:1px solid var(--border);background:var(--card-bg);color:var(--text);cursor:pointer;font-size:0.9rem;transition:all 0.15s}
  .btn:hover{background:var(--drop-zone);border-color:var(--primary)}
  .btn-primary{background:var(--primary);color:#fff;border-color:var(--primary)}
  .btn-primary:hover{background:#2c4661;border-color:#2c4661;color:#fff}
  .nav-row{display:flex;justify-content:space-between;margin-top:0.8rem;gap:0.6rem}
  .overview-panel{display:none;background:var(--card-bg);border-radius:12px;padding:1.6rem 1.8rem;box-shadow:0 4px 16px var(--shadow);margin-bottom:1.2rem}
  .overview-panel.show{display:block}
  .overview-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.0rem;flex-wrap:wrap;gap:0.5rem}
  .overview-header h2{margin:0;font-size:1.15rem;font-weight:500}
  .overview-stats{display:flex;gap:0.5rem;flex-wrap:wrap}
  .filter-btn{padding:0.4rem 0.8rem;background:var(--drop-zone);border:1px solid var(--border);border-radius:6px;cursor:pointer;font-size:0.82rem;transition:all 0.15s}
  .filter-btn.active{background:var(--primary);color:#fff;border-color:var(--primary)}
  .filter-btn:hover:not(.active){background:#dbe4ee}
  .overview-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(60px,1fr));gap:0.5rem}
  .overview-item{aspect-ratio:1;border:1.5px solid var(--border);border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;background:var(--status-unanswered);transition:all 0.15s;font-size:0.85rem}
  .overview-item.correct{background:var(--status-correct);border-color:var(--accent);color:var(--accent)}
  .overview-item.wrong{background:var(--status-wrong);border-color:var(--accent-wrong);color:var(--accent-wrong)}
  .overview-item:hover{transform:scale(1.05);box-shadow:0 2px 6px var(--shadow)}
  .overview-item .ov-num{font-weight:600;font-size:0.95rem}
  .overview-item .ov-type{font-size:0.7rem;opacity:0.7;margin-top:2px}
  .source-link{display:inline-block;margin-top:1.0rem;padding:0.5rem 1.0rem;background:var(--drop-zone);border-radius:6px;color:var(--primary);text-decoration:none;font-size:0.88rem;border:1px solid var(--border)}
  .source-link:hover{background:#dbe4ee}
</style>
</head>
<body>
<header>
  <h1>__TITLE__</h1>
  <p>__SUBTITLE__</p>
</header>
<div class="container">

<div class="nav-tabs">
  <div class="nav-tab active" data-type="all">全部</div>
  <div class="nav-tab" data-type="drag">拖拽填空</div>
  <div class="nav-tab" data-type="single">单选题</div>
  <div class="nav-tab" data-type="multi">多选题</div>
  <div class="nav-tab" data-type="tf">判断题</div>
</div>

<div class="score-bar">
  <div class="score-mini">已答:<span class="score-num" id="answered-num">0</span> / <span id="total-num">0</span></div>
  <div class="score-mini">正确:<span class="score-num" id="correct-num">0</span></div>
  <div class="score-mini">错误:<span class="score-num" id="wrong-num">0</span></div>
  <div class="score-mini">得分:<span class="score-num" id="score-pct">0%</span></div>
  <div style="flex:1"></div>
  <button class="btn" id="btn-overview">📊 题目总览</button>
  <button class="btn" id="btn-reset-all">🔄 重置所有分数</button>
</div>
<div class="progress-text" id="progress-text">第 1 题 / 共 0 题</div>
<div class="progress-bar"><div class="progress-fill" id="progress-fill" style="width:0%"></div></div>

<div class="overview-panel" id="overview-panel">
  <div class="overview-header">
    <h2>题目总览</h2>
    <div class="overview-stats">
      <div class="filter-btn active" data-filter="all">全部</div>
      <div class="filter-btn" data-filter="unanswered">未答</div>
      <div class="filter-btn" data-filter="correct">正确</div>
      <div class="filter-btn" data-filter="wrong">错误</div>
    </div>
  </div>
  <div class="overview-grid" id="overview-grid"></div>
</div>

<div id="q-container"></div>

<div class="nav-row">
  <button class="btn btn-primary" id="btn-prev">← 上一题</button>
  <button class="btn btn-primary" id="btn-next">下一题 →</button>
</div>

<a class="source-link" href="./__SOURCE_MD__">📄 查看原始笔记(MD)</a>

</div>

<script>
// 题目数据
const dragQuestions = __DRAG_JSON__;
const singleQuestions = __SINGLE_JSON__;
const multiQuestions = __MULTI_JSON__;
const trueFalseQuestions = __TF_JSON__;

const allQuestions = [
  ...dragQuestions.map((q,i)=>({type:'drag', index:i})),
  ...singleQuestions.map((q,i)=>({type:'single', index:i})),
  ...multiQuestions.map((q,i)=>({type:'multi', index:i})),
  ...trueFalseQuestions.map((q,i)=>({type:'tf', index:i}))
];

let currentQ = 0;
let currentType = 'all';
let overviewOpen = false;
let overviewFilter = 'all';
let answeredSet = new Map();

function qKey(type, idx) { return type + '_' + idx; }
function getTotal() { return allQuestions.length; }
function getFilteredIndices() {
  if (currentType === 'all') return allQuestions.map((_,i)=>i);
  return allQuestions.map((q,i)=>q.type===currentType?i:-1).filter(i=>i>=0);
}

function getCurrentQDef() {
  const def = allQuestions[currentQ];
  if (def.type === 'drag') return { def: dragQuestions[def.index], type: 'drag', num: def.index+1 };
  if (def.type === 'single') return { def: singleQuestions[def.index], type: 'single', num: def.index+1 };
  if (def.type === 'multi') return { def: multiQuestions[def.index], type: 'multi', num: def.index+1 };
  return { def: trueFalseQuestions[def.index], type: 'tf', num: def.index+1 };
}

function setAnswered(type, idx, result) {
  answeredSet.set(qKey(type, idx), result);
  updateScoreBar();
  updateOverviewGrid();
}

function updateScoreBar() {
  const total = getTotal();
  let correct = 0, wrong = 0;
  for (const v of answeredSet.values()) {
    if (v === 'correct') correct++;
    else if (v === 'wrong') wrong++;
  }
  const answered = correct + wrong;
  document.getElementById('answered-num').textContent = answered;
  document.getElementById('correct-num').textContent = correct;
  document.getElementById('wrong-num').textContent = wrong;
  const pct = total > 0 ? Math.round((correct / total) * 100) : 0;
  document.getElementById('score-pct').textContent = pct + '%';
}

function updateProgress() {
  const filtered = getFilteredIndices();
  const pos = filtered.indexOf(currentQ);
  const total = filtered.length;
  document.getElementById('progress-text').textContent = `第 ${pos+1} 题 / 共 ${total} 题`;
  document.getElementById('progress-fill').style.width = (total > 0 ? ((pos+1)/total)*100 : 0) + '%';
  document.getElementById('total-num').textContent = total;
}

function updateOverviewGrid() {
  const grid = document.getElementById('overview-grid');
  grid.innerHTML = '';
  allQuestions.forEach((q, i) => {
    const div = document.createElement('div');
    div.className = 'overview-item';
    const status = answeredSet.get(qKey(q.type, q.index));
    if (status === 'correct') div.classList.add('correct');
    else if (status === 'wrong') div.classList.add('wrong');
    if (i === currentQ) div.style.outline = '3px solid var(--primary)';
    if (overviewFilter === 'unanswered' && status) { div.style.display = 'none'; return; }
    if (overviewFilter === 'correct' && status !== 'correct') { div.style.display = 'none'; return; }
    if (overviewFilter === 'wrong' && status !== 'wrong') { div.style.display = 'none'; return; }
    const typeMap = { drag: '拖', single: '单', multi: '多', tf: '判' };
    div.innerHTML = `<div class="ov-num">${i+1}</div><div class="ov-type">${typeMap[q.type]}</div>`;
    div.onclick = () => { currentQ = i; renderQuestion(); toggleOverview(false); };
    grid.appendChild(div);
  });
}

function toggleOverview(force) {
  const panel = document.getElementById('overview-panel');
  if (typeof force === 'boolean') { overviewOpen = force; panel.classList.toggle('show', force); }
  else { overviewOpen = !overviewOpen; panel.classList.toggle('show', overviewOpen); }
  if (overviewOpen) updateOverviewGrid();
}

// 拖拽填空
function renderDrag(def) {
  const container = document.getElementById('q-container');
  const parts = def.sentence.split(/(\\{\\d+\\})/g);
  let slotsHTML = '';
  let slotIdx = 0;
  for (const p of parts) {
    const m = p.match(/^\\{(\\d+)\\}$/);
    if (m) { slotsHTML += `<span class="drop-zone" data-slot="${slotIdx}" data-empty="true">　</span>`; slotIdx++; }
    else { slotsHTML += p; }
  }
  const shuffled = [...def.pool].sort(()=>Math.random()-0.5);
  let poolHTML = '<div class="drag-pool">';
  for (const term of shuffled) {
    poolHTML += `<div class="draggable" draggable="true" data-term="${term}">${term}</div>`;
  }
  poolHTML += '</div>';
  container.innerHTML = `
    <div class="card">
      <h3><span class="card-number">${currentQ+1}</span>${def.sentence.replace(/[{}]/g,'').substring(0,40)}…<span class="q-type">拖拽填空</span></h3>
      <div class="drag-sentence">${slotsHTML}</div>
      ${poolHTML}
      <div class="feedback" id="feedback"></div>
      <div class="action-row">
        <button class="btn btn-primary" id="btn-check">检查答案</button>
        <button class="btn" id="btn-reset">重置本题</button>
      </div>
    </div>
  `;
  const fillState = Array(def.answers.length).fill(null);
  const draggables = container.querySelectorAll('.draggable');
  const dropZones = container.querySelectorAll('.drop-zone');
  draggables.forEach(d => {
    d.addEventListener('dragstart', e => {
      e.dataTransfer.setData('text/plain', d.dataset.term);
      e.dataTransfer.effectAllowed = 'move';
    });
  });
  dropZones.forEach(zone => {
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
    zone.addEventListener('drop', e => {
      e.preventDefault();
      zone.classList.remove('drag-over');
      const term = e.dataTransfer.getData('text/plain');
      const slot = parseInt(zone.dataset.slot);
      const existingSlot = fillState.indexOf(term);
      if (existingSlot >= 0 && existingSlot !== slot) {
        fillState[existingSlot] = null;
        const oldZone = container.querySelector(`[data-slot="${existingSlot}"]`);
        oldZone.textContent = '　';
        oldZone.dataset.empty = 'true';
        oldZone.classList.remove('filled', 'correct', 'wrong');
      }
      fillState[slot] = term;
      zone.innerHTML = `<span class="dropped-text">${term}</span>`;
      zone.dataset.empty = 'false';
      zone.classList.add('filled');
      zone.classList.remove('correct', 'wrong');
      const sourceDraggable = Array.from(draggables).find(d => d.dataset.term === term);
      if (sourceDraggable) sourceDraggable.classList.add('used');
      hideFeedback();
    });
    zone.addEventListener('click', () => {
      if (zone.dataset.empty === 'true' || !fillState[parseInt(zone.dataset.slot)]) return;
      const slot = parseInt(zone.dataset.slot);
      const term = fillState[slot];
      fillState[slot] = null;
      zone.textContent = '　';
      zone.dataset.empty = 'true';
      zone.classList.remove('filled', 'correct', 'wrong');
      const sourceDraggable = Array.from(draggables).find(d => d.dataset.term === term);
      if (sourceDraggable) sourceDraggable.classList.remove('used');
      hideFeedback();
    });
  });
  document.getElementById('btn-check').onclick = () => {
    let allCorrect = true;
    fillState.forEach((term, i) => {
      const zone = container.querySelector(`[data-slot="${i}"]`);
      zone.classList.remove('correct', 'wrong');
      if (term === def.answers[i]) zone.classList.add('correct');
      else { zone.classList.add('wrong'); allCorrect = false; }
    });
    const isFull = fillState.every(t => t !== null);
    if (!isFull) { showFeedback(false, '<b>未填完</b><br>请把所有空位都填上后再检查。'); return; }
    let html = '<span class="feedback-title">' + (allCorrect ? '✅ 完全正确！' : '❌ 有错误') + '</span><ul>';
    fillState.forEach((term, i) => {
      const ok = term === def.answers[i];
      html += `<li>第 ${i+1} 空：<b>${ok?'✅ 正确':'❌ 错误'}</b> —— 你的答案：<code>${term}</code>；正确答案：<code>${def.answers[i]}</code>。${def.per_slot_analysis[i]}</li>`;
    });
    html += '</ul>';
    showFeedback(allCorrect, html);
    setAnswered('drag', dragQuestions.indexOf(def), allCorrect ? 'correct' : 'wrong');
  };
  document.getElementById('btn-reset').onclick = () => renderDrag(def);
}

// 单选
function renderSingle(def) {
  const container = document.getElementById('q-container');
  let optsHTML = '<div class="options-list">';
  def.options.forEach((opt, i) => {
    const label = opt.length > 1 && opt[1] === '.' ? opt.substring(2) : opt;
    optsHTML += `<div class="option" data-opt="${i}"><span class="opt-marker">${String.fromCharCode(65+i)}</span><span>${label}</span></div>`;
  });
  optsHTML += '</div>';
  container.innerHTML = `
    <div class="card">
      <h3><span class="card-number">${currentQ+1}</span>${def.question}<span class="q-type">单选题</span></h3>
      ${optsHTML}
      <div class="feedback" id="feedback"></div>
      <div class="action-row">
        <button class="btn btn-primary" id="btn-check">检查答案</button>
        <button class="btn" id="btn-reset">重置本题</button>
      </div>
    </div>
  `;
  let selected = null;
  const opts = container.querySelectorAll('.option');
  opts.forEach(o => {
    o.onclick = () => { if (selected !== null) return; selected = parseInt(o.dataset.opt); o.classList.add('selected'); hideFeedback(); };
  });
  document.getElementById('btn-check').onclick = () => {
    if (selected === null) { showFeedback(false, '<b>未选择</b><br>请先选一个选项。'); return; }
    const ok = selected === def.correct;
    opts.forEach((o, i) => {
      if (i === def.correct) o.classList.add('correct-mark');
      if (i === selected && i !== def.correct) o.classList.add('wrong-mark');
    });
    let html = '<span class="feedback-title">' + (ok ? '✅ 回答正确！' : '❌ 回答错误') + '</span><ul>';
    def.analysis.forEach((a, i) => html += `<li>${a}</li>`);
    html += '</ul>';
    showFeedback(ok, html);
    setAnswered('single', singleQuestions.indexOf(def), ok ? 'correct' : 'wrong');
  };
  document.getElementById('btn-reset').onclick = () => renderSingle(def);
}

// 多选
function renderMulti(def) {
  const container = document.getElementById('q-container');
  let optsHTML = '<div class="options-list">';
  def.options.forEach((opt, i) => {
    const label = opt.length > 1 && opt[1] === '.' ? opt.substring(2) : opt;
    optsHTML += `<div class="option" data-opt="${i}"><span class="opt-marker">${String.fromCharCode(65+i)}</span><span>${label}</span></div>`;
  });
  optsHTML += '</div>';
  container.innerHTML = `
    <div class="card">
      <h3><span class="card-number">${currentQ+1}</span>${def.question}<span class="q-type">多选题</span></h3>
      ${optsHTML}
      <div class="feedback" id="feedback"></div>
      <div class="action-row">
        <button class="btn btn-primary" id="btn-check">检查答案</button>
        <button class="btn" id="btn-reset">重置本题</button>
      </div>
    </div>
  `;
  const selected = new Set();
  const opts = container.querySelectorAll('.option');
  opts.forEach(o => {
    o.onclick = () => {
      const i = parseInt(o.dataset.opt);
      if (selected.has(i)) { selected.delete(i); o.classList.remove('selected'); }
      else { selected.add(i); o.classList.add('selected'); }
      hideFeedback();
    };
  });
  document.getElementById('btn-check').onclick = () => {
    if (selected.size === 0) { showFeedback(false, '<b>未选择</b><br>多选题必须至少选 1 项。'); return; }
    const correctSet = new Set(def.correct);
    const isExactMatch = selected.size === correctSet.size && [...selected].every(i => correctSet.has(i));
    opts.forEach((o, i) => {
      if (correctSet.has(i)) o.classList.add('correct-mark');
      if (selected.has(i) && !correctSet.has(i)) o.classList.add('wrong-mark');
    });
    let html = '<span class="feedback-title">' + (isExactMatch ? '✅ 完全正确！' : '❌ 有错误 / 漏选') + '</span><ul>';
    def.analysis.forEach((a, i) => html += `<li>${a}</li>`);
    html += '</ul>';
    showFeedback(isExactMatch, html);
    setAnswered('multi', multiQuestions.indexOf(def), isExactMatch ? 'correct' : 'wrong');
  };
  document.getElementById('btn-reset').onclick = () => renderMulti(def);
}

// 判断
function renderTF(def) {
  const container = document.getElementById('q-container');
  container.innerHTML = `
    <div class="card">
      <h3><span class="card-number">${currentQ+1}</span>${def.question}<span class="q-type">判断题</span></h3>
      <div class="tf-options">
        <div class="tf-btn" data-tf="true">✅ 正确(True)</div>
        <div class="tf-btn" data-tf="false">❌ 错误(False)</div>
      </div>
      <div class="feedback" id="feedback"></div>
      <div class="action-row">
        <button class="btn btn-primary" id="btn-check">检查答案</button>
        <button class="btn" id="btn-reset">重置本题</button>
      </div>
    </div>
  `;
  let selected = null;
  const btns = container.querySelectorAll('.tf-btn');
  btns.forEach(b => {
    b.onclick = () => { btns.forEach(x => x.classList.remove('selected')); b.classList.add('selected'); selected = b.dataset.tf === 'true'; hideFeedback(); };
  });
  document.getElementById('btn-check').onclick = () => {
    if (selected === null) { showFeedback(false, '<b>未选择</b><br>请先选 True 或 False。'); return; }
    const ok = selected === def.answer;
    btns.forEach(b => {
      const v = b.dataset.tf === 'true';
      if (v === def.answer) b.classList.add('correct-mark');
      if (v === selected && v !== def.answer) b.classList.add('wrong-mark');
    });
    const analysisParts = def.analysis.split('\\n\\n');
    let html = '<span class="feedback-title">' + (ok ? '✅ 判断正确！' : '❌ 判断错误') + '</span>';
    html += '<div style="white-space:pre-line;margin-top:0.3rem">' + analysisParts[0] + '</div>';
    if (analysisParts.length > 1) {
      html += '<div style="margin-top:0.6rem;padding-top:0.6rem;border-top:1px dashed var(--border);white-space:pre-line;color:var(--text-light)">' + analysisParts.slice(1).join('\\n\\n') + '</div>';
    }
    showFeedback(ok, html);
    setAnswered('tf', trueFalseQuestions.indexOf(def), ok ? 'correct' : 'wrong');
  };
  document.getElementById('btn-reset').onclick = () => renderTF(def);
}

function renderQuestion() {
  const { def, type } = getCurrentQDef();
  if (type === 'drag') renderDrag(def);
  else if (type === 'single') renderSingle(def);
  else if (type === 'multi') renderMulti(def);
  else renderTF(def);
  updateProgress();
  updateOverviewGrid();
}

function showFeedback(ok, html) {
  const fb = document.getElementById('feedback');
  fb.innerHTML = html;
  fb.classList.add('show');
  fb.classList.toggle('feedback-correct', ok);
  fb.classList.toggle('feedback-wrong', !ok);
}

function hideFeedback() {
  const fb = document.getElementById('feedback');
  if (fb) { fb.classList.remove('show'); fb.innerHTML = ''; }
}

function navTo(direction) {
  const filtered = getFilteredIndices();
  if (filtered.length === 0) return;
  const pos = filtered.indexOf(currentQ);
  let newPos = pos + direction;
  if (newPos < 0) newPos = filtered.length - 1;
  if (newPos >= filtered.length) newPos = 0;
  currentQ = filtered[newPos];
  renderQuestion();
}

document.getElementById('btn-prev').onclick = () => navTo(-1);
document.getElementById('btn-next').onclick = () => navTo(1);
document.getElementById('btn-overview').onclick = () => toggleOverview();
document.getElementById('btn-reset-all').onclick = () => {
  if (!confirm('确认重置全部答题记录？')) return;
  answeredSet.clear();
  updateScoreBar();
  updateOverviewGrid();
  currentQ = 0;
  renderQuestion();
};

document.querySelectorAll('.nav-tab').forEach(t => {
  t.onclick = () => {
    document.querySelectorAll('.nav-tab').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    currentType = t.dataset.type;
    const filtered = getFilteredIndices();
    if (filtered.length > 0) currentQ = filtered[0];
    renderQuestion();
  };
});

document.querySelectorAll('.filter-btn').forEach(b => {
  b.onclick = () => {
    document.querySelectorAll('.filter-btn').forEach(x => x.classList.remove('active'));
    b.classList.add('active');
    overviewFilter = b.dataset.filter;
    updateOverviewGrid();
  };
});

document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  if (e.key === 'ArrowLeft') navTo(-1);
  else if (e.key === 'ArrowRight') navTo(1);
  else if (e.key === 'o' || e.key === 'O') toggleOverview();
});

updateScoreBar();
renderQuestion();
updateOverviewGrid();
</script>

</body>
</html>
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for entry in ENTRIES:
        base = entry["basename"]
        out_path = os.path.join(OUT_DIR, base + ".html")
        html = make_html(entry)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        size_kb = len(html.encode("utf-8")) / 1024
        n_total = len(entry["drag"]) + len(entry["single"]) + len(entry["multi"]) + len(entry["tf"])
        print(f"✓ {base}.html  ({size_kb:.1f} KB, {n_total} 题)")
    print(f"\n全部 {len(ENTRIES)} 个文件生成完成 → {OUT_DIR}")


if __name__ == "__main__":
    main()