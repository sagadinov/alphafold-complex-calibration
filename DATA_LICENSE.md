# Data Provenance and Licensing Notes

This repository contains software, locked models, derived evaluation tables,
and selected CSV datasets used for paper reproduction. The MIT software license
in `LICENSE` does **not** automatically apply to all data files.

This document records provenance and redistribution status to the extent known
at release time.

## 1. `data/abag_test_v2.csv`

- Contents: Ab-Ag evaluation summary table with DockQ labels, calibrated-input features, and audit/status columns
- Source: author-generated release dataset derived from SAbDab-linked antibody-antigen benchmarking workflows
- Original upstream source: SAbDab-derived structures plus AlphaFold prediction outputs used in the manuscript pipeline
- Transformations: recomputed v2 iPAE-style features; removal of local cluster path columns for public release
- Redistribution status: **uncertain**
- Recommendation: keep under author-controlled release review until dataset redistribution terms are explicitly confirmed

## 2. `data/abag_train_v2_parts/`

- Contents: target-preserving shards of the Ab-Ag training summary table
- Source: author-generated release split from the internal `abag_train_v2.csv`
- Original upstream source: SAbDab-derived antibody-antigen training benchmark and AlphaFold prediction outputs
- Transformations: split by `target_id`; removal of local cluster path columns for public release
- Redistribution status: **uncertain**
- Notes: scientific columns are retained; internal filesystem audit columns were removed

## 3. `data/general_v2.csv`

- Contents: general multimer benchmark summary table used for General/CASP16 calibrator training or evaluation
- Source: author-generated normalized release table
- Original upstream source: AFM benchmark derived from Zhu et al. 2023 benchmarking data
- Transformations: column normalization to release schema
- Redistribution status: **uncertain**
- Recommendation: if redistribution is questioned, distribute regeneration instructions and derived prediction exports instead

## 4. `data/casp16_v2.csv`

- Contents: CASP16 summary table with v2 DockQ and calibrated-input features
- Source: author-generated release dataset
- Original upstream source: CASP16 / MassiveFold / Bjorn prediction collections plus author recomputation pipeline
- Transformations: recomputed DockQ v2 and iPAE-style features; removal of local cluster path columns for public release
- Redistribution status: **uncertain**

## 5. `data/abag_predictions_v3.csv`, `data/general_predictions_v3.csv`, `data/casp16_predictions_v3.csv`

- Contents: locked per-model prediction exports for all methods used by the public reproduction scripts
- Source: author-generated derived result files
- Upstream dependencies: evaluation datasets and locked models
- Transformations: method-level probability exports derived from frozen release results
- Redistribution status: likely author-controlled derived data, but still depends on upstream benchmark provenance

## 6. `data/casp16_bootstrap_summary.csv`

- Contents: locked bootstrap summary used for the CASP16 paper table
- Source: author-generated derived evaluation artifact
- Redistribution status: likely author-controlled derived result file

## 7. `data/report_data_v3.json`

- Contents: locked aggregate result summary for the paper
- Source: author-generated derived evaluation artifact
- Redistribution status: likely author-controlled derived result file

## 8. `analysis/afdb/`

- Contents: AFDB benchmark comparison tables and derived features/results
- Source: author-generated analysis outputs on top of the AFDB complexes supplementary benchmark
- Original upstream source: AFDB complex benchmark supplementary data and AFDB/NVIDIA model files
- Transformations: derived features, comparisons, matched-precision analysis, figures
- Redistribution status: **mixed**
- Notes: raw AFDB CIF/PAE model files are not redistributed here

## 9. `models/*.pt`, `models/*.pkl`

- Contents: locked MLP weights and preprocessing scalers
- Source: author-generated model artifacts
- Upstream dependencies: manuscript training datasets
- Redistribution status: expected to be redistributable by the authors, subject to upstream data-use constraints

## 10. `paper/figures/` and `paper/tables/`

- Contents: frozen manuscript figures and tables plus reproduced outputs generated from locked release data
- Source: author-generated paper artifacts
- Redistribution status: expected to be redistributable by the authors

## 11. Software files

- Paths: `src/`, `scripts/`, workflow files, tests, metadata
- License: MIT under `LICENSE`

## Release caveats

Known data-rights questions remain for benchmark CSV redistribution, especially
for SAbDab-derived Ab-Ag tables and AFM/CASP-derived summary tables. Those
files were not deleted automatically because they are required for exact paper
reproduction, but they should be reviewed before making the repository public.
