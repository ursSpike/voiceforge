# VoiceForge — Build Spec v3 (FINAL · Handoff Document)

> **What this file is:** the complete, self-contained build bible for VoiceForge — a 3-day hackathon prototype for the Bolna × Cartesia Voc-a-thon (Bengaluru, demo **Saturday June 13, 2026**; prototype submission June 12 night). It is written to be handed to a **fresh Claude Code session** with zero prior context, which will set up the working directory and drive the build hour by hour.
>
> **How to use:** `mkdir ~/voiceforge && cp` this file in as `SPEC.md`, open Claude Code in `~/voiceforge`, and say: *"Read SPEC.md fully. You are my build copilot for the next 3 days. Set up the repo per §6, then drive me block by block per §5 — enforce the timeboxes, the push-per-block discipline, and the operating rules in §2."*
>
> Converged across three reviewers (Claude Opus, GPT-5.5, Claude Fable) over two verified web-recon passes. v3 locks: **timestamp-table money shot first · A/B loop boxed to one hero call with a 3-hour hard clock · rubric.yaml from day one · business-value chart included · pilot calibration as a fixed, non-negotiable block (size flexes, existence doesn't) · English-first with language as a schema dimension.**

---

## §1. Context for the Agent (read first)

**The builder:** Spike — IIT KGP CSE '25, R&D engineer at Fujitsu Research (scientific ML, benchmarking, perf/accuracy evals on ARM). Comfortable with Python/scripts/ML; NOT a React expert. Long-term lane: model-quality engineering, voice-agent evals, LLM behavior — this prototype is the first public artifact of that lane.

**The event:** Bolna × Cartesia "Voc-a-thon" (real, luma.com/ubu85bxv). In-person Bengaluru. Build week ends June 12 (submission), demo day June 13. Room = founders + founding engineers from Bolna (YC F25, voice-agent platform), Cartesia (Sonic 3.5 TTS), and adjacent voice-AI teams. A Monday panel follows on multilingual/multiregional voice deployment. Goal is not the prize; it's "send me the repo" from a founding engineer.

**The thesis:** *Most voice-agent demos stop when the call ends. VoiceForge starts there.* It turns raw call logs into structured outcomes, quality evals (deterministic + LLM-judged), failure timestamps, cost signals, and (chosen, rejected) DPO-style preference pairs — the improvement data layer no existing voice-eval tool (Coval, Hamming, Cekura, Roark) produces. Vendor-neutral, sits downstream of any voice stack.

**Two audiences, alternate the hooks:** founders need to *feel* it (audible failure, before/after, cost chart); ML/founding engineers need to *trust* it (deterministic ms numbers, human-calibrated judge, honest limitations). The demo order in §9 is engineered for this alternation.

**Current state:** nothing is built. This spec is the only artifact. Hours available: ~33–35 across June 10 evening → June 12 night, plus ~2h demo prep June 13 morning.

**Resources in hand:**
- **Gemini API key** (free tier / student Pro via AI Studio) → this runs the LLM judge. NOTE: Spike's Claude Max and ChatGPT Plus subscriptions are NOT API keys — do not attempt to run the batch judge through them. Claude Code (you) and Codex are build copilots only.
- **Bolna + Cartesia credits: NOT in hand, possibly arriving June 11.** Nothing on the critical path may depend on them (§7.G is the bonus path).
- **Friend:** fluent Telugu/English/Hindi, availability UNCONFIRMED (maybe June 11 evening). Everything involving him is an optional upgrade, never a dependency (see §7.E, §7.F).
- Mac M4, 24GB RAM. Plenty.

**Recovery context (respect quietly, don't lecture):** Spike is days into a sober streak after a relapse; this sprint is deliberately structured as protection — every hour has a target and a commit, no empty time. Two hard gates: (1) substances stay gone; (2) **sleep ~7h/night sits OUTSIDE the 35 hours and is never traded for a feature.** If it's past ~00:30 IST, recommend stopping; never suggest pushing through the night. The demo already works by end of Day 2 — say that back to him if hour 28 feels heavy.

---

## §2. Operating Rules for the Agent

1. **Drive block by block (§5).** At each block start: state the goal, the timebox, and remaining total budget. At each block end: make the git commit+push with the given message, then write one line each for "what now exists" / "what you learned."
2. **Enforce timeboxes ruthlessly.** The A/B loop has a **3-hour hard clock** — at 3h, it ships as-is or converts to the "loop shape" slide (§8). The dashboard has a **90-minute toolchain trigger** — if a Next.js shell isn't rendering JSON within 90 min, drop to themed Streamlit, no second chances.
3. **Refuse scope additions** unless something of equal size is explicitly cut. The §3 cut-list is pre-authorized. New ideas go to `docs/later.md`, not into the sprint.
4. **English-first rule:** the pipeline, gold set, calibration, and charts are English-only this sprint. `language` remains a schema field and `language_match` a rubric dimension (populated `en`). The ONE multilingual artifact is the hero call (§7.E — Tenglish caller × English agent). IndicVoices and full multilingual support are roadmap, not build.
5. **Definition of Done (cannot demo without — protect these above all):**
   - Hero call audio + failure table with hard ms numbers
   - ≥9 public-data calls scored end-to-end with reasons
   - ≥10 DPO pairs in valid TRL JSONL
   - Pilot calibration: ≥40 blind human labels, kappa + 2 disagreement cases (single-human anchor acceptable if friend unavailable — framed honestly)
   - 1 business-value chart
   - Demo script + a recorded fallback clip of the money shot
   Everything else is bonus.
6. **Honesty is a feature.** Every judge score carries a reason + evidence. The hero call is disclosed as a constructed scenario. The A/B is "one closed-loop demonstration, not statistical proof." Limitations get their own doc AND slide. Never let polish drift into overclaiming.
7. This repo (`~/voiceforge`) pushes freely per block — it is separate from Spike's daily-sync vault and its git discipline.

---

## §3. Pre-Authorized Cut List (cut in this order if time attacks)

1. Wavesurfer waveform (garnish — the timestamp table IS the money shot)
2. Bolna live ingest (→ adapter-contract slide)
3. Next.js polish depth (→ themed Streamlit)
4. A/B live re-run (→ loop-shape slide, after its 3h clock)
5. Sample expansion beyond 9 calls
6. Cross-cut chart (keep the business-value chart — that one survives)
7. Second human labeler (→ single-anchor framing)
NEVER cut: hero call, signals math, judge-with-reasons, DPO export, pilot calibration, fallback recording.

---

## §4. The Money Shot & The Two Lines

**The 20-second sequence everything serves** (open AND close the demo with it):
1. **Audio plays aloud.** English TTS agent talks over a hesitant Tenglish caller mid-answer (barge-in), and elsewhere leaves a ~1.6s dead-air gap. The room *hears* it.
2. **The failure table flags the exact timestamps with deterministic numbers:** `0:14 — agent barge-in — 800ms overlap` · `0:41 — response latency — 1,620ms gap`. Measurements, not vibe scores.
3. **The kicker:** that failure becomes a **(chosen, rejected) DPO pair on screen** — rejected = what the agent said; chosen = the corrected turn — one JSONL line, training-ready.

Pain → hard number → why → better response → preference pair → calibration. Zero research vocabulary in the first 30 seconds (no kappa, no DPO, no dataset names until the room has heard the failure).

**The two locked lines:**
- Engineer line: **"VoiceForge judges the conversation trace, not just the transcript"** — language, timing, overlap, task outcome, cost, repair quality. Transcript-only evals structurally miss the voice-native failures.
- Close: **"Most voice-agent demos stop when the call ends. VoiceForge starts there — it turns the call into evals, failures, cost signals, and the next training example."**

---

## §5. Build Schedule (block by block, real calendar)

### DAY 1 — Tonight, June 10 (~4h)

**Block 0 (1h) — Skeleton.**
Repo + tree (§6) · 5 schemas (§7.A) · `rubric.yaml` v0 (§7.B) · Gemini API key created in AI Studio + one smoke-test judge call from Python · README thesis ¶ · `docs/limitations.md` started (write it first; it sets the honest tone).
→ push: `"skeleton: tree + 5 schemas + rubric.yaml + gemini smoke test + limitations"`

**Block 1 (2.5–3h) — Hero call, solo (§7.E).**
Script (~90–120s, EN agent × Tenglish caller, one ambiguous locality answer, one >1.5s hesitation pause, agent commits: one barge-in + one long dead-air) · TTS the agent lines (edge-tts/Gemini TTS now; Cartesia re-voice later if credits) · record caller lines on phone/laptop · assemble in Audacity/ffmpeg with a deliberate ~800ms overlap and ~1.6s gap · export WAV + **write `turns.json` straight from the editing timeline (assembly = ground-truth timestamps; no ASR, no diarization)** · run `signals.py` (§7.C) on it → the failure table prints with real ms numbers.
→ push: `"hero call: audio + ground-truth turns + FTO failure table (barge-in 800ms, gap 1.6s)"`
**Milestone: the money-shot DATA exists on night one.** Sleep by ~00:30.

### DAY 2 — June 11 (~13h)

**Block 2 (2h) — Money-shot surface.**
Simplest page that works: `<audio>` element + clickable failure-table rows that seek (`audio.currentTime = t`) + transcript turn list. Static HTML or a bare Next.js page — whichever renders fastest. NO waveform library yet.
→ push: `"money shot v0: audio + clickable timestamp table seeking"`
**Milestone: the demo exists end-to-end on one call by ~hour 7. Nothing after this can kill it.**

**Block 3 (4h) — Pipeline over real public calls.**
Download SpokenWOZ train+dev (§7.D) · normalize 9–12 calls (+2–3 AMI calls for genuine overlap if trivial) into the schema · run signals across all · wire the Gemini judge (§7.B): JSON output, temperature 0, every score = {score, reason, evidence_turn_ids}, responses cached to disk · emit `out/calls.json` + `out/call_<id>.json`.
→ push: `"pipeline: 9-12 SpokenWOZ calls normalized -> signals + judged scorecards (reasons+evidence)"`

**Block 4 (1h) — Blind labels, human #1.**
Spike labels 40–60 calls on ONE binary dimension (task success OR acceptable-voice-behavior — pick one, stay fast, ~1–2 min each) **before viewing any judge output on those calls**. Stratified across stress profiles, aligned by call id. Save `eval/labels_spike.csv`.
→ push: `"calibration: 40-60 blind human labels (rater 1)"`

**Block 5 (2h) — DPO export (§7.F).**
For each failed/suboptimal call: one (chosen, rejected) pair where the ONLY meaningful difference is the detected voice-failure (over-talk → shorter turn; ignored pause → wait+clarify; language-mismatch → in-language reply; missed field → clean re-ask). 10–20 pairs → `out/queue.jsonl` (TRL conversational) + OpenAI-format mirror via the 3-line mapper.
→ push: `"dpo: 10-20 preference pairs (TRL + OpenAI), failure-axis-only diffs"`

**Evening, IF friend materializes (1–2h, all optional):** friend blind-labels the same set (`labels_friend.csv` → human-human ceiling) · optionally re-record the caller side live for a more natural hero-call take · if Cartesia credits landed, re-voice the agent side with Sonic 3.5 (sponsor-on-brand).
→ push: `"calibration rater 2 + hero call upgrade"` *(skip without guilt if he doesn't show)*

Sleep by ~00:30. **End of Day 2: spine + artifact + labels all exist.**

### DAY 3 — June 12 (~13h, submission tonight)

**Block 6 (3h HARD CLOCK) — A/B loop (§8).**
v1 system prompt = the flawed agent. VoiceForge's detected failures → generate v2 prompt/policy. Re-run the SAME user turns through Gemini-as-agent under v2 (text turns; TTS only if trivial). Re-score both with the same pipeline. Before/after panel: turns ↓, failures ↓, score ↑. **At 3h, ship whatever exists or convert to the loop-shape slide. No extensions.**
→ push: `"a/b: v1 vs v2 same-scenario replay, rescored (or: loop-shape slide)"`

**Block 7 (1.5h) — Kappa (§7.F).**
`cohen_kappa_score` judge-vs-Spike (+ judge-vs-friend and human-vs-human if rater 2 exists) · bootstrap 95% CI · confusion matrix · pull the **2 disagreement cases** (these go ON a slide). Framing locked: **"pilot calibration"** — never claim "substantial agreement" unless the number + CI genuinely land in 0.61–0.80.
→ push: `"calibration: pilot kappa + CI + confusion matrix + 2 disagreement cases"`

**Block 8 (2h) — Charts.**
**Business-value chart (the founder magnet):** calls with voice failures → lower task completion AND higher estimated cost per successful call (cost = turns × per-turn LLM/TTS/STT estimate; label "estimated, prototype data"). Cross-cut by stress profile (clean / pause-heavy / interruption / ambiguous); hero call appears as an honest n=1 language row. Emit `out/analytics.json` + chart images.
→ push: `"analytics: business-value chart + stress-profile cross-cut"`

**Block 9 (3h) — Dashboard assembly (§7.H).**
Next.js + shadcn + Tremor, static over `out/*.json`: shell → call list → call detail (the Block-2 player, now styled) → analytics → improvement queue (JSONL drawer). **90-min trigger:** shell not rendering JSON → themed Streamlit, move on. Theme: zinc-950 + one accent, Geist font, p-6 cards. Wavesurfer ONLY if everything through Block 11 is done.
→ push: `"dashboard: list/detail/analytics/queue over static json"`

**Block 10 (1h) — Sponsor bonus.**
Credits landed → ingest 1 Bolna call (§7.G: executions list → `/log` → recording; timing from `/log` diffs, NEVER the scrubbed transcript) and run it through the same pipeline. No credits → the **adapter-contract slide**: `Bolna logs / Cartesia audio / any transcript → VoiceForge normalized schema`. Provider-neutral, sponsor-compatible.
→ push: `"bolna ingest bonus | adapter-contract slide"`

**Block 11 (1.5h) — Package + SUBMIT.**
Slides (§9 order) · screenshots · **screen-record the money shot as the fallback clip (real catch, never staged)** · limitations slide (judge biases, n=1 A/B, constructed hero call, estimated costs) · submit per Luma instructions · FREEZE.
→ push: `"demo package: slides + script + fallback recording — SUBMITTED + FROZEN"`

Sleep ~7h. **June 13:** 1–2h rehearsal (3-min + 7-min, out loud), glance at the cite-card (§10), walk in slept.

---

## §6. Repo Tree

```
voiceforge/
├── SPEC.md                          # this file
├── README.md                        # thesis, architecture, demo, limitations, future
├── docs/    {architecture,demo-script,limitations,later}.md
├── rubric.yaml                      # eval dimensions: weights, type, thresholds — THE config
├── schemas/ {call_log,task_outcome,scorecard,cost,improvement_example}.md
├── data/    spokenwoz/  ami/  hero/  normalized/
├── pipeline/ normalize.py signals.py judge.py score.py dpo_export.py crosscut.py costs.py
├── eval/    labels_spike.csv  labels_friend.csv  kappa.py
├── out/     calls.json  call_<id>.json  analytics.json  queue.jsonl  queue_openai.jsonl
├── web/                             # Next.js (or streamlit_app.py fallback) — reads ../out
└── reports/ charts/  screenshots/  fallback_demo.mp4
```

---

## §7. Technical Appendix

### A. The 5 Schemas (keep general — no hardcoded vertical)
- **call_log:** `call_id, source(spokenwoz|ami|hero|bolna), language, stress_profile(clean|pause_heavy|interruption|ambiguous|kb_gap), workflow_type, turns[{turn_id, speaker(user|agent), text, start_ms, end_ms}], audio_path, metadata`
- **task_outcome:** `call_id, task_completed(bool), required_fields[{name, captured, value}], escalation_needed, confidence`
- **scorecard:** `call_id, dimensions[{name, type(deterministic|judge), score, reason, evidence_turn_ids[]}], overall`
- **cost:** `call_id, duration_s, turn_count, est_llm_calls, est_cost_total, est_cost_per_success_note("estimated, prototype")`
- **improvement_example:** `call_id, failure_dimension, rejected_turn, chosen_turn, reason, quality_delta, needs_human_review(bool)`

### B. rubric.yaml + the Judge
```yaml
dimensions:
  barge_in:        {type: deterministic, weight: 0.2, threshold_overlap_ms: 100}
  latency_gap:     {type: deterministic, weight: 0.2, laggy_ms: 800}
  task_completion: {type: deterministic, weight: 0.2}      # from required-field checklist
  language_match:  {type: judge, weight: 0.15}             # the multilingual slot, en for now
  faithfulness:    {type: judge, weight: 0.15}
  repair_quality:  {type: judge, weight: 0.10}             # clarification handling
```
Pipeline reads ONLY this file for weights/dimensions → live-editable on demo day ("for you, handoff matters more? watch:" edit → rerun → dashboard updates). Judge = **Gemini Flash** (AI Studio key), temperature 0, JSON mode, prompt returns `{score, reason, evidence_turn_ids}` per judge-dimension; cache every response to `data/.judge_cache/` keyed by (call_id, dimension, prompt_hash) so reruns are free and idempotent. Disclose Gemini as the judge.

### C. Signal Math (FTO — the deterministic core)
```python
def turn_metrics(turns):                       # {turn_id, speaker, start_ms, end_ms}
    turns = sorted(turns, key=lambda t: t["start_ms"])
    out = []
    for a, b in zip(turns, turns[1:]):
        fto = b["start_ms"] - a["end_ms"]      # negative = overlap, positive = gap
        out.append({"prev_spk": a["speaker"], "next_spk": b["speaker"], "at_ms": b["start_ms"],
                    "fto_ms": fto, "overlap_ms": max(0, -fto), "gap_ms": max(0, fto)})
    return out
```
**Barge-in** = `overlap_ms > 100` (≤100 = backchannel, ignore); track agent-interrupts-user and user-interrupts-agent SEPARATELY. **Latency** = `gap_ms` on user→agent (≤300 snappy · ≤800 ok · >800 laggy). Report median + p90, never mean. Same units, same clock per call. Single timestamps (no end_ms) → latency only, NEVER fake overlap.

### D. Data
- **SpokenWOZ** (spokenwoz.github.io, train+dev): real two-party task calls, word-level timestamps, separated channels. English. CC BY-NC (fine for hackathon eval; flag before commercial). Synthesize turn bounds from word times (first word start → last word end per same-speaker run). Few real barge-ins (protocol) → latency-rich.
- **AMI** (HF `edinburghcstr/ami`, CC BY 4.0, one-line load): real overlap (~20%) for genuine barge-in rows. Meetings-domain — use 2–3 calls, narrowly.
- **Roadmap only:** IndicVoices (gated; timestamps undocumented), multilingual expansion, real customer-call corpora. One README line.

### E. Hero Call (solo recipe — no friend, no diarization)
1. Script ~90–120s: service/appointment workflow. Caller = Spike, **Tenglish** (code-switching), hesitant, one ambiguous locality answer, one >1.5s thinking pause. Agent = **English TTS** — commits exactly two sins: barges in during the pause, and one >1.5s dead-air before a response. (EN-agent × Tenglish-caller = the real deployment pattern; language-mismatch is itself a rubric dimension.)
2. TTS agent lines (edge-tts / Gemini TTS today; **re-voice with Cartesia Sonic 3.5 if credits land** — sponsor flagship, on-brand).
3. Record caller lines (phone mic, quiet room). Assemble in Audacity/ffmpeg: place clips, create ~800ms overlap + ~1.6s gap deliberately. Export mono WAV.
4. **Write `turns.json` from the editing timeline — assembly IS ground truth.** Zero ASR/diarization on the critical path.
5. Disclosure (slide + if asked): "constructed demo scenario; timestamps from assembly; validity comes from the public-data calibration." Friend tomorrow = optional naturalness upgrade only.

### F. Calibration (pilot) + DPO
**Kappa:** labels blind-before-judge, id-aligned, one binary dimension, 40 floor / 60 target.
```python
from sklearn.metrics import cohen_kappa_score, confusion_matrix
k = cohen_kappa_score(human, judge)            # same items, same order
# bootstrap CI: resample item indices 1000x -> 2.5/97.5 percentiles
```
Landis-Koch bands; claim "substantial" ONLY if number+CI land 0.61–0.80; otherwise report honestly ("moderate, directional"). Show the 2 disagreement cases proudly — that's the credibility move. Friend absent → "single-human pilot anchor; second rater planned" (honest, acceptable). **The mature sentence:** *"I'm not pretending this judge is magic; I tested where it agrees with humans and where it fails."*

**DPO JSONL** (TRL conversational; author once, map to OpenAI):
```json
{"prompt":[{"role":"system","content":"Voice agent for appointment booking. Replies under 2 sentences. Never speak while the caller is mid-answer."},{"role":"user","content":"haan area... ante... Madhapur side anukunta, near the er... metro station"}],"chosen":[{"role":"assistant","content":"Got it — Madhapur, near the metro station. Morning or evening slot work better?"}],"rejected":[{"role":"assistant","content":"I need your complete address with pincode landmark and door number before we can proceed any further with this booking request, please provide all details now."}]}
```
The ONLY diff = the detected failure axis (over-talk/ignored-hesitation vs short acknowledge+advance). Mapper: `{"input":{"messages":p},"preferred_output":c,"non_preferred_output":r}` → `queue_openai.jsonl`.

### G. Bolna Bonus Path (only if credits land — never critical)
Auth `Bearer <key>`, base `https://api.bolna.ai`. List: `GET /v2/agent/{agent_id}/executions?page_size=50` (read, free — transcript + `telephony_data.recording_url` + cost inline). Detail: `GET /executions/{id}`. **Timing: `GET /executions/{id}/log` ONLY** — diff `created_at` across component events (transcriber-response → user turn; llm/synthesizer → agent turn). **Traps:** top-level transcript = single string, no roles, no timing, and "precise transcript" mode actively DELETES interrupted content (barge-in scrubbed); `post_dial_delay`/`ring_duration` = PSTN setup, NOT turn latency; cost aggregate-only. Download recordings immediately (signed URLs expire).

### H. Dashboard
Doctrine: **timestamp table first, waveform last.** Block 2's player is the demo; Block 9 styles it. Next.js (App Router) + Tailwind + shadcn/ui + Tremor, static read-only over `out/*.json`, audio in `public/` — no backend/DB/auth. v0.dev for scaffolds; theme: zinc-950 + one saturated accent + Geist (next/font) + p-6 cards / gap-6 / border-border / shadow-sm. **90-min trigger → themed Streamlit** (dark theme.toml + Plotly; audio + timestamp-button list). Wavesurfer (@wavesurfer/react + Regions) only if Blocks 0–11 are ALL done.

---

## §8. A/B Loop (boxed) — the honesty framing, verbatim

Build: v1 flawed prompt → VoiceForge detects failures → v2 prompt generated from them → SAME user turns re-run through Gemini-as-agent → re-scored by the same pipeline → before/after panel (turns ↓ failures ↓ score ↑). **3-hour hard clock, one scenario only.**

Say exactly this: *"This is one scenario replay, not statistical evidence. VoiceForge caught the failure, proposed the fix, and the same evaluator scored v2 higher. The point is the closed-loop shape — production would require more logs, human review, and offline training. At scale, this loop is the dataset."* Founder-sexy, engineer-safe.

---

## §9. Demo Script (3-min spine · 7-min adds dashboard+charts)

Emotional order locked: **pain → measurement → correction → dataset → scale.** No research vocabulary in the first 30s.

1. **(15s)** "Voice agents demo great and fail quietly in production. Teams can't see why calls fail, what they cost, or how failures become the next version. Listen to this."
2. **(45s) MONEY SHOT:** hero call plays → room hears the barge-in → table flags `0:14 · 800ms overlap` + `0:41 · 1,620ms gap` → scorecard reason → corrected response → **the DPO pair appears.** "Every call is unlabeled preference data. We label it automatically."
3. **(30s) A/B:** before/after panel + the §8 honesty line. (Or loop-shape slide.)
4. **(30s) Trust:** "It's not vibes — deterministic timing signals, plus an LLM judge **pilot-calibrated** against blind human labels: here's the agreement, and here are two cases where the judge was *wrong*." (engineer hook)
5. **(30s) Scale:** dashboard sweep + **business-value chart** — "calls with voice failures complete less and cost more per success." (founder hook) + adapter-contract slide: provider-neutral, sponsor-compatible.
6. **(15s)** "VoiceForge judges the **conversation trace**, not just the transcript. Most demos stop when the call ends — VoiceForge starts there: evals, failures, cost signals, and the next training example." 
7. Q&A pivots: §10 cite-card + competitive one-liners.

**Competitive one-liners:** Coval/Hamming/Cekura → "test harnesses tell you *what* failed; VoiceForge mines the same calls for *improvement data* — the DPO pairs they don't produce." · Roark → "replays calls to *test* you; VoiceForge mines calls to *train* you." · Leaping AI → "closes the loop but locks you to their platform, prompt-level only; VoiceForge is neutral and outputs portable weight-level data you own." · Langfuse/Braintrust → "great plumbing, text-first and voice-blind; my preference label IS the voice signal."

**Monday networking:** open with a question, not a pitch — "deploying voice across languages/regions, what's been the harder bottleneck: latency, turn-taking, accent robustness, task-completion evals, or structured feedback from real calls?" Then, only if it opens: the one-liner + repo. Calm. The artifact speaks first.

---

## §10. Citation Card (all verified real — June 2026; click links before citing)

| Reference | Cite precisely |
|---|---|
| VoiceAgentBench (arXiv:2510.07978, Krutrim) | "English + **six Indic languages**", "**6,000+** spoken queries", **preprint**. Motivates the multilingual roadmap. |
| WildASR (arXiv:2603.25727) | Benchmark name, NOT paper title — paper = *"Back to Basics: Revisiting ASR in the Age of Voice Agents."* EN/ZH/JA/KO. |
| τ-Voice (arXiv:2603.13686, Sierra+Princeton) | Killer stat: voice agents retain **~30–45% of text capability** (31–51% clean vs ~85% text). Code = `sierra-research/tau2-bench`. |
| LTS-VoiceAgent (arXiv:2601.19952, Meituan) | "Thinker–Speaker async reasoning." Preprint. |
| Bolna docs | **Dispositions power Extractions** (nested, not two features). API host `api.bolna.ai`. |
| Cartesia Sonic 3.5 (sponsor!) | **42 languages · 82ms** end-to-end TTFA. Don't cite "~40ms Turbo" (unverified). "#1 naturalness" = their/Artificial-Analysis claim. |
| ElevenLabs | `/docs/eleven-agents/...` path. Don't attribute "sub-500ms first-turn" to them. |
| Voc-a-thon | Judges not publicly named; no published prize figure. Don't invent either. |

---

## Version Log
- v1–v2 (Jun 9): recon + first hour-by-hour.
- **v3 (Jun 10, FINAL):** three-reviewer convergence. Locks: timestamp-table-first · A/B 3h clock · rubric.yaml day-one · business-value chart · pilot calibration fixed-block/flex-size · **English-first, language-as-dimension** · hero call solo-buildable (TTS agent × Tenglish caller, assembly = ground-truth timestamps) · friend fully optional · rewritten as a cold-start handoff for a fresh Claude Code session.
