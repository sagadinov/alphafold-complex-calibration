# Post-hoc Calibration of AlphaFold Confidence Scores for Protein Complex Quality Prediction

This repository is the curated reproducibility release for the manuscript **Post-hoc Calibration of AlphaFold Confidence Scores for Protein Complex Quality Prediction**.
It contains locked calibrators, frozen evaluation outputs, manuscript reproduction scripts, and lightweight inference code.
The repository remains private until manuscript submission.

## What this repository contains

- locked Ab-Ag and General post-hoc calibrators
- frozen per-model prediction exports used for the manuscript tables and figures
- manuscript-facing reproduction scripts for the final paper artifacts
- supplementary analyses retained for appendix/supporting validation
- a small public inference API for applying the locked models to precomputed features

## Scope

This is a **post-hoc calibration** release.
It does not retrain AlphaFold, retrain structure generators, or parse raw AF3/AFM directory trees end-to-end.
Inputs to the shipped predictor must already contain the required complex-level summary features.

These probabilities are probabilities of satisfying specified **DockQ structural criteria**. They are not probabilities of biological binding, function, or experimental success.
Calibration can improve interpretability within a validated setting, but it does not guarantee transfer under arbitrary distribution shift.

## Quick start

### Installation

Recommended Python: `3.11`

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For the exact tested package set, see `requirements-lock.txt`.

### Run a calibrator

```python
import pandas as pd
from src.predict import CalibratedPredictor

df = pd.read_csv("your_complex_scores.csv")
predictor = CalibratedPredictor.load("models", domain="abag")
probs = predictor.predict(df)
print(probs.head())
```

Supported domains:

- `domain="abag"`: antibody-antigen complexes
- `domain="general"`: general protein complexes

Do not treat the Ab-Ag model as a general-complex calibrator, or vice versa.

## Required features

The locked 5-feature MLP expects:

- `iface_pae_mean`
- `interchain_block_mean`
- `iptm`
- `ranking_score`
- `ptm`

If `ranking_score` is absent, it is computed as:

```text
0.8 * iptm + 0.2 * ptm
```

Outputs:

- `p_acceptable`: estimated probability that `DockQ >= 0.23`
- `p_medium`: estimated probability that `DockQ >= 0.49`
- `p_high`: estimated probability that `DockQ >= 0.80`

## Feature assumptions

| Feature | Meaning |
| --- | --- |
| `iface_pae_mean` | Mean PAE over ordered cross-chain residue pairs with predicted C-beta distance < 8 A |
| `interchain_block_mean` | Mean PAE over all ordered cross-chain residue pairs |
| `iptm` | Interface predicted TM-score |
| `ptm` | Predicted TM-score |
| `ranking_score` | `0.8 * iptm + 0.2 * ptm` |

Important limits:

- `iface_pae_mean` is defined on predicted contacts, not native contacts
- cross-chain residue pairs are counted as ordered pairs, matching the locked v2 pipeline
- no-contact complexes return `NaN` for `iface_pae_mean`
- raw AF3/AFM output parsing is not part of this public release

## Reproduce the paper

Main paper artifacts:

```bash
bash scripts/run_all.sh
```

This reproduces the final manuscript-facing outputs:

- `paper/tables/tab1_abag_main.*`
- `paper/tables/tab2_general_main.*`
- `paper/tables/tab3_fixed_ranking_yield.*`
- `paper/tables/tab4_casp16_bootstrap.*`
- `paper/figures/F1_reliability_abag.*`
- `paper/figures/F2_fixed_ranking_yield.*`
- `paper/figures/F3_reliability_transfer.*`

Supplementary/supporting artifacts:

```bash
bash scripts/run_supplementary.sh
```

## Decision-use experiments

The manuscript uses two probability-dependent decision-use experiments.

### Fixed-ranking expected-yield estimation

Candidate identities are fixed by a raw ranking score.
Observed successes are structural hits (`DockQ >= 0.23`), while predicted successes are sums of estimated probabilities over the same fixed set.
The primary metric is mean absolute error in predicted success fraction across targets (Yield MAE).

### Minimum-reliability filtering

Calibrated rules use `p >= q`.
Transferred raw-score rules use a score threshold chosen on General and then applied unchanged to external datasets.
The key outputs are observed precision and coverage as functions of the requested minimum reliability.

See `analysis/decision_use/README.md` for the frozen supporting artifacts.

## Data and provenance

Shipped evaluation/prediction files include:

- `data/abag_test_v2.csv`
- `data/general_v2.csv`
- `data/casp16_v2.csv`
- `data/abag_predictions_v3.csv`
- `data/general_predictions_v3.csv`
- `data/casp16_predictions_v3.csv`
- `data/casp16_bootstrap_summary.csv`
- `data/report_data_v3.json`

The original Ab-Ag training CSV is shipped as target-preserving shards under `data/abag_train_v2_parts/`.

Validate the shards:

```bash
python scripts/validate_abag_train_parts.py
```

Reconstruct a local merged CSV if needed:

```bash
python scripts/merge_abag_train_parts.py --output data/abag_train_v2.csv
```

See `DATA_LICENSE.md` for provenance and redistribution notes.

## Repository structure

```text
alphafold-complex-calibration/
├── analysis/             # frozen supporting analyses
├── data/                 # frozen evaluation datasets and prediction exports
├── models/               # locked MLP checkpoints and scalers
├── paper/                # manuscript-facing figures and tables
├── scripts/              # reproduction scripts
├── src/                  # lightweight public inference code
└── tests/                # smoke/integrity tests for the curated release
```

## Citation

See `CITATION.cff`.

## License

Software is MIT-licensed under `LICENSE`.
Data and model artifacts may have separate provenance constraints; see `DATA_LICENSE.md`.

## Limitations

- no raw AlphaFold output parser is included
- benchmark redistribution status remains under review for some upstream-derived tables
- AFDB raw CIF/PAE files are not redistributed; only frozen derived analysis outputs are shipped

## Workshop Version

A five-page workshop version of this work is prepared for a NeurIPS 2026
workshop. It focuses on isotonic calibration of ipTM and fixed-ranking yield
estimation across Ab-Ag, General, and AFDB evaluations. The workshop main
narrative excludes the multi-feature MLP and iPAE analyses; iPAE is retained
only in appendix artifacts. See `analysis/workshop/` for the frozen
workshop-specific outputs.
