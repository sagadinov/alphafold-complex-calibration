"""Shared helpers for public reproduction scripts."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.evaluate import compute_all_metrics

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
PAPER_FIG = ROOT / "paper" / "figures"
PAPER_TAB = ROOT / "paper" / "tables"

THRESHOLDS = [("acceptable", 0.23), ("medium", 0.49), ("high", 0.80)]
METHOD_LABELS = {
    "Raw ipTM": "p_raw_iptm",
    "Raw ranking conf.": "p_raw_rank",
    "Raw iPAE proxy": "p_raw_ipae",
    "pDockQ2 (published)": "p_pdockq2_published",
    "Iso. ipTM": {
        "acceptable": "p_iso_iptm_acceptable",
        "medium": "p_iso_iptm_medium",
        "high": "p_iso_iptm_high",
    },
    "Iso. iPAE": {
        "acceptable": "p_iso_ipae_acceptable",
        "medium": "p_iso_ipae_medium",
        "high": "p_iso_ipae_high",
    },
    "MLP 5-feat CE": {
        "acceptable": "p_mlp_ce_acceptable",
        "medium": "p_mlp_ce_medium",
        "high": "p_mlp_ce_high",
    },
}
TABLE_METHOD_ORDER = [
    "Raw ipTM",
    "Raw ranking conf.",
    "Raw iPAE proxy",
    "pDockQ2 (published)",
    "Iso. ipTM",
    "Iso. iPAE",
    "MLP 5-feat CE",
]


def ensure_dirs() -> None:
    PAPER_FIG.mkdir(parents=True, exist_ok=True)
    PAPER_TAB.mkdir(parents=True, exist_ok=True)


def load_predictions(dataset: str) -> pd.DataFrame:
    path = DATA / f"{dataset}_predictions_v3.csv"
    return pd.read_csv(path, low_memory=False)


def score_column(method: str, threshold_name: str) -> str:
    spec = METHOD_LABELS[method]
    if isinstance(spec, dict):
        return spec[threshold_name]
    return spec


def compute_table_from_predictions(df: pd.DataFrame, methods: list[str] | None = None) -> pd.DataFrame:
    rows = []
    methods = methods or TABLE_METHOD_ORDER
    for thr_name, thr_val in THRESHOLDS:
        y_true = (df["dockq"].to_numpy(dtype=float) >= thr_val).astype(int)
        for method in methods:
            col = score_column(method, thr_name)
            metrics = compute_all_metrics(y_true, df[col].to_numpy(dtype=float))
            rows.append(
                {
                    "threshold": thr_name,
                    "threshold_val": thr_val,
                    "method": method,
                    "n_pos": int(y_true.sum()),
                    "n_total": int(len(y_true)),
                    **metrics,
                }
            )
    out = pd.DataFrame(rows)
    out["method_order"] = out["method"].map({m: i for i, m in enumerate(methods)})
    out["thr_order"] = out["threshold"].map({t: i for i, (t, _) in enumerate(THRESHOLDS)})
    out = out.sort_values(["thr_order", "method_order"]).drop(columns=["thr_order", "method_order"])
    return out


def markdown_table(df: pd.DataFrame, columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in df.iterrows():
        vals = []
        for col in columns:
            val = row[col]
            if isinstance(val, float):
                vals.append(f"{val:.4f}")
            else:
                vals.append(str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def save_main_table(df: pd.DataFrame, stem: str) -> None:
    ensure_dirs()
    df.to_csv(PAPER_TAB / f"{stem}.csv", index=False)
    main_cols = ["method", "brier", "ece", "auroc", "mcc", "ppv"]
    md = [f"# {stem}", ""]
    for thr_name, thr_val in THRESHOLDS:
        sub = df[df["threshold"] == thr_name][main_cols]
        md.append(f"## DockQ >= {thr_val:.2f}")
        md.append("")
        md.append(markdown_table(sub, main_cols))
        md.append("")
    (PAPER_TAB / f"{stem}.md").write_text("\n".join(md), encoding="utf-8")


def save_simple_latex(df: pd.DataFrame, stem: str, caption: str, label: str) -> None:
    lines = [
        "\\begin{table}[t]",
        "\\centering",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        "\\begin{tabular}{lccccc}",
        "\\toprule",
        "Method & Brier & ECE & AUROC & MCC & PPV \\\\",
        "\\midrule",
    ]
    for thr_name, thr_val in THRESHOLDS:
        lines.append(f"\\multicolumn{{6}}{{l}}{{\\textit{{DockQ $\\geq$ {thr_val:.2f}}}}} \\\\")
        sub = df[df["threshold"] == thr_name]
        for _, row in sub.iterrows():
            lines.append(
                f"{row['method']} & {row['brier']:.4f} & {row['ece']:.4f} & "
                f"{row['auroc']:.4f} & {row['mcc']:.4f} & {row['ppv']:.4f} \\\\"
            )
        if thr_name != THRESHOLDS[-1][0]:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    (PAPER_TAB / f"{stem}.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_report() -> dict:
    return json.loads((DATA / "report_data_v3.json").read_text(encoding="utf-8"))


def base_axes_style(ax, title: str) -> None:
    ax.set_title(title, fontsize=12)
    ax.grid(True, alpha=0.12)

