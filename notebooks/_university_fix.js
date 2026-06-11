export const meta = {
  name: 'voiceforge-university-fix',
  description: 'Fix the 10 notebooks with substantive review findings (prose contradicting output), each verified by an independent re-run that quotes corrected-prose-vs-output',
  phases: [{ title: 'Fix' }, { title: 'Verify' }],
}

const SPEC = 'notebooks/_BUILD_SPEC.md'

// each book: the EXACT fixes the reviewer specified (prose must end up matching printed output)
const BOOKS = [
  { id: 'P02', file: 'P02_tables_and_pandas', sev: 'medium', fixes:
`FACTUAL: the notebook wrongly attributes an 'outcome' field to the REAL schema (schemas/call_log.md has NO top-level outcome; real fields: call_id, source, language, stress_profile, workflow_type, turns, audio_path, metadata; 'outcome' is only the TOY column this lesson adds).
- cell-8 markdown: change the claimed real-schema fields to "real fields: call_id, source, language, stress_profile, plus a turns list" and DROP 'outcome' from the real-schema claim (keep outcome only as the toy column).
- cell-73 markdown: remove 'outcome' from the "EXACTLY the fields" list -> "call_id, source, language, stress_profile, and a turns list (the normalized schema in schemas/call_log.md has no top-level outcome; outcome here is a toy-cast simplification)."` },
  { id: 'P03', file: 'P03_basic_plots_for_evals', sev: 'low', fixes:
`TERMINOLOGY: the toy-timeline calls any negative-FTO overlap a "barge-in" with no threshold. Add the 100ms distinction in Act 2 (cell-30 markdown and/or cell-34 comment): an overlap counts as a barge-in only when it exceeds ~100ms; smaller overlaps are "backchannels" and are ignored (per rubric.yaml threshold_overlap_ms=100). Act 4 (cell-61/63) already cites this, so just forward-reference it. Every overlap actually drawn is >100ms so no number changes — this is a wording precision fix only.` },
  { id: '04', file: '04_turns_gaps_overlap_latency', sev: 'medium', fixes:
`FACTUAL: prose says FOUR user->agent latency gaps but the chart (cell-68) draws FIVE bars (it builds from ALL user->agent seams incl. t2->t3 which is an OVERLAP fto=-800, gap 0). The count 4 is CORRECT (analyze() n_handoffs=4 filters fto_ms>=0); the CHART is wrong.
- cell-68: build the chart from gap-bearing handoffs only: lat_handoffs = [e for e in user_to_agent if e['fto_ms'] >= 0]; derive labels and gaps_ms from lat_handoffs -> exactly 4 bars [t4->t5=400, t6->t7=1620, t8->t9=350, t10->t11=400]. Add a reasoning comment that t2->t3 is excluded as an overlap (fto<0), not a latency gap.
- cell-30: print hero['turns'][:3] (so t3, referenced by cell-31, is actually shown) — or reword cell-31 to not say "look at" an unprinted turn.` },
  { id: '09', file: '09_language_conditions', sev: 'medium', fixes:
`FACTUAL: cell-20 claims "turn count rose ... as the language moved away from English" but the printed table is English=4, Hinglish=6, Telugu-English=4 (rises then FALLS, not monotone). Rewrite cell-20 to NOT claim a monotone rise. Accurate version: "The English call finished in the fewest turns and succeeded; the Hinglish call took the MOST turns (6) and only partially completed; the Tenglish call also took few turns (4) but FAILED outright — the booking died fast rather than dragging on. The two failure modes look different in turn count (Hinglish drags, Tenglish collapses), but BOTH are non-success once the language moves off clean English — the lesson is the OUTCOME shift, not a tidy turn-count ranking." Drop the phrase "turn count rose ... as the language moved away from English".` },
  { id: '13', file: '13_confusion_matrix', sev: 'high', fixes:
`FACTUAL (root cause): the toy dataset in cell-10 is 5 failures / 5 fine (BALANCED 50/50), so the "always fine" lazy detector scores accuracy 0.5 — but the whole Act-3 narrative (cells 40,42,43,47) is written as if 'fine' were a dominant majority. Cleanest fix: make cell-10's labels MAJORITY-FINE (e.g. ~8 fine / 2 failure) so the lazy detector genuinely scores HIGH accuracy and the narrative becomes TRUE. Then re-run and RECONCILE every downstream number to the new output: cell-40 PREDICT ("most calls really are fine"), cell-42 "respectable accuracy"/all-TN, cell-43 CHECKPOINT 4 (high accuracy via TN/FN/majority), cell-47 seesaw. ALSO remove the stray "92%" from cell-42 — that figure belongs only to the separate rare-failure trap at cell-52 (TN=92/100); do not state 92% next to this detector. Keep cell-52's 92%-fine trap as-is. VERIFY the printed lazy accuracy, TP/FP/TN/FN, precision, recall all match the corrected prose.` },
  { id: '17', file: '17_preference_pairs', sev: 'high', fixes:
`FACTUAL (centerpiece): the axes-moved detector prints FEWER axes than the prose claims.
- cell-45/46: prose says "Three axes moved: length, language, tone" but printed "['language','tone-padding'] -> 2 axes" (length did not fire: bad_chosen 19 vs rejected 21 words, diff<5). Either make bad_chosen long enough that length fires (word-count diff >=5) so printed=3, OR change cells 42/43/46 prose to "two axes (language, tone-padding) moved" and drop the length/over-talk axis. Prose and printed number MUST agree.
- cell-56/57/58 (the WRONG-INTUITION TRAP the whole book is built on): prose says "better on every axis"/"better on N axes" but cell-57 printed "axes moved: [] -> 0 axes". Make better_everything actually trip the detector on the claimed axes — include a pad_marker the tuple recognizes (e.g. 'sorry sorry' or 'please!') and/or make it long enough to fire length — so printed axes >1 supports the "better on every axis = multi-axis = confounded" reveal.
- cell-64: call_C's chosen must be byte-identical to reference_chosen used in Act 2-3 (add 'station': "Got it - Madhapur, near the metro STATION. Morning or evening slot work better?").
- cell-55: the "multi-axis break" default my_bad_chosen currently moves only 1 axis; ship a default that moves 2+ (add a te_marker or pad_marker) so the unfilled cell shows the lesson, OR rephrase the heading.
VERIFY each corrected claim against the freshly printed 'axes moved' line.` },
  { id: '20', file: '20_ab_loop', sev: 'high', fixes:
`FACTUAL + self-contradiction: cell-28 prints "DETECTED failure axis: barge_in" (min() tie: barge_in AND repair_quality both 0.0, returns first) but cell-30 says "The detected failure was repair_quality". And the book preaches SINGLE-AXIS ("fix THIS axis and change nothing else") yet v2 (cell-33) moves THREE dims (barge_in, repair_quality, task_completion all rise). Make code, output, and prose AGREE:
- Make detection self-consistent: have cell-28 print BOTH zeroed dimensions (barge_in AND repair_quality, both 0.0) and cell-30 say the two lowest both scored 0.0 — they are the SAME underlying behaviour (the agent steamrolling a partial answer), so v2 targets that one BEHAVIOUR.
- Reframe the discipline as "change one BEHAVIOUR (which may touch >1 scored dimension)": edit cell-28's printout away from the literal "fix THIS axis and change nothing else", and note explicitly that v2 lifts barge_in, repair_quality AND task_completion because they share one root cause. cell-30 "two instructions" must be consistent with that.
VERIFY cell-28's printed axis/axes equals what cell-30 calls the detected failure, and the single-axis language no longer contradicts the multi-dimension panel (cell-42 failures 2->0).` },
  { id: '21', file: '21_rubric_config_driven', sev: 'high', fixes:
`FACTUAL (two):
- cell-57/58 trap claims a weight edit cuts BOTH directions ("one overall rose, the other fell"/"Raise the weight and a good score speaks louder (overall up)") but the run shows GOOD-latency 0.93->0.93 (UNCHANGED) and BAD 0.77->0.61 (fell) — only 'fell' is demonstrated. Root cause: the GOOD call has barge_in=1.0 (the dimension being down-weighted) so nothing moves. FIX: give the GOOD call a non-perfect barge_in, e.g. scores_good_latency = {**toy_scores, 'latency_gap': 1.0, 'barge_in': 0.4}, so up-weighting latency_gap genuinely RAISES its overall. VERIFY the new run prints GOOD base < heavy before keeping the "one overall rose" line.
- cell-63 says "the call scored 0.4" (call_C) but cell-64 prints "call_C: overall 0.245". Change cell-63 to "the call scored 0.245" (or reword to let cell-64 supply the number). VERIFY against the printed 0.245.` },
  { id: '22', file: '22_user_simulators', sev: 'medium', fixes:
`FACTUAL + beginner:
- cell-56 claims "Same language" but cell-54's table prints SYNTHETIC language 'Telugu-English' vs REAL HERO 'te-en' (two different field values). Reword cell-56 to "same language CONDITION (both Telugu-English code-switching), noted differently in the field (Telugu-English vs te-en)" — do not assert field-value sameness the table disproves. (Alternatively set the synthetic persona language to 'te-en'.)
- Define 'te-en' once (cell-51 or cell-54 markdown/comment): "the hero file labels the language te-en (the schema's BCP-47-ish code for Telugu-English; schemas/call_log.md)". The learner currently sees the unexplained code 'te-en' at runtime with no key.
- Soften the "EXACT schemas/call_log.md shape" claims (cells 0/14/19/56): source='synthetic' is NOT in the schema's source enum (spokenwoz|ami|hero|bolna). Say "the same shape the pipeline reads, with source extended to synthetic (a value the deterministic signals ignore)" rather than "EXACT schema shape".
- cell-25/28: turn counts tie (cooperative=angry=code_switcher=4, hesitant=6); cell-28 prints 'fewest: p_cooperative' only because it is first. Make the fewest-check accept ANY persona at the min turn count (compare against the set at min), so a learner who answers p_angry is not wrongly told 'DIFFERED'.
VERIFY against printed output.` },
  { id: '23', file: '23_dataset_hierarchy', sev: 'low', fixes:
`BEGINNER: cell-34's comment claims "We compute the gap so your guess can be checked against the actual missing-from-disk set," but the cell computes no gap and checks nothing; the variable 'defined' is dead code. FIX: either (a) actually compute and print the gap and check the guess: missing_jobs = {'synthetic','provider_log'}; print('jobs the pool does not fill:', sorted(missing_jobs)); print('your guess correct?', set(my_missing_sources)==missing_jobs) — and remove/repair the dead 'defined' (collapse spokenwoz->public so the gap is the TWO jobs the prose promises, not three); or (b) drop the false promise: change the comment to "we print your guess and the present sources so you can eyeball the gap yourself" and delete the dead 'defined' variable. VERIFY the cell runs clean unfilled and the comment matches what the code does.` },
]

const FIX_SCHEMA = {
  type: 'object',
  required: ['file', 'audit_pass', 'execution_ok', 'verification'],
  properties: {
    file: { type: 'string' }, audit_pass: { type: 'boolean' }, execution_ok: { type: 'boolean' },
    fixes_applied: { type: 'string' },
    verification: { type: 'string', description: 'for each flagged claim: quote the corrected prose AND the matching printed-output line proving they now agree' },
    unresolved: { type: 'string', description: 'empty if all resolved' },
  },
}
const VERIFY_SCHEMA = {
  type: 'object',
  required: ['file', 'factual_now', 'residual_issues'],
  properties: {
    file: { type: 'string' },
    factual_now: { type: 'boolean', description: 'true only if NO markdown claim contradicts the notebook’s own printed output anymore' },
    gates_green: { type: 'boolean' },
    residual_issues: { type: 'array', items: { type: 'string' } },
  },
}

const results = await pipeline(
  BOOKS,
  (b) => agent(
`Fix ONE notebook by editing its build script. Read ${SPEC} (cast + terminology), then Read notebooks/build_${b.id}.py AND notebooks/${b.file}.ipynb.

Apply EXACTLY these fixes (the prose must end up matching the notebook's own printed output):
${b.fixes}

Then rebuild and re-gate, iterating until green:
  .venv/bin/python notebooks/build_${b.id}.py
  .venv/bin/python notebooks/run_nb.py notebooks/${b.file}.ipynb     (EXECUTION OK)
  .venv/bin/python notebooks/audit_nb.py notebooks/${b.file}.ipynb   (ALL PASS)

CRITICAL: gates green is NOT enough — these are FACTUAL bugs the structural audit cannot see. After rebuilding, RUN the notebook and read its actual stdout, then for EACH flagged claim quote the corrected prose line AND the matching printed-output line proving they now agree. If you changed code/data (books 13/17/20/21), re-derive and confirm EVERY downstream number the prose cites matches the new output. Do not break any other cell, keep the gym structure (>=5 CHECKPOINT, >=8 PREDICT, >=6 YOUR TURN, >=2 BREAK-IT, the trap, teach-back, clean sentence, self-audit). Return FIX_SCHEMA from the ACTUAL gate output + your quoted verification.`,
    { label: `fix:${b.id}`, phase: 'Fix', agentType: 'general-purpose', schema: FIX_SCHEMA }).then(fix => ({ b, fix })),

  ({ b, fix }) => agent(
`Independent verifier. The notebook notebooks/${b.file}.ipynb was just edited to fix factual contradictions. Confirm they are actually gone.

Read notebooks/${b.file}.ipynb, then RUN it and watch stdout:
  .venv/bin/python notebooks/run_nb.py notebooks/${b.file}.ipynb
  .venv/bin/python notebooks/audit_nb.py notebooks/${b.file}.ipynb

The original flagged problems were:
${b.fixes}

Re-check: does ANY markdown claim still contradict the notebook's own printed/computed output (the original issues AND any new contradiction the edit may have introduced)? Cross-check every quantitative/superlative claim against the run output. Return VERIFY_SCHEMA: factual_now=true ONLY if no contradiction remains; else list residual_issues with cell numbers and the conflicting quote-vs-output.`,
    { label: `verify:${b.id}`, phase: 'Verify', agentType: 'general-purpose', schema: VERIFY_SCHEMA }).then(verify => ({ b, fix, verify })),
)

const out = results.filter(Boolean).map(r => ({
  id: r.b.id, file: r.b.file + '.ipynb', sev: r.b.sev,
  audit_pass: !!(r.fix && r.fix.audit_pass), execution_ok: !!(r.fix && r.fix.execution_ok),
  factual_now: !!(r.verify && r.verify.factual_now),
  residual: (r.verify && r.verify.residual_issues) || ['verify agent returned nothing'],
  verification: (r.fix && r.fix.verification) || '',
}))
const good = out.filter(o => o.audit_pass && o.execution_ok && o.factual_now)
log(`fixed ${out.length}/10 · fully-resolved ${good.length} · still-needs ${out.length - good.length}`)
return { results: out }
