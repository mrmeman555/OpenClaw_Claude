# Sync Command

Context-aware sync protocol for the ML OS multi-workspace system.

## Step 1 — Read the inbox

- Read `.claude/INBOX.md` in OpenClaw_Claude
- Surface any `[UNREAD]` entries to the operator — these are notes left by cloud agents (Claude Chat) from recent sessions
- After surfacing, mark them `[READ]` in the file

## Step 2 — Read the situation (do this silently before saying anything)

Gather all of the following before producing any output:

- `git log --oneline -5` on the current branch in OpenClaw_Claude — what's been committed recently?
- `git status` in OpenClaw_Claude — any uncommitted changes?
- What branch is currently active — is it a session branch or main?
- Read the VAULT_DIR path from `Home_Lab_2026/.env` (sibling repo), then `cd <vault-repo-root> && git fetch origin -q && git log HEAD..origin/main --oneline` — how many commits is the vault behind? The vault repo root is the parent of VAULT_DIR.
- If the vault server is running (`curl -s localhost:3001/api/tasks`), check task count

## Step 3 — Make an intelligent prediction, then ask

Based on what you found, present a short situational summary and propose what to sync. Examples:

- *"Claude-Cowork-Vault has 3 new commits since your last pull (2 task updates, 1 bootstrap fix). Session branch is active. Want me to: (1) pull vault, (2) push session branch, or (3) both?"*
- *"Everything looks current. Vault is up to date, session branch is pushed. Nothing obvious to sync — what did you have in mind?"*
- *"You have uncommitted changes in OpenClaw_Claude. Want me to commit and push those before syncing anything else?"*

## Step 4 — Wait for confirmation, then execute

Only act after the operator confirms or redirects. Do not auto-execute anything.

## Step 5 — Report what was done

Brief summary: what was pulled, what was pushed, what changed.
