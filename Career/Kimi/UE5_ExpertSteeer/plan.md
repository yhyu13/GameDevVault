# Plan: UE5 Game Dev Expert Steering for LLM Training

## Goal
Answer: "wtf is human expert steering in LLM training" and map the JD's three responsibilities to concrete workflows, skills, and deliverables.

## JD Core Responsibilities
1. 评估模型能力：基于真实业务场景，系统性评估模型在游戏开发任务上的表现
2. 编写示例代码：输出工程化、可复用的参考实现，作为模型学习的目标
3. 制定改进建议：分析模型在不同类型任务中的不足，沉淀结构化的改进建议，推动能力持续提升

## Stage 1 — Research (Parallel)
Load `deep-research-swarm` guidance. Deploy 3 parallel research workers:

### Worker_A: LLM_Training_Paradigms
**Role**: AI Training Process Researcher
**Mission**: Research how domain experts contribute to LLM training data improvement.
- SFT (Supervised Fine-Tuning): how demonstration data is created, what makes good training examples
- RLHF / DPO / RLAIF: how human preferences shape model behavior
- Data curation: quality filtering, diversity balancing, difficulty grading
- Expert annotation workflows: prompt engineering for experts, annotation interfaces, consensus mechanisms
- **Key output**: A structured overview of where human experts fit in the LLM training pipeline

### Worker_B: UE5_GameDev_AI_Data
**Role**: Game Engine AI Data Researcher  
**Mission**: Research how UE5/game dev expertise is specifically used for AI training.
- What types of UE5/game dev tasks are LLMs being trained on (shader writing, blueprint generation, debugging, optimization)
- Existing datasets: Stack Overflow, GitHub, UE5 documentation, tutorials
- Gaps in current models: where do LLMs fail on UE5 tasks (Nanite, Lumen, Virtual Shadow Maps, Niagara, Chaos Physics)
- How game dev experts create training data (code snippets, step-by-step guides, error case studies)
- **Key output**: Domain-specific analysis of UE5 training data needs and gaps

### Worker_C: Industry_Practices
**Role**: Industry Practice Researcher
**Mission**: Research real-world practices of companies using domain experts for AI training.
- Moonshot AI (Kimi), OpenAI, Anthropic, Google — how they hire and use domain experts
- "Expert steering" vs "data annotation" — what is the actual difference
- Tools and platforms used (Scale AI, Surge AI, internal tools)
- Case studies: GitHub Copilot, Codeium, Amazon CodeWhisperer — how were they trained with dev expertise
- **Key output**: Industry landscape and tooling for expert-driven LLM improvement

## Stage 2 — Synthesis
Consolidate Stage 1 findings into:
1. **Skills Breakdown**: Technical skills, evaluation skills, communication skills needed
2. **Output Framework**: What concrete artifacts the expert produces (evaluation rubrics, example code repos, improvement reports)
3. **Workflow Mapping**: How the three JD responsibilities map to the LLM training lifecycle

## Stage 3 — Final Deliverable
- Markdown report saved to workspace
- Structured breakdown: Skills → Outputs → Workflows
- Concrete examples for UE5 domain
