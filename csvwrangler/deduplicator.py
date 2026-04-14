"""CSV deduplication module for csvwrangler."""

import csv
import hashlib
from typing import Iterator, Optional


def _row_hash(row: dict, key_fields: Optional[list] = None) -> str:
    """Generate a hash for a CSV row, optionally using only specific fields."""
    if key_fields:
        values = {k: row[k] for k in key_fields if k in row}
    else:
        values = row
    content = str(sorted(values.items())).encode("utf-8")
    return hashlib.md5(content).hexdigest()


def deduplicate_rows(
    rows: Iterator[dict],
    key_fields: Optional[list] = None,
    keep: str = "first",
) -> list[dict]:
    """Remove duplicate rows from an iterable of dicts.

    Args:
        rows: Iterable of row dicts (from csv.DictReader).
        key_fields: Optional list of field names to use as the uniqueness key.
                    If None, all fields are used.
        keep: 'first' to keep the first occurrence, 'last' to keep the last.

    Returns:
        List of deduplicated row dicts.
    """
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    seen: dict[str, dict] = {}
    for row in rows:
        h = _row_hash(row, key_fields)
        if keep == "first" and h not in seen:
            seen[h] = row
        elif keep == "last":
            seen[h] = row

    return list(seen.values())


def deduplicate_file(
    input_path: str,
    output_path: str,
    key_fields: Optional[list] = None,
    keep: str = "first",
) -> tuple[int, int]:
    """Deduplicate a CSV file and write results to output_path.

    Returns:
        Tuple of (original_count, deduplicated_count).
    """
    with open(input_path, newline="", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    original_count = len(rows)
    deduped = deduplicate_rows(rows, key_fields=key_fields, keep=keep)
    deduped_count = len(deduped)

    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduped)

    return original_count, deduped_count
