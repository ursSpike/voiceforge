export const meta = {
  name: 'voiceforge-university-resume',
  description: 'Build the 6 notebooks the interrupted run never started (03, 08, 10, 28, 29, 30); each gated by execute + audit + beginner-brutality review + conditional fix',
  phases: [{ title: 'Build' }, { title: 'Review' }, { title: 'Fix' }],
}

const SPEC = 'notebooks/_BUILD_SPEC.md'

const BOOKS = [
  { id: '03', file: '03_pandas_for_call_data', title: 'Python/pandas for call data',
    concept: 'real calls as rows; group and count outcomes at scale',
    prev: '02 schemas', next: '04 timing',
    clean: 'A DataFrame lets me treat calls like benchmark rows.',
    cover: 'load data/normalized/*.json into a DataFrame; one row = one call; manual dict-loop count FIRST then pandas; group by stress_profile and by source; count; the benchmark-row analogy from his Fujitsu world',
    data: 'data/normalized/*.json (11 real calls)' },
  { id: '08', file: '08_cost_per_successful_call', title: 'Cost per successful call',
    concept: 'cost = turns x unit price; failures shrink the denominator',
    prev: '07 failure tags', next: '09 language',
    clean: 'Voice quality is a money number, not a feelings number.',
    cover: 'assign toy unit costs (LLM/TTS/STT per turn); compute cost per call by hand; then cost per SUCCESSFUL call (spend / completed calls); clean vs messy comparison; always label "estimated, prototype"; reference schemas/cost.md',
    data: 'data/normalized pool + toy unit costs' },
  { id: '10', file: '10_llm_as_judge_from_zero', title: 'LLM-as-judge from zero',
    concept: 'a judge reads a transcript and returns a structured score; the reliability contract',
    prev: '09 language', next: '11 evidence',
    clean: 'A judge you can rerun and get the same answer is an instrument; anything else is a mood.',
    cover: 'a FAKE hand-written judge first (a plain function returning a score from keywords); then the real Gemini judge via pipeline/judge.py (temperature 0, JSON, disk cache); why determinism + caching make it an instrument; disclose the judge. CRITICAL: any live Gemini call MUST be wrapped in try/except with a cached/canned fallback so notebooks/run_nb.py passes with NO network and NO key — never let a live call be the only path',
    data: 'a pool call + pipeline/judge.py (guarded so run_nb passes offline)' },
  { id: '28', file: '28_talking_like_an_engineer', title: 'Talking like an engineer, not a bluffer',
    concept: 'the honest lines, drilled, plus competitor positioning',
    prev: '27 adapters', next: '29 the demo',
    clean: 'I tested where the judge agrees with humans — and where it fails.',
    cover: 'the honest lines (I do not train live / this is pilot calibration / one closed-loop demonstration / trace not transcript); competitor one-liners (Coval/Hamming, Roark, Langfuse, Leaping AI); sharp-question practice with honest answers. Mostly markdown, but STILL keep the gyms: >=8 PREDICT prompts and >=6 YOUR TURN cells where the learner types their OWN answer to a sharp question into a string variable, and >=2 break-it cells where a weak/bluffy answer is shown then dismantled',
    data: 'drills (string-variable answers, no heavy compute)' },
  { id: '29', file: '29_the_3_minute_demo', title: 'The 3-minute demo',
    concept: 'the demo spine, rehearsed out loud',
    prev: '28 engineer-talk', next: '30 post-hackathon',
    clean: 'Pain -> measurement -> correction -> dataset -> scale.',
    cover: 'the locked order (audible failure -> timestamp -> scorecard -> better response -> DPO pair -> chart -> calibration -> close); the two locked lines; timing budget per beat; reference the REAL artifacts (data/hero/turns.json gives 0:18 barge-in 800ms / 0:53 gap 1620ms; web/shot.html). Learner types their own version of each beat into string vars (YOUR TURN); break-it = a demo beat in the WRONG order or that overclaims, shown then fixed',
    data: 'real artifacts (hero turns.json, web/shot.html) + string-var rehearsal' },
  { id: '30', file: '30_post_hackathon_path', title: 'Post-hackathon path',
    concept: 'what turns a weekend artifact into a lane',
    prev: '29 the demo', next: 'none (course end)',
    clean: 'A weekend artifact becomes a lane when the data layer keeps compounding.',
    cover: 'the roadmap (more call logs, real provider adapters, multilingual eval set, human-review UI for the improvement queue, DPO export, public write-up); WHY the improvement-data layer compounds while a one-off demo does not; how to not abandon it after Saturday. Keep the gym shape: PREDICT/YOUR TURN cells where the learner drafts their own next 3 steps; a wrong-intuition trap ("a good demo = a product")',
    data: 'conceptual + the learners own roadmap drafts' },
]

const BUILD_SCHEMA = {
  type: 'object',
  required: ['file', 'cells_total', 'audit_pass', 'execution_ok', 'can_explain'],
  properties: {
    file: { type: 'string' }, cells_total: { type: 'integer' },
    cells_code: { type: 'integer' }, cells_md: { type: 'integer' },
    audit_pass: { type: 'boolean' }, execution_ok: { type: 'boolean' },
    failing_metric: { type: 'string' }, can_explain: { type: 'string' },
  },
}
const REVIEW_SCHEMA = {
  type: 'object',
  required: ['verdict', 'beginner_proof', 'cast_consistent', 'teaches_one_concept', 'issues'],
  properties: {
    verdict: { type: 'string', enum: ['PASS', 'NEEDS_FIX'] },
    beginner_proof: { type: 'boolean' }, cast_consistent: { type: 'boolean' },
    teaches_one_concept: { type: 'boolean' },
    issues: { type: 'array', items: { type: 'string' } },
    severity: { type: 'string', enum: ['none', 'low', 'medium', 'high'] },
  },
}

function buildPrompt(b, isFix, prior) {
  return `Build ONE VoiceForge University notebook. ${isFix ? 'FIX pass — a prior build/review found problems; address them all.' : ''}

FIRST: Read ${SPEC} in full (binding contract: four-act skeleton, marker conventions the audit greps, recurring cast A/B/C, learner-cell guard pattern, self-audit template, real repo anchors). Then Read notebooks/P00_how_to_learn.ipynb (gold style) and notebooks/04_turns_gaps_overlap_latency.ipynb (a strong already-built sibling) for rhythm.

This notebook:
- id/filename: ${b.id} -> notebooks/${b.file}.ipynb
- title: ${b.title}
- the ONE atomic concept: ${b.concept}
- knowledge-flow map: ${b.prev}  ->  THIS (${b.title})  ->  ${b.next}
- must cover: ${b.cover}
- data: ${b.data}
- end with the clean sentence: "${b.clean}"
${isFix && prior ? `\nPRIOR ISSUES TO FIX:\n${prior}\n` : ''}
Write notebooks/build_${b.id}.py (Python emitting the .ipynb with md()/code() helpers, exactly like notebooks/build_P00.py). 50-90 small cells; four acts; >=5 specific CHECKPOINT gates (uppercase "CHECKPOINT"); 4 act-end "knowledge-flow checkpoint" gates (lowercase); >=8 PREDICT prompts; >=6 "YOUR TURN" learner-owned cells (guarded so they run clean UNFILLED — None/"" placeholders + if-guards); >=2 break-it cells (use the literal "BREAK-IT"; a crashing teaching cell also needs "EXPECTED FAILURE FOR LEARNING" then a recovery cell); >=1 "WRONG-INTUITION TRAP"; beginner/engineer/founder explanations; 3 defense questions; a "TEACH-BACK" gate; the "clean sentence"; and the self-audit cell as the LAST cell (filename "${b.file}.ipynb"). Every code cell needs a reasoning comment. Manual-before-function, raw-before-transformed, toy-before-real. Never write: obviously / as you know / simply / intuitively.

Then run BOTH gates and ITERATE the build script until both are green:
  .venv/bin/python notebooks/build_${b.id}.py
  .venv/bin/python notebooks/run_nb.py notebooks/${b.file}.ipynb     (must print EXECUTION OK)
  .venv/bin/python notebooks/audit_nb.py notebooks/${b.file}.ipynb   (must print ALL PASS)

Report BUILD_SCHEMA fields from the ACTUAL gate output. If a gate will not go green, report audit_pass:false + the failing_metric — never fake it.`
}

function reviewPrompt(b, built) {
  return `Beginner-Brutality + Consistency reviewer. Judge notebooks/${b.file}.ipynb as if you know NOTHING about ${b.title}. Read it; also Read ${SPEC} for cast + terminology. (build self-audit pass=${built ? built.audit_pass : '?'}, exec=${built ? built.execution_ok : '?'}.)
Check: (1) beginner_proof — no skipped assumptions, no jargon-before-definition, no passive walls, manual-before-function. (2) cast_consistent — call_A/call_B/call_C with languages English/Hinglish/Telugu-English, outcomes success/partial/failure; terminology matches spec. (3) teaches_one_concept — exactly "${b.concept}", framed ${b.prev} -> ${b.title} -> ${b.next}.
You may run: .venv/bin/python notebooks/audit_nb.py notebooks/${b.file}.ipynb. Return REVIEW_SCHEMA: verdict PASS only if all three booleans true AND build gates passed; else NEEDS_FIX with concrete cell-level issues.`
}

const results = await pipeline(
  BOOKS,
  (b) => agent(buildPrompt(b, false, null),
    { label: `build:${b.id}`, phase: 'Build', agentType: 'general-purpose', schema: BUILD_SCHEMA }).then(built => ({ b, built })),
  ({ b, built }) => {
    if (!built) return { b, built: null, review: { verdict: 'NEEDS_FIX', beginner_proof: false, cast_consistent: false, teaches_one_concept: false, issues: ['build returned nothing'], severity: 'high' } }
    return agent(reviewPrompt(b, built),
      { label: `review:${b.id}`, phase: 'Review', agentType: 'general-purpose', schema: REVIEW_SCHEMA }).then(review => ({ b, built, review }))
  },
  ({ b, built, review }) => {
    const needsFix = !built || !built.audit_pass || !built.execution_ok || (review && review.verdict === 'NEEDS_FIX')
    if (!needsFix) return { b, built, review, fixed: null }
    const prior = [
      built && !built.audit_pass ? `audit failing: ${built.failing_metric || 'unknown'}` : '',
      built && !built.execution_ok ? 'run_nb.py did not print EXECUTION OK — a non-teaching cell raised' : '',
      ...(review && review.issues ? review.issues : []),
    ].filter(Boolean).join('\n- ')
    return agent(buildPrompt(b, true, '- ' + prior),
      { label: `fix:${b.id}`, phase: 'Fix', agentType: 'general-purpose', schema: BUILD_SCHEMA }).then(fixed => ({ b, built: fixed, review, fixed }))
  },
)

const summary = results.filter(Boolean).map(r => ({
  id: r.b.id, file: r.b.file + '.ipynb',
  audit_pass: !!(r.built && r.built.audit_pass), execution_ok: !!(r.built && r.built.execution_ok),
  review: (r.review && r.review.verdict) || 'unknown', fixed: !!r.fixed,
  failing_metric: (r.built && r.built.failing_metric) || '',
  issues: (r.review && r.review.issues ? r.review.issues : []).slice(0, 3),
}))
const clean = summary.filter(s => s.audit_pass && s.execution_ok && s.review === 'PASS')
log(`resume built ${summary.length}/6 · clean ${clean.length} · attention ${summary.length - clean.length}`)
return { summary }
