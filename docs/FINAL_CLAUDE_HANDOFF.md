# FINAL CLAUDE HANDOFF — one bounded repair before Spike leaves

Do not re-plan. Do not spawn unrelated research. Do not move/delete scratch files. Do not push without
Spike’s explicit `push`.

## Non-Negotiable Clock

Current execution target:

- **08:30–08:45 IST:** live-contract ID/provenance fixes + freeze the two UI data contracts.
- **08:45–09:20:** finish `/` as eight viewport-sized presenter scenes.
- **09:20–09:50:** finish `/platform` as the operator workspace.
- **09:50–10:10:** browser QA at all three resolutions, fix only failed acceptance checks.
- **10:10:** write the report and stop.
- **10:15 hard stop:** no further redesign. If `/platform` is not cleared, route it to the audited
  `out/dashboard.html` fallback and report the missing operator features honestly. Never destabilize
  the cleared `/` presentation to chase platform polish.

Parallelize P0A and P0B only after the shared data contracts are frozen. One coordinator integrates.

## P0A — Presentation `/`

Align the existing Claude Design surface to the eight beats in `docs/demo_docs.md`.

Requirements:

- exactly 8 presenter scenes;
- each scene fits within one viewport at `1280×720`, `1440×900`, and `1920×1080`;
- no scene body is taller than the viewport in presenter mode;
- the full 76-call table and full improvement queue must not render inline;
- show representative rows/cards and move full corpus browsing into a drawer/search overlay;
- preserve real artifact data and all provenance labels;
- keyboard: Left/Right, Home, End, Escape;
- call drawer must open the selected call, stay within viewport, and close cleanly;
- no external resources; offline load;
- current warm design is acceptable if the full green refinement cannot be completed safely.

Do not call this done from DOM presence alone. Measure every scene’s bounding box.

## P0B — Operator `/platform`

Use a separate but related Claude Design layout. It is an operator product, not a second presentation.

Required layout:

- fixed left call-directory rail with search and filters;
- clear `Frozen Pilot` / `Live Today` switch;
- aggregate and individual-call modes;
- individual call view: transcript, deterministic signals, task outcome, judge evidence, phenotype,
  recommendation, provenance;
- Live Today cards display `LIVE · UNCALIBRATED` prominently;
- live empty state is useful and near the top, not at the bottom of a 4,800px report;
- clicking a live call opens its complete evidence view;
- no ingest button unless it actually performs a safe supported action; an execution-ID helper may show
  the exact terminal command instead;
- keep `out/dashboard.html` untouched as fallback.

## P0C — QA

Before UI QA, close two remaining live-contract edges:

- the normalized JSON’s internal `call_id` must also be namespaced as `bolna_live_<prefix>`; do not
  rely only on the filename/subdirectory for identity or cache separation;
- do not stamp “Cartesia voice” merely because a call is live. Validate synthesizer provenance from
  the fetched execution/config when available; otherwise say provider unverified rather than infer it.

Run and report:

```bash
.venv/bin/python pipeline/test_live_isolation.py
.venv/bin/python pipeline/ingest_live.py --selftest
.venv/bin/python pipeline/judge_live.py --selftest
.venv/bin/python pipeline/preflight.py --offline
```

Browser-test `/` and `/platform` at all three target resolutions. Test:

- eight scene dimensions;
- keyboard sequence;
- representative call drawer;
- platform search/filter;
- Frozen/Live switch;
- empty Live state;
- one temporary fixture live-call rendering;
- zero console errors;
- zero external requests;
- frozen artifact hashes unchanged.

## P0D — Human Operations

Keep these files:

- `docs/TODAY.md` — Spike opens this first at the venue.
- `docs/ROOM_PLAYBOOK.md` — Spike reads this in the cab.
- `docs/PUSH_PROTOCOL.md` — ship-check agent follows this.

Update `docs/SPRINT_CONTROL.md` so the current state is honest:

- event/check-in begins around 09:30;
- presentation and platform remain `IN PROGRESS` until P0A/P0B QA passes;
- remove stale “go P0” actions;
- first on-site engineering gate is one real execution-ID fetch with the Bolna Buddy.

## Stop Condition

Stop after one commit and a report containing:

- exact files changed;
- exact scene heights at each viewport;
- screenshots of `/` and `/platform`;
- test outputs;
- frozen before/after hashes;
- remaining limitations.

Do not claim demo-cleared unless every requirement above passes.
