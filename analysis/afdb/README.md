# AFDB Confidence Benchmark Comparison

## Source
Steinegger et al. AFDB predicted-complex confidence benchmark.
The local benchmark table has 691 rows: 324 positive and 367 negative labels.
Positive means an experimentally validated complex is available in PDB.

## Data
- Source benchmark: `../../data/AFDB Complexes Supplementary Data__Confidence_benchmark_PDB_access.csv`
- Sheet scores: ipTM, pLDDT, ipSAE min/max, LIS min/max, pDockQ2 min/max
- Computed by us from raw CIF + PAE: iPAE over 8A predicted Cb contacts, interchain_block_mean, pTM, ranking_score

## Raw model files
- Downloaded from AFDB/NVIDIA bulk FTP homodimer and heterodimer archives.
- 687 / 691 benchmark entries had CIF + PAE files extracted successfully.
- 4 archive entries were missing expected members and were excluded from recomputed-feature methods.
- 679 / 687 extracted entries have finite interface iPAE; 8 have zero predicted cross-chain contacts within 8A.
- Mapping/provenance: `bulk_tar_mapping.csv` and `bulk_extraction_manifest.csv`.
- Raw CIF + PAE files remain on Berzelius at:
  `/proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/af3_atlas/PAPER_REVISION/analysis/afdb_models/`
- Raw files are not committed to GitHub.

## Evaluations

### Binary label evaluation: positive/negative benchmark labels
Primary comparison uses General-trained calibrators/models, matching the AFDB general-complex domain and the CASP16 protocol.

Files:
- `full691_comparison.csv`: AUROC, AUPRC, MCC/PPV/recall at 0.5, all methods
- `full691_matched_precision.csv`: matched 90% precision comparison
- `full691_pr_curve.pdf/png`: precision-recall curves
- `full691_summary.md`: generated summary
- `full691_abagtrained_comparison.csv`: secondary Ab-Ag-trained transfer run
- `training_regime_comparison.csv`: General-trained vs Ab-Ag-trained comparison

### DockQ threshold evaluation: positive subset only
For the 324 positive entries, DockQ was computed against listed experimental PDB candidates.
For each AFDB model, all listed candidate PDB IDs were tried and the best DockQ was retained with `best_pdb` and `best_chains` for audit.

Files:
- `afdb_positive_dockq.csv`: per-entry best DockQ and native PDB audit information
- `afdb_positive_dockq_features.csv`: merged features + DockQ labels
- `afdb_positive_dockq_full_comparison.csv`: DockQ >= 0.23 / 0.49 / 0.80 metrics
- `afdb_positive_dockq_matched_precision.csv`: matched 90% precision by DockQ threshold
- `afdb_positive_dockq_steinegger_transfer.csv`: fixed Steinegger rule success rate across DockQ thresholds
- `afdb_positive_dockq_pr_acceptable.pdf/png`: PR curve for DockQ >= 0.23
- `afdb_positive_dockq_summary.md`: generated summary

DockQ coverage:
- Positive rows: 324
- Finite DockQ rows: 304
- Status counts: ok_total_full=184, ok_total_mapped=120, no_candidates=17, missing_pred=3

## Key findings
1. ipSAEmax is the strongest overall ranker on the full AFDB benchmark.
2. On positive-only DockQ labels, MLP 5-feat CE gives the largest matched-90%-precision coverage at DockQ >= 0.23: 51 selected at 90.2% precision vs ipSAEmax 34 selected.
3. The Steinegger fixed filter is high precision but its structural success rate is threshold-dependent: 82.1% for DockQ >= 0.23, 70.2% for DockQ >= 0.49, 42.9% for DockQ >= 0.80.
4. General-trained calibrators transfer better to AFDB than Ab-Ag-trained calibrators, especially for MLP.
5. Calibrated probabilities provide user-adjustable confidence levels; fixed thresholds do not.

## Calibrator training
- Primary: General-trained (`models/locked_ce_5feat_general.pt`)
- Isotonic fitted on full `af3_atlas/PAPER_REVISION/data/general_v2.csv`
- Secondary/domain-transfer: Ab-Ag-trained (`models/locked_ce_5feat_abag.pt`)

## Reproduction scripts
- `run_comparison.py`: full benchmark comparison after CIF/PAE extraction
- `run_positive_dockq.py`: compute best DockQ over PDB candidates for positive entries
- `evaluate_positive_dockq.py`: evaluate DockQ-threshold metrics after DockQ scoring
