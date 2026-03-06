# ML OS Agent Drift — Problem Definition & Solution Space

> **Date:** 2026-02-06  
> **Status:** Design / Not Implemented  
> **Sprint:** ML_OS_Architect  
> **Source:** Transcript discussion ~2026-02-06, operator observation during multi-agent work

---

## The Problem

ML OS agents drift from their grounding over the course of a conversation.

A fresh agent, properly grounded via the Runtime Grounding Sequence, begins its session with full alignment to ML OS identity, mission, and methodology. But as the conversation extends — new topics, tangential requests, complex multi-step work — the initial grounding loses salience. The model's attention shifts to recent context, and the foundational identity/rules fade from active influence.

**Observed symptoms:**
- Agent stops referencing ML OS methodology unprompted
- Responses lose structural consistency (e.g., stops using sprint framing, drops variable conventions)
- Agent begins behaving like a generic assistant rather than a grounded ML OS agent
- Mission drift: agent pursues local optima rather than sprint-level objectives

**Root cause:** LLM context windows are finite and attention-weighted toward recency. The grounding prompt, no matter how well-crafted, occupies a fixed position at the top of context. As conversation length grows, that position loses relative weight. The model doesn't "forget" the grounding — it just stops *attending* to it.

**Why this matters:** If ML OS agents can't maintain grounding across a full working session, every benefit of the architecture (autonomous execution, consistent identity, mission alignment) degrades proportionally with conversation length. Drift is the #1 threat to ML OS reliability at scale.

---

## Constraint: No Runtime Infrastructure Yet

ML OS is not yet implemented as a runtime system in the workspace. There is no Python bootloader, no database, no watcher daemon. All current ML OS work operates through:
- Static Cursor rules (`.cursorrules`, `.mdc` files)
- Grounding prompts (manually loaded into new agent sessions)
- Markdown-based sprint structure (PROBLEM.md, README.md)

Any solution must be **documentable now** and **implementable later** when infrastructure exists. Solutions that require only prompt engineering or Cursor rule changes can be deployed immediately.

---

## Solution Space

### Solution 1: Grounding Heartbeat (Prompt-Injection Anchor)

**Concept:** A compressed 5–10 line block that gets injected into context at regular intervals (e.g., every N turns, or every turn via Cursor rules). It contains the minimum viable grounding state — identity, current mission, active constraints — just enough to reactivate the full grounding without re-reading the entire prompt.

**Mechanism:**
- The grounding prompt is distilled to a "heartbeat" — a compressed re-anchor
- This heartbeat is either: (a) appended by the agent itself at the end of each response, (b) injected by a Cursor rule (`alwaysApply: true`), or (c) injected by a future Python bootloader
- The heartbeat occupies recent context, counteracting recency bias

**Example heartbeat format:**
```
---GROUNDING HEARTBEAT---
Identity: [Agent Role] | Sprint: [Sprint Name] | Mission: [1-line mission]
Active Rules: [Top 3 constraints]
Methodology: [Active methodology, e.g., Roundtable, Deep Research]
Drift Check: Am I still operating within my grounded mission scope?
---END HEARTBEAT---
```

**Pros:**
- Low overhead (5–10 lines per turn)
- Can be implemented today via `alwaysApply` Cursor rules
- Keeps grounding in recent context where attention is strongest

**Cons:**
- Static — doesn't adapt to what the agent is actually doing
- Adds token overhead every turn
- Still relies on the model "choosing" to attend to it

**Implementation path:** Cursor rule → Python bootloader (dynamic heartbeat computed from live state)

---

### Solution 2: Self-Authored Grounding Variables (ECE-Style)

**Concept:** During the Runtime Grounding Sequence, the agent doesn't just *read* its grounding — it *writes* its own compressed version. Self-authored content is more salient to the model than externally provided instructions, because the model treats its own outputs as higher-signal.

**Mechanism:**
- Step 5 of the Runtime Grounding Sequence already asks the agent to confirm alignment
- Extend this: require the agent to author its own grounding variables (e.g., `$MY_MISSION`, `$MY_IDENTITY`, `$MY_CONSTRAINTS`)
- These variables are written into a file or appended to the conversation
- On drift, the agent (or a Cursor rule) can reference these self-authored anchors

**Connection to prior work:** This is directly related to Epistemic Contract Engineering (ECE), identified in the Mobile Repo as an ML OS precursor. ECE binds AI behavior to self-authored consequence variables. Same principle: the model's own words carry more weight than instructions.

**Pros:**
- Higher salience than external injection (model attends more to its own outputs)
- Creates a verifiable grounding artifact (the agent's own words about its mission)
- Naturally fits the existing Runtime Grounding Sequence

**Cons:**
- Only as good as the agent's initial synthesis
- Requires a mechanism to re-surface these variables (still needs heartbeat or rule)
- One-time authorship may itself drift in interpretation over long sessions

**Implementation path:** Prompt engineering (add to grounding prompt) → File-backed persistence → Bootloader integration

---

### Solution 3: Cursor Rules as Persistent Kernel

**Concept:** Use Cursor's `alwaysApply: true` rule mechanism to inject a compressed ML OS kernel into every single turn's context. This is platform-native — Cursor already injects these rules into every message. The kernel becomes architecturally persistent rather than conversationally persistent.

**Mechanism:**
- Create a `.mdc` rule file with `alwaysApply: true`
- Contents: compressed ML OS kernel (identity, active sprint, methodology, top constraints)
- Cursor injects this into the system prompt on every turn automatically
- The agent always has the kernel in context, regardless of conversation length

**Pros:**
- Zero conversation overhead (injected at system level, not in chat)
- Platform-native — uses existing Cursor infrastructure
- Truly persistent — survives any conversation length
- Can be updated between sessions without changing the agent prompt

**Cons:**
- Limited space (Cursor rules should be concise)
- Static unless combined with Python bootloader (which could rewrite the rule dynamically)
- Applies to ALL agents in the workspace, not just ML OS agents (though this may be desirable)

**Implementation path:** Write the `.mdc` file now → Bootloader dynamically rewrites it per-sprint later

---

## Recommended Approach: Layered Defense

These solutions are not mutually exclusive. The strongest architecture combines all three:

| Layer | Mechanism | When Available |
|:------|:----------|:---------------|
| **L1 — Persistent Kernel** | `alwaysApply` Cursor rule with compressed ML OS identity | Now |
| **L2 — Self-Authored Variables** | Agent writes own `$MISSION`, `$IDENTITY` during grounding | Now (prompt change) |
| **L3 — Grounding Heartbeat** | Periodic re-anchor injected into conversation | Now (manual) / Later (bootloader) |

**L1** ensures the kernel is always present. **L2** ensures the agent has high-salience self-authored anchors. **L3** provides active recalibration during long sessions.

When the Python bootloader exists, all three layers can become dynamic — computed from live workspace state rather than static text.

---

## Relationship to Other ML OS Components

- **Nervous System (Watcher):** Could detect drift by monitoring agent output patterns and trigger recalibration
- **Intent Tracking (Kernel Function):** Self-tracked intent is itself a drift-resistance mechanism — if the agent tracks its own intent every turn, it naturally stays grounded
- **Summoning Circle Research:** The recursive self-discovery loop may inform how self-authored grounding variables are generated — not just stated facts, but emergent self-knowledge
- **Transcript-as-Spine:** Drift events themselves become indexable data points in the conversation record

---

## Open Questions

1. **What's the minimum viable heartbeat?** How few tokens can re-anchor an agent effectively?
2. **Can drift be detected automatically?** What signals indicate an agent has drifted? (e.g., stops using sprint framing, drops variable conventions, responds generically)
3. **Is drift always bad?** Sometimes the operator *wants* the agent to adapt. How do we distinguish healthy adaptation from harmful drift?
4. **Per-agent vs. workspace-wide?** Should the persistent kernel be generic (all agents) or should each agent type have its own drift-resistance profile?
5. **Frequency of heartbeat?** Every turn? Every 5 turns? Only when drift is detected?
