"""Truncate CSV rows by limiting the number of characters in each cell."""

import csv
import io
from typing import Optional


def truncate_rows(
    rows: list[dict],
    max_length: int,
    columns: Optional[list[str]] = None,
    placeholder: str = "...",
) -> list[dict]:
    """Return rows with cell values truncated to max_length characters.

    Args:
        rows: List of row dicts.
        max_length: Maximum number of characters allowed per cell value.
        columns: If provided, only truncate these columns; otherwise truncate all.
        placeholder: String appended when a value is truncated.

    Returns:
        New list of row dicts with truncated values.
    """
    if max_length < len(placeholder):
        raise ValueError(
            f"max_length ({max_length}) must be >= len(placeholder) ({len(placeholder)})"
        )

    result = []
    for row in rows:
        new_row = {}
        for key, value in row.items():
            if columns is None or key in columns:
                if len(value) > max_length:
                    cut = max_length - len(placeholder)
                    value = value[:cut] + placeholder
            new_row[key] = value
        result.append(new_row)
    return result


def truncate_file(
    input_path: str,
    output_path: str,
    max_length: int,
    columns: Optional[list[str]] = None,
    placeholder: str = "...",
) -> None:
    """Read a CSV file, truncate cell values, and write to output."""
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    truncated = truncate_rows(rows, max_length, columns, placeholder)

    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(truncated)
