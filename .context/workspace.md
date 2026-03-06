# Workspace Conventions

This repo is a shared workspace accessed by multiple Claude surfaces. Understanding how it's used prevents conflicts and ensures continuity.

---

## Access Points

Three tools interact with this repo. Each has different strengths:

| Tool | Primary Use | Repo Access | Best For |
|------|------------|-------------|----------|
| **Claude Chat App** | Long conversations, deep project work, file creation/editing | Full GitHub repo access (clone/pull/push) | Engine-driven sessions (lab builds, study modes, design reviews). Loads project-specific engine prompts for extended work. |
| **Cowork** | Task management, file operations, browser automation | Local workspace folder (synced with repo) | File organization, quick edits, workspace maintenance, creating/managing artifacts. |
| **Claude Code** | CLI-driven coding, git operations, scripting | Full repo access via terminal | Git operations, code changes, scripting, anything that benefits from direct terminal access. |

## Repo Structure

```
CLAUDE.md                        ← Boot sequence. Every agent reads this first.
.context/
  mimir.md                       ← Operator profile (persistent across all projects)
  workspace.md                   ← This file. How the workspace works.
  flow.md                        ← Flow Mode + System Reflexivity protocol
  reflexivity_log.md             ← Running log of drift observations and engine evolution
  engines/                       ← Project-specific engine prompts
    security_lab_build.md        ← Sec+ lab build (Design Review / Build Mode / etc.)
    network_architect_mentor.md  ← CCNA/Net+ mentor (Lab Mode / Subnetting Mode / etc.)
    (new engines added as projects evolve)
  reference/
    ml_os/                       ← ML OS lineage docs and architecture mapping
system_prompts/                  ← Archive of raw system prompts (reference copies)
```

### Key Directories (will grow as projects are added)

- **`.context/`** — Agent context files. The CLAUDE.md points here. This is the "brain" of the workspace.
- **`.context/engines/`** — Deep project-specific prompts. These are what get loaded when Mimir says "I'm working on X today."
- **`.context/reference/ml_os/`** — The ML OS (Meta-Language Operating System) documentation that this workspace architecture descends from. Includes the original framework docs, a Notion Bridge Architect scenario instantiation, Claude's methodology assessment, and an `architecture_mapping.md` that traces every ML OS concept to its workspace equivalent. Read this to understand *why* the workspace is structured the way it is.
- **`system_prompts/`** — Archive of the original system prompts as written. Reference copies. The `.context/engines/` versions may diverge as they're adapted for this workspace.

## Conventions

### File Naming
- Engine prompts: `snake_case.md` descriptive of the project
- Progress files: `PROGRESS.md` within the relevant project directory
- Session artifacts: Include date or "transcript" in filename for sorting
- Daily notes: Include "daily_note" in filename

### Progress Tracking
Every project that has active work should maintain a `PROGRESS.md` (or equivalent). The format may vary by project, but it should always answer: *Where did we leave off? What's next?*

### Git Workflow
- The Chat App is the primary tool for pushing to the repo.
- Cowork and Claude Code may read from the repo and create local files.
- Avoid conflicts: if multiple tools are active, coordinate through the repo's state files (PROGRESS.md, etc.).

### Engine Prompt Design Patterns
Based on established patterns from existing engines, new engine prompts should include:

1. **Phase 0 (Context Inventory)** — Scan available files, detect current state, orient before acting.
2. **Trigger-Based Modes** — Named entry points ("Design Review", "Lab Mode", etc.) that scope the conversation.
3. **File Categorization Logic** — How to sort and prioritize the project's files.
4. **Core Directives** — Universal rules for the project (safety boundaries, pedagogical approach, etc.).
5. **Progress Format** — How to track and record session outcomes.
6. **Reflexivity Hook** — A brief section noting what drift signals to watch for in this engine's domain (e.g., skill calibration thresholds, workflow assumptions that may evolve). See `.context/flow.md` Part 2.
7. **Lineage Note** — If the engine was crystallized from Flow Mode, note the date, the pattern that generated it, and the sessions that informed it. If adapted from an existing prompt, note the source.

### Engine Lifecycle

Engines are not permanent. They follow a lifecycle:

- **Crystallization** — A new engine emerges from Flow Mode or is authored directly.
- **Active Use** — The engine is loaded regularly and guides project work.
- **Drift** — The operator's skills, interests, or workflows evolve past the engine's assumptions.
- **Recalibration** — The engine is updated to match current reality (via the Reflexivity process in `.context/flow.md`).
- **Archival** — If an engine is no longer relevant (project completed, interest shifted), move it to `.context/engines/archive/` rather than deleting it. It preserves institutional memory.

### Flow Mode & Reflexivity

The workspace includes a meta-process layer documented in `.context/flow.md`. This governs:

- **Flow Mode** — How unstructured work becomes structured (new engines emerge from observed patterns).
- **System Reflexivity** — How existing engines and docs are continuously evaluated against actual use and updated when they drift.

These are not engines themselves — they're workspace-level awareness that runs alongside all work. Any agent interacting with this workspace should read `flow.md` during boot (Step 5 in `CLAUDE.md`).
