# UE5 Game Dev Expert → AI Training Steering: Complete Guide

**Research Date:** 2026-07-01  
**Scope:** Answering "wtf is human expert steering in LLM training" for the Moonshot AI (Kimi) 游戏开发专家（AI 训练方向）position.  
**Sources:** 48+ independent searches across academic papers, industry reports, job listings, and frontier-lab publications. Cross-verified across three research dimensions.

---

## 1. Executive Summary: WTF Is Human Expert Steering?

**Human expert steering** is the process of channeling domain expertise into the LLM training pipeline so the model learns not just *what* to say, but *how to think correctly* about a specific domain. You are not training the model yourself (that's the ML engineer's job). You are **the compass** — defining what correct looks like, creating examples of expert-level work, and judging when the model gets it wrong.

### The Core Insight

LLMs are trained in stages. The first stage (pre-training) teaches the model to predict the next token from trillions of words of internet text. The second stage (post-training) teaches the model to be useful, accurate, and aligned with human intent. **Post-training is where domain experts matter most** — and it accounts for the majority of a model's usable capability [^1][^2].

For a game development expert, your job is to ensure that when the model writes UE5 C++, explains Lumen GI, or debugs a Niagara system, it does so at the level of a senior engine programmer — not a Stack Overflow copy-paster.

### The "Coach" Metaphor

Think of yourself as an **AI coach** (or "AI trainer" — 人工智能训练师, a formal national occupation in China since 2020 [^3]). A sports coach doesn't play the game; they design drills, correct form, and set the standard. You design the "drills" (training examples), correct the model's "form" (rank its outputs), and set the standard (define what "good" means for UE5 code).

OpenAI reportedly pays **$100–200/hour** for PhD-level experts to do exactly this [^4]. Surge AI pays domain experts **$100–500/hour** depending on specialty (software engineers: $100–300/hr) [^5]. The reason: **one wrong example in training data teaches the model to hallucinate**. One right example from a true expert is worth more than 10 scraped Stack Overflow posts.

---

## 2. The LLM Training Pipeline: Where You Fit

Here is the 2026 frontier-lab training pipeline. Your role appears at **multiple stages**:

```
┌─────────────────────────────────────────────────────────────────────┐
│  PRE-TRAINING (10-15T tokens)                                       │
│  → Raw internet text, code, docs. You DON'T do this.               │
│                                                                     │
│  ↓                                                                  │
│  SFT — SUPERVISED FINE-TUNING (5K-50K examples)                     │
│  → YOU WRITE: Golden example prompt-response pairs                 │
│  → "Given this UE5 task, here is the correct solution..."          │
│                                                                     │
│  ↓                                                                  │
│  PREFERENCE OPTIMIZATION (DPO / IPO / KTO)                         │
│  → YOU RANK: Which of these two model outputs is better?            │
│  → You judge correctness, helpfulness, UE5 idiomaticity             │
│                                                                     │
│  ↓                                                                  │
│  RL WITH VERIFIABLE REWARDS (GRPO / RLVR)                           │
│  → YOU DESIGN: Test cases, correctness rules, execution env       │
│  → Code compiles? Passes tests? That's the reward signal.           │
│                                                                     │
│  ↓                                                                  │
│  EVALUATION & RED-TEAMING                                           │
│  → YOU EVALUATE: Systematic testing on UE5 tasks                   │
│  → YOU REPORT: Failure patterns, improvement suggestions            │
│                                                                     │
│  ↓                                                                  │
│  SYNTHETIC DATA VALIDATION                                          │
│  → YOU REVIEW: AI-generated examples, correct errors, approve       │
│  → 500 expert seeds → 50K synthetic examples (with your check)     │
└─────────────────────────────────────────────────────────────────────┘
```

### The Shift from "RLHF" to "Verifiable Rewards"

The old paradigm (2022-2024) was **RLHF**: human experts rank outputs, a reward model learns from those rankings, and the LLM is fine-tuned to maximize the reward. The new paradigm (2025-2026) for code and reasoning is **RLVR** (Reinforcement Learning with Verifiable Rewards): the reward comes from whether the code compiles and passes unit tests — not from human preference [^6][^7].

**For you as a UE5 expert, this means:**
- Your **code examples** are more valuable than your **opinions**
- Your **test cases** become the training signal
- Your **execution pipeline** (can we compile this in UE5?) replaces subjective ranking

---

## 3. Mapping the JD to the Pipeline

The JD lists three responsibilities. Here is exactly how each maps to the training pipeline and what you produce.

### 3.1 评估模型能力 → Model Evaluation & Red-Teaming

**Pipeline stage:** Post-training evaluation + continuous monitoring  
**What you do:** Systematically test the model on real UE5 tasks and score its outputs against a structured rubric.

**Concrete workflow:**
1. **Design evaluation tasks** across UE5 subsystems (rendering, physics, networking, VFX, animation, GamePlay)
2. **Run the model** on each task (generate code, answer questions, debug scenarios)
3. **Score outputs** using a multi-dimensional rubric (see Section 6.2)
4. **Categorize failures** using an error taxonomy (e.g., TRAIL: 3 classes, 21 subtypes [^8])
5. **Quantify performance**: compute pass rates, compare against baseline models, track trends

**Example evaluation task:**

```
Prompt: "Write a UE5 C++ Actor that uses Chaos Physics to create a destructible 
wall. The wall should fracture on collision with a projectile. Include the Geometry 
Collection setup code and the collision event handler."

Model Output: [generates code]

Your Evaluation:
- Correctness: 3/5 (misses FBodyInstance configuration for async physics tick)
- Idiomaticity: 4/5 (uses correct UCLASS macros but wrong fracture map workflow)
- Completeness: 2/5 (no mention of GC asset requirement, no Level Sequence setup)
- Safety: 5/5 (no harmful content)
- Verdict: REJECTED — needs iteration on physics determinism section
```

**Key insight:** The model doesn't just need to be "vaguely right." It needs to generate **compilable, runtime-tested code**. AutoUE's research shows that removing engine constraints from prompts causes **100% compilation failure** in ablations [^9]. Your evaluation must include compilation checks.

---

### 3.2 编写示例代码 → SFT Demonstration Data + Synthetic Seed Data

**Pipeline stage:** SFT (Supervised Fine-Tuning) + Synthetic data generation  
**What you do:** Write engineering-grade, reusable reference implementations that the model learns to imitate.

**The "Three-Element" Format** (problem → solution思路 → answer) [^4][^10]:

```json
{
  "instruction": "Write a custom UGameInstance in UE5 C++ that stores persistent 
                  player score across level transitions, exposes it to Blueprints, 
                  and initializes a Steam subsystem if available.",
  "context": {
    "engine_version": "UE 5.4",
    "modules": ["Core", "Engine", "OnlineSubsystemSteam"],
    "constraints": [
      "Must use UPROPERTY(BlueprintReadOnly) for score",
      "Must override Init() and Shutdown()",
      "Must include generated.h header"
    ]
  },
  "solution思路": [
    "1. Create UCLASS(BlueprintType) class inheriting from UGameInstance.",
    "2. Add UPROPERTY(BlueprintReadOnly, Category='PlayerData') float TotalScore.",
    "3. Override Init() to call Super::Init() and initialize Steam.",
    "4. Override Shutdown() to clean up."
  ],
  "answer": {
    "header": "// MyGameInstance.h\n...",
    "source": "// MyGameInstance.cpp\n..."
  }
}
```

**Why this format matters:**
- The `solution思路` teaches the model **how to reason** about the problem, not just what to output
- The `context` provides engine-specific constraints that scraped data lacks
- The `constraints` field tells the model what MUST be true (e.g., `BlueprintReadOnly` not `EditAnywhere`)

**Quality properties you enforce** [^11]:

| Property | Why It Matters for UE5 |
|----------|------------------------|
| **Correctness** | Code must compile in UE5 Editor. One wrong `UFUNCTION` specifier teaches the model to hallucinate. |
| **Completeness** | Must include `.Build.cs` module dependencies, `#include` headers, and `GENERATED_BODY()`. |
| **Idiomaticity** | Uses Epic's conventions (`UCLASS`, `UPROPERTY`, `Super::`), not generic C++. |
| **Version accuracy** | References UE5.4 APIs, not UE4 deprecated ones. |
| **Performance awareness** | Mentions frame budget, draw calls, or memory implications where relevant. |

**Quantity:** Modern practice shows that **1,000–5,000 high-quality examples** outperform 100K scraped ones [^12]. Your 500 compiler-verified UE5 examples are worth more than 50,000 Stack Overflow snippets.

---

### 3.3 制定改进建议 → Structured Improvement Reports + Data Strategy

**Pipeline stage:** Feedback loop into next training iteration  
**What you do:** Analyze patterns in model failures, diagnose root causes, and propose concrete training data or architecture changes.

**The standard report template** [^13]:

```markdown
# Model Improvement Report — UE5 Rendering — 2026-07-01

## 1. Executive Summary
- Problem: Model generates incorrect VSM (Virtual Shadow Map) fixes in 73% of 
  multi-light scene prompts.
- Severity: P1 (high user impact, affects common UE5 workflow)
- Recommended action: Add 200+ VSM debugging examples to SFT dataset

## 2. Evidence
- Quantitative: 73% failure rate on VSM tasks (n=150 evaluation samples)
- Qualitative: Model consistently recommends `r.Shadow.Virtual.MaxPhysicalPages=8000` 
  as a fix-all, regardless of root cause (light density vs. page count)
- Comparative: GPT-4 fails at 68%; Claude 4 fails at 71%; our model fails at 73%

## 3. Root Cause Analysis
- Error taxonomy: Class 1 (Output Generation Error) — Incorrect reasoning chain
- Data analysis: Training corpus has only 12 VSM-specific examples; most are generic 
  "shadow fix" posts from pre-UE5.3 era
- User impact: Users with 20+ lights in scenes get useless advice, leading to frustration

## 4. Improvement Recommendations
| Priority | Action | Data/Model | Cost | Expected Impact |
|----------|--------|------------|------|-----------------|
| P0 | Add 200 VSM examples with scene metadata | Data | 2 weeks | +40% VSM pass rate |
| P1 | Add console command lore with version tags | Data | 1 week | +15% accuracy |
| P2 | Implement execution verifier for .ini commands | Model | 3 weeks | Reduces hallucinations |

## 5. Implementation Plan
- Owner: [ML Engineer name]
- Timeline: SFT data ready by July 15; model retrain by July 30
- Success metrics: VSM task pass rate ≥ 85% on same evaluation set
- Risk: Console commands change per UE version; need versioning system

## 6. Appendices
- Raw evaluation data: [link]
- Rubric used: [link]
- Annotated failure examples: [link]
```

**This is not optional feedback.** In Chinese AI companies (ByteDance, Moonshot, DeepSeek), these reports directly drive the **data flywheel** — user feedback → expert analysis → training data updates → model retrain → validation [^14]. Your report is the bridge between "the model is bad at VSM" and "here's exactly what data to add."

---

## 4. Skills Breakdown: What You Need to Succeed

Based on the JD requirements and industry practice, the required skills split into four categories.

### 4.1 Domain Expertise (UE5 / Game Dev) — THE MOAT

| Skill | Why It Matters | JD Requirement |
|-------|---------------|----------------|
| **UE5 engine internals** | You must know Nanite, Lumen, VSM, Niagara, Chaos, GAS at the level of someone who has debugged them in production. | "UE5优先（Nanite、Lumen、Virtual Shadow Maps等）" |
| **C++ + Blueprint dual fluency** | The model must generate both. You must evaluate both. | "扎实的编程能力...熟悉着色器编程（HLSL/GLSL）" |
| **Rendering pipeline** | LLMs fail hardest on rendering. You need to diagnose why. | "了解渲染管线（实时渲染）" |
| **Physics / Animation / VFX / Networking** | The model needs breadth across all game dev subsystems. | "物理系统、动画系统、特效系统、网络系统、GamePlay" |
| **Full project lifecycle** | Only someone who has shipped knows where models fail. | "全流程完整参与过一个商业级项目" |
| **Cross-discipline awareness** | You must understand TA, design, QA perspectives to evaluate model outputs for different roles. | "了解开发、TA、策划、测试的工作内容" |

**Why this is your moat:** Generic annotators cannot distinguish between a correct `UFUNCTION` specifier and a wrong one. They don't know that `BlueprintNativeEvent` requires an `_Implementation` suffix. They can't tell when a Niagara module uses the wrong parameter map namespace. **Your 3+ years of shipping experience is the barrier to entry.**

### 4.2 AI / ML Literacy — THE INTERFACE

| Skill | Why It Matters | Application |
|-------|---------------|-------------|
| **Understand SFT** | You write the examples the model learns from. | Formatting prompt-response pairs |
| **Understand RLHF / DPO / GRPO** | You rank outputs and design reward signals. | Preference ranking, rubric design |
| **Understand RLVR** | For code, the reward is "does it compile?" | Designing test cases, execution pipelines |
| **Prompt engineering** | You write prompts that elicit good model outputs for data generation. | Synthetic data generation, evaluation |
| **Data quality assessment** | You spot bad training data before it poisons the model. | Filtering scraped data, validating synthetic data |
| **Basic Python** | You need to script evaluation pipelines, process JSON datasets. | Data manipulation, automation |

**You don't need to be an ML engineer.** You need to know **enough** to have intelligent conversations with ML engineers and understand how your work feeds into the pipeline. The ByteDance JDs explicitly require "understanding of SFT and RL basics" and "Python proficiency" [^15].

### 4.3 Evaluation & Analysis — THE ENGINE

| Skill | Why It Matters | Application |
|-------|---------------|-------------|
| **Rubric design** | Consistent evaluation requires structured scoring. | Creating 5-dimension rubrics for code quality |
| **Error taxonomy** | Categorizing failures enables systematic improvement. | TRAIL framework: 3 classes, 21 subtypes [^8] |
| **Inter-annotator agreement** | Your judgments must be consistent enough to be reliable. | Cohen's κ target ≥ 0.8 [^16] |
| **Quantitative analysis** | You must prove the model improved, not just feel it. | Pass rates, A/B comparisons, trend tracking |
| **Root cause analysis** | "The model is wrong" is not enough. "The model is wrong because training data lacks X" is actionable. | Improvement reports |

### 4.4 Communication & Collaboration — THE MULTIPLIER

| Skill | Why It Matters | Application |
|-------|---------------|-------------|
| **Cross-functional communication** | You translate domain failures into ML-engineer-actionable tickets. | Weekly syncs with algorithm team |
| **Guideline writing** | You write the rules that annotator teams follow. | Annotation guidelines, rubric docs |
| **Teaching / mentoring** | Senior experts calibrate junior annotators. | Calibration sessions, honeypot design |
| **Chinese + English** | Moonshot is a Chinese company; UE5 docs are English. | Bilingual report writing, doc reading |
| **Structured writing** | Your reports must be scannable by busy engineers. | Markdown reports with clear sections, tables, evidence |

---

## 5. Concrete Output Artifacts: What You Actually Produce

Here is the complete inventory of tangible deliverables you produce in this role, with formats and examples.

### 5.1 Golden Example Datasets (SFT Data)

**Format:** JSONL files with structured prompt-response pairs  
**Volume:** 50–500 examples per sprint (quality > quantity)  
**Standard:** Each example includes: instruction, context (engine version, constraints), solution思路, answer, and verification log (compile success screenshot)

**Example file:** `ue5_sft_gameinstance_v1.jsonl`

```jsonl
{"instruction": "...", "context": {...}, "solution思路": [...], "answer": {...}, "verification": "compiled_ue5.4_20260701.png"}
{"instruction": "...", "context": {...}, "solution思路": [...], "answer": {...}, "verification": "compiled_ue5.4_20260701.png"}
```

### 5.2 Preference Datasets (DPO / RLHF Data)

**Format:** JSONL with pairwise comparisons: `prompt`, `chosen`, `rejected`  
**Volume:** 100–1,000 pairs per sprint  
**Standard:** Each pair ranked by you using a 5-dimension rubric

```jsonl
{
  "prompt": "Explain how to fix flickering Lumen reflections in UE5.4",
  "chosen": "Lumen reflections flicker when Surface Cache resolution is insufficient... [correct, detailed]",
  "rejected": "Just increase r.Shadow.Virtual.MaxPhysicalPages to 8000... [wrong, generic]",
  "ranker_id": "expert_001",
  "rubric_scores": {
    "chosen": {"accuracy": 5, "helpfulness": 5, "completeness": 4},
    "rejected": {"accuracy": 2, "helpfulness": 2, "completeness": 1}
  }
}
```

### 5.3 Evaluation Rubrics

**Format:** Markdown documents with dimension definitions, scoring criteria, and examples  
**Purpose:** Standardize evaluation across all experts and annotators

```markdown
## UE5 Code Quality Rubric v1.2

### Dimension 1: Correctness (40%)
- 5: Compiles and runs correctly in UE5.4 Editor on all test cases
- 4: Minor edge case failure (1/10 test cases)
- 3: Partial correctness, core logic works but has significant bugs
- 2: Major logical errors, does not solve the problem
- 1: Completely wrong or hallucinated APIs

### Dimension 2: UE5 Idiomaticity (25%)
- 5: Follows Epic conventions (UCLASS, UPROPERTY, Super::), correct macro specifiers
- 4: Mostly correct, minor style issues (e.g., missing EditAnywhere vs. VisibleAnywhere distinction)
- 3: Inconsistent, some non-idiomatic patterns (e.g., raw pointers instead of TWeakObjectPtr)
- 2: Poor understanding of UE5 patterns (e.g., missing GENERATED_BODY())
- 1: Generic C++ with no UE5 awareness

### Dimension 3: Completeness (20%)
- 5: Addresses all parts of prompt, includes headers, Build.cs dependencies, error handling
- 4: Mostly complete, minor omissions
- 3: Missing important context (e.g., no module dependency listed)
- 2: Incomplete, major parts missing
- 1: Barely addresses the prompt

### Dimension 4: Performance Awareness (10%)
- 5: Explicitly considers frame budget, draw calls, memory, replication cost
- 4: Mentions performance implicitly
- 3: Neutral, no performance consideration
- 2: Anti-patterns that hurt performance
- 1: Disastrous for performance (e.g., infinite loops in Tick())

### Dimension 5: Safety / Robustness (5%)
- 5: Comprehensive input validation, null checks, graceful failure
- 4: Basic validation
- 3: Some validation but missing edge cases
- 2: Minimal error handling
- 1: No safety checks (e.g., unchecked Cast<> that will crash)
```

### 5.4 Error Analysis Reports

**Format:** Markdown with tables, frequency counts, severity ratings  
**Frequency:** Weekly or per-evaluation-cycle

```markdown
## UE5 Model Error Analysis — Week of 2026-06-23

### Summary
- Total evaluation samples: 450
- Overall pass rate: 34% (↓ 2% vs. last week)
- Most improved: Niagara (+8%)
- Most degraded: Networking (-12%)

### Top 5 Failure Patterns
| Rank | Pattern | Frequency | Severity | Example |
|------|---------|-----------|----------|---------|
| 1 | Missing `_Implementation` for `BlueprintNativeEvent` | 23% | P0 | [link] |
| 2 | Recommending Nanite for mobile/Quest | 18% | P1 | [link] |
| 3 | Wrong GAS prediction setup | 15% | P0 | [link] |
| 4 | VSM page overflow misdiagnosed | 12% | P1 | [link] |
| 5 | Niagara CPU vs GPU sim wrong | 9% | P2 | [link] |

### Recommended Actions
1. Add 100 `BlueprintNativeEvent` examples with `_Implementation` pattern (P0)
2. Add mobile platform compatibility matrix to context (P1)
3. Add GAS prediction setup tutorial to SFT data (P0)
```

### 5.5 Annotation Guidelines

**Format:** Confluence/Notion docs with rules, edge cases, and examples of correct/incorrect labels  
**Purpose:** Enable scaling annotation to junior team members

### 5.6 Code Example Repositories

**Format:** Git repositories with README, unit tests, multiple difficulty levels  
**Purpose:** Provide the ML team with compilable, verifiable reference code

```
ue5-training-examples/
├── README.md
├── rubric.md
├── beginner/
│   ├── 01_custom_gameinstance/
│   │   ├── MyGameInstance.h
│   │   ├── MyGameInstance.cpp
│   │   ├── test_case.json
│   │   └── verification_log.md
│   └── 02_simple_actor_component/
├── intermediate/
│   ├── 01_gas_ability_setup/
│   ├── 02_niagara_gpu_module/
│   └── 03_replication_rpc/
└── advanced/
    ├── 01_custom_render_pass/
    ├── 02_chaos_destruction_fracture/
    └── 03_multiplayer_prediction/
```

### 5.7 Improvement Proposals

**Format:** Structured reports (see Section 3.3 template)  
**Frequency:** Bi-weekly or triggered by significant evaluation findings

### 5.8 Quality Metrics Dashboards

**Format:** Excel/Tableau dashboards tracking: annotation quality (κ scores), model performance trends, throughput stats  
**Purpose:** Monitor the health of the data pipeline

---

## 6. What Your Day Actually Looks Like

Based on industry JDs and platform workflows [^13][^17], here is a realistic day:

| Time | Activity | Output |
|------|----------|--------|
| 09:00–09:30 | Review overnight model evaluation results, check Slack/Feishu for ML engineer questions | Mental model of today's priorities |
| 09:30–12:00 | **Deep evaluation work:** Run model on 10–15 UE5 tasks, score outputs, document failures | 15 scored samples, 3 failure patterns flagged |
| 12:00–13:30 | Lunch + async review of team annotation quality | Feedback on 5 annotator samples |
| 13:30–15:30 | **Produce training data:** Write 2–3 golden example prompt-response pairs, compile and verify in UE5 Editor | 3 verified JSON examples with compile logs |
| 15:30–16:30 | **Cross-functional sync:** Meet with ML engineers to discuss model weaknesses, review data effectiveness | Meeting notes, 2 action items |
| 16:30–18:00 | **Analysis and reporting:** Compile error patterns, update error taxonomy, draft improvement suggestion | Weekly error analysis report draft |
| 18:00–18:30 | Submit deliverables, update task tracker | All artifacts checked in |

**Key distinction:** You spend only ~30% of your time on direct "annotation" (writing examples, ranking outputs). The majority is on **analysis, design, and communication** — defining what good looks like, diagnosing why the model fails, and translating that into actionable training data strategy.

A basic annotator does the opposite: 80%+ repetitive labeling, 20% thinking. **You are paid for the thinking.**

---

## 7. Expert vs. Annotator: Why the JD Requires 3+ Years

| Dimension | Basic Annotator | Domain Expert (You) |
|-----------|----------------|---------------------|
| **Education** | High school – Bachelor, any major | Bachelor+, CS/engineering, relevant domain |
| **Experience** | 0–1 year, no domain requirement | 3+ years, full project lifecycle |
| **Primary task** | Follow rules, label data, hit quotas | Design rules, evaluate quality, analyze failures, propose improvements |
| **Compensation** | ¥3,000–8,000/mo or $10–15/hr | ¥20,000–50,000/mo or $100–300/hr |
| **Decision authority** | None — follows guidelines | Defines guidelines, arbitrates disagreements, approves edge cases |
| **Code skills** | Usually none | Python, data analysis, understanding of ML pipelines |
| **Output type** | Raw labeled data | Analysis reports, guidelines, code examples, training strategies |
| **Why the model fails** | Doesn't know, doesn't care | Knows exactly why and can fix it |

The JD requires "全流程完整参与过一个商业级项目" because:
1. **Edge case judgment:** Only someone who has shipped knows where models fail in practice
2. **Cross-functional communication:** You must translate domain failures into ML-engineer-actionable feedback
3. **Quality calibration:** Your inter-rater agreement (Cohen's κ) must be > 0.8 to be the golden standard
4. **Tool creation:** You build the infrastructure (guidelines, templates) that scales annotation
5. **Data flywheel design:** You design feedback loops where production data improves training data

---

## 8. How to Prepare for This Role

### Immediate Actions (Next 2 Weeks)

1. **Study the pipeline:** Read the InstructGPT paper, the DeepSeek-R1 paper, and the DPO paper. You don't need to understand every equation, but you need to know what SFT, DPO, and GRPO mean and how they differ.

2. **Build a sample code repository:** Create 10–20 UE5 examples ranging from beginner (Blueprint) to advanced (custom render pass, compute shader). Include:
   - Problem description
   - Step-by-step reasoning
   - Complete, compilable code
   - Unit tests or verification steps
   - Difficulty tag

3. **Practice rubric design:** Take a UE5 coding task and design a 5-dimension rubric. Test it by scoring ChatGPT/Claude/Kimi outputs. Calibrate with a colleague.

4. **Document failure modes:** List 20 ways an LLM fails on UE5 tasks:
   - Hallucinated APIs (e.g., `SetTimerByEvent` in C++)
   - Wrong macro usage (e.g., `UFUNCTION` inside user-defined macros)
   - Version drift (e.g., recommending UE4 patterns in UE5)
   - Missing `_Implementation` for `BlueprintNativeEvent`
   - Anti-patterns (e.g., raw pointers instead of `TWeakObjectPtr`)

5. **Learn prompt engineering:** Practice writing system prompts and few-shot examples that elicit correct UE5 code. Document what works.

6. **Engage with the Chinese AI community:** Follow Moonshot, DeepSeek, ByteDance Seed team publications. Understand their specific approaches.

### Deeper Preparation (Next 2 Months)

7. **Set up a UE5 compilation verification pipeline:** Can you automatically compile AI-generated C++ code in UE5? This is the core of RLVR for code.

8. **Contribute to open-source evaluation:** Look for UE5 evaluation benchmarks (AutoUE, UnrealLLM) and try to improve them or replicate them.

9. **Build a synthetic data generator:** Use GPT-4/Kimi to generate 100 UE5 code examples, then review and correct them. Measure your correction rate. This simulates the "AI-first, human-reviewed" workflow.

10. **Study the business:** Read Moonshot AI's publications on long-context processing and Kimi K2. Understand what makes their models different and where your UE5 expertise fits.

---

## 9. The Bottom Line

**"AI Training Direction Game Development Expert" is not a game developer role.** You will not be building games. You will be **teaching the model to build games** — or more precisely, teaching the model to think about game development at the level of a senior UE5 engineer.

Your value proposition is **scarcity**: the number of people who can write correct `UCLASS` code, debug VSM page overflow, architect GAS replication, AND understand how LLMs are trained is vanishingly small. Every verified example you write is worth orders of magnitude more than scraped data.

The workflow is:
1. **You define correct** (rubrics, guidelines, test cases)
2. **You demonstrate correct** (golden examples, reasoning traces)
3. **You judge deviations from correct** (evaluation, preference ranking)
4. **You prescribe corrections** (improvement reports, data strategy)
5. **The model learns** (SFT, DPO, RLVR)
6. **You validate the learning** (re-evaluation, A/B testing)
7. **Repeat**

This is the **data flywheel** that powers frontier AI. You are the critical human in the loop.

---

## References

[^1]: Post-Training LLMs Guide: SFT, RLHF, DPO & GRPO Explained (2026). Sundeep Teki. https://www.sundeepteki.org/advice/the-complete-guide-to-post-training-llms-how-sft-rlhf-dpo-and-grpo-shape-llms

[^2]: LLM Anatomy in 2026: 5 Counter-Intuitive Truths About Frontier AI Model Training. Pasquale Pillitteri. https://pasqualepillitteri.it/en/news/2023/llm-anatomy-2026-frontier-ai-training

[^3]: 《人工智能训练师》国家职业技能标准. 2020. https://www.sohu.com/a/864599391_121798711

[^4]: 逐句讲解DeepSeek-R1、Kimi K1.5、OpenAI o1技术报告. Xiaoyuzhou FM. https://www.xiaoyuzhoufm.com/episode/67a1b697247d51713c868367

[^5]: The Role of RLHF Platforms in AI Advancement. Lemon.io. https://lemon.io/blog/rlhf-platforms/

[^6]: CodeScaler: Scaling Code LLM Training and Test-Time Inference via Execution-Free Reward Models. arXiv:2602.17684. https://arxiv.org/html/2602.17684v1

[^7]: ExecVerify: White-Box RL with Verifiable Stepwise Rewards for Code Execution Reasoning. arXiv:2603.11226. https://arxiv.org/html/2603.11226

[^8]: TRAIL: Trace Reasoning and Agentic Issue Localization. Patronus AI. https://arxiv.org/abs/2505.08638

[^9]: AutoUE: Ablation Study on UE5 Code Generation. ACL 2026 Findings. https://aclanthology.org/2026.findings-acl.111.pdf

[^10]: OpenCodeInstruct / Genetic-Instruct: 5M-sample dataset combining evol-instruct and self-instruct. https://www.emergentmind.com/papers/2504.04030

[^11]: Curating High-Quality SFT Datasets. APXML. https://apxml.com/courses/rlhf-reinforcement-learning-human-feedback/chapter-2-sft-phase-rlhf/sft-dataset-curation

[^12]: Training Small Expert Agents With Minimal Examples. CEUR-WS. https://ceur-ws.org/Vol-4200/keynote2.pdf

[^13]: Structured Feedback Mechanisms. 讲师台. https://www.jiangshitai.com/rc/3109.html

[^14]: 字节在跳动，阿里在躁动，AI六小龙被震动. Xiaoyuzhou FM. https://www.xiaoyuzhoufm.com/episode/67559babbdb9877a973dd607

[^15]: ByteDance AI Job Descriptions. Zhaopin. https://www.zhaopin.com/jobdetail/CC469217510J40717299901.htm

[^16]: Complete Guide to RLHF Human Annotation [2026]. Annotera. https://www.annotera.ai/blog/rlhf-human-annotation-guide/

[^17]: RLHF Preference Annotator. Claru AI Jobs. https://claru.ai/jobs/rlhf-preference-annotator
