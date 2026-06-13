# BATCH 2 — Sprint-day playbook (the goldmine) + the Project Bible

**New reality from goldmine.md:** Jun 13 is an ON-SITE SPRINT, not a pure demo day.
Schedule: ~10:30–13:45 **Build Sprint 1** → **13:45 prototype submission link** (repo + description +
URL/loom) → Top-10 cut → 15:00–16:30 **Build Sprint 2** (Top 10) → presentations (5–8 min).
Bolna Buddies on-site for tech support. **Bolna + Cartesia credits available to burn.**
Everyone had the 7 days → pre-built is the baseline; our transparent git history is an asset.

## The framing sentence (memorize — it's the honest meta)
> "I engineered the framework, eval pipeline, and UI over the week. Today I'm running **live
> evaluations**: fresh Cartesia-voiced Bolna calls with deliberate edge cases — interruptions,
> code-switching, noise — pushed through the same calibrated pipeline, live."

## Deliverable A — PROJECT_BIBLE.md (built TONIGHT by an agent, read by Spike on the commute)
One file = the entire project understood. Distinct from demo_docs.md (that's the *performance*; this
is the *understanding*). Contents:
- The story in 10 lines (what VoiceForge is, who it's for, the loop).
- **Data flow end-to-end** with every file named: provider logs → ingest (bolna/cmd/swz adapters) →
  schema constitution → deterministic signals (FTO math, thresholds) → blind label booth + frozen
  manifest → quarantined judge (5 dims + binary, validate-before-cache) → calibration (κ + balanced
  accuracy + the truth correction) → phenotypes/archetypes → improvement queue → dashboard/present.
- Every metric defined in 2 lines each + its caveat (κ, balanced acc, Youden, failure recall, MCC,
  metric trap, cost/success, brittle share).
- Every honest limitation and WHY it's a strength in the room.
- The audit-trail story (frozen hashes, gates, what "calibrated" does/doesn't mean).
- Glossary for terms Spike may get asked (FTO, barge-in, prevalence paradox, bootstrap CI, DPO-roadmap).

## Deliverable B — Sprint 1 execution list (10:30–13:45, ~3h, credits burn)
Priority order — stop wherever the clock says:
1. **Fresh live Bolna calls through the Cartesia-voiced agent** (the upgrade we've wanted since Jun 11
   — the ingested execution predates the Cartesia config; today we fix that ON SITE). Script 4–6 calls,
   ~2 min each, deliberate edge cases: (a) clean happy-path booking; (b) caller interrupts mid-sentence
   ×2; (c) Hinglish code-switching; (d) ambiguous/changing request (repair loop); (e) background noise;
   (f) optional prompt-injection attempt. **Download logs + recordings IMMEDIATELY** (signed URLs expire).
2. **Ingest each live** (`pipeline/ingest_bolna.py`) → normalize → score → judge (`judge_run` paths) →
   regenerate surface. ⚠️ GUARD: new calls are **corpus-only additions** — they do NOT enter the frozen
   46-call manifest, do NOT touch calibration (κ stays the audited pilot). Label them live as a
   "fresh slice" if time allows (booth still works), shown separately.
3. **A "LIVE today" chapter/section** on the present surface: today's calls, their signals/judgments,
   timestamps proving on-site work. This is the optics + the substance in one.
4. **Bolna Buddy questions** (use them): webhook/telemetry endpoint for post-call auto-ingest (replaces
   polling), recording URL retention, any 429/limits on the venue network.
5. **Commit cadence**: commit after each milestone with honest messages ("live call #3: barge-in case
   ingested + judged"). See Batch 3 choreography.
6. **13:45 submission package** (prepare the text TONIGHT, paste tomorrow): repo link + 5-line
   description + demo URL/loom. Fallback loom = screen recording of the present surface (record in the
   morning if possible).

## Deliverable C — Sprint 2 list (15:00–16:30, if Top 10)
1. **Before/after beat**: take the worst live failure from Sprint 1, apply one improvement-queue
   recommendation to the Bolna agent prompt, re-run the same scenario, show both calls side by side on
   the surface. Framed honestly: "one scenario, loop demonstrated — not a measured lift claim."
2. Fallback capture: screenshots + screen recording of the final surface.
3. Rehearse with demo_docs.md, full run ×2, trim overruns.
4. Fix only demo-blocking bugs. No refactors after 16:00.

## Credits math (so we burn smart, not dry)
- Bolna wallet was $5 default (+ organizer top-up promised). Observed cost ≈ $0.06/call (5.96¢/13-turn).
  Even 20 live calls ≈ $1.20 — credits are NOT the constraint; TIME is. Cartesia spend happens inside
  Bolna's synthesizer (no separate key) — no separate burn needed.
- If organizers top up big: optional stretch — batch-run 10–15 scripted scenarios for a richer live slice.

## Risks
- Venue Wi-Fi: all demo paths offline-capable already; live-call segment is the only network-dependent
  piece — do it early in Sprint 1, cache everything instantly.
- Rate limits on judge (free tier): reuse `--delay 7` discipline; judge only the live calls (≤8 calls
  ≈ 48 judgments ≈ fits free tier).
- Don't let live work touch frozen artifacts: the gates already enforce this; respect them.

**Sequencing: Bible agent TONIGHT (parallel with Batch 1 agents). Everything else executes ON SITE
tomorrow with this file open.**

## PLATINUM AMENDMENTS (from platinum.md)
- **Presentation window**: 4:40–6:30 PM, 10 teams ≈ 10–12 min each INCLUDING Q&A → 6:30 talk + ~4 min
  Q&A defense. Framework: hook (60s) → live under-the-hood demo (the surface) → architecture flex →
  Q&A. Matches Batch 1's slide spec; Agent B uses this as the outer frame.
- **Bolna Buddy playbook** (use them all day; they pre-sell you to the judging desk):
  - 10:30 kickoff: the framing intro (ML-eval positioning + what today's live evals are) + ask: "what
    telemetry/webhook payloads do enterprise clients watch when agents face conversational friction?"
  - 11:30 integration: "cleanest way to intercept WebSocket data/transcripts without adding latency?"
    and "does Bolna surface an explicit interruption token/timestamp in telemetry I can parse into my
    failure clustering?" (directly feeds our barge-in story).
  - 13:00 presentation check: show the surface — "if you were judging, what metric/visualization would
    you want highlighted to prove enterprise-ready?" Apply one piece of their feedback live + tell them.
- **Q&A defense (add to demo_docs.md):** (1) "How do you ensure the eval layer doesn't hallucinate?" →
  evidence-cited judgments validated before caching, deterministic-first doctrine, blind human labels,
  κ measured-not-assumed, the judge is marked uncalibrated where calibration doesn't cover it. (2) "How
  does this scale?" → honest: batch pipeline is async-ready + cache-keyed per call/dim; calibration
  protocol is the scalable part (n grows, machinery unchanged); live-stream ingestion is roadmap via
  Bolna webhooks (ask Buddy which payloads).
- **Submission window rule:** NO breaking pushes 1:45–2:45 PM (judges may clone). Freeze, then Sprint-2
  work resumes on the same repo.
