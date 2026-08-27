# AFDB Workshop Recalibration Summary

- Source: `analysis/afdb/afdb_positive_dockq_features.csv`
- General source: `alphafold-complex-calibration/data/general_v2.csv`
- AFDB finite-DockQ universe asserted at 304 rows.
- Raw ipTM, raw ipSAEmax, and frozen General isotonic ipTM are each evaluated once on all 304 AFDB complexes and rendered as fixed horizontal reference lines.
- Local recalibration uses paired disjoint `StratifiedShuffleSplit` partitions shared by ipTM and ipSAEmax.
- Repeats: 100
- Seed base: 42
- Local calibration sizes: 5, 10, 15, ..., 100 AFDB complexes (1.6% to 32.9% of the 304-complex universe).
- Repeat-level local results: `analysis/workshop/workshop_afdb_recalibration_repeats.csv`.

## DockQ >= 0.23
- Raw ipTM: full-AFDB fixed Brier 0.1418 (no split-wise SD).
- Isotonic ipTM (General frozen): full-AFDB fixed Brier 0.1561 (no split-wise SD).
- Isotonic ipTM (local AFDB): best local-holdout mean Brier 0.1377 ± 0.0114 at train_size=100.
- Raw ipSAEmax: full-AFDB fixed Brier 0.1334 (no split-wise SD).
- Isotonic ipSAEmax (local AFDB): best local-holdout mean Brier 0.1182 ± 0.0113 at train_size=100.

## DockQ >= 0.49
- Raw ipTM: full-AFDB fixed Brier 0.1464 (no split-wise SD).
- Isotonic ipTM (General frozen): full-AFDB fixed Brier 0.1873 (no split-wise SD).
- Isotonic ipTM (local AFDB): best local-holdout mean Brier 0.1450 ± 0.0103 at train_size=85.
- Raw ipSAEmax: full-AFDB fixed Brier 0.1326 (no split-wise SD).
- Isotonic ipSAEmax (local AFDB): best local-holdout mean Brier 0.1341 ± 0.0119 at train_size=100.

## DockQ >= 0.8
- Raw ipTM: full-AFDB fixed Brier 0.2124 (no split-wise SD).
- Isotonic ipTM (General frozen): full-AFDB fixed Brier 0.1122 (no split-wise SD).
- Isotonic ipTM (local AFDB): best local-holdout mean Brier 0.1099 ± 0.0102 at train_size=100.
- Raw ipSAEmax: full-AFDB fixed Brier 0.1776 (no split-wise SD).
- Isotonic ipSAEmax (local AFDB): best local-holdout mean Brier 0.0976 ± 0.0120 at train_size=100.
