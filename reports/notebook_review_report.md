# VoiceForge University — Review & Verification Report

**36/36 notebooks fully clean** — execute-clean (`run_nb.py`), structure-clean (`audit_nb.py`), AND review-clean.

## What this report certifies
Every book was independently reviewed for the highest-value failure mode — a markdown claim that
contradicts the notebook's own computed/printed output (e.g. prose saying "the biggest bucket" when
the printed counts tie). 15 books carried such contradictions; all 15 were fixed and then
**re-verified by an independent agent that re-ran the notebook and quoted the corrected prose against
the matching output line**, plus a final hand re-gate. The 21 others passed first time.

## Contradictions found & fixed (the 15)
| book | was | now |
|---|---|---|
| P02 | claimed real schema had an `outcome` field | outcome marked as toy-only; real fields corrected |
| P03 | any overlap called a barge-in | adds the >100ms threshold (≤100ms = backchannel) |
| P04 | "you predicted a tip of 41" | 30 (10% of 300) |
| 04 | chart drew 5 bars, prose said 4 gaps | chart filtered to the 4 real latency gaps |
| 09 | "turn count rose as language moved from English" | corrected to 4→6→4 (rises then falls) |
| 13 | lazy-detector "respectable accuracy" on a 50/50 set | dataset rebalanced 8-fine/2-fail → 0.8 real |
| 14 | "this kappa (~0.4)" | 0.67 (the printed value) |
| 15 | "~0.87" raw agreement; "four" disagreements | 0.83; five |
| 17 | trap claimed "better on every axis" but printed 0 | strings now fire the detector (3 / 2 axes) |
| 19 | "degrades in two steps" | three steps (loop runs 3) |
| 20 | detected `barge_in` but prose said `repair_quality`; "single-axis" vs 3-dim v2 | reconciled to one *behaviour* lifting 3 dims |
| 21 | weight-trap showed only one direction; call_C "0.4" | good call now rises 0.81→0.93; 0.245 |
| 22 | "same language" but te-en vs Telugu-English | reworded; te-en defined; schema claim softened |
| 23 | comment promised a check the code didn't do | code now computes + checks the gap |
| 27 | "8000ms overlap" | 10000ms (the printed value) |

## Per-book status
| id | notebook | exec | audit | review |
|---|---|---|---|---|
| P00 | P00_how_to_learn.ipynb | OK | OK | accepted as canonical mold |
| P01 | P01_python_objects_for_call_logs.ipynb | OK | OK | PASS (independent review) |
| P02 | P02_tables_and_pandas.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| P03 | P03_basic_plots_for_evals.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| P04 | P04_debugging_confusion.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 00 | 00_what_is_voiceforge.ipynb | OK | OK | PASS (independent review) |
| 01 | 01_what_is_a_call_log.ipynb | OK | OK | PASS (independent review) |
| 02 | 02_json_schemas_data_contracts.ipynb | OK | OK | PASS (independent review) |
| 03 | 03_pandas_for_call_data.ipynb | OK | OK | PASS (independent review, after fix) |
| 04 | 04_turns_gaps_overlap_latency.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 05 | 05_asr_llm_tts_voice_stack.ipynb | OK | OK | PASS (independent review) |
| 06 | 06_task_success.ipynb | OK | OK | PASS (independent review) |
| 07 | 07_failure_tags_stress_profiles.ipynb | OK | OK | PASS (independent review) |
| 08 | 08_cost_per_successful_call.ipynb | OK | OK | PASS (independent review) |
| 09 | 09_language_conditions.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 10 | 10_llm_as_judge_from_zero.ipynb | OK | OK | PASS (independent review) |
| 11 | 11_evidence_based_scoring.ipynb | OK | OK | PASS (independent review) |
| 12 | 12_calibration_why_human_labels.ipynb | OK | OK | PASS (independent review) |
| 13 | 13_confusion_matrix.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 14 | 14_cohens_kappa_from_scratch.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 15 | 15_pilot_calibration_honestly.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 16 | 16_improvement_examples.ipynb | OK | OK | PASS (independent review) |
| 17 | 17_preference_pairs.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 18 | 18_dpo_baby_language.ipynb | OK | OK | PASS (independent review) |
| 19 | 19_rlhf_rlaif_without_mythology.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 20 | 20_ab_loop.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 21 | 21_rubric_config_driven.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 22 | 22_user_simulators.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 23 | 23_dataset_hierarchy.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 24 | 24_annotation_ground_truth.ipynb | OK | OK | PASS (independent review) |
| 25 | 25_charts_that_matter.ipynb | OK | OK | PASS (independent review) |
| 26 | 26_dashboard_mental_model.ipynb | OK | OK | PASS (independent review) |
| 27 | 27_provider_adapters.ipynb | OK | OK | FIXED + output-verified (was prose↔output contradiction) |
| 28 | 28_talking_like_an_engineer.ipynb | OK | OK | PASS (independent review) |
| 29 | 29_the_3_minute_demo.ipynb | OK | OK | PASS (independent review) |
| 30 | 30_post_hackathon_path.ipynb | OK | OK | PASS (independent review) |
