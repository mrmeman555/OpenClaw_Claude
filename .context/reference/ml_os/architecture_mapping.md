# ML OS → Workspace Architecture Mapping

This document traces the lineage from Mimir's ML OS (Meta-Language Operating System) — originally designed for Notebook LM — to the shared workspace architecture used across Claude Chat App, Cowork, and Claude Code.

The workspace is not a reimplementation of ML OS. It's the same architecture adapted for a persistent, multi-tool environment with a real file system and git-backed state.

---

## The Core Insight

ML OS was designed to solve a fundamental problem: **LLM agents have no persistent identity or state.** Every conversation starts from zero. ML OS addresses this by formalizing a boot sequence that reconstructs identity, behavioral rules, and domain context from a structured document before any work begins.

The workspace faces the same problem across a *wider surface* — three different Claude tools, each starting fresh sessions — but has an advantage ML OS didn't: a real file system and a git repo. Instead of packing everything into a single context document, we distribute the architecture across files and let the boot sequence load them lazily.

---

## Section-Level Mapping

| ML OS Section | System Analogy | Workspace Implementation | File(s) |
|---|---|---|---|
| **§1 — System Overview** (Kernel) | Firmware / POST | `CLAUDE.md` — the boot sequence. First thing any agent reads. Establishes identity, points to context files, defines the grounding protocol. Immutable across sessions. | `CLAUDE.md` |
| **§2 — AI Schema** (Behavioral Engine) | CPU / Runtime | `mimir.md` — persistent operator profile. Cognitive style, interaction preferences, core philosophies ("Crab in the Bucket"), skill calibration, hard boundaries (production network). Governs *how* the agent reasons and communicates. | `.context/mimir.md` |
| **§3 — Scenario** (Application Layer) | Execution Environment | Engine prompts — project-specific contexts with triggers, modes, Phase 0 protocols, and evaluation criteria. Each engine is a "cartridge" that slots into the kernel. | `.context/engines/*.md` |
| **§4 — Sources** (Storage / Input) | Storage Subsystem | The repo itself — project files, PROGRESS.md trackers, transcripts, reference docs. Unlike ML OS (where sources live in NotebookLM's context window), our sources live on disk and are loaded on demand. | Repo files, `PROGRESS.md`, project directories |
| **§5 — Outputs** (Display / Results) | Output Interface | Session artifacts — design docs, notes, code, updated progress files. Written to the repo during or after sessions. Persist via git. | Created during sessions |

---

## Boot Sequence Comparison

### ML OS (Notebook LM)
```
[Power-On] → $SYSTEM_PROMPT executes
  → Loads §1 Kernel (immutable identity)
  → Binds $AGENT_NAME, $OUTPUT_FORMAT, $CONTEXT_VERSION
  → Initializes §2 AI Schema (behavioral engine)
  → §3 Scenario contextualizes the domain
  → [Runtime Active]
```

### Workspace (Claude Chat / Cowork / Claude Code)
```
[Session Start] → Agent reads CLAUDE.md
  → Step 1: Reads .context/mimir.md (operator profile = §1 + §2)
  → Step 2: Reads .context/workspace.md (conventions)
  → Step 3: Scans for state (PROGRESS.md, recent commits)
  → Step 3: Scans .context/engines/ (available scenarios = §3)
  → Step 3: Asks operator for grounding ("What are we working on?")
  → Loads relevant engine prompt → follows its Phase 0
  → [Runtime Active]
```

### Key Difference: Lazy Loading

ML OS front-loads everything into the context window at boot because Notebook LM has no file system — the kernel, schema, scenario, and sources must all be present simultaneously.

The workspace uses **lazy loading**. The boot sequence (`CLAUDE.md`) is lean — it tells the agent *where things are* and *how to ask for direction*, rather than dumping everything upfront. The agent only loads the specific engine and source files relevant to the current session. This scales better as the number of engines and projects grows.

---

## Concept Mapping

| ML OS Concept | Workspace Equivalent | Notes |
|---|---|---|
| **$SYSTEM_PROMPT** (Bootloader) | `CLAUDE.md` | Both are the first thing executed. Both establish identity before work begins. |
| **$AGENT_NAME** binding | Implicit — the agent knows it's working with Mimir via `mimir.md` | ML OS needs explicit binding because the agent name varies per scenario. Our workspace always has one operator. |
| **$OUTPUT_FORMAT** | Not enforced globally | ML OS mandates raw Markdown for all outputs. The workspace lets output format vary by tool and context (Cowork might produce .docx, Claude Code produces code, etc.). |
| **Immutable Kernel** (§1 is unchangeable) | `CLAUDE.md` + `mimir.md` are stable, rarely edited | Same principle: the core identity doesn't change per session. But the workspace files *can* be updated (via git), they just evolve slowly. |
| **Scenario Cartridge Swapping** | Engine selection via trigger words | Same mechanism. "Design Review" loads `security_lab_build.md`. "Lab Mode" loads `network_architect_mentor.md`. The kernel doesn't change — only the active scenario does. |
| **Phase 0 (Context Inventory)** | Preserved in each engine prompt | Every engine still runs its own Phase 0 when activated. The workspace adds a *pre-Phase 0* at the CLAUDE.md level (scan for state before asking what to load). |
| **Grounding Integrity** (§2.4) | Enforced via `mimir.md` directives | "Socratic over lecture," "why before how," "don't re-teach what he knows" — these are the behavioral constraints that persist regardless of scenario. |
| **Recursive Context Maintenance** (Living Doc Protocol) | `PROGRESS.md` + git history | ML OS has the agent re-analyze the Master Doc when new parts are added. Our workspace uses PROGRESS.md files and git commits to achieve the same continuity. |

---

## What the Workspace Gains Over ML OS

1. **True persistence.** ML OS simulates persistence through document structure. The workspace has actual file-system persistence via git. State survives not just across sessions, but across tools.

2. **Multi-agent coordination.** ML OS runs one agent in one Notebook LM instance. The workspace coordinates three different Claude surfaces against the same repo. The boot sequence works regardless of which tool connects.

3. **Lazy loading.** The workspace doesn't pay the context-window cost of loading everything upfront. It loads what's needed when it's needed.

4. **Artifact accumulation.** ML OS outputs live in chat history (ephemeral). Workspace outputs are files in a repo (permanent, versioned, diffable).

5. **Organic growth.** New engines can be added by dropping a `.md` file in `.context/engines/` and adding a line to the routing table in `CLAUDE.md`. No kernel modification needed.

---

## What ML OS Has That the Workspace Should Preserve

1. **Formal boot sequence discipline.** ML OS forces every interaction through a defined initialization. The workspace should maintain this rigor — don't let agents skip grounding.

2. **Immutability of the kernel.** `CLAUDE.md` and `mimir.md` should evolve slowly and deliberately. They're not scratch pads.

3. **Explicit variable binding.** ML OS binds `$AGENT_NAME` and `$OUTPUT_FORMAT` at boot. While the workspace doesn't need the same formalism, each engine should clearly declare its role and output expectations when loaded.

4. **Meta-reflection.** ML OS includes a "Meta-Reflection Cue" — the awareness that the agent is both the instrument and the subject. This self-awareness pattern produces better-calibrated outputs and should be preserved in how engine prompts are written.

---

## Source Documents

The original ML OS documents are archived in this directory:

- `ml_os_system_architect.pdf` — The full ML OS framework (§1-§5) as implemented for the System Architect Agent in Notebook LM
- `notion_bridge_architect.pdf` — A scenario instantiation (§3) of ML OS for the Notion Bridge Architect role
- `Claude-MLOS-Assessment.docx` — Claude's assessment of the ML OS methodology and Mimir's competitive positioning
