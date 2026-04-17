"""Clip numeric values in CSV columns to a specified range."""

import csv
import io
from typing import Iterable, Iterator, Optional


def _clip_value(value: str, low: Optional[float], high: Optional[float]) -> str:
    """Clip a numeric string to [low, high]. Non-numeric values pass through."""
    try:
        num = float(value)
    except ValueError:
        return value
    if low is not None and num < low:
        num = low
    if high is not None and num > high:
        num = high
    # Preserve int-like appearance when possible
    if num == int(num) and '.' not in value:
        return str(int(num))
    return str(num)


def clip_rows(
    rows: Iterable[dict],
    columns: list[str],
    low: Optional[float] = None,
    high: Optional[float] = None,
) -> Iterator[dict]:
    """Yield rows with specified columns clipped to [low, high]."""
    if low is None and high is None:
        raise ValueError("At least one of low or high must be specified.")
    for row in rows:
        new_row = dict(row)
        for col in columns:
            if col in new_row:
                new_row[col] = _clip_value(new_row[col], low, high)
        yield new_row


def clip_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    columns: list[str],
    low: Optional[float] = None,
    high: Optional[float] = None,
) -> None:
    """Read from reader, clip columns, write to writer."""
    writer.writeheader()
    for row in clip_rows(reader, columns, low=low, high=high):
        writer.writerow(row)
