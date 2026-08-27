#!/usr/bin/env python3
"""Compute AFDB workshop recalibration curves from frozen 304-complex features."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss
from sklearn.model_selection import StratifiedShuffleSplit

from common import ANALYSIS, DATA, THRESHOLDS, write_text

AFDB_INPUT = ANALYSIS / "afdb" / "afdb_positive_dockq_features.csv"
GENERAL_INPUT = DATA / "general_v2.csv"
OUTPUT = ANALYSIS / "workshop" / "workshop_afdb_recalibration_source.csv"
REPEAT_OUTPUT = ANALYSIS / "workshop" / "workshop_afdb_recalibration_repeats.csv"
SUMMARY = ANALYSIS / "workshop" / "workshop_afdb_recalibration_summary.md"
# All requested local calibration-set sizes, retaining the paired split setup.
TRAIN_SIZES = list(range(5, 101, 5))
N_REPEATS = 100
SEED = 42


def compute_ece(y_true: np.ndarray, probability: np.ndarray, n_bins: int = 10) -> float:
    probability = np.clip(np.asarray(probability, dtype=float), 0.0, 1.0)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for index in range(n_bins):
        if index < n_bins - 1:
            mask = (probability >= edges[index]) & (probability < edges[index + 1])
        else:
            mask = (probability >= edges[index]) & (probability <= edges[index + 1])
        if mask.any():
            ece += mask.mean() * abs(float(probability[mask].mean()) - float(y_true[mask].mean()))
    return float(ece)


def summarise(values: list[float]) -> tuple[float, float]:
    arr = np.asarray(values, dtype=float)
    if len(arr) == 0:
        return float("nan"), float("nan")
    if len(arr) == 1:
        return float(arr[0]), 0.0
    return float(arr.mean()), float(arr.std(ddof=1))


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    afdb = pd.read_csv(AFDB_INPUT, low_memory=False)
    afdb["dockq_native"] = pd.to_numeric(afdb["dockq_native"], errors="coerce")
    afdb = afdb.loc[np.isfinite(afdb["dockq_native"])].copy()
    if len(afdb) != 304:
        raise RuntimeError(f"Expected 304 finite-DockQ AFDB entries, found {len(afdb)}")
    for column in ["iptm", "ipsae_max"]:
        afdb[column] = pd.to_numeric(afdb[column], errors="coerce")
        if not np.isfinite(afdb[column]).all():
            raise RuntimeError(f"AFDB column {column} contains non-finite values on the 304-row universe")

    general = pd.read_csv(GENERAL_INPUT, low_memory=False)
    general["dockq"] = pd.to_numeric(general["dockq"], errors="coerce")
    general["iptm"] = pd.to_numeric(general["iptm"], errors="coerce")
    general = general.loc[np.isfinite(general["dockq"]) & np.isfinite(general["iptm"])].copy()
    if len(general) != 5496:
        raise RuntimeError(f"Expected 5,496 finite General rows, found {len(general)}")
    return afdb, general


def compute_source_data() -> pd.DataFrame:
    afdb, general = load_inputs()
    rows: list[dict[str, object]] = []
    repeat_rows: list[dict[str, object]] = []

    for threshold_index, (threshold_name, threshold_value) in enumerate(THRESHOLDS):
        y_afdb = (afdb["dockq_native"].to_numpy(dtype=float) >= threshold_value).astype(int)
        y_general = (general["dockq"].to_numpy(dtype=float) >= threshold_value).astype(int)
        general_iso = IsotonicRegression(out_of_bounds="clip")
        general_iso.fit(general["iptm"].to_numpy(dtype=float), y_general)
        iptm = afdb["iptm"].to_numpy(dtype=float)
        ipsae = afdb["ipsae_max"].to_numpy(dtype=float)

        # Fixed methods are evaluated exactly once on the complete 304-complex
        # AFDB universe. They are intentionally not re-evaluated on local
        # calibration holdouts, because they do not depend on local labels.
        fixed_predictions = {
            "Raw ipTM": np.clip(iptm, 0.0, 1.0),
            "Raw ipSAEmax": np.clip(ipsae, 0.0, 1.0),
            "Isotonic ipTM (General frozen)": general_iso.predict(iptm),
        }
        for method, probability in fixed_predictions.items():
            for metric, value in [
                ("brier", float(brier_score_loss(y_afdb, np.clip(probability, 0.0, 1.0)))),
                ("ece", compute_ece(y_afdb, probability)),
            ]:
                for train_size in TRAIN_SIZES:
                    rows.append(
                        {
                            "threshold": threshold_name,
                            "threshold_val": threshold_value,
                            "train_size": train_size,
                            "n_repeats": 1,
                            "method": method,
                            "metric": metric,
                            "mean": value,
                            "std": 0.0,
                            "available": True,
                            "reason": "fixed baseline evaluated once on full 304-complex AFDB universe",
                            "n_total": len(afdb),
                            "n_pos_total": int(y_afdb.sum()),
                            "n_neg_total": int((1 - y_afdb).sum()),
                            "holdout_size": len(afdb),
                            "train_pos_mean": np.nan,
                            "train_pos_min": np.nan,
                            "train_pos_max": np.nan,
                            "source_file": str(AFDB_INPUT.relative_to(AFDB_INPUT.parents[2])),
                            "split_protocol": "fixed full-AFDB evaluation; no local calibration split",
                            "seed": np.nan,
                        }
                    )

        for train_size in TRAIN_SIZES:
            splitter = StratifiedShuffleSplit(
                n_splits=N_REPEATS,
                train_size=train_size,
                random_state=SEED + 1000 * threshold_index + train_size,
            )

            metric_store: dict[str, dict[str, list[float]]] = {
                "Isotonic ipTM (local AFDB)": {"brier": [], "ece": []},
                "Isotonic ipSAEmax (local AFDB)": {"brier": [], "ece": []},
            }
            train_pos_counts: list[int] = []
            holdout_sizes: list[int] = []

            for repeat_index, (train_idx, holdout_idx) in enumerate(splitter.split(iptm, y_afdb)):
                overlap = np.intersect1d(train_idx, holdout_idx)
                if overlap.size:
                    raise RuntimeError("Calibration and evaluation splits overlap")
                holdout_sizes.append(int(len(holdout_idx)))
                train_pos_counts.append(int(y_afdb[train_idx].sum()))

                y_holdout = y_afdb[holdout_idx]
                iptm_holdout = iptm[holdout_idx]
                ipsae_holdout = ipsae[holdout_idx]

                local_iptm = IsotonicRegression(out_of_bounds="clip")
                local_iptm.fit(iptm[train_idx], y_afdb[train_idx])
                local_ipsae = IsotonicRegression(out_of_bounds="clip")
                local_ipsae.fit(ipsae[train_idx], y_afdb[train_idx])

                predictions = {
                    "Isotonic ipTM (local AFDB)": local_iptm.predict(iptm_holdout),
                    "Isotonic ipSAEmax (local AFDB)": local_ipsae.predict(ipsae_holdout),
                }
                for method, probability in predictions.items():
                    values = {
                        "brier": float(brier_score_loss(y_holdout, np.clip(probability, 0.0, 1.0))),
                        "ece": compute_ece(y_holdout, probability),
                    }
                    for metric, value in values.items():
                        metric_store[method][metric].append(value)
                        repeat_rows.append(
                            {
                                "threshold": threshold_name,
                                "threshold_val": threshold_value,
                                "train_size": train_size,
                                "train_percent": 100.0 * train_size / len(afdb),
                                "repeat_index": repeat_index,
                                "method": method,
                                "metric": metric,
                                "value": value,
                                "n_total": len(afdb),
                                "holdout_size": len(holdout_idx),
                                "train_pos": int(y_afdb[train_idx].sum()),
                                "holdout_pos": int(y_holdout.sum()),
                                "seed": SEED + 1000 * threshold_index + train_size,
                                "split_protocol": "paired StratifiedShuffleSplit across ipTM and ipSAEmax",
                            }
                        )

            if len(set(holdout_sizes)) != 1:
                raise RuntimeError(f"Holdout sizes differ for train_size={train_size}: {sorted(set(holdout_sizes))}")

            for method, metric_map in metric_store.items():
                for metric, values in metric_map.items():
                    mean, std = summarise(values)
                    rows.append(
                        {
                            "threshold": threshold_name,
                            "threshold_val": threshold_value,
                            "train_size": train_size,
                            "n_repeats": N_REPEATS,
                            "method": method,
                            "metric": metric,
                            "mean": mean,
                            "std": std,
                            "available": True,
                            "reason": "",
                            "n_total": len(afdb),
                            "n_pos_total": int(y_afdb.sum()),
                            "n_neg_total": int((1 - y_afdb).sum()),
                            "holdout_size": int(holdout_sizes[0]),
                            "train_pos_mean": float(np.mean(train_pos_counts)),
                            "train_pos_min": int(np.min(train_pos_counts)),
                            "train_pos_max": int(np.max(train_pos_counts)),
                            "source_file": str(AFDB_INPUT.relative_to(AFDB_INPUT.parents[2])),
                            "split_protocol": "paired StratifiedShuffleSplit across ipTM and ipSAEmax",
                            "seed": SEED + 1000 * threshold_index + train_size,
                        }
                    )

    result = pd.DataFrame(rows)
    repeats = pd.DataFrame(repeat_rows)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)
    repeats.to_csv(REPEAT_OUTPUT, index=False)
    write_summary(result)
    return result


def write_summary(result: pd.DataFrame) -> None:
    lines = [
        "# AFDB Workshop Recalibration Summary",
        "",
        f"- Source: `{AFDB_INPUT.relative_to(AFDB_INPUT.parents[2])}`",
        f"- General source: `{GENERAL_INPUT.relative_to(GENERAL_INPUT.parents[2])}`",
        "- AFDB finite-DockQ universe asserted at 304 rows.",
        "- Raw ipTM, raw ipSAEmax, and frozen General isotonic ipTM are each evaluated once on all 304 AFDB complexes and rendered as fixed horizontal reference lines.",
        "- Local recalibration uses paired disjoint `StratifiedShuffleSplit` partitions shared by ipTM and ipSAEmax.",
        f"- Repeats: {N_REPEATS}",
        f"- Seed base: {SEED}",
        "- Local calibration sizes: 5, 10, 15, ..., 100 AFDB complexes (1.6% to 32.9% of the 304-complex universe).",
        f"- Repeat-level local results: `{REPEAT_OUTPUT.relative_to(REPEAT_OUTPUT.parents[2])}`.",
        "",
    ]
    available = result.loc[result["available"]].copy()
    for threshold_name, threshold_value in THRESHOLDS:
        lines.append(f"## DockQ >= {threshold_value}")
        subset = available.loc[(available["threshold"] == threshold_name) & (available["metric"] == "brier")]
        for method in [
            "Raw ipTM",
            "Isotonic ipTM (General frozen)",
            "Isotonic ipTM (local AFDB)",
            "Raw ipSAEmax",
            "Isotonic ipSAEmax (local AFDB)",
        ]:
            view = subset.loc[subset["method"] == method].sort_values("train_size")
            if view.empty:
                continue
            if method in {"Raw ipTM", "Raw ipSAEmax", "Isotonic ipTM (General frozen)"}:
                fixed = view.iloc[0]
                lines.append(f"- {method}: full-AFDB fixed Brier {fixed['mean']:.4f} (no split-wise SD).")
            else:
                best = view.loc[view["mean"].idxmin()]
                lines.append(
                    f"- {method}: best local-holdout mean Brier {best['mean']:.4f} ± {best['std']:.4f} at train_size={int(best['train_size'])}."
                )
        lines.append("")
    write_text(SUMMARY, "\n".join(lines).rstrip() + "\n")


def main() -> None:
    result = compute_source_data()
    print(result.to_string(index=False))
    print(f"Wrote {OUTPUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
