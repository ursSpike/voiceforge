# SPRINT 1 RUNBOOK — exactly what SPIKE does, 10:30–13:45 (the careful version)

**The golden rule:** YOU make calls and paste execution IDs. The PIPELINE (me + agents) does ingest,
judge, and surface. You never hand-edit a data file. The frozen calibration experiment is sealed — live
calls live in a SEPARATE lane (`bolna_live_*`, `out/live_calls.json`) and are always shown
`LIVE · UNCALIBRATED`. If you ever feel unsure, STOP and paste into SPRINT_CONTROL INBOX — don't touch
files.

## What "don't meddle with the pipeline" means concretely
- ✅ You DO: dial the Bolna agent, run the scripted scenarios, download each call's logs/recording,
  paste the execution ID into the sprint convo.
- ❌ You DON'T: open/edit anything in `eval/`, `out/`, `data/normalized/`, `pipeline/`. No manual JSON
  edits, ever. No `git add -A`. No re-running calibration.
- The bridge (`pipeline/ingest_live.py` + live judge) is built so a live call can NEVER write into a
  frozen file — but the human rule above is the real safety.

## The call set (do in THIS order — stop wherever the clock says)
Each call ≈ 2 min. After EACH call: download logs + recording immediately (signed URLs expire), then
paste the execution ID. Don't batch the downloads — do it per call.

1. **Clean booking** (happy path) — establishes the baseline "this is what success looks like."
2. **Hinglish / code-switching** — switch between English and Hindi mid-call. (Feeds the multilingual story.)
3. **Ambiguous request with repair** — start vague, make the agent ask clarifying questions.
4. **Changed slot midway** — book one thing, then change your mind mid-call. (Repair-loop phenotype.)
5. **Interruption / barge-in** — ONLY run this if the Bolna Buddy confirms Bolna exposes an interruption
   token/timestamp in telemetry (Buddy Question #1). If not confirmed, SKIP — we will not claim barge-in
   detection we can't back with data. Latency we can always reconstruct; overlap we cannot fake.
6. *(optional, only if time + credits)* background noise, or a prompt-injection attempt.

**Target: 4 solid calls beats 6 rushed ones.** Calls 1–4 are the core; 5–6 are bonus.

## The loop per call (≈4 min total each)
1. You: dial + run the scenario (~2 min).
2. You: download logs + recording (~30s). Paste execution ID into sprint convo INBOX:
   `live call N <scenario> exec=<id>` (+ "recording saved" / "no audio").
3. Me: `python pipeline/ingest_live.py --execution <id>` → normalize → deterministic signals →
   `python pipeline/judge_live.py` → `out/live_calls.json` updated → /platform LIVE-TODAY refreshes.
4. Me: one-line readback — what the deterministic signals + judge found (its phenotype, any failure).
5. You: glance at /platform LIVE-TODAY, move to the next call.

## Credits — burn freely, you can't run dry
~$0.06/call observed. 6 calls ≈ $0.36. Time is the only real constraint. Don't ration; do ration TIME.

## Bolna Buddy — talk to them early (questions in SPRINT_CONTROL)
Lead with the framing: *"I built the framework + eval pipeline + UI over the week; today I'm running
live evals — fresh Cartesia-voiced Bolna calls with deliberate edge cases through the same eval
machinery, kept as a separate uncalibrated lane."* Then ask Q1 (interruption telemetry — gates call #5), Q2 (webhook payloads), Q4 (private
repo + collaborator OK for submission?). Paste their answers into INBOX; I adapt the plan.

## Pushes during Sprint 1 (you confirm each — 3–4 total)
1. ~11:00 arrival state. 2. first live calls ingested. 3. live calls judged + /platform LIVE-TODAY.
4. 13:35–40 final + tag `submission-jun13`. I prep each, show you the diff, you say "push." Secret-scan
runs first every time. **No pushes 13:45–14:45** (judges clone).

## 13:45 submission (text pre-drafted by the submission agent; you just paste)
Repo URL + 5-line description + demo URL/loom + tag. If Wi-Fi is shaky, the loom = a screen-recording of
`/` + `/platform` made in the morning.

## If something breaks
- A live call won't ingest → skip it, keep presenting the frozen 46-call story; live is a bonus slice.
- Wi-Fi dies → everything demo-critical is offline already; only the live-call segment needs network, so
  do calls EARLY and cache instantly.
- You're behind on time → drop to 4 calls, then stop. The frozen pilot + the surface already win on
  their own; live calls are the cherry, not the cake.
