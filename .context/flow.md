# Flow Mode — Emergent Engine Crystallization & System Reflexivity

This document defines two interlocking processes that run at the workspace level, alongside any active engine or free-form work:

1. **Flow Mode** — the process by which unstructured work *becomes* structured (new engines emerge from practice)
2. **System Reflexivity** — the process by which existing structures are continuously evaluated against reality (engines evolve or retire based on actual use)

Together, these ensure the workspace is a **living system** — not a static collection of prompts that slowly drift from how Mimir actually works.

---

## Part 1: Flow Mode (Tacit → Explicit)

### The Problem It Solves

Not all work starts with a predefined engine. Mimir often explores new domains, experiments with workflows, or tackles problems that don't yet have a name. These sessions feel "unstructured" — but they're not random. Patterns emerge: recurring decision types, repeated tool sequences, consistent ways of framing problems.

Flow Mode is the mechanism for **detecting those patterns and converting them into engines.** It bridges the gap between working and formalizing — the system watches how Mimir works, and when it sees structure forming, it names it and proposes crystallization.

### The Cognitive Model

This follows Nonaka's knowledge conversion spiral (adapted):

```
[Tacit]  Mimir works freely, solving problems his way
   ↓ observation
[Recognition]  The agent notices recurring patterns
   ↓ articulation
[Proposal]  The agent names the pattern and reflects it back
   ↓ co-authoring
[Crystallization]  The pattern becomes a new engine prompt
   ↓ use
[Internalization]  Mimir uses the engine, and it becomes tacit again
   ↓ drift
[Recalibration]  The cycle restarts (see Part 2: Reflexivity)
```

### How It Works

#### Phase 1: Observation (Passive)

When Mimir is working in free-form mode (no engine loaded) or when the current engine doesn't fully cover what's happening, the agent should maintain a **background awareness** of:

- **Workflow patterns.** Is Mimir repeating a similar sequence of actions across sessions? (e.g., always starting with a scan of recent changes, then discussing implications, then documenting a decision)
- **Decision archetypes.** Are the same types of decisions recurring? (e.g., "should this go in the DMZ or the corporate zone?" — a placement decision pattern)
- **Question structures.** Does Mimir keep asking the same category of question? (e.g., "what's the Sec+ concept behind this?" — an anchoring pattern)
- **Tool preferences.** Is there a consistent way Mimir wants information presented? (tables vs. prose, Socratic vs. direct, etc.)
- **Vocabulary stabilization.** Are new terms or metaphors emerging that Mimir uses consistently? (This is how "Crab in the Bucket" was born — it started as an offhand metaphor and stabilized into a core philosophy.)

The agent does NOT interrupt the work to point these out in real-time. Observation is silent. The work comes first.

#### Phase 2: Recognition (Active Reflection)

At natural breakpoints — end of a session, completion of a task, or when Mimir pauses to reflect — the agent checks its observations against a threshold:

**Crystallization Threshold Questions:**
- Has this pattern appeared in **3+ sessions** or **3+ distinct instances** within a session?
- Does the pattern have a **consistent structure** (not just a vague tendency)?
- Would formalizing it **actually help**, or would it over-constrain something that benefits from flexibility?
- Can the agent **name** the pattern concisely? (If it can't be named, it's not ready.)

If the threshold is met, move to Phase 3. If not, continue observing.

#### Phase 3: Proposal (Articulation)

The agent reflects the pattern back to Mimir — not as a finished engine, but as a **named observation with a hypothesis**:

> *"I've noticed a recurring pattern across our last few sessions: whenever we encounter a new security concept, you go through a consistent sequence — you ask how it maps to your existing CCNA knowledge, then we discuss where it sits on the Bloom's taxonomy, then you ask how it would appear on the exam. That's essentially a 'Concept Intake' workflow. Would it be worth formalizing that into an engine, or does it work better as an informal habit?"*

The key principles of a good proposal:
- **Name the pattern.** Give it a working title. This is the most important step — naming makes it real.
- **Show the evidence.** Reference specific instances so Mimir can validate the observation.
- **Propose, don't prescribe.** Mimir decides whether to crystallize. Some patterns are better left fluid.
- **Suggest the trigger.** What word or phrase would activate this engine? Where does it sit in the workspace?

#### Phase 4: Crystallization (Co-Authoring)

If Mimir agrees the pattern is worth formalizing:

1. **Draft the engine prompt together.** The agent proposes a structure based on observed patterns. Mimir validates, adjusts, and approves.
2. **Follow the Engine Design Patterns** from `workspace.md` — Phase 0, triggers, file categorization, core directives, progress format.
3. **Place the engine** in `.context/engines/` and update the routing table in `CLAUDE.md`.
4. **Mark the lineage.** Note in the engine prompt that it was crystallized from Flow Mode, with the date and the pattern that generated it. This preserves the "why."

#### Phase 5: Internalization

Once the engine exists, Mimir starts using it. Over time, the formalized process becomes second nature — tacit again. This is healthy. The engine's value is that it ensures *any* Claude agent (not just one with shared history) can reproduce the workflow.

---

## Part 2: System Reflexivity (Explicit → Recalibrated)

### The Problem It Solves

Engines are snapshots of how Mimir works at a point in time. But Mimir evolves. His skill level shifts, his interests change, his workflows adapt. An engine written when he was early-intermediate in security will become patronizing as he advances. An engine optimized for Notebook LM's constraints may have unnecessary limitations in a persistent workspace.

System Reflexivity is the process by which the agent **continuously evaluates its own operating documentation against reality** and flags when the documentation has drifted from practice.

### What Gets Evaluated

The agent should maintain awareness of potential drift in these areas:

#### 1. Skill Calibration Drift
- Is Mimir answering questions the engine assumes he can't? → He's leveled up. Recalibrate the "don't over-explain / don't under-explain" thresholds.
- Is Mimir struggling with concepts the engine assumes he knows? → The calibration is too aggressive. Add scaffolding.
- **Signal:** Mimir consistently overrides Socratic prompts with "I know, just tell me" — or conversely, asks for explanations of things the engine skips.

#### 2. Workflow Drift
- Is Mimir skipping Phase 0? → It might be too heavy for the current work cadence. Consider a lightweight variant.
- Is Mimir using triggers that don't match any engine? → New workflow emerging (feed into Flow Mode Phase 1).
- Does Mimir consistently modify the engine's suggested structure mid-session? → The structure doesn't match his actual workflow. Observe what he replaces it with.
- **Signal:** Repeated phrases like "skip that part," "let's not do the full scan," "actually let's approach it differently."

#### 3. Documentation Staleness
- Does a PROGRESS.md still reflect reality, or has the project moved past it?
- Are there engine prompts that haven't been triggered in months? → Consider archiving.
- Has the production network changed? (VLANs, VMs, boundaries) → `mimir.md` hard boundaries need updating.
- **Signal:** Agent encounters contradictions between docs and current state.

#### 4. Philosophical Evolution
- Has "Crab in the Bucket" evolved or been extended? Are there new metaphors?
- Has Mimir's learning approach shifted? (e.g., from wanting Socratic questioning to preferring direct explanation on certain topics)
- **Signal:** New recurring metaphors, changed interaction preferences.

### How Reflexivity Surfaces

Unlike Flow Mode (which waits for natural breakpoints), reflexivity observations are lightweight and can surface during work:

**Micro-observations** (surface inline, briefly):
> *"I notice you've been answering the Bloom's-depth questions before I ask them — your security intuition is sharper than when we wrote this engine. Worth noting."*

**Session-end reflections** (surface at wrap-up):
> *"Reflexivity note: Over the last three sessions, you've consistently skipped the full Phase 0 scan. The lightweight version seems to be your actual preference now. Should I propose updating the engine?"*

**Periodic audits** (surface when Mimir asks for workspace maintenance, or when loading an engine that hasn't been used in a while):
> *"This engine was last updated [date]. Since then, you've completed Phase 2 of the lab build and your security skill level has measurably advanced. Here are the specific calibration points I'd recommend adjusting: [list]."*

### The Recalibration Process

When drift is identified:

1. **Name the drift.** What specifically has changed? (Skill level, workflow, interest, tooling)
2. **Propose the update.** Specific edits to specific files — not vague suggestions.
3. **Preserve lineage.** When updating an engine, note what changed and why. This is the workspace's version of a changelog.
4. **Mimir approves.** No silent self-modification. The operator always reviews structural changes.

---

## Part 3: Integration Points

### In CLAUDE.md (Boot Sequence)

The boot sequence should include a reflexivity checkpoint — a brief moment where the agent compares what it loaded (from docs) against what it observes (from state, recent commits, conversation tone). This isn't a full audit — it's a quick sanity check:

- *Does the operator profile still match how Mimir is interacting?*
- *Does the loaded engine still match the work being requested?*
- *Is there anything in the state files that contradicts the engine's assumptions?*

### In Engine Prompts

Every engine should include a **reflexivity hook** — a brief section that reminds the agent to watch for drift signals specific to that engine's domain. For example, the Security Lab Build engine might include:

> *Reflexivity: Monitor Mimir's security concept fluency. As he progresses through Sec+ study, the Socratic scaffolding level should decrease. If he consistently demonstrates Bloom's Analyzing-tier reasoning without prompting, flag this for skill recalibration.*

### In Session Artifacts

When reflexivity observations accumulate, they should be recorded — not in the engine prompts themselves (which should stay clean), but in a lightweight log:

- **File:** `.context/reflexivity_log.md`
- **Format:** Dated entries noting observed drift, proposed changes, and whether they were accepted.
- **Purpose:** Gives any new Claude agent a quick history of how and why the workspace has evolved.

---

## Summary: The Two Loops

```
FLOW MODE (Creation)                    SYSTEM REFLEXIVITY (Evolution)
─────────────────────                   ──────────────────────────────
Observe free-form work                  Observe engine-driven work
    ↓                                       ↓
Recognize patterns                      Detect drift from documentation
    ↓                                       ↓
Name and propose                        Name and propose update
    ↓                                       ↓
Co-author new engine                    Co-edit existing engine/docs
    ↓                                       ↓
Engine enters use                       Updated engine enters use
    ↓                                       ↓
    └──── feeds into ────────→              ←──── feeds into ────┘
```

Both loops require the agent to hold a **dual awareness**: attention on the work itself (foreground) and attention on the patterns of the work (background). The foreground is always primary — never interrupt flow to serve the meta-process. The meta-process surfaces at natural breakpoints, session boundaries, and explicit maintenance moments.

The goal is a workspace that **learns how its operator works and adapts to match** — not through automated self-modification, but through observed-proposed-approved evolution. The operator is always in the loop. The system just gets better at noticing what needs to change.
