# VoiceForge

**Most voice-agent demos stop when the call ends. VoiceForge starts there.**

VoiceForge is the improvement-data layer for voice agents. It takes raw call logs from any
voice stack — vendor-neutral, downstream of Bolna, Cartesia, or a bare transcript+audio pair —
and turns them into:

- **Structured outcomes** — task completed or not, which required fields were captured
- **Quality evals** — deterministic conversation-trace signals (barge-in overlap in ms,
  response-latency gaps) plus an LLM judge where every score carries a reason and evidence turns
- **Failure timestamps** — the exact moment a call went wrong, measured, not vibe-scored
- **Cost signals** — estimated cost per successful call, so failures show up in money
- **Improvement queue** — every detected failure becomes an evidence-cited, ranked fix (the shipped
  deliverable). *(Turning these into (chosen, rejected) DPO pairs is roadmap — `pipeline/dpo_export.py`
  is a stub.)*

The one-line thesis for engineers: **VoiceForge judges the conversation trace, not just the
transcript** — language, timing, overlap, task outcome, cost, repair quality. Transcript-only
evals structurally miss voice-native failures.

> **Status:** 3-day prototype built for the Bolna × Cartesia Voc-a-thon (Bengaluru, June 2026).
> Built honest: see [docs/limitations.md](docs/limitations.md). The hero demo call is a disclosed
> constructed scenario; the LLM judge is pilot-calibrated against blind human labels; costs are estimates.

## How it works

```
raw call (audio + log)
   └─ pipeline/normalize.py ──▶ call_log (schemas/)
        ├─ pipeline/signals.py ──▶ deterministic dims: barge-in ms, latency gaps (FTO math)
        ├─ pipeline/judge.py ────▶ judged dims: {score, reason, evidence_turn_ids} (Gemini, cached)
        └─ pipeline/score.py ───▶ scorecard, weighted by rubric.yaml  ──▶ out/calls.json
             ├─ improvement queue ──▶ out/demo_report_data.json (evidence-cited ranked fixes — SHIPPED)
             │     (pipeline/dpo_export.py → DPO JSONL is a roadmap stub, not wired)
             └─ pipeline/costs.py + crosscut.py ──▶ out/analytics.json
                  └─ web/ + pipeline/build_surface.py ──▶ out/dashboard.html, out/surface/ (read-only over out/)
```

`rubric.yaml` is the single source of truth for dimensions, weights, and thresholds —
edit it, rerun, and every scorecard updates.

## Quickstart

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env      # add your Gemini API key (aistudio.google.com/apikey)
.venv/bin/python pipeline/judge.py --smoke          # one cached judge call
.venv/bin/python pipeline/signals.py data/hero/turns.json   # failure table (after Block 1)
```

## Roadmap (not in this sprint)
Broader Indic coverage (IndicVoices et al., real Tenglish audio), live-stream Bolna ingest via
webhooks, second human rater, larger corpora, real billing-data costs, DPO-pair export.
See [docs/later.md](docs/later.md).
*(Already shipped, not roadmap: Hindi-English multilingual evals — 30 code-mixed calls are the
calibration backbone — and an on-site live-call ingest bridge, `pipeline/ingest_live.py`.)*
