"""Reproduce the General multimer main table from locked OOF predictions."""

from __future__ import annotations

from scripts.common import compute_table_from_predictions, load_predictions, save_main_table, save_simple_latex


def main() -> None:
    df = load_predictions("general")
    table = compute_table_from_predictions(df)
    save_main_table(table, "tab_general_main_reproduced")
    save_simple_latex(
        table,
        "tab_general_main_reproduced",
        "Reproduced General multimer evaluation from locked out-of-fold predictions.",
        "tab:general_reproduced",
    )
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()

