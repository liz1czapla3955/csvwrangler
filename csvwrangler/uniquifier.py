"""Uniquify: keep only rows where a column value appears exactly once."""

import csv
import io
from collections import Counter
from typing import Iterable, Iterator


def uniquify_rows(
    rows: Iterable[dict],
    column: str,
    invert: bool = False,
) -> Iterator[dict]:
    """Yield rows whose value in *column* is unique (appears exactly once).

    Args:
        rows: Iterable of row dicts (all rows must be buffered to count).
        column: Column name to check for uniqueness.
        invert: If True, yield rows whose value appears MORE than once.

    Raises:
        KeyError: If *column* is not present in any row.
    """
    buffered = list(rows)
    if not buffered:
        return

    if column not in buffered[0]:
        raise KeyError(f"Column '{column}' not found in CSV headers.")

    counts: Counter = Counter(row[column] for row in buffered)

    for row in buffered:
        is_unique = counts[row[column]] == 1
        if invert:
            if not is_unique:
                yield row
        else:
            if is_unique:
                yield row


def uniquify_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str,
    invert: bool = False,
) -> None:
    """Read from *reader*, filter unique rows, write to *writer*."""
    writer.writeheader()
    for row in uniquify_rows(reader, column=column, invert=invert):
        writer.writerow(row)
