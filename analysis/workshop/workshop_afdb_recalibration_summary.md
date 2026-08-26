# AFDB Workshop Recalibration Summary

- Source: `analysis/afdb/afdb_positive_dockq_features.csv`
- General source: `alphafold-complex-calibration/data/general_v2.csv`
- AFDB finite-DockQ universe asserted at 304 rows.
- Local recalibration uses paired disjoint `StratifiedShuffleSplit` partitions shared by ipTM and ipSAEmax.
- Repeats: 100
- Seed base: 42
- `train_size = 1` is marked unavailable because a disjoint stratified binary calibration split cannot be defined with fewer than two calibration examples.

## DockQ >= 0.23
- Raw ipTM: best mean Brier 0.1406 ± 0.0067 at train_size=100.
- Isotonic ipTM (General frozen): best mean Brier 0.1548 ± 0.0090 at train_size=100.
- Isotonic ipTM (local AFDB): best mean Brier 0.1377 ± 0.0114 at train_size=100.
- Raw ipSAEmax: best mean Brier 0.1322 ± 0.0086 at train_size=100.
- Isotonic ipSAEmax (local AFDB): best mean Brier 0.1182 ± 0.0113 at train_size=100.

## DockQ >= 0.49
- Raw ipTM: best mean Brier 0.1460 ± 0.0050 at train_size=50.
- Isotonic ipTM (General frozen): best mean Brier 0.1865 ± 0.0109 at train_size=100.
- Isotonic ipTM (local AFDB): best mean Brier 0.1466 ± 0.0136 at train_size=100.
- Raw ipSAEmax: best mean Brier 0.1314 ± 0.0056 at train_size=50.
- Isotonic ipSAEmax (local AFDB): best mean Brier 0.1341 ± 0.0119 at train_size=100.

## DockQ >= 0.8
- Raw ipTM: best mean Brier 0.2121 ± 0.0038 at train_size=20.
- Isotonic ipTM (General frozen): best mean Brier 0.1112 ± 0.0032 at train_size=50.
- Isotonic ipTM (local AFDB): best mean Brier 0.1099 ± 0.0102 at train_size=100.
- Raw ipSAEmax: best mean Brier 0.1775 ± 0.0017 at train_size=5.
- Isotonic ipSAEmax (local AFDB): best mean Brier 0.0976 ± 0.0120 at train_size=100.
