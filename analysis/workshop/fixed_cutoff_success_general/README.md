# Fixed Cutoff Success-Fraction Analysis (General OOF)

Frozen input: `data/general_predictions_v3.csv` (5,496 rows). No score was fitted or refitted during this analysis.

For each fixed cutoff $c$, the reported value is $P(\mathrm{DockQ} \ge t \mid s \ge c)$. The cutoff grid is 0.00 to 0.95 in increments of 0.05. Rows with zero selected models are retained in the CSV with an undefined success fraction and omitted from the plotted line.

`c=0.80` is reported for every method without substitution. The separate pDockQ2 `c=0.23` rows are descriptive fixed-cutoff rows, included because .8 may retain relatively few pDockQ2 predictions.

## c=0.80 and descriptive pDockQ2 c=0.23

| threshold | threshold_val | cutoff_label | method | n_selected | fraction_selected | observed_success_fraction |
|---|---|---|---|---|---|---|
| acceptable | 0.2300 | hard-coded c=0.80 | Raw ipTM | 2051 | 0.3732 | 0.9274 |
| acceptable | 0.2300 | hard-coded c=0.80 | Isotonic ipTM | 2160 | 0.3930 | 0.9153 |
| acceptable | 0.2300 | hard-coded c=0.80 | pDockQ2 (published) | 660 | 0.1201 | 0.9197 |
| acceptable | 0.2300 | hard-coded c=0.80 | pDockQ2 (General refit) | 0 | 0.0000 | NA |
| medium | 0.4900 | hard-coded c=0.80 | Raw ipTM | 2051 | 0.3732 | 0.8445 |
| medium | 0.4900 | hard-coded c=0.80 | Isotonic ipTM | 1330 | 0.2420 | 0.9015 |
| medium | 0.4900 | hard-coded c=0.80 | pDockQ2 (published) | 660 | 0.1201 | 0.8697 |
| medium | 0.4900 | hard-coded c=0.80 | pDockQ2 (General refit) | 0 | 0.0000 | NA |
| high | 0.8000 | hard-coded c=0.80 | Raw ipTM | 2051 | 0.3732 | 0.4188 |
| high | 0.8000 | hard-coded c=0.80 | Isotonic ipTM | 73 | 0.0133 | 0.8630 |
| high | 0.8000 | hard-coded c=0.80 | pDockQ2 (published) | 660 | 0.1201 | 0.5833 |
| high | 0.8000 | hard-coded c=0.80 | pDockQ2 (General refit) | 0 | 0.0000 | NA |
| acceptable | 0.2300 | descriptive pDockQ2 c=0.23 | pDockQ2 (published) | 3263 | 0.5937 | 0.7827 |
| acceptable | 0.2300 | descriptive pDockQ2 c=0.23 | pDockQ2 (General refit) | 3846 | 0.6998 | 0.7444 |
| medium | 0.4900 | descriptive pDockQ2 c=0.23 | pDockQ2 (published) | 3263 | 0.5937 | 0.6384 |
| medium | 0.4900 | descriptive pDockQ2 c=0.23 | pDockQ2 (General refit) | 3846 | 0.6998 | 0.5837 |
| high | 0.8000 | descriptive pDockQ2 c=0.23 | pDockQ2 (published) | 3263 | 0.5937 | 0.2884 |
| high | 0.8000 | descriptive pDockQ2 c=0.23 | pDockQ2 (General refit) | 3846 | 0.6998 | 0.2533 |
