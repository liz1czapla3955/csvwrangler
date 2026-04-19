import csv
import itertools
from typing import Iterator


def crossjoin_rows(
    left: list[dict],
    right: list[dict],
    left_prefix: str = "left_",
    right_prefix: str = "right_",
) -> list[dict]:
    """Return the Cartesian product of two lists of rows."""
    if not left or not right:
        return []

    left_keys = list(left[0].keys())
    right_keys = list(right[0].keys())
    conflicts = set(left_keys) & set(right_keys)

    result = []
    for l_row, r_row in itertools.product(left, right):
        merged = {}
        for k, v in l_row.items():
            key = f"{left_prefix}{k}" if k in conflicts else k
            merged[key] = v
        for k, v in r_row.items():
            key = f"{right_prefix}{k}" if k in conflicts else k
            merged[key] = v
        result.append(merged)
    return result


def crossjoin_files(
    reader_left,
    reader_right,
    writer,
    left_prefix: str = "left_",
    right_prefix: str = "right_",
) -> None:
    left_rows = list(reader_left)
    right_rows = list(reader_right)

    rows = crossjoin_rows(left_rows, right_rows, left_prefix, right_prefix)
    if not rows:
        return

    writer.writeheader()
    for row in rows:
        writer.writerow(row)
