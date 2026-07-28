#!/usr/bin/env python3
"""Validate the shipped Ab-Ag training shards and their manifest."""

from __future__ import annotations

from src.abag_train_parts import validate_manifest


def main() -> None:
    summary = validate_manifest()
    print(
        "Validated {n_parts} Ab-Ag training shards "
        "(rows={n_rows}, unique_targets={n_targets})".format(**summary)
    )


if __name__ == "__main__":
    main()
