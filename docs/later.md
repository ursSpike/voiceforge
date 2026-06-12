# Later — the parking lot

New ideas land here during the sprint, not in the build (SPEC §2.3). Nothing in this file
blocks the demo.

## Before repo goes public
- [ ] Replace SPEC.md with a sanitized public version (it is an internal working document —
      review §1 in full before any visibility flip). Repo stays **private** until this is done.

## Cut-list items (pre-authorized, restore post-sprint if cut)
- Wavesurfer waveform + regions on the call player
- Bolna live ingest (adapter-contract slide stands in)
- Next.js polish depth
- A/B live re-run
- Samples beyond the current 46 calls
- Cross-cut chart extras
- Second human labeler

## Roadmap (post-hackathon)
- Multilingual evals: IndicVoices (gated, timestamps undocumented — investigate), code-switch
  detection as a first-class signal
- Optional: re-synthesize the hero agent with a newer Cartesia Sonic voice (reproduction only — the
  live Bolna agent already runs Cartesia inside its synthesizer; no separate Cartesia key required)
- Real billing-data costs instead of estimates
- Human-review UI for the improvement queue (`needs_human_review` workflow)
- Larger calibration: 2+ raters, multiple dimensions, per-dimension kappa
- Real customer-call corpora partnerships

## Ideas dumped mid-sprint
*(append below, one line each, keep building)*
- Live-agent sandbox (Spike, Jun 10): host a deliberately-flawed LIVE voice agent (streaming
  STT→LLM→TTS, Bolna-style) so anyone can call it, generate organic failures, and watch
  VoiceForge mine their own call — self-serve demo loop. Post-hackathon: it's a multi-week
  build and adjacent to what Bolna already sells; in-sprint, the same itch is covered by
  Block 6 (live Gemini-as-agent replay) + Block 10 (real Bolna call ingest if credits land).
