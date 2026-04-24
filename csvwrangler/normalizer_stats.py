"""Statistical normalization for CSV numeric columns.

Supports min-max normalization (scale to [0, 1]) and z-score standardization
(mean=0, std=1), with optional custom output column naming.
"""

import csv
import io
import math
from typing import Iterable, Iterator


def _mean(values: list[float]) -> float:
    """Return the arithmetic mean of a non-empty list."""
    return sum(values) / len(values)


def _stddev(values: list[float]) -> float:
    """Return the population standard deviation."""
    if len(values) < 2:
        return 0.0
    mu = _mean(values)
    return math.sqrt(sum((v - mu) ** 2 for v in values) / len(values))


def _minmax(values: list[float]) -> tuple[float, float]:
    """Return (min, max) of a list."""
    return min(values), max(values)


def normalize_rows(
    rows: Iterable[dict],
    columns: list[str],
    method: str = "minmax",
    suffix: str = "_norm",
    in_place: bool = False,
) -> Iterator[dict]:
    """Normalize numeric columns in *rows*.

    Parameters
    ----------
    rows:
        Iterable of row dicts (consumed into a list for two-pass processing).
    columns:
        Column names to normalize.
    method:
        ``"minmax"`` scales values to [0, 1]; ``"zscore"`` standardizes to
        mean=0 / std=1.
    suffix:
        Appended to each source column name to form the output column name.
        Ignored when *in_place* is True.
    in_place:
        If True, overwrite the source column instead of adding a new one.
    """
    if method not in ("minmax", "zscore"):
        raise ValueError(f"Unknown normalization method: {method!r}")

    all_rows = list(rows)
    if not all_rows:
        return

    # Collect numeric values per column (skip non-numeric / empty strings)
    col_values: dict[str, list[float]] = {c: [] for c in columns}
    for row in all_rows:
        for col in columns:
            raw = row.get(col, "")
            try:
                col_values[col].append(float(raw))
            except (ValueError, TypeError):
                pass

    # Pre-compute stats
    stats: dict[str, tuple] = {}
    for col in columns:
        vals = col_values[col]
        if method == "minmax":
            lo, hi = _minmax(vals) if vals else (0.0, 0.0)
            stats[col] = (lo, hi)
        else:  # zscore
            mu = _mean(vals) if vals else 0.0
            sd = _stddev(vals) if vals else 0.0
            stats[col] = (mu, sd)

    for row in all_rows:
        out = dict(row)
        for col in columns:
            raw = row.get(col, "")
            dest = col if in_place else col + suffix
            try:
                v = float(raw)
            except (ValueError, TypeError):
                out[dest] = raw
                continue

            if method == "minmax":
                lo, hi = stats[col]
                out[dest] = str((v - lo) / (hi - lo)) if hi != lo else "0.0"
            else:  # zscore
                mu, sd = stats[col]
                out[dest] = str((v - mu) / sd) if sd != 0.0 else "0.0"

        yield out


def normalize_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    columns: list[str],
    method: str = "minmax",
    suffix: str = "_norm",
    in_place: bool = False,
) -> None:
    """Read from *reader*, normalize *columns*, write to *writer*."""
    rows = list(reader)
    if not rows:
        writer.writeheader()
        return

    result = list(
        normalize_rows(rows, columns, method=method, suffix=suffix, in_place=in_place)
    )

    # Build fieldnames: original order + new columns appended
    existing = list(rows[0].keys())
    if not in_place:
        new_cols = [c + suffix for c in columns if c + suffix not in existing]
        fieldnames = existing + new_cols
    else:
        fieldnames = existing

    writer.fieldnames = fieldnames
    writer.writeheader()
    for row in result:
        writer.writerow(row)
