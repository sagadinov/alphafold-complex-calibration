# Table 2: General multimer main metrics

## DockQ >= 0.23 (n+=3,219, n-=2,277)

| Method | Brier | ECE | AUROC | MCC | PPV |
| --- | --- | --- | --- | --- | --- |
| Raw ipTM | 0.1379 | 0.0774 | 0.891 | 0.609 | 0.800 |
| Raw ranking confidence | 0.1423 | 0.0864 | 0.889 | 0.597 | 0.786 |
| Raw pDockQ2 (published) | 0.2148 | 0.1990 | 0.827 | 0.450 | 0.856 |
| Raw pDockQ2 (refit) | 0.2056 | 0.1914 | 0.826 | 0.442 | 0.856 |
| Isotonic ipTM | 0.1307 | 0.0195 | 0.884 | 0.618 | 0.841 |
| Isotonic iPAE | 0.1781 | 0.0082 | 0.764 | 0.473 | 0.725 |
| MLP 5-feat CE | 0.1258 | 0.0142 | 0.895 | 0.641 | 0.844 |

## DockQ >= 0.49 (n+=2,382, n-=3,114)

| Method | Brier | ECE | AUROC | MCC | PPV |
| --- | --- | --- | --- | --- | --- |
| Raw ipTM | 0.1728 | 0.1957 | 0.913 | 0.583 | 0.639 |
| Raw ranking confidence | 0.1806 | 0.2080 | 0.912 | 0.559 | 0.622 |
| Raw pDockQ2 (published) | 0.1645 | 0.0506 | 0.843 | 0.508 | 0.740 |
| Raw pDockQ2 (refit) | 0.1680 | 0.0639 | 0.842 | 0.507 | 0.745 |
| Isotonic ipTM | 0.1186 | 0.0086 | 0.907 | 0.667 | 0.771 |
| Isotonic iPAE | 0.1822 | 0.0120 | 0.774 | 0.446 | 0.643 |
| MLP 5-feat CE | 0.1161 | 0.0123 | 0.913 | 0.676 | 0.796 |

## DockQ >= 0.80 (n+=1,002, n-=4,494)

| Method | Brier | ECE | AUROC | MCC | PPV |
| --- | --- | --- | --- | --- | --- |
| Raw ipTM | 0.3224 | 0.4428 | 0.876 | 0.330 | 0.273 |
| Raw ranking confidence | 0.3313 | 0.4557 | 0.875 | 0.316 | 0.265 |
| Raw pDockQ2 (published) | 0.1781 | 0.2044 | 0.838 | 0.407 | 0.373 |
| Raw pDockQ2 (refit) | 0.1697 | 0.2191 | 0.837 | 0.412 | 0.380 |
| Isotonic ipTM | 0.1055 | 0.0118 | 0.869 | 0.437 | 0.600 |
| Isotonic iPAE | 0.1264 | 0.0181 | 0.780 | 0.000 | 0.000 |
| MLP 5-feat CE | 0.1046 | 0.0150 | 0.876 | 0.414 | 0.610 |
