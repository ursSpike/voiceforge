export const meta = {
  name: 'voiceforge-university-review',
  description: 'Independent beginner-brutality + factual-consistency review of the 29 notebooks whose review was lost when the build run was killed',
  phases: [{ title: 'Review' }],
}

const SPEC = 'notebooks/_BUILD_SPEC.md'

// the 29 not independently reviewed this session (all minus P00, 03, 08, 10, 28, 29, 30)
const FILES = [
  ['P01', 'P01_python_objects_for_call_logs'], ['P02', 'P02_tables_and_pandas'],
  ['P03', 'P03_basic_plots_for_evals'], ['P04', 'P04_debugging_confusion'],
  ['00', '00_what_is_voiceforge'], ['01', '01_what_is_a_call_log'],
  ['02', '02_json_schemas_data_contracts'], ['04', '04_turns_gaps_overlap_latency'],
  ['05', '05_asr_llm_tts_voice_stack'], ['06', '06_task_success'],
  ['07', '07_failure_tags_stress_profiles'], ['09', '09_language_conditions'],
  ['11', '11_evidence_based_scoring'], ['12', '12_calibration_why_human_labels'],
  ['13', '13_confusion_matrix'], ['14', '14_cohens_kappa_from_scratch'],
  ['15', '15_pilot_calibration_honestly'], ['16', '16_improvement_examples'],
  ['17', '17_preference_pairs'], ['18', '18_dpo_baby_language'],
  ['19', '19_rlhf_rlaif_without_mythology'], ['20', '20_ab_loop'],
  ['21', '21_rubric_config_driven'], ['22', '22_user_simulators'],
  ['23', '23_dataset_hierarchy'], ['24', '24_annotation_ground_truth'],
  ['25', '25_charts_that_matter'], ['26', '26_dashboard_mental_model'],
  ['27', '27_provider_adapters'],
]

const REVIEW_SCHEMA = {
  type: 'object',
  required: ['file', 'verdict', 'factual_consistency', 'beginner_proof', 'cast_consistent', 'teaches_one_concept', 'issues'],
  properties: {
    file: { type: 'string' },
    verdict: { type: 'string', enum: ['PASS', 'NEEDS_FIX'] },
    factual_consistency: { type: 'boolean', description: 'no markdown claim contradicts the notebook’s own computed/printed output' },
    beginner_proof: { type: 'boolean', description: 'no skipped assumptions, no jargon-before-definition, no passive lecture walls, manual-before-function' },
    cast_consistent: { type: 'boolean', description: 'cast A/B/C ids/languages/outcomes + terminology match the spec' },
    teaches_one_concept: { type: 'boolean' },
    issues: { type: 'array', items: { type: 'string' }, description: 'concrete, cell-numbered, actionable; empty if PASS' },
    severity: { type: 'string', enum: ['none', 'low', 'medium', 'high'] },
  },
}

function reviewPrompt(id, file) {
  return `Independent reviewer. Audit notebooks/${file}.ipynb HARD, as if you know nothing about the topic and you are trying to FAIL it.

Read notebooks/${file}.ipynb (markdown claims AND code) and Read ${SPEC} (cast A/B/C + terminology).

THEN run it and watch its real output:
  .venv/bin/python notebooks/run_nb.py notebooks/${file}.ipynb
(every cell's print() goes to stdout; this is how you check claims against reality.)

Four checks — be ruthless and specific (cite cell numbers):
1. factual_consistency (HIGHEST VALUE — this is how book 03 failed): does ANY markdown claim
   contradict the notebook's own computed/printed output? e.g. prose says "X is the biggest/most/
   highest" but the printed numbers tie or disagree; a stated count/threshold/result that the code
   does not actually produce. Cross-check every quantitative or superlative claim against the run output.
2. beginner_proof: any skipped assumption, term used before it is defined, clever compact code, a
   function shown before the manual version, or a passive "run this and move on" stretch.
3. cast_consistent: if it uses the recurring calls, ids are call_A/call_B/call_C, languages
   English/Hinglish/Telugu-English, outcomes success/partial/failure; terminology (FTO, barge-in,
   latency, scorecard, preference pair, etc.) matches the spec. (Books anchored on the REAL pool —
   hero_001 te-en + SpokenWOZ en — correctly do NOT use the toy cast; that is fine, not an issue.)
4. teaches_one_concept: exactly one atomic concept, framed previous -> current -> next.

Return REVIEW_SCHEMA. verdict=PASS only if all four booleans are true. Otherwise NEEDS_FIX with
concrete, cell-numbered issues and the exact fix (especially any factual contradiction — quote the
claim and the conflicting output). Do not modify any file; this is review only.`
}

const results = await pipeline(
  FILES,
  ([id, file]) => agent(reviewPrompt(id, file),
    { label: `review:${id}`, phase: 'Review', agentType: 'general-purpose', schema: REVIEW_SCHEMA })
    .then(r => ({ id, file, r })),
)

const out = results.filter(Boolean).map(x => ({
  id: x.id, file: x.file + '.ipynb',
  verdict: x.r ? x.r.verdict : 'ERROR',
  factual: x.r ? x.r.factual_consistency : false,
  beginner: x.r ? x.r.beginner_proof : false,
  cast: x.r ? x.r.cast_consistent : false,
  one_concept: x.r ? x.r.teaches_one_concept : false,
  severity: x.r ? x.r.severity : 'high',
  issues: x.r && x.r.issues ? x.r.issues : ['review agent returned nothing'],
}))
const needs = out.filter(o => o.verdict !== 'PASS')
log(`reviewed ${out.length}/29 · PASS ${out.length - needs.length} · NEEDS_FIX ${needs.length}`)
return { reviewed: out.length, pass: out.length - needs.length, needs_fix: out }
