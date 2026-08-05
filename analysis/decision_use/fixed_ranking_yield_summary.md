# Decision-Use v2 Fixed-Ranking Summary

Primary fixed-ranking interpretation should focus on DockQ >= 0.23.
Candidate identities were fixed by the indicated raw score and were identical across probability estimators within each comparison universe.

## iptm-ranked candidate sets

### abag

| K | probability_method | n_targets | mae_hits | normalized_mae | signed_bias | pearson |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | Raw ipTM | 1257 | 1.4912 | 0.2982 | 0.6852 | 0.7661 |
| 5 | Isotonic ipTM | 1257 | 1.0273 | 0.2055 | 0.1380 | 0.7858 |
| 5 | MLP 5-feat CE | 1257 | 0.8953 | 0.1791 | 0.2725 | 0.8042 |
| 10 | Raw ipTM | 1257 | 2.8462 | 0.2846 | 1.3102 | 0.7772 |
| 10 | Isotonic ipTM | 1257 | 1.9595 | 0.1959 | 0.1965 | 0.7957 |
| 10 | MLP 5-feat CE | 1257 | 1.6653 | 0.1665 | 0.4160 | 0.8211 |
| 20 | Raw ipTM | 1257 | 5.4712 | 0.2736 | 2.5423 | 0.7824 |
| 20 | Isotonic ipTM | 1257 | 3.7026 | 0.1851 | 0.2660 | 0.8027 |
| 20 | MLP 5-feat CE | 1257 | 3.0949 | 0.1547 | 0.5663 | 0.8337 |
| 50 | Raw ipTM | 1128 | 12.7120 | 0.2542 | 5.9905 | 0.7990 |
| 50 | Isotonic ipTM | 1128 | 8.5397 | 0.1708 | 0.2234 | 0.8218 |
| 50 | MLP 5-feat CE | 1128 | 6.5919 | 0.1318 | 0.2225 | 0.8708 |

### general

| K | probability_method | n_targets | mae_hits | normalized_mae | signed_bias | pearson |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | Raw ipTM | 193 | 1.2618 | 0.2524 | 0.2044 | 0.8168 |
| 5 | Isotonic ipTM | 193 | 0.9612 | 0.1922 | -0.1375 | 0.8306 |
| 5 | MLP 5-feat CE | 193 | 0.9686 | 0.1937 | -0.1824 | 0.8320 |

### casp16

| K | probability_method | n_targets | mae_hits | normalized_mae | signed_bias | pearson |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | Raw ipTM | 25 | 1.4238 | 0.2848 | 0.4102 | 0.1842 |
| 5 | Isotonic ipTM | 25 | 1.4101 | 0.2820 | 0.5545 | 0.1474 |
| 5 | MLP 5-feat CE | 25 | 1.5517 | 0.3103 | 0.1120 | 0.1272 |
| 10 | Raw ipTM | 25 | 2.6342 | 0.2634 | 1.1893 | 0.3204 |
| 10 | Isotonic ipTM | 25 | 2.6136 | 0.2614 | 1.4233 | 0.2959 |
| 10 | MLP 5-feat CE | 25 | 2.8632 | 0.2863 | 0.5906 | 0.2635 |
| 20 | Raw ipTM | 24 | 5.6848 | 0.2842 | 2.6303 | 0.3877 |
| 20 | Isotonic ipTM | 24 | 5.4624 | 0.2731 | 3.1075 | 0.3411 |
| 20 | MLP 5-feat CE | 24 | 5.7817 | 0.2891 | 1.4900 | 0.3370 |
| 50 | Raw ipTM | 24 | 14.3131 | 0.2863 | 5.9412 | 0.4004 |
| 50 | Isotonic ipTM | 24 | 13.6863 | 0.2737 | 6.4809 | 0.3681 |
| 50 | MLP 5-feat CE | 24 | 13.8918 | 0.2778 | 2.5555 | 0.4242 |

## ipae-ranked candidate sets

### abag

| K | probability_method | n_targets | mae_hits | normalized_mae | signed_bias | pearson |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | Raw iPAE proxy | 1257 | 1.6800 | 0.3360 | -1.3263 | 0.7764 |
| 5 | Calibrated iPAE probability | 1257 | 1.0078 | 0.2016 | 0.3899 | 0.7992 |
| 5 | MLP 5-feat CE | 1257 | 0.8977 | 0.1795 | 0.3205 | 0.8057 |
| 10 | Raw iPAE proxy | 1257 | 3.2866 | 0.3287 | -2.6516 | 0.7808 |
| 10 | Calibrated iPAE probability | 1257 | 1.8849 | 0.1885 | 0.6201 | 0.8141 |
| 10 | MLP 5-feat CE | 1257 | 1.6492 | 0.1649 | 0.4898 | 0.8250 |
| 20 | Raw iPAE proxy | 1257 | 6.3718 | 0.3186 | -5.2188 | 0.7806 |
| 20 | Calibrated iPAE probability | 1257 | 3.5492 | 0.1775 | 0.9005 | 0.8241 |
| 20 | MLP 5-feat CE | 1257 | 3.0799 | 0.1540 | 0.6637 | 0.8362 |
| 50 | Raw iPAE proxy | 1128 | 15.4511 | 0.3090 | -13.1524 | 0.7900 |
| 50 | Calibrated iPAE probability | 1128 | 7.7870 | 0.1557 | 0.6795 | 0.8549 |
| 50 | MLP 5-feat CE | 1128 | 6.5919 | 0.1318 | 0.2225 | 0.8708 |

## Row-universe impact on target eligibility and selected identities

| dataset | ranking_family | dockq_threshold_name | K | n_targets_common | n_targets_pairwise | n_targets_overlap | n_changed_selected_id_sets | n_targets_only_pairwise | n_targets_only_common |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| abag | iptm | acceptable | 5 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | iptm | acceptable | 10 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | iptm | acceptable | 20 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | iptm | acceptable | 50 | 1128 | 1128 | 1128 | 0 | 0 | 0 |
| abag | iptm | medium | 5 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | iptm | medium | 10 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | iptm | medium | 20 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | iptm | medium | 50 | 1128 | 1128 | 1128 | 0 | 0 | 0 |
| abag | iptm | high | 5 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | iptm | high | 10 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | iptm | high | 20 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | iptm | high | 50 | 1128 | 1128 | 1128 | 0 | 0 | 0 |
| general | iptm | acceptable | 5 | 193 | 193 | 193 | 0 | 0 | 0 |
| general | iptm | medium | 5 | 193 | 193 | 193 | 0 | 0 | 0 |
| general | iptm | high | 5 | 193 | 193 | 193 | 0 | 0 | 0 |
| casp16 | iptm | acceptable | 5 | 25 | 25 | 25 | 0 | 0 | 0 |
| casp16 | iptm | acceptable | 10 | 25 | 25 | 25 | 0 | 0 | 0 |
| casp16 | iptm | acceptable | 20 | 24 | 24 | 24 | 0 | 0 | 0 |
| casp16 | iptm | acceptable | 50 | 24 | 24 | 24 | 0 | 0 | 0 |
| casp16 | iptm | medium | 5 | 25 | 25 | 25 | 0 | 0 | 0 |
| casp16 | iptm | medium | 10 | 25 | 25 | 25 | 0 | 0 | 0 |
| casp16 | iptm | medium | 20 | 24 | 24 | 24 | 0 | 0 | 0 |
| casp16 | iptm | medium | 50 | 24 | 24 | 24 | 0 | 0 | 0 |
| casp16 | iptm | high | 5 | 25 | 25 | 25 | 0 | 0 | 0 |
| casp16 | iptm | high | 10 | 25 | 25 | 25 | 0 | 0 | 0 |
| casp16 | iptm | high | 20 | 24 | 24 | 24 | 0 | 0 | 0 |
| casp16 | iptm | high | 50 | 24 | 24 | 24 | 0 | 0 | 0 |
| abag | ipae | acceptable | 5 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | ipae | acceptable | 10 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | ipae | acceptable | 20 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | ipae | acceptable | 50 | 1128 | 1128 | 1128 | 0 | 0 | 0 |
| abag | ipae | medium | 5 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | ipae | medium | 10 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | ipae | medium | 20 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | ipae | medium | 50 | 1128 | 1128 | 1128 | 0 | 0 | 0 |
| abag | ipae | high | 5 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | ipae | high | 10 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | ipae | high | 20 | 1257 | 1257 | 1257 | 0 | 0 | 0 |
| abag | ipae | high | 50 | 1128 | 1128 | 1128 | 0 | 0 | 0 |

