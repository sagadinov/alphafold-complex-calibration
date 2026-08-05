# Decision-Use v2 Validation Report

- canonical_repository_verified: `True`
- project_root: `/proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration`
- n_bootstrap: `2000`
- seed: `42`

## Source files

| label | path |
| --- | --- |
| abag_predictions_v3 | /proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/af3_atlas/PAPER_REVISION/data/abag_predictions_v3.csv |
| general_predictions_v3 | /proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/af3_atlas/PAPER_REVISION/data/general_predictions_v3.csv |
| casp16_predictions_v3 | /proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/af3_atlas/PAPER_REVISION/data/casp16_predictions_v3.csv |
| abag_train_v2 | /proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/af3_atlas/PAPER_REVISION/data/abag_train_v2.csv |
| abag_test_v2 | /proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/af3_atlas/PAPER_REVISION/data/abag_test_v2.csv |
| general_v2 | /proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/af3_atlas/PAPER_REVISION/data/general_v2.csv |
| locked_ce_5feat_general | /proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/models/locked_ce_5feat_general.pt |
| scaler_5feat_general | /proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/models/scaler_5feat_general.pkl |
| locked_ce_5feat_abag | /proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/models/locked_ce_5feat_abag.pt |
| scaler_5feat_abag | /proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration/models/scaler_5feat_abag.pkl |

## Missingness audit

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

## Row universe audit

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

## Bootstrap validity summary

- fixed_boot_rows: `936`
- reliability_boot_rows: `4158`

## Fixed-ranking bootstrap delta audit

- audit_rows: `156`
- max_identity_abs_error: `4.441e-15`
- max_bootstrap_mean_minus_point_abs: `0.047043`

## Warnings

- none

