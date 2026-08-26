# Workshop Figure Results Summary

- Figure 1, Ab-Ag, DockQ >= 0.23: ECE 0.1462 -> 0.0282, Brier 0.1213 -> 0.0929.
- Figure 1, Ab-Ag, DockQ >= 0.49: ECE 0.1907 -> 0.0143, Brier 0.1327 -> 0.0821.
- Figure 1, Ab-Ag, DockQ >= 0.80: ECE 0.3336 -> 0.0133, Brier 0.2032 -> 0.0716.
- Figure 1, General, DockQ >= 0.23: ECE 0.0774 -> 0.0195, Brier 0.1379 -> 0.1307.
- Figure 1, General, DockQ >= 0.49: ECE 0.1957 -> 0.0086, Brier 0.1728 -> 0.1186.
- Figure 1, General, DockQ >= 0.80: ECE 0.4428 -> 0.0118, Brier 0.3224 -> 0.1055.

- Figure 2 published, DockQ >= 0.23, K=20: observed 7.78/20, Raw ipTM 10.32/20, Isotonic ipTM 8.05/20, pDockQ2 published 3.76/20.
- Figure 2 published, DockQ >= 0.49, K=20: observed 6.46/20, Raw ipTM 10.32/20, Isotonic ipTM 6.42/20, pDockQ2 published 3.76/20.
- Figure 2 published, DockQ >= 0.80, K=20: observed 3.30/20, Raw ipTM 10.32/20, Isotonic ipTM 3.46/20, pDockQ2 published 3.76/20.

- Figure 3: `train_size = 1` is unavailable under the paired disjoint stratified protocol; the curves therefore begin at 5 examples.
- Figure 3, DockQ >= 0.23: local isotonic ipTM Brier reaches 0.1377; local isotonic ipSAEmax reaches 0.1182; frozen General isotonic ipTM averages 0.1559 across the matched holdout splits.
- Figure 3, DockQ >= 0.49: local isotonic ipTM Brier reaches 0.1466; local isotonic ipSAEmax reaches 0.1341; frozen General isotonic ipTM averages 0.1871 across the matched holdout splits.
- Figure 3, DockQ >= 0.80: local isotonic ipTM Brier reaches 0.1099; local isotonic ipSAEmax reaches 0.0976; frozen General isotonic ipTM averages 0.1118 across the matched holdout splits.
