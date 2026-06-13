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

## INBOX (Spike writes here — newest on top)
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
