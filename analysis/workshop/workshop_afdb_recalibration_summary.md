# AFDB Workshop Recalibration Summary

- Source: `analysis/afdb/afdb_positive_dockq_features.csv`
- General source: `alphafold-complex-calibration/data/general_v2.csv`
- AFDB finite-DockQ universe asserted at 304 rows.
- Local recalibration uses paired disjoint `StratifiedShuffleSplit` partitions shared by ipTM and ipSAEmax.
- Repeats: 100
- Seed base: 42
- `train_size = 1` is marked unavailable because a disjoint stratified binary calibration split cannot be defined with fewer than two calibration examples.

## DockQ >= 0.23
- Raw ipTM: best mean Brier 0.1416 ± 0.0027 at train_size=20.
- Isotonic ipTM (General frozen): best mean Brier 0.1557 ± 0.0035 at train_size=20.
- Isotonic ipTM (local AFDB): best mean Brier 0.1437 ± 0.0113 at train_size=50.
- Raw ipSAEmax: best mean Brier 0.1329 ± 0.0035 at train_size=20.
- Isotonic ipSAEmax (local AFDB): best mean Brier 0.1258 ± 0.0127 at train_size=50.

## DockQ >= 0.49
- Raw ipTM: best mean Brier 0.1460 ± 0.0050 at train_size=50.
- Isotonic ipTM (General frozen): best mean Brier 0.1870 ± 0.0071 at train_size=50.
- Isotonic ipTM (local AFDB): best mean Brier 0.1491 ± 0.0110 at train_size=50.
- Raw ipSAEmax: best mean Brier 0.1314 ± 0.0056 at train_size=50.
- Isotonic ipSAEmax (local AFDB): best mean Brier 0.1391 ± 0.0122 at train_size=50.

## DockQ >= 0.8
- Raw ipTM: best mean Brier 0.2121 ± 0.0038 at train_size=20.
- Isotonic ipTM (General frozen): best mean Brier 0.1112 ± 0.0032 at train_size=50.
- Isotonic ipTM (local AFDB): best mean Brier 0.1139 ± 0.0140 at train_size=50.
- Raw ipSAEmax: best mean Brier 0.1775 ± 0.0017 at train_size=5.
- Isotonic ipSAEmax (local AFDB): best mean Brier 0.1033 ± 0.0125 at train_size=50.
