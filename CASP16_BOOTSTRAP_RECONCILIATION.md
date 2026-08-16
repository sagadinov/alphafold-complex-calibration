# CASP16 Bootstrap Reconciliation

## Executive answer
1. The clean-release CASP16 table comes from a committed target-balanced bootstrap producer and is reproducible from frozen inputs.
2. The conflicting locked-manuscript CASP16 values are not present in any committed table, JSON, or bootstrap CSV in this workspace.
3. The only two committed CASP16 result pipelines on disk are:
   - a pre-bootstrap pooled evaluation pipeline;
   - the final target-balanced bootstrap pipeline.
4. The manuscript-only values match neither committed pipeline exactly and show a hybrid pattern across metrics, consistent with draft-table synchronization drift rather than a third committed producer.

## Files and artifact families located

### Protocol A: final target-balanced bootstrap
- Producer script: `af3_atlas/PAPER_REVISION/casp16/build_casp16_v2_pipeline.py`
- Frozen inputs used by the clean release:
  - `data/casp16_v2.csv`
  - `data/general_v2.csv`
  - `models/locked_ce_5feat_general.pt`
- Frozen outputs:
  - `data/casp16_bootstrap_summary.csv`
  - `paper/tables/tab4_casp16_bootstrap.tex`
  - `data/report_data_v3.json`
- Private frozen source files copied into the release:
  - `af3_atlas/PAPER_REVISION/casp16/casp16_bootstrap_summary.csv`
  - `af3_atlas/PAPER_REVISION/tables/report_data_v3.json`
- Exporter that copies these into the clean repo:
  - `af3_atlas/PAPER_REVISION/build_final_v2_release.py`
- Introduction commits:
  - `0149de5231f289a75afdf04f65dfb0f0c163c856` on `2026-06-30 21:53:31 +0200`
  - `0d337b0a1120ce7165cf15968c328d18e00449f7` on `2026-07-02 09:54:12 +0200`

### Protocol B: old pooled CASP16 evaluation
- Producer script: `PAPER_FIGURES/build_paper_deliverables.py`
- Frozen outputs:
  - `PAPER_FIGURES/tables/T2_casp16_main.tex`
  - `PAPER_FIGURES/tables/report_data.json`
- Introduction commit:
  - `ce5f8c53e2d786147aadc30e3c501de22fd4fadc` on `2026-05-15 07:58:54 +0200`
- This is not bootstrapped. It is the old pooled all-row CASP16 table.

## What each protocol actually does

### Protocol A: final target-balanced bootstrap
Implementation source: `af3_atlas/PAPER_REVISION/casp16/build_casp16_v2_pipeline.py`

Exact behavior:
- Input table: `casp16_v2.csv`
- Raw input size: `16,199` rows, `25` targets
- Upstream target scope:
  - `H1265` is already absent from `data/casp16_v2.csv`
  - so the release dataset is already a post-H1265 CASP16 set of `25` targets
- Common-valid filtering before any method evaluation:
  - rows must have finite values for all of:
    - `dockq_v2`
    - `iptm`
    - `ptm`
    - `ranking_score`
    - `mean_plddt`
    - `iface_pae_mean`
    - `interchain_block_mean`
- Common-valid universe size after filtering:
  - `15,323` rows
- Target count after common-valid filtering:
  - `25`
- Minimum-model eligibility filter:
  - `min_models = 100`
- Targets excluded by `min_models`:
  - `H1217` (`12` rows)
  - `H1258` (`70` rows)
- Eligible bootstrap targets actually used:
  - `23`
- Sampling procedure:
  - `100` bootstrap iterations
  - sample targets with replacement
  - number of sampled targets per iteration = number of eligible targets = `23`
  - within each sampled target, sample `100` model rows
  - row sampling is without replacement for all current eligible targets, because each eligible target has at least `100` rows
  - pooled sampled size per iteration = `2,300` rows
- Metric aggregation:
  - metrics are computed on one pooled target-balanced bootstrap sample per iteration
  - summary mean/std are taken across the `100` iteration-level pooled metrics
- ECE implementation:
  - 10 equal-width bins on `[0,1]`
  - clipped probabilities
  - weighted absolute calibration gap
- Raw-score treatment for Brier/ECE:
  - raw score methods are used directly as probabilities after clipping to `[0,1]`
- pDockQ2 columns/parameters:
  - published: logistic with original Zhu et al. parameters applied to `iface_pae_mean` and `mean_plddt`
  - refit: parameters refit on full General training data inside `fit_pdockq2_refit_params(train_df)`
- Isotonic columns:
  - `ipTM` and `iPAE = 1 / (1 + iface_pae_mean)`
  - fit on full General training data per threshold
- MLP columns:
  - General-trained locked CE model
  - features: `iface_pae_mean`, `interchain_block_mean`, `iptm`, `ranking_score`, `ptm`

## Verification replay of Protocol A
I reran the frozen Protocol A bootstrap from the original producer code using the preserved clean-release inputs because the original private hardcoded paths for the General training CSV and CE bundle are no longer live.

Replay inputs used:
- `data/casp16_v2.csv`
- `data/general_v2.csv`
- `models/locked_ce_5feat_general.pt`

Replay result:
- The regenerated summary matches `data/casp16_bootstrap_summary.csv` exactly to the displayed precision across all methods and thresholds.
- Therefore the clean-release `data/casp16_bootstrap_summary.csv` is a verified frozen output of Protocol A.

## Protocol B: old pooled evaluation
Implementation source: `PAPER_FIGURES/build_paper_deliverables.py`

Exact behavior:
- No target-balanced bootstrap
- No iteration-level target resampling
- Metrics computed directly on the pooled CASP16 evaluation table
- Old table example:
  - `PAPER_FIGURES/tables/T2_casp16_main.tex`
  - acceptable Raw ipTM = `0.1025 / 0.2072 / 0.9675 / 0.7471 / 0.6928`

This does not match the final manuscript Methods definition for Table 4.

## Comparison against the final manuscript Methods definition

### Final manuscript Methods definition (as frozen in the clean repo artifacts)
- target-balanced bootstrap
- `100` iterations
- `100` models per target
- minimum `100` models per target
- General-trained frozen methods applied to CASP16

### Match assessment
- Protocol A matches the manuscript Methods structure.
- Protocol B does not match because it is not bootstrapped and not target-balanced.

### Important ambiguity / mismatch in documentation
The release metadata currently says:
- `n_targets_used = 22`
- `876 models ... were excluded from iPAE-based evaluations`

The code proves instead:
- `n_targets_used = 23`
- the `876` rows are excluded from the common bootstrap evaluation universe before any method is evaluated, not only from iPAE-based methods.

Therefore:
- the Protocol A numbers are authoritative;
- some descriptive metadata in `data/report_data_v3.json` is stale or misleading.

## Where the conflicting locked-manuscript values stand
The conflicting manuscript values supplied for audit were compared against both committed artifact families.

For `Raw ipTM`, the manuscript row is hybrid by metric:
- acceptable:
  - Brier closer to Protocol A
  - ECE closer to Protocol B
  - AUROC closer to Protocol A
  - MCC closer to Protocol A
  - PPV closer to Protocol B
- medium:
  - Brier/ECE closer to Protocol B
  - AUROC/MCC closer to Protocol A
  - PPV closer to Protocol B
- high:
  - Brier/ECE closer to Protocol B
  - AUROC/MCC closer to Protocol A
  - PPV closer to Protocol B

That pattern is not consistent with a single committed computation pipeline.

Search result:
- No committed `csv/json/tex/md` artifact in this workspace contains the locked-manuscript CASP16 table values as a generated table.
- The manuscript-only values therefore do not come from either committed Protocol A or committed Protocol B.

## Root cause of the CASP16 discrepancy
The discrepancy is not between two equally valid frozen bootstrap summaries.

It is between:
1. the committed, reproducible target-balanced bootstrap summary (Protocol A), and
2. a manuscript-side draft table that does not correspond to any committed generated artifact in this workspace and appears to mix metrics from different artifact families.

## Authoritative source of truth
The authoritative CASP16 Table 4 source is Protocol A:
- `data/casp16_bootstrap_summary.csv`
- rendered by `scripts/reproduce_table4_casp16.py`
- exported into `data/report_data_v3.json`
- reproduced successfully from the frozen producer code and frozen release inputs

## What should change
- Manuscript:
  - Table 4 should be synchronized to the clean-release Protocol A numbers.
- Repository:
  - numeric CASP16 table values do not need correction
  - metadata/documentation should be corrected:
    - `n_targets_used` should be `23`, not `22`
    - the `876`-row note should describe exclusion from the common bootstrap-valid universe, not only iPAE-based evaluations

## Scientific impact
No scientific conclusion changes.

What changes is provenance clarity:
- the final CASP16 table should be understood as a target-balanced bootstrap over the common-valid 15,323-row CASP16 universe, using 23 eligible targets and 2,300 sampled rows per bootstrap iteration.
