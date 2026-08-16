# Release Audit

## Repository state

- branch: `main`
- repository visibility: `PRIVATE`
- working tree state: finalized cleanup state validated locally on `main` before push
- canonical remote: `git@github.com:sagadinov/alphafold-complex-calibration.git`
- clean validation environment used: `/tmp/afcal_release_venv` with Python `3.11.13`

## Main paper artifacts

| Artifact | Frozen source | Reproduction script | Generated output |
| --- | --- | --- | --- |
| Figure 1 | `data/abag_predictions_v3.csv` | `scripts/reproduce_figure1.py` | `paper/figures/F1_reliability_abag.pdf` |
| Figure 2 | `analysis/decision_use/fixed_ranking_yield_metrics.csv`, `analysis/decision_use/fixed_ranking_yield_bootstrap.csv` | `scripts/reproduce_figure2.py` | `paper/figures/F2_fixed_ranking_yield.pdf` |
| Figure 3 | `analysis/decision_use/reliability_operating_curve.csv`, `analysis/decision_use/reliability_operating_curve_bootstrap.csv` | `scripts/reproduce_figure3.py` | `paper/figures/F3_reliability_transfer.pdf` |
| Table 1 | `data/report_data_v3.json` | `scripts/reproduce_table1_abag.py` | `paper/tables/tab1_abag_main.tex` |
| Table 2 | `data/report_data_v3.json` | `scripts/reproduce_table2_general.py` | `paper/tables/tab2_general_main.tex` |
| Table 3 | `analysis/decision_use/fixed_ranking_yield_metrics.csv` | `scripts/reproduce_table3_yield.py` | `paper/tables/tab3_fixed_ranking_yield.tex` |
| Table 4 | `data/casp16_bootstrap_summary.csv` | `scripts/reproduce_table4_casp16.py` | `paper/tables/tab4_casp16_bootstrap.tex` |

## Supplementary artifacts

- `paper/supplementary/figures/S1_permutation_importance.*`
- `paper/supplementary/figures/S2_abag_ipae_reliability.*`
- `paper/supplementary/figures/afdb_positive_dockq_pr_acceptable.*`
- `paper/supplementary/figures/full691_pr_curve.pdf`
- `paper/supplementary/tables/afdb_*.csv`
- AFDB supporting structural validation under `analysis/afdb/`
- decision-use supporting audits under `analysis/decision_use/`

## Scientific consistency checks

- Ab-Ag: `62,681` evaluated models / `1,257` targets
- General: `5,496` models / `1,922` targets
- CASP16: `16,199` models / `25` scoreable targets
- CASP16 common MLP universe: `15,323` rows where relevant in the frozen analyses
- AFDB: `691` labelled / `324` positive / `304` finite DockQ
- decision-use q grid: `0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95`
- fixed-ranking K grid: `5, 10, 20, 50`
- decision-use bootstrap: `n=2000`, `seed=42`
- strict isotonic ordering inversions: `0`
- decision-use validation warnings: `none expected in frozen release`

## Reproducibility

Validated in this pass:

- `bash scripts/verify_manifest.sh`: PASS
- `python scripts/validate_abag_train_parts.py`: PASS
- `bash scripts/run_all.sh`: PASS
- `bash scripts/run_supplementary.sh`: PASS
- `pytest -q`: PASS (`14 passed`)

Observed warning:

- `sklearn` emitted `InconsistentVersionWarning` when unpickling shipped `StandardScaler` objects trained under `scikit-learn 1.8.0` while validating with `1.9.0`.
- The warning did not break inference or tests, but the release should keep this version drift in mind for future public packaging.

## Remaining pre-publication actions

1. Resolve or decide data redistribution items.
2. Make the repository public at manuscript submission.
3. Create the final immutable public release tag.
4. Add preprint/DOI metadata when available.
