#!/usr/bin/env python3
"""Render score-distribution bars for the workshop calibration comparison."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PAPER_FIGURES = ROOT / "paper" / "figures"
SOURCE_DIR = PAPER_FIGURES / "source_data"
BINS = np.linspace(0.0, 1.0, 6)
BIN_LABELS = ["0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]
COLORS = {"Ab-Ag": "#2563EB", "General": "#FA8072", "AFDB": "#059669"}


def load_scores(ipsae_path: Path) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    abag = pd.read_csv(ROOT / "data" / "abag_predictions_v3.csv", usecols=["target_id", "model_id", "iptm"])
    general = pd.read_csv(ROOT / "data" / "general_predictions_v3.csv", usecols=["target_id", "iptm"])
    afdb = pd.read_csv(ROOT / "analysis" / "afdb" / "afdb_positive_dockq_features.csv", usecols=["modelEntityId", "iptm", "ipsae_max"])
    ipsae = pd.read_csv(ipsae_path, usecols=["target_id", "model_id", "ipsae_model_max"])
    abag = abag.merge(ipsae, on=["target_id", "model_id"], how="left", validate="one_to_one")
    if abag["ipsae_model_max"].isna().any():
        raise RuntimeError("True ipSAEmax did not cover every locked Ab-Ag prediction")

    result: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for name, frame, score, group in [
        ("Ab-Ag ipTM", abag, "iptm", "target_id"),
        ("General ipTM", general, "iptm", "target_id"),
        ("AFDB ipTM", afdb, "iptm", "modelEntityId"),
        ("Ab-Ag ipSAEmax", abag, "ipsae_model_max", "target_id"),
        ("AFDB ipSAEmax", afdb, "ipsae_max", "modelEntityId"),
    ]:
        values = pd.to_numeric(frame[score], errors="coerce")
        valid = frame.loc[values.notna(), [group]].copy()
        valid[score] = values.loc[values.notna()].to_numpy(float)
        array = valid[score].to_numpy(float)
        if not np.all((array >= 0.0) & (array <= 1.0)):
            raise RuntimeError(f"{name} is outside [0, 1]")
        result[name] = (array, valid.groupby(group)[score].mean().to_numpy(float))
    return result


def summarize(score_name: str, datasets: list[str], loaded: dict[str, tuple[np.ndarray, np.ndarray]]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for dataset in datasets:
        values, target_means = loaded[f"{dataset} {score_name}"]
        for level, scores in [("pooled_models", values), ("per_target_mean", target_means)]:
            counts, _ = np.histogram(scores, bins=BINS)
            for index, count in enumerate(counts):
                rows.append({
                    "score": score_name,
                    "dataset": dataset,
                    "level": level,
                    "bin_left": BINS[index],
                    "bin_right": BINS[index + 1],
                    "bin_label": BIN_LABELS[index],
                    "count": int(count),
                    "fraction": float(count / len(scores)),
                    "n_values": int(len(scores)),
                })
    return pd.DataFrame(rows)


def render(summary: pd.DataFrame, score_name: str, datasets: list[str], output_name: str) -> None:
    plt.rcParams.update({"font.size": 17, "axes.labelsize": 18, "axes.titlesize": 19, "xtick.labelsize": 15, "ytick.labelsize": 16, "legend.fontsize": 15})
    fig, axes = plt.subplots(1, 2, figsize=(14.6, 5.2), sharey=True)
    x = np.arange(len(BIN_LABELS))
    width = 0.72 / len(datasets)
    offsets = np.linspace(-0.36 + width / 2, 0.36 - width / 2, len(datasets))
    for axis, level, title in zip(axes, ["pooled_models", "per_target_mean"], ["Pooled models", "Per-target mean score"]):
        for offset, dataset in zip(offsets, datasets):
            panel = summary.loc[(summary["dataset"] == dataset) & (summary["level"] == level)].sort_values("bin_left")
            axis.bar(x + offset, panel["fraction"], width=width, color=COLORS[dataset], label=dataset)
        axis.set_xticks(x, BIN_LABELS, rotation=18)
        axis.set_ylim(0.0, 1.0)
        axis.set_xlabel(f"{score_name} bin")
        axis.set_title(title)
        axis.grid(axis="y", alpha=0.16)
    axes[0].set_ylabel("Fraction")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=len(datasets), frameon=False, bbox_to_anchor=(0.5, 1.04))
    if score_name == "ipSAEmax":
        fig.text(0.5, 0.01, "General is omitted: no true ipSAEmax was computed for the locked General benchmark.", ha="center", fontsize=13, color="#4B5563")
        rect = (0, 0.05, 1, 0.92)
    else:
        rect = (0, 0, 1, 0.92)
    fig.tight_layout(rect=rect)
    PAPER_FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(PAPER_FIGURES / f"{output_name}.pdf", bbox_inches="tight", metadata={"Creator": "alphafold-complex-calibration"})
    fig.savefig(PAPER_FIGURES / f"{output_name}.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--abag-ipsae", type=Path, required=True, help="Per-model true ipSAEmax CSV for the locked Ab-Ag test rows")
    args = parser.parse_args()
    loaded = load_scores(args.abag_ipsae)
    iptm = summarize("ipTM", ["Ab-Ag", "General", "AFDB"], loaded)
    ipsae = summarize("ipSAEmax", ["Ab-Ag", "AFDB"], loaded)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    iptm.to_csv(SOURCE_DIR / "F5_workshop_iptm_distribution.csv", index=False)
    ipsae.to_csv(SOURCE_DIR / "F5_workshop_ipsaemax_distribution.csv", index=False)
    render(iptm, "ipTM", ["Ab-Ag", "General", "AFDB"], "F5_workshop_iptm_distribution")
    render(ipsae, "ipSAEmax", ["Ab-Ag", "AFDB"], "F5_workshop_ipsaemax_distribution")


if __name__ == "__main__":
    main()
