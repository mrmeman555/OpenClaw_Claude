# Agent Inbox

Messages left by cloud agents for local agents to read on next sync.
After reading, mark entries as `[READ]` — do not delete, archive at bottom.

---

## [READ] Session 2026-03-07 — Cloud Agent (Claude Chat)

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

*Entries below this line are archived (already read)*
