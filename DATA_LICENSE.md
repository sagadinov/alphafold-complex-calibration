# Data Provenance and Redistribution Plan

This repository contains software, locked model artifacts, frozen evaluation outputs, and benchmark-derived CSV files. The MIT license in `LICENSE` applies to software only. Data and model files may carry separate provenance constraints.

This document classifies shipped artifacts into four categories:

- **A. author-generated / expected redistributable**
- **B. author-derived aggregate artifact / likely redistributable**
- **C. upstream redistribution uncertain**
- **D. should not be redistributed directly**

The repository is still private. Files in category C are retained because they are required for exact manuscript reproduction, but they must be reviewed again before a public release.

## A. Author-generated / expected redistributable

- `models/locked_ce_5feat_abag.pt`
- `models/scaler_5feat_abag.pkl`
- `models/locked_ce_5feat_general.pt`
- `models/scaler_5feat_general.pkl`
- `paper/figures/`
- `paper/tables/`
- `paper/supplementary/`
- `analysis/decision_use/*.csv`
- `analysis/decision_use/*.md`
- `analysis/permutation_importance_abag_v2.csv`
- `analysis/permutation_importance_general_v2.csv`
- `analysis/afdb/*comparison.csv`
- `analysis/afdb/*summary.md`
- all software under `src/`, `scripts/`, `tests/`, and workflow/config files

## B. Author-derived aggregate artifacts / likely redistributable

- `data/abag_predictions_v3.csv`
- `data/general_predictions_v3.csv`
- `data/casp16_predictions_v3.csv`
- `data/casp16_bootstrap_summary.csv`
- `data/report_data_v3.json`
- `analysis/afdb/afdb_positive_dockq.csv`
- `analysis/afdb/afdb_positive_dockq_features.csv`
- `analysis/afdb/afdb_positive_dockq_matched_precision.csv`
- `analysis/afdb/afdb_positive_dockq_steinegger_transfer.csv`

These are frozen aggregate or derived outputs, but their upstream benchmark provenance should still be documented when the repository is made public.

## C. Upstream redistribution uncertain

- `data/abag_test_v2.csv`
- `data/abag_train_v2_parts/`
- `data/general_v2.csv`
- `data/casp16_v2.csv`
- `analysis/afdb/benchmark_full_features.csv`
- `analysis/afdb/computed_features.csv`
- `data/AFDB Complexes Supplementary Data__Confidence_benchmark_PDB_access.csv` if present in future revisions

These files are required for exact end-to-end reproduction of the locked manuscript results, but they depend on upstream benchmark collections whose redistribution terms should be confirmed before public release.

## D. Should not be redistributed directly

Not shipped in this repository:

- raw AlphaFold3 / AlphaFold-Multimer prediction directories
- raw AFDB/NVIDIA bulk CIF and PAE archives
- raw CASP16 cluster working directories
- private cluster audit metadata and filesystem paths

## Public-release plan

If category C redistribution cannot be confirmed before public release:

1. Remove the affected benchmark CSVs from the public repository.
2. Keep category A/B derived predictions, tables, and figures where allowed.
3. Provide acquisition and regeneration instructions for the removed benchmark tables.
4. Keep repository-relative scripts that can operate once the user has acquired the permitted upstream inputs.

## Additional notes

- The current private release intentionally omits machine-specific path columns from public-facing CSVs.
- AFDB raw CIF/PAE files are not redistributed here; only frozen derived feature/result artifacts are included.
- This document records practical redistribution handling, not legal advice.
