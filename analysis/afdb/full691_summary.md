# AFDB Full Method Comparison

- Rows: 691
- Labels: `324` positive, `367` negative
- Rows with computed iPAE/interchain features: `679 / 691`
- Calibrator/MLP training CSV: `data/general_v2.csv`
- MLP model: `models/locked_ce_5feat_general.pt`
- MLP scaler: `models/scaler_5feat_general.pkl`
- Labels are AFDB/PDB-access positive/negative labels, not DockQ thresholds.
- Ab-Ag calibrators are retained only as transfer comparisons.
- Exact Steinegger fixed filter: `ipsae_max >= 0.6 and pdockq2_max >= 0.23`

Detailed per-method metrics remain in:

- `full691_comparison.csv`
- `full691_matched_precision.csv`
- `full691_pr_curve.pdf`
- `full691_abagtrained_comparison.csv`
- `training_regime_comparison.csv`
