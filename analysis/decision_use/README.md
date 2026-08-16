# Decision-Use Experiments

These frozen artifacts support the final manuscript decision-use section.

## Experiment 1: Fixed-ranking expected-yield estimation

Candidates are first selected by a raw ranking score. Candidate identities are then fixed across probability estimators, so only the predicted expected yield differs.
Observed successes are models satisfying `DockQ >= 0.23`. Predicted successes are the sum of estimated probabilities over the same fixed candidate set.
The primary metric is mean absolute difference between predicted and observed success fractions across targets (Yield MAE).

Interpretation:
- strong within-domain Ab-Ag benefit is present, especially for iPAE-ranked candidate sets;
- General is limited to `K=5` because larger `K` values do not have enough eligible models per target in the locked dataset;
- there is no clear transferred yield-estimation benefit on CASP16.

## Experiment 2: Minimum-reliability filtering

For calibrated methods, predictions are selected using `p >= q`.
For raw ipTM, a score threshold is chosen on General to maximize coverage subject to the requested precision floor, then frozen for external transfer.
General source evaluation uses target-grouped cross-fitting.
General-trained calibrated probabilities are then applied frozen to Ab-Ag and CASP16.
Precision and coverage must be interpreted jointly.

Calibrated-rule point estimates met or exceeded the requested precision at the tested operating points more consistently than frozen raw-score thresholds, at the cost of reduced coverage.
Calibration does not guarantee transfer under arbitrary distribution shift.

## Files

- `fixed_ranking_yield_metrics.csv`
- `fixed_ranking_yield_bootstrap.csv`
- `fixed_ranking_yield_per_target.csv`
- `reliability_operating_curve.csv`
- `reliability_operating_curve_bootstrap.csv`
- `ranking_invariance_audit.csv`
- `missingness_audit.csv`
- `manifest.yaml`
- `validation_report.md`

## Reproduction

Main manuscript-facing artifacts:

```bash
python scripts/reproduce_decision_use.py
```

This reconstructs:
- `paper/tables/tab3_fixed_ranking_yield.*`
- `paper/figures/F2_fixed_ranking_yield.*`
- `paper/figures/F3_reliability_transfer.*`

Supplementary Ab-Ag iPAE reliability figure:

```bash
python scripts/reproduce_supplementary_ipae_reliability.py
```
