# AFDB Full Method Comparison

- Rows: 691
- Labels: {'negative': 367, 'positive': 324}
- Rows with computed iPAE/interchain features: 679 / 691
- Calibrator/MLP training CSV: `af3_atlas/PAPER_REVISION/data/general_v2.csv`
- MLP model: `models/locked_ce_5feat_general.pt`
- MLP scaler: `models/scaler_5feat_general.pkl`
- Labels are AFDB/PDB-access positive/negative labels, not DockQ thresholds. Ab-Ag calibrators are evaluated as transfer scores.
- Exact Steinegger fixed filter: `ipsae_max >= 0.6 and pdockq2_max >= 0.23`.

## Main Metrics at 0.5 Decision Threshold
| calibrator_threshold | method | n_valid | auroc | auprc | mcc_at_05 | precision_at_05 | recall_at_05 | tp | fp | tn | fn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| acceptable | Raw ipTM | 691 | 0.743 | 0.761 | 0.436 | 0.841 | 0.457 | 148 | 28 | 339 | 176 |
| acceptable | pDockQ2max (Steinegger) | 691 | 0.719 | 0.739 | 0.306 | 0.939 | 0.191 | 62 | 4 | 363 | 262 |
| acceptable | ipSAEmax | 691 | 0.755 | 0.773 | 0.486 | 0.907 | 0.454 | 147 | 15 | 352 | 177 |
| acceptable | 1/(1+iPAE) | 679 | 0.702 | 0.725 | 0.000 | 0.000 | 0.000 | 0 | 0 | 359 | 320 |
| acceptable | pDockQ2 (our computation) | 679 | 0.702 | 0.737 | 0.265 | 0.940 | 0.147 | 47 | 3 | 356 | 273 |
| acceptable | Raw ranking conf. | 687 | 0.733 | 0.761 | 0.454 | 0.856 | 0.464 | 149 | 25 | 341 | 172 |
| acceptable | Iso. ipTM | 691 | 0.741 | 0.748 | 0.382 | 0.849 | 0.364 | 118 | 21 | 346 | 206 |
| acceptable | Iso. iPAE | 679 | 0.698 | 0.713 | 0.368 | 0.830 | 0.366 | 117 | 24 | 335 | 203 |
| acceptable | MLP 5-feat CE | 679 | 0.731 | 0.760 | 0.409 | 0.858 | 0.397 | 127 | 21 | 338 | 193 |
| acceptable | Steinegger fixed filter | 691 | 0.621 | 0.589 | 0.360 | 0.933 | 0.259 | 84 | 6 | 361 | 240 |
| medium | Raw ipTM | 691 | 0.743 | 0.761 | 0.436 | 0.841 | 0.457 | 148 | 28 | 339 | 176 |
| medium | pDockQ2max (Steinegger) | 691 | 0.719 | 0.739 | 0.306 | 0.939 | 0.191 | 62 | 4 | 363 | 262 |
| medium | ipSAEmax | 691 | 0.755 | 0.773 | 0.486 | 0.907 | 0.454 | 147 | 15 | 352 | 177 |
| medium | 1/(1+iPAE) | 679 | 0.702 | 0.725 | 0.000 | 0.000 | 0.000 | 0 | 0 | 359 | 320 |
| medium | pDockQ2 (our computation) | 679 | 0.702 | 0.737 | 0.265 | 0.940 | 0.147 | 47 | 3 | 356 | 273 |
| medium | Raw ranking conf. | 687 | 0.733 | 0.761 | 0.454 | 0.856 | 0.464 | 149 | 25 | 341 | 172 |
| medium | Iso. ipTM | 691 | 0.737 | 0.733 | 0.381 | 0.915 | 0.299 | 97 | 9 | 358 | 227 |
| medium | Iso. iPAE | 679 | 0.696 | 0.703 | 0.308 | 0.939 | 0.194 | 62 | 4 | 355 | 258 |
| medium | MLP 5-feat CE | 679 | 0.735 | 0.762 | 0.365 | 0.953 | 0.253 | 81 | 4 | 355 | 239 |
| medium | Steinegger fixed filter | 691 | 0.621 | 0.589 | 0.360 | 0.933 | 0.259 | 84 | 6 | 361 | 240 |
| high | Raw ipTM | 691 | 0.743 | 0.761 | 0.436 | 0.841 | 0.457 | 148 | 28 | 339 | 176 |
| high | pDockQ2max (Steinegger) | 691 | 0.719 | 0.739 | 0.306 | 0.939 | 0.191 | 62 | 4 | 363 | 262 |
| high | ipSAEmax | 691 | 0.755 | 0.773 | 0.486 | 0.907 | 0.454 | 147 | 15 | 352 | 177 |
| high | 1/(1+iPAE) | 679 | 0.702 | 0.725 | 0.000 | 0.000 | 0.000 | 0 | 0 | 359 | 320 |
| high | pDockQ2 (our computation) | 679 | 0.702 | 0.737 | 0.265 | 0.940 | 0.147 | 47 | 3 | 356 | 273 |
| high | Raw ranking conf. | 687 | 0.733 | 0.761 | 0.454 | 0.856 | 0.464 | 149 | 25 | 341 | 172 |
| high | Iso. ipTM | 691 | 0.719 | 0.703 | 0.145 | 0.938 | 0.046 | 15 | 1 | 366 | 309 |
| high | Iso. iPAE | 679 | 0.697 | 0.675 | 0.000 | 0.000 | 0.000 | 0 | 0 | 359 | 320 |
| high | MLP 5-feat CE | 679 | 0.735 | 0.763 | 0.148 | 1.000 | 0.041 | 13 | 0 | 359 | 307 |
| high | Steinegger fixed filter | 691 | 0.621 | 0.589 | 0.360 | 0.933 | 0.259 | 84 | 6 | 361 | 240 |

## Matched 90% Precision
| calibrator_threshold | method | n_valid | threshold | selected | precision | recall | mcc |
| --- | --- | --- | --- | --- | --- | --- | --- |
| acceptable | Raw ipTM | 691 | 0.710 | 106 | 0.915 | 0.299 | 0.381 |
| acceptable | pDockQ2max (Steinegger) | 691 | 0.257 | 101 | 0.901 | 0.281 | 0.358 |
| acceptable | ipSAEmax | 691 | 0.493 | 165 | 0.903 | 0.460 | 0.487 |
| acceptable | 1/(1+iPAE) | 679 | 0.182 | 90 | 0.900 | 0.253 | 0.336 |
| acceptable | pDockQ2 (our computation) | 679 | 0.203 | 96 | 0.906 | 0.272 | 0.354 |
| acceptable | Raw ranking conf. | 687 | 0.689 | 106 | 0.906 | 0.299 | 0.375 |
| acceptable | Iso. ipTM | 691 | 0.756 | 80 | 0.963 | 0.238 | 0.358 |
| acceptable | Iso. iPAE | 679 | 0.583 | 90 | 0.900 | 0.253 | 0.336 |
| acceptable | MLP 5-feat CE | 679 | 0.645 | 120 | 0.900 | 0.338 | 0.398 |
| medium | Raw ipTM | 691 | 0.710 | 106 | 0.915 | 0.299 | 0.381 |
| medium | pDockQ2max (Steinegger) | 691 | 0.257 | 101 | 0.901 | 0.281 | 0.358 |
| medium | ipSAEmax | 691 | 0.493 | 165 | 0.903 | 0.460 | 0.487 |
| medium | 1/(1+iPAE) | 679 | 0.182 | 90 | 0.900 | 0.253 | 0.336 |
| medium | pDockQ2 (our computation) | 679 | 0.203 | 96 | 0.906 | 0.272 | 0.354 |
| medium | Raw ranking conf. | 687 | 0.689 | 106 | 0.906 | 0.299 | 0.375 |
| medium | Iso. ipTM | 691 | 0.541 | 106 | 0.915 | 0.299 | 0.381 |
| medium | Iso. iPAE | 679 | 0.369 | 90 | 0.900 | 0.253 | 0.336 |
| medium | MLP 5-feat CE | 679 | 0.372 | 113 | 0.903 | 0.319 | 0.386 |
| high | Raw ipTM | 691 | 0.710 | 106 | 0.915 | 0.299 | 0.381 |
| high | pDockQ2max (Steinegger) | 691 | 0.257 | 101 | 0.901 | 0.281 | 0.358 |
| high | ipSAEmax | 691 | 0.493 | 165 | 0.903 | 0.460 | 0.487 |
| high | 1/(1+iPAE) | 679 | 0.182 | 90 | 0.900 | 0.253 | 0.336 |
| high | pDockQ2 (our computation) | 679 | 0.203 | 96 | 0.906 | 0.272 | 0.354 |
| high | Raw ranking conf. | 687 | 0.689 | 106 | 0.906 | 0.299 | 0.375 |
| high | Iso. ipTM | 691 | 0.165 | 89 | 0.955 | 0.262 | 0.375 |
| high | Iso. iPAE | 679 | 0.074 | 90 | 0.900 | 0.253 | 0.336 |
| high | MLP 5-feat CE | 679 | 0.071 | 114 | 0.904 | 0.322 | 0.389 |