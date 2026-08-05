# Release Notes: v1.0

## Scientific scope

This release packages the locked public reproduction repository for:

**Post-hoc Calibration of AlphaFold Confidence Scores for Protein Complex Quality Prediction**

Included:

- locked Ab-Ag and General calibrated MLP models
- frozen evaluation datasets and prediction exports used in the manuscript
- public reproduction scripts for the shipped tables and figures
- split Ab-Ag training data with integrity validation and reconstruction support

## Reproducible artifacts

Figures:

- `paper/figures/F1_reliability_abag.*`
- `paper/figures/F2_matched_precision_bars.*`
- `paper/figures/F3_permutation_importance.*`

Tables:

- `paper/tables/tab_abag_main.tex`
- `paper/tables/tab_general_v2.tex`
- `paper/tables/tab_casp16_bootstrap_v2.tex`
- `paper/tables/tab_*_reproduced.*`
- `paper/tables/tab_afdb_*`

## Integrity verification

Run:

```bash
bash scripts/verify_manifest.sh
python scripts/validate_abag_train_parts.py
```

## Known limitations

- The release does not automate parsing of complete raw AF3/AFM output directories.
- Some benchmark dataset redistribution rights remain to be confirmed; see `DATA_LICENSE.md`.
- `predict_with_sample_size()` provides an independence-based estimate, not a guaranteed required number of seeds.
- The public CSVs intentionally omit internal cluster filesystem path columns.

## Data licensing caveats

See `DATA_LICENSE.md`. Software is MIT-licensed; data may have separate upstream constraints.

## Exact release state

- Repository URL: `https://github.com/sagadinov/alphafold-complex-calibration`
- Release tag: `v1.0`
- Commit SHA: the exact release commit is the commit pointed to by the `v1.0` tag

## Decision-use v2 addendum

Added:

- fixed-ranking expected-yield estimation outputs under `analysis/decision_use/`
- transfer reliability operating curves and bootstrap summaries
- decision-use figures in `paper/figures/*v2*`
- shipped decision-use reproduction script

