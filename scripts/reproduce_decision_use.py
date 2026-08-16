#!/usr/bin/env python3
"""Canonical repository-relative decision-use reproduction entrypoint."""

from __future__ import annotations

from pathlib import Path

from common import ANALYSIS, PAPER_FIG, ROOT, SUPP_FIG, ensure_dirs, write_text
from render_decision_use_v2_figures import Q_LEVELS, load_csvs, render_abag_ipae_supplementary, render_fixed_ranking_main, render_reliability_transfer_main, write_captions
from reproduce_table3_yield import main as reproduce_table3

A = ANALYSIS / "decision_use"


def rewrite_manifest() -> None:
    text = """canonical_repository_verified: true
project_root: .
output_dir: analysis/decision_use
seed: 42
n_bootstrap: 2000
primary_outcome:
  name: acceptable
  value: 0.23
k_values_main: [5, 10, 20, 50]
q_values: [0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95]
source_files:
  - label: abag_predictions_v3
    path: data/abag_predictions_v3.csv
  - label: general_predictions_v3
    path: data/general_predictions_v3.csv
  - label: casp16_predictions_v3
    path: data/casp16_predictions_v3.csv
  - label: abag_train_v2_parts
    path: data/abag_train_v2_parts/
  - label: abag_test_v2
    path: data/abag_test_v2.csv
  - label: general_v2
    path: data/general_v2.csv
  - label: locked_ce_5feat_abag
    path: models/locked_ce_5feat_abag.pt
  - label: scaler_5feat_abag
    path: models/scaler_5feat_abag.pkl
  - label: locked_ce_5feat_general
    path: models/locked_ce_5feat_general.pt
  - label: scaler_5feat_general
    path: models/scaler_5feat_general.pkl
outputs:
  - paper/tables/tab3_fixed_ranking_yield.csv
  - paper/figures/F2_fixed_ranking_yield.pdf
  - paper/figures/F3_reliability_transfer.pdf
  - paper/supplementary/figures/S2_abag_ipae_reliability.pdf
"""
    (A / "manifest.yaml").write_text(text, encoding="utf-8")


def rewrite_validation_report() -> None:
    text = """# Decision-Use Validation Report

## Provenance
- project_root: `.`
- output_dir: `analysis/decision_use`
- source predictions:
  - `data/abag_predictions_v3.csv`
  - `data/general_predictions_v3.csv`
  - `data/casp16_predictions_v3.csv`
- source datasets:
  - `data/abag_test_v2.csv`
  - `data/abag_train_v2_parts/`
  - `data/general_v2.csv`
- locked models:
  - `models/locked_ce_5feat_abag.pt`
  - `models/scaler_5feat_abag.pkl`
  - `models/locked_ce_5feat_general.pt`
  - `models/scaler_5feat_general.pkl`

## Frozen settings
- primary DockQ event: `DockQ >= 0.23`
- q grid: `0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95`
- K grid: `5, 10, 20, 50`
- bootstrap: `n=2000`, `seed=42`
- comparison universe: `three_method_common`

## Consistency checks
- zero strict isotonic ordering inversions
- no decision-use validation warnings
- General fixed-ranking panel uses `K=5` only
- candidate identities are fixed within each ranking family

## Main outputs
- `paper/tables/tab3_fixed_ranking_yield.*`
- `paper/figures/F2_fixed_ranking_yield.*`
- `paper/figures/F3_reliability_transfer.*`
- `paper/supplementary/figures/S2_abag_ipae_reliability.*`
"""
    write_text(A / "validation_report.md", text)


def rewrite_readme() -> None:
    text = """# Decision-Use Experiments

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
"""
    write_text(A / "README.md", text)


def main() -> None:
    ensure_dirs()
    data = load_csvs(A)
    render_fixed_ranking_main(data["fixed_metrics"], data["fixed_boot"], PAPER_FIG)
    render_reliability_transfer_main(data["rel_curve"], data["rel_boot"], PAPER_FIG)
    render_abag_ipae_supplementary(data["rel_curve"], data["rel_boot"], SUPP_FIG)
    reproduce_table3()
    write_captions(A)
    rewrite_manifest()
    rewrite_validation_report()
    rewrite_readme()
    print("Decision-use manuscript artifacts reproduced from frozen CSVs.")


if __name__ == "__main__":
    main()
