# Decision-Use Experiments v2: Shareable Report

This file is a single self-contained summary of the corrected `decision_use_v2` analysis from the AF3 calibration paper workspace. It is intended to be pasted into ChatGPT or shared directly without requiring the recipient to inspect the repository first.

## Status

- Analysis status: complete
- Date: 2026-08-03
- Repository root:
  - `/proj/berzelius-2021-29/users/x_sasag/projects/AF3_Calibration`
- Output directory:
  - `af3_atlas/PAPER_REVISION/analysis/decision_use_v2/`
- Runtime:
  - full v2 compute finished in about `189s`

## Goal

The scientific question is:

> Do calibrated probabilities improve decisions that require probabilities, while either:
> 1. holding candidate ranking fixed, or
> 2. evaluating a predefined requested-reliability rule?

This v2 analysis was built to correct and extend the earlier decision-use experiments without changing the frozen paper pipeline.

## What Was Corrected or Added

1. Reliability-curve bootstrap was corrected.
2. Existing ipTM fixed-ranking yield experiment was preserved.
3. Ab-Ag iPAE fixed-ranking yield experiment was added.
4. Ab-Ag iPAE reliability operating-curve experiment was added.
5. Missingness and row-universe handling were made explicit.
6. Ranking invariance after isotonic calibration was audited explicitly.

## Frozen Experimental Setup

### Primary outcome

- `DockQ >= 0.23`

### Supplementary outcomes

- `DockQ >= 0.49`
- `DockQ >= 0.80`

### Fixed-ranking batch sizes

- `K = 5, 10, 20, 50`

For Ab-Ag iPAE-ranked fixed-ranking:

- `K = 5, 10, 20`

### Requested reliability levels

- `q = 0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95`

### Bootstrap

- `2000` target-level replicates
- seed `42`
- percentile `95%` confidence intervals

### No changes allowed in v2

The analysis did **not** introduce:

- new models
- new features
- new losses
- new datasets
- new quality definitions

## Methods Included

### ipTM family

- Raw ipTM
- Isotonic ipTM
- MLP 5-feat CE

### iPAE family

- Raw iPAE proxy
- Calibrated iPAE probability
- MLP 5-feat CE

Raw iPAE proxy is defined exactly as:

```text
1 / (1 + iPAE)
```

This is a score proxy, not a calibrated probability.

## Training / Evaluation Regimes

### Ab-Ag

- isotonic ipTM: Ab-Ag trained
- isotonic iPAE: Ab-Ag trained
- MLP: Ab-Ag trained
- evaluation: untouched Ab-Ag test set

### General

- grouped 5-fold OOF predictions
- fold-specific isotonic mappings
- fold-specific MLP predictions

### CASP16

- General-trained calibrators and General-trained MLP
- applied frozen
- no fitting on CASP16

## Source Files Used

- `af3_atlas/PAPER_REVISION/data/abag_predictions_v3.csv`
- `af3_atlas/PAPER_REVISION/data/general_predictions_v3.csv`
- `af3_atlas/PAPER_REVISION/data/casp16_predictions_v3.csv`
- `af3_atlas/PAPER_REVISION/data/abag_train_v2.csv`
- `af3_atlas/PAPER_REVISION/data/abag_test_v2.csv`
- `af3_atlas/PAPER_REVISION/data/general_v2.csv`
- `models/locked_ce_5feat_general.pt`
- `models/scaler_5feat_general.pkl`
- `models/locked_ce_5feat_abag.pt`
- `models/scaler_5feat_abag.pkl`

## Output Files Produced

### Main CSV outputs

- `fixed_ranking_yield_per_target_v2.csv`
- `fixed_ranking_yield_metrics_v2.csv`
- `fixed_ranking_yield_bootstrap_v2.csv`
- `reliability_operating_curve_v2.csv`
- `reliability_operating_curve_bootstrap_v2.csv`
- `missingness_audit_v2.csv`
- `row_universe_audit_v2.csv`
- `ranking_invariance_audit_v2.csv`

### Markdown / manifest outputs

- `fixed_ranking_yield_summary_v2.md`
- `reliability_operating_curve_summary_v2.md`
- `bootstrap_audit_v2.md`
- `decision_use_manifest_v2.yaml`
- `decision_use_validation_report_v2.md`

### Row counts

- `fixed_ranking_yield_per_target_v2.csv`: `161,298` rows
- `fixed_ranking_yield_metrics_v2.csv`: `180` rows
- `fixed_ranking_yield_bootstrap_v2.csv`: `864` rows
- `reliability_operating_curve_v2.csv`: `630` rows
- `reliability_operating_curve_bootstrap_v2.csv`: `4,158` rows
- `missingness_audit_v2.csv`: `24` rows
- `row_universe_audit_v2.csv`: `36` rows
- `ranking_invariance_audit_v2.csv`: `24` rows

## Row Universe and Missingness

### Ab-Ag

- input rows: `62,681`
- no rows dropped in fixed-ranking or reliability analyses

### General

- input rows: `5,496`
- no rows dropped

### CASP16

- input rows: `16,199`
- raw-vs-isotonic pairwise universe: `16,199`
- three-method common universe: `15,323`
- dropped from three-method common universe: `876`
- drop reason: `mlp_missing`

## Critical Audit Results

### Candidate identity preservation

For every fixed-ranking comparison, the selected candidate IDs were identical across probability estimators within the relevant comparison universe.

- `n_changed_selected_id_sets = 0` everywhere

This is important because it means the probability estimators are being compared on the **same candidate sets**, not on different ranked subsets.

### Ranking invariance after isotonic calibration

There were no strict ordering inversions in the isotonic ranking audit.

Examples:

- Ab-Ag ipAE acceptable:
  - Spearman `0.9977`
  - Kendall `0.9791`
  - strict ordering inversions `0`
- Ab-Ag ipTM acceptable:
  - Spearman `0.9962`
  - Kendall `0.9716`
  - strict ordering inversions `0`
- CASP16 ipTM acceptable:
  - Spearman `0.9929`
  - Kendall `0.9481`
  - strict ordering inversions `0`

Interpretation:

- isotonic calibration introduces many ties
- but it does not create strict order reversals

## Main Results

## 1. Fixed-Ranking Expected-Yield Estimation

Interpretation rule:

- candidate ranking is fixed by the raw score
- compared methods only differ in how they estimate expected successes among that same selected set

### 1A. ipTM-ranked candidate sets

#### Ab-Ag

Normalized MAE of predicted hit count:

| K | Raw ipTM | Isotonic ipTM | MLP 5-feat CE |
| --- | ---: | ---: | ---: |
| 5 | 0.2982 | 0.2224 | 0.1990 |
| 10 | 0.2846 | 0.2155 | 0.1904 |
| 20 | 0.2736 | 0.2067 | 0.1817 |
| 50 | 0.2542 | 0.1961 | 0.1676 |

Takeaway:

- On Ab-Ag, if ranking is fixed by raw ipTM, calibrated probabilities improve expected-yield estimation.
- MLP is best.
- Isotonic ipTM is clearly better than raw ipTM.

Bias pattern:

- Raw ipTM overestimates yield:
  - signed bias ranges from `+0.6852` to `+5.9905`
- Isotonic and MLP tend to underestimate modestly:
  - isotonic signed bias ranges from `-0.4097` to `-4.8041`
  - MLP signed bias ranges from `-0.3316` to `-4.7158`

#### General

Available summary row:

| K | Raw ipTM | Isotonic ipTM | MLP 5-feat CE |
| --- | ---: | ---: | ---: |
| 5 normalized MAE | 0.2524 | 0.2591 | 0.2650 |

Takeaway:

- On General OOF, the clear Ab-Ag yield-estimation advantage does not transfer.
- Raw ipTM is slightly best for this estimand in the available summary.

#### CASP16

Normalized MAE:

| K | Raw ipTM | Isotonic ipTM | MLP 5-feat CE |
| --- | ---: | ---: | ---: |
| 5 | 0.2848 | 0.3491 | 0.3930 |
| 10 | 0.2634 | 0.3251 | 0.3626 |
| 20 | 0.2842 | 0.3239 | 0.3480 |
| 50 | 0.2863 | 0.3330 | 0.3410 |

Takeaway:

- On CASP16, frozen General-trained probabilities do not improve expected-yield estimation over raw ipTM for ipTM-ranked candidate sets.

### 1B. iPAE-ranked candidate sets on Ab-Ag

Normalized MAE of predicted hit count:

| K | Raw iPAE proxy | Calibrated iPAE probability | MLP 5-feat CE |
| --- | ---: | ---: | ---: |
| 5 | 0.3360 | 0.2059 | 0.1960 |
| 10 | 0.3287 | 0.1981 | 0.1868 |
| 20 | 0.3186 | 0.1917 | 0.1794 |

Takeaway:

- On Ab-Ag, when ranking is fixed by iPAE, calibration substantially improves expected-yield estimation over the raw inverse-iPAE proxy.
- MLP is slightly better than calibrated iPAE.
- The main effect is removal of strong raw-proxy underestimation bias.

Bias pattern:

- Raw iPAE proxy strongly underestimates:
  - signed bias from `-1.3263` to `-5.2188`
- Calibrated iPAE is much closer:
  - signed bias from `-0.2176` to `-1.3568`
- MLP remains slightly better in normalized MAE:
  - signed bias from `-0.2934` to `-1.5351`

## 2. Reliability Operating Curves at DockQ >= 0.23

Interpretation rule:

- a method is asked to satisfy a requested success probability `q`
- we examine how often it actually meets that target and what coverage it retains

### 2A. ipTM family

#### General

| Method | Mean nominal shortfall | Max nominal shortfall | Mean coverage | Coverage at q=0.90 | Mean abs calibration gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw ipTM | 0.0006 | 0.0026 | 0.6771 | 0.4461 |  |
| Isotonic ipTM | 0.0000 | 0.0000 | 0.4052 | 0.2420 | 0.0060 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.3981 | 0.2653 | 0.0070 |

Takeaway:

- On General OOF, all methods are close to the requested reliability target.
- Calibrated methods are more conservative.
- MLP retains slightly more coverage than isotonic ipTM at `q=0.90`.

#### Ab-Ag

| Method | Mean nominal shortfall | Max nominal shortfall | Mean coverage | Coverage at q=0.90 | Mean abs calibration gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw ipTM | 0.0742 | 0.2025 | 0.5243 | 0.2870 |  |
| Isotonic ipTM | 0.0015 | 0.0107 | 0.2526 | 0.1462 | 0.0143 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.2386 | 0.1831 | 0.0137 |

Takeaway:

- On Ab-Ag, raw ipTM materially overstates requested reliability.
- Both calibrated ipTM and MLP largely satisfy the requested target.
- MLP retains more coverage than isotonic ipTM at `q=0.90`.

#### CASP16

| Method | Mean nominal shortfall | Max nominal shortfall | Mean coverage | Coverage at q=0.90 | Mean abs calibration gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw ipTM | 0.1604 | 0.3522 | 0.4591 | 0.2062 |  |
| Isotonic ipTM | 0.0000 | 0.0000 | 0.1716 | 0.0698 | 0.0251 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.1595 | 0.1162 | 0.0098 |

Takeaway:

- On CASP16, raw ipTM fails badly as a requested-reliability score.
- Frozen calibrated probabilities are much more conservative.
- MLP retains more usable coverage than isotonic ipTM at `q=0.90`.

### 2B. iPAE family

#### Ab-Ag

| Method | Mean nominal shortfall | Max nominal shortfall | Mean coverage | Coverage at q=0.90 | Mean abs calibration gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw iPAE proxy | 0.0449 | 0.0909 | 0.4527 | 0.3070 |  |
| Calibrated iPAE probability | 0.0000 | 0.0000 | 0.2311 | 0.1921 | 0.0162 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.2661 | 0.2288 | 0.0090 |

Takeaway:

- On Ab-Ag, raw inverse-iPAE is not trustworthy as a requested-reliability score.
- Calibrated iPAE and MLP satisfy requested reliability much better.
- MLP retains the most coverage at `q=0.90`.

#### General

| Method | Mean nominal shortfall | Max nominal shortfall | Mean coverage | Coverage at q=0.90 | Mean abs calibration gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw iPAE proxy | 0.0002 | 0.0007 | 0.3955 | 0.0000 |  |
| Calibrated iPAE probability | 0.0000 | 0.0000 | 0.2727 | 0.0000 | 0.0056 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.3981 | 0.2653 | 0.0070 |

Takeaway:

- On General, the raw iPAE proxy is less catastrophic than on CASP16, but it still is not a clean probability score.
- MLP remains the only method here with meaningful `q=0.90` coverage.

#### CASP16

| Method | Mean nominal shortfall | Max nominal shortfall | Mean coverage | Coverage at q=0.90 | Mean abs calibration gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw iPAE proxy | 0.2360 | 0.3350 | 0.3009 | 0.0000 |  |
| Calibrated iPAE probability | 0.0000 | 0.0000 | 0.0654 | 0.0000 | 0.1701 |
| MLP 5-feat CE | 0.0000 | 0.0000 | 0.1595 | 0.1162 | 0.0098 |

Takeaway:

- Raw iPAE proxy transfers poorly to CASP16 as a requested-reliability score.
- Calibrated iPAE is extremely conservative and retains almost no `q=0.90` coverage.
- MLP is the most usable of the three for high-confidence decisions under transfer.

## Bottom-Line Interpretation

The clean conclusion from v2 is:

1. **For fixed-ranking expected-yield estimation**, calibration helps clearly on Ab-Ag.
2. The strongest fixed-ranking result is the Ab-Ag iPAE-ranked experiment:
   - raw inverse-iPAE is a poor expected-yield estimator
   - calibrated iPAE and MLP are substantially better
3. **For requested-reliability decisions**, calibrated probabilities are the right tool:
   - raw ipTM and raw inverse-iPAE can rank well
   - but they do not behave like trustworthy requested-success probabilities, especially on CASP16
4. **The MLP is not universally superior on every estimand and every dataset.**
   - It is strongest on Ab-Ag.
   - On General and especially CASP16, the robust claim is about improved probability validity, not blanket metric dominance.

## Caveats

1. CASP16 has `876` rows without MLP probabilities, so three-method common-universe analyses there use `15,323` rows.
2. The validation report contains several bootstrap sign-mismatch warnings for pairwise delta summaries, especially in smaller-target or transfer settings.
3. These warnings do **not** invalidate the main point estimates or the generated CSVs, but they mean pairwise bootstrap-delta interpretations should be phrased cautiously.
4. The compute outputs are complete, but the v2 figure files have not yet been rendered from these outputs.

## Practical Summary in One Paragraph

If you hold ranking fixed and ask which probability estimator best predicts how many good models are inside the selected set, calibration helps clearly on Ab-Ag, especially for iPAE-ranked selections. If instead you ask for an operating rule like “give me only models with predicted success probability at least 0.90,” raw ranking scores are not enough: raw ipTM and raw inverse-iPAE do not transfer as trustworthy probabilities, particularly on CASP16. Frozen calibrated probabilities, especially the MLP, are much better suited for that decision-use setting, even when they are more conservative.

## Main Files to Inspect

- `af3_atlas/PAPER_REVISION/analysis/decision_use_v2/fixed_ranking_yield_metrics_v2.csv`
- `af3_atlas/PAPER_REVISION/analysis/decision_use_v2/fixed_ranking_yield_bootstrap_v2.csv`
- `af3_atlas/PAPER_REVISION/analysis/decision_use_v2/reliability_operating_curve_v2.csv`
- `af3_atlas/PAPER_REVISION/analysis/decision_use_v2/reliability_operating_curve_bootstrap_v2.csv`
- `af3_atlas/PAPER_REVISION/analysis/decision_use_v2/fixed_ranking_yield_summary_v2.md`
- `af3_atlas/PAPER_REVISION/analysis/decision_use_v2/reliability_operating_curve_summary_v2.md`
- `af3_atlas/PAPER_REVISION/analysis/decision_use_v2/decision_use_validation_report_v2.md`
- `af3_atlas/PAPER_REVISION/analysis/decision_use_v2/decision_use_manifest_v2.yaml`

