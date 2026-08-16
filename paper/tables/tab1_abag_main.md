# Table 1: Ab-Ag main metrics

## DockQ >= 0.23 (n+=22,231, n-=40,450)

| Method | Brier | ECE | AUROC | MCC | PPV |
| --- | --- | --- | --- | --- | --- |
| Raw ipTM | 0.1213 | 0.1462 | 0.927 | 0.722 | 0.778 |
| Raw ranking confidence | 0.1478 | 0.1944 | 0.926 | 0.682 | 0.712 |
| Raw pDockQ2 (published) | 0.1583 | 0.1929 | 0.943 | 0.558 | 0.951 |
| Raw pDockQ2 (refit) | 0.1006 | 0.0969 | 0.943 | 0.736 | 0.924 |
| ABAG-Rank | --- | --- | 0.895 | 0.686 | 0.867 |
| Isotonic ipTM | 0.0929 | 0.0282 | 0.926 | 0.742 | 0.855 |
| Isotonic iPAE | 0.0826 | 0.0255 | 0.944 | 0.764 | 0.862 |
| MLP 5-feat CE | 0.0783 | 0.0150 | 0.946 | 0.773 | 0.867 |

## DockQ >= 0.49 (n+=18,029, n-=44,652)

| Method | Brier | ECE | AUROC | MCC | PPV |
| --- | --- | --- | --- | --- | --- |
| Raw ipTM | 0.1327 | 0.1907 | 0.938 | 0.696 | 0.674 |
| Raw ranking confidence | 0.1661 | 0.2563 | 0.936 | 0.643 | 0.606 |
| Raw pDockQ2 (published) | 0.1147 | 0.1260 | 0.949 | 0.594 | 0.888 |
| Raw pDockQ2 (refit) | 0.0814 | 0.0725 | 0.949 | 0.766 | 0.848 |
| ABAG-Rank | --- | --- | 0.912 | 0.685 | 0.848 |
| Isotonic ipTM | 0.0821 | 0.0143 | 0.938 | 0.739 | 0.790 |
| Isotonic iPAE | 0.0726 | 0.0155 | 0.950 | 0.771 | 0.846 |
| MLP 5-feat CE | 0.0639 | 0.0110 | 0.960 | 0.797 | 0.866 |

## DockQ >= 0.80 (n+=9,070, n-=53,611)

| Method | Brier | ECE | AUROC | MCC | PPV |
| --- | --- | --- | --- | --- | --- |
| Raw ipTM | 0.2032 | 0.3336 | 0.932 | 0.497 | 0.359 |
| Raw ranking confidence | 0.2461 | 0.3992 | 0.928 | 0.446 | 0.316 |
| Raw pDockQ2 (published) | 0.0730 | 0.0284 | 0.933 | 0.579 | 0.600 |
| Raw pDockQ2 (refit) | 0.0971 | 0.1306 | 0.933 | 0.598 | 0.485 |
| ABAG-Rank | --- | --- | 0.879 | 0.092 | 0.523 |
| Isotonic ipTM | 0.0716 | 0.0133 | 0.933 | 0.599 | 0.610 |
| Isotonic iPAE | 0.0700 | 0.0092 | 0.937 | 0.572 | 0.610 |
| MLP 5-feat CE | 0.0629 | 0.0154 | 0.949 | 0.641 | 0.653 |

{\footnotesize $^\dagger$ABAG-Rank is evaluated on the ABAG-Rank test split (25{,}440 models, 1{,}091 targets), which overlaps our test split by 983 targets. Brier and ECE are not reported because its output is continuous DockQ rather than calibrated probability.}
