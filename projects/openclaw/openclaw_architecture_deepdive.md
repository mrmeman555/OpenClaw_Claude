# OpenClaw Architecture Deep-Dive
> **Created:** 2026-03-06  
> **Purpose:** Source-level analysis of OpenClaw internals through the lens of the Tier 2 vault watcher problem  
> **Method:** GitHub issue mining, official docs, architecture reconstruction from bug reports and discussions  
> **Status:** Research complete — see Tier 2 fit assessment at bottom

---

## The Question This Answers

The Tier 2 problem needs a **persistent watcher runtime**: something that runs continuously, detects new transcripts/vault changes, calls an LLM with ML OS grounding, and writes context files back. The question is whether any specific OpenClaw mechanism could serve as that runtime *without* adopting all of OpenClaw.

---

## 1. Gateway Architecture — The WebSocket Control Plane

### What It Is

The Gateway is OpenClaw's central process — a long-running Node.js daemon (bound to `127.0.0.1:18789` by default) that acts as a **channel-agnostic message router**. The key design insight: the agent logic (`run_agent_turn`) is completely decoupled from the channel it receives messages from.

```
[Telegram] ─┐
[Discord]  ─┤          ┌─────────────────┐         ┌──────────────┐
[WhatsApp] ─┼──────────▶  Gateway (18789) ├─────────▶  Agent Turn  │
[HTTP/WS]  ─┤          │  (command queue) │         │  (LLM + tools) │
[Cron]     ─┘          └─────────────────┘         └──────────────┘
```

### The Command Queue

All inbound events (messages, heartbeats, exec completions, cron fires) are routed through a **single serialized command queue**. This is a crucial architectural choice — it means concurrent external events don't race each other. From the bug reports:

- Heartbeats route through a "separate command queue lane" so they never block real-time messages
- Each inbound channel adapter normalizes to the same internal event format before enqueuing
- The queue serializes agent turns: one turn runs at a time per session key

### Session Keys

Every conversation is namespaced by a session key: `agent:<agentId>:<channelKey>`. For example:
- `agent:main:main` — the primary session
- `agent:main:discord:channel:1234` — a Discord channel session
- `cron:morning-briefing` — a cron-isolated session

Session keys are how OpenClaw keeps scheduled tasks from polluting interactive history, and how multi-channel state stays coherent (different channels share memory through the same agent state, but each has its own session key for queue and history purposes).

### Health/Liveness

As of recent versions, the gateway exposes `/health`, `/healthz`, `/ready`, `/readyz` HTTP endpoints — designed for Docker/Kubernetes probes. This confirms it's built to run as a persistent service, not a one-shot process.

### Tier 2 Relevance

The gateway as a whole is too heavy to adopt just for the watcher runtime. But its core pattern — **a Node.js process with a command queue that normalizes diverse triggers into a unified agent-turn interface** — is directly applicable and extractable. The "gateway without channels" is essentially just a scheduler loop calling `run_agent_turn`.

---

## 2. Cron/Heartbeat System — `src/cron/` and `src/infra/`

This is the most directly relevant system for Tier 2.

### File Anatomy

From bug reports and issues, the key files are:
- `src/cron/service.ts` — job registry and lifecycle management
- `src/cron/service/timer.ts` — the timing engine (`armTimer`, `runDueJobs`, `onTimer`)
- `src/cron/isolated-agent/run.ts` — isolated execution path (separate session key per job)
- `src/infra/heartbeat-runner.ts` — the main heartbeat execution function (`runHeartbeatOnce`)
- `src/infra/heartbeat-wake.ts` — the wake signal layer (`requestHeartbeatNow`)
- `src/infra/system-events.ts` — per-session event queue (`Map<string, SessionQueue>`)
- `src/gateway/server-cron.ts` — gateway integration point

### How It Works

#### The Timer Layer (`timer.ts`)

```
armTimer(nextWakeAtMs)
  └─ setTimeout → onTimer()
       ├─ runDueJobs()  (find all jobs where nextRunAtMs <= now)
       └─ for each due job:
            ├─ wakeMode: "now"  → requestHeartbeatNow({ reason: "cron:<jobId>" })
            └─ wakeMode: "next-heartbeat" → just mark due, let next scheduled heartbeat pick it up
```

`armTimer` uses `setTimeout` — a single timer always points to the next due job's timestamp. When it fires, it reschedules immediately for the next job. This is a minimal cron implementation: no separate cron process, just a chain of `setTimeout` calls anchored to wall clock time.

#### The Heartbeat Runner (`heartbeat-runner.ts`)

`runHeartbeatOnce({ reason })` is the actual agent invocation:

1. **Read HEARTBEAT.md** from the workspace — this is the agent's periodic instruction document
2. **Check for pending system events** (`peekSystemEvents(sessionKey)`) — cron payloads, exec completions
3. **Decide whether to act:** if HEARTBEAT.md is effectively empty AND no pending events → skip (return `{ status: "skipped", reason: "empty-heartbeat-file" }`)
4. **Build the agent turn:** compose system prompt + pending events + HEARTBEAT.md instructions
5. **Call the model** via the normal agent turn machinery
6. **Advance schedule:** calculate `nextDueMs` and re-arm the timer

Key config: `agents.*.heartbeat` block in `openclaw.json`:
```json
{
  "agents": {
    "heartbeat": {
      "every": "30m",        // interval (supports cron expressions too)
      "activeHours": "8-22", // optional window
      "lightContext": false   // opt-in lightweight bootstrap (recent feature)
    }
  }
}
```

#### The Wake Layer (`heartbeat-wake.ts`)

A lightweight signal mechanism for triggering out-of-schedule heartbeats:

```typescript
export function requestHeartbeatNow(opts?: { reason?: string; coalesceMs?: number }) {
  pendingReason = opts?.reason ?? pendingReason ?? "requested";
  schedule(opts?.coalesceMs ?? DEFAULT_COALESCE_MS); // DEFAULT = 250ms
}

function schedule(coalesceMs: number) {
  if (timer) { return; } // coalescing: only one pending wake allowed
  timer = setTimeout(() => {
    timer = null;
    runHeartbeatOnce({ reason: pendingReason });
  }, coalesceMs);
}
```

This is module-level state — a single pending timer. The coalescing means rapid-fire events (e.g., 10 exec completions in a row) result in only one heartbeat wake. There's a documented bug where the `if (timer) { return; }` check causes delayed execution when a regular heartbeat timer is already armed — the 250ms coalesce becomes the full heartbeat interval.

#### Job Execution Modes

1. **Main session heartbeat** — job fires → `requestHeartbeatNow` → regular heartbeat runner uses main session key → standard HEARTBEAT.md-driven turn
2. **Isolated agent run** (`sessionTarget: "isolated"`) — job fires → `src/cron/isolated-agent/run.ts` → fresh session key (`cron:<jobId>`) → dedicated agent turn → optional delivery to channel

The isolated path is what makes cron safe for background automation: it doesn't pollute your main session history.

#### HEARTBEAT.md — The Primitive

HEARTBEAT.md is a flat markdown file in the workspace. The agent reads it on every heartbeat and decides what (if anything) to do. From the "You Could've Invented OpenClaw" tutorial:

> Each heartbeat uses its own session key (`cron:morning-briefing`). This keeps scheduled tasks from cluttering your main conversation history. The heartbeat calls the same `run_agent_turn` function — it's just another message, triggered by a timer instead of a human.

This is architecturally identical to what Tier 2 needs: a file that tells a background agent what to check and what to do. HEARTBEAT.md is just SOUL.md for a scheduled agent.

### Tier 2 Relevance: **HIGH**

The cron/heartbeat system IS the Tier 2 runtime, nearly verbatim:
- Timer fires → runner reads instruction file → checks for pending events → calls model → acts
- Isolated sessions keep background work clean
- The `every: "30m"` or cron expression config matches "poll for new transcripts periodically"
- HEARTBEAT.md is exactly the ML OS grounding prompt for the vault watcher task

**The gap:** HEARTBEAT.md is a static file. It doesn't natively read from your vault's `index.json` or detect new transcripts. You'd need to either (a) write a HEARTBEAT.md that instructs the agent to check those files itself, or (b) use a systemEvent to push "new transcript detected" into the queue.

---

## 3. ACP Protocol — `src/acp/`

### What ACP Actually Is

ACP (Agent Client Protocol) is a **JSON-RPC 2.0 standard** created by Zed Industries for editor-to-agent communication. It lets a client (Zed, JetBrains, or in this case OpenClaw) talk to an agent (Claude Code, Codex, Gemini CLI) over **stdio** (agent runs as subprocess) or HTTP.

OpenClaw's ACP integration works through the `acpx` CLI (`github.com/openclaw/acpx`), which wraps the raw ACP protocol with:
- Named persistent sessions (`acpx codex sessions new --name api`)
- Prompt queueing (submit while one is running, they execute in order)
- Fire-and-forget (`--no-wait`)
- Cooperative cancel (sends `session/cancel` via IPC without killing session state)

### How OpenClaw Dispatches Claude Code

From the ACP docs and config schema:

```json
{
  "agents": {
    "list": [{
      "id": "claude",
      "runtime": {
        "type": "acp",
        "acp": {
          "agent": "claude",
          "backend": "acpx",
          "mode": "persistent"
        }
      }
    }]
  }
}
```

And the ACP backend config:
```json
{
  "acp": {
    "backend": "acpx",
    "defaultAgent": "codex",
    "allowedAgents": ["pi", "claude", "codex", "opencode", "gemini", "kimi"],
    "maxConcurrentSessions": 8
  }
}
```

When OpenClaw's main agent decides to delegate a coding task, it:
1. Calls the `acp` tool with `{ "task": "...", "runtime": "acp", "agentId": "claude", "mode": "session" }`
2. OpenClaw's ACP layer spawns or reconnects to an `acpx` session for that agent
3. The task is queued to the ACP backend (Claude Code running with `--acp` flag)
4. Output streams back through the gateway and is delivered to the configured channel

### The acpx Layer

```
OpenClaw ──(tool call)──▶ ACP dispatcher ──(spawns)──▶ acpx process
                                                              │
                                               ┌─────────────┘
                                               │  acpx manages:
                                               │  - session IPC (Unix socket)
                                               │  - prompt queue
                                               │  - Claude Code subprocess (stdio ACP)
                                               │  - output streaming back to gateway
                                               └─────────────────────────────────────
```

The key insight from the Twitter thread about acpx's creation: before acpx, OpenClaw had to **scrape PTY sessions** to drive Claude Code — watching terminal output character by character. ACP provides a structured JSON-RPC protocol instead.

### Tier 2 Relevance: **LOW-MEDIUM**

For Tier 2, you don't need ACP. ACP is for **orchestrating external coding agents from within a running session**. The Tier 2 problem is different: you want a background process to call Claude Code headless (`claude -p`) with a vault-processing prompt.

Where ACP becomes interesting is if you want the vault watcher itself to be able to **dispatch coding subtasks** — e.g., "I noticed a major architectural decision in this transcript, spawn a Claude Code session to update the relevant files." But that's Tier 3 complexity, not the initial Tier 2 need.

**What IS extractable:** The acpx pattern (named persistent sessions, prompt queuing, cooperative cancel) could be used independently of OpenClaw to build a Tier 2 runtime that manages long-running Claude Code sessions. `acpx` is a standalone npm package.

---

## 4. Context Engine — `src/context-engine/`

### What It Does

OpenClaw's context engine is responsible for building the system prompt that gets sent to the model on each turn. From the docs and issues, it assembles:

1. **SOUL.md** — agent identity and behavioral rules (analogous to ML OS kernel + schema)
2. **Loaded skills** — each eligible skill's SKILL.md content is injected
3. **Tool schemas** — structured function definitions for all enabled tools
4. **Agent-level overrides** — per-agent config that modifies the base context
5. **Pending system events** — from `peekSystemEvents(sessionKey)`
6. **Bootstrap context** — workspace state, available tools summary

The recent "Cron/Heartbeat light bootstrap context" feature (`--light-context` flag) is telling: full bootstrap is expensive (reads workspace, indexes tools, loads all skills). The light mode skips this for automation runs where you just want the model to execute a specific task without the full environmental context.

### The `before_prompt_build` Hook

From the Mnemon memory system discussion, there's a plugin hook called `before_prompt_build` that fires before each API call and can inject content into the prompt. This is how memory plugins work: at turn start, retrieve relevant memories → inject into system prompt extension. The hook receives the current context and can append to it.

This hook is architecturally equivalent to what ML OS context packs do at session initialization — but in OpenClaw, it fires on every turn, not just at startup.

### Session Compaction

Long sessions hit context limits. OpenClaw handles this via compaction: the session history is summarized and the full `.jsonl` is replaced with a compressed version. From issues, compaction can cause the main session to become temporarily unreachable during the compaction run, and the heartbeat scheduler can die if it fires during a compaction cycle.

### Tier 2 Relevance: **MEDIUM**

The context engine's most relevant feature for Tier 2 is the **`before_prompt_build` hook** — it's the native mechanism for injecting dynamic context (like "here's what changed in the vault since the last heartbeat") into every agent turn. If you run OpenClaw as your Tier 2 runtime, this hook is where you'd inject vault delta information.

The `--light-context` / `lightContext` flag is also directly relevant: for cron-driven vault processing tasks, you want minimal bootstrap overhead. You're not doing interactive work, you're running a focused extraction task.

---

## 5. Skill System — `skills/` + `src/plugins/`

### Skill Structure

Each skill is a directory with a `SKILL.md` file containing YAML frontmatter + instructions:

```
my-skill/
  SKILL.md        # Required: frontmatter metadata + agent instructions
  references/     # Optional: docs, guides loaded on demand
  assets/         # Optional: binary files
  scripts/        # Optional: executable helpers
```

SKILL.md frontmatter:
```yaml
---
name: my-skill
description: Brief description (min 20 chars)
metadata: {
  "openclaw": {
    "requires": {
      "bins": ["required-binary"],
      "env": ["REQUIRED_API_KEY"],
      "config": ["some.config.flag"]
    },
    "primaryEnv": "REQUIRED_API_KEY"
  }
}
---
# Skill Content
Instructions for the agent when this skill is loaded...
```

### Loading and Precedence

Skills are loaded at gateway startup (not per-turn) and filtered by environment:
1. **Workspace skills** (`<workspace>/skills/`) — highest precedence, agent-specific
2. **Managed/local skills** (`~/.openclaw/skills/`) — shared across agents
3. **Plugin skills** — bundled with plugins
4. **Extra dirs** (`skills.load.extraDirs` in config) — lowest precedence
5. **Bundled skills** — shipped with OpenClaw

A skill is **eligible** only if all its `requires` conditions are met (binaries installed, env vars set, config flags enabled). This is how OpenClaw avoids injecting useless tool instructions for tools the agent can't actually use.

### How Skills Inject Into Context

Skills contribute to the system prompt in two ways:
1. **Human-readable guidance** — the SKILL.md content goes into the system prompt as instructions
2. **Tool schemas** — if the skill's backing tool is loaded, its JSON schema is sent to the model API

From the docs: "If a tool doesn't appear in the system prompt or the schema, the model cannot call it." Skills are the mechanism for making tools real to the model.

### Plugins vs Skills

**Skills** = prompt injection only. They teach the agent what to do.  
**Plugins** = code-level extensions. They register new tools, CLI commands, channel adapters, and hooks.

A plugin can ship a skill alongside its tool implementation. The skill teaches the agent how to use the tool; the plugin provides the actual execution.

### The `agent:bootstrap` Hook

Plugins can register an `agent:bootstrap` hook that fires at session start and injects content into the system prompt. This is distinct from skills (which are static file loads) — bootstrap hooks can run code and inject dynamic content.

From the Mnemon example:
```
Session starts → agent:bootstrap hook fires → loads ~/.mnemon/prompt/guide.md 
                                             + current memory status
                                             → injects into system prompt
```

This is the hook mechanism for custom context injection at session start.

### Tier 2 Relevance: **HIGH** (for a different reason)

Skills are not directly relevant to building the Tier 2 runtime. But they're highly relevant to **the Tier 2 task specification itself** — this is what Decision D-008 identified.

A well-engineered vault skill could:
1. Teach the agent the `ingest.py` and `moc.py` CLI interfaces
2. Document the vault's zone semantics (vault/bench/inbox)
3. Define the trigger patterns ("if you see X in a transcript, update Y")
4. Be loaded into any OpenClaw session, making vault operations available everywhere

The skill is literally the delivery mechanism for an ML OS grounding prompt. A vault skill IS the Tier 2 task specification, packaged for reuse.

---

## 6. The Tier 2 Fit Assessment

Framing: *Which specific mechanisms could serve as the persistent watcher runtime for the vault architecture?*

### Mechanism 1: OpenClaw's Cron + Heartbeat (Native)

**How it maps:**
- `heartbeat.every: "5m"` → polls for new transcripts every 5 minutes
- HEARTBEAT.md → contains the ML OS grounding prompt + vault watcher instructions
- Isolated session per heartbeat → each watcher run is clean, doesn't pollute main conversation
- `requestHeartbeatNow` + system events → file watcher could push "new transcript" event to trigger immediate watcher run

**What you get:** The full OpenClaw stack running as a daemon, with cron/heartbeat already wired together. You write HEARTBEAT.md and configure the interval.

**What you pay:** Node.js daemon, full OpenClaw install, API key requirement (no Max subscription), ~500K lines of code you don't control, two documented Jan 2026 security incidents.

**Verdict:** Overkill for Tier 2, but the pattern is exactly right. The implementation would be trivial once running.

### Mechanism 2: Extract the Cron Pattern (DIY)

The core cron/heartbeat logic is ~200 lines of TypeScript. The extractable pattern:

```python
# Python equivalent of OpenClaw's heartbeat loop
import time, subprocess
from pathlib import Path

def arm_timer(interval_secs):
    while True:
        time.sleep(interval_secs)
        run_watcher_turn()

def run_watcher_turn():
    new_transcripts = scan_for_new_transcripts()
    if not new_transcripts:
        return  # OpenClaw's "empty-heartbeat-file" optimization
    
    # Build ML OS grounding prompt + task
    prompt = build_grounding_prompt(new_transcripts)
    
    # Call claude -p (D-007) or direct API
    subprocess.run(["claude", "-p", prompt])
```

This is OpenClaw's heartbeat loop, minus all the channel adapter complexity. The session isolation (fresh session per run) is free when using `claude -p`.

**Verdict:** This is the correct approach for Tier 2. It's the minimum viable extraction of the OpenClaw pattern without adopting OpenClaw itself.

### Mechanism 3: ACP as Dispatch Protocol

If the vault watcher itself ever needs to delegate focused coding tasks (e.g., "refactor this file based on what I learned from the transcript"), `acpx` is the dispatch protocol:

```bash
acpx claude sessions ensure --name vault-processor
acpx claude "Process this transcript and update decisions.md: $(cat transcript.md)"
```

**Verdict:** Not needed for initial Tier 2. Worth knowing for future agent-to-agent delegation.

### Mechanism 4: OpenClaw Skill as ML OS Packaging

The cleanest use of OpenClaw's skill system without adopting OpenClaw: build a vault skill for deployment into whatever runtime you choose. The skill format (YAML frontmatter + markdown instructions + optional scripts) is compatible with any skill-loading runtime, not just OpenClaw.

```
vault-processor/
  SKILL.md          # ML OS grounding prompt for vault operations
  references/
    vault-schema.md # Zone semantics, index format
    tier2-tasks.md  # What to extract from transcripts
  scripts/
    ingest.py       # Already built
    moc.py          # Already built
```

**Verdict:** This is D-008's "Custom skills as ML OS delivery mechanism" in concrete form. Build this regardless of which runtime you choose.

---

## 7. Synthesis: What OpenClaw Teaches About the Tier 2 Runtime

The key architectural lessons, extracted and reapplied:

| OpenClaw Mechanism | Vault Architecture Equivalent |
|--------------------|-------------------------------|
| HEARTBEAT.md | ML OS grounding prompt for vault watcher |
| Heartbeat `every: "30m"` | `cron` or `watchdog` polling interval |
| Isolated session per heartbeat | `claude -p` (always fresh, no session pollution) |
| `requestHeartbeatNow` + system events | `watchdog` file event → trigger immediate watcher |
| `lightContext` flag | Skip workspace scan, just run the task |
| Skill SKILL.md injection | Vault skill loaded into every session via `skills.load.extraDirs` |
| `before_prompt_build` hook | `watchdog` event callback that prepends delta to prompt |
| SOUL.md | ML OS kernel.yaml + schema.yaml |
| `empty-heartbeat-file` optimization | `if not new_transcripts: return` |

**The core insight:** OpenClaw solved exactly the Tier 2 problem for a different use case (personal assistant, not vault). Its solution is: a persistent process, a polling interval, an instruction file, and isolated execution per run. The mechanism is simple. The complexity in OpenClaw comes from the channel adapters (Telegram, Discord, etc.) that you don't need.

**The recommended path remains D-007:** Start with `claude -p` triggered by cron/watchdog. This is OpenClaw's heartbeat loop, distilled to its minimum viable form. The ML OS grounding prompt IS the HEARTBEAT.md. The session isolation IS the `-p` flag. The only thing missing is the daemon wrapper — which is `systemd` or `launchd` or `python-watchdog`.

---

## 8. Open Questions After This Research

1. **Does `acpx` work without a running OpenClaw gateway?** If yes, it's a clean way to manage Claude Code sessions from a Python watcher daemon without adopting the full stack.

2. **Can the `lightContext` optimization be replicated with `claude -p`?** The flag skips workspace indexing. Does `claude -p` with a minimal `CLAUDE.md` achieve the same thing?

3. **What's the actual token cost of a HEARTBEAT.md-driven turn vs. a `claude -p` turn?** Both call the same API, but OpenClaw may inject more context (skills, tool schemas) that adds tokens. The lightContext flag was added specifically to address this for cron runs.

4. **Is there a minimal OpenClaw config that's just "cron + heartbeat, no channels"?** If the gateway can run with zero channel adapters and just the cron scheduler active, it might be worth running as a dedicated Tier 2 service separate from any interactive use.

---

## Associated Files

- `pickup.md` — Project pickup document (read first)  
- `vault_session_summary.md` — Full 881-turn session summary (context on the vault system)

---

**Prepared:** 2026-03-06  
**Research method:** GitHub issue mining, bug report analysis, official docs, "You Could've Invented OpenClaw" tutorial  
**Confidence:** High on cron/heartbeat/skill internals, medium on ACP internals (less source available), low on context-engine internals (most opaque layer)
