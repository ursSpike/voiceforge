# Learning curriculum — DRAFT v1 for discussion (mark this file up in Cursor)

Audience: one student. Strong daily Python/numpy/scientific-computing (protein docking,
benchmarking at Fujitsu). Assume ZERO on: ML/DL practice, NLP, LLMs, audio, speech, RL,
voice agents, eval methodology, post-training. IIT-KGP CSE math exists but is rusty —
re-derive everything, fast, never skip a step silently.

## Global design rules (apply to every book)
1. **From absolute zero**: every term defined at first use; no "as you know".
2. **Predict → run → read the plot → explain back.** Every plot comes with a "what do you
   see / what would change if…" prompt. No cell runs un-predicted.
3. **Real anchors**: wherever possible cells run on OUR artifacts (hero call, 11-call pool,
   rubric, judge cache). Toy data only where the real thing is too big to see through.
4. Each book: 20–40 min · one concept cluster · ends with 3–5 self-checks (answers collapsed)
   + one "gotcha" an expert would probe.
5. Spoon-feeding is a feature. Repetition across books is deliberate (spaced re-encounter).

## The books

### Part A — Bedrock statistics (fast lane for you, but complete)
- **A1 · Distributions, tails, and why means lie** — from "what is a histogram" to reading
  skewed latency data; mean/median/p90 on real response gaps. *(anchor: corpus gap data)*
- **A2 · Uncertainty from scratch** — sampling error, what a confidence interval actually
  claims, bootstrap built by hand, watching CIs shrink with n. *(anchor: used later for kappa)*
- **A3 · Two measurers, one truth** — comparing raters/instruments; raw agreement, chance
  agreement, Cohen's kappa derived by hand; prevalence paradox. *(anchor: judge-vs-human, but
  taught generic — same math as replicate agreement in any lab)*

### Part B — Machine learning from zero (only what this lane needs)
- **B1 · What "learning" is** — loss, gradient, learning rate; fit a line by gradient descent
  in raw numpy; convergence plots; divergence when lr too big.
- **B2 · Classification end-to-end** — logits → softmax → cross-entropy; train a tiny 2-feature
  classifier; decision boundary plots; train/val split; overfitting seen with eyes.
- **B3 · Words as vectors** — one-hot → co-occurrence → embeddings; cosine similarity;
  PCA plot of a tiny corpus; why "meaning as geometry" unlocked NLP.
- **B4 · A neural net in 100 lines** — MLP forward/backward in numpy on B2's data; depth vs
  width; why DL scaled. *(no frameworks — concepts only; frameworks are a tool decision later)*

### Part C — Language models and LLMs (the biggest gap, taken slowly)
- **C1 · Language modeling = next-token prediction** — build a character/word Markov model on a
  small corpus; SAMPLE from it; perplexity intuition; temperature implemented by hand on logits
  → why temp 0 = deterministic argmax (this is literally our judge setting).
- **C2 · Tokens, context windows, cost** — what a token is (BPE walkthrough by example);
  count tokens via the real Gemini API; context window limits; why prompts cost money.
- **C3 · From autocomplete to assistant** — pretraining vs instruction tuning (SFT) vs RLHF at
  concept level; chat format (system/user/assistant role arrays — the exact shape inside our
  DPO files); experiment: same question under 3 system prompts, watch behavior change. *(live API)*
- **C4 · Sampling, determinism, structured output** — temp/top-p experiments (same prompt ×10 at
  temp 0 vs 1, diversity plotted); JSON mode; why eval pipelines pin temperature 0.
- **C5 · How LLMs fail** — hallucination, sycophancy, verbosity preference, position bias —
  each elicited live with a tiny designed experiment. *(this is judge-bias bedrock)*

### Part D — Audio and speech from zero
- **D1 · Sound as numbers** — sample rate, amplitude, frames; load the hero WAV; zoom from 90s
  to 10ms; hear it vs see it; RMS energy. *(anchor: your own voice)*
- **D2 · "Is someone talking?"** — energy VAD built by hand; endpointing; the hold-time knife
  edge; reproduce the booth's auto-advance; watch it cut your t2 pause when tuned wrong.
- **D3 · How machines hear: spectrograms and ASR** — frequencies without scary math; spectrogram
  of the hero call; why accents/code-switching/garbled entities happen; **WER computed from
  scratch via edit distance** (a DP kata for you) on a real garbled SpokenWOZ line.
- **D4 · Making machines speak: TTS and the latency budget** — TTS pipeline conceptually;
  synthesize lines live with edge-tts; TTFA measured crudely; assemble the full
  STT→LLM→TTS per-turn latency budget; where 82ms TTS claims fit.

### Part E — Conversation science and voice agents
- **E1 · Turn-taking: the physics of conversation** — floors, handoffs, FTO; barge-in vs
  backchannel; the 100ms and 800ms lines; hero-call timeline plot, sins found by eye then by code.
- **E2 · The corpus lab** — all 11 calls; stress profiles as workload classes; stratified
  selection (and why it isn't cherry-picking); cross-cut tables; dirty-data honesty
  (9.4s "overlaps", missing end_ms rule).
- **E3 · Anatomy of a voice agent** — the full relay; endpointing tradeoff; which failure
  classes originate where; fix depth: config vs prompt vs weights (one table you'll reuse
  in every hackathon conversation).

### Part F — Evals and judging (the lane itself)
- **F1 · Deterministic first** — measurement vs judgment doctrine; re-derive the failure table
  from raw turns yourself (rebuild signals.py's core in 20 lines).
- **F2 · LLM-as-judge** — why, the contract (temp 0 / JSON / score+reason+evidence), anchored
  scales vs 1–10, caching; judge real pool calls; break the rubric deliberately and read the wreckage.
- **F3 · Calibrating the judge** — blind protocol; kappa + bootstrap CI (now trivial — A2/A3
  did the math); confusion matrix; disagreement mining as the credibility move; honest-claim rules.
- **F4 · Outcomes and money** — required-fields checklists from SpokenWOZ goals; task success;
  estimated cost per successful call; build a first business-value chart from our pool.
  *(directly feeds Build Blocks 4/7/8)*

### Part G — Post-training and improvement data
- **G1 · The training ladder** — pretraining → SFT → preference tuning; what data each stage
  eats; where a (chosen, rejected) pair enters the machinery.
- **G2 · DPO from first principles** — Bradley–Terry "probability A beats B" on toy numbers;
  the DPO objective computed BY HAND in numpy on toy log-probs; β as the leash to the reference
  model; loss-vs-margin plots. No GPU, no framework, fully transparent.
- **G3 · Authoring improvement data** — single-axis rule (your ablation instinct); trainable vs
  config-fixable failures; TRL + OpenAI formats; author real pairs from the pool; needs_human_review.

### Part H — The room
- **H1 · The industry map and honest claims** — Bolna, Cartesia, Coval/Hamming/Cekura, Roark,
  Langfuse/Braintrust, Leaping; the verified cite-card; the two locked lines; Q&A playbook.
- **H2 · Capstone exam** — the full oral quiz (Claude grades, harshly); "explain VoiceForge to a
  founder / an ML engineer / your mom" drill; teach-back of the three hardest concepts.

**Count: 28.**

## Sequencing against the hackathon (the honest arithmetic)
28 books ≈ 12–15 study hours — that does NOT fit before Saturday alongside ~20h of build.
Two tracks:
- **Critical core before demo day (≈ 8–9 books, ~5h):** D1 → D2 → E1 → E2 → E3 → F1 → F2 → F3
  (+ G3 light). These make you fluent in everything the demo claims.
- **Full foundations (A, B, C, D3-4, G1-2, F4 deep):** the permanent asset; continue after
  June 13 at leisure. The existing 6 notebooks get absorbed/expanded into E1/E2/F2/F3/G3/H1 —
  nothing thrown away.

## Decisions (Spike, Jun 11 ~00:20)
1. **Tools:** has RUN PyTorch training without understanding internals; matplotlib/pandas
   effectively new. → Every first-of-its-kind plot gets a "how to read this" walkthrough;
   NO pandas anywhere (dicts/lists/numpy only); Part B stays framework-free, and B4 ends by
   connecting the numpy net to "what PyTorch was automating for you at work".
2. **Math:** one refresher cell for derivatives/chain rule, then move.
3. **Audio:** read-level on spectrograms/FFT (use, don't derive).
4. **Order: BUILD SET ASIDE ENTIRELY for now.** Strict foundations order A1 → H2. The goal is
   genuinely reaching do-this-project-for-real level, not demo cramming. Build resumes only
   when Spike says so (docs/RESUME.md unchanged, still accurate). Copilot flags the calendar
   decision point — by Jun 12 ~09:00 IST the remaining Definition-of-Done core (~10h: judge+score,
   blind labels, DPO export, kappa, business chart, package+submit) must either start or be
   consciously dropped — Spike's call, made explicit, no sleepwalking into it.
