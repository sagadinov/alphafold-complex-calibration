# AFDB Supporting Validation

This directory contains the frozen AFDB-based supporting validation used in the manuscript.
It intentionally separates two distinct evaluations.

## 1. Full 691-entry binary benchmark

This is the broad external validation set with 691 AFDB complexes carrying positive/negative labels for whether an experimentally validated PDB complex is available.
These labels are **not DockQ thresholds**.

Files:

- `full691_comparison.csv`
- `full691_matched_precision.csv`
- `full691_pr_curve.pdf`
- `full691_summary.md`
- `full691_abagtrained_comparison.csv`
- `training_regime_comparison.csv`

Interpretation:

- this is a domain-transfer confidence benchmark,
- not the manuscript's main structural-threshold table,
- and it is best treated as supporting/supplementary external validation.

## 2. Positive-only structural DockQ benchmark

This is the manuscript-used AFDB supporting structural analysis.
It starts from the 324 positive-label complexes and evaluates structural success against experimental PDB complexes using best-match DockQ.
Finite DockQ is available for 304 entries.

Files:

- `afdb_positive_dockq.csv`
- `afdb_positive_dockq_features.csv`
- `afdb_positive_dockq_full_comparison.csv`
- `afdb_positive_dockq_matched_precision.csv`
- `afdb_positive_dockq_steinegger_transfer.csv`
- `afdb_positive_dockq_pr_acceptable.pdf`
- `afdb_positive_dockq_summary.md`

Manuscript-facing supporting results include:

- matched ~90% precision at `DockQ >= 0.23`:
  - `MLP 5-feat CE`: 51 selected, precision ~0.902, recall ~0.303
  - `ipSAEmax`: 34 selected, precision ~0.912, recall ~0.204
- Steinegger fixed-filter structural success:
  - `DockQ >= 0.23`: 82.1%
  - `DockQ >= 0.49`: 70.2%
  - `DockQ >= 0.80`: 42.9%

## Feature provenance

The release ships frozen **derived** AFDB feature/result tables only.
Raw AFDB/NVIDIA CIF and PAE files are not redistributed here.
Computed features include:

- interface iPAE over predicted 8 A cross-chain C-beta contacts
- interchain block mean PAE
- pTM reconstructed from shipped PAE matrices during the original analysis
- ranking score derived as `0.8 * ipTM + 0.2 * pTM`

## Training regimes

Primary AFDB comparisons use the **General-trained** calibrators/models, matching the general-complex setting and the CASP16 protocol.
Ab-Ag-trained transfer comparisons are retained only as secondary supporting artifacts.

## Reproduction scope

This curated release reproduces AFDB manuscript claims from the frozen result tables already shipped in this directory.
It does not attempt to redownload or reconstruct the raw AFDB bulk archives.
