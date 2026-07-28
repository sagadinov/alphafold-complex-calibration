#!/usr/bin/env python3
"""Merge the shipped target-preserving Ab-Ag training shards into one CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.abag_train_parts import default_output_path, merge_parts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=default_output_path(),
        help="Output CSV path. Defaults to data/abag_train_v2.csv inside the repository.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing output CSV.",
    )
    args = parser.parse_args()
    summary = merge_parts(output_path=args.output, force=args.force)
    print(
        "Merged {n_parts} shards -> {output} "
        "(rows={n_rows}, unique_targets={n_targets})".format(**summary)
    )


if __name__ == "__main__":
    main()
