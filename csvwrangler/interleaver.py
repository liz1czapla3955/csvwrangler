"""Interleave rows from two CSV sources, alternating between them."""

import csv
import io
from itertools import zip_longest
from typing import Iterator, List, Optional

_SENTINEL = object()


def interleave_rows(
    rows_a: List[dict],
    rows_b: List[dict],
    fill: bool = False,
    fill_value: str = "",
) -> List[dict]:
    """Interleave two sequences of rows, alternating A then B.

    Both row sequences must share the same fieldnames.

    Args:
        rows_a: First sequence of rows.
        rows_b: Second sequence of rows.
        fill: If True, continue with remaining rows when one source is exhausted.
        fill_value: Value used to fill missing fields when sources differ in length
                    and *fill* is True.

    Returns:
        Interleaved list of rows.
    """
    if not rows_a and not rows_b:
        return []

    result: List[dict] = []

    if fill:
        # Determine unified fieldnames
        fields_a = list(rows_a[0].keys()) if rows_a else []
        fields_b = list(rows_b[0].keys()) if rows_b else []
        all_fields = fields_a or fields_b

        for row_a, row_b in zip_longest(rows_a, rows_b):
            if row_a is not None:
                result.append(row_a)
            else:
                result.append({f: fill_value for f in all_fields})
            if row_b is not None:
                result.append(row_b)
            else:
                result.append({f: fill_value for f in all_fields})
    else:
        for row_a, row_b in zip(rows_a, rows_b):
            result.append(row_a)
            result.append(row_b)

    return result


def interleave_files(
    reader_a,
    reader_b,
    writer,
    fill: bool = False,
    fill_value: str = "",
) -> None:
    """Read from two CSV readers, interleave, and write to *writer*."""
    rows_a = list(reader_a)
    rows_b = list(reader_b)

    if not rows_a and not rows_b:
        return

    fieldnames = list(rows_a[0].keys()) if rows_a else list(rows_b[0].keys())
    writer.fieldnames = fieldnames
    writer.writeheader()

    for row in interleave_rows(rows_a, rows_b, fill=fill, fill_value=fill_value):
        writer.writerow(row)
