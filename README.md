# Post-hoc Calibration of AlphaFold Confidence Scores for Protein Complex Quality Prediction

Code, locked models, release data, and reproduction scripts for the preprint:

**Post-hoc Calibration of AlphaFold Confidence Scores for Protein Complex Quality Prediction**

This repository is a frozen preprint release. It is currently private and intended
to become public at manuscript submission without changing scientific results.

## Scope

The repository ships:

- locked Ab-Ag and General calibrated MLP models
- evaluation datasets and frozen prediction exports used in the paper
- public reproduction scripts for the shipped tables and figures
- utilities for reconstructing the split Ab-Ag training CSV

It does **not** ship a full automated parser for raw AlphaFold3 or
AlphaFold-Multimer output directories. `src/features.py` works on
pre-extracted arrays that are already aligned to a PAE matrix.

## Quick Start

### Installation

Recommended Python: `3.11`

Tested environment:

- Python `3.11`
- CPU-only inference supported
- CUDA not required for any shipped script

Install the user-facing dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For the exact tested package set, see `requirements-lock.txt`.

### Run the locked calibrator

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

### Required input columns

Minimum required columns:

- `iface_pae_mean`
- `interchain_block_mean`
- `iptm`
- `ptm`

Optional derived column:

- `ranking_score`

If `ranking_score` is absent, it is computed as:

```text
0.8 * iptm + 0.2 * ptm
```

Output columns:

- `p_acceptable`: estimated probability that `DockQ >= 0.23`
- `p_medium`: estimated probability that `DockQ >= 0.49`
- `p_high`: estimated probability that `DockQ >= 0.80`

These are post-hoc calibrated probabilities from a locked 4-class cumulative
MLP. They are not guarantees and should not be interpreted outside the model's
training domain without additional validation.

## Feature Assumptions

The public model uses five features:

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
- the shipped feature helpers accept pre-extracted arrays; raw AF3/AFM directory parsing is not part of this release

## Reproducing the Paper Artifacts

Run all shipped reproduction scripts:

```bash
bash scripts/run_all.sh
```

This regenerates:

- `paper/tables/tab_abag_main_reproduced.*`
- `paper/tables/tab_general_main_reproduced.*`
- `paper/tables/tab_casp16_bootstrap_reproduced.*`
- `paper/tables/tab_afdb_*`
- `paper/figures/F1_reliability_abag.*`
- `paper/figures/F2_matched_precision_bars.*`
- `paper/figures/F3_permutation_importance.*`

The scripts use only files shipped in this repository.

## Checksum Verification

Verify all frozen artifacts:

```bash
bash scripts/verify_manifest.sh
```

This checks the repository-wide `MANIFEST.sha256`.

## Ab-Ag Training Shards

The original Ab-Ag training CSV is too large for a single GitHub-tracked file,
so the public release ships target-preserving shards under:

```text
data/abag_train_v2_parts/
```

Validate the shards:

```bash
python scripts/validate_abag_train_parts.py
```

Reconstruct a single local CSV:

```bash
python scripts/merge_abag_train_parts.py --output data/abag_train_v2.csv
```

The merge script validates checksums and refuses to overwrite an existing file
unless `--force` is passed.

## Included Data

- `data/abag_test_v2.csv`: Ab-Ag evaluation set
- `data/general_v2.csv`: General multimer benchmark
- `data/casp16_v2.csv`: CASP16 evaluation set
- `data/casp16_bootstrap_summary.csv`: locked CASP16 bootstrap table source
- `data/abag_predictions_v3.csv`
- `data/general_predictions_v3.csv`
- `data/casp16_predictions_v3.csv`
- `data/report_data_v3.json`: locked paper summary JSON

Local cluster path columns were removed from the public CSV releases because
they were internal-only audit metadata and are not required for scientific
reproduction.

See `DATA_LICENSE.md` for provenance and redistribution notes.

## Models

Shipped model artifacts:

- `models/locked_ce_5feat_abag.pt`
- `models/scaler_5feat_abag.pkl`
- `models/locked_ce_5feat_general.pt`
- `models/scaler_5feat_general.pkl`

Locked architecture:

```text
5 -> 64 -> 32 -> 4
```

with ReLU activations, dropout `0.1`, and cumulative softmax probabilities
over DockQ bins.


## Decision-Use Experiments

The paper demonstrates two tasks where calibrated probabilities provide value beyond ranking.

### Expected-yield estimation
Among a fixed set of top-K predictions, calibrated probabilities estimate the number of structurally successful models more accurately than treating raw scores as probabilities.

### Reliability-controlled filtering
A fixed calibrated rule (`P >= q`) maintains the requested reliability level across datasets more consistently than transferred raw-score thresholds, at a coverage cost.

See `analysis/decision_use/README.md` for details and reproduction.

## Repository Layout

```text
alphafold-complex-calibration/
├── analysis/
├── data/
├── models/
├── paper/
│   ├── figures/
│   └── tables/
├── scripts/
├── src/
├── tests/
├── CITATION.cff
├── DATA_LICENSE.md
├── MANIFEST.sha256
└── RELEASE_NOTES.md
```

## Citation

See `CITATION.cff`.

Preprint DOI: pending.

## License

Software is released under MIT: see `LICENSE`.

Data and derived result files may have different provenance and redistribution
constraints: see `DATA_LICENSE.md`.

## Contact

Public correspondence email is not yet attached to this release. Until that is
added, use the repository issue tracker for release-related questions.
