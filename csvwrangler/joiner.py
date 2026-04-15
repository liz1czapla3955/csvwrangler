"""Join two CSV files on a common key column."""

import csv
from typing import IO


def join_rows(
    left_rows: list[dict],
    right_rows: list[dict],
    key: str,
    how: str = "inner",
) -> list[dict]:
    """Join two lists of row dicts on a common key.

    Supports 'inner', 'left', and 'right' join types.
    Columns from side that share a name with the left (excluding the
    key) are suff"""
    if how not in ("inner", "left", "right"):
        raise ValueError(f"Unsupported join type: {how!r}. Use or 'right'.")

    right_index: dict[str, list[dict]] = {}
    for row in right_rows:
        k = row.get(key)
        right_index.setdefault(k, []).append(row)

    if how == "right":
        left_rows, right_rows = right_rows, left_rows
        right_index = {}
        for row in right_rows:
            k = row.get(key)
            right_index.setdefault(k, []).append(row)
        how = "left"

    results: list[dict] = []
    for left_row in left_rows:
        k = left_row.get(key)
        matches = right_index.get(k)
        if matches:
            for right_row in matches:
                merged = dict(left_row)
                for col, val in right_row.items():
                    if col == key:
                        continue
                    dest = col if col not in merged else f"{col}_right"
                    merged[dest] = val
                results.append(merged)
        elif how == "left":
            results.append(dict(left_row))

    return results


def join_files(
    left_file: IO[str],
    right_file: IO[str],
    output_file: IO[str],
    key: str,
    how: str = "inner",
) -> int:
    """Read two CSV files, join them, and write the result. Returns row count."""
    left_rows = list(csv.DictReader(left_file))
    right_rows = list(csv.DictReader(right_file))

    joined = join_rows(left_rows, right_rows, key=key, how=how)

    if not joined:
        output_file.write("")
        return 0

    fieldnames = list(joined[0].keys())
    writer = csv.DictWriter(output_file, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(joined)
    return len(joined)
