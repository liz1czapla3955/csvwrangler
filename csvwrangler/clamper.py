"""Clamp numeric values in CSV columns to a [low, high] range (inclusive).

Unlike the clipper (which clips to literal bounds), the clamper accepts
percentile-based bounds computed from the data itself.
"""

from __future__ import annotations

import csv
import io
from typing import Iterable, Iterator


def _percentile(values: list[float], p: float) -> float:
    """Return the p-th percentile (0-100) of a sorted list."""
    if not values:
        raise ValueError("Cannot compute percentile of empty list")
    values = sorted(values)
    idx = (p / 100) * (len(values) - 1)
    lo = int(idx)
    hi = lo + 1
    if hi >= len(values):
        return values[lo]
    frac = idx - lo
    return values[lo] + frac * (values[hi] - values[lo])


def clamp_rows(
    rows: Iterable[dict],
    column: str,
    low: float | None = None,
    high: float | None = None,
    low_pct: float | None = None,
    high_pct: float | None = None,
    output_column: str | None = None,
) -> list[dict]:
    """Return rows with *column* values clamped to [low, high].

    If *low_pct* / *high_pct* are given they override *low* / *high* and are
    resolved from the data before clamping.
    """
    rows = list(rows)
    if not rows:
        return rows

    out_col = output_column or column

    if low_pct is not None or high_pct is not None:
        numeric: list[float] = []
        for r in rows:
            try:
                numeric.append(float(r.get(column, "")))
            except (ValueError, TypeError):
                pass
        if low_pct is not None:
            low = _percentile(numeric, low_pct)
        if high_pct is not None:
            high = _percentile(numeric, high_pct)

    result: list[dict] = []
    for row in rows:
        new_row = dict(row)
        raw = row.get(column, "")
        try:
            val = float(raw)
            if low is not None:
                val = max(val, low)
            if high is not None:
                val = min(val, high)
            # Preserve int-like appearance when possible
            new_row[out_col] = str(int(val)) if val == int(val) else str(val)
        except (ValueError, TypeError):
            new_row[out_col] = raw
        result.append(new_row)
    return result


def clamp_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str,
    low: float | None = None,
    high: float | None = None,
    low_pct: float | None = None,
    high_pct: float | None = None,
    output_column: str | None = None,
) -> None:
    rows = clamp_rows(
        reader,
        column=column,
        low=low,
        high=high,
        low_pct=low_pct,
        high_pct=high_pct,
        output_column=output_column,
    )
    if rows:
        writer.writeheader()
        writer.writerows(rows)
