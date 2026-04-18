"""Coalesce: fill empty values in a column from one or more fallback columns."""

import csv
import io
from typing import Iterator


def coalesce_rows(
    rows: Iterator[dict],
    target: str,
    sources: list[str],
    *,
    empty_values: tuple[str, ...] = ("",),
) -> Iterator[dict]:
    """For each row, if *target* is empty, fill it from the first non-empty
    value found in *sources* (left-to-right).

    Args:
        rows: iterable of row dicts.
        target: column to fill.
        sources: ordered list of fallback columns.
        empty_values: values treated as "empty" (default: just empty string).

    Yields:
        Row dicts with *target* potentially filled.
    """
    for row in rows:
        if row.get(target, "") in empty_values:
            for src in sources:
                val = row.get(src, "")
                if val not in empty_values:
                    row = dict(row)
                    row[target] = val
                    break
        yield row


def coalesce_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    target: str,
    sources: list[str],
    empty_values: tuple[str, ...] = ("",),
) -> None:
    """Stream-process *reader*, coalescing *target* from *sources*, write to *writer*."""
    writer.writeheader()
    for row in coalesce_rows(reader, target, sources, empty_values=empty_values):
        writer.writerow(row)
