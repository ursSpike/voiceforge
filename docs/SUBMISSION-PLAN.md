# SUBMISSION PLAN — frozen reference (written Jun 11, 17:33 IST)

Deadline: **working prototype submitted Jun 12 night** · demo Jun 13 at Bolna HQ.
Internal freeze: **Jun 12, 22:30 IST** — after that, only packaging, no code.
Check progress anytime: `.venv/bin/python pipeline/preflight.py` (the executable version of this plan).

## Official rules → how we satisfy them
| rule (Sonam's email) | satisfied by | check |
|---|---|---|
| MUST use a Cartesia voice model | live Bolna agent voiced Devansh/sonic-3 ✓ + hero call re-voiced ✓ | preflight `cartesia-live`, `hero-cartesia` |
| Bolna + Cartesia at the core | Bolna agent makes calls → VoiceForge ingests Bolna logs (Block 10, NOW CORE not bonus) | preflight `bolna-ingested` |
| functional + demonstrable Jun 13 | live pipeline + /shot page + fallback recording | preflight `fallback`, rehearsal Jun 13 |
| original work in Jun 11–12 window | core product (ingest, judge pipeline, DPO, calibration, charts, dashboard) all built Jun 11–12; Jun 10 evening was scaffolding/recon — git history is transparent, say it honestly if asked | — |
| one submission | solo | — |

## Done already (verified)
hero call (Cartesia Devansh, self-check OK, failures 0:15/0:48) · money-shot page /shot (click-to-seek verified) · normalize+signals over **46 calls** (44 SpokenWOZ + hero + Bolna, Batch 2) · Gemini judge harness (smoke + cache) · Bolna agent live + 1 ingested execution (246cd9f3…) · both sponsor keys verified · 36 training notebooks.

## CRITICAL PATH (in order — ~13h of work vs ~13h available; A/B is OUT unless ahead)
| # | block | what | time | owner |
|---|---|---|---|---|
| 1 | B10 | **Bolna ingest**: execution 246cd9f3 (+1–2 fresh calls with deliberate failures) → call_log → signals+judge. Timing from `/log` created_at diffs, NEVER scrubbed transcript. Download recording immediately (signed URLs expire). | 2h | me |
| 2 | B3b | **Eval core**: expand pool to ~45 SpokenWOZ calls (labels need ≥40!) · judge 3 dims/call (cached) · score.py → `out/calls.json` + `out/call_<id>.json` | 2.5h | me |
| 3 | B4 | **Blind labels**: Spike labels 40–60 calls, ONE binary dim, BEFORE seeing any judge output (see tripwire below) → `eval/labels_spike.csv` | 1–1.5h | HIM |
| 4 | B5 | **DPO export**: 10–20 pairs, single-axis diffs → `out/queue.jsonl` + OpenAI mirror | 1.5h | me |
| 5 | B7 | **Kappa**: judge-vs-Spike + bootstrap CI + confusion matrix + 2 disagreement cases | 1h | me |
| 6 | B8 | **Business-value chart** + stress cross-cut → `out/analytics.json` + `reports/charts/` | 1.5h | me |
| 7 | B9 | **Dashboard**: extend existing local server — call list + scorecard view over `out/`. /shot already exists. 90-min cap, then it ships as-is. NO Next.js. | 1.5h | me |
| 8 | B11 | **Package + SUBMIT**: slides (§9 order), screenshots, fallback recording of money shot (real catch), limitations slide, submit, FREEZE | 1.5h | both |
| — | B6 | A/B loop: ONLY if ≥2h ahead at 15:00 Jun 12; otherwise the loop-shape slide (pre-authorized) | (3h cap) | me |

## Ordering tripwires (the misses this doc exists to prevent)
1. **BLIND-LABEL RULE**: Spike must NOT see per-call judge scores before `labels_spike.csv` is saved. I may RUN the judge while he's away (outputs stay unopened by him); on his return, labeling is his FIRST task, reveal after. Violating this voids the calibration claim.
2. **SUBMISSION MECHANISM UNKNOWN**: the email never says HOW to submit. Spike replies to Sonam TODAY asking the mechanism (+ nudges credits). Do not discover this at 21:00 tomorrow.
3. **Bolna agent voice can drift**: any dashboard edit could reset the synthesizer. Preflight re-checks `provider=cartesia` live before submission.
4. **Fallback recording is NEVER cut** and gets made at ~20:30 Jun 12, not last-minute.
5. **Sleep gate stands**: stop ~00:30 tonight regardless of notebook momentum; tomorrow is a 13h day.
6. **Timestamps changed with the re-voice**: demo copy says **0:15 barge-in / 0:48 gap** now (not 0:18/0:53).

## Updated cut order (if time attacks, cut top-down)
1. A/B live re-run → loop-shape slide · 2. AMI overlap calls · 3. Dashboard polish beyond list+detail · 4. Cross-cut chart extras · 5. Pool beyond ~45 calls.
**NEVER cut**: hero call · signals math · judge-with-reasons · ≥40 blind labels + kappa · DPO export · **Bolna ingest** · **Cartesia voice** · fallback recording.

## Notebook-time honesty (Spike's study track)
Full course = 12–15h; it does not fit before submission. Suggested tonight (~3–4h): P00 → 00, 01, 02, 04, 06 (survival) + 10, 11, 12 (judge/evidence/calibration — directly relevant to labeling tomorrow). Books 14, 17, 18 in tomorrow's breaks. **28 + 29 are Jun-13-morning rehearsal material.** Tier-2/3 depth is post-hackathon — the course doesn't expire.

## Jun 13 (demo day, ~2h morning)
Rehearse 3-min + 7-min out loud (book 29 is the script) · glance cite-card (SPEC §10) · verify /shot serves + audio plays on demo machine · walk in slept.

## Scheduled tripwires (cron, local machine — best-effort nudges, this doc is the truth)
- Jun 12 09:00 IST — morning gate: preflight count + start B10/B3b
- Jun 12 15:00 IST — cut-list gate: if B5/B7 not started, invoke cuts
- Jun 12 20:00 IST — package gate: start B11 now, freeze 22:30
