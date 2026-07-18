# -*- coding: utf-8 -*-
"""
生成 W29 工作产出的 Q&A 互动卡 HTML。
覆盖 5 个文件: VSM 源码 / Nanite 源码 / Mac 平台 / W28 snapshot / W29 复盘。
模板紧贴 interview-card-system 规范: 拖拽填空 / 单选 / 多选 / 判断题 / 总览 / 打分。
基于 gen_p1_cards.py 改造: 支持 per-entry out_dir(5 个文件不同目录)。

用法:
    python gen_w29_cards.py

输出:
    各 entry 自己的 out_dir/<basename>.html
"""
import os
import json

# 默认输出目录(per-entry 可覆盖)
DEFAULT_OUT_DIR = r"C:\Git-repo-my\GameDevVault\Routine\05-技术雷达"

# 5 个 W29 文件的题目数据
ENTRIES = [
    {
        "out_dir": r"C:\Git-repo-my\GameDevVault\Routine\02-引擎源码分析库\Unreal-Engine\W29",
        "basename": "UE5-VSM-源码追踪",
        "title": "VSM 虚拟阴影映射 — 引擎源码追踪(W29)",
        "subtitle": "W29 落盘 | page table + Cache + Clipmap 完整源码拆解",
        "source_md": "UE5-VSM-源码追踪.md",
        "drag": [
            {
                "sentence": "VSM 虚拟页 = {0}×{0} 像素,物理页寻址 = {1} bit,最大物理页数 = {2}。",
                "answers": ["128", "16", "65536"],
                "pool": ["128", "256", "16", "32", "65536", "1048576"],
                "per_slot_analysis": [
                    "FVirtualShadowMap::PageSize = 128(从 VSM_PAGE_SIZE 常量)",
                    "PhysicalPageAddressBits = 16(物理页地址用 16 bit 编码)",
                    "MaxPhysicalTextureDimPages = 1 << 16 = 65536"
                ]
            },
            {
                "sentence": "VSM 缓存 key 由 {0} + {1} + {2} 三元组组成。",
                "answers": ["ViewUniqueID", "LightSceneId", "ShadowTypeId"],
                "pool": ["ViewUniqueID", "LightSceneId", "ShadowTypeId", "PrimitiveId", "MaterialId"],
                "per_slot_analysis": [
                    "ViewUniqueID 区分 view 维度(主/反射/阴影 pass)",
                    "LightSceneId 区分光源(方向光/点光/聚光)",
                    "ShadowTypeId 区分同一 light + view 下的多个 shadow(eg 静态 + 动态)"
                ]
            }
        ],
        "single": [
            {
                "question": "FVirtualShadowMapArrayCacheManager 继承自哪个 UE 接口?",
                "options": [
                    "A. IRendererModule",
                    "B. ISceneExtension",
                    "C. IModuleInterface",
                    "D. FRenderResource"
                ],
                "correct": 1,
                "analysis": [
                    "❌ IRendererModule 是 Renderer 模块接口,不是 scene extension",
                    "✅ FVirtualShadowMapArrayCacheManager 通过 DECLARE_SCENE_EXTENSION 继承 ISceneExtension,生命周期跟 FScene 绑定",
                    "❌ IModuleInterface 是动态链接模块接口",
                    "❌ FRenderResource 是 RHI 资源基类"
                ]
            },
            {
                "question": "FVirtualShadowMapCacheEntry::UpdateClipmapLevel 接受的 5 个参数是?",
                "options": [
                    "A. LightDir, LightRadius, ViewCenter, ViewRadius, MipLevel",
                    "B. PageSpaceLocation, LevelRadius, ViewCenterZ, ViewRadiusZ, WPODistanceDisabledThreshold",
                    "C. LevelIndex, LightPos, CameraPos, FarPlane, NearPlane",
                    "D. MipOffset, ViewportRect, ProjectionMatrix, DepthBias, LightRadius"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 这不是 UpdateClipmapLevel 的签名",
                    "✅ 5 参数是源码明确列出的:PageSpaceLocation(FInt64Point)+ LevelRadius(double)+ ViewCenterZ(double)+ ViewRadiusZ(double)+ WPODistanceDisabledThreshold(double)",
                    "❌ 这些是其他 shadow 函数可能用的参数",
                    "❌ 同样不是 UpdateClipmapLevel"
                ]
            },
            {
                "question": "VSM 帧数据持久化用哪种 RHI 资源包装?",
                "options": [
                    "A. FRDGTexture 直接持有",
                    "B. TRefCountPtr<IPooledRenderTarget>",
                    "C. FTextureRHIRef 裸引用",
                    "D. TArray<uint8> CPU 镜像"
                ],
                "correct": 1,
                "analysis": [
                    "❌ RDG 资源是 transient,不能跨帧持有",
                    "✅ FVirtualShadowMapArrayFrameData 用 TRefCountPtr<IPooledRenderTarget> 持有前一帧的 pooled target,新帧通过 RDG externally-pooled 引入",
                    "❌ FTextureRHIRef 不带引用计数,容易悬挂",
                    "❌ 9 个资源不可能 CPU 镜像,显存太大"
                ]
            }
        ],
        "multi": [
            {
                "question": "VSM 的关键 CVar 中,关闭会显著影响性能的是?(多选)",
                "options": [
                    "A. r.Shadow.Virtual.Cache",
                    "B. r.Shadow.Virtual.MaxPhysicalPages",
                    "C. r.Shadow.Virtual.AllowHZB",
                    "D. r.Shadow.Virtual.MegaLights",
                    "E. r.Shadow.Virtual.Debug"
                ],
                "correct": [0, 1, 2],
                "analysis": [
                    "✅ r.Shadow.Virtual.Cache=0 关闭 LRU,每帧全重渲,性能断崖下降",
                    "✅ r.Shadow.Virtual.MaxPhysicalPages 调小 → 页溢出 → 阴影棋盘瑕疵 + 反复重渲",
                    "✅ r.Shadow.Virtual.AllowHZB=0 关闭 HZB 加速 local receiver mask,CPU 开销上升",
                    "❌ r.Shadow.Virtual.MegaLights=0 关闭多光源 VSM 集成,性能影响不大",
                    "❌ r.Shadow.Virtual.Debug 只影响调试可视化,不影响性能"
                ]
            },
            {
                "question": "VSM 在 Mac Metal RHI 上的已知问题包括?(多选)",
                "options": [
                    "A. BC6H 压缩部分早期 Apple Silicon 不支持",
                    "B. 物理页池 atomic 行为差异需调小 MaxPhysicalPages",
                    "C. Async compute pass 是 sequential",
                    "D. Multithreaded command encoding 强制单线程",
                    "E. VSM 在 Mac 上完全不支持"
                ],
                "correct": [0, 1, 2, 3],
                "analysis": [
                    "✅ BC6H 压缩在 Apple Silicon 部分早期不支持,5.4+ 加 fallback",
                    "✅ MTLBuffer atomic 行为差异,MaxPhysicalPages 需调小",
                    "✅ Metal async compute 是 sequential,需要 Throttle 主动控制",
                    "✅ Metal 强制单线程 command encoding,dispatch 策略不同",
                    "❌ VSM 在 Mac 上完全不支持是错的,5.4+ 完整支持"
                ]
            }
        ],
        "tf": [
            {
                "question": "FVirtualShadowMap::MaxMipLevels ≤ 8 是 hard constraint,超过需要更多 PageFlags bit。",
                "answer": True,
                "analysis": "✅ 正确理解:源码有 static_assert(MaxMipLevels <= 8),超过 8 mip 需要 VSM_PAGE_FLAGS_BITS_PER_HMIP 加位。\n\n❌ 常见误解:以为 mip 数无限制——其实 8 mip 是 PageFlags 的位宽硬约束。"
            },
            {
                "question": "FVirtualShadowMapPerLightCacheEntry::RenderedPrimitives 是 TBitArray,标记哪些 primitive 在本帧被这个 light 渲染过。",
                "answer": True,
                "analysis": "✅ 正确理解:RenderedPrimitives = TBitArray<>(false, MaxPersistentScenePrimitiveIndex),位索引 = PersistentPrimitiveIndex,是 VSM 失效追踪的核心。\n\n❌ 常见误解:以为每帧重建——其实是 BitArray,set/clear 操作,没有分配开销。"
            },
            {
                "question": "VSM 在 UE 5.4+ 完全支持 Mac Metal RHI,没有任何兼容性问题。",
                "answer": False,
                "analysis": "✅ 正确理解:5.4+ 完整支持但有 4 大问题:BC6H 压缩、atomic 行为、async compute 串行化、单线程 command encoding。\n\n❌ 常见误解:以为'支持'='无问题'——支持跟好用是两回事,需要 CVar 调优。"
            }
        ]
    },
    {
        "out_dir": r"C:\Git-repo-my\GameDevVault\Routine\02-引擎源码分析库\Unreal-Engine\W29",
        "basename": "UE5-Nanite-MeshPass-ClusterDAG-PageStreaming-源码追踪",
        "title": "Nanite 虚拟几何 — Mesh Pass + Cluster DAG + Page Streaming 源码追踪(W29)",
        "subtitle": "W29 起头 | 38 文件结构 + 关键子系统入口",
        "source_md": "UE5-Nanite-MeshPass-ClusterDAG-PageStreaming-源码追踪.md",
        "drag": [
            {
                "sentence": "Nanite 集群大小 = {0} 三角,Nanite 公开 API EmitShadowMap + {1} + {2} 共 4 个。",
                "answers": ["128", "EmitCubemapShadow", "PrintStats"],
                "pool": ["128", "256", "EmitCubemapShadow", "ExtractShadingDebug", "PrintStats", "StreamOutData"],
                "per_slot_analysis": [
                    "128-tri cluster = SIMD 优化边界,GPU 一次 threadgroup 32 线程可处理",
                    "EmitCubemapShadow 是立方体阴影(点光源用)",
                    "PrintStats 是 GPU 端 Nanite 统计打印"
                ]
            }
        ],
        "single": [
            {
                "question": "ERasterScheduling 枚举的 3 个值是?",
                "options": [
                    "A. HardwareOnly / HardwareThenSoftware / HardwareAndSoftwareOverlap",
                    "B. Sync / Async / Hybrid",
                    "C. SinglePass / MultiPass / Deferred",
                    "D. Direct / Indirect / Compute"
                ],
                "correct": 0,
                "analysis": [
                    "✅ 源码明确枚举:HardwareOnly=0(仅硬件光栅)/ HardwareThenSoftware=1(硬件大三角 + 软件小三角)/ HardwareAndSoftwareOverlap=2(两者并行)",
                    "❌ 这是 RHI 的术语,不是 Nanite raster scheduling",
                    "❌ 这是 Pass 概念,跟 raster scheduling 不同",
                    "❌ 这是 GPU dispatch 模式,不是 raster scheduling"
                ]
            },
            {
                "question": "Nanite FPackedView 中的 PreViewTranslationHigh/Low 用途是?",
                "options": [
                    "A. 提升渲染精度",
                    "B. 32-bit float 大场景下精度丢失,High/Low 拆分避免",
                    "C. 内存对齐优化",
                    "D. 多 GPU 同步"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 不是简单的'提升精度'",
                    "✅ PreViewTranslationHigh 存大场景整体偏移的高位,PreViewTranslationLow 存相对偏移,GPU 端 WorldPos = TranslatedWorld + (High - Low) 重建,避免大世界坐标在 32-bit float 下精度丢失",
                    "❌ 跟内存对齐无关",
                    "❌ 多 GPU 同步另用机制,跟 PreViewTranslation 无关"
                ]
            },
            {
                "question": "Nanite FRasterParameters 的 OutVisBuffer64 是什么?",
                "options": [
                    "A. 64-bit RGB 颜色缓冲",
                    "B. 64-bit packed visibility buffer = cluster ID + triangle ID",
                    "C. 64 位精度的深度缓冲",
                    "D. 64-bit UV 坐标缓冲"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 不是颜色缓冲",
                    "✅ OutVisBuffer64 = 64-bit packed = 32-bit cluster ID + 32-bit triangle ID,shading pass 二次读取,Nanite'GPU-Driven'的关键",
                    "❌ 深度通常是 32-bit 浮点,不是 64-bit",
                    "❌ UV 在材质求值时单独处理"
                ]
            }
        ],
        "multi": [
            {
                "question": "Nanite 38 个源文件按功能分组,包括?(多选)",
                "options": [
                    "A. 渲染子系统:CullRaster / Visibility / Shading / Composition / DrawList",
                    "B. 材质:Materials / MaterialsSceneExtension / Shared",
                    "C. 流式加载:StreamOut / Feedback",
                    "D. Ray Tracing:RayTracing / RayTracingASCache / Translucency",
                    "E. CPU 网格处理:CPUGeometry",
                    "F. Scene 扩展:OwnershipVisibilitySceneExtension / Editor"
                ],
                "correct": [0, 1, 2, 3, 5],
                "analysis": [
                    "✅ 渲染子系统 5 个:NaniteCullRaster / NaniteVisibility / NaniteShading / NaniteComposition / NaniteDrawList",
                    "✅ 材质 3 个:NaniteMaterials / NaniteMaterialsSceneExtension / NaniteShared",
                    "✅ 流式加载 2 个:NaniteStreamOut / NaniteFeedback",
                    "✅ Ray Tracing 3 个:NaniteRayTracing / NaniteRayTracingASCache / NaniteTranslucency",
                    "❌ 没有 CPUGeometry 这个文件",
                    "✅ Scene 扩展 2 个:NaniteOwnershipVisibilitySceneExtension / NaniteEditor"
                ]
            },
            {
                "question": "Nanite Stream-out 系统的 3 个数据结构是?(多选)",
                "options": [
                    "A. FStreamOutRequest",
                    "B. FStreamOutMeshDataHeader",
                    "C. FStreamOutMeshDataSegment",
                    "D. FStreamOutTexture",
                    "E. FStreamOutCommand"
                ],
                "correct": [0, 1, 2],
                "analysis": [
                    "✅ FStreamOutRequest = 单个 stream-out 请求(per primitive),含 PrimitiveId/NumMaterials/NumSegments 等",
                    "✅ FStreamOutMeshDataHeader = 输出的 mesh 数据头(Cluster/Vertex/Index counts)",
                    "✅ FStreamOutMeshDataSegment = mesh 段(用于 LOD chain 的 segment)",
                    "❌ 没有 FStreamOutTexture",
                    "❌ 没有 FStreamOutCommand"
                ]
            }
        ],
        "tf": [
            {
                "question": "Nanite::EmitShadowMap 是 Nanite 公开 API,被 VSM 调用作为 Nanite → VSM 的入口。",
                "answer": True,
                "analysis": "✅ 正确理解:EmitShadowMap 在 Nanite.h:33-44 定义,被 VSM 的 FShadowRenderer 调用,把 Nanite 几何作为阴影源。\n\n❌ 常见误解:以为 EmitShadowMap 只能从主渲染调用——其实是公开 API,任何需要 Nanite 阴影的 pass 都能用。"
            },
            {
                "question": "EOutputBufferMode 的 VisBuffer 模式只输出 depth,不输出 ID。",
                "answer": False,
                "analysis": "✅ 正确理解:VisBuffer 模式输出 64-bit packed ID + depth(默认模式);DepthOnly 模式只输出 depth(用于 VSM / depth pre-pass)。\n\n❌ 常见误解:以为 VisBuffer = depth-only——VisBuffer 是 visibility buffer 的简称,包含 ID 用于二次材质求值。"
            },
            {
                "question": "Nanite 5.0 → 5.4 的跃迁中,4015 bin → 3675 空 bin 浪费 90%,5.4 通过材质 Bin 调度减少 80% 空调度。",
                "answer": True,
                "analysis": "✅ 正确理解:W29 README + W29 Lumen SurfaceCache 源码分析都提到这个数字。5.4 通过按需调度材质 bin,把空 bin 浪费从 90% 降到 ~10%。\n\n❌ 常见误解:以为 5.4 只是性能提升——其实是 shader scheduling 范式改变。"
            }
        ]
    },
    {
        "out_dir": r"C:\Git-repo-my\GameDevVault\Routine\Mac-平台",
        "basename": "00-README",
        "title": "Mac 平台 — Apple Silicon UE5 vault 索引(W29)",
        "subtitle": "W29 起头 | 5 anchor + DX12/Metal 差异速查",
        "source_md": "00-README.md",
        "drag": [
            {
                "sentence": "Mac 平台 vault 立 {0} 个 anchor,首篇 W30 起的 anchor 是 {1} 和 {2}。",
                "answers": ["5", "渲染特性 × Metal RHI 兼容矩阵", "RAG 语料切分策略"],
                "pool": ["5", "3", "渲染特性 × Metal RHI 兼容矩阵", "Lyra on Mac", "RAG 语料切分策略", "MSLL 编译坑"],
                "per_slot_analysis": [
                    "5 个 anchor 是 W29 立的待办,每个 anchor 后续展开成一篇实质笔记",
                    "Anchor 1 渲染特性 × Metal RHI 兼容矩阵是 W30 必做,跟 Lumen/Nanite/VSM 升'已掌握'门槛绑定",
                    "Anchor 4 RAG 语料切分策略是 day-job 落地直接依赖"
                ]
            }
        ],
        "single": [
            {
                "question": "Mac 平台 vault 的 5 个 anchor 不包括?",
                "options": [
                    "A. Mac Metal RHI 适配清单",
                    "B. Apple Silicon Unified Memory 对 GPU 预算的影响",
                    "C. Metal Shader (MSLL) 编译坑",
                    "D. Nanite Cluster 切分算法源码"
                ],
                "correct": 3,
                "analysis": [
                    "✅ Anchor 1:Mac Metal RHI 适配清单",
                    "✅ Anchor 2:Apple Silicon Unified Memory 对 GPU 预算的影响",
                    "✅ Anchor 3:Metal Shader (MSLL) 编译坑",
                    "❌ Nanite Cluster 切分算法源码 属于 02-引擎源码分析库 W30 续写,不在 Mac 平台 anchor 里"
                ]
            },
            {
                "question": "Apple Silicon 的 Unified Memory 关键优势是?",
                "options": [
                    "A. GPU 显存跟 CPU 内存独立",
                    "B. CPU 和 GPU 共享同一块内存,理论可用空间更大",
                    "C. 显存频率比 PC GPU 高 10x",
                    "D. 内存带宽无限"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 独立显存是传统 PC GPU 模式",
                    "✅ Apple Silicon Unified Memory = CPU 和 GPU 共享同一块内存,理论可用空间更大(eg M2 Max 96GB 共享),但 atomic 行为跟 PC GPU 不同",
                    "❌ 频率不是 10x,跟 PC GPU 同代差不多",
                    "❌ 带宽无限是营销话术,实际有上限"
                ]
            }
        ],
        "multi": [
            {
                "question": "UE 渲染特性 × Metal RHI 兼容性矩阵中,Mac 上有兼容问题需要 CVar 调优的是?(多选)",
                "options": [
                    "A. Lumen 全局光照",
                    "B. Nanite 虚拟几何",
                    "C. VSM 虚拟阴影",
                    "D. MegaLights 随机光照",
                    "E. Substrate 材质系统"
                ],
                "correct": [0, 1, 2, 3],
                "analysis": [
                    "✅ Lumen 反射 tier 降级在 Mac Metal 上可能跟 DX12 不一致,需要 Anchor 1 验证",
                    "✅ Nanite Page Streaming 在 Apple Silicon 上内存压力需评估,5.4+ 已加 fallback",
                    "✅ VSM BC6H 压缩 + atomic 行为在 Mac 上需调 MaxPhysicalPages",
                    "✅ MegaLights 跟 Metal threadgroup 不兼容,5.4+ 已修但仍需验证",
                    "❌ Substrate 在 Mac 上完整支持,无已知问题"
                ]
            }
        ],
        "tf": [
            {
                "question": "Mac 平台 vault 缺位 1 个季度,W29 必建是 Lumen/Nanite/VSM 升'已掌握'门槛的先决条件。",
                "answer": True,
                "analysis": "✅ 正确理解:Mac 实测是 3 大渲染特性升'已掌握'的硬门槛(必须 Mac Metal RHI 上跑通),缺位 → 8/7 月度回顾时无法升'已掌握'。\n\n❌ 常见误解:以为 Mac 是锦上添花——其实是 day-job 主线硬约束。"
            }
        ]
    },
    {
        "out_dir": r"C:\Git-repo-my\GameDevVault\Routine\05-技术雷达\Weekly-Log\W28-2026-07-12",
        "basename": "W28-snapshot",
        "title": "W28 周复盘(2026-07-06 ~ 2026-07-12)— 历史快照",
        "subtitle": "W28 兑现率 10% | 渲染三特性正式入 P0",
        "source_md": "W28-snapshot.md",
        "drag": [
            {
                "sentence": "W28 4 主题源码追踪包括 {0} / {1} / {2} / {3}。",
                "answers": ["MegaLights", "Substrate", "InstanceCulling", "HeterogeneousVolumes"],
                "pool": ["MegaLights", "Substrate", "InstanceCulling", "HeterogeneousVolumes", "Lumen", "VSM"],
                "per_slot_analysis": [
                    "MegaLights = 5.4+ 随机光照",
                    "Substrate = 现代材质系统",
                    "InstanceCulling = GPU 裁剪",
                    "HeterogeneousVolumes = 体素体积(7 pipeline)"
                ]
            }
        ],
        "single": [
            {
                "question": "W28 雷达补全新增了哪个 P0 子节?",
                "options": [
                    "A. P0-立即学习(工具链轴)",
                    "B. P0-渲染特性",
                    "C. P1-持续关注",
                    "D. P2-了解即可"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 工具链轴 P0 是 7-03 已有的",
                    "✅ W28 (7-12) 新增 P0-渲染特性子节,放 Lumen / Nanite / VSM 3 项,跟工具链轴 P0 正交",
                    "❌ P1 / P2 在 W28 没动"
                ]
            },
            {
                "question": "W28 自爆的兑现率是?",
                "options": [
                    "A. 100%",
                    "B. 70%",
                    "C. 30%(硬数字 10%)",
                    "D. 0%"
                ],
                "correct": 2,
                "analysis": [
                    "❌ 100% 不可能,W28 漏了 5 个复评 + Hunyuan3D",
                    "❌ 70% 是 W29 收尾的兑现率",
                    "✅ W28 自爆 30%(README 公开写的);硬数字计算 1/10 = 10%(4 主题 + 渲染特性入 P0 算入后 ~30%)",
                    "❌ 0% 显然不对,4 主题源码 + 渲染特性入 P0 完成"
                ]
            }
        ],
        "multi": [
            {
                "question": "W28 4 主题源码追踪每个都配套了哪些产物?(多选)",
                "options": [
                    "A. MD 笔记",
                    "B. HTML 互动卡牌",
                    "C. W28 README 索引",
                    "D. 提交到 master 分支"
                ],
                "correct": [0, 1, 2],
                "analysis": [
                    "✅ 4 主题每个都有 MD 笔记(31-39KB)",
                    "✅ 4 主题每个都有 HTML 互动卡牌(41-53KB)",
                    "✅ W28 README 索引文件汇总 4 主题",
                    "❌ '提交到 master 分支'不是产物,是发布动作,不能算每个主题的产物"
                ]
            }
        ],
        "tf": [
            {
                "question": "W28 雷达补全:渲染三大特性(Lumen / Nanite / VSM)全部都补了完整源码追踪。",
                "answer": False,
                "analysis": "✅ 正确理解:W28 只把 3 特性'加入' P0 雷达(MD 文件 + 现状说明),源码追踪是 W29 才起的头,W30 续写。\n\n❌ 常见误解:把'加入 P0 雷达'跟'完成源码追踪'混为一谈——前者是状态变化,后者是工程产出。"
            }
        ]
    },
    {
        "out_dir": r"C:\Git-repo-my\GameDevVault\Routine\05-技术雷达\Weekly-Log\W29-2026-07-19",
        "basename": "W29-周复盘",
        "title": "W29 周复盘(2026-07-13 ~ 2026-07-19)",
        "subtitle": "W29 兑现率 30% → 70% | 6 文件 / 63KB 产出",
        "source_md": "W29-周复盘.md",
        "drag": [
            {
                "sentence": "W29 产出 6 文件,核心是 VSM {0} 行 + Nanite {1} 行 + Mac 平台 {2} anchor。",
                "answers": ["470", "340", "5"],
                "pool": ["470", "600", "340", "800", "5", "3"],
                "per_slot_analysis": [
                    "VSM 源码追踪 470 行,目标 ≥ 600 行,完成 78%",
                    "Nanite 源码追踪 340 行,W29 份额,目标 ≥ 800 行(W29/W30 两周)",
                    "Mac 平台 vault 立 5 个 anchor,每个 anchor 待 W30 续写"
                ]
            }
        ],
        "single": [
            {
                "question": "W29 推给用户(必须本人)的工作包括?",
                "options": [
                    "A. VSM 源码追踪",
                    "B. Nanite 源码追踪",
                    "C. Hunyuan3D 接 API + 骨骼 demo",
                    "D. Mac 平台 vault 索引页"
                ],
                "correct": 2,
                "analysis": [
                    "❌ VSM 是我做的(W29 470/600 行)",
                    "❌ Nanite 是我做的(W29 340/800 行)",
                    "✅ Hunyuan3D 接 API + 骨骼 demo 需要用户本人跑(腾讯云注册 + UE 导入 + 骨骼 demo)",
                    "❌ Mac 平台索引页也是我做的"
                ]
            },
            {
                "question": "O3 Lumen 升'已掌握' 8/7 前完成概率?",
                "options": [
                    "A. 100%",
                    "B. 60%",
                    "C. 20%",
                    "D. 0%"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 100% 太乐观",
                    "✅ ~60%,取决于 W30 Mac 实测(渲染特性 × Metal RHI 兼容矩阵 + Lyra on Mac 跑通)",
                    "❌ 20% 太悲观,Lumen Surface Cache 源码已 57 KB + 5 篇配套,基础已好",
                    "❌ 0% 显然不对,这是 8/7 月度回顾的首选目标"
                ]
            }
        ],
        "multi": [
            {
                "question": "W29 完成的 3 项核心承诺是?(多选)",
                "options": [
                    "A. VSM 源码追踪起头(470/600 行)",
                    "B. Nanite 源码追踪起头(340/800 行)",
                    "C. Mac 平台 vault 索引页(4.1KB / 5 anchor)",
                    "D. Hunyuan3D API 集成",
                    "E. AI-Code-Assistant + UnrealMCP 联动测试"
                ],
                "correct": [0, 1, 2],
                "analysis": [
                    "✅ VSM 源码追踪起头 470/600 行,W29 完成 78%",
                    "✅ Nanite 源码追踪起头 340/800 行,W29 完成 43%(W30 续)",
                    "✅ Mac 平台 vault 索引页 4.1KB / 5 anchor,完成",
                    "❌ Hunyuan3D API 集成推 W30(需用户本人)",
                    "❌ AI-Code-Assistant + UnrealMCP 联动推 W30(需用户本人)"
                ]
            }
        ],
        "tf": [
            {
                "question": "W29 兑现率 30% → 70%(W28 兑现率 10%,W29 收尾补到 70%)。",
                "answer": True,
                "analysis": "✅ 正确理解:W28 兑现率 10%(硬数字)→ W29 收尾后 70%(6 文件 63KB 产出),W30 续写 + 推用户补 30% 剩余。\n\n❌ 常见误解:以为 100% 才是成功——Q3 OKR O3 看 8/7 升'已掌握',中间 70% 已经是显著进步。"
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


HTML_TEMPLATE = """
<!DOCTYPE html>
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
    """每个 entry 用自己的 out_dir(per-entry 覆盖默认)."""
    for entry in ENTRIES:
        base = entry["basename"]
        out_dir = entry.get("out_dir", DEFAULT_OUT_DIR)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, base + ".html")
        html = make_html(entry)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        size_kb = len(html.encode("utf-8")) / 1024
        n_total = len(entry["drag"]) + len(entry["single"]) + len(entry["multi"]) + len(entry["tf"])
        print(f"✓ {base}.html  ({size_kb:.1f} KB, {n_total} 题)  → {out_dir}")
    print(f"\n全部 {len(ENTRIES)} 个文件生成完成")


if __name__ == "__main__":
    main()
