# Timing Threshold Sensitivity - Robustness Audit (Agent 3)

> **ROBUSTNESS, NOT CORRECTNESS. The TIMED slice (n=46) has NO human failure labels; the human-fail calls are the text-only code_mixed_dialog calls, which are 'unmeasured' (no timing) and produce ZERO timing events. Timing events therefore CANNOT be correlated with binary failure in this slice. We measure only sensitivity of the event picture to the two VoiceForge threshold choices (barge-in overlap, laggy latency).**

## Slice

- Total calls in `out/calls.json`: **76**
- **Timed** (analysed): **46**
- **Unmeasured** (excluded, no timing): **30**
- **Mixed** (excluded, partial clock): **0**

## Coverage of the timed slice
- source: {'bolna': 1, 'hero': 1, 'spokenwoz': 44}
- stress_profile: {'clean': 20, 'interruption': 21, 'pause_heavy': 5}
- workflow_type: {'appointment_booking': 1, 'appliance_service_booking': 1, 'attraction+profile+train': 4, 'hotel+profile+train': 11, 'attraction+profile+restaurant': 3, 'attraction+hotel+profile': 1, 'hotel+profile+restaurant+taxi': 2, 'profile+restaurant+train': 15, 'attraction+profile+restaurant+taxi': 2, 'hotel+profile+restaurant': 6}
- language: {'hi-en': 1, 'te-en': 1, 'en': 44}

## Grid
- overlap thresholds (ms): [0, 100, 200, 300, 500]
- lag thresholds (ms): [500, 800, 1000, 1500, 2000]
- VoiceForge default: overlap>100ms, lag>800ms (25 cells total)

## Per-setting event & affected-call counts
| overlap>ms | lag>ms | barge_in ev | latency_gap ev | total ev | calls w/ barge | calls w/ lag | calls affected | default |
|---:|---:|---:|---:|---:|---:|---:|---:|:---:|
| 0 | 500 | 215 | 337 | 552 | 40 | 44 | 46 |  |
| 0 | 800 | 215 | 183 | 398 | 40 | 33 | 45 |  |
| 0 | 1000 | 215 | 122 | 337 | 40 | 29 | 45 |  |
| 0 | 1500 | 215 | 57 | 272 | 40 | 25 | 45 |  |
| 0 | 2000 | 215 | 28 | 243 | 40 | 14 | 43 |  |
| 100 | 500 | 107 | 337 | 444 | 31 | 44 | 46 |  |
| 100 | 800 | 107 | 183 | 290 | 31 | 33 | 41 | YES |
| 100 | 1000 | 107 | 122 | 229 | 31 | 29 | 41 |  |
| 100 | 1500 | 107 | 57 | 164 | 31 | 25 | 41 |  |
| 100 | 2000 | 107 | 28 | 135 | 31 | 14 | 38 |  |
| 200 | 500 | 66 | 337 | 403 | 25 | 44 | 46 |  |
| 200 | 800 | 66 | 183 | 249 | 25 | 33 | 39 |  |
| 200 | 1000 | 66 | 122 | 188 | 25 | 29 | 39 |  |
| 200 | 1500 | 66 | 57 | 123 | 25 | 25 | 38 |  |
| 200 | 2000 | 66 | 28 | 94 | 25 | 14 | 34 |  |
| 300 | 500 | 53 | 337 | 390 | 23 | 44 | 45 |  |
| 300 | 800 | 53 | 183 | 236 | 23 | 33 | 38 |  |
| 300 | 1000 | 53 | 122 | 175 | 23 | 29 | 37 |  |
| 300 | 1500 | 53 | 57 | 110 | 23 | 25 | 36 |  |
| 300 | 2000 | 53 | 28 | 81 | 23 | 14 | 32 |  |
| 500 | 500 | 40 | 337 | 377 | 19 | 44 | 45 |  |
| 500 | 800 | 40 | 183 | 223 | 19 | 33 | 36 |  |
| 500 | 1000 | 40 | 122 | 162 | 19 | 29 | 35 |  |
| 500 | 1500 | 40 | 57 | 97 | 19 | 25 | 33 |  |
| 500 | 2000 | 40 | 28 | 68 | 19 | 14 | 28 |  |

## How much the picture moves
- barge_in event count across grid: **40 .. 215**
- latency_gap event count across grid: **28 .. 337**

### Isolating the overlap axis (lag held at default 800ms)
| overlap>ms | barge_in ev | latency_gap ev |
|---:|---:|---:|
| 0 | 215 | 183 |
| 100 | 107 | 183 |
| 200 | 66 | 183 |
| 300 | 53 | 183 |
| 500 | 40 | 183 |

### Isolating the lag axis (overlap held at default 100ms)
| lag>ms | barge_in ev | latency_gap ev |
|---:|---:|---:|
| 500 | 107 | 337 |
| 800 | 107 | 183 |
| 1000 | 107 | 122 |
| 1500 | 107 | 57 |
| 2000 | 107 | 28 |

## Failure-cluster RANK stability (vs default setting)
Calls ranked by total timing-event load. `tau` = rank-agreement vs default (1.0 = identical order); `J` = Jaccard of the exact per-call event set vs default; `top5∩` = how many of the default top-5 calls remain in this setting's top-5.
| setting | total ev | J events vs default | rank tau vs default | top5∩ |
|:--|---:|---:|---:|---:|
| ov0_lg500 | 552 | 0.5254 | 0.7121 | 2 |
| ov0_lg800 | 398 | 0.7286 | 0.7232 | 3 |
| ov0_lg1000 | 337 | 0.5754 | 0.602 | 2 |
| ov0_lg1500 | 272 | 0.4121 | 0.3717 | 2 |
| ov0_lg2000 | 243 | 0.3392 | 0.2848 | 2 |
| ov100_lg500 | 444 | 0.6532 | 0.7585 | 3 |
| ov100_lg800 | 290 | 1.0 | 1.0 | 5 |
| ov100_lg1000 | 229 | 0.7897 | 0.8244 | 4 |
| ov100_lg1500 | 164 | 0.5655 | 0.539 | 3 |
| ov100_lg2000 | 135 | 0.4655 | 0.461 | 2 |
| ov200_lg500 | 403 | 0.5608 | 0.6966 | 3 |
| ov200_lg800 | 249 | 0.8586 | 0.8122 | 4 |
| ov200_lg1000 | 188 | 0.6483 | 0.7585 | 3 |
| ov200_lg1500 | 123 | 0.4241 | 0.5317 | 4 |
| ov200_lg2000 | 94 | 0.3241 | 0.4707 | 3 |
| ov300_lg500 | 390 | 0.5315 | 0.6599 | 2 |
| ov300_lg800 | 236 | 0.8138 | 0.7561 | 3 |
| ov300_lg1000 | 175 | 0.6034 | 0.7146 | 4 |
| ov300_lg1500 | 110 | 0.3793 | 0.522 | 3 |
| ov300_lg2000 | 81 | 0.2793 | 0.4561 | 3 |
| ov500_lg500 | 377 | 0.5023 | 0.6251 | 2 |
| ov500_lg800 | 223 | 0.769 | 0.6634 | 3 |
| ov500_lg1000 | 162 | 0.5586 | 0.6122 | 3 |
| ov500_lg1500 | 97 | 0.3345 | 0.422 | 3 |
| ov500_lg2000 | 68 | 0.2345 | 0.3171 | 3 |

- **Most stable vs default:** `ov200_lg800` (J=0.8586, tau=0.8122)
- **Least stable vs default:** `ov500_lg2000` (J=0.2345, tau=0.3171)

## Default-setting top-10 failure cluster
| rank | call_id | total timing events |
|---:|:--|---:|
| 1 | swz_MUL0056 | 18 |
| 2 | swz_MUL0142 | 15 |
| 3 | swz_MUL0174 | 15 |
| 4 | swz_MUL0035 | 13 |
| 5 | swz_MUL0297 | 13 |
| 6 | swz_MUL0153 | 12 |
| 7 | swz_MUL0154 | 12 |
| 8 | swz_MUL0213 | 11 |
| 9 | swz_MUL0106 | 10 |
| 10 | swz_MUL0239 | 10 |

## Calls whose classification CHANGES across the grid
- **46** calls change their (barge_in, latency_gap) event counts somewhere in the grid.
- **18** calls cross the affected / not-affected (0-event) boundary.

IDs changing any event count:
`bolna_246cd9f3, hero_001, swz_MUL0035, swz_MUL0043, swz_MUL0056, swz_MUL0069, swz_MUL0071, swz_MUL0106, swz_MUL0125, swz_MUL0142, swz_MUL0153, swz_MUL0154, swz_MUL0167, swz_MUL0174, swz_MUL0189, swz_MUL0211, swz_MUL0213, swz_MUL0226, swz_MUL0239, swz_MUL0247, swz_MUL0258, swz_MUL0265, swz_MUL0271, swz_MUL0280, swz_MUL0283, swz_MUL0287, swz_MUL0293, swz_MUL0297, swz_MUL0322, swz_MUL0329, swz_MUL0335, swz_MUL0357, swz_MUL0398, swz_MUL0431, swz_MUL0658, swz_MUL0815, swz_MUL0836, swz_MUL0864, swz_MUL0867, swz_MUL0999, swz_MUL1004, swz_MUL1552, swz_MUL1560, swz_MUL1685, swz_MUL2483, swz_MUL2658`

IDs crossing the 0-event boundary:
`bolna_246cd9f3, swz_MUL0043, swz_MUL0069, swz_MUL0167, swz_MUL0211, swz_MUL0239, swz_MUL0265, swz_MUL0271, swz_MUL0280, swz_MUL0293, swz_MUL0322, swz_MUL0335, swz_MUL0815, swz_MUL0999, swz_MUL1004, swz_MUL1552, swz_MUL1685, swz_MUL2658`

### Per-call detail (source / stress / ranges)
| call_id | source | stress | barge_in range | latency_gap range | crosses 0-boundary |
|:--|:--|:--|:--|:--|:--:|
| bolna_246cd9f3 | bolna | clean | [0, 0] | [0, 2] | YES |
| hero_001 | hero | interruption | [1, 1] | [0, 1] |  |
| swz_MUL0035 | spokenwoz | interruption | [2, 7] | [0, 10] |  |
| swz_MUL0043 | spokenwoz | interruption | [0, 13] | [0, 3] | YES |
| swz_MUL0056 | spokenwoz | interruption | [4, 5] | [5, 15] |  |
| swz_MUL0069 | spokenwoz | clean | [0, 0] | [0, 8] | YES |
| swz_MUL0071 | spokenwoz | interruption | [2, 22] | [0, 2] |  |
| swz_MUL0106 | spokenwoz | clean | [0, 1] | [2, 15] |  |
| swz_MUL0125 | spokenwoz | interruption | [2, 3] | [0, 11] |  |
| swz_MUL0142 | spokenwoz | interruption | [2, 2] | [0, 16] |  |
| swz_MUL0153 | spokenwoz | pause_heavy | [0, 1] | [1, 18] |  |
| swz_MUL0154 | spokenwoz | interruption | [2, 5] | [1, 15] |  |
| swz_MUL0167 | spokenwoz | interruption | [0, 8] | [0, 3] | YES |
| swz_MUL0174 | spokenwoz | interruption | [5, 16] | [0, 9] |  |
| swz_MUL0189 | spokenwoz | interruption | [2, 8] | [0, 3] |  |
| swz_MUL0211 | spokenwoz | interruption | [0, 8] | [0, 8] | YES |
| swz_MUL0213 | spokenwoz | interruption | [5, 20] | [0, 4] |  |
| swz_MUL0226 | spokenwoz | interruption | [3, 8] | [0, 10] |  |
| swz_MUL0239 | spokenwoz | interruption | [0, 8] | [0, 6] | YES |
| swz_MUL0247 | spokenwoz | interruption | [0, 6] | [1, 6] |  |
| swz_MUL0258 | spokenwoz | interruption | [2, 4] | [1, 5] |  |
| swz_MUL0265 | spokenwoz | clean | [0, 4] | [0, 4] | YES |
| swz_MUL0271 | spokenwoz | clean | [0, 1] | [0, 7] | YES |
| swz_MUL0280 | spokenwoz | clean | [0, 3] | [0, 3] | YES |
| swz_MUL0283 | spokenwoz | clean | [0, 1] | [2, 6] |  |
| swz_MUL0287 | spokenwoz | clean | [0, 5] | [1, 11] |  |
| swz_MUL0293 | spokenwoz | interruption | [0, 6] | [0, 5] | YES |
| swz_MUL0297 | spokenwoz | interruption | [2, 3] | [2, 13] |  |
| swz_MUL0322 | spokenwoz | clean | [0, 1] | [0, 7] | YES |
| swz_MUL0329 | spokenwoz | interruption | [1, 6] | [0, 4] |  |
| swz_MUL0335 | spokenwoz | clean | [0, 2] | [0, 3] | YES |
| swz_MUL0357 | spokenwoz | interruption | [1, 9] | [0, 3] |  |
| swz_MUL0398 | spokenwoz | clean | [1, 7] | [0, 0] |  |
| swz_MUL0431 | spokenwoz | clean | [1, 2] | [0, 12] |  |
| swz_MUL0658 | spokenwoz | clean | [1, 2] | [2, 12] |  |
| swz_MUL0815 | spokenwoz | clean | [0, 1] | [0, 5] | YES |
| swz_MUL0836 | spokenwoz | clean | [0, 1] | [2, 5] |  |
| swz_MUL0864 | spokenwoz | clean | [0, 0] | [3, 12] |  |
| swz_MUL0867 | spokenwoz | clean | [0, 0] | [2, 12] |  |
| swz_MUL0999 | spokenwoz | clean | [0, 6] | [0, 0] | YES |
| swz_MUL1004 | spokenwoz | clean | [0, 3] | [0, 1] | YES |
| swz_MUL1552 | spokenwoz | pause_heavy | [0, 3] | [0, 12] | YES |
| swz_MUL1560 | spokenwoz | pause_heavy | [1, 2] | [0, 12] |  |
| swz_MUL1685 | spokenwoz | clean | [0, 1] | [0, 1] | YES |
| swz_MUL2483 | spokenwoz | pause_heavy | [0, 0] | [3, 8] |  |
| swz_MUL2658 | spokenwoz | pause_heavy | [0, 0] | [0, 9] | YES |
