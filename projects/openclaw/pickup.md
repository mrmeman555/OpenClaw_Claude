# OpenClaw Project — Pickup Document

> **Created:** 2026-03-06
> **Session:** Cowork — OpenClaw Research & Architecture Discussion
> **Status:** Early research / requirements discovery

---

## 1. What This Project Is

OpenClaw is a research and architecture project exploring how to build persistent, cost-effective AI agent infrastructure on top of Mimir's ML OS methodology. The name comes from the open-source tool "OpenClaw" which is one candidate in the design space, but the project scope is broader: **what is the minimum viable persistent layer needed to close the Tier 2 gap in Mimir's vault architecture?**

### The Problem Being Solved

Mimir's vault system (built in `Home_Lab_2026/`) has two tiers of automation:

- **Tier 1 (Mechanical):** Deterministic state regeneration from filesystem/index/git. Buildable now with scripts and hooks. No LLM needed.
- **Tier 2 (Intelligent):** Semantic extraction from transcripts and events — understanding *what happened* and *why*, then updating context files. Requires an LLM but was blocked by Claude Code hook limitations (transcript access broken, hooks not path-scoped, synchronous, can't trigger other conversations).

This project explores external solutions for Tier 2.

---

## 2. Key Decisions Made

### D-001: Native-First, Then External
Mimir deliberately exhausted native Anthropic tooling (Claude Code hooks, PostToolUse, stop hooks, transcript access) before reaching for external tools. The gaps are documented — this isn't speculation, it's empirically verified limitations.

### D-002: SQLite + JSON Hybrid Storage
The project tracking system will use SQLite with relational columns for stable structure (project IDs, entity types, timestamps, relationships) and JSON columns for variable agent-emitted metadata. Rationale: agents can emit structured JSON bycatch that drops directly into JSON columns without schema mapping, while relational structure handles connections between entities.

### D-003: Model as Commodity Hardware
If context engineering (ML OS grounding prompts) is tight enough, the Tier 2 model doesn't need to be a frontier model. Haiku, local models via Ollama, or cheap API providers could handle structured extraction tasks. The intelligence lives in the grounding architecture, not the model. This is testable — run the same prompt against Opus, Sonnet, Haiku, and a local model, compare quality.

### D-004: Context Caching as Cost Strategy
ML OS's kernel/schema/scenario separation is designed for prompt caching. The immutable kernel and stable schema form a large cacheable prefix. Repeated Tier 2 calls against the same grounding template pay full price once, then ~90% discount on subsequent calls. This was intentional architecture, not accidental.

### D-005: Vault Browser as Read Layer
The vault browser concept (from `Home_Lab_2026/server.py`) should be integrated into this workspace as the visualization layer on top of the SQLite database. No more manually organizing folders — projects are the organizing principle, and everything (transcripts, artifacts, agents, context files) is associated relationally.

### D-006: Project-Centric Organization
Moving from file/folder organization to relation-organized structure. A transcript isn't filed in `/Inbox/` — it's linked to a project. Artifacts created during a session are linked to both the project and the transcript that spawned them. Agents, CLAUDE.md files, context packs — all nodes in a graph with the project as hub.

### D-007: Claude Code Headless as Tier 2 Runtime (Start Here)
Before adopting any external orchestrator, start with Claude Code's headless mode (`claude -p`) triggered by cron. This runs on the existing Max subscription ($200/month plan) — no API key needed, no external dependencies. The loop: cron detects new transcripts or vault changes → shell script calls `claude -p` with an ML OS grounding prompt → Claude reads, extracts, writes back to vault → exits. If rate limits or capability gaps emerge, *then* evaluate OpenClaw/NanoClaw with concrete evidence of what's missing. External tooling is the fallback, not the starting point.

### D-008: Leverage Existing Skill/MCP/Schedule Infrastructure
Rather than building raw orchestration infrastructure, use what's already built into the Claude tool ecosystem:
- **Schedule skill** (Cowork) — creates scheduled tasks on intervals. Potential lighter path to Tier 2 watchers than system-level cron.
- **MCP Builder skill** — expose the vault system (SQLite DB, ingest pipeline, index queries) as an MCP server. Any Claude tool (Chat, Cowork, Code) could then interact with the vault through native tool calls instead of CLI wrappers.
- **Skill Creator skill** — build custom skills with Mimir's cognitive engineering methodology. Skills are essentially ML OS grounding prompts with tool access and trigger conditions. The skill-creator includes eval/benchmarking tooling for measuring performance scientifically.
- **Custom skills as ML OS delivery mechanism** — a skill IS a grounding prompt packaged for reuse. Mimir's psych/cognitive science background applied to skill architecture could produce agents that self-enforce scope boundaries through cognitive framing rather than code-level permissions.

This is the "cheater tools" strategy: use existing scaffolding to unlock complex builds. Each well-built skill/MCP server compounds into the next tier of capability.

---

## 3. Research Findings

### OpenClaw
- Persistent self-hosted AI agent (Node.js Gateway at 127.0.0.1:18789)
- 214K+ GitHub stars, created by Peter Steinberger
- Runs continuously as a daemon — the missing persistence layer
- Built-in cron/heartbeat system (default every 30 min, reads HEARTBEAT.md, decides whether to act)
- ACP (Agent Client Protocol) can orchestrate external coding agents including Claude Code
- Skill registry (ClawHub) with 13K+ community skills
- Supports Anthropic API, OpenAI, Ollama (local models)
- **Requires Anthropic API key** — Pro/Max OAuth tokens blocked as of Jan 2026
- Half a million lines of code, 53 config files, 70+ dependencies — heavyweight
- Had a high-severity security vulnerability (Jan 30, 2026) — 42K instances exposed

### NanoClaw
- Lightweight alternative, built on Anthropic Agent SDK (runs Claude Code natively)
- Container-isolated (Docker/Apple Container) — true OS-level sandboxing
- ~35K tokens total codebase — Claude can read and understand the entire thing
- SQLite for state, per-group CLAUDE.md for persistent memory
- Task scheduler for recurring jobs
- Single-process polling model: Channels -> SQLite -> Polling Loop -> Container -> Response
- Much closer to Mimir's "small, curated, first-principles" philosophy

### Key Comparison

| Dimension | OpenClaw | NanoClaw | Custom (Python + watchdog + API) |
|-----------|----------|----------|----------------------------------|
| Persistence | Built-in daemon | Built-in daemon | DIY with systemd/launchd |
| Scheduling | Cron/heartbeat native | Task scheduler | DIY with cron or watchdog |
| Claude Code orchestration | ACP protocol | IS Claude Code | Subprocess/API calls |
| Complexity | ~500K lines | ~35K tokens | Whatever you build |
| Messaging integration | WhatsApp, Telegram, Slack, etc. | Same | Not needed |
| Local model support | Ollama | Via Agent SDK | Direct Ollama API |
| Security model | App-level (weaker) | Container isolation | Your choice |

---

## 4. Open Research Threads

### Must Resolve
- **Tier 2 task specification:** What exactly do the watcher prompts look like? Spec them at the prompt level to determine minimum model capability needed.
- **Model cost benchmarking:** Run identical extraction tasks against Opus/Sonnet/Haiku/local to find the quality floor.
- **Orchestrator decision:** OpenClaw vs NanoClaw vs custom Python daemon. Depends on what Tier 2 tasks actually require.

### Should Explore
- **ACP protocol deep-dive:** How exactly does OpenClaw dispatch Claude Code sessions? Could this be extracted without adopting all of OpenClaw?
- **Anthropic Agent Teams:** Released Feb 5, 2026 as Research Preview. Built-in orchestration layer hidden in Claude Code under "TeammateTool" feature flag. Could this eventually replace external orchestrators?
- **Context caching implementation:** How to structure API calls to maximize cache hits with ML OS grounding templates.

### Future Design
- **SQLite schema design:** Entity types, relationship model, JSON column specs for the project database.
- **Vault browser adaptation:** Port/adapt the Home_Lab_2026 vault browser for this workspace's project structure.
- **Transcript auto-processing pipeline:** From raw .jsonl export -> processed markdown -> project association -> artifact linking.

---

## 5. Deferred Artifacts

These should be created when the time is right — not now.

| Artifact | Purpose | When to Create |
|----------|---------|----------------|
| `schema.sql` | SQLite database schema for project tracking | When ready to implement the DB layer |
| `openclaw_architecture_deepdive.md` | Source-level analysis of cron/heartbeat/ACP/context-engine/skill internals through Tier 2 lens | **CREATED 2026-03-06** — see `projects/openclaw/openclaw_architecture_deepdive.md` |
| `openclaw_eval.md` | Detailed technical evaluation of OpenClaw for Tier 2 | After ACP deep-dive and hands-on testing |
| `tier2_task_specs.md` | Actual prompt specifications for each Tier 2 watcher task | When designing the watcher agents |
| `cost_model.md` | Token cost analysis across model tiers with caching | After running benchmark tests |
| `vault_browser_v2/` | Adapted vault browser for project-centric SQLite backend | After schema is designed |
| Custom skills | ML OS-engineered skills for vault operations, scheduling, context maintenance | After analyzing prebuilt skill patterns |
| Vault MCP server | MCP server exposing vault/DB to all Claude tools natively | After SQLite schema + MCP builder skill review |

---

## 6. Associated Transcripts

### This Session (Cowork — OpenClaw Research)
- **Location:** Will be exported to `Inbox/` on session end
- **Content:** Grounding in prior work (workspace setup session + Claude Code vault session), OpenClaw/NanoClaw research, cost strategy discussion, architectural decisions about SQLite + JSON hybrid, project-centric organization, this pickup document
- **Key moments:** Cost optimization via ML OS grounding, "the model is commodity hardware" validated against Tier 2, context caching as intentional (not accidental) architecture, shift from folder-organized to relation-organized, discovery of schedule/MCP/skill-creator infrastructure as low-hanging fruit, "cheater tools" strategy for enabling complex builds

### Claude Code Vault Session
- **Location:** `Inbox/bb17b72e-d58d-4787-8305-bfd4f817884f.jsonl`
- **Content:** 881-turn session building the vault architecture in Home_Lab_2026 — ingest.py, index.json, moc.py, server.py, vault browser, context pack creation, Tier 1/Tier 2 problem definition, PostToolUse hook investigation
- **Key moments:** Vault/bench/inbox zone design, minimal index schema, "Claude Code as interface" pivot, write command for direct-to-vault, first context pack (mlos-dev)

### Workspace Setup Session
- **Location:** `.context/transcripts/2026-03-06_set_up_shared_workspace_repository.md`
- **Content:** 88-turn session building CLAUDE.md boot sequence, operator profile, engine prompts, Flow Mode, reflexivity system
- **Key moments:** Kernel/schema/scenario mapping to file structure, "propose don't prescribe" principle, engine-as-cartridge architecture

---

## 7. For the Next Agent

If you're reading this to continue the OpenClaw project:

1. **Read this document first** — it's the convergence point for three sessions of work.
2. **Read the Claude Code vault transcript** (`Inbox/bb17b72e-...jsonl`) if you need deep technical context on the vault architecture and Tier 2 problem. Use the transcript processor (`.context/tools/process_transcript.py`) to convert it to readable markdown.
3. **Don't assume decisions are final.** This project is in discovery phase. The decisions above reflect current thinking, not commitments.
4. **Ask Mimir for grounding.** He knows where the project is heading better than any document can capture. Present what you see, ask what's next.
