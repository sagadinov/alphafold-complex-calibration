"""Reproduce final manuscript Table 1: Ab-Ag calibration and classification metrics."""

from __future__ import annotations

import pandas as pd

from common import (
    ABAG_METHOD_ORDER,
    DATA,
    DISPLAY_NAME_TEX,
    PAPER_TAB,
    THRESHOLDS,
    bold_best,
    ensure_dirs,
    format_metric,
    load_report,
    method_rows_from_report,
    write_text,
)

MAIN_METRICS = ["brier", "ece", "auroc", "mcc", "ppv"]

CAPTION = (
    "Ab-Ag calibration and classification results (62,681 evaluated models, 1,257 targets; "
    "65,650 raw models total). All methods fitted on the Ab-Ag training split. Models with "
    "missing DockQ or required confidence features (n=2,969) were excluded from evaluation. "
    "pDockQ2 (published) uses original parameters from Zhu et al.; pDockQ2 (refit) uses "
    "parameters optimized on our training data. ABAG-Rank is evaluated on Matteo's test split, "
    "which overlaps our test split by 983 targets. Best per column in \\textbf{bold}."
)

FOOTNOTE = (
    "{\\footnotesize $^\\dagger$ABAG-Rank is evaluated on Matteo's test split (25{,}440 models, "
    "1{,}091 targets), which overlaps our test split by 983 targets. Brier and ECE are not "
    "reported because its output is continuous DockQ rather than calibrated probability.}"
)


def build_dataframe(report: dict) -> pd.DataFrame:
    rows = []
    for thr_name, thr_val in THRESHOLDS:
        for row in method_rows_from_report(report, "abag", thr_name, ABAG_METHOD_ORDER):
            rows.append({"threshold": thr_name, "threshold_val": thr_val, **row})
    return pd.DataFrame(rows)


def build_markdown(df: pd.DataFrame) -> str:
    lines = ["# Table 1: Ab-Ag main metrics", ""]
    for thr_name, thr_val in THRESHOLDS:
        sub = df[df["threshold"] == thr_name].copy()
        n_pos = int(sub["n_pos"].dropna().iloc[0])
        n_neg = int(sub["n_neg"].dropna().iloc[0])
        lines += [f"## DockQ >= {thr_val:.2f} (n+={n_pos:,}, n-={n_neg:,})", ""]
        cols = ["Method", "Brier", "ECE", "AUROC", "MCC", "PPV"]
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
        for _, row in sub.iterrows():
            vals = [
                row["method"],
                format_metric(row["brier"], 4),
                format_metric(row["ece"], 4),
                format_metric(row["auroc"], 3),
                format_metric(row["mcc"], 3),
                format_metric(row["ppv"], 3),
            ]
            lines.append("| " + " | ".join(vals) + " |")
        lines.append("")
    lines += [FOOTNOTE, ""]
    return "\n".join(lines)


def build_latex(df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[t]",
        f"\\caption{{{CAPTION}}}",
        "\\label{tab:abag_main}",
        "\\centering",
        "\\resizebox{\\columnwidth}{!}{%",
        "\\begin{tabular}{lccccc}",
        "\\toprule",
        "Method & Brier$\\downarrow$ & ECE$\\downarrow$ & AUROC$\\uparrow$ & MCC$\\uparrow$ & PPV$\\uparrow$ \\",
        "\\midrule",
    ]
    for idx, (thr_name, thr_val) in enumerate(THRESHOLDS):
        sub = df[df["threshold"] == thr_name].copy()
        n_pos = int(sub["n_pos"].dropna().iloc[0])
        n_neg = int(sub["n_neg"].dropna().iloc[0])
        lines.append(
            f"\\multicolumn{{6}}{{l}}{{\\textit{{DockQ $\\ge$ {thr_val:.2f} --- $n_+$\\!=\\!{n_pos:,}, $n_-$\\!=\\!{n_neg:,}}}}} \\")
        best = {metric: bold_best(sub.to_dict('records'), metric) for metric in MAIN_METRICS}
        for _, row in sub.iterrows():
            cells = [DISPLAY_NAME_TEX[row["method"]]]
            for metric in MAIN_METRICS:
                decimals = 4 if metric in {"brier", "ece"} else 3
                text = format_metric(row[metric], decimals, drop_zero=True)
                if row["method"] in best[metric] and text != "---":
                    text = f"\\textbf{{{text}}}"
                cells.append(text)
            lines.append(" & ".join(cells) + " \\")
        if idx != len(THRESHOLDS) - 1:
            lines.append("\\midrule")
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "}%",
        "\\vspace{2pt}",
        FOOTNOTE,
        "\\end{table}",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()
    report = load_report()
    df = build_dataframe(report)
    df.to_csv(PAPER_TAB / "tab1_abag_main.csv", index=False)
    write_text(PAPER_TAB / "tab1_abag_main.md", build_markdown(df))
    write_text(PAPER_TAB / "tab1_abag_main.tex", build_latex(df))
    print(df[["threshold", "method", "brier", "ece", "auroc", "mcc", "ppv"]].to_string(index=False))


if __name__ == "__main__":
    main()
