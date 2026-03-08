# CLAUDE.md — Workspace Boot Sequence

You are entering Mimir's shared workspace. Before doing anything, run the full boot sequence below in order. Do not skip steps.

---

## Repository

- **Remote:** `https://github.com/mrmeman555/OpenClaw_Claude.git`
- **Auth:** GitHub PAT stored in `.context/.secrets` (gitignored, local only). To push: `git remote set-url origin https://<user>:<pat>@github.com/mrmeman555/OpenClaw_Claude.git`
- **Branch:** `main` (or active session branch if bootstrap was run)

---

## Step 0: Orient Before Anything Else

Run these silently before saying a word.

### 0a — Pull latest
```bash
git pull origin main
```
If on a session branch, pull that branch too. If remote is ahead, note what changed.

### 0b — Read INBOX
Read `.claude/INBOX.md`. Surface any `[UNREAD]` entries immediately — these are notes left by cloud agents (Claude Chat) from recent sessions. They contain decisions made, tasks created, and what to prioritize. Mark them `[READ]` after surfacing.

If INBOX has unread entries, **lead with them** before anything else in your first response.

### 0c — Check active session branch
```bash
git branch --show-current
```
If on a `session/{project}/{date}/{id}` branch — a bootstrap session is active. Note the project and date. If on `main` — no session is active, bootstrap has not been run yet.

### 0d — Pull vault then query open tasks
```bash
cd $MLOS_ROOT/Home_Lab_2026 && git pull origin main
python $MLOS_ROOT/Home_Lab_2026/.mlos/ingest.py task list --project mlos-dev
```
Pull Claude-Cowork-Vault first — task list is stale without this. Then scan for high priority open tasks and surface the top 3-5 in your opening summary.

### 0e — Freshness check (per-turn)
On every subsequent turn — not just at boot — check if remote is ahead:
```bash
git fetch origin -q && git log HEAD..origin/main --oneline
```
If new commits exist, pull before responding. Briefly note what changed: "Pulled — 2 new commits on vault (task updates)." This keeps the agent in sync when other agents push mid-session.

---

## Step 1: Know Who You're Working With

Read `.context/mimir.md` for the full operator profile. The short version:

- Mimir is a systems thinker with deep CCNA networking knowledge, currently working through Security+ and building out a home lab.
- Background in experimental psychology (near-PhD, 3.97 GPA) — applies cognitive science to AI context engineering. His ML OS methodology treats prompts as cognitive architectures, not instructions.
- Lead with "why" before "how." Socratic over lecture. Don't re-teach what he already knows.
- Production network (VLANs 10/20/99) is **off-limits**. Lab work lives on VLANs 50/51/52.
- Building ML OS infrastructure as a long-term personal system. Career direction: sysadmin/security.

---

## Step 2: Understand the Workspace

Read `.context/workspace.md` for full conventions. The short version:

- This repo is shared across **Claude Code**, **Cowork**, and **Claude Chat App**.
- `.context/engines/` contains project-specific engine prompts.
- `projects/` contains project-specific artifacts, pickup documents, and research.
- `.claude/transcripts/registry.md` — share URLs for Claude Chat sessions.
- `.claude/commands/` — slash commands. `/sync` for context-aware repo sync.

---

## Step 3: Ground Yourself

**Do not assume what Mimir wants to work on.** Instead:

1. **Scan for state.** Check `projects/` for pickup docs and `PROGRESS.md` files. Check recent commits (`git log --oneline -5`).
2. **Scan available engines.** List what is in `.context/engines/`.
3. **Present and ask.** Summarize what you found and ask what to work on.

Format your opening like:
> "[INBOX: <summary of unread notes if any>] | Active session: <branch or none> | Top tasks: <t-xxxx, t-xxxx> | Recent commits: <summary> | What are we working on?"

If Mimir names a specific engine, load the full engine prompt from `.context/engines/` and follow its protocol including Phase 0.

If Mimir names a project, load `projects/<n>/pickup.md`.

If no engine exists yet, enter **Flow Mode** — read `.context/flow.md`.

If Mimir gives a quick/simple request, just do it. Do not over-ceremonialize trivial tasks.

---

## Step 4: Work

- **Leave artifacts.** Sessions should produce or update files. Conversations that evaporate are wasted.
- **Track progress.** Keep `PROGRESS.md` or `pickup.md` current.
- **Respect boundaries.** Flag anything touching VLANs 10/20/99 with a warning.
- **Stay calibrated.** Intermediate-to-advanced networking, early-intermediate security, advanced cognitive/prompt engineering.
- **Commit and push.** Auth in `.context/.secrets`.
- **Update tasks.** Use ingest.py if tasks were created or completed this session.

---

## Step 5: Reflect

Read `.context/flow.md` for the full reflexivity protocol. Runs continuously in the background.

- Watch for drift — is the engine still matching how Mimir works?
- Watch for emergence — are patterns forming that could become engines?
- Surface at natural breakpoints. Propose, do not prescribe.
- Log significant observations in `.context/reflexivity_log.md`.

---

## Step 6: Close the Session

When Mimir signals end of session:

1. Update `.claude/INBOX.md` with a session summary for the next agent.
2. Commit outstanding changes and push.
3. If on a session branch, offer to run session-close.sh.

INBOX update format:
```
## [UNREAD] Session {date} — {surface}
**Branch:** {branch}
### What we worked on
### Tasks created/updated
### Key decisions
### What to do next
```

---

## Linked Workspaces

Paths are device-local — defined in `Home_Lab_2026/.env` (gitignored). Each device sets this file once.
Variables: `MLOS_ROOT`, `OPENCLAW_DIR`, `VAULT_DIR`, `CLAUDETEST_DIR`

| Workspace | Path | What Lives There |
|-----------|------|-----------------|
| **Home_Lab_2026** (Vault) | `$MLOS_ROOT/Home_Lab_2026` | ingest.py CLI, server.py API (port 3001), vault browser, tasks.json. Git: Claude-Cowork-Vault |
| **ClaudeTest** (ML OS Demo) | `$CLAUDETEST_DIR` | ML OS visualization, dev server port 3000 |
| **OpenClaw_Claude** (This Repo) | `$OPENCLAW_DIR` | Engines, research, operator profile, reflexivity system |

### Key commands
- **Task list:** `python $MLOS_ROOT/Home_Lab_2026/.mlos/ingest.py task list --project mlos-dev`
- **Task add:** `python $MLOS_ROOT/Home_Lab_2026/.mlos/ingest.py task add --project mlos-dev --title "..." --priority high --type task --notes "..."`
- **Vault browser:** `python $MLOS_ROOT/Home_Lab_2026/server.py` then http://localhost:3001
- **Bootstrap:** `bash $MLOS_ROOT/Home_Lab_2026/.mlos/bootstrap.sh`
- **Session close:** `bash $MLOS_ROOT/Home_Lab_2026/.mlos/session-close.sh`

---

## Quick Reference: Active Projects

| Project | Pickup Doc | Status |
|---------|-----------|--------|
| OpenClaw Research | `projects/openclaw/pickup.md` | Early research / requirements discovery |
| ML OS Infrastructure | `vault/mlos-dev/tasks.json` | Active build — see task list |

## Quick Reference: Available Engines

| Engine | File | Triggers |
|--------|------|----------|
| Security Lab Build | `.context/engines/security_lab_build.md` | "Design Review", "Build Mode", "Lab Exercise", "Concept Bridge" |
| Network Architect Mentor | `.context/engines/network_architect_mentor.md` | "Lab Mode", "Subnetting Mode", "General Chat" |

*These tables update as new projects and engines are added.*
