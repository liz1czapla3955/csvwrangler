"""Round numeric values in specified CSV columns to a given number of decimal places."""

import csv
import io
from typing import Iterable, Iterator


def _round_value(value: str, decimals: int) -> str:
    """Attempt to round a numeric string; return original on failure."""
    try:
        num = float(value)
        if decimals == 0:
            return str(int(round(num, 0)))
        return str(round(num, decimals))
    except (ValueError, TypeError):
        return value


def round_rows(
    rows: Iterable[dict],
    columns: list[str],
    decimals: int = 2,
) -> Iterator[dict]:
    """Yield rows with numeric values in *columns* rounded to *decimals* places.

    Args:
        rows:     Iterable of row dicts (as produced by csv.DictReader).
        columns:  Column names whose values should be rounded.
        decimals: Number of decimal places to round to (default 2).

    Yields:
        Row dicts with the specified columns rounded.
    """
    col_set = set(columns)
    for row in rows:
        new_row = {}
        for key, val in row.items():
            if key in col_set:
                new_row[key] = _round_value(val, decimals)
            else:
                new_row[key] = val
        yield new_row


def round_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    columns: list[str],
    decimals: int = 2,
) -> None:
    """Read from *reader*, round specified columns, and write to *writer*."""
    writer.writeheader()
    for row in round_rows(reader, columns, decimals):
        writer.writerow(row)
