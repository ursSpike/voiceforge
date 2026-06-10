# Demo Script — DRAFT (finalized in Block 11)

Emotional order, locked: **pain → measurement → correction → dataset → scale.**
No research vocabulary in the first 30 seconds — no kappa, no DPO, no dataset names
until the room has heard the failure.

## 3-minute spine

1. **(15s) Hook.** "Voice agents demo great and fail quietly in production. Teams can't see
   why calls fail, what they cost, or how failures become the next version. Listen to this."
2. **(45s) MONEY SHOT.** Hero call plays aloud — the room hears the barge-in and the dead air.
   Failure table flags `0:14 · agent barge-in · 800ms overlap` and `0:41 · response latency ·
   1,620ms gap`. Scorecard reason → corrected response → **the preference pair appears on
   screen.** "Every call is unlabeled preference data. We label it automatically."
3. **(30s) A/B.** Before/after panel. Verbatim honesty line: "This is one scenario replay, not
   statistical evidence. VoiceForge caught the failure, proposed the fix, and the same evaluator
   scored v2 higher. The point is the closed-loop shape — production would require more logs,
   human review, and offline training. At scale, this loop is the dataset."
   *(Fallback: loop-shape slide.)*
4. **(30s) Trust.** "It's not vibes — deterministic timing signals, plus an LLM judge
   pilot-calibrated against blind human labels: here's the agreement, and here are two cases
   where the judge was wrong." *(engineer hook)*
5. **(30s) Scale.** Dashboard sweep + business-value chart — "calls with voice failures complete
   less and cost more per success." *(founder hook)* + adapter-contract slide: provider-neutral.
6. **(15s) Close.** "VoiceForge judges the conversation trace, not just the transcript. Most
   demos stop when the call ends — VoiceForge starts there: evals, failures, cost signals, and
   the next training example."

7-minute version adds: dashboard walk (call list → detail → queue drawer) + live rubric.yaml
edit → rerun → scores update + cross-cut chart.

## Q&A pivots
- Coval/Hamming/Cekura → "test harnesses tell you *what* failed; VoiceForge mines the same calls
  for *improvement data* — the DPO pairs they don't produce."
- Roark → "replays calls to *test* you; VoiceForge mines calls to *train* you."
- Leaping AI → "closes the loop but locks you to their platform, prompt-level only; VoiceForge is
  neutral and outputs portable weight-level data you own."
- Langfuse/Braintrust → "great plumbing, text-first and voice-blind; my preference label IS the
  voice signal."
- Citations: SPEC §10 cite-card — click links before citing.
