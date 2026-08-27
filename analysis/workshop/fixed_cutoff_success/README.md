# Fixed Cutoff Success-Fraction Analysis (Ab-Ag Test)

Frozen input: `data/abag_predictions_v3.csv` (62,681 held-out models). No score was fitted or refitted on the test set.

For each fixed cutoff $c$, the reported value is $P(\mathrm{DockQ} \ge t \mid s \ge c)$. The cutoff grid is 0.00 to 0.95 in increments of 0.05. Rows with zero selected models are retained in the CSV with an undefined success fraction and omitted from the plotted line.

`c=0.80` is reported for every method without substitution. The separate pDockQ2 `c=0.23` rows are descriptive fixed-cutoff rows, included because .8 may retain relatively few pDockQ2 predictions.

## c=0.80 and descriptive pDockQ2 c=0.23

| threshold | threshold_val | cutoff_label | method | n_selected | fraction_selected | observed_success_fraction |
|---|---|---|---|---|---|---|
| acceptable | 0.2300 | hard-coded c=0.80 | Raw ipTM | 15978 | 0.2549 | 0.9114 |
| acceptable | 0.2300 | hard-coded c=0.80 | Isotonic ipTM | 16510 | 0.2634 | 0.9080 |
| acceptable | 0.2300 | hard-coded c=0.80 | pDockQ2 (published) | 1421 | 0.0227 | 0.9901 |
| acceptable | 0.2300 | hard-coded c=0.80 | pDockQ2 (Ab-Ag refit) | 1067 | 0.0170 | 0.9906 |
| medium | 0.4900 | hard-coded c=0.80 | Raw ipTM | 15978 | 0.2549 | 0.8308 |
| medium | 0.4900 | hard-coded c=0.80 | Isotonic ipTM | 11842 | 0.1889 | 0.8577 |
| medium | 0.4900 | hard-coded c=0.80 | pDockQ2 (published) | 1421 | 0.0227 | 0.9353 |
| medium | 0.4900 | hard-coded c=0.80 | pDockQ2 (Ab-Ag refit) | 1067 | 0.0170 | 0.9288 |
| high | 0.8000 | hard-coded c=0.80 | Raw ipTM | 15978 | 0.2549 | 0.5097 |
| high | 0.8000 | hard-coded c=0.80 | Isotonic ipTM | 0 | 0.0000 | NA |
| high | 0.8000 | hard-coded c=0.80 | pDockQ2 (published) | 1421 | 0.0227 | 0.7565 |
| high | 0.8000 | hard-coded c=0.80 | pDockQ2 (Ab-Ag refit) | 1067 | 0.0170 | 0.7526 |
| acceptable | 0.2300 | descriptive pDockQ2 c=0.23 | pDockQ2 (published) | 15762 | 0.2515 | 0.9381 |
| acceptable | 0.2300 | descriptive pDockQ2 c=0.23 | pDockQ2 (Ab-Ag refit) | 23351 | 0.3725 | 0.8188 |
| medium | 0.4900 | descriptive pDockQ2 c=0.23 | pDockQ2 (published) | 15762 | 0.2515 | 0.8717 |
| medium | 0.4900 | descriptive pDockQ2 c=0.23 | pDockQ2 (Ab-Ag refit) | 23351 | 0.3725 | 0.7135 |
| high | 0.8000 | descriptive pDockQ2 c=0.23 | pDockQ2 (published) | 15762 | 0.2515 | 0.5214 |
| high | 0.8000 | descriptive pDockQ2 c=0.23 | pDockQ2 (Ab-Ag refit) | 23351 | 0.3725 | 0.3841 |
