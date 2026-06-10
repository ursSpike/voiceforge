export const meta = {
  name: 'voiceforge-university',
  description: 'Build 35 beginner-proof training notebooks (P01-P04, 00-30) in parallel; each gated by execute + programmatic audit + independent beginner-brutality review + conditional fix',
  phases: [
    { title: 'Build' },
    { title: 'Review' },
    { title: 'Fix' },
    { title: 'Manifest' },
  ],
}

// ---- shared context handed to every agent (the cast + harness live in _BUILD_SPEC.md) ----
const SPEC = 'notebooks/_BUILD_SPEC.md'

const BOOKS = [
  // PREREQS — build the recurring cast A/B/C BY HAND (that's the lesson)
  { id: 'P01', file: 'P01_python_objects_for_call_logs', title: 'Python objects for call logs',
    concept: 'nested Python objects (dict/list/JSON) are the natural shape of a call',
    prev: 'P00 the learning ritual', next: 'P02 tables',
    clean: 'A call log is a structured object: lists hold sequences, dictionaries hold facts, and nesting lets one call contain many turns.',
    cover: 'variables/str/num/bool; lists; dicts; nested dict-of-lists; JSON-like; why a call is naturally nested; BUILD cast A/B/C by hand as nested call_log objects; index/walk into them',
    data: 'toy + build cast by hand' },
  { id: 'P02', file: 'P02_tables_and_pandas', title: 'Tables and pandas',
    concept: 'rows are things, columns are facts; a DataFrame from a list of call dicts',
    prev: 'P01 objects', next: 'P03 plots',
    clean: 'A DataFrame turns a pile of call objects into rows I can filter, group, and count.',
    cover: 'list-of-dicts; one row = one call; manual loop count FIRST, then pandas; select a column; filter rows; groupby language and count successes/failures',
    data: 'toy + cast' },
  { id: 'P03', file: 'P03_basic_plots_for_evals', title: 'Basic plots for evals',
    concept: 'reading and making bar / timeline / histogram, and what a chart does NOT license',
    prev: 'P02 tables', next: 'P04 debugging',
    clean: 'A chart is an argument; I must be able to say what its axes are and what claim it does and does not license.',
    cover: 'the 4-question chart ritual; bar (counts); timeline (turns as bars over time — preview of call C overlap); histogram (a distribution); a misleading-chart trap',
    data: 'toy + cast turns' },
  { id: 'P04', file: 'P04_debugging_confusion', title: 'Debugging confusion',
    concept: 'the debug ritual: print the input, print the intermediate, shrink the example',
    prev: 'P03 plots', next: 'book 00',
    clean: 'When output surprises me, I print the input, print the intermediate, and shrink the example — I do not guess.',
    cover: 'a wrong-number bug; read a traceback bottom-up; the 3-step ritual; stale-state recap; the silent-wrongness trap',
    data: 'toy' },

  // WAVE 2 — survival vocabulary
  { id: '00', file: '00_what_is_voiceforge', title: 'What is VoiceForge?',
    concept: 'VoiceForge is the layer AFTER the call: messy call in, five structured artifacts out',
    prev: 'P04 debugging', next: '01 call log',
    clean: 'VoiceForge is the layer after the call ends.',
    cover: 'the thesis (most demos stop when the call ends); ONE tiny fake call in -> 5 outputs conceptually (outcome, scorecard, failure tags, cost, improvement pair); why a voice-AI company needs this; it is NOT a voice bot',
    data: 'toy fake call' },
  { id: '01', file: '01_what_is_a_call_log', title: 'What is a call log?',
    concept: 'trace (timed turns) vs transcript (text only)',
    prev: '00 what is VoiceForge', next: '02 schemas',
    clean: 'We judge the conversation trace, not just the transcript.',
    cover: 'turns, speakers, timestamps, metadata; load cast A/B/C and print as turns; show a transcript loses timing/overlap; reference real data/hero/turns.json',
    data: 'cast + data/hero/turns.json' },
  { id: '02', file: '02_json_schemas_data_contracts', title: 'JSON, schemas, data contracts',
    concept: 'a schema is a data contract; normalize an ugly dict into call_log',
    prev: '01 call log', next: '03 pandas for calls',
    clean: 'One schema in, every tool downstream works.',
    cover: 'what JSON is; what a schema is; take an ugly inconsistent dict -> clean normalized call_log; the field table; why structure is non-negotiable; reference schemas/call_log.md and pipeline/normalize.py',
    data: 'toy ugly dict + schemas/call_log.md' },
  { id: '03', file: '03_pandas_for_call_data', title: 'Python/pandas for call data',
    concept: 'real calls as rows; group and count outcomes at scale',
    prev: '02 schemas', next: '04 timing',
    clean: 'A DataFrame lets me treat calls like benchmark rows.',
    cover: 'load data/normalized/*.json into a DataFrame; one row = one call; group by stress_profile and by source; count; the benchmark-row analogy from his Fujitsu world',
    data: 'data/normalized/*.json (11 real calls)' },
  { id: '04', file: '04_turns_gaps_overlap_latency', title: 'Turns, gaps, overlap, latency',
    concept: 'FTO per handoff -> gap/overlap/barge-in/latency, p50/p90, thresholds',
    prev: '03 pandas', next: '05 voice stack',
    clean: 'Voice failures are measurable in milliseconds, not just judgeable from text.',
    cover: 'two turns -> compute gap; nudge a timestamp until it becomes overlap; barge-in vs backchannel (100ms line); latency >800ms; CHANGE the threshold -> more calls flagged; p50/p90 vs mean trap; use pipeline/signals.py turn_metrics on data/hero/turns.json (real 0:18 barge-in 800ms, 0:53 gap 1620ms). THE money-shot book — make it long and careful',
    data: 'data/hero/turns.json + signals.py' },
  { id: '05', file: '05_asr_llm_tts_voice_stack', title: 'ASR / LLM / TTS — the voice stack',
    concept: 'the three-model relay and where the latency budget is spent',
    prev: '04 timing', next: '06 task success',
    clean: 'Every turn is a three-model relay under a time budget.',
    cover: 'simulate audio->ASR text->LLM->TTS->logs with plain strings; where ms accrue each turn; TTFA; Cartesia Sonic 82ms context; do NOT teach model internals — vocabulary and the relay only',
    data: 'string simulation' },
  { id: '06', file: '06_task_success', title: 'Task success',
    concept: 'required-fields checklist; a polite call that still failed',
    prev: '05 voice stack', next: '07 failure tags',
    clean: 'A call can sound great and still not do the job.',
    cover: 'define required fields (area/time/phone/confirm); check capture on cast A/B/C; field-capture rate; task_completed bool; reference schemas/task_outcome.md',
    data: 'cast' },
  { id: '07', file: '07_failure_tags_stress_profiles', title: 'Failure tags & stress profiles',
    concept: 'failure taxonomy + scenario stress classes; scenario != performance',
    prev: '06 task success', next: '08 cost',
    clean: 'Raw chaos becomes engineering signal through categories.',
    cover: 'tag toy calls (language mismatch / interruption / kb gap / too many turns); stress profile classes (clean/pause_heavy/interruption); a failure-distribution bar chart; the clean-call-that-still-failed (scenario vs performance) lesson',
    data: 'data/normalized/*.json' },
  { id: '08', file: '08_cost_per_successful_call', title: 'Cost per successful call',
    concept: 'cost = turns x unit price; failures shrink the denominator',
    prev: '07 failure tags', next: '09 language',
    clean: 'Voice quality is a money number, not a feelings number.',
    cover: 'assign toy unit costs (LLM/TTS/STT per turn); cost per call; cost per SUCCESSFUL call; clean vs messy comparison; always label "estimated, prototype"',
    data: 'pool + toy unit costs' },
  { id: '09', file: '09_language_conditions', title: 'Language conditions',
    concept: 'language is an eval dimension, not a feature checkbox',
    prev: '08 cost', next: '10 judge',
    clean: 'Multilinguality is an eval dimension, not a checkbox.',
    cover: 'same task in EN vs Hinglish vs Tenglish (cast A/B/C); success and turn-count by language; code-switching; why English-trained stacks degrade on it',
    data: 'cast' },

  // WAVE 3 — measurement engine
  { id: '10', file: '10_llm_as_judge_from_zero', title: 'LLM-as-judge from zero',
    concept: 'a judge reads a transcript and returns a structured score; the reliability contract',
    prev: '09 language', next: '11 evidence',
    clean: 'A judge you can rerun and get the same answer is an instrument; anything else is a mood.',
    cover: 'a FAKE hand-written judge first (just a function returning a score); then the real Gemini judge via pipeline/judge.py (temperature 0, JSON, disk cache); why determinism+caching; disclose the judge. IMPORTANT: any live call must be wrapped so run_nb.py passes WITHOUT network — try/except around the live call with a cached/canned fallback',
    data: 'a pool call + pipeline/judge.py (guarded)' },
  { id: '11', file: '11_evidence_based_scoring', title: 'Evidence-based scoring',
    concept: 'no naked scores — every score carries a reason and evidence turn ids',
    prev: '10 judge', next: '12 calibration',
    clean: 'A score you cannot audit is a vibe.',
    cover: 'a bad output (quality: 4) vs a good one (score + reason + evidence_turn_ids); falsifiability — can you check the reason against the transcript; the scorecard schema (schemas/scorecard.md)',
    data: 'toy + cast' },
  { id: '12', file: '12_calibration_why_human_labels', title: 'Calibration: why human labels',
    concept: 'the circularity problem; blind labels break the circle',
    prev: '11 evidence', next: '13 confusion matrix',
    clean: 'Human labels break the circle the judge cannot break itself.',
    cover: 'judge scoring its own pipeline = circular reasoning; the blind protocol (label BEFORE seeing the judge); compare 10 toy human vs judge labels; preview agreement (sets up kappa)',
    data: 'toy labels' },
  { id: '13', file: '13_confusion_matrix', title: 'Confusion matrix, accuracy, precision, recall',
    concept: 'TP/FP/TN/FN and which error type kills a failure-detector',
    prev: '12 calibration', next: '14 kappa',
    clean: 'Knowing WHICH way it is wrong matters more than how often.',
    cover: 'build a 2x2 by hand from toy labels; accuracy, precision, recall in plain words; for a failure-DETECTOR a missed failure is the dangerous cell; the accuracy-is-enough trap',
    data: 'toy labels' },
  { id: '14', file: '14_cohens_kappa_from_scratch', title: "Cohen's kappa from scratch",
    concept: 'chance-corrected agreement, the prevalence trap, a bootstrap CI',
    prev: '13 confusion matrix', next: '15 pilot calibration',
    clean: 'Kappa asks: better than luck — and the interval decides what I may claim.',
    cover: 'raw agreement is broken (the lazy constant judge); compute p_e by hand; the kappa formula; the prevalence trap (same competence, lower kappa as classes imbalance); a from-scratch bootstrap 95% CI; Landis-Koch bands',
    data: 'toy labels' },
  { id: '15', file: '15_pilot_calibration_honestly', title: 'Pilot calibration, said honestly',
    concept: 'presenting a mediocre number without fraud or shame',
    prev: '14 kappa', next: '16 improvement examples',
    clean: 'Small sample, honest framing, disagreements shown proudly.',
    cover: 'Landis-Koch bands; the claim rule (say "substantial" ONLY if number AND CI land 0.61-0.80, else "moderate, directional"); show the 2 disagreement cases proudly; the mature sentence; anchor with a toy kappa+CI',
    data: 'toy kappa+CI' },
  { id: '16', file: '16_improvement_examples', title: 'Improvement examples',
    concept: 'failure -> better response -> why; trainable vs config-fixable',
    prev: '15 pilot calibration', next: '17 preference pairs',
    clean: 'Every agent-side failure can propose its own fix.',
    cover: 'take the hero/cast-C barge-in; write the better agent turn; state why; which failures are weight-fixable (token choice) vs config-fixable (dead air = endpointing, not tokens); improvement_example schema',
    data: 'cast C / hero' },
  { id: '17', file: '17_preference_pairs', title: 'Preference pairs',
    concept: 'chosen vs rejected; the single-axis diff rule',
    prev: '16 improvement examples', next: '18 DPO',
    clean: 'A clean pair teaches one lesson; a messy pair teaches confusion.',
    cover: 'human preference example first; the prompt/chosen/rejected shape; author a pair from the hero failure; then make a BAD multi-axis pair and catch why it is bad (like an ablation changing one variable); schemas/improvement_example.md',
    data: 'hero / cast' },
  { id: '18', file: '18_dpo_baby_language', title: 'DPO in baby language',
    concept: 'DPO teaches a model to prefer chosen over rejected; the JSONL format, no training',
    prev: '17 preference pairs', next: '19 RLHF/RLAIF',
    clean: 'DPO teaches a model to prefer chosen over rejected — VoiceForge mines those pairs from real failures.',
    cover: 'human-preference intuition FIRST, the name LAST; the training ladder (pretrain/SFT/preference) in plain words; DPO vs RLHF one sentence each; the TRL conversational JSONL + the OpenAI mirror format (format only, NO training, no GPU); the "any pair is useful" trap',
    data: 'authored pairs (no training)' },
  { id: '19', file: '19_rlhf_rlaif_without_mythology', title: 'RLHF / RLAIF without mythology',
    concept: 'feedback-based alignment in plain words; why VoiceForge does not train live',
    prev: '18 DPO', next: '20 A/B loop',
    clean: 'VoiceForge builds the dataset layer for safe offline optimization.',
    cover: 'RLHF = learning from human feedback; RLAIF = AI-generated feedback; the reward-model idea in one breath; online vs offline; VoiceForge produces the dataset layer, it does not train live',
    data: 'conceptual + toy' },

  // WAVE 4 — system & defense
  { id: '20', file: '20_ab_loop', title: 'The A/B loop',
    concept: 'one-scenario replay; demo evidence vs statistical evidence',
    prev: '19 RLHF/RLAIF', next: '21 rubric',
    clean: 'One closed-loop demonstration, not statistical proof — the shape is the point.',
    cover: 'v1 flawed prompt -> detect failure -> v2 prompt -> rescore; a toy before/after panel (turns down, failures down, score up); the honesty line verbatim; why n=1 is shape not proof',
    data: 'toy before/after' },
  { id: '21', file: '21_rubric_config_driven', title: 'rubric.yaml & config-driven evals',
    concept: 'what "good" means lives in one editable config; edit -> rerun -> everything updates',
    prev: '20 A/B loop', next: '22 simulators',
    clean: "What 'good' means lives in one editable file.",
    cover: 'load the real rubric.yaml; read its dimensions/weights/thresholds; change a weight or a threshold and recompute a toy score; the live-edit demo story; reference pipeline/signals.py reading it',
    data: 'rubric.yaml' },
  { id: '22', file: '22_user_simulators', title: 'User simulators',
    concept: 'synthetic caller personas; simulation buys coverage not validity',
    prev: '21 rubric', next: '23 dataset hierarchy',
    clean: 'Simulation buys coverage, never validity.',
    cover: 'persona scripts (cooperative, hesitant, angry, code-switching); generate a synthetic call object; sim != real logs; when simulation is useful and when it lies',
    data: 'toy personas' },
  { id: '23', file: '23_dataset_hierarchy', title: 'Dataset hierarchy',
    concept: 'hero / public / synthetic / provider logs — each with a job',
    prev: '22 simulators', next: '24 annotation',
    clean: 'Each data source has a job; disclosure makes them all legitimate.',
    cover: 'a strengths/weaknesses table; hero = theater (feel it), public = validity (SpokenWOZ/AMI), synthetic = coverage, provider logs = production reality (Bolna); disclosure is what makes mixed sources honest',
    data: 'conceptual table' },
  { id: '24', file: '24_annotation_ground_truth', title: 'Annotation & ground truth',
    concept: 'assembly-as-truth, hand-verified timestamps, disclosure ethics',
    prev: '23 dataset hierarchy', next: '25 charts',
    clean: 'Annotation is not cheating if you say exactly how the numbers were made.',
    cover: 'the hero call assembly = ground truth (no ASR, no diarization); mark a failure at a timestamp; disclose it as a constructed scenario; reference data/hero and docs/limitations.md',
    data: 'data/hero' },
  { id: '25', file: '25_charts_that_matter', title: 'Charts that matter',
    concept: 'the five demo charts; narrate or it is decoration',
    prev: '24 annotation', next: '26 dashboard',
    clean: 'A chart you cannot narrate is decoration.',
    cover: 'success-by-language, failure distribution, cost-per-successful-call, turns-by-language, voice-fail vs completion; plot small over the normalized pool; read each chart aloud with the 4-question ritual',
    data: 'data/normalized/*.json' },
  { id: '26', file: '26_dashboard_mental_model', title: 'Dashboard mental model',
    concept: 'each view exists for a specific persons question',
    prev: '25 charts', next: '27 adapters',
    clean: 'Every view exists for a specific persons question.',
    cover: 'call list / call detail / analytics / improvement queue mapped to founder (business value), engineer (inspect the trace), ML person (the eval/data artifact); reference the real web/shot.html money-shot page',
    data: 'conceptual + web/' },
  { id: '27', file: '27_provider_adapters', title: 'Provider adapters',
    concept: 'provider-neutrality is achieved by normalizing every source to one schema',
    prev: '26 dashboard', next: '28 engineer-talk',
    clean: 'Provider-neutral is an architecture fact, not a slide claim.',
    cover: 'mock a Bolna-ish execution log and a Cartesia-ish record; normalize BOTH into the same call_log; the adapter contract; reference pipeline/normalize.py and the Bolna timing traps (use /log diffs, not the scrubbed transcript)',
    data: 'mock provider payloads' },
  { id: '28', file: '28_talking_like_an_engineer', title: 'Talking like an engineer, not a bluffer',
    concept: 'the honest lines, drilled, plus competitor positioning',
    prev: '27 adapters', next: '29 the demo',
    clean: 'I tested where the judge agrees with humans — and where it fails.',
    cover: 'the honest lines (I do not train live / this is pilot calibration / one closed-loop demonstration / trace not transcript); competitor one-liners (Coval/Hamming, Roark, Langfuse, Leaping); sharp-question practice with answers',
    data: 'drills (mostly markdown, still keep predict/checkpoints with tiny string cells)' },
  { id: '29', file: '29_the_3_minute_demo', title: 'The 3-minute demo',
    concept: 'the demo spine, rehearsed out loud',
    prev: '28 engineer-talk', next: '30 post-hackathon',
    clean: 'Pain -> measurement -> correction -> dataset -> scale.',
    cover: 'the locked order (audible failure -> timestamp -> scorecard -> better response -> DPO pair -> chart -> calibration -> close); speak each section; timing budget; the two locked lines',
    data: 'the real artifacts (hero, /shot)' },
  { id: '30', file: '30_post_hackathon_path', title: 'Post-hackathon path',
    concept: 'what turns a weekend artifact into a lane',
    prev: '29 the demo', next: 'none (course end)',
    clean: 'A weekend artifact becomes a lane when the data layer keeps compounding.',
    cover: 'the roadmap (more call logs, real provider adapters, multilingual eval set, human-review UI, DPO export, public write-up); why the improvement-data layer compounds; how to not abandon it after Saturday',
    data: 'conceptual' },
]

const BUILD_SCHEMA = {
  type: 'object',
  required: ['file', 'cells_total', 'audit_pass', 'execution_ok', 'can_explain'],
  properties: {
    file: { type: 'string' },
    cells_total: { type: 'integer' },
    cells_code: { type: 'integer' },
    cells_md: { type: 'integer' },
    audit_pass: { type: 'boolean' },
    execution_ok: { type: 'boolean' },
    failing_metric: { type: 'string', description: 'empty if all passed; else the metric that would not go green' },
    can_explain: { type: 'string', description: 'one line: what the learner can explain after this book' },
  },
}

const REVIEW_SCHEMA = {
  type: 'object',
  required: ['verdict', 'beginner_proof', 'cast_consistent', 'teaches_one_concept', 'issues'],
  properties: {
    verdict: { type: 'string', enum: ['PASS', 'NEEDS_FIX'] },
    beginner_proof: { type: 'boolean', description: 'no skipped assumptions, no unexplained jargon, no passive lecture walls' },
    cast_consistent: { type: 'boolean', description: 'cast A/B/C ids/languages/outcomes match the spec; terminology consistent' },
    teaches_one_concept: { type: 'boolean', description: 'one atomic concept, correct prev->current->next framing' },
    issues: { type: 'array', items: { type: 'string' }, description: 'concrete fixes; empty if PASS' },
    severity: { type: 'string', enum: ['none', 'low', 'medium', 'high'] },
  },
}

function buildPrompt(b, isFix, prior) {
  return `Build ONE VoiceForge University notebook. ${isFix ? 'This is a FIX pass — a prior build/review found problems; address them all.' : ''}

FIRST: Read ${SPEC} in full (the binding builder contract: four-act skeleton, marker conventions the audit greps for, the recurring cast A/B/C, the learner-cell guard pattern, the self-audit cell template, real repo anchors). Then Read notebooks/P00_how_to_learn.ipynb as the gold style reference.

This notebook:
- id/filename: ${b.id} -> notebooks/${b.file}.ipynb
- title: ${b.title}
- the ONE atomic concept: ${b.concept}
- knowledge-flow map: ${b.prev}  ->  THIS (${b.title})  ->  ${b.next}
- must cover: ${b.cover}
- data to use: ${b.data}
- the book's clean sentence (end with it): "${b.clean}"
${isFix && prior ? `\nPRIOR ISSUES TO FIX:\n${prior}\n` : ''}
Write notebooks/build_${b.id}.py (Python emitting the .ipynb with md()/code() helpers, exactly like notebooks/build_P00.py). 50-90 small cells, four acts, >=5 specific CHECKPOINT gates, 4 act-end "knowledge-flow checkpoint" gates, >=8 PREDICT prompts, >=6 "YOUR TURN" learner-owned cells (guarded so they run clean UNFILLED), >=2 break-it cells, >=1 WRONG-INTUITION TRAP, beginner/engineer/founder explanations, 3 defense questions, a TEACH-BACK gate, the clean sentence, and the self-audit cell as the LAST cell (filename "${b.file}.ipynb"). Every code cell needs a reasoning comment (why the line exists, not syntax). Manual-before-function, raw-before-transformed, toy-before-real. Never write the banned words: obviously / as you know / simply / intuitively.

Then run BOTH gates and ITERATE on your build script until both are green:
  .venv/bin/python notebooks/build_${b.id}.py
  .venv/bin/python notebooks/run_nb.py notebooks/${b.file}.ipynb     (must print EXECUTION OK)
  .venv/bin/python notebooks/audit_nb.py notebooks/${b.file}.ipynb   (must print ALL PASS)

Report the BUILD_SCHEMA fields. Set audit_pass/execution_ok ONLY from the actual gate output. If a gate will not go green after honest effort, report audit_pass:false and the failing_metric — never fake it.`
}

function reviewPrompt(b, built) {
  return `You are the Beginner-Brutality + Consistency reviewer. A notebook was just built. Judge it as if you know NOTHING about ${b.title} — flag every skipped assumption, unexplained term, or passive lecture wall a true beginner would trip on.

Read it: notebooks/${b.file}.ipynb (built; self-audit pass=${built ? built.audit_pass : 'unknown'}, exec ok=${built ? built.execution_ok : 'unknown'}). Also Read ${SPEC} for the cast + terminology.

Check, concretely:
1. beginner_proof — no jumps, no jargon used before it is defined, no "run this and move on" passivity; manual shown before any function; raw shown before transformed.
2. cast_consistent — if it uses the recurring calls, ids are call_A/call_B/call_C with languages English/Hinglish/Telugu-English and outcomes success/partial/failure EXACTLY; terminology (FTO, barge-in, latency, scorecard, preference pair, etc.) matches the spec.
3. teaches_one_concept — exactly one atomic concept (${b.concept}), framed prev->current->next as: ${b.prev} -> ${b.title} -> ${b.next}.

You may run .venv/bin/python notebooks/audit_nb.py notebooks/${b.file}.ipynb to confirm structure. Return REVIEW_SCHEMA: verdict PASS only if all three booleans are true AND the build gates passed; else NEEDS_FIX with concrete, actionable issues (each issue names the cell/section and the fix).`
}

// ---- BUILD -> REVIEW -> conditional FIX, per notebook, fully pipelined (no barriers) ----
const results = await pipeline(
  BOOKS,
  (b) => agent(buildPrompt(b, false, null),
    { label: `build:${b.id}`, phase: 'Build', agentType: 'general-purpose', schema: BUILD_SCHEMA })
    .then(built => ({ b, built })),

  ({ b, built }) => {
    if (!built) return { b, built: null, review: { verdict: 'NEEDS_FIX', beginner_proof: false, cast_consistent: false, teaches_one_concept: false, issues: ['build agent returned nothing'], severity: 'high' } }
    return agent(reviewPrompt(b, built),
      { label: `review:${b.id}`, phase: 'Review', agentType: 'general-purpose', schema: REVIEW_SCHEMA })
      .then(review => ({ b, built, review }))
  },

  ({ b, built, review }) => {
    const needsFix = !built || !built.audit_pass || !built.execution_ok || (review && review.verdict === 'NEEDS_FIX')
    if (!needsFix) return { b, built, review, fixed: null }
    const priorIssues = [
      built && !built.audit_pass ? `audit failing: ${built.failing_metric || 'unknown metric'}` : '',
      built && !built.execution_ok ? 'run_nb.py did not print EXECUTION OK — a non-teaching cell raised' : '',
      ...(review && review.issues ? review.issues : []),
    ].filter(Boolean).join('\n- ')
    return agent(buildPrompt(b, true, '- ' + priorIssues),
      { label: `fix:${b.id}`, phase: 'Fix', agentType: 'general-purpose', schema: BUILD_SCHEMA })
      .then(fixed => ({ b, built: fixed, review, fixed }))
  },
)

// ---- MANIFEST: deterministic summary + a writer agent for the report files ----
const clean = results.filter(Boolean)
const summary = clean.map(r => {
  const x = r.built || {}
  const rv = r.review || {}
  return {
    id: r.b.id, file: r.b.file + '.ipynb', wave: r.b.id.startsWith('P') ? 1 : (Number(r.b.id) <= 9 ? 2 : Number(r.b.id) <= 19 ? 3 : 4),
    cells: x.cells_total || 0, audit_pass: !!x.audit_pass, execution_ok: !!x.execution_ok,
    review: rv.verdict || 'unknown', fixed: !!r.fixed, failing_metric: x.failing_metric || '',
    issues: (rv.issues || []).slice(0, 4),
  }
})
const passed = summary.filter(s => s.audit_pass && s.execution_ok && s.review === 'PASS')
const needfix = summary.filter(s => !(s.audit_pass && s.execution_ok && s.review === 'PASS'))
log(`built ${summary.length}/35 · clean PASS ${passed.length} · needs attention ${needfix.length}`)

await agent(
  `Write three report files from this build summary (JSON below). Do not rebuild notebooks — only write reports.

SUMMARY: ${JSON.stringify(summary)}

1. reports/notebook_audit_report.md — a table over every notebook: id, file, wave, cells, audit_pass, execution_ok, review verdict, fixed?, and any issues. Group by wave. Put a header line with counts (total, clean-pass, needs-attention).
2. reports/notebook_manifest.md — the recommended RUN ORDER for the learner: P00 (exists), then P01-P04, then 00-30 in numeric order, one line each "id — title — status". Mark any non-clean ones with a (needs fix) tag.
3. notebooks/README.md — a short learner-facing guide: what VoiceForge University is, the predict->run->explain->change->defend ritual, the run order, ~20-30 min per book, how to run the self-audit, and that P00 teaches the method first. Keep it warm and short.

Report just "reports written".`,
  { label: 'manifest', phase: 'Manifest', agentType: 'general-purpose' })

return { built: summary.length, passed: passed.length, needs_attention: needfix.map(s => s.id) }
