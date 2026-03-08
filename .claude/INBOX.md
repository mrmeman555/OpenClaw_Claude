# Agent Inbox

Messages left by cloud agents for local agents to read on next sync.
After reading, mark entries as `[READ]` — do not delete, archive at bottom.

---

## [UNREAD] Session 2026-03-07 — Cloud Agent (Claude Chat)

**Session branch:** session/mlos-dev/2026-03-07/bwgh

### What we worked on
Long design session covering context pack generation, the ML OS Case Study 001 (Net+ Autonomous Grounding), vault browser improvements, and agent-to-agent communication patterns.

### Tasks created this session (all in Claude-Cowork-Vault / mlos-dev)
- `t-50fea1` — Design context pack generator (grounding prompt factory) — HIGH
- `t-889a68` — Revisit: associate Claude Chat sessions with vault + transcript capture — MEDIUM (parked)
- `t-45aa7d` — Add `created_from` + `agent_id` fields to task schema and ingest.py — HIGH (do this next)
- `t-2da901` — Add manual refresh button to vault browser tasks view — LOW (quick win)
- `t-49c238` — Architect direct cloud-agent-to-vault sync via Cloudflare/ngrok tunnel — MEDIUM
- `t-cbeff8` — EXTENDED (already existed) — updated notes with generated-context-on-demand design direction

### Key decisions / context
1. **`t-45aa7d` is the priority build task** — schema addition to tasks.json + ingest.py `--session` and `--agent` flags. Backward compatible. This is a clean Code agent handoff.
2. **Context pack generator** — the ML OS Runtime Grounding Sequence (Identity Recall → State Ingestion → History Loading → Artifact Contextualization → Gap Identification) is the template. Generator takes domain + history + state + gap and outputs a complete `.context/` folder. Reference: `CASE_STUDY.md` uploaded this session.
3. **Vault browser static files** — `project-state.md`, `decisions.md`, `session-history.md`, `pickup.md` should NOT exist as stored documents. Replace with `GET /api/project/{name}/context` that generates fresh snapshots from tasks.json + git log + watcher.db. Real artifacts (case studies, design docs) stay as files.
4. **`/sync` command** — being set up this session via `/setup-sync`. Inbox-first pattern: sync reads this file before doing anything else.
5. **Tunnel architecture** — current git-as-sync-layer is a workaround. Long term: expose localhost:3001 via Cloudflare Tunnel, cloud agent writes directly to vault API. Git reverts to version control only.

### What local agent should do
- Pull Claude-Cowork-Vault to see the 6 new tasks
- Prioritize `t-45aa7d` for next Code agent session
- Run `/setup-sync` if it hasn't been run yet — will build the `/sync` command

---


## [UNREAD] Session 2026-03-07 (cont.) — Cloud Agent (Claude Chat)

**Share URL:** https://claude.ai/share/e2be28ae-36c5-47b6-8514-e57cb590b018
**Follows from:** https://claude.ai/share/ef10710c-f1aa-4035-bc99-f5521c354a13

### Key decisions this session
1. **Switching to Claude Code** for future design sessions — replaces Claude Chat. Local `.jsonl` transcripts make context capture native, no browser extension needed for Code surface.
2. **Transcript registry created** — `.claude/transcripts/registry.md` in OpenClaw_Claude stores share URLs for session bwgh until real capture infrastructure exists.
3. **Boot sequence assessment** — CLAUDE.md is missing: INBOX read at boot, vault/task query, session branch awareness. Needs Step 0 added.

### Tasks created this session
- `t-9271e6` — Browser extension for real-time Claude Chat transcript capture — HIGH
- `t-47b4df` — Add active file watcher to watcher.py (GAP-008) — HIGH
- `t-265094` — Design system for agents to self-modify boot sequences/engines — HIGH
- `t-11cc79` — Figure out what to do with stored transcript URLs — HIGH

### What to do next
- Boot Claude Code, run bootstrap.sh, pick mlos-dev
- Read `.claude/transcripts/registry.md` — two chat URLs stored there
- Priority build: `t-45aa7d` (created_from + agent_id on task schema) — still the cleanest next Code agent task
- CLAUDE.md needs Step 0: read INBOX before anything else
- Unresolved at session end: how Claude Code app environment/branch selection works — Mimir was too tired to explore


---

*Entries below this line are archived (already read)*
