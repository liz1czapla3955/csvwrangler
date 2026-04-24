"""Exponential moving average (EMA) smoothing for numeric CSV columns."""

import csv
import io
from typing import Iterator


def smooth_rows(
    rows: list[dict],
    column: str,
    alpha: float = 0.3,
    output_column: str | None = None,
) -> list[dict]:
    """Apply exponential moving average smoothing to a numeric column.

    Args:
        rows: Input rows as dicts.
        column: Column to smooth.
        alpha: Smoothing factor in (0, 1]. Higher = less smoothing.
        output_column: Name for the result column. Defaults to '<column>_ema'.

    Returns:
        List of rows with the smoothed column appended.
    """
    if not 0 < alpha <= 1:
        raise ValueError(f"alpha must be in (0, 1], got {alpha}")

    out_col = output_column or f"{column}_ema"
    result = []
    ema: float | None = None

    for row in rows:
        raw = row.get(column, "")
        try:
            value = float(raw)
        except (ValueError, TypeError):
            result.append({**row, out_col: raw})
            continue

        if ema is None:
            ema = value
        else:
            ema = alpha * value + (1 - alpha) * ema

        result.append({**row, out_col: f"{ema:.6g}"})

    return result


def smooth_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str,
    alpha: float = 0.3,
    output_column: str | None = None,
) -> None:
    """Stream-smooth a CSV file column using EMA."""
    rows = list(reader)
    if not rows:
        return

    smoothed = smooth_rows(rows, column, alpha=alpha, output_column=output_column)

    out_col = output_column or f"{column}_ema"
    fieldnames = list(rows[0].keys())
    if out_col not in fieldnames:
        fieldnames = fieldnames + [out_col]

    writer.fieldnames = fieldnames
    writer.writeheader()
    for row in smoothed:
        writer.writerow(row)
