# Post-hoc Calibration of AlphaFold Confidence Scores for Protein Complex Quality Assessment

Code, locked models, evaluation data, and reproduction scripts for calibrating AlphaFold3 and AlphaFold-Multimer confidence scores into probabilities of complex structural quality.

## Quick Start

### Apply the locked calibrator in three lines

```python
from src.predict import CalibratedPredictor
import pandas as pd

probs = CalibratedPredictor.load("models", domain="abag").predict(pd.read_csv("your_predictions.csv"))
print(probs.head())
```

Expected input columns:
`iface_pae_mean`, `interchain_block_mean`, `iptm`, `ptm`

`ranking_score` is computed automatically as `0.8 * iptm + 0.2 * ptm` if missing.

### Reproduce the paper artifacts

```bash
pip install -r requirements.txt
bash scripts/run_all.sh
```

This regenerates the public reproduction tables and figures from the locked release data.

## Included Data

`data/abag_test_v2.csv`
Ab-Ag evaluation set.

`data/general_v2.csv`
General multimer benchmark.

`data/casp16_v2.csv`
CASP16 evaluation set.

`data/casp16_bootstrap_summary.csv`
Locked bootstrap summary used for the CASP16 paper table.

`data/abag_predictions_v3.csv`, `data/general_predictions_v3.csv`, `data/casp16_predictions_v3.csv`
Locked per-model prediction exports used to regenerate the final paper figures and tables without hidden retraining state.

`data/report_data_v3.json`
Single-source summary of the locked paper results.

The Ab-Ag training set is included in split form under `data/abag_train_v2_parts/` because the unsplit CSV is 277 MB and exceeds GitHub's per-file limit. Use `scripts/merge_abag_train_parts.py` if you need a single file locally. The public reproduction scripts still use the locked prediction exports rather than refitting from raw training rows.

## Models

`models/locked_ce_5feat_abag.pt`
`models/scaler_5feat_abag.pkl`

`models/locked_ce_5feat_general.pt`
`models/scaler_5feat_general.pkl`

Architecture:
`5 -> 64 -> 32 -> 4`, ReLU, dropout `0.1`, cumulative softmax over DockQ bins.

Use `domain="abag"` for antibody-antigen complexes and `domain="general"` for other complexes.

## Feature Definition

The public model uses five features:

| Feature | Meaning |
| --- | --- |
| `iface_pae_mean` | Mean PAE over cross-chain residue pairs within 8A predicted Cbeta contacts |
| `interchain_block_mean` | Mean PAE over all cross-chain residue pairs |
| `iptm` | Interface predicted TM-score |
| `ptm` | Predicted TM-score |
| `ranking_score` | `0.8 * iptm + 0.2 * ptm` |

See `src/features.py` for array-level feature computation utilities from coordinates and PAE matrices.

## Repository Layout

```text
alphafold-complex-calibration/
├── models/
├── data/
├── src/
├── scripts/
├── analysis/
│   └── afdb/
└── paper/
    ├── figures/
    └── tables/
```

## Paper Artifacts

Reference figures are shipped in `paper/figures/`.
Reference tables are shipped in `paper/tables/`.

The reproduction scripts generate public rederived artifacts alongside those locked references:

`scripts/reproduce_table1_abag.py`
`scripts/reproduce_table2_general.py`
`scripts/reproduce_table3_casp16.py`
`scripts/reproduce_table4_afdb.py`
`scripts/reproduce_figure1.py`
`scripts/reproduce_figure2.py`
`scripts/reproduce_figure3.py`
`scripts/merge_abag_train_parts.py`

## License

MIT. See [LICENSE](LICENSE).
