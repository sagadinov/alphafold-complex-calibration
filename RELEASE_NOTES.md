# Release Notes

## Status

This repository is a **private pre-submission release candidate** for the manuscript:

**Post-hoc Calibration of AlphaFold Confidence Scores for Protein Complex Quality Prediction**

It is not yet the final public scientific release. The repository remains private, and no immutable public release tag has been created for manuscript submission yet.

## Final manuscript organization

### Main figures

- `paper/figures/F1_reliability_abag.*`
- `paper/figures/F2_fixed_ranking_yield.*`
- `paper/figures/F3_reliability_transfer.*`

### Main tables

- `paper/tables/tab1_abag_main.*`
- `paper/tables/tab2_general_main.*`
- `paper/tables/tab3_fixed_ranking_yield.*`
- `paper/tables/tab4_casp16_bootstrap.*`

### Supporting analyses retained in the release

- AFDB supporting validation under `analysis/afdb/`
- decision-use supporting files under `analysis/decision_use/`
- supplementary figure/table reproduction under `paper/supplementary/`
- permutation-importance CSVs under `analysis/`
- Ab-Ag training shards under `data/abag_train_v2_parts/`

## Scientific scope of this release

Included:

- locked Ab-Ag and General calibrated MLP models
- frozen evaluation datasets and per-model prediction exports used in the manuscript
- repository-local reproduction scripts for the final manuscript artifacts
- supporting analyses required for appendix/external-validation claims

Not included:

- AlphaFold retraining
- raw AF3/AFM directory parsing workflows
- raw AFDB CIF/PAE redistribution
- exploratory model-selection history beyond retained frozen supporting outputs

## Reproducibility

Main-paper reproduction:

```bash
bash scripts/run_all.sh
```

Supplementary/supporting reproduction:

```bash
bash scripts/run_supplementary.sh
```

Integrity checks:

```bash
bash scripts/verify_manifest.sh
python scripts/validate_abag_train_parts.py
pytest -q
```

## Known limitations

- benchmark redistribution rights remain to be confirmed for some upstream-derived CSVs
- AFDB raw model files are not redistributed in this repository
- probabilities are structural-quality probabilities, not biological-function probabilities
- calibration improves interpretability only within validated operating conditions and does not guarantee transfer under arbitrary shift

## Pre-publication actions remaining

1. Resolve or decide the final handling of data redistribution uncertainties.
2. Make the repository public at manuscript submission.
3. Create the final immutable public release tag.
4. Add preprint/DOI metadata when available.
