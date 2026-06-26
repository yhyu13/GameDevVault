# Human-in-the-Loop LLM Self-Improvement: A Practical Guide

> **Context**: This document explains how modern LLM training pipelines use human experts to steer data generation, and how to apply these principles to the UE5 domain-specific model we are building.  
> **Based on**: RLHF, DPO, Self-Instruct, Evol-Instruct, RL-AIF (Constitutional AI), and iterative rejection sampling workflows from 2023-2024 literature.

---

## 1. The Core Paradigm: It's Not "Human Labels Data" Anymore

Old way (pre-2023):
```
Human writes data → feeds to model → model trains once → done
```

Modern way (2024):
```
Model generates candidates → Human judges / steers / filters → 
Model retrains on filtered data → Model generates better candidates → 
Human judges again → ... (iterative loop)
```

The human is not writing data from scratch. The human is **steering the model's own data generation**. This is the fundamental shift.

---

## 2. The Four Mechanisms of Modern HITL Data Generation

### 2.1 Rejection Sampling with Human Criteria (Most Common)

**How it works:**
1. Model generates N candidate answers to the same prompt (e.g., N=8)
2. Human (or LLM-as-judge calibrated by human) scores each candidate
3. Keep the top-k, discard the rest
4. Train the model on the winning candidates
5. Repeat

**Human intervention timing:**
- **Batch-level**: After the model generates a batch of candidates, human reviews the distribution
- **Example-level**: Human spots a particularly bad generation and flags the pattern
- **Criteria-level**: Human realizes "the model keeps getting X wrong" and adds a new filter rule

**What to steer:**
- **Factuality**: Does the answer contain wrong technical details?
- **Structure**: Does it follow the expected format (e.g., "作用/为什么/如果改会怎样")?
- **Depth**: Is it surface-level or does it reach source-code-path depth?
- **Tone**: Does it sound like a confident senior engineer or a vague intern?

**UE5 Example:**
```
Prompt: "Explain Nanite's Cluster Culling"

Candidate A (score: 0.9): "Cluster Culling operates on geometry units 
(~128 triangles) using HZB for occlusion. Source: NaniteClusterCulling.cpp."

Candidate B (score: 0.3): "It's a culling technique that makes things faster."

→ Human (or calibrated judge) keeps A, rejects B.
→ Model learns: specific numbers, source paths, and mechanisms are rewarded.
```

**Key insight:** The model learns not from "what is right" but from "what is *more right than the alternatives*." This is the preference signal.

---

### 2.2 Preference Optimization (DPO / RLHF)

**How it works:**
Instead of scoring single answers, the human provides **pairs**: "Answer A is better than Answer B."

The model learns a **policy** (a probability distribution over answers) that maximizes the chance of producing the preferred answer.

**Human intervention timing:**
- After initial SFT (supervised fine-tuning), when the model can generate plausible but varying-quality answers
- **Not during pre-training** — the model needs to be able to generate candidates first

**What to steer:**
- **Pairwise comparisons**: "Given these two answers, which is better?"
- **Ranking**: Order 4 answers from best to worst
- **Critiques**: "What's wrong with the worse answer?"

**Why this works:**
Humans are much better at comparing two things than at scoring one thing absolutely. "Is this a 7/10?" is hard. "Is this better than that?" is easy.

**UE5 Example:**
```
Prompt: "Why does Nanite need software rasterization?"

Answer A: "For small triangles." (too vague)
Answer B: "Hardware rasterizer uses 2×2 quads, causing overdraw for 
sub-pixel triangles. Software rasterizer in CS handles pixel-accurate 
coverage. Source: NaniteRasterizer.cpp." (specific, sourced)

→ Human labels: B > A
→ Model learns: vague one-liners are worse than specific explanations 
  with source code references.
```

**DPO vs RLHF:**
- **RLHF** (older): Train a reward model from human preferences, then use PPO to optimize the policy. Complex, unstable.
- **DPO** (Direct Preference Optimization, 2023): Skip the reward model. Directly optimize the policy to increase the probability of preferred answers and decrease the probability of rejected answers. Simpler, more stable, works well for domain-specific fine-tuning.

**Recommendation for UE5 project:** Use **DPO** after initial SFT. Your preference data comes from comparing model-generated answers to your expert answers.

---

### 2.3 Self-Play / Constitutional AI (Model Critiques Itself, Human Defines Constitution)

**How it works:**
1. Human writes a "constitution" — a set of principles (not labels)
2. Model generates an answer
3. Model critiques its own answer against the constitution
4. Model revises its answer based on the critique
5. The revised answer becomes training data

**Human intervention timing:**
- **Upfront**: Writing the constitution (one-time, high-leverage)
- **Occasionally**: When the model's self-critique misses something, human adds a new principle

**What to steer:**
- The **constitution**, not individual examples. The constitution encodes the human's values/quality standards.

**UE5 Constitution Example:**
```
"When answering technical questions about UE5:
1. Always include source code file paths when possible.
2. Distinguish between 'runtime behavior' and 'offline Cook behavior'.
3. If explaining an optimization, also explain the trade-off (what it costs).
4. If a feature has limitations, mention them honestly.
5. Use the format: What → Why → Source Code → Trade-off."
```

**Why this is powerful:**
One human writes 10 principles. The model generates 10,000 self-critiques. The human's effort is amplified by 1000x.

**Key paper**: *Constitutional AI: Harmlessness from AI Feedback* (Anthropic, 2022). The same principle applies to domain-specific quality, not just safety.

---

### 2.4 Evol-Instruct / Iterative Complexity Ramping (Human Defines Complexity Levels)

**How it works:**
1. Start with simple questions (e.g., "What is Nanite?")
2. Model or human evolves them into harder questions (e.g., "Compare Nanite's DAG-based LOD to UE4's discrete LOD in terms of memory overhead and popping artifacts")
3. Train on the evolved questions
4. Model gets better at hard questions
5. Evolve again to even harder questions

**Human intervention timing:**
- **Define the evolution operators**: "How do I make this question harder?"
- **Filter evolved questions**: Some evolutions are nonsensical; human removes them
- **Set the ceiling**: Human decides when questions are hard enough for the target domain

**What to steer:**
- **Complexity dimensions**: Add constraints, ask for comparisons, require source code, ask for trade-offs
- **Quality gate**: "Is this evolved question actually answerable by a senior engineer?"

**UE5 Evolution Example:**
```
Level 1: "What is Surface Cache?"
Level 2: "How does Surface Cache's incremental update work?"
Level 3: "Compare Surface Cache's incremental update to full refresh 
          in terms of GPU cost and visual lag."
Level 4: "If CardCapturesPerFrame is doubled, how does the frame time 
          distribution change between Surface Cache update and 
          Screen Probe Gather?"
```

**Key paper**: *WizardLM: Empowering Large Language Models to Follow Complex Instructions* (2023). "Evol-Instruct" method.

---

## 3. The Human Intervention Decision Matrix

| When to Intervene | What to Do | Why It Matters | How AI Learns |
|-------------------|-----------|----------------|---------------|
| **Model can generate plausible but inconsistent quality** | Rejection sampling + preference labeling | Quality variance is the bottleneck; model already knows the domain but doesn't know what's "good enough" | Distribution shifts toward high-quality outputs |
| **Model has systematic errors** | Add constitutional rule + examples of the error + corrected version | Catching error patterns is high-leverage; fixing one pattern fixes thousands of future generations | Policy learns to avoid the error mode |
| **Model answers are too shallow** | Evolve instructions to harder versions + provide deep examples | The model's capacity isn't the limit; the training data's depth is | Model learns to allocate more tokens to reasoning and source references |
| **Model answers lack structure** | Define output format in constitution + provide structured examples | Format consistency is easy for humans to judge but hard for models to learn from raw text | Attention mechanisms learn to follow structural templates |
| **Model hallucinates source code paths** | Fact-check + reward correct paths, penalize wrong ones | Hallucination is the #1 failure mode in technical domains | Reward model (or DPO) learns that specific correct paths are preferred over plausible-sounding wrong ones |
| **New topic emerges** (e.g., UE5.6 new feature) | Human writes seed examples → model generates variations → human filters | Cold-start problem for new knowledge | Model bootstraps from few examples to many via self-generation |

---

## 4. The Specific Mechanics: How AI Actually "Learns from Steering"

### 4.1 Gradient-Level Explanation (Simplified)

When you label "Answer B > Answer A":

**DPO objective** (in plain language):
```
Increase the probability that the model generates B.
Decrease the probability that the model generates A.
Keep the model from changing too much (KL divergence constraint).
```

At the parameter level:
- The model's weights are updated to make the token sequence of B more likely
- The model's weights are updated to make the token sequence of A less likely
- The magnitude of the update depends on how much better B is than A (the preference margin)

**The steering is not explicit programming.** The model doesn't "remember" your label. It changes its internal probability distribution over token sequences so that future generations in similar contexts will statistically resemble B more than A.

### 4.2 Attention Mechanism Interpretation

What the model actually learns from "B > A":
- **"Source code paths are important"**: Attention weights shift to pay more attention to patterns like `Engine\Source\...` in the context
- **"Specific numbers are better than vague terms"**: The model learns that sequences like "128 triangles" are more likely to be in preferred outputs than "a bunch of triangles"
- **"Structure matters"**: The model learns that outputs with markdown headers (##) and bullet points are preferred over wall-of-text paragraphs

This is why **consistent examples** matter more than **volume**. If every preferred answer includes a source code path, the model learns that source code paths are a high-probability feature of "good" answers.

---

## 5. Practical Workflow for the UE5 Project

### Phase 1: Seed Data (Human-Driven)
```
You write 50 high-quality examples using templates
→ train_lora.py (SFT) → model can generate plausible UE5 answers
```
**Human effort**: ~8 hours of writing  
**Output**: Model can talk about UE5 coherently but with variable quality

### Phase 2: Rejection Sampling (Human-Filtered)
```
Model generates 8 answers for each of your 50 prompts
→ You pick the best 1-2 per prompt (or use your expert answers as reference)
→ train_lora.py (SFT on filtered data) → model quality improves
```
**Human effort**: ~2 hours of reviewing  
**Output**: Model's average output quality increases

### Phase 3: Preference Learning (DPO)
```
Model generates 2 answers per prompt
→ You label which is better (or compare to your expert answer)
→ DPO training on pairwise preferences → model learns "what makes a good answer"
```
**Human effort**: ~1 hour of pairwise comparisons  
**Output**: Model learns the *style and depth* of good answers, not just facts

### Phase 4: Constitutional Self-Critique (Human Defines Rules)
```
You write 10 constitutional rules for UE5 answers
→ Model generates answer → critiques itself → revises → train on revisions
→ Human occasionally reviews critiques and adds rules
```
**Human effort**: ~1 hour upfront + 10 min/week maintenance  
**Output**: Model self-corrects based on encoded principles

### Phase 5: Evol-Instruct (Human Defines Complexity)
```
Model evolves simple questions to harder ones
→ You filter the evolved questions (remove nonsensical ones)
→ Model generates answers to hard questions
→ You review and label
→ Train on hard Q&A pairs
```
**Human effort**: ~1 hour of filtering per batch  
**Output**: Model handles senior-level interview questions

### Phase 6: Continuous Iteration
```
Deploy model on interview questions
→ Collect model outputs that users mark as "wrong" or "shallow"
→ Human writes corrected versions or adds constitutional rules
→ Retrain model
→ Repeat
```
**Human effort**: ~30 min/week  
**Output**: Model continuously improves based on real-world usage

---

## 6. Why This Works: The Theory

### 6.1 The Data Scaling Hypothesis is Wrong for Domain Fine-Tuning

OpenAI's claim: "More data = better model"  
Domain fine-tuning reality: **Better data = better model**. The correlation breaks down after ~1,000 high-quality examples.

For UE5 specifically:
- 100 expertly written examples with source code paths > 1,000 auto-extracted markdown paragraphs
- Because the model learns **patterns** ("good answers include source paths"), not facts

### 6.2 The Preference Signal is the Real Teacher

The model doesn't learn from "this is a correct answer about Nanite."  
It learns from "this answer is better than that answer because it's more specific, includes source code, and explains trade-offs."

The **comparison** encodes the human's quality criteria. The model internalizes the criteria as a probability bias.

### 6.3 Human Effort Follows a Power Law

| Iteration | Human Effort | Model Improvement | Effort/Improvement Ratio |
|-----------|-------------|-------------------|------------------------|
| 1 (seed) | 8h | 0 → 60% quality | High |
| 2 (rejection sampling) | 2h | 60% → 75% | Medium |
| 3 (DPO) | 1h | 75% → 85% | Low (high leverage) |
| 4 (constitution) | 1h upfront | 85% → 90% | Very low |
| 5+ (continuous) | 0.5h/week | 90% → 95% | Minimal |

**The first 10 hours get you to 85%. The next 10 hours get you to 95%.** The human effort is front-loaded but the marginal cost of improvement drops rapidly.

---

## 7. Key Papers and Techniques Reference

| Technique | Year | Paper | Use in UE5 Project |
|-----------|------|-------|-------------------|
| **RLHF** | 2022 | *Training language models to follow instructions with human feedback* (Ouyang et al.) | Initial understanding |
| **DPO** | 2023 | *Direct Preference Optimization* (Rafailov et al.) | **Primary preference learning method** |
| **Constitutional AI** | 2022 | *Constitutional AI: Harmlessness from AI Feedback* (Bai et al.) | Self-critique rules for technical depth |
| **Self-Instruct** | 2022 | *Self-Instruct: Aligning Language Models with Self-Generated Instructions* | Generate varied questions from seed |
| **Evol-Instruct** | 2023 | *WizardLM: Empowering Large Language Models to Follow Complex Instructions* | Ramp question complexity |
| **Rejection Sampling** | 2024 | Standard in Llama 3, GPT-4 training | Filter model outputs for quality |
| **LLM-as-a-Judge** | 2023 | *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena* (Zheng et al.) | Calibrate automated evaluation |
| **Iterative DPO** | 2024 | *Iterative Direct Preference Optimization* (Xu et al.) | Multiple rounds of DPO for continuous improvement |

---

## 8. Common Pitfalls to Avoid

1. **"I'll write 1,000 examples myself"** → No. Write 50 great ones, then let the model generate variations. Human effort is the bottleneck.

2. **"I'll just keep doing SFT with more data"** → Diminishing returns. After ~200 examples, SFT plateaus. Switch to DPO or rejection sampling.

3. **"The model should be 100% accurate before deployment"** → Impossible. Deploy at 85% with a feedback loop. Real-world usage reveals edge cases that synthetic data misses.

4. **"I need to label every example perfectly"** → Pairwise comparisons are easier and more effective than absolute scoring. Use DPO, not reward modeling.

5. **"Human-in-the-loop means human reviews everything"** → No. Human defines the constitution, the model self-critiques. Human only intervenes when the model's critique is wrong.

---

## Summary

Modern LLM self-improvement is not about humans writing data. It's about:

1. **Humans writing seed data** (high quality, small volume)
2. **Models generating candidates** (large volume, variable quality)
3. **Humans steering via preferences and constitutions** (judging, not writing)
4. **Models learning the preference distribution** (DPO, not reward models)
5. **Iterating with decreasing human effort** (front-loaded, then self-sustaining)

The human's role shifts from **data writer** to **quality arbiter** to **constitution designer**. The AI does the heavy lifting of generation and variation. The human ensures the direction is correct.

---

> **Next step**: Apply this framework to the UE5 project. Start with Phase 1 (write 50 seed examples using templates), then proceed to Phase 2 (rejection sampling with model-generated variations).
