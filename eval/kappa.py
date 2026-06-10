#!/usr/bin/env python3
"""Pilot calibration: judge vs blind human labels. SPEC §7.F. — Block 7.

from sklearn.metrics import cohen_kappa_score, confusion_matrix
k = cohen_kappa_score(human, judge)          # same items, same order (id-aligned!)
# bootstrap CI: resample item indices 1000x -> 2.5/97.5 percentiles

Inputs: eval/labels_spike.csv (rater 1, labeled blind BEFORE seeing judge output),
optionally eval/labels_friend.csv (rater 2 -> human-human ceiling).
Outputs: kappa + 95% CI + confusion matrix + the 2 disagreement cases (slide material).

Framing locked: "pilot calibration". Claim "substantial agreement" ONLY if the number AND
the CI land in 0.61-0.80 (Landis-Koch); otherwise report honestly ("moderate, directional").
"""
raise SystemExit("TODO Block 7 (June 12). Labels are collected in Block 4 (June 11).")
