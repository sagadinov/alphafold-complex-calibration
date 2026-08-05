# Decision-Use v2 Figure Captions

## fixed_ranking_yield_figure_v2

Fixed-ranking expected-yield estimation at DockQ ≥0.23. Top-left: Ab-Ag, candidates ranked by raw ipTM. Top-right: Ab-Ag, candidates ranked by iPAE. Bottom-left: General, candidates ranked by raw ipTM. Bottom-right: CASP16, candidates ranked by raw ipTM. Within each panel, candidate identities were identical for the compared estimators; only the estimated probability of structural success differed. The y-axis reports MAE in predicted success fraction, defined as the target-level mean of |Ĥ_t/K - H_t/K|. Points show target-level MAE in predicted success fraction and error bars show 95% target-bootstrap confidence intervals. General is shown only at K=5, because no General target contained at least ten eligible predictions in the locked dataset.

## reliability_transfer_figure_v2

Transfer of minimum-reliability decision rules at DockQ ≥0.23. Top row: observed precision. Bottom row: coverage. For calibrated methods, predictions were selected using p-hat ≥ q. On General, raw ipTM thresholds were evaluated using target-grouped cross-fitting. For external transfer, one threshold per requested reliability level was fitted using all General OOF predictions and applied unchanged to Ab-Ag and CASP16. General-trained calibrated probabilities were likewise applied frozen to both external benchmarks. Points show observed precision and coverage; error bars show 95% target-bootstrap confidence intervals. The dashed line in the precision panels represents the requested minimum reliability; values above it indicate conservative selection rather than perfect calibration.

## reliability_precision_figure_v2

Observed precision under minimum-reliability decision rules at DockQ ≥0.23. The dashed line represents the requested minimum reliability, not an ideal calibration line. Values above the line indicate that the rule satisfies or exceeds the requested minimum reliability.

## reliability_coverage_figure_v2

Coverage of minimum-reliability decision rules at DockQ ≥0.23. Coverage is the fraction of eligible predictions retained by the rules evaluated in the accompanying precision figure. Precision and coverage should therefore be interpreted jointly.

## abag_ipae_reliability_figure_v2

Within-domain reliability and coverage of iPAE-based decision rules on the held-out Ab-Ag test set at DockQ ≥0.23. Raw inverse-iPAE thresholds were selected using the Ab-Ag training/calibration data and applied frozen to the test set. Calibrated iPAE and the five-feature MLP selected predictions with p-hat ≥ q. Left: observed precision relative to the requested minimum reliability. Right: corresponding coverage. High-q operating points with very small selected sets are marked explicitly by selected-count annotations on the coverage panel.

