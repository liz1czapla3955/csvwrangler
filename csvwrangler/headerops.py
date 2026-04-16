"""Header operations: reorder, insert, drop columns by name."""
from __future__ import annotations
from typing import Iterable, Iterator


def reorder_columns(rows: Iterable[dict], order: list[str]) -> Iterator[dict]:
    """Yield rows with columns reordered; unknown columns appended at end."""
    rows = list(rows)
    if not rows:
        return
    existing = list(rows[0].keys())
    unknown = [c for c in existing if c not in order]
    final_order = [c for c in order if c in existing] + unknown
    for row in rows:
        yield {c: row[c] for c in final_order if c in row}


def drop_columns(rows: Iterable[dict], columns: list[str]) -> Iterator[dict]:
    """Yield rows with specified columns removed."""
    for row in rows:
        yield {k: v for k, v in row.items() if k not in columns}


def insert_column(
    rows: Iterable[dict],
    name: str,
    value: str,
    position: int = -1,
) -> Iterator[dict]:
    """Yield rows with a new column inserted at position (-1 = end)."""
    for row in rows:
        items = list(row.items())
        entry = (name, value)
        if position < 0 or position >= len(items):
            items.append(entry)
        else:
            items.insert(position, entry)
        yield dict(items)


def headerops_file(
    reader,
    writer,
    operation: str,
    columns: list[str] | None = None,
    insert_name: str | None = None,
    insert_value: str = "",
    insert_position: int = -1,
) -> None:
    rows = list(reader)
    if operation == "reorder":
        result = reorder_columns(rows, columns or [])
    elif operation == "drop":
        result = drop_columns(rows, columns or [])
    elif operation == "insert":
        result = insert_column(rows, insert_name or "new", insert_value, insert_position)
    else:
        raise ValueError(f"Unknown headerops operation: {operation!r}")
    for row in result:
        writer.writerow(row)
