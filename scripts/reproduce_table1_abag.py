"""Reproduce the Ab-Ag main table from locked prediction exports."""

from __future__ import annotations

from scripts.common import compute_table_from_predictions, load_predictions, save_main_table, save_simple_latex


def main() -> None:
    df = load_predictions("abag")
    table = compute_table_from_predictions(df)
    save_main_table(table, "tab_abag_main_reproduced")
    save_simple_latex(
        table,
        "tab_abag_main_reproduced",
        "Reproduced Ab-Ag evaluation from locked per-model predictions.",
        "tab:abag_reproduced",
    )
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()

