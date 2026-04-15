"""Pivot CSV rows: group by a column, spread a second column's values as headers,
and aggregate a third column's values into the resulting cells."""

from collections import defaultdict
from typing import Iterable


def pivot_rows(
    rows: list[dict],
    index: str,
    columns: str,
    values: str,
    aggfunc: str = "sum",
) -> list[dict]:
    """Pivot *rows* in memory.

    Args:
        rows:     Input list of row dicts.
        index:    Column whose distinct values become row identifiers.
        columns:  Column whose distinct values become new column headers.
        values:   Column whose values are aggregated into cells.
        aggfunc:  Aggregation function – one of 'sum', 'count', 'min', 'max', 'first'.

    Returns:
        List of dicts representing the pivoted table.
    """
    if aggfunc not in {"sum", "count", "min", "max", "first"}:
        raise ValueError(f"Unsupported aggfunc '{aggfunc}'. Choose from: sum, count, min, max, first.")

    # Collect raw value lists: buckets[index_val][col_val] = [v1, v2, ...]
    buckets: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    col_order: list[str] = []

    for row in rows:
        idx_val = row.get(index, "")
        col_val = row.get(columns, "")
        raw = row.get(values, "")
        buckets[idx_val][col_val].append(raw)
        if col_val not in col_order:
            col_order.append(col_val)

    def _agg(vals: list) -> str:
        if not vals:
            return ""
        if aggfunc == "count":
            return str(len(vals))
        if aggfunc == "first":
            return str(vals[0])
        numeric = []
        for v in vals:
            try:
                numeric.append(float(v))
            except (ValueError, TypeError):
                pass
        if not numeric:
            return str(vals[0])
        if aggfunc == "sum":
            result = sum(numeric)
        elif aggfunc == "min":
            result = min(numeric)
        else:  # max
            result = max(numeric)
        return str(int(result) if result == int(result) else result)

    result = []
    for idx_val, col_map in buckets.items():
        record = {index: idx_val}
        for col_val in col_order:
            record[col_val] = _agg(col_map.get(col_val, []))
        result.append(record)

    return result


def pivot_file(
    reader: Iterable[dict],
    index: str,
    columns: str,
    values: str,
    aggfunc: str = "sum",
) -> list[dict]:
    """Read all rows from *reader* and return pivoted rows."""
    return pivot_rows(list(reader), index=index, columns=columns, values=values, aggfunc=aggfunc)
