# Setup Sync Command

Create the `/sync` slash command for this workspace. This is a one-time setup task.

## What to build

Create the file `.claude/commands/sync.md` in this repo (OpenClaw_Claude) with the following behavior:

### The `/sync` command should:

**Step 1 — Read the inbox first**
- Read `.claude/INBOX.md` in OpenClaw_Claude
- Surface any `[UNREAD]` entries to the operator — these are notes left by cloud agents (Claude Chat) from recent sessions
- After surfacing, mark them `[READ]` in the file

**Step 2 — Read the situation (do this silently before saying anything)**
- Check `git log --oneline -5` on the current branch — what's been committed recently?
- Check `git status` — any uncommitted changes?
- Check what branch is currently active — is it a session branch or main?
- Run `cd C:/Users/Erinh/Desktop/Home_Lab_2026 && git fetch origin -q && git log HEAD..origin/main --oneline` — how many commits is the vault behind?
- If the vault server is running, check `curl -s localhost:3001/api/tasks` for task count — compare against what the agent last saw

**Step 3 — Make an intelligent prediction, then ask**

Based on what you found, present a short situational summary and propose what to sync. Examples of what good output looks like:

- *"Claude-Cowork-Vault has 3 new commits since your last pull (2 task updates, 1 bootstrap fix). Session branch session/mlos-dev/2026-03-07/bwgh is active. Want me to: (1) pull vault, (2) push session branch to remote, or (3) both?"*
- *"Everything looks current. Vault is up to date, session branch is pushed. Nothing obvious to sync — what did you have in mind?"*
- *"You have uncommitted changes in OpenClaw_Claude. Want me to commit and push those before syncing anything else?"*

**Step 4 — Wait for confirmation, then execute**

Only act after the operator confirms or redirects. Don't auto-execute anything.

**Step 5 — Report what was done**

Brief summary: what was pulled, what was pushed, what changed.

---

## After creating the file

1. Confirm the file exists at `.claude/commands/sync.md`
2. Commit it: `git add .claude/commands/sync.md && git commit -m "feat: add /sync slash command — context-aware sync protocol"`
3. Push to origin main
4. Tell the operator: "Done — type `/sync` next time you want to sync and I'll read the situation first."
