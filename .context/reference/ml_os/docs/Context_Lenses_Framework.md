# The Seven Context Lenses

> **Date:** 2026-02-06  
> **Status:** Design / Extracted from transcript  
> **Sprint:** ML_OS_Architect  
> **Source:** Transcript `2026-02-03_01-57Z-sprint-methodology-workspace-design.md`, lines ~17040–17280

---

## Overview

Every system built in the workspace exists to answer a specific *kind* of question. Each is a "lens" — a way of viewing the workspace from a particular angle. Agents need multiple simultaneous lenses to be grounded; no single file can do it.

The reason so many systems were built (PROBLEM.md, INDEX.md, DailyNote, Task DB, Control Surface, README.md, Cursor Rules, Transcripts, etc.) is that each one serves a different contextual need. This document identifies the seven core lenses and shows how they unify under a single data model.

---

## The Seven Lenses

### 1. WHAT — "What needs to be done?"

**Systems that serve this lens:**
- PROBLEM.md roadmap/checklist sections
- Task DB (`tasks.db`)
- Control Surface (HUD view of active tasks)
- Task Inbox (ingestion point)

**Why four systems exist for one lens:** Task context has layers. The DB is the *truth*. The Control Surface is the *view*. The Inbox is the *input*. PROBLEM.md was the *narrative wrapper* — it didn't just list tasks, it explained what the tasks meant in context. A flat `SELECT * FROM tasks` doesn't tell an agent "Phase 1.2 is complete and you're transitioning to 1.3." PROBLEM.md did.

---

### 2. WHERE — "Where am I? Where is everything?"

**Systems that serve this lens:**
- INDEX.md (workspace-level map of all sprints)
- README.md (sprint-level map of all files)
- Sprint folder structure itself
- Asset Inventory sections of PROBLEM.md

**Why multiple systems:** Spatial context is hierarchical. INDEX.md answers "what sprints exist." README.md answers "what's in this sprint." The Asset Inventory in PROBLEM.md answers "what's in this sprint *and what each file is for*." An agent needs all three levels or it's lost.

---

### 3. WHEN — "What's happening now? What happened before?"

**Systems that serve this lens:**
- DailyNote.md (today's state — active sprints, completed tasks, focus)
- Methodology Log (pointers to when/where methodologies were designed)
- Transcripts (`.specstory/history/`)
- Git history

**Why multiple systems:** Temporal context has two dimensions — *present* and *historical*. DailyNote answers "what's active right now." Transcripts answer "how did we get here." The Methodology Log bridges them — it says "this methodology was designed in *this* transcript at *this* point." Without the temporal lens, an agent doesn't know if a task was created 5 minutes ago or 3 weeks ago.

---

### 4. WHY — "What's the mission? What's the strategy?"

**Systems that serve this lens:**
- PROBLEM.md Purpose/Goal/Strategy sections
- Sprint naming conventions (`Sprint_NetPlus`, `Sprint_CareerStrategy`)
- The narrative sections of PROBLEM.md that explain *why tasks exist*

**Why this lens matters most:** This is what made the Net+ agent work. It didn't just read a task list. It read the *story* — the Verb Cipher's origin, Domain 5 as the Master Key, the Three Trees. The WHY lens turns a task executor into a *collaborator*. The DB can never provide this. This is the one lens that must stay manual/narrative.

---

### 5. HOW — "What are the rules? What tools exist?"

**Systems that serve this lens:**
- `.cursor/rules/` (behavioral rules)
- `TOOLS_INDEX.md` (available tools)
- `WORKSPACE.md` (global constraints — venv, shared tools)
- Agent_WakeUp.md / Agent_Instantiation.md (onboarding protocols)
- ML OS Kernel spec (behavioral engine — §2 AI Schema)

**Why multiple systems:** Different granularities. Cursor rules are *automatic* (injected by the IDE). WORKSPACE.md is *reference* (read on request). The ML OS kernel is *identity-level* (defines what the agent fundamentally IS). These are three layers of the same lens.

---

### 6. WHO — "What agent am I? What's my role?"

**Systems that serve this lens:**
- ML OS Kernel §1 (identity binding — `$AGENT_NAME`)
- Agent_WakeUp.md handshake (forces agent to declare identity)
- Runtime Grounding Sequence (§1.7)
- Per-agent grounding prompts

**Why this exists separately from HOW:** Identity constrains behavior. The Net+ Architect Agent and the Case Study Archivist have the same behavioral rules (§2 AI Schema) but completely different identities, missions, and contexts. WHO determines which subset of the workspace the agent cares about.

---

### 7. BETWEEN — "How does this relate to everything else?"

**Systems that serve this lens:**
- DailyNote listing active sprints (connecting *time* to *space*)
- INDEX.md linking sprints to PROBLEM.md files (connecting *where* to *what*)
- PROBLEM.md Asset Inventory (connecting *files* to *tasks*)
- Task DB sprint tags (connecting *tasks* to *sprints*)
- Methodology Log transcript references (connecting *methods* to *history*)

**Why this is the hardest lens:** It connects all the others. DailyNote listed active sprints because the *temporal* lens needed a bridge to the *spatial* lens. PROBLEM.md had an asset inventory because the *mission* lens needed to point to the *spatial* lens. Every cross-link ever built was this lens.

---

## The Pattern: Agent_WakeUp.md Already Had Most of This

The original Agent_WakeUp.md handshake captured the lenses intuitively:

| Handshake Step | Lens |
|---|---|
| 1. Temporal Frame (Time) | **WHEN** |
| 2. Spatial Frame (Space) | **WHERE** |
| 3. Constitutional Frame (Law) | **HOW** |
| 4. Tooling Frame (Capabilities) | **HOW** (subset) |
| 5. Logging Frame (Closure) | **BETWEEN** (connecting work back to time) |

What was missing: **WHAT** (tasks), **WHY** (mission), and **WHO** (identity). Those were added through PROBLEM.md (WHAT + WHY) and the ML OS kernel (WHO). The full set is seven lenses.

---

## Unification: Every Lens Is a Query Against Tasks

The key insight that emerged from this analysis: the **task** is the unifying data object. Every lens relates back to tasks in a different way:

| Lens | Question | How Tasks Answer It |
|------|----------|---------------------|
| **WHAT** | What needs doing? | The task itself — description, status, priority |
| **WHERE** | Where does it live? | The task's sprint tag + file references |
| **WHEN** | When is it relevant? | Created date, completed date, active right now |
| **WHY** | Why does it exist? | Inherited from the sprint's mission (stays narrative) |
| **HOW** | How do I do it? | Rules + tools (Cursor rules, not the DB — but tasks can *point* to relevant rules) |
| **WHO** | Who's responsible? | Agent assignment on the task |
| **BETWEEN** | How does it relate? | Dependencies, sprint grouping, transcript references |

Every "view" in the workspace becomes a different `SELECT` statement:

```
PROBLEM.md  = SELECT * FROM tasks WHERE sprint = 'Sprint_NetPlus'
              + the sprint's narrative mission (manual, stays human)

INDEX.md    = SELECT sprint, COUNT(*), status FROM tasks GROUP BY sprint

DailyNote   = SELECT * FROM tasks WHERE completed_at = today
              UNION
              SELECT * FROM tasks WHERE status = 'active'

Control     = SELECT * FROM tasks WHERE priority = 1
Surface       ORDER BY created_at DESC

Agent       = SELECT * FROM tasks WHERE sprint = $current_sprint
Context       + sprint mission + relevant files + rules
```

---

## Transition Strategy

The seven lenses don't all need to become computed at once. Recommended order:

1. **WHAT** — already computed (Task DB + Control Surface). Keep using it.
2. **WHERE** — compute INDEX.md from filesystem + DB. Low risk, high clarity.
3. **BETWEEN** — this is the bootloader. It says "for this sprint, here are active tasks, relevant files, mission context."
4. **WHEN** — compute daily state from DB + git + transcripts.
5. **WHY** — stays manual. Always. This is the human layer.
6. **HOW** — stays in Cursor rules. Already working.
7. **WHO** — the kernel. Computed by the bootloader from sprint context.

---

## Relationship to Other ML OS Components

- **Nervous System:** The Watcher/Index/Compiler architecture (see `DESIGN_BRIEF.md`) is the mechanism that makes computed lenses possible by indexing transcripts into queryable metadata.
- **Python Bootloader:** The bootloader is essentially the BETWEEN lens — it computes the right context for the right agent at the right time from live workspace state.
- **Intent Tracking:** The evolution from "task as the atom" to "intent as the atom" (see `Intent_Tracking_Design.md`) refines which data object sits at the center of all seven lenses.
- **Drift Recalibration:** Agent drift is what happens when one or more lenses go stale mid-session.

---

## Note on "Task as the Atom" Evolution

This document captures the original insight that tasks are the unifying data object. A subsequent discussion in the same session evolved this to **intent as the atom** — recognizing that intent is the natural unit of a transcript, and tasks are derived from intent rather than the other way around. See `Intent_Tracking_Design.md` for the full evolution.
