# Decision-Use Figure Captions

## F2_fixed_ranking_yield

Fixed-ranking expected-yield estimation at DockQ >= 0.23. Candidate identities were fixed by the indicated raw confidence score and were identical across probability estimators; only the predicted expected yield differed. Panels show Ab-Ag ipTM-ranked, Ab-Ag iPAE-ranked, General ipTM-ranked, and CASP16 ipTM-ranked. The y-axis is MAE in predicted success fraction, defined as the mean absolute difference between predicted and observed success fractions across targets. Only K=5 is shown because no General target contained at least ten eligible models in the locked dataset.

## F3_reliability_transfer

Transfer of minimum-reliability decision rules at DockQ >= 0.23. Top row: observed precision. Bottom row: coverage. On General, raw ipTM thresholds were evaluated using target-grouped cross-fitting. For external transfer, one threshold per requested reliability level was fitted using all General OOF predictions and applied unchanged to Ab-Ag and CASP16. General-trained calibrated probabilities were likewise applied frozen to both external benchmarks.

## S2_abag_ipae_reliability

Within-domain Ab-Ag reliability and coverage of iPAE-based decision rules at DockQ >= 0.23. Raw inverse-iPAE proxy, calibrated iPAE probability, and the five-feature MLP are compared. Precision is omitted at q values where no predictions are selected.

