# Decision-Use Validation Report

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
