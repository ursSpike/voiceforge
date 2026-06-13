# Limitations

Written before the first line of pipeline code, on purpose. Every claim in this repo
should survive contact with this file. If a limitation disappears, it gets deleted here
with a commit that says why — it does not get quietly papered over.

## The hero call is constructed
The flagship demo call is a scripted, assembled scenario (English TTS agent × code-switching
human caller). Its timestamps come from the audio-assembly timeline, which makes them exact —
but it is a demonstration of what VoiceForge detects, not evidence drawn from production traffic.
Validity comes from the public-data calibration, not from this call. Disclosed on its own slide.

## The judge is an LLM, pilot-calibrated only
- Judge = Gemini Flash (temperature 0, JSON output). LLM judges have known biases:
  verbosity preference, position effects, leniency drift, and blind spots for audio-native
  phenomena they only see as text + timing annotations.
- Calibration is a **pilot**: one binary dimension, 40–60 blind human labels, small n.
  We report Cohen's kappa with a bootstrap CI and show disagreement cases. We do not claim
  "substantial agreement" unless the number **and** the CI land in 0.61–0.80 (Landis–Koch).
- If only one human rater was available, this is a single-human anchor; a second rater is planned.

## Deterministic signals depend on timestamp quality
- Barge-in and latency math is exact **given correct turn boundaries**. SpokenWOZ turn bounds
  are synthesized from word-level timestamps; hero-call bounds come from assembly.
- Sources with single timestamps (no end times) get latency treatment only — we never fake overlap.
- SpokenWOZ is protocol-collected: few genuine barge-ins. AMI *could* supply real overlap but is
  **not in the current pool** (roadmap); where overlap matters now it comes from the hero call. AMI is
  meetings-domain, not task calls. Frozen labeled slice is **46 calls** (30 Hindi-English `cmd_hi_*` +
  14 SpokenWOZ controls + hero + Bolna); full scored corpus **76** — directional, not statistical.

## Costs are estimates
Cost-per-call and cost-per-successful-call use turn counts × public per-unit price estimates
(LLM/TTS/STT). Labeled "estimated, prototype data" everywhere they appear. No real billing data.

## A/B loop is one scenario
If shown: one closed-loop replay (v1 flawed prompt → detected failures → v2 prompt → same user
turns re-run → re-scored by the same pipeline). It demonstrates the loop's *shape*, not a
statistically meaningful improvement. Production would need more logs, human review, offline training.

## Multilingual: shipped, Hindi-English majority (updated Jun 13)
The frozen labeled slice is **majority code-switched**: **30 of 46 calls are Hindi-English**
(`cmd_hi_*`, Code-Mixed-Dialog, romanized Hinglish) plus the hero (`te-en`) and the real Bolna call
(`hi-en`); the 14 SpokenWOZ calls are the English control arm. `language` is a real schema field and
`language_match` a rubric dimension. The calibration's headline finding lives here: agreement on
hi-en (71%) ≈ English (69%) — language is **not** the reliability axis on this sample (annotator
confidence is). Broader Indic coverage (IndicVoices, real Tenglish audio) is roadmap; the
single-rater pilot n is the real statistical limit, not language coverage.

## Licenses
SpokenWOZ is CC BY-NC — fine for hackathon evaluation; flagged before any commercial use.
AMI is CC BY 4.0.
