"""Compute pairwise Pearson correlation coefficients between numeric columns."""

from __future__ import annotations

import csv
import math
from typing import Iterable, Iterator


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    """Return Pearson r for two equal-length lists, or None if undefined."""
    n = len(xs)
    if n < 2:
        return None
    mx, my = _mean(xs), _mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denom_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if denom_x == 0 or denom_y == 0:
        return None
    return num / (denom_x * denom_y)


def correlate_rows(
    rows: Iterable[dict[str, str]],
    columns: list[str],
    decimals: int = 4,
) -> Iterator[dict[str, str]]:
    """Yield correlation matrix rows for the requested numeric columns."""
    data: dict[str, list[float]] = {col: [] for col in columns}
    for row in rows:
        for col in columns:
            raw = row.get(col, "").strip()
            try:
                data[col].append(float(raw))
            except ValueError:
                data[col].append(float("nan"))

    # Remove rows where any selected column is NaN (pairwise complete)
    n_rows = min(len(v) for v in data.values()) if data else 0
    clean: dict[str, list[float]] = {col: [] for col in columns}
    for i in range(n_rows):
        if all(not math.isnan(data[col][i]) for col in columns):
            for col in columns:
                clean[col].append(data[col][i])

    for col_a in columns:
        result: dict[str, str] = {"column": col_a}
        for col_b in columns:
            r = _pearson(clean[col_a], clean[col_b])
            result[col_b] = "" if r is None else f"{r:.{decimals}f}"
        yield result


def correlate_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    columns: list[str],
    decimals: int = 4,
) -> None:
    rows = list(reader)
    output_fieldnames = ["column"] + columns
    writer.fieldnames = output_fieldnames
    writer.writeheader()
    for row in correlate_rows(rows, columns, decimals=decimals):
        writer.writerow(row)
