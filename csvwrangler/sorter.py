"""CSV row sorting functionality."""

import csv
from typing import List, Optional


def sort_rows(
    rows: List[dict],
    keys: List[str],
    reverse: bool = False,
    numeric: bool = False,
) -> List[dict]:
    """Sort a list of row dicts by one or more column keys.

    Args:
        rows: List of row dictionaries.
        keys: Column names to sort by (left = highest priority).
        reverse: If True, sort descending.
        numeric: If True, attempt numeric comparison for sort keys.

    Returns:
        New sorted list of row dictionaries.
    """
    if not rows:
        return []

    for key in keys:
        if key not in rows[0]:
            raise KeyError(f"Sort key '{key}' not found in CSV headers.")

    def sort_key(row: dict):
        values = []
        for k in keys:
            val = row.get(k, "")
            if numeric:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    values.append(float("-inf") if not reverse else float("inf"))
            else:
                values.append(val)
        return values

    return sorted(rows, key=sort_key, reverse=reverse)


def sort_file(
    input_path: str,
    output_path: str,
    keys: List[str],
    reverse: bool = False,
    numeric: bool = False,
    delimiter: str = ",",
) -> int:
    """Sort a CSV file and write the result to output_path.

    Returns:
        Number of rows written.
    """
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    sorted_rows = sort_rows(rows, keys=keys, reverse=reverse, numeric=numeric)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(sorted_rows)

    return len(sorted_rows)
