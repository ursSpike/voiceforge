# MASTER PLAN — Jun 13, now → 7 PM presentation. The one timeline.

Built so we never re-plan. Each phase: who does what, the gate to clear it, and the fallback. Coordinator
(Claude) governed by `docs/SPRINT_CONTROL.md`. Frozen artifacts sealed all day. Live calls = separate
uncalibrated lane. 3–4 confirmed pushes, none 13:45–14:45.

## PHASE 0 — PRE-DEPARTURE (07:20 → ~09:30) — agents work while Spike preps
| # | Work | Owner | Gate | Status |
|---|---|---|---|---|
| 0.1 | `docs/demo_docs.md` (8-slide script + coaching + Q&A) | script agent | reads aloud ≤6:30 | 🟡 running |
| 0.2 | `PROJECT_BIBLE.md` (whole project understood) | bible agent | Spike skims on commute | 🟡 running |
| 0.3 | `pipeline/ingest_live.py` + live-judge + offline selftest | live-bridge agent | selftest green, frozen unchanged | 🟡 running |
| 0.4 | `/` (real-data presentation) + `/platform` (operator + LIVE TODAY) | routes agent | both load offline, 76 calls | 🟡 running |
| 0.5 | Verify each lane as it lands; QA the two code lanes; 1–2 honest commits | coordinator | frozen hashes identical | ⏳ |
| 0.6 | Spike reads demo_docs.md aloud ONCE; trim overruns | Spike + me | fits the clock | ⏳ |
**Gate to leave:** demo_docs readable, /+/platform serve, live-bridge selftest green, repo committed.
**Fallback if a lane slips:** `out/dashboard.html` is the always-working demo; a slipped `/` just means
we present the dashboard. Nothing here is load-bearing alone.

## PHASE 1 — TRAVEL (~09:30 → 10:30)
Spike reads PROJECT_BIBLE.md + demo_docs.md on the way. No building. (If I'm reachable, `explain <topic>`
on anything shaky.)

## PHASE 2 — BUILD SPRINT 1 (10:30 → 13:45) — live evals → submission
Drive from `docs/SPRINT1_RUNBOOK.md`. Spike makes calls; pipeline ingests/judges; /platform fills.
- 10:30 Buddy kickoff (framing + Q1/Q2/Q4). 10:45 first call.
- Calls 1–4 core (clean / Hinglish / repair / changed-slot), call 5 barge-in ONLY if Buddy confirms
  telemetry. Each: download → paste exec id → I ingest+judge → glance /platform.
- Pushes at arrival / first-ingested / judged / 13:35-final(+tag). Submission text pasted 13:45.
**Gate:** repo clean + `/`+`/platform` live + ≥3 live calls in LIVE-TODAY + submission in.
**Fallback:** zero live calls still submits a complete, audited 46-call product.

## PHASE 3 — JUDGING FREEZE (13:45 → 14:45)
NO pushes (judges may clone). Eat. Run the `spar` agent (10 hard judge questions, rehearse answers).
Optionally `explain` anything Q&A-shaky.

## PHASE 4 — BUILD SPRINT 2 (15:00 → 16:30, IF Top 10)
1. **Before/after**: worst live failure from Sprint 1 → apply one improvement-queue recommendation to the
   Bolna agent prompt → re-run THAT scenario → show both calls side-by-side on the surface. Framed:
   "one scenario, the loop demonstrated — not a measured lift claim."
2. `capture` agent: screenshots + fallback screen-recording of `/` and `/platform`.
3. Rehearse full run ×2 from a clean server, Wi-Fi OFF. Trim overruns.
4. Demo-blocking bugs only. No refactors after 16:00. Final push + `demo-jun13` tag.
**Gate:** rehearsed ≤6:30, fallback recording exists, surface runs offline.
**Fallback:** if not Top 10, day ends at submission — still a strong public artifact.

## PHASE 5 — PRESENTATIONS (16:40 → 18:30) — 10 teams, ~10–12 min each incl. Q&A
Spike's slot: **`/` for the story** (8 slides, keypress, ~6:15) → at the Bolna×Cartesia slide, **switch to
`/platform`** and show a real live call's phenotype + improvement recommendation → close → Q&A from
demo_docs kill-list. If Wi-Fi dies mid-demo, pivot to the fallback recording without breaking stride.
**The money sequence (if a live call lands):** open `/`, explain the system, then on `/platform` show a
call YOU made today, its failure phenotype, and the fix it recommends — product taste + sponsor
integration + eval engineering + a real workflow, in one move.

---

## OPERATING MODEL (how Spike and the coordinator work together)
- **One file is enough:** `docs/SPRINT_CONTROL.md`. Attach/point me (or the audit master) at it; whatever
  you paste in INBOX, I classify NOW/NEXT/IGNORE, update lanes, hand back your single next action + a time
  check. The plan docs (this file, runbook, roster, batches) are the stable backdrop; SPRINT_CONTROL is
  the living surface.
- **Separate sprint convo:** yes — keep a fresh lightweight conversation just for the loop. Bootstrap it
  ONCE with the prompt in `docs/SPRINT_CONTROL.md` → "BOOTSTRAP PROMPT" (added there). Then each message
  is just an INBOX item; I reply with the re-ranked plan.
- **Interaction cadence:** event-driven, not clock-driven. Ping me whenever (a) a call finishes,
  (b) the Buddy says something, (c) anything breaks, (d) you have an idea or a doubt. That naturally lands
  ~every 15–20 min (call rhythm). Between pings you're heads-down on calls.
- **The 15-min pacer:** I run a "pace check" on every ping — elapsed vs this timeline, am I on track, what
  to cut to stay on time. If you want a hands-off heartbeat too, say "set the heartbeat" in the sprint
  convo and I'll arrange a ~20-min recurring nudge during sprint hours (off by default so it can't fire
  mid-presentation). Default = your pings ARE the cadence; it's more reliable for a hands-busy solo.
- **What I never do:** push without your "push", touch frozen artifacts, run `git add -A`, claim a number
  not in a committed artifact.
