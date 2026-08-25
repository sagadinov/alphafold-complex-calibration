# pDockQ2 Refit Verification

## Frozen Procedure

- Training data: the five released `data/abag_train_v2_parts/` shards only.
- Training rows: 269,105 across 7,045 targets; valid continuous-DockQ fit rows: 248,670.
- Target: continuous `dockq`, not a thresholded binary label.
- Input: `mean_plddt / (1 + (iface_pae_mean / 10)^2)` with `d0 = 10` fixed.
- Optimizer: `scipy.optimize.curve_fit`, initial `[L, x0, k, b] = [1.31, 84.733, 0.075, 0.005]`,
  `maxfev=10000`, bounds `L:[0,2]`, `x0:[0,200]`, `k:[0,1]`, `b:[-1,1]`.
- Optimized parameters: `L`, `x0`, `k`, `b`; output clipped to `[0,1]` only after fitting.

## Parameters

- `L = 2.00000000`
- `x0 = 40.21941805`
- `k = 0.01947584`
- `b = -0.65947117`
- `d0 = 10.0 (fixed)`

## Ab-Ag Test Check

- Evaluation rows: 62,681.
- DockQ >= 0.23: Brier `0.100590`, MCC `0.736144`, AUROC `0.943322`.

The implementation matches `af3_atlas/PAPER_REVISION/build_results_revision.py` and its successor
`build_final_v2_release.py`. Those scripts use the parameter order `(L, x0, k, b)`; the alternate
order in an informal example must not be used with their published initial vector.

## Legacy-value Note

The released final-v2 machine-readable source (`data/report_data_v3.json`) records the same
acceptable-event Brier value, `0.100590`. The approximate `0.096` value cited in an earlier
instruction is not produced by this final-v2 data/protocol and must not be used to validate it.
