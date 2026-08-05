# Decision-Use Experiments

These experiments test whether calibrated probabilities improve decisions that require probabilities, not just rankings.

## Experiment 1: Fixed-ranking expected yield

Question: among the top-K predictions selected by a raw ranking score, how many satisfy `DockQ >= 0.23`?

Design: candidate identity is fixed by the raw score ranking. Only the probability estimate changes. This isolates calibration from discrimination.

Key result: on Ab-Ag, calibration reduces fixed-set yield estimation error substantially, especially for iPAE-ranked candidate sets.

Files:
- `fixed_ranking_yield_metrics.csv`
- `fixed_ranking_yield_bootstrap.csv`
- `fixed_ranking_yield_per_target.csv`
- `fixed_ranking_delta_audit.csv`
- `fixed_ranking_yield_summary.md`

## Experiment 2: Reliability operating curves

Question: if a user requests predictions with at least `q` probability of success, does the observed precision match the request?

Design: for calibrated methods, select predictions with `P >= q`. For raw scores, tune a threshold on one dataset and transfer it unchanged.

Key result: raw transferred thresholds provide more coverage but lose their intended reliability meaning under transfer. Calibrated probability rules preserve requested minimum reliability more consistently, at a coverage cost.

Files:
- `reliability_operating_curve.csv`
- `reliability_operating_curve_bootstrap.csv`
- `reliability_operating_curve_summary.md`

## Audits

- `ranking_invariance_audit.csv`
- `missingness_audit.csv`
- `validation_report.md`
- `manifest.yaml`
- `figure_captions.md`

## Main figures

- `fixed_ranking_yield_figure_v2.*`
- `reliability_transfer_figure_v2.*`
- `abag_ipae_reliability_figure_v2.*`

## Reproduction

Use the shipped precomputed outputs directly:

```bash
python scripts/reproduce_decision_use.py
```
