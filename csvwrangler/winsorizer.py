"""Winsorize numeric columns by clamping values at given percentile bounds."""

import csv
import io
from typing import Iterable, Iterator


def _percentile(values: list[float], pct: float) -> float:
    """Return the value at the given percentile (0-100) using linear interpolation."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    index = (pct / 100.0) * (n - 1)
    lo = int(index)
    hi = lo + 1
    if hi >= n:
        return sorted_vals[-1]
    frac = index - lo
    return sorted_vals[lo] + frac * (sorted_vals[hi] - sorted_vals[lo])


def winsorize_rows(
    rows: Iterable[dict],
    columns: list[str],
    lower_pct: float = 5.0,
    upper_pct: float = 95.0,
) -> list[dict]:
    """Winsorize the specified columns in rows.

    Values below the lower percentile are clamped to that percentile value;
    values above the upper percentile are clamped to that percentile value.
    Non-numeric values are passed through unchanged.
    """
    rows = list(rows)
    if not rows:
        return []

    bounds: dict[str, tuple[float, float]] = {}
    for col in columns:
        numeric_vals: list[float] = []
        for row in rows:
            val = row.get(col, "")
            try:
                numeric_vals.append(float(val))
            except (ValueError, TypeError):
                pass
        if numeric_vals:
            lo = _percentile(numeric_vals, lower_pct)
            hi = _percentile(numeric_vals, upper_pct)
            bounds[col] = (lo, hi)

    result = []
    for row in rows:
        new_row = dict(row)
        for col, (lo, hi) in bounds.items():
            val = new_row.get(col, "")
            try:
                fval = float(val)
                clamped = max(lo, min(hi, fval))
                # Preserve int-like representation when possible
                if clamped == int(clamped) and "." not in str(val):
                    new_row[col] = str(int(clamped))
                else:
                    new_row[col] = str(clamped)
            except (ValueError, TypeError):
                pass
        result.append(new_row)
    return result


def winsorize_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    columns: list[str],
    lower_pct: float = 5.0,
    upper_pct: float = 95.0,
) -> None:
    """Read from reader, winsorize columns, write to writer."""
    rows = list(reader)
    result = winsorize_rows(rows, columns, lower_pct=lower_pct, upper_pct=upper_pct)
    writer.writeheader()
    for row in result:
        writer.writerow(row)
