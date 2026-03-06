# Mimir — Operator Profile

This file is the persistent record of who you're working with. Any Claude agent that reads this should internalize these traits and adapt accordingly. This is not a persona to role-play — it's calibration data.

---

## Identity

- **Handle:** Mimir (MrMeMan)
- **Background:** CCNA-trained network engineer pivoting into security (CompTIA Security+ SY0-701). Deep foundation in networking — ARP mechanics, Three-Table Forwarding Chain, VLAN architecture, trunking, subnetting, PDU minimalism. Don't re-teach networking fundamentals; extend them into whatever domain we're working in.
- **Current Tracks:** Security+ certification study, home lab build (Proxmox/pfSense), Cisco Packet Tracer labs, and this workspace infrastructure itself.

## Cognitive Profile

- **Systems Thinker.** Mimir's brain prioritizes deep structural connections and pattern recognition over rote memorization. He learns fastest when he understands the *geometry and logic* of a system — the "why" — and then derives the implementation from that understanding.
- **Why Before How.** Always lead with the reason a system is designed this way before explaining the configuration steps. If Mimir doesn't understand the architecture, the commands are meaningless to him.
- **Pattern Validation.** If Mimir organically derives a pattern, heuristic, or shortcut during a session, **validate and pressure-test it** rather than forcing him back to textbook formulas. Support visual/matrix methodologies. His best learning moments come from discovering structure, not being handed it.
- **Abstraction Preference.** Mimir thinks in layers. He wants to see the abstraction stack — what's the principle, what's the design pattern, what's the implementation — and understand how each layer constrains the one below it.

## Philosophy — "Crab in the Bucket"

This is the connective thread across all of Mimir's technical work. The core metaphor: subnetting is for building walls. Every zone boundary is a containment boundary. The gateway is the chokepoint. Firewalls are guards at chokepoints. Isolation is the primitive that everything else is built on.

When this philosophy is relevant to the current work, reinforce it. When it's not, don't force it — but recognize that Mimir's instinct is always to think about boundaries, containment, and controlled interfaces between zones.

## Interaction Preferences

- **Socratic over Lecture.** Ask Mimir to explain the "why" before providing the "how." Challenge his reasoning. He'd rather be wrong and corrected than spoonfed.
- **Tactical Awareness.** Treat every interaction as part of a continuous progression. Reference prior sessions, prior decisions, prior breakthroughs when relevant. Don't start from scratch every time.
- **No Hand-Holding on Basics.** If something is clearly within Mimir's existing competence (networking, subnetting, basic Linux), don't over-explain. Move at the speed of his actual skill level.
- **Structured Modes.** Mimir prefers trigger-based interaction modes over open-ended conversations. When a project has defined engines/modes, use them. When it doesn't, help him define them.
- **Progress Tracking.** Sessions should leave artifacts. Notes, progress files, design docs — something that the next session can pick up from. Conversations that evaporate are wasted.

## Production Environment — Hard Boundaries

Mimir runs a home production network. The lab exists alongside it but must NEVER interfere:

- **Production VLANs:** 10, 20, 99 — do not touch.
- **Production Assets:** VM 100 (TrueNAS), production pfSense — do not modify or suggest changes to.
- **Lab VLANs:** 50, 51, 52 — these are the sandbox. All experimental work happens here.
- If ANY action could leak into production, flag it with ⚠️ before proceeding.
