# AFDB Positive-Only DockQ Analysis

- Positive AFDB rows: 324
- Finite DockQ rows: 304
- DockQ status counts: {'ok_total_full': 184, 'ok_total_mapped': 120, 'no_candidates': 17, 'missing_pred': 3}

## Acceptable DockQ >= 0.23

| method | n_valid | n_pos | auroc | auprc | brier | ece | mcc_at_05 | ppv_at_05 | recall_at_05 | selected_p_ge_09 | precision_p_ge_09 | recall_p_ge_09 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ipSAEmax | 324 | 152 | 0.894 | 0.862 | 0.138 | 0.102 | 0.646 | 0.823 | 0.796 | 3.000 | 1.000 | 0.020 |
| MLP 5-feat CE | 320 | 152 | 0.871 | 0.826 | 0.165 | 0.121 | 0.520 | 0.795 | 0.664 | 38.000 | 0.921 | 0.230 |
| Raw ranking conf. | 321 | 152 | 0.866 | 0.825 | 0.155 | 0.107 | 0.569 | 0.779 | 0.763 | 13.000 | 0.923 | 0.079 |
| Raw ipTM | 324 | 152 | 0.868 | 0.810 | 0.150 | 0.091 | 0.578 | 0.784 | 0.763 | 15.000 | 0.867 | 0.086 |
| pDockQ2max (Steinegger) | 324 | 152 | 0.863 | 0.809 | 0.273 | 0.277 | 0.345 | 0.823 | 0.336 | 6.000 | 1.000 | 0.039 |
| Iso. ipTM | 324 | 152 | 0.866 | 0.798 | 0.161 | 0.105 | 0.522 | 0.814 | 0.632 | 31.000 | 0.839 | 0.171 |
| 1/(1+iPAE) | 320 | 152 | 0.854 | 0.795 | 0.329 | 0.349 | 0.000 | 0.000 | 0.000 | 0.000 |  | 0.000 |
| pDockQ2 (our computation) | 320 | 152 | 0.835 | 0.787 | 0.305 | 0.309 | 0.312 | 0.851 | 0.263 | 1.000 | 1.000 | 0.007 |
| Iso. iPAE | 320 | 152 | 0.850 | 0.779 | 0.190 | 0.141 | 0.473 | 0.786 | 0.605 | 0.000 |  | 0.000 |
| Steinegger fixed filter | 324 | 152 | 0.683 | 0.629 |  |  | 0.418 | 0.821 | 0.454 |  |  |  |

## Matched 90% Precision

| threshold_name | threshold | method | selected | precision | recall | mcc | n_valid |
| --- | --- | --- | --- | --- | --- | --- | --- |
| acceptable | 0.872 | MLP 5-feat CE | 51 | 0.902 | 0.303 | 0.372 | 320 |
| acceptable | 0.832 | Raw ranking conf. | 43 | 0.907 | 0.257 | 0.341 | 321 |
| acceptable | 0.832 | ipSAEmax | 34 | 0.912 | 0.204 | 0.304 | 324 |
| acceptable | 0.346 | 1/(1+iPAE) | 21 | 0.905 | 0.125 | 0.228 | 320 |
| acceptable | 0.871 | pDockQ2max (Steinegger) | 14 | 0.929 | 0.086 | 0.196 | 324 |
| acceptable | 0.807 | pDockQ2 (our computation) | 11 | 0.909 | 0.066 | 0.164 | 320 |
| acceptable | 0.940 | Raw ipTM | 4 | 1.000 | 0.026 | 0.119 | 324 |
| acceptable |  | Steinegger fixed filter | 0 |  | 0.000 |  | 324 |
| acceptable |  | Iso. ipTM | 0 |  | 0.000 |  | 324 |
| acceptable |  | Iso. iPAE | 0 |  | 0.000 |  | 320 |

## Steinegger Fixed Transfer

| threshold_name | threshold | selected | successes | success_rate | recall | n_pos | n_total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| acceptable | 0.230 | 84 | 69 | 0.821 | 0.454 | 152 | 324 |
| medium | 0.490 | 84 | 59 | 0.702 | 0.476 | 124 | 324 |
| high | 0.800 | 84 | 36 | 0.429 | 0.692 | 52 | 324 |
