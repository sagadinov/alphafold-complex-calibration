#!/usr/bin/env python3
"""Render score-distribution bars for the workshop calibration comparison."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression


ROOT = Path(__file__).resolve().parents[1]
PAPER_FIGURES = ROOT / "paper" / "figures"
SOURCE_DIR = PAPER_FIGURES / "source_data"
BINS = np.linspace(0.0, 1.0, 6)
BIN_LABELS = ["0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"]
COLORS = {"Ab-Ag": "#2563EB", "General": "#FA8072", "AFDB": "#059669"}
THRESHOLDS = (("acceptable", 0.23), ("medium", 0.49), ("high", 0.80))


def store_score(result: dict[str, tuple[np.ndarray, np.ndarray]], name: str, frame: pd.DataFrame, score: str, group: str) -> None:
    values = pd.to_numeric(frame[score], errors="coerce")
    valid = frame.loc[values.notna(), [group]].copy()
    valid[score] = values.loc[values.notna()].to_numpy(float)
    array = valid[score].to_numpy(float)
    if not np.all((array >= 0.0) & (array <= 1.0)):
        raise RuntimeError(f"{name} is outside [0, 1]")
    result[name] = (array, valid.groupby(group)[score].mean().to_numpy(float))


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
        store_score(result, name, frame, score, group)

    # Freeze one General-trained mapping per event, then apply it unchanged to
    # all domains. This isolates score-distribution shift from refitting.
    general_dockq = pd.read_csv(ROOT / "data" / "general_predictions_v3.csv", usecols=["dockq"])["dockq"]
    for threshold_name, threshold_value in THRESHOLDS:
        model = IsotonicRegression(out_of_bounds="clip").fit(
            general["iptm"].to_numpy(float),
            (general_dockq.to_numpy(float) >= threshold_value).astype(int),
        )
        for dataset, frame, group in [
            ("Ab-Ag", abag, "target_id"),
            ("General", general, "target_id"),
            ("AFDB", afdb, "modelEntityId"),
        ]:
            mapped = frame[[group]].copy()
            mapped["iso_iptm"] = model.predict(frame["iptm"].to_numpy(float))
            store_score(result, f"{dataset} iso_iptm_{threshold_name}", mapped, "iso_iptm", group)
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


def render_iso_panels(summaries: dict[str, pd.DataFrame]) -> None:
    """Render General-frozen isotonic probabilities for all three events."""
    plt.rcParams.update({"font.size": 16, "axes.labelsize": 17, "axes.titlesize": 18, "xtick.labelsize": 13, "ytick.labelsize": 14, "legend.fontsize": 14})
    fig, axes = plt.subplots(2, 3, figsize=(15.6, 8.2), sharey=True)
    x = np.arange(len(BIN_LABELS))
    width = 0.24
    offsets = (-width, 0.0, width)
    for column, (threshold_name, threshold_value) in enumerate(THRESHOLDS):
        summary = summaries[threshold_name]
        for row, (level, title) in enumerate([("pooled_models", "Pooled models"), ("per_target_mean", "Per-target mean probability")]):
            axis = axes[row, column]
            for offset, dataset in zip(offsets, ["Ab-Ag", "General", "AFDB"]):
                panel = summary.loc[(summary["dataset"] == dataset) & (summary["level"] == level)].sort_values("bin_left")
                axis.bar(x + offset, panel["fraction"], width=width, color=COLORS[dataset], label=dataset)
            axis.set_title(f"DockQ >= {threshold_value:.2f}")
            axis.set_xticks(x, BIN_LABELS, rotation=18)
            if row == 1:
                axis.set_xlabel("Predicted probability bin")
            axis.grid(axis="y", alpha=0.16)
            if column == 0:
                axis.set_ylabel(f"Fraction\n{title}")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(PAPER_FIGURES / "F5_workshop_iso_iptm_distribution.pdf", bbox_inches="tight", metadata={"Creator": "alphafold-complex-calibration"})
    fig.savefig(PAPER_FIGURES / "F5_workshop_iso_iptm_distribution.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


def render_overview(raw: pd.DataFrame, iso: pd.DataFrame, ipsae: pd.DataFrame) -> None:
    """Compare raw score, frozen calibrated probability, and true ipSAEmax."""
    plt.rcParams.update({"font.size": 16, "axes.labelsize": 17, "axes.titlesize": 18, "xtick.labelsize": 13, "ytick.labelsize": 14, "legend.fontsize": 14})
    panels = [
        ("Raw ipTM", raw, ["Ab-Ag", "General", "AFDB"]),
        ("Isotonic ipTM (General), DockQ >= 0.23", iso, ["Ab-Ag", "General", "AFDB"]),
        ("True ipSAEmax", ipsae, ["Ab-Ag", "AFDB"]),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(15.6, 8.2), sharey=True)
    x = np.arange(len(BIN_LABELS))
    for column, (title, summary, datasets) in enumerate(panels):
        width = 0.72 / len(datasets)
        offsets = np.linspace(-0.36 + width / 2, 0.36 - width / 2, len(datasets))
        for row, (level, level_title) in enumerate([("pooled_models", "Pooled models"), ("per_target_mean", "Per-target mean")]):
            axis = axes[row, column]
            for offset, dataset in zip(offsets, datasets):
                panel = summary.loc[(summary["dataset"] == dataset) & (summary["level"] == level)].sort_values("bin_left")
                axis.bar(x + offset, panel["fraction"], width=width, color=COLORS[dataset], label=dataset)
            axis.set_title(title)
            axis.set_xticks(x, BIN_LABELS, rotation=18)
            axis.grid(axis="y", alpha=0.16)
            if column == 0:
                axis.set_ylabel(f"Fraction\n{level_title}")
            if row == 1:
                axis.set_xlabel("Score / probability bin")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.text(0.5, 0.006, "True ipSAEmax: General unavailable.", ha="center", fontsize=13, color="#4B5563")
    fig.tight_layout(rect=(0, 0.035, 1, 0.94))
    fig.savefig(PAPER_FIGURES / "F5_workshop_score_distribution_overview.pdf", bbox_inches="tight", metadata={"Creator": "alphafold-complex-calibration"})
    fig.savefig(PAPER_FIGURES / "F5_workshop_score_distribution_overview.png", bbox_inches="tight", dpi=300)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--abag-ipsae", type=Path, required=True, help="Per-model true ipSAEmax CSV for the locked Ab-Ag test rows")
    args = parser.parse_args()
    loaded = load_scores(args.abag_ipsae)
    iptm = summarize("ipTM", ["Ab-Ag", "General", "AFDB"], loaded)
    ipsae = summarize("ipSAEmax", ["Ab-Ag", "AFDB"], loaded)
    iso_summaries = {
        threshold_name: summarize(f"iso_iptm_{threshold_name}", ["Ab-Ag", "General", "AFDB"], loaded)
        for threshold_name, _ in THRESHOLDS
    }
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    iptm.to_csv(SOURCE_DIR / "F5_workshop_iptm_distribution.csv", index=False)
    ipsae.to_csv(SOURCE_DIR / "F5_workshop_ipsaemax_distribution.csv", index=False)
    for threshold_name, summary in iso_summaries.items():
        summary.to_csv(SOURCE_DIR / f"F5_workshop_iso_iptm_distribution_{threshold_name}.csv", index=False)
    render(iptm, "ipTM", ["Ab-Ag", "General", "AFDB"], "F5_workshop_iptm_distribution")
    render(ipsae, "ipSAEmax", ["Ab-Ag", "AFDB"], "F5_workshop_ipsaemax_distribution")
    render_iso_panels(iso_summaries)
    render_overview(iptm, iso_summaries["acceptable"], ipsae)


if __name__ == "__main__":
    main()
