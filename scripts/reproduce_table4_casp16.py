"""Reproduce final manuscript Table 4: CASP16 bootstrap evaluation."""

from __future__ import annotations

import pandas as pd

from common import DATA, PAPER_TAB, THRESHOLDS, ensure_dirs, format_metric, write_text

METHOD_ORDER = [
    "Raw ipTM",
    "Raw ranking confidence",
    "Raw pDockQ2 (published)",
    "Raw pDockQ2 (refit)",
    "Isotonic ipTM",
    "Isotonic iPAE",
    "MLP 5-feat CE",
]

CAPTION = (
    "CASP16 external calibration and classification results summarized by target-balanced bootstrap "
    "(100 iterations, 100 models per target, minimum 100 models per target, seed 42). All fitted "
    "methods are trained on AFM-benchmark and applied frozen to CASP16. H1265 was excluded because "
    "DockQ v2 chain-mapping optimization did not converge within computational limits; H1217 and "
    "H1258 were excluded from bootstrap because they contain fewer than 100 scored models. pDockQ2 "
    "(published) uses original parameters; pDockQ2 (refit) uses AFM-benchmark refit parameters. "
    "Best mean per column in \\textbf{bold}. Values are reported as mean$\\pm$std."
)


def build_markdown(df: pd.DataFrame) -> str:
    lines = ["# Table 4: CASP16 bootstrap evaluation", ""]
    for thr_name, thr_val in THRESHOLDS:
        sub = df[df["threshold_name"] == thr_name].copy()
        lines += [f"## DockQ >= {thr_val:.2f}", ""]
        headers = ["Method", "Brier", "ECE", "AUROC", "MCC", "PPV"]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for _, row in sub.iterrows():
            vals = [
                row["method"],
                f"{row['brier_mean']:.4f}±{row['brier_std']:.4f}",
                f"{row['ece_mean']:.4f}±{row['ece_std']:.4f}",
                f"{row['auroc_mean']:.4f}±{row['auroc_std']:.4f}",
                f"{row['mcc_mean']:.4f}±{row['mcc_std']:.4f}",
                f"{row['ppv_mean']:.4f}±{row['ppv_std']:.4f}",
            ]
            lines.append("| " + " | ".join(vals) + " |")
        lines.append("")
    return "\n".join(lines)


def build_latex(df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[t]",
        f"\\caption{{{CAPTION}}}",
        "\\label{tab:casp16_bootstrap}",
        "\\centering",
        "\\resizebox{\\columnwidth}{!}{%",
        "\\begin{tabular}{lccccc}",
        "\\toprule",
        "Method & Brier$\\downarrow$ & ECE$\\downarrow$ & AUROC$\\uparrow$ & MCC$\\uparrow$ & PPV$\\uparrow$ \\",
        "\\midrule",
    ]
    for idx, (thr_name, thr_val) in enumerate(THRESHOLDS):
        sub = df[df["threshold_name"] == thr_name].copy()
        lines.append(f"\\multicolumn{{6}}{{l}}{{\\textit{{DockQ $\\geq$ {thr_val:.2f}}}}} \\")
        for _, row in sub.iterrows():
            cells = [row["method"]]
            for metric in ["brier", "ece", "auroc", "mcc", "ppv"]:
                mean = format_metric(row[f"{metric}_mean"], 4 if metric in {"brier", "ece"} else 4, drop_zero=True)
                std = format_metric(row[f"{metric}_std"], 4, drop_zero=True)
                cells.append(f"{mean}$\\pm${std}")
            lines.append(" & ".join(cells) + " \\")
        if idx != len(THRESHOLDS) - 1:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}", "}%", "\\end{table}"]
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_dirs()
    df = pd.read_csv(DATA / "casp16_bootstrap_summary.csv")
    df["method_order"] = df["method"].map({m: i for i, m in enumerate(METHOD_ORDER)})
    df = df.sort_values(["threshold", "method_order"]).drop(columns=["method_order"])
    df.to_csv(PAPER_TAB / "tab4_casp16_bootstrap.csv", index=False)
    write_text(PAPER_TAB / "tab4_casp16_bootstrap.md", build_markdown(df))
    write_text(PAPER_TAB / "tab4_casp16_bootstrap.tex", build_latex(df))
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
