# AGENT ROSTER — the fleet, who does what, when, and how to summon them

One page Spike can scan. Every agent: PURPOSE · TRIGGER (when it runs) · INPUTS → OUTPUTS · PRIORITY ·
GUARDRAILS. Coordinator = Claude main loop (me), governed by `docs/SPRINT_CONTROL.md`. NOTHING pushes
or modifies frozen artifacts; every consequential output is verified by the coordinator (and the QA
agent for code) before integration.

**Frozen forever (every agent inherits this):** `eval/label_manifest.json` · `eval/labels_spike.csv` ·
`eval/label_snapshot.json` · `out/judge_results.json` · `out/calls.json` · calibration numbers · `rubric.yaml`.

---

## P0 — PRE-DEPARTURE FLEET (fire NOW, parallel, ~07:20–09:20)

### 1. Script Agent (`demo_docs`)
- **PURPOSE:** `docs/demo_docs.md` — THE one file Spike reads. Word-for-word script in short speakable
  phrases for a **10-min slot = 6:15–6:30 talk + Q&A defense**; 8 slides (thesis/intro · metric trap
  25/45 · deterministic-first · hero call · blind labels+calibration · phenotypes+queue ·
  Bolna×Cartesia+LIVE-today slot · value/limits/close); intro ("Saivarshith — Spike — CSE IIT-KGP '25,
  SDE Fujitsu Research, solo"); [PAUSE]/[SLOW]/[PUNCH] coaching marks (silence replaces filler);
  WHAT-THIS-MEANS plain-language boxes under every beat; Q&A kill-list incl. "how does the eval layer
  not hallucinate" + "how does it scale".
- **TRIGGER:** background, once, now. **OUT:** docs/demo_docs.md. **PRIORITY: P0-highest.**

### 2. Bible Agent (`project_bible`)
- **PURPOSE:** `PROJECT_BIBLE.md` — the whole project *understood* (vs performed): end-to-end data flow
  with every file named, each metric in 2 lines + caveat, every limitation and why it's a strength,
  audit-trail story, glossary (FTO, prevalence paradox, bootstrap CI…). Spike reads on the commute.
- **TRIGGER:** background, once, now. **OUT:** PROJECT_BIBLE.md. **PRIORITY: P0.**

### 3. Live-Bridge Agent (`live_ingest`)
- **PURPOSE:** the Sprint-1 engineering prerequisite. Generalize the hardcoded ingest:
  `pipeline/ingest_live.py --execution <id> | --latest` → cache `data/provider_logs/bolna_live_<id>.json`
  → normalize `data/normalized/bolna_live_<id>.json` → deterministic `build_record()` →
  **separate live judge** (reuses judge machinery, writes `out/live_judge_results.json`, provenance
  `LIVE · UNCALIBRATED`) → merge view `out/live_calls.json`. Offline selftest replays the cached
  246cd9f3 payload through the new path. NO network call until on-site.
- **TRIGGER:** background, once, now (code + selftest; coordinator + QA verify). **PRIORITY: P0.**
- **GUARD:** never writes into frozen artifacts or the calibration path; live calls are corpus-only.

### 4. Surface Agent (`routes`)
- **PURPOSE:** the two-route architecture. `serve_demo.py` (or extend serve.py): **`/` = presentation**
  (repaired design bundle as visual base, fed FULL real data — a generator emits `design_data.js` from
  out/* artifacts, replacing the 5-row fixture; keys ←/→/Home/Esc) · **`/platform` = operator mode**
  (the existing audited `dashboard.html` + a LIVE-TODAY section reading out/live_calls.json + one-click
  "refresh after ingest"). Both self-contained offline; `out/dashboard.html` remains the fallback.
- **TRIGGER:** background, once, now; coordinator browser-verifies (1280×720/1440×900/1920×1080).
- **PRIORITY: P0.** (Claude-design refinement happens LATER against this real DOM — never another fixture.)

## P1 — ON-SITE FLEET (sprint control)

### 5. Coordinator (me — not a subagent)
- Reads `docs/SPRINT_CONTROL.md` INBOX every turn; classifies NOW/NEXT/IGNORE; spawns lanes; verifies
  every output (DOM-coverage audit for any fetched design, tests for any code); never auto-pushes.

### 6. QA/Audit Agent (`qa`)
- **PURPOSE:** independent adversarial check of any consequential artifact before integration —
  stand-in for GPT/Codex when they're not around (per Spike electing me audit master: I rule, this
  agent gives me an independent second pair of eyes).
- **TRIGGER:** on-demand after each P0/P1 lane completes. **OUT:** verdict in lane dir.

### 7. Explainer-on-Demand (`explain <topic>`) — Spike's "doubt resolver"
- **PURPOSE:** Spike names ANY topic he's shaky on ("explain κ vs balanced accuracy", "how does the
  booth enforce blindness", "what exactly happens in ingest") → agent maps EVERYTHING about that one
  thing into `docs/explainers/<topic>.md`: what it is in plain words → where it lives in the repo
  (files/lines) → the numbers it produces → the honest caveat → 3 likely judge questions + answers.
- **TRIGGER:** on-demand, any time (works during sprint waiting periods). **PRIORITY: P1, unlimited uses.**
- **HOW TO SUMMON:** Spike just types: `explain <thing>` — coordinator fires it with the standard prompt.

### 8. Buddy-Notes Integrator (`buddy`)
- **PURPOSE:** Spike pastes whatever the Bolna Buddy said into SPRINT_CONTROL INBOX; agent extracts
  facts (e.g., interruption telemetry exists? webhook payloads?), updates the live-bridge plan, drafts
  the follow-up question.
- **TRIGGER:** on-demand when notes arrive.

## P2 — SUPPORT FLEET (as time allows)

### 9. Submission-Copy Agent (`submission`)
- 5-line submission description + form answers + **README truth-pass** (kill the false DPO/queue.jsonl
  diagram, current honest numbers). Prepared text tonight/morning; pasted at 13:45.

### 10. Hygiene + Secret-Scan (`ship-check`)
- Pre-push check only (NO auto `git add -A`): secret scan, frozen-hash check, `audit.md` restored
  (currently tracked-but-deleted — restore), staged-file review. Spike confirms every push (3–4 total).

### 11. Q&A Sparring Agent (`spar`)
- Generates 10 hard judge questions in role (Bolna founder / Cartesia ML eng / product judge), Spike
  answers out loud, agent grades against the artifacts and tightens his phrasing. Use while waiting.

### 12. Capture Checklist (`capture`)
- Drives the screenshot/fallback-recording checklist (needs Spike's hands for audio/QuickTime).
  Sprint-2 priority, or any idle window.

---

## Timebox (today, brutal version)
- **07:20–09:20** P0 fleet runs parallel; coordinator verifies as each lands; 1–2 commits.
- **09:20–09:45** Spike reads demo_docs once aloud; pack; leave.
- **10:30–13:45** Sprint 1 per `docs/plans/batch2_sprint_day_goldmine.md` + SPRINT_CONTROL loop:
  live calls (clean / Hinglish / repair-loop / changed-slot; barge-in ONLY if Buddy confirms telemetry)
  → live-bridge → /platform LIVE-TODAY → 3–4 confirmed pushes → 13:40 tag → submit 13:45.
- **13:45–14:45** freeze (judges clone). Eat. Spar agent.
- **15:00–16:30** Sprint 2: before/after scenario, capture, rehearse ×2.
- **16:40–18:30** presentations: `/` for the story, `/platform` for the live proof.
