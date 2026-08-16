# Table 1 Reconciliation

## Scope
This note reconciles the Ab-Ag `DockQ >= 0.23` `Isotonic ipTM` row discrepancy between the current clean-release repository and the locked manuscript draft.

## Version A: current clean-release repository
- Render source: `data/report_data_v3.json`
- Render script: `scripts/reproduce_table1_abag.py`
- Rendered table: `paper/tables/tab1_abag_main.tex`
- Current row:
  - Brier `0.0929051264807380`
  - ECE `0.0281710528865097`
  - AUROC `0.9262668956516192`
  - MCC `0.7420704328071938`
  - PPV `0.8553648068669528`
- Rounded manuscript-form row in repo:
  - `.0929 / .0282 / .926 / .742 / .855`
- Private number-producing source:
  - `af3_atlas/PAPER_REVISION/tables/report_data_v3.json`
- Private producer script:
  - `af3_atlas/PAPER_REVISION/build_results_revision.py`
- Commit introducing the corrected Ab-Ag v2 row:
  - `0d337b0a1120ce7165cf15968c328d18e00449f7`
  - Date: `2026-07-02 09:54:12 +0200`
  - Message: `Close paper lock issues: bootstrap CASP16 and refresh Ab-Ag counts`
- Training/evaluation split:
  - Train: `abag_train_v2.csv`
  - Test: `abag_test_v2.csv`
  - Audited raw universe: `65,650` rows total
  - Evaluated universe: `62,681` rows
  - Excluded rows: `2,969`
  - Threshold counts at `DockQ >= 0.23`: `n_pos=22,231`, `n_neg=40,450`
- Isotonic fitting protocol:
  - Per-threshold binary labels on Ab-Ag train
  - `IsotonicRegression(out_of_bounds='clip')`
  - Fit on train `ipTM`, applied to test `ipTM`
- ECE implementation:
  - `af3_atlas/calibration_analysis/run_calibration_analysis.py:341`
  - 10 equal-width bins on `[0,1]`
  - probabilities clipped to `[0,1]`
  - weighted absolute gap `|mean_pred - mean_obs|`
  - last bin inclusive on the upper edge

## Version B: locked manuscript row supplied for audit
- Supplied row:
  - `.0929 / .0306 / .930 / .740 / .854`
- Expected source file:
  - Not found in this workspace.
- Search result:
  - No committed file in either the clean release repo or the private research repo contains this exact metric combination.
- Exact-source status:
  - No machine-generated source file on disk.
  - Therefore the exact manuscript row cannot be traced to a committed generator output.

## Nearest committed predecessor
The nearest committed predecessor with the older Ab-Ag artifact family is:
- Source file: `af3_atlas/PAPER_REVISION/tables/report_data_v2.json`
- Rendered table in the private repo history: `af3_atlas/PAPER_REVISION/tables/tab_abag_main.tex` at commit `d3490ec29d1786a11003c34be98dde10da914a67`
- Commit date: `2026-05-28 12:21:49 +0200`
- Pre-v2 row:
  - Brier `0.0897288333871516`
  - ECE `0.0291659114373525`
  - AUROC `0.9300186731486048`
  - MCC `0.7504231319854668`
  - PPV `0.8656370656370657`
- Rounded row:
  - `.0897 / .0292 / .930 / .750 / .866`
- Pre-v2 universe:
  - Evaluated rows: `62,424`
  - Threshold counts at `DockQ >= 0.23`: `n_pos=22,217`, `n_neg=40,207`
- Producer family:
  - same private `build_results_revision.py` lineage before the Ab-Ag v2 correction
  - older `PAPER_FIGURES/build_paper_deliverables.py` also renders the old-family numbers, not the mixed manuscript row

## Why the two visible versions differ
There are two distinct machine-generated Ab-Ag artifact families on disk:
1. Pre-v2 Ab-Ag results on the older `62,424`-row test universe.
2. Post-v2 Ab-Ag results on the audited `62,681`-row evaluated universe.

The locked manuscript row mixes characteristics of both families:
- Brier matches the post-v2 row.
- AUROC matches the pre-v2 row after rounding.
- ECE, MCC, and PPV do not match any committed row exactly.

That pattern is not produced by any committed generator output I found. The most defensible explanation is a draft-table synchronization error during the Ab-Ag v2 transition, not a third committed computation protocol.

## Authoritative source
The authoritative machine-readable source is Version A:
- `data/report_data_v3.json` in the clean release repo
- provenance chain:
  - private number producer: `af3_atlas/PAPER_REVISION/build_results_revision.py`
  - private frozen export: `af3_atlas/PAPER_REVISION/tables/report_data_v3.json`
  - public frozen copy: `data/report_data_v3.json`
  - public renderer: `scripts/reproduce_table1_abag.py`
  - public table: `paper/tables/tab1_abag_main.tex`

## Correct row to use in manuscript and repository
Use:
- Brier `.0929`
- ECE `.0282`
- AUROC `.926`
- MCC `.742`
- PPV `.855`

## Decision
- Repository: already correct numerically for this row.
- Manuscript: the mixed row should be replaced with the Version A row above.
- Scientific impact: none. This is a paper-vs-artifact synchronization issue, not a change in the underlying Ab-Ag evaluation protocol.
