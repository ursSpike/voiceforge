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
- **(chosen, rejected) preference pairs** — every detected failure becomes a DPO-ready JSONL line

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
             ├─ pipeline/dpo_export.py ──▶ out/queue.jsonl (TRL) + out/queue_openai.jsonl
             └─ pipeline/costs.py + crosscut.py ──▶ out/analytics.json
                  └─ web/ — static dashboard, read-only over out/
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
Multilingual evals (IndicVoices et al.), live Bolna ingest adapter, second human rater,
larger corpora, real billing-data costs. See [docs/later.md](docs/later.md).
