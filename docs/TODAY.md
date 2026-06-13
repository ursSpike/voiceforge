# OPEN THIS FIRST AT THE VENUE

TIME | CHECK | COMMAND / ACTION | PASS CONDITION | NEXT
---|---|---|---|---
arrival | work in the canonical repo | `cd /Users/varsh/voiceforge` | `pwd` ends in `/voiceforge` | continue
arrival + 1m | clock and Git state | `date; git status --short --branch` | expected branch; no surprise tracked changes | do not clean blindly
arrival + 3m | core artifact gate | `.venv/bin/python pipeline/preflight.py --offline` | `0 FAIL` | continue
arrival + 5m | live-lane isolation | `.venv/bin/python pipeline/test_live_isolation.py` | all checks pass | continue
arrival + 7m | start product server | `.venv/bin/python pipeline/serve_surface.py --port 7871` | both URLs print | leave terminal running
arrival + 8m | presentation smoke | open `http://localhost:7871/` | loads, keys work, drawer closes | use only as current build, not final-cleared
arrival + 10m | platform smoke | open `http://localhost:7871/platform` | loads; frozen data visible | live section may initially be empty
10:10 latest | frontend handoff check | read Claude’s final QA report | both routes cleared, or `/platform` explicitly uses audited fallback | do not extend redesign past 10:15
first Buddy chat | verify execution API before depending on it | ask for exact execution and log endpoints | one real execution ID fetch succeeds | record answer in `SPRINT_CONTROL.md`
first live call | make a clean baseline in Bolna | save execution ID immediately | ID copied; call completed | ingest
after each call | ingest into isolated live lane | `.venv/bin/python pipeline/ingest_live.py --execution <ID>` | file lands under `data/normalized/live/` | judge
after ingest | judge live calls | `.venv/bin/python pipeline/judge_live.py` | `out/live_calls.json` updated; marked `LIVE · UNCALIBRATED` | refresh `/platform`
after each result | protect frozen experiment | `.venv/bin/python pipeline/test_live_isolation.py` | frozen hashes unchanged | next scenario
before any commit | inspect only intended files | `git status --short; git diff --check; git diff --stat` | no scratch, secrets, frozen outputs, or accidental notebook edits | stage allowlist
before any push | review commit and run gate | `.venv/bin/python pipeline/preflight.py --offline` | `0 FAIL`; commit reviewed | ask Spike before push
before selection | capture fallback | screenshot `/` and `/platform`; keep `out/dashboard.html` | files open without Wi-Fi | freeze risky work
if Top 10 | improve one demonstrated failure only | rerun the same scenario after one prompt change | honest before/after, no lift claim | rehearse twice
before presenting | final clean rehearsal | Wi-Fi off; `/` → `/platform` → fallback | finishes in 6–6.5 min | stop editing

## Today’s Core Scenarios

1. Clean booking baseline.
2. Hinglish/code-switching.
3. Ambiguous request that should trigger clarification.
4. Change a required slot midway.
5. Barge-in only if Bolna confirms explicit interruption telemetry.

## Hard Rules

- Never edit `eval/`, frozen `out/*.json`, `rubric.yaml`, or normalized JSON by hand.
- Never run `git add -A`.
- Never call live calls calibrated. Say: **same eval machinery, separate uncalibrated live lane**.
- Never move/delete scratch or design files during the sprint.
- Never push automatically. Spike reviews the staged paths and explicitly says `push`.
- Safe fallback: `out/dashboard.html`.
- When confused: add one line under `INBOX` in `docs/SPRINT_CONTROL.md`, then send `tick`.
