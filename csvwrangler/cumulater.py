"""Cumulative aggregation (running total/min/max/product) over a numeric column."""

import csv
import io
from typing import Iterable, Iterator

_SUPPORTED_OPS = ("sum", "min", "max", "product")


def cumulate_rows(
    rows: Iterable[dict],
    column: str,
    op: str = "sum",
    output_column: str | None = None,
) -> Iterator[dict]:
    """Yield rows with a new column holding the running cumulative value.

    Args:
        rows: Iterable of dicts (CSV rows).
        column: Name of the numeric column to accumulate.
        op: One of 'sum', 'min', 'max', 'product'.
        output_column: Name for the new column (defaults to 'cumulative_{op}').

    Yields:
        Each input row with the extra cumulative column appended.
    """
    if op not in _SUPPORTED_OPS:
        raise ValueError(f"Unsupported op '{op}'. Choose from: {_SUPPORTED_OPS}")

    out_col = output_column or f"cumulative_{op}"
    accumulator: float | None = None

    for row in rows:
        raw = row.get(column, "")
        try:
            value = float(raw)
        except (ValueError, TypeError):
            row[out_col] = ""
            yield row
            continue

        if accumulator is None:
            accumulator = value
        elif op == "sum":
            accumulator += value
        elif op == "min":
            accumulator = min(accumulator, value)
        elif op == "max":
            accumulator = max(accumulator, value)
        elif op == "product":
            accumulator *= value

        # Emit as int string when the result is a whole number
        row[out_col] = (
            str(int(accumulator))
            if accumulator == int(accumulator)
            else str(accumulator)
        )
        yield row


def cumulate_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str,
    op: str = "sum",
    output_column: str | None = None,
) -> None:
    """Read from *reader*, cumulate, and write to *writer*."""
    out_col = output_column or f"cumulative_{op}"
    fieldnames = list(reader.fieldnames or []) + [out_col]
    writer.fieldnames = fieldnames
    writer.writeheader()
    for row in cumulate_rows(reader, column=column, op=op, output_column=out_col):
        writer.writerow(row)
