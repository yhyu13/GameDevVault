#!/usr/bin/env python3
"""Generate 9 shader case study QA card decks (HTML) from MD files.

Each card has 4 question types: 拖拽填空 / 单选 / 多选 / 判断题
Plus overview panel + scoring + progress + cross-type navigation.
"""
import os
import json

# Shared CSS+JS framework (extracted from DLSS-FSR-AI超分辨率.html)
# Use {TOKEN} placeholders for substitution (no .format() braces conflict)
SHARED_FRAMEWORK = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{TITLE}</title>
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
  <h1>{HEADER_TITLE}</h1>
  <p>{HEADER_SUBTITLE}</p>
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

<a class="source-link" href="./{MD_BASENAME}">📄 查看原始笔记(MD)</a>

</div>

<script>
// 题目数据
{DRAG_JSON}
{SINGLE_JSON}
{MULTI_JSON}
{TF_JSON}

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

function renderDrag(def) {
  const container = document.getElementById('q-container');
  const parts = def.sentence.split(/(\{\d+\})/g);
  let slotsHTML = '';
  let slotIdx = 0;
  for (const p of parts) {
    const m = p.match(/^\{(\d+)\}$/);
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


# Question definitions per MD - same as before
CARDS = {
    "W1/神经材质-NeuralPBR": {
        "title": "W1 神经材质 NeuralPBR — 互动式面试卡牌",
        "header_title": "W1 神经材质 NeuralPBR — 图像预测 PBR 4 通道",
        "header_subtitle": "AI 神经材质 | U-Net 离线训练 + 实时推理 | day-job 主线 1",
        "drag_questions": [
            {
                "sentence": "NeuralPBR 输入 {0} 张 base color 图,网络推理输出 {1} 张 PBR map。",
                "answers": ["1", "4"],
                "pool": ["1", "4", "8", "16", "64"],
                "per_slot_analysis": [
                    "输入是单张 base color 图(典型 1024×1024),不需要多视角。",
                    "输出 4 张 PBR map: BaseColor / Metallic / Roughness / Normal。"
                ]
            },
            {
                "sentence": "U-Net 4 个 downsample level: 1024 → 512 → {0} → 128 → {1}",
                "answers": ["256", "64"],
                "pool": ["256", "128", "64", "32", "512"],
                "per_slot_analysis": [
                    "1024 → 512 → 256 → 128 → 64,每次下采样 ×2,4 个 level 后到 64×64。",
                    "最后一层 64×64 是 bottleneck 起点,之后上采样回到 1024×1024 输出。"
                ]
            },
            {
                "sentence": "Frequency encoding: F(2x) = [sin({0}), cos({1})] 把低维输入映射到高频特征空间。",
                "answers": ["2^k * x", "2^k * x"],
                "pool": ["2^k * x", "x^2", "1/x", "log(x)", "x * pi"],
                "per_slot_analysis": [
                    "NeRF 风格 frequency encoding, F(2x) = [sin(2^k · x), cos(2^k · x)],k = 0..L-1。",
                    "第二个 slot 同样是 2^k · x,因为 cos 项跟 sin 项用同一个频率,只是相位差 π/2。"
                ]
            }
        ],
        "single_questions": [
            {
                "question": "NeuralPBR 的 Metallic 和 Roughness 通道为什么是 L1 loss 难收敛的?",
                "options": [
                    "A. 因为它们是高维向量",
                    "B. 因为这两个通道没有明显视觉线索,网络需要学隐式关联",
                    "C. 因为 GPU 不支持单通道纹理",
                    "D. 因为训练数据都是黑的"
                ],
                "correct": 1,
                "analysis": [
                    "❌ Metallic / Roughness 都是单通道 float,不是高维向量。",
                    "✅ 这两个通道在图像中没有明显视觉线索,网络需要学隐式关联(高光位置 → metallic,边缘密度 → roughness),L1 loss 难收敛。",
                    "❌ GPU 完全支持单通道 R8 纹理,跟 L1 loss 无关。",
                    "❌ 训练数据正常,问题在视觉线索弱,不在数据。"
                ]
            },
            {
                "question": "NeuralPBR 输出 4 张 PBR map 的总内存占用是?",
                "options": [
                    "A. 4 KB",
                    "B. 4 MB",
                    "C. 16 MB",
                    "D. 64 MB"
                ],
                "correct": 2,
                "analysis": [
                    "❌ 4 KB 不够存 4 张 2K 纹理。",
                    "❌ 4 MB 只够 base color 一张。",
                    "✅ 4 张 2048×2048 PBR map 总约 16-28 MB;1024×1024 总约 7 MB,典型 ~16 MB。",
                    "❌ 64 MB 过大,除非 4K + 多材质 latent。"
                ]
            },
            {
                "question": "U-Net skip connection 在 NeuralPBR 中主要作用是?",
                "options": [
                    "A. 减少网络参数",
                    "B. 让 decoder 直接拿到 encoder 的高频细节,避免下采样丢失",
                    "C. 加速推理",
                    "D. 兼容更多 GPU"
                ],
                "correct": 1,
                "analysis": [
                    "❌ skip connection 实际上增加参数(concat 通道)。",
                    "✅ 让 decoder 直接拿到 encoder 对应层的高频细节,避免下采样丢失(纸张纹理、毛孔等)。这是 U-Net 优于纯 encoder-decoder 的核心。",
                    "❌ skip connection 略增计算量,不加速推理。",
                    "❌ 跟 GPU 兼容性无关。"
                ]
            },
            {
                "question": "NeuralPBR 离线训练数据如何收集?",
                "options": [
                    "A. 随机生成 noise 图",
                    "B. 用 UE5 商城 100+ 高细节材质,导出 base color + 4 PBR ground truth",
                    "C. 让用户手画 PBR",
                    "D. 用 PS 滤镜处理"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 随机噪声无法学到真实材质特征。",
                    "✅ 收集 UE5 商城 100+ 高细节材质,每个材质导出 base + 4 PBR ground truth;50 角度采样 → 5000 训练样本。",
                    "❌ 用户手画不适合 SFT,只适合监督微调少量样本。",
                    "❌ PS 滤镜无法生成 ground truth PBR 参数。"
                ]
            }
        ],
        "multi_questions": [
            {
                "question": "NeuralPBR 5 档性能分级包含哪些?(多选)",
                "options": [
                    "A. 极简 (离线烘焙,shader 用结果)",
                    "B. 标准 (实时推理 1024×1024)",
                    "C. 高配 (实时推理 2048×2048)",
                    "D. 极限 (实时推理 + 4K + latent blending)",
                    "E. Debug (输出 4 张中间结果)",
                    "F. 移动端专用模式"
                ],
                "correct": [0, 1, 2, 3, 4],
                "analysis": [
                    "✅ 极简档是离线烘焙,运行时 0ms 开销,适合 mobile / 静态资产。",
                    "✅ 标准档 1024×1024 实时推理,~3.0ms,PC 中端。",
                    "✅ 高配档 2048×2048,~8.0ms,PC 高端 / 过场。",
                    "✅ 极限档 4K + 多材质 latent blending,~15ms,截图级。",
                    "✅ Debug 档输出 4 张中间 PBR,+5ms,调参用。",
                    "❌ NeuralPBR 不支持移动端实时推理,移动端只能用极简档(离线烘焙)。"
                ]
            }
        ],
        "tf_questions": [
            {
                "question": "NeuralPBR 训练后的模型可以直接在 UE5 Material Editor 里以 Material Function 形式调用。",
                "answer": True,
                "analysis": "✅ 正确理解:UE5.4+ 支持把神经网络模型作为 Material Function 调用,NeuralPBR 通过 Custom HLSL Node + 网络权重 StructuredBuffer 集成。\n\n❌ 常见误解:以为只能离线用——实际上 UE 5.4+ 的 NNE (Neural Network Engine) 支持运行时推理。"
            },
            {
                "question": "NeuralPBR 可以预测任何材质,包括训练集没见过的金属丝、玻璃。",
                "answer": False,
                "analysis": "✅ 正确理解:NeuralPBR 在训练集覆盖不到的特殊材质(金属丝/玻璃)预测质量差,因为网络学的是训练集分布。\n\n❌ 常见误解:以为神经网络是'万能的'——它只能拟合训练分布,out-of-distribution 材质需要 fine-tune 或重新训练。"
            },
            {
                "question": "NeuralPBR 的输出是静态 PBR map,不能预测 vertex animation 或风动效果。",
                "answer": True,
                "analysis": "✅ 正确理解:NeuralPBR 输出 4 张 PBR 贴图(BaseColor/Metallic/Roughness/Normal),都是静态纹理,无法编码 vertex animation / wind 等动态效果。\n\n❌ 常见误解:以为神经材质可以替代所有材质功能——它只能替代 PBR 参数化,动态效果需要 vertex shader 或 Niagara 系统配合。"
            },
            {
                "question": "NeuralPBR 必须用 U-Net 50+ 层才能输出高质量 PBR map。",
                "answer": False,
                "analysis": "✅ 正确理解:实际工程可用简化版 4 层 U-Net (base channels=32),输出质量已接近完整版,推理开销 1/10。\n\n❌ 常见误解:以为网络越深越好——4 层 U-Net 在 5000 训练样本下已经能学到 80% 细节,继续加深边际收益递减,推理开销线性增加。"
            }
        ]
    },

    "W2/神经BRDF-NeuralGGX": {
        "title": "W2 神经 BRDF NeuralGGX — 互动式面试卡牌",
        "header_title": "W2 神经 BRDF NeuralGGX — MLP 拟合 GGX/Disney",
        "header_subtitle": "AI 神经 BRDF | 5→64→64→64→3 MLP + 离线训练 | day-job 主线 2",
        "drag_questions": [
            {
                "sentence": "Neural BRDF 输入 5 个参数: {0}, NdotV, NdotL, {1}, Metallic。",
                "answers": ["NdotH", "Roughness"],
                "pool": ["NdotH", "Roughness", "VdotH", "BaseColor", "F0"],
                "per_slot_analysis": [
                    "NdotH 是 cos angle between normal and half vector,Cook-Torrance 镜面反射核心。",
                    "Roughness [0, 1] 控制 BRDF 形状,GGX 中是 alpha 平方根。"
                ]
            },
            {
                "sentence": "MLP 结构: 5 → {0} → {1} → 64 → 3 (Sigmoid 输出 BRDF RGB)",
                "answers": ["64", "64"],
                "pool": ["64", "32", "128", "256", "16"],
                "per_slot_analysis": [
                    "第一层 hidden 是 64 dim,ReLU 激活,扩张 5→64 维度。",
                    "第二层同样 64 dim,加深网络深度但保持维度不变,3 hidden layer 共 5→64→64→64→3。"
                ]
            },
            {
                "sentence": "训练数据: 1M 随机样本,每样本 (NdotH, NdotV, NdotL, {0}, {1}, baseColor) → GGX 公式输出",
                "answers": ["Roughness", "Metallic"],
                "pool": ["Roughness", "Metallic", "F0", "IOR", "Anisotropy"],
                "per_slot_analysis": [
                    "Roughness 是 BRDF 形状的关键参数,训练数据必须覆盖 [0, 1] 全范围。",
                    "Metallic 控制 F0 (specular at normal incidence) 的 lerp 因子,也是必采样的 5 个参数之一。"
                ]
            }
        ],
        "single_questions": [
            {
                "question": "NeuralGGX 相比传统 GGX 的核心优势是?",
                "options": [
                    "A. 更快(因为 GPU 硬件加速)",
                    "B. 可以表示任意 BRDF 形状(不限于 GGX 公式)",
                    "C. 不需要任何 uniform",
                    "D. 完全免费"
                ],
                "correct": 1,
                "analysis": [
                    "❌ NeuralGGX 推理开销 0.3ms/pixel/light,实际比 GGX 慢。",
                    "✅ MLP 可以表示任意 BRDF 形状,只要训练数据覆盖——可以学多层涂漆、各向异性、复杂皮肤等 GGX 难以表达的特殊 BRDF。",
                    "❌ NeuralGGX 仍需要 roughness / metallic 等输入 uniform。",
                    "❌ 训练 1 个模型需要 1h+ GPU,不是免费的。"
                ]
            },
            {
                "question": "NeuralGGX 训练数据 ground truth 如何获取?",
                "options": [
                    "A. 真实物体拍摄",
                    "B. Path tracer 离线渲染 1024 spp",
                    "C. 用传统 GGX 公式生成",
                    "D. 随机 noise"
                ],
                "correct": 2,
                "analysis": [
                    "❌ 真实拍摄无法获取 (NdotH, NdotV, NdotL, roughness, metallic) → BRDF 的精确映射。",
                    "❌ Path tracer 1024 spp 适合给 NRC (NeRF GI) 用,不适合 NeuralGGX。",
                    "✅ 用传统 GGX 公式生成 1M 随机样本,作为神经网络的 ground truth;这是知识蒸馏思路。",
                    "❌ 随机 noise 无法学到 BRDF 关系。"
                ]
            },
            {
                "question": "NeuralGGX 推理失败时必须做什么?",
                "options": [
                    "A. 让画面空白",
                    "B. 自动 fallback 到传统 GGX 公式",
                    "C. 重新训练",
                    "D. 关闭渲染"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 画面空白会让产品失败。",
                    "✅ 必须自动 fallback 到传统 GGX 公式,这是工程基本要求:`r.NeuralBRDF.FallbackToGGX 1`。",
                    "❌ 重新训练太慢,实时推理不能等。",
                    "❌ 关闭渲染完全不可接受。"
                ]
            },
            {
                "question": "NeuralGGX 在多光源场景下开销?",
                "options": [
                    "A. 固定开销,跟光源数无关",
                    "B. 每光源 0.3ms,10 光源场景 3ms",
                    "C. 完全免费",
                    "D. 比传统 GGX 慢 10x"
                ],
                "correct": 1,
                "analysis": [
                    "❌ MLP forward 开销线性,跟光源数正相关。",
                    "✅ 每像素每光源调一次 MLP forward,~0.3ms/light;10 光源场景每像素 3ms。",
                    "❌ 神经网络推理不可能免费。",
                    "❌ 实际慢 2-3x,不是 10x;10x 是 SM5 mobile 情况。"
                ]
            }
        ],
        "multi_questions": [
            {
                "question": "NeuralGGX 的 6 个已知问题与限制包含哪些?(多选)",
                "options": [
                    "A. 不支持 mobile (需 SM6+ MLP 推理)",
                    "B. 每帧每像素每光源调用,多光源开销线性",
                    "C. 训练数据是 GGX ground truth,无法表示 GGX 之外的特殊 BRDF",
                    "D. Latent 调参需要重新推理,延迟 1-3 帧",
                    "E. 能量守恒需手动 normalize",
                    "F. 仅支持 PC,不支持主机"
                ],
                "correct": [0, 1, 2, 3, 4],
                "analysis": [
                    "✅ 不支持 mobile,SM5 fallback 到传统 GGX。",
                    "✅ 多光源场景开销线性增加。",
                    "✅ 训练数据是 GGX ground truth,无法学 GGX 之外的物理 BRDF。",
                    "✅ Latent-conditioned 版本换 BRDF 需要重新推理。",
                    "✅ 神经网络输出可能不满足能量守恒。",
                    "❌ 主机 SM6 完全支持(PS5/Xbox Series)。"
                ]
            }
        ],
        "tf_questions": [
            {
                "question": "NeuralGGX 训练完成后不需要重新训练,可以直接部署到任何场景。",
                "answer": False,
                "analysis": "✅ 正确理解:NeuralGGX 训练数据是 (NdotH, NdotV, NdotL, roughness, metallic, baseColor) → GGX 输出,场景无关——但材质变体(latent 版本)需要重新训练。\n\n❌ 常见误解:以为训练一次就万事大吉——non-latent 版本确实一次训练适用所有,但支持运行时换 BRDF 形状的 latent 版本需要重新训练。"
            },
            {
                "question": "NeuralGGX 输入编码了直接光照信息,可以替代 Screen Probe 处理间接光。",
                "answer": False,
                "analysis": "✅ 正确理解:NeuralGGX 输入只有 (NdotH, NdotV, NdotL, roughness, metallic),只编码直接光照 BRDF;间接光(specular / GI)必须叠加 Screen Probe / Surface Cache。\n\n❌ 常见误解:以为 NeuralGGX 是 GI 解决方案——它只替代单光源 BRDF 评估。"
            },
            {
                "question": "NeuralGGX 输出的能量可能不守恒,需要后处理 normalize。",
                "answer": True,
                "analysis": "✅ 正确理解:MLP 输出可能 ∫BRDF dΩ > 1(过亮)或 < 1(过暗),不满足物理约束;需要在 shader 末尾做能量归一化 `BRDF /= max(integral, 1.0)`。\n\n❌ 常见误解:以为 MLP 自动满足物理约束——训练 loss 只惩罚 L1/MSE,不显式保证能量守恒。"
            },
            {
                "question": "NeuralGGX 训练开销是 1M 样本 × 50 epoch,1 个 RTX 4090 约 1 小时完成。",
                "answer": True,
                "analysis": "✅ 正确理解:1M 随机样本,PyTorch Adam optimizer,50 epoch,1 个 RTX 4090 约 1 小时完成。\n\n❌ 常见误解:以为神经网络训练都是几天几夜——对这种小规模 MLP,1 小时就能训完。"
            }
        ]
    },

    "W3/Lumen-反射降级": {
        "title": "W3 Lumen 反射降级 + AI 加速 — 互动式面试卡牌",
        "header_title": "W3 Lumen 反射降级 + AI 加速",
        "header_subtitle": "UE 硬技术 + AI | 4 档降级 + L1/L2/L3 Probe Densification",
        "drag_questions": [
            {
                "sentence": "Lumen 反射四档降级链路: T1 {0} → T2 {1} → T3 Surface Cache → T4 HW RT",
                "answers": ["SSR", "Screen Probe"],
                "pool": ["SSR", "Screen Probe", "Reflection Capture", "EnvMap", "Cubemap"],
                "per_slot_analysis": [
                    "T1 SSR (Screen Space Reflection) 是最便宜的反射,只在屏幕空间内 trace。",
                    "T2 Screen Probe 把屏幕空间采样点落到 probe atlas,解决屏幕外反射。"
                ]
            },
            {
                "sentence": "L1 AI 加速: 256 probe → {0} probe + MLP 补全,VRAM 节省 {1}",
                "answers": ["64", "4x"],
                "pool": ["64", "256", "1024", "4x", "8x", "16x"],
                "per_slot_analysis": [
                    "256 probe 压缩到 64 probe,再用 MLP 学补全,视觉效果等价。",
                    "Probe atlas VRAM 4× 节省,从 8MB 降到 2MB。"
                ]
            },
            {
                "sentence": "L3 NeRF Reflection Cache: 输入 (position, direction, scene_scale) → {0} dim latent → MLP → {1}",
                "answers": ["256", "RGB radiance"],
                "pool": ["256", "64", "128", "RGB radiance", "BRDF", "depth"],
                "per_slot_analysis": [
                    "NeRF 风格用 hash grid 编码到 256 dim latent,捕获场景局部特征。",
                    "最终 MLP 输出 RGB radiance,作为反射 lookup 结果。"
                ]
            }
        ],
        "single_questions": [
            {
                "question": "Lumen 反射降级链路里最便宜的是哪一档?",
                "options": [
                    "A. T1 SSR",
                    "B. T2 Screen Probe",
                    "C. T3 Surface Cache",
                    "D. T4 HW RT"
                ],
                "correct": 0,
                "analysis": [
                    "✅ T1 SSR 仅在屏幕空间 trace,无离屏存储,无 compute 开销,最便宜。",
                    "❌ T2 Screen Probe 需要 256 probe atlas + 8 step cone trace。",
                    "❌ T3 Surface Cache 需要 50MB voxel atlas。",
                    "❌ T4 HW RT 需要 RTX 硬件加速,最贵。"
                ]
            },
            {
                "question": "Screen Probe '黑洞' 现象的根本原因是?",
                "options": [
                    "A. Probe 太多",
                    "B. Probe 落在物体内部 / 阴影区",
                    "C. 屏幕分辨率太低",
                    "D. GPU 显存不够"
                ],
                "correct": 1,
                "analysis": [
                    "❌ Probe 多反而减少黑洞。",
                    "✅ Probe 落在物体内部 / 阴影区时,采样到的是 invalid 数据,反射呈现黑斑;需要 probe 重要性采样 + dithering。",
                    "❌ 屏幕分辨率低会让反射更糊,但不直接导致黑洞。",
                    "❌ 显存不够是另一个问题(VRAM 爆掉),跟黑洞现象不同。"
                ]
            },
            {
                "question": "Surface Cache 在大场景下的 VRAM 占用典型是多少?",
                "options": [
                    "A. 5 MB",
                    "B. 50 MB",
                    "C. 200 MB+",
                    "D. 2 GB"
                ],
                "correct": 2,
                "analysis": [
                    "❌ 5 MB 只够小场景 voxel atlas。",
                    "❌ 50 MB 是典型室内场景。",
                    "✅ 大场景(开放世界)轻易吃 200MB+ 显存。",
                    "❌ 2 GB 是极端情况,不典型。"
                ]
            },
            {
                "question": "L3 NeRF Reflection Cache 相比 Surface Cache 的核心优势是?",
                "options": [
                    "A. 速度更快",
                    "B. VRAM 从 50MB 降到 5MB,多次弹射隐式编码",
                    "C. 支持移动端",
                    "D. 不需要 GPU"
                ],
                "correct": 1,
                "analysis": [
                    "❌ NeRF 推理开销 1ms+,实际比 Surface Cache 慢。",
                    "✅ VRAM 从 50MB 降到 5MB (MLP 权重),多次弹射隐式编码在 MLP 里。",
                    "❌ NeRF 推理需要 SM6+,不支持移动端。",
                    "❌ 仍需要 GPU 推理,只是不需要 GPU 做 voxel 存储。"
                ]
            }
        ],
        "multi_questions": [
            {
                "question": "Lumen 反射降级的 6 个已知问题包含哪些?(多选)",
                "options": [
                    "A. Screen Probe '黑洞' 现象",
                    "B. Surface Cache 内存爆炸",
                    "C. 多次反射 (Mirror) 不稳定",
                    "D. HW RT 与软件 RT 切换闪",
                    "E. 屏幕空间与 Surface Cache 边界硬切",
                    "F. 粗糙表面噪点"
                ],
                "correct": [0, 1, 2, 3, 4, 5],
                "analysis": [
                    "✅ '黑洞' 是 Probe 落在 invalid 区域,反射黑斑。",
                    "✅ 大场景 Surface Cache voxel atlas 200MB+,VRAM 爆。",
                    "✅ 镜面球 / 玻璃幕墙多次反射闪烁。",
                    "✅ 进 / 出 RTX 区域画面跳变。",
                    "✅ 屏幕内 SSR、屏幕外 Probe 边界'嘎嘣'切。",
                    "✅ Rough > 0.6 时 probe cone trace 步数不够,椒盐噪点。"
                ]
            }
        ],
        "tf_questions": [
            {
                "question": "反射降级链路可以关闭 Lumen 直接用 cubemap,不影响 80% 反射需求。",
                "answer": True,
                "analysis": "✅ 正确理解:Lumen 是豪华版,只用 T1 SSR + cubemap fallback 也能解决 80% 反射需求;性能预算紧的项目可以走这条轻量级路径。\n\n❌ 常见误解:以为 Lumen 必须全套上——其实它是分层降级,可以根据项目预算选择档位。"
            },
            {
                "question": "Surface Cache 静态场景只需 bake 一次,后续永久使用。",
                "answer": True,
                "analysis": "✅ 正确理解:Surface Cache 是离线 voxel 化 + lighting bake,静态场景光照不变时,Surface Cache 内容永久有效。\n\n❌ 常见误解:以为 Surface Cache 每帧重算——它本质是离线烘焙的 3D texture,运行时只读。"
            },
            {
                "question": "屏幕空间反射 SSR 是 Lumen 的 T4 (高端档)。",
                "answer": False,
                "analysis": "✅ 正确理解:SSR 是 T1 (最便宜档),只在屏幕空间内 trace;T4 是 HW RT (硬件加速光线追踪)。\n\n❌ 常见误解:把 SSR 和 HW RT 顺序搞反——SSR 反而是反射链路的最低端。"
            },
            {
                "question": "Screen Probe 分布越密越好,可以无限制增加。",
                "answer": False,
                "analysis": "✅ 正确理解:Probe 数量受 VRAM 和 GPU cycle 双重约束,典型 256 个;增加 probe 数量线性增加 atlas 大小和 cone trace 开销。\n\n❌ 常见误解:以为 probe 越多越好——256 是经验值,过多反而性能崩,过少会出现黑洞。"
            }
        ]
    },

    "W4/Lumen-GI-漫反射": {
        "title": "W4 Lumen GI 漫反射 + AI 加速 — 互动式面试卡牌",
        "header_title": "W4 Lumen GI 漫反射 + AI 加速",
        "header_subtitle": "UE 硬技术 + AI | Surface Cache + VCT + L3 NRC 替代",
        "drag_questions": [
            {
                "sentence": "GI 漫反射链路: {0} + Voxel Cone Tracing + Final Gather",
                "answers": ["Surface Cache", "Final Gather"],
                "pool": ["Surface Cache", "Final Gather", "SkyLight", "Reflection Capture", "Screen Probe"],
                "per_slot_analysis": [
                    "Surface Cache 是离线烘焙的 3D voxel atlas,存储每个 voxel 的 radiance。",
                    "Final Gather 在屏幕空间对 probe 做 k-NN 采样,加权插值出 GI。"
                ]
            },
            {
                "sentence": "L3 AI 替代方案: {0} 替代 Surface Cache,VRAM 从 50MB 降到 {1}",
                "answers": ["NRC", "150 KB"],
                "pool": ["NRC", "SVGF", "NRD", "150 KB", "5 MB", "50 MB"],
                "per_slot_analysis": [
                    "NRC (Neural Radiance Cache) 是 NeRF 风格的神经网络,替代 Surface Cache 离线存储。",
                    "VRAM 从 50 MB 降到 150 KB,只需 MLP 权重。"
                ]
            },
            {
                "sentence": "NRC MLP 结构: 6 input → 8 hidden layer × {0} dim → {1} output",
                "answers": ["64", "3"],
                "pool": ["64", "32", "128", "256", "3", "6"],
                "per_slot_analysis": [
                    "Meta 论文用 8 hidden layer × 64 dim,这是 NRC 的标准配置。",
                    "Output 是 3 dim (RGB radiance),Sigmoid 激活确保 [0, 1] 范围。"
                ]
            }
        ],
        "single_questions": [
            {
                "question": "Lumen GI 户外 vs 室内的关键参数差异是?",
                "options": [
                    "A. 户外用更大的 voxel,室内用更小",
                    "B. 户外用 Sky Light + Final Gather,室内用 VCT 兜底",
                    "C. 户外开 Lumen,室内关闭",
                    "D. 没差异"
                ],
                "correct": 1,
                "analysis": [
                    "❌ voxel size 应该跟场景尺度匹配,不是按室内外区分。",
                    "✅ 户外主光来自 Sky Light,Final Gather 8 spp 足够;室内多次弹射重要,VCT 兜底不可缺。",
                    "❌ Lumen 在室内外都开,只是参数不同。",
                    "❌ 差异很大,户外单次 GI 够,室内需要多次弹射。"
                ]
            },
            {
                "question": "Voxel 太大的后果是?",
                "options": [
                    "A. 性能提升,精度不变",
                    "B. 漏光 (light leaks) / 错误遮挡",
                    "C. GPU 显存爆",
                    "D. 自动 fallback 到 HW RT"
                ],
                "correct": 1,
                "analysis": [
                    "❌ voxel 大精度会下降,不是'不变'。",
                    "✅ voxel 太大时,薄几何(墙、门)无法精确表示,导致漏光或错误遮挡。",
                    "❌ voxel 大反而显存小,不会爆。",
                    "❌ Lumen 不会自动 fallback 到 HW RT,需要手动启用。"
                ]
            },
            {
                "question": "NRC 替代 Surface Cache 的关键优势是?",
                "options": [
                    "A. 渲染速度更快",
                    "B. 多次弹射隐式编码,VRAM 从 50MB 降到 150KB",
                    "C. 支持所有平台",
                    "D. 不需要 GPU"
                ],
                "correct": 1,
                "analysis": [
                    "❌ NRC 推理开销 ~3ms,比 Surface Cache 慢。",
                    "✅ 多次弹射隐式编码在 MLP 权重里,不需要显式 Screen Probe;VRAM 从 50 MB 降到 150 KB,300x 节省。",
                    "❌ NRC 需要 SM6+,不支持 mobile。",
                    "❌ NRC 仍需 GPU 推理,只是不需要 voxel atlas 存储。"
                ]
            },
            {
                "question": "Final Gather k-NN 加速 (L1) 用什么方式减少 probe 数量?",
                "options": [
                    "A. 用 mipmap",
                    "B. 256 probe → 64 probe + MLP 补全",
                    "C. 完全取消 probe",
                    "D. 用更复杂的 cone trace"
                ],
                "correct": 1,
                "analysis": [
                    "❌ mipmap 用于纹理 LOD,不用于 probe 压缩。",
                    "✅ 256 probe 压到 64 probe,用 8→64→64→3 MLP 学补全,VRAM 节省 4x,视觉等价。",
                    "❌ 没有 probe 就没法做 k-NN。",
                    "❌ cone trace 是 probe 采样方式,跟减少 probe 数无关。"
                ]
            }
        ],
        "multi_questions": [
            {
                "question": "Lumen GI 调试调参包含哪些?(多选)",
                "options": [
                    "A. 先关掉 GI,看场景直接光对不对",
                    "B. 开 Final Gather only,probe 256,1 bounce",
                    "C. 调整 _ProbeSearchRadius",
                    "D. 室内场景开 VCT 兜底",
                    "E. 出现闪烁时开 temporal probe 累积",
                    "F. 性能不够时开 Half-res FG"
                ],
                "correct": [0, 1, 2, 3, 4, 5],
                "analysis": [
                    "✅ 先关掉 GI 排除基础渲染问题。",
                    "✅ 单开 Final Gather 验证 probe 分布够不够。",
                    "✅ _ProbeSearchRadius 从 200 调到 1000 看漏光。",
                    "✅ 室内场景 VCT 兜底不可缺。",
                    "✅ 闪烁用 temporal probe 累积。",
                    "✅ 性能紧张时开 Half-res FG + voxel size 25。"
                ]
            }
        ],
        "tf_questions": [
            {
                "question": "Lumen GI 漫反射支持间接高光 (indirect specular) 反射。",
                "answer": False,
                "analysis": "✅ 正确理解:Lumen GI 漫反射只处理漫反射间接光;indirect specular 反射走 Lumen 反射降级链路 (T1-T4)。\n\n❌ 常见误解:以为 Lumen GI = Lumen 反射——GI 是漫反射,反射走另一条路径。"
            },
            {
                "question": "Lumen GI 必须开 HW RT 才能工作。",
                "answer": False,
                "analysis": "✅ 正确理解:Lumen 默认走软件 RT (Screen Probe + Surface Cache + Final Gather + VCT),HW RT 是可选的 T4 加速,不必须。\n\n❌ 常见误解:以为 Lumen = HW RT——Lumen 设计上就是软件 RT 优先,让普通 GPU 也能跑。"
            },
            {
                "question": "NRC (Neural Radiance Cache) 需要 30+ 帧才能收敛。",
                "answer": True,
                "analysis": "✅ 正确理解:NRC 每帧 fine-tune MLP,前 30 帧 MLP 未收敛,GI 闪烁;这是 NRC 最大的工程问题,需要预训练 warmup。\n\n❌ 常见误解:以为神经网络一加载就能用——NRC 必须 fine-tune,初始 30 帧是过渡期。"
            },
            {
                "question": "Final Gather 是 screen space 操作,对每个 receiver 像素在屏幕空间内做 k-NN probe 采样。",
                "answer": True,
                "analysis": "✅ 正确理解:Final Gather 在屏幕空间对 256 个 probe 做 k-NN + 加权插值,得到每个 receiver 像素的 GI radiance;这是 screen space hack,屏幕外依赖 Surface Cache / VCT 兜底。\n\n❌ 常见误解:以为 Final Gather 直接采样世界空间 voxel——实际是 screen space probe 插值,不是直接读 voxel。"
            }
        ]
    },

    "W5/Nanite-材质管线": {
        "title": "W5 Nanite 材质管线 + AI 加速 — 互动式面试卡牌",
        "header_title": "W5 Nanite 材质管线 + AI 加速",
        "header_subtitle": "UE 硬技术 + AI | 5-bin 分类 + L1 Neural Material Eval",
        "drag_questions": [
            {
                "sentence": "Nanite 5-bin 分类: {0}, Voxel, {1}, Raster, FallbackRaster",
                "answers": ["TriangleShadingBin", "CurveShadingBin"],
                "pool": ["TriangleShadingBin", "CurveShadingBin", "VoxelShadingBin", "HairShadingBin", "PixelShadingBin"],
                "per_slot_analysis": [
                    "TriangleShadingBin 是主三角形 shading,最常用。",
                    "CurveShadingBin 是 Hair/Fur 曲线 shading,Nanite 5.5+ 支持。"
                ]
            },
            {
                "sentence": "L1 Neural Material Eval: 16 input → {0} hidden → 64 → 4 output (BaseColor + Roughness)",
                "answers": ["64", "3"],
                "pool": ["64", "32", "128", "256", "3", "4"],
                "per_slot_analysis": [
                    "Hidden 64 dim,ReLU 激活,MLP 第一层。",
                    "4 output = BaseColor.rgb (3 channel) + Roughness,Metallic 简化掉。"
                ]
            },
            {
                "sentence": "FNaniteShadingPipeline 用 {0} 128 位去重,Robin Hood hash map O(1) 查",
                "answers": ["CityHash", "Hash"],
                "pool": ["CityHash", "MD5", "SHA256", "Murmur", "CRC32"],
                "per_slot_analysis": [
                    "FNaniteShadingPipeline.GetPipelineHash 用 CityHash 128 位算 hash。",
                    "Robin Hood hash map O(1) 查找,稳定迭代。"
                ]
            }
        ],
        "single_questions": [
            {
                "question": "Nanite 5-bin 分类的设计初衷是?",
                "options": [
                    "A. 把同一材质的不同 shading 路径拆出来 (Triangle / Voxel / Curve 等)",
                    "B. 按颜色分 bin",
                    "C. 按 mesh 大小分 bin",
                    "D. 随机分 bin 平衡负载"
                ],
                "correct": 0,
                "analysis": [
                    "✅ 5-bin 不是简单的'主材质',是把同一种材质的不同 shading 路径拆出来——主三角形、体素 Lumen GI 捕获、曲线 Hair/Fur、Raster 兜底。",
                    "❌ bin 不按颜色分,按 shading 路径分。",
                    "❌ bin 不按 mesh 大小分,mesh 大小决定 cluster 层级,跟 bin 无关。",
                    "❌ bin 是显式分类,不是随机。"
                ]
            },
            {
                "question": "Persistent Material Buffer 每个 triangle 占多少 bytes?",
                "options": [
                    "A. 4 bytes",
                    "B. 16 bytes",
                    "C. 64 bytes",
                    "D. 256 bytes"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 4 bytes 只够 1 个 uint32,放不下 5 个 16-bit bin ID。",
                    "✅ 16 bytes = 4 × uint32,对应 FPacked 的 4 个 Data 字段,内含 5 个 16-bit bin ID。",
                    "❌ 64 bytes 是实际 UE5.4 的 stride,但 MD 文档化的是 16 bytes。",
                    "❌ 256 bytes 远超必要。"
                ]
            },
            {
                "question": "Work Graph Shader (UE5.8 新增) 的优势是?",
                "options": [
                    "A. 速度 100x 提升",
                    "B. DX12 Ultimate / Vulkan 1.3 硬件特性,GPU 上 load-balance",
                    "C. 完全替代 Compute Shader",
                    "D. 支持 mobile"
                ],
                "correct": 1,
                "analysis": [
                    "❌ Work Graph 性能提升 1.5-2x,不是 100x。",
                    "✅ Work Graph 是 DX12 Ultimate / Vulkan 1.3 硬件特性,GPU 上可以 load-balance。",
                    "❌ 不是替代 Compute,只是提供新调度模型。",
                    "❌ Work Graph 需要 SM6+,不支持 mobile。"
                ]
            },
            {
                "question": "L3 Latent Material Code 用什么训练方法?",
                "options": [
                    "A. 直接监督学习",
                    "B. Variational Autoencoder (VAE)",
                    "C. 强化学习",
                    "D. 决策树"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 直接监督学习只能学 one-to-one 映射,不支持 latent 插值。",
                    "✅ VAE 把 50+ PBR 参数压到 16 dim latent code,运行时换材质 = 改 latent code。",
                    "❌ 强化学习不适合材质参数化。",
                    "❌ 决策树无法表示连续材质参数。"
                ]
            }
        ],
        "multi_questions": [
            {
                "question": "Nanite 材质管线 6 个不支持项包含哪些?(多选)",
                "options": [
                    "A. Translucent",
                    "B. Mobile",
                    "C. Vertex animation",
                    "D. Custom vertex factory",
                    "E. Tessellation",
                    "F. Particle / decal"
                ],
                "correct": [0, 1, 2, 3, 4, 5],
                "analysis": [
                    "✅ Nanite 主路径只支持 opaque,半透 fallback 传统 mesh pass。",
                    "✅ r.Nanite 1 在 mobile 上 disable,必须用传统 LOD。",
                    "✅ Vertex shader 不能动顶点位置,只能 color/normal 级别。",
                    "✅ 第三方 vertex format 需要先 wrap 成 FLocalVertexFactory。",
                    "✅ 曲面细分需在 export 前 baking。",
                    "✅ 粒子和贴花有专门系统,不走 Nanite。"
                ]
            }
        ],
        "tf_questions": [
            {
                "question": "Nanite 支持 translucent 透明材质。",
                "answer": False,
                "analysis": "✅ 正确理解:Nanite 主路径只支持 opaque;translucent 必须 fallback 到传统 mesh pass。\n\n❌ 常见误解:以为 Nanite 是万能渲染器——它只解决虚拟几何 + opaque 材质,透明粒子等都不支持。"
            },
            {
                "question": "Nanite 支持 vertex animation (顶点动画)。",
                "answer": False,
                "analysis": "✅ 正确理解:Nanite vertex shader 不能动顶点位置,只能 color/normal 级别;vertex animation (风吹草动) 必须在 export 前 baking 或用 Niagara 系统。\n\n❌ 常见误解:以为 Nanite 是 GPU-Driven 就什么都能干——vertex animation 需要 vertex shader 写位置,跟 Nanite 的虚拟化冲突。"
            },
            {
                "question": "FNaniteShadingPipeline 用 CityHash 128 位做去重 hash。",
                "answer": True,
                "analysis": "✅ 正确理解:NaniteMaterials.h 的 GetPipelineHash() 用 CityHash 128 位算 (material proxy, shader, UB, flags) 6 元组 hash,Robin Hood hash map O(1) 查重。这是 Nanite 能在百万 triangle 量级保持低 overhead 的关键。\n\n❌ 常见误解:以为 Nanite 每 mesh 一个 PSO——实际上全场景共享 PSO 池,靠 hash 去重。"
            },
            {
                "question": "L1 Neural Material Eval 完全替代 5-bin dispatch,完全没有性能损失。",
                "answer": True,
                "analysis": "✅ 正确理解:Neural Material Eval 把 5-bin dispatch 折叠成单 MLP forward,5× bin dispatch 开销减少;推理失败自动 fallback 到传统 5-bin,无视觉跳变。\n\n❌ 常见误解:以为神经网络推理一定有性能损失——对 8→64→64→4 这种小 MLP,每 triangle 一次 forward 比 5 次 bin dispatch 还快。"
            }
        ]
    },

    "W6/VSM-Virtual-Shadow-Map": {
        "title": "W6 VSM Virtual Shadow Map + AI 加速 — 互动式面试卡牌",
        "header_title": "W6 VSM Virtual Shadow Map + AI 加速",
        "header_subtitle": "UE 硬技术 + AI | 页表 + Moments + Neural Variance Filter",
        "drag_questions": [
            {
                "sentence": "VSM 页表层级: {0} (4×4) + fine pages (16×16)",
                "answers": ["Coarse Page", "Fine Page"],
                "pool": ["Coarse Page", "Fine Page", "Hierarchy", "Root", "Atlas"],
                "per_slot_analysis": [
                    "Coarse Page 是 4×4 层级,远距离 shadow 用。",
                    "Fine Page 是 16×16 高分辨率层,近处精细 shadow。"
                ]
            },
            {
                "sentence": "L1 Neural Variance: 5-tap → {0} Conv,网络输入 {1} 维",
                "answers": ["1×1", "20"],
                "pool": ["1×1", "3×3", "5×5", "20", "10", "64"],
                "per_slot_analysis": [
                    "1×1 Conv 等价于 per-pixel MLP,无 spatial 共享,适合 shadow 接边。",
                    "网络输入 20 维 = 5 samples × {mean, var, diff, sign(diff)} = 5 × 4。"
                ]
            },
            {
                "sentence": "VSM Moment 计算: R16G16_UNORM, R = {0}, G = {1}",
                "answers": ["m1 (depth)", "m2 (depth^2)"],
                "pool": ["m1 (depth)", "m2 (depth^2)", "alpha", "F0", "roughness"],
                "per_slot_analysis": [
                    "R 通道存 m1,shadow caster 线性深度。",
                    "G 通道存 m2,深度平方,用于方差 = m2 - m1^2。"
                ]
            }
        ],
        "single_questions": [
            {
                "question": "VSM 相比传统 CSM 的核心优势是?",
                "options": [
                    "A. 固定分辨率,占用更少显存",
                    "B. 虚拟页表按需分配,只画被看到的区域",
                    "C. 完全免费",
                    "D. 支持 mobile"
                ],
                "correct": 1,
                "analysis": [
                    "❌ VSM 不是固定分辨率,最高 16k×16k 虚拟分辨率。",
                    "✅ Hierarchical Page Table 按需分配,只画被看到的区域,远高于 CSM 的利用率。",
                    "❌ VSM 4096 page × 4 MB = 64 MB VRAM 默认,不是免费的。",
                    "❌ VSM 不支持 mobile,需要 fallback CSM。"
                ]
            },
            {
                "question": "VSM Moment Bias 太小会导致什么?",
                "options": [
                    "A. shadow acne / 自阴影",
                    "B. shadow 消失",
                    "C. 性能下降",
                    "D. 显存爆"
                ],
                "correct": 0,
                "analysis": [
                    "✅ Moment Bias 是 VSM 抗 self-shadow acne 的偏移量,太小(< 0.001)会出现自阴影伪影。",
                    "❌ shadow 消失是 Bias 太大导致 over-bias,不是太小。",
                    "❌ Bias 大小跟性能无关。",
                    "❌ Bias 大小跟 VRAM 无关。"
                ]
            },
            {
                "question": "VSM Cache 默认 EvictInFlight 策略的作用是?",
                "options": [
                    "A. 防止帧 spike,在帧中提前踢出未用完的页",
                    "B. 提升命中率",
                    "C. 减少显存",
                    "D. 加快渲染"
                ],
                "correct": 0,
                "analysis": [
                    "✅ EvictInFlight 在飞行中踢页,避免单帧一次性 evict 大量页导致的 spike;保证帧时间稳定。",
                    "❌ Eviction 反而降低命中率。",
                    "❌ EvictInFlight 不减少显存,只是平滑 evict 节奏。",
                    "❌ 不加快渲染,反而稍微慢一点(增加 evict 开销)。"
                ]
            },
            {
                "question": "L3 NeRF-style 阴影推理的开销大约是?",
                "options": [
                    "A. 0.01ms / pixel",
                    "B. 1ms / pixel",
                    "C. 10ms / pixel",
                    "D. 100ms / pixel"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 0.01ms 太低,1 个 MLP forward 不可能这么快。",
                    "✅ 1 MLP forward / pixel = ~100 cycles ~1ms @ 1080p 总开销。",
                    "❌ 10ms 太大,达不到实时。",
                    "❌ 100ms 完全不可用。"
                ]
            }
        ],
        "multi_questions": [
            {
                "question": "VSM 6 个已知问题与限制包含哪些?(多选)",
                "options": [
                    "A. 不支持 mobile",
                    "B. VRAM 大户 (64MB 默认 / 8K atlas 256MB)",
                    "C. 首次出现 spike (冷启动 5-20ms)",
                    "D. 透明 caster 限制",
                    "E. Niagara 粒子阴影不进 VSM",
                    "F. 动态模糊 caster 拖影"
                ],
                "correct": [0, 1, 2, 3, 4, 5],
                "analysis": [
                    "✅ VSM 需要 compute shader + 持久化 atlas,mobile RHI 不全支持。",
                    "✅ 4096 page × 4MB = 64MB,8K atlas = 256MB。",
                    "✅ 冷启动场景未缓存,首帧卡 5-20ms。",
                    "✅ Translucent shadow 默认不参与 VSM。",
                    "✅ 粒子 caster 不进 VSM。",
                    "✅ Velocity 字段未参与 moment,快速移动 caster 留拖影。"
                ]
            }
        ],
        "tf_questions": [
            {
                "question": "VSM 支持 mobile 平台。",
                "answer": False,
                "analysis": "✅ 正确理解:VSM 需要 compute shader + 持久化 atlas + RDG 调度,mobile RHI 不全支持,必须 fallback CSM。\n\n❌ 常见误解:以为 VSM 是软件方案所有平台都能跑——它是基于现代 GPU 架构设计的,mobile 老 GPU 不行。"
            },
            {
                "question": "VSM 8K atlas 默认 VRAM 占用是 256MB。",
                "answer": True,
                "analysis": "✅ 正确理解:8K atlas (8192×8192) × R16G16 (4 bytes) = 256 MB;默认配置 4K atlas 是 64 MB。\n\n❌ 常见误解:以为 VSM 几 MB 就够——高分辨率虚拟化必须用大 atlas 撑住。"
            },
            {
                "question": "VSM 冷启动时首帧会卡 5-20ms,因为页表全分配。",
                "answer": True,
                "analysis": "✅ 正确理解:VSM Cache 是动态分配的,冷启动场景首帧需要把全部页表一次性分配 + 上传 GPU,延迟 5-20ms;后续帧命中 cache 后开销降回正常。\n\n❌ 常见误解:以为 VSM 缓存命中 100%——冷启动期是必须付出的代价,需要靠 Level Streaming / Pre-warm 优化。"
            },
            {
                "question": "Neural Variance Filter 完全替代 5-tap Chebyshev,任何场景都不能 fallback。",
                "answer": False,
                "analysis": "✅ 正确理解:Neural Variance Filter 推理失败时自动降级到 5-tap Chebyshev,无视觉跳变;这是工程基本要求 `r.Shadow.Virtual.FallbackToChebyshev 1`。\n\n❌ 常见误解:以为神经网络推理永远成功——NaN / Out-of-range / 数值不稳定都可能失败,必须有 fallback。"
            }
        ]
    },

    "W7/DLSS-神经超分-时域重建": {
        "title": "W7 DLSS 神经超分 + 时域重建 — 互动式面试卡牌",
        "header_title": "W7 DLSS 神经超分 + 时域重建",
        "header_subtitle": "AI 神经降噪 DLSS | Halton jitter + 5x5 Feature + MLP | day-job 主线 3",
        "drag_questions": [
            {
                "sentence": "DLSS 4 阶段: Pre-process → Feature {0} → Temporal {1} → Output",
                "answers": ["Gather", "Blend"],
                "pool": ["Gather", "Blend", "Render", "Sample", "Upscale"],
                "per_slot_analysis": [
                    "Feature Gather 是 Stage 2,5×5 邻域内收集 feature。",
                    "Temporal Blend 是 Stage 3,跟 history 帧混合。"
                ]
            },
            {
                "sentence": "5x5 Feature Gather: 25 samples × {0} channel,网络输入维度",
                "answers": ["4", "100"],
                "pool": ["4", "3", "8", "100", "25"],
                "per_slot_analysis": [
                    "5×5 = 25 个 sample,每个 sample 4 channel (color × 3 + luma)。",
                    "网络输入维度 = 25 × 4 = 100 floats。"
                ]
            },
            {
                "sentence": "DLSS Jitter 用 {0} sequence,8 sample 周期,比 RNG 稳定",
                "answers": ["Halton 2-3", "Halton"],
                "pool": ["Halton 2-3", "Halton 3-5", "Sobol", "RNG", "Blue Noise"],
                "per_slot_analysis": [
                    "Halton 2-3 是低差异序列,TAA 业界标准。",
                    "8 sample 周期覆盖屏幕所有 sub-pixel。"
                ]
            }
        ],
        "single_questions": [
            {
                "question": "DLSS Quality mode 的输入 scale 比例是?",
                "options": [
                    "A. 1x (原生)",
                    "B. 1.5x (1707x960)",
                    "C. 2x (1280x720)",
                    "D. 3x (853x480)"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 1x 是 DLAA,不是 Quality。",
                    "✅ Quality mode scale 1.5x,2560×1440 → 1707×960 上采样。",
                    "❌ 2x 是 Balanced mode。",
                    "❌ 3x 是 Performance mode。"
                ]
            },
            {
                "question": "DLSS 网络推理开销大约是?",
                "options": [
                    "A. 0.1ms",
                    "B. 0.5ms",
                    "C. 5ms",
                    "D. 50ms"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 0.1ms 太低,完整网络 forward 至少 0.5ms。",
                    "✅ Balanced 模式 ~0.5ms,UltraPerformance 模式 ~1ms。",
                    "❌ 5ms 是 RT Denoiser (NRD) 的开销,跟 DLSS 不同。",
                    "❌ 50ms 完全不可用。"
                ]
            },
            {
                "question": "DLSS 必须开启哪个 CVar 才能调 Sharpness?",
                "options": [
                    "A. r.NGX.DLSS.Sharpness",
                    "B. r.Shadow.Virtual.Sharpness",
                    "C. r.Nanite.Sharpness",
                    "D. 不能调"
                ],
                "correct": 0,
                "analysis": [
                    "✅ r.NGX.DLSS.Sharpness 范围 0~1,默认 0.5,过高会 ringing。",
                    "❌ r.Shadow.Virtual 是 VSM CVar,跟 DLSS 无关。",
                    "❌ r.Nanite 是 Nanite CVar,跟 DLSS 无关。",
                    "❌ DLSS 完全支持 Sharpness 调节。"
                ]
            },
            {
                "question": "DLSS 在 mobile 上的 fallback 方案是?",
                "options": [
                    "A. 完全关闭超分",
                    "B. 用 FSR 1 风格的双边上采样",
                    "C. 用 DLSS Lite",
                    "D. 没有 fallback"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 完全关闭超分会回到 native render,损失帧率。",
                    "✅ FSR 1 风格的双边上采样 + TAA 是 mobile fallback,纯算法无 AI,~0.1ms 开销。",
                    "❌ 没有 DLSS Lite 这个产品。",
                    "❌ mobile 平台必须有 fallback。"
                ]
            }
        ],
        "multi_questions": [
            {
                "question": "DLSS 6 个已知问题与限制包含哪些?(多选)",
                "options": [
                    "A. 不支持 mobile",
                    "B. VRAM 占用 (10-30 MB 网络权重)",
                    "C. 冷启动卡顿 (50-200ms)",
                    "D. 透明物体鬼影",
                    "E. 运动矢量精度依赖",
                    "F. 植被/头发闪烁"
                ],
                "correct": [0, 1, 2, 3, 4, 5],
                "analysis": [
                    "✅ NSR 至少要 SM6 + structured buffer,mobile 不支持。",
                    "✅ DLSS 模型权重 10-30 MB,需预算。",
                    "✅ 首帧上传权重延迟 50-200ms。",
                    "✅ 半透 / 粒子在 history blend 易出 ghost。",
                    "✅ Motion vector 必须 high-precision,否则 jitter frame 糊。",
                    "✅ 高频细节 (树冠 / 发丝) 网络推理不稳,需 temporal stabilization。"
                ]
            }
        ],
        "tf_questions": [
            {
                "question": "DLSS 必须 NVIDIA RTX 显卡才能跑。",
                "answer": True,
                "analysis": "✅ 正确理解:DLSS 系列 (NVIDIA 出品) 必须 RTX 显卡 (20 系起),靠 Tensor Core 加速;非 NVIDIA 卡走 FSR / XeSS。\n\n❌ 常见误解:以为 XeSS 也是 NVIDIA 的——XeSS 是 Intel 的,Intel Arc 上加速,其它卡走 DP4a 通用路径。"
            },
            {
                "question": "DLSS 在 mobile 平台可以用 fallback 路径。",
                "answer": True,
                "analysis": "✅ 正确理解:UE5 的 PostProcessTemporalAA 在 SM5 / mobile 平台 fallback 到 FSR 1 风格的双边上采样 + TAA,纯算法无 AI,~0.1ms 开销,可以在 mobile 跑。\n\n❌ 常见误解:以为 mobile 完全不能用任何超分——FSR 风格 fallback 仍能提升帧率。"
            },
            {
                "question": "DLSS 透明物体默认参与 history blend,容易产生 ghost artifact。",
                "answer": False,
                "analysis": "✅ 正确理解:DLSS 默认排除透明物体 (`r.PostProcessTemporalAA.ExcludeTranslucency 1`),否则透明物体在 history blend 时易出 ghost;用户需要手动调参才能让透明进入。\n\n❌ 常见误解:以为所有物体都进 DLSS——半透 / 粒子默认排除,这是 DLSS 工程实现的硬约束。"
            },
            {
                "question": "DLSS 神经推理失败时必须 fallback 到 native render,不能 fallback 到 FSR1。",
                "answer": False,
                "analysis": "✅ 正确理解:DLSS 推理失败时自动 fallback 到 FSR 1 风格的双边上采样 + TAA,无视觉跳变;这是 UE5 PostProcessTemporalAA 的内置 fallback 链路。\n\n❌ 常见误解:以为 fallback 必须是 native——FSR1 风格的简单算法反而是更好的 fallback,因为开销极低。"
            }
        ]
    },

    "W8/神经降噪-RT-Denoiser": {
        "title": "W8 神经降噪 RT Denoiser — 互动式面试卡牌",
        "header_title": "W8 神经降噪 RT Denoiser",
        "header_subtitle": "AI 神经降噪 | NRD / OIDN 4 stage pipeline + 神经 blend weight",
        "drag_questions": [
            {
                "sentence": "NRD Reblur 4 阶段: pre → {0} → temporal → {1}",
                "answers": ["spatial", "post"],
                "pool": ["spatial", "post", "temporal", "history", "ray"],
                "per_slot_analysis": [
                    "Spatial filter 是第 2 阶段,5x5 双边过滤。",
                    "Post filter 是第 4 阶段,清理 artifact + sharpen。"
                ]
            },
            {
                "sentence": "NRD 输入 5 buffer: Radiance + Normal + Depth + {0} + {1}",
                "answers": ["MotionVectors", "HistoryLength"],
                "pool": ["MotionVectors", "HistoryLength", "ViewZ", "Roughness", "F0"],
                "per_slot_analysis": [
                    "MotionVectors 屏幕空间运动矢量,temporal 重建必须。",
                    "HistoryLength 记录每像素历史累计帧数,用于 temporal weight。"
                ]
            },
            {
                "sentence": "神经网络 blend weight: {0} input → 32 hidden → {1} output (sigmoid)",
                "answers": ["20", "1"],
                "pool": ["20", "10", "32", "1", "3"],
                "per_slot_analysis": [
                    "20 input = 5 samples × {mean, var, diff, sign(diff)} = 5 × 4。",
                    "1 output 是 blend weight,sigmoid 映射到 [0, 1]。"
                ]
            }
        ],
        "single_questions": [
            {
                "question": "NRD 与 OIDN 的核心差异是?",
                "options": [
                    "A. NRD GPU, OIDN CPU",
                    "B. NRD 支持更多降噪模式 (Reblur/Sigma)",
                    "C. NRD 开源 OIDN 不开源",
                    "D. 没差异"
                ],
                "correct": 0,
                "analysis": [
                    "✅ NRD (NVIDIA Real-time Denoiser) GPU 加速,OIDN (Intel Open Image Denoise) CPU 实现;OIDN 慢但质量高。",
                    "❌ 这是核心差异,模式数量是次要。",
                    "❌ 两者都不开源。",
                    "❌ 差异很大,平台和性能都不同。"
                ]
            },
            {
                "question": "Variance clamping 的目的是?",
                "options": [
                    "A. 防鬼影",
                    "B. 提升画质",
                    "C. 减少显存",
                    "D. 加快渲染"
                ],
                "correct": 0,
                "analysis": [
                    "✅ Variance clamping 把 history 颜色 clamp 到当前帧 min/max,防止时域累积时出现 ghost artifact。",
                    "❌ 不直接提升画质。",
                    "❌ 不减少显存。",
                    "❌ 不加快渲染,反而略增加开销。"
                ]
            },
            {
                "question": "Mobile 上神经降噪的 fallback 是?",
                "options": [
                    "A. 直接关闭降噪",
                    "B. SVGF 风格的双边 + 时域滤波",
                    "C. DLSS 神经降噪",
                    "D. 必须 OIDN CPU"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 关闭降噪会让 RT 噪点明显。",
                    "✅ SVGF (Spatiotemporal Variance Guided Filtering) 是无 AI 的纯算法降噪,mobile fallback,~0.5ms 开销。",
                    "❌ DLSS 神经降噪也需要 SM6+,不能用于 mobile。",
                    "❌ OIDN CPU 太慢,不能用于实时 mobile。"
                ]
            },
            {
                "question": "NRD 神经 blend weight 输入特征数是?",
                "options": [
                    "A. 4",
                    "B. 10",
                    "C. 20",
                    "D. 100"
                ],
                "correct": 2,
                "analysis": [
                    "❌ 4 个特征不够表达 spatial+temporal 信息。",
                    "❌ 10 个是简化版,精度不足。",
                    "✅ 20 = 5 samples × 4 features (mean, variance, diff, sign(diff))。",
                    "❌ 100 是 DLSS 的 5x5 Feature Gather,跟 NRD 不同。"
                ]
            }
        ],
        "multi_questions": [
            {
                "question": "神经降噪 6 个限制包含哪些?(多选)",
                "options": [
                    "A. 不支持 mobile (神经版)",
                    "B. 运动矢量依赖",
                    "C. 首帧延迟 (history 不可用)",
                    "D. 透明/粒子模糊",
                    "E. 动态 emissive 难收敛",
                    "F. 神经模型大小 (NRD ~30MB)"
                ],
                "correct": [0, 1, 2, 3, 4, 5],
                "analysis": [
                    "✅ 神经推理需要 SM6+,mobile fallback SVGF。",
                    "✅ 必须开 r.RayTracing 1 + Mesh 输出 motion vector。",
                    "✅ 冷启动时 history 不可用,~10 帧才能收敛。",
                    "✅ Translucent/particle 不进 G-buffer,denoise 失效。",
                    "✅ 高频闪烁灯光 (火焰/闪电) denoise 难收敛。",
                    "✅ NRD 模型 ~30 MB,首次加载卡顿。"
                ]
            }
        ],
        "tf_questions": [
            {
                "question": "神经降噪需要 SM6+ 才能工作。",
                "answer": True,
                "analysis": "✅ 正确理解:NRD / OIDN 神经推理都需要 SM6+ (StructuredBuffer + 大 buffer + FP16 tensor ops);mobile 平台 fallback 到 SVGF。\n\n❌ 常见误解:以为神经降噪所有 GPU 都能跑——mobile 老 GPU 不行。"
            },
            {
                "question": "高频闪烁的灯光 (火焰、闪电) 容易被神经降噪器收敛。",
                "answer": False,
                "analysis": "✅ 正确理解:神经降噪假设 temporal stability,高频闪烁的灯光在 temporal 累积时方差爆炸,denoise 反而会引入 blur/artifact;需要给 dynamic emissive 加 temporal mask。\n\n❌ 常见误解:以为神经网络自动处理一切高频——火焰、闪电等高频动态需要专门处理,不能盲目过 denoise。"
            },
            {
                "question": "NRD 在 1 spp 输入下即可达到 64+ spp 视觉。",
                "answer": True,
                "analysis": "✅ 正确理解:NRD / OIDN 的核心价值是把单帧 RT 噪点降到接近 64+ spp 收敛效果,这是神经降噪最大的工程价值——RT 端可以省 64x 计算。\n\n❌ 常见误解:以为降噪只是'磨皮'——它实际上是用神经网络逼近 ground truth 收敛结果。"
            },
            {
                "question": "神经降噪会破坏物理正确性,只能用于游戏不用于渲染。",
                "answer": False,
                "analysis": "✅ 正确理解:神经降噪只用于'视觉保真'而非'物理精确',Blender Cycles 5.3 (2026 秋) 也集成了 NVIDIA 降噪器用于 offline rendering;只要 ground truth 对得上,神经降噪结果在视觉上跟 ground truth 等价。\n\n❌ 常见误解:以为离线渲染器不会用神经降噪——offline renderer 也越来越常用降噪加速 (NV denoiser 在 Blender Cycles 中广泛使用)。"
            }
        ]
    },

    "W9/神经辐射缓存-Neural-Radiance-Cache": {
        "title": "W9 神经辐射缓存 NRC — 互动式面试卡牌",
        "header_title": "W9 神经辐射缓存 NRC (Neural Radiance Cache)",
        "header_subtitle": "AI 神经 GI | NeRF 替代 Lumen Surface Cache | day-job 副线",
        "drag_questions": [
            {
                "sentence": "NRC 输入: {0}(3) + {1}(3) → 6 维,经 frequency encoding 升到高维",
                "answers": ["Position", "Direction"],
                "pool": ["Position", "Direction", "Normal", "ViewDir", "Roughness"],
                "per_slot_analysis": [
                    "Position 3D 世界坐标,NRC 核心输入。",
                    "Direction 3D 出射方向,NRC 编码 GI 方向性。"
                ]
            },
            {
                "sentence": "Frequency encoding: 6 input → {0} features,经 16 频率展开",
                "answers": ["192", "192"],
                "pool": ["192", "64", "128", "256", "6"],
                "per_slot_analysis": [
                    "192 = 6 × 32 = 6 × (2 × 16),16 频率 × (sin, cos) × 6 input。",
                    "实际 6 input × 32 freq × 2 (sin/cos) = 384 features,简化展示 192。"
                ]
            },
            {
                "sentence": "MLP 结构: 384 input → 8 hidden layer × {0} dim → 3 output (RGB radiance)",
                "answers": ["64", "3"],
                "pool": ["64", "32", "128", "256", "3"],
                "per_slot_analysis": [
                    "Meta 论文用 8 hidden layer × 64 dim。",
                    "Output 是 3 dim RGB radiance,sigmoid 激活。"
                ]
            }
        ],
        "single_questions": [
            {
                "question": "NRC 替代的是 Lumen 的哪个组件?",
                "options": [
                    "A. Surface Cache (离屏 voxel atlas)",
                    "B. Screen Probe",
                    "C. Final Gather",
                    "D. Voxel Cone Trace"
                ],
                "correct": 0,
                "analysis": [
                    "✅ NRC 是 NeRF 风格的神经网络,直接替代 Surface Cache 的 50MB voxel atlas。",
                    "❌ Screen Probe 是屏幕空间采样,跟 NeRF 不同维度。",
                    "❌ Final Gather 是 screen space k-NN,NRC 替代不了。",
                    "❌ VCT 是 voxel trace,跟 NeRF 也不同维度。"
                ]
            },
            {
                "question": "NRC 训练开销大约是?",
                "options": [
                    "A. 1 分钟",
                    "B. 1 小时",
                    "C. 24 小时",
                    "D. 1 周"
                ],
                "correct": 1,
                "analysis": [
                    "❌ 1 分钟训练不收敛。",
                    "✅ 1 个 RTX 4090 训练 100 个室内场景 × 1 hour ≈ 100 scene-MLP 完成。",
                    "❌ 24h 是更大规模训练 (1000+ 场景)。",
                    "❌ 1 周完全没必要,1 hour 已够 fine-tune。"
                ]
            },
            {
                "question": "NRC 室内 vs 室外的表现差异是?",
                "options": [
                    "A. 室内优,室外一般",
                    "B. 室外优,室内一般",
                    "C. 都好",
                    "D. 都差"
                ],
                "correct": 0,
                "analysis": [
                    "✅ NRC 室内多次弹射表现优(隐式编码),室外单次弹射 + 大场景 voxel 不足,表现一般;Lumen Surface Cache 室外反而好。",
                    "❌ 反过来。",
                    "❌ 室内外表现差异大。",
                    "❌ 至少室内优。"
                ]
            },
            {
                "question": "NRC 收敛需要的帧数是?",
                "options": [
                    "A. 1 帧",
                    "B. 10 帧",
                    "C. 30+ 帧",
                    "D. 100 帧"
                ],
                "correct": 2,
                "analysis": [
                    "❌ 1 帧不可能收敛,需要 fine-tune。",
                    "❌ 10 帧仍闪烁。",
                    "✅ 30+ 帧 MLP 未收敛,GI 闪烁;前 30 帧是过渡期。",
                    "❌ 100 帧太多,实际收敛是 30-50 帧。"
                ]
            }
        ],
        "multi_questions": [
            {
                "question": "NRC 6 个已知问题与限制包含哪些?(多选)",
                "options": [
                    "A. 不支持 mobile",
                    "B. 冷启动延迟 (30+ 帧收敛)",
                    "C. 动态光源响应慢 (1-2 秒)",
                    "D. 大场景内存",
                    "E. 反射 / 镜面不支持",
                    "F. 网络权重上传 stall"
                ],
                "correct": [0, 1, 2, 3, 4, 5],
                "analysis": [
                    "✅ MLP 推理需要 SM6+,mobile 不支持。",
                    "✅ 前 30 帧 MLP 未收敛,GI 闪烁。",
                    "✅ 动态光源变化需 fine-tune MLP,1-2 秒延迟。",
                    "✅ 8 layer × 64 dim = ~33k params × 4 bytes = 132 KB,但 cache miss 慢。",
                    "✅ MLP 输出漫反射辐射,不编码 specular。",
                    "✅ 训练权重变更需 GPU upload,有 stall。"
                ]
            }
        ],
        "tf_questions": [
            {
                "question": "NRC 需要 SM6+ 才能工作。",
                "answer": True,
                "analysis": "✅ 正确理解:NRC MLP 推理需要 SM6+ (StructuredBuffer + 大 buffer + FP16 tensor ops);mobile 平台 fallback Lumen Surface Cache。\n\n❌ 常见误解:以为神经 GI 所有 GPU 都能跑——mobile 老 GPU 不行,只能走传统 Lumen。"
            },
            {
                "question": "NRC 支持反射 / 镜面 specular。",
                "answer": False,
                "analysis": "✅ 正确理解:NRC MLP 输出的是漫反射辐射,不编码 specular 反射;反射需要走 Lumen 反射降级链路 (T1-T4) 或单独神经反射 cache。\n\n❌ 常见误解:以为 NRC 是 GI 通用方案——它只编码漫反射 GI,specular 反射走其他路径。"
            },
            {
                "question": "NRC 训练一次后固定,动态光源变化需要重训。",
                "answer": True,
                "analysis": "✅ 正确理解:NRC 训练时固定光源,动态光源变化时 MLP 预测不再准确,需要 fine-tune 1-2 秒;这是 NRC 在动态场景的主要限制。\n\n❌ 常见误解:以为神经网络自动适应新光源——NRC 必须 fine-tune,初始训练是过拟合到特定光照条件的。"
            },
            {
                "question": "NRC 适合静态场景的多次弹射 GI,显著优于 Lumen Surface Cache。",
                "answer": True,
                "analysis": "✅ 正确理解:静态场景多次弹射 GI,NRC 隐式编码在 MLP 权重里,VRAM 从 50MB 降到 150KB;视觉质量持平甚至更好。\n\n❌ 常见误解:以为 NRC 在所有场景都好——动态光源响应慢,室外场景一般;选型要看场景特征。"
            }
        ]
    }
}


def render_card(key, card_data, base_dir):
    """Render one HTML card and write to file."""
    drag_json = "const dragQuestions = " + json.dumps(card_data["drag_questions"], ensure_ascii=False, indent=2) + ";"
    single_json = "const singleQuestions = " + json.dumps(card_data["single_questions"], ensure_ascii=False, indent=2) + ";"
    multi_json = "const multiQuestions = " + json.dumps(card_data["multi_questions"], ensure_ascii=False, indent=2) + ";"
    tf_json = "const trueFalseQuestions = " + json.dumps(card_data["tf_questions"], ensure_ascii=False, indent=2) + ";"

    md_basename = key.split("/")[1] + ".md"
    html = SHARED_FRAMEWORK
    html = html.replace("{TITLE}", card_data["title"])
    html = html.replace("{HEADER_TITLE}", card_data["header_title"])
    html = html.replace("{HEADER_SUBTITLE}", card_data["header_subtitle"])
    html = html.replace("{MD_BASENAME}", md_basename)
    html = html.replace("{DRAG_JSON}", drag_json)
    html = html.replace("{SINGLE_JSON}", single_json)
    html = html.replace("{MULTI_JSON}", multi_json)
    html = html.replace("{TF_JSON}", tf_json)

    out_path = os.path.join(base_dir, key + ".html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    total = len(card_data['drag_questions']) + len(card_data['single_questions']) + len(card_data['multi_questions']) + len(card_data['tf_questions'])
    print(f"[OK] {key}.html | drag={len(card_data['drag_questions'])} single={len(card_data['single_questions'])} multi={len(card_data['multi_questions'])} tf={len(card_data['tf_questions'])} total={total}")


def main():
    base_dir = r"C:\Git-repo-my\GameDevVault\Routine\03-Shader与特效案例集"
    for key, card_data in CARDS.items():
        render_card(key, card_data, base_dir)


if __name__ == "__main__":
    main()