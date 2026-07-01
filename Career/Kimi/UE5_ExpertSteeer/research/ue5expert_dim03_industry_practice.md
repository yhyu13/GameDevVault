# Dimension 03: Industry Practice — What "AI Training Expert" Jobs Actually Look Like

**Research Date:** 2026-07-01  
**Sources:** 15+ independent web searches covering Chinese job listings (ByteDance, Baidu, Alibaba, Moonshot, DeepSeek), international RLHF platforms (Scale AI, Surge AI, OpenAI), evaluation methodologies, and data quality standards.  
**Researcher:** Industry_Practice_Researcher

---

## 1. What "AI Training Expert" Means in Industry

### 1.1 Job Category Definition

The term "AI训练专家" (AI Training Expert) or "数据训练专家" (Data Training Expert) has emerged as a formal job category in China's AI industry since 2020, when China's Ministry of Human Resources and Social Security officially classified "人工智能训练师" (Artificial Intelligence Trainer) as a new profession with national occupational skill standards [^11]. The standard defines the role as: "personnel who use intelligent training software to perform database management, algorithm parameter setting, human-computer interaction design, performance testing and tracking, and other auxiliary operations during the actual use of AI products" [^11].

The national standard further splits this into two sub-occupations: **数据标注员** (Data Annotator) and **人工智能算法测试员** (AI Algorithm Tester) [^11]. However, the skill levels range from Level 1 (entry) to Level 5 (senior technician), with higher levels requiring capabilities in **business analysis, intelligent training, intelligent system design, and training guidance** — far beyond simple annotation [^11].

### 1.2 What Top Chinese AI Companies Actually Ask For

**ByteDance** (the parent company of Moonshot AI's competitor Doubao) posts multiple variations of this role:

| Role | Key Responsibilities | Requirements |
|------|---------------------|--------------|
| AI数据训练专家（翻译方向）| Cross-language content editing, translation quality evaluation, annotation guideline development, data quality assessment system building, model output analysis using data analytics, valuable analysis reports [^1] | Bachelor+, 1-3 years data training experience, TEM-8 or IELTS 7+, editing experience, Prompt Engineering skills |
| AI技术数据专家 | Design data automation strategies combining PE and AI Agent architecture, produce high-quality video data for different training stages, build Agents for generation/evaluation/data extraction, use PE for efficiency [^2] | Bachelor+, CS/AI/SE major, PE project experience, understand SFT and RL basics, Python/Java proficiency |
| 大模型Agent数据运营专家 | Design annotation schemes and rules, organize team for daily data production, use PE for data production and filtering, analyze data core needs, communicate with R&D teams [^3] | Bachelor+, statistics/CS major, project management experience, PE workflow experience |
| AI搜索数据专家 | Machine production of search engine training data, optimize data production standards, data mining/preprocessing/synthesis, closed-loop validation of data effectiveness on model experiments [^4] | Bachelor+, CS/STEM major, deep understanding of search products, data analysis skills, AI understanding |

**Key insight from ByteDance JDs:** The role is **not** basic annotation. It requires: domain expertise (translation, search, agent design), programming ability (Python), understanding of training paradigms (SFT, RL), data analysis capability, and cross-functional collaboration with algorithm and product teams.

### 1.3 The Moonshot AI (Kimi) Specific Context

Moonshot AI currently has approximately **300 employees**, with half being post-1990s generation [^13]. The team includes NLP, computer vision, reinforcement learning, and infrastructure specialists [^13]. While specific data training JDs were not found in this search, the company's focus on long-context processing and Chinese language capabilities implies their data training experts would need:

- Deep understanding of Chinese linguistic nuances
- Ability to evaluate model performance on long documents
- Expertise in domain-specific scenarios (coding, research, creative writing)
- Cross-modal data evaluation capabilities (text + image for K2 multimodal)

### 1.4 International Benchmark: OpenAI, Scale AI, Surge AI

On the international side, the "AI training expert" role manifests as **RLHF (Reinforcement Learning from Human Feedback) specialists**:

- **OpenAI** reportedly pays **$100–200/hour** for PhD-level data annotation for RLHF [^6]. They hire domain experts (doctors, lawyers, PhD researchers) to produce high-quality preference data and golden-standard responses [^6].
- **Scale AI** (valued at $15.9B, Meta holds 49% stake) provides technical annotation and model evaluation services, paying **$25–65/hour** for advanced technical roles [^12]. They work directly with major AI labs including OpenAI [^12].
- **Surge AI** (bootstrapped to $1.2B ARR, ~50,000 expert contractors) specializes in RLHF and SFT data. They pay **$100–500/hour** depending on expertise: medical doctors ($200–500/hr), PhD researchers ($150–350/hr), software engineers ($100–300/hr) [^5].
- **Mercor** ($10B valuation, 2025) matches specialized experts to RLHF tasks, with pay ranging from **$20–400/hour** [^12].

**The pay gap is massive:** Beginner annotation tasks pay $10–15/hour, while domain expert roles pay $200+/hour — a **10–20x difference** based purely on expertise [^12].

---

## 2. Daily Workflow of a Domain Expert

### 2.1 Hour-by-Hour Breakdown (Based on JD Analysis and Platform Descriptions)

Based on the responsibilities outlined in ByteDance JDs and RLHF platform workflows, a typical day for an AI Training Expert (domain specialist level) might look like:

| Time Block | Activity | Tools/Outputs |
|-----------|----------|---------------|
| **09:00–10:00** | Review overnight model evaluation results, check new annotation tasks queued | Evaluation dashboard, Slack/Feishu |
| **10:00–12:00** | **Deep evaluation work**: Systematically test model on assigned domain scenarios, document failures, score outputs against rubric | Custom evaluation interface, Rubric docs, Spreadsheet |
| **12:00–13:30** | Lunch + async review of team annotation quality | Mobile annotation app |
| **13:30–15:00** | **Produce training data**: Write engineering-grade example code, create high-quality Q&A pairs, refine prompt templates | IDE (VS Code), Git, Annotation platform |
| **15:00–16:00** | **Cross-functional sync**: Meet with ML engineers to discuss model weaknesses, review training data effectiveness | Feishu/Slack, Confluence, Data analysis tools |
| **16:00–17:30** | **Analysis and reporting**: Compile error patterns, categorize model weaknesses, draft improvement suggestions | Jupyter, Excel, Markdown |
| **17:30–18:00** | Submit daily deliverables, update task tracker, handoff to QA | Project management tool |

**Note:** This is a **specialist** workflow. Basic annotators spend 80%+ of their time on repetitive labeling tasks (e.g., 10–20 simple classifications per hour, or 5–10 bounding boxes per hour) [^15]. Domain experts spend only 30–40% on direct labeling, with the majority on analysis, guideline development, and cross-functional communication.

### 2.2 Workflow Variations by Company Type

**Chinese Big Tech (ByteDance, Baidu, Alibaba):**
- Heavy emphasis on **data flywheel** — user feedback from production apps (Doubao, Wenxin, Qwen) feeds back into training data pipelines [^18]
- Internal toolchains (ByteDance uses DataLeap, ByteHouse, and custom annotation platforms) [^18]
- Six-month performance reviews for AI teams; frontier research teams have longer cycles [^18]

**AI Startups (Moonshot, DeepSeek):**
- Smaller teams, more end-to-end ownership
- DeepSeek specifically emphasizes **"data distillation + human expert feedback"** and focuses on high-quality reasoning data with a 3:1 ratio of reasoning to non-reasoning data [^14]
- Direct collaboration with core algorithm researchers

**International Platforms (Scale AI, Surge AI):**
- Project-based work, often remote
- Contractors work through platform interfaces
- Emphasis on throughput + quality metrics (inter-rater agreement κ > 0.8) [^7]

---

## 3. Output Artifacts (Concrete Examples of What They Produce)

### 3.1 Core Deliverables

Based on job descriptions, platform documentation, and research papers, an AI Training Expert produces these tangible artifacts:

| Artifact Type | Description | Example Format |
|--------------|-------------|----------------|
| **Evaluation Rubrics** | Structured scoring guidelines for model outputs | Markdown/JSON with dimension definitions, score descriptions, and examples |
| **Annotated Datasets** | Labeled training data with quality metadata | JSONL, CSV, or proprietary platform format with annotations, confidence scores, reviewer IDs |
| **Error Analysis Reports** | Categorized model failures with root cause analysis | Structured markdown with tables, error taxonomy, frequency counts, severity ratings |
| **Example Code Repositories** | Engineering-grade, reusable code examples for training | Git repo with README, unit tests, comments, multiple difficulty levels |
| **Prompt Templates** | Standardized prompts for data generation or evaluation | YAML/JSON with variable slots, few-shot examples, system prompts |
| **Annotation Guidelines** | Detailed instruction manuals for annotator teams | Confluence/Notion doc with rules, edge cases, examples of correct/incorrect labels |
| **Improvement Proposals** | Formal recommendations for model training adjustments | Structured report with problem statement, evidence, proposed solution, expected impact |
| **Quality Metrics Dashboards** | Tracking annotation quality, inter-rater agreement, model performance trends | Tableau/Excel with κ scores, accuracy trends, throughput stats |

### 3.2 Evaluation Rubric Example (Code Generation Task)

Based on industry rubric design practices [^7][^8], a code evaluation rubric might include these dimensions:

```markdown
## Code Quality Rubric

### Dimension 1: Correctness (Weight: 40%)
- 5: Code compiles and runs correctly on all test cases
- 4: Minor edge case failure (1/10 test cases)
- 3: Partial correctness, core logic works but has significant bugs
- 2: Major logical errors, code does not solve the problem
- 1: Completely wrong or irrelevant code

### Dimension 2: Code Style & Readability (Weight: 20%)
- 5: Follows PEP 8 (or language-specific style guide), meaningful variable names, appropriate comments
- 4: Mostly clean, minor style issues
- 3: Inconsistent formatting, some unclear naming
- 2: Poor formatting, cryptic names, missing comments on complex logic
- 1: Unreadable, no structure

### Dimension 3: Efficiency (Weight: 15%)
- 5: Optimal time/space complexity for the problem
- 4: Good but not optimal (e.g., O(n log n) vs possible O(n))
- 3: Acceptable but unnecessarily complex
- 2: Inefficient, would fail on large inputs
- 1: Exponential complexity on problems solvable in polynomial time

### Dimension 4: Error Handling (Weight: 15%)
- 5: Comprehensive input validation, graceful error handling
- 4: Basic validation, handles common errors
- 3: Some validation but missing edge cases
- 2: Minimal error handling
- 1: No error handling, crashes on invalid input

### Dimension 5: Reusability (Weight: 10%)
- 5: Modular design, clear interfaces, easily extensible
- 4: Mostly modular, minor coupling issues
- 3: Some reusable components but mixed with logic
- 2: Monolithic, hard to reuse
- 1: Spaghetti code
```

### 3.3 Code Example Quality Standards

For code used as LLM training data, quality standards include [^9][^16]:

- **Specificity**: Instructions must contain sufficient detail for the model to satisfy the request
- **Coherence**: Internal requests within the instruction should have logical connections
- **Solvability**: The request must be solvable with available tools/APIs
- **Parameter Alignment**: API call parameters must be correctly extracted or inferred from the instruction
- **Sufficiency**: The code must cover all aspects of the instruction
- **Minimality**: Code should use the minimum number of steps/calls necessary
- **Format Compliance**: Follows language-specific style guides (PEP 8 for Python, etc.)
- **Test Coverage**: Includes unit tests for core logic
- **Documentation**: Comments explain "why" not just "what"

---

## 4. Expert vs. Annotator: The Skill Gap

### 4.1 The Fundamental Divide

The distinction between a basic data annotator and a domain expert is stark and well-documented in both Chinese and international contexts:

| Dimension | Basic Annotator | Domain Expert |
|-----------|----------------|---------------|
| **Education** | High school – Bachelor, any major | Bachelor – PhD, relevant field (CS, linguistics, domain specialty) |
| **Experience** | 0–1 year, no domain requirement | 3+ years, full project lifecycle experience [^17] |
| **Primary Task** | Follow rules, label data, hit quotas | Design rules, evaluate quality, analyze failures, propose improvements |
| **Compensation** | ¥3,000–8,000/month ($400–1,100) or $10–15/hr | ¥20,000–50,000/month ($2,700–7,000) or $100–500/hr [^12] |
| **Decision Authority** | None — follows guidelines exactly | Defines guidelines, arbitrates disagreements, approves edge cases |
| **Code/Technical Skills** | Usually none required | Python, data analysis, understanding of ML training pipelines |
| **Output Type** | Raw labeled data | Analysis reports, guidelines, code examples, training strategies |

### 4.2 Why the JD Requires 3+ Years and Full Project Experience

The requirement for "3+ years experience and full project experience" in the Moonshot JD reflects several realities:

1. **Edge case judgment**: Only someone who has shipped real projects knows where models fail in practice. A junior annotator can follow a rubric; a senior expert knows when the rubric is wrong.

2. **Cross-functional communication**: Experts must translate model failures into actionable feedback for ML engineers. This requires understanding both the domain (e.g., UE5 game development) and the training process.

3. **Quality calibration**: Experts serve as the "golden standard" against which annotator teams are measured. Their inter-rater agreement scores (Cohen's κ) must be > 0.8 to be reliable [^7].

4. **Tool creation**: Experts build the infrastructure (guidelines, templates, evaluation frameworks) that enables scaling annotation to hundreds of workers.

5. **Data flywheel design**: In Chinese big tech, experts are expected to design feedback loops where production user data continuously improves training data [^18].

---

## 5. Evaluation Rubrics and Methodologies

### 5.1 The Rubric-Centered Evaluation Paradigm

The industry has shifted from intuition-based evaluation to **structured rubric-based evaluation** [^7]. A rubric is a structured guide that defines what "good" looks like for each model output dimension, consisting of:

1. **Dimension list** (e.g., "Does code compile?", "Are comments included?")
2. **Performance descriptors** per dimension (e.g., "Yes / Yes (with warnings) / No")
3. **Scoring rules** mapping performance to numerical values [^7]

### 5.2 Multi-Layered Evaluation Metrics

Industry practice uses a **three-tiered metric system** [^8]:

**L1: Business-Level Metrics (Pass/Fail Thresholds)**
- OOD (Out-of-Distribution) Answer Success Rate ≥ 65%
- Multi-turn Completion Rate ≥ 75% (85% for high-risk scenarios like customer service) [^8]

**L2: Automatic Metrics (Quantitative)**
- **Loss / Perplexity**: Training convergence monitoring
- **Accuracy**: Classification tasks
- **BLEU**: Translation quality (n-gram overlap with reference)
- **ROUGE**: Summarization quality
- **GPT-4 Judge / LLM-as-Judge**: Automated scoring of open-ended outputs using rubric prompts [^8]

**L3: Human Evaluation (Qualitative)**
- **Preference Comparison (A/B)**: Which model output is better?
- **Rubric Scoring**: Human experts score each dimension
- **Inter-rater Agreement**: Cohen's κ or Fleiss' κ must exceed 0.7–0.8 for reliability [^7]

### 5.3 Specialized Evaluation Frameworks

Different organizations have developed their own frameworks:

- **Google ML Test Score**: 28 independent checks converted into an executable scorecard, improving accuracy by double digits and catching "hidden data drift" early [^7]
- **Microsoft RUBICON**: Uses LLMs to propose candidate evaluation metrics, then refines into rubrics, improving precision by 18% over previous methods [^7]
- **Databricks RAG Evaluation**: GPT-4 with explicit rubric prompts scores thousands of Q&A pairs per hour with >80% expert agreement [^7]
- **TRAIL (Patronus AI)**: Categorizes AI agent errors into 3 classes and 21 subtypes, finding that even top models have only 11% accuracy on error identification tasks [^19][^20]

### 5.4 Error Taxonomy (Model Weakness Categories)

Based on the TRAIL framework and industry practice, model weaknesses are categorized as [^19]:

**Class 1: Output Generation Errors (42% of all errors)**
- Pure language hallucinations
- Format errors
- Content policy violations
- Incorrect reasoning chains

**Class 2: System Execution Errors**
- Configuration errors
- API failures (rate limits, auth errors)
- Resource management (memory leaks, infinite loops)

**Class 3: Planning and Coordination Errors**
- Context management failures (forgetting prior conversation)
- Resource abuse (redundant tool calls)
- Goal deviation (drifting from original task)
- Task coordination failures (in multi-agent systems)

---

## 6. Improvement Report Structure

### 6.1 Standard Report Template

Based on ByteDance JD requirements ("output valuable analysis reports") and industry best practices, a structured improvement report includes:

```markdown
# Model Improvement Report — [Domain] — [Date]

## 1. Executive Summary
- Problem statement in one sentence
- Severity rating (P0–P3)
- Recommended action and expected impact

## 2. Evidence
- Quantitative: Failure rate on specific task type, performance degradation metrics
- Qualitative: Representative failure examples (anonymized)
- Comparative: How baseline model performs vs. current model

## 3. Root Cause Analysis
- Error taxonomy classification (see Section 5.4)
- Data analysis: Is this a training data issue, architecture limitation, or inference problem?
- User impact assessment

## 4. Improvement Recommendations
- Data side: Specific data to add, modify, or remove
- Model side: Architecture or training paradigm suggestions (if applicable)
- Inference side: Prompt engineering or decoding strategy adjustments
- Priority ranking with cost/benefit estimate

## 5. Implementation Plan
- Owner assignment
- Timeline
- Success metrics (how to verify the fix worked)
- Risk assessment

## 6. Appendices
- Raw evaluation data
- Rubric used
- Annotated examples
```

### 6.2 Feedback Loop Integration

The report doesn't end in a vacuum. Industry practice follows this flow [^10]:

1. **Expert produces report** → Submits to ML engineering team
2. **Engineering triage** → Validates findings, estimates implementation cost
3. **Data team action** → Sources or generates recommended training data
4. **Model retraining** → Incorporates fixes into next training run
5. **Validation** → Expert re-evaluates on same task set to verify improvement
6. **Documentation** → Updates rubrics and guidelines based on learnings

---

## 7. Tools and Platforms

### 7.1 Annotation and Evaluation Platforms

| Tool | Type | Best For | Cost |
|------|------|----------|------|
| **Label Studio** | Open-source (self-hosted) | Multi-modal projects, custom workflows, RLHF | Free (self-hosted) / $25–300/mo (cloud) [^15] |
| **Prodigy** | Licensed software | NLP-focused, active learning, Python teams | $300–1,200/year [^15] |
| **Scale AI** | Managed service | Production ML, rapid turnaround, quality guarantees | $0.25–$5/sample, $500–2,000/project min [^15] |
| **Labelbox** | Managed SaaS | Computer vision, 3D/point cloud, model-assisted | $2–5/sample [^15] |
| **Surge AI (Taskup.ai)** | Expert contractor platform | High-skill RLHF, domain experts, PhD-level | $100–500/hr for experts [^5] |
| **CVAT** | Open-source | Video, 3D, computer vision | Free [^15] |
| **HumanSignal Platform** | Enterprise | Auto-labeling with human-in-the-loop review | Custom enterprise pricing |

### 7.2 Daily Workflow Tools

- **Communication**: Feishu (ByteDance/Moonshot), Slack, Lark
- **Code/IDE**: VS Code, Jupyter Notebook, Git
- **Data Analysis**: Excel, Pandas, Tableau, ByteHouse (ByteDance)
- **Project Management**: Jira, Confluence, custom internal tools
- **ML Experiment Tracking**: Weights & Biases, TensorBoard, MLflow
- **Model Evaluation**: OpenCompass, lm-eval-harness, custom evaluation pipelines

### 7.3 Chinese-Specific Infrastructure

- **ByteDance**: DataLeap (data development governance), ByteHouse (OLAP), custom A/B testing platform [^18]
- **Baidu**: PaddlePaddle framework, Baidu AI Studio
- **Alibaba**: ModelScope (open model community), PAI (machine learning platform)
- **DeepSeek**: Custom RLHF pipeline with data distillation focus [^14]

---

## 8. Org Structure and Career Path

### 8.1 Where Data Training Experts Sit in the Organization

**Chinese Big Tech Structure (ByteDance, Alibaba, Baidu):**

```
AI Department (e.g., ByteDance Seed, Alibaba Qwen Team, Baidu TPG)
├── Algorithm Research (pre-training, post-training, RL)
├── Engineering (infrastructure, training frameworks)
├── Data Team ← YOU ARE HERE
│   ├── Data Strategy (senior experts, guideline design)
│   ├── Data Production (annotators, quality control)
│   ├── Data Engineering (pipelines, automation, PE/Agent tools)
│   └── Evaluation & Analysis (model evaluation, error analysis)
├── Product (C-end and B-end applications)
└── Operations (user feedback, data flywheel)
```

**Key organizational insight:** In ByteDance, the AI Lab was merged into the Seed team in 2024 to consolidate AI R&D forces [^18]. Baidu's structure is more fragmented — training, product, and B-solution teams sit in different business groups, causing cross-department coordination friction [^18].

**Startup Structure (Moonshot, DeepSeek):**
- Flatter, more integrated teams
- Data experts work directly with algorithm researchers
- Less silo between "data" and "model" — everyone is expected to understand the full pipeline

### 8.2 Career Progression

Based on the national occupational standard (L1–L5) and industry JDs [^11]:

| Level | Title | Key Capabilities | Salary Range (China) |
|-------|-------|------------------|---------------------|
| L1 | Junior Annotator | Basic data collection, simple labeling, tool operation | ¥3,000–6,000/mo |
| L2 | Data Annotator | Independent labeling, quality self-check, guideline adherence | ¥6,000–10,000/mo |
| L3 | AI Training Specialist | Data evaluation, guideline development, cross-team collaboration, basic PE | ¥10,000–20,000/mo |
| L4 | AI Training Expert | Full project ownership, rubric design, model weakness analysis, data strategy | ¥20,000–40,000/mo |
| L5 | Senior Expert / Manager | Team leadership, training framework design, strategic data planning, mentoring | ¥40,000–80,000/mo |

**International contractor track:** Beginners ($10–15/hr) → Mid-tier ($20–40/hr) → Domain experts ($100–500/hr) [^12]. The ceiling is higher for contractors but lacks benefits and stability.

### 8.3 Compensation Data Points

- **AI industry average recruitment salary in China (Q3 2024):** ¥12,768/month, median ¥10,500 [^12]
- **AI engineer average:** ¥21,930/month [^12]
- **Specialized roles (navigation algorithms, deep learning, NLP):** Highest pay brackets [^12]
- **International PhD-level RLHF:** $100–500/hour (~$15,000–75,000/month if full-time) [^5][^6]
- **Data annotation engineer average (2022):** ¥6,030/month, but 3–5 year experience jumps to ¥17,300/month [^12]

---

## 9. Key Takeaways for UE5 Expert

### 9.1 What the Moonshot JD Actually Wants

Reading between the lines of the "游戏开发专家（AI 训练方向）" position:

1. **Not a game developer role** — It's a data training role with game domain expertise. You won't be building games; you'll be teaching the model to understand, evaluate, and generate game-related content.

2. **Three core deliverables** map directly to industry standards:
   - **"Evaluate model capability"** → Rubric-based evaluation, error taxonomy, structured reporting
   - **"Write example code"** → Engineering-grade, reusable code repos with tests and documentation
   - **"Create improvement suggestions"** → Formal improvement reports with root cause analysis and implementation plans

3. **The "3+ years, full project experience" requirement** means they need someone who:
   - Has shipped a real UE5 project (knows where the bodies are buried)
   - Can identify nuanced failures (e.g., "this Blueprint graph is technically valid but follows anti-patterns that would fail in multiplayer")
   - Can communicate with ML engineers (understands training pipelines, data formats, evaluation metrics)

### 9.2 How to Position Yourself

| Your Asset | How to Frame It |
|-----------|-----------------|
| UE5 project experience | "Domain expertise in real-time 3D graphics pipelines, asset workflows, and engine internals" |
| Shader/graphics knowledge | "Ability to evaluate and generate technically correct rendering code" |
| Blueprint + C++ dual capability | "Can assess both visual scripting and code-based solutions across skill levels" |
| Problem-solving obsession | "Expert error pattern recognition — knows where models fail on complex technical tasks" |
| Mathematical rigor (Jacobian, change-of-variables) | "Can verify correctness of mathematical reasoning in model outputs" |
| "WTF is X" habit | "Ensures precise, unambiguous training data and evaluation criteria" |

### 9.3 Immediate Actions to Prepare

1. **Study RLHF and SFT basics**: Understand how models are trained from human feedback. You don't need to implement it, but you need to know what "preference data" and "reward model" mean.

2. **Practice rubric design**: Take a UE5 coding task and design a 5-dimension rubric (correctness, style, efficiency, error handling, reusability). Test it by scoring ChatGPT/Claude outputs.

3. **Build a sample code repository**: Create 10–20 UE5 code examples ranging from beginner (simple Blueprint) to advanced (custom render pass, compute shader). Include tests, comments, and difficulty tags.

4. **Document failure modes**: List 20 ways an LLM fails on UE5 tasks (hallucinated APIs, wrong version syntax, anti-patterns, missing error handling). This is your error taxonomy.

5. **Learn prompt engineering**: Practice writing system prompts and few-shot examples that elicit correct UE5 code from current models. Document what works and what doesn't.

6. **Engage with Chinese AI community**: Follow Moonshot, DeepSeek, ByteDance Seed team publications. Understand their specific technical approaches (e.g., DeepSeek's reasoning data focus, Moonshot's long-context work).

---

## Footnotes

[^1]: ByteDance. "AI数据训练专家（翻译方向）" Job Description. Zhaopin. https://www.zhaopin.com/jobdetail/CC469217510J40717299901.htm

[^2]: ByteDance. "AI技术数据专家-AI数据与安全" Job Description. Zhaopin. https://www.zhaopin.com/jobdetail/CC469217510J40789822201.htm

[^3]: ByteDance. "大模型Agent数据运营专家-DMC" Job Description. Zhaopin. https://www.zhaopin.com/jobdetail/CC469217510J40724988901.htm

[^4]: ByteDance. "AI搜索数据专家（综合搜索方向）" Job Description. Zhaopin. https://www.zhaopin.com/jobdetail/CC469217510J40849365901.htm

[^5]: Lemon.io. "The Role of RLHF Platforms in AI Advancement." 2026-05-25. https://lemon.io/blog/rlhf-platforms/

[^6]: Xiaoyuzhou FM. "逐句讲解DeepSeek-R1、Kimi K1.5、OpenAI o1技术报告." 2025-02-04. https://www.xiaoyuzhoufm.com/episode/67a1b697247d51713c868367

[^7]: CSDN Blog. "Rubric第一讲：评分量表（Rubrics）如何帮助提升大模型可靠性." 2026-01-11. https://blog.csdn.net/yimianqianshi/article/details/156823602

[^8]: CSDN Blog. "大模型精度评估实战：任务集设计、指标体系与对比评测流程." 2025-04-13. https://blog.csdn.net/sinat_28461591/article/details/147158615

[^9]: Moonlight. "Quality Matters: Evaluating Synthetic Data for Tool-Using LLMs." 2025-03-21. https://www.themoonlight.io/zh/review/quality-matters-evaluating-synthetic-data-for-tool-using-llms

[^10]: 讲师台. "结构化反馈机制." 2025-03-31. https://www.jiangshitai.com/rc/3109.html

[^11]: 搜狐. "《人工智能训练师》国家职业技能标准-职业编码：4-04-05-05." 2025-08-30. https://www.sohu.com/a/864599391_121798711

[^12]: RemoteStack. "Get Paid to Train AI — RLHF Jobs & Platforms." June 2026. https://remotestack.in/ai-training-jobs

[^13]: 新华网. "用时间积累换突破——月之暗面专注通用人工智能领域." 2025-08-12. http://www.news.cn/tech/20250812/b7cd492c960a48cd80f360c938af0908/c.html

[^14]: CAICT. "DeepSeek开启数据标注的新范式." 2025. https://www.caict.ac.cn/kxyj/qwfb/ztbg/202508/P020250829585535422955.pdf

[^15]: DeployBase. "Best Data Labeling Tools 2026: Label Studio, Scale AI, Labelbox, Prodigy, CVAT, Supervisely." 2026-03-13. https://deploybase.ai/articles/best-data-labeling-tools

[^16]: 全国数据标准化技术委员会. "高质量数据集质量评测." 2025. https://sjj.hubei.gov.cn/bmdt/tzgg/202511/P020251110587761615062.pdf

[^17]: 景烁科技. "普通数据标注-模型标注员" Job Description. BOSS Zhipin. https://m.zhipin.com/job_detail/2bd32721fd929ff31H1-3N-0GFBY.html

[^18]: Xiaoyuzhou FM. "字节在跳动，阿里在躁动，AI六小龙被震动." 2024-12-08. https://www.xiaoyuzhoufm.com/episode/67559babbdb9877a973dd607

[^19]: Patronus AI. "TRAIL: Trace Reasoning and Agentic Issue Localization." arXiv:2505.08638v3. 2025.

[^20]: MSN/搜狐. "Patronus AI突破性发现：大模型在复杂任务中的真实弱点，错误率竟高达89%." 2025-07-10. https://www.sohu.com/a/912304177_114765
