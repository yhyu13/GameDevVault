# Plan: AI-Augmented Game Engine Programmer Weekly System

## Goal
1. Analyze every task in the weekly plan for AI augmentation potential
2. Create two managed skills:
   - `ai-assisted-learning`: How to maximize human learning efficiency with AI collaboration
   - `quiz-html-generator`: Convert study content into interactive HTML quizzes (T/F, MCQ, Fill-blank, Multi-select)
3. Generate a working demo HTML quiz from the Lumen paper sample content

## Stage 1 — Analysis (Orchestrator completes)
- Map each weekday task to AI augmentation level (★☆☆☆☆ to ★★★★★)
- Define the golden rule: AI handles low-value friction; human retains high-value cognition
- Document anti-patterns (when NOT to use AI)

## Stage 2 — Skill Creation (Orchestrator completes, parallel)
- `ai-assisted-learning/SKILL.md`: Workflow, principles, weekly task breakdown, anti-patterns
- `quiz-html-generator/SKILL.md`: Input spec, Python generation pipeline, output format, usage examples
- Both skills stored in `~/.kimi/daimon/skills/`

## Stage 3 — Demo Artifact (PythonRun)
- Generate a self-contained HTML file from Lumen paper content
- Include: True/False, Single Choice, Multiple Choice, Fill-in-blank
- Features: immediate feedback, score tracking, wrong answer review, confetti on completion
- Save to workspace as `Lumen-Quiz-Demo.html`

## Output
- Plan: this file
- Skills: 2x SKILL.md
- Demo: 1x .html file
- Report: summary of weekly AI-augmentation map
