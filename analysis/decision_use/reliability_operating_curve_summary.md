# Decision-Use v2 Reliability Summary

Primary reliability interpretation should focus on DockQ >= 0.23.
Raw thresholds were frozen before the target bootstrap and were never refit inside the bootstrap.

## Ranking invariance audit

| score_family | dataset | dockq_threshold_name | fold_id | spearman | kendall | strict_ordering_inversions | isotonic_ties | n_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ipae | Ab-Ag | acceptable | all | 0.9977 | 0.9791 | 0 | 62560 | 62681 |
| ipae | Ab-Ag | high | all | 0.9974 | 0.9708 | 0 | 62585 | 62681 |
| ipae | Ab-Ag | medium | all | 0.9980 | 0.9765 | 0 | 62537 | 62681 |
| iptm | Ab-Ag | acceptable | all | 0.9962 | 0.9716 | 0 | 62639 | 62681 |
| iptm | Ab-Ag | high | all | 0.9933 | 0.9600 | 0 | 62653 | 62681 |
| iptm | Ab-Ag | medium | all | 0.9970 | 0.9760 | 0 | 62639 | 62681 |
| iptm | CASP16 | acceptable | all | 0.9929 | 0.9481 | 0 | 15657 | 16199 |
| iptm | CASP16 | high | all | 0.8698 | 0.7721 | 0 | 15715 | 16199 |
| iptm | CASP16 | medium | all | 0.9806 | 0.9189 | 0 | 15766 | 16199 |
| iptm | General | acceptable | 1 | 0.9951 | 0.9580 | 0 | 1072 | 1099 |
| iptm | General | acceptable | 2 | 0.9981 | 0.9732 | 0 | 1069 | 1099 |
| iptm | General | acceptable | 3 | 0.9957 | 0.9625 | 0 | 1074 | 1100 |
| iptm | General | acceptable | 4 | 0.9971 | 0.9681 | 0 | 1076 | 1100 |
| iptm | General | acceptable | 5 | 0.9969 | 0.9661 | 0 | 1076 | 1098 |
| iptm | General | high | 1 | 0.9913 | 0.9461 | 0 | 1077 | 1099 |
| iptm | General | high | 2 | 0.9937 | 0.9554 | 0 | 1074 | 1099 |
| iptm | General | high | 3 | 0.9826 | 0.9284 | 0 | 1082 | 1100 |
| iptm | General | high | 4 | 0.9925 | 0.9519 | 0 | 1074 | 1100 |
| iptm | General | high | 5 | 0.9909 | 0.9413 | 0 | 1084 | 1098 |
| iptm | General | medium | 1 | 0.9951 | 0.9565 | 0 | 1077 | 1099 |
| iptm | General | medium | 2 | 0.9974 | 0.9686 | 0 | 1074 | 1099 |
| iptm | General | medium | 3 | 0.9961 | 0.9611 | 0 | 1081 | 1100 |
| iptm | General | medium | 4 | 0.9974 | 0.9699 | 0 | 1073 | 1100 |
| iptm | General | medium | 5 | 0.9964 | 0.9634 | 0 | 1073 | 1098 |

## Missingness and row universes

| dataset | analysis_name | score_family | dockq_threshold_name | n_input_rows | n_finite_dockq | n_finite_raw_score | n_finite_isotonic_probability | n_finite_mlp_probability | comparison_universe | n_common_valid | n_dropped | drop_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ab-Ag | fixed_ranking_ipae | ipae | acceptable | 62681 | 62681 | 62681 | 62681 | 62681 | raw_iso_pairwise | 62681 | 0 | none |
| Ab-Ag | fixed_ranking_ipae | ipae | acceptable | 62681 | 62681 | 62681 | 62681 | 62681 | three_method_common | 62681 | 0 | none |
| Ab-Ag | fixed_ranking_ipae | ipae | high | 62681 | 62681 | 62681 | 62681 | 62681 | raw_iso_pairwise | 62681 | 0 | none |
| Ab-Ag | fixed_ranking_ipae | ipae | high | 62681 | 62681 | 62681 | 62681 | 62681 | three_method_common | 62681 | 0 | none |
| Ab-Ag | fixed_ranking_ipae | ipae | medium | 62681 | 62681 | 62681 | 62681 | 62681 | raw_iso_pairwise | 62681 | 0 | none |
| Ab-Ag | fixed_ranking_ipae | ipae | medium | 62681 | 62681 | 62681 | 62681 | 62681 | three_method_common | 62681 | 0 | none |
| Ab-Ag | fixed_ranking_iptm | iptm | acceptable | 62681 | 62681 | 62681 | 62681 | 62681 | raw_iso_pairwise | 62681 | 0 | none |
| Ab-Ag | fixed_ranking_iptm | iptm | acceptable | 62681 | 62681 | 62681 | 62681 | 62681 | three_method_common | 62681 | 0 | none |
| Ab-Ag | fixed_ranking_iptm | iptm | high | 62681 | 62681 | 62681 | 62681 | 62681 | raw_iso_pairwise | 62681 | 0 | none |
| Ab-Ag | fixed_ranking_iptm | iptm | high | 62681 | 62681 | 62681 | 62681 | 62681 | three_method_common | 62681 | 0 | none |
| Ab-Ag | fixed_ranking_iptm | iptm | medium | 62681 | 62681 | 62681 | 62681 | 62681 | raw_iso_pairwise | 62681 | 0 | none |
| Ab-Ag | fixed_ranking_iptm | iptm | medium | 62681 | 62681 | 62681 | 62681 | 62681 | three_method_common | 62681 | 0 | none |
| CASP16 | fixed_ranking_iptm | iptm | acceptable | 16199 | 16199 | 16199 | 16199 | 15323 | raw_iso_pairwise | 16199 | 0 | none |
| CASP16 | fixed_ranking_iptm | iptm | acceptable | 16199 | 16199 | 16199 | 16199 | 15323 | three_method_common | 15323 | 876 | mlp_missing |
| CASP16 | fixed_ranking_iptm | iptm | high | 16199 | 16199 | 16199 | 16199 | 15323 | raw_iso_pairwise | 16199 | 0 | none |
| CASP16 | fixed_ranking_iptm | iptm | high | 16199 | 16199 | 16199 | 16199 | 15323 | three_method_common | 15323 | 876 | mlp_missing |
| CASP16 | fixed_ranking_iptm | iptm | medium | 16199 | 16199 | 16199 | 16199 | 15323 | raw_iso_pairwise | 16199 | 0 | none |
| CASP16 | fixed_ranking_iptm | iptm | medium | 16199 | 16199 | 16199 | 16199 | 15323 | three_method_common | 15323 | 876 | mlp_missing |
| General | fixed_ranking_iptm | iptm | acceptable | 5496 | 5496 | 5496 | 5496 | 5496 | raw_iso_pairwise | 5496 | 0 | none |
| General | fixed_ranking_iptm | iptm | acceptable | 5496 | 5496 | 5496 | 5496 | 5496 | three_method_common | 5496 | 0 | none |
| General | fixed_ranking_iptm | iptm | high | 5496 | 5496 | 5496 | 5496 | 5496 | raw_iso_pairwise | 5496 | 0 | none |
| General | fixed_ranking_iptm | iptm | high | 5496 | 5496 | 5496 | 5496 | 5496 | three_method_common | 5496 | 0 | none |
| General | fixed_ranking_iptm | iptm | medium | 5496 | 5496 | 5496 | 5496 | 5496 | raw_iso_pairwise | 5496 | 0 | none |
| General | fixed_ranking_iptm | iptm | medium | 5496 | 5496 | 5496 | 5496 | 5496 | three_method_common | 5496 | 0 | none |

## iptm reliability at DockQ >= 0.23

### general

| method | mean_nominal_shortfall | max_nominal_shortfall | mean_coverage | coverage_at_q0.90 | mean_abs_calibration_gap |
| --- | --- | --- | --- | --- | --- |
| Isotonic ipTM | 0.0000 | 0.0000 | 0.4052 | 0.2420 | 0.0060 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.3981 | 0.2653 | 0.0070 |
| Raw ipTM | 0.0006 | 0.0026 | 0.6771 | 0.4461 |  |

### abag

| method | mean_nominal_shortfall | max_nominal_shortfall | mean_coverage | coverage_at_q0.90 | mean_abs_calibration_gap |
| --- | --- | --- | --- | --- | --- |
| Isotonic ipTM | 0.0015 | 0.0107 | 0.2526 | 0.1462 | 0.0143 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.2386 | 0.1831 | 0.0137 |
| Raw ipTM | 0.0742 | 0.2025 | 0.5243 | 0.2870 |  |

### casp16

| method | mean_nominal_shortfall | max_nominal_shortfall | mean_coverage | coverage_at_q0.90 | mean_abs_calibration_gap |
| --- | --- | --- | --- | --- | --- |
| Isotonic ipTM | 0.0000 | 0.0000 | 0.1716 | 0.0698 | 0.0251 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.1595 | 0.1162 | 0.0098 |
| Raw ipTM | 0.1604 | 0.3522 | 0.4591 | 0.2062 |  |

## ipae reliability at DockQ >= 0.23

### abag

| method | mean_nominal_shortfall | max_nominal_shortfall | mean_coverage | coverage_at_q0.90 | mean_abs_calibration_gap |
| --- | --- | --- | --- | --- | --- |
| Calibrated iPAE probability | 0.0000 | 0.0000 | 0.2311 | 0.1921 | 0.0162 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.2661 | 0.2288 | 0.0090 |
| Raw iPAE proxy | 0.0449 | 0.0909 | 0.4527 | 0.3070 |  |

### general

| method | mean_nominal_shortfall | max_nominal_shortfall | mean_coverage | coverage_at_q0.90 | mean_abs_calibration_gap |
| --- | --- | --- | --- | --- | --- |
| Calibrated iPAE probability | 0.0000 | 0.0000 | 0.2727 | 0.0000 | 0.0056 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.3981 | 0.2653 | 0.0070 |
| Raw iPAE proxy | 0.0002 | 0.0007 | 0.3955 | 0.0000 |  |

### casp16

| method | mean_nominal_shortfall | max_nominal_shortfall | mean_coverage | coverage_at_q0.90 | mean_abs_calibration_gap |
| --- | --- | --- | --- | --- | --- |
| Calibrated iPAE probability | 0.0000 | 0.0000 | 0.0654 | 0.0000 | 0.1701 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.1595 | 0.1162 | 0.0098 |
| Raw iPAE proxy | 0.2360 | 0.3350 | 0.3009 | 0.0000 |  |

