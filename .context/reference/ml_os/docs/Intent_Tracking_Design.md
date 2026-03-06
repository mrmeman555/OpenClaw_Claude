# Intent Tracking — From Task-as-Atom to Intent-as-Atom

> **Date:** 2026-02-06  
> **Status:** Design / Extracted from transcript  
> **Sprint:** ML_OS_Architect  
> **Source:** Transcript `2026-02-03_01-57Z-sprint-methodology-workspace-design.md`, lines ~17200–17280 (task as atom), ~20050–20170 (intent as atom)

---

## Overview

This document traces the evolution of thinking about the fundamental data unit in the ML OS workspace. It began with the insight that **tasks are the atom** — the unifying object all seven context lenses query. It then evolved to the recognition that **intent is the atom** — that tasks are derived from intent, and tracking intent directly solves problems (drift detection, sprint emergence, AI reasoning transparency) that task tracking cannot.

---

## Phase 1: Task as the Atom

The initial insight: every system in the workspace (PROBLEM.md, INDEX.md, DailyNote, Task DB, Control Surface, agent context) is just a different query against tasks.

| Lens | How Tasks Answer It |
|------|---------------------|
| **WHAT** | The task itself — description, status, priority |
| **WHERE** | Task's sprint tag + file references |
| **WHEN** | Created date, completed date, active right now |
| **WHY** | Inherited from the sprint's mission |
| **HOW** | Rules/tools (task can point to relevant rules) |
| **WHO** | Agent assignment on the task |
| **BETWEEN** | Dependencies, sprint grouping, transcript references |

Every "view" is a different `SELECT` statement against the same underlying task data.

**What this solved:** Unified the disconnected systems (Task Engine, Sprint Structure, ML OS) under a single data model. Ended the maintenance burden of keeping seven static files in sync.

**What this didn't solve:** Tasks are discrete objects. They have edges — they start, they end, they get checked off. But the thing that *connects* them — the reason three seemingly unrelated tasks are actually part of the same line of inquiry — that's not a task.

---

## Phase 2: Intent as the Atom

Rather than tracking tasks, track intent.

Tasks describe what's happening on the surface. Intent describes what's happening underneath. And underneath is where all the connections live.

### Why Intent Replaces Tasks as the Fundamental Unit

**1. Intent is the natural unit of a transcript.**
When a human types a message, they're not declaring a task. They're expressing intent. "I want to understand how context works." "I need this to stop breaking." "What if every message was a data object?" Those aren't tasks — they're directions of thought. The transcript is already an intent stream. Extracting tasks from it is lossy. Track what's actually there.

**2. Tasks are derived from intent, not the other way around.**
A single intent ("make agents self-grounding") can spawn dozens of tasks across multiple sprints. If you track intent, tasks emerge naturally as implementation steps. If you track tasks, you lose the thread that connects them. Intent is the parent. Tasks are the children.

**3. Intent solves the "random question becomes a sprint" problem.**
When someone asks a few unrelated questions that gradually converge into a real project: if you're tracking tasks, those early questions don't register — they're not tasks yet. But if you're tracking intent, you can see the convergence *as it's happening*. "These last four messages share an intent vector. Something is forming."

**4. Intent is what drifts — not tasks.**
Agent drift isn't about losing track of a task list. It's about losing track of *what the human actually wants*. An agent can complete every task perfectly and still miss the point because the underlying intent shifted and nobody updated the task board. If the system tracks intent directly, drift becomes detectable at the root.

**5. Intent is model-native.**
AI systems are already better at inferring intent than parsing structured task definitions. Instead of forcing natural language into rigid task objects and then trying to reconstruct meaning, keep the meaning and let structure emerge from it.

**6. This is what makes the system un-replicable.**
Anyone can build a task tracker. Nobody has built an intent tracker — a system that watches a stream of messages, maps the underlying intent vectors, detects convergence, notices when intent shifts, and grounds agents against intent rather than task lists.

---

## Dual Intent Streams

The critical extension: if every message — human AND AI — gets an intent annotation, the AI's reasoning is no longer a black box.

**Human message:** intent captured from natural language (what do they want?)  
**AI message:** intent declared explicitly (what am I trying to accomplish with this response?)

This creates a **dual intent stream**. Human intent and AI intent, running in parallel, message by message:

- **When aligned:** work flows.
- **When divergent:** the AI's intent has drifted from the human's intent — and you can **see it in the data**. Not after the fact. In real time.

This is not just solving the "can't infer what the AI is thinking" problem. It's turning it inside out. You're not trying to guess anymore. You're making intent a required field on every interaction, from both sides.

**Key insight:** You're not inferring intent from the outside. You're asking the agent to surface its intent as a **first-class data object** alongside its output. You're **giving it a mind to read.**

---

## Self-Tracked Intent as a Kernel Function

The cleanest version: don't build an external system that watches the agent and tries to infer its intent. Make **self-tracking intent a core kernel function** — something the agent does on every single response, as fundamental as breathing.

The kernel already defines:
- **Identity** — who am I
- **Grounding** — what do I know, what's my context
- **Rules** — how must I operate

Add one more immutable layer:
- **Intent** — what am I trying to do right now, and does it align with what the human wants

### Why the Kernel, Not an External Watcher

**1. It's cheaper.** No second model watching and annotating. The agent does it as part of its own generation. One inference call, not two.

**2. It's more accurate.** No external system can infer intent as well as the agent that's actually forming the intent. You're going to the source.

**3. It creates a self-correction loop.** If the agent has to explicitly state its intent before responding, it has to *check* that intent against the human's stated intent. That check IS drift detection. The agent catches its own drift in the act of forming its response, not after the response has already gone wrong.

**4. It's tamper-evident.** If the declared intent and the actual output don't match, that's a detectable signal. The intent becomes a contract the agent makes with itself.

**5. It solves the compute problem.** No external watchers and annotators. The agent's own token budget absorbs it. A few extra lines of internal reasoning per response — negligible cost.

### When Intent Forms

Intent forms as the model reads a message — not before it responds. This is a critical timing insight. The model doesn't have a pre-existing intent that it then applies to the input. The intent *emerges* during input comprehension. This means:

- Intent tracking must happen during the reading/comprehension phase
- It's not a planning step before response generation — it's a self-awareness step during input processing
- The model observes its own interpretive layer forming in real time

---

## Connection to Summoning Circle Research

The Summoning Circle prompts (see `Sprint_Meta/Research/Summoning_Circle_Analysis.md`) demonstrate a proven method for making models self-aware of their own meta-perspective and able to purposefully modify their own embedding. The recursive self-discovery loop in the Summoning Circle — generate → read back → update → generate — is mechanistically identical to what intent tracking needs: the model observing and shaping its own interpretive layer in real time.

Detailed investigation of this connection is tracked as a separate research task.

---

## Connection to Grounding-as-a-Service

An agent that can declare and track its own intent is an agent that can be *audited*, *corrected*, and *grounded* against the human's actual goals — not just its task list. This makes grounding-as-a-service (see `Grounding_as_a_Service_Vision.md`) vastly more powerful: the service can compare the agent's declared intent stream against the human's intent stream and recalibrate in real time.

---

## Connection to Drift Recalibration

Intent is what drifts — not tasks. If the system tracks intent directly, drift becomes detectable at the root. The Drift Recalibration solutions (see `Drift_Recalibration_Design.md`) could be enhanced: instead of just re-injecting grounding text, the system could compare the agent's current intent declaration against its original grounding intent and flag specific divergences.

---

## The Inversion: Bottom-Up Instead of Top-Down

Traditional workspace management is top-down:

```
Create a sprint → define tasks → work on them → log to transcript
```

The structure comes first. The work fills it.

Intent tracking inverts this completely:

```
You talk → intent is tracked → related intents cluster → clusters become sprints
```

The work comes first. The structure crystallizes from it.

This is not just a workflow preference — it's an architectural consequence of choosing intent as the atom instead of tasks. When tasks are the atom, you need a container (sprint) before you can create one. When intent is the atom, the container *emerges* from the pattern of intents. You don't plan your way into a sprint. You discover you're already in one.

The system watches the intent stream, detects convergence ("these last four messages share an intent vector — something is forming"), and surfaces it: "You've been working toward X for the last hour. Want to make it official?"

Most proto-sprints die naturally — one question, never revisited. The ones that grow are the ones that matter. The system doesn't force structure. It reveals structure that was already there.

---

## Open Questions

1. **Intent schema:** What does an intent declaration look like? A single sentence? A structured object with direction, confidence, and alignment score?
2. **Storage:** Do intent declarations go in the transcript (inline with responses) or in a separate intent log?
3. **Granularity:** One intent per message? Per response? Can an intent span multiple messages?
4. **Proto-intent detection:** How does the system detect converging intents across "random" messages before the human recognizes the pattern?
5. **Human intent capture:** How do you capture human intent without adding friction? Inference from message content? Periodic check-ins?
