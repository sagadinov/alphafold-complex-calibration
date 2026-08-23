# Workshop Paper Analysis

NeurIPS 2026 workshop submission: isotonic calibration of AlphaFold complex
confidence scores.

## Scope

| | Workshop | Full paper (later) |
| --- | --- | --- |
| Datasets | Ab-Ag, General, AFDB | + CASP16 |
| Main methods | Raw ipTM, isotonic ipTM, pDockQ2, ipSAEmax | + MLP 5-feat CE |
| Yield experiment | ipTM-ranked, K=5/10/20 | + iPAE-ranked |
| Main figures | Reliability and fixed-ranking yield | + transfer operating curves |
| iPAE | Appendix tables only | Expanded supporting analysis |

## Key files

- `workshop_yield_simplified.csv` - observed versus predicted success fraction
  for raw-ipTM-ranked fixed candidate sets.
- `workshop_fair_coverage.csv` - training-fitted, matched-precision coverage
  comparison for raw and isotonic ipTM.
- `workshop_afdb_304_metrics.csv` - AFDB evaluation on the audited 304-row
  finite-DockQ universe.
- `workshop_abag_table.csv` - Ab-Ag calibration metrics without MLP.
- `workshop_general_table.csv` - General calibration metrics without MLP.
- `workshop_report_v3.md` - concise provenance and scope report.

The release repository remains private until manuscript submission. These are
frozen outputs; raw AF3/AFM prediction files are not redistributed.

## Macro versus global yield

`workshop_yield_simplified.csv` contains two distinct aggregations:

- `macro_fixed_K`: equal-weight per-target yield for the same raw-ipTM top-K
  candidates.
- `global_all_models`: model-weighted yield pooled over every finite scored
  model, with no K restriction.

`workshop_yield_macro_vs_global.csv` additionally contains K=5
hard/medium/easy target-difficulty strata and signed prediction errors.
