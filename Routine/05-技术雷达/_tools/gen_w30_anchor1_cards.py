# -*- coding: utf-8 -*-
"""
生成 W30 Anchor 1(Mac Metal RHI 适配清单)配套 Q&A HTML 卡。
基于 gen_p1 / gen_w29 模板,但只 1 个 entry(单主题深度卡)。

用法:
    python gen_w30_anchor1_cards.py

输出:
    Routine/Mac-平台/Mac-Metal-RHI-适配清单.html
"""
import os
import json

OUT_DIR = r"C:\Git-repo-my\GameDevVault\Routine\Mac-平台"

# 1 个 W30 Anchor 1 条目的题目数据
ENTRIES = [
    {
        "basename": "Mac-Metal-RHI-适配清单",
        "title": "Mac Metal RHI 适配清单(Anchor 1)— W30",
        "subtitle": "W30 落盘 | 21 特性 × Mac 状态 + 4 NNE 后端 × 3 平台",
        "source_md": "Mac-Metal-RHI-适配清单.md",
        "drag": [
            {
                "sentence": "Mac NNE 4 个后端中,Mac 唯一可用的是 {0} 后端,性能约 GPU 的 {1}。",
                "answers": ["CPU", "1/10"],
                "pool": ["CPU", "TensorRT for RTX", "DirectML", "CUDA", "1/2", "1/5", "1/10", "1/100"],
                "per_slot_analysis": [
                    "Mac 没有 NVIDIA GPU,也没有 Windows,所以 TensorRT for RTX / DirectML 都不支持;CUDA 是 NVIDIA 专属 Linux/Windows 工具链,Mac 也不支持。CPU 是 Mac 唯一可用后端,慢但保证功能。",
                    "CPU 推理约 GPU 1/10 速度,但 Apple Silicon M2/M3 的 NEON 加速让 CPU 推理比预期好,不至于完全卡死。"
                ]
            },
            {
                "sentence": "Mac 上 VSM 关键调优 4 件套:MaxPhysicalPages={0} / AllowHZB={1} / Throttle={2} / MegaLights={3}。",
                "answers": ["1024", "0", "1", "0"],
                "pool": ["512", "1024", "2048", "0", "1", "0", "1", "0", "1"],
                "per_slot_analysis": [
                    "MaxPhysicalPages 从默认 2048 减半到 1024,避免 Apple Silicon GPU atomic 争用。",
                    "AllowHZB=0 是 HZB 在 Metal 上偶尔 hang 的 workaround,5.4+ 修复。",
                    "Throttle=1 让 GPU 自适应,避免 frame 抖动。",
                    "MegaLights=0 是 5.4 之前 threadgroup 不兼容的 workaround,5.4+ 默认开。"
                ]
            }
        ],
        "single": [
            {
                "question": "Mac 上 Lumen 调优必须开的 3 个 CVar 是?",
                "options": [
                    "A. r.Lumen.Enable / r.Lumen.Trace / r.Lumen.Cache",
                    "B. r.Lumen.DiffuseIndirect.Allow / r.Lumen.FinalGather.Allow / r.Lumen.SurfaceCache.Allow",
                    "C. r.Lumen.On / r.Lumen.Off / r.Lumen.Debug",
                    "D. r.Lumen.GI / r.Lumen.Reflection / r.Lumen.SkyLight"
                ],
                "correct": 1,
                "analysis": [
                    "❌ Lumen 没有这些 CVar,Enable/Trace/Cache 是猜的命名",
                    "✅ 3 件套 = DiffuseIndirect.Allow + FinalGather.Allow + SurfaceCache.Allow,全部默认 1,Mac 上无需改,跟 DX12 行为一致",
                    "❌ Lumen 没有 On/Off/Debug 这种开关(那是 RHI 的概念)",
                    "❌ Lumen.GI / Reflection / SkyLight 不是标准 CVar 名"
                ]
            },
            {
                "question": "Lumen 反射 tier L1 (SSR) 在 Mac 上的行为是?",
                "options": [
                    "A. 跟 DX12 性能完全一致",
                    "B. 比 DX12 慢约 20%(Apple GPU 算力差异)",
                    "C. 完全不支持",
                    "D. 比 DX12 快 2 倍"
                ],
                "correct": 1,
                "analysis": [
                    "❌ Metal RHI overhead + Apple GPU 算力差异,Mac 上 SSR 不可能跟 DX12 完全一致",
                    "✅ L1 SSR 在 Mac 上比 DX12 慢约 20%,这是 GPU 算力差异,不是 bug",
                    "❌ L1 在 Mac 上完整支持",
                    "❌ Apple GPU 不会比 DX12 GPU 快 2 倍"
                ]
            },
            {
                "question": "NNE TensorRT for RTX 后端在 Mac 上的状态是?",
                "options": [
                    "A. ✅ 完整支持(Apple Silicon 优化)",
                    "B. ⚠️ 部分支持(需要 CVar 调优)",
                    "C. ❌ 不支持(仅 NVIDIA RTX 显卡可用)",
                    "D. ✅ 完整支持但需 fallback 到 CPU"
                ],
                "correct": 2,
                "analysis": [
                    "❌ TensorRT for RTX 是 NVIDIA 专属,Mac 没有 NVIDIA GPU",
                    "❌ 不存在部分支持,要么完整要么不支持",
                    "✅ TensorRT for RTX 仅 NVIDIA RTX 显卡可用,Mac 没有 NVIDIA GPU → 完全不支持",
                    "❌ Mac 不会'完整支持但 fallback',要么支持要么不支持"
                ]
            }
        ],
        "multi": [
            {
                "question": "Mac 上 ⚠️ 部分(需要 CVar 调优 / 有已知问题)的特性是?(多选)",
                "options": [
                    "A. Lumen 反射(SSR + Capture)",
                    "B. Nanite Page Streaming",
                    "C. VSM 物理页池 + LRU",
                    "D. VSM BC6H 压缩",
                    "E. Substrate 材质系统",
                    "F. MegaLights(5.3)"
                ],
                "correct": [0, 1, 2, 3, 5],
                "analysis": [
                    "✅ Lumen 反射 ⚠️:L1/L2 行为跟 DX12 略不同,L3 偶尔闪烁",
                    "✅ Nanite Page Streaming ⚠️:unified memory thrashing 风险",
                    "✅ VSM 物理页池 + LRU ⚠️:atomic 行为差异,需 MaxPhysicalPages 减半",
                    "✅ VSM BC6H 压缩 ⚠️:M1 早期不支持,5.4+ fallback RGBA16F",
                    "❌ Substrate 在 Mac 上是 ✅ 完整支持,无已知问题",
                    "✅ MegaLights(5.3)⚠️:threadgroup 不兼容,5.4+ 修复"
                ]
            },
            {
                "question": "NNE 在 Mac 上不可用的后端是?(多选)",
                "options": [
                    "A. TensorRT for RTX",
                    "B. DirectML",
                    "C. CUDA",
                    "D. CPU",
                    "E. Apple Neural Engine(ANE)"
                ],
                "correct": [0, 1, 2],
                "analysis": [
                    "✅ TensorRT for RTX 是 NVIDIA 专属,Mac 没有 NVIDIA GPU",
                    "✅ DirectML 是 Windows-only,Mac 不支持",
                    "✅ CUDA 是 NVIDIA 专属,Mac 不支持(虽然 Mac Pro 2018 之前有 NVIDIA eGPU 但已被淘汰)",
                    "❌ CPU 在 Mac 上是唯一可用后端,不是'不可用'",
                    "❌ Apple Neural Engine(ANE)目前不在 UE NNE 后端列表里,UE 还没接 ANE,理论未来可加"
                ]
            }
        ],
        "tf": [
            {
                "question": "Lumen 在 UE 5.4+ Mac Metal 上完整支持,无已知问题。",
                "answer": True,
                "analysis": "✅ 正确理解:Lumen GI + Final Gather + Surface Cache 在 Mac 上都是 ✅ 完整,SW Ray Tracing 优先路径反而比 DX12 性能好(Apple GPU 优化)。\n\n❌ 常见误解:以为 Mac 上 Lumen 有大坑——其实 Mac 上 Lumen 的主要 CVar 跟 DX12 一样,只有 L1 SSR 慢 20% 这种小问题。"
            },
            {
                "question": "NNE TensorRT for RTX 后端在 Mac 上可用,只是需要 CVar 调优。",
                "answer": False,
                "analysis": "✅ 正确理解:TensorRT for RTX 是 NVIDIA 专属后端,只支持 NVIDIA RTX 显卡。Mac 没有 NVIDIA GPU,所以这个后端根本不可用,不是调优问题。\n\n❌ 常见误解:以为 UE 的 NNE 后端都能跨平台——其实 4 个后端中只有 CPU 是真正跨平台,其他 3 个都有平台限制。"
            },
            {
                "question": "Substrate 材质系统在 Mac 上完整支持,Apple GPU 优化好(因为 Substrate 是 tile-based,Apple GPU 也是 tile-based)。",
                "answer": True,
                "analysis": "✅ 正确理解:Substrate 设计哲学是 tile-based closure,Apple GPU 也是 tile-based 架构,两者天然契合,无已知兼容问题。\n\n❌ 常见误解:以为 Substrate 是 Windows-only——其实从 5.3+ 完整支持 Mac,Apple GPU 反而是 Substrate 跑得最好的平台之一。"
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
