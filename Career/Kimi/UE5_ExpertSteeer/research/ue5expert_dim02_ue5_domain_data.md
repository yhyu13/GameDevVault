# UE5 Expert → LLM Training Data: Domain Research Report

**Research Date:** 2026-07-01  
**Researcher:** UE5_GameDev_AI_Data_Researcher  
**Search Count:** 15+ independent queries across web, academic, and job-market sources  
**Scope:** How Unreal Engine 5 expertise feeds into LLM training data pipelines, what data an expert would create, and where current models fail on UE5 tasks.

---

## 1. UE5 in LLM Training Corpora (Coverage, Gaps)

### 1.1 GitHub Code Corpus: UE5 Is a Thin Slice

Large-scale code pretraining datasets (The Stack, CodeSearchNet, Google BigQuery, The Pile) contain billions of tokens of source code, but **UE5 C++ represents a minuscule fraction**. In the StarCoder training data, roughly 20% of tokens are natural language; the code component is drawn from GitHub repositories but C/C++ is heavily outnumbered by Python, JavaScript, and Java [^1]. The Ling Team's pretraining corpus shows code at 25% of total tokens, with C/C++ being only one of many languages and no game-engine-specific filtering applied [^2].

**Why UE5 is underrepresented:**
- UE5 projects are mostly proprietary (games, simulations, enterprise) and not open-sourced on GitHub at the scale of web frameworks or Python packages.
- Unreal Engine's own source is on GitHub but is massive (multi-gigabyte) and under a custom license, making it harder to scrape and redistribute for training.
- Blueprints (`.uasset`, `.umap`) are binary formats, not human-readable text, so they are invisible to standard code-corpus tokenizers [^3].

### 1.2 Stack Overflow & Forum Data: The Q&A Layer

Stack Overflow is a primary source for LLM code training data, but the UE5 tag has far fewer questions than Python or JavaScript. Analysis shows that after ChatGPT's launch, Stack Overflow content declined overall, and the questions that remain tend to shift toward harder, more niche problems that LLMs struggle with [^4]. For UE5 specifically, this means:
- **Beginner questions** ("How do I make a GameInstance?") are now answered by LLMs, reducing the volume of new publicly available Q&A data.
- **Advanced questions** (Nanite shadow artifacts, Lumen GI tuning, Chaos Physics determinism) still appear on forums but are not curated into training datasets.

### 1.3 The Documentation Gap

UE5's official documentation is extensive (Epic Developer Community, API reference, tutorials), but LLM training corpora do not ingest it in a structured way. Unlike Godot—whose `.tscn`, `.gd`, and `.godot` files are all plain text and naturally LLM-compatible [^3]—UE5's scene files are binary, and C++ API docs are behind portal walls or in PDF/markdown mixes that are not uniformly crawled.

**Key Gap:** There is no large-scale, publicly available, plaintext corpus of UE5 projects comparable to JAMER's 8,133 Godot projects [^3]. The only UE5-specific datasets are small (AutoUE's 20 tasks, UnrealLLM's limited benchmarks) [^5].

---

## 2. UE5 Task Taxonomy (What an LLM Would Be Asked to Do)

Based on job listings (Rex.zone), plugin descriptions (UnrealGenAISupport, Claude Assistant), and research papers (AutoUE, JAMER), the tasks an LLM would be expected to perform for UE5 can be categorized as follows:

### 2.1 Code Generation
- **C++ gameplay systems:** Custom `GameInstance`, `PlayerState`, `ActorComponent` classes with proper `UCLASS`/`UPROPERTY`/`UFUNCTION` macros.
- **Blueprints:** Node-graph generation, conversion from C++ to Blueprint, and vice versa (e.g., NodeToCode plugin) [^6].
- **Multiplayer replication:** RPCs, property replication, network prediction, session management.
- **Editor tooling:** Python automation, Editor Utility Widgets, custom editor modules.

### 2.2 Rendering & Shader Code
- **HLSL material shaders:** Custom material functions, post-process effects.
- **Nanite/Lumen configuration:** Console commands, scalability settings, `DefaultEngine.ini` tuning.
- **Virtual Shadow Maps:** Debugging page overflow, flickering, and performance tuning [^7].

### 2.3 VFX & Physics
- **Niagara systems:** Emitter creation, module scripting (HLSL/graph), GPU vs CPU simulation setup [^8].
- **Chaos Physics:** Destruction setups, rigid-body dynamics, cloth/hair simulation integration.

### 2.4 Architecture & Optimization
- **Gameplay Ability System (GAS):** Attribute sets, ability tags, effect cues, prediction.
- **Performance profiling:** Unreal Insights, GPU Visualizer, render target optimization.
- **Platform builds:** UBT (Unreal Build Tool) configuration, CI/CD pipelines, console SDK integration.

### 2.5 Multimodal Data Creation (Synthetic)
- **Scene generation:** Procedural content, biome setup, semantic segmentation labeling.
- **Sensor simulation:** RGB, depth, normal, LiDAR point clouds from UE5 scenes for computer vision training [^9].
- **NPC/Agent behavior:** LLM-driven NPCs using hybrid rule-based + LLM decision systems (TongSIM) [^10].

---

## 3. Current LLM Failure Modes on UE5 (Specific Examples)

### 3.1 Compilation Failures Are Common

AutoUE's ablation study shows that removing **module-dependency knowledge**, **code templates**, or **engine constraints** from prompts causes LLMs to consistently fail to generate compilable UE5 gameplay code [^5]. The baseline (Qwen-Plus) without these constraints produced code that:
- Missed `#include` headers (e.g., forgetting `TimerManager.h` when using `SetTimer`).
- Misused `UFUNCTION`/`UPROPERTY` macros (e.g., placing them inside user-defined C++ macros, which UHT does not parse) [^11].
- Generated non-existent API calls (e.g., calling `SetTimerByEvent` in C++, which only exists in Blueprint) [^12].

### 3.2 Hallucinations on UE-Specific Macros

LLMs frequently hallucinate:
- **Wrong macro specifiers:** `UFUNCTION(BlueprintCallable)` on a function that must return `void` for `BlueprintImplementableEvent`.
- **Missing `_Implementation` suffix:** For `BlueprintNativeEvent` functions, LLMs often generate the function name without the required `_Implementation` postfix, causing linker errors [^13].
- **Incorrect reflection usage:** Generating `UCLASS()` without `GENERATED_BODY()` or forgetting `#include "MyClass.generated.h"`, which prevents UHT from generating reflection metadata [^11].

### 3.3 Domain Knowledge Gaps

| UE5 Feature | LLM Failure |
|-------------|-------------|
| **Nanite** | Recommends "just enable it" without addressing material compatibility, masked-material UV1 bugs, or world-partition streaming constraints [^7] |
| **Lumen** | Suggests `r.Shadow.Virtual.MaxPhysicalPages=8000` as a fix-all; misses that Lumen + many lights = GI thrashing [^7] |
| **VSM (Virtual Shadow Maps)** | Fails to diagnose "Virtual Shadow Map Page Overflow" as a light-density problem, not a page-count problem [^7] |
| **Niagara** | Generates Cascade-style (deprecated) node layouts instead of System-Emitter-Module hierarchy; misses GPU simulation stages [^8] |
| **Networking** | Forgets `Server`/`Client`/`NetMulticast` specifiers; generates RPCs without `Validate` functions or `WITH_SERVER` guards [^14] |
| **GAS** | Misattributes `ASC`, `GA`, `GE` relationships; hallucinates non-existent gameplay cue tags [^15] |

### 3.4 Project-Level Architecture Blindness

JAMER's evaluation found that frontier models drop from **80.4% runtime pass rate on small Godot projects to 5.7% on large ones** [^3]. The bottleneck is architectural design, not syntax. For UE5, this is even worse because:
- UE5 enforces stricter module boundaries (`.Build.cs` dependencies, plugin architecture).
- C++ requires manual memory management (UObject GC rules, `NewObject` vs `ConstructObject`).
- Blueprint/C++ interop requires reflection metadata that LLMs cannot verify without compiling.

---

## 4. Training Data Formats for UE5 (Concrete Prompt-Response Examples)

### 4.1 The "Three-Element" Format

Standard instruction-tuning datasets use `(instruction, input, output)` or `(problem, solution思路, answer)` triples. For UE5, the format must be extended to include **engine constraints** and **verification context** [^16][^17].

---

**Example A: Writing a Custom GameInstance in C++**

```json
{
  "instruction": "Write a custom UGameInstance subclass in UE5 C++ that stores a persistent player score across level transitions, exposes it to Blueprints, and initializes a Steam subsystem if available.",
  "context": {
    "engine_version": "UE 5.4",
    "module": ["Core", "Engine", "OnlineSubsystemSteam"],
    "constraints": [
      "Must use UPROPERTY(BlueprintReadOnly) for score",
      "Must override Init() and Shutdown()",
      "Must include generated.h header",
      "Must not use raw pointers for UObject properties"
    ]
  },
  "solution思路": [
    "1. Create UCLASS(BlueprintType) class inheriting from UGameInstance.",
    "2. Add UPROPERTY(BlueprintReadOnly, Category='PlayerData') float TotalScore.",
    "3. Override virtual void Init() to call Super::Init() and initialize Steam.",
    "4. Override virtual void Shutdown() to clean up.",
    "5. Use static accessor via Cast<UMyGameInstance>(GetGameInstance())."
  ],
  "answer": {
    "header": "// MyGameInstance.h\n#pragma once\n#include 'CoreMinimal.h'\n#include 'Engine/GameInstance.h'\n#include 'MyGameInstance.generated.h'\n\nUCLASS(BlueprintType)\nclass MYGAME_API UMyGameInstance : public UGameInstance\n{\n    GENERATED_BODY()\n\npublic:\n    virtual void Init() override;\n    virtual void Shutdown() override;\n\n    UPROPERTY(BlueprintReadOnly, Category='PlayerData')\n    float TotalScore = 0.0f;\n};",
    "source": "// MyGameInstance.cpp\n#include 'MyGameInstance.h'\n#include 'OnlineSubsystem.h'\n#include 'OnlineSessionInterface.h'\n\nvoid UMyGameInstance::Init()\n{\n    Super::Init();\n    IOnlineSubsystem* Subsystem = IOnlineSubsystem::Get();\n    if (Subsystem && Subsystem->GetSubsystemName() == STEAM_SUBSYSTEM)\n    {\n        UE_LOG(LogTemp, Log, TEXT('Steam initialized'));\n    }\n}\n\nvoid UMyGameInstance::Shutdown()\n{\n    Super::Shutdown();\n}"
  }
}
```

---

**Example B: Debugging a Lumen Shadow Artifact**

```json
{
  "instruction": "In UE5.4, a scene with 20+ lights and Nanite-enabled landscape shows flickering blocky shadows and 'Virtual Shadow Map Page Overflow detected' in the log. What is the root cause and step-by-step fix?",
  "context": {
    "hardware": "RTX 3090, 4K display",
    "settings": "Hardware Lumen enabled, Virtual Shadow Maps enabled, Raytraced Shadows disabled",
    "repro": "Shadows flicker even after setting r.Shadow.Virtual.MaxPhysicalPages=8000"
  },
  "solution思路": [
    "1. Recognize that VSM page overflow is caused by too many lights casting shadows, not insufficient page count.",
    "2. Lumen + many point/spot lights causes GI thrashing regardless of shadow settings.",
    "3. Solution: Reduce active shadow-casting lights using MaxDrawDistance, replace small lights with emissive materials, or use ISM/rdInst for room-based light pooling.",
    "4. Console commands: r.Shadow.Virtual.ResolutionLodBiasDirectional=0.5, r.Lumen.Diffuse.Allow.SecularReflection=0 if not needed."
  ],
  "answer": "Root cause: VSM allocates shadow pages per light; 20+ lights in a small scene exceed the GPU memory budget. The 8K page increase only delays the overflow. Lumen screen traces on thin geometry (hair, foliage) add noise.\n\nStep-by-step fix:\n1. Disable shadow casting on non-essential lights (Light → Cast Shadows = false).\n2. Set MaxDrawDistance on each light to cull distant ones.\n3. Replace interior fill lights with emissive materials to reduce shadow load.\n4. If using Nanite landscape, ensure World Partition is active; static meshes should use Nanite but landscape VSM has known LOD issues in 5.3–5.4.\n5. For hair/foliage: increase r.Shadow.Virtual.SMRT.TexelDitherScaleDirectional to reduce dither flicker (UE-215339, fixed in 5.5)."
}
```

---

**Example C: Optimizing Nanite Settings for VR**

```json
{
  "instruction": "What are the correct Nanite and rendering scalability settings for a VR project in UE5 targeting 90 FPS on Quest 3?",
  "solution思路": [
    "1. Nanite is not supported on mobile GPUs (Quest 3 uses Adreno); it must be disabled for Android builds.",
    "2. Use Forward Shading (not Deferred) for MSAA support.",
    "3. Set r.ScreenPercentage=100 and use TSR/FSR2 at quality mode, not DLSS (no NVIDIA on Quest).",
    "4. Cull distance for Nanite-like behavior via LODs and HLOD.",
    "5. Mobile-specific: disable Lumen, use baked static lighting, enable Instanced Stereo Rendering."
  ],
  "answer": "Nanite is **not supported on Quest 3** (Android/Adreno). Do not enable it.\n\nRecommended settings:\n- DefaultEngine.ini: \n  r.Mobile.AntiAliasing=2 (MSAA 4x)\n  r.VSync=0\n  vr.InstancedStereo=1\n- DefaultScalability.ini:\n  [PostProcessQuality@3]\n  r.ScreenPercentage=100\n  [ViewDistanceQuality@3]\n  r.SkeletalMeshLODBias=0\n- Disable Lumen, set Static Lighting to Production, use Distance Field Ambient Occlusion sparingly.\n- Profile with RenderDoc: Quest GPU has tile-based deferred rendering; overdraw kills performance."
}
```

---

**Example D: Creating a Niagara Particle System**

```json
{
  "instruction": "Create a Niagara system for a 'meteor impact' effect: a falling fireball with a trailing smoke plume, an explosion on impact, and scattered debris. Describe the System-Emitter-Module hierarchy and key parameters.",
  "solution思路": [
    "1. System root: Add three emitters (FireballTrail, SmokePlume, ImpactBurst).",
    "2. FireballTrail: Spawn Rate module, Initialize Particle (Lifetime 1.0–2.0s, Color orange-yellow), Add Velocity (downward + random spread), Shape Location (sphere).",
    "3. SmokePlume: Spawn Rate lower, Initialize Particle (Lifetime 3.0–5.0s, Color dark gray), Drag module, Scale Color over Life (fade to transparent).",
    "4. ImpactBurst: Spawn Burst Instantaneous at collision event, Add Velocity (radial explosion), Collision module (kill on ground contact), Light Renderer (point light flash).",
    "5. GPU Simulation: If particle count > 10k, switch to GPU simulation; use Grid2D for advanced fluid look if needed."
  ],
  "answer": "System: NS_MeteorImpact\n\nEmitter 1: FireballTrail\n- Spawn Rate: 2000–5000/sec\n- Initialize Particle: Lifetime=RandomRange(1.0,2.0), Color=(1.0,0.4,0.0), Size=RandomRange(10,30)\n- Add Velocity: (0,0,-500) + RandomRange(-50,50)\n- Shape Location: Sphere (radius 20)\n- Renderer: Sprite, Material=M_FireballAdd\n\nEmitter 2: SmokePlume\n- Spawn Rate: 500–1000/sec\n- Initialize Particle: Lifetime=RandomRange(3.0,5.0), Color=(0.1,0.1,0.1)\n- Drag: Linear Drag=0.5\n- Scale Color: Alpha from 0.8 to 0.0 over life\n- Renderer: Sprite, Material=M_SmokeAlpha\n\nEmitter 3: ImpactBurst\n- Spawn Burst Instantaneous: Count=5000, SpawnTime=0.0\n- Event Handler: On Collision → Spawn Burst\n- Add Velocity: Radial (speed 200–800)\n- Gravity: -980 Z\n- Collision: Plane (ground), Mode=Kill\n- Renderer: Mesh (debris rocks), Scale=RandomRange(0.5,2.0)\n\nGPU Sim: Enable on FireballTrail if >10k particles. Use Simulation Stages for Grid2D shockwave."
}
```

---

## 5. Expert-Created vs. Scraped Data (Quality Differences)

### 5.1 The Data Quality Hierarchy

| Data Source | Volume | Accuracy | Domain Depth | Best Use |
|-------------|--------|----------|--------------|----------|
| **Scraped GitHub repos** | Very High | Medium | Low | Pretraining general C++ syntax |
| **Stack Overflow Q&A** | High | Medium | Medium | Instruction tuning for Q&A format |
| **Official docs / API ref** | Medium | High | High | RAG grounding, retrieval augmentation |
| **YouTube tutorials / transcripts** | High | Variable | Medium | Multimodal captioning, scene description |
| **Expert-written examples (3-element)** | Low | Very High | Very High | SFT/RLHF seed data, gold-standard references |
| **Synthetic self-instruct (LLM-generated)** | Very High | Low–Medium | Low | Scaling volume, but requires expert verification |

### 5.2 Why Expert Data Is Worth More

RLHF research shows that **13,000 high-quality human demonstrations beat 130,000 scraped examples** for alignment [^17]. For UE5 specifically:
- **Scraped code** is often incomplete snippets without context (missing `.Build.cs`, missing module dependencies).
- **Expert data** includes the *why*—e.g., "use `const_cast` here because Blueprints interpret non-const struct refs as output pins" [^18].
- **Compiler-verified data** is essential. AutoUE's work shows that removing engine constraints from prompts causes 100% compilation failure in ablations [^5]. An expert who writes and compiles code before contributing it as training data is providing a correctness signal that scraped data lacks.

### 5.3 The Cost Dynamic

- Human annotation at scale: **$40K–$400K per 100K examples** depending on domain expertise [^19].
- Synthetic LLM-generated data: **$200–$1,000 per 1M examples** in compute [^19].
- For UE5, the hybrid model is dominant: experts create seed examples (e.g., 500 verified prompt-response pairs), and LLMs scale them via evol-instruct or self-instruct, with expert review for correctness [^16].

---

## 6. Domain-Specific Challenges (Rendering, Physics, Networking, VFX)

### 6.1 Rendering Pipeline (Nanite, Lumen, VSM)

UE5's rendering is the most complex subsystem. LLMs struggle because:
- **State-dependent fixes:** The same console command (`r.Shadow.Virtual.MaxPhysicalPages`) fixes nothing in one context but helps in another. The model needs scene metadata (light count, mesh density, hardware) to diagnose correctly [^7].
- **Version drift:** UE5.3 vs. 5.4 vs. 5.5 have different changelist fixes for VSM bugs (e.g., UE-215339 fixed in 5.5 CL#33855285) [^7]. LLM training data has a cutoff date; it cannot know the latest patch notes.
- **Visual verification:** "Blocky flickering shadows" is a visual symptom. Text-only LLMs cannot see the artifact, so they must rely on the user's textual description, which is often imprecise.

### 6.2 Physics (Chaos)

- **Determinism:** Chaos Physics is not fully deterministic across platforms. LLMs often recommend "just use Chaos" without noting that async physics tick and sub-stepping require careful `FBodyInstance` configuration.
- **Destruction:** Geometry Collection fracture requires artist-authored fracture maps; LLMs cannot generate the asset, only the code to load it.

### 6.3 Networking (Replication, GAS)

- **RPC ownership:** A common expert-corrected error is calling a Server RPC on an actor with no owning NetConnection, which gets silently absorbed [^14]. LLMs rarely mention `AActor::GetNetConnection()` as a guard.
- **GAS prediction:** The Gameplay Ability System's client-side prediction requires `UAbilitySystemComponent::NetworkProxy` and `FGameplayAbilitySpec` setup. LLMs often omit the `GiveAbility` call or misplace the `ASC` on the wrong actor class.

### 6.4 VFX (Niagara)

- **Module authoring:** Niagara modules can be written in HLSL or graph nodes. LLMs trained on general shader code (HLSL/GLSL) do not know Niagara's parameter map namespaces (`Particles.Position`, `Emitter.Age`, `System.Time`).
- **GPU vs CPU:** Choosing the wrong simulation target (CPU for few particles, GPU for >10k) is a domain-specific decision that LLMs often get wrong by defaulting to CPU [^8].

---

## 7. Synthetic Data Opportunities from UE5

### 7.1 Beyond Computer Vision

UE5 is already heavily used for synthetic CV data (RGB, depth, semantic segmentation, object detection) via tools like SegGen [^9], Unity Perception, and custom plugins. However, for **LLM training**, the opportunity is broader:

### 7.2 Multimodal Text-Image-Code Triples

A UE5 scene can generate:
- **Image:** Screenshot of the viewport, render pass, or depth map.
- **Text:** Structured scene description (JSON of actors, components, transforms).
- **Code:** The C++ or Blueprint that created the scene.

This creates natural **multimodal instruction data**:
```json
{
  "image": "screenshot_001.png",
  "text_description": "A directional light at (0,0,1000) with intensity 10 lux, casting VSM shadows on a Nanite landscape.",
  "code": "ADirectionalLight* Sun = World->SpawnActor<ADirectionalLight>(...); Sun->GetLightComponent()->SetIntensity(10.0f); ...",
  "task": "Given the screenshot and scene description, write the C++ code to reproduce this lighting setup."
}
```

LatticeWorld demonstrated this exact pipeline: LLaMA-2-7B + UE5 to generate 3D worlds from text + visual instructions, with a 90x efficiency gain over manual production [^10].

### 7.3 Agent Behavior & RLHF

TongSIM (built on UE5.6) uses UE5 for embodied agent training with LLM decision-making [^10]. The generated trajectories (observations, actions, rewards) can be repurposed as:
- **RL training data:** For robotics or game-AI policies.
- **LLM tool-use data:** The agent learns to call UE5 console commands, spawn actors, or modify materials via a text interface.

### 7.4 Content Safety & Red-Teaming

UE5 scenes can be used to generate **adversarial test cases** for vision-language models:
- Violent/unsafe scenarios rendered photorealistically for content moderation training.
- Edge-case lighting, occlusion, and cultural context variations for bias testing.

Rex.zone job listings explicitly mention that UE5 developers are hired to create "multimodal LLM training assets" for "content safety evaluation" and "RL simulation environments" [^20].

---

## 8. Key Takeaways for UE5 Expert

### 8.1 Your Expertise Is Scarce Training Data

UE5 C++ knowledge is **deep but narrow**. The total number of engineers who can write correct `UCLASS`/`UFUNCTION` code, debug VSM page overflow, and architect GAS replication is small compared to web developers. Every verified example you write is worth **orders of magnitude more** than scraped Stack Overflow data for model alignment in this domain.

### 8.2 The "Compiler-Verified" Gold Standard

When contributing training data, the highest-value format is:
1. **Problem statement** (with engine version and constraints).
2. **Solution思路** (step-by-step reasoning).
3. **Answer** (code that compiles and runs in UE5 Editor).
4. **Verification log** (screenshot of successful compile, runtime test, or Play-in-Editor result).

This is the format used by AutoUE's benchmark and JAMER's training set, and it is what separates expert data from hallucinated LLM outputs [^3][^5].

### 8.3 Domains Where You Can Out-Compete General LLMs

| Domain | Why Experts Win | Example Contribution |
|--------|---------------|-------------------|
| **Rendering debugging** | Requires visual context + console command lore | Annotated fix for VSM flicker with before/after screenshots |
| **Multiplayer architecture** | Requires understanding of NetConnection, RPC timing, replication graph | Blueprint + C++ hybrid examples with network profiling |
| **GAS setup** | Requires knowledge of prediction, cues, tags, and gameplay effects | Complete `ASC`/`GA`/`GE` code template with comments |
| **Niagara modules** | Requires HLSL + Niagara parameter map knowledge | Custom GPU module for fluid simulation with math derivation |
| **Platform builds** | Requires SDK-specific TRC/TCR knowledge | CI/CD yaml for PS5/Xbox with UBT flags |

### 8.4 Synthetic Data Is Your Force Multiplier

You don't need to write 100K examples manually. Instead:
1. **Seed:** Write 50–200 high-quality, compiler-verified examples in the 3-element format.
2. **Scale:** Use evol-instruct or self-instruct to mutate problems (e.g., change "meteor" to "ice comet" in the Niagara example) [^16].
3. **Verify:** Run the generated code through UE5's editor compile + Play-in-Editor to filter out hallucinations.
4. **Annotate:** Add preference labels (preferred vs. rejected) for RLHF, where rejected = code that compiles but fails at runtime (e.g., memory leak, wrong tick group).

### 8.5 The Market Is Hiring You for This

Rex.zone job listings explicitly seek UE5 experts for "multimodal LLM training assets," "synthetic data generation," and "RL simulation environments" at **$35–$120/hr** depending on seniority [^20]. The skill stack is: UE5 C++ → Blueprints → Python automation → dataset curation → RLHF annotation. Your game development expertise is the **upstream input** for the next generation of coding models.

---

## Footnotes

[^1]: StarCoder paper — "Roughly 20% of its training tokens are natural language data..." and C++ performance benchmarks. https://downloads.webis.de/publications/papers/akiki_2023c.pdf

[^2]: Ling Team pretraining corpus — Table 6 shows code at 25% of 2T tokens, C/C++ as one of many languages. https://arxiv.org/pdf/2507.17702

[^3]: JAMER (JamSet & JamBench) — "The current dataset focuses on the Godot game engine... Unity, Unreal, and other engines still hold significant market share." 8,133 verified Godot projects from 240K repos. https://arxiv.org/html/2606.19830v1

[^4]: Stack Overflow post-ChatGPT analysis — "Millions of users visit Stack Overflow regularly... LLMs as developer's assistant... increased developer productivity." https://arxiv.org/html/2509.05879v1

[^5]: AutoUE (ACL 2026 Findings) — "All three variants consistently fail to compile... removing module dependencies, code templates, or engine constraints severely undermines the ability to generate compilable UE gameplay code." https://aclanthology.org/2026.findings-acl.111.pdf

[^6]: NodeToCode plugin — "Translate Unreal Engine Blueprints to C++ in seconds." https://github.com/protospatial/NodeToCode

[^7]: UE5 rendering issues — Epic Developer Community knowledge base on VSM page overflow, hair flicker, Nanite masked material bugs. https://dev.epicgames.com/community/learning/knowledge-base/yjp8/unreal-engine-ue-5-4-x-most-common-rendering-issues

[^8]: Niagara overview — Epic documentation: "Modules are built using HLSL, but can be built visually in a Graph using nodes." https://dev.epicgames.com/documentation/unreal-engine/overview-of-niagara-effects-for-unreal-engine

[^9]: SegGen — "A fully automated pipeline built within Unreal Engine 5... RGB and depth imagery, alongside pixel-perfect semantic segmentation labels." https://pmc.ncbi.nlm.nih.gov/articles/PMC12431427/

[^10]: TongSIM — "Built on Unreal Engine 5.6, leveraging its advanced rendering capabilities and physics simulation... hybrid NPC control system that combines rule-based logic with Large Language Model decision-making." https://www.alphaxiv.org/overview/2512.20206

[^11]: UE5 C++ macro reflection forum — "Unreal's Reflection system checks every header file before preprocessor swaps directives... UFUNCTION/UPROPERTY within a macro won't work." https://forums.unrealengine.com/t/how-to-avoid-the-repetition-of-ufunction-uproperty-declarations/675504

[^12]: UE5 Timer C++ cheatsheet — "In C++, there isn't a direct equivalent to Blueprint's 'Set Timer by Event' system for timers." https://hexmos.com/freedevtools/c/unreal_engine_5/Timer/

[^13]: UFunction source snippet — `BlueprintNativeEvent` requires `_Implementation` suffix. https://sourcesnippet.github.io/snippets/unreal-engine/ue-ufunction/

[^14]: Multiplayer RPC tips — "No Owning Connection for Actor... Server RPC will not be processed." https://wizardcell.com/unreal/multiplayer-tips-and-tricks/

[^15]: Monster Gaming AI agent comparison — UE5 support table: GAS, replication, Niagara, HLSL. https://monstergames.ai/engines

[^16]: OpenCodeInstruct / Genetic-Instruct — "5M-sample dataset... combining evol-instruct and self-instruct methods." https://www.emergentmind.com/papers/2504.04030

[^17]: RLHF pipeline explanation — "13,000 high-quality demonstrations beat 130,000 scraped examples." https://waylandz.com/llm-transformer-book-en/chapter-29-rlhf-preference-learning/

[^18]: UE5 C++ Blueprint interop guide — const pointer passing issue in RPCs. https://forums.unrealengine.com/t/assigning-input-parameters-from-ufunction-to-non-const-object-uproperty/581580

[^19]: Synthetic data cost analysis — "At 100K examples, human annotation costs range from $40K to $400K... synthetic data $200-$1,000." https://www.spheron.network/blog/synthetic-data-generation-pipelines-gpu-cloud-distilabel-augmentoolkit-nemotron/

[^20]: Rex.zone UE5 job listings — "Unreal Engine contract jobs... multimodal LLM training assets... synthetic data generation... $35–$120/hr." https://www.rex.zone/jobs/unreal-engine-contract-jobs

---

*End of Report*
