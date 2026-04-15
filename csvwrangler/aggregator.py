"""Aggregation functions for CSV data: group-by with count, sum, min, max, mean."""

from collections import defaultdict
from typing import Dict, List, Optional


SUPPORTED_AGGS = ("count", "sum", "min", "max", "mean")


def aggregate_rows(
    rows: List[Dict[str, str]],
    group_by: List[str],
    agg_column: Optional[str],
    agg_func: str,
) -> List[Dict[str, str]]:
    """Group rows by *group_by* columns and compute an aggregation.

    Args:
        rows: Input rows as list of dicts.
        group_by: Column names to group on.
        agg_column: Column to aggregate (not required for 'count').
        agg_func: One of 'count', 'sum', 'min', 'max', 'mean'.

    Returns:
        List of result rows with group keys plus the aggregated value.

    Raises:
        ValueError: On unsupported agg_func or missing columns.
    """
    if agg_func not in SUPPORTED_AGGS:
        raise ValueError(f"Unsupported aggregation '{agg_func}'. Choose from {SUPPORTED_AGGS}.")
    if agg_func != "count" and not agg_column:
        raise ValueError(f"agg_column is required for aggregation '{agg_func}'.")

    buckets: Dict[tuple, List[str]] = defaultdict(list)

    for row in rows:
        missing = [c for c in group_by if c not in row]
        if missing:
            raise ValueError(f"Group-by column(s) not found in row: {missing}")
        key = tuple(row[c] for c in group_by)
        if agg_func != "count":
            if agg_column not in row:
                raise ValueError(f"Aggregation column '{agg_column}' not found in row.")
            buckets[key].append(row[agg_column])
        else:
            buckets[key]  # ensure key exists
            buckets[key]  # no-op; defaultdict creates it

    # For count we only need the key counts
    if agg_func == "count":
        result_col = "count"
        results = []
        for key, vals in buckets.items():
            r = dict(zip(group_by, key))
            r[result_col] = str(len(vals) if vals else 0)
            results.append(r)
        # Re-count properly
        count_buckets: Dict[tuple, int] = defaultdict(int)
        for row in rows:
            key = tuple(row[c] for c in group_by)
            count_buckets[key] += 1
        results = []
        for key, cnt in count_buckets.items():
            r = dict(zip(group_by, key))
            r["count"] = str(cnt)
            results.append(r)
        return results

    result_col = f"{agg_func}_{agg_column}"
    results = []
    for key, raw_vals in buckets.items():
        try:
            nums = [float(v) for v in raw_vals]
        except ValueError:
            raise ValueError(f"Non-numeric value encountered in column '{agg_column}'.")
        if agg_func == "sum":
            agg_val = sum(nums)
        elif agg_func == "min":
            agg_val = min(nums)
        elif agg_func == "max":
            agg_val = max(nums)
        elif agg_func == "mean":
            agg_val = sum(nums) / len(nums)
        r = dict(zip(group_by, key))
        r[result_col] = str(agg_val)
        results.append(r)
    return results


def aggregate_file(
    input_path: str,
    output_path: str,
    group_by: List[str],
    agg_column: Optional[str],
    agg_func: str,
) -> int:
    """Read *input_path*, aggregate, and write results to *output_path*.

    Returns the number of result rows written.
    """
    import csv

    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    result_rows = aggregate_rows(rows, group_by, agg_column, agg_func)

    if not result_rows:
        return 0

    fieldnames = list(result_rows[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result_rows)

    return len(result_rows)
