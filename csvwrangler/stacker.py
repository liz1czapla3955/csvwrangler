"""Stack (concatenate) multiple CSV row sets vertically."""
from typing import Iterable, List, Dict, Optional
import csv
import io


def stack_rows(
    sources: List[List[Dict[str, str]]],
    fill_value: str = "",
    strict: bool = False,
) -> List[Dict[str, str]]:
    """Vertically stack multiple lists of rows.

    Args:
        sources: A list of row-lists to concatenate.
        fill_value: Value to use for missing columns when strict=False.
        strict: If True, raise ValueError when column sets differ.

    Returns:
        Combined list of rows with a unified header.
    """
    if not sources:
        return []

    # Collect all column names preserving first-seen order
    seen: dict = {}
    for rows in sources:
        for row in rows:
            for col in row:
                if col not in seen:
                    seen[col] = None
    all_columns: List[str] = list(seen.keys())

    if strict:
        for idx, rows in enumerate(sources):
            if rows:
                cols = list(rows[0].keys())
                if cols != all_columns:
                    raise ValueError(
                        f"Column mismatch in source {idx}: "
                        f"expected {all_columns}, got {cols}"
                    )

    result: List[Dict[str, str]] = []
    for rows in sources:
        for row in rows:
            new_row = {col: row.get(col, fill_value) for col in all_columns}
            result.append(new_row)
    return result


def stack_files(
    readers: List[csv.DictReader],
    writer: csv.DictWriter,
    fill_value: str = "",
    strict: bool = False,
) -> None:
    """Read from multiple DictReaders, stack rows, write to DictWriter."""
    sources = [list(r) for r in readers]
    rows = stack_rows(sources, fill_value=fill_value, strict=strict)
    if not rows:
        return
    writer.writeheader()
    writer.writerows(rows)
