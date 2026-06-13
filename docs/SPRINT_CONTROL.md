# SPRINT CONTROL — the adaptive coordinator file (Jun 13)

**How this works:** Spike pastes ANYTHING new into the INBOX below (Buddy answers, schedule changes,
judge gossip, an idea, a bug sighting) — telegraphic is fine. Every coordinator turn: read INBOX →
classify each item NOW / NEXT / IGNORE → update the plan + agent lanes → verify outputs → clear the
item into the LOG with its resolution. The coordinator NEVER pushes without Spike's confirm and NEVER
touches frozen artifacts.

## BOOTSTRAP PROMPT (paste this ONCE to start a fresh sprint convo)
> You are my VoiceForge sprint coordinator and audit master. Read `docs/SPRINT_CONTROL.md`,
> `docs/MASTER_PLAN_JUN13.md`, `docs/SPRINT1_RUNBOOK.md`, and `docs/plans/agent_roster.md` — that is the
> full plan; don't re-plan it. Every message I send is an INBOX item (telegraphic is fine). Each turn:
> classify each item NOW/NEXT/IGNORE, update SPRINT_CONTROL.md, then give me ONE next action + a time
> check against the master timeline. Rules you never break: never push without my explicit "push", never
> modify frozen artifacts (`eval/*`, `out/judge_results.json`, `out/calls.json`, `out/analytics.json`,
> `out/demo_report_data.json`, calibration numbers, `rubric.yaml`), never `git add -A`, never claim a
> number not in a committed artifact. Live calls are a separate `LIVE · UNCALIBRATED` lane. When I type
> `explain <topic>` spawn the explainer agent. Start by reading the files and telling me my current next action.

## 🎯 RUBRIC REORIENTATION (Jun 13, from hackathon.md — OVERRIDES prior submission assumptions)
**The deliverable is a WORKING BOLNA VOICE AGENT, scored + tested live. VoiceForge = the Scale-Up
criterion + proof-of-quality, NOT the submission.** Schedule corrected: 10:30 build · **11:45 submission
link · 2:00 PM HARD deadline** (submit: live agent link + problem statement + target metric + backup
recording) · 2:45 Top-10 · 3:00–4:30 Sprint-2 · 4:40–6:30 **3-MIN demos** (Problem→Workflow→Live Agent→Impact).
Rubric (5×20): Problem Applicability · Cartesia+Bolna Usage · Multilinguality · **Scale-Up (VoiceForge's win)** ·
Agent Quality (judges CALL IT LIVE).

**AGENT-FIRST priority (agent = 4 of 5 criteria; VoiceForge = the Impact/Scale-Up beat):**
1. LOCK problem statement (4 Qs) — recommend **inbound restaurant table-booking agent, Hinglish** (matches
   existing agent + cmd_hi data; metric = booking-completion rate, which VoiceForge measures).
2. Credits: find Buddy, top up (mandatory).
3. Build/polish the Bolna agent (7 steps): system prompt (identity/objective/paths/guardrails/exit) ·
   Cartesia voice (deliberate) · multilingual (Hindi+English+Hinglish mid-call switch) · KB · guardrails.
4. Test 5 scenarios (happy/confused/refusal/interruption/out-of-scope) — these ARE the live calls.
5. Feed those calls → VoiceForge (ingest_live+judge_live) → /platform Live Today = the measured Impact.
6. Submit by 2:00: agent link + problem + metric + backup recording (record early).
**Discipline: AGENT first, VoiceForge second. Don't over-polish the eval lab — the live test scores the agent.**

## INBOX (Spike writes here — newest on top)
- **[DONE] Final clinic agent created.** `Aarogya Clinic & Diagnostics — Aarav`,
  agent ID `cb7dee37-fe1b-43fb-a669-4f56a46eeb46`, Bolna status `processed`.
  Cartesia Devansh matches the male persona; Hindi + English/Hinglish; processed
  knowledge base attached. Phone requires exactly 10 digits; home collection
  requires an address.
- **[DONE] First live call ingested.** Execution
  `a0f508ad-c1af-4b1b-981e-bea87f4648df` exposed the original persona,
  phone-length, and missing-address defects; all three are repaired in the final
  agent. The call remains preserved as an honest before-improvement example.
  Hindi+English/Hinglish, Cartesia Devansh on both language paths, 13 structured
  appointment/safety fields. Open `docs/AGENT_READY.md`; next action is five
  builder test calls, then ingest each execution into Live Today.
- **[ACTIONED] Bolna API research (docs/BOLNA_API_NOTES.md).** ✅ ingest_live.fetch_raw MATCHES the real
  API (GET /executions/{id} + /log, Bearer auth) — first real execution ID will just work. Outbound =
  POST /call (agent_id + recipient_phone_number; vars in `user_data`). Fixed fetch_latest → real endpoint
  GET /v2/agent/{id}/executions?page_size=1&page_number=1, agent id from $BOLNA_AGENT_ID; selftests green.
  ⚠️ **HONESTY: Bolna gives NO interruption/barge-in field and NO per-turn timestamps** (transcript = flat
  string; timing only reconstructable from /log event times). → For LIVE calls, VoiceForge scores task
  outcome + judge dims + cost (+ reconstructed latency), **NOT barge-in**. Do NOT claim live barge-in
  detection. The "interruption" test scenario = AGENT-recovery (Agent Quality), not a VoiceForge metric.
  Cartesia stays proven from agent config (GET /v2/agent/{id}), not the call → synthesizer_verified=False.
  (ingest_live.py + BOLNA_API_NOTES.md uncommitted — fold into the next natural push w/ first live call.)
- **[ACTIONED ~08:55] Spike steer — problem-first cold open + Bolna/Cartesia multi-agent talking point.**
  Disposition: applied as DELIVERY layer in demo_docs.md (Slide 1 reworked to where-calls-fail → who-I-am →
  thesis; metric-trap Slide 2 is the "why"; multi-agent talking point added to Slide 7 + ROOM_PLAYBOOK).
  Kept as script framing, NOT new scenes, so it doesn't desync P0A's 8-scene build. OPTION (post-P0A,
  clock permitting, only if it doesn't destabilize cleared `/`): sharpen scene-1/2 COPY to read explicitly
  problem-first. Deferred to coordinator's integration pass.

## CURRENT PHASE
FINAL UI REPAIR (post-Codex-audit) — P0A (`/` 8 scenes) + P0B (`/platform` operator) running; hard stop
10:15. Venue check-in ~09:30; build sprint 10:30. P0C live-contract edges CLOSED (call_id namespaced,
synthesizer provenance no longer inferred). `/` and `/platform` remain **IN PROGRESS** until measured
viewport QA passes — `out/dashboard.html` is the cleared fallback meanwhile.

## PROTECTED INVARIANTS (no agent may violate)
- Frozen: label manifest/CSV/snapshot · judge_results.json · calls.json · calibration numbers · rubric.
- Live sprint calls = corpus-only, separate artifacts (`bolna_live_*`, out/live_*.json), always
  labeled `LIVE · UNCALIBRATED`.
- Honesty wording everywhere (estimated/heuristic/uncalibrated/measured-not-assumed).
- No pushes 13:45–14:45 (judges clone). 3–4 confirmed pushes total. Secret-scan before every push.
- Demo never requires network; `out/dashboard.html` is the always-working fallback.

## ACTIVE LANES (coordinator updates)
| lane | agent | output | status |
|---|---|---|---|
| script | demo_docs | docs/demo_docs.md | ✅ DONE — 6:30, verified |
| bible | project_bible | PROJECT_BIBLE.md | ✅ DONE — verified; caught 2 stale docs (fixed) |
| live-bridge | live_ingest | pipeline/ingest_live.py + judge_live.py | ✅ DONE — selftests re-run 8/8+16/16, safe-refusal ✓, frozen sealed, no leak |
| routes | surface | / + /platform | ✅ DONE — build_surface+serve_surface; browser-verified 76 calls, 0 console errs, 0 external refs, /platform LIVE-TODAY graceful |

**P0 FLEET COMPLETE (07:55). Next: Spike reads demo_docs aloud once → leave for venue.**
Stale-doc truth-pass landed: docs/dataset_card.md + docs/limitations.md corrected (were pre-Phase-B:
claimed English-only / 46=44 SpokenWOZ; real = 30 Hindi-English + 14 SpokenWOZ + hero + Bolna).
README false-DPO truth-pass DONE (diagram now marks DPO a roadmap stub; multilingual/live-ingest shown
as shipped). All six Codex truth-fixes landed.

## TOP 3 NEXT ACTIONS
1. Coordinator: integrate P0A/P0B when they land; MEASURE every scene bbox at 1280×720/1440×900/1920×1080;
   if `/platform` doesn't clear by 10:15, route it to `out/dashboard.html` fallback and report honestly.
2. One final reviewed commit (incl. TODAY/ROOM_PLAYBOOK/PUSH_PROTOCOL) + QA report; do NOT push (Spike pushes).
3. FIRST ON-SITE ENGINEERING GATE: one real execution-ID fetch with the Bolna Buddy before any live call
   is trusted (verifies the unproven `--execution` endpoint). Record the answer in INBOX.

## BUDDY QUESTIONS (carry to venue — answers go in INBOX)
1. Telemetry: does Bolna expose an explicit interruption token/timestamp? (gates the barge-in scenario)
2. Webhook payloads enterprises watch for conversational friction? (roadmap slide + live-bridge v2)
3. Cleanest WebSocket/transcript intercept without latency?
4. Is private repo + collaborator access acceptable for submission? (privacy gate)
5. Venue Wi-Fi / rate-limit quirks?

## SUBMISSION SNAPSHOT (fill by 13:30)
- Repo URL: github.com/ursSpike/voiceforge (private→decision pending Buddy answer)
- 5-line description: (submission agent drafts)
- Demo URL / loom: local server + fallback recording
- Tag: `submission-jun13`

## LOG (resolved items move here)
- 07:17 verified GPT-treasure claims: clock real, audit.md tracked-but-deleted (restore in next commit),
  README stale (DPO diagram false — truth-pass queued), ingest hardcoded (live-bridge lane created),
  judge manifest-only by design (separate live judge path in live-bridge lane).

## DEFERRED (good ideas, not today)
- In-platform Bolna call origination/agent-config UI (Sprint-2+ only if Buddy confirms API; "too
  far-fetched" — Spike's own read was right).
- Claude-design round-3 refinement (only AFTER / + /platform run on real DOM; never another fixture).
- Grounded-outcome P1 integration; second-rater run; DPO export.
