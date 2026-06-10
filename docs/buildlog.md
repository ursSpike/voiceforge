# Build Log

Per-block record: what now exists / what was learned. Written at each block's close,
right after the push (SPEC §2.1).

---

## Block 0 — Skeleton · Jun 10, 20:34–21:15 IST · box 1h, used ~40m
- commit `2751961` → pushed (github.com/ursSpike/voiceforge, private)
- **What now exists:** full §6 tree · 5 schemas · rubric.yaml v0 · signals.py FTO core,
  sanity-tested (synthetic fixture → `0:10 agent barge-in 800ms` + `0:19 latency 1,620ms`,
  exact money-shot format) · judge.py with disk cache + --smoke · limitations.md written first ·
  venv with google-genai + pyyaml.
- **What we learned:** the deterministic core is proven before the hero call depends on it;
  gh was already authed so push-per-block is frictionless. Open item carried into Block 1:
  GEMINI_API_KEY → live smoke run (this buildlog entry rides with the Block 1 commit).

## Block 1 — Hero call · Jun 10, 21:05–21:35 IST · box 2.5–3h, used ~30m
- push: "hero call: audio + ground-truth turns + FTO failure table (barge-in 800ms, gap 1.6s)"
- **What now exists:** `hero_001.wav` (86.5s, en-IN Neerja agent × Tenglish caller, recorded
  in-browser) · `turns.json` written from the assembly placement (self-check: every measured
  FTO == engineered) · the real failure table: `0:18 — agent barge-in — 800ms overlap` and
  `0:50 — response latency — 1,620ms gap` · the recording booth (teleprompter + mic +
  one-click assemble) that replaced the phone/AirDrop flow.
- **What we learned:** in-browser capture made retakes free and kept the speaker in flow;
  engineered-FTO-in == measured-FTO-out makes the money shot self-validating. Real demo
  timestamps are 0:18/0:50 (spec's 0:14/0:41 were placeholders — demo copy updates in Block 11).

## Block 2 — Money-shot surface (PULLED FORWARD from Day 2) · Jun 10, 21:25–22:10 IST · box 2h, used ~45m
*(second pass at Spike's request: hands-free one-take booth flow — VAD auto-advance with
per-turn silence hold, t2's scripted pause protected — + player upgraded to custom transport
with failure ticks on the seekbar + chat-bubble conversation with inline failure strips;
all five seek paths re-verified programmatically, consoles clean)*
- push: "money shot v0: audio + clickable timestamp table seeking"
- **What now exists:** `/shot` page over the same local server — sticky player, stat chips
  (median/p90/barge-ins/laggy), the failure table with rows that seek to 1.5s before the moment
  and play, transcript with live turn highlight (both speakers light up during the overlap).
  `/signals.json` recomputes from rubric.yaml per request — edit rubric, refresh, table updates.
- **What we learned:** the stdlib server needed HTTP Range (206) support — without it Chrome
  marks audio non-seekable and silently swallows currentTime writes. Caught by a programmatic
  click-test in the preview browser; would otherwise have died on stage. **Demo exists
  end-to-end on night one** (spec target was Day 2 ~hour 7).

