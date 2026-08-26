# Workshop Figure Reproduction

## Commands

Run from the repository root:

```bash
/proj/berzelius-2021-29/users/x_sasag/projects/af3_atlas/.venv_threshold_analysis311/bin/python scripts/render_workshop_final_figures.py
```

This script will recompute the AFDB local-recalibration source table and then render:

- `paper/figures/F1_workshop_within_domain_reliability_2x3.pdf`
- `paper/figures/F1_workshop_within_domain_reliability_abag.pdf`
- `paper/figures/F2_workshop_fixedset_published.pdf`
- `paper/figures/F2_workshop_fixedset_refit.pdf`
- `paper/figures/F3_workshop_afdb_recalibration.pdf`

PNG previews are written alongside each PDF.

## Canonical inputs

- Figure 1: `data/abag_predictions_v3.csv`, `data/general_predictions_v3.csv`, `analysis/workshop/workshop_abag_table.csv`, `analysis/workshop/workshop_general_table.csv`
- Figure 2 published variant: `analysis/workshop/workshop_yield_simplified.csv`, `analysis/decision_use/fixed_ranking_yield_metrics.csv`, `analysis/decision_use/fixed_ranking_yield_per_target.csv`
- Figure 2 refit variant: `analysis/workshop_yield_with_refit.csv`, `analysis/decision_use/fixed_ranking_yield_metrics.csv`, `analysis/decision_use/fixed_ranking_yield_per_target.csv`
- Figure 3: `analysis/afdb/afdb_positive_dockq_features.csv`, `data/general_v2.csv`

## Source-data CSVs

Machine-readable source-data tables are written to `paper/figures/source_data/`.

## Assertions enforced by the scripts

- Ab-Ag within-domain evaluation universe is exactly 62,681 rows.
- General within-domain evaluation universe is exactly 5,496 rows.
- AFDB structural recalibration universe is exactly 304 finite-DockQ complexes.
- Figure 2 uses the fixed-candidate audit from `analysis/decision_use/fixed_ranking_yield_per_target.csv`.
- AFDB local recalibration uses disjoint calibration/evaluation splits, paired between ipTM and ipSAEmax.
