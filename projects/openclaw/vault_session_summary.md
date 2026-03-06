# Comprehensive Summary: OpenClaw Research Session

**Session Duration:** 881 turns, 252KB transcript
**Participant:** Mimir (operator), Claude Code Agent
**Primary Focus:** Building the ML OS-based knowledge management system ("Claude-Cowork-Vault")

---

## 1. THE VAULT ARCHITECTURE

### Overall Design Philosophy

The vault is a **file-based, git-backed knowledge management system** designed for storing, ingesting, and querying curated document collections. The architecture prioritizes:

- **Small, focused vaults** over monolithic libraries — each vault is a scoped context for a specific purpose
- **No duplication** — single source of truth in the filesystem + git
- **Provenance tracking** — every file knows its origin (ingested from human vs. created by agent)
- **Append-only operations** — immutable storage, changes tracked via git commits
- **Minimal upfront metadata** — 6 auto-derivable fields at ingest; richer metadata added later in batches

### Directory Structure

```
Project Root (e.g., C:\Users\Erinh\Desktop\Home_Lab_2026\)
├── vault/
│   ├── sec-plus/               # Storage zone: ingested materials
│   │   ├── file1.md
│   │   └── file2.pdf
│   ├── net-plus/
│   └── mlos-dev/               # Populated example project
│       ├── project-state.md
│       ├── decisions.md
│       ├── session-history.md
│       └── pickup.md
├── bench/
│   ├── sec-plus/               # Work products zone: analysis, derivatives
│   │   └── MOC.md
│   └── net-plus/
├── io/
│   └── inbox/                  # Drop zone for external materials
├── .mlos/                       # System layer
│   ├── ingest.py               # Core ingestion pipeline
│   ├── moc.py                  # Map of Content generator
│   ├── index.json              # Metadata index
│   ├── kernel.yaml             # ML OS immutable identity
│   ├── schema.yaml             # ML OS behavioral rules
│   ├── prompts/
│   │   ├── grounding.md        # Agent onboarding
│   │   ├── explore-with-me.md  # Session initialization
│   │   └── pickup.md           # Context pack loader
│   ├── scenarios/              # ML OS agent role templates
│   │   ├── system-architect.yaml
│   │   ├── research-analyst.yaml
│   │   ├── code-auditor.yaml
│   │   └── doc-writer.yaml
│   ├── registry.yaml           # Agent registry (from cowork)
│   ├── context.md              # Master context doc (Living Doc)
│   ├── memory/                 # Shared agent work products
│   ├── DRAFT_index_schema_and_workflow.md  # Design specification
│   ├── output/                 # Generated outputs (MOCs, exports)
│   └── mlos.py                 # Template composer CLI
├── .claude/
│   └── launch.json             # Dev server configurations
├── .git/                        # Version control
├── CLAUDE.md                    # Project orientation
└── server.py                    # Vault browser HTTP server

```

### Core Files and Key Design Decisions

#### `.mlos/ingest.py` — Ingestion Pipeline

**File Path:** `C:\Users\Erinh\Desktop\Home_Lab_2026\.mlos\ingest.py`

**Responsibilities:** Move files from inbox to vault, auto-index, validate integrity

**Commands:**

| Command | Purpose | Key Flags |
|---------|---------|-----------|
| `scan` | Preview inbox contents without changes | (none) |
| `add <path>` | Ingest files from inbox to vault | `--project <name>`, `--flatten`, `--preserve`, `--prefix <str>`, `--dry-run` |
| `write` | AI direct-to-vault (no inbox needed) | `--project <name>`, `--filename <name>`, `--content "..."`, `--stdin`, `--title`, `--dry-run` |
| `view` | Query index with filters | `--project <name>`, `--type <type>` |
| `check` | Validate index vs filesystem | (none) |
| `export` | Render index as markdown | `--project <name>`, output piped to file |

**Design Decisions:**

1. **8-character hex hash IDs** — Generated from `hashlib.sha256(f"{filename}:{timestamp}").hexdigest()[:8]`
   - Rationale: Compact, collision-resistant, deterministic within same ingest run

2. **Nesting strategy: Interactive prompt** — Scan shows structure; user chooses flatten or preserve (or pass `--flatten`/`--preserve` CLI flags)
   - Rationale: Different sources need different handling; make it explicit, not implicit

3. **Inbox-only source** — Files must originate from `io/inbox/` to be ingested
   - Rationale: Keeps the pipeline predictable; allows inspection before committing

4. **No stored paths in index** — Paths are derived at query time from `vault/{project}/{filename}`
   - Rationale: Prevents stale paths if files move; single source of truth is filesystem

5. **Auto-rename on collision** — If `README.md` already exists, new one becomes `README_2.md`
   - Rationale: No data loss, preserves both files, user must decide what to do

6. **Auto title extraction** — From `.md`, `.py`, `.yaml`, `.txt`, `.docx` first heading; falls back to filename
   - Rationale: Most files have structure; saves manual metadata entry

7. **Cleans up empty inbox folders after ingest**
   - Rationale: Keeps inbox clean; signals completion

8. **Write command includes `"source": "agent"` tag** in index
   - Rationale: AI-created content distinguishable from human ingestion

#### `.mlos/index.json` — The Metadata Index

**6-field auto-derivable schema:**

```json
{
  "version": "1.0",
  "projects": {
    "sec-plus": [
      {
        "id": "a1b2c3d4",
        "filename": "Lab_01_Overview.docx",
        "type": "docx",
        "size": 45678,
        "title": "Security+ Lab 01: Overview",
        "ingested": "2026-03-06T14:30:00Z",
        "project": "sec-plus",
        "source": "human"  // or "agent" for AI-created
      }
    ]
  }
}
```

**Fields intentionally left out for later enrichment:**
- tags, objectives, source_url, blooms_level, description, notes, references, related_files

Rationale: Schema over-design kills adoption. Start minimal, add metadata in batches as needed.

#### `.mlos/moc.py` — Map of Content Generator

**File Path:** `C:\Users\Erinh\Desktop\Home_Lab_2026\.mlos\moc.py`

**Purpose:** Auto-generate table-of-contents markdown for any directory

**Commands:**

```bash
python .mlos/moc.py <directory>           # Print to stdout
python .mlos/moc.py <directory> -o        # Write to {directory}/MOC.md
python .mlos/moc.py <directory> --depth 1 # Limit recursion depth
python .mlos/moc.py <directory> --flat    # Flatten instead of grouping by subdir
```

**Design:**
- Scans recursively, groups files by subdirectory
- Extracts headings using regex (`.md`, `.py`, `.yaml`, `.json`, `.txt`, `.docx`)
- Generates markdown table with: File | Type | Size | Description (first heading)
- Tested on: `Sec+Analysis/` (2 files), `io/inbox/` (29 files, 5 dirs), `Docs/net+Analysis/` (6 markdown files)

#### `server.py` — Vault Browser

**File Path:** `C:\Users\Erinh\Desktop\Home_Lab_2026\server.py`

**Purpose:** HTTP server serving a web UI for browsing vault contents

**Port:** 3001 (default; configured in `.claude/launch.json`)

**Features:**
- Dark terminal aesthetic (same theme as ML OS demo)
- Sidebar: Overview, Projects (with item counts), Raw Index view
- Main view: File browser with inline markdown rendering
- Renders headings, code blocks, lists, tables with styling
- Status bar showing current path
- File viewer with "Back" button

**Design:**
- Reads live from `vault/`, `index.json`
- No database; filesystem is source of truth
- Simple Flask-like routing in Python HTTP server
- Serves `index.html` + JS/CSS inline or as assets

---

## 2. THE TIER 1 / TIER 2 PROBLEM

### What Is This About?

**The Problem: Context Rot**

Files like `project-state.md`, `decisions.md`, `session-history.md` go stale because:
- They require manual updating at end of sessions
- Agents get context-overloaded or sessions terminate early
- Changes happen continuously but updates are batched/forgotten
- No mechanism keeps them in sync with reality

### Tier 1: Mechanical (No LLM Needed)

**What it does:** Deterministic state regeneration from filesystem/index/git

**Examples:**
- Scan vault directories → regenerate `project-state.md` listing what exists
- Parse git commits → append to raw event log
- Validate `index.json` against filesystem
- Rebuild MOCs from file structure

**Implementation:** Git hooks (`pre-commit`, `post-commit`) or Python file watchers (`watchdog`)

**Status:** BUILDABLE right now; straightforward shell/Python scripts

### Tier 2: Intelligent (LLM Required)

**What it does:** Semantic extraction from raw signals — understanding what happened and why

**Examples:**
- Read transcript files + event log → write intelligent session summary
- Detect decision patterns in conversation → append to `decisions.md`
- Analyze what changed in this session → update `project-state.md` description

**Implementation Requirements:**
- Must call Claude API (or other LLM) from background process
- Needs transcript access — can parse `.jsonl` files written by Claude Code
- Should run async from main agent session (not block Claude Code)

**Status:** PARTIALLY BLOCKED (see constraints below)

### Key Constraints Identified

#### 1. **PostToolUse Hook Limitations**

**What is PostToolUse?** A Claude Code hook that fires after a tool executes (Read, Write, Edit, Bash, etc.)

**Capability:** Receives `tool_name`, `tool_input`, `tool_output`, `transcript_path`

**Limitation:** Cannot read transcript contents reliably
- The hook input includes a `transcript_path` field pointing to session `.jsonl` file
- **Confirmed regression:** Stop hooks receive incomplete or broken transcript access
- Use case from docs ("Analyze the conversation and determine if...") is non-functional

**Implication:** Cannot build intelligent summary from conversation within a hook — transcript semantics unavailable

#### 2. **Transcript Access Issues**

**Format:** Claude Code stores transcripts as `.jsonl` (JSON Lines) files
- Path: `~/.claude/projects/.../session-id.jsonl`
- Readable by external scripts post-session ✓
- Accessible mid-session from hooks ✗ (regression)

**Implication:** External watcher agent could read old transcripts, but hook-based approach is broken

#### 3. **PostToolUse Fires Too Broadly**

- Fires on **every** Write/Edit operation
- **Not path-scoped** — cannot fire only for `vault/` writes
- **Synchronous by default** — blocks agent if hook is slow
- **Per-machine, not per-project** — same hook runs for all Claude Code sessions
- **Cannot trigger other conversations** — hook can only run shell commands

**Implication:** Cannot reliably use hooks as the sole trigger mechanism for Tier 2

### Why Tier 2 Is Unsolved

**The gap:** No native way within Claude Code + hooks ecosystem to:

1. Detect when meaningful work happened (hard to distinguish "user fixed indentation" from "major architectural decision")
2. Read + understand what happened (transcript access broken in hooks)
3. Trigger intelligent processing asynchronously without blocking the working agent
4. Keep multiple context files in sync as a side effect of normal work

**OpenClaw/GitClaw connection:** User has a dockerized OpenClaw setup but wants to explore native options first before resorting to external framework

---

## 3. OPENCLAW RESEARCH FINDINGS

### What Is OpenClaw?

**Context:** User mentioned OpenClaw in passing as a potential solution but never dug deep. The research phase was actually:
1. Documenting what native Claude Code can do
2. Finding the gaps
3. Understanding whether OpenClaw (or similar) is necessary

**What was researched:**
- Claude Code hook capabilities and limitations
- Transcript storage format and accessibility
- Structured JSON output for machine parsing
- Agent SDK native capabilities

### Key Findings from Research

From the "Anthropic Infrastructure Architect" documentation agent (turn ~4000):

**PostToolUse Hook Capabilities:**
- CAN trigger after specific tool use (Write, Edit, Bash)
- CAN receive tool input/output
- CAN have path-based matchers (`"matcher": "Write|Edit"`)
- CANNOT read transcripts reliably (confirmed regression)
- CANNOT trigger other Claude conversations

**Transcript Telemetry:**
- Stored as `.jsonl` files — structured, readable by external scripts
- Path available in hook input (`transcript_path`)
- Different paths for main session vs subagents
- Accessible post-session ✓ but mid-session access broken ✗

**Structured Bycatch (JSON Mode):**
- Claude Code doesn't have native "invisible JSON emission"
- Structured metadata must flow through tool calls or external parsing
- No way to embed machine-readable signals in conversation without it appearing in chat

**Agent SDK Native Capabilities:**
- Strictly request/response, not persistent loops
- No native watcher/daemon mode
- Designed for triggered agents, not background watchers

### Why OpenClaw Was Deferred

User's conclusion: OpenClaw/GitClaw could provide persistent background agent capability (Tier 2 watcher), but:
1. Adds external Docker dependency
2. Complicates deployment (already using Claude Code + git)
3. Native options worth exploring first

Decision: **Focused on what's buildable with Claude Code + git + hooks (Tier 1) before adopting external framework**

---

## 4. DESIGN PHILOSOPHY

### Small Curated Context Packs vs. Comprehensive Dumps

**Philosophy:**
"I never edit notes by hand, it's all through AI. I think at first I will make small vaults with carefully selected items in each vault for specific purposes."

**Implication:** Vaults are **scoped contexts**, not storage libraries

- **Bad:** One 500-file vault with everything → AI context overloaded → hallucination/forgetting
- **Good:** Five 10-file vaults, each for a specific purpose (Security+ study, API design, home lab docs, etc.)

Each vault is a **context engineering** problem: what's the right information for this task?

### Append-Only Structures

**In the vault:** Files are immutable once ingested
- Updated via new versions (e.g., `note_v2.md`)
- Old versions preserved for history
- Changes tracked via git commits

**In the index:** New entries always appended
- Never modify existing index entries in place
- Invalid entries marked with status field (future design)
- Full audit trail of what changed when

**Rationale:** Prevents accidental data loss; enables reconstruction of past states

### Provenance Tracking

**Every indexed file knows its origin:**

```json
"source": "human"  // ingested from io/inbox/
"source": "agent"  // created by ingest.py write command
```

**Rationale:** Context engineering requires understanding what you're looking at:
- Agent-generated content might be draft/experimental
- Human-ingested material has external authority
- Upstream sources (GitHub, downloads) different from in-situ creation

### Self-Awareness of Origin

From the design discussions:
- **Vault** = immutable storage (processed, organized, trustworthy)
- **Bench** = work products (analysis, derivatives, experimental)
- **Inbox** = raw drop zone (unprocessed, unvetted)

Each zone's purpose is clear; agents understand where files belong and what semantics apply.

### Living Documents vs. Static Snapshots

**Living Doc Protocol** (from Notion Bridge Architect PDF):

After every meaningful change, re-index context files:
- Update `project-state.md` to reflect new structure
- Append to `decisions.md` with new rationale
- Summarize session in `session-history.md`

**Automation:** Tier 1 can regenerate state (filesystem scan). Tier 2 would add intelligence (semantic summaries).

**Rationale:** Next session starts with current context, not stale information

---

## 5. WHAT WAS ACTUALLY BUILT vs. WHAT'S PLANNED

### Completed Artifacts

#### ClaudeTest Project

**Location:** `C:\Users\Erinh\Desktop\ClaudeTest\`

1. **ML OS Interactive Demo** (early session)
   - `index.html` — Full SPA with boot animation, 6-panel dashboard
   - `server.py` — Python HTTP dev server on port 3000
   - `src/boot.js`, `src/dashboard.js`, `src/agents.js` — Interactive UI components
   - `src/styles.css` — Dark terminal theme with CSS variables
   - `.cursorrules` — Cursor IDE rules for the project
   - `.claude/launch.json` — Dev server configuration

2. **ML OS Template Composer** (`mlos.py`)
   - Commands: `list`, `compose`, `boot`, `create`
   - Composes Kernel + Schema + Scenario YAML into full system prompts
   - Colored terminal boot sequence display
   - Windows UTF-8 encoding fix applied

3. **ML OS Configuration**
   - `kernel.yaml` — Immutable identity, constants, rules
   - `schema.yaml` — Reasoning protocol, interaction style, behavioral rules
   - `scenarios/` — 4 agent templates (system-architect, research-analyst, code-auditor, doc-writer)

4. **Agent Orchestration** (`cowork.py`)
   - Commands: `init`, `status`, `dispatch`, `assign`, `report`, `sync`, `history`, `memory`
   - Living Doc Protocol: rebuild master context from registry + memory
   - Shared memory directory for agent work products
   - `registry.yaml` — Agent registry with status, task counts, history
   - `context.md` — Master Context Document (auto-updated by sync)

#### Home_Lab_2026 Project

**Location:** `C:\Users\Erinh\Desktop\Home_Lab_2026\`

1. **Vault Ingestion Pipeline** (`.mlos/ingest.py`)
   - `scan` command — preview inbox with structure detection
   - `add` command — ingest files with flatten/preserve nesting
   - `write` command — AI direct-to-vault with auto-index
   - `view` command — query index by project/type
   - `check` command — validate index vs filesystem
   - `export` command — render index as markdown
   - Tests completed and passing; all code exercised

2. **Map of Content Generator** (`.mlos/moc.py`)
   - Recursive directory scanning with heading extraction
   - Markdown table generation with file metadata
   - CLI: `python .mlos/moc.py <dir> [-o] [--depth N] [--flat]`
   - Tested on multiple directories

3. **Metadata Index** (`.mlos/index.json`)
   - 6-field schema: id, filename, type, size, title, ingested, project, source
   - JSON structure for queries and validation
   - Empty but structurally ready

4. **Design Documentation**
   - `.mlos/DRAFT_index_schema_and_workflow.md` — 300+ line spec covering:
     - Directory layout, index schema, processing workflow
     - Path resolution strategy, bench-to-vault referencing
     - Nesting decisions, ID format, open questions
   - `.mlos/prompts/grounding.md` — Agent onboarding about vault structure
   - `.mlos/prompts/explore-with-me.md` — Session initialization prompt

5. **Vault Browser** (`server.py` + `index.html`)
   - HTTP server on port 3001
   - Sidebar navigation (Overview, Projects, Raw Index)
   - File browser with inline markdown rendering
   - File viewer with heading, metadata, code formatting
   - Dark terminal aesthetic matching ML OS demo
   - Status bar showing current path

6. **Context Pack** (First populated vault project: `mlos-dev`)
   - `vault/mlos-dev/project-state.md` — What ML OS is, what exists, current status
   - `vault/mlos-dev/decisions.md` — 8 architectural decisions (D-000 to D-007) with rationale
   - `vault/mlos-dev/session-history.md` — Distilled session summaries
   - `vault/mlos-dev/pickup.md` — The prompt to load full context in new sessions

### In Design / Not Yet Built

1. **Tier 2 Intelligent Watchers**
   - Blocked pending resolution of transcript access via hooks
   - Would read event log + transcripts, update context files
   - No framework chosen yet (native vs. OpenClaw decision pending)

2. **Frontend Visual App**
   - Vault browser exists (read-only)
   - Interactive features not yet implemented:
     - Drag-and-drop file intake
     - Create new vault projects from UI
     - Search across file *contents* (not just index)
     - Update/archive vault items
     - Build context packs from selections

3. **Backend API**
   - Vault browser serves files via simple Flask-like routing
   - Not yet a full REST API for external access
   - Git is storage; GitHub is remote view
   - Home web server concept mentioned but not prioritized

4. **ML OS Integration with Vault**
   - Kernel/Schema/Scenario system exists in ClaudeTest
   - Not yet applied to vault agents
   - Could design agents specific to vault operations

5. **Automatic Context Maintenance**
   - Manual creation of `mlos-dev` context pack
   - Could be automated with proper Tier 1+2 watchers
   - Policy: After each session, update `session-history.md` and `project-state.md`

---

## 6. KEY DECISIONS AND TURNING POINTS

### Turning Point 1: From Scattered Repo to Vault Architecture (Turn ~1600-1650)

**What happened:** User showed the restructured Home_Lab_2026 and Claude recognized it as a complete redesign

**Decision:** "Vault" terminology + three-zone architecture (vault/bench/inbox)

**Rationale:** Clear semantic zones prevent confusion:
- Vault = source of truth, immutable, processed
- Bench = work products, mutable, analysis
- Inbox = raw drop zone, transient

**Impact:** Shaped all downstream tooling (ingest pipeline, index schema)

### Turning Point 2: Minimal Index Schema (Turn ~1640-1750)

**What happened:** Claude proposed a rich upfront index schema; user questioned it

**Decision:** Start with 6 auto-derivable fields; add richer metadata later in batches

**Rationale:** Friction kills adoption. Early versions always under-specify. Better to grow schema as usage patterns emerge.

**Impact:** Enables rapid ingest without manual metadata entry; reduced barrier to first vault population

### Turning Point 3: No Stored Paths (Turn ~1645)

**What happened:** Schema design showed storing file paths in index

**Decision:** Derive paths from `vault/{project}/{filename}` at query time

**Rationale:** Paths go stale; single source of truth is filesystem. Derive on the fly.

**Impact:** Prevents a common source of bugs (orphaned index entries when files move)

### Turning Point 4: From Frontend App to Claude Code as Interface (Turn ~2970)

**What happened:** User said "we don't have to make an app that has a super intricate front end interface, it can be designed to be operated by claude code itself"

**Decision:** Shift from "build a web UI" to "build CLI tools that Claude Code operates"

**Rationale:** Claude is already the interaction layer. Don't duplicate chat; extend the tools.

**Impact:** Simplified architecture. Vault browser is now a *viewer*, not an editor.

### Turning Point 5: Git as Storage Layer (Turn ~2428-2450)

**What happened:** User asked whether storage should be git or home web server

**Decision:** Git is primary storage now; home server comes later as frontend host

**Rationale:**
- Git already works, versioning free, multi-device via pull
- Binary files (PDFs, docx) bloat over time, but small purpose-built vaults won't hit that limit soon
- Home server hosts the visual layer, not the storage

**Impact:** Clarified the architecture stack:
```
Storage: git repo
System:  .mlos/ CLI tools
AI:      Claude (read/write/commit)
Visual:  Frontend app (future)
```

### Turning Point 6: First Context Pack (Turn ~2835-2965)

**What happened:** User proposed vaults as "context packs" for project development

**Decision:** Populate `mlos-dev` vault with 4 files capturing the entire project state

**Rationale:** Dogfood the system; make the first populated vault an example of what's possible

**Impact:** Demonstrated the full loop: ingest → index → query → context. Next session can load pickup.md and continue.

### Turning Point 7: Write Command as Direct-to-Vault (Turn ~2451-2640)

**What happened:** Discussed whether AI-generated content goes through inbox or directly to vault

**Decision:** Added `write` command for direct-to-vault with automatic indexing

**Rationale:**
- AI already knows what it's creating and where it belongs
- Inbox is for human-dropped files needing classification
- Eliminate unnecessary steps for agent-generated content

**Impact:** Closed the loop on "give AI ability to create/store/retrieve files"

---

## 7. OPEN QUESTIONS AND UNRESOLVED ISSUES

### Architectural

1. **Tier 2 Implementation**
   - PostToolUse hooks can't read transcripts reliably (confirmed regression)
   - Need background agent capability for intelligent context maintenance
   - Decision pending: Native solution vs. OpenClaw/GitClaw integration

2. **Backend API**
   - Vault browser works for viewing
   - No full REST API yet for programmatic access
   - Will be needed if running multiple devices or integrating with external tools

3. **Home Web Server**
   - Concept mentioned but deprioritized
   - When needed: Will host vault browser UI accessible from home network
   - Not urgent while git + GitHub + localhost suffice

### Operational

4. **Document Population**
   - Vault system is built and ready
   - No documents ingested yet (structure exists, pipeline works, index empty)
   - User pain point: reliably pulling docs from multiple sources (downloads, old projects, GitHub) into inbox
   - Gap: No tooling to pull from external sources; manual file copy only

5. **Living Doc Maintenance Policy**
   - `mlos-dev` context pack created manually this session
   - Future sessions should update `project-state.md`, `decisions.md`, `session-history.md` after work
   - No automation yet (waiting on Tier 2 solution)

6. **ML OS Agent Integration**
   - Kernel/Schema/Scenario system exists but separate from vault
   - Could design vault-specific agents (ingest coordinator, context maintainer, query agent, etc.)
   - Deferred pending Tier 1+2 watcher completion

### Technical Debt

7. **Encoding Issues (Mostly Fixed)**
   - Windows UTF-8 mojibake (em-dash rendering as `â€"`) — fixed with `sys.stdout` wrapping
   - Fix applied to: mlos.py, cowork.py, ingest.py
   - Server.py may need same fix for file reading

8. **File Watcher Not Yet Implemented**
   - Concept discussed; Python `watchdog` mentioned as approach
   - Would trigger Tier 1 regeneration (rebuild MOCs, validate index)
   - Deferred in favor of explicit commands for now

9. **Git Integration**
   - `write` command doesn't auto-commit (user specified this: keep git separate)
   - Pipeline complete but no auto-push workflow documented
   - Manual `git add + commit + push` after ingest

10. **Search Capability**
    - Index query (by project/type) works
    - Full-text search across file *contents* not yet implemented
    - Would require either:
      - Building an in-memory search index (lightweight)
      - Using grep against vault directory (command-line only)
      - Indexing in SQLite (adds dependency)

### Design Decisions Still Pending

11. **Context Pack Template**
    - Created `mlos-dev` manually (project-state, decisions, session-history, pickup)
    - Should this become a standard template for all new vaults?
    - When to populate: before first use or lazily as documentation emerges?

12. **Bench-to-Vault Referencing**
    - Spec mentions using HTML comments and relative paths
    - Not yet implemented or tested
    - Needed for MOCs and analysis documents to link back to source materials

13. **Subpath Preservation in Index**
    - `ingest.py` preserves nested folder structure with `subpath` field (when `--preserve` used)
    - Not yet used in views/queries
    - Could enable hierarchical browsing, but adds complexity

---

## 8. SESSION ARTIFACTS CREATED

### Python Scripts

1. **`.mlos/ingest.py`** — 500+ lines
   - Core ingest pipeline with all commands (scan, add, write, view, check, export)
   - Auto title extraction, collision handling, 8-char ID generation
   - Index read/write, filesystem operations
   - Tested end-to-end

2. **`.mlos/moc.py`** — 300+ lines
   - Directory scanning with heading extraction
   - Markdown rendering with tables and grouping
   - CLI with multiple output formats

3. **`mlos.py`** (ClaudeTest) — 200+ lines
   - ML OS template composer
   - Kernel + Schema + Scenario composition
   - Terminal boot sequence display with colors

4. **`cowork.py`** (ClaudeTest) — 400+ lines
   - Agent orchestration and dispatch
   - Living Doc Protocol implementation
   - Registry, memory, history management

5. **`server.py`** (Home_Lab_2026) — 150+ lines
   - Flask-like HTTP routing
   - `/api/` endpoints for vault queries
   - File reading and markdown rendering

### YAML Configurations

6. **`.mlos/kernel.yaml`** — Immutable ML OS identity
7. **`.mlos/schema.yaml`** — Behavioral engine for agents
8. **`.mlos/scenarios/` × 4** — system-architect, research-analyst, code-auditor, doc-writer
9. **`.mlos/registry.yaml`** — Agent registry
10. **`.claude/launch.json`** × 2 — Dev server configs (ClaudeTest, Home_Lab_2026)

### Documentation

11. **`.mlos/DRAFT_index_schema_and_workflow.md`** — 300+ lines, full design spec
12. **`.mlos/prompts/grounding.md`** — Agent onboarding
13. **`.mlos/prompts/explore-with-me.md`** — Session initialization
14. **`CLAUDE.md`** × 2 — Project orientation docs

### Populated Vault Content

15. **`vault/mlos-dev/project-state.md`** — System overview and status
16. **`vault/mlos-dev/decisions.md`** — 8 architectural decisions with rationale
17. **`vault/mlos-dev/session-history.md`** — Session summaries
18. **`vault/mlos-dev/pickup.md`** — Context loading prompt

### UI Files

19. **`index.html`** (ClaudeTest) — ML OS demo SPA (650+ lines)
20. **`index.html`** (Home_Lab_2026) — Vault browser SPA (500+ lines)
21. **`src/boot.js`, `src/dashboard.js`, `src/agents.js`, `src/styles.css`** (ClaudeTest)

---

## 9. KEY TECHNICAL PATTERNS

### Pattern 1: Index-Driven Architecture

Everything traces back to `index.json`:
- Ingest writes to index
- Queries read from index
- Validation checks index vs filesystem
- Views render from index
- Frontend displays index

No database; filesystem + JSON as source of truth

### Pattern 2: Minimal Metadata at Ingest, Richer Later

Ingest creates only what's auto-derivable (6 fields).
Richer metadata (tags, objectives, references) added later in batches as patterns emerge.
Prevents friction; enables iteration.

### Pattern 3: Git as Free Versioning

Every ingest, every write, every change → git commit.
No need for separate version management system.
History, rollback, audit trail all free.

### Pattern 4: CLI-First Interface

All operations exposed as command-line tools.
Claude Code operates them through Bash.
Web UI is optional viewer on top.

### Pattern 5: Provenance Tracking via Source Field

`"source": "human"` vs. `"source": "agent"` in every index entry.
Enables understanding what you're looking at.
Could extend to include URL, timestamp, project origin, etc.

### Pattern 6: Living Documents

Context files are regenerated/updated after each session.
Tier 1: Filesystem scan (mechanical)
Tier 2: Transcript analysis (intelligent, pending implementation)

### Pattern 7: Staged Processing

Raw → Inbox → Vault → Bench
Each stage has different semantics:
- Inbox: unvetted, transient, raw
- Vault: organized, indexed, immutable (versioned)
- Bench: processed, analysis, work products

---

## 10. TECHNICAL CONSTRAINTS AND LIMITATIONS DISCOVERED

### Claude Code Hooks

- **PostToolUse works:** Fires after Write/Edit, receives file path, supports matchers
- **Stop hook broken:** Transcript access regression, cannot read conversation contents
- **Cannot scope to paths:** Fires on all writes, not filterable to vault/ only
- **Cannot trigger conversations:** Can only run shell commands
- **Synchronous:** Blocks if slow (no async escape hatch)

### Transcript Access

- **Storage:** `.jsonl` files in `~/.claude/projects/*/`
- **Post-session:** Readable by external scripts ✓
- **Mid-session from hooks:** Broken ✗ (confirmed regression)
- **Implication:** Cannot do Tier 2 intelligent processing within hook; must be external daemon

### Python Platform Quirks

- **Windows encoding:** UTF-8 mojibake with box-drawing chars; fix: `sys.stdout = io.TextIOWrapper(...)`
- **Missing `head` command:** Git Bash on Windows doesn't have `head`; work around with Python
- **Node.js not installed:** npm/npx/node not available; pivoted to vanilla JS + Python server

### Git-Based Vault

- **Binary bloat:** PDFs, docx files bloat repo over time
- **Mitigation:** Small purpose-built vaults won't hit limit soon; Git LFS available if needed
- **No native performance:** git operations slower than database queries (not an issue at current scale)

---

## SUMMARY

**What was built:** A fully functional vault ingestion and browsing system with:
- 3-zone architecture (vault/bench/inbox)
- Automated index generation and querying
- Direct-to-vault writing for AI agents
- Web UI vault browser
- First populated context pack (`mlos-dev`)
- Design docs and agent prompts
- Working ingest pipeline tested end-to-end

**What remains:**
- Tier 2 intelligent watchers (context maintenance)
- Full document population (docs sourcing/collection)
- Extended CLI features (search, batch operations)
- ML OS agent integration with vault
- Home web server for multi-device access

**Key insight:** The system is fundamentally sound but unfinished. It works for small, carefully curated vaults. Scaling to large document collections or adding intelligent context maintenance requires solving the Tier 2 watcher problem.

**User's position:** "Small vaults for specific purposes" — context engineering, not storage. This aligns with the design.

---

**Prepared:** 2026-03-06
**Status:** Session Complete
**Next Phase:** Tier 2 implementation or document population
