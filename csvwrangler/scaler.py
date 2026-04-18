"""Numeric column scaling: min-max normalization or z-score standardization."""
import csv
import io
from typing import Iterable, Iterator


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _stddev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = _mean(values)
    variance = sum((v - m) ** 2 for v in values) / len(values)
    return variance ** 0.5


def scale_rows(
    rows: Iterable[dict],
    columns: list[str],
    method: str = "minmax",
) -> list[dict]:
    """Scale numeric columns using 'minmax' or 'zscore' method."""
    if method not in ("minmax", "zscore"):
        raise ValueError(f"Unknown scaling method: {method!r}. Use 'minmax' or 'zscore'.")

    rows = list(rows)
    if not rows:
        return []

    stats: dict[str, dict] = {}
    for col in columns:
        vals = []
        for row in rows:
            try:
                vals.append(float(row[col]))
            except (ValueError, KeyError):
                pass
        if method == "minmax":
            lo = min(vals) if vals else 0.0
            hi = max(vals) if vals else 0.0
            stats[col] = {"lo": lo, "hi": hi, "range": hi - lo}
        else:
            m = _mean(vals)
            s = _stddev(vals)
            stats[col] = {"mean": m, "std": s}

    result = []
    for row in rows:
        new_row = dict(row)
        for col in columns:
            try:
                v = float(row[col])
            except (ValueError, KeyError):
                result.append(new_row)
                continue
            if method == "minmax":
                r = stats[col]["range"]
                new_row[col] = str((v - stats[col]["lo"]) / r) if r != 0 else "0.0"
            else:
                s = stats[col]["std"]
                new_row[col] = str((v - stats[col]["mean"]) / s) if s != 0 else "0.0"
        result.append(new_row)
    return result


def scale_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    columns: list[str],
    method: str = "minmax",
) -> None:
    rows = list(reader)
    scaled = scale_rows(rows, columns, method)
    writer.writeheader()
    for row in scaled:
        writer.writerow(row)
