"""Diff two CSV files and report added, removed, or changed rows."""

import csv
import io
from typing import Iterator


def diff_rows(
    rows_a: list[dict],
    rows_b: list[dict],
    key_fields: list[str],
) -> list[dict]:
    """Compare two lists of row dicts by key fields.

    Returns a list of dicts with an added '_diff' field:
      'added'   – row present in B but not A
      'removed' – row present in A but not B
      'changed' – row present in both but with different non-key values
      'unchanged' – identical in both
    """
    def make_key(row: dict) -> tuple:
        return tuple(row.get(f, "") for f in key_fields)

    index_a = {make_key(r): r for r in rows_a}
    index_b = {make_key(r): r for r in rows_b}

    results: list[dict] = []

    for key, row in index_a.items():
        if key not in index_b:
            results.append({**row, "_diff": "removed"})
        else:
            row_b = index_b[key]
            if row == row_b:
                results.append({**row, "_diff": "unchanged"})
            else:
                results.append({**row_b, "_diff": "changed"})

    for key, row in index_b.items():
        if key not in index_a:
            results.append({**row, "_diff": "added"})

    return results


def diff_files(
    path_a: str,
    path_b: str,
    key_fields: list[str],
    output: io.TextIOWrapper,
    include_unchanged: bool = False,
) -> None:
    """Read two CSV files, diff them, and write results to output."""
    def read_csv(path: str) -> list[dict]:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    rows_a = read_csv(path_a)
    rows_b = read_csv(path_b)

    if not rows_a and not rows_b:
        return

    diffed = diff_rows(rows_a, rows_b, key_fields)

    if not include_unchanged:
        diffed = [r for r in diffed if r["_diff"] != "unchanged"]

    if not diffed:
        return

    fieldnames = list(diffed[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(diffed)
