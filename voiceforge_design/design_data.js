window.__DATA__ = {
  "gate_open": true,
  "floor": 40,
  "val": {
    "binary": 45,
    "unsure": 1
  },
  "analytics": {
    "n_calls": 76,
    "success_rate": 0.566,
    "avg_overall": 0.711,
    "timing_coverage": {
      "timed": 46,
      "unmeasured": 30
    },
    "cost_per_successful_call": 0.1188,
    "by_stress_profile": [
      {
        "stress_profile": "unmeasured",
        "n": 30,
        "n_completed": 26,
        "cost": 0.9650000000000005,
        "success_rate": 0.867,
        "cost_per_successful_call": 0.0371
      },
      {
        "stress_profile": "interruption",
        "n": 21,
        "n_completed": 8,
        "cost": 1.965,
        "success_rate": 0.381,
        "cost_per_successful_call": 0.2456
      },
      {
        "stress_profile": "clean",
        "n": 20,
        "n_completed": 8,
        "cost": 1.8496,
        "success_rate": 0.4,
        "cost_per_successful_call": 0.2312
      },
      {
        "stress_profile": "pause_heavy",
        "n": 5,
        "n_completed": 1,
        "cost": 0.33,
        "success_rate": 0.2,
        "cost_per_successful_call": 0.33
      }
    ],
    "failure_clusters": [
      {
        "dimension": "latency_gap",
        "count": 183,
        "example_call_ids": [
          "hero_001",
          "swz_MUL0035",
          "swz_MUL0056",
          "swz_MUL0069",
          "swz_MUL0106"
        ]
      },
      {
        "dimension": "barge_in",
        "count": 107,
        "example_call_ids": [
          "hero_001",
          "swz_MUL0035",
          "swz_MUL0043",
          "swz_MUL0056",
          "swz_MUL0071"
        ]
      }
    ],
    "note": "deterministic eval only (judge dims add in Batch 4); costs estimated, prototype. avg_overall is over TIMED calls only (consistent dim basis) — see timing_coverage."
  },
  "report": {
    "manifest_total": 46,
    "corpus": {
      "n_scored": 76,
      "timing_coverage": {
        "timed": 46,
        "unmeasured": 30
      },
      "success_rate_heuristic": 0.566,
      "cost_per_success_est": 0.1188,
      "failure_event_clusters": [
        {
          "dimension": "latency_gap",
          "count": 183,
          "example_call_ids": [
            "hero_001",
            "swz_MUL0035",
            "swz_MUL0056",
            "swz_MUL0069",
            "swz_MUL0106"
          ]
        },
        {
          "dimension": "barge_in",
          "count": 107,
          "example_call_ids": [
            "hero_001",
            "swz_MUL0035",
            "swz_MUL0043",
            "swz_MUL0056",
            "swz_MUL0071"
          ]
        }
      ]
    },
    "labels": {
      "total": 46,
      "binary": 45,
      "unsure": 1,
      "floor": 40,
      "floor_met": true,
      "distribution": {
        "success": 37,
        "fail": 8,
        "unsure": 1
      }
    },
    "product": {
      "human_success_rate": 0.822,
      "human_successes": 37,
      "human_failures": 8,
      "cost_per_human_success_est": 0.0511,
      "failed_call_spend_est": 0.265,
      "brittle_success_spend_est": 0.185,
      "friction_or_failure_spend_est": 0.7946,
      "friction_or_failure_spend_share": 0.421,
      "brittle_share_of_successes": 0.135,
      "matrix": {
        "n": 45,
        "seamless_success": 25,
        "recovered_success": 7,
        "brittle_success": 5,
        "failure": 8,
        "unsure_excluded": 1
      },
      "fix_first": {
        "phenotype_id": "poor_clarification_or_recovery",
        "affected_calls": 11,
        "estimated_spend_usd": 0.47,
        "modeled_exposure_per_1k_usd": 10.44,
        "evidence_call_ids": [
          "cmd_hi_0000",
          "cmd_hi_0001",
          "cmd_hi_0011",
          "cmd_hi_0015",
          "cmd_hi_0017",
          "cmd_hi_0024",
          "cmd_hi_0028",
          "cmd_hi_0029",
          "cmd_hi_0030",
          "swz_MUL0815",
          "swz_MUL0035"
        ],
        "recommendation": "replace generic re-asks with a targeted clarifying question naming the unclear slot",
        "expected_mechanism": "A targeted question names the unclear slot and lowers the caller's repair burden.",
        "needs_human_review": true,
        "provenance": "single-rater phenotype + estimated prototype cost"
      },
      "caveat": "Human labels are single-rater; costs are estimated prototype values. Per-1,000 exposure is a modeled extrapolation from this slice, not observed savings."
    },
    "calibration": {
      "n": 45,
      "raw_agreement": 0.711,
      "kappa": 0.206,
      "ci95": [
        -0.108,
        0.499
      ],
      "confusion": {
        "h_fail|j_fail": 4,
        "h_fail|j_success": 4,
        "h_success|j_fail": 9,
        "h_success|j_success": 28
      },
      "disagreements": [
        "cmd_hi_0001",
        "cmd_hi_0006",
        "cmd_hi_0007",
        "cmd_hi_0009",
        "cmd_hi_0013",
        "cmd_hi_0014",
        "cmd_hi_0018",
        "cmd_hi_0022",
        "cmd_hi_0024",
        "swz_MUL2483",
        "swz_MUL0247",
        "swz_MUL1560",
        "swz_MUL0035"
      ],
      "disagreements_code_switched": 9,
      "band": "slight",
      "caption": "Slight agreement (Landis–Koch); the 95% CI includes 0 — at n=45 with 82% success prevalence, the prevalence paradox compresses κ. Balanced accuracy 0.63 (Youden's J +0.26) reports the same 45 calls without that imbalance penalty; failure recall 0.50 is the more actionable number for risk surfaces. The reliability axis is NOT language — hi-en 22/31≈71% and English 9/13≈69% are statistically indistinguishable on this sample. The defensible split is annotator confidence (high ≈83% vs medium ≈50%), known only post-annotation — so it supports a second-rater review queue, not an auto-router. Measured, not assumed — a team trusting this judge uncalibrated would be wrong on 13/45 calls and never know."
    },
    "metric_trap": {
      "n": 45,
      "agree": 25,
      "heuristic_agreement": 0.556,
      "missed_successes": 13,
      "false_passes": 7,
      "human_failures": 8,
      "caption": "The completion heuristic — the metric most voice-agent teams ship — agrees with blind human judgment on only 25/45 calls (56%). It missed 13 real successes and passed 7 of 8 real failures. A success-rate dashboard is blind exactly where it costs money.",
      "provenance": "deterministic keyword heuristic (task_completed) vs single-rater blind labels"
    },
    "tags": {
      "positive": {
        "understood_user": 37,
        "adapted_language_well": 35,
        "user_satisfied": 34,
        "completed_or_clear_next_step": 31,
        "handled_confusion_well": 23,
        "easy_to_understand": 21
      },
      "negative": {
        "poor_clarification_or_recovery": 11,
        "missing_or_wrong_information": 10,
        "workflow_or_tool_failed": 10,
        "repeated_or_stuck": 8,
        "misunderstood_user": 6,
        "wrong_language_or_tone": 4,
        "hard_to_understand": 4,
        "user_frustrated": 1
      },
      "context": {
        "multi_step_request": 42,
        "mixed_languages": 40,
        "user_unclear_or_hesitant": 8,
        "transcript_unclear": 8
      },
      "co_occurrence_top": [
        {
          "pair": [
            "mixed_languages",
            "multi_step_request"
          ],
          "n": 38
        },
        {
          "pair": [
            "multi_step_request",
            "understood_user"
          ],
          "n": 34
        },
        {
          "pair": [
            "adapted_language_well",
            "multi_step_request"
          ],
          "n": 33
        },
        {
          "pair": [
            "mixed_languages",
            "understood_user"
          ],
          "n": 32
        },
        {
          "pair": [
            "multi_step_request",
            "user_satisfied"
          ],
          "n": 32
        },
        {
          "pair": [
            "understood_user",
            "user_satisfied"
          ],
          "n": 31
        },
        {
          "pair": [
            "adapted_language_well",
            "mixed_languages"
          ],
          "n": 31
        },
        {
          "pair": [
            "mixed_languages",
            "user_satisfied"
          ],
          "n": 30
        }
      ],
      "caveat": "single-rater exploratory (n=1 annotator) — NOT calibrated"
    },
    "archetypes": {
      "counts": {
        "seamless_success": 25,
        "brittle_success": 5,
        "recovered_success": 7,
        "language_mismatch_failure": 0,
        "intent_or_slot_loss_failure": 3,
        "repair_loop_failure": 0,
        "workflow_failure": 5,
        "ambiguous_or_unassessable": 1
      },
      "derivation": "deterministic from Level-1 outcome + Level-2 tags (precedence: workflow > language > intent/slot > repair-loop); never hand-labeled"
    },
    "representatives": [
      {
        "call_id": "bolna_246cd9f3",
        "human": "success/high",
        "archetype": "recovered_success",
        "tags": [
          "wrong_language_or_tone"
        ],
        "deterministic_failures": [],
        "judge": "success",
        "recommendation": "detect caller language/register in the first 2 turns and switch the response style"
      },
      {
        "call_id": "hero_001",
        "human": "success/high",
        "archetype": "brittle_success",
        "tags": [
          "wrong_language_or_tone"
        ],
        "deterministic_failures": [
          "barge_in",
          "latency_gap"
        ],
        "judge": "success",
        "recommendation": "detect caller language/register in the first 2 turns and switch the response style"
      },
      {
        "call_id": "cmd_hi_0000",
        "human": "fail/medium",
        "archetype": "workflow_failure",
        "tags": [
          "missing_or_wrong_information",
          "poor_clarification_or_recovery",
          "workflow_or_tool_failed"
        ],
        "deterministic_failures": [],
        "judge": "fail",
        "recommendation": "require slot read-back before closing; re-ask for any unfilled required slot"
      },
      {
        "call_id": "cmd_hi_0001",
        "human": "fail/medium",
        "archetype": "intent_or_slot_loss_failure",
        "tags": [
          "missing_or_wrong_information",
          "repeated_or_stuck",
          "poor_clarification_or_recovery"
        ],
        "deterministic_failures": [],
        "judge": "success",
        "recommendation": "require slot read-back before closing; re-ask for any unfilled required slot"
      },
      {
        "call_id": "cmd_hi_0002",
        "human": "success/high",
        "archetype": "seamless_success",
        "tags": [
          "adapted_language_well",
          "user_satisfied",
          "handled_confusion_well",
          "understood_user",
          "completed_or_clear_next_step"
        ],
        "deterministic_failures": [],
        "judge": "success",
        "recommendation": null
      }
    ],
    "improvement_queue": [
      {
        "call_id": "bolna_246cd9f3",
        "human": "success/high",
        "archetype": "recovered_success",
        "evidence_tags": [
          "wrong_language_or_tone"
        ],
        "recommendation": "detect caller language/register in the first 2 turns and switch the response style"
      },
      {
        "call_id": "hero_001",
        "human": "success/high",
        "archetype": "brittle_success",
        "evidence_tags": [
          "wrong_language_or_tone"
        ],
        "recommendation": "detect caller language/register in the first 2 turns and switch the response style"
      },
      {
        "call_id": "cmd_hi_0000",
        "human": "fail/medium",
        "archetype": "workflow_failure",
        "evidence_tags": [
          "missing_or_wrong_information",
          "poor_clarification_or_recovery",
          "workflow_or_tool_failed"
        ],
        "recommendation": "require slot read-back before closing; re-ask for any unfilled required slot"
      },
      {
        "call_id": "cmd_hi_0001",
        "human": "fail/medium",
        "archetype": "intent_or_slot_loss_failure",
        "evidence_tags": [
          "missing_or_wrong_information",
          "repeated_or_stuck",
          "poor_clarification_or_recovery"
        ],
        "recommendation": "require slot read-back before closing; re-ask for any unfilled required slot"
      },
      {
        "call_id": "cmd_hi_0004",
        "human": "fail/medium",
        "archetype": "workflow_failure",
        "evidence_tags": [
          "workflow_or_tool_failed",
          "missing_or_wrong_information",
          "misunderstood_user"
        ],
        "recommendation": "add a tool-failure fallback path (acknowledge, retry once, then offer human handoff)"
      },
      {
        "call_id": "cmd_hi_0011",
        "human": "success/high",
        "archetype": "recovered_success",
        "evidence_tags": [
          "workflow_or_tool_failed",
          "misunderstood_user",
          "poor_clarification_or_recovery"
        ],
        "recommendation": "add a tool-failure fallback path (acknowledge, retry once, then offer human handoff)"
      },
      {
        "call_id": "cmd_hi_0013",
        "human": "success/medium",
        "archetype": "brittle_success",
        "evidence_tags": [
          "missing_or_wrong_information",
          "workflow_or_tool_failed"
        ],
        "recommendation": "require slot read-back before closing; re-ask for any unfilled required slot"
      },
      {
        "call_id": "cmd_hi_0015",
        "human": "fail/medium",
        "archetype": "intent_or_slot_loss_failure",
        "evidence_tags": [
          "missing_or_wrong_information",
          "repeated_or_stuck",
          "poor_clarification_or_recovery",
          "hard_to_understand"
        ],
        "recommendation": "require slot read-back before closing; re-ask for any unfilled required slot"
      },
      {
        "call_id": "cmd_hi_0016",
        "human": "success/high",
        "archetype": "recovered_success",
        "evidence_tags": [
          "repeated_or_stuck",
          "workflow_or_tool_failed"
        ],
        "recommendation": "cap repeats at 2, then rephrase with a concrete example instead of repeating verbatim"
      },
      {
        "call_id": "cmd_hi_0017",
        "human": "success/medium",
        "archetype": "brittle_success",
        "evidence_tags": [
          "repeated_or_stuck",
          "workflow_or_tool_failed",
          "poor_clarification_or_recovery",
          "misunderstood_user"
        ],
        "recommendation": "cap repeats at 2, then rephrase with a concrete example instead of repeating verbatim"
      },
      {
        "call_id": "cmd_hi_0020",
        "human": "success/medium",
        "archetype": "recovered_success",
        "evidence_tags": [
          "missing_or_wrong_information",
          "hard_to_understand"
        ],
        "recommendation": "require slot read-back before closing; re-ask for any unfilled required slot"
      },
      {
        "call_id": "cmd_hi_0022",
        "human": "fail/medium",
        "archetype": "workflow_failure",
        "evidence_tags": [
          "missing_or_wrong_information",
          "workflow_or_tool_failed",
          "repeated_or_stuck",
          "misunderstood_user"
        ],
        "recommendation": "require slot read-back before closing; re-ask for any unfilled required slot"
      },
      {
        "call_id": "cmd_hi_0024",
        "human": "fail/medium",
        "archetype": "workflow_failure",
        "evidence_tags": [
          "workflow_or_tool_failed",
          "poor_clarification_or_recovery",
          "misunderstood_user"
        ],
        "recommendation": "add a tool-failure fallback path (acknowledge, retry once, then offer human handoff)"
      },
      {
        "call_id": "cmd_hi_0028",
        "human": "success/medium",
        "archetype": "brittle_success",
        "evidence_tags": [
          "repeated_or_stuck",
          "hard_to_understand",
          "missing_or_wrong_information",
          "poor_clarification_or_recovery"
        ],
        "recommendation": "cap repeats at 2, then rephrase with a concrete example instead of repeating verbatim"
      },
      {
        "call_id": "cmd_hi_0029",
        "human": "fail/high",
        "archetype": "workflow_failure",
        "evidence_tags": [
          "poor_clarification_or_recovery",
          "workflow_or_tool_failed",
          "misunderstood_user",
          "repeated_or_stuck",
          "missing_or_wrong_information",
          "user_frustrated"
        ],
        "recommendation": "replace generic re-asks with a targeted clarifying question naming the unclear slot"
      },
      {
        "call_id": "cmd_hi_0030",
        "human": "success/medium",
        "archetype": "brittle_success",
        "evidence_tags": [
          "poor_clarification_or_recovery"
        ],
        "recommendation": "replace generic re-asks with a targeted clarifying question naming the unclear slot"
      },
      {
        "call_id": "cmd_hi_0031",
        "human": "success/medium",
        "archetype": "recovered_success",
        "evidence_tags": [
          "missing_or_wrong_information",
          "repeated_or_stuck",
          "workflow_or_tool_failed"
        ],
        "recommendation": "require slot read-back before closing; re-ask for any unfilled required slot"
      },
      {
        "call_id": "swz_MUL0815",
        "human": "unsure/high",
        "archetype": "ambiguous_or_unassessable",
        "evidence_tags": [
          "poor_clarification_or_recovery"
        ],
        "recommendation": "replace generic re-asks with a targeted clarifying question naming the unclear slot"
      },
      {
        "call_id": "swz_MUL1560",
        "human": "success/medium",
        "archetype": "recovered_success",
        "evidence_tags": [
          "wrong_language_or_tone"
        ],
        "recommendation": "detect caller language/register in the first 2 turns and switch the response style"
      },
      {
        "call_id": "swz_MUL0035",
        "human": "success/medium",
        "archetype": "recovered_success",
        "evidence_tags": [
          "wrong_language_or_tone",
          "hard_to_understand",
          "poor_clarification_or_recovery"
        ],
        "recommendation": "detect caller language/register in the first 2 turns and switch the response style"
      }
    ],
    "judge_run": {
      "mode": "full",
      "status": "complete",
      "model": "gemini-3.1-flash-lite",
      "temperature": 0,
      "rubric_hash": "c1cc81415e230e74",
      "judge_prompt_hash": "079d57698a629192",
      "labels_csv_sha256": "b3884f9ede7d753a18a5011801c25ddc930d1543e7858736ce4d08c328c25338",
      "manifest_sha256": "aec4ba49000c9f4fdfa203cfca4bc787b71004abb47e4a7eff899175446cae33",
      "n_calls": 46,
      "expected_judgments": 276,
      "validated_judgments": 276,
      "cache_hits": 178,
      "failures": 0,
      "failed_calls": [],
      "binary_rule": "dedicated outcome judgment per call (temperature 0, JSON, evidence-cited); label in {success,fail}; same question the blind annotator answered. NOT derived from the 5 semantic dims; kappa calibrates THIS judgment only — the semantic dims remain uncalibrated diagnostics.",
      "started_at": "2026-06-12T22:22:37+05:30",
      "checkpointed_at": "2026-06-12T22:35:52+05:30",
      "finished_at": "2026-06-12T22:35:52+05:30",
      "elapsed_s": 795.5
    }
  },
  "judge_run": {
    "mode": "full",
    "status": "complete",
    "model": "gemini-3.1-flash-lite",
    "temperature": 0,
    "rubric_hash": "c1cc81415e230e74",
    "judge_prompt_hash": "079d57698a629192",
    "labels_csv_sha256": "b3884f9ede7d753a18a5011801c25ddc930d1543e7858736ce4d08c328c25338",
    "manifest_sha256": "aec4ba49000c9f4fdfa203cfca4bc787b71004abb47e4a7eff899175446cae33",
    "n_calls": 46,
    "expected_judgments": 276,
    "validated_judgments": 276,
    "cache_hits": 178,
    "failures": 0,
    "failed_calls": [],
    "binary_rule": "dedicated outcome judgment per call (temperature 0, JSON, evidence-cited); label in {success,fail}; same question the blind annotator answered. NOT derived from the 5 semantic dims; kappa calibrates THIS judgment only — the semantic dims remain uncalibrated diagnostics.",
    "started_at": "2026-06-12T22:22:37+05:30",
    "checkpointed_at": "2026-06-12T22:35:52+05:30",
    "finished_at": "2026-06-12T22:35:52+05:30",
    "elapsed_s": 795.5
  },
  "sponsor_proof": {
    "agent_id": "199b03e7-06c6-40e5-8741-37c5c9598061",
    "fetched_at": "2026-06-12T22:19:32+05:30",
    "synthesizer_provider": "cartesia",
    "cartesia_voice": "Devansh",
    "cartesia_model": "sonic-3"
  },
  "rows": [
    {
      "id": "hero_001",
      "source": "hero",
      "lang": "te-en",
      "profile": "interruption",
      "wf": "appliance_service_booking",
      "turns": 12,
      "outcome": true,
      "overall": 0.803,
      "dims": [
        {
          "name": "barge_in",
          "type": "deterministic",
          "score": 0.66,
          "reason": "agent interrupted the caller 1x (overlap 800ms)",
          "evidence_turn_ids": [
            "t2",
            "t3"
          ]
        },
        {
          "name": "latency_gap",
          "type": "deterministic",
          "score": 0.75,
          "reason": "median 400.0ms / p90 1620ms; 1/4 responses laggy (>800ms)",
          "evidence_turn_ids": [
            "t7"
          ]
        },
        {
          "name": "task_completion",
          "type": "deterministic",
          "score": 1.0,
          "reason": "captured 3/3 required fields (heuristic from goal/workflow)",
          "evidence_turn_ids": []
        }
      ],
      "failures": [
        {
          "at_ms": 15844,
          "dimension": "barge_in",
          "label": "agent barge-in",
          "detail": "800ms overlap",
          "evidence_turn_ids": [
            "t2",
            "t3"
          ],
          "call_id": "hero_001",
          "origin": "deterministic"
        },
        {
          "at_ms": 48519,
          "dimension": "latency_gap",
          "label": "response latency",
          "detail": "1,620ms gap",
          "evidence_turn_ids": [
            "t6",
            "t7"
          ],
          "call_id": "hero_001",
          "origin": "deterministic"
        }
      ],
      "transcript": [
        {
          "id": "t1",
          "s": "agent",
          "x": "Hi, this is the service desk for QuickCool appliance care. I can help you book a technician visit. May I know which area you're calling from?"
        },
        {
          "id": "t2",
          "s": "user",
          "x": "haan hello... area ante... Madhapur side anukunta... near the, er... metro station."
        },
        {
          "id": "t3",
          "s": "agent",
          "x": "I need your complete address with pincode, landmark and door number before we can proceed any further with this booking request."
        },
        {
          "id": "t4",
          "s": "user",
          "x": "ayyo okay okay... full address kavala? it's plot 42, ante... near metro pillar number... I don't remember exactly ya."
        },
        {
          "id": "t5",
          "s": "agent",
          "x": "Thank you. And what appliance needs servicing today?"
        },
        {
          "id": "t6",
          "s": "user",
          "x": "AC unit... cooling sariga ledu, very weak airflow vastundi."
        },
        {
          "id": "t7",
          "s": "agent",
          "x": "Got it — an AC cooling issue. Would you prefer a morning or an evening visit tomorrow?"
        },
        {
          "id": "t8",
          "s": "user",
          "x": "morning better... around ten ayite manchidi."
        },
        {
          "id": "t9",
          "s": "agent",
          "x": "Perfect, tomorrow morning around ten AM. Could I get a callback number?"
        },
        {
          "id": "t10",
          "s": "user",
          "x": "nine eight four nine two... double five... zero three one."
        },
        {
          "id": "t11",
          "s": "agent",
          "x": "Thank you. Your booking is confirmed for tomorrow at ten AM in Madhapur. The technician will call you before arriving."
        },
        {
          "id": "t12",
          "s": "user",
          "x": "sare, thanks ya."
        }
      ],
      "judge": {
        "dims": [
          {
            "name": "language_match",
            "type": "judge",
            "score": 0.2,
            "reason": "The agent consistently ignores the user's code-switching into Telugu and English, responding exclusively in English despite the user's clear preference for a bilingual conversational style.",
            "evidence_turn_ids": [
              "t2",
              "t3",
              "t4",
              "t5",
              "t6",
              "t7",
              "t8"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "faithfulness",
            "type": "judge",
            "score": 1.0,
            "reason": "The agent accurately captured the location, appliance issue, and appointment time provided by the user without introducing any unsupported information.",
            "evidence_turn_ids": [
              "t2",
              "t4",
              "t6",
              "t8",
              "t10",
              "t11"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "repair_quality",
            "type": "judge",
            "score": 0.0,
            "reason": "In turn 3, the agent ignored the user's partial address information and instead issued an over-demanding request for the full address, pincode, and door number without acknowledging the provided location details.",
            "evidence_turn_ids": [
              "t3"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "conciseness",
            "type": "judge",
            "score": 1.0,
            "reason": "The agent maintains a professional, direct tone throughout the interaction, avoiding unnecessary filler or repetitive explanations while efficiently gathering required information.",
            "evidence_turn_ids": [
              "t1",
              "t3",
              "t5",
              "t7",
              "t9",
              "t11"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "user_frustration",
            "type": "judge",
            "score": 1.0,
            "reason": "The caller remains cooperative and polite throughout the interaction, providing necessary details without expressing irritation or entering repair loops.",
            "evidence_turn_ids": [
              "t12"
            ],
            "provenance": "uncalibrated"
          }
        ],
        "binary": {
          "label": "success",
          "reason": "The agent successfully collected all necessary information including the address, appliance issue, preferred time, and contact number to confirm the service booking.",
          "evidence_turn_ids": [
            "t3",
            "t5",
            "t7",
            "t9",
            "t11"
          ],
          "rule": "dedicated outcome judgment per call (temperature 0, JSON, evidence-cited); label in {success,fail}; same question the blind annotator answered. NOT derived from the 5 semantic dims; kappa calibrates THIS judgment only — the semantic dims remain uncalibrated diagnostics.",
          "provenance": "pending calibration (binary)"
        }
      },
      "in_manifest": true,
      "human": {
        "label": "success",
        "confidence": "high",
        "positive": [
          "understood_user",
          "completed_or_clear_next_step",
          "user_satisfied"
        ],
        "negative": [
          "wrong_language_or_tone"
        ],
        "context": [
          "mixed_languages"
        ]
      }
    },
    {
      "id": "cmd_hi_0000",
      "source": "code_mixed_dialog",
      "lang": "hi-en",
      "profile": "unmeasured",
      "wf": "restaurant_reservation",
      "turns": 11,
      "outcome": true,
      "overall": 1.0,
      "dims": [
        {
          "name": "task_completion",
          "type": "deterministic",
          "score": 1.0,
          "reason": "captured 4/4 required fields (heuristic from goal/workflow)",
          "evidence_turn_ids": []
        }
      ],
      "failures": [],
      "transcript": [
        {
          "id": "t1",
          "s": "agent",
          "x": "Hello , Cambridge restaurant system mein aapka swagat hai . Aap pa sakte hai restaurant by area , price range ya food type . Aap ko kaise help kar sakta hu main ?"
        },
        {
          "id": "t2",
          "s": "user",
          "x": "south part of town meh expensive restaurant hai"
        },
        {
          "id": "t3",
          "s": "agent",
          "x": "Aap kaunse type ka food lene chahege ?"
        },
        {
          "id": "t4",
          "s": "user",
          "x": "koi bhi"
        },
        {
          "id": "t5",
          "s": "agent",
          "x": "town ke south mein good luck chinese food takeaway achha restaurant hai jo chinese food serve karta hai"
        },
        {
          "id": "t6",
          "s": "user",
          "x": "pata"
        },
        {
          "id": "t7",
          "s": "agent",
          "x": "jarur , the good luck chinese food takeaway the_good_luck_chinese_food_takeaway_address pe hai"
        },
        {
          "id": "t8",
          "s": "user",
          "x": "food ki type"
        },
        {
          "id": "t9",
          "s": "agent",
          "x": "good luck chinese food takeaway ek accha place hain south of town mein jo expensive price range mein hain"
        },
        {
          "id": "t10",
          "s": "user",
          "x": "Thank you , good bye ."
        },
        {
          "id": "t11",
          "s": "agent",
          "x": "Welcome , alvida"
        }
      ],
      "judge": {
        "dims": [
          {
            "name": "language_match",
            "type": "judge",
            "score": 1.0,
            "reason": "The agent consistently maintains a natural Hinglish code-switching style throughout the conversation, mirroring the user's language patterns.",
            "evidence_turn_ids": [
              "t1",
              "t3",
              "t5",
              "t7",
              "t9",
              "t11"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "faithfulness",
            "type": "judge",
            "score": 0.0,
            "reason": "The agent hallucinated that the restaurant is in the expensive price range, whereas the user never specified a price range and the system did not verify this attribute.",
            "evidence_turn_ids": [
              "t2",
              "t9"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "repair_quality",
            "type": "judge",
            "score": 0.0,
            "reason": "The agent failed to address the user's specific request for food type in turn 8, instead repeating information already provided in turn 9, which constitutes a derailment.",
            "evidence_turn_ids": [
              "t8",
              "t9"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "conciseness",
            "type": "judge",
            "score": 0.6,
            "reason": "The agent provides redundant information in turn 9 by repeating details already established in turn 5, though it remains generally functional.",
            "evidence_turn_ids": [
              "t5",
              "t9"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "user_frustration",
            "type": "judge",
            "score": 0.5,
            "reason": "The user exhibits frustration through repetitive, clipped queries in turns 6 and 8 due to the agent's failure to provide the requested food type, though they eventually conclude the call politely.",
            "evidence_turn_ids": [
              "t6",
              "t8",
              "t10"
            ],
            "provenance": "uncalibrated"
          }
        ],
        "binary": {
          "label": "fail",
          "reason": "The agent failed to provide an expensive restaurant in the south part of town, as the suggested restaurant is not categorized as expensive.",
          "evidence_turn_ids": [
            "t2",
            "t5",
            "t9"
          ],
          "rule": "dedicated outcome judgment per call (temperature 0, JSON, evidence-cited); label in {success,fail}; same question the blind annotator answered. NOT derived from the 5 semantic dims; kappa calibrates THIS judgment only — the semantic dims remain uncalibrated diagnostics.",
          "provenance": "pending calibration (binary)"
        }
      },
      "in_manifest": true,
      "human": {
        "label": "fail",
        "confidence": "medium",
        "positive": [
          "completed_or_clear_next_step"
        ],
        "negative": [
          "missing_or_wrong_information",
          "poor_clarification_or_recovery",
          "workflow_or_tool_failed"
        ],
        "context": [
          "multi_step_request",
          "mixed_languages"
        ]
      }
    },
    {
      "id": "cmd_hi_0001",
      "source": "code_mixed_dialog",
      "lang": "hi-en",
      "profile": "unmeasured",
      "wf": "restaurant_reservation",
      "turns": 17,
      "outcome": true,
      "overall": 1.0,
      "dims": [
        {
          "name": "task_completion",
          "type": "deterministic",
          "score": 1.0,
          "reason": "captured 4/4 required fields (heuristic from goal/workflow)",
          "evidence_turn_ids": []
        }
      ],
      "failures": [],
      "transcript": [
        {
          "id": "t1",
          "s": "agent",
          "x": "Hello , Cambridge restaurant system mein aapka swagat hai . Aap pa sakte hai restaurant by area , price range ya food type . Aap ko kaise help kar sakta hu main ?"
        },
        {
          "id": "t2",
          "s": "user",
          "x": "west part of town mein lebanese restaurant"
        },
        {
          "id": "t3",
          "s": "agent",
          "x": "Aap kaunse type ka food lene chahege ?"
        },
        {
          "id": "t4",
          "s": "user",
          "x": "lebanese"
        },
        {
          "id": "t5",
          "s": "agent",
          "x": "sorry town ki west me koi lebanese restaurant nahin hai"
        },
        {
          "id": "t6",
          "s": "user",
          "x": "shehar ke west me thai food"
        },
        {
          "id": "t7",
          "s": "agent",
          "x": "sala_thong ek achha restaurant hai nagar ke west bhaag mein jo thai khana serve karta hai"
        },
        {
          "id": "t8",
          "s": "user",
          "x": "pata"
        },
        {
          "id": "t9",
          "s": "agent",
          "x": "Bilkul , sala_thong sala_thong_address par hai"
        },
        {
          "id": "t10",
          "s": "user",
          "x": "phone number"
        },
        {
          "id": "t11",
          "s": "agent",
          "x": "sala_thong ka phone number hai sala_thong_phone"
        },
        {
          "id": "t12",
          "s": "user",
          "x": "price range"
        },
        {
          "id": "t13",
          "s": "agent",
          "x": "kya main aapki aur kuch madad kar sakta hu ?"
        },
        {
          "id": "t14",
          "s": "user",
          "x": "price range kya hai"
        },
        {
          "id": "t15",
          "s": "agent",
          "x": "sala_thong expensive range mein hai"
        },
        {
          "id": "t16",
          "s": "user",
          "x": "Thank you , good bye ."
        },
        {
          "id": "t17",
          "s": "agent",
          "x": "Welcome , alvida"
        }
      ],
      "judge": {
        "dims": [
          {
            "name": "language_match",
            "type": "judge",
            "score": 1.0,
            "reason": "The agent consistently maintains a natural Hinglish code-switching style throughout the conversation, matching the user's language usage perfectly.",
            "evidence_turn_ids": [
              "t1",
              "t3",
              "t5",
              "t7",
              "t9",
              "t11",
              "t13",
              "t15",
              "t17"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "faithfulness",
            "type": "judge",
            "score": 1.0,
            "reason": "The agent correctly identified the restaurant, address, phone number, and price range based on the user's request without introducing any unsupported information.",
            "evidence_turn_ids": [
              "t7",
              "t9",
              "t11",
              "t15"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "repair_quality",
            "type": "judge",
            "score": 0.0,
            "reason": "The agent failed to acknowledge the user's initial request for a Lebanese restaurant in the west part of town, instead asking for the food type again despite it being clearly stated in the previous turn.",
            "evidence_turn_ids": [
              "t2",
              "t3"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "conciseness",
            "type": "judge",
            "score": 0.6,
            "reason": "The agent fails to acknowledge the user's specific request for price range in turn 12, forcing the user to repeat the question, and repeats the restaurant name unnecessarily in turn 9.",
            "evidence_turn_ids": [
              "t9",
              "t13"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "user_frustration",
            "type": "judge",
            "score": 1.0,
            "reason": "The user remains calm and polite throughout the interaction, successfully obtaining the requested information despite a minor clarification loop, and concludes with a polite thank you.",
            "evidence_turn_ids": [
              "t16"
            ],
            "provenance": "uncalibrated"
          }
        ],
        "binary": {
          "label": "success",
          "reason": "The agent successfully provided the restaurant name, address, phone number, and price range for a Thai restaurant in the west part of town as requested by the user.",
          "evidence_turn_ids": [
            "t7",
            "t9",
            "t11",
            "t15"
          ],
          "rule": "dedicated outcome judgment per call (temperature 0, JSON, evidence-cited); label in {success,fail}; same question the blind annotator answered. NOT derived from the 5 semantic dims; kappa calibrates THIS judgment only — the semantic dims remain uncalibrated diagnostics.",
          "provenance": "pending calibration (binary)"
        }
      },
      "in_manifest": true,
      "human": {
        "label": "fail",
        "confidence": "medium",
        "positive": [
          "understood_user"
        ],
        "negative": [
          "missing_or_wrong_information",
          "repeated_or_stuck",
          "poor_clarification_or_recovery"
        ],
        "context": [
          "mixed_languages",
          "multi_step_request",
          "user_unclear_or_hesitant"
        ]
      }
    },
    {
      "id": "cmd_hi_0002",
      "source": "code_mixed_dialog",
      "lang": "hi-en",
      "profile": "unmeasured",
      "wf": "restaurant_reservation",
      "turns": 15,
      "outcome": true,
      "overall": 1.0,
      "dims": [
        {
          "name": "task_completion",
          "type": "deterministic",
          "score": 1.0,
          "reason": "captured 4/4 required fields (heuristic from goal/workflow)",
          "evidence_turn_ids": []
        }
      ],
      "failures": [],
      "transcript": [
        {
          "id": "t1",
          "s": "agent",
          "x": "Hello , Cambridge restaurant system mein aapka swagat hai . Aap pa sakte hai restaurant by area , price range ya food type . Aap ko kaise help kar sakta hu main ? Kya aap cheap , moderate , ya expensive price range mein kuchh pasand karenge ?"
        },
        {
          "id": "t2",
          "s": "user",
          "x": "cheap"
        },
        {
          "id": "t3",
          "s": "agent",
          "x": "aapke mind me town ka kaun sa part hai ?"
        },
        {
          "id": "t4",
          "s": "user",
          "x": "pata nahi per kya ye vegetarian khana hai"
        },
        {
          "id": "t5",
          "s": "agent",
          "x": "Sorry cheap price range me koi vegetarian restaurant nahi hai"
        },
        {
          "id": "t6",
          "s": "user",
          "x": "aur fir indian me kya hain"
        },
        {
          "id": "t7",
          "s": "agent",
          "x": "the_missing_sock ek achha restaurant hai nagar ke east bhaag mein jo international khana serve karta hai"
        },
        {
          "id": "t8",
          "s": "user",
          "x": "cheap indian khana"
        },
        {
          "id": "t9",
          "s": "agent",
          "x": "mahal_of_cambridge ek achha restaurant hai nagar ke centre bhaag mein jo indian khana serve karta hai"
        },
        {
          "id": "t10",
          "s": "user",
          "x": "cheap price range me"
        },
        {
          "id": "t11",
          "s": "agent",
          "x": "mahal_of_cambridge cheap range mein hai"
        },
        {
          "id": "t12",
          "s": "user",
          "x": "kya mujhe address mil sakta hai"
        },
        {
          "id": "t13",
          "s": "agent",
          "x": "Bilkul , mahal_of_cambridge mahal_of_cambridge_address par hai"
        },
        {
          "id": "t14",
          "s": "user",
          "x": "Thank you , good bye ."
        },
        {
          "id": "t15",
          "s": "agent",
          "x": "Welcome , alvida"
        }
      ],
      "judge": {
        "dims": [
          {
            "name": "language_match",
            "type": "judge",
            "score": 1.0,
            "reason": "The agent consistently maintains a natural Hinglish code-switching style throughout the conversation, matching the user's language input perfectly.",
            "evidence_turn_ids": [
              "t1",
              "t3",
              "t5",
              "t7",
              "t9",
              "t11",
              "t13",
              "t15"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "faithfulness",
            "type": "judge",
            "score": 0.0,
            "reason": "The agent hallucinates that 'mahal_of_cambridge' is in the 'cheap' price range in turn 11, despite the system database typically classifying it as moderate or expensive, and it fails to provide a valid address in turn 13.",
            "evidence_turn_ids": [
              "t11",
              "t13"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "repair_quality",
            "type": "judge",
            "score": 1.0,
            "reason": "The agent successfully identified the user's constraints throughout the conversation and provided relevant information without needing clarification, as the user's requests were clear.",
            "evidence_turn_ids": [
              "t1",
              "t2",
              "t3",
              "t4",
              "t5",
              "t6",
              "t7",
              "t8",
              "t9",
              "t10",
              "t11",
              "t12",
              "t13"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "conciseness",
            "type": "judge",
            "score": 0.7,
            "reason": "The agent is generally concise, but the initial greeting is overly verbose by listing all search criteria and price options simultaneously, and turn 13 is slightly redundant by repeating the restaurant name.",
            "evidence_turn_ids": [
              "t1",
              "t13"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "user_frustration",
            "type": "judge",
            "score": 1.0,
            "reason": "The caller maintains a polite and cooperative tone throughout the interaction, successfully resolving their query without any signs of irritation or repetitive repair loops.",
            "evidence_turn_ids": [
              "t14"
            ],
            "provenance": "uncalibrated"
          }
        ],
        "binary": {
          "label": "success",
          "reason": "The agent successfully identified a restaurant that met the user's criteria for price and cuisine and provided the requested address.",
          "evidence_turn_ids": [
            "t8",
            "t9",
            "t10",
            "t11",
            "t12",
            "t13"
          ],
          "rule": "dedicated outcome judgment per call (temperature 0, JSON, evidence-cited); label in {success,fail}; same question the blind annotator answered. NOT derived from the 5 semantic dims; kappa calibrates THIS judgment only — the semantic dims remain uncalibrated diagnostics.",
          "provenance": "pending calibration (binary)"
        }
      },
      "in_manifest": true,
      "human": {
        "label": "success",
        "confidence": "high",
        "positive": [
          "adapted_language_well",
          "user_satisfied",
          "handled_confusion_well",
          "understood_user",
          "completed_or_clear_next_step"
        ],
        "negative": [],
        "context": [
          "mixed_languages",
          "multi_step_request"
        ]
      }
    },
    {
      "id": "swz_MUL0035",
      "source": "spokenwoz",
      "lang": "en",
      "profile": "interruption",
      "wf": "attraction+profile+train",
      "turns": 28,
      "outcome": false,
      "overall": 0.547,
      "dims": [
        {
          "name": "barge_in",
          "type": "deterministic",
          "score": 0.66,
          "reason": "agent interrupted the caller 1x (overlap 580ms)",
          "evidence_turn_ids": [
            "t17",
            "t18"
          ]
        },
        {
          "name": "latency_gap",
          "type": "deterministic",
          "score": 0.538,
          "reason": "median 800ms / p90 1410ms; 6/13 responses laggy (>800ms)",
          "evidence_turn_ids": [
            "t6",
            "t8",
            "t10",
            "t22",
            "t24",
            "t26"
          ]
        },
        {
          "name": "task_completion",
          "type": "deterministic",
          "score": 0.444,
          "reason": "captured 4/9 required fields (heuristic from goal/workflow)",
          "evidence_turn_ids": []
        }
      ],
      "failures": [
        {
          "at_ms": 7250,
          "dimension": "barge_in",
          "label": "user barge-in",
          "detail": "2220ms overlap",
          "evidence_turn_ids": [
            "t2",
            "t3"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 18460,
          "dimension": "barge_in",
          "label": "user barge-in",
          "detail": "200ms overlap",
          "evidence_turn_ids": [
            "t4",
            "t5"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 23770,
          "dimension": "latency_gap",
          "label": "response latency",
          "detail": "850ms gap",
          "evidence_turn_ids": [
            "t5",
            "t6"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 43900,
          "dimension": "latency_gap",
          "label": "response latency",
          "detail": "1,750ms gap",
          "evidence_turn_ids": [
            "t7",
            "t8"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 51610,
          "dimension": "barge_in",
          "label": "user barge-in",
          "detail": "290ms overlap",
          "evidence_turn_ids": [
            "t8",
            "t9"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 55110,
          "dimension": "latency_gap",
          "label": "response latency",
          "detail": "1,410ms gap",
          "evidence_turn_ids": [
            "t9",
            "t10"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 94380,
          "dimension": "barge_in",
          "label": "user barge-in",
          "detail": "400ms overlap",
          "evidence_turn_ids": [
            "t14",
            "t15"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 104220,
          "dimension": "barge_in",
          "label": "user barge-in",
          "detail": "160ms overlap",
          "evidence_turn_ids": [
            "t16",
            "t17"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 104620,
          "dimension": "barge_in",
          "label": "agent barge-in",
          "detail": "580ms overlap",
          "evidence_turn_ids": [
            "t17",
            "t18"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 129600,
          "dimension": "latency_gap",
          "label": "response latency",
          "detail": "870ms gap",
          "evidence_turn_ids": [
            "t21",
            "t22"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 145880,
          "dimension": "latency_gap",
          "label": "response latency",
          "detail": "1,210ms gap",
          "evidence_turn_ids": [
            "t23",
            "t24"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 157450,
          "dimension": "latency_gap",
          "label": "response latency",
          "detail": "950ms gap",
          "evidence_turn_ids": [
            "t25",
            "t26"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        },
        {
          "at_ms": 160080,
          "dimension": "barge_in",
          "label": "user barge-in",
          "detail": "110ms overlap",
          "evidence_turn_ids": [
            "t26",
            "t27"
          ],
          "call_id": "swz_MUL0035",
          "origin": "deterministic"
        }
      ],
      "transcript": [
        {
          "id": "t1",
          "s": "user",
          "x": "yeah ."
        },
        {
          "id": "t2",
          "s": "agent",
          "x": "i customer service and my sister ."
        },
        {
          "id": "t3",
          "s": "user",
          "x": "i i think .  uh , could you please assist me in looking for a train , please ."
        },
        {
          "id": "t4",
          "s": "agent",
          "x": "no problem . where are you departing from , where are you going to ."
        },
        {
          "id": "t5",
          "s": "user",
          "x": "um it should head to lift and should depart from courage ."
        },
        {
          "id": "t6",
          "s": "agent",
          "x": "the problem cambridge and on any particular day or time ."
        },
        {
          "id": "t7",
          "s": "user",
          "x": "um it should leave on thursday and should arrive .  roughly brief .  15 minutes of the um , 9 30 pm ."
        },
        {
          "id": "t8",
          "s": "agent",
          "x": "okay . and 21 . okay , let me check a look on the system . give me a second ."
        },
        {
          "id": "t9",
          "s": "user",
          "x": "okay , not a problem ."
        },
        {
          "id": "t10",
          "s": "agent",
          "x": "okay . is it around 21 . um okay , this one option we should be doing . 20 r 0 folder how much is this ."
        },
        {
          "id": "t11",
          "s": "user",
          "x": "okay . um , could you please assist me um with making a booking for me and to my other friends ."
        },
        {
          "id": "t12",
          "s": "agent",
          "x": "okay , no problem . or i don't . just to complete the booking , i will need your id number , please ."
        },
        {
          "id": "t13",
          "s": "user",
          "x": "okay . um , it's 1 0 , 8 .  8 1 7 0 2 5 ."
        },
        {
          "id": "t14",
          "s": "agent",
          "x": "okay , so that is 1 0 , 8 , 8 1 . 7 0 2 5 going ."
        },
        {
          "id": "t15",
          "s": "user",
          "x": "and then afterwards followed , followed by 2 0 . 5 , 6 0 , 0 , 6 ."
        },
        {
          "id": "t16",
          "s": "agent",
          "x": "okay , that's 2 0 . 5 , 7 0 0 6 all right , got it ."
        },
        {
          "id": "t17",
          "s": "user",
          "x": "yes ."
        },
        {
          "id": "t18",
          "s": "agent",
          "x": "3 ."
        },
        {
          "id": "t19",
          "s": "user",
          "x": "um could you also let me in looking for places to go to mint ali ."
        },
        {
          "id": "t20",
          "s": "agent",
          "x": "okay , no prompt anything in specific you're looking at ."
        },
        {
          "id": "t21",
          "s": "user",
          "x": "um it should be in a type of a college and should be located in the central part of ."
        },
        {
          "id": "t22",
          "s": "agent",
          "x": "college there . okay . um . okay , i think i found a good option , which would be the . downing college ."
        },
        {
          "id": "t23",
          "s": "user",
          "x": "okay , that's totally fine . can you please provide me with a poisoned , please ."
        },
        {
          "id": "t24",
          "s": "agent",
          "x": "okay , the post code for downloading college . c b2 1 dk a dq sorry ."
        },
        {
          "id": "t25",
          "s": "user",
          "x": "okay . um thank you very much for that ."
        },
        {
          "id": "t26",
          "s": "agent",
          "x": "okay , no problem . anything else i can help you ."
        },
        {
          "id": "t27",
          "s": "user",
          "x": "i know that will be all for me . thank you very ."
        },
        {
          "id": "t28",
          "s": "agent",
          "x": "again , i said think of all in every day ."
        }
      ],
      "judge": {
        "dims": [
          {
            "name": "language_match",
            "type": "judge",
            "score": 1.0,
            "reason": "The agent consistently communicates in English throughout the interaction, matching the language used by the user.",
            "evidence_turn_ids": [
              "t2",
              "t4",
              "t6",
              "t8",
              "t10",
              "t12",
              "t14",
              "t16",
              "t18",
              "t20",
              "t22",
              "t24",
              "t26",
              "t28"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "faithfulness",
            "type": "judge",
            "score": 0.2,
            "reason": "The agent repeatedly hallucinates information, including misinterpreting the user's ID number, mishearing the destination city, and generating nonsensical phrases.",
            "evidence_turn_ids": [
              "t2",
              "t6",
              "t10",
              "t14",
              "t16",
              "t28"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "repair_quality",
            "type": "judge",
            "score": 0.0,
            "reason": "The agent incorrectly transcribed the user's ID number in turn 16 and failed to verify or repair the discrepancy, leading to an inaccurate record of the user's information.",
            "evidence_turn_ids": [
              "t15",
              "t16"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "conciseness",
            "type": "judge",
            "score": 0.3,
            "reason": "The agent frequently uses filler words, repeats information incorrectly, and struggles with coherent sentence structure throughout the conversation.",
            "evidence_turn_ids": [
              "t2",
              "t6",
              "t10",
              "t14",
              "t16",
              "t24",
              "t28"
            ],
            "provenance": "uncalibrated"
          },
          {
            "name": "user_frustration",
            "type": "judge",
            "score": 1.0,
            "reason": "The user remains polite and cooperative throughout the interaction, providing necessary information without expressing frustration despite the agent's occasional speech recognition errors.",
            "evidence_turn_ids": [
              "t9",
              "t25",
              "t27"
            ],
            "provenance": "uncalibrated"
          }
        ],
        "binary": {
          "label": "fail",
          "reason": "The agent failed to confirm the train booking and did not provide a reference number, leaving the primary task of booking the train incomplete.",
          "evidence_turn_ids": [
            "t11",
            "t12",
            "t13",
            "t14",
            "t15",
            "t16",
            "t17",
            "t18"
          ],
          "rule": "dedicated outcome judgment per call (temperature 0, JSON, evidence-cited); label in {success,fail}; same question the blind annotator answered. NOT derived from the 5 semantic dims; kappa calibrates THIS judgment only — the semantic dims remain uncalibrated diagnostics.",
          "provenance": "pending calibration (binary)"
        }
      },
      "in_manifest": true,
      "human": {
        "label": "success",
        "confidence": "medium",
        "positive": [
          "handled_confusion_well",
          "adapted_language_well",
          "completed_or_clear_next_step"
        ],
        "negative": [
          "wrong_language_or_tone",
          "hard_to_understand",
          "poor_clarification_or_recovery"
        ],
        "context": [
          "transcript_unclear",
          "mixed_languages",
          "multi_step_request"
        ]
      }
    }
  ],
  "fixture": false,
  "design_handoff": true,
  "privacy_note": "Aggregates are real. Transcripts are limited to public-dataset or constructed calls; the real Bolna transcript is intentionally excluded."
};
